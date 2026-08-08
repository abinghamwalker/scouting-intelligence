"""Closed W04 Wyscout Bronze-to-Gold data contracts.

This module defines immutable boundary values only.  It deliberately contains no
filesystem access, serializer, product materialisation, runtime orchestration, or
provider access.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from decimal import Decimal, localcontext
from enum import StrEnum
from itertools import groupby
from typing import Annotated, Literal, Self, cast
from unicodedata import normalize
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import Field, Strict, StringConstraints, model_validator

from .evidence import (
    DependencyKind,
    DependencyLineage,
    EvidenceDependency,
    LicenceUseClass,
    Sha256Digest,
    SourceUseClassification,
)
from .primitives import ContractModel, StrictUuid, TenantContext, UtcInstant

SOURCE_MANIFEST_ID = UUID("4e16bdb5-afe7-5601-88ad-adc124cfce3b")
SOURCE_MANIFEST_SHA256 = "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
SOURCE_COMPLETION_INDEX_SHA256 = "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
SOURCE_RELEASE = datetime(2020, 1, 28, 14, 24, 27, tzinfo=UTC)
SOURCE_ACQUIRED_AT = datetime(2026, 7, 29, 15, 51, 8, 598589, tzinfo=UTC)
TENANT_ID = UUID("65a43912-d412-5ff9-a364-7f84d1ad6c5d")

_ATTRIBUTION_TEXT = (
    "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
    "Wyscout, figshare collection v5, licensed CC BY 4.0."
)

FIELD_CANDIDATE_SHA256 = "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959"
FIELD_ACCEPTANCE_SHA256 = "beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436"
POSSESSION_CANDIDATE_SHA256 = "3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881"
POSSESSION_ACCEPTANCE_SHA256 = "2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1"
FEATURE_SCHEMA_HASH = "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
FEATURE_ACCEPTANCE_SHA256 = "d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c"
IDENTITY_CANDIDATE_SHA256 = "9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c"
IDENTITY_ACCEPTANCE_SHA256 = "37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86"

PRODUCT_CONTRACT_PREIMAGE_SHA256 = (
    "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
)
SCHEMA_BUNDLE_PREIMAGE_SHA256 = "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"

ROLE_CONTEXT_VERSION = "w04-neutral-role-context-v1"
ROLE_CONTEXT_STATE = "neutral_unscoped"
ROLE_CONTEXT_NAMESPACE = uuid5(NAMESPACE_URL, "urn:scouting-intelligence:role-context")
ROLE_CONTEXT_ID = uuid5(
    ROLE_CONTEXT_NAMESPACE,
    f"{ROLE_CONTEXT_VERSION}:{ROLE_CONTEXT_STATE}",
)

type StrictNonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
type StrictPositiveInt = Annotated[int, Field(strict=True, ge=1)]
type StrictDecimal = Annotated[Decimal, Strict()]
type ReasonCode = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^[A-Z][A-Z0-9_]{1,127}$"),
]
type JsonPath = Annotated[
    str,
    Strict(),
    StringConstraints(pattern=r"^\$(?:\.[A-Za-z][A-Za-z0-9]*(?:\[\])?|\.\*)*$"),
]


def accepted_source_classification() -> SourceUseClassification:
    """Return the exact immutable source rights inherited by every W04 row."""

    return SourceUseClassification(
        use_class=LicenceUseClass.RESTRICTED,
        derived_data_allowed=True,
        internal_review_allowed=True,
        export_allowed=False,
        attribution_required=True,
        attribution_text=_ATTRIBUTION_TEXT,
    )


def _classification_is_exact(classification: SourceUseClassification) -> bool:
    return classification == accepted_source_classification()


def _tenant_is_exact(tenant_context: TenantContext) -> bool:
    return tenant_context.tenant_id == TENANT_ID and tenant_context.club_id is None


class CanonicalJsonKind(StrEnum):
    """The exact JSON type retained by immutable raw evidence."""

    NULL = "null"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    OBJECT = "object"


class CanonicalJsonNull(ContractModel):
    kind: Literal[CanonicalJsonKind.NULL] = CanonicalJsonKind.NULL
    value: None = None


class CanonicalJsonBoolean(ContractModel):
    kind: Literal[CanonicalJsonKind.BOOLEAN] = CanonicalJsonKind.BOOLEAN
    value: bool


class CanonicalJsonInteger(ContractModel):
    kind: Literal[CanonicalJsonKind.INTEGER] = CanonicalJsonKind.INTEGER
    value: int = Field(strict=True)


class CanonicalJsonNumber(ContractModel):
    kind: Literal[CanonicalJsonKind.NUMBER] = CanonicalJsonKind.NUMBER
    value: StrictDecimal

    @model_validator(mode="after")
    def number_is_finite(self) -> Self:
        if not self.value.is_finite():
            raise ValueError("canonical JSON numbers must be finite")
        return self


class CanonicalJsonString(ContractModel):
    kind: Literal[CanonicalJsonKind.STRING] = CanonicalJsonKind.STRING
    value: str = Field(strict=True)


class CanonicalJsonArray(ContractModel):
    kind: Literal[CanonicalJsonKind.ARRAY] = CanonicalJsonKind.ARRAY
    value: tuple[CanonicalJsonValue, ...]


class CanonicalJsonMember(ContractModel):
    key: str = Field(strict=True)
    value: CanonicalJsonValue

    @model_validator(mode="after")
    def key_is_unicode_scalar_text(self) -> Self:
        if any(0xD800 <= ord(character) <= 0xDFFF for character in self.key):
            raise ValueError("canonical JSON object keys cannot contain surrogates")
        return self


class CanonicalJsonObject(ContractModel):
    kind: Literal[CanonicalJsonKind.OBJECT] = CanonicalJsonKind.OBJECT
    value: tuple[CanonicalJsonMember, ...]

    @model_validator(mode="after")
    def members_are_unique_and_sorted(self) -> Self:
        keys = tuple(member.key for member in self.value)
        if len(keys) != len(set(keys)):
            raise ValueError("canonical JSON object keys must be unique")
        if keys != tuple(sorted(keys)):
            raise ValueError("canonical JSON object keys must be sorted")
        return self


type CanonicalJsonValue = Annotated[
    CanonicalJsonNull
    | CanonicalJsonBoolean
    | CanonicalJsonInteger
    | CanonicalJsonNumber
    | CanonicalJsonString
    | CanonicalJsonArray
    | CanonicalJsonObject,
    Field(discriminator="kind"),
]


def canonicalize_json_value(value: object) -> CanonicalJsonValue:
    """Convert already parsed JSON into a deeply immutable typed value.

    JSON non-integer numbers must already be :class:`Decimal`; accepting a Python
    float here would silently retain parser rounding rather than source evidence.
    """

    if value is None:
        return CanonicalJsonNull()
    if type(value) is bool:
        return CanonicalJsonBoolean(value=value)
    if type(value) is int:
        return CanonicalJsonInteger(value=value)
    if type(value) is Decimal:
        return CanonicalJsonNumber(value=value)
    if type(value) is str:
        return CanonicalJsonString(value=value)
    if type(value) in {list, tuple}:
        sequence = cast(list[object] | tuple[object, ...], value)
        return CanonicalJsonArray(value=tuple(canonicalize_json_value(item) for item in sequence))
    if type(value) is dict:
        mapping = cast(dict[object, object], value)
        if any(type(key) is not str for key in mapping):
            raise TypeError("canonical JSON objects require string keys")
        string_mapping = cast(dict[str, object], value)
        return CanonicalJsonObject(
            value=tuple(
                CanonicalJsonMember(
                    key=key,
                    value=canonicalize_json_value(string_mapping[key]),
                )
                for key in sorted(string_mapping)
            )
        )
    raise TypeError(f"unsupported parsed JSON value: {type(value).__name__}")


def _decimal_json_token(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("canonical JSON numbers must be finite")
    if value.is_zero():
        return "0"
    token = format(value, "f")
    if "." in token:
        token = token.rstrip("0").rstrip(".")
    return token


def _raw_json_text(value: CanonicalJsonValue) -> str:
    if isinstance(value, CanonicalJsonNull):
        return "null"
    if isinstance(value, CanonicalJsonBoolean):
        return "true" if value.value else "false"
    if isinstance(value, CanonicalJsonInteger):
        return str(value.value)
    if isinstance(value, CanonicalJsonNumber):
        return _decimal_json_token(value.value)
    if isinstance(value, CanonicalJsonString):
        return json.dumps(value.value, ensure_ascii=False, separators=(",", ":"))
    if isinstance(value, CanonicalJsonArray):
        return "[" + ",".join(_raw_json_text(item) for item in value.value) + "]"
    return (
        "{"
        + ",".join(
            json.dumps(member.key, ensure_ascii=False) + ":" + _raw_json_text(member.value)
            for member in value.value
        )
        + "}"
    )


def canonical_raw_json_bytes(value: CanonicalJsonValue) -> bytes:
    """Return deterministic UTF-8 JSON bytes for the retained raw value."""

    return _raw_json_text(value).encode("utf-8")


def canonical_contract_json_bytes(value: ContractModel) -> bytes:
    """Return deterministic canonical JSON for an immutable contract value."""

    return json.dumps(
        value.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


class SourceRecordKind(StrEnum):
    COMPETITION = "competition"
    TEAM = "team"
    PLAYER = "player"
    EVENT_TAXONOMY = "event-taxonomy"
    TAG_TAXONOMY = "tag-taxonomy"
    MATCH = "match"
    ACTION = "action"


class CountryPartition(StrEnum):
    ENGLAND = "england"
    FRANCE = "france"
    GERMANY = "germany"
    ITALY = "italy"
    SPAIN = "spain"


_SOURCE_PATH_ROWS: dict[
    str,
    tuple[SourceRecordKind, str, CountryPartition | None, int],
] = {
    "objects/competitions.json": (
        SourceRecordKind.COMPETITION,
        "39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1",
        None,
        7,
    ),
    "objects/teams.json": (
        SourceRecordKind.TEAM,
        "9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d",
        None,
        142,
    ),
    "objects/players.json": (
        SourceRecordKind.PLAYER,
        "877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e",
        None,
        3603,
    ),
    "objects/eventid2name.csv": (
        SourceRecordKind.EVENT_TAXONOMY,
        "ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842",
        None,
        36,
    ),
    "objects/tags2name.csv": (
        SourceRecordKind.TAG_TAXONOMY,
        "e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922",
        None,
        59,
    ),
}
for _country_title in ("England", "France", "Germany", "Italy", "Spain"):
    _country = CountryPartition(_country_title.lower())
    _match_digests = {
        "England": "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29",
        "France": "851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea",
        "Germany": "6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9",
        "Italy": "afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725",
        "Spain": "9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce",
    }
    _action_digests = {
        "England": "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad",
        "France": "18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317",
        "Germany": "2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3",
        "Italy": "b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84",
        "Spain": "b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154",
    }
    _SOURCE_PATH_ROWS[f"archive-members/matches_{_country_title}.json"] = (
        SourceRecordKind.MATCH,
        _match_digests[_country_title],
        _country,
        {
            "England": 380,
            "France": 380,
            "Germany": 306,
            "Italy": 380,
            "Spain": 380,
        }[_country_title],
    )
    _SOURCE_PATH_ROWS[f"archive-members/events_{_country_title}.json"] = (
        SourceRecordKind.ACTION,
        _action_digests[_country_title],
        _country,
        {
            "England": 643150,
            "France": 632807,
            "Germany": 519407,
            "Italy": 647372,
            "Spain": 628659,
        }[_country_title],
    )


class WyscoutRawSourceRowReference(ContractModel):
    """Physical source-row identity before discriminator admission."""

    source_manifest_id: StrictUuid
    completion_relative_path: str = Field(strict=True)
    source_sha256: Sha256Digest
    source_record_ordinal: StrictNonNegativeInt

    @model_validator(mode="after")
    def source_row_is_manifested(self) -> Self:
        if self.source_manifest_id != SOURCE_MANIFEST_ID:
            raise ValueError("source_manifest_id must equal the accepted source manifest")
        row = _SOURCE_PATH_ROWS.get(self.completion_relative_path)
        if row is None:
            raise ValueError("completion_relative_path is not an admitted record source")
        if row[1] != self.source_sha256:
            raise ValueError("source_sha256 must equal the admitted completion row")
        if self.source_record_ordinal >= row[3]:
            raise ValueError("source_record_ordinal must be below the manifested row count")
        return self

    @property
    def country_partition(self) -> CountryPartition | None:
        return _SOURCE_PATH_ROWS[self.completion_relative_path][2]


class WyscoutSourceRowReference(WyscoutRawSourceRowReference):
    """One exact admitted row with its envelope-owned record family."""

    record_kind: SourceRecordKind
    raw_record_sha256: Sha256Digest

    @model_validator(mode="after")
    def record_kind_matches_completion_path(self) -> Self:
        if _SOURCE_PATH_ROWS[self.completion_relative_path][0] is not self.record_kind:
            raise ValueError("record_kind must come only from the exact completion path map")
        return self


class WyscoutSourceRecordEnvelope(ContractModel):
    """The exact seven-kind completion-reader envelope."""

    envelope_version: Literal["w04-source-record-envelope-v1"] = "w04-source-record-envelope-v1"
    source_manifest_id: StrictUuid
    completion_relative_path: str = Field(strict=True)
    source_sha256: Sha256Digest
    source_record_ordinal: StrictNonNegativeInt
    record_kind: SourceRecordKind
    raw_record: CanonicalJsonObject

    @model_validator(mode="after")
    def envelope_is_exact(self) -> Self:
        reference = self.source_row_reference
        if (
            reference.raw_record_sha256
            != hashlib.sha256(canonical_raw_json_bytes(self.raw_record)).hexdigest()
        ):
            raise AssertionError("raw record digest construction failed")
        return self

    @property
    def source_row_reference(self) -> WyscoutSourceRowReference:
        return WyscoutSourceRowReference(
            source_manifest_id=self.source_manifest_id,
            completion_relative_path=self.completion_relative_path,
            source_sha256=self.source_sha256,
            source_record_ordinal=self.source_record_ordinal,
            record_kind=self.record_kind,
            raw_record_sha256=hashlib.sha256(canonical_raw_json_bytes(self.raw_record)).hexdigest(),
        )


class RawKindState(StrEnum):
    MISSING = "missing"
    NULL = "null"
    NON_STRING = "non-string"
    STRING_UNKNOWN_SAFE = "string-unknown-safe"
    STRING_UNSAFE = "string-unsafe"


class RawKindEvidence(ContractModel):
    """Root-safe canonical identity for an unknown envelope discriminator."""

    envelope_version: Literal["w04-raw-kind-v1"] = "w04-raw-kind-v1"
    raw_kind_state: RawKindState
    value_present: bool
    value: CanonicalJsonValue
    envelope_bytes: bytes
    raw_kind_sha256: Sha256Digest

    @model_validator(mode="after")
    def evidence_matches_state_and_framed_digest(self) -> Self:
        if not self.value_present:
            if not isinstance(self.value, CanonicalJsonNull):
                raise ValueError("missing raw kind cannot carry a value")
            expected_state = RawKindState.MISSING
        elif isinstance(self.value, CanonicalJsonNull):
            expected_state = RawKindState.NULL
        elif not isinstance(self.value, CanonicalJsonString):
            expected_state = RawKindState.NON_STRING
        else:
            if self.value.value in {kind.value for kind in SourceRecordKind}:
                raise ValueError("known record kinds cannot enter unknown quarantine")
            expected_state = (
                RawKindState.STRING_UNKNOWN_SAFE
                if _SAFE_UNKNOWN_KIND.fullmatch(self.value.value)
                else RawKindState.STRING_UNSAFE
            )
        if self.raw_kind_state is not expected_state:
            raise ValueError("raw_kind_state must be derived from the exact typed value")
        expected_bytes = _raw_kind_envelope_bytes(expected_state, self.value_present, self.value)
        if self.envelope_bytes != expected_bytes:
            raise ValueError("raw-kind envelope bytes must be canonical")
        frame = b"w04-raw-kind-v1\x00" + len(expected_bytes).to_bytes(8, "big") + expected_bytes
        if self.raw_kind_sha256 != hashlib.sha256(frame).hexdigest():
            raise ValueError("raw_kind_sha256 must equal the framed envelope digest")
        return self


_SAFE_UNKNOWN_KIND = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")


def _raw_kind_envelope_bytes(
    state: RawKindState,
    value_present: bool,
    value: CanonicalJsonValue,
) -> bytes:
    state_token = state.value.replace("-", "_").upper()
    return (
        '{"envelope_version":"w04-raw-kind-v1","state":'
        + json.dumps(state_token)
        + ',"value":'
        + _raw_json_text(value)
        + ',"value_present":'
        + ("true" if value_present else "false")
        + "}"
    ).encode("utf-8")


def classify_raw_record_kind(*, value_present: bool, value: object = None) -> RawKindEvidence:
    """Classify only the envelope discriminator; known kinds are rejected here."""

    canonical = canonicalize_json_value(value)
    if not value_present:
        if value is not None:
            raise ValueError("missing raw kind cannot carry a value")
        state = RawKindState.MISSING
    elif value is None:
        state = RawKindState.NULL
    elif type(value) is not str:
        state = RawKindState.NON_STRING
    else:
        string_value = value
        if string_value in {kind.value for kind in SourceRecordKind}:
            raise ValueError("known record kinds cannot enter unknown quarantine")
        state = (
            RawKindState.STRING_UNKNOWN_SAFE
            if _SAFE_UNKNOWN_KIND.fullmatch(string_value)
            else RawKindState.STRING_UNSAFE
        )
    envelope = _raw_kind_envelope_bytes(state, value_present, canonical)
    frame = b"w04-raw-kind-v1\x00" + len(envelope).to_bytes(8, "big") + envelope
    return RawKindEvidence(
        raw_kind_state=state,
        value_present=value_present,
        value=canonical,
        envelope_bytes=envelope,
        raw_kind_sha256=hashlib.sha256(frame).hexdigest(),
    )


class AuthorityKind(StrEnum):
    FIELD = "FIELD"
    POSSESSION = "POSSESSION"
    SUPPORTED_FEATURE = "SUPPORTED_FEATURE"
    IDENTITY = "IDENTITY"


class WyscoutAuthorityReference(ContractModel):
    """The exact seven-field accepted-authority reference."""

    acceptance_id: str = Field(strict=True)
    acceptance_sha256: Sha256Digest
    authority_kind: AuthorityKind
    candidate_id: str = Field(strict=True)
    candidate_sha256: Sha256Digest
    review_id: str = Field(strict=True)
    review_sha256: Sha256Digest

    @model_validator(mode="after")
    def reference_is_the_accepted_authority(self) -> Self:
        if self.model_dump(mode="json") != _AUTHORITY_REFERENCE_ROWS[self.authority_kind]:
            raise ValueError("authority reference differs from the accepted seven-field row")
        return self


_AUTHORITY_REFERENCE_ROWS: dict[AuthorityKind, dict[str, str]] = {
    AuthorityKind.FIELD: {
        "acceptance_id": "w04-wyscout-field-semantic-acceptance-v2",
        "acceptance_sha256": FIELD_ACCEPTANCE_SHA256,
        "authority_kind": "FIELD",
        "candidate_id": "w04-wyscout-field-registry-v2",
        "candidate_sha256": FIELD_CANDIDATE_SHA256,
        "review_id": "w04-wyscout-field-semantic-independent-review-v2-R1",
        "review_sha256": "76c4744d302b4c6d86f4d537498695e365f0d3c733211bfafcb1e5c2805c0886",
    },
    AuthorityKind.POSSESSION: {
        "acceptance_id": "w04-wyscout-possession-semantic-acceptance-v2",
        "acceptance_sha256": POSSESSION_ACCEPTANCE_SHA256,
        "authority_kind": "POSSESSION",
        "candidate_id": "w04-wyscout-possession-taxonomy-v2",
        "candidate_sha256": POSSESSION_CANDIDATE_SHA256,
        "review_id": "w04-wyscout-possession-semantic-independent-review-v2-R1",
        "review_sha256": "c1e249c377d11258415cea84e83f0d3742436ebcb7aa640b885c44d245cb1e97",
    },
    AuthorityKind.SUPPORTED_FEATURE: {
        "acceptance_id": "w04-wyscout-supported-feature-registry-acceptance-v1",
        "acceptance_sha256": FEATURE_ACCEPTANCE_SHA256,
        "authority_kind": "SUPPORTED_FEATURE",
        "candidate_id": "w04-wyscout-supported-count-features-v1",
        "candidate_sha256": FEATURE_SCHEMA_HASH,
        "review_id": "w04-wyscout-supported-feature-registry-independent-review-R1",
        "review_sha256": "a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73",
    },
    AuthorityKind.IDENTITY: {
        "acceptance_id": "w04-wyscout-identity-ruleset-acceptance-v1",
        "acceptance_sha256": IDENTITY_ACCEPTANCE_SHA256,
        "authority_kind": "IDENTITY",
        "candidate_id": "w04-wyscout-identity-ruleset-v1",
        "candidate_sha256": IDENTITY_CANDIDATE_SHA256,
        "review_id": "w04-wyscout-identity-ruleset-independent-review-R1",
        "review_sha256": "62295d6a1da681fbec23285ca6c74124e3ef44fe3962c1472f0523ef46fb2a19",
    },
}


def accepted_authority_references() -> tuple[WyscoutAuthorityReference, ...]:
    """Return FIELD, POSSESSION, SUPPORTED_FEATURE, IDENTITY in fixed order."""

    references: list[WyscoutAuthorityReference] = []
    for kind in AuthorityKind:
        row: dict[str, object] = dict(_AUTHORITY_REFERENCE_ROWS[kind])
        row["authority_kind"] = kind
        references.append(WyscoutAuthorityReference.model_validate(row))
    return tuple(references)


_AUTHORITY_CLOCK_ROWS: dict[AuthorityKind, tuple[datetime, datetime, datetime]] = {
    AuthorityKind.FIELD: (
        datetime(2026, 7, 30, 20, 22, 17, tzinfo=UTC),
        datetime(2026, 7, 30, 21, 15, 45, tzinfo=UTC),
        datetime(2026, 7, 30, 21, 21, 23, tzinfo=UTC),
    ),
    AuthorityKind.POSSESSION: (
        datetime(2026, 7, 30, 22, 14, 21, tzinfo=UTC),
        datetime(2026, 7, 31, 8, 24, 2, tzinfo=UTC),
        datetime(2026, 7, 31, 8, 28, 40, tzinfo=UTC),
    ),
    AuthorityKind.SUPPORTED_FEATURE: (
        datetime(2026, 7, 31, 8, 37, tzinfo=UTC),
        datetime(2026, 7, 31, 10, 7, 30, tzinfo=UTC),
        datetime(2026, 7, 31, 10, 15, 16, tzinfo=UTC),
    ),
    AuthorityKind.IDENTITY: (
        datetime(2026, 7, 31, 12, 44, 27, tzinfo=UTC),
        datetime(2026, 7, 31, 14, 11, 16, tzinfo=UTC),
        datetime(2026, 7, 31, 14, 15, 26, tzinfo=UTC),
    ),
}


class WyscoutAuthorityClock(ContractModel):
    """Exact decision, independent-review, and master-acceptance clocks."""

    authority_kind: AuthorityKind
    decided_at: UtcInstant
    reviewed_at: UtcInstant
    accepted_at: UtcInstant

    @model_validator(mode="after")
    def clocks_are_the_accepted_authority_clocks(self) -> Self:
        if (self.decided_at, self.reviewed_at, self.accepted_at) != _AUTHORITY_CLOCK_ROWS[
            self.authority_kind
        ]:
            raise ValueError("authority clocks differ from the accepted records")
        if not self.decided_at <= self.reviewed_at <= self.accepted_at:
            raise ValueError("authority clocks must be decision-review-acceptance ordered")
        return self


def accepted_authority_clocks() -> tuple[WyscoutAuthorityClock, ...]:
    return tuple(
        WyscoutAuthorityClock(
            authority_kind=kind,
            decided_at=_AUTHORITY_CLOCK_ROWS[kind][0],
            reviewed_at=_AUTHORITY_CLOCK_ROWS[kind][1],
            accepted_at=_AUTHORITY_CLOCK_ROWS[kind][2],
        )
        for kind in AuthorityKind
    )


class WyscoutSourceAuthority(ContractModel):
    """Closed source snapshot, tenant, receipt-clock, and rights authority."""

    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    tenant_context: TenantContext
    available_at: UtcInstant
    acquired_at: UtcInstant
    classification: SourceUseClassification

    @model_validator(mode="after")
    def source_authority_is_exact(self) -> Self:
        if (
            self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or not _tenant_is_exact(self.tenant_context)
            or self.available_at != SOURCE_RELEASE
            or self.acquired_at != SOURCE_ACQUIRED_AT
            or not _classification_is_exact(self.classification)
        ):
            raise ValueError("source authority differs from the accepted source snapshot")
        return self


def accepted_source_authority() -> WyscoutSourceAuthority:
    return WyscoutSourceAuthority(
        source_manifest_id=SOURCE_MANIFEST_ID,
        source_manifest_sha256=SOURCE_MANIFEST_SHA256,
        tenant_context=TenantContext(tenant_id=TENANT_ID),
        available_at=SOURCE_RELEASE,
        acquired_at=SOURCE_ACQUIRED_AT,
        classification=accepted_source_classification(),
    )


class WyscoutRowLineage(ContractModel):
    """Exact source, authority, and dependency lineage carried by every product row."""

    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    source_completion_index_sha256: Sha256Digest
    source_rows: Annotated[tuple[WyscoutSourceRowReference, ...], Field(min_length=1)]
    authority_references: Annotated[
        tuple[WyscoutAuthorityReference, ...], Field(min_length=4, max_length=4)
    ]
    authority_clocks: Annotated[
        tuple[WyscoutAuthorityClock, ...], Field(min_length=4, max_length=4)
    ]
    source_authority: WyscoutSourceAuthority
    dependency_lineage: DependencyLineage

    @model_validator(mode="after")
    def lineage_is_closed(self) -> Self:
        if (
            self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or self.source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256
        ):
            raise ValueError("lineage must bind the immutable source manifest and completion index")
        if tuple(reference.authority_kind for reference in self.authority_references) != tuple(
            AuthorityKind
        ):
            raise ValueError("authority references must have the exact fixed order")
        if self.authority_references != accepted_authority_references():
            raise ValueError("lineage authority references must be the accepted rows")
        if self.authority_clocks != accepted_authority_clocks():
            raise ValueError("lineage authority clocks must be the accepted rows")
        if self.source_authority != accepted_source_authority():
            raise ValueError("lineage source authority must be the accepted snapshot")
        identities = tuple(
            (row.completion_relative_path, row.source_record_ordinal) for row in self.source_rows
        )
        if identities != tuple(sorted(identities)) or len(identities) != len(set(identities)):
            raise ValueError(
                "source rows must be unique by physical path/ordinal and lexically ordered"
            )
        _validate_exact_dependency_lineage(self.dependency_lineage)
        return self


class RawFieldMeasurement(ContractModel):
    json_path: JsonPath
    measured_json_type: CanonicalJsonKind


def _top_level_measurements(raw_record: CanonicalJsonObject) -> tuple[RawFieldMeasurement, ...]:
    return tuple(
        RawFieldMeasurement(
            json_path=f"$.{member.key}",
            measured_json_type=member.value.kind,
        )
        for member in raw_record.value
    )


class BronzeKnownRecord(ContractModel):
    schema_version: Literal["w04-wyscout-bronze-known-record-v1"] = (
        "w04-wyscout-bronze-known-record-v1"
    )
    build_id: Sha256Digest
    tenant_context: TenantContext
    source_row: WyscoutSourceRowReference
    raw_record: CanonicalJsonObject
    raw_record_sha256: Sha256Digest
    measured_raw_fields: Annotated[tuple[RawFieldMeasurement, ...], Field(min_length=1)]
    admission: Literal["ADMITTED_BY_EXACT_COMPLETION_PATH"] = "ADMITTED_BY_EXACT_COMPLETION_PATH"
    classification: SourceUseClassification
    lineage: WyscoutRowLineage

    @model_validator(mode="after")
    def raw_record_is_preserved_once(self) -> Self:
        digest = hashlib.sha256(canonical_raw_json_bytes(self.raw_record)).hexdigest()
        if digest != self.raw_record_sha256 or digest != self.source_row.raw_record_sha256:
            raise ValueError("Bronze raw record digest must equal canonical source bytes")
        if self.source_row not in self.lineage.source_rows:
            raise ValueError("Bronze source row must occur in lineage")
        if self.measured_raw_fields != _top_level_measurements(self.raw_record):
            raise ValueError("measured raw paths/types must exactly cover top-level raw fields")
        if not _tenant_is_exact(self.tenant_context):
            raise ValueError("Bronze rows require the accepted no-club tenant context")
        if self.tenant_context != self.lineage.source_authority.tenant_context:
            raise ValueError("Bronze tenant must equal source authority tenant")
        if not _classification_is_exact(self.classification):
            raise ValueError("Bronze classification must equal the accepted restricted rights")
        return self


class BronzeRejectedRecord(ContractModel):
    schema_version: Literal["w04-wyscout-bronze-rejected-record-v1"] = (
        "w04-wyscout-bronze-rejected-record-v1"
    )
    build_id: Sha256Digest
    tenant_context: TenantContext
    source_row: WyscoutRawSourceRowReference
    raw_record: CanonicalJsonObject
    raw_record_sha256: Sha256Digest
    raw_kind: RawKindEvidence
    rejection_code: Literal["UNKNOWN_RECORD_KIND"] = "UNKNOWN_RECORD_KIND"
    classification: SourceUseClassification
    lineage: WyscoutRowLineage

    @model_validator(mode="after")
    def rejected_record_is_closed(self) -> Self:
        if (
            self.raw_record_sha256
            != hashlib.sha256(canonical_raw_json_bytes(self.raw_record)).hexdigest()
        ):
            raise ValueError("rejected raw record digest must equal canonical bytes")
        if not _tenant_is_exact(self.tenant_context):
            raise ValueError("rejected records require the accepted no-club tenant")
        if not _classification_is_exact(self.classification):
            raise ValueError("rejected-record rights must equal the source authority")
        if self.tenant_context != self.lineage.source_authority.tenant_context:
            raise ValueError("rejected-record tenant must equal source authority tenant")
        if not any(
            row.completion_relative_path == self.source_row.completion_relative_path
            and row.source_sha256 == self.source_row.source_sha256
            and row.source_record_ordinal == self.source_row.source_record_ordinal
            and row.raw_record_sha256 == self.raw_record_sha256
            for row in self.lineage.source_rows
        ):
            raise ValueError("rejected source row must occur exactly in lineage")
        return self


class RejectedFieldDecision(StrEnum):
    PRESERVE_UNMAPPED = "PRESERVE_UNMAPPED"
    FORBIDDEN = "FORBIDDEN"


_FIELD_REGISTRY_ROWS_TEXT = """\
competition|$|PRESERVE_UNMAPPED|object
competition|$.area|PRESERVE_UNMAPPED|object
competition|$.area.alpha2code|PRESERVE_UNMAPPED|string
competition|$.area.alpha3code|PRESERVE_UNMAPPED|string
competition|$.area.id|PRESERVE_UNMAPPED|integer,string
competition|$.area.name|FORBIDDEN|string
competition|$.format|PRESERVE_UNMAPPED|string
competition|$.name|FORBIDDEN|string
competition|$.type|PRESERVE_UNMAPPED|string
competition|$.wyId|TRANSFORM|integer
team|$|PRESERVE_UNMAPPED|object
team|$.area|PRESERVE_UNMAPPED|object
team|$.area.alpha2code|PRESERVE_UNMAPPED|string
team|$.area.alpha3code|PRESERVE_UNMAPPED|string
team|$.area.id|PRESERVE_UNMAPPED|integer,string
team|$.area.name|FORBIDDEN|string
team|$.city|FORBIDDEN|string
team|$.name|FORBIDDEN|string
team|$.officialName|FORBIDDEN|string
team|$.type|PRESERVE_UNMAPPED|string
team|$.wyId|TRANSFORM|integer
player|$|PRESERVE_UNMAPPED|object
player|$.birthArea|PRESERVE_UNMAPPED|object
player|$.birthArea.alpha2code|PRESERVE_UNMAPPED|string
player|$.birthArea.alpha3code|PRESERVE_UNMAPPED|string
player|$.birthArea.id|PRESERVE_UNMAPPED|integer,string
player|$.birthArea.name|FORBIDDEN|string
player|$.birthDate|PRESERVE_UNMAPPED|string
player|$.currentNationalTeamId|FORBIDDEN|integer,string
player|$.currentTeamId|FORBIDDEN|integer,null,string
player|$.firstName|FORBIDDEN|string
player|$.foot|PRESERVE_UNMAPPED|string
player|$.height|PRESERVE_UNMAPPED|integer
player|$.lastName|FORBIDDEN|string
player|$.middleName|FORBIDDEN|string
player|$.passportArea|PRESERVE_UNMAPPED|object
player|$.passportArea.alpha2code|PRESERVE_UNMAPPED|string
player|$.passportArea.alpha3code|PRESERVE_UNMAPPED|string
player|$.passportArea.id|PRESERVE_UNMAPPED|integer,string
player|$.passportArea.name|FORBIDDEN|string
player|$.role|FORBIDDEN|object
player|$.role.code2|FORBIDDEN|string
player|$.role.code3|FORBIDDEN|string
player|$.role.name|FORBIDDEN|string
player|$.shortName|FORBIDDEN|string
player|$.weight|PRESERVE_UNMAPPED|integer
player|$.wyId|TRANSFORM|integer
match|$|PRESERVE_UNMAPPED|object
match|$.competitionId|TRANSFORM|integer
match|$.date|PRESERVE_UNMAPPED|string
match|$.dateutc|TRANSFORM|string
match|$.duration|PRESERVE_UNMAPPED|string
match|$.gameweek|TRANSFORM|integer
match|$.label|FORBIDDEN|string
match|$.referees|PRESERVE_UNMAPPED|array
match|$.referees[]|PRESERVE_UNMAPPED|object
match|$.referees[].refereeId|PRESERVE_UNMAPPED|integer
match|$.referees[].role|PRESERVE_UNMAPPED|string
match|$.roundId|TRANSFORM|integer
match|$.seasonId|TRANSFORM|integer
match|$.status|PRESERVE_UNMAPPED|string
match|$.teamsData|PRESERVE_UNMAPPED|object
match|$.teamsData.*|PRESERVE_UNMAPPED|object
match|$.teamsData.*.coachId|PRESERVE_UNMAPPED|integer
match|$.teamsData.*.formation|PRESERVE_UNMAPPED|object
match|$.teamsData.*.formation.bench|PRESERVE_UNMAPPED|array
match|$.teamsData.*.formation.bench[]|PRESERVE_UNMAPPED|object
match|$.teamsData.*.formation.bench[].goals|FORBIDDEN|string
match|$.teamsData.*.formation.bench[].ownGoals|FORBIDDEN|string
match|$.teamsData.*.formation.bench[].playerId|TRANSFORM|integer
match|$.teamsData.*.formation.bench[].redCards|FORBIDDEN|string
match|$.teamsData.*.formation.bench[].yellowCards|FORBIDDEN|string
match|$.teamsData.*.formation.lineup|PRESERVE_UNMAPPED|array
match|$.teamsData.*.formation.lineup[]|PRESERVE_UNMAPPED|object
match|$.teamsData.*.formation.lineup[].goals|FORBIDDEN|string
match|$.teamsData.*.formation.lineup[].ownGoals|FORBIDDEN|string
match|$.teamsData.*.formation.lineup[].playerId|TRANSFORM|integer
match|$.teamsData.*.formation.lineup[].redCards|FORBIDDEN|string
match|$.teamsData.*.formation.lineup[].yellowCards|FORBIDDEN|string
match|$.teamsData.*.formation.substitutions|PRESERVE_UNMAPPED|array,string
match|$.teamsData.*.formation.substitutions[]|PRESERVE_UNMAPPED|object
match|$.teamsData.*.formation.substitutions[].minute|TRANSFORM|integer
match|$.teamsData.*.formation.substitutions[].playerIn|TRANSFORM|integer
match|$.teamsData.*.formation.substitutions[].playerOut|TRANSFORM|integer
match|$.teamsData.*.hasFormation|PRESERVE_UNMAPPED|integer
match|$.teamsData.*.score|FORBIDDEN|integer
match|$.teamsData.*.scoreET|FORBIDDEN|integer
match|$.teamsData.*.scoreHT|FORBIDDEN|integer
match|$.teamsData.*.scoreP|FORBIDDEN|integer
match|$.teamsData.*.side|PRESERVE_UNMAPPED|string
match|$.teamsData.*.teamId|TRANSFORM|integer
match|$.venue|FORBIDDEN|string
match|$.winner|FORBIDDEN|integer
match|$.wyId|TRANSFORM|integer
action|$|PRESERVE_UNMAPPED|object
action|$.eventId|TRANSFORM|integer
action|$.eventName|FORBIDDEN|string
action|$.eventSec|TRANSFORM|integer,number
action|$.id|TRANSFORM|integer
action|$.matchId|TRANSFORM|integer
action|$.matchPeriod|TRANSFORM|string
action|$.playerId|TRANSFORM|integer
action|$.positions|TRANSFORM|array
action|$.positions[]|PRESERVE_UNMAPPED|object
action|$.positions[].x|PRESERVE_UNMAPPED|integer
action|$.positions[].y|PRESERVE_UNMAPPED|integer
action|$.subEventId|TRANSFORM|integer,string
action|$.subEventName|FORBIDDEN|string
action|$.tags|PRESERVE_UNMAPPED|array
action|$.tags[]|PRESERVE_UNMAPPED|object
action|$.tags[].id|TRANSFORM|integer
action|$.teamId|TRANSFORM|integer
event-taxonomy|$.event|TRANSFORM|integer
event-taxonomy|$.event_label|FORBIDDEN|string
event-taxonomy|$.subevent|TRANSFORM|integer
event-taxonomy|$.subevent_label|FORBIDDEN|string
tag-taxonomy|$.Description|FORBIDDEN|string
tag-taxonomy|$.Label|FORBIDDEN|string
tag-taxonomy|$.Tag|TRANSFORM|integer
"""


def _field_registry_rows() -> dict[
    tuple[SourceRecordKind, str], tuple[str, frozenset[CanonicalJsonKind]]
]:
    rows: dict[tuple[SourceRecordKind, str], tuple[str, frozenset[CanonicalJsonKind]]] = {}
    for line in _FIELD_REGISTRY_ROWS_TEXT.splitlines():
        record_kind, path, decision, kinds = line.split("|")
        rows[(SourceRecordKind(record_kind), path)] = (
            decision,
            frozenset(CanonicalJsonKind(kind) for kind in kinds.split(",")),
        )
    if len(rows) != 119:
        raise AssertionError("embedded field-v2 registry must contain exactly 119 rows")
    return rows


_FIELD_REGISTRY_ROWS = _field_registry_rows()


class BronzeRejectedField(ContractModel):
    schema_version: Literal["w04-wyscout-bronze-rejected-field-v1"] = (
        "w04-wyscout-bronze-rejected-field-v1"
    )
    build_id: Sha256Digest
    tenant_context: TenantContext
    source_row: WyscoutSourceRowReference
    record_kind: SourceRecordKind
    json_path: JsonPath
    original_value: CanonicalJsonValue
    original_value_sha256: Sha256Digest
    measured_json_type: CanonicalJsonKind
    action_event_taxonomy_id: StrictNonNegativeInt | None = None
    decision: RejectedFieldDecision
    reason_code: ReasonCode
    field_authority: WyscoutAuthorityReference
    classification: SourceUseClassification
    lineage: WyscoutRowLineage

    @model_validator(mode="after")
    def rejected_value_is_exact(self) -> Self:
        if self.source_row.record_kind is not self.record_kind:
            raise ValueError("rejected-field record_kind must equal its exact source row")
        if self.original_value.kind is not self.measured_json_type:
            raise ValueError("measured_json_type must equal the retained typed value")
        if (
            self.original_value_sha256
            != hashlib.sha256(canonical_raw_json_bytes(self.original_value)).hexdigest()
        ):
            raise ValueError("rejected-field digest must equal canonical raw value")
        if self.field_authority != accepted_authority_references()[0]:
            raise ValueError("rejected fields must bind the exact accepted field-v2 authority")
        registry_row = _FIELD_REGISTRY_ROWS.get((self.record_kind, self.json_path))
        if registry_row is None:
            raise ValueError("rejected field is absent from the accepted 119-row registry")
        registry_decision, admitted_kinds = registry_row
        is_subevent = (
            self.record_kind is SourceRecordKind.ACTION and self.json_path == "$.subEventId"
        )
        if is_subevent:
            expected_reason = {
                CanonicalJsonKind.STRING: ActionSubeventReason.STRING.value,
                CanonicalJsonKind.BOOLEAN: ActionSubeventReason.BOOLEAN.value,
                CanonicalJsonKind.NULL: ActionSubeventReason.NULL.value,
                CanonicalJsonKind.NUMBER: ActionSubeventReason.NUMBER.value,
                CanonicalJsonKind.ARRAY: ActionSubeventReason.ARRAY.value,
                CanonicalJsonKind.OBJECT: ActionSubeventReason.OBJECT.value,
                CanonicalJsonKind.INTEGER: ActionSubeventReason.UNKNOWN_INTEGER.value,
            }[self.original_value.kind]
            if (
                self.decision is not RejectedFieldDecision.PRESERVE_UNMAPPED
                or self.reason_code != expected_reason
            ):
                raise ValueError("rejected subevent decision/reason must equal R21 authority")
            if (
                isinstance(self.original_value, CanonicalJsonInteger)
                and self.action_event_taxonomy_id is not None
                and (self.action_event_taxonomy_id, self.original_value.value)
                in _ADMITTED_EVENT_SUBEVENT_PAIRS
            ):
                raise ValueError("an admitted strict integer subevent cannot be rejected")
        else:
            if self.action_event_taxonomy_id is not None:
                raise ValueError("non-subevent rejected fields cannot carry action-event evidence")
            if self.original_value.kind not in admitted_kinds:
                raise ValueError("measured type differs from the accepted field-v2 registry")
            if registry_decision == "TRANSFORM":
                raise ValueError("successfully transformable registry fields cannot be rejected")
            expected_decision = RejectedFieldDecision(registry_decision)
            expected_reason = f"FIELD_V2_{registry_decision}"
            if self.decision is not expected_decision or self.reason_code != expected_reason:
                raise ValueError("generic rejected-field decision/reason differs from field-v2")
        if not _classification_is_exact(self.classification):
            raise ValueError("W04 rejected evidence retains exact restricted source rights")
        if not _tenant_is_exact(self.tenant_context):
            raise ValueError("rejected fields require the accepted no-club tenant")
        if self.source_row not in self.lineage.source_rows:
            raise ValueError("rejected-field source row must occur in lineage")
        return self


_SOURCE_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5",
)


def canonical_source_uuid(record_kind: SourceRecordKind, source_id: int) -> UUID:
    """Derive exact numeric-key identity for supported canonical entity kinds."""

    if record_kind not in {
        SourceRecordKind.COMPETITION,
        SourceRecordKind.TEAM,
        SourceRecordKind.PLAYER,
        SourceRecordKind.MATCH,
        SourceRecordKind.ACTION,
    }:
        raise ValueError("taxonomy records do not receive canonical source UUIDs")
    if type(source_id) is not int or source_id <= 0:
        raise ValueError("source identity must be a strict positive integer")
    kind_namespace = uuid5(_SOURCE_NAMESPACE, record_kind.value)
    return uuid5(kind_namespace, f"figshare-v5:{source_id}")


class WyscoutProductRow(ContractModel):
    """Shared immutable provenance carried by the eight Silver and Gold rows."""

    construction_authority_state: Literal["semantic_only_unchecked"] = "semantic_only_unchecked"
    build_id: Sha256Digest
    tenant_context: TenantContext
    source_completion_index_sha256: Sha256Digest
    source_rows: Annotated[tuple[WyscoutSourceRowReference, ...], Field(min_length=1)]
    lineage: WyscoutRowLineage

    @model_validator(mode="after")
    def tenant_is_the_fixed_poc_context(self) -> Self:
        if not _tenant_is_exact(self.tenant_context):
            raise ValueError("W04 rows require the accepted no-club tenant context")
        if (
            self.source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256
            or self.source_completion_index_sha256 != self.lineage.source_completion_index_sha256
        ):
            raise ValueError("row must bind the accepted source-completion index")
        if self.tenant_context != self.lineage.source_authority.tenant_context:
            raise ValueError("row tenant must equal lineage source authority tenant")
        keys = tuple(
            (row.completion_relative_path, row.source_record_ordinal) for row in self.source_rows
        )
        if keys != tuple(sorted(set(keys))):
            raise ValueError("selected source rows must be unique and physically ordered")
        if any(row not in self.lineage.source_rows for row in self.source_rows):
            raise ValueError("every selected source row must occur exactly in lineage")
        return self


def _require_source_kinds(
    lineage: WyscoutRowLineage,
    required: frozenset[SourceRecordKind],
) -> None:
    actual = {row.record_kind for row in lineage.source_rows}
    missing = required - actual
    if missing:
        raise ValueError(
            "lineage is missing required source families: "
            + ",".join(sorted(kind.value for kind in missing))
        )


class SilverCompetition(WyscoutProductRow):
    competition_schema_version: Literal["w04-wyscout-silver-competition-v1"] = (
        "w04-wyscout-silver-competition-v1"
    )
    competition_source_id: StrictPositiveInt
    competition_id: StrictUuid

    @model_validator(mode="after")
    def competition_identity_is_exact(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.COMPETITION
        ):
            raise ValueError("competition must select exactly its physical competition row")
        if self.competition_id != canonical_source_uuid(
            SourceRecordKind.COMPETITION, self.competition_source_id
        ):
            raise ValueError("competition_id must use the exact source UUIDv5 rule")
        return self


class SilverTeam(WyscoutProductRow):
    team_schema_version: Literal["w04-wyscout-silver-team-v1"] = "w04-wyscout-silver-team-v1"
    team_source_id: StrictPositiveInt
    team_id: StrictUuid

    @model_validator(mode="after")
    def team_identity_is_exact(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.TEAM
        ):
            raise ValueError("team must select exactly its physical team row")
        if self.team_id != canonical_source_uuid(SourceRecordKind.TEAM, self.team_source_id):
            raise ValueError("team_id must use the exact source UUIDv5 rule")
        return self


class SilverPlayer(WyscoutProductRow):
    player_schema_version: Literal["w04-wyscout-silver-player-v1"] = "w04-wyscout-silver-player-v1"
    player_source_id: StrictPositiveInt
    player_id: StrictUuid

    @model_validator(mode="after")
    def player_identity_is_exact_and_nonzero(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.PLAYER
        ):
            raise ValueError("player must select exactly its physical player row")
        if self.player_id != canonical_source_uuid(SourceRecordKind.PLAYER, self.player_source_id):
            raise ValueError("player_id must use the exact non-zero source UUIDv5 rule")
        return self


class SilverMatch(WyscoutProductRow):
    match_schema_version: Literal["w04-wyscout-silver-match-v1"] = "w04-wyscout-silver-match-v1"
    match_source_id: StrictPositiveInt
    match_id: StrictUuid
    competition_id: StrictUuid
    season_id: StrictUuid
    season_source_id: StrictNonNegativeInt
    match_start_utc: UtcInstant
    team_ids: Annotated[tuple[StrictUuid, StrictUuid], Field(min_length=2, max_length=2)]
    source_partition: CountryPartition

    @model_validator(mode="after")
    def match_identity_and_teams_are_exact(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.MATCH
        ):
            raise ValueError("match must select exactly its physical match row")
        if self.source_partition is not self.source_rows[0].country_partition:
            raise ValueError("match country partition must derive from its selected source row")
        if self.match_id != canonical_source_uuid(SourceRecordKind.MATCH, self.match_source_id):
            raise ValueError("match_id must use the exact source UUIDv5 rule")
        if len(set(self.team_ids)) != 2:
            raise ValueError("Silver match requires exactly two distinct teams")
        if self.team_ids != tuple(sorted(self.team_ids, key=lambda value: value.bytes)):
            raise ValueError("Silver match team_ids must be canonically ordered")
        return self


class ActionPosition(ContractModel):
    x: StrictDecimal
    y: StrictDecimal
    within_accepted_bounds: bool

    @model_validator(mode="after")
    def bound_flag_preserves_anomalies_without_clamping(self) -> Self:
        _validate_decimal128_22_18(self.x, max(0, -cast(int, self.x.as_tuple().exponent)))
        _validate_decimal128_22_18(self.y, max(0, -cast(int, self.y.as_tuple().exponent)))
        expected = Decimal(0) <= self.x <= Decimal(100) and Decimal(0) <= self.y <= Decimal(100)
        if self.within_accepted_bounds is not expected:
            raise ValueError("coordinate bound flag must reflect exact preserved axes")
        return self


class PossessionEligibilityState(StrEnum):
    ELIGIBLE_RESOLVED = "ELIGIBLE_RESOLVED"
    INELIGIBLE_UNMAPPED = "INELIGIBLE_UNMAPPED"


class PossessionPredicateState(StrEnum):
    PREDICATE_ADMITTED = "PREDICATE_ADMITTED"
    PREDICATE_UNMAPPED = "PREDICATE_UNMAPPED"


class PossessionPredicateDecision(StrEnum):
    CONTESTED = "CONTESTED"
    CONTROL = "CONTROL"
    DEAD_BALL_PRECEDING = "DEAD_BALL_PRECEDING"
    DEAD_BALL_UNASSIGNED = "DEAD_BALL_UNASSIGNED"
    NON_CONTROL_ADMIN = "NON_CONTROL_ADMIN"
    RESTART = "RESTART"
    UNMAPPED = "UNMAPPED"


_CONTESTED_PAIRS = frozenset({(1, 10), (1, 11), (1, 12), (1, 13)})
_DEAD_BALL_PRECEDING_PAIRS = frozenset({(2, 20), (2, 21), (2, 22), (2, 27), (5, 50), (6, 60)})
_DEAD_BALL_UNASSIGNED_PAIRS = frozenset({(2, 23), (5, 51)})
_NON_CONTROL_ADMIN_PAIRS = frozenset({(2, 24), (2, 26)})
_EXPLICIT_UNMAPPED_PAIRS = frozenset({(2, 25), (4, 40), (9, 90), (9, 91)})
_RESTART_PAIRS = frozenset({(3, value) for value in range(30, 37)})
_CONTROL_PAIRS = frozenset(
    {(7, 70), (7, 71), (7, 72), (10, 100)} | {(8, value) for value in range(80, 87)}
)


def _possession_predicate_decision(
    event_id: int | None,
    subevent_id: int | None,
    team_id: UUID | None,
    tag_ids: tuple[int, ...],
) -> PossessionPredicateDecision:
    pair = (event_id, subevent_id)
    if (
        tag_ids != tuple(sorted(set(tag_ids)))
        or pair not in _ADMITTED_EVENT_SUBEVENT_PAIRS
        or (pair in _RESTART_PAIRS | _CONTROL_PAIRS and team_id is None)
    ):
        return PossessionPredicateDecision.UNMAPPED
    if pair in _EXPLICIT_UNMAPPED_PAIRS:
        return PossessionPredicateDecision.UNMAPPED
    if pair in _CONTESTED_PAIRS:
        return PossessionPredicateDecision.CONTESTED
    if pair in _DEAD_BALL_PRECEDING_PAIRS:
        return PossessionPredicateDecision.DEAD_BALL_PRECEDING
    if pair in _DEAD_BALL_UNASSIGNED_PAIRS:
        return PossessionPredicateDecision.DEAD_BALL_UNASSIGNED
    if pair in _NON_CONTROL_ADMIN_PAIRS:
        return PossessionPredicateDecision.NON_CONTROL_ADMIN
    if pair in _RESTART_PAIRS:
        return (
            PossessionPredicateDecision.RESTART
            if team_id is not None
            else PossessionPredicateDecision.UNMAPPED
        )
    if pair in _CONTROL_PAIRS:
        return (
            PossessionPredicateDecision.CONTROL
            if team_id is not None
            else PossessionPredicateDecision.UNMAPPED
        )
    raise AssertionError("accepted possession pair is missing its frozen decision")


def _possession_predicate_state(
    event_id: int | None,
    subevent_id: int | None,
    team_id: UUID | None,
    tag_ids: tuple[int, ...],
) -> PossessionPredicateState:
    pair = (event_id, subevent_id)
    if (
        tag_ids != tuple(sorted(set(tag_ids)))
        or pair not in _ADMITTED_EVENT_SUBEVENT_PAIRS
        or (pair in _RESTART_PAIRS | _CONTROL_PAIRS and team_id is None)
    ):
        return PossessionPredicateState.PREDICATE_UNMAPPED
    return PossessionPredicateState.PREDICATE_ADMITTED


class PossessionSequenceAction(ContractModel):
    """Exact canonical fields needed to resolve one same-period action."""

    action_id: StrictUuid
    source_event_record_id: StrictPositiveInt
    source_row: WyscoutSourceRowReference
    match_id: StrictUuid
    player_id: StrictUuid | None
    team_id: StrictUuid | None
    action_event_taxonomy_id: StrictNonNegativeInt | None
    action_subevent_taxonomy_id: StrictNonNegativeInt | None
    action_period_code: str = Field(strict=True, min_length=1, max_length=16)
    period_rank: StrictNonNegativeInt
    period_elapsed_seconds: StrictDecimal
    source_record_ordinal: StrictNonNegativeInt
    action_tag_ids: tuple[StrictNonNegativeInt, ...]

    @model_validator(mode="after")
    def sequence_action_is_exact(self) -> Self:
        if self.source_row.record_kind is not SourceRecordKind.ACTION:
            raise ValueError("possession sequence entries require exact action source rows")
        if self.source_record_ordinal != self.source_row.source_record_ordinal:
            raise ValueError("sequence ordinal must derive from its physical action row")
        if self.action_id != canonical_source_uuid(
            SourceRecordKind.ACTION, self.source_event_record_id
        ):
            raise ValueError("sequence action identity must derive from the source event ID")
        if not self.period_elapsed_seconds.is_finite() or self.period_elapsed_seconds < 0:
            raise ValueError("sequence time must be finite non-negative period-relative evidence")
        if self.action_tag_ids != tuple(sorted(set(self.action_tag_ids))):
            raise ValueError("sequence tag IDs must be sorted unique strict integers")
        return self

    @property
    def action_order_key(self) -> tuple[int, Decimal, int, int]:
        return (
            self.period_rank,
            self.period_elapsed_seconds,
            self.source_record_ordinal,
            self.source_event_record_id,
        )


class PossessionPeriodSequence(ContractModel):
    """Complete canonical action evidence for exactly one match period."""

    construction_authority_state: Literal["semantic_only_unchecked"] = "semantic_only_unchecked"
    match_id: StrictUuid
    source_completion_index_sha256: Sha256Digest
    source_completion_membership_sha256: Sha256Digest
    action_period_code: str = Field(strict=True, min_length=1, max_length=16)
    period_action_count: StrictPositiveInt
    actions: Annotated[tuple[PossessionSequenceAction, ...], Field(min_length=1)]
    complete_period_evidence: Literal[True] = True

    @model_validator(mode="after")
    def period_sequence_is_complete_unique_and_ordered(self) -> Self:
        if self.source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256:
            raise ValueError("period sequence must bind the accepted source-completion index")
        if self.period_action_count != len(self.actions):
            raise ValueError("period_action_count must equal the complete sequence cardinality")
        if any(
            action.match_id != self.match_id or action.action_period_code != self.action_period_code
            for action in self.actions
        ):
            raise ValueError("complete sequence cannot cross match or period")
        order = tuple(action.action_order_key for action in self.actions)
        if order != tuple(sorted(order)) or len(order) != len(set(order)):
            raise ValueError("complete period actions must have unique canonical order")
        identities = tuple(action.action_id for action in self.actions)
        if len(identities) != len(set(identities)):
            raise ValueError("complete period actions must have unique action identities")
        physical = tuple(
            (action.source_row.completion_relative_path, action.source_record_ordinal)
            for action in self.actions
        )
        if len(physical) != len(set(physical)):
            raise ValueError("complete period actions must have unique physical rows")
        return self


def _resolved_possession_groups(
    sequence: PossessionPeriodSequence,
) -> tuple[tuple[UUID, tuple[UUID, ...]], ...]:
    groups: list[tuple[UUID, list[UUID]]] = []
    active_index: int | None = None
    active_team: UUID | None = None
    pending_contested: list[UUID] = []
    clock_groups = groupby(
        sequence.actions,
        key=lambda action: (action.period_rank, action.period_elapsed_seconds),
    )
    for _clock, clock_group in clock_groups:
        clock_actions = tuple(clock_group)
        decisions = tuple(
            _possession_predicate_decision(
                action.action_event_taxonomy_id,
                action.action_subevent_taxonomy_id,
                action.team_id,
                action.action_tag_ids,
            )
            for action in clock_actions
        )
        controlling_teams = {
            action.team_id
            for action, decision in zip(clock_actions, decisions, strict=True)
            if decision
            in {PossessionPredicateDecision.CONTROL, PossessionPredicateDecision.RESTART}
        }
        if len(controlling_teams) > 1:
            pending_contested.clear()
            active_index = None
            active_team = None
            continue
        for action, decision in zip(clock_actions, decisions, strict=True):
            if decision is PossessionPredicateDecision.CONTESTED:
                pending_contested.append(action.action_id)
                continue
            if decision in {
                PossessionPredicateDecision.CONTROL,
                PossessionPredicateDecision.RESTART,
            }:
                if action.team_id is None:
                    raise AssertionError("admitted control/restart must have a team")
                if (
                    decision is PossessionPredicateDecision.RESTART
                    or active_index is None
                    or active_team != action.team_id
                ):
                    groups.append((action.team_id, []))
                    active_index = len(groups) - 1
                    active_team = action.team_id
                groups[active_index][1].extend(pending_contested)
                pending_contested.clear()
                groups[active_index][1].append(action.action_id)
                continue
            if decision is PossessionPredicateDecision.DEAD_BALL_PRECEDING:
                if active_index is not None:
                    groups[active_index][1].append(action.action_id)
                active_index = None
                active_team = None
                continue
            if decision is PossessionPredicateDecision.DEAD_BALL_UNASSIGNED:
                active_index = None
                active_team = None
    return tuple((team_id, tuple(action_ids)) for team_id, action_ids in groups if action_ids)


def _accepted_position_feature_evidence(action_positions: tuple[ActionPosition, ...]) -> bool:
    return (
        len(action_positions) in {1, 2}
        and all(position.x.is_finite() and position.y.is_finite() for position in action_positions)
        and all(position.within_accepted_bounds for position in action_positions)
    )


def _validate_decimal128_22_18(value: Decimal, declared_scale: int) -> None:
    if not value.is_finite():
        raise ValueError("decimal128(22,18) values must be finite")
    exponent = cast(int, value.as_tuple().exponent)
    scale = max(0, -exponent)
    coefficient_digits = len(value.as_tuple().digits)
    integer_digits = max(0, coefficient_digits + exponent)
    if scale > 18 or integer_digits > 4 or integer_digits + scale > 22 or declared_scale != scale:
        raise ValueError(
            "value must retain exact finite decimal128(22,18) lexical scale and capacity"
        )


class SilverAction(WyscoutProductRow):
    action_schema_version: Literal["w04-wyscout-silver-action-v1"] = "w04-wyscout-silver-action-v1"
    action_source_id: StrictPositiveInt
    action_id: StrictUuid
    source_event_record_id: StrictPositiveInt
    match_id: StrictUuid
    competition_id: StrictUuid | None
    player_id: StrictUuid | None
    team_id: StrictUuid | None
    action_event_taxonomy_id: StrictNonNegativeInt | None
    action_subevent_taxonomy_id: StrictNonNegativeInt | None
    action_period_code: str = Field(strict=True, min_length=1, max_length=16)
    period_rank: StrictNonNegativeInt
    period_elapsed_seconds: StrictDecimal
    event_sec_source_scale: Annotated[int, Field(strict=True, ge=0, le=18)]
    source_record_ordinal: StrictNonNegativeInt
    action_tag_ids: tuple[StrictNonNegativeInt, ...]
    action_positions: tuple[ActionPosition, ...]
    possession_predicate_state: PossessionPredicateState
    possession_period_sequence: PossessionPeriodSequence
    possession_eligibility_state: PossessionEligibilityState
    occurrence_precision: Literal["period_relative"] = "period_relative"
    occurrence_utc: None = None

    @model_validator(mode="after")
    def action_is_strict_and_orderable(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.ACTION
        ):
            raise ValueError("action must select exactly its physical action row")
        if self.action_id != canonical_source_uuid(SourceRecordKind.ACTION, self.action_source_id):
            raise ValueError("action_id must use the exact source UUIDv5 rule")
        if self.source_event_record_id != self.action_source_id:
            raise ValueError("provider event record ID must equal the action source ID")
        if self.source_record_ordinal != self.source_rows[0].source_record_ordinal:
            raise ValueError("action source ordinal must derive from its selected source row")
        if not self.period_elapsed_seconds.is_finite():
            raise ValueError("period-relative action seconds must be finite")
        if self.period_elapsed_seconds < 0:
            raise ValueError("period-relative action seconds cannot be negative")
        _validate_decimal128_22_18(
            self.period_elapsed_seconds,
            self.event_sec_source_scale,
        )
        if self.action_tag_ids != tuple(sorted(set(self.action_tag_ids))):
            raise ValueError("action_tag_ids must be sorted unique strict integers")
        if self.action_subevent_taxonomy_id is not None and self.action_event_taxonomy_id is None:
            raise ValueError("canonical subevent requires a canonical event taxonomy ID")
        if (
            self.action_subevent_taxonomy_id is not None
            and (
                self.action_event_taxonomy_id,
                self.action_subevent_taxonomy_id,
            )
            not in _ADMITTED_EVENT_SUBEVENT_PAIRS
        ):
            raise ValueError("canonical action subevent requires an admitted strict integer pair")
        expected_predicate_state = _possession_predicate_state(
            self.action_event_taxonomy_id,
            self.action_subevent_taxonomy_id,
            self.team_id,
            self.action_tag_ids,
        )
        if self.possession_predicate_state is not expected_predicate_state:
            raise ValueError("predicate admission must derive from exact possession-v2 inputs")
        sequence = self.possession_period_sequence
        if (
            sequence.match_id != self.match_id
            or sequence.action_period_code != self.action_period_code
        ):
            raise ValueError("possession sequence must equal the action match/period scope")
        if any(entry.source_row not in self.lineage.source_rows for entry in sequence.actions):
            raise ValueError("complete possession sequence rows must occur exactly in lineage")
        own_entries = tuple(
            entry for entry in sequence.actions if entry.action_id == self.action_id
        )
        if len(own_entries) != 1:
            raise ValueError("complete possession sequence must contain the action exactly once")
        own = own_entries[0]
        if (
            own.source_event_record_id != self.source_event_record_id
            or own.source_row != self.source_rows[0]
            or own.match_id != self.match_id
            or own.player_id != self.player_id
            or own.team_id != self.team_id
            or own.action_event_taxonomy_id != self.action_event_taxonomy_id
            or own.action_subevent_taxonomy_id != self.action_subevent_taxonomy_id
            or own.action_period_code != self.action_period_code
            or own.period_rank != self.period_rank
            or own.period_elapsed_seconds != self.period_elapsed_seconds
            or own.source_record_ordinal != self.source_record_ordinal
            or own.action_tag_ids != self.action_tag_ids
        ):
            raise ValueError("action fields must equal its exact complete-sequence entry")
        resolved_action_ids = {
            action_id
            for _, action_ids in _resolved_possession_groups(sequence)
            for action_id in action_ids
        }
        expected_eligibility = (
            PossessionEligibilityState.ELIGIBLE_RESOLVED
            if self.action_id in resolved_action_ids
            else PossessionEligibilityState.INELIGIBLE_UNMAPPED
        )
        if self.possession_eligibility_state is not expected_eligibility:
            raise ValueError(
                "possession eligibility must derive from the complete same-period sequence"
            )
        return self

    @property
    def action_order_key(self) -> tuple[int, Decimal, int, int]:
        return (
            self.period_rank,
            self.period_elapsed_seconds,
            self.source_record_ordinal,
            self.source_event_record_id,
        )


class NominalMinuteInterval(ContractModel):
    lower: StrictNonNegativeInt
    upper: StrictPositiveInt

    @model_validator(mode="after")
    def interval_is_one_nominal_minute(self) -> Self:
        if self.upper != self.lower + 1:
            raise ValueError("substitution nominal minute interval must be [m,m+1)")
        return self


class SilverLineupStint(WyscoutProductRow):
    lineup_stint_schema_version: Literal["w04-wyscout-silver-lineup-stint-v1"] = (
        "w04-wyscout-silver-lineup-stint-v1"
    )
    lineup_stint_id: StrictUuid
    match_id: StrictUuid
    player_id: StrictUuid
    team_id: StrictUuid
    start_interval: NominalMinuteInterval | None
    end_interval: NominalMinuteInterval | None
    lower_bound_minutes: StrictNonNegativeInt | None
    upper_bound_minutes: StrictNonNegativeInt | None
    right_censored: bool
    elapsed_minutes: None = None
    per90_eligible: Literal[False] = False
    suppression_reason: Literal["suppressed_unsupported_denominator"] = (
        "suppressed_unsupported_denominator"
    )

    @model_validator(mode="after")
    def stint_bounds_are_interval_derived(self) -> Self:
        if (
            len(self.source_rows) != 1
            or self.source_rows[0].record_kind is not SourceRecordKind.MATCH
        ):
            raise ValueError("lineup stint must select exactly its physical match row")
        if self.start_interval is None or self.end_interval is None:
            if not self.right_censored or any(
                value is not None for value in (self.lower_bound_minutes, self.upper_bound_minutes)
            ):
                raise ValueError("open lineup stints must remain right-censored without minutes")
            return self
        lower = max(0, self.end_interval.lower - self.start_interval.upper)
        upper = max(0, self.end_interval.upper - self.start_interval.lower)
        if (self.lower_bound_minutes, self.upper_bound_minutes) != (lower, upper):
            raise ValueError("lineup bounds must use the exact nominal interval equation")
        if self.right_censored:
            raise ValueError("bounded lineup stints cannot be right-censored")
        return self


class SilverPossession(WyscoutProductRow):
    possession_schema_version: Literal["w04-wyscout-silver-possession-v1"] = (
        "w04-wyscout-silver-possession-v1"
    )
    possession_id: StrictUuid
    match_id: StrictUuid
    action_period_code: str = Field(strict=True, min_length=1, max_length=16)
    team_id: StrictUuid
    contributing_actions: Annotated[tuple[SilverAction, ...], Field(min_length=1)]
    action_ids: Annotated[tuple[StrictUuid, ...], Field(min_length=1)]
    first_action_order: tuple[
        StrictNonNegativeInt,
        StrictDecimal,
        StrictNonNegativeInt,
        StrictNonNegativeInt,
    ]
    last_action_order: tuple[
        StrictNonNegativeInt,
        StrictDecimal,
        StrictNonNegativeInt,
        StrictNonNegativeInt,
    ]
    project_taxonomy_state: Literal["project_defined_resolved"] = "project_defined_resolved"
    provider_native_claim: Literal[False] = False

    @model_validator(mode="after")
    def possession_is_one_ordered_same_period_sequence(self) -> Self:
        actions = self.contributing_actions
        expected_actions = tuple(
            sorted(actions, key=lambda action: (action.action_order_key, action.action_id.bytes))
        )
        if actions != expected_actions or len({action.action_id for action in actions}) != len(
            actions
        ):
            raise ValueError("possession actions must be unique and canonically ordered")
        sequence = actions[0].possession_period_sequence
        if any(action.possession_period_sequence != sequence for action in actions):
            raise ValueError("possession actions must bind one identical complete period sequence")
        matching_groups = tuple(
            action_ids
            for team_id, action_ids in _resolved_possession_groups(sequence)
            if team_id == self.team_id
            and action_ids == tuple(action.action_id for action in actions)
        )
        if len(matching_groups) != 1:
            raise ValueError("possession actions must equal one complete resolved sequence group")
        for action in actions:
            if (
                action.build_id != self.build_id
                or action.tenant_context != self.tenant_context
                or action.lineage != self.lineage
                or action.match_id != self.match_id
                or action.action_period_code != self.action_period_code
                or action.possession_eligibility_state
                is not PossessionEligibilityState.ELIGIBLE_RESOLVED
            ):
                raise ValueError("possession action identity/authority/scope is inconsistent")
            decision = _possession_predicate_decision(
                action.action_event_taxonomy_id,
                action.action_subevent_taxonomy_id,
                action.team_id,
                action.action_tag_ids,
            )
            if (
                decision
                in {
                    PossessionPredicateDecision.CONTROL,
                    PossessionPredicateDecision.RESTART,
                }
                and action.team_id != self.team_id
            ):
                raise ValueError("possession control action team must match possession team")
        expected_source_rows = tuple(
            sorted(
                {entry.source_row for entry in sequence.actions},
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        )
        if self.source_rows != expected_source_rows:
            raise ValueError("possession source rows must cover its complete causal sequence")
        expected_ids = tuple(action.action_id for action in actions)
        if self.action_ids != expected_ids:
            raise ValueError("possession action IDs must derive exactly from contributing actions")
        if (
            self.first_action_order != actions[0].action_order_key
            or self.last_action_order != actions[-1].action_order_key
        ):
            raise ValueError(
                "possession action bounds must derive exactly from contributing actions"
            )
        return self


class GoldCoverageDimensionName(StrEnum):
    IDENTITY = "identity"
    LINEUP = "lineup"
    ACTION = "action"
    COORDINATE = "coordinate"
    POSSESSION = "possession"
    TEMPORAL = "temporal"


class GoldCoverageState(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    NOT_APPLICABLE_ZERO_DENOMINATOR = "not_applicable_zero_denominator"
    MISSING_ZERO_DENOMINATOR = "missing_zero_denominator"
    AUTHORITY_MISSING = "authority_missing"
    FAILED = "failed"


class GoldCoverageDimension(ContractModel):
    name: GoldCoverageDimensionName
    numerator: StrictNonNegativeInt
    denominator: StrictNonNegativeInt
    coverage: StrictDecimal
    state: GoldCoverageState
    reason_codes: tuple[ReasonCode, ...] = ()
    zero_denominator_authority: WyscoutAuthorityReference | None = None

    @model_validator(mode="after")
    def coverage_is_exact(self) -> Self:
        if self.numerator > self.denominator:
            raise ValueError("coverage numerator cannot exceed denominator")
        if self.reason_codes != tuple(sorted(set(self.reason_codes))):
            raise ValueError("coverage reason_codes must be sorted unique")
        if self.state in {GoldCoverageState.AUTHORITY_MISSING, GoldCoverageState.FAILED}:
            if self.numerator != 0 or self.coverage != 0:
                raise ValueError("failed coverage states must fail closed at zero")
            if not self.reason_codes:
                raise ValueError("failed coverage states require explicit reasons")
            if self.zero_denominator_authority is not None:
                raise ValueError("failed coverage states cannot carry an accepted zero proof")
            return self
        if self.denominator > 0:
            if self.zero_denominator_authority is not None:
                raise ValueError("positive denominators forbid zero-denominator authority proof")
            with localcontext() as context:
                context.prec = 38
                expected = Decimal(self.numerator) / Decimal(self.denominator)
            if self.coverage != expected:
                raise ValueError("coverage must be the exact Decimal N/D")
            expected_state = (
                GoldCoverageState.COMPLETE
                if self.numerator == self.denominator
                else GoldCoverageState.PARTIAL
            )
            if self.state is not expected_state:
                raise ValueError("positive-denominator coverage state is inconsistent")
            if self.state is GoldCoverageState.COMPLETE and self.reason_codes:
                raise ValueError("complete coverage cannot carry failure reasons")
            if self.state is GoldCoverageState.PARTIAL and not self.reason_codes:
                raise ValueError("partial coverage requires explicit reasons")
        elif self.name in {
            GoldCoverageDimensionName.COORDINATE,
            GoldCoverageDimensionName.POSSESSION,
        }:
            if self.state is GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR:
                if self.numerator != 0 or self.coverage != 1:
                    raise ValueError("authority-proven optional zero denominator has coverage one")
                if not self.reason_codes:
                    raise ValueError("not-applicable coverage requires an explicit reason")
                expected_authority = (
                    AuthorityKind.FIELD
                    if self.name is GoldCoverageDimensionName.COORDINATE
                    else AuthorityKind.POSSESSION
                )
                if (
                    self.zero_denominator_authority is None
                    or self.zero_denominator_authority.authority_kind is not expected_authority
                ):
                    raise ValueError(
                        "optional zero denominator requires its exact accepted authority"
                    )
            elif self.state is GoldCoverageState.MISSING_ZERO_DENOMINATOR:
                if self.numerator != 0 or self.coverage != 0 or not self.reason_codes:
                    raise ValueError("unproven optional zero denominator must fail closed")
                if self.zero_denominator_authority is not None:
                    raise ValueError("unproven optional zero denominator forbids authority proof")
            else:
                raise ValueError("optional zero denominator has an invalid coverage state")
        else:
            if self.numerator != 0 or self.coverage != 0:
                raise ValueError("mandatory zero denominator has coverage zero")
            if self.state is not GoldCoverageState.MISSING_ZERO_DENOMINATOR:
                raise ValueError("mandatory zero denominator requires missing state")
            if self.zero_denominator_authority is not None:
                raise ValueError("mandatory zero denominator forbids optional authority proof")
            if not self.reason_codes:
                raise ValueError("missing mandatory coverage requires explicit reasons")
        return self


_MISSING_COVERAGE_STATES = {
    GoldCoverageState.PARTIAL,
    GoldCoverageState.MISSING_ZERO_DENOMINATOR,
    GoldCoverageState.AUTHORITY_MISSING,
    GoldCoverageState.FAILED,
}


class GoldCoverage(ContractModel):
    dimensions: Annotated[tuple[GoldCoverageDimension, ...], Field(min_length=6, max_length=6)]
    coverage_overall: StrictDecimal
    missing_dimensions: tuple[GoldCoverageDimensionName, ...]

    @model_validator(mode="after")
    def six_dimensions_are_exact(self) -> Self:
        if tuple(dimension.name for dimension in self.dimensions) != tuple(
            GoldCoverageDimensionName
        ):
            raise ValueError("Gold coverage dimensions must have exact fixed order")
        expected_missing = tuple(
            sorted(
                (
                    dimension.name
                    for dimension in self.dimensions
                    if dimension.state in _MISSING_COVERAGE_STATES
                ),
                key=lambda name: name.value,
            )
        )
        if self.missing_dimensions != expected_missing:
            raise ValueError("missing_dimensions must be the exact lexical missing set")
        if self.coverage_overall != min(dimension.coverage for dimension in self.dimensions):
            raise ValueError("coverage_overall must be the exact dimension minimum")
        return self


class W04Applicability(StrEnum):
    SUPPRESSED = "suppressed"
    RESEARCH_ONLY = "research_only"
    W04_DATA_READY = "w04_data_ready"


class W04ApplicabilityAssessment(ContractModel):
    state: W04Applicability
    reason_codes: tuple[ReasonCode, ...]

    @model_validator(mode="after")
    def reasons_are_sorted_unique(self) -> Self:
        if self.reason_codes != tuple(sorted(set(self.reason_codes))):
            raise ValueError("applicability reason_codes must be sorted unique")
        if self.state is not W04Applicability.W04_DATA_READY and not self.reason_codes:
            raise ValueError("non-ready applicability must state a reason")
        if self.state is W04Applicability.W04_DATA_READY and self.reason_codes:
            raise ValueError("data-ready applicability cannot carry failure reasons")
        return self


_MANDATORY_COVERAGE_DIMENSIONS = {
    GoldCoverageDimensionName.IDENTITY,
    GoldCoverageDimensionName.LINEUP,
    GoldCoverageDimensionName.ACTION,
    GoldCoverageDimensionName.TEMPORAL,
}


def _expected_applicability_state(
    coverage: GoldCoverage,
    *,
    uncertain: bool,
) -> W04Applicability:
    hard_failure = any(
        dimension.state in {GoldCoverageState.AUTHORITY_MISSING, GoldCoverageState.FAILED}
        or (
            dimension.name in _MANDATORY_COVERAGE_DIMENSIONS
            and dimension.state is GoldCoverageState.MISSING_ZERO_DENOMINATOR
        )
        for dimension in coverage.dimensions
    )
    if hard_failure:
        return W04Applicability.SUPPRESSED
    if uncertain or coverage.missing_dimensions:
        return W04Applicability.RESEARCH_ONLY
    return W04Applicability.W04_DATA_READY


_UNCERTAINTY_REASON: ReasonCode = "RIGHT_CENSORED_OR_UNCERTAIN"


def _expected_applicability_assessment(
    coverage: GoldCoverage,
    *,
    uncertain: bool,
) -> W04ApplicabilityAssessment:
    state = _expected_applicability_state(coverage, uncertain=uncertain)
    reasons = {
        reason
        for dimension in coverage.dimensions
        if dimension.state in _MISSING_COVERAGE_STATES
        for reason in dimension.reason_codes
    }
    if uncertain:
        reasons.add(_UNCERTAINTY_REASON)
    return W04ApplicabilityAssessment(
        state=state,
        reason_codes=tuple(sorted(reasons)) if state is not W04Applicability.W04_DATA_READY else (),
    )


_DEPENDENCY_NAMESPACE = uuid5(
    NAMESPACE_URL,
    "urn:scouting-intelligence:w04:wyscout:evidence-dependency:v1",
)


def identity_dependency_id(identity_bundle_sha256: str) -> UUID:
    """Derive the exact content-addressed R20 identity-bundle dependency ID."""

    if re.fullmatch(r"[0-9a-f]{64}", identity_bundle_sha256) is None:
        raise ValueError("identity bundle digest must be canonical SHA-256")
    return uuid5(_DEPENDENCY_NAMESPACE, "identity_bundle:" + identity_bundle_sha256)


def feature_dependency_id(
    artifact_type: Literal["field_registry", "possession_taxonomy", "supported_feature_registry"],
    artifact_id: str,
    artifact_digest: str,
    acceptance_digest: str,
) -> UUID:
    return uuid5(
        _DEPENDENCY_NAMESPACE,
        f"feature_schema:{artifact_type}:{artifact_id}:{artifact_digest}:{acceptance_digest}",
    )


FIELD_DEPENDENCY_ID = feature_dependency_id(
    "field_registry",
    "w04-wyscout-field-registry-v2",
    FIELD_CANDIDATE_SHA256,
    FIELD_ACCEPTANCE_SHA256,
)
POSSESSION_DEPENDENCY_ID = feature_dependency_id(
    "possession_taxonomy",
    "w04-wyscout-possession-taxonomy-v2",
    POSSESSION_CANDIDATE_SHA256,
    POSSESSION_ACCEPTANCE_SHA256,
)
FEATURE_DEPENDENCY_ID = feature_dependency_id(
    "supported_feature_registry",
    "w04-wyscout-supported-count-features-v1",
    FEATURE_SCHEMA_HASH,
    FEATURE_ACCEPTANCE_SHA256,
)

_DEPENDENCY_KIND_RANK = {kind: rank for rank, kind in enumerate(DependencyKind)}


def dependency_sort_key(
    dependency: EvidenceDependency,
) -> tuple[int, bytes, str, datetime, datetime]:
    return (
        _DEPENDENCY_KIND_RANK[dependency.kind],
        dependency.dependency_id.bytes,
        dependency.digest,
        dependency.observed_at,
        dependency.available_at,
    )


def dependency_lineage_hash(
    dependencies: tuple[EvidenceDependency, ...],
    *,
    source_completion_index_sha256: str = SOURCE_COMPLETION_INDEX_SHA256,
) -> str:
    rows = [dependency.model_dump(mode="json") for dependency in dependencies]
    payload = json.dumps(
        {
            "dependencies": rows,
            "source_completion_index_sha256": source_completion_index_sha256,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return hashlib.sha256(payload).hexdigest()


def _validate_exact_dependency_lineage(lineage: DependencyLineage) -> None:
    dependencies = lineage.dependencies
    if len(dependencies) != 5:
        raise ValueError("W04 dependency lineage requires exactly five rows")
    if dependencies != tuple(sorted(dependencies, key=dependency_sort_key)):
        raise ValueError("W04 dependencies must be in exact canonical order")
    if dependency_lineage_hash(dependencies) != lineage.lineage_hash:
        raise ValueError("dependency lineage hash must be recomputed from all ordered rows")
    by_kind = {kind: [row for row in dependencies if row.kind is kind] for kind in DependencyKind}
    if (
        len(by_kind[DependencyKind.SOURCE_MANIFEST]) != 1
        or len(by_kind[DependencyKind.IDENTITY_EVIDENCE]) != 1
        or len(by_kind[DependencyKind.FEATURE_SCHEMA]) != 3
        or by_kind[DependencyKind.MODEL_ARTIFACT]
        or by_kind[DependencyKind.RETRIEVAL_INDEX]
    ):
        raise ValueError("dependencies must be source, identity, and three feature schemas")
    source = by_kind[DependencyKind.SOURCE_MANIFEST][0]
    if (
        source.dependency_id != SOURCE_MANIFEST_ID
        or source.digest != SOURCE_MANIFEST_SHA256
        or source.observed_at != SOURCE_RELEASE
        or source.available_at != SOURCE_RELEASE
    ):
        raise ValueError("source dependency differs from the immutable manifest")
    identity = by_kind[DependencyKind.IDENTITY_EVIDENCE][0]
    identity_clocks = _AUTHORITY_CLOCK_ROWS[AuthorityKind.IDENTITY]
    if (
        identity.dependency_id != identity_dependency_id(identity.digest)
        or identity.observed_at != identity_clocks[0]
        or identity.available_at != identity_clocks[2]
    ):
        raise ValueError("identity dependency clocks differ from accepted authority")
    expected_features = {
        FIELD_DEPENDENCY_ID: (
            FIELD_CANDIDATE_SHA256,
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.FIELD][0],
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.FIELD][2],
        ),
        POSSESSION_DEPENDENCY_ID: (
            POSSESSION_CANDIDATE_SHA256,
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.POSSESSION][0],
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.POSSESSION][2],
        ),
        FEATURE_DEPENDENCY_ID: (
            FEATURE_SCHEMA_HASH,
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.SUPPORTED_FEATURE][0],
            _AUTHORITY_CLOCK_ROWS[AuthorityKind.SUPPORTED_FEATURE][2],
        ),
    }
    actual_features = {
        dependency.dependency_id: (
            dependency.digest,
            dependency.observed_at,
            dependency.available_at,
        )
        for dependency in by_kind[DependencyKind.FEATURE_SCHEMA]
    }
    if actual_features != expected_features:
        raise ValueError("feature dependencies differ from accepted v2/v2/v1 authority")


class W04SemanticTemporalProof(ContractModel):
    """Clock-free semantic proof: no generation, run, host, or output time exists."""

    semantic_proof_schema_version: Literal["w04-wyscout-semantic-temporal-proof-v1"] = (
        "w04-wyscout-semantic-temporal-proof-v1"
    )
    snapshot_as_of_ts: UtcInstant
    available_at_watermark: UtcInstant
    valid_from_ts: UtcInstant
    feature_cutoff_ts: UtcInstant
    source_manifest_ids: Annotated[tuple[StrictUuid, ...], Field(min_length=1, max_length=1)]
    source_completion_index_sha256: Sha256Digest
    feature_schema_hash: Sha256Digest
    dependency_lineage_hash: Sha256Digest
    dependency_lineage: DependencyLineage
    source_authority: WyscoutSourceAuthority
    authority_clocks: Annotated[
        tuple[WyscoutAuthorityClock, ...], Field(min_length=4, max_length=4)
    ]
    occurrence_precision: Literal["period_relative"] = "period_relative"
    partial_match_claim_supported: Literal[False] = False

    @model_validator(mode="after")
    def proof_has_exact_five_strict_dependencies(self) -> Self:
        dependencies = self.dependency_lineage.dependencies
        if self.source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256:
            raise ValueError("temporal proof must bind the accepted source-completion index")
        _validate_exact_dependency_lineage(self.dependency_lineage)
        identities = tuple(
            (dependency.kind, dependency.dependency_id) for dependency in dependencies
        )
        if len(identities) != len(set(identities)):
            raise ValueError("duplicate dependency kind/ID is forbidden")
        if (
            [dependency.kind for dependency in dependencies].count(DependencyKind.SOURCE_MANIFEST)
            != 1
            or [dependency.kind for dependency in dependencies].count(
                DependencyKind.IDENTITY_EVIDENCE
            )
            != 1
            or [dependency.kind for dependency in dependencies].count(DependencyKind.FEATURE_SCHEMA)
            != 3
        ):
            raise ValueError("dependencies must be source, identity, and three feature schemas")
        if self.source_authority != accepted_source_authority():
            raise ValueError("temporal proof source authority must be exact")
        if self.authority_clocks != accepted_authority_clocks():
            raise ValueError("temporal proof authority clocks must be exact")
        if any(
            dependency.observed_at >= self.feature_cutoff_ts
            or dependency.available_at >= self.feature_cutoff_ts
            for dependency in dependencies
        ):
            raise ValueError("every dependency clock must be strictly before cutoff")
        if self.source_authority.acquired_at >= self.feature_cutoff_ts or any(
            clock >= self.feature_cutoff_ts
            for row in self.authority_clocks
            for clock in (row.decided_at, row.reviewed_at, row.accepted_at)
        ):
            raise ValueError("every source and authority clock must be strictly before cutoff")
        watermark = max(dependency.available_at for dependency in dependencies)
        if self.available_at_watermark != watermark or watermark >= self.feature_cutoff_ts:
            raise ValueError("watermark must be the strict pre-cutoff availability maximum")
        if self.valid_from_ts != max(self.snapshot_as_of_ts, watermark):
            raise ValueError("valid_from_ts must equal max(snapshot, availability watermark)")
        if self.snapshot_as_of_ts >= self.feature_cutoff_ts:
            raise ValueError("snapshot must be strictly before cutoff")
        digest = dependency_lineage_hash(
            dependencies,
            source_completion_index_sha256=self.source_completion_index_sha256,
        )
        if self.dependency_lineage.lineage_hash != digest or self.dependency_lineage_hash != digest:
            raise ValueError("dependency lineage hash must cover all five ordered rows")
        if self.source_manifest_ids != (SOURCE_MANIFEST_ID,):
            raise ValueError("source_manifest_ids must contain the exact accepted manifest")
        if self.feature_schema_hash != FEATURE_SCHEMA_HASH:
            raise ValueError("feature_schema_hash must equal the accepted feature candidate")
        return self


class SilverPlayerMatchFact(WyscoutProductRow):
    player_match_fact_schema_version: Literal["w04-wyscout-player-match-fact-v1"] = (
        "w04-wyscout-player-match-fact-v1"
    )
    source_manifest_id: StrictUuid
    match_id: StrictUuid
    player_id: StrictUuid
    competition_id: StrictUuid
    season_id: StrictUuid
    match_start_utc: UtcInstant
    match_team_id: StrictUuid | None
    lineup_evidence_present: bool
    contributing_lineup_stints: tuple[SilverLineupStint, ...]
    contributing_actions: tuple[SilverAction, ...]
    contributing_possessions: tuple[SilverPossession, ...]
    action_count: StrictNonNegativeInt
    coordinate_known_action_count: StrictNonNegativeInt
    resolved_possession_action_count: StrictNonNegativeInt
    right_censored_or_uncertain: bool
    elapsed_minutes: None = None
    per90_eligible: Literal[False] = False
    coverage: GoldCoverage
    applicability: W04ApplicabilityAssessment
    temporal_proof: W04SemanticTemporalProof

    @model_validator(mode="after")
    def player_match_key_and_state_are_exact(self) -> Self:
        if self.source_manifest_id != SOURCE_MANIFEST_ID:
            raise ValueError("player-match key must use the accepted source manifest")
        lineups = self.contributing_lineup_stints
        if lineups != tuple(sorted(lineups, key=lambda row: row.lineup_stint_id.bytes)) or len(
            {row.lineup_stint_id for row in lineups}
        ) != len(lineups):
            raise ValueError("fact lineup stints must be unique and canonically ordered")
        for lineup in lineups:
            if (
                lineup.build_id != self.build_id
                or lineup.tenant_context != self.tenant_context
                or lineup.lineage != self.lineage
                or lineup.match_id != self.match_id
                or lineup.player_id != self.player_id
                or self.match_team_id is None
                or lineup.team_id != self.match_team_id
            ):
                raise ValueError("contributing lineup leaks across fact identity or authority")
        if self.lineup_evidence_present is not bool(lineups):
            raise ValueError("lineup_evidence_present must derive from selected lineup stints")
        actions = self.contributing_actions
        if actions != tuple(
            sorted(actions, key=lambda action: (action.action_order_key, action.action_id.bytes))
        ) or len({action.action_id for action in actions}) != len(actions):
            raise ValueError("fact actions must be unique and canonically ordered")
        for action in actions:
            if (
                action.build_id != self.build_id
                or action.tenant_context != self.tenant_context
                or action.lineage != self.lineage
                or action.match_id != self.match_id
                or action.player_id != self.player_id
                or action.competition_id != self.competition_id
                or self.match_team_id is None
                or action.team_id != self.match_team_id
            ):
                raise ValueError("contributing action leaks across fact identity or authority")
        if not actions and not lineups:
            raise ValueError("player-match candidates require lineup or non-zero action evidence")
        sequences: dict[tuple[UUID, str], PossessionPeriodSequence] = {}
        for action in actions:
            key = (action.match_id, action.action_period_code)
            existing = sequences.setdefault(key, action.possession_period_sequence)
            if existing != action.possession_period_sequence:
                raise ValueError("fact actions in one period must share complete sequence evidence")
        expected_player_action_ids = {
            entry.action_id
            for sequence in sequences.values()
            for entry in sequence.actions
            if entry.player_id == self.player_id
        }
        if {action.action_id for action in actions} != expected_player_action_ids:
            raise ValueError("fact actions must completely cover row-player period evidence")
        possessions = self.contributing_possessions
        if possessions != tuple(
            sorted(possessions, key=lambda row: row.possession_id.bytes)
        ) or len({row.possession_id for row in possessions}) != len(possessions):
            raise ValueError("fact possessions must be unique and canonically ordered")
        action_ids = {action.action_id for action in actions}
        actions_by_id = {action.action_id: action for action in actions}
        membership: dict[UUID, int] = {action_id: 0 for action_id in action_ids}
        for possession in possessions:
            if (
                possession.build_id != self.build_id
                or possession.tenant_context != self.tenant_context
                or possession.lineage != self.lineage
                or possession.match_id != self.match_id
                or not any(action_id in action_ids for action_id in possession.action_ids)
            ):
                raise ValueError("contributing possession leaks across fact identity or actions")
            if any(
                action.action_id in actions_by_id and actions_by_id[action.action_id] != action
                for action in possession.contributing_actions
            ):
                raise ValueError("possession action evidence must equal the selected fact action")
            for action_id in possession.action_ids:
                if action_id in membership:
                    membership[action_id] += 1
        for action in actions:
            expected_membership = (
                1
                if action.possession_eligibility_state
                is PossessionEligibilityState.ELIGIBLE_RESOLVED
                else 0
            )
            if membership[action.action_id] != expected_membership:
                raise ValueError("resolved possession state requires exact single membership")
        causal_action_rows = {
            entry.source_row for sequence in sequences.values() for entry in sequence.actions
        }
        expected_source_rows = tuple(
            sorted(
                {
                    *(row for lineup in lineups for row in lineup.source_rows),
                    *causal_action_rows,
                },
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        )
        if self.source_rows != expected_source_rows:
            raise ValueError("fact source rows must cover all causal contributing evidence")
        expected_counts = (
            len(actions),
            sum(_accepted_position_feature_evidence(action.action_positions) for action in actions),
            sum(membership.values()),
        )
        if (
            self.action_count,
            self.coordinate_known_action_count,
            self.resolved_possession_action_count,
        ) != expected_counts:
            raise ValueError("fact feature counts must derive exactly from contributing evidence")
        if self.lineage.dependency_lineage != self.temporal_proof.dependency_lineage:
            raise ValueError("fact row lineage must equal temporal-proof lineage")
        if self.lineage.source_authority != self.temporal_proof.source_authority:
            raise ValueError("fact source authority must equal temporal proof")
        if self.lineage.authority_clocks != self.temporal_proof.authority_clocks:
            raise ValueError("fact authority clocks must equal temporal proof")
        if self.match_start_utc >= self.temporal_proof.feature_cutoff_ts:
            raise ValueError("fact match start must be strictly before the temporal cutoff")
        expected_coverage = _derive_fact_coverage(self, membership)
        if self.coverage != expected_coverage:
            raise ValueError("fact six-dimension coverage must derive exactly from evidence")
        expected_applicability = _expected_applicability_assessment(
            expected_coverage,
            uncertain=self.right_censored_or_uncertain,
        )
        if self.applicability != expected_applicability:
            raise ValueError("player-match applicability state/reasons must be exactly derived")
        return self

    @property
    def primary_key(self) -> tuple[UUID, UUID, UUID, UUID, str]:
        return (
            self.tenant_context.tenant_id,
            self.source_manifest_id,
            self.match_id,
            self.player_id,
            self.player_match_fact_schema_version,
        )


def _derive_fact_coverage(
    fact: SilverPlayerMatchFact,
    membership: dict[UUID, int],
) -> GoldCoverage:
    actions = fact.contributing_actions
    lineups = fact.contributing_lineup_stints
    identity_count = len(actions) + len(lineups)
    coordinate_denominator = sum(bool(action.action_positions) for action in actions)
    coordinate_numerator = sum(
        _accepted_position_feature_evidence(action.action_positions) for action in actions
    )
    possession_eligible_ids = {
        action.action_id
        for action in actions
        if _possession_predicate_decision(
            action.action_event_taxonomy_id,
            action.action_subevent_taxonomy_id,
            action.team_id,
            action.action_tag_ids,
        )
        in {
            PossessionPredicateDecision.CONTESTED,
            PossessionPredicateDecision.CONTROL,
            PossessionPredicateDecision.DEAD_BALL_PRECEDING,
            PossessionPredicateDecision.RESTART,
        }
    }
    temporal_count = len(fact.temporal_proof.dependency_lineage.dependencies) + 1 + len(actions)
    counts = {
        GoldCoverageDimensionName.IDENTITY: (identity_count, identity_count),
        GoldCoverageDimensionName.LINEUP: (1, 1),
        GoldCoverageDimensionName.ACTION: (len(actions), len(actions)),
        GoldCoverageDimensionName.COORDINATE: (
            coordinate_numerator,
            coordinate_denominator,
        ),
        GoldCoverageDimensionName.POSSESSION: (
            sum(membership[action_id] == 1 for action_id in possession_eligible_ids),
            len(possession_eligible_ids),
        ),
        GoldCoverageDimensionName.TEMPORAL: (temporal_count, temporal_count),
    }
    partial_reasons = {
        GoldCoverageDimensionName.IDENTITY: "IDENTITY_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.LINEUP: "LINEUP_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.ACTION: "ACTION_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.COORDINATE: "COORDINATE_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.POSSESSION: "POSSESSION_EVIDENCE_INCOMPLETE",
        GoldCoverageDimensionName.TEMPORAL: "TEMPORAL_EVIDENCE_INCOMPLETE",
    }
    dimensions: list[GoldCoverageDimension] = []
    authority_rows = {row.authority_kind: row for row in accepted_authority_references()}
    for name in GoldCoverageDimensionName:
        numerator, denominator = counts[name]
        if denominator > 0:
            with localcontext() as context:
                context.prec = 38
                coverage = Decimal(numerator) / Decimal(denominator)
            state = (
                GoldCoverageState.COMPLETE
                if numerator == denominator
                else GoldCoverageState.PARTIAL
            )
            dimensions.append(
                GoldCoverageDimension(
                    name=name,
                    numerator=numerator,
                    denominator=denominator,
                    coverage=coverage,
                    state=state,
                    reason_codes=(partial_reasons[name],)
                    if state is GoldCoverageState.PARTIAL
                    else (),
                )
            )
        elif name in {
            GoldCoverageDimensionName.COORDINATE,
            GoldCoverageDimensionName.POSSESSION,
        }:
            authority_kind = (
                AuthorityKind.FIELD
                if name is GoldCoverageDimensionName.COORDINATE
                else AuthorityKind.POSSESSION
            )
            reason = (
                "NO_APPLICABLE_COORDINATE_EVIDENCE"
                if name is GoldCoverageDimensionName.COORDINATE
                else "NO_POSSESSION_ELIGIBLE_ACTIONS"
            )
            dimensions.append(
                GoldCoverageDimension(
                    name=name,
                    numerator=0,
                    denominator=0,
                    coverage=Decimal(1),
                    state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
                    reason_codes=(reason,),
                    zero_denominator_authority=authority_rows[authority_kind],
                )
            )
        else:
            dimensions.append(
                GoldCoverageDimension(
                    name=name,
                    numerator=0,
                    denominator=0,
                    coverage=Decimal(0),
                    state=GoldCoverageState.MISSING_ZERO_DENOMINATOR,
                    reason_codes=(partial_reasons[name],),
                )
            )
    frozen = tuple(dimensions)
    missing = tuple(
        sorted(
            (dimension.name for dimension in frozen if dimension.state in _MISSING_COVERAGE_STATES),
            key=lambda name: name.value,
        )
    )
    return GoldCoverage(
        dimensions=frozen,
        coverage_overall=min(dimension.coverage for dimension in frozen),
        missing_dimensions=missing,
    )


def _aggregate_fact_coverage(facts: tuple[SilverPlayerMatchFact, ...]) -> GoldCoverage:
    dimensions: list[GoldCoverageDimension] = []
    for index, name in enumerate(GoldCoverageDimensionName):
        inputs = tuple(fact.coverage.dimensions[index] for fact in facts)
        denominator = sum(dimension.denominator for dimension in inputs)
        reasons = tuple(
            sorted(
                {
                    reason
                    for dimension in inputs
                    if dimension.state in _MISSING_COVERAGE_STATES
                    for reason in dimension.reason_codes
                }
            )
        )
        states = {dimension.state for dimension in inputs}
        if GoldCoverageState.FAILED in states:
            dimension = GoldCoverageDimension(
                name=name,
                numerator=0,
                denominator=denominator,
                coverage=Decimal(0),
                state=GoldCoverageState.FAILED,
                reason_codes=reasons,
            )
        elif GoldCoverageState.AUTHORITY_MISSING in states or (
            denominator > 0 and GoldCoverageState.MISSING_ZERO_DENOMINATOR in states
        ):
            dimension = GoldCoverageDimension(
                name=name,
                numerator=0,
                denominator=denominator,
                coverage=Decimal(0),
                state=GoldCoverageState.AUTHORITY_MISSING,
                reason_codes=reasons,
            )
        elif denominator == 0:
            optional = name in {
                GoldCoverageDimensionName.COORDINATE,
                GoldCoverageDimensionName.POSSESSION,
            }
            if optional and states == {GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR}:
                expected_kind = (
                    AuthorityKind.FIELD
                    if name is GoldCoverageDimensionName.COORDINATE
                    else AuthorityKind.POSSESSION
                )
                authority = next(
                    reference
                    for reference in accepted_authority_references()
                    if reference.authority_kind is expected_kind
                )
                if any(item.zero_denominator_authority != authority for item in inputs):
                    raise ValueError("fact optional-zero authority cannot drift during aggregation")
                dimension = GoldCoverageDimension(
                    name=name,
                    numerator=0,
                    denominator=0,
                    coverage=Decimal(1),
                    state=GoldCoverageState.NOT_APPLICABLE_ZERO_DENOMINATOR,
                    reason_codes=tuple(
                        sorted({reason for item in inputs for reason in item.reason_codes})
                    ),
                    zero_denominator_authority=authority,
                )
            else:
                dimension = GoldCoverageDimension(
                    name=name,
                    numerator=0,
                    denominator=0,
                    coverage=Decimal(0),
                    state=GoldCoverageState.MISSING_ZERO_DENOMINATOR,
                    reason_codes=reasons,
                )
        else:
            numerator = sum(item.numerator for item in inputs)
            with localcontext() as context:
                context.prec = 38
                coverage = Decimal(numerator) / Decimal(denominator)
            state = (
                GoldCoverageState.COMPLETE
                if numerator == denominator
                else GoldCoverageState.PARTIAL
            )
            dimension = GoldCoverageDimension(
                name=name,
                numerator=numerator,
                denominator=denominator,
                coverage=coverage,
                state=state,
                reason_codes=reasons if state is GoldCoverageState.PARTIAL else (),
            )
        dimensions.append(dimension)
    frozen = tuple(dimensions)
    missing = tuple(
        sorted(
            (item.name for item in frozen if item.state in _MISSING_COVERAGE_STATES),
            key=lambda item: item.value,
        )
    )
    return GoldCoverage(
        dimensions=frozen,
        coverage_overall=min(item.coverage for item in frozen),
        missing_dimensions=missing,
    )


class GoldFeatureValues(ContractModel):
    """The entire closed W04 Gold feature vector."""

    action_count: StrictNonNegativeInt
    coordinate_known_action_count: StrictNonNegativeInt
    match_count: StrictNonNegativeInt
    resolved_possession_action_count: StrictNonNegativeInt

    @model_validator(mode="after")
    def component_counts_cannot_exceed_actions(self) -> Self:
        if self.coordinate_known_action_count > self.action_count:
            raise ValueError("coordinate-known count cannot exceed action_count")
        if self.resolved_possession_action_count > self.action_count:
            raise ValueError("resolved-possession count cannot exceed action_count")
        return self


class GoldPlayerWindow(WyscoutProductRow):
    gold_schema_version: Literal["w04-wyscout-gold-player-window-v1"] = (
        "w04-wyscout-gold-player-window-v1"
    )
    player_id: StrictUuid
    competition_id: StrictUuid
    season_id: StrictUuid
    role_context_id: StrictUuid
    role_context_version: Literal["w04-neutral-role-context-v1"]
    role_context_state: Literal["neutral_unscoped"]
    window_definition_id: StrictUuid
    window_start_utc: UtcInstant
    window_end_utc: UtcInstant
    feature_cutoff_ts: UtcInstant
    dependency_lineage_hash: Sha256Digest
    feature_schema_hash: Sha256Digest
    temporal_proof: W04SemanticTemporalProof
    coverage: GoldCoverage
    applicability: W04ApplicabilityAssessment
    features: GoldFeatureValues
    contributing_player_match_facts: Annotated[
        tuple[SilverPlayerMatchFact, ...],
        Field(min_length=1),
    ]
    contributing_player_match_keys: Annotated[
        tuple[tuple[StrictUuid, StrictUuid, StrictUuid, StrictUuid, str], ...],
        Field(min_length=1),
    ]

    @model_validator(mode="after")
    def gold_key_and_feature_state_are_exact(self) -> Self:
        if (
            self.role_context_id != ROLE_CONTEXT_ID
            or self.role_context_version != ROLE_CONTEXT_VERSION
            or self.role_context_state != ROLE_CONTEXT_STATE
        ):
            raise ValueError("Gold must use the exact neutral role UUIDv5 context")
        if not self.window_start_utc < self.window_end_utc:
            raise ValueError("Gold window_start_utc must be before window_end_utc")
        if self.feature_cutoff_ts != self.temporal_proof.feature_cutoff_ts:
            raise ValueError("Gold cutoff must equal temporal proof cutoff")
        if self.dependency_lineage_hash != self.temporal_proof.dependency_lineage_hash:
            raise ValueError("Gold lineage hash must equal temporal proof lineage")
        if self.lineage.dependency_lineage != self.temporal_proof.dependency_lineage:
            raise ValueError("Gold row lineage must equal temporal-proof lineage")
        if self.lineage.source_authority != self.temporal_proof.source_authority:
            raise ValueError("Gold source authority must equal temporal proof")
        if self.lineage.authority_clocks != self.temporal_proof.authority_clocks:
            raise ValueError("Gold authority clocks must equal temporal proof")
        if self.feature_schema_hash != FEATURE_SCHEMA_HASH or (
            self.feature_schema_hash != self.temporal_proof.feature_schema_hash
        ):
            raise ValueError("Gold feature schema must be the accepted non-key digest")
        facts = self.contributing_player_match_facts
        fact_keys = tuple(fact.primary_key for fact in facts)
        if fact_keys != tuple(sorted(set(fact_keys))):
            raise ValueError("contributing player-match facts must be unique and ordered")
        if self.contributing_player_match_keys != fact_keys:
            raise ValueError("contributing player-match keys must derive exactly from facts")
        for fact in facts:
            if (
                fact.build_id != self.build_id
                or fact.tenant_context != self.tenant_context
                or fact.source_manifest_id != SOURCE_MANIFEST_ID
                or fact.player_id != self.player_id
                or fact.competition_id != self.competition_id
                or fact.season_id != self.season_id
                or fact.lineage != self.lineage
                or fact.temporal_proof != self.temporal_proof
            ):
                raise ValueError("contributing fact identity/authority differs from Gold")
            if not self.window_start_utc <= fact.match_start_utc < self.window_end_utc:
                raise ValueError("contributing fact falls outside the Gold window")
            if fact.match_start_utc >= self.feature_cutoff_ts:
                raise ValueError("contributing fact is not strictly before feature cutoff")
        expected_source_rows = tuple(
            sorted(
                {row for fact in facts for row in fact.source_rows},
                key=lambda row: (row.completion_relative_path, row.source_record_ordinal),
            )
        )
        if self.source_rows != expected_source_rows:
            raise ValueError("Gold source rows must derive exactly from selected facts")
        expected_features = GoldFeatureValues(
            action_count=sum(fact.action_count for fact in facts),
            coordinate_known_action_count=sum(fact.coordinate_known_action_count for fact in facts),
            match_count=len({fact.match_id for fact in facts}),
            resolved_possession_action_count=sum(
                fact.resolved_possession_action_count for fact in facts
            ),
        )
        if self.features != expected_features:
            raise ValueError("Gold four-feature vector must reconcile exactly to selected facts")
        expected_coverage = _aggregate_fact_coverage(facts)
        if self.coverage != expected_coverage:
            raise ValueError("Gold six-dimension coverage must aggregate exactly from facts")
        expected_applicability = _expected_applicability_assessment(
            expected_coverage,
            uncertain=any(fact.right_censored_or_uncertain for fact in facts),
        )
        if self.applicability != expected_applicability:
            raise ValueError("Gold applicability state/reasons must be exactly derived")
        return self

    @property
    def primary_key(
        self,
    ) -> tuple[UUID, UUID, UUID, UUID, UUID, str, UUID, datetime, datetime, datetime, str]:
        return (
            self.tenant_context.tenant_id,
            self.player_id,
            self.competition_id,
            self.season_id,
            self.role_context_id,
            self.role_context_version,
            self.window_definition_id,
            self.window_start_utc,
            self.window_end_utc,
            self.feature_cutoff_ts,
            self.dependency_lineage_hash,
        )


_ADMITTED_EVENT_SUBEVENT_PAIRS = frozenset(
    {
        (1, 10),
        (1, 11),
        (1, 12),
        (1, 13),
        (2, 20),
        (2, 21),
        (2, 22),
        (2, 23),
        (2, 24),
        (2, 25),
        (2, 26),
        (2, 27),
        (3, 30),
        (3, 31),
        (3, 32),
        (3, 33),
        (3, 34),
        (3, 35),
        (3, 36),
        (4, 40),
        (5, 50),
        (5, 51),
        (6, 60),
        (7, 70),
        (7, 71),
        (7, 72),
        (8, 80),
        (8, 81),
        (8, 82),
        (8, 83),
        (8, 84),
        (8, 85),
        (8, 86),
        (9, 90),
        (9, 91),
        (10, 100),
    }
)


class ActionSubeventReason(StrEnum):
    STRING = "ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED"
    BOOLEAN = "ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER"
    NULL = "ACTION_SUBEVENT_NULL_UNMAPPED"
    NUMBER = "ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED"
    ARRAY = "ACTION_SUBEVENT_ARRAY_UNMAPPED"
    OBJECT = "ACTION_SUBEVENT_OBJECT_UNMAPPED"
    UNKNOWN_INTEGER = "ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY"


class ActionSubeventOutcome(ContractModel):
    action_event_taxonomy_id: StrictNonNegativeInt | None
    raw_subevent: CanonicalJsonValue
    canonical_value: StrictNonNegativeInt | None = None
    rejected_raw_value: CanonicalJsonValue | None = None
    reason_code: ActionSubeventReason | None = None

    @model_validator(mode="after")
    def emitting_and_rejected_states_are_disjoint(self) -> Self:
        expected_canonical, expected_rejected, expected_reason = _classify_action_subevent_parts(
            self.action_event_taxonomy_id, self.raw_subevent
        )
        if (
            self.canonical_value != expected_canonical
            or self.rejected_raw_value != expected_rejected
            or self.reason_code is not expected_reason
        ):
            raise ValueError(
                "subevent outcome must derive exactly from its raw event/value evidence"
            )
        return self


def _classify_action_subevent_parts(
    action_event_taxonomy_id: int | None,
    raw_subevent: CanonicalJsonValue,
) -> tuple[int | None, CanonicalJsonValue | None, ActionSubeventReason | None]:

    if isinstance(raw_subevent, CanonicalJsonInteger):
        value = raw_subevent.value
        if (
            type(action_event_taxonomy_id) is int
            and value >= 0
            and (action_event_taxonomy_id, value) in _ADMITTED_EVENT_SUBEVENT_PAIRS
        ):
            return value, None, None
        reason = ActionSubeventReason.UNKNOWN_INTEGER
    elif isinstance(raw_subevent, CanonicalJsonString):
        reason = ActionSubeventReason.STRING
    elif isinstance(raw_subevent, CanonicalJsonBoolean):
        reason = ActionSubeventReason.BOOLEAN
    elif isinstance(raw_subevent, CanonicalJsonNull):
        reason = ActionSubeventReason.NULL
    elif isinstance(raw_subevent, CanonicalJsonNumber):
        reason = ActionSubeventReason.NUMBER
    elif isinstance(raw_subevent, CanonicalJsonArray):
        reason = ActionSubeventReason.ARRAY
    else:
        reason = ActionSubeventReason.OBJECT
    return None, raw_subevent, reason


def classify_action_subevent(
    action_event_taxonomy_id: int | None,
    raw_subevent: CanonicalJsonValue,
) -> ActionSubeventOutcome:
    """Apply only the accepted strict integer event/subevent pair transform."""

    canonical, rejected, reason = _classify_action_subevent_parts(
        action_event_taxonomy_id, raw_subevent
    )
    return ActionSubeventOutcome(
        action_event_taxonomy_id=action_event_taxonomy_id,
        raw_subevent=raw_subevent,
        canonical_value=canonical,
        rejected_raw_value=rejected,
        reason_code=reason,
    )


class ProductPathRole(StrEnum):
    BRONZE_KNOWN_RECORD = "BRONZE_KNOWN_RECORD"
    BRONZE_REJECTED_RECORD = "BRONZE_REJECTED_RECORD"
    BRONZE_REJECTED_FIELD = "BRONZE_REJECTED_FIELD"
    SILVER_COMPETITION = "SILVER_COMPETITION"
    SILVER_TEAM = "SILVER_TEAM"
    SILVER_PLAYER = "SILVER_PLAYER"
    SILVER_MATCH = "SILVER_MATCH"
    SILVER_ACTION = "SILVER_ACTION"
    SILVER_LINEUP_STINT = "SILVER_LINEUP_STINT"
    SILVER_POSSESSION = "SILVER_POSSESSION"
    SILVER_PLAYER_MATCH_FACT = "SILVER_PLAYER_MATCH_FACT"
    GOLD_PLAYER_WINDOW = "GOLD_PLAYER_WINDOW"
    BRONZE_MANIFEST = "BRONZE_MANIFEST"
    SILVER_MANIFEST = "SILVER_MANIFEST"
    GOLD_MANIFEST = "GOLD_MANIFEST"
    REBUILD_INVOCATION_RECEIPT = "REBUILD_INVOCATION_RECEIPT"
    TEMPORAL_BOUNDARY_RECEIPT = "TEMPORAL_BOUNDARY_RECEIPT"


_SHA = r"[0-9a-f]{64}"
_UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}"
_COUNTRY = r"(?:england|france|germany|italy|spain)"
_UTC_TOKEN = r"[0-9]{8}T[0-9]{12}Z"  # nosec B105
_KNOWN_KIND = r"(?:competition|team|player|event-taxonomy|tag-taxonomy|match|action)"
_RAW_STATE = r"(?:missing|null|non-string|string-unknown-safe|string-unsafe)"

_PATH_PATTERNS: dict[ProductPathRole, re.Pattern[str]] = {
    ProductPathRole.BRONZE_KNOWN_RECORD: re.compile(
        rf"^data/working/wyscout/v5/bronze/build_id={_SHA}/records/record_kind={_KNOWN_KIND}/source_sha256={_SHA}/part-00000\.parquet$"
    ),
    ProductPathRole.BRONZE_REJECTED_RECORD: re.compile(
        rf"^data/working/wyscout/v5/bronze/build_id={_SHA}/quarantine/rejected-record/record_kind=unknown/raw_kind_state={_RAW_STATE}/raw_kind_sha256={_SHA}/source_sha256={_SHA}/part-00000\.parquet$"
    ),
    ProductPathRole.BRONZE_REJECTED_FIELD: re.compile(
        rf"^data/working/wyscout/v5/bronze/build_id={_SHA}/quarantine/rejected-field/record_kind={_KNOWN_KIND}/source_sha256={_SHA}/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_COMPETITION: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/competition/source_partition=global/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_TEAM: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/team/source_partition=global/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_PLAYER: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/player/source_partition=global/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_MATCH: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/match/source_partition={_COUNTRY}/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_ACTION: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/action/source_partition={_COUNTRY}/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_LINEUP_STINT: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/lineup-stint/source_partition={_COUNTRY}/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_POSSESSION: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/possession/source_partition={_COUNTRY}/part-00000\.parquet$"
    ),
    ProductPathRole.SILVER_PLAYER_MATCH_FACT: re.compile(
        rf"^data/working/wyscout/v5/silver/build_id={_SHA}/player-match-fact/source_partition={_COUNTRY}/part-00000\.parquet$"
    ),
    ProductPathRole.GOLD_PLAYER_WINDOW: re.compile(
        rf"^data/working/wyscout/v5/gold/build_id={_SHA}/player-window/competition_id={_UUID}/window_definition_id={_UUID}/window_start_utc={_UTC_TOKEN}/window_end_utc={_UTC_TOKEN}/feature_cutoff_ts={_UTC_TOKEN}/part-00000\.parquet$"
    ),
    ProductPathRole.BRONZE_MANIFEST: re.compile(
        rf"^data/manifests/wyscout/v5/bronze/{_SHA}\.manifest\.json$"
    ),
    ProductPathRole.SILVER_MANIFEST: re.compile(
        rf"^data/manifests/wyscout/v5/silver/{_SHA}\.manifest\.json$"
    ),
    ProductPathRole.GOLD_MANIFEST: re.compile(
        rf"^data/manifests/wyscout/v5/gold/{_SHA}\.manifest\.json$"
    ),
    ProductPathRole.REBUILD_INVOCATION_RECEIPT: re.compile(
        rf"^runs/w04/wyscout-rebuild/{_SHA}/{_UUID}\.receipt\.json$"
    ),
    ProductPathRole.TEMPORAL_BOUNDARY_RECEIPT: re.compile(
        rf"^runs/w04/wyscout-rebuild/{_SHA}/{_UUID}/boundary/{_SHA}\.temporal-boundary-receipt\.json$"
    ),
}


class WyscoutProductPath(ContractModel):
    path_role: ProductPathRole
    relative_path: str = Field(strict=True)

    @model_validator(mode="after")
    def path_is_the_exact_role_template(self) -> Self:
        if normalize("NFC", self.relative_path) != self.relative_path:
            raise ValueError("product path must be NFC")
        if _PATH_PATTERNS[self.path_role].fullmatch(self.relative_path) is None:
            raise ValueError("relative_path does not match its exact path role")
        for token in re.findall(_UUID, self.relative_path):
            if str(UUID(token)) != token:
                raise ValueError("path UUID token must be canonical")
        for token in re.findall(_UTC_TOKEN, self.relative_path):
            try:
                datetime.strptime(token, "%Y%m%dT%H%M%S%fZ")
            except ValueError as exc:
                raise ValueError("path UTC token must be a real six-fraction instant") from exc
        return self


class Layer(StrEnum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"


class ManifestPartitionValue(ContractModel):
    key: str = Field(strict=True, pattern=r"^[a-z][a-z0-9_]{0,63}$")
    value: str = Field(strict=True, min_length=1, max_length=512)


class ParentLayerManifest(ContractModel):
    layer: Layer
    build_id: Sha256Digest
    relative_path: str = Field(strict=True)
    sha256: Sha256Digest

    @model_validator(mode="after")
    def parent_path_is_exact_and_safe(self) -> Self:
        if self.layer is Layer.GOLD:
            raise ValueError("Gold cannot be a parent layer")
        expected = (
            f"data/manifests/wyscout/v5/{self.layer.value.lower()}/{self.build_id}.manifest.json"
        )
        if self.relative_path != expected:
            raise ValueError("parent manifest path must be the exact safe same-build path")
        return self


_SERIALIZER_OWNER: dict[ProductPathRole, str] = {
    ProductPathRole.BRONZE_KNOWN_RECORD: "bronze.py",
    ProductPathRole.BRONZE_REJECTED_RECORD: "bronze.py",
    ProductPathRole.BRONZE_REJECTED_FIELD: "bronze.py",
    ProductPathRole.SILVER_COMPETITION: "entities.py",
    ProductPathRole.SILVER_TEAM: "entities.py",
    ProductPathRole.SILVER_PLAYER: "entities.py",
    ProductPathRole.SILVER_MATCH: "entities.py",
    ProductPathRole.SILVER_ACTION: "actions.py",
    ProductPathRole.SILVER_LINEUP_STINT: "lineups.py",
    ProductPathRole.SILVER_POSSESSION: "possessions.py",
    ProductPathRole.SILVER_PLAYER_MATCH_FACT: "player_match.py",
    ProductPathRole.GOLD_PLAYER_WINDOW: "gold.py",
    ProductPathRole.BRONZE_MANIFEST: "bronze.py",
    ProductPathRole.SILVER_MANIFEST: "silver_manifest.py",
    ProductPathRole.GOLD_MANIFEST: "gold.py",
    ProductPathRole.REBUILD_INVOCATION_RECEIPT: "rebuild.py",
    ProductPathRole.TEMPORAL_BOUNDARY_RECEIPT: "temporal_boundary.py",
}


class LayerManifestEntry(ContractModel):
    path: WyscoutProductPath
    serializer: str = Field(strict=True)
    serializer_version: str = Field(strict=True, min_length=1, max_length=128)
    schema_role: str = Field(strict=True, min_length=1, max_length=128)
    row_count: StrictPositiveInt
    semantic_sha256: Sha256Digest
    physical_sha256: Sha256Digest
    size_bytes: StrictPositiveInt
    ordered_parent_paths: tuple[str, ...]
    partition_values: tuple[ManifestPartitionValue, ...]
    classification: SourceUseClassification
    complete: Literal[True] = True

    @model_validator(mode="after")
    def entry_binds_owner_rights_and_partition_order(self) -> Self:
        if self.serializer != _SERIALIZER_OWNER[self.path.path_role]:
            raise ValueError("manifest entry serializer does not own the path role")
        if self.schema_role != self.path.path_role.value:
            raise ValueError("manifest schema_role must equal path_role")
        expected_partitions = tuple(
            sorted(
                (
                    ManifestPartitionValue(key=key, value=value)
                    for segment in self.path.relative_path.split("/")
                    if (match := re.fullmatch(r"([a-z][a-z0-9_]*)=(.+)", segment))
                    for key, value in (match.groups(),)
                ),
                key=lambda item: item.key,
            )
        )
        if len({item.key for item in expected_partitions}) != len(expected_partitions):
            raise ValueError("path partition keys must be unique")
        if self.partition_values != expected_partitions:
            raise ValueError("manifest partition values must exactly equal sorted path pairs")
        if not _classification_is_exact(self.classification):
            raise ValueError("manifest entries retain exact restricted source rights")
        if self.ordered_parent_paths != tuple(sorted(set(self.ordered_parent_paths))):
            raise ValueError("manifest parent product paths must be unique and ordered")
        entry_layer = next(
            layer for layer, roles in _LAYER_PRODUCT_ROLES.items() if self.path.path_role in roles
        )
        if entry_layer is Layer.BRONZE:
            if self.ordered_parent_paths:
                raise ValueError("Bronze product entries have no parent products")
        else:
            if not self.ordered_parent_paths:
                raise ValueError("Silver and Gold entries require preceding-layer parents")
            expected_parent_layer = Layer.BRONZE if entry_layer is Layer.SILVER else Layer.SILVER
            build_match = re.search(r"/build_id=([0-9a-f]{64})/", self.path.relative_path)
            if build_match is None:
                raise ValueError("product entry path lacks build identity")
            for parent_path in self.ordered_parent_paths:
                parent_role = _path_role_for_product(parent_path)
                if parent_role not in _LAYER_PRODUCT_ROLES[expected_parent_layer]:
                    raise ValueError("manifest parent product crosses the preceding layer")
                if f"/build_id={build_match.group(1)}/" not in parent_path:
                    raise ValueError("manifest parent product must use the same build")
        return self


_LAYER_PRODUCT_ROLES: dict[Layer, set[ProductPathRole]] = {
    Layer.BRONZE: {
        ProductPathRole.BRONZE_KNOWN_RECORD,
        ProductPathRole.BRONZE_REJECTED_RECORD,
        ProductPathRole.BRONZE_REJECTED_FIELD,
    },
    Layer.SILVER: {
        ProductPathRole.SILVER_COMPETITION,
        ProductPathRole.SILVER_TEAM,
        ProductPathRole.SILVER_PLAYER,
        ProductPathRole.SILVER_MATCH,
        ProductPathRole.SILVER_ACTION,
        ProductPathRole.SILVER_LINEUP_STINT,
        ProductPathRole.SILVER_POSSESSION,
        ProductPathRole.SILVER_PLAYER_MATCH_FACT,
    },
    Layer.GOLD: {ProductPathRole.GOLD_PLAYER_WINDOW},
}
_LAYER_MANIFEST_ROLE = {
    Layer.BRONZE: ProductPathRole.BRONZE_MANIFEST,
    Layer.SILVER: ProductPathRole.SILVER_MANIFEST,
    Layer.GOLD: ProductPathRole.GOLD_MANIFEST,
}


def _path_role_for_product(relative_path: str) -> ProductPathRole:
    matching = tuple(
        role
        for layer_roles in _LAYER_PRODUCT_ROLES.values()
        for role in layer_roles
        if _PATH_PATTERNS[role].fullmatch(relative_path) is not None
    )
    if len(matching) != 1:
        raise ValueError("parent product path must match exactly one product role")
    return matching[0]


class LayerManifest(ContractModel):
    manifest_schema_version: Literal["w04-wyscout-layer-manifest-v1"] = (
        "w04-wyscout-layer-manifest-v1"
    )
    construction_authority_state: Literal["semantic_only_unchecked"] = "semantic_only_unchecked"
    layer: Layer
    build_id: Sha256Digest
    manifest_path: WyscoutProductPath
    source_manifest_id: StrictUuid
    source_manifest_sha256: Sha256Digest
    source_completion_index_sha256: Sha256Digest
    tenant_context: TenantContext
    classification: SourceUseClassification
    source_available_at: UtcInstant
    source_acquired_at: UtcInstant
    authority_clocks: Annotated[
        tuple[WyscoutAuthorityClock, ...], Field(min_length=4, max_length=4)
    ]
    feature_schema_hash: Sha256Digest
    dependency_lineage_hash: Sha256Digest
    dependency_lineage: DependencyLineage
    entries: Annotated[tuple[LayerManifestEntry, ...], Field(min_length=1)]
    parent_layer_manifests: tuple[ParentLayerManifest, ...]
    complete: Literal[True] = True

    @model_validator(mode="after")
    def layer_order_and_entries_are_exact(self) -> Self:
        if self.manifest_path.path_role is not _LAYER_MANIFEST_ROLE[self.layer]:
            raise ValueError("layer manifest path role differs from layer")
        if (
            self.source_manifest_id != SOURCE_MANIFEST_ID
            or self.source_manifest_sha256 != SOURCE_MANIFEST_SHA256
            or self.source_completion_index_sha256 != SOURCE_COMPLETION_INDEX_SHA256
        ):
            raise ValueError("layer manifest must bind source manifest and completion index")
        expected_manifest_path = (
            f"data/manifests/wyscout/v5/{self.layer.value.lower()}/{self.build_id}.manifest.json"
        )
        if self.manifest_path.relative_path != expected_manifest_path:
            raise ValueError("manifest filename/layer/build must be exactly equal")
        if (
            not _tenant_is_exact(self.tenant_context)
            or not _classification_is_exact(self.classification)
            or self.source_available_at != SOURCE_RELEASE
            or self.source_acquired_at != SOURCE_ACQUIRED_AT
        ):
            raise ValueError("layer manifest source authority is not exact")
        if self.authority_clocks != accepted_authority_clocks():
            raise ValueError("layer manifest authority clocks are not exact")
        if self.feature_schema_hash != FEATURE_SCHEMA_HASH:
            raise ValueError("layer manifest feature schema must be accepted")
        _validate_exact_dependency_lineage(self.dependency_lineage)
        if (
            self.dependency_lineage_hash != self.dependency_lineage.lineage_hash
            or self.dependency_lineage_hash
            != dependency_lineage_hash(self.dependency_lineage.dependencies)
        ):
            raise ValueError("layer manifest dependency lineage hash must be recomputed")
        paths = tuple(entry.path.relative_path for entry in self.entries)
        if paths != tuple(sorted(paths)) or len(paths) != len(set(paths)):
            raise ValueError("manifest entry paths must be unique and ordered")
        if any(
            entry.path.path_role not in _LAYER_PRODUCT_ROLES[self.layer] for entry in self.entries
        ):
            raise ValueError("manifest entry crosses its layer")
        build_token = f"build_id={self.build_id}"
        if any(build_token not in entry.path.relative_path for entry in self.entries):
            raise ValueError("every product entry path must carry the manifest build ID")
        if self.layer is Layer.BRONZE:
            if self.parent_layer_manifests:
                raise ValueError("Bronze has no parent layer manifest")
        else:
            expected_parent = Layer.BRONZE if self.layer is Layer.SILVER else Layer.SILVER
            if len(self.parent_layer_manifests) != 1 or (
                self.parent_layer_manifests[0].layer is not expected_parent
            ):
                raise ValueError("layer order must be Bronze-to-Silver-to-Gold")
            if self.parent_layer_manifests[0].build_id != self.build_id:
                raise ValueError("parent layer manifest must use the same build")
        return self


__all__ = [
    "ActionPosition",
    "ActionSubeventOutcome",
    "ActionSubeventReason",
    "AuthorityKind",
    "BronzeKnownRecord",
    "BronzeRejectedField",
    "BronzeRejectedRecord",
    "CanonicalJsonArray",
    "CanonicalJsonBoolean",
    "CanonicalJsonInteger",
    "CanonicalJsonKind",
    "CanonicalJsonMember",
    "CanonicalJsonNull",
    "CanonicalJsonNumber",
    "CanonicalJsonObject",
    "CanonicalJsonString",
    "CanonicalJsonValue",
    "CountryPartition",
    "FEATURE_DEPENDENCY_ID",
    "FEATURE_SCHEMA_HASH",
    "FIELD_DEPENDENCY_ID",
    "GoldCoverage",
    "GoldCoverageDimension",
    "GoldCoverageDimensionName",
    "GoldCoverageState",
    "GoldFeatureValues",
    "GoldPlayerWindow",
    "Layer",
    "LayerManifest",
    "LayerManifestEntry",
    "ManifestPartitionValue",
    "NominalMinuteInterval",
    "POSSESSION_DEPENDENCY_ID",
    "ParentLayerManifest",
    "PossessionEligibilityState",
    "ProductPathRole",
    "ROLE_CONTEXT_ID",
    "ROLE_CONTEXT_STATE",
    "ROLE_CONTEXT_VERSION",
    "RawKindEvidence",
    "RawFieldMeasurement",
    "RawKindState",
    "RejectedFieldDecision",
    "SOURCE_MANIFEST_ID",
    "SOURCE_MANIFEST_SHA256",
    "SOURCE_COMPLETION_INDEX_SHA256",
    "SOURCE_ACQUIRED_AT",
    "SilverAction",
    "SilverCompetition",
    "SilverLineupStint",
    "SilverMatch",
    "SilverPlayer",
    "SilverPlayerMatchFact",
    "SilverPossession",
    "SilverTeam",
    "SourceRecordKind",
    "W04Applicability",
    "W04ApplicabilityAssessment",
    "W04SemanticTemporalProof",
    "WyscoutAuthorityReference",
    "WyscoutAuthorityClock",
    "WyscoutProductPath",
    "WyscoutRawSourceRowReference",
    "WyscoutRowLineage",
    "WyscoutSourceRecordEnvelope",
    "WyscoutSourceRowReference",
    "WyscoutSourceAuthority",
    "accepted_authority_references",
    "accepted_authority_clocks",
    "accepted_source_authority",
    "accepted_source_classification",
    "canonical_contract_json_bytes",
    "canonical_raw_json_bytes",
    "canonical_source_uuid",
    "canonicalize_json_value",
    "classify_action_subevent",
    "classify_raw_record_kind",
    "dependency_lineage_hash",
    "dependency_sort_key",
    "feature_dependency_id",
]
