"""Source-complete, sidecar-free W04 Wyscout initial identity runtime."""

from __future__ import annotations

import hashlib
import io
import json
import os
import stat
from collections import defaultdict
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid5

import yaml  # type: ignore[import-untyped]
from pydantic import ValidationError

from scouting.contracts.evidence import IdentityMatchMethod, SourceIdentity
from scouting.contracts.primitives import TenantContext
from scouting.contracts.wyscout_data import (
    IDENTITY_ACCEPTANCE_SHA256,
    IDENTITY_CANDIDATE_SHA256,
    SOURCE_MANIFEST_ID,
    SOURCE_MANIFEST_SHA256,
    SOURCE_RELEASE,
    TENANT_ID,
    SourceRecordKind,
    WyscoutSourceRowReference,
    canonical_source_uuid,
)
from scouting.contracts.wyscout_identity import (
    IDENTITY_ACCEPTANCE_ID,
    IDENTITY_ACCEPTED_AT,
    IDENTITY_DECIDED_AT,
    IDENTITY_DECISION_ID,
    IDENTITY_DECISION_SHA256,
    IDENTITY_REVIEW_ID,
    IDENTITY_REVIEW_PATH,
    IDENTITY_REVIEW_SHA256,
    IDENTITY_REVIEWED_AT,
    IDENTITY_RULESET_ID,
    W04IdentityCrosswalkRow,
    WyscoutIdentityBundle,
    WyscoutIdentityClassificationMethod,
    WyscoutIdentityEffectiveState,
    WyscoutIdentityEntityKind,
    WyscoutIdentityQueueItem,
    WyscoutIdentityQueueStatus,
    WyscoutIdentityReviewQueue,
    WyscoutIdentityState,
    crosswalk_evidence_digest,
    crosswalk_row_identity,
    identity_bundle_id,
    queue_item_identity,
)
from scouting.sources import wyscout_manifest as bridge
from scouting.sources.wyscout_completion_index import _canonical_value_bytes
from scouting.storage.formats import canonical_json_bytes

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SOURCE_ROOT_RELATIVE = Path("data/source/wyscout/v5")
_MANIFEST_ROOT_RELATIVE = Path("data/manifests")
_IDENTITY_ROOT_RELATIVE = Path("data/working/wyscout/v5/identity")
_SOURCE_MANIFEST_RELATIVE_PATH = (
    "wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
)
_SOURCE_MANIFEST_SHA256 = SOURCE_MANIFEST_SHA256
_COMPLETION_MANIFEST_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
_RULESET_PHYSICAL_SHA256 = "8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547"
_CHUNK_SIZE = 1024 * 1024
_FILE_MODE = 0o600


class WyscoutIdentityError(RuntimeError):
    """Base fail-closed identity runtime error."""


class WyscoutIdentityPathError(WyscoutIdentityError):
    """A declared source, authority, or identity artifact path is unsafe."""


class WyscoutIdentityConflictError(WyscoutIdentityError):
    """An immutable identity address already contains unequal bytes."""


@dataclass(frozen=True, slots=True)
class _JsonMemberSpec:
    path: str
    sha256: str
    size_bytes: int
    row_count: int
    record_kind: SourceRecordKind


_MASTER_MEMBERS = (
    _JsonMemberSpec(
        "objects/competitions.json",
        "39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1",
        1_209,
        7,
        SourceRecordKind.COMPETITION,
    ),
    _JsonMemberSpec(
        "objects/teams.json",
        "9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d",
        27_404,
        142,
        SourceRecordKind.TEAM,
    ),
    _JsonMemberSpec(
        "objects/players.json",
        "877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e",
        1_737_347,
        3_603,
        SourceRecordKind.PLAYER,
    ),
)

_MATCH_MEMBERS = tuple(
    _JsonMemberSpec(path, digest, size, rows, SourceRecordKind.MATCH)
    for path, digest, size, rows in (
        (
            "archive-members/matches_England.json",
            "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
            1_694_720,
            380,
        ),
        (
            "archive-members/matches_France.json",
            "851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea",
            1_707_222,
            380,
        ),
        (
            "archive-members/matches_Germany.json",
            "6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9",
            1_377_328,
            306,
        ),
        (
            "archive-members/matches_Italy.json",
            "afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725",
            2_019_196,
            380,
        ),
        (
            "archive-members/matches_Spain.json",
            "9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce",
            1_705_380,
            380,
        ),
    )
)

_ACTION_MEMBERS = tuple(
    _JsonMemberSpec(path, digest, size, rows, SourceRecordKind.ACTION)
    for path, digest, size, rows in (
        (
            "archive-members/events_England.json",
            "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
            188_888_614,
            643_150,
        ),
        (
            "archive-members/events_France.json",
            "18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317",
            186_374_196,
            632_807,
        ),
        (
            "archive-members/events_Germany.json",
            "2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3",
            152_916_631,
            519_407,
        ),
        (
            "archive-members/events_Italy.json",
            "b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84",
            190_544_685,
            647_372,
        ),
        (
            "archive-members/events_Spain.json",
            "b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154",
            184_164_406,
            628_659,
        ),
    )
)

_KIND_MAP = {
    SourceRecordKind.COMPETITION: WyscoutIdentityEntityKind.COMPETITION,
    SourceRecordKind.TEAM: WyscoutIdentityEntityKind.TEAM,
    SourceRecordKind.PLAYER: WyscoutIdentityEntityKind.PLAYER,
    SourceRecordKind.MATCH: WyscoutIdentityEntityKind.MATCH,
}


@dataclass(frozen=True, slots=True)
class WyscoutIdentityBuild:
    """Exact source-derived queue and bundle canonical preimages."""

    queue: WyscoutIdentityReviewQueue
    queue_bytes: bytes
    queue_sha256: str
    queue_relative_path: str
    bundle: WyscoutIdentityBundle
    bundle_bytes: bytes
    bundle_sha256: str
    bundle_id: UUID
    bundle_relative_path: str


@dataclass(frozen=True, slots=True)
class WyscoutIdentityMaterialization:
    """Materialized and independently reopened initial identity artifacts."""

    build: WyscoutIdentityBuild
    queue_created: bool
    bundle_created: bool


def _strict_positive(value: object, *, context: str) -> int:
    if type(value) is not int or value <= 0:
        raise WyscoutIdentityError(f"{context} must be a strict positive integer")
    return value


def _strict_nonnegative(value: object, *, context: str) -> int:
    if type(value) is not int or value < 0:
        raise WyscoutIdentityError(f"{context} must be a strict non-negative integer")
    return value


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WyscoutIdentityError(f"source JSON repeats key {key!r}")
        result[key] = value
    return result


def _read_exact_bytes(root: Path, relative_path: str) -> bytes:
    try:
        with bridge._open_regular_beneath(root, relative_path) as descriptor:
            before = os.fstat(descriptor)
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, _CHUNK_SIZE):
                chunks.append(chunk)
            after = os.fstat(descriptor)
    except (OSError, bridge.WyscoutSourceManifestError) as exc:
        raise WyscoutIdentityPathError(f"cannot read exact path {relative_path}") from exc
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutIdentityError(f"file changed during read: {relative_path}")
    return b"".join(chunks)


def _verify_digest(payload: bytes, expected: str, *, context: str) -> None:
    if hashlib.sha256(payload).hexdigest() != expected:
        raise WyscoutIdentityError(f"{context} SHA-256 drifted")


def _verify_authorities(manifest_root: Path) -> None:
    manifest = _read_exact_bytes(manifest_root, _SOURCE_MANIFEST_RELATIVE_PATH)
    _verify_digest(manifest, _SOURCE_MANIFEST_SHA256, context="source manifest")
    try:
        source_doc = json.loads(manifest, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutIdentityError("source manifest is not strict JSON") from exc
    if (
        type(source_doc) is not dict
        or source_doc.get("manifest_id") != str(SOURCE_MANIFEST_ID)
        or source_doc.get("tenant_context") != {"club_id": None, "tenant_id": str(TENANT_ID)}
    ):
        raise WyscoutIdentityError("source manifest identity/tenant drifted")

    completion = _read_exact_bytes(
        _PROJECT_ROOT / _SOURCE_ROOT_RELATIVE, "completion-manifest.json"
    )
    _verify_digest(completion, _COMPLETION_MANIFEST_SHA256, context="completion manifest")
    try:
        completion_doc = json.loads(completion, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutIdentityError("completion manifest is not strict JSON") from exc
    if canonical_json_bytes(completion_doc) != completion:
        raise WyscoutIdentityError("completion manifest is not canonical")

    decision_path = "reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json"
    ruleset_path = "configs/schema/wyscout-v5-identity-ruleset-v1.yaml"
    review_path = IDENTITY_REVIEW_PATH
    acceptance_path = "reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json"
    decision = _read_exact_bytes(_PROJECT_ROOT, decision_path)
    ruleset = _read_exact_bytes(_PROJECT_ROOT, ruleset_path)
    review = _read_exact_bytes(_PROJECT_ROOT, review_path)
    acceptance = _read_exact_bytes(_PROJECT_ROOT, acceptance_path)
    _verify_digest(decision, IDENTITY_DECISION_SHA256, context="identity decision")
    _verify_digest(ruleset, _RULESET_PHYSICAL_SHA256, context="identity ruleset")
    _verify_digest(review, IDENTITY_REVIEW_SHA256, context="identity review")
    _verify_digest(acceptance, IDENTITY_ACCEPTANCE_SHA256, context="identity acceptance")
    try:
        decision_doc = json.loads(decision, object_pairs_hook=_reject_duplicate_keys)
        ruleset_doc = yaml.safe_load(ruleset)
        acceptance_doc = json.loads(acceptance, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise WyscoutIdentityError("identity authority graph cannot be parsed") from exc
    if type(ruleset_doc) is not dict:
        raise WyscoutIdentityError("identity ruleset must be one mapping")
    if hashlib.sha256(canonical_json_bytes(ruleset_doc)).hexdigest() != IDENTITY_CANDIDATE_SHA256:
        raise WyscoutIdentityError("identity ruleset canonical SHA-256 drifted")
    if (
        type(decision_doc) is not dict
        or type(acceptance_doc) is not dict
        or decision_doc.get("decision_id") != IDENTITY_DECISION_ID
        or ruleset_doc.get("ruleset_id") != IDENTITY_RULESET_ID
        or ruleset_doc.get("decision_sha256") != IDENTITY_DECISION_SHA256
        or acceptance_doc.get("acceptance_id") != IDENTITY_ACCEPTANCE_ID
        or acceptance_doc.get("candidate_sha256") != IDENTITY_CANDIDATE_SHA256
        or acceptance_doc.get("review_id") != IDENTITY_REVIEW_ID
        or acceptance_doc.get("review_physical_sha256") != IDENTITY_REVIEW_SHA256
        or acceptance_doc.get("review_recommendation") != "PASS"
    ):
        raise WyscoutIdentityError("identity authority graph edges drifted")


def _iter_json_values(stream: io.TextIOBase) -> Iterator[dict[str, object]]:
    decoder = json.JSONDecoder(
        parse_float=Decimal,
        object_pairs_hook=_reject_duplicate_keys,
    )
    buffer = ""
    position = 0
    eof = False

    def fill() -> bool:
        nonlocal buffer, position, eof
        if eof:
            return False
        if position:
            buffer = buffer[position:]
            position = 0
        chunk = stream.read(_CHUNK_SIZE)
        if chunk == "":
            eof = True
            return False
        buffer += chunk
        return True

    def skip_space() -> None:
        nonlocal position
        while True:
            while position < len(buffer) and buffer[position] in " \t\r\n":
                position += 1
            if position < len(buffer) or not fill():
                return

    skip_space()
    if position >= len(buffer) or buffer[position] != "[":
        raise WyscoutIdentityError("source JSON must be one top-level array")
    position += 1
    first = True
    while True:
        skip_space()
        if position >= len(buffer):
            raise WyscoutIdentityError("source JSON array is incomplete")
        if buffer[position] == "]":
            position += 1
            break
        if not first:
            if buffer[position] != ",":
                raise WyscoutIdentityError("source JSON array separator is invalid")
            position += 1
            skip_space()
        while True:
            try:
                value, end = decoder.raw_decode(buffer, position)
                break
            except json.JSONDecodeError as exc:
                if not fill():
                    raise WyscoutIdentityError("source JSON row is malformed") from exc
        if type(value) is not dict:
            raise WyscoutIdentityError("source JSON rows must be objects")
        position = end
        first = False
        yield cast(dict[str, object], value)
    remainder = buffer[position:] + stream.read()
    if remainder.strip():
        raise WyscoutIdentityError("source JSON has trailing content")


def _iter_verified_rows(
    root: Path, spec: _JsonMemberSpec
) -> Iterator[tuple[int, dict[str, object]]]:
    try:
        with bridge._open_regular_beneath(root, spec.path) as descriptor:
            before = os.fstat(descriptor)
            digest = hashlib.sha256()
            size = 0
            while chunk := os.read(descriptor, _CHUNK_SIZE):
                size += len(chunk)
                if size > spec.size_bytes:
                    raise WyscoutIdentityError(f"source size exceeds authority: {spec.path}")
                digest.update(chunk)
            if size != spec.size_bytes or digest.hexdigest() != spec.sha256:
                raise WyscoutIdentityError(f"source member bytes drifted: {spec.path}")
            os.lseek(descriptor, 0, os.SEEK_SET)
            duplicate = os.dup(descriptor)
            count = 0
            try:
                with os.fdopen(duplicate, "rb", closefd=True) as binary:
                    with io.TextIOWrapper(binary, encoding="utf-8", errors="strict") as text:
                        for count, row in enumerate(_iter_json_values(text), start=1):
                            yield count - 1, row
            finally:
                # fdopen owns ``duplicate`` unless construction failed.
                try:
                    os.close(duplicate)
                except OSError:
                    pass
            after = os.fstat(descriptor)
    except UnicodeError as exc:
        raise WyscoutIdentityError(f"source member is not strict UTF-8: {spec.path}") from exc
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutIdentityError(f"source member changed during read: {spec.path}")
    if count != spec.row_count:
        raise WyscoutIdentityError(f"source member row count drifted: {spec.path}")


def _source_ref(
    spec: _JsonMemberSpec,
    ordinal: int,
    row: Mapping[str, object],
) -> WyscoutSourceRowReference:
    raw_digest = hashlib.sha256(_canonical_value_bytes(dict(row))).hexdigest()
    return WyscoutSourceRowReference(
        source_manifest_id=SOURCE_MANIFEST_ID,
        completion_relative_path=spec.path,
        source_sha256=spec.sha256,
        source_record_ordinal=ordinal,
        record_kind=spec.record_kind,
        raw_record_sha256=raw_digest,
    )


def _sorted_refs(
    rows: Sequence[WyscoutSourceRowReference],
) -> tuple[WyscoutSourceRowReference, ...]:
    return tuple(
        sorted(
            set(rows),
            key=lambda row: (
                row.completion_relative_path,
                row.source_record_ordinal,
                row.raw_record_sha256,
            ),
        )
    )


def _initial_crosswalk_row(
    *,
    entity_kind: WyscoutIdentityEntityKind,
    source_id: int,
    source_refs: Sequence[WyscoutSourceRowReference],
    state: WyscoutIdentityState,
) -> W04IdentityCrosswalkRow:
    source_identity = SourceIdentity(
        provider="Wyscout",
        source_id=f"{entity_kind.value.lower()}:{source_id}",
        source_version="figshare-v5",
    )
    if state is WyscoutIdentityState.RESOLVED:
        classification = WyscoutIdentityClassificationMethod.SOURCE_KEY_DETERMINISTIC_RESOLUTION
        method = IdentityMatchMethod.DETERMINISTIC
        canonical_id = canonical_source_uuid(SourceRecordKind(entity_kind.value.lower()), source_id)
        confidence = 1.0
        reasons = ("SOURCE_KEY_DETERMINISTIC_RESOLUTION",)
    elif state is WyscoutIdentityState.REVIEW_REQUIRED:
        classification = WyscoutIdentityClassificationMethod.SOURCE_KEY_REVIEW_REQUIRED
        method = None
        canonical_id = None
        confidence = 0.0
        reasons = ("NONZERO_ABSENT_PLAYER_MASTER",)
    else:
        classification = WyscoutIdentityClassificationMethod.PROVIDER_ZERO_ACTOR_REJECTION
        method = None
        canonical_id = None
        confidence = 0.0
        reasons = ("PROVIDER_ZERO_ACTOR_REJECTION",)
    values: dict[str, object] = {
        "schema_version": 1,
        "crosswalk_schema_version": "w04-wyscout-crosswalk-v2",
        "tenant_context": TenantContext(tenant_id=TENANT_ID),
        "entity_kind": entity_kind,
        "source_identity": source_identity,
        "source_manifest_id": SOURCE_MANIFEST_ID,
        "source_manifest_sha256": SOURCE_MANIFEST_SHA256,
        "source_row_refs": _sorted_refs(source_refs),
        "canonical_id": canonical_id,
        "version": 1,
        "classification_method": classification,
        "identity_match_method": method,
        "confidence": confidence,
        "state": state,
        "valid_from": SOURCE_RELEASE,
        "valid_to": None,
        "available_at": IDENTITY_ACCEPTED_AT,
        "reviewed_by": None,
        "supersedes_evidence_digest": None,
        "identity_ruleset_id": IDENTITY_RULESET_ID,
        "identity_ruleset_sha256": IDENTITY_CANDIDATE_SHA256,
        "identity_decision_id": IDENTITY_DECISION_ID,
        "identity_decision_sha256": IDENTITY_DECISION_SHA256,
        "identity_review_id": IDENTITY_REVIEW_ID,
        "identity_review_sha256": IDENTITY_REVIEW_SHA256,
        "identity_acceptance_id": IDENTITY_ACCEPTANCE_ID,
        "identity_acceptance_sha256": IDENTITY_ACCEPTANCE_SHA256,
        "reason_codes": reasons,
        "evidence_digest": "0" * 64,
        "crosswalk_row_id": UUID(int=0),
        "trace_id": UUID(int=0),
    }
    draft = cast(Any, W04IdentityCrosswalkRow).model_construct(**values)
    digest = crosswalk_evidence_digest(draft)
    values["evidence_digest"] = digest
    identified = cast(Any, W04IdentityCrosswalkRow).model_construct(**values)
    row_id = crosswalk_row_identity(identified)
    values["crosswalk_row_id"] = row_id
    values["trace_id"] = uuid5(row_id, "w04-identity-crosswalk-trace-v2")
    return W04IdentityCrosswalkRow.model_validate(values)


def _formation_player_ids(
    formation: object,
    *,
    context: str,
) -> tuple[int, ...]:
    if type(formation) is not dict:
        raise WyscoutIdentityError(f"{context} formation must be an object")
    value = cast(dict[str, object], formation)
    if set(value) != {"bench", "lineup", "substitutions"}:
        raise WyscoutIdentityError(f"{context} formation keys drifted")
    result: list[int] = []
    for family in ("bench", "lineup"):
        rows = value[family]
        if type(rows) is not list:
            raise WyscoutIdentityError(f"{context}.{family} must be an array")
        for index, row in enumerate(cast(list[object], rows)):
            if type(row) is not dict:
                raise WyscoutIdentityError(f"{context}.{family}[{index}] must be an object")
            result.append(
                _strict_nonnegative(
                    cast(dict[str, object], row).get("playerId"),
                    context=f"{context}.{family}[{index}].playerId",
                )
            )
    substitutions = value["substitutions"]
    if type(substitutions) is str:
        if substitutions != "null":
            raise WyscoutIdentityError(
                f"{context}.substitutions string must be the measured unmapped null token"
            )
    elif type(substitutions) is list:
        for index, row in enumerate(cast(list[object], substitutions)):
            if type(row) is not dict:
                raise WyscoutIdentityError(f"{context}.substitutions[{index}] must be an object")
            mapping = cast(dict[str, object], row)
            _strict_nonnegative(
                mapping.get("minute"),
                context=f"{context}.substitutions[{index}].minute",
            )
            result.extend(
                (
                    _strict_nonnegative(
                        mapping.get("playerIn"),
                        context=f"{context}.substitutions[{index}].playerIn",
                    ),
                    _strict_nonnegative(
                        mapping.get("playerOut"),
                        context=f"{context}.substitutions[{index}].playerOut",
                    ),
                )
            )
    else:
        raise WyscoutIdentityError(f"{context}.substitutions must be an array or empty string")
    return tuple(result)


def _derive_population(source_root: Path) -> tuple[W04IdentityCrosswalkRow, ...]:
    master_refs: dict[
        WyscoutIdentityEntityKind,
        dict[int, WyscoutSourceRowReference],
    ] = {}
    for spec in _MASTER_MEMBERS:
        entity_kind = _KIND_MAP[spec.record_kind]
        entity_rows: dict[int, WyscoutSourceRowReference] = {}
        for ordinal, row in _iter_verified_rows(source_root, spec):
            source_id = _strict_positive(row.get("wyId"), context=f"{spec.path}[{ordinal}].wyId")
            if source_id in entity_rows:
                raise WyscoutIdentityError(f"duplicate {entity_kind.value} master source key")
            entity_rows[source_id] = _source_ref(spec, ordinal, row)
        master_refs[entity_kind] = entity_rows

    competition_ids = set(master_refs[WyscoutIdentityEntityKind.COMPETITION])
    team_ids = set(master_refs[WyscoutIdentityEntityKind.TEAM])
    player_ids = set(master_refs[WyscoutIdentityEntityKind.PLAYER])
    match_refs: dict[int, WyscoutSourceRowReference] = {}
    unresolved_player_refs: defaultdict[int, set[WyscoutSourceRowReference]] = defaultdict(set)
    zero_refs: set[WyscoutSourceRowReference] = set()
    for spec in _MATCH_MEMBERS:
        for ordinal, row in _iter_verified_rows(source_root, spec):
            match_id = _strict_positive(row.get("wyId"), context=f"{spec.path}[{ordinal}].wyId")
            if match_id in match_refs:
                raise WyscoutIdentityError("duplicate match master source key")
            competition_id = _strict_positive(
                row.get("competitionId"), context=f"{spec.path}[{ordinal}].competitionId"
            )
            if competition_id not in competition_ids:
                raise WyscoutIdentityError("match competition is absent from its master")
            teams_data = row.get("teamsData")
            if type(teams_data) is not dict or len(teams_data) != 2:
                raise WyscoutIdentityError("match teamsData must contain exactly two teams")
            source_ref = _source_ref(spec, ordinal, row)
            match_refs[match_id] = source_ref
            actual_team_ids: set[int] = set()
            for key, team_value in cast(dict[str, object], teams_data).items():
                if type(team_value) is not dict:
                    raise WyscoutIdentityError("match team row must be an object")
                team = cast(dict[str, object], team_value)
                team_id = _strict_positive(
                    team.get("teamId"), context=f"{spec.path}[{ordinal}].teamsData.teamId"
                )
                if key != str(team_id):
                    raise WyscoutIdentityError("teamsData key must equal canonical teamId text")
                if team_id not in team_ids or team_id in actual_team_ids:
                    raise WyscoutIdentityError("match team identity is absent or duplicated")
                actual_team_ids.add(team_id)
                formation = team.get("formation")
                if formation is None and team.get("hasFormation") == 0:
                    continue
                for player_id in _formation_player_ids(
                    formation,
                    context=f"{spec.path}[{ordinal}].teamsData[{key}]",
                ):
                    if player_id == 0:
                        zero_refs.add(source_ref)
                    elif player_id not in player_ids:
                        unresolved_player_refs[player_id].add(source_ref)
    if len(match_refs) != 1_826:
        raise WyscoutIdentityError("match master population must contain exactly 1,826 rows")

    for spec in _ACTION_MEMBERS:
        for ordinal, row in _iter_verified_rows(source_root, spec):
            match_id = _strict_positive(
                row.get("matchId"), context=f"{spec.path}[{ordinal}].matchId"
            )
            if match_id not in match_refs:
                raise WyscoutIdentityError("action match is absent from the match master")
            team_id = _strict_positive(row.get("teamId"), context=f"{spec.path}[{ordinal}].teamId")
            if team_id not in team_ids:
                raise WyscoutIdentityError("action team is absent from the team master")
            player_id = _strict_nonnegative(
                row.get("playerId"), context=f"{spec.path}[{ordinal}].playerId"
            )
            if player_id == 0:
                zero_refs.add(_source_ref(spec, ordinal, row))
            elif player_id not in player_ids:
                unresolved_player_refs[player_id].add(_source_ref(spec, ordinal, row))

    if (
        len(unresolved_player_refs) != 15
        or sum(len(rows) for rows in unresolved_player_refs.values()) != 23
    ):
        raise WyscoutIdentityError("non-zero absent-player population must reconcile 23-to-15")
    if len(zero_refs) != 226_041:
        raise WyscoutIdentityError("player-zero source references must equal 226,041")

    master_refs[WyscoutIdentityEntityKind.MATCH] = match_refs
    all_rows: list[W04IdentityCrosswalkRow] = []
    for entity_kind in WyscoutIdentityEntityKind:
        for source_id, source_ref in master_refs[entity_kind].items():
            all_rows.append(
                _initial_crosswalk_row(
                    entity_kind=entity_kind,
                    source_id=source_id,
                    source_refs=(source_ref,),
                    state=WyscoutIdentityState.RESOLVED,
                )
            )
    all_rows.append(
        _initial_crosswalk_row(
            entity_kind=WyscoutIdentityEntityKind.PLAYER,
            source_id=0,
            source_refs=tuple(zero_refs),
            state=WyscoutIdentityState.REJECTED,
        )
    )
    for source_id, references in unresolved_player_refs.items():
        all_rows.append(
            _initial_crosswalk_row(
                entity_kind=WyscoutIdentityEntityKind.PLAYER,
                source_id=source_id,
                source_refs=tuple(references),
                state=WyscoutIdentityState.REVIEW_REQUIRED,
            )
        )
    rank = {kind: index for index, kind in enumerate(WyscoutIdentityEntityKind)}
    ordered = tuple(
        sorted(
            all_rows,
            key=lambda row: (
                rank[row.entity_kind],
                row.source_identity.provider,
                row.source_identity.source_id,
                row.source_identity.source_version,
                row.version,
                row.evidence_digest,
            ),
        )
    )
    if len(ordered) != 5_594:
        raise WyscoutIdentityError("initial current-row population must equal 5,594")
    return ordered


def _queue_from_rows(
    rows: tuple[W04IdentityCrosswalkRow, ...],
) -> WyscoutIdentityReviewQueue:
    items: list[WyscoutIdentityQueueItem] = []
    for row in rows:
        if row.state is not WyscoutIdentityState.REVIEW_REQUIRED:
            continue
        values: dict[str, object] = {
            "queue_item_id": UUID(int=0),
            "tenant_context": row.tenant_context,
            "entity_kind": row.entity_kind,
            "source_identity": row.source_identity,
            "source_manifest_id": row.source_manifest_id,
            "reason_family": "NONZERO_ABSENT_MASTER",
            "reason_codes": ("NONZERO_ABSENT_PLAYER_MASTER",),
            "source_row_refs": row.source_row_refs,
            "first_seen_source_valid_at": SOURCE_RELEASE,
            "available_at": IDENTITY_ACCEPTED_AT,
            "status": WyscoutIdentityQueueStatus.OPEN,
            "disposition_id": None,
        }
        draft = cast(Any, WyscoutIdentityQueueItem).model_construct(**values)
        values["queue_item_id"] = queue_item_identity(draft)
        items.append(WyscoutIdentityQueueItem.model_validate(values))
    rank = {kind: index for index, kind in enumerate(WyscoutIdentityEntityKind)}
    ordered = tuple(
        sorted(
            items,
            key=lambda item: (
                rank[item.entity_kind],
                item.source_identity.provider,
                item.source_identity.source_id,
                item.source_identity.source_version,
                item.reason_family,
                item.queue_item_id.bytes,
            ),
        )
    )
    return WyscoutIdentityReviewQueue(
        tenant_context=TenantContext(tenant_id=TENANT_ID),
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        identity_ruleset_id=IDENTITY_RULESET_ID,
        identity_ruleset_sha256=IDENTITY_CANDIDATE_SHA256,
        identity_decision_id=IDENTITY_DECISION_ID,
        identity_decision_sha256=IDENTITY_DECISION_SHA256,
        identity_review_id=IDENTITY_REVIEW_ID,
        identity_review_sha256=IDENTITY_REVIEW_SHA256,
        identity_acceptance_id=IDENTITY_ACCEPTANCE_ID,
        identity_acceptance_sha256=IDENTITY_ACCEPTANCE_SHA256,
        prior_queue_sha256=None,
        items=ordered,
        counts_by_kind_and_status={"PLAYER:OPEN": len(ordered)},
    )


def build_initial_identity_bundle(
    *,
    source_root: Path,
    manifest_root: Path,
) -> WyscoutIdentityBuild:
    """Recompute the exact full source population and both canonical artifacts."""

    try:
        source = bridge._exact_root_argument(
            source_root,
            relative=_SOURCE_ROOT_RELATIVE,
            context="source root",
        )
        manifests = bridge._exact_root_argument(
            manifest_root,
            relative=_MANIFEST_ROOT_RELATIVE,
            context="manifest root",
        )
    except bridge.WyscoutSourceManifestPathError as exc:
        raise WyscoutIdentityPathError("identity runtime root argument is not exact") from exc
    _verify_authorities(manifests)
    rows = _derive_population(source)
    queue = _queue_from_rows(rows)
    queue_bytes = canonical_json_bytes(queue.model_dump(mode="json"))
    queue_sha256 = hashlib.sha256(queue_bytes).hexdigest()
    queue_path = f"review-queues/{queue_sha256}.identity-review-queue.json"
    counts: dict[str, int] = {}
    for row in rows:
        key = f"{row.entity_kind.value}:{row.state.value}"
        counts[key] = counts.get(key, 0) + 1
    effective_index = tuple(
        sorted(
            (
                WyscoutIdentityEffectiveState(
                    evidence_digest=row.evidence_digest,
                    classification_method=row.classification_method,
                    effective_state=row.state,
                )
                for row in rows
            ),
            key=lambda item: item.evidence_digest,
        )
    )
    bundle = WyscoutIdentityBundle(
        tenant_context=TenantContext(tenant_id=TENANT_ID),
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        identity_ruleset_id=IDENTITY_RULESET_ID,
        identity_ruleset_sha256=IDENTITY_CANDIDATE_SHA256,
        identity_decision_id=IDENTITY_DECISION_ID,
        identity_decision_sha256=IDENTITY_DECISION_SHA256,
        identity_decided_at=IDENTITY_DECIDED_AT,
        identity_review_id=IDENTITY_REVIEW_ID,
        identity_review_path=IDENTITY_REVIEW_PATH,
        identity_review_sha256=IDENTITY_REVIEW_SHA256,
        identity_reviewed_at=IDENTITY_REVIEWED_AT,
        identity_acceptance_id=IDENTITY_ACCEPTANCE_ID,
        identity_acceptance_sha256=IDENTITY_ACCEPTANCE_SHA256,
        identity_accepted_at=IDENTITY_ACCEPTED_AT,
        current_rows=rows,
        historical_row_digests=(),
        effective_state_index=effective_index,
        supersession_edges=(),
        counts_by_entity_kind_and_effective_state=counts,
        review_queue_path=queue_path,
        review_queue_sha256=queue_sha256,
        accepted_corrections=(),
        prior_identity_bundle_id=None,
        prior_identity_bundle_sha256=None,
        observed_at=IDENTITY_DECIDED_AT,
        available_at=IDENTITY_ACCEPTED_AT,
    )
    bundle_bytes = canonical_json_bytes(bundle.model_dump(mode="json"))
    bundle_sha256 = hashlib.sha256(bundle_bytes).hexdigest()
    bundle_path = f"bundles/{bundle_sha256}.identity-bundle.json"
    return WyscoutIdentityBuild(
        queue=queue,
        queue_bytes=queue_bytes,
        queue_sha256=queue_sha256,
        queue_relative_path=queue_path,
        bundle=bundle,
        bundle_bytes=bundle_bytes,
        bundle_sha256=bundle_sha256,
        bundle_id=identity_bundle_id(bundle_sha256),
        bundle_relative_path=bundle_path,
    )


def _identity_inventory(root: Path) -> dict[str, tuple[str, ...]]:
    if not root.exists():
        return {"review-queues": (), "bundles": ()}
    if root.is_symlink() or not root.is_dir():
        raise WyscoutIdentityPathError("identity root must be a real directory")
    allowed = {"review-queues", "bundles"}
    names = {entry.name for entry in os.scandir(root)}
    if not names <= allowed:
        raise WyscoutIdentityPathError("identity root contains an unreferenced artifact")
    result: dict[str, tuple[str, ...]] = {}
    for directory in sorted(allowed):
        path = root / directory
        if not path.exists():
            result[directory] = ()
            continue
        if path.is_symlink() or not path.is_dir():
            raise WyscoutIdentityPathError("identity artifact directory is unsafe")
        entries = tuple(sorted(entry.name for entry in os.scandir(path)))
        for entry in os.scandir(path):
            if entry.is_symlink() or not entry.is_file(follow_symlinks=False):
                raise WyscoutIdentityPathError("identity artifact is not a regular file")
            if stat.S_IMODE(entry.stat(follow_symlinks=False).st_mode) != _FILE_MODE:
                raise WyscoutIdentityPathError("identity artifact mode is unsafe")
        result[directory] = entries
    return result


def _check_inventory(
    root: Path,
    *,
    queue_filename: str,
    bundle_filename: str,
    allow_absent: bool,
) -> None:
    inventory = _identity_inventory(root)
    expected = {
        "review-queues": (queue_filename,),
        "bundles": (bundle_filename,),
    }
    if inventory == expected:
        return
    if allow_absent and inventory == {"review-queues": (), "bundles": ()}:
        return
    raise WyscoutIdentityPathError(
        "identity root contains missing, additional, stale, partial, or unreferenced artifacts"
    )


def _read_identity_artifact(root: Path, relative_path: str) -> bytes:
    return _read_exact_bytes(root, relative_path)


def _verify_reopened(root: Path, expected: WyscoutIdentityBuild) -> None:
    queue_bytes = _read_identity_artifact(root, expected.queue_relative_path)
    bundle_bytes = _read_identity_artifact(root, expected.bundle_relative_path)
    if (
        queue_bytes != expected.queue_bytes
        or bundle_bytes != expected.bundle_bytes
        or hashlib.sha256(queue_bytes).hexdigest() != expected.queue_sha256
        or hashlib.sha256(bundle_bytes).hexdigest() != expected.bundle_sha256
    ):
        raise WyscoutIdentityError("identity artifact bytes/address differ on readback")
    try:
        queue = WyscoutIdentityReviewQueue.model_validate_json(queue_bytes)
        bundle = WyscoutIdentityBundle.model_validate_json(bundle_bytes)
    except ValidationError as exc:
        raise WyscoutIdentityError("identity artifact contract readback failed") from exc
    if queue != expected.queue or bundle != expected.bundle:
        raise WyscoutIdentityError("identity artifact semantics differ on readback")
    if bundle.review_queue_sha256 != hashlib.sha256(queue_bytes).hexdigest():
        raise WyscoutIdentityError("bundle does not recursively bind reopened queue bytes")
    queued_rows = {item.source_identity: item.source_row_refs for item in queue.items}
    review_rows = {
        row.source_identity: row.source_row_refs
        for row in bundle.current_rows
        if row.state is WyscoutIdentityState.REVIEW_REQUIRED
    }
    if queued_rows != review_rows:
        raise WyscoutIdentityError("queue does not equal review-required bundle population")


def materialize_initial_identity_bundle(
    *,
    source_root: Path,
    manifest_root: Path,
    identity_root: Path,
) -> WyscoutIdentityMaterialization:
    """Build, atomically materialize, reopen, and recursively verify both artifacts."""

    expected_root = _PROJECT_ROOT / _IDENTITY_ROOT_RELATIVE
    if (identity_root.is_absolute() and identity_root != expected_root) or (
        not identity_root.is_absolute()
        and (identity_root != _IDENTITY_ROOT_RELATIVE or Path.cwd() != _PROJECT_ROOT)
    ):
        raise WyscoutIdentityPathError("identity root must be the exact W04 working root")
    build = build_initial_identity_bundle(source_root=source_root, manifest_root=manifest_root)
    return _materialize_identity_build(expected_root, build)


def _materialize_identity_build(
    expected_root: Path,
    build: WyscoutIdentityBuild,
) -> WyscoutIdentityMaterialization:
    """Persist one already source-derived build; retained for idempotency verification."""

    queue_filename = Path(build.queue_relative_path).name
    bundle_filename = Path(build.bundle_relative_path).name
    _check_inventory(
        expected_root,
        queue_filename=queue_filename,
        bundle_filename=bundle_filename,
        allow_absent=True,
    )
    expected_root.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        with bridge._created_parent_descriptor(
            expected_root.parent,
            (expected_root.name, "review-queues"),
        ) as queue_parent:
            queue_created = bridge._persist_immutable_file(
                queue_parent,
                queue_filename,
                build.queue_bytes,
            )
        with bridge._created_parent_descriptor(
            expected_root.parent,
            (expected_root.name, "bundles"),
        ) as bundle_parent:
            bundle_created = bridge._persist_immutable_file(
                bundle_parent,
                bundle_filename,
                build.bundle_bytes,
            )
    except bridge.WyscoutSourceManifestConflictError as exc:
        raise WyscoutIdentityConflictError("immutable identity artifact conflicts") from exc
    _check_inventory(
        expected_root,
        queue_filename=queue_filename,
        bundle_filename=bundle_filename,
        allow_absent=False,
    )
    _verify_reopened(expected_root, build)
    return WyscoutIdentityMaterialization(
        build=build,
        queue_created=queue_created,
        bundle_created=bundle_created,
    )


def load_initial_identity_bundle(
    *,
    source_root: Path,
    manifest_root: Path,
    identity_root: Path,
    identity_bundle_sha256: str,
) -> WyscoutIdentityBuild:
    """Recompute source authority before accepting one exact bundle address."""

    expected_root = _PROJECT_ROOT / _IDENTITY_ROOT_RELATIVE
    if identity_root != expected_root:
        raise WyscoutIdentityPathError("identity root must be the exact absolute W04 root")
    build = build_initial_identity_bundle(source_root=source_root, manifest_root=manifest_root)
    if identity_bundle_sha256 != build.bundle_sha256:
        raise WyscoutIdentityError("caller bundle digest is not the source-derived address")
    _check_inventory(
        expected_root,
        queue_filename=Path(build.queue_relative_path).name,
        bundle_filename=Path(build.bundle_relative_path).name,
        allow_absent=False,
    )
    _verify_reopened(expected_root, build)
    return build


__all__ = [
    "WyscoutIdentityBuild",
    "WyscoutIdentityConflictError",
    "WyscoutIdentityError",
    "WyscoutIdentityMaterialization",
    "WyscoutIdentityPathError",
    "build_initial_identity_bundle",
    "load_initial_identity_bundle",
    "materialize_initial_identity_bundle",
]
