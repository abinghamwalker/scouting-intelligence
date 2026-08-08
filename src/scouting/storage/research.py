"""Immutable SQLite and guarded-artifact persistence for W09 research state."""

from __future__ import annotations

import json
import re
from typing import Any, Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import ValidationError
from sqlalchemy import Engine, text
from sqlalchemy.engine import RowMapping
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from scouting.contracts.research import (
    ResearchReplayReceipt,
    ResearchReplayStatus,
    SavedResearchExperiment,
    SavedResearchExperimentSummary,
    canonical_research_digest,
)
from scouting.contracts.validation import revalidate_exact_contract

from .formats import FormatError, canonical_json_bytes
from .guarded import ArtifactConflictError, GuardedStorage, StorageError, sha256_hex

RESEARCH_REPORT_ROOT_NAME = "research_reports"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_REPLAY_RECEIPT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w09:research-replay-receipt:v1",
)


class ResearchStorageError(RuntimeError):
    """Base class for fail-closed research persistence errors."""


class ResearchStorageConfigurationError(ResearchStorageError):
    """The injected persistence components cannot serve W09 research state."""


class ResearchStorageIntegrityError(ResearchStorageError):
    """Persisted research metadata or report bytes failed exact verification."""


class ResearchStorageConflictError(ResearchStorageError):
    """An immutable experiment, receipt, or report address conflicts."""


class ResearchExperimentNotFoundError(ResearchStorageError, LookupError):
    """The requested immutable experiment does not exist."""


def research_report_relative_path(
    report_digest: str,
    report_format: Literal["json", "html"],
) -> str:
    """Return the sole content address accepted for one research report digest."""

    if type(report_digest) is not str or _SHA256.fullmatch(report_digest) is None:
        raise ResearchStorageIntegrityError("report digest is not canonical SHA-256")
    if report_format not in {"json", "html"}:
        raise ResearchStorageIntegrityError("research report format is unsupported")
    return f"sha256/{report_digest[:2]}/{report_digest}.{report_format}"


def research_replay_receipt_id(receipt: ResearchReplayReceipt) -> UUID:
    """Derive UUIDv5 from semantic receipt fields, excluding IDs and evidence clocks."""

    if type(receipt) is not ResearchReplayReceipt:
        raise TypeError("receipt must be an exact ResearchReplayReceipt")
    projection = receipt.model_dump(
        mode="json",
        exclude={"replay_receipt_id", "receipt_digest", "replayed_at"},
    )
    return uuid5(_REPLAY_RECEIPT_NAMESPACE, canonical_research_digest(projection))


def _canonical_model_text(value: object) -> str:
    try:
        return canonical_json_bytes(value).decode("utf-8", errors="strict")
    except (FormatError, UnicodeError) as exc:
        raise ResearchStorageIntegrityError("research JSON is not canonical") from exc


def _validated_experiment(experiment: SavedResearchExperiment) -> SavedResearchExperiment:
    return revalidate_exact_contract(
        experiment,
        SavedResearchExperiment,
        label="saved experiment",
        error_type=ResearchStorageIntegrityError,
    )


def _validated_receipt(receipt: ResearchReplayReceipt) -> ResearchReplayReceipt:
    return revalidate_exact_contract(
        receipt,
        ResearchReplayReceipt,
        label="replay receipt",
        error_type=ResearchStorageIntegrityError,
    )


def _canonical_contract_text(value: object) -> str:
    model_dump = getattr(value, "model_dump", None)
    if not callable(model_dump):
        raise TypeError("research contract must expose model_dump")
    return _canonical_model_text(model_dump(mode="json"))


def _decode_canonical_object(value: object, *, field: str) -> dict[str, Any]:
    if type(value) is not str:
        raise ResearchStorageIntegrityError(f"persisted {field} must be exact text")
    encoded = value.encode("utf-8", errors="strict")
    try:
        decoded = json.loads(encoded)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ResearchStorageIntegrityError(f"persisted {field} is not strict JSON") from exc
    if type(decoded) is not dict or canonical_json_bytes(decoded) != encoded:
        raise ResearchStorageIntegrityError(f"persisted {field} is not canonical JSON")
    return cast(dict[str, Any], decoded)


def _json_datetime(value: SavedResearchExperiment, field: str) -> str:
    rendered = value.model_dump(mode="json")[field]
    if type(rendered) is not str:
        raise AssertionError(f"validated experiment {field} did not render as text")
    return rendered


class ResearchExperimentStore:
    """Persist exact experiments, guarded reports, and immutable replay receipts."""

    def __init__(self, engine: Engine, storage: GuardedStorage) -> None:
        if not isinstance(engine, Engine):
            raise TypeError("engine must be a SQLAlchemy Engine")
        if engine.dialect.name != "sqlite":
            raise ResearchStorageConfigurationError("research state requires SQLite")
        if not isinstance(storage, GuardedStorage):
            raise TypeError("storage must be GuardedStorage")
        self._engine = engine
        self._storage = storage

    def save_experiment(
        self,
        experiment: SavedResearchExperiment,
        report_bytes: bytes,
    ) -> SavedResearchExperiment:
        """Atomically bind one immutable database row to verified report bytes.

        SQLite intent is inserted before guarded bytes. A storage conflict therefore
        rolls back the database transaction. If process or commit failure leaves an
        unreferenced byte-identical content address, an exact retry safely adopts it.
        """

        validated = _validated_experiment(experiment)
        self._validate_submitted_report(validated, report_bytes)
        try:
            with self._engine.begin() as connection:
                existing_row = (
                    connection.execute(
                        text(
                            "SELECT * FROM research_experiments "
                            "WHERE experiment_id = :experiment_id"
                        ),
                        {"experiment_id": str(validated.experiment_id)},
                    )
                    .mappings()
                    .one_or_none()
                )
                if existing_row is not None:
                    existing = self._verified_experiment_from_row(existing_row)
                    if existing != validated:
                        raise ResearchStorageConflictError(
                            "experiment id already binds different immutable state"
                        )
                    self._verify_report(existing, expected_bytes=report_bytes)
                    return existing

                connection.execute(
                    text(
                        """INSERT INTO research_experiments (
                        experiment_id, schema_version, name, note, created_at,
                        query_id, result_id, dataset_version, dataset_manifest_digest,
                        matrix_version, matrix_digest, index_version,
                        index_manifest_digest, request_json, result_json, comparison_json,
                        report_json, report_digest, report_relative_path, experiment_digest
                        ) VALUES (
                        :experiment_id, :schema_version, :name, :note, :created_at,
                        :query_id, :result_id, :dataset_version, :dataset_manifest_digest,
                        :matrix_version, :matrix_digest, :index_version,
                        :index_manifest_digest, :request_json, :result_json,
                        :comparison_json, :report_json, :report_digest, :report_relative_path,
                        :experiment_digest
                        )"""
                    ),
                    self._experiment_parameters(validated),
                )
                try:
                    self._storage.write_bytes(
                        RESEARCH_REPORT_ROOT_NAME,
                        validated.report.report_relative_path,
                        report_bytes,
                        media_type=self._report_media_type(validated),
                        lineage=self._report_lineage(validated),
                        retention={
                            "append_only": True,
                            "external_export": False,
                            "policy": "immutable_local_research_report",
                        },
                    )
                    self._verify_report(validated, expected_bytes=report_bytes)
                except ArtifactConflictError as exc:
                    raise ResearchStorageConflictError(
                        "research report content address conflicts"
                    ) from exc
                except (StorageError, OSError) as exc:
                    raise ResearchStorageIntegrityError(
                        "research report persistence failed closed"
                    ) from exc
        except ResearchStorageError:
            raise
        except IntegrityError as exc:
            return self._resolve_experiment_insert_race(validated, report_bytes, exc)
        except SQLAlchemyError as exc:
            raise ResearchStorageIntegrityError("research experiment persistence failed") from exc
        return validated

    def load_experiment(self, experiment_id: UUID) -> SavedResearchExperiment:
        """Load one experiment only after canonical JSON and report verification."""

        if type(experiment_id) is not UUID:
            raise TypeError("experiment_id must be an exact UUID")
        try:
            with self._engine.connect() as connection:
                row = (
                    connection.execute(
                        text(
                            "SELECT * FROM research_experiments "
                            "WHERE experiment_id = :experiment_id"
                        ),
                        {"experiment_id": str(experiment_id)},
                    )
                    .mappings()
                    .one_or_none()
                )
        except SQLAlchemyError as exc:
            raise ResearchStorageIntegrityError("research experiment lookup failed") from exc
        if row is None:
            raise ResearchExperimentNotFoundError(f"research experiment not found: {experiment_id}")
        return self._verified_experiment_from_row(row)

    def list_experiments(self) -> tuple[SavedResearchExperimentSummary, ...]:
        """List bounded metadata projections in deterministic newest-first order."""

        try:
            with self._engine.connect() as connection:
                rows = (
                    connection.execute(
                        text(
                            """SELECT schema_version, experiment_id, name, note, created_at,
                            query_id, result_id, dataset_version, dataset_manifest_digest,
                            matrix_version, matrix_digest, index_version, index_manifest_digest,
                            report_digest, report_relative_path, experiment_digest
                            FROM research_experiments """
                            "ORDER BY created_at DESC, experiment_id"
                        )
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            raise ResearchStorageIntegrityError("research experiment listing failed") from exc
        summaries: list[SavedResearchExperimentSummary] = []
        for row in rows:
            relative_path = row["report_relative_path"]
            if type(relative_path) is not str:
                raise ResearchStorageIntegrityError("persisted report path must be exact text")
            if relative_path.endswith(".json"):
                report_format: Literal["json", "html"] = "json"
            elif relative_path.endswith(".html"):
                report_format = "html"
            else:
                raise ResearchStorageIntegrityError(
                    "persisted report path has an unsupported suffix"
                )
            try:
                summaries.append(
                    SavedResearchExperimentSummary.model_validate_json(
                        canonical_json_bytes({**dict(row), "report_format": report_format})
                    )
                )
            except ValidationError as exc:
                raise ResearchStorageIntegrityError(
                    "saved experiment summary contract rejected"
                ) from exc
        return tuple(summaries)

    def load_report_bytes(self, experiment_id: UUID) -> bytes:
        """Return exact saved report bytes only after experiment and digest verification."""

        experiment = self.load_experiment(experiment_id)
        return self._verify_report(experiment)

    def append_replay_receipt(self, receipt: ResearchReplayReceipt) -> UUID:
        """Append or idempotently confirm one deterministic replay receipt."""

        validated = _validated_receipt(receipt)
        receipt_id = research_replay_receipt_id(validated)
        if validated.replay_receipt_id != receipt_id:
            raise ResearchStorageIntegrityError(
                "replay_receipt_id is not the deterministic semantic identity"
            )
        receipt_json = _canonical_contract_text(validated)
        try:
            with self._engine.begin() as connection:
                experiment_row = (
                    connection.execute(
                        text(
                            "SELECT * FROM research_experiments "
                            "WHERE experiment_id = :experiment_id"
                        ),
                        {"experiment_id": str(validated.experiment_id)},
                    )
                    .mappings()
                    .one_or_none()
                )
                if experiment_row is None:
                    raise ResearchExperimentNotFoundError(
                        f"research experiment not found: {validated.experiment_id}"
                    )
                experiment = self._verified_experiment_from_row(experiment_row)
                self._verify_receipt_against_experiment(validated, experiment)

                existing_row = (
                    connection.execute(
                        text(
                            "SELECT * FROM research_replay_receipts "
                            "WHERE replay_receipt_id = :replay_receipt_id"
                        ),
                        {"replay_receipt_id": str(receipt_id)},
                    )
                    .mappings()
                    .one_or_none()
                )
                if existing_row is not None:
                    existing = self._receipt_from_row(existing_row)
                    if existing != validated:
                        raise ResearchStorageConflictError(
                            "replay receipt id already binds different immutable state"
                        )
                    return receipt_id

                replayed_at = validated.model_dump(mode="json")["replayed_at"]
                if type(replayed_at) is not str:
                    raise AssertionError("validated replayed_at did not render as text")
                connection.execute(
                    text(
                        """INSERT INTO research_replay_receipts (
                        replay_receipt_id, experiment_id, replayed_at, reproduced,
                        original_result_digest, replay_result_digest, receipt_json
                        ) VALUES (
                        :replay_receipt_id, :experiment_id, :replayed_at, :reproduced,
                        :original_result_digest, :replay_result_digest, :receipt_json
                        )"""
                    ),
                    {
                        "replay_receipt_id": str(receipt_id),
                        "experiment_id": str(validated.experiment_id),
                        "replayed_at": replayed_at,
                        "reproduced": int(validated.status is ResearchReplayStatus.REPRODUCED),
                        "original_result_digest": validated.original_result_digest,
                        "replay_result_digest": validated.replay_result_digest,
                        "receipt_json": receipt_json,
                    },
                )
        except ResearchStorageError:
            raise
        except IntegrityError as exc:
            return self._resolve_receipt_insert_race(validated, receipt_id, exc)
        except SQLAlchemyError as exc:
            raise ResearchStorageIntegrityError("replay receipt persistence failed") from exc
        return receipt_id

    def list_replay_receipts(
        self,
        experiment_id: UUID,
    ) -> tuple[ResearchReplayReceipt, ...]:
        """List validated receipts while retaining their exact saved and loaded pins."""

        if type(experiment_id) is not UUID:
            raise TypeError("experiment_id must be an exact UUID")
        # This also verifies that the experiment's guarded report remains intact.
        experiment = self.load_experiment(experiment_id)
        try:
            with self._engine.connect() as connection:
                rows = (
                    connection.execute(
                        text(
                            "SELECT * FROM research_replay_receipts "
                            "WHERE experiment_id = :experiment_id "
                            "ORDER BY replayed_at DESC, replay_receipt_id"
                        ),
                        {"experiment_id": str(experiment_id)},
                    )
                    .mappings()
                    .all()
                )
        except SQLAlchemyError as exc:
            raise ResearchStorageIntegrityError("replay receipt listing failed") from exc
        receipts = tuple(self._receipt_from_row(row) for row in rows)
        for receipt in receipts:
            self._verify_receipt_against_experiment(receipt, experiment)
        return receipts

    @staticmethod
    def _validate_submitted_report(
        experiment: SavedResearchExperiment,
        report_bytes: bytes,
    ) -> None:
        if type(report_bytes) is not bytes:
            raise TypeError("report_bytes must be exact bytes")
        if sha256_hex(report_bytes) != experiment.report.report_digest:
            raise ResearchStorageIntegrityError("report bytes do not match report_digest")
        expected_path = research_report_relative_path(
            experiment.report.report_digest,
            experiment.report.report_format,
        )
        if experiment.report.report_relative_path != expected_path:
            raise ResearchStorageIntegrityError(
                "report_relative_path is not the digest content address"
            )
        if experiment.report.report_format == "json":
            try:
                decoded = json.loads(report_bytes.decode("utf-8", errors="strict"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ResearchStorageIntegrityError(
                    "JSON research report is not strict UTF-8 JSON"
                ) from exc
            if canonical_json_bytes(decoded) != report_bytes:
                raise ResearchStorageIntegrityError("JSON research report is not canonical")
        else:
            try:
                report_bytes.decode("utf-8", errors="strict")
            except UnicodeError as exc:
                raise ResearchStorageIntegrityError(
                    "HTML research report is not strict UTF-8"
                ) from exc

    @staticmethod
    def _experiment_parameters(experiment: SavedResearchExperiment) -> dict[str, object]:
        pins = experiment.request.pins
        return {
            "experiment_id": str(experiment.experiment_id),
            "schema_version": experiment.schema_version,
            "name": experiment.name,
            "note": experiment.note,
            "created_at": _json_datetime(experiment, "created_at"),
            "query_id": str(experiment.request.query_id),
            "result_id": str(experiment.result.result_id),
            "dataset_version": pins.dataset_version,
            "dataset_manifest_digest": pins.dataset_manifest_digest,
            "matrix_version": pins.matrix_version,
            "matrix_digest": pins.matrix_digest,
            "index_version": pins.index_version,
            "index_manifest_digest": pins.index_manifest_digest,
            "request_json": _canonical_contract_text(experiment.request),
            "result_json": _canonical_contract_text(experiment.result),
            "comparison_json": (
                _canonical_contract_text(experiment.comparison)
                if experiment.comparison is not None
                else None
            ),
            "report_json": _canonical_contract_text(experiment.report),
            "report_digest": experiment.report.report_digest,
            "report_relative_path": experiment.report.report_relative_path,
            "experiment_digest": experiment.experiment_digest,
        }

    @staticmethod
    def _report_lineage(experiment: SavedResearchExperiment) -> dict[str, object]:
        pins = experiment.request.pins
        return {
            "dataset_version": pins.dataset_version,
            "dataset_manifest_digest": pins.dataset_manifest_digest,
            "index_version": pins.index_version,
            "index_manifest_digest": pins.index_manifest_digest,
            "matrix_version": pins.matrix_version,
            "matrix_digest": pins.matrix_digest,
            "query_digest": experiment.request.query_digest,
            "report_digest": experiment.report.report_digest,
            "report_format": experiment.report.report_format,
            "result_digest": experiment.result.result_digest,
        }

    @staticmethod
    def _report_media_type(experiment: SavedResearchExperiment) -> str:
        if experiment.report.report_format == "json":
            return "application/json"
        return "text/html; charset=utf-8"

    def _verified_experiment_from_row(
        self,
        row: RowMapping,
    ) -> SavedResearchExperiment:
        request_payload = _decode_canonical_object(row["request_json"], field="request_json")
        result_payload = _decode_canonical_object(row["result_json"], field="result_json")
        comparison_value = row["comparison_json"]
        comparison_payload = (
            _decode_canonical_object(comparison_value, field="comparison_json")
            if comparison_value is not None
            else None
        )
        report_payload = _decode_canonical_object(row["report_json"], field="report_json")
        outer = {
            "schema_version": row["schema_version"],
            "experiment_id": row["experiment_id"],
            "name": row["name"],
            "note": row["note"],
            "created_at": row["created_at"],
            "request": request_payload,
            "result": result_payload,
            "comparison": comparison_payload,
            "report": report_payload,
            "experiment_digest": row["experiment_digest"],
        }
        try:
            experiment = SavedResearchExperiment.model_validate_json(canonical_json_bytes(outer))
        except (FormatError, ValidationError) as exc:
            raise ResearchStorageIntegrityError("persisted experiment contract rejected") from exc
        pins = experiment.request.pins
        redundant = {
            "query_id": str(experiment.request.query_id),
            "result_id": str(experiment.result.result_id),
            "dataset_version": pins.dataset_version,
            "dataset_manifest_digest": pins.dataset_manifest_digest,
            "matrix_version": pins.matrix_version,
            "matrix_digest": pins.matrix_digest,
            "index_version": pins.index_version,
            "index_manifest_digest": pins.index_manifest_digest,
        }
        if any(str(row[key]) != value for key, value in redundant.items()):
            raise ResearchStorageIntegrityError("persisted experiment pins or ids drifted")
        expected_parameters = self._experiment_parameters(experiment)
        for key in (
            "request_json",
            "result_json",
            "comparison_json",
            "report_json",
            "report_digest",
            "report_relative_path",
            "created_at",
        ):
            if row[key] != expected_parameters[key]:
                raise ResearchStorageIntegrityError(f"persisted experiment {key} drifted")
        self._validate_submitted_report(
            experiment,
            self._read_report(experiment.report.report_relative_path),
        )
        return experiment

    def _read_report(self, relative_path: str) -> bytes:
        try:
            return self._storage.read_bytes(RESEARCH_REPORT_ROOT_NAME, relative_path)
        except (StorageError, OSError) as exc:
            raise ResearchStorageIntegrityError("research report is missing or unreadable") from exc

    def _verify_report(
        self,
        experiment: SavedResearchExperiment,
        *,
        expected_bytes: bytes | None = None,
    ) -> bytes:
        payload = self._read_report(experiment.report.report_relative_path)
        self._validate_submitted_report(experiment, payload)
        if expected_bytes is not None and payload != expected_bytes:
            raise ResearchStorageIntegrityError("research report bytes differ from submitted bytes")
        return payload

    @staticmethod
    def _receipt_from_row(row: RowMapping) -> ResearchReplayReceipt:
        payload = _decode_canonical_object(row["receipt_json"], field="receipt_json")
        try:
            receipt = ResearchReplayReceipt.model_validate_json(canonical_json_bytes(payload))
        except (FormatError, ValidationError) as exc:
            raise ResearchStorageIntegrityError("persisted replay receipt rejected") from exc
        expected_id = research_replay_receipt_id(receipt)
        replayed_at = receipt.model_dump(mode="json")["replayed_at"]
        redundant = {
            "replay_receipt_id": str(receipt.replay_receipt_id),
            "experiment_id": str(receipt.experiment_id),
            "replayed_at": replayed_at,
            "reproduced": int(receipt.status is ResearchReplayStatus.REPRODUCED),
            "original_result_digest": receipt.original_result_digest,
            "replay_result_digest": receipt.replay_result_digest,
        }
        if receipt.replay_receipt_id != expected_id:
            raise ResearchStorageIntegrityError("persisted replay receipt id is not deterministic")
        if any(row[key] != value for key, value in redundant.items()):
            raise ResearchStorageIntegrityError("persisted replay receipt columns drifted")
        if row["receipt_json"] != _canonical_contract_text(receipt):
            raise ResearchStorageIntegrityError("persisted replay receipt JSON drifted")
        return receipt

    @staticmethod
    def _verify_receipt_against_experiment(
        receipt: ResearchReplayReceipt,
        experiment: SavedResearchExperiment,
    ) -> None:
        if receipt.experiment_id != experiment.experiment_id:
            raise ResearchStorageIntegrityError("replay receipt experiment id drifted")
        if receipt.replay_receipt_id != research_replay_receipt_id(receipt):
            raise ResearchStorageIntegrityError("replay receipt id is not deterministic")
        if receipt.saved_experiment_digest != experiment.experiment_digest:
            raise ResearchStorageIntegrityError(
                "replay receipt saved experiment digest differs from experiment"
            )
        if receipt.saved_query_digest != experiment.request.query_digest:
            raise ResearchStorageIntegrityError(
                "replay receipt saved query digest differs from experiment"
            )
        if receipt.saved_pins != experiment.request.pins:
            raise ResearchStorageIntegrityError("replay receipt saved pins differ from experiment")
        if receipt.original_result_id != experiment.result.result_id:
            raise ResearchStorageIntegrityError(
                "replay receipt original result id differs from experiment"
            )
        if receipt.original_result_digest != experiment.result.result_digest:
            raise ResearchStorageIntegrityError(
                "replay receipt original result differs from experiment"
            )

    def _resolve_experiment_insert_race(
        self,
        experiment: SavedResearchExperiment,
        report_bytes: bytes,
        error: IntegrityError,
    ) -> SavedResearchExperiment:
        try:
            existing = self.load_experiment(experiment.experiment_id)
        except ResearchExperimentNotFoundError:
            raise ResearchStorageConflictError(
                "research experiment immutable uniqueness conflict"
            ) from error
        if existing != experiment:
            raise ResearchStorageConflictError(
                "experiment id already binds different immutable state"
            ) from error
        self._verify_report(existing, expected_bytes=report_bytes)
        return existing

    def _resolve_receipt_insert_race(
        self,
        receipt: ResearchReplayReceipt,
        receipt_id: UUID,
        error: IntegrityError,
    ) -> UUID:
        try:
            receipts = self.list_replay_receipts(receipt.experiment_id)
        except ResearchExperimentNotFoundError:
            raise ResearchStorageConflictError("replay receipt parent disappeared") from error
        if any(
            research_replay_receipt_id(existing) == receipt_id and existing == receipt
            for existing in receipts
        ):
            return receipt_id
        raise ResearchStorageConflictError(
            "replay receipt immutable uniqueness conflict"
        ) from error


__all__ = [
    "RESEARCH_REPORT_ROOT_NAME",
    "ResearchExperimentNotFoundError",
    "ResearchExperimentStore",
    "ResearchStorageConfigurationError",
    "ResearchStorageConflictError",
    "ResearchStorageError",
    "ResearchStorageIntegrityError",
    "research_replay_receipt_id",
    "research_report_relative_path",
]
