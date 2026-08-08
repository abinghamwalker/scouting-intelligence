"""Fail-closed local persistence for the blinded W10 expert study."""
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import sqlite3
import stat
import tempfile
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, cast
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import TypeAdapter, ValidationError

from scouting.contracts.expert_relevance import (
    AssessmentBasisV2,
    CandidateEvidenceJudgementV2,
    CandidateJudgement,
    CandidatePresentation,
    CompletionReceipt,
    ConsentRecord,
    EvidenceGapV2,
    EvidenceSufficiencyV2,
    ExpertExperienceKind,
    ExpertRelevanceProtocol,
    ExpertStudyPresentationBundle,
    FormalStudySubmission,
    HistoricalComparisonJudgementV1,
    HistoricalComparisonPilotDebriefV1,
    JudgementState,
    ParticipantEligibility,
    ParticipantEvidenceComparisonV2,
    PresentationKind,
    PresentedCandidate,
    PresentedExpertQuery,
    ProtocolApproval,
    QualitativeFailureCategory,
    StudyMode,
    StudySession,
    build_formal_candidate_presentations,
    participant_code_digest,
    participant_keyed_candidate_order,
    validate_response_comparison_v2,
)
from scouting.contracts.research import canonical_research_digest
from scouting.storage.formats import FormatError, canonical_json_bytes

PROTOCOL_APPROVAL_CONFIRMATION = (
    "I approve this exact protocol and frozen query pack for formal G-RW4 participation."
)
FROZEN_PROTOCOL_DIGEST = "7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f"
FROZEN_QUERY_PACK_DIGEST = "cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5"
FROZEN_PRESENTATION_DIGEST = "4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96"

_PARTICIPANT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:expert-study-participant:v1",
)
_SESSION_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:expert-study-session:v1",
)
_PRESENTATION_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:expert-study-presentation:v1",
)
_JUDGEMENT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:expert-study-judgement:v1",
)
_APPROVAL_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:protocol-approval:v1",
)
_SUBMISSION_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:formal-study-submission:v1",
)
_RECEIPT_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w10:formal-study-receipt:v1",
)
_CAPABILITY = re.compile(r"^[A-Za-z0-9_-]{32,128}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")

type CompletionResult = CompletionReceipt | Mapping[str, object]

_JSON_OBJECT_ADAPTER = TypeAdapter(dict[str, object])


class ExpertStudyStorageError(RuntimeError):
    """Base class for W10 study persistence failures."""


class ExpertStudyConfigurationError(ExpertStudyStorageError):
    """The database, capture root or injected authority is unsafe."""


class ExpertStudyConflictError(ExpertStudyStorageError):
    """An immutable identity, command or expected revision conflicts."""


class ExpertStudyIntegrityError(ExpertStudyStorageError):
    """Persisted state or immutable bytes failed exact verification."""


class ExpertStudyPreparationError(ExpertStudyStorageError):
    """Eligibility, consent or formal approval does not permit a session."""


class ExpertStudyNotFoundError(ExpertStudyStorageError, LookupError):
    """No session is bound to the supplied opaque browser capability."""


@dataclass(frozen=True, slots=True)
class PreparedStudySession:
    """New session plus the sole raw browser capability returned by preparation."""

    capability: str
    snapshot: StudySessionSnapshot


@dataclass(frozen=True, slots=True)
class StudySessionSnapshot:
    """Verified server-authoritative state for one browser session."""

    session: StudySession
    eligibility: ParticipantEligibility
    consent: ConsentRecord
    judgements: tuple[CandidateJudgement, ...]
    revision: int
    completion: CompletionResult | None

    @property
    def answered_count(self) -> int:
        return len(self.judgements)

    @property
    def total_count(self) -> int:
        return len(self.session.presentations)

    @property
    def complete(self) -> bool:
        return self.completion is not None


@dataclass(frozen=True, slots=True)
class StudyTask:
    """Participant-safe task projection for one frozen presentation."""

    presentation: CandidatePresentation
    query: PresentedExpertQuery
    candidate: PresentedCandidate
    ordinal: int
    total: int


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _canonical_text(value: object) -> str:
    try:
        return canonical_json_bytes(value).decode("utf-8", errors="strict")
    except (FormatError, UnicodeError) as exc:
        raise ExpertStudyIntegrityError("study state is not canonical JSON") from exc


def _contract_text(value: object) -> str:
    model_dump = getattr(value, "model_dump", None)
    if not callable(model_dump):
        raise TypeError("study contract must expose model_dump")
    return _canonical_text(model_dump(mode="json"))


def _validated_from_text[T](model: type[T], value: object, *, field: str) -> T:
    if type(value) is not str:
        raise ExpertStudyIntegrityError(f"persisted {field} must be exact text")
    try:
        parsed = model.model_validate_json(value)  # type: ignore[attr-defined]
    except (AttributeError, ValidationError) as exc:
        raise ExpertStudyIntegrityError(f"persisted {field} contract rejected") from exc
    if _contract_text(parsed) != value:
        raise ExpertStudyIntegrityError(f"persisted {field} is not canonical")
    return cast(T, parsed)


def _digest_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _hash_order(key: str, value: UUID | int) -> bytes:
    return hashlib.sha256(f"{key}\0{value}".encode()).digest()


def _participant_identity(code: str) -> tuple[str, UUID]:
    try:
        digest = participant_code_digest(code)
    except ValueError as exc:
        raise ExpertStudyPreparationError(str(exc)) from exc
    return digest, uuid5(_PARTICIPANT_NAMESPACE, digest)


def _absolute_unresolved(path: Path) -> Path:
    return Path(os.path.abspath(path.expanduser()))


def _reject_symlink_components(path: Path, root: Path, *, field: str) -> None:
    if not path.is_relative_to(root):
        raise ExpertStudyConfigurationError(f"{field} escaped its guarded root")
    current = root
    if current.is_symlink():
        raise ExpertStudyConfigurationError(f"{field} contains a symlink component")
    for part in path.relative_to(root).parts:
        current = current / part
        if current.is_symlink():
            raise ExpertStudyConfigurationError(f"{field} contains a symlink component")


def _require_single_link_regular_file(path: Path, *, field: str) -> None:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ExpertStudyConfigurationError(f"{field} cannot be inspected safely") from exc
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise ExpertStudyConfigurationError(f"{field} must be a single-link regular file")


def _validate_command_inputs(
    capability: str,
    command_id: UUID,
    expected_revision: int,
    request_digest: str,
) -> None:
    if type(capability) is not str or _CAPABILITY.fullmatch(capability) is None:
        raise ExpertStudyNotFoundError("study session is unavailable")
    if type(command_id) is not UUID:
        raise TypeError("command_id must be an exact UUID")
    if type(expected_revision) is not int or expected_revision < 0:
        raise TypeError("expected_revision must be a non-negative exact integer")
    if type(request_digest) is not str or _SHA256.fullmatch(request_digest) is None:
        raise TypeError("request_digest must be lowercase SHA-256 hex")


def _derived_contract[T](model: type[T], payload: dict[str, object], digest_field: str) -> T:
    json_projection = _JSON_OBJECT_ADAPTER.dump_python(payload, mode="json")
    projection = dict(payload)
    projection[digest_field] = canonical_research_digest(json_projection)
    try:
        return cast(T, model.model_validate(projection))  # type: ignore[attr-defined]
    except (AttributeError, ValidationError) as exc:
        raise ExpertStudyIntegrityError(f"could not construct {model.__name__}") from exc


class ExpertStudyStore:
    """Separate SQLite authority for one pilot or formal W10 evidence lane."""

    def __init__(
        self,
        *,
        database_path: Path,
        capture_root: Path,
        allowed_root: Path,
        mode: Literal[StudyMode.MECHANICS_PILOT, StudyMode.FORMAL_G_RW4],
        protocol: ExpertRelevanceProtocol,
        presentation: ExpertStudyPresentationBundle,
        test_only: bool = False,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        if type(protocol) is not ExpertRelevanceProtocol:
            raise TypeError("protocol must be an exact ExpertRelevanceProtocol")
        if type(presentation) is not ExpertStudyPresentationBundle:
            raise TypeError("presentation must be an exact ExpertStudyPresentationBundle")
        if mode not in {StudyMode.MECHANICS_PILOT, StudyMode.FORMAL_G_RW4}:
            raise ExpertStudyConfigurationError("store mode must be pilot or formal")
        if presentation.protocol_digest != protocol.protocol_digest:
            raise ExpertStudyConfigurationError("presentation protocol digest is incompatible")
        if (
            protocol.protocol_digest != FROZEN_PROTOCOL_DIGEST
            or presentation.query_pack_digest != FROZEN_QUERY_PACK_DIGEST
            or presentation.presentation_digest != FROZEN_PRESENTATION_DIGEST
        ):
            raise ExpertStudyConfigurationError(
                "study authority is not the exact frozen W10 authority"
            )

        guard_input = _absolute_unresolved(allowed_root)
        if (
            not guard_input.is_dir()
            or guard_input.is_symlink()
            or guard_input.resolve() != guard_input
        ):
            raise ExpertStudyConfigurationError(
                "allowed root must be an existing non-symlink directory"
            )
        guard = guard_input
        database = _absolute_unresolved(database_path)
        captures = _absolute_unresolved(capture_root)
        if guard == Path(guard.anchor):
            raise ExpertStudyConfigurationError("allowed root cannot be a filesystem root")
        if not database.is_relative_to(guard) or not captures.is_relative_to(guard):
            raise ExpertStudyConfigurationError("study paths must remain inside allowed root")
        _reject_symlink_components(database, guard, field="study database path")
        _reject_symlink_components(captures, guard, field="capture root path")
        expected_name = "pilot.sqlite3" if mode is StudyMode.MECHANICS_PILOT else "formal.sqlite3"
        if database.name != expected_name:
            raise ExpertStudyConfigurationError(f"{mode.value} store requires {expected_name}")
        if database.exists():
            _require_single_link_regular_file(database, field="study database")
        if captures.exists() and (not captures.is_dir() or captures.is_symlink()):
            raise ExpertStudyConfigurationError("capture root must be a regular directory")

        self.database_path = database
        self.capture_root = captures
        self.allowed_root = guard
        self.mode = mode
        self.protocol = protocol
        self.presentation = presentation
        self.test_only = test_only
        self._clock = clock
        self._schema_lock = threading.Lock()
        self._schema_ready = False

    def _connect(self) -> sqlite3.Connection:
        self._ensure_schema()
        self._validate_storage_paths()
        connection = sqlite3.connect(
            self.database_path,
            timeout=5.0,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA synchronous = FULL")
        return connection

    def _validate_storage_paths(self) -> None:
        _reject_symlink_components(
            self.database_path,
            self.allowed_root,
            field="study database path",
        )
        _reject_symlink_components(
            self.capture_root,
            self.allowed_root,
            field="capture root path",
        )
        if self.database_path.exists():
            _require_single_link_regular_file(
                self.database_path,
                field="study database",
            )
        if self.capture_root.exists() and (
            not self.capture_root.is_dir() or self.capture_root.is_symlink()
        ):
            raise ExpertStudyConfigurationError("capture root must be a non-symlink directory")

    def _ensure_schema(self) -> None:
        if self._schema_ready:
            return
        with self._schema_lock:
            self._validate_storage_paths()
            self.database_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            self.capture_root.mkdir(mode=0o700, parents=True, exist_ok=True)
            self._validate_storage_paths()
            connection = sqlite3.connect(self.database_path, timeout=5.0)
            try:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS expert_study_authority (
                        authority_key INTEGER PRIMARY KEY CHECK (authority_key = 1),
                        mode TEXT NOT NULL,
                        protocol_digest TEXT NOT NULL,
                        query_pack_digest TEXT NOT NULL,
                        presentation_digest TEXT NOT NULL,
                        test_only INTEGER NOT NULL CHECK (test_only IN (0, 1))
                    );
                    CREATE TABLE IF NOT EXISTS protocol_approvals (
                        approval_id TEXT PRIMARY KEY,
                        approval_digest TEXT NOT NULL UNIQUE,
                        approval_json TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS study_sessions (
                        session_id TEXT PRIMARY KEY,
                        participant_id TEXT NOT NULL UNIQUE,
                        participant_code_digest TEXT NOT NULL UNIQUE,
                        capability_digest TEXT NOT NULL UNIQUE,
                        revision INTEGER NOT NULL CHECK (revision >= 0),
                        session_json TEXT NOT NULL,
                        eligibility_json TEXT NOT NULL,
                        consent_json TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS study_judgements (
                        session_id TEXT NOT NULL,
                        presentation_id TEXT NOT NULL,
                        judgement_json TEXT NOT NULL,
                        PRIMARY KEY (session_id, presentation_id),
                        FOREIGN KEY (session_id) REFERENCES study_sessions(session_id)
                    );
                    CREATE TABLE IF NOT EXISTS study_judgement_revisions (
                        session_id TEXT NOT NULL,
                        presentation_id TEXT NOT NULL,
                        revision_ordinal INTEGER NOT NULL CHECK (revision_ordinal >= 1),
                        supersedes_judgement_digest TEXT,
                        judgement_json TEXT NOT NULL,
                        PRIMARY KEY (session_id, presentation_id, revision_ordinal),
                        FOREIGN KEY (session_id) REFERENCES study_sessions(session_id)
                    );
                    CREATE TRIGGER IF NOT EXISTS study_judgement_revisions_no_update
                    BEFORE UPDATE ON study_judgement_revisions
                    BEGIN
                        SELECT RAISE(ABORT, 'judgement revision history is append-only');
                    END;
                    CREATE TRIGGER IF NOT EXISTS study_judgement_revisions_no_delete
                    BEFORE DELETE ON study_judgement_revisions
                    BEGIN
                        SELECT RAISE(ABORT, 'judgement revision history is append-only');
                    END;
                    CREATE TABLE IF NOT EXISTS study_commands (
                        command_id TEXT PRIMARY KEY,
                        session_id TEXT NOT NULL,
                        command_kind TEXT NOT NULL,
                        request_digest TEXT NOT NULL,
                        response_json TEXT NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES study_sessions(session_id)
                    );
                    CREATE TABLE IF NOT EXISTS study_completions (
                        session_id TEXT PRIMARY KEY,
                        command_id TEXT NOT NULL UNIQUE,
                        request_digest TEXT NOT NULL,
                        completion_json TEXT NOT NULL,
                        capture_relative_path TEXT NOT NULL UNIQUE,
                        receipt_relative_path TEXT,
                        FOREIGN KEY (session_id) REFERENCES study_sessions(session_id)
                    );
                    """
                )
                expected = (
                    self.mode.value,
                    self.protocol.protocol_digest,
                    self.presentation.query_pack_digest,
                    self.presentation.presentation_digest,
                    int(self.test_only),
                )
                row = connection.execute(
                    "SELECT mode, protocol_digest, query_pack_digest, "
                    "presentation_digest, test_only FROM expert_study_authority "
                    "WHERE authority_key = 1"
                ).fetchone()
                if row is None:
                    connection.execute(
                        "INSERT INTO expert_study_authority VALUES (1, ?, ?, ?, ?, ?)",
                        expected,
                    )
                elif tuple(row) != expected:
                    raise ExpertStudyConfigurationError(
                        "existing study database authority is incompatible"
                    )
                connection.commit()
            except sqlite3.DatabaseError as exc:
                raise ExpertStudyConfigurationError("study schema initialization failed") from exc
            finally:
                connection.close()
            self._validate_storage_paths()
            self._schema_ready = True

    def record_protocol_approval(
        self,
        *,
        approved_by_pseudonym: str,
        confirmation: str,
    ) -> ProtocolApproval:
        """Persist one explicit human approval; no caller default can approve."""

        if self.mode is not StudyMode.FORMAL_G_RW4:
            raise ExpertStudyPreparationError("pilot store cannot hold formal approval")
        if confirmation != PROTOCOL_APPROVAL_CONFIRMATION:
            raise ExpertStudyPreparationError("exact product-owner confirmation is required")
        # This validates the pseudonym without retaining its raw value outside the approval.
        try:
            participant_code_digest(approved_by_pseudonym)
        except ValueError as exc:
            raise ExpertStudyPreparationError(str(exc)) from exc
        now = self._clock()
        payload: dict[str, object] = {
            "schema_version": 1,
            "approval_id": uuid5(
                _APPROVAL_NAMESPACE,
                "\0".join(
                    (
                        self.protocol.protocol_digest,
                        self.presentation.query_pack_digest,
                        approved_by_pseudonym,
                    )
                ),
            ),
            "protocol_version": self.protocol.protocol_version,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_version": "w10-frozen-query-pack-v1",
            "query_pack_digest": self.presentation.query_pack_digest,
            "approved_at": now,
            "approved_by_pseudonym": approved_by_pseudonym,
            "confirmation": confirmation,
        }
        approval = _derived_contract(ProtocolApproval, payload, "approval_digest")
        encoded = _contract_text(approval)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute("SELECT approval_json FROM protocol_approvals").fetchone()
            if existing is not None:
                saved = _validated_from_text(
                    ProtocolApproval,
                    existing["approval_json"],
                    field="approval_json",
                )
                if (
                    saved.protocol_digest != approval.protocol_digest
                    or saved.query_pack_digest != approval.query_pack_digest
                    or saved.approved_by_pseudonym != approval.approved_by_pseudonym
                    or saved.confirmation != approval.confirmation
                ):
                    raise ExpertStudyConflictError(
                        "an immutable approval already exists for this formal authority"
                    )
                connection.commit()
                return saved
            connection.execute(
                "INSERT INTO protocol_approvals "
                "(approval_id, approval_digest, approval_json) VALUES (?, ?, ?)",
                (str(approval.approval_id), approval.approval_digest, encoded),
            )
            connection.commit()
            return approval
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ExpertStudyConflictError("protocol approval uniqueness conflict") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def load_protocol_approval(self) -> ProtocolApproval | None:
        if self.mode is not StudyMode.FORMAL_G_RW4:
            return None
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT approval_json FROM protocol_approvals ORDER BY approval_id"
            ).fetchall()
        finally:
            connection.close()
        if not rows:
            return None
        if len(rows) != 1:
            raise ExpertStudyIntegrityError("formal authority has ambiguous approvals")
        approval = _validated_from_text(
            ProtocolApproval,
            rows[0]["approval_json"],
            field="approval_json",
        )
        if (
            approval.protocol_digest != self.protocol.protocol_digest
            or approval.query_pack_digest != self.presentation.query_pack_digest
        ):
            raise ExpertStudyIntegrityError("protocol approval is stale or incompatible")
        return approval

    def prepare_session(
        self,
        *,
        participant_code: str,
        years_experience: int,
        experience_kinds: Sequence[ExpertExperienceKind],
        assessed_players_within_window: bool,
        conflict_declared: bool,
        conflict_note: str | None,
        consent_items: Mapping[str, bool],
    ) -> PreparedStudySession:
        code_digest, participant_id = _participant_identity(participant_code)
        kinds = tuple(experience_kinds)
        accepted = set(self.protocol.eligibility.accepted_experience)
        eligible = (
            years_experience >= self.protocol.eligibility.minimum_years_experience
            and bool(kinds)
            and set(kinds).issubset(accepted)
            and (
                assessed_players_within_window
                or not self.protocol.eligibility.requires_recent_player_assessment
            )
            and not conflict_declared
        )
        if self.mode is StudyMode.FORMAL_G_RW4 and not eligible:
            raise ExpertStudyPreparationError(
                "formal participation requires exact eligibility and no material conflict"
            )
        if conflict_declared != (conflict_note is not None):
            raise ExpertStudyPreparationError(
                "a bounded conflict note must match the conflict declaration"
            )
        required_consent = (
            "voluntary_participation",
            "local_pseudonymous_storage",
            "withdrawal_before_submission_understood",
            "immutable_after_submission_understood",
            "research_limitations_understood",
        )
        if any(consent_items.get(name) is not True for name in required_consent):
            raise ExpertStudyPreparationError("every consent item must be accepted")

        approval = self.load_protocol_approval()
        if self.mode is StudyMode.FORMAL_G_RW4 and approval is None:
            raise ExpertStudyPreparationError("formal protocol approval is absent")
        now = self._clock()
        eligibility_payload: dict[str, object] = {
            "schema_version": 1,
            "participant_id": participant_id,
            "participant_code_digest": code_digest,
            "assessed_at": now,
            "years_experience": years_experience,
            "experience_kinds": kinds,
            "assessed_players_within_window": assessed_players_within_window,
            "conflict_declared": conflict_declared,
            "conflict_note": conflict_note,
            "eligible": eligible,
        }
        eligibility = _derived_contract(
            ParticipantEligibility,
            eligibility_payload,
            "eligibility_digest",
        )
        consent_payload: dict[str, object] = {
            "schema_version": 1,
            "consent_id": uuid5(
                _SESSION_NAMESPACE,
                f"consent\0{participant_id}\0{self.protocol.protocol_digest}",
            ),
            "participant_id": participant_id,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_digest": self.presentation.query_pack_digest,
            "consented_at": now,
            **{name: True for name in required_consent},
        }
        consent = _derived_contract(ConsentRecord, consent_payload, "consent_digest")
        session_id = uuid5(
            _SESSION_NAMESPACE,
            "\0".join(
                (
                    self.mode.value,
                    str(participant_id),
                    self.protocol.protocol_digest,
                    self.presentation.query_pack_digest,
                )
            ),
        )
        presentations = self._presentations_for(session_id, code_digest)
        session = StudySession(
            session_id=session_id,
            mode=self.mode,
            participant_id=participant_id,
            protocol_digest=self.protocol.protocol_digest,
            query_pack_digest=self.presentation.query_pack_digest,
            approval_digest=approval.approval_digest if approval is not None else None,
            eligibility_digest=eligibility.eligibility_digest,
            consent_digest=consent.consent_digest,
            started_at=now,
            last_activity_at=now,
            presentations=presentations,
            submitted_at=None,
        )
        capability = secrets.token_urlsafe(32)
        capability_digest = _digest_bytes(capability.encode("ascii"))
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT session_id FROM study_sessions WHERE participant_code_digest = ?",
                (code_digest,),
            ).fetchone()
            if existing is not None:
                raise ExpertStudyConflictError(
                    "this pseudonymous participant already has a prepared session; "
                    "resume from the original browser"
                )
            connection.execute(
                """INSERT INTO study_sessions (
                    session_id, participant_id, participant_code_digest,
                    capability_digest, revision, session_json, eligibility_json, consent_json
                ) VALUES (?, ?, ?, ?, 0, ?, ?, ?)""",
                (
                    str(session.session_id),
                    str(participant_id),
                    code_digest,
                    capability_digest,
                    _contract_text(session),
                    _contract_text(eligibility),
                    _contract_text(consent),
                ),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ExpertStudyConflictError("session identity uniqueness conflict") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return PreparedStudySession(capability, self.load_session(capability))

    def _presentations_for(
        self,
        session_id: UUID,
        participant_digest: str,
    ) -> tuple[CandidatePresentation, ...]:
        if self.mode is StudyMode.FORMAL_G_RW4:
            try:
                return build_formal_candidate_presentations(
                    self.presentation,
                    session_id=session_id,
                    participant_digest=participant_digest,
                )
            except ValueError as exc:
                raise ExpertStudyIntegrityError(
                    "frozen formal presentation schedule cannot be constructed"
                ) from exc
        queries = self.presentation.queries[:2]
        ordered_queries = tuple(
            sorted(
                queries,
                key=lambda item: _hash_order(participant_digest, item.query_id),
            )
        )
        primary: list[CandidatePresentation] = []
        for query in ordered_queries:
            candidates = sorted(
                query.candidates,
                key=lambda item: _hash_order(
                    f"{participant_digest}\0{query.query_id}",
                    item.candidate_id,
                ),
            )
            for candidate in candidates:
                ordinal = len(primary) + 1
                presentation_id = uuid5(
                    _PRESENTATION_NAMESPACE,
                    f"{session_id}\0primary\0{query.query_id}\0{candidate.candidate_id}",
                )
                primary.append(
                    CandidatePresentation(
                        presentation_id=presentation_id,
                        query_id=query.query_id,
                        candidate_id=candidate.candidate_id,
                        presentation_ordinal=ordinal,
                        kind=PresentationKind.PRIMARY,
                        repeat_of_presentation_id=None,
                    )
                )
        # Pilot rehearses the repeat mechanics with two local participant-keyed candidates.
        repeat_anchors = tuple(
            sorted(
                primary[:10],
                key=lambda item: _hash_order(
                    f"{participant_digest}\0repeat-anchor",
                    item.presentation_id,
                ),
            )[:2]
        )
        minimum_primary_delay = 3
        repeat_slots: dict[int, CandidatePresentation] = {}
        for anchor in repeat_anchors:
            candidate_slots = tuple(
                slot
                for slot in range(
                    anchor.presentation_ordinal + minimum_primary_delay,
                    len(primary),
                )
                if slot not in repeat_slots
            )
            if not candidate_slots:
                raise ExpertStudyIntegrityError(
                    "participant-keyed repeat has no delayed nonterminal slot"
                )
            slot = min(
                candidate_slots,
                key=lambda value: _hash_order(
                    f"{participant_digest}\0repeat-slot\0{anchor.candidate_id}",
                    value,
                ),
            )
            repeat_slots[slot] = anchor
        presentations: list[CandidatePresentation] = []
        for primary_count, item in enumerate(primary, start=1):
            presentations.append(
                item.model_copy(update={"presentation_ordinal": len(presentations) + 1})
            )
            placed_anchor = repeat_slots.get(primary_count)
            if placed_anchor is not None:
                presentations.append(
                    CandidatePresentation(
                        presentation_id=uuid5(
                            _PRESENTATION_NAMESPACE,
                            f"{session_id}\0repeat\0{placed_anchor.presentation_id}",
                        ),
                        query_id=placed_anchor.query_id,
                        candidate_id=placed_anchor.candidate_id,
                        presentation_ordinal=len(presentations) + 1,
                        kind=PresentationKind.REPEAT,
                        repeat_of_presentation_id=placed_anchor.presentation_id,
                    )
                )
        return tuple(presentations)

    def load_session(self, capability: str) -> StudySessionSnapshot:
        if type(capability) is not str or _CAPABILITY.fullmatch(capability) is None:
            raise ExpertStudyNotFoundError("study session is unavailable")
        capability_digest = _digest_bytes(capability.encode("utf-8", errors="strict"))
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT * FROM study_sessions WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone()
            if row is None:
                raise ExpertStudyNotFoundError("study session is unavailable")
            return self._snapshot(connection, row)
        finally:
            connection.close()

    def _snapshot(
        self,
        connection: sqlite3.Connection,
        row: sqlite3.Row,
    ) -> StudySessionSnapshot:
        session = _validated_from_text(
            StudySession,
            row["session_json"],
            field="session_json",
        )
        eligibility = _validated_from_text(
            ParticipantEligibility,
            row["eligibility_json"],
            field="eligibility_json",
        )
        consent = _validated_from_text(
            ConsentRecord,
            row["consent_json"],
            field="consent_json",
        )
        if (
            session.mode is not self.mode
            or session.protocol_digest != self.protocol.protocol_digest
            or session.query_pack_digest != self.presentation.query_pack_digest
            or session.eligibility_digest != eligibility.eligibility_digest
            or session.consent_digest != consent.consent_digest
        ):
            raise ExpertStudyIntegrityError("persisted session authority drifted")
        judgement_rows = connection.execute(
            "SELECT presentation_id, judgement_json FROM study_judgements WHERE session_id = ? "
            "ORDER BY presentation_id",
            (str(session.session_id),),
        ).fetchall()
        judgements = tuple(
            _validated_from_text(
                CandidateJudgement,
                item["judgement_json"],
                field="judgement_json",
            )
            for item in judgement_rows
        )
        revision_rows = connection.execute(
            "SELECT presentation_id, revision_ordinal, supersedes_judgement_digest, "
            "judgement_json FROM study_judgement_revisions WHERE session_id = ? "
            "ORDER BY presentation_id, revision_ordinal",
            (str(session.session_id),),
        ).fetchall()
        revision_chains: dict[str, list[tuple[int, str | None, CandidateJudgement, str]]] = {}
        for item in revision_rows:
            revision = _validated_from_text(
                CandidateJudgement,
                item["judgement_json"],
                field="judgement revision json",
            )
            revision_chains.setdefault(str(item["presentation_id"]), []).append(
                (
                    int(item["revision_ordinal"]),
                    item["supersedes_judgement_digest"],
                    revision,
                    str(item["judgement_json"]),
                )
            )
        current_text_by_presentation = {
            str(item["presentation_id"]): str(item["judgement_json"]) for item in judgement_rows
        }
        if set(revision_chains) != set(current_text_by_presentation):
            raise ExpertStudyIntegrityError("judgement revision roster differs from current state")
        for presentation_id, chain in revision_chains.items():
            previous_digest: str | None = None
            for expected_ordinal, (ordinal, supersedes, revision, _) in enumerate(chain, start=1):
                if ordinal != expected_ordinal or supersedes != previous_digest:
                    raise ExpertStudyIntegrityError("judgement revision chain is incompatible")
                previous_digest = revision.judgement_digest
            if chain[-1][3] != current_text_by_presentation[presentation_id]:
                raise ExpertStudyIntegrityError(
                    "current judgement differs from append-only history"
                )
        completion_row = connection.execute(
            "SELECT completion_json, capture_relative_path, receipt_relative_path "
            "FROM study_completions WHERE session_id = ?",
            (str(session.session_id),),
        ).fetchone()
        completion: CompletionResult | None = None
        if completion_row is not None:
            if self.mode is StudyMode.FORMAL_G_RW4:
                if self.test_only:
                    completion = self._verified_test_only_formal_completion(
                        completion_row["completion_json"]
                    )
                else:
                    completion = _validated_from_text(
                        CompletionReceipt,
                        completion_row["completion_json"],
                        field="completion_json",
                    )
            else:
                completion = self._verified_pilot_completion(completion_row["completion_json"])
            self._verify_capture_file(completion_row["capture_relative_path"])
            if completion_row["receipt_relative_path"] is not None:
                self._verify_capture_file(completion_row["receipt_relative_path"])
        return StudySessionSnapshot(
            session=session,
            eligibility=eligibility,
            consent=consent,
            judgements=judgements,
            revision=int(row["revision"]),
            completion=completion,
        )

    def current_task(self, snapshot: StudySessionSnapshot) -> StudyTask | None:
        answered = {value.presentation_id for value in snapshot.judgements}
        presentation = next(
            (
                item
                for item in snapshot.session.presentations
                if item.presentation_id not in answered
            ),
            None,
        )
        if presentation is None:
            return None
        query = next(
            item for item in self.presentation.queries if item.query_id == presentation.query_id
        )
        candidate = next(
            item for item in query.candidates if item.candidate_id == presentation.candidate_id
        )
        return StudyTask(
            presentation=presentation,
            query=query,
            candidate=candidate,
            ordinal=presentation.presentation_ordinal,
            total=len(snapshot.session.presentations),
        )

    def record_judgement(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
        presentation_id: UUID,
        state: JudgementState,
        relevance_rating: int | None,
        confidence: int | None,
        failure_category: QualitativeFailureCategory | None,
        explanation: str | None,
    ) -> StudySessionSnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        if type(presentation_id) is not UUID:
            raise TypeError("presentation_id must be an exact UUID")
        capability_digest = _digest_bytes(capability.encode("utf-8", errors="strict"))
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM study_sessions WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone()
            if row is None:
                raise ExpertStudyNotFoundError("study session is unavailable")
            existing_command = self._existing_command(
                connection,
                command_id,
                request_digest,
                str(row["session_id"]),
                "judgement",
            )
            if existing_command:
                connection.commit()
                return self._snapshot(connection, row)
            if int(row["revision"]) != expected_revision:
                raise ExpertStudyConflictError("study session revision is stale")
            snapshot = self._snapshot(connection, row)
            if snapshot.complete or snapshot.session.submitted_at is not None:
                raise ExpertStudyConflictError("completed study session is immutable")
            current = self.current_task(snapshot)
            if current is None or current.presentation.presentation_id != presentation_id:
                raise ExpertStudyConflictError("response does not match the current frozen task")
            now = self._clock()
            payload: dict[str, object] = {
                "schema_version": 1,
                "judgement_id": uuid5(
                    _JUDGEMENT_NAMESPACE,
                    f"{snapshot.session.session_id}\0{presentation_id}\0{command_id}",
                ),
                "session_id": snapshot.session.session_id,
                "participant_id": snapshot.session.participant_id,
                "presentation_id": presentation_id,
                "query_id": current.presentation.query_id,
                "candidate_id": current.presentation.candidate_id,
                "state": state,
                "relevance_rating": relevance_rating,
                "confidence": confidence,
                "failure_category": failure_category,
                "explanation": explanation,
                "recorded_at": now,
            }
            judgement = _derived_contract(
                CandidateJudgement,
                payload,
                "judgement_digest",
            )
            updated_session = StudySession.model_validate(
                snapshot.session.model_dump(mode="python") | {"last_activity_at": now}
            )
            next_revision = expected_revision + 1
            connection.execute(
                "INSERT INTO study_judgements "
                "(session_id, presentation_id, judgement_json) VALUES (?, ?, ?)",
                (
                    str(snapshot.session.session_id),
                    str(presentation_id),
                    _contract_text(judgement),
                ),
            )
            connection.execute(
                "INSERT INTO study_judgement_revisions "
                "(session_id, presentation_id, revision_ordinal, "
                "supersedes_judgement_digest, judgement_json) VALUES (?, ?, 1, NULL, ?)",
                (
                    str(snapshot.session.session_id),
                    str(presentation_id),
                    _contract_text(judgement),
                ),
            )
            connection.execute(
                "UPDATE study_sessions SET revision = ?, session_json = ? WHERE session_id = ?",
                (
                    next_revision,
                    _contract_text(updated_session),
                    str(snapshot.session.session_id),
                ),
            )
            response = _canonical_text(
                {"revision": next_revision, "answered_count": snapshot.answered_count + 1}
            )
            connection.execute(
                "INSERT INTO study_commands VALUES (?, ?, 'judgement', ?, ?)",
                (
                    str(command_id),
                    str(snapshot.session.session_id),
                    request_digest,
                    response,
                ),
            )
            connection.commit()
            updated_row = connection.execute(
                "SELECT * FROM study_sessions WHERE session_id = ?",
                (str(snapshot.session.session_id),),
            ).fetchone()
            if updated_row is None:
                raise ExpertStudyIntegrityError("updated session disappeared")
            return self._snapshot(connection, updated_row)
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ExpertStudyConflictError("concurrent judgement conflict") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def revise_judgement(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
        presentation_id: UUID,
        state: JudgementState,
        relevance_rating: int | None,
        confidence: int | None,
        failure_category: QualitativeFailureCategory | None,
        explanation: str | None,
    ) -> StudySessionSnapshot:
        """Append one pre-seal correction and update the verified current projection."""

        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        if type(presentation_id) is not UUID:
            raise TypeError("presentation_id must be an exact UUID")
        capability_digest = _digest_bytes(capability.encode("utf-8", errors="strict"))
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM study_sessions WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone()
            if row is None:
                raise ExpertStudyNotFoundError("study session is unavailable")
            existing_command = self._existing_command(
                connection,
                command_id,
                request_digest,
                str(row["session_id"]),
                "judgement_correction",
            )
            if existing_command:
                connection.commit()
                return self._snapshot(connection, row)
            if int(row["revision"]) != expected_revision:
                raise ExpertStudyConflictError("study session revision is stale")
            snapshot = self._snapshot(connection, row)
            if snapshot.complete or snapshot.session.submitted_at is not None:
                raise ExpertStudyConflictError("completed study session is immutable")
            if snapshot.answered_count != snapshot.total_count:
                raise ExpertStudyConflictError(
                    "corrections are available only during complete pre-submit review"
                )
            presentation = next(
                (
                    item
                    for item in snapshot.session.presentations
                    if item.presentation_id == presentation_id
                ),
                None,
            )
            current = next(
                (item for item in snapshot.judgements if item.presentation_id == presentation_id),
                None,
            )
            if presentation is None or current is None:
                raise ExpertStudyConflictError("correction target is not a reviewed response")
            now = self._clock()
            payload: dict[str, object] = {
                "schema_version": 1,
                "judgement_id": uuid5(
                    _JUDGEMENT_NAMESPACE,
                    f"{snapshot.session.session_id}\0correction\0{presentation_id}\0{command_id}",
                ),
                "session_id": snapshot.session.session_id,
                "participant_id": snapshot.session.participant_id,
                "presentation_id": presentation_id,
                "query_id": presentation.query_id,
                "candidate_id": presentation.candidate_id,
                "state": state,
                "relevance_rating": relevance_rating,
                "confidence": confidence,
                "failure_category": failure_category,
                "explanation": explanation,
                "recorded_at": now,
            }
            judgement = _derived_contract(
                CandidateJudgement,
                payload,
                "judgement_digest",
            )
            prior_count = connection.execute(
                "SELECT COUNT(*) AS count FROM study_judgement_revisions "
                "WHERE session_id = ? AND presentation_id = ?",
                (str(snapshot.session.session_id), str(presentation_id)),
            ).fetchone()
            if prior_count is None or int(prior_count["count"]) < 1:
                raise ExpertStudyIntegrityError("correction target lost its revision history")
            revision_ordinal = int(prior_count["count"]) + 1
            connection.execute(
                "INSERT INTO study_judgement_revisions "
                "(session_id, presentation_id, revision_ordinal, "
                "supersedes_judgement_digest, judgement_json) VALUES (?, ?, ?, ?, ?)",
                (
                    str(snapshot.session.session_id),
                    str(presentation_id),
                    revision_ordinal,
                    current.judgement_digest,
                    _contract_text(judgement),
                ),
            )
            connection.execute(
                "UPDATE study_judgements SET judgement_json = ? "
                "WHERE session_id = ? AND presentation_id = ?",
                (
                    _contract_text(judgement),
                    str(snapshot.session.session_id),
                    str(presentation_id),
                ),
            )
            updated_session = StudySession.model_validate(
                snapshot.session.model_dump(mode="python") | {"last_activity_at": now}
            )
            next_revision = expected_revision + 1
            connection.execute(
                "UPDATE study_sessions SET revision = ?, session_json = ? WHERE session_id = ?",
                (
                    next_revision,
                    _contract_text(updated_session),
                    str(snapshot.session.session_id),
                ),
            )
            connection.execute(
                "INSERT INTO study_commands VALUES (?, ?, 'judgement_correction', ?, ?)",
                (
                    str(command_id),
                    str(snapshot.session.session_id),
                    request_digest,
                    _canonical_text({"revision": next_revision, "corrected": True}),
                ),
            )
            connection.commit()
            updated_row = connection.execute(
                "SELECT * FROM study_sessions WHERE session_id = ?",
                (str(snapshot.session.session_id),),
            ).fetchone()
            if updated_row is None:
                raise ExpertStudyIntegrityError("corrected session disappeared")
            return self._snapshot(connection, updated_row)
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            raise ExpertStudyConflictError("concurrent judgement correction conflict") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def complete_session(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
    ) -> CompletionResult:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        capability_digest = _digest_bytes(capability.encode("utf-8", errors="strict"))
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM study_sessions WHERE capability_digest = ?",
                (capability_digest,),
            ).fetchone()
            if row is None:
                raise ExpertStudyNotFoundError("study session is unavailable")
            existing_command = self._existing_command(
                connection,
                command_id,
                request_digest,
                str(row["session_id"]),
                "completion",
            )
            if existing_command:
                existing = connection.execute(
                    "SELECT completion_json FROM study_completions WHERE session_id = ?",
                    (str(row["session_id"]),),
                ).fetchone()
                if existing is None:
                    raise ExpertStudyIntegrityError("completion command has no completion")
                connection.commit()
                return self._completion_from_text(existing["completion_json"])
            if int(row["revision"]) != expected_revision:
                raise ExpertStudyConflictError("study session revision is stale")
            snapshot = self._snapshot(connection, row)
            if snapshot.completion is not None:
                raise ExpertStudyConflictError("study session was already submitted")
            if snapshot.answered_count != snapshot.total_count:
                raise ExpertStudyPreparationError(
                    "every frozen presentation must have an explicit response"
                )
            now = self._clock()
            submitted_session = StudySession.model_validate(
                snapshot.session.model_dump(mode="python")
                | {"last_activity_at": now, "submitted_at": now}
            )
            completion: CompletionResult
            capture_path: str
            receipt_path: str | None
            if self.mode is StudyMode.FORMAL_G_RW4:
                completion, capture_path, receipt_path = self._complete_formal(
                    submitted_session,
                    snapshot.eligibility,
                    snapshot.consent,
                    snapshot.judgements,
                    now,
                )
            else:
                completion, capture_path, receipt_path = self._complete_pilot(
                    submitted_session,
                    snapshot.eligibility,
                    snapshot.consent,
                    snapshot.judgements,
                    now,
                )
            next_revision = expected_revision + 1
            connection.execute(
                "UPDATE study_sessions SET revision = ?, session_json = ? WHERE session_id = ?",
                (
                    next_revision,
                    _contract_text(submitted_session),
                    str(submitted_session.session_id),
                ),
            )
            connection.execute(
                "INSERT INTO study_commands VALUES (?, ?, 'completion', ?, ?)",
                (
                    str(command_id),
                    str(submitted_session.session_id),
                    request_digest,
                    _canonical_text({"revision": next_revision, "submitted": True}),
                ),
            )
            connection.execute(
                "INSERT INTO study_completions VALUES (?, ?, ?, ?, ?, ?)",
                (
                    str(submitted_session.session_id),
                    str(command_id),
                    request_digest,
                    self._completion_text(completion),
                    capture_path,
                    receipt_path,
                ),
            )
            connection.commit()
            return completion
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            resolved = self._resolve_completion_race(capability_digest, command_id, request_digest)
            if resolved is not None:
                return resolved
            raise ExpertStudyConflictError("concurrent completion conflict") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _existing_command(
        self,
        connection: sqlite3.Connection,
        command_id: UUID,
        request_digest: str,
        session_id: str,
        command_kind: Literal["judgement", "judgement_correction", "completion"],
    ) -> bool:
        row = connection.execute(
            "SELECT session_id, command_kind, request_digest FROM study_commands "
            "WHERE command_id = ?",
            (str(command_id),),
        ).fetchone()
        if row is None:
            return False
        if (
            row["session_id"] != session_id
            or row["command_kind"] != command_kind
            or row["request_digest"] != request_digest
        ):
            raise ExpertStudyConflictError(
                "command id was reused for a different exact operation or request bytes"
            )
        return True

    def _complete_formal(
        self,
        session: StudySession,
        eligibility: ParticipantEligibility,
        consent: ConsentRecord,
        judgements: tuple[CandidateJudgement, ...],
        submitted_at: datetime,
    ) -> tuple[CompletionResult, str, str | None]:
        approval = self.load_protocol_approval()
        if approval is None or session.approval_digest != approval.approval_digest:
            raise ExpertStudyIntegrityError("formal approval is absent or incompatible")
        if self.test_only:
            return self._complete_test_only_formal(
                session,
                eligibility,
                consent,
                judgements,
                submitted_at,
            )
        submission_id = uuid5(_SUBMISSION_NAMESPACE, str(session.session_id))
        submission_payload: dict[str, object] = {
            "schema_version": 1,
            "submission_id": submission_id,
            "mode": StudyMode.FORMAL_G_RW4,
            "session_id": session.session_id,
            "participant_id": session.participant_id,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_digest": self.presentation.query_pack_digest,
            "approval_digest": approval.approval_digest,
            "w09_pins": self.protocol.w09_pins,
            "session": session,
            "eligibility": eligibility,
            "consent": consent,
            "submitted_at": submitted_at,
            "judgements": tuple(sorted(judgements, key=lambda value: value.presentation_id.bytes)),
        }
        submission = _derived_contract(
            FormalStudySubmission,
            submission_payload,
            "submission_digest",
        )
        receipt_payload: dict[str, object] = {
            "schema_version": 1,
            "receipt_id": uuid5(_RECEIPT_NAMESPACE, str(submission_id)),
            "submission_id": submission_id,
            "participant_id": session.participant_id,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_digest": self.presentation.query_pack_digest,
            "submission_digest": submission.submission_digest,
            "issued_at": submitted_at,
            "formal_evidence_recorded": True,
        }
        receipt = _derived_contract(CompletionReceipt, receipt_payload, "receipt_digest")
        submission_bytes = canonical_json_bytes(submission.model_dump(mode="json"))
        receipt_bytes = canonical_json_bytes(receipt.model_dump(mode="json"))
        submission_path = self._write_content_addressed(
            "formal-submissions",
            _digest_bytes(submission_bytes),
            submission_bytes,
        )
        receipt_path = self._write_content_addressed(
            "formal-receipts",
            _digest_bytes(receipt_bytes),
            receipt_bytes,
        )
        return receipt, submission_path, receipt_path

    def _complete_test_only_formal(
        self,
        session: StudySession,
        eligibility: ParticipantEligibility,
        consent: ConsentRecord,
        judgements: tuple[CandidateJudgement, ...],
        submitted_at: datetime,
    ) -> tuple[Mapping[str, object], str, None]:
        payload: dict[str, object] = {
            "schema_version": 1,
            "record_type": "w10_expert_relevance_test_only_formal_capture",
            "mode": StudyMode.FORMAL_G_RW4.value,
            "test_only": True,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_digest": self.presentation.query_pack_digest,
            "presentation_digest": self.presentation.presentation_digest,
            "capture_id": f"TEST_ONLY-{session.session_id}",
            "session": session.model_dump(mode="json"),
            "eligibility": eligibility.model_dump(mode="json"),
            "consent": consent.model_dump(mode="json"),
            "judgements": [
                value.model_dump(mode="json")
                for value in sorted(judgements, key=lambda item: item.presentation_id.bytes)
            ],
            "submitted_at": submitted_at.isoformat().replace("+00:00", "Z"),
            "formal_evidence_recorded": False,
        }
        completed = payload | {"capture_digest": canonical_research_digest(payload)}
        encoded = canonical_json_bytes(completed)
        path = self._write_content_addressed(
            "test-only-formal-captures",
            _digest_bytes(encoded),
            encoded,
        )
        return completed, path, None

    def _complete_pilot(
        self,
        session: StudySession,
        eligibility: ParticipantEligibility,
        consent: ConsentRecord,
        judgements: tuple[CandidateJudgement, ...],
        submitted_at: datetime,
    ) -> tuple[Mapping[str, object], str, None]:
        payload: dict[str, object] = {
            "schema_version": 1,
            "record_type": "w10_expert_relevance_mechanics_pilot_capture",
            "mode": StudyMode.MECHANICS_PILOT.value,
            "test_only": self.test_only,
            "protocol_digest": self.protocol.protocol_digest,
            "query_pack_digest": self.presentation.query_pack_digest,
            "presentation_digest": self.presentation.presentation_digest,
            "session": session.model_dump(mode="json"),
            "eligibility": eligibility.model_dump(mode="json"),
            "consent": consent.model_dump(mode="json"),
            "judgements": [
                value.model_dump(mode="json")
                for value in sorted(judgements, key=lambda item: item.presentation_id.bytes)
            ],
            "submitted_at": submitted_at.isoformat().replace("+00:00", "Z"),
            "formal_evidence_recorded": False,
        }
        capture_digest = canonical_research_digest(payload)
        completed = payload | {"capture_digest": capture_digest}
        path = self._write_content_addressed(
            "pilot-captures",
            _digest_bytes(canonical_json_bytes(completed)),
            canonical_json_bytes(completed),
        )
        return completed, path, None

    def export_formal_evidence(self, output_path: Path) -> Path:
        """Write one formal-only evaluator envelope with exclusive no-follow creation."""

        if self.mode is not StudyMode.FORMAL_G_RW4:
            raise ExpertStudyPreparationError("pilot authority cannot export formal evidence")
        if self.test_only:
            raise ExpertStudyPreparationError(
                "TEST_ONLY authority cannot export a formal evidence envelope"
            )
        approval = self.load_protocol_approval()
        if approval is None:
            raise ExpertStudyPreparationError("formal protocol approval is absent")
        connection = self._connect()
        try:
            rows = connection.execute(
                """SELECT c.capture_relative_path, c.receipt_relative_path,
                c.completion_json, s.session_json
                FROM study_completions c
                JOIN study_sessions s ON s.session_id = c.session_id
                ORDER BY c.session_id"""
            ).fetchall()
        finally:
            connection.close()
        if not rows:
            raise ExpertStudyPreparationError("no immutable formal submissions are available")

        submissions: list[FormalStudySubmission] = []
        seen_digests: set[str] = set()
        for row in rows:
            capture_path = row["capture_relative_path"]
            receipt_path = row["receipt_relative_path"]
            if (
                type(capture_path) is not str
                or not capture_path.startswith("formal-submissions/sha256/")
                or type(receipt_path) is not str
                or not receipt_path.startswith("formal-receipts/sha256/")
            ):
                raise ExpertStudyIntegrityError(
                    "formal export encountered a non-formal capture path"
                )
            submission_bytes = self._verify_capture_file(capture_path)
            receipt_bytes = self._verify_capture_file(receipt_path)
            try:
                submission = FormalStudySubmission.model_validate_json(submission_bytes)
                receipt = CompletionReceipt.model_validate_json(receipt_bytes)
            except ValidationError as exc:
                raise ExpertStudyIntegrityError(
                    "formal export contract verification failed"
                ) from exc
            persisted_receipt = _validated_from_text(
                CompletionReceipt,
                row["completion_json"],
                field="completion_json",
            )
            session = _validated_from_text(
                StudySession,
                row["session_json"],
                field="session_json",
            )
            if (
                submission.mode is not StudyMode.FORMAL_G_RW4
                or submission.protocol_digest != self.protocol.protocol_digest
                or submission.query_pack_digest != self.presentation.query_pack_digest
                or submission.approval_digest != approval.approval_digest
                or submission.session != session
                or receipt != persisted_receipt
                or receipt.submission_id != submission.submission_id
                or receipt.submission_digest != submission.submission_digest
                or submission.submission_digest in seen_digests
            ):
                raise ExpertStudyIntegrityError(
                    "formal export encountered mixed, stale or duplicate evidence"
                )
            if canonical_json_bytes(submission.model_dump(mode="json")) != submission_bytes:
                raise ExpertStudyIntegrityError("formal submission bytes are not canonical")
            if canonical_json_bytes(receipt.model_dump(mode="json")) != receipt_bytes:
                raise ExpertStudyIntegrityError("formal receipt bytes are not canonical")
            seen_digests.add(submission.submission_digest)
            submissions.append(submission)

        envelope = {
            "schema_version": 1,
            "evidence_class": "FORMAL_G_RW4",
            "submissions": [
                value.model_dump(mode="json")
                for value in sorted(submissions, key=lambda item: item.submission_id.bytes)
            ],
        }
        payload = canonical_json_bytes(envelope)
        target = self._prepare_exclusive_export_target(output_path)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor: int | None = None
        try:
            descriptor = os.open(target, flags, 0o600)
            with os.fdopen(descriptor, "wb", closefd=True) as destination:
                descriptor = None
                destination.write(payload)
                destination.flush()
                os.fsync(destination.fileno())
        except FileExistsError as exc:
            raise ExpertStudyConflictError("formal evidence output already exists") from exc
        except OSError as exc:
            if target.exists() and target.is_file():
                target.unlink()
            raise ExpertStudyIntegrityError("formal evidence export failed closed") from exc
        finally:
            if descriptor is not None:
                os.close(descriptor)
        _require_single_link_regular_file(target, field="formal evidence output")
        if target.read_bytes() != payload:
            raise ExpertStudyIntegrityError("formal evidence output bytes differ")
        return target

    def _prepare_exclusive_export_target(self, output_path: Path) -> Path:
        """Resolve only a new non-symlink JSON target beneath the guarded root."""

        target = output_path.expanduser()
        if not target.is_absolute():
            target = self.allowed_root / target
        target = _absolute_unresolved(target)
        _reject_symlink_components(
            target,
            self.allowed_root,
            field="formal evidence output path",
        )
        if (
            not target.is_relative_to(self.allowed_root)
            or target.suffix != ".json"
            or target.exists()
            or target.is_symlink()
        ):
            raise ExpertStudyConfigurationError(
                "formal evidence output must be a new JSON file inside the guarded root"
            )
        target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        _reject_symlink_components(
            target,
            self.allowed_root,
            field="formal evidence output path",
        )
        return target

    def _write_content_addressed(
        self,
        category: str,
        digest: str,
        payload: bytes,
    ) -> str:
        self._validate_storage_paths()
        if _digest_bytes(payload) != digest:
            raise ExpertStudyIntegrityError("capture digest does not match canonical bytes")
        directory = self.capture_root / category / "sha256" / digest[:2]
        if not directory.is_relative_to(self.capture_root):
            raise ExpertStudyConfigurationError("capture path escaped its guarded root")
        _reject_symlink_components(
            directory,
            self.capture_root,
            field="capture path",
        )
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        _reject_symlink_components(
            directory,
            self.capture_root,
            field="capture path",
        )
        target = directory / f"{digest}.json"
        if target.is_symlink():
            raise ExpertStudyIntegrityError("capture target cannot be a symlink")
        if target.exists():
            try:
                _require_single_link_regular_file(target, field="capture target")
            except ExpertStudyConfigurationError as exc:
                raise ExpertStudyIntegrityError("capture target is an unsafe collision") from exc
        temporary_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=directory,
                prefix=f".{digest}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(payload)
                temporary.flush()
                os.fsync(temporary.fileno())
                temporary_name = temporary.name
            try:
                os.link(temporary_name, target)
            except FileExistsError:
                if target.read_bytes() != payload:
                    raise ExpertStudyConflictError("content address already binds different bytes")
            if target.read_bytes() != payload:
                raise ExpertStudyIntegrityError("persisted capture bytes differ")
        finally:
            if temporary_name is not None and Path(temporary_name).exists():
                Path(temporary_name).unlink()
        try:
            _require_single_link_regular_file(target, field="capture target")
        except ExpertStudyConfigurationError as exc:
            raise ExpertStudyIntegrityError("capture target is not immutable") from exc
        return target.relative_to(self.capture_root).as_posix()

    def _verify_capture_file(self, relative_path: object) -> bytes:
        if type(relative_path) is not str:
            raise ExpertStudyIntegrityError("capture relative path must be text")
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ExpertStudyIntegrityError("capture path escaped or is a symlink")
        target = self.capture_root / relative
        try:
            _reject_symlink_components(
                target,
                self.capture_root,
                field="capture path",
            )
            _require_single_link_regular_file(target, field="capture file")
        except ExpertStudyConfigurationError as exc:
            raise ExpertStudyIntegrityError(
                "capture path is unsafe or not a single-link regular file"
            ) from exc
        try:
            payload = target.read_bytes()
        except OSError as exc:
            raise ExpertStudyIntegrityError("immutable capture is unavailable") from exc
        expected = target.stem
        if _digest_bytes(payload) != expected:
            raise ExpertStudyIntegrityError("immutable capture digest verification failed")
        return payload

    @staticmethod
    def _verified_pilot_completion(value: object) -> Mapping[str, object]:
        if type(value) is not str:
            raise ExpertStudyIntegrityError("pilot completion must be exact text")
        try:
            import json

            payload = json.loads(value)
        except (ValueError, UnicodeError) as exc:
            raise ExpertStudyIntegrityError("pilot completion is invalid JSON") from exc
        if type(payload) is not dict or _canonical_text(payload) != value:
            raise ExpertStudyIntegrityError("pilot completion is not canonical")
        if (
            payload.get("record_type") != "w10_expert_relevance_mechanics_pilot_capture"
            or payload.get("formal_evidence_recorded") is not False
        ):
            raise ExpertStudyIntegrityError("pilot completion evidence lane drifted")
        return cast(dict[str, object], payload)

    @staticmethod
    def _verified_test_only_formal_completion(value: object) -> Mapping[str, object]:
        if type(value) is not str:
            raise ExpertStudyIntegrityError("TEST_ONLY completion must be exact text")
        try:
            import json

            payload = json.loads(value)
        except (ValueError, UnicodeError) as exc:
            raise ExpertStudyIntegrityError("TEST_ONLY completion is invalid JSON") from exc
        if type(payload) is not dict or _canonical_text(payload) != value:
            raise ExpertStudyIntegrityError("TEST_ONLY completion is not canonical")
        if (
            payload.get("record_type") != "w10_expert_relevance_test_only_formal_capture"
            or payload.get("test_only") is not True
            or payload.get("formal_evidence_recorded") is not False
        ):
            raise ExpertStudyIntegrityError("TEST_ONLY formal evidence lane drifted")
        return cast(dict[str, object], payload)

    def _completion_from_text(self, value: object) -> CompletionResult:
        if self.mode is StudyMode.FORMAL_G_RW4:
            if self.test_only:
                return self._verified_test_only_formal_completion(value)
            return _validated_from_text(
                CompletionReceipt,
                value,
                field="completion_json",
            )
        return self._verified_pilot_completion(value)

    @staticmethod
    def _completion_text(value: CompletionResult) -> str:
        if isinstance(value, CompletionReceipt):
            return _contract_text(value)
        return _canonical_text(value)

    def _resolve_completion_race(
        self,
        capability_digest: str,
        command_id: UUID,
        request_digest: str,
    ) -> CompletionResult | None:
        connection = self._connect()
        try:
            row = connection.execute(
                """SELECT c.completion_json, c.command_id, c.request_digest
                FROM study_completions c
                JOIN study_sessions s ON s.session_id = c.session_id
                WHERE s.capability_digest = ?""",
                (capability_digest,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            return None
        if row["command_id"] != str(command_id) or row["request_digest"] != request_digest:
            return None
        return self._completion_from_text(row["completion_json"])


__all__ = [
    "ExpertStudyConfigurationError",
    "ExpertStudyConflictError",
    "ExpertStudyIntegrityError",
    "ExpertStudyNotFoundError",
    "ExpertStudyPreparationError",
    "ExpertStudyStorageError",
    "ExpertStudyStore",
    "FROZEN_PRESENTATION_DIGEST",
    "FROZEN_PROTOCOL_DIGEST",
    "FROZEN_QUERY_PACK_DIGEST",
    "PROTOCOL_APPROVAL_CONFIRMATION",
    "PreparedStudySession",
    "StudySessionSnapshot",
    "StudyTask",
]


# V2 is deliberately a different physical authority.  It does not reuse the v1
# protocol, approval, presentation, capability, or database tables above.
V2_MECHANICS_PILOT_AUTHORITY_VERSION = "w10-v2-mechanics-pilot-authority-v1"
_V2_SCHEMA_CONTRACT = "w10-v2-mechanics-pilot-sqlite-contract-v3"
_V2_SCHEMA_SQL_DIGEST = "a2b5eb22b8fbc2be9802797ccab3689610e8b870f7aa3efbefe365e6cdb560a0"
_V2_PARTICIPANT_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:w10:v2:participant")
_V2_SESSION_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:w10:v2:session")
_V2_PRESENTATION_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:w10:v2:presentation")
_V2_JUDGEMENT_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:w10:v2:judgement")
_V2_FORBIDDEN_PARTICIPANT_KEYS = frozenset(
    {
        "origin",
        "retrieval_rank",
        "retrieval_score",
        "similarity",
        "distance",
        "score",
        "control_rank",
        "control_match_rule",
        "control_selection_rule",
        "evidence_band",
        "difficulty",
        "repeat_anchor_candidate_ids",
        "repeat_of_presentation_id",
        "presentation_kind",
        "expected_outcome",
        "expected_result",
        "previous_response",
        "aggregate_response",
        "grain_id",
        "player_id",
        "candidate_id",
        "query_id",
    }
)
_V2_FORBIDDEN_PARTICIPANT_VALUES = frozenset(
    {"retrieved", "control", "straightforward", "difficult", "lower", "higher"}
)


def _v2_participant_safe_comparison_bytes(
    comparison: ParticipantEvidenceComparisonV2,
) -> bytes:
    """Recheck the protected browser boundary without importing data-product code."""

    payload = comparison.model_dump(mode="json")

    def inspect(value: object) -> None:
        if isinstance(value, dict):
            if _V2_FORBIDDEN_PARTICIPANT_KEYS.intersection(value):
                raise ExpertStudyConfigurationError(
                    "protected provenance key reached v2 participant authority"
                )
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)
        elif isinstance(value, str) and value.casefold() in _V2_FORBIDDEN_PARTICIPANT_VALUES:
            raise ExpertStudyConfigurationError(
                "protected provenance value reached v2 participant authority"
            )

    inspect(payload)
    return canonical_json_bytes(payload)


@dataclass(frozen=True, slots=True)
class V2StudySnapshot:
    session_id: UUID
    participant_id: UUID
    revision: int
    presentation_tokens: tuple[str, ...]
    judgements: tuple[CandidateEvidenceJudgementV2, ...]
    complete: bool


class V2MechanicsPilotStore:
    """Pilot-only v2 persistence, isolated from all retained v1 production paths.

    Authority file schema (for A5): canonical JSON with exactly
    ``schema_version: 2``, ``authority_version`` equal to
    :data:`V2_MECHANICS_PILOT_AUTHORITY_VERSION`, ``lane: MECHANICS_PILOT``, and
    a non-empty ``comparisons`` array.  Each item is the exact canonical JSON
    projection of ``ParticipantEvidenceComparisonV2``; no wrapping query ids or
    provenance may be added.  The store verifies each item's safe bytes before
    it creates a database.
    """

    def __init__(
        self,
        *,
        database_path: Path,
        authority_path: Path,
        allowed_root: Path,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        root = _absolute_unresolved(allowed_root)
        database = _absolute_unresolved(database_path)
        authority = _absolute_unresolved(authority_path)
        if root == Path(root.anchor):
            raise ExpertStudyConfigurationError("v2 allowed root cannot be a filesystem root")
        if not root.is_dir() or root.is_symlink() or root.resolve() != root:
            raise ExpertStudyConfigurationError("v2 allowed root must be a real directory")
        if not database.is_relative_to(root) or not authority.is_relative_to(root):
            raise ExpertStudyConfigurationError("v2 paths must remain inside their guarded root")
        _reject_symlink_components(database, root, field="v2 pilot database")
        _reject_symlink_components(authority, root, field="v2 pilot authority")
        _require_single_link_regular_file(authority, field="v2 pilot authority")
        if database.exists():
            _require_single_link_regular_file(database, field="v2 pilot database")
        if database.name != "mechanics-pilot-v2.sqlite3":
            raise ExpertStudyConfigurationError(
                "v2 pilot database name must be mechanics-pilot-v2.sqlite3"
            )
        self.database_path, self.authority_path, self.allowed_root = database, authority, root
        self.comparisons, self.authority_digest = self._load_authority()
        self._clock = clock
        self._lock = threading.Lock()
        self._ready: bool = False

    def _load_authority(self) -> tuple[tuple[ParticipantEvidenceComparisonV2, ...], str]:
        try:
            raw = self.authority_path.read_bytes()
            decoded = json.loads(raw)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ExpertStudyConfigurationError(
                "v2 mechanics-pilot authority is unavailable"
            ) from exc
        if type(decoded) is not dict or canonical_json_bytes(decoded) != raw:
            raise ExpertStudyConfigurationError(
                "v2 mechanics-pilot authority must be canonical JSON"
            )
        if (
            decoded.get("schema_version") != 2
            or decoded.get("authority_version") != V2_MECHANICS_PILOT_AUTHORITY_VERSION
            or decoded.get("lane") != "MECHANICS_PILOT"
            or set(decoded) != {"schema_version", "authority_version", "lane", "comparisons"}
            or type(decoded.get("comparisons")) is not list
            or not decoded["comparisons"]
        ):
            raise ExpertStudyConfigurationError("v2 mechanics-pilot authority schema is invalid")
        comparisons: list[ParticipantEvidenceComparisonV2] = []
        comparison_digests: set[str] = set()
        for item in decoded["comparisons"]:
            try:
                # Authority is canonical JSON, so preserve JSON coercion for
                # tuple/enums/instants while still validating its exact bytes.
                comparison = ParticipantEvidenceComparisonV2.model_validate_json(
                    canonical_json_bytes(item)
                )
                if _v2_participant_safe_comparison_bytes(comparison) != canonical_json_bytes(item):
                    raise ValueError("not exact participant-safe bytes")
            except (ValidationError, ValueError, FormatError) as exc:
                raise ExpertStudyConfigurationError("v2 authority comparison is unsafe") from exc
            if comparison.comparison_digest in comparison_digests:
                raise ExpertStudyConfigurationError(
                    "v2 mechanics-pilot authority contains a duplicate comparison digest"
                )
            comparison_digests.add(comparison.comparison_digest)
            comparisons.append(comparison)
        return tuple(comparisons), _digest_bytes(raw)

    def _participant_keyed_comparisons(
        self, participant_digest: str
    ) -> tuple[ParticipantEvidenceComparisonV2, ...]:
        comparison_by_candidate_id = {
            comparison.comparison_digest: comparison for comparison in self.comparisons
        }
        candidate_ids = participant_keyed_candidate_order(
            participant_digest,
            tuple(comparison_by_candidate_id),
        )
        return tuple(comparison_by_candidate_id[candidate_id] for candidate_id in candidate_ids)

    def _connect(self) -> sqlite3.Connection:
        self._validate_storage_paths()
        self._ensure_schema()
        self._validate_storage_paths()
        connection = sqlite3.connect(self.database_path, timeout=5, isolation_level=None)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA busy_timeout = 5000")
            self._validate_database_contract(connection)
            connection.execute("PRAGMA journal_mode = WAL")
        except Exception:
            connection.close()
            raise
        return connection

    def _validate_storage_paths(self) -> None:
        if (
            self.allowed_root == Path(self.allowed_root.anchor)
            or not self.allowed_root.is_dir()
            or self.allowed_root.is_symlink()
            or self.allowed_root.resolve() != self.allowed_root
        ):
            raise ExpertStudyConfigurationError("v2 allowed root is no longer a real directory")
        _reject_symlink_components(
            self.database_path,
            self.allowed_root,
            field="v2 pilot database",
        )
        _reject_symlink_components(
            self.authority_path,
            self.allowed_root,
            field="v2 pilot authority",
        )
        _require_single_link_regular_file(
            self.authority_path,
            field="v2 pilot authority",
        )
        if self.database_path.exists():
            _require_single_link_regular_file(
                self.database_path,
                field="v2 pilot database",
            )
        elif getattr(self, "_ready", False):
            raise ExpertStudyConfigurationError(
                "v2 pilot database disappeared after initialization"
            )
        try:
            authority_digest = _digest_bytes(self.authority_path.read_bytes())
        except OSError as exc:
            raise ExpertStudyConfigurationError(
                "v2 pilot authority cannot be revalidated safely"
            ) from exc
        if hasattr(self, "authority_digest") and authority_digest != self.authority_digest:
            raise ExpertStudyConfigurationError("v2 pilot authority bytes changed")

    def _validate_database_contract(self, con: sqlite3.Connection) -> None:
        try:
            schema_rows = [
                {
                    "type": row[0],
                    "name": row[1],
                    "table": row[2],
                    "sql": row[3],
                }
                for row in con.execute(
                    "SELECT type,name,tbl_name,sql FROM sqlite_master "
                    "WHERE name LIKE 'v2_%' OR "
                    "(type IN ('trigger','index') AND tbl_name LIKE 'v2_%' AND sql IS NOT NULL) "
                    "ORDER BY type,name"
                )
            ]
            contract_rows = [
                tuple(row)
                for row in con.execute("SELECT key,contract FROM v2_schema_contract ORDER BY key")
            ]
            authority_rows = [
                tuple(row)
                for row in con.execute(
                    "SELECT key,authority_digest,lane,presentation_count "
                    "FROM v2_authority ORDER BY key"
                )
            ]
        except sqlite3.DatabaseError as exc:
            raise ExpertStudyConfigurationError("v2 database schema cannot be attested") from exc
        if _digest_bytes(canonical_json_bytes(schema_rows)) != _V2_SCHEMA_SQL_DIGEST:
            raise ExpertStudyConfigurationError("v2 database table or trigger SQL is incompatible")
        if contract_rows != [(1, _V2_SCHEMA_CONTRACT)]:
            raise ExpertStudyConfigurationError("v2 database schema contract is incompatible")
        expected_authority = (
            1,
            self.authority_digest,
            "MECHANICS_PILOT",
            len(self.comparisons),
        )
        if authority_rows != [expected_authority]:
            raise ExpertStudyConfigurationError("v2 database authority is incompatible")

    def _ensure_schema(self) -> None:
        with self._lock:
            if self._ready:
                return
            self._validate_storage_paths()
            self.database_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            self._validate_storage_paths()
            con = sqlite3.connect(self.database_path)
            try:
                self._validate_storage_paths()
                existing = con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='v2_schema_contract'"
                ).fetchone()
                other_v2_tables = con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'v2_%'"
                ).fetchall()
                if other_v2_tables and existing is None:
                    raise ExpertStudyConfigurationError(
                        "v2 database predates the fresh schema contract"
                    )
                is_new = existing is None
                if not is_new:
                    contract_rows = [
                        tuple(row)
                        for row in con.execute(
                            "SELECT key,contract FROM v2_schema_contract ORDER BY key"
                        )
                    ]
                    if contract_rows != [(1, _V2_SCHEMA_CONTRACT)]:
                        raise ExpertStudyConfigurationError(
                            "v2 database schema contract is incompatible"
                        )
                    self._validate_database_contract(con)
                if is_new:
                    con.executescript("""
                    CREATE TABLE v2_schema_contract (key INTEGER PRIMARY KEY CHECK(key=1), contract TEXT NOT NULL);
                    CREATE TABLE v2_authority (key INTEGER PRIMARY KEY CHECK(key=1), authority_digest TEXT NOT NULL, lane TEXT NOT NULL, presentation_count INTEGER NOT NULL CHECK(presentation_count > 0));
                    CREATE TABLE v2_sessions (session_id TEXT PRIMARY KEY, participant_id TEXT UNIQUE NOT NULL, code_digest TEXT UNIQUE NOT NULL, capability_digest TEXT UNIQUE NOT NULL, revision INTEGER NOT NULL CHECK(revision >= 0), complete INTEGER NOT NULL DEFAULT 0 CHECK(complete IN (0,1)), consent_json TEXT NOT NULL);
                    CREATE TABLE v2_presentations (session_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), presentation_id TEXT NOT NULL, token TEXT NOT NULL UNIQUE, comparison_json TEXT NOT NULL, PRIMARY KEY(session_id, ordinal), FOREIGN KEY(session_id) REFERENCES v2_sessions(session_id));
                    CREATE TABLE v2_judgements (session_id TEXT NOT NULL, presentation_id TEXT NOT NULL, judgement_json TEXT NOT NULL, PRIMARY KEY(session_id,presentation_id), FOREIGN KEY(session_id) REFERENCES v2_sessions(session_id));
                    CREATE TABLE v2_commands (command_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), command_kind TEXT NOT NULL CHECK(command_kind IN ('record','complete')), request_digest TEXT NOT NULL, response_json TEXT NOT NULL, UNIQUE(session_id,ordinal), FOREIGN KEY(session_id) REFERENCES v2_sessions(session_id));
                    CREATE TABLE v2_judgement_revisions (session_id TEXT NOT NULL, presentation_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), command_id TEXT UNIQUE NOT NULL, command_ordinal INTEGER NOT NULL CHECK(command_ordinal > 0), judgement_json TEXT NOT NULL, PRIMARY KEY(session_id,presentation_id,ordinal), UNIQUE(session_id,command_ordinal), FOREIGN KEY(command_id) REFERENCES v2_commands(command_id));
                    CREATE TABLE v2_completions (session_id TEXT PRIMARY KEY, receipt_json TEXT NOT NULL, receipt_digest TEXT NOT NULL UNIQUE, completed_at TEXT NOT NULL, FOREIGN KEY(session_id) REFERENCES v2_sessions(session_id));
                    CREATE TRIGGER v2_revisions_no_update BEFORE UPDATE ON v2_judgement_revisions BEGIN SELECT RAISE(ABORT, 'v2 revisions are append-only'); END;
                    CREATE TRIGGER v2_revisions_no_delete BEFORE DELETE ON v2_judgement_revisions BEGIN SELECT RAISE(ABORT, 'v2 revisions are append-only'); END;
                    CREATE TRIGGER v2_completed_session_no_update BEFORE UPDATE ON v2_sessions WHEN OLD.complete=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_session_no_delete BEFORE DELETE ON v2_sessions WHEN OLD.complete=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_session_identity_no_update BEFORE UPDATE OF session_id,participant_id,code_digest,capability_digest,consent_json ON v2_sessions BEGIN SELECT RAISE(ABORT, 'v2 session identity and consent are immutable'); END;
                    CREATE TRIGGER v2_session_completion_requires_receipt BEFORE UPDATE OF complete ON v2_sessions WHEN OLD.complete=0 AND NEW.complete=1 AND NOT EXISTS(SELECT 1 FROM v2_completions WHERE session_id=OLD.session_id) BEGIN SELECT RAISE(ABORT, 'v2 completion requires its exact receipt'); END;
                    CREATE TRIGGER v2_presentations_insert_guard BEFORE INSERT ON v2_presentations WHEN NOT EXISTS(SELECT 1 FROM v2_sessions WHERE session_id=NEW.session_id AND complete=0 AND revision=0) OR NEW.ordinal != (SELECT count(*) + 1 FROM v2_presentations WHERE session_id=NEW.session_id) OR (SELECT count(*) FROM v2_presentations WHERE session_id=NEW.session_id) >= (SELECT presentation_count FROM v2_authority WHERE key=1) BEGIN SELECT RAISE(ABORT, 'v2 presentation schedule is sealed'); END;
                    CREATE TRIGGER v2_commands_insert_guard BEFORE INSERT ON v2_commands WHEN NOT EXISTS(SELECT 1 FROM v2_sessions WHERE session_id=NEW.session_id AND complete=0 AND revision + 1=NEW.ordinal) BEGIN SELECT RAISE(ABORT, 'v2 command order is incompatible'); END;
                    CREATE TRIGGER v2_revision_command_guard BEFORE INSERT ON v2_judgement_revisions WHEN NOT EXISTS(SELECT 1 FROM v2_commands c JOIN v2_sessions s ON s.session_id=c.session_id WHERE c.command_id=NEW.command_id AND c.session_id=NEW.session_id AND c.command_kind='record' AND c.response_json=NEW.judgement_json AND c.ordinal=NEW.command_ordinal AND c.ordinal=s.revision + 1 AND s.complete=0) BEGIN SELECT RAISE(ABORT, 'v2 revision command binding is incompatible'); END;
                    CREATE TRIGGER v2_completion_insert_guard BEFORE INSERT ON v2_completions WHEN NOT EXISTS(SELECT 1 FROM v2_sessions WHERE session_id=NEW.session_id AND complete=0) OR (SELECT count(*) FROM v2_presentations WHERE session_id=NEW.session_id) != (SELECT presentation_count FROM v2_authority WHERE key=1) OR (SELECT count(*) FROM v2_judgements WHERE session_id=NEW.session_id) != (SELECT presentation_count FROM v2_authority WHERE key=1) BEGIN SELECT RAISE(ABORT, 'v2 completion requires the exact answered schedule'); END;
                    CREATE TRIGGER v2_completed_no_presentation_insert BEFORE INSERT ON v2_presentations WHEN (SELECT complete FROM v2_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_no_revision_insert BEFORE INSERT ON v2_judgement_revisions WHEN (SELECT complete FROM v2_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_no_judgement_insert BEFORE INSERT ON v2_judgements WHEN (SELECT complete FROM v2_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_no_judgement_update BEFORE UPDATE ON v2_judgements WHEN (SELECT complete FROM v2_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_no_judgement_delete BEFORE DELETE ON v2_judgements WHEN (SELECT complete FROM v2_sessions WHERE session_id=OLD.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_completed_no_command_insert BEFORE INSERT ON v2_commands WHEN (SELECT complete FROM v2_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final v2 submission is immutable'); END;
                    CREATE TRIGGER v2_commands_no_update BEFORE UPDATE ON v2_commands BEGIN SELECT RAISE(ABORT, 'v2 commands are append-only'); END;
                    CREATE TRIGGER v2_commands_no_delete BEFORE DELETE ON v2_commands BEGIN SELECT RAISE(ABORT, 'v2 commands are append-only'); END;
                    CREATE TRIGGER v2_completions_no_update BEFORE UPDATE ON v2_completions BEGIN SELECT RAISE(ABORT, 'v2 completions are append-only'); END;
                    CREATE TRIGGER v2_completions_no_delete BEFORE DELETE ON v2_completions BEGIN SELECT RAISE(ABORT, 'v2 completions are append-only'); END;
                    CREATE TRIGGER v2_presentations_no_update BEFORE UPDATE ON v2_presentations BEGIN SELECT RAISE(ABORT, 'v2 presentation schedule is immutable'); END;
                    CREATE TRIGGER v2_presentations_no_delete BEFORE DELETE ON v2_presentations BEGIN SELECT RAISE(ABORT, 'v2 presentation schedule is immutable'); END;
                    """)
                    con.execute(
                        "INSERT INTO v2_schema_contract VALUES(1,?)", (_V2_SCHEMA_CONTRACT,)
                    )
                row = con.execute(
                    "SELECT authority_digest,lane,presentation_count FROM v2_authority WHERE key=1"
                ).fetchone()
                expected = (self.authority_digest, "MECHANICS_PILOT", len(self.comparisons))
                if row is None:
                    if not is_new:
                        raise ExpertStudyConfigurationError("v2 database authority is incomplete")
                    con.execute("INSERT INTO v2_authority VALUES(1,?,?,?)", expected)
                elif tuple(row) != expected:
                    raise ExpertStudyConfigurationError("v2 database authority is incompatible")
                self._validate_database_contract(con)
                con.commit()
            finally:
                con.close()
            self._ready = True

    def prepare_session(
        self,
        *,
        participant_code: str,
        years_experience: int,
        experience_kinds: Sequence[ExpertExperienceKind],
        assessed_players_within_window: bool,
        conflict_declared: bool,
        conflict_note: str | None,
        consent_items: Mapping[str, bool],
    ) -> tuple[str, V2StudySnapshot]:
        required = (
            "voluntary_participation",
            "local_pseudonymous_storage",
            "withdrawal_before_submission_understood",
            "immutable_after_submission_understood",
            "research_limitations_understood",
        )
        if any(consent_items.get(item) is not True for item in required):
            raise ExpertStudyPreparationError("every v2 pilot consent item must be accepted")
        if (
            years_experience < 2
            or not experience_kinds
            or any(not isinstance(item, ExpertExperienceKind) for item in experience_kinds)
            or len(set(experience_kinds)) != len(experience_kinds)
            or not assessed_players_within_window
            or conflict_declared
            or conflict_declared != (conflict_note is not None)
        ):
            raise ExpertStudyPreparationError(
                "v2 mechanics pilot requires an eligible, conflict-free football reviewer"
            )
        try:
            code_digest = participant_code_digest(participant_code)
        except ValueError as exc:
            raise ExpertStudyPreparationError(str(exc)) from exc
        participant_id = uuid5(_V2_PARTICIPANT_NAMESPACE, code_digest)
        session_id = uuid5(_V2_SESSION_NAMESPACE, code_digest)
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            row = con.execute(
                "SELECT session_id, consent_json FROM v2_sessions WHERE participant_id=?",
                (str(participant_id),),
            ).fetchone()
            consent = {
                "consent": dict(consent_items),
                "years_experience": years_experience,
                "experience_kinds": [item.value for item in experience_kinds],
                "assessed_players_within_window": assessed_players_within_window,
                "conflict_declared": conflict_declared,
                "conflict_note": conflict_note,
                "recorded_at": self._clock().isoformat(),
            }
            if row is not None:
                raise ExpertStudyConflictError(
                    "this participant pseudonym already has a v2 pilot session; "
                    "resume from the original browser"
                )
            capability = secrets.token_urlsafe(32)
            con.execute(
                "INSERT INTO v2_sessions VALUES(?,?,?,?,?,?,?)",
                (
                    str(session_id),
                    str(participant_id),
                    code_digest,
                    _digest_bytes(capability.encode()),
                    0,
                    0,
                    _canonical_text(consent),
                ),
            )
            for ordinal, comparison in enumerate(
                self._participant_keyed_comparisons(code_digest), 1
            ):
                presentation_id = uuid5(_V2_PRESENTATION_NAMESPACE, f"{session_id}:{ordinal}")
                token = secrets.token_urlsafe(24)
                comparison_text = _v2_participant_safe_comparison_bytes(comparison).decode("utf-8")
                con.execute(
                    "INSERT INTO v2_presentations VALUES(?,?,?,?,?)",
                    (str(session_id), ordinal, str(presentation_id), token, comparison_text),
                )
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
        return capability, self.load_session(capability)

    def load_session(self, capability: str) -> V2StudySnapshot:
        if type(capability) is not str or _CAPABILITY.fullmatch(capability) is None:
            raise ExpertStudyNotFoundError("v2 session is unavailable")
        con = self._connect()
        try:
            row = con.execute(
                "SELECT * FROM v2_sessions WHERE capability_digest=?",
                (_digest_bytes(capability.encode()),),
            ).fetchone()
            if row is None:
                raise ExpertStudyNotFoundError("v2 session is unavailable")
            presentations = con.execute(
                "SELECT * FROM v2_presentations WHERE session_id=? ORDER BY ordinal",
                (row["session_id"],),
            ).fetchall()
            judgement_rows = con.execute(
                "SELECT presentation_id,judgement_json FROM v2_judgements WHERE session_id=?",
                (row["session_id"],),
            ).fetchall()
            revision_rows = con.execute(
                "SELECT session_id,presentation_id,ordinal,command_id,command_ordinal,judgement_json "
                "FROM v2_judgement_revisions WHERE session_id=? "
                "ORDER BY presentation_id,ordinal",
                (row["session_id"],),
            ).fetchall()
            completion_rows = con.execute(
                "SELECT receipt_json,receipt_digest,completed_at FROM v2_completions WHERE session_id=?",
                (row["session_id"],),
            ).fetchall()
            command_rows = con.execute(
                "SELECT command_id,session_id,ordinal,command_kind,request_digest,response_json "
                "FROM v2_commands WHERE session_id=? ORDER BY ordinal",
                (row["session_id"],),
            ).fetchall()
        finally:
            con.close()
        try:
            return self._reconstruct_snapshot(
                row,
                presentations,
                judgement_rows,
                revision_rows,
                completion_rows,
                command_rows,
            )
        except (KeyError, TypeError, ValueError, ValidationError, json.JSONDecodeError) as exc:
            raise ExpertStudyIntegrityError("v2 session evidence failed reconstruction") from exc

    def _reconstruct_snapshot(
        self,
        session_row: sqlite3.Row,
        presentation_rows: Sequence[sqlite3.Row],
        judgement_rows: Sequence[sqlite3.Row],
        revision_rows: Sequence[sqlite3.Row],
        completion_rows: Sequence[sqlite3.Row],
        command_rows: Sequence[sqlite3.Row],
    ) -> V2StudySnapshot:
        session_id = UUID(session_row["session_id"])
        participant_id = UUID(session_row["participant_id"])
        code_digest = session_row["code_digest"]
        if (
            type(code_digest) is not str
            or _SHA256.fullmatch(code_digest) is None
            or participant_id != uuid5(_V2_PARTICIPANT_NAMESPACE, code_digest)
            or session_id != uuid5(_V2_SESSION_NAMESPACE, code_digest)
        ):
            raise ExpertStudyIntegrityError("v2 session identity is incompatible")
        consent = json.loads(session_row["consent_json"])
        if type(consent) is not dict or _canonical_text(consent) != session_row["consent_json"]:
            raise ExpertStudyIntegrityError("v2 consent bytes are not canonical")
        if len(presentation_rows) != len(self.comparisons):
            raise ExpertStudyIntegrityError("v2 presentation schedule count drifted")
        comparison_by_presentation: dict[str, ParticipantEvidenceComparisonV2] = {}
        tokens: list[str] = []
        ordered_comparisons = self._participant_keyed_comparisons(code_digest)
        for ordinal, (stored, comparison) in enumerate(
            zip(presentation_rows, ordered_comparisons, strict=True), 1
        ):
            expected_presentation_id = uuid5(_V2_PRESENTATION_NAMESPACE, f"{session_id}:{ordinal}")
            expected_comparison = _v2_participant_safe_comparison_bytes(comparison).decode("utf-8")
            if (
                stored["ordinal"] != ordinal
                or stored["presentation_id"] != str(expected_presentation_id)
                or stored["comparison_json"] != expected_comparison
                or type(stored["token"]) is not str
                or _CAPABILITY.fullmatch(stored["token"]) is None
            ):
                raise ExpertStudyIntegrityError("v2 presentation schedule bytes drifted")
            comparison_by_presentation[stored["presentation_id"]] = comparison
            tokens.append(stored["token"])
        if session_row["revision"] != len(command_rows):
            raise ExpertStudyIntegrityError("v2 session revision does not match command history")
        record_judgements: dict[str, CandidateEvidenceJudgementV2] = {}
        record_response_text: dict[str, str] = {}
        record_command_ordinals: dict[str, int] = {}
        for ordinal, stored in enumerate(command_rows, 1):
            command_id = stored["command_id"]
            command_kind = stored["command_kind"]
            if (
                type(command_id) is not str
                or str(UUID(command_id)) != command_id
                or stored["session_id"] != str(session_id)
                or stored["ordinal"] != ordinal
                or type(stored["request_digest"]) is not str
                or _SHA256.fullmatch(stored["request_digest"]) is None
                or command_kind not in ("record", "complete")
                or type(stored["response_json"]) is not str
            ):
                raise ExpertStudyIntegrityError("v2 command history is incompatible")
            if command_kind == "complete":
                if ordinal != len(command_rows):
                    raise ExpertStudyIntegrityError("v2 completion command is not final")
                continue
            response = CandidateEvidenceJudgementV2.model_validate_json(stored["response_json"])
            bound_comparison = comparison_by_presentation.get(str(response.presentation_id))
            if (
                _contract_text(response) != stored["response_json"]
                or response.session_id != session_id
                or response.participant_id != participant_id
                or bound_comparison is None
            ):
                raise ExpertStudyIntegrityError("v2 record command response drifted")
            validate_response_comparison_v2(response, bound_comparison)
            record_judgements[command_id] = response
            record_response_text[command_id] = stored["response_json"]
            record_command_ordinals[command_id] = stored["ordinal"]
        revision_history: dict[str, list[sqlite3.Row]] = {}
        used_record_commands: set[str] = set()
        for stored in revision_rows:
            presentation_id = stored["presentation_id"]
            history = revision_history.setdefault(presentation_id, [])
            command_id = stored["command_id"]
            revision_response = record_judgements.get(command_id)
            if (
                stored["session_id"] != str(session_id)
                or presentation_id not in comparison_by_presentation
                or stored["ordinal"] != len(history) + 1
                or command_id in used_record_commands
                or revision_response is None
                or stored["command_ordinal"] != record_command_ordinals.get(command_id)
                or str(revision_response.presentation_id) != presentation_id
                or stored["judgement_json"] != record_response_text[command_id]
            ):
                raise ExpertStudyIntegrityError("v2 revision and command history diverged")
            history.append(stored)
            used_record_commands.add(command_id)
        if used_record_commands != set(record_judgements):
            raise ExpertStudyIntegrityError("v2 record command lacks one exact revision")
        if len(judgement_rows) != len({item["presentation_id"] for item in judgement_rows}):
            raise ExpertStudyIntegrityError("v2 judgement identity is ambiguous")
        if {item["presentation_id"] for item in judgement_rows} != set(revision_history):
            raise ExpertStudyIntegrityError("v2 current judgement and revision roster diverged")
        judgement_by_presentation: dict[str, CandidateEvidenceJudgementV2] = {}
        for stored in judgement_rows:
            bound_comparison = comparison_by_presentation.get(stored["presentation_id"])
            if bound_comparison is None:
                raise ExpertStudyIntegrityError("v2 judgement escaped its presentation schedule")
            judgement = CandidateEvidenceJudgementV2.model_validate_json(stored["judgement_json"])
            if (
                _contract_text(judgement) != stored["judgement_json"]
                or judgement.session_id != session_id
                or judgement.participant_id != participant_id
                or str(judgement.presentation_id) != stored["presentation_id"]
                or stored["judgement_json"]
                != revision_history[stored["presentation_id"]][-1]["judgement_json"]
            ):
                raise ExpertStudyIntegrityError(
                    "v2 current judgement diverged from append-only history"
                )
            validate_response_comparison_v2(judgement, bound_comparison)
            judgement_by_presentation[stored["presentation_id"]] = judgement
        judgements = tuple(
            judgement_by_presentation[item["presentation_id"]]
            for item in presentation_rows
            if item["presentation_id"] in judgement_by_presentation
        )
        complete = session_row["complete"] == 1
        if session_row["complete"] not in (0, 1) or complete != (len(completion_rows) == 1):
            raise ExpertStudyIntegrityError("v2 completion state and receipt disagree")
        complete_commands = [item for item in command_rows if item["command_kind"] == "complete"]
        if complete != (len(complete_commands) == 1):
            raise ExpertStudyIntegrityError("v2 completion command history is incompatible")
        if complete:
            receipt_row = completion_rows[0]
            receipt = json.loads(receipt_row["receipt_json"])
            expected_receipt_keys = {
                "record_type",
                "session_id",
                "authority_digest",
                "response_digests",
                "completed_at",
                "immutable",
            }
            if (
                type(receipt) is not dict
                or set(receipt) != expected_receipt_keys
                or _canonical_text(receipt) != receipt_row["receipt_json"]
                or _digest_bytes(receipt_row["receipt_json"].encode())
                != receipt_row["receipt_digest"]
                or receipt["record_type"] != "w10_v2_mechanics_pilot_completion"
                or receipt["session_id"] != str(session_id)
                or receipt["authority_digest"] != self.authority_digest
                or receipt["response_digests"] != [item.judgement_digest for item in judgements]
                or receipt["completed_at"] != receipt_row["completed_at"]
                or receipt["immutable"] is not True
                or complete_commands[0]["response_json"] != receipt_row["receipt_json"]
                or len(judgements) != len(self.comparisons)
            ):
                raise ExpertStudyIntegrityError("v2 completion receipt failed exact reconstruction")
        return V2StudySnapshot(
            session_id,
            participant_id,
            session_row["revision"],
            tuple(tokens),
            judgements,
            complete,
        )

    def task(self, capability: str) -> tuple[str, ParticipantEvidenceComparisonV2, int, int] | None:
        snapshot = self.load_session(capability)
        if snapshot.complete:
            return None
        answered = {item.presentation_id for item in snapshot.judgements}
        con = self._connect()
        try:
            rows = con.execute(
                "SELECT ordinal,presentation_id,token,comparison_json FROM v2_presentations WHERE session_id=? ORDER BY ordinal",
                (str(snapshot.session_id),),
            ).fetchall()
        finally:
            con.close()
        for row in rows:
            if UUID(row["presentation_id"]) not in answered:
                return (
                    row["token"],
                    ParticipantEvidenceComparisonV2.model_validate_json(row["comparison_json"]),
                    row["ordinal"],
                    len(rows),
                )
        return None

    def review_tasks(
        self, capability: str
    ) -> tuple[
        tuple[str, CandidateEvidenceJudgementV2, int, tuple[tuple[str, str, bool], ...]], ...
    ]:
        """Return opaque correction handles and their visible mandatory families."""
        snapshot = self.load_session(capability)
        if snapshot.complete:
            return ()
        con = self._connect()
        try:
            rows = con.execute(
                "SELECT p.ordinal,p.token,p.comparison_json,j.judgement_json FROM v2_presentations p "
                "JOIN v2_judgements j ON j.session_id=p.session_id "
                "AND j.presentation_id=p.presentation_id WHERE p.session_id=? ORDER BY p.ordinal",
                (str(snapshot.session_id),),
            ).fetchall()
        finally:
            con.close()
        return tuple(
            (
                row["token"],
                CandidateEvidenceJudgementV2.model_validate_json(row["judgement_json"]),
                row["ordinal"],
                tuple(
                    (
                        family.label,
                        family.label,
                        family.family_id
                        in CandidateEvidenceJudgementV2.model_validate_json(
                            row["judgement_json"]
                        ).cited_independent_family_ids,
                    )
                    for family in ParticipantEvidenceComparisonV2.model_validate_json(
                        row["comparison_json"]
                    ).exemplar.independent_descriptors
                    if family.mandatory_for_selected_rubric
                ),
            )
            for row in rows
        )

    def record(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
        presentation_token: str,
        state: JudgementState,
        evidence_sufficiency: EvidenceSufficiencyV2,
        assessment_basis: AssessmentBasisV2,
        relevance_rating: int | None,
        confidence: int | None,
        evidence_gap: EvidenceGapV2 | None,
        citations: Sequence[str],
        explanation: str | None,
    ) -> V2StudySnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        snapshot = self.load_session(capability)
        con = self._connect()
        try:
            replay = con.execute(
                "SELECT session_id,command_kind,request_digest FROM v2_commands WHERE command_id=?",
                (str(command_id),),
            ).fetchone()
        finally:
            con.close()
        if replay is not None:
            if (
                replay["session_id"] != str(snapshot.session_id)
                or replay["command_kind"] != "record"
                or replay["request_digest"] != request_digest
            ):
                raise ExpertStudyConflictError("v2 command id was reused with different payload")
            return self.load_session(capability)
        if snapshot.complete:
            raise ExpertStudyConflictError("final v2 submission is immutable")
        if expected_revision != snapshot.revision:
            raise ExpertStudyConflictError("v2 session changed; refresh before saving")
        con = self._connect()
        try:
            item = con.execute(
                "SELECT * FROM v2_presentations WHERE session_id=? AND token=?",
                (str(snapshot.session_id), presentation_token),
            ).fetchone()
            if item is None:
                raise ExpertStudyNotFoundError("presentation is unavailable")
            comparison = ParticipantEvidenceComparisonV2.model_validate_json(
                item["comparison_json"]
            )
            visible_citations = {
                family.label: family.family_id
                for player in (comparison.exemplar, comparison.candidate)
                for family in player.independent_descriptors
                if family.mandatory_for_selected_rubric
            }
            if len(set(citations)) != len(citations) or any(
                citation not in visible_citations for citation in citations
            ):
                raise ExpertStudyConflictError(
                    "v2 citations must be selected from displayed mandatory evidence families"
                )
            payload: dict[str, object] = {
                "schema_version": 2,
                "response_version": "w10-expert-evidence-response-v2",
                "judgement_id": uuid5(
                    _V2_JUDGEMENT_NAMESPACE, f"{snapshot.session_id}:{item['presentation_id']}"
                ),
                "session_id": snapshot.session_id,
                "participant_id": snapshot.participant_id,
                "presentation_id": UUID(item["presentation_id"]),
                "query_id": uuid5(NAMESPACE_URL, comparison.comparison_digest + ":query"),
                "candidate_id": uuid5(
                    NAMESPACE_URL, comparison.candidate.bundle_digest + ":candidate"
                ),
                "comparison_digest": comparison.comparison_digest,
                "position_code": comparison.position_code,
                "md_subrubric": comparison.md_subrubric,
                "state": state,
                "evidence_sufficiency": evidence_sufficiency,
                "assessment_basis": assessment_basis,
                "relevance_rating": relevance_rating,
                "confidence": confidence,
                "evidence_gap": evidence_gap,
                "cited_independent_family_ids": tuple(
                    visible_citations[item] for item in citations
                ),
                "explanation": explanation,
                "recorded_at": self._clock(),
            }
            payload["judgement_digest"] = canonical_research_digest(
                _JSON_OBJECT_ADAPTER.dump_python(payload, mode="json")
            )
            judgement = CandidateEvidenceJudgementV2.model_validate(payload)
            validate_response_comparison_v2(judgement, comparison)
            encoded = _contract_text(judgement)
            con.execute("BEGIN IMMEDIATE")
            # A concurrent exact winner may have committed between the initial
            # optimistic read and acquiring this write transaction.
            if self._command_replay_in_transaction(
                con, snapshot.session_id, command_id, "record", request_digest
            ):
                con.commit()
                return self.load_session(capability)
            current = con.execute(
                "SELECT revision,complete FROM v2_sessions WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            if current["revision"] != expected_revision or current["complete"]:
                raise ExpertStudyConflictError("v2 session changed; refresh before saving")
            previous = con.execute(
                "SELECT judgement_json FROM v2_judgements WHERE session_id=? AND presentation_id=?",
                (str(snapshot.session_id), item["presentation_id"]),
            ).fetchone()
            ordinal = (
                con.execute(
                    "SELECT count(*) FROM v2_judgement_revisions WHERE session_id=? AND presentation_id=?",
                    (str(snapshot.session_id), item["presentation_id"]),
                ).fetchone()[0]
                + 1
            )
            con.execute(
                "INSERT INTO v2_commands VALUES(?,?,?,?,?,?)",
                (
                    str(command_id),
                    str(snapshot.session_id),
                    expected_revision + 1,
                    "record",
                    request_digest,
                    encoded,
                ),
            )
            con.execute(
                "INSERT INTO v2_judgement_revisions VALUES(?,?,?,?,?,?)",
                (
                    str(snapshot.session_id),
                    item["presentation_id"],
                    ordinal,
                    str(command_id),
                    expected_revision + 1,
                    encoded,
                ),
            )
            if previous is None:
                con.execute(
                    "INSERT INTO v2_judgements VALUES(?,?,?)",
                    (str(snapshot.session_id), item["presentation_id"], encoded),
                )
            else:
                con.execute(
                    "UPDATE v2_judgements SET judgement_json=? WHERE session_id=? AND presentation_id=?",
                    (encoded, str(snapshot.session_id), item["presentation_id"]),
                )
            con.execute(
                "UPDATE v2_sessions SET revision=revision+1 WHERE session_id=?",
                (str(snapshot.session_id),),
            )
            con.commit()
        except sqlite3.IntegrityError as exc:
            con.rollback()
            if self._command_replay(snapshot.session_id, command_id, "record", request_digest):
                return self.load_session(capability)
            raise ExpertStudyConflictError("v2 command conflict") from exc
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
        return self.load_session(capability)

    def _command_replay(
        self, session_id: UUID, command_id: UUID, kind: str, request_digest: str
    ) -> bool:
        con = self._connect()
        try:
            row = con.execute(
                "SELECT session_id,command_kind,request_digest FROM v2_commands WHERE command_id=?",
                (str(command_id),),
            ).fetchone()
            return row is not None and tuple(row) == (str(session_id), kind, request_digest)
        finally:
            con.close()

    @staticmethod
    def _command_replay_in_transaction(
        con: sqlite3.Connection, session_id: UUID, command_id: UUID, kind: str, request_digest: str
    ) -> bool:
        row = con.execute(
            "SELECT session_id,command_kind,request_digest FROM v2_commands WHERE command_id=?",
            (str(command_id),),
        ).fetchone()
        if row is None:
            return False
        if tuple(row) != (str(session_id), kind, request_digest):
            raise ExpertStudyConflictError("v2 command id was reused with different payload")
        return True

    def complete(
        self, *, capability: str, command_id: UUID, expected_revision: int, request_digest: str
    ) -> V2StudySnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        snapshot = self.load_session(capability)
        con = self._connect()
        try:
            replay = con.execute(
                "SELECT session_id,command_kind,request_digest FROM v2_commands WHERE command_id=?",
                (str(command_id),),
            ).fetchone()
        finally:
            con.close()
        if replay is not None:
            if (
                replay["session_id"] != str(snapshot.session_id)
                or replay["command_kind"] != "complete"
                or replay["request_digest"] != request_digest
            ):
                raise ExpertStudyConflictError("v2 command id was reused with different payload")
            return self.load_session(capability)
        if expected_revision != snapshot.revision or len(snapshot.judgements) != len(
            snapshot.presentation_tokens
        ):
            raise ExpertStudyConflictError(
                "all v2 pilot responses must be saved at the current revision"
            )
        con = self._connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            if self._command_replay_in_transaction(
                con, snapshot.session_id, command_id, "complete", request_digest
            ):
                con.commit()
                return self.load_session(capability)
            current = con.execute(
                "SELECT revision,complete FROM v2_sessions WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            if (
                current is None
                or current["revision"] != expected_revision
                or current["complete"] != 0
            ):
                raise ExpertStudyConflictError("v2 session changed; refresh before submitting")
            receipt = {
                "record_type": "w10_v2_mechanics_pilot_completion",
                "session_id": str(snapshot.session_id),
                "authority_digest": self.authority_digest,
                "response_digests": [item.judgement_digest for item in snapshot.judgements],
                "completed_at": self._clock().isoformat(),
                "immutable": True,
            }
            receipt_text = _canonical_text(receipt)
            receipt_digest = _digest_bytes(receipt_text.encode())
            con.execute(
                "INSERT INTO v2_completions VALUES(?,?,?,?)",
                (str(snapshot.session_id), receipt_text, receipt_digest, receipt["completed_at"]),
            )
            con.execute(
                "INSERT INTO v2_commands VALUES(?,?,?,?,?,?)",
                (
                    str(command_id),
                    str(snapshot.session_id),
                    expected_revision + 1,
                    "complete",
                    request_digest,
                    receipt_text,
                ),
            )
            updated = con.execute(
                "UPDATE v2_sessions SET complete=1, revision=revision+1 WHERE session_id=? AND complete=0 AND revision=?",
                (str(snapshot.session_id), expected_revision),
            )
            if updated.rowcount != 1:
                raise ExpertStudyConflictError("v2 session changed; refresh before submitting")
            con.commit()
        except sqlite3.IntegrityError as exc:
            con.rollback()
            if self._command_replay(snapshot.session_id, command_id, "complete", request_digest):
                return self.load_session(capability)
            raise ExpertStudyConflictError("v2 command conflict") from exc
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
        return self.load_session(capability)


__all__ += ["V2_MECHANICS_PILOT_AUTHORITY_VERSION", "V2MechanicsPilotStore", "V2StudySnapshot"]


# The participant-language rework is a new physical and logical pilot issue.
# The retained v2 store above remains the exact reader for the stopped pilot.
HISTORICAL_COMPARISON_AUTHORITY_VERSION = "historical-player-comparison-pilot-authority-v1"
HISTORICAL_COMPARISON_PARTICIPANT_VERSION = "historical-player-comparison-participant-v1"
HISTORICAL_COMPARISON_RESPONSE_VERSION = "historical-player-comparison-response-v1"
HISTORICAL_COMPARISON_DEBRIEF_VERSION = "historical-player-comparison-debrief-v1"
_HISTORICAL_SCHEMA_CONTRACT = "historical-player-comparison-sqlite-contract-v1"
_HISTORICAL_PARTICIPANT_NAMESPACE = uuid5(
    NAMESPACE_URL, "urn:scouting-intelligence:historical-comparison:participant:v1"
)
_HISTORICAL_SESSION_NAMESPACE = uuid5(
    NAMESPACE_URL, "urn:scouting-intelligence:historical-comparison:session:v1"
)
_HISTORICAL_PRESENTATION_NAMESPACE = uuid5(
    NAMESPACE_URL, "urn:scouting-intelligence:historical-comparison:presentation:v1"
)
_HISTORICAL_JUDGEMENT_NAMESPACE = uuid5(
    NAMESPACE_URL, "urn:scouting-intelligence:historical-comparison:judgement:v1"
)
_HISTORICAL_DEBRIEF_NAMESPACE = uuid5(
    NAMESPACE_URL, "urn:scouting-intelligence:historical-comparison:debrief:v1"
)

_HISTORICAL_SCHEMA_SQL = """
CREATE TABLE hpc_schema_contract (key INTEGER PRIMARY KEY CHECK(key=1), contract TEXT NOT NULL);
CREATE TABLE hpc_authority (key INTEGER PRIMARY KEY CHECK(key=1), authority_digest TEXT NOT NULL, authority_version TEXT NOT NULL, participant_version TEXT NOT NULL, response_version TEXT NOT NULL, debrief_version TEXT NOT NULL, lane TEXT NOT NULL, presentation_count INTEGER NOT NULL CHECK(presentation_count > 0));
CREATE TABLE hpc_sessions (session_id TEXT PRIMARY KEY, participant_id TEXT UNIQUE NOT NULL, code_digest TEXT UNIQUE NOT NULL, capability_digest TEXT UNIQUE NOT NULL, revision INTEGER NOT NULL CHECK(revision >= 0), complete INTEGER NOT NULL DEFAULT 0 CHECK(complete IN (0,1)), consent_json TEXT NOT NULL);
CREATE TABLE hpc_presentations (session_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), presentation_id TEXT NOT NULL, token TEXT NOT NULL UNIQUE, comparison_json TEXT NOT NULL, PRIMARY KEY(session_id, ordinal), FOREIGN KEY(session_id) REFERENCES hpc_sessions(session_id));
CREATE TABLE hpc_judgements (session_id TEXT NOT NULL, presentation_id TEXT NOT NULL, judgement_json TEXT NOT NULL, PRIMARY KEY(session_id,presentation_id), FOREIGN KEY(session_id) REFERENCES hpc_sessions(session_id));
CREATE TABLE hpc_debriefs (session_id TEXT PRIMARY KEY, debrief_json TEXT NOT NULL, FOREIGN KEY(session_id) REFERENCES hpc_sessions(session_id));
CREATE TABLE hpc_commands (command_id TEXT PRIMARY KEY, session_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), command_kind TEXT NOT NULL CHECK(command_kind IN ('record','debrief','complete')), request_digest TEXT NOT NULL, response_json TEXT NOT NULL, UNIQUE(session_id,ordinal), FOREIGN KEY(session_id) REFERENCES hpc_sessions(session_id));
CREATE TABLE hpc_judgement_revisions (session_id TEXT NOT NULL, presentation_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), command_id TEXT UNIQUE NOT NULL, command_ordinal INTEGER NOT NULL CHECK(command_ordinal > 0), judgement_json TEXT NOT NULL, PRIMARY KEY(session_id,presentation_id,ordinal), UNIQUE(session_id,command_ordinal), FOREIGN KEY(command_id) REFERENCES hpc_commands(command_id));
CREATE TABLE hpc_debrief_revisions (session_id TEXT NOT NULL, ordinal INTEGER NOT NULL CHECK(ordinal > 0), command_id TEXT UNIQUE NOT NULL, command_ordinal INTEGER NOT NULL CHECK(command_ordinal > 0), debrief_json TEXT NOT NULL, PRIMARY KEY(session_id,ordinal), UNIQUE(session_id,command_ordinal), FOREIGN KEY(command_id) REFERENCES hpc_commands(command_id));
CREATE TABLE hpc_completions (session_id TEXT PRIMARY KEY, receipt_json TEXT NOT NULL, receipt_digest TEXT NOT NULL UNIQUE, completed_at TEXT NOT NULL, FOREIGN KEY(session_id) REFERENCES hpc_sessions(session_id));
CREATE TRIGGER hpc_judgement_revisions_no_update BEFORE UPDATE ON hpc_judgement_revisions BEGIN SELECT RAISE(ABORT, 'comparison response revisions are append-only'); END;
CREATE TRIGGER hpc_judgement_revisions_no_delete BEFORE DELETE ON hpc_judgement_revisions BEGIN SELECT RAISE(ABORT, 'comparison response revisions are append-only'); END;
CREATE TRIGGER hpc_debrief_revisions_no_update BEFORE UPDATE ON hpc_debrief_revisions BEGIN SELECT RAISE(ABORT, 'pilot feedback revisions are append-only'); END;
CREATE TRIGGER hpc_debrief_revisions_no_delete BEFORE DELETE ON hpc_debrief_revisions BEGIN SELECT RAISE(ABORT, 'pilot feedback revisions are append-only'); END;
CREATE TRIGGER hpc_completed_session_no_update BEFORE UPDATE ON hpc_sessions WHEN OLD.complete=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_session_no_delete BEFORE DELETE ON hpc_sessions WHEN OLD.complete=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_session_identity_no_update BEFORE UPDATE OF session_id,participant_id,code_digest,capability_digest,consent_json ON hpc_sessions BEGIN SELECT RAISE(ABORT, 'participant identity and consent are immutable'); END;
CREATE TRIGGER hpc_session_completion_requires_receipt BEFORE UPDATE OF complete ON hpc_sessions WHEN OLD.complete=0 AND NEW.complete=1 AND NOT EXISTS(SELECT 1 FROM hpc_completions WHERE session_id=OLD.session_id) BEGIN SELECT RAISE(ABORT, 'completion requires its exact local receipt'); END;
CREATE TRIGGER hpc_presentations_insert_guard BEFORE INSERT ON hpc_presentations WHEN NOT EXISTS(SELECT 1 FROM hpc_sessions WHERE session_id=NEW.session_id AND complete=0 AND revision=0) OR NEW.ordinal != (SELECT count(*) + 1 FROM hpc_presentations WHERE session_id=NEW.session_id) OR (SELECT count(*) FROM hpc_presentations WHERE session_id=NEW.session_id) >= (SELECT presentation_count FROM hpc_authority WHERE key=1) BEGIN SELECT RAISE(ABORT, 'comparison schedule is sealed'); END;
CREATE TRIGGER hpc_commands_insert_guard BEFORE INSERT ON hpc_commands WHEN NOT EXISTS(SELECT 1 FROM hpc_sessions WHERE session_id=NEW.session_id AND complete=0 AND revision + 1=NEW.ordinal) BEGIN SELECT RAISE(ABORT, 'participant action order is incompatible'); END;
CREATE TRIGGER hpc_judgement_revision_command_guard BEFORE INSERT ON hpc_judgement_revisions WHEN NOT EXISTS(SELECT 1 FROM hpc_commands c JOIN hpc_sessions s ON s.session_id=c.session_id WHERE c.command_id=NEW.command_id AND c.session_id=NEW.session_id AND c.command_kind='record' AND c.response_json=NEW.judgement_json AND c.ordinal=NEW.command_ordinal AND c.ordinal=s.revision + 1 AND s.complete=0) BEGIN SELECT RAISE(ABORT, 'response revision action binding is incompatible'); END;
CREATE TRIGGER hpc_debrief_revision_command_guard BEFORE INSERT ON hpc_debrief_revisions WHEN NOT EXISTS(SELECT 1 FROM hpc_commands c JOIN hpc_sessions s ON s.session_id=c.session_id WHERE c.command_id=NEW.command_id AND c.session_id=NEW.session_id AND c.command_kind='debrief' AND c.response_json=NEW.debrief_json AND c.ordinal=NEW.command_ordinal AND c.ordinal=s.revision + 1 AND s.complete=0) BEGIN SELECT RAISE(ABORT, 'pilot feedback revision action binding is incompatible'); END;
CREATE TRIGGER hpc_completion_insert_guard BEFORE INSERT ON hpc_completions WHEN NOT EXISTS(SELECT 1 FROM hpc_sessions WHERE session_id=NEW.session_id AND complete=0) OR (SELECT count(*) FROM hpc_presentations WHERE session_id=NEW.session_id) != (SELECT presentation_count FROM hpc_authority WHERE key=1) OR (SELECT count(*) FROM hpc_judgements WHERE session_id=NEW.session_id) != (SELECT presentation_count FROM hpc_authority WHERE key=1) OR NOT EXISTS(SELECT 1 FROM hpc_debriefs WHERE session_id=NEW.session_id) BEGIN SELECT RAISE(ABORT, 'completion requires every comparison and pilot-feedback answer'); END;
CREATE TRIGGER hpc_completed_no_presentation_insert BEFORE INSERT ON hpc_presentations WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_judgement_insert BEFORE INSERT ON hpc_judgements WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_judgement_update BEFORE UPDATE ON hpc_judgements WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_judgement_delete BEFORE DELETE ON hpc_judgements WHEN (SELECT complete FROM hpc_sessions WHERE session_id=OLD.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_debrief_insert BEFORE INSERT ON hpc_debriefs WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_debrief_update BEFORE UPDATE ON hpc_debriefs WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_debrief_delete BEFORE DELETE ON hpc_debriefs WHEN (SELECT complete FROM hpc_sessions WHERE session_id=OLD.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_completed_no_command_insert BEFORE INSERT ON hpc_commands WHEN (SELECT complete FROM hpc_sessions WHERE session_id=NEW.session_id)=1 BEGIN SELECT RAISE(ABORT, 'final comparison submission is immutable'); END;
CREATE TRIGGER hpc_commands_no_update BEFORE UPDATE ON hpc_commands BEGIN SELECT RAISE(ABORT, 'participant actions are append-only'); END;
CREATE TRIGGER hpc_commands_no_delete BEFORE DELETE ON hpc_commands BEGIN SELECT RAISE(ABORT, 'participant actions are append-only'); END;
CREATE TRIGGER hpc_completions_no_update BEFORE UPDATE ON hpc_completions BEGIN SELECT RAISE(ABORT, 'completion receipts are append-only'); END;
CREATE TRIGGER hpc_completions_no_delete BEFORE DELETE ON hpc_completions BEGIN SELECT RAISE(ABORT, 'completion receipts are append-only'); END;
CREATE TRIGGER hpc_presentations_no_update BEFORE UPDATE ON hpc_presentations BEGIN SELECT RAISE(ABORT, 'comparison schedule is immutable'); END;
CREATE TRIGGER hpc_presentations_no_delete BEFORE DELETE ON hpc_presentations BEGIN SELECT RAISE(ABORT, 'comparison schedule is immutable'); END;
"""


def _historical_schema_rows(connection: sqlite3.Connection) -> list[dict[str, object]]:
    return [
        {"type": row[0], "name": row[1], "table": row[2], "sql": row[3]}
        for row in connection.execute(
            "SELECT type,name,tbl_name,sql FROM sqlite_master "
            "WHERE name LIKE 'hpc_%' OR "
            "(type IN ('trigger','index') AND tbl_name LIKE 'hpc_%' AND sql IS NOT NULL) "
            "ORDER BY type,name"
        )
    ]


def _historical_expected_schema_digest() -> str:
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(_HISTORICAL_SCHEMA_SQL)
        return _digest_bytes(canonical_json_bytes(_historical_schema_rows(connection)))
    finally:
        connection.close()


HISTORICAL_COMPARISON_SCHEMA_SQL_DIGEST = _historical_expected_schema_digest()


@dataclass(frozen=True, slots=True)
class HistoricalComparisonStudySnapshot:
    session_id: UUID
    participant_id: UUID
    revision: int
    presentation_tokens: tuple[str, ...]
    judgements: tuple[HistoricalComparisonJudgementV1, ...]
    debrief: HistoricalComparisonPilotDebriefV1 | None
    complete: bool
    completed_at: str | None
    receipt_digest: str | None


class HistoricalComparisonPilotStore:
    """Separate append-only store for the participant-language pilot issue."""

    def __init__(
        self,
        *,
        database_path: Path,
        authority_path: Path,
        allowed_root: Path,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        root = _absolute_unresolved(allowed_root)
        database = _absolute_unresolved(database_path)
        authority = _absolute_unresolved(authority_path)
        if root == Path(root.anchor):
            raise ExpertStudyConfigurationError(
                "participant-study root cannot be a filesystem root"
            )
        if not root.is_dir() or root.is_symlink() or root.resolve() != root:
            raise ExpertStudyConfigurationError("participant-study root must be a real directory")
        if not database.is_relative_to(root) or not authority.is_relative_to(root):
            raise ExpertStudyConfigurationError(
                "participant-study files must stay in their local folder"
            )
        _reject_symlink_components(database, root, field="participant response database")
        _reject_symlink_components(authority, root, field="comparison authority")
        _require_single_link_regular_file(authority, field="comparison authority")
        if database.exists():
            _require_single_link_regular_file(database, field="participant response database")
        if database.name != "historical-player-comparison-pilot-v1.sqlite3":
            raise ExpertStudyConfigurationError("participant response database has the wrong name")
        self.database_path = database
        self.authority_path = authority
        self.allowed_root = root
        self.comparisons, self.authority_digest = self._load_authority()
        self._clock = clock
        self._lock = threading.Lock()
        self._ready = False

    def _load_authority(self) -> tuple[tuple[ParticipantEvidenceComparisonV2, ...], str]:
        try:
            raw = self.authority_path.read_bytes()
            decoded = json.loads(raw)
        except (OSError, UnicodeError, ValueError) as exc:
            raise ExpertStudyConfigurationError("comparison set is unavailable") from exc
        expected_keys = {
            "schema_version",
            "authority_version",
            "participant_contract_version",
            "response_contract_version",
            "debrief_contract_version",
            "lane",
            "comparisons",
        }
        if type(decoded) is not dict or canonical_json_bytes(decoded) != raw:
            raise ExpertStudyConfigurationError("comparison set must use exact canonical JSON")
        if (
            set(decoded) != expected_keys
            or decoded.get("schema_version") != 3
            or decoded.get("authority_version") != HISTORICAL_COMPARISON_AUTHORITY_VERSION
            or decoded.get("participant_contract_version")
            != HISTORICAL_COMPARISON_PARTICIPANT_VERSION
            or decoded.get("response_contract_version") != HISTORICAL_COMPARISON_RESPONSE_VERSION
            or decoded.get("debrief_contract_version") != HISTORICAL_COMPARISON_DEBRIEF_VERSION
            or decoded.get("lane") != "MECHANICS_PILOT"
            or type(decoded.get("comparisons")) is not list
            or not decoded["comparisons"]
        ):
            raise ExpertStudyConfigurationError("comparison set version is incompatible")
        comparisons: list[ParticipantEvidenceComparisonV2] = []
        digests: set[str] = set()
        for item in decoded["comparisons"]:
            try:
                item_bytes = canonical_json_bytes(item)
                comparison = ParticipantEvidenceComparisonV2.model_validate_json(item_bytes)
                if _v2_participant_safe_comparison_bytes(comparison) != item_bytes:
                    raise ValueError("comparison bytes are not exact")
            except (ValidationError, ValueError, FormatError) as exc:
                raise ExpertStudyConfigurationError(
                    "comparison set contains unsafe evidence"
                ) from exc
            if comparison.comparison_digest in digests:
                raise ExpertStudyConfigurationError("comparison set contains a duplicate task")
            digests.add(comparison.comparison_digest)
            comparisons.append(comparison)
        return tuple(comparisons), _digest_bytes(raw)

    def _ordered_comparisons(
        self, participant_digest: str
    ) -> tuple[ParticipantEvidenceComparisonV2, ...]:
        by_digest = {item.comparison_digest: item for item in self.comparisons}
        ordered = participant_keyed_candidate_order(participant_digest, tuple(by_digest))
        return tuple(by_digest[item] for item in ordered)

    def _validate_paths(self) -> None:
        if (
            self.allowed_root == Path(self.allowed_root.anchor)
            or not self.allowed_root.is_dir()
            or self.allowed_root.is_symlink()
            or self.allowed_root.resolve() != self.allowed_root
        ):
            raise ExpertStudyConfigurationError("participant-study root is no longer safe")
        _reject_symlink_components(
            self.database_path, self.allowed_root, field="participant response database"
        )
        _reject_symlink_components(
            self.authority_path, self.allowed_root, field="comparison authority"
        )
        _require_single_link_regular_file(self.authority_path, field="comparison authority")
        if self.database_path.exists():
            _require_single_link_regular_file(
                self.database_path, field="participant response database"
            )
        elif self._ready:
            raise ExpertStudyConfigurationError("participant response database disappeared")
        try:
            current_digest = _digest_bytes(self.authority_path.read_bytes())
        except OSError as exc:
            raise ExpertStudyConfigurationError("comparison set cannot be rechecked") from exc
        if current_digest != self.authority_digest:
            raise ExpertStudyConfigurationError("comparison set changed after preparation")

    def _validate_database_contract(self, connection: sqlite3.Connection) -> None:
        try:
            schema_digest = _digest_bytes(canonical_json_bytes(_historical_schema_rows(connection)))
            contracts = list(
                connection.execute("SELECT key,contract FROM hpc_schema_contract ORDER BY key")
            )
            authority = list(
                connection.execute(
                    "SELECT key,authority_digest,authority_version,participant_version,"
                    "response_version,debrief_version,lane,presentation_count "
                    "FROM hpc_authority ORDER BY key"
                )
            )
        except sqlite3.DatabaseError as exc:
            raise ExpertStudyConfigurationError("participant database cannot be verified") from exc
        expected_authority = (
            1,
            self.authority_digest,
            HISTORICAL_COMPARISON_AUTHORITY_VERSION,
            HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
            HISTORICAL_COMPARISON_RESPONSE_VERSION,
            HISTORICAL_COMPARISON_DEBRIEF_VERSION,
            "MECHANICS_PILOT",
            len(self.comparisons),
        )
        if schema_digest != HISTORICAL_COMPARISON_SCHEMA_SQL_DIGEST:
            raise ExpertStudyConfigurationError("participant database structure changed")
        if [tuple(item) for item in contracts] != [(1, _HISTORICAL_SCHEMA_CONTRACT)]:
            raise ExpertStudyConfigurationError("participant database contract is incompatible")
        if [tuple(item) for item in authority] != [expected_authority]:
            raise ExpertStudyConfigurationError(
                "participant database comparison set is incompatible"
            )

    def _ensure_schema(self) -> None:
        with self._lock:
            if self._ready:
                return
            self._validate_paths()
            self.database_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            connection = sqlite3.connect(self.database_path)
            try:
                existing = connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "AND name='hpc_schema_contract'"
                ).fetchone()
                other = connection.execute(
                    "SELECT name FROM sqlite_master WHERE name LIKE 'hpc_%'"
                ).fetchall()
                if other and existing is None:
                    raise ExpertStudyConfigurationError(
                        "participant database predates this contract"
                    )
                if existing is None:
                    connection.executescript(_HISTORICAL_SCHEMA_SQL)
                    connection.execute(
                        "INSERT INTO hpc_schema_contract VALUES(1,?)",
                        (_HISTORICAL_SCHEMA_CONTRACT,),
                    )
                    connection.execute(
                        "INSERT INTO hpc_authority VALUES(1,?,?,?,?,?,?,?)",
                        (
                            self.authority_digest,
                            HISTORICAL_COMPARISON_AUTHORITY_VERSION,
                            HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
                            HISTORICAL_COMPARISON_RESPONSE_VERSION,
                            HISTORICAL_COMPARISON_DEBRIEF_VERSION,
                            "MECHANICS_PILOT",
                            len(self.comparisons),
                        ),
                    )
                self._validate_database_contract(connection)
                connection.commit()
            finally:
                connection.close()
            self._ready = True

    def _connect(self) -> sqlite3.Connection:
        self._validate_paths()
        self._ensure_schema()
        self._validate_paths()
        connection = sqlite3.connect(self.database_path, timeout=5, isolation_level=None)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA busy_timeout = 5000")
            self._validate_database_contract(connection)
            connection.execute("PRAGMA journal_mode = WAL")
        except Exception:
            connection.close()
            raise
        return connection

    def prepare_session(
        self,
        *,
        participant_code: str,
        years_experience: int,
        experience_kinds: Sequence[ExpertExperienceKind],
        assessed_players_within_window: bool,
        conflict_declared: bool,
        conflict_note: str | None,
        consent_items: Mapping[str, bool],
    ) -> tuple[str, HistoricalComparisonStudySnapshot]:
        required = (
            "voluntary_participation",
            "local_pseudonymous_storage",
            "withdrawal_before_submission_understood",
            "immutable_after_submission_understood",
            "research_limitations_understood",
        )
        if any(consent_items.get(item) is not True for item in required):
            raise ExpertStudyPreparationError("Please accept every consent statement to continue.")
        if years_experience < 2:
            raise ExpertStudyPreparationError(
                "This trial requires at least two years of relevant professional football experience."
            )
        if (
            not experience_kinds
            or any(not isinstance(item, ExpertExperienceKind) for item in experience_kinds)
            or len(set(experience_kinds)) != len(experience_kinds)
        ):
            raise ExpertStudyPreparationError(
                "Select at least one relevant professional football role."
            )
        if not assessed_players_within_window:
            raise ExpertStudyPreparationError(
                "You must have assessed players professionally within the last five years."
            )
        if conflict_declared or conflict_declared != (conflict_note is not None):
            raise ExpertStudyPreparationError(
                "A current or recent responsibility for a shown player or club makes this trial ineligible."
            )
        try:
            code_digest = participant_code_digest(participant_code)
        except ValueError as exc:
            raise ExpertStudyPreparationError(
                "Use 6–32 uppercase letters, numbers or hyphens for the participant code."
            ) from exc
        participant_id = uuid5(_HISTORICAL_PARTICIPANT_NAMESPACE, code_digest)
        session_id = uuid5(_HISTORICAL_SESSION_NAMESPACE, code_digest)
        capability = secrets.token_urlsafe(32)
        consent = {
            "consent": dict(consent_items),
            "years_experience": years_experience,
            "experience_kinds": [item.value for item in experience_kinds],
            "assessed_players_within_window": assessed_players_within_window,
            "conflict_declared": conflict_declared,
            "conflict_note": conflict_note,
            "recorded_at": self._clock().isoformat(),
        }
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT 1 FROM hpc_sessions WHERE participant_id=?", (str(participant_id),)
            ).fetchone()
            if existing is not None:
                raise ExpertStudyConflictError(
                    "This participant code already has a trial session. Resume it in the original browser."
                )
            connection.execute(
                "INSERT INTO hpc_sessions VALUES(?,?,?,?,?,?,?)",
                (
                    str(session_id),
                    str(participant_id),
                    code_digest,
                    _digest_bytes(capability.encode()),
                    0,
                    0,
                    _canonical_text(consent),
                ),
            )
            for ordinal, comparison in enumerate(self._ordered_comparisons(code_digest), 1):
                presentation_id = uuid5(
                    _HISTORICAL_PRESENTATION_NAMESPACE, f"{session_id}:{ordinal}"
                )
                connection.execute(
                    "INSERT INTO hpc_presentations VALUES(?,?,?,?,?)",
                    (
                        str(session_id),
                        ordinal,
                        str(presentation_id),
                        secrets.token_urlsafe(24),
                        _v2_participant_safe_comparison_bytes(comparison).decode(),
                    ),
                )
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return capability, self.load_session(capability)

    def load_session(self, capability: str) -> HistoricalComparisonStudySnapshot:
        if type(capability) is not str or _CAPABILITY.fullmatch(capability) is None:
            raise ExpertStudyNotFoundError("Your saved local session is unavailable.")
        connection = self._connect()
        try:
            session = connection.execute(
                "SELECT * FROM hpc_sessions WHERE capability_digest=?",
                (_digest_bytes(capability.encode()),),
            ).fetchone()
            if session is None:
                raise ExpertStudyNotFoundError("Your saved local session is unavailable.")
            presentations = connection.execute(
                "SELECT * FROM hpc_presentations WHERE session_id=? ORDER BY ordinal",
                (session["session_id"],),
            ).fetchall()
            judgements = connection.execute(
                "SELECT * FROM hpc_judgements WHERE session_id=?",
                (session["session_id"],),
            ).fetchall()
            judgement_revisions = connection.execute(
                "SELECT * FROM hpc_judgement_revisions WHERE session_id=? "
                "ORDER BY presentation_id,ordinal",
                (session["session_id"],),
            ).fetchall()
            debriefs = connection.execute(
                "SELECT * FROM hpc_debriefs WHERE session_id=?",
                (session["session_id"],),
            ).fetchall()
            debrief_revisions = connection.execute(
                "SELECT * FROM hpc_debrief_revisions WHERE session_id=? ORDER BY ordinal",
                (session["session_id"],),
            ).fetchall()
            commands = connection.execute(
                "SELECT * FROM hpc_commands WHERE session_id=? ORDER BY ordinal",
                (session["session_id"],),
            ).fetchall()
            completions = connection.execute(
                "SELECT * FROM hpc_completions WHERE session_id=?",
                (session["session_id"],),
            ).fetchall()
        finally:
            connection.close()
        try:
            return self._reconstruct(
                session,
                presentations,
                judgements,
                judgement_revisions,
                debriefs,
                debrief_revisions,
                commands,
                completions,
            )
        except ExpertStudyIntegrityError:
            raise
        except (KeyError, TypeError, ValueError, ValidationError, json.JSONDecodeError) as exc:
            raise ExpertStudyIntegrityError(
                "Local participant evidence failed reconstruction."
            ) from exc

    def _reconstruct(
        self,
        session: sqlite3.Row,
        presentation_rows: Sequence[sqlite3.Row],
        judgement_rows: Sequence[sqlite3.Row],
        judgement_revision_rows: Sequence[sqlite3.Row],
        debrief_rows: Sequence[sqlite3.Row],
        debrief_revision_rows: Sequence[sqlite3.Row],
        command_rows: Sequence[sqlite3.Row],
        completion_rows: Sequence[sqlite3.Row],
    ) -> HistoricalComparisonStudySnapshot:
        session_id = UUID(session["session_id"])
        participant_id = UUID(session["participant_id"])
        code_digest = session["code_digest"]
        if (
            type(code_digest) is not str
            or _SHA256.fullmatch(code_digest) is None
            or participant_id != uuid5(_HISTORICAL_PARTICIPANT_NAMESPACE, code_digest)
            or session_id != uuid5(_HISTORICAL_SESSION_NAMESPACE, code_digest)
        ):
            raise ExpertStudyIntegrityError("Participant session identity changed.")
        consent = json.loads(session["consent_json"])
        if type(consent) is not dict or _canonical_text(consent) != session["consent_json"]:
            raise ExpertStudyIntegrityError("Participant consent bytes changed.")
        if len(presentation_rows) != len(self.comparisons):
            raise ExpertStudyIntegrityError("Comparison schedule count changed.")
        ordered_comparisons = self._ordered_comparisons(code_digest)
        comparisons: dict[str, ParticipantEvidenceComparisonV2] = {}
        tokens: list[str] = []
        for ordinal, (stored, comparison) in enumerate(
            zip(presentation_rows, ordered_comparisons, strict=True), 1
        ):
            presentation_id = uuid5(_HISTORICAL_PRESENTATION_NAMESPACE, f"{session_id}:{ordinal}")
            if (
                stored["ordinal"] != ordinal
                or stored["presentation_id"] != str(presentation_id)
                or stored["comparison_json"]
                != _v2_participant_safe_comparison_bytes(comparison).decode()
                or type(stored["token"]) is not str
                or _CAPABILITY.fullmatch(stored["token"]) is None
            ):
                raise ExpertStudyIntegrityError("Comparison schedule bytes changed.")
            comparisons[str(presentation_id)] = comparison
            tokens.append(stored["token"])
        if session["revision"] != len(command_rows):
            raise ExpertStudyIntegrityError("Participant action history is incomplete.")
        response_commands: dict[str, HistoricalComparisonJudgementV1] = {}
        debrief_commands: dict[str, HistoricalComparisonPilotDebriefV1] = {}
        response_text: dict[str, str] = {}
        command_ordinals: dict[str, int] = {}
        completion_commands: list[sqlite3.Row] = []
        for ordinal, command in enumerate(command_rows, 1):
            command_id = command["command_id"]
            kind = command["command_kind"]
            if (
                type(command_id) is not str
                or str(UUID(command_id)) != command_id
                or command["session_id"] != str(session_id)
                or command["ordinal"] != ordinal
                or type(command["request_digest"]) is not str
                or _SHA256.fullmatch(command["request_digest"]) is None
                or kind not in ("record", "debrief", "complete")
                or type(command["response_json"]) is not str
            ):
                raise ExpertStudyIntegrityError("Participant action history changed.")
            command_ordinals[command_id] = ordinal
            response_text[command_id] = command["response_json"]
            if kind == "record":
                command_response = HistoricalComparisonJudgementV1.model_validate_json(
                    command["response_json"]
                )
                bound_comparison = comparisons.get(str(command_response.presentation_id))
                if (
                    _contract_text(command_response) != command["response_json"]
                    or command_response.session_id != session_id
                    or command_response.participant_id != participant_id
                    or bound_comparison is None
                ):
                    raise ExpertStudyIntegrityError("Saved comparison response changed.")
                validate_response_comparison_v2(command_response, bound_comparison)
                response_commands[command_id] = command_response
            elif kind == "debrief":
                command_debrief = HistoricalComparisonPilotDebriefV1.model_validate_json(
                    command["response_json"]
                )
                if (
                    _contract_text(command_debrief) != command["response_json"]
                    or command_debrief.session_id != session_id
                    or command_debrief.participant_id != participant_id
                ):
                    raise ExpertStudyIntegrityError("Saved pilot feedback changed.")
                debrief_commands[command_id] = command_debrief
            else:
                if ordinal != len(command_rows):
                    raise ExpertStudyIntegrityError("Completion action is not final.")
                completion_commands.append(command)
        used_response_commands: set[str] = set()
        histories: dict[str, list[sqlite3.Row]] = {}
        for revision in judgement_revision_rows:
            presentation_id = revision["presentation_id"]
            history = histories.setdefault(presentation_id, [])
            command_id = revision["command_id"]
            revision_response = response_commands.get(command_id)
            if (
                revision["session_id"] != str(session_id)
                or presentation_id not in comparisons
                or revision["ordinal"] != len(history) + 1
                or command_id in used_response_commands
                or revision_response is None
                or str(revision_response.presentation_id) != presentation_id
                or revision["command_ordinal"] != command_ordinals[command_id]
                or revision["judgement_json"] != response_text[command_id]
            ):
                raise ExpertStudyIntegrityError("Comparison response history changed.")
            history.append(revision)
            used_response_commands.add(command_id)
        if used_response_commands != set(response_commands):
            raise ExpertStudyIntegrityError("A comparison response revision is missing.")
        if len(judgement_rows) != len({item["presentation_id"] for item in judgement_rows}):
            raise ExpertStudyIntegrityError("Saved comparison response identity is ambiguous.")
        if {item["presentation_id"] for item in judgement_rows} != set(histories):
            raise ExpertStudyIntegrityError("Current comparison responses and history differ.")
        by_presentation: dict[str, HistoricalComparisonJudgementV1] = {}
        for stored in judgement_rows:
            current_response = HistoricalComparisonJudgementV1.model_validate_json(
                stored["judgement_json"]
            )
            current_comparison = comparisons.get(stored["presentation_id"])
            if (
                current_comparison is None
                or _contract_text(current_response) != stored["judgement_json"]
                or str(current_response.presentation_id) != stored["presentation_id"]
                or stored["judgement_json"]
                != histories[stored["presentation_id"]][-1]["judgement_json"]
            ):
                raise ExpertStudyIntegrityError("Current comparison response changed.")
            validate_response_comparison_v2(current_response, current_comparison)
            by_presentation[stored["presentation_id"]] = current_response
        judgements = tuple(
            by_presentation[item["presentation_id"]]
            for item in presentation_rows
            if item["presentation_id"] in by_presentation
        )
        if len(debrief_rows) > 1:
            raise ExpertStudyIntegrityError("Pilot feedback identity is ambiguous.")
        used_debrief_commands: set[str] = set()
        debrief_history: list[sqlite3.Row] = []
        for revision in debrief_revision_rows:
            command_id = revision["command_id"]
            revision_debrief = debrief_commands.get(command_id)
            if (
                revision["session_id"] != str(session_id)
                or revision["ordinal"] != len(debrief_history) + 1
                or command_id in used_debrief_commands
                or revision_debrief is None
                or revision["command_ordinal"] != command_ordinals[command_id]
                or revision["debrief_json"] != response_text[command_id]
            ):
                raise ExpertStudyIntegrityError("Pilot feedback history changed.")
            debrief_history.append(revision)
            used_debrief_commands.add(command_id)
        if used_debrief_commands != set(debrief_commands):
            raise ExpertStudyIntegrityError("A pilot feedback revision is missing.")
        current_debrief: HistoricalComparisonPilotDebriefV1 | None = None
        if debrief_rows:
            if not debrief_history:
                raise ExpertStudyIntegrityError("Pilot feedback history is missing.")
            current_debrief = HistoricalComparisonPilotDebriefV1.model_validate_json(
                debrief_rows[0]["debrief_json"]
            )
            if (
                _contract_text(current_debrief) != debrief_rows[0]["debrief_json"]
                or debrief_rows[0]["debrief_json"] != debrief_history[-1]["debrief_json"]
            ):
                raise ExpertStudyIntegrityError("Current pilot feedback changed.")
        elif debrief_history:
            raise ExpertStudyIntegrityError("Current pilot feedback is missing.")
        complete = session["complete"] == 1
        if session["complete"] not in (0, 1) or complete != (len(completion_rows) == 1):
            raise ExpertStudyIntegrityError("Completion state and local receipt differ.")
        if complete != (len(completion_commands) == 1):
            raise ExpertStudyIntegrityError("Completion action history is incompatible.")
        completed_at: str | None = None
        receipt_digest: str | None = None
        if complete:
            receipt_row = completion_rows[0]
            receipt = json.loads(receipt_row["receipt_json"])
            expected_keys = {
                "receipt_version",
                "session_id",
                "authority_digest",
                "response_digests",
                "debrief_digest",
                "completed_at",
                "immutable",
            }
            if (
                type(receipt) is not dict
                or set(receipt) != expected_keys
                or _canonical_text(receipt) != receipt_row["receipt_json"]
                or _digest_bytes(receipt_row["receipt_json"].encode())
                != receipt_row["receipt_digest"]
                or receipt["receipt_version"]
                != "historical-player-comparison-completion-receipt-v1"
                or receipt["session_id"] != str(session_id)
                or receipt["authority_digest"] != self.authority_digest
                or receipt["response_digests"] != [item.judgement_digest for item in judgements]
                or current_debrief is None
                or receipt["debrief_digest"] != current_debrief.debrief_digest
                or receipt["completed_at"] != receipt_row["completed_at"]
                or receipt["immutable"] is not True
                or completion_commands[0]["response_json"] != receipt_row["receipt_json"]
                or len(judgements) != len(self.comparisons)
            ):
                raise ExpertStudyIntegrityError("Local completion receipt failed reconstruction.")
            completed_at = receipt_row["completed_at"]
            receipt_digest = receipt_row["receipt_digest"]
        return HistoricalComparisonStudySnapshot(
            session_id=session_id,
            participant_id=participant_id,
            revision=session["revision"],
            presentation_tokens=tuple(tokens),
            judgements=judgements,
            debrief=current_debrief,
            complete=complete,
            completed_at=completed_at,
            receipt_digest=receipt_digest,
        )

    def task(self, capability: str) -> tuple[str, ParticipantEvidenceComparisonV2, int, int] | None:
        snapshot = self.load_session(capability)
        if snapshot.complete:
            return None
        answered = {item.presentation_id for item in snapshot.judgements}
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT ordinal,presentation_id,token,comparison_json FROM hpc_presentations "
                "WHERE session_id=? ORDER BY ordinal",
                (str(snapshot.session_id),),
            ).fetchall()
        finally:
            connection.close()
        for row in rows:
            if UUID(row["presentation_id"]) not in answered:
                return (
                    row["token"],
                    ParticipantEvidenceComparisonV2.model_validate_json(row["comparison_json"]),
                    row["ordinal"],
                    len(rows),
                )
        return None

    def review_tasks(
        self, capability: str
    ) -> tuple[
        tuple[str, HistoricalComparisonJudgementV1, int, ParticipantEvidenceComparisonV2], ...
    ]:
        snapshot = self.load_session(capability)
        if snapshot.complete:
            return ()
        connection = self._connect()
        try:
            rows = connection.execute(
                "SELECT p.ordinal,p.token,p.comparison_json,j.judgement_json "
                "FROM hpc_presentations p JOIN hpc_judgements j "
                "ON j.session_id=p.session_id AND j.presentation_id=p.presentation_id "
                "WHERE p.session_id=? ORDER BY p.ordinal",
                (str(snapshot.session_id),),
            ).fetchall()
        finally:
            connection.close()
        return tuple(
            (
                row["token"],
                HistoricalComparisonJudgementV1.model_validate_json(row["judgement_json"]),
                row["ordinal"],
                ParticipantEvidenceComparisonV2.model_validate_json(row["comparison_json"]),
            )
            for row in rows
        )

    def _replay(self, session_id: UUID, command_id: UUID, kind: str, request_digest: str) -> bool:
        connection = self._connect()
        try:
            row = connection.execute(
                "SELECT session_id,command_kind,request_digest FROM hpc_commands "
                "WHERE command_id=?",
                (str(command_id),),
            ).fetchone()
            if row is None:
                return False
            if tuple(row) != (str(session_id), kind, request_digest):
                raise ExpertStudyConflictError(
                    "This browser action was already used for different information."
                )
            return True
        finally:
            connection.close()

    @staticmethod
    def _replay_in_transaction(
        connection: sqlite3.Connection,
        session_id: UUID,
        command_id: UUID,
        kind: str,
        request_digest: str,
    ) -> bool:
        row = connection.execute(
            "SELECT session_id,command_kind,request_digest FROM hpc_commands WHERE command_id=?",
            (str(command_id),),
        ).fetchone()
        if row is None:
            return False
        if tuple(row) != (str(session_id), kind, request_digest):
            raise ExpertStudyConflictError(
                "This browser action was already used for different information."
            )
        return True

    def record(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
        presentation_token: str,
        state: JudgementState,
        evidence_sufficiency: EvidenceSufficiencyV2,
        assessment_basis: AssessmentBasisV2,
        relevance_rating: int | None,
        confidence: int | None,
        evidence_gap: EvidenceGapV2 | None,
        citation_family_ids: Sequence[str],
        statistics_helped: bool,
        explanation: str | None,
    ) -> HistoricalComparisonStudySnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        snapshot = self.load_session(capability)
        if self._replay(snapshot.session_id, command_id, "record", request_digest):
            return self.load_session(capability)
        if snapshot.complete:
            raise ExpertStudyConflictError("Your final submission cannot be changed.")
        if expected_revision != snapshot.revision:
            raise ExpertStudyConflictError("This page is out of date. Reload before saving.")
        connection = self._connect()
        try:
            presentation = connection.execute(
                "SELECT * FROM hpc_presentations WHERE session_id=? AND token=?",
                (str(snapshot.session_id), presentation_token),
            ).fetchone()
            if presentation is None:
                raise ExpertStudyNotFoundError("This comparison is unavailable.")
            comparison = ParticipantEvidenceComparisonV2.model_validate_json(
                presentation["comparison_json"]
            )
            admissible_citations = {
                family.family_id
                for panel in (comparison.exemplar, comparison.candidate)
                for family in panel.independent_descriptors
                if family.mandatory_for_selected_rubric
            }
            if len(set(citation_family_ids)) != len(citation_family_ids) or any(
                item not in admissible_citations for item in citation_family_ids
            ):
                raise ExpertStudyConflictError(
                    "Choose helpful information only from the sections shown on this comparison."
                )
            values: dict[str, object] = {
                "schema_version": 3,
                "response_version": HISTORICAL_COMPARISON_RESPONSE_VERSION,
                "judgement_id": uuid5(
                    _HISTORICAL_JUDGEMENT_NAMESPACE,
                    f"{snapshot.session_id}:{presentation['presentation_id']}",
                ),
                "session_id": snapshot.session_id,
                "participant_id": snapshot.participant_id,
                "presentation_id": UUID(presentation["presentation_id"]),
                "query_id": uuid5(NAMESPACE_URL, comparison.comparison_digest + ":query"),
                "candidate_id": uuid5(
                    NAMESPACE_URL, comparison.candidate.bundle_digest + ":candidate"
                ),
                "comparison_digest": comparison.comparison_digest,
                "position_code": comparison.position_code,
                "md_subrubric": comparison.md_subrubric,
                "state": state,
                "evidence_sufficiency": evidence_sufficiency,
                "assessment_basis": assessment_basis,
                "relevance_rating": relevance_rating,
                "confidence": confidence,
                "evidence_gap": evidence_gap,
                "cited_independent_family_ids": tuple(citation_family_ids),
                "statistics_used_to_find_similar_players_helped": statistics_helped,
                "explanation": explanation,
                "recorded_at": self._clock(),
            }
            values["judgement_digest"] = canonical_research_digest(
                _JSON_OBJECT_ADAPTER.dump_python(values, mode="json")
            )
            judgement = HistoricalComparisonJudgementV1.model_validate(values)
            validate_response_comparison_v2(judgement, comparison)
            encoded = _contract_text(judgement)
            connection.execute("BEGIN IMMEDIATE")
            if self._replay_in_transaction(
                connection, snapshot.session_id, command_id, "record", request_digest
            ):
                connection.commit()
                return self.load_session(capability)
            current = connection.execute(
                "SELECT revision,complete FROM hpc_sessions WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            if current["revision"] != expected_revision or current["complete"]:
                raise ExpertStudyConflictError("This page is out of date. Reload before saving.")
            prior = connection.execute(
                "SELECT 1 FROM hpc_judgements WHERE session_id=? AND presentation_id=?",
                (str(snapshot.session_id), presentation["presentation_id"]),
            ).fetchone()
            revision_ordinal = (
                connection.execute(
                    "SELECT count(*) FROM hpc_judgement_revisions "
                    "WHERE session_id=? AND presentation_id=?",
                    (str(snapshot.session_id), presentation["presentation_id"]),
                ).fetchone()[0]
                + 1
            )
            connection.execute(
                "INSERT INTO hpc_commands VALUES(?,?,?,?,?,?)",
                (
                    str(command_id),
                    str(snapshot.session_id),
                    expected_revision + 1,
                    "record",
                    request_digest,
                    encoded,
                ),
            )
            connection.execute(
                "INSERT INTO hpc_judgement_revisions VALUES(?,?,?,?,?,?)",
                (
                    str(snapshot.session_id),
                    presentation["presentation_id"],
                    revision_ordinal,
                    str(command_id),
                    expected_revision + 1,
                    encoded,
                ),
            )
            if prior is None:
                connection.execute(
                    "INSERT INTO hpc_judgements VALUES(?,?,?)",
                    (str(snapshot.session_id), presentation["presentation_id"], encoded),
                )
            else:
                connection.execute(
                    "UPDATE hpc_judgements SET judgement_json=? "
                    "WHERE session_id=? AND presentation_id=?",
                    (encoded, str(snapshot.session_id), presentation["presentation_id"]),
                )
            connection.execute(
                "UPDATE hpc_sessions SET revision=revision+1 WHERE session_id=?",
                (str(snapshot.session_id),),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            if self._replay(snapshot.session_id, command_id, "record", request_digest):
                return self.load_session(capability)
            raise ExpertStudyConflictError("The response could not be saved safely.") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.load_session(capability)

    def record_debrief(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
        names_or_minutes_only: bool,
        names_or_minutes_details: str | None,
        position_lacked_evidence: bool,
        position_evidence_details: str | None,
        interface_unclear: bool,
        interface_clarity_details: str | None,
        system_preference_revealed: bool,
        preference_revelation_details: str | None,
    ) -> HistoricalComparisonStudySnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        snapshot = self.load_session(capability)
        if self._replay(snapshot.session_id, command_id, "debrief", request_digest):
            return self.load_session(capability)
        if snapshot.complete:
            raise ExpertStudyConflictError("Your final submission cannot be changed.")
        if len(snapshot.judgements) != len(snapshot.presentation_tokens):
            raise ExpertStudyConflictError(
                "Complete every player comparison before answering the pilot feedback."
            )
        if expected_revision != snapshot.revision:
            raise ExpertStudyConflictError("This page is out of date. Reload before saving.")
        values: dict[str, object] = {
            "schema_version": 1,
            "debrief_version": HISTORICAL_COMPARISON_DEBRIEF_VERSION,
            "debrief_id": uuid5(_HISTORICAL_DEBRIEF_NAMESPACE, str(snapshot.session_id)),
            "session_id": snapshot.session_id,
            "participant_id": snapshot.participant_id,
            "names_or_minutes_only_for_any_comparison": names_or_minutes_only,
            "names_or_minutes_only_details": names_or_minutes_details,
            "any_position_lacked_enough_evidence": position_lacked_evidence,
            "position_evidence_details": position_evidence_details,
            "any_label_chart_warning_or_navigation_unclear": interface_unclear,
            "interface_clarity_details": interface_clarity_details,
            "form_appeared_to_reveal_system_preference": system_preference_revealed,
            "preference_revelation_details": preference_revelation_details,
            "recorded_at": self._clock(),
        }
        values["debrief_digest"] = canonical_research_digest(
            _JSON_OBJECT_ADAPTER.dump_python(values, mode="json")
        )
        debrief = HistoricalComparisonPilotDebriefV1.model_validate(values)
        encoded = _contract_text(debrief)
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            if self._replay_in_transaction(
                connection, snapshot.session_id, command_id, "debrief", request_digest
            ):
                connection.commit()
                return self.load_session(capability)
            current = connection.execute(
                "SELECT revision,complete FROM hpc_sessions WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            if current["revision"] != expected_revision or current["complete"]:
                raise ExpertStudyConflictError("This page is out of date. Reload before saving.")
            prior = connection.execute(
                "SELECT 1 FROM hpc_debriefs WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            revision_ordinal = (
                connection.execute(
                    "SELECT count(*) FROM hpc_debrief_revisions WHERE session_id=?",
                    (str(snapshot.session_id),),
                ).fetchone()[0]
                + 1
            )
            connection.execute(
                "INSERT INTO hpc_commands VALUES(?,?,?,?,?,?)",
                (
                    str(command_id),
                    str(snapshot.session_id),
                    expected_revision + 1,
                    "debrief",
                    request_digest,
                    encoded,
                ),
            )
            connection.execute(
                "INSERT INTO hpc_debrief_revisions VALUES(?,?,?,?,?)",
                (
                    str(snapshot.session_id),
                    revision_ordinal,
                    str(command_id),
                    expected_revision + 1,
                    encoded,
                ),
            )
            if prior is None:
                connection.execute(
                    "INSERT INTO hpc_debriefs VALUES(?,?)",
                    (str(snapshot.session_id), encoded),
                )
            else:
                connection.execute(
                    "UPDATE hpc_debriefs SET debrief_json=? WHERE session_id=?",
                    (encoded, str(snapshot.session_id)),
                )
            connection.execute(
                "UPDATE hpc_sessions SET revision=revision+1 WHERE session_id=?",
                (str(snapshot.session_id),),
            )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            if self._replay(snapshot.session_id, command_id, "debrief", request_digest):
                return self.load_session(capability)
            raise ExpertStudyConflictError("The pilot feedback could not be saved safely.") from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.load_session(capability)

    def complete(
        self,
        *,
        capability: str,
        command_id: UUID,
        expected_revision: int,
        request_digest: str,
    ) -> HistoricalComparisonStudySnapshot:
        _validate_command_inputs(capability, command_id, expected_revision, request_digest)
        snapshot = self.load_session(capability)
        if self._replay(snapshot.session_id, command_id, "complete", request_digest):
            return self.load_session(capability)
        if (
            expected_revision != snapshot.revision
            or len(snapshot.judgements) != len(snapshot.presentation_tokens)
            or snapshot.debrief is None
        ):
            raise ExpertStudyConflictError(
                "Review every comparison and answer all pilot-feedback questions before submitting."
            )
        connection = self._connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            if self._replay_in_transaction(
                connection, snapshot.session_id, command_id, "complete", request_digest
            ):
                connection.commit()
                return self.load_session(capability)
            current = connection.execute(
                "SELECT revision,complete FROM hpc_sessions WHERE session_id=?",
                (str(snapshot.session_id),),
            ).fetchone()
            if (
                current is None
                or current["revision"] != expected_revision
                or current["complete"] != 0
            ):
                raise ExpertStudyConflictError(
                    "This page is out of date. Reload before submitting."
                )
            receipt = {
                "receipt_version": "historical-player-comparison-completion-receipt-v1",
                "session_id": str(snapshot.session_id),
                "authority_digest": self.authority_digest,
                "response_digests": [item.judgement_digest for item in snapshot.judgements],
                "debrief_digest": snapshot.debrief.debrief_digest,
                "completed_at": self._clock().isoformat(),
                "immutable": True,
            }
            receipt_text = _canonical_text(receipt)
            receipt_digest = _digest_bytes(receipt_text.encode())
            connection.execute(
                "INSERT INTO hpc_completions VALUES(?,?,?,?)",
                (
                    str(snapshot.session_id),
                    receipt_text,
                    receipt_digest,
                    receipt["completed_at"],
                ),
            )
            connection.execute(
                "INSERT INTO hpc_commands VALUES(?,?,?,?,?,?)",
                (
                    str(command_id),
                    str(snapshot.session_id),
                    expected_revision + 1,
                    "complete",
                    request_digest,
                    receipt_text,
                ),
            )
            updated = connection.execute(
                "UPDATE hpc_sessions SET complete=1,revision=revision+1 "
                "WHERE session_id=? AND complete=0 AND revision=?",
                (str(snapshot.session_id), expected_revision),
            )
            if updated.rowcount != 1:
                raise ExpertStudyConflictError(
                    "This page is out of date. Reload before submitting."
                )
            connection.commit()
        except sqlite3.IntegrityError as exc:
            connection.rollback()
            if self._replay(snapshot.session_id, command_id, "complete", request_digest):
                return self.load_session(capability)
            raise ExpertStudyConflictError(
                "The final submission could not be saved safely."
            ) from exc
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
        return self.load_session(capability)


__all__ += [
    "HISTORICAL_COMPARISON_AUTHORITY_VERSION",
    "HISTORICAL_COMPARISON_DEBRIEF_VERSION",
    "HISTORICAL_COMPARISON_PARTICIPANT_VERSION",
    "HISTORICAL_COMPARISON_RESPONSE_VERSION",
    "HISTORICAL_COMPARISON_SCHEMA_SQL_DIGEST",
    "HistoricalComparisonPilotStore",
    "HistoricalComparisonStudySnapshot",
]
