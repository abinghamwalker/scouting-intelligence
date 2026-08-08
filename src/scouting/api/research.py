"""Strict local FastAPI boundary for the governed W09 research workbench."""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import OrderedDict
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta
from threading import RLock
from typing import Annotated, Any, Literal, NoReturn
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request, Response, status
from pydantic import Field, ValidationError, model_validator

from scouting.contracts.primitives import (
    CanonicalPlayerId,
    ContractModel,
    NonEmptyString,
    StrictUuid,
    UtcInstant,
)
from scouting.contracts.research import (
    FeatureMatrixRow,
    MinuteEvidenceState,
    ResearchCapability,
    ResearchComparison,
    ResearchComparisonRequest,
    ResearchDatasetDescriptor,
    ResearchQueryMode,
    ResearchQueryRequest,
    ResearchQueryResult,
    ResearchReplayReason,
    ResearchReplayReceipt,
    ResearchReplayStatus,
    ResearchVersionPins,
    SavedResearchExperiment,
    SavedResearchExperimentSummary,
    canonical_research_digest,
)
from scouting.contracts.validation import revalidate_exact_contract
from scouting.reporting.research import ResearchReportInputError, render_research_report
from scouting.serving.research import (
    ResearchServingConflictError,
    ResearchServingError,
    ResearchServingService,
)
from scouting.storage.research import (
    ResearchExperimentNotFoundError,
    ResearchExperimentStore,
    ResearchStorageConflictError,
    ResearchStorageError,
    ResearchStorageIntegrityError,
    research_replay_receipt_id,
)

_API_PREFIX = "/api/w09"
_AUTHORITY_CACHE_LIMIT = 128
_MAX_UNICODE = chr(0x10FFFF)


class ResearchApiError(RuntimeError):
    """Base error for a closed W09 API boundary."""


class ResearchApiInputError(ResearchApiError, ValueError):
    """A locally valid wire value cannot be served by this research boundary."""


class ResearchApiNotFoundError(ResearchApiError, LookupError):
    """A requested immutable in-process authority is absent."""


class ResearchApiConflictError(ResearchApiError):
    """A request conflicts with immutable or version-pinned research state."""


class SaveResearchExperimentRequest(ContractModel):
    """Exact cached authorities to bind into one immutable saved experiment."""

    experiment_id: StrictUuid
    name: NonEmptyString
    note: NonEmptyString | None = None
    result_id: StrictUuid
    result_digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    comparison_id: StrictUuid | None = None
    comparison_digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")] | None = None
    report_format: Literal["json", "html"] = "json"

    @model_validator(mode="after")
    def comparison_reference_is_complete(self) -> SaveResearchExperimentRequest:
        if (self.comparison_id is None) != (self.comparison_digest is None):
            raise ValueError("comparison id and digest must be supplied together")
        return self


class ResearchPlayerSummary(ContractModel):
    """A searchable real-player row from the exact governed feature matrix."""

    grain_id: NonEmptyString
    player_id: CanonicalPlayerId
    display_name: NonEmptyString
    competition_id: StrictUuid
    competition_name: NonEmptyString
    season_id: NonEmptyString
    position_code: Literal["GK", "DF", "MD", "FW"]
    team_ids: tuple[StrictUuid, ...]
    team_names: tuple[NonEmptyString, ...]
    minutes: Annotated[float, Field(strict=True, gt=0.0, allow_inf_nan=False)]
    minute_state: Literal[
        MinuteEvidenceState.EXACT,
        MinuteEvidenceState.CONSERVATIVE_LOWER_BOUND,
    ]
    feature_cutoff_ts: UtcInstant
    contains_synthetic_data: Literal[False] = False


class ResearchPlayerSearchResponse(ContractModel):
    """Bounded deterministic page over the exact governed matrix population."""

    dataset_version: NonEmptyString
    matrix_version: NonEmptyString
    matrix_digest: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    name: NonEmptyString | None
    position_code: Literal["GK", "DF", "MD", "FW"] | None
    competition_id: StrictUuid | None
    offset: Annotated[int, Field(strict=True, ge=0)]
    limit: Annotated[int, Field(strict=True, ge=1, le=100)]
    total_matches: Annotated[int, Field(strict=True, ge=0)]
    players: tuple[ResearchPlayerSummary, ...]
    contains_synthetic_rows: Literal[False] = False

    @model_validator(mode="after")
    def page_is_bounded(self) -> ResearchPlayerSearchResponse:
        if len(self.players) > self.limit:
            raise ValueError("player search response exceeds its declared limit")
        if self.offset > self.total_matches and self.players:
            raise ValueError("player page cannot contain rows after the result set")
        return self


def _fresh_model[T: ContractModel](value: T, model: type[T], *, label: str) -> T:
    return revalidate_exact_contract(
        value,
        model,
        label=label,
        error_type=ResearchApiConflictError,
    )


def _strict_text(value: object, *, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be exact text")
    if not value or value != value.strip() or len(value) > 512:
        raise ResearchApiInputError(f"{label} must be trimmed non-empty text")
    return value


class ResearchApiRuntime:
    """Dependency-injected local authority for one exact W09 research dataset."""

    __slots__ = (
        "_attribution",
        "_clock",
        "_comparisons",
        "_dataset",
        "_lock",
        "_matrix_rows",
        "_name_suffix_index",
        "_results",
        "_rights_limitations",
        "_serving",
        "_store",
    )

    def __init__(
        self,
        *,
        dataset: ResearchDatasetDescriptor,
        serving: ResearchServingService,
        store: ResearchExperimentStore,
        retained_attribution: str,
        rights_limitations: tuple[str, ...],
        utc_clock: Callable[[], datetime],
    ) -> None:
        validated_dataset = _fresh_model(
            dataset,
            ResearchDatasetDescriptor,
            label="dataset descriptor",
        )
        if type(serving) is not ResearchServingService:
            raise TypeError("serving must be an exact ResearchServingService")
        if type(store) is not ResearchExperimentStore:
            raise TypeError("store must be an exact ResearchExperimentStore")
        if not callable(utc_clock):
            raise TypeError("utc_clock must be callable")
        attribution = _strict_text(retained_attribution, label="retained_attribution")
        if attribution != validated_dataset.attribution:
            raise ResearchApiConflictError(
                "retained attribution must equal the governed dataset attribution"
            )
        if type(rights_limitations) is not tuple or not rights_limitations:
            raise TypeError("rights_limitations must be a non-empty exact tuple")
        limitations = tuple(
            _strict_text(item, label=f"rights_limitations[{index}]")
            for index, item in enumerate(rights_limitations)
        )
        if len(limitations) != len(set(limitations)):
            raise ResearchApiInputError("rights limitations must be unique")

        pins = serving.pins
        matrix = serving.matrix_manifest
        dataset_binding = (
            validated_dataset.dataset_version,
            validated_dataset.dataset_manifest_digest,
            validated_dataset.identity_bundle_digest,
            validated_dataset.feature_cutoff_ts,
            validated_dataset.window_start_utc,
            validated_dataset.window_end_utc,
        )
        serving_binding = (
            pins.dataset_version,
            pins.dataset_manifest_digest,
            pins.identity_bundle_digest,
            pins.feature_cutoff_ts,
            matrix.window_start_utc,
            matrix.window_end_utc,
        )
        if dataset_binding != serving_binding:
            raise ResearchApiConflictError(
                "dataset descriptor is stale or incompatible with the serving authority"
            )
        rows = serving.matrix_rows
        if type(rows) is not tuple or any(type(row) is not FeatureMatrixRow for row in rows):
            raise TypeError("serving matrix_rows must contain exact FeatureMatrixRow contracts")
        if not rows or any(row.contains_synthetic_data for row in rows):
            raise ResearchApiConflictError(
                "player search requires a non-empty governed matrix with no synthetic rows"
            )

        self._dataset = validated_dataset
        self._serving = serving
        self._store = store
        self._attribution = attribution
        self._rights_limitations = limitations
        self._clock = utc_clock
        self._matrix_rows = tuple(
            sorted(
                rows,
                key=lambda row: (
                    row.display_name.casefold(),
                    row.player_id.bytes,
                    row.competition_id.bytes,
                    row.grain_id,
                ),
            )
        )
        self._name_suffix_index = tuple(
            sorted(
                (folded[start:], index)
                for index, row in enumerate(self._matrix_rows)
                for folded in (row.display_name.casefold(),)
                for start in range(len(folded))
            )
        )
        self._lock = RLock()
        self._results: OrderedDict[UUID, ResearchQueryResult] = OrderedDict()
        self._comparisons: OrderedDict[UUID, ResearchComparison] = OrderedDict()

    @property
    def dataset(self) -> ResearchDatasetDescriptor:
        return self._dataset

    def list_datasets(self) -> tuple[ResearchDatasetDescriptor, ...]:
        return (self._dataset,)

    def search_players(
        self,
        *,
        name: str | None,
        position_code: Literal["GK", "DF", "MD", "FW"] | None,
        competition_id: UUID | None,
        offset: int,
        limit: int,
    ) -> ResearchPlayerSearchResponse:
        if type(offset) is not int or isinstance(offset, bool) or offset < 0:
            raise ResearchApiInputError("offset must be a non-negative integer")
        if type(limit) is not int or isinstance(limit, bool) or not 1 <= limit <= 100:
            raise ResearchApiInputError("limit must be between 1 and 100")
        if competition_id is not None and type(competition_id) is not UUID:
            raise ResearchApiInputError("competition_id must be an exact UUID")
        normalized_name: str | None = None
        if name is not None:
            normalized_name = _strict_text(name, label="name")
            if len(normalized_name) > 100:
                raise ResearchApiInputError("name must be at most 100 characters")
        folded = normalized_name.casefold() if normalized_name is not None else None
        candidate_indices: Sequence[int]
        if folded is None:
            candidate_indices = range(len(self._matrix_rows))
        else:
            lower = bisect_left(self._name_suffix_index, (folded, -1))
            upper = bisect_right(
                self._name_suffix_index,
                (folded + _MAX_UNICODE, len(self._matrix_rows)),
            )
            candidate_indices = sorted({index for _, index in self._name_suffix_index[lower:upper]})
        selected = tuple(
            self._matrix_rows[index]
            for index in candidate_indices
            if (position_code is None or self._matrix_rows[index].position_code == position_code)
            and (
                competition_id is None or self._matrix_rows[index].competition_id == competition_id
            )
        )
        page = selected[offset : offset + limit]
        return ResearchPlayerSearchResponse(
            dataset_version=self._dataset.dataset_version,
            matrix_version=self._serving.pins.matrix_version,
            matrix_digest=self._serving.pins.matrix_digest,
            name=normalized_name,
            position_code=position_code,
            competition_id=competition_id,
            offset=offset,
            limit=limit,
            total_matches=len(selected),
            players=tuple(self._player_summary(row) for row in page),
        )

    def execute_query(self, request: ResearchQueryRequest) -> ResearchQueryResult:
        validated = _fresh_model(request, ResearchQueryRequest, label="research query")
        required_capability = {
            ResearchQueryMode.EXEMPLAR: ResearchCapability.EXEMPLAR_QUERY,
            ResearchQueryMode.WEIGHTED_PROFILE: ResearchCapability.WEIGHTED_PROFILE_QUERY,
        }[validated.mode]
        if required_capability not in self._dataset.capabilities:
            raise ResearchApiConflictError("query mode is not declared by the governed dataset")
        generated_at = self._now(not_before=validated.requested_at)
        result = self._serving.execute_query(validated, generated_at=generated_at)
        fresh = _fresh_model(result, ResearchQueryResult, label="research result")
        with self._lock:
            existing = self._results.get(fresh.result_id)
            if existing is not None:
                if existing.result_digest != fresh.result_digest:
                    raise ResearchApiConflictError(
                        "result id already binds different immutable cached state"
                    )
                self._results.move_to_end(fresh.result_id)
                return existing
            self._results[fresh.result_id] = fresh
            if len(self._results) > _AUTHORITY_CACHE_LIMIT:
                evicted_result_id, _ = self._results.popitem(last=False)
                stale_comparison_ids = tuple(
                    comparison_id
                    for comparison_id, comparison in self._comparisons.items()
                    if comparison.request.result_id == evicted_result_id
                )
                for comparison_id in stale_comparison_ids:
                    del self._comparisons[comparison_id]
        return fresh

    def load_result(self, result_id: UUID) -> ResearchQueryResult:
        with self._lock:
            result = self._results.get(result_id)
            if result is not None:
                self._results.move_to_end(result_id)
        if result is None:
            raise ResearchApiNotFoundError(f"research result not found: {result_id}")
        return _fresh_model(result, ResearchQueryResult, label="cached research result")

    def compare(self, request: ResearchComparisonRequest) -> ResearchComparison:
        validated = _fresh_model(
            request,
            ResearchComparisonRequest,
            label="research comparison request",
        )
        result = self.load_result(validated.result_id)
        comparison = self._serving.compare(validated, result)
        fresh = _fresh_model(
            comparison,
            ResearchComparison,
            label="research comparison",
        )
        comparison_id = fresh.request.comparison_id
        with self._lock:
            existing = self._comparisons.get(comparison_id)
            if existing is not None and existing != fresh:
                raise ResearchApiConflictError(
                    "comparison id already binds different immutable cached state"
                )
            self._comparisons[comparison_id] = fresh
            self._comparisons.move_to_end(comparison_id)
            if len(self._comparisons) > _AUTHORITY_CACHE_LIMIT:
                self._comparisons.popitem(last=False)
        return fresh

    def save_experiment(
        self,
        request: SaveResearchExperimentRequest,
    ) -> SavedResearchExperiment:
        validated = _fresh_model(
            request,
            SaveResearchExperimentRequest,
            label="save experiment request",
        )
        with self._lock:
            result = self._results.get(validated.result_id)
            if result is None:
                raise ResearchApiNotFoundError(
                    f"cached research result not found: {validated.result_id}"
                )
            if result.result_digest != validated.result_digest:
                raise ResearchApiConflictError("cached result digest does not match save request")
            comparison = self._resolve_save_comparison(validated, result)
            self._results.move_to_end(validated.result_id)
            if comparison is not None:
                self._comparisons.move_to_end(comparison.request.comparison_id)
        existing = self._existing_experiment(validated, result, comparison)
        if existing is not None:
            return existing
        generated_at = self._now(not_before=result.generated_at)
        rendered = render_research_report(
            result,
            comparison=comparison,
            report_format=validated.report_format,
            generated_at=generated_at,
            rights_classification=self._dataset.rights_classification,
            attribution=self._attribution,
            rights_limitations=self._rights_limitations,
        )
        draft = SavedResearchExperiment.model_construct(
            experiment_id=validated.experiment_id,
            name=validated.name,
            note=validated.note,
            created_at=generated_at,
            request=result.request,
            result=result,
            comparison=comparison,
            report=rendered.descriptor,
            experiment_digest="0" * 64,
        )
        experiment = SavedResearchExperiment(
            experiment_id=draft.experiment_id,
            name=draft.name,
            note=draft.note,
            created_at=draft.created_at,
            request=draft.request,
            result=draft.result,
            comparison=draft.comparison,
            report=draft.report,
            experiment_digest=canonical_research_digest(
                draft.model_dump(mode="json", exclude={"experiment_digest"})
            ),
        )
        saved = self._store.save_experiment(experiment, rendered.payload)
        return _fresh_model(saved, SavedResearchExperiment, label="saved experiment")

    def load_experiment(self, experiment_id: UUID) -> SavedResearchExperiment:
        return _fresh_model(
            self._store.load_experiment(experiment_id),
            SavedResearchExperiment,
            label="loaded experiment",
        )

    def list_experiments(self) -> tuple[SavedResearchExperimentSummary, ...]:
        return tuple(
            _fresh_model(item, SavedResearchExperimentSummary, label=f"experiments[{index}]")
            for index, item in enumerate(self._store.list_experiments())
        )

    def load_report(self, experiment_id: UUID) -> tuple[bytes, str]:
        experiment = self.load_experiment(experiment_id)
        payload = self._store.load_report_bytes(experiment_id)
        media_type = (
            "application/json"
            if experiment.report.report_format == "json"
            else "text/html; charset=utf-8"
        )
        return payload, media_type

    def replay_experiment(self, experiment_id: UUID) -> ResearchReplayReceipt:
        experiment = self.load_experiment(experiment_id)
        loaded_pins = _fresh_model(
            self._serving.pins,
            ResearchVersionPins,
            label="loaded research pins",
        )
        replayed_at = self._now(not_before=experiment.created_at)
        if experiment.request.pins != loaded_pins:
            status_value = ResearchReplayStatus.INCOMPATIBLE_PINS
            reason = ResearchReplayReason.SAVED_ARTIFACTS_UNAVAILABLE_OR_REPLACED
            replay_result_id = experiment.result.result_id
            replay_result_digest = experiment.result.result_digest
        else:
            replay = self._serving.execute_query(
                experiment.request,
                generated_at=replayed_at,
            )
            replay = _fresh_model(
                replay,
                ResearchQueryResult,
                label="replayed research result",
            )
            replay_result_id = replay.result_id
            replay_result_digest = replay.result_digest
            reproduced = (
                replay_result_id == experiment.result.result_id
                and replay_result_digest == experiment.result.result_digest
            )
            status_value = (
                ResearchReplayStatus.REPRODUCED
                if reproduced
                else ResearchReplayStatus.RESULT_MISMATCH
            )
            reason = (
                ResearchReplayReason.EXACT_REPRODUCTION
                if reproduced
                else ResearchReplayReason.DETERMINISTIC_RESULT_MISMATCH
            )
        receipt = self._replay_receipt(
            experiment=experiment,
            replayed_at=replayed_at,
            loaded_pins=loaded_pins,
            replay_result_id=replay_result_id,
            replay_result_digest=replay_result_digest,
            status_value=status_value,
            reason=reason,
        )
        for existing in self._store.list_replay_receipts(experiment_id):
            if existing.replay_receipt_id == receipt.replay_receipt_id:
                if existing.receipt_digest != receipt.receipt_digest:
                    raise ResearchApiConflictError(
                        "deterministic replay receipt id conflicts with saved evidence"
                    )
                return _fresh_model(
                    existing,
                    ResearchReplayReceipt,
                    label="saved replay receipt",
                )
        self._store.append_replay_receipt(receipt)
        return _fresh_model(receipt, ResearchReplayReceipt, label="replay receipt")

    def _resolve_save_comparison(
        self,
        request: SaveResearchExperimentRequest,
        result: ResearchQueryResult,
    ) -> ResearchComparison | None:
        if request.comparison_id is None:
            return None
        comparison = self._comparisons.get(request.comparison_id)
        if comparison is None:
            raise ResearchApiNotFoundError(f"cached comparison not found: {request.comparison_id}")
        if comparison.comparison_digest != request.comparison_digest:
            raise ResearchApiConflictError("cached comparison digest does not match save request")
        if (
            comparison.request.result_id != result.result_id
            or comparison.request.result_digest != result.result_digest
        ):
            raise ResearchApiConflictError("cached comparison is not bound to the saved result")
        return comparison

    def _existing_experiment(
        self,
        request: SaveResearchExperimentRequest,
        result: ResearchQueryResult,
        comparison: ResearchComparison | None,
    ) -> SavedResearchExperiment | None:
        try:
            existing = self.load_experiment(request.experiment_id)
        except ResearchExperimentNotFoundError:
            return None
        if (
            existing.name != request.name
            or existing.note != request.note
            or existing.result != result
            or existing.comparison != comparison
            or existing.report.report_format != request.report_format
        ):
            raise ResearchApiConflictError(
                "experiment id already binds different immutable saved state"
            )
        return existing

    @staticmethod
    def _player_summary(row: FeatureMatrixRow) -> ResearchPlayerSummary:
        return ResearchPlayerSummary(
            grain_id=row.grain_id,
            player_id=row.player_id,
            display_name=row.display_name,
            competition_id=row.competition_id,
            competition_name=row.competition_name,
            season_id=row.season_id,
            position_code=row.position_code,
            team_ids=row.team_ids,
            team_names=row.team_names,
            minutes=row.minutes,
            minute_state=row.minute_state,
            feature_cutoff_ts=row.feature_cutoff_ts,
        )

    @staticmethod
    def _replay_receipt(
        *,
        experiment: SavedResearchExperiment,
        replayed_at: datetime,
        loaded_pins: ResearchVersionPins,
        replay_result_id: UUID,
        replay_result_digest: str,
        status_value: ResearchReplayStatus,
        reason: ResearchReplayReason,
    ) -> ResearchReplayReceipt:
        if type(loaded_pins) is not ResearchVersionPins:
            raise TypeError("loaded_pins must be an exact ResearchVersionPins")
        common: dict[str, Any] = {
            "experiment_id": experiment.experiment_id,
            "saved_experiment_digest": experiment.experiment_digest,
            "saved_query_digest": experiment.request.query_digest,
            "replay_query_digest": experiment.request.query_digest,
            "replayed_at": replayed_at,
            "saved_pins": experiment.request.pins,
            "loaded_pins": loaded_pins,
            "original_result_id": experiment.result.result_id,
            "replay_result_id": replay_result_id,
            "original_result_digest": experiment.result.result_digest,
            "replay_result_digest": replay_result_digest,
            "status": status_value,
            "reason": reason,
        }
        identity_draft = ResearchReplayReceipt.model_construct(
            replay_receipt_id=UUID(int=0),
            receipt_digest="0" * 64,
            **common,
        )
        receipt_id = research_replay_receipt_id(identity_draft)
        digest_draft = ResearchReplayReceipt.model_construct(
            replay_receipt_id=receipt_id,
            receipt_digest="0" * 64,
            **common,
        )
        return ResearchReplayReceipt(
            replay_receipt_id=receipt_id,
            receipt_digest=canonical_research_digest(digest_draft.digest_projection()),
            **common,
        )

    def _now(self, *, not_before: datetime) -> datetime:
        value = self._clock()
        if type(value) is not datetime:
            raise ResearchApiConflictError("UTC clock returned a non-datetime value")
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ResearchApiConflictError("UTC clock must return timezone-aware UTC")
        if value < not_before:
            raise ResearchApiInputError("request time is after the injected UTC clock")
        return value


def _raise_http_error(exc: Exception) -> NoReturn:
    if isinstance(exc, (ResearchApiNotFoundError, ResearchExperimentNotFoundError)):
        code = status.HTTP_404_NOT_FOUND
        detail = "research_not_found"
    elif isinstance(
        exc,
        (
            ResearchApiConflictError,
            ResearchServingConflictError,
            ResearchStorageConflictError,
            ResearchStorageIntegrityError,
        ),
    ):
        code = status.HTTP_409_CONFLICT
        detail = "research_conflict"
    elif isinstance(exc, ResearchStorageError):
        code = status.HTTP_409_CONFLICT
        detail = "research_storage_conflict"
    elif isinstance(
        exc,
        (
            ResearchApiInputError,
            ResearchReportInputError,
            ResearchServingError,
            TypeError,
            ValidationError,
        ),
    ):
        code = status.HTTP_422_UNPROCESSABLE_CONTENT
        detail = "research_request_rejected"
    else:
        raise exc
    raise HTTPException(status_code=code, detail=detail) from exc


async def _strict_json_body[T: ContractModel](request: Request, model: type[T]) -> T:
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().casefold()
    if content_type != "application/json":
        raise ResearchApiInputError("request content type must be application/json")
    payload = await request.body()
    if not payload:
        raise ResearchApiInputError("request body must contain one JSON object")
    try:
        return model.model_validate_json(payload)
    except ValidationError as exc:
        raise ResearchApiInputError(f"{model.__name__} request body rejected: {exc}") from exc


def create_research_router(runtime: ResearchApiRuntime) -> APIRouter:
    """Create an isolated router; production app construction remains out of scope."""

    if type(runtime) is not ResearchApiRuntime:
        raise TypeError("runtime must be an exact ResearchApiRuntime")
    router = APIRouter(prefix=_API_PREFIX, tags=["w09-research"])

    @router.get("/datasets", response_model=tuple[ResearchDatasetDescriptor, ...])
    def list_datasets() -> tuple[ResearchDatasetDescriptor, ...]:
        return runtime.list_datasets()

    @router.get("/players", response_model=ResearchPlayerSearchResponse)
    def search_players(
        name: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
        position: Literal["GK", "DF", "MD", "FW"] | None = None,
        competition_id: UUID | None = None,
        offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> ResearchPlayerSearchResponse:
        try:
            return runtime.search_players(
                name=name,
                position_code=position,
                competition_id=competition_id,
                offset=offset,
                limit=limit,
            )
        except Exception as exc:
            _raise_http_error(exc)

    @router.post("/queries", response_model=ResearchQueryResult)
    async def execute_query(request: Request) -> ResearchQueryResult:
        try:
            return runtime.execute_query(await _strict_json_body(request, ResearchQueryRequest))
        except Exception as exc:
            _raise_http_error(exc)

    @router.get("/results/{result_id}", response_model=ResearchQueryResult)
    def load_result(result_id: UUID) -> ResearchQueryResult:
        try:
            return runtime.load_result(result_id)
        except Exception as exc:
            _raise_http_error(exc)

    @router.post("/comparisons", response_model=ResearchComparison)
    async def compare(request: Request) -> ResearchComparison:
        try:
            return runtime.compare(await _strict_json_body(request, ResearchComparisonRequest))
        except Exception as exc:
            _raise_http_error(exc)

    @router.post("/experiments", response_model=SavedResearchExperiment)
    async def save_experiment(request: Request) -> SavedResearchExperiment:
        try:
            return runtime.save_experiment(
                await _strict_json_body(request, SaveResearchExperimentRequest)
            )
        except Exception as exc:
            _raise_http_error(exc)

    @router.get("/experiments", response_model=tuple[SavedResearchExperimentSummary, ...])
    def list_experiments() -> tuple[SavedResearchExperimentSummary, ...]:
        try:
            return runtime.list_experiments()
        except Exception as exc:
            _raise_http_error(exc)

    @router.get("/experiments/{experiment_id}", response_model=SavedResearchExperiment)
    def load_experiment(experiment_id: UUID) -> SavedResearchExperiment:
        try:
            return runtime.load_experiment(experiment_id)
        except Exception as exc:
            _raise_http_error(exc)

    @router.post(
        "/experiments/{experiment_id}/replay",
        response_model=ResearchReplayReceipt,
    )
    def replay_experiment(experiment_id: UUID) -> ResearchReplayReceipt:
        try:
            return runtime.replay_experiment(experiment_id)
        except Exception as exc:
            _raise_http_error(exc)

    @router.get("/experiments/{experiment_id}/report", response_class=Response)
    def load_report(experiment_id: UUID) -> Response:
        try:
            payload, media_type = runtime.load_report(experiment_id)
            return Response(content=payload, media_type=media_type)
        except Exception as exc:
            _raise_http_error(exc)

    return router


__all__ = [
    "ResearchApiConflictError",
    "ResearchApiError",
    "ResearchApiInputError",
    "ResearchApiNotFoundError",
    "ResearchApiRuntime",
    "ResearchPlayerSearchResponse",
    "ResearchPlayerSummary",
    "SaveResearchExperimentRequest",
    "create_research_router",
]
