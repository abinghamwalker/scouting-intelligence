"""Derive and validate the immutable W04 Wyscout source-completion index."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path, PurePosixPath
from types import MappingProxyType
from typing import Never, cast
from uuid import UUID
from weakref import WeakKeyDictionary

from scouting.contracts.wyscout_data import (
    SOURCE_COMPLETION_INDEX_SHA256,
    GoldPlayerWindow,
    Layer,
    LayerManifest,
    PossessionPeriodSequence,
    PossessionSequenceAction,
    SilverAction,
    SilverLineupStint,
    SilverPlayerMatchFact,
    SilverPossession,
    SourceRecordKind,
    WyscoutSourceRowReference,
    canonical_source_uuid,
)
from scouting.sources import wyscout_manifest as bridge
from scouting.storage.formats import canonical_json_bytes

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SOURCE_ROOT_RELATIVE = Path("data/source/wyscout/v5")
_MANIFEST_ROOT_RELATIVE = Path("data/manifests")
_SOURCE_MANIFEST_ID = UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b")
_SOURCE_MANIFEST_SHA256 = "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
_COMPLETION_MANIFEST_SHA256 = "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
_SOURCE_MANIFEST_RELATIVE_PATH = (
    "wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
)
_INDEX_DIRECTORY = PurePosixPath("wyscout/v5/source-completion")
_INDEX_SCHEMA_VERSION = "w04-wyscout-source-completion-index-v1"
_ACCEPTED_INDEX_SHA256 = "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
_ACTION_FRAME_VERSION = b"w04-wyscout-source-completion-action-v1\x00"
_MEMBERSHIP_FRAME_VERSION = b"w04-wyscout-source-completion-period-v1\x00"
_AGGREGATE_ACTION_COUNT = 3_071_395
_PERIOD_RANK = {"1H": 1, "2H": 2}
_CHUNK_SIZE = 1024 * 1024
_VERTICAL_SLICE_MEMBER_PATH = "archive-members/events_England.json"
_VERTICAL_SLICE_MATCH_SOURCE_ID = 2_499_719
_VERTICAL_SLICE_MATCH_ACTION_COUNT = 1_768


class WyscoutCompletionIndexError(RuntimeError):
    """Base failure for completion-index derivation or public validation."""


class WyscoutCompletionIndexConflictError(WyscoutCompletionIndexError):
    """Raised when immutable index bytes already exist with different content."""


@dataclass(frozen=True, slots=True)
class EventMemberSpec:
    path: str
    sha256: str
    size_bytes: int
    row_count: int


_EVENT_MEMBERS = (
    EventMemberSpec(
        "archive-members/events_England.json",
        "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
        188_888_614,
        643_150,
    ),
    EventMemberSpec(
        "archive-members/events_France.json",
        "18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317",
        186_374_196,
        632_807,
    ),
    EventMemberSpec(
        "archive-members/events_Germany.json",
        "2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3",
        152_916_631,
        519_407,
    ),
    EventMemberSpec(
        "archive-members/events_Italy.json",
        "b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84",
        190_544_685,
        647_372,
    ),
    EventMemberSpec(
        "archive-members/events_Spain.json",
        "b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154",
        184_164_406,
        628_659,
    ),
)


@dataclass(frozen=True, slots=True)
class CompletionActionEvidence:
    """One exact source action projected for completion comparison."""

    source_member_path: str
    source_member_sha256: str
    source_record_ordinal: int
    source_event_record_id: int
    match_source_id: int
    action_period_code: str
    period_rank: int
    period_elapsed_seconds_token: str
    player_source_id: int | None
    team_source_id: int | None
    action_event_taxonomy_id: int
    action_subevent_taxonomy_id: int | None
    raw_tags: tuple[object, ...]
    possession_tag_ids: tuple[int, ...]
    raw_record_sha256: str

    @property
    def order_key(self) -> tuple[int, Decimal, int, int]:
        return (
            self.period_rank,
            Decimal(self.period_elapsed_seconds_token),
            self.source_record_ordinal,
            self.source_event_record_id,
        )


@dataclass(frozen=True, slots=True)
class VerifiedMatchAction:
    """One immutable raw action paired with its exact projected evidence."""

    raw_record: Mapping[str, object]
    canonical_raw_record: bytes
    evidence: CompletionActionEvidence


@dataclass(frozen=True, slots=True)
class VerifiedMatchPopulation:
    """One exact verified raw match population and its checked authority."""

    index: SourceCompletionIndex
    source_member_path: str
    match_source_id: int
    actions: tuple[VerifiedMatchAction, ...]
    completion: CheckedCompletionPopulation


@dataclass(frozen=True, slots=True)
class CompletionPeriodRow:
    source_member_path: str
    source_member_sha256: str
    match_source_id: int
    action_period_code: str
    period_rank: int
    action_count: int
    membership_sha256: str

    @property
    def key(self) -> tuple[str, int, int, str]:
        return (
            self.source_member_path,
            self.match_source_id,
            self.period_rank,
            self.action_period_code,
        )


@dataclass(frozen=True, slots=True)
class CompletionMemberRow:
    path: str
    sha256: str
    row_count: int
    indexed_action_count: int
    periods: tuple[CompletionPeriodRow, ...]


@dataclass(frozen=True, slots=True)
class SourceCompletionIndex:
    schema_version: str
    source_manifest_id: UUID
    source_manifest_sha256: str
    completion_manifest_sha256: str
    aggregate_action_count: int
    members: tuple[CompletionMemberRow, ...]
    sha256: str
    canonical_bytes: bytes

    @property
    def periods_by_key(self) -> dict[tuple[str, int, int, str], CompletionPeriodRow]:
        return {period.key: period for member in self.members for period in member.periods}


@dataclass(frozen=True, slots=True)
class SourceCompletionMaterialization:
    index: SourceCompletionIndex
    relative_path: str
    size_bytes: int
    created: bool


@dataclass(frozen=True, slots=True)
class _CheckedCompletionRecord:
    index: SourceCompletionIndex
    actions: tuple[CompletionActionEvidence, ...]
    scope_kind: str


@dataclass(frozen=True, slots=True)
class _VerifiedCompletionRecord:
    index: SourceCompletionIndex
    sequences: tuple[PossessionPeriodSequence, ...]
    period_keys: tuple[tuple[str, int, int, str], ...]
    complete_match: bool


class CheckedCompletionPopulation:
    """Opaque, non-replayable evidence of an exact accepted population comparison."""

    __slots__ = ("__weakref__",)

    def __new__(cls) -> CheckedCompletionPopulation:
        raise TypeError("checked completion populations are issued only by the reader")

    @property
    def sequences(self) -> tuple[PossessionPeriodSequence, ...]:
        return _checked_completion_record(self).sequences

    def __copy__(self) -> CheckedCompletionPopulation:
        raise TypeError("checked completion populations cannot be copied")

    def __deepcopy__(self, _memo: object) -> CheckedCompletionPopulation:
        raise TypeError("checked completion populations cannot be copied")

    def __reduce__(self) -> Never:
        raise TypeError("checked completion populations cannot be serialized")


@dataclass(frozen=True, slots=True)
class _CheckedProductRecord:
    construction_kind: str
    value: object
    completions: tuple[CheckedCompletionPopulation, ...]
    payload_items: tuple[tuple[str, object], ...]
    lineup_stints: tuple[SilverLineupStint, ...] = ()
    action_dependencies: tuple[CheckedProduct[SilverAction], ...] = ()
    possession_dependencies: tuple[CheckedProduct[SilverPossession], ...] = ()
    fact_dependencies: tuple[CheckedProduct[SilverPlayerMatchFact], ...] = ()
    product_dependencies: tuple[CheckedProduct[object], ...] = ()


@dataclass(frozen=True, slots=True)
class _VerifiedProductRecord:
    construction_kind: str
    value: object
    completions: tuple[CheckedCompletionPopulation, ...]


@dataclass(slots=True)
class _VerificationContext:
    completions: dict[int, _VerifiedCompletionRecord]
    products: dict[int, _VerifiedProductRecord]
    active_products: set[int]


def _verification_context() -> _VerificationContext:
    return _VerificationContext(completions={}, products={}, active_products=set())


class CheckedProduct[CheckedValue]:
    """Opaque authorized handle; raw contract models remain semantic-only values."""

    __slots__ = ("__weakref__",)

    def __new__(cls) -> CheckedProduct[CheckedValue]:
        raise TypeError("checked products are issued only by checked construction boundaries")

    @property
    def value(self) -> CheckedValue:
        return cast(CheckedValue, _checked_product_record(self).value)

    @property
    def construction_authority_state(self) -> str:
        _checked_product_record(self)
        return "completion_reader_checked"

    def __copy__(self) -> CheckedProduct[CheckedValue]:
        raise TypeError("checked products cannot be copied")

    def __deepcopy__(self, _memo: object) -> CheckedProduct[CheckedValue]:
        raise TypeError("checked products cannot be copied")

    def __reduce__(self) -> Never:
        raise TypeError("checked products cannot be serialized")


type _IssueCompletion = Callable[[_CheckedCompletionRecord], CheckedCompletionPopulation]
type _GetCompletion = Callable[[CheckedCompletionPopulation], object]
type _IssueProduct = Callable[[_CheckedProductRecord], CheckedProduct[object]]
type _GetProduct = Callable[[CheckedProduct[object]], object]


def _capability_registries() -> tuple[
    _IssueCompletion,
    _GetCompletion,
    _IssueProduct,
    _GetProduct,
]:
    completion_records: WeakKeyDictionary[CheckedCompletionPopulation, object] = WeakKeyDictionary()
    product_records: WeakKeyDictionary[CheckedProduct[object], object] = WeakKeyDictionary()

    def issue_completion(record: _CheckedCompletionRecord) -> CheckedCompletionPopulation:
        capability = object.__new__(CheckedCompletionPopulation)
        completion_records[capability] = record
        return capability

    def get_completion(capability: CheckedCompletionPopulation) -> object:
        if type(capability) is not CheckedCompletionPopulation:
            raise WyscoutCompletionIndexError("completion capability type is not authentic")
        try:
            return completion_records[capability]
        except KeyError as exc:
            raise WyscoutCompletionIndexError(
                "completion capability was not issued by the accepted reader"
            ) from exc

    def issue_product(record: _CheckedProductRecord) -> CheckedProduct[object]:
        capability = object.__new__(CheckedProduct)
        product_records[capability] = record
        return capability

    def get_product(capability: CheckedProduct[object]) -> object:
        if type(capability) is not CheckedProduct:
            raise WyscoutCompletionIndexError("checked product type is not authentic")
        try:
            return product_records[capability]
        except KeyError as exc:
            raise WyscoutCompletionIndexError(
                "product was not issued by a checked construction boundary"
            ) from exc

    return issue_completion, get_completion, issue_product, get_product


(
    _issue_checked_completion,
    _get_checked_completion,
    _issue_checked_product,
    _get_checked_product,
) = _capability_registries()


def _checked_completion_record(
    capability: CheckedCompletionPopulation,
    *,
    verification: _VerificationContext | None = None,
) -> _VerifiedCompletionRecord:
    context = verification if verification is not None else _verification_context()
    identity = id(capability)
    cached = context.completions.get(identity)
    if cached is not None:
        return cached
    record = _get_checked_completion(capability)
    if type(record) is not _CheckedCompletionRecord:
        raise WyscoutCompletionIndexError("completion capability record is malformed")
    checked = _verify_completion_evidence(record)
    context.completions[identity] = checked
    return checked


def _checked_product_record(
    capability: CheckedProduct[object],
    *,
    verification: _VerificationContext | None = None,
) -> _VerifiedProductRecord:
    context = verification if verification is not None else _verification_context()
    identity = id(capability)
    cached = context.products.get(identity)
    if cached is not None:
        return cached
    if identity in context.active_products:
        raise WyscoutCompletionIndexError("checked product dependency graph contains a cycle")
    record = _get_checked_product(capability)
    if type(record) is not _CheckedProductRecord:
        raise WyscoutCompletionIndexError("checked product capability record is malformed")
    context.active_products.add(identity)
    try:
        checked = _verify_product_evidence(record, verification=context)
    finally:
        context.active_products.remove(identity)
    context.products[identity] = checked
    return checked


def _strict_int(value: object, *, context: str) -> int:
    if type(value) is not int:
        raise WyscoutCompletionIndexError(f"{context} must be a strict integer")
    return value


def _strict_int_or_null(value: object, *, context: str) -> int | None:
    if value is None:
        return None
    return _strict_int(value, context=context)


def _event_seconds(value: object) -> tuple[Decimal, str]:
    if type(value) is int:
        decimal_value = Decimal(value)
        token = str(value)
    elif type(value) is Decimal:
        decimal_value = value
        token = format(decimal_value, "f")
    else:
        raise WyscoutCompletionIndexError("eventSec must be a strict integer or JSON number")
    if not decimal_value.is_finite() or decimal_value < 0:
        raise WyscoutCompletionIndexError("eventSec must be finite and non-negative")
    return decimal_value, token


def _canonical_value_text(value: object) -> str:
    """Encode already-strict parsed JSON with Bronze canonical semantics."""

    if value is None:
        return "null"
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if type(value) is Decimal:
        decimal_value = value
        if not decimal_value.is_finite():
            raise WyscoutCompletionIndexError("canonical JSON number must be finite")
        if decimal_value.is_zero():
            return "0"
        token = format(decimal_value, "f")
        return token.rstrip("0").rstrip(".") if "." in token else token
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    if type(value) is list or type(value) is tuple:
        return "[" + ",".join(_canonical_value_text(item) for item in value) + "]"
    if type(value) is dict:
        mapping = cast(dict[object, object], value)
        if any(type(key) is not str for key in mapping):
            raise WyscoutCompletionIndexError("canonical JSON object keys must be strings")
        string_mapping = cast(dict[str, object], value)
        return (
            "{"
            + ",".join(
                json.dumps(key, ensure_ascii=False)
                + ":"
                + _canonical_value_text(string_mapping[key])
                for key in sorted(string_mapping)
            )
            + "}"
        )
    if type(value) is MappingProxyType:
        immutable_tag = cast(Mapping[object, object], value)
        if set(immutable_tag) != {"id"} or type(immutable_tag["id"]) is not int:
            raise WyscoutCompletionIndexError(
                "canonical immutable mapping must be one strict tag ID"
            )
        return '{"id":' + str(immutable_tag["id"]) + "}"
    raise WyscoutCompletionIndexError(f"unsupported strict JSON value: {type(value).__name__}")


def _canonical_value_bytes(value: object) -> bytes:
    return _canonical_value_text(value).encode("utf-8")


def _raw_tags_and_projection(value: object) -> tuple[tuple[object, ...], tuple[int, ...]]:
    if type(value) is not list:
        raise WyscoutCompletionIndexError("tags must be an exact JSON array")
    immutable_tags: list[object] = []
    projected: set[int] = set()
    for index, item in enumerate(cast(list[object], value)):
        if type(item) is not dict:
            raise WyscoutCompletionIndexError(f"tags[{index}] must be an exact JSON object")
        tag = cast(dict[str, object], item)
        if set(tag) != {"id"}:
            raise WyscoutCompletionIndexError(f"tags[{index}] must contain only strict id")
        tag_id = _strict_int(tag["id"], context=f"tags[{index}].id")
        immutable_tags.append(MappingProxyType({"id": tag_id}))
        projected.add(tag_id)
    return tuple(immutable_tags), tuple(sorted(projected))


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise WyscoutCompletionIndexError(f"source action repeats key {key!r}")
        result[key] = value
    return result


def _decode_action_member(payload: bytes, *, context: str) -> list[dict[str, object]]:
    try:
        decoded = json.loads(
            payload,
            parse_float=Decimal,
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutCompletionIndexError(f"{context} is not strict JSON") from exc
    if type(decoded) is not list or any(type(row) is not dict for row in decoded):
        raise WyscoutCompletionIndexError(f"{context} must be one array of objects")
    return cast(list[dict[str, object]], decoded)


def completion_action_evidence(
    *,
    source_member_path: str,
    source_member_sha256: str,
    source_record_ordinal: int,
    raw_record: Mapping[str, object],
) -> CompletionActionEvidence:
    """Project one raw source action without coercion or label matching."""

    event_id = _strict_int(raw_record.get("eventId"), context="eventId")
    subevent_value = raw_record.get("subEventId")
    subevent_id = (
        _strict_int(subevent_value, context="subEventId") if type(subevent_value) is int else None
    )
    period = raw_record.get("matchPeriod")
    if type(period) is not str or period not in _PERIOD_RANK:
        raise WyscoutCompletionIndexError("matchPeriod must be exact admitted 1H or 2H")
    period_code = period
    _clock, clock_token = _event_seconds(raw_record.get("eventSec"))
    raw_tags, tag_ids = _raw_tags_and_projection(raw_record.get("tags"))
    return CompletionActionEvidence(
        source_member_path=source_member_path,
        source_member_sha256=source_member_sha256,
        source_record_ordinal=source_record_ordinal,
        source_event_record_id=_strict_int(raw_record.get("id"), context="id"),
        match_source_id=_strict_int(raw_record.get("matchId"), context="matchId"),
        action_period_code=period_code,
        period_rank=_PERIOD_RANK[period_code],
        period_elapsed_seconds_token=clock_token,
        player_source_id=_strict_int_or_null(raw_record.get("playerId"), context="playerId"),
        team_source_id=_strict_int_or_null(raw_record.get("teamId"), context="teamId"),
        action_event_taxonomy_id=event_id,
        action_subevent_taxonomy_id=subevent_id,
        raw_tags=raw_tags,
        possession_tag_ids=tag_ids,
        raw_record_sha256=hashlib.sha256(_canonical_value_bytes(dict(raw_record))).hexdigest(),
    )


def _action_payload(action: CompletionActionEvidence) -> dict[str, object]:
    return {
        "action_event_taxonomy_id": action.action_event_taxonomy_id,
        "action_period_code": action.action_period_code,
        "action_subevent_taxonomy_id": action.action_subevent_taxonomy_id,
        "match_source_id": action.match_source_id,
        "period_elapsed_seconds_token": action.period_elapsed_seconds_token,
        "period_rank": action.period_rank,
        "player_source_id": action.player_source_id,
        "possession_tag_ids": list(action.possession_tag_ids),
        "raw_record_sha256": action.raw_record_sha256,
        "raw_tags": list(action.raw_tags),
        "source_event_record_id": action.source_event_record_id,
        "source_member_path": action.source_member_path,
        "source_member_sha256": action.source_member_sha256,
        "source_record_ordinal": action.source_record_ordinal,
        "team_source_id": action.team_source_id,
    }


def action_frame(action: CompletionActionEvidence) -> bytes:
    payload = _canonical_value_bytes(_action_payload(action))
    return _ACTION_FRAME_VERSION + len(payload).to_bytes(8, "big") + payload


def period_membership_sha256(actions: Sequence[CompletionActionEvidence]) -> str:
    digest = hashlib.sha256()
    digest.update(_MEMBERSHIP_FRAME_VERSION)
    for action in actions:
        framed = action_frame(action)
        digest.update(len(framed).to_bytes(8, "big"))
        digest.update(framed)
    return digest.hexdigest()


def _read_verified_member(root: Path, spec: EventMemberSpec) -> bytes:
    chunks: list[bytes] = []
    digest = hashlib.sha256()
    size_bytes = 0
    with bridge._open_regular_beneath(root, spec.path) as descriptor:
        before = os.fstat(descriptor)
        while chunk := os.read(descriptor, _CHUNK_SIZE):
            size_bytes += len(chunk)
            if size_bytes > spec.size_bytes:
                raise WyscoutCompletionIndexError(
                    f"source member size exceeds authority: {spec.path}"
                )
            digest.update(chunk)
            chunks.append(chunk)
        after = os.fstat(descriptor)
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutCompletionIndexError(f"source member changed during read: {spec.path}")
    if size_bytes != spec.size_bytes or digest.hexdigest() != spec.sha256:
        raise WyscoutCompletionIndexError(
            f"source member conflicts with frozen bridge: {spec.path}"
        )
    return b"".join(chunks)


def _validate_source_manifest_bytes(manifest_root: Path) -> None:
    root = bridge._exact_root_argument(
        manifest_root,
        relative=_MANIFEST_ROOT_RELATIVE,
        context="manifest root",
    )
    with bridge._open_regular_beneath(root, _SOURCE_MANIFEST_RELATIVE_PATH) as descriptor:
        before = os.fstat(descriptor)
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, _CHUNK_SIZE):
            chunks.append(chunk)
        after = os.fstat(descriptor)
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise WyscoutCompletionIndexError("source snapshot manifest changed during read")
    payload = b"".join(chunks)
    if hashlib.sha256(payload).hexdigest() != _SOURCE_MANIFEST_SHA256:
        raise WyscoutCompletionIndexError("source snapshot manifest bytes drifted")


def _period_payload(period: CompletionPeriodRow) -> dict[str, object]:
    return {
        "action_count": period.action_count,
        "action_period_code": period.action_period_code,
        "match_source_id": period.match_source_id,
        "membership_sha256": period.membership_sha256,
        "period_rank": period.period_rank,
    }


def _index_payload(members: Sequence[CompletionMemberRow]) -> dict[str, object]:
    return {
        "aggregate_action_count": _AGGREGATE_ACTION_COUNT,
        "completion_manifest_sha256": _COMPLETION_MANIFEST_SHA256,
        "members": [
            {
                "indexed_action_count": member.indexed_action_count,
                "path": member.path,
                "periods": [_period_payload(period) for period in member.periods],
                "row_count": member.row_count,
                "sha256": member.sha256,
            }
            for member in members
        ],
        "schema_version": _INDEX_SCHEMA_VERSION,
        "source_manifest_id": str(_SOURCE_MANIFEST_ID),
        "source_manifest_sha256": _SOURCE_MANIFEST_SHA256,
    }


def _build_index_value(members: tuple[CompletionMemberRow, ...]) -> SourceCompletionIndex:
    payload = canonical_json_bytes(_index_payload(members))
    return SourceCompletionIndex(
        schema_version=_INDEX_SCHEMA_VERSION,
        source_manifest_id=_SOURCE_MANIFEST_ID,
        source_manifest_sha256=_SOURCE_MANIFEST_SHA256,
        completion_manifest_sha256=_COMPLETION_MANIFEST_SHA256,
        aggregate_action_count=_AGGREGATE_ACTION_COUNT,
        members=members,
        sha256=hashlib.sha256(payload).hexdigest(),
        canonical_bytes=payload,
    )


def derive_source_completion_index(
    *, source_root: Path, manifest_root: Path
) -> SourceCompletionIndex:
    """Reverify the full bridge, then derive the five-member canonical index."""

    root = bridge._exact_root_argument(
        source_root,
        relative=_SOURCE_ROOT_RELATIVE,
        context="source root",
    )
    manifest = bridge.build_source_snapshot_manifest(
        source_root=source_root,
        tenant_id=bridge._TENANT_ID,
    )
    if manifest.manifest_id != _SOURCE_MANIFEST_ID:
        raise WyscoutCompletionIndexError("source manifest identity drifted")
    _validate_source_manifest_bytes(manifest_root)
    members: list[CompletionMemberRow] = []
    for spec in _EVENT_MEMBERS:
        records = _decode_action_member(_read_verified_member(root, spec), context=spec.path)
        if len(records) != spec.row_count:
            raise WyscoutCompletionIndexError(f"source member row count drifted: {spec.path}")
        grouped: defaultdict[tuple[int, str], list[CompletionActionEvidence]] = defaultdict(list)
        for ordinal, record in enumerate(records):
            evidence = completion_action_evidence(
                source_member_path=spec.path,
                source_member_sha256=spec.sha256,
                source_record_ordinal=ordinal,
                raw_record=record,
            )
            grouped[(evidence.match_source_id, evidence.action_period_code)].append(evidence)
        periods: list[CompletionPeriodRow] = []
        for (match_source_id, period_code), actions in grouped.items():
            ordered = tuple(sorted(actions, key=lambda action: action.order_key))
            if len({action.source_event_record_id for action in ordered}) != len(ordered):
                raise WyscoutCompletionIndexError("provider event identity is not unique in period")
            periods.append(
                CompletionPeriodRow(
                    source_member_path=spec.path,
                    source_member_sha256=spec.sha256,
                    match_source_id=match_source_id,
                    action_period_code=period_code,
                    period_rank=_PERIOD_RANK[period_code],
                    action_count=len(ordered),
                    membership_sha256=period_membership_sha256(ordered),
                )
            )
        ordered_periods = tuple(sorted(periods, key=lambda period: period.key))
        members.append(
            CompletionMemberRow(
                path=spec.path,
                sha256=spec.sha256,
                row_count=spec.row_count,
                indexed_action_count=sum(period.action_count for period in ordered_periods),
                periods=ordered_periods,
            )
        )
        del records
    return validate_index(_build_index_value(tuple(members)))


def validate_index(index: SourceCompletionIndex) -> SourceCompletionIndex:
    """Validate canonical scope, ordering, uniqueness, counts, and address."""

    if index.sha256 != _ACCEPTED_INDEX_SHA256:
        raise WyscoutCompletionIndexError("completion index address is not accepted")
    expected_members = tuple((row.path, row.sha256, row.row_count) for row in _EVENT_MEMBERS)
    actual_members = tuple((row.path, row.sha256, row.row_count) for row in index.members)
    if (
        index.schema_version != _INDEX_SCHEMA_VERSION
        or index.source_manifest_id != _SOURCE_MANIFEST_ID
        or index.source_manifest_sha256 != _SOURCE_MANIFEST_SHA256
        or index.completion_manifest_sha256 != _COMPLETION_MANIFEST_SHA256
        or index.aggregate_action_count != _AGGREGATE_ACTION_COUNT
        or actual_members != expected_members
    ):
        raise WyscoutCompletionIndexError("completion index source bindings drifted")
    keys: list[tuple[str, int, int, str]] = []
    aggregate = 0
    for member in index.members:
        if member.indexed_action_count != sum(period.action_count for period in member.periods):
            raise WyscoutCompletionIndexError("member indexed action count drifted")
        if member.indexed_action_count != member.row_count:
            raise WyscoutCompletionIndexError("member row reconciliation drifted")
        if tuple(period.key for period in member.periods) != tuple(
            sorted(period.key for period in member.periods)
        ):
            raise WyscoutCompletionIndexError("period rows are not canonically ordered")
        for period in member.periods:
            if (
                period.source_member_path != member.path
                or period.source_member_sha256 != member.sha256
                or period.period_rank != _PERIOD_RANK.get(period.action_period_code)
                or period.action_count <= 0
                or len(period.membership_sha256) != 64
            ):
                raise WyscoutCompletionIndexError("period row binding drifted")
            keys.append(period.key)
        aggregate += member.indexed_action_count
    if len(keys) != len(set(keys)):
        raise WyscoutCompletionIndexError("completion index period identity is duplicated")
    if aggregate != index.aggregate_action_count:
        raise WyscoutCompletionIndexError("aggregate action reconciliation drifted")
    expected_payload = canonical_json_bytes(_index_payload(index.members))
    expected_sha = hashlib.sha256(expected_payload).hexdigest()
    if index.canonical_bytes != expected_payload or index.sha256 != expected_sha:
        raise WyscoutCompletionIndexError("completion index canonical address drifted")
    if expected_sha != _ACCEPTED_INDEX_SHA256:
        raise WyscoutCompletionIndexError("computed completion index address is not accepted")
    return index


def _require_exact_keys(row: Mapping[str, object], keys: set[str], *, context: str) -> None:
    if set(row) != keys:
        raise WyscoutCompletionIndexError(f"{context} keys drifted")


def _parse_index_payload(payload: bytes) -> SourceCompletionIndex:
    try:
        decoded = json.loads(payload, object_pairs_hook=_reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise WyscoutCompletionIndexError("completion index is not strict JSON") from exc
    if type(decoded) is not dict or canonical_json_bytes(decoded) != payload:
        raise WyscoutCompletionIndexError("completion index bytes are not canonical")
    root = cast(dict[str, object], decoded)
    _require_exact_keys(
        root,
        {
            "aggregate_action_count",
            "completion_manifest_sha256",
            "members",
            "schema_version",
            "source_manifest_id",
            "source_manifest_sha256",
        },
        context="index",
    )
    raw_members = root["members"]
    if type(raw_members) is not list:
        raise WyscoutCompletionIndexError("index members must be an array")
    members: list[CompletionMemberRow] = []
    for raw_member in cast(list[object], raw_members):
        if type(raw_member) is not dict:
            raise WyscoutCompletionIndexError("index member must be an object")
        member = cast(dict[str, object], raw_member)
        _require_exact_keys(
            member,
            {"indexed_action_count", "path", "periods", "row_count", "sha256"},
            context="member",
        )
        raw_periods = member["periods"]
        if type(raw_periods) is not list:
            raise WyscoutCompletionIndexError("member periods must be an array")
        periods: list[CompletionPeriodRow] = []
        for raw_period in cast(list[object], raw_periods):
            if type(raw_period) is not dict:
                raise WyscoutCompletionIndexError("period must be an object")
            period = cast(dict[str, object], raw_period)
            _require_exact_keys(
                period,
                {
                    "action_count",
                    "action_period_code",
                    "match_source_id",
                    "membership_sha256",
                    "period_rank",
                },
                context="period",
            )
            periods.append(
                CompletionPeriodRow(
                    source_member_path=cast(str, member["path"]),
                    source_member_sha256=cast(str, member["sha256"]),
                    match_source_id=_strict_int(
                        period["match_source_id"], context="match_source_id"
                    ),
                    action_period_code=cast(str, period["action_period_code"]),
                    period_rank=_strict_int(period["period_rank"], context="period_rank"),
                    action_count=_strict_int(period["action_count"], context="action_count"),
                    membership_sha256=cast(str, period["membership_sha256"]),
                )
            )
        members.append(
            CompletionMemberRow(
                path=cast(str, member["path"]),
                sha256=cast(str, member["sha256"]),
                row_count=_strict_int(member["row_count"], context="row_count"),
                indexed_action_count=_strict_int(
                    member["indexed_action_count"], context="indexed_action_count"
                ),
                periods=tuple(periods),
            )
        )
    try:
        source_manifest_id = UUID(cast(str, root["source_manifest_id"]))
    except (ValueError, TypeError) as exc:
        raise WyscoutCompletionIndexError("source manifest ID is not a UUID") from exc
    return validate_index(
        SourceCompletionIndex(
            schema_version=cast(str, root["schema_version"]),
            source_manifest_id=source_manifest_id,
            source_manifest_sha256=cast(str, root["source_manifest_sha256"]),
            completion_manifest_sha256=cast(str, root["completion_manifest_sha256"]),
            aggregate_action_count=_strict_int(
                root["aggregate_action_count"], context="aggregate_action_count"
            ),
            members=tuple(members),
            sha256=hashlib.sha256(payload).hexdigest(),
            canonical_bytes=payload,
        )
    )


def _index_filename(digest: str) -> str:
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
        raise WyscoutCompletionIndexError("index SHA-256 must be canonical lowercase")
    return f"{digest}.source-completion-index.json"


def materialize_source_completion_index(
    *, manifest_root: Path, index: SourceCompletionIndex
) -> SourceCompletionMaterialization:
    validated = validate_index(index)
    root = bridge._exact_root_argument(
        manifest_root,
        relative=_MANIFEST_ROOT_RELATIVE,
        context="manifest root",
    )
    filename = _index_filename(validated.sha256)
    root.parent.mkdir(mode=bridge._DIRECTORY_MODE, parents=True, exist_ok=True)
    if root.parent.is_symlink():
        raise bridge.WyscoutSourceManifestPathError("data root cannot be a link")
    try:
        with bridge._created_parent_descriptor(
            root.parent, (root.name, *_INDEX_DIRECTORY.parts)
        ) as parent:
            created = bridge._persist_immutable_file(parent, filename, validated.canonical_bytes)
            readback = bridge._read_immutable(parent, filename)
    except bridge.WyscoutSourceManifestConflictError as exc:
        raise WyscoutCompletionIndexConflictError("immutable completion index conflicts") from exc
    if readback is None or readback[0] != validated.canonical_bytes:
        raise WyscoutCompletionIndexError("immutable completion index readback failed")
    return SourceCompletionMaterialization(
        index=validated,
        relative_path=(
            _MANIFEST_ROOT_RELATIVE / Path(_INDEX_DIRECTORY.as_posix()) / filename
        ).as_posix(),
        size_bytes=len(validated.canonical_bytes),
        created=created,
    )


def load_source_completion_index(
    *, manifest_root: Path, index_sha256: str
) -> SourceCompletionIndex:
    if index_sha256 != _ACCEPTED_INDEX_SHA256:
        raise WyscoutCompletionIndexError("requested completion index address is not accepted")
    root = bridge._exact_root_argument(
        manifest_root,
        relative=_MANIFEST_ROOT_RELATIVE,
        context="manifest root",
    )
    filename = _index_filename(index_sha256)
    relative = (_INDEX_DIRECTORY / filename).as_posix()
    with bridge._open_regular_beneath(root, relative) as descriptor:
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, _CHUNK_SIZE):
            chunks.append(chunk)
    payload = b"".join(chunks)
    if hashlib.sha256(payload).hexdigest() != index_sha256:
        raise WyscoutCompletionIndexError("completion index payload address drifted")
    index = _parse_index_payload(payload)
    if index.sha256 != index_sha256:
        raise WyscoutCompletionIndexError("completion index filename address drifted")
    return index


def _immutable_json(value: object) -> object:
    if type(value) is dict:
        mapping = cast(dict[str, object], value)
        return MappingProxyType({key: _immutable_json(item) for key, item in mapping.items()})
    if type(value) is list:
        return tuple(_immutable_json(item) for item in cast(list[object], value))
    if value is None or type(value) in {bool, int, Decimal, str}:
        return value
    raise WyscoutCompletionIndexError(
        f"verified raw action contains unsupported value: {type(value).__name__}"
    )


def _vertical_slice_member(source_member_path: str) -> EventMemberSpec:
    if type(source_member_path) is not str:
        raise WyscoutCompletionIndexError("source member path must be an exact string")
    if source_member_path != _VERTICAL_SLICE_MEMBER_PATH:
        raise WyscoutCompletionIndexError("source member is not admitted for this vertical slice")
    matches = tuple(spec for spec in _EVENT_MEMBERS if spec.path == source_member_path)
    if len(matches) != 1:
        raise WyscoutCompletionIndexError("vertical-slice source member authority drifted")
    return matches[0]


def load_verified_match_population(
    *,
    source_root: Path,
    manifest_root: Path,
    index_sha256: str,
    source_member_path: str,
    match_source_id: int,
) -> VerifiedMatchPopulation:
    """Return the sole admitted raw match only after exact source/index equality."""

    if index_sha256 != _ACCEPTED_INDEX_SHA256:
        raise WyscoutCompletionIndexError("requested completion index address is not accepted")
    spec = _vertical_slice_member(source_member_path)
    if type(match_source_id) is not int or match_source_id <= 0:
        raise WyscoutCompletionIndexError("match source ID must be a strict positive integer")
    if match_source_id != _VERTICAL_SLICE_MATCH_SOURCE_ID:
        raise WyscoutCompletionIndexError("match is not admitted for this vertical slice")

    root = bridge._exact_root_argument(
        source_root,
        relative=_SOURCE_ROOT_RELATIVE,
        context="source root",
    )
    _validate_source_manifest_bytes(manifest_root)
    index = load_source_completion_index(
        manifest_root=manifest_root,
        index_sha256=index_sha256,
    )
    indexed_members = tuple(member for member in index.members if member.path == spec.path)
    if len(indexed_members) != 1:
        raise WyscoutCompletionIndexError("completion index does not bind the admitted member")
    indexed_member = indexed_members[0]
    if (
        indexed_member.sha256,
        indexed_member.row_count,
        indexed_member.indexed_action_count,
    ) != (spec.sha256, spec.row_count, spec.row_count):
        raise WyscoutCompletionIndexError("completion index member binding drifted")

    records = _decode_action_member(_read_verified_member(root, spec), context=spec.path)
    if len(records) != spec.row_count:
        raise WyscoutCompletionIndexError("source member decoded row count drifted")
    selected: list[tuple[CompletionActionEvidence, dict[str, object], bytes]] = []
    for ordinal, record in enumerate(records):
        row_match_source_id = _strict_int(
            record.get("matchId"),
            context=f"{spec.path}[{ordinal}].matchId",
        )
        if row_match_source_id != match_source_id:
            continue
        evidence = completion_action_evidence(
            source_member_path=spec.path,
            source_member_sha256=spec.sha256,
            source_record_ordinal=ordinal,
            raw_record=record,
        )
        canonical_raw_record = _canonical_value_bytes(record)
        if hashlib.sha256(canonical_raw_record).hexdigest() != evidence.raw_record_sha256:
            raise WyscoutCompletionIndexError("raw action digest binding drifted")
        selected.append((evidence, record, canonical_raw_record))
    if not selected:
        raise WyscoutCompletionIndexError("admitted match is missing from the verified member")

    ordered = tuple(sorted(selected, key=lambda item: item[0].order_key))
    match_evidence = tuple(item[0] for item in ordered)
    periods = validate_match_population(index=index, actions=match_evidence)
    if (
        len(match_evidence) != _VERTICAL_SLICE_MATCH_ACTION_COUNT
        or sum(period.action_count for period in periods) != _VERTICAL_SLICE_MATCH_ACTION_COUNT
    ):
        raise WyscoutCompletionIndexError("vertical-slice match action count drifted")
    completion = validate_checked_match_population(index=index, actions=match_evidence)
    actions = tuple(
        VerifiedMatchAction(
            raw_record=cast(Mapping[str, object], _immutable_json(record)),
            canonical_raw_record=canonical_raw_record,
            evidence=action,
        )
        for action, record, canonical_raw_record in ordered
    )
    return VerifiedMatchPopulation(
        index=index,
        source_member_path=spec.path,
        match_source_id=match_source_id,
        actions=actions,
        completion=completion,
    )


def validate_match_period_population(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> CompletionPeriodRow:
    """Compare an entire ordered source population to its accepted index row."""

    validated = validate_index(index)
    supplied = tuple(actions)
    if not supplied:
        raise WyscoutCompletionIndexError("whole-period omission is forbidden")
    first = supplied[0]
    key = (
        first.source_member_path,
        first.match_source_id,
        first.period_rank,
        first.action_period_code,
    )
    expected = validated.periods_by_key.get(key)
    if expected is None:
        raise WyscoutCompletionIndexError("supplied population has no indexed match-period")
    if any(
        (
            action.source_member_path,
            action.match_source_id,
            action.period_rank,
            action.action_period_code,
        )
        != key
        or action.source_member_sha256 != expected.source_member_sha256
        for action in supplied
    ):
        raise WyscoutCompletionIndexError("population crosses member, match, or period")
    identities = tuple(
        (action.source_record_ordinal, action.source_event_record_id) for action in supplied
    )
    if len(identities) != len(set(identities)):
        raise WyscoutCompletionIndexError("population contains duplicate action evidence")
    if tuple(action.order_key for action in supplied) != tuple(
        sorted(action.order_key for action in supplied)
    ):
        raise WyscoutCompletionIndexError("population is not in canonical action order")
    if len(supplied) != expected.action_count:
        raise WyscoutCompletionIndexError("population count differs from completion index")
    if period_membership_sha256(supplied) != expected.membership_sha256:
        raise WyscoutCompletionIndexError("population membership differs from completion index")
    return expected


def validate_match_population(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> tuple[CompletionPeriodRow, ...]:
    """Validate every indexed period for exactly one source member and match."""

    validated = validate_index(index)
    supplied = tuple(actions)
    if not supplied:
        raise WyscoutCompletionIndexError("whole-match omission is forbidden")
    first = supplied[0]
    match_scope = (first.source_member_path, first.match_source_id)
    if any(
        (action.source_member_path, action.match_source_id) != match_scope for action in supplied
    ):
        raise WyscoutCompletionIndexError("population crosses source member or match")
    expected = tuple(
        period
        for member in validated.members
        for period in member.periods
        if (period.source_member_path, period.match_source_id) == match_scope
    )
    if not expected:
        raise WyscoutCompletionIndexError("supplied population has no indexed match")
    grouped: defaultdict[tuple[int, str], list[CompletionActionEvidence]] = defaultdict(list)
    for action in supplied:
        grouped[(action.period_rank, action.action_period_code)].append(action)
    expected_keys = tuple((period.period_rank, period.action_period_code) for period in expected)
    if tuple(sorted(grouped)) != expected_keys:
        raise WyscoutCompletionIndexError("match population omits or adds an indexed period")
    for period in expected:
        validate_match_period_population(
            index=validated,
            actions=grouped[(period.period_rank, period.action_period_code)],
        )
    expected_count = sum(period.action_count for period in expected)
    if len(supplied) != expected_count:
        raise WyscoutCompletionIndexError("match population count does not reconcile")
    return expected


def _canonical_optional_source_uuid(
    record_kind: SourceRecordKind, source_id: int | None
) -> UUID | None:
    if source_id is None or source_id == 0:
        return None
    return canonical_source_uuid(record_kind, source_id)


def build_possession_period_sequence(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> PossessionPeriodSequence:
    """Build one contract sequence only after exact indexed population equality."""

    period = validate_match_period_population(index=index, actions=actions)
    return _build_possession_period_sequence_from_validated_period(
        index=index,
        actions=tuple(actions),
        period=period,
    )


def _build_possession_period_sequence_from_validated_period(
    *,
    index: SourceCompletionIndex,
    actions: tuple[CompletionActionEvidence, ...],
    period: CompletionPeriodRow,
) -> PossessionPeriodSequence:
    """Project a sequence after its caller performed the exact period comparison."""

    if index.sha256 != SOURCE_COMPLETION_INDEX_SHA256:
        raise WyscoutCompletionIndexError("contract completion-index binding drifted")
    match_id = canonical_source_uuid(SourceRecordKind.MATCH, period.match_source_id)
    entries = tuple(
        PossessionSequenceAction(
            action_id=canonical_source_uuid(SourceRecordKind.ACTION, action.source_event_record_id),
            source_event_record_id=action.source_event_record_id,
            source_row=WyscoutSourceRowReference(
                source_manifest_id=index.source_manifest_id,
                completion_relative_path=action.source_member_path,
                source_sha256=action.source_member_sha256,
                source_record_ordinal=action.source_record_ordinal,
                record_kind=SourceRecordKind.ACTION,
                raw_record_sha256=action.raw_record_sha256,
            ),
            match_id=match_id,
            player_id=_canonical_optional_source_uuid(
                SourceRecordKind.PLAYER, action.player_source_id
            ),
            team_id=_canonical_optional_source_uuid(SourceRecordKind.TEAM, action.team_source_id),
            action_event_taxonomy_id=action.action_event_taxonomy_id,
            action_subevent_taxonomy_id=action.action_subevent_taxonomy_id,
            action_period_code=action.action_period_code,
            period_rank=action.period_rank,
            period_elapsed_seconds=Decimal(action.period_elapsed_seconds_token),
            source_record_ordinal=action.source_record_ordinal,
            action_tag_ids=action.possession_tag_ids,
        )
        for action in actions
    )
    return PossessionPeriodSequence(
        match_id=match_id,
        source_completion_index_sha256=index.sha256,
        source_completion_membership_sha256=period.membership_sha256,
        action_period_code=period.action_period_code,
        period_action_count=period.action_count,
        actions=entries,
    )


def build_match_period_sequences(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> tuple[PossessionPeriodSequence, ...]:
    """Build every indexed period sequence for exactly one admitted source match."""

    periods = validate_match_population(index=index, actions=actions)
    supplied = tuple(actions)
    grouped: defaultdict[tuple[int, str], list[CompletionActionEvidence]] = defaultdict(list)
    for action in supplied:
        grouped[(action.period_rank, action.action_period_code)].append(action)
    return tuple(
        _build_possession_period_sequence_from_validated_period(
            index=index,
            actions=tuple(grouped[(period.period_rank, period.action_period_code)]),
            period=period,
        )
        for period in periods
    )


def _checked_period_record(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> _CheckedCompletionRecord:
    return _CheckedCompletionRecord(
        index=index,
        actions=tuple(actions),
        scope_kind="period",
    )


def _checked_match_record(
    *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
) -> _CheckedCompletionRecord:
    return _CheckedCompletionRecord(
        index=index,
        actions=tuple(actions),
        scope_kind="match",
    )


def _verify_completion_evidence(
    record: _CheckedCompletionRecord,
) -> _VerifiedCompletionRecord:
    if type(record.index) is not SourceCompletionIndex or type(record.actions) is not tuple:
        raise WyscoutCompletionIndexError("completion evidence has malformed index or population")
    if any(type(action) is not CompletionActionEvidence for action in record.actions):
        raise WyscoutCompletionIndexError("completion population evidence is malformed")
    sequences: tuple[PossessionPeriodSequence, ...]
    period_keys: tuple[tuple[str, int, int, str], ...]
    if record.scope_kind == "period":
        period = validate_match_period_population(index=record.index, actions=record.actions)
        sequences = (
            _build_possession_period_sequence_from_validated_period(
                index=record.index,
                actions=record.actions,
                period=period,
            ),
        )
        period_keys = (period.key,)
        complete_match = False
    elif record.scope_kind == "match":
        periods = validate_match_population(index=record.index, actions=record.actions)
        grouped: defaultdict[tuple[int, str], list[CompletionActionEvidence]] = defaultdict(list)
        for action in record.actions:
            grouped[(action.period_rank, action.action_period_code)].append(action)
        sequences = tuple(
            _build_possession_period_sequence_from_validated_period(
                index=record.index,
                actions=tuple(grouped[(period.period_rank, period.action_period_code)]),
                period=period,
            )
            for period in periods
        )
        period_keys = tuple(period.key for period in periods)
        complete_match = True
    else:
        raise WyscoutCompletionIndexError("completion evidence scope kind is malformed")
    return _VerifiedCompletionRecord(
        index=record.index,
        sequences=sequences,
        period_keys=period_keys,
        complete_match=complete_match,
    )


def _bind_completion_boundaries(
    issuer: _IssueCompletion,
) -> tuple[
    Callable[..., CheckedCompletionPopulation],
    Callable[..., CheckedCompletionPopulation],
]:
    def checked_period(
        *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
    ) -> CheckedCompletionPopulation:
        """Issue opaque authority only after one exact accepted period comparison."""

        capability = issuer(_checked_period_record(index=index, actions=actions))
        _checked_completion_record(capability)
        return capability

    def checked_match(
        *, index: SourceCompletionIndex, actions: Sequence[CompletionActionEvidence]
    ) -> CheckedCompletionPopulation:
        """Issue opaque authority only after every indexed match period agrees."""

        capability = issuer(_checked_match_record(index=index, actions=actions))
        _checked_completion_record(capability)
        return capability

    return checked_period, checked_match


(
    validate_checked_period_population,
    validate_checked_match_population,
) = _bind_completion_boundaries(_issue_checked_completion)


def _payload_without(
    payload: object, forbidden: frozenset[str], *, context: str
) -> dict[str, object]:
    if isinstance(
        payload,
        (
            SilverAction,
            SilverPossession,
            SilverPlayerMatchFact,
            GoldPlayerWindow,
            LayerManifest,
        ),
    ):
        raise WyscoutCompletionIndexError(f"{context} requires fields, not a direct model value")
    if not isinstance(payload, Mapping):
        raise WyscoutCompletionIndexError(f"{context} requires a field mapping")
    overlap = forbidden & payload.keys()
    if overlap:
        raise WyscoutCompletionIndexError(
            f"{context} cannot accept caller-selected derived fields: {','.join(sorted(overlap))}"
        )
    return dict(payload)


def require_checked_product[ProductValue](
    product: object, *, expected_type: type[ProductValue]
) -> ProductValue:
    """Return a product value only when its opaque checked handle is authentic."""

    verification = _verification_context()
    record = _checked_product_record(
        cast(CheckedProduct[object], product),
        verification=verification,
    )
    if type(record.value) is not expected_type:
        raise WyscoutCompletionIndexError(f"checked product is not exact {expected_type.__name__}")
    for completion in record.completions:
        _checked_completion_record(completion, verification=verification)
    return record.value


def _checked_value_for_completion[ProductValue](
    product: object,
    *,
    expected_type: type[ProductValue],
    completion: CheckedCompletionPopulation,
    verification: _VerificationContext,
) -> ProductValue:
    _checked_completion_record(completion, verification=verification)
    record = _checked_product_record(
        cast(CheckedProduct[object], product),
        verification=verification,
    )
    if type(record.value) is not expected_type or not any(
        candidate is completion for candidate in record.completions
    ):
        raise WyscoutCompletionIndexError(
            f"checked {expected_type.__name__} is not bound to this completion population"
        )
    return record.value


def _prepare_checked_silver_action(
    *,
    completion: CheckedCompletionPopulation,
    payload: Mapping[str, object],
    verification: _VerificationContext | None = None,
) -> SilverAction:
    context = verification if verification is not None else _verification_context()
    record = _checked_completion_record(completion, verification=context)
    prepared = _payload_without(
        payload,
        frozenset({"possession_period_sequence"}),
        context="checked SilverAction",
    )
    source_event_record_id = _strict_int(
        prepared.get("source_event_record_id"), context="source_event_record_id"
    )
    matches = tuple(
        (sequence, entry)
        for sequence in record.sequences
        for entry in sequence.actions
        if entry.source_event_record_id == source_event_record_id
    )
    if len(matches) != 1:
        raise WyscoutCompletionIndexError(
            "checked SilverAction must identify exactly one validated source action"
        )
    sequence, _entry = matches[0]
    prepared["possession_period_sequence"] = sequence
    value = SilverAction.model_validate(prepared)
    if value.possession_period_sequence is not sequence:
        raise WyscoutCompletionIndexError(
            "SilverAction did not retain the issued sequence identity"
        )
    return value


def _prepare_checked_silver_possession(
    *,
    completion: CheckedCompletionPopulation,
    payload: Mapping[str, object],
    contributing_actions: Sequence[CheckedProduct[SilverAction]],
    verification: _VerificationContext | None = None,
) -> SilverPossession:
    context = verification if verification is not None else _verification_context()
    _checked_completion_record(completion, verification=context)
    actions = tuple(
        _checked_value_for_completion(
            action,
            expected_type=SilverAction,
            completion=completion,
            verification=context,
        )
        for action in contributing_actions
    )
    if not actions:
        raise WyscoutCompletionIndexError("checked possession requires checked actions")
    prepared = _payload_without(
        payload,
        frozenset(
            {
                "source_rows",
                "contributing_actions",
                "action_ids",
                "first_action_order",
                "last_action_order",
            }
        ),
        context="checked SilverPossession",
    )
    sequence = actions[0].possession_period_sequence
    prepared.update(
        source_rows=tuple(
            sorted(
                {entry.source_row for entry in sequence.actions},
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        ),
        contributing_actions=actions,
        action_ids=tuple(action.action_id for action in actions),
        first_action_order=actions[0].action_order_key,
        last_action_order=actions[-1].action_order_key,
    )
    value = SilverPossession.model_validate(prepared)
    return value


def _prepare_checked_silver_player_match_fact(
    *,
    completion: CheckedCompletionPopulation,
    payload: Mapping[str, object],
    contributing_lineup_stints: Sequence[SilverLineupStint],
    contributing_actions: Sequence[CheckedProduct[SilverAction]],
    contributing_possessions: Sequence[CheckedProduct[SilverPossession]],
    verification: _VerificationContext | None = None,
) -> SilverPlayerMatchFact:
    context = verification if verification is not None else _verification_context()
    completion_record = _checked_completion_record(completion, verification=context)
    if not completion_record.complete_match:
        raise WyscoutCompletionIndexError(
            "checked player-match facts require a full match capability"
        )
    actions = tuple(
        _checked_value_for_completion(
            action,
            expected_type=SilverAction,
            completion=completion,
            verification=context,
        )
        for action in contributing_actions
    )
    possessions = tuple(
        _checked_value_for_completion(
            possession,
            expected_type=SilverPossession,
            completion=completion,
            verification=context,
        )
        for possession in contributing_possessions
    )
    prepared = _payload_without(
        payload,
        frozenset(
            {
                "source_rows",
                "lineup_evidence_present",
                "contributing_lineup_stints",
                "contributing_actions",
                "contributing_possessions",
            }
        ),
        context="checked SilverPlayerMatchFact",
    )
    player_id = prepared.get("player_id")
    match_id = prepared.get("match_id")
    expected_player_action_ids = {
        entry.action_id
        for sequence in completion_record.sequences
        for entry in sequence.actions
        if entry.player_id == player_id
    }
    if {action.action_id for action in actions} != expected_player_action_ids:
        raise WyscoutCompletionIndexError(
            "checked fact actions do not equal all validated row-player match actions"
        )
    if any(sequence.match_id != match_id for sequence in completion_record.sequences):
        raise WyscoutCompletionIndexError("checked fact match differs from completion population")
    selected_sequences = {action.possession_period_sequence for action in actions}
    source_rows = {
        entry.source_row for sequence in selected_sequences for entry in sequence.actions
    }
    source_rows.update(row for lineup in contributing_lineup_stints for row in lineup.source_rows)
    prepared.update(
        source_rows=tuple(
            sorted(
                source_rows,
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        ),
        lineup_evidence_present=bool(contributing_lineup_stints),
        contributing_lineup_stints=tuple(contributing_lineup_stints),
        contributing_actions=actions,
        contributing_possessions=possessions,
    )
    value = SilverPlayerMatchFact.model_validate(prepared)
    return value


def _prepare_checked_gold_player_window(
    *,
    payload: Mapping[str, object],
    contributing_player_match_facts: Sequence[CheckedProduct[SilverPlayerMatchFact]],
    verification: _VerificationContext | None = None,
) -> tuple[GoldPlayerWindow, tuple[CheckedCompletionPopulation, ...]]:
    context = verification if verification is not None else _verification_context()
    fact_records = tuple(
        _checked_product_record(
            cast(CheckedProduct[object], fact),
            verification=context,
        )
        for fact in contributing_player_match_facts
    )
    if not fact_records:
        raise WyscoutCompletionIndexError("checked Gold requires checked facts")
    facts_list: list[SilverPlayerMatchFact] = []
    for record in fact_records:
        if type(record.value) is not SilverPlayerMatchFact:
            raise WyscoutCompletionIndexError("checked product is not exact SilverPlayerMatchFact")
        facts_list.append(record.value)
    facts = tuple(facts_list)
    prepared = _payload_without(
        payload,
        frozenset(
            {
                "source_rows",
                "contributing_player_match_facts",
                "contributing_player_match_keys",
            }
        ),
        context="checked GoldPlayerWindow",
    )
    prepared.update(
        source_rows=tuple(
            sorted(
                {row for fact in facts for row in fact.source_rows},
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        ),
        contributing_player_match_facts=facts,
        contributing_player_match_keys=tuple(fact.primary_key for fact in facts),
    )
    value = GoldPlayerWindow.model_validate(prepared)
    completions = tuple(
        dict.fromkeys(completion for record in fact_records for completion in record.completions)
    )
    return value, completions


def _prepare_checked_layer_manifest(
    *,
    payload: Mapping[str, object],
    completions: Sequence[CheckedCompletionPopulation],
    contributing_products: Sequence[CheckedProduct[object]],
    verification: _VerificationContext | None = None,
) -> LayerManifest:
    context = verification if verification is not None else _verification_context()
    completion_tuple = tuple(completions)
    if not completion_tuple:
        raise WyscoutCompletionIndexError("checked layer manifests require completion scopes")
    records = tuple(
        _checked_completion_record(completion, verification=context)
        for completion in completion_tuple
    )
    if len({id(completion) for completion in completion_tuple}) != len(completion_tuple):
        raise WyscoutCompletionIndexError("layer completion scopes must be unique")
    if any(record.index.sha256 != records[0].index.sha256 for record in records[1:]):
        raise WyscoutCompletionIndexError("layer completion scopes must share one index binding")
    period_keys = tuple(key for record in records for key in record.period_keys)
    if len(period_keys) != len(set(period_keys)):
        raise WyscoutCompletionIndexError(
            "layer completion scopes cannot overlap one indexed period population"
        )
    product_records = tuple(
        _checked_product_record(product, verification=context) for product in contributing_products
    )
    prepared = _payload_without(
        payload,
        frozenset(),
        context="checked LayerManifest",
    )
    value = LayerManifest.model_validate(prepared)
    if value.layer is not Layer.BRONZE and not product_records:
        raise WyscoutCompletionIndexError("checked Silver/Gold manifests require checked products")
    supplied_completion_ids = {id(completion) for completion in completion_tuple}
    product_completion_ids = {
        id(completion)
        for product_record in product_records
        for completion in product_record.completions
    }
    if product_records and product_completion_ids != supplied_completion_ids:
        raise WyscoutCompletionIndexError(
            "checked manifest completion scopes must exactly equal product scopes"
        )
    for product_record in product_records:
        if not all(
            any(candidate is completion for candidate in completion_tuple)
            for completion in product_record.completions
        ):
            raise WyscoutCompletionIndexError(
                "checked manifest product has an unvalidated completion scope"
            )
        product = product_record.value
        if (
            getattr(product, "build_id", None) != value.build_id
            or getattr(product, "tenant_context", None) != value.tenant_context
        ):
            raise WyscoutCompletionIndexError(
                "checked manifest product differs from manifest build or tenant"
            )
        if value.layer is Layer.GOLD and type(product) is not GoldPlayerWindow:
            raise WyscoutCompletionIndexError("Gold manifest requires checked Gold products")
        if value.layer is Layer.SILVER and type(product) not in {
            SilverAction,
            SilverPossession,
            SilverPlayerMatchFact,
        }:
            raise WyscoutCompletionIndexError("Silver manifest product type is unsupported")
    return value


def _freeze_product_payload(payload: Mapping[str, object]) -> tuple[tuple[str, object], ...]:
    copied = dict(payload)
    if any(type(key) is not str for key in copied):
        raise WyscoutCompletionIndexError("checked product payload keys must be exact strings")
    return tuple(sorted(copied.items(), key=lambda item: item[0]))


def _thaw_product_payload(record: _CheckedProductRecord) -> dict[str, object]:
    if type(record.payload_items) is not tuple or any(
        type(item) is not tuple or len(item) != 2 or type(item[0]) is not str
        for item in record.payload_items
    ):
        raise WyscoutCompletionIndexError("checked product payload evidence is malformed")
    keys = tuple(item[0] for item in record.payload_items)
    if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
        raise WyscoutCompletionIndexError("checked product payload keys are not canonical")
    return dict(record.payload_items)


def _same_capability_sequence(
    left: Sequence[CheckedCompletionPopulation],
    right: Sequence[CheckedCompletionPopulation],
) -> bool:
    return len(left) == len(right) and all(
        candidate is expected for candidate, expected in zip(left, right, strict=True)
    )


def _verify_product_evidence(
    record: _CheckedProductRecord,
    *,
    verification: _VerificationContext,
) -> _VerifiedProductRecord:
    tuple_fields = (
        record.completions,
        record.lineup_stints,
        record.action_dependencies,
        record.possession_dependencies,
        record.fact_dependencies,
        record.product_dependencies,
    )
    if any(type(field) is not tuple for field in tuple_fields):
        raise WyscoutCompletionIndexError("checked product dependency evidence is malformed")
    payload = _thaw_product_payload(record)
    kind = record.construction_kind
    expected_completions: tuple[CheckedCompletionPopulation, ...]
    value: object
    if kind == "silver_action":
        if (
            len(record.completions) != 1
            or record.lineup_stints
            or record.action_dependencies
            or record.possession_dependencies
            or record.fact_dependencies
            or record.product_dependencies
        ):
            raise WyscoutCompletionIndexError("checked Action dependency graph is malformed")
        expected_completions = record.completions
        value = _prepare_checked_silver_action(
            completion=record.completions[0],
            payload=payload,
            verification=verification,
        )
    elif kind == "silver_possession":
        if (
            len(record.completions) != 1
            or not record.action_dependencies
            or record.lineup_stints
            or record.possession_dependencies
            or record.fact_dependencies
            or record.product_dependencies
        ):
            raise WyscoutCompletionIndexError("checked Possession dependency graph is malformed")
        expected_completions = record.completions
        value = _prepare_checked_silver_possession(
            completion=record.completions[0],
            payload=payload,
            contributing_actions=record.action_dependencies,
            verification=verification,
        )
    elif kind == "silver_player_match_fact":
        if len(record.completions) != 1 or record.fact_dependencies or record.product_dependencies:
            raise WyscoutCompletionIndexError("checked Fact dependency graph is malformed")
        expected_completions = record.completions
        value = _prepare_checked_silver_player_match_fact(
            completion=record.completions[0],
            payload=payload,
            contributing_lineup_stints=record.lineup_stints,
            contributing_actions=record.action_dependencies,
            contributing_possessions=record.possession_dependencies,
            verification=verification,
        )
    elif kind == "gold_player_window":
        if (
            not record.fact_dependencies
            or record.lineup_stints
            or record.action_dependencies
            or record.possession_dependencies
            or record.product_dependencies
        ):
            raise WyscoutCompletionIndexError("checked Gold dependency graph is malformed")
        value, expected_completions = _prepare_checked_gold_player_window(
            payload=payload,
            contributing_player_match_facts=record.fact_dependencies,
            verification=verification,
        )
    elif kind == "layer_manifest":
        if (
            record.lineup_stints
            or record.action_dependencies
            or record.possession_dependencies
            or record.fact_dependencies
        ):
            raise WyscoutCompletionIndexError("checked manifest dependency graph is malformed")
        expected_completions = record.completions
        value = _prepare_checked_layer_manifest(
            payload=payload,
            completions=record.completions,
            contributing_products=record.product_dependencies,
            verification=verification,
        )
    else:
        raise WyscoutCompletionIndexError("checked product construction kind is malformed")
    for completion in expected_completions:
        _checked_completion_record(completion, verification=verification)
    if not _same_capability_sequence(record.completions, expected_completions):
        raise WyscoutCompletionIndexError("checked product completion scopes drifted")
    if type(record.value) is not type(value) or record.value != value:
        raise WyscoutCompletionIndexError("checked product value differs from exact rederivation")
    return _VerifiedProductRecord(
        construction_kind=kind,
        value=value,
        completions=expected_completions,
    )


def _bind_checked_product_boundaries(
    issuer: _IssueProduct,
) -> tuple[
    Callable[..., CheckedProduct[SilverAction]],
    Callable[..., CheckedProduct[SilverPossession]],
    Callable[..., CheckedProduct[SilverPlayerMatchFact]],
    Callable[..., CheckedProduct[GoldPlayerWindow]],
    Callable[..., CheckedProduct[LayerManifest]],
]:
    def issue[ProductValue](
        record: _CheckedProductRecord,
        *,
        verification: _VerificationContext,
    ) -> CheckedProduct[ProductValue]:
        if not record.completions:
            raise WyscoutCompletionIndexError("checked products require completion capabilities")
        for completion in record.completions:
            _checked_completion_record(completion, verification=verification)
        capability = cast(CheckedProduct[ProductValue], issuer(record))
        _checked_product_record(
            cast(CheckedProduct[object], capability),
            verification=verification,
        )
        return capability

    def checked_action(
        *,
        completion: CheckedCompletionPopulation,
        payload: Mapping[str, object],
    ) -> CheckedProduct[SilverAction]:
        """Construct checked Action with the exact reader-produced period sequence."""

        verification = _verification_context()
        return issue(
            _CheckedProductRecord(
                construction_kind="silver_action",
                value=_prepare_checked_silver_action(
                    completion=completion,
                    payload=payload,
                    verification=verification,
                ),
                completions=(completion,),
                payload_items=_freeze_product_payload(payload),
            ),
            verification=verification,
        )

    def checked_possession(
        *,
        completion: CheckedCompletionPopulation,
        payload: Mapping[str, object],
        contributing_actions: Sequence[CheckedProduct[SilverAction]],
    ) -> CheckedProduct[SilverPossession]:
        """Construct checked possession only from checked actions of one population."""

        dependencies = tuple(contributing_actions)
        verification = _verification_context()
        return issue(
            _CheckedProductRecord(
                construction_kind="silver_possession",
                value=_prepare_checked_silver_possession(
                    completion=completion,
                    payload=payload,
                    contributing_actions=dependencies,
                    verification=verification,
                ),
                completions=(completion,),
                payload_items=_freeze_product_payload(payload),
                action_dependencies=dependencies,
            ),
            verification=verification,
        )

    def checked_fact(
        *,
        completion: CheckedCompletionPopulation,
        payload: Mapping[str, object],
        contributing_lineup_stints: Sequence[SilverLineupStint],
        contributing_actions: Sequence[CheckedProduct[SilverAction]],
        contributing_possessions: Sequence[CheckedProduct[SilverPossession]],
    ) -> CheckedProduct[SilverPlayerMatchFact]:
        """Construct checked Fact only from one complete checked match population."""

        lineups = tuple(contributing_lineup_stints)
        actions = tuple(contributing_actions)
        possessions = tuple(contributing_possessions)
        verification = _verification_context()
        return issue(
            _CheckedProductRecord(
                construction_kind="silver_player_match_fact",
                value=_prepare_checked_silver_player_match_fact(
                    completion=completion,
                    payload=payload,
                    contributing_lineup_stints=lineups,
                    contributing_actions=actions,
                    contributing_possessions=possessions,
                    verification=verification,
                ),
                completions=(completion,),
                payload_items=_freeze_product_payload(payload),
                lineup_stints=lineups,
                action_dependencies=actions,
                possession_dependencies=possessions,
            ),
            verification=verification,
        )

    def checked_gold(
        *,
        payload: Mapping[str, object],
        contributing_player_match_facts: Sequence[CheckedProduct[SilverPlayerMatchFact]],
    ) -> CheckedProduct[GoldPlayerWindow]:
        """Construct checked Gold only from transitively checked Facts."""

        verification = _verification_context()
        value, completions = _prepare_checked_gold_player_window(
            payload=payload,
            contributing_player_match_facts=(facts := tuple(contributing_player_match_facts)),
            verification=verification,
        )
        return issue(
            _CheckedProductRecord(
                construction_kind="gold_player_window",
                value=value,
                completions=completions,
                payload_items=_freeze_product_payload(payload),
                fact_dependencies=facts,
            ),
            verification=verification,
        )

    def checked_manifest(
        *,
        payload: Mapping[str, object],
        completions: Sequence[CheckedCompletionPopulation],
        contributing_products: Sequence[CheckedProduct[object]],
    ) -> CheckedProduct[LayerManifest]:
        """Construct checked manifest only from every accepted population scope."""

        completion_tuple = tuple(completions)
        products = tuple(contributing_products)
        verification = _verification_context()
        return issue(
            _CheckedProductRecord(
                construction_kind="layer_manifest",
                value=_prepare_checked_layer_manifest(
                    payload=payload,
                    completions=completion_tuple,
                    contributing_products=products,
                    verification=verification,
                ),
                completions=completion_tuple,
                payload_items=_freeze_product_payload(payload),
                product_dependencies=products,
            ),
            verification=verification,
        )

    return checked_action, checked_possession, checked_fact, checked_gold, checked_manifest


(
    build_checked_silver_action,
    build_checked_silver_possession,
    build_checked_silver_player_match_fact,
    build_checked_gold_player_window,
    build_checked_layer_manifest,
) = _bind_checked_product_boundaries(_issue_checked_product)

del _issue_checked_completion
del _issue_checked_product


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    derive = subcommands.add_parser("derive")
    derive.add_argument("--source-root", required=True, type=Path)
    derive.add_argument("--manifest-root", required=True, type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command != "derive":
            raise WyscoutCompletionIndexError("unsupported completion-index command")
        index = derive_source_completion_index(
            source_root=arguments.source_root,
            manifest_root=arguments.manifest_root,
        )
        result = materialize_source_completion_index(
            manifest_root=arguments.manifest_root,
            index=index,
        )
    except (OSError, bridge.WyscoutSourceManifestError, WyscoutCompletionIndexError) as exc:
        print(f"W04 Wyscout source-completion index failed: {exc}", file=sys.stderr)
        return 1
    state = "created" if result.created else "confirmed"
    print(
        f"W04 Wyscout source-completion index {state}: {result.relative_path} "
        f"sha256={result.index.sha256} rows={result.index.aggregate_action_count} "
        f"size_bytes={result.size_bytes}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "CheckedCompletionPopulation",
    "CheckedProduct",
    "CompletionActionEvidence",
    "CompletionMemberRow",
    "CompletionPeriodRow",
    "SourceCompletionIndex",
    "SourceCompletionMaterialization",
    "VerifiedMatchAction",
    "VerifiedMatchPopulation",
    "WyscoutCompletionIndexConflictError",
    "WyscoutCompletionIndexError",
    "action_frame",
    "build_match_period_sequences",
    "build_possession_period_sequence",
    "build_checked_gold_player_window",
    "build_checked_layer_manifest",
    "build_checked_silver_action",
    "build_checked_silver_player_match_fact",
    "build_checked_silver_possession",
    "completion_action_evidence",
    "derive_source_completion_index",
    "load_source_completion_index",
    "load_verified_match_population",
    "main",
    "materialize_source_completion_index",
    "period_membership_sha256",
    "require_checked_product",
    "validate_index",
    "validate_match_population",
    "validate_match_period_population",
    "validate_checked_match_population",
    "validate_checked_period_population",
]
