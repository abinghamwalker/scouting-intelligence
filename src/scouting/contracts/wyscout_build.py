"""Strict, standalone contracts for the bounded W04 Wyscout build.

The module is intentionally declarative and side-effect free.  It does not read or
write the filesystem, contact a provider, materialise a product, or import another
``scouting`` module.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Annotated, Final, Literal, Self, cast
from unicodedata import is_normalized, normalize
from uuid import NAMESPACE_URL, UUID, uuid5

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

Sha256 = Annotated[str, StringConstraints(strict=True, pattern=r"^[0-9a-f]{64}$")]
CanonicalUuid = Annotated[
    str,
    StringConstraints(
        strict=True,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    ),
]
UuidV4 = Annotated[
    str,
    StringConstraints(
        strict=True,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    ),
]
UuidV5 = Annotated[
    str,
    StringConstraints(
        strict=True,
        pattern=r"^[0-9a-f]{8}-[0-9a-f]{4}-5[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    ),
]
UtcInstant = Annotated[
    str,
    StringConstraints(
        strict=True,
        pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z$",
    ),
]
RelativePath = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^[A-Za-z0-9._=/-]+$", min_length=1),
]
Base64Url = Annotated[
    str,
    StringConstraints(strict=True, pattern=r"^[A-Za-z0-9_-]+$", min_length=1),
]
StrictPositiveInt = Annotated[int, Field(strict=True, ge=1)]
StrictNonNegativeInt = Annotated[int, Field(strict=True, ge=0)]
JsonInteger = Annotated[int, Field(strict=True, ge=0, le=9_007_199_254_740_991)]

SOURCE_MANIFEST_ID: Final = "4e16bdb5-afe7-5601-88ad-adc124cfce3b"
SOURCE_MANIFEST_SHA256: Final = "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
SOURCE_COMPLETION_INDEX_SHA256: Final = (
    "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
)
MATCH_ID: Final = "bad97950-6fac-5cf0-a93c-094f91abbb9b"
WINDOW_DEFINITION_ID: Final = "a0af8d56-e41d-5467-b46e-82887c4861e0"
WINDOW_START_UTC: Final = "2017-08-11T00:00:00Z"
WINDOW_END_UTC: Final = "2017-08-12T00:00:00Z"
WINDOW_SCHEMA_VERSION: Final = "w04-single-match-poc-window-v1"
WINDOW_BYTES_SHA256: Final = "3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327"
SELECTED_MATCH_START_TS: Final = "2017-08-11T18:45:00Z"
SNAPSHOT_AS_OF_TS: Final = "2017-08-11T18:45:00Z"
FEATURE_CUTOFF_TS: Final = "2026-08-01T00:00:00Z"
DEPENDENCY_WATERMARK: Final = "2026-07-31T14:15:26Z"
TENANT_ID: Final = "65a43912-d412-5ff9-a364-7f84d1ad6c5d"
COMPETITION_ID: Final = "cb5c5317-fa4a-571e-93dc-ef6ce482eab7"
FEATURE_SCHEMA_HASH: Final = "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
IDENTITY_BUNDLE_ID: Final = "31638732-5b25-57db-9eb4-8e943a47a387"
IDENTITY_BUNDLE_SHA256: Final = "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"
ROLE_CONTEXT_ID: Final = "3a17850f-5ac4-5ad8-ac9a-b753f10bdf77"
ROLE_CONTEXT_STATE: Final = "neutral_unscoped"
ROLE_CONTEXT_VERSION: Final = "w04-neutral-role-context-v1"
PROJECTION_SCHEMA_VERSION: Final = "w04-wyscout-pre-build-projection-v1"

PRODUCT_CONTRACT_V1_SHA256: Final = (
    "0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293"
)
SCHEMA_BUNDLE_V1_SHA256: Final = "a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f"

WINDOW_NAMESPACE_NAME: Final = "urn:scouting-intelligence:w04:wyscout:window-definition:v1"
SOURCE_NAMESPACE_NAME: Final = (
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5"
)
CODE_MANIFEST_NAMESPACE_NAME: Final = "urn:scouting-intelligence:w04:wyscout:evidence-dependency:v1"

PRE_BUILD_PROJECTION_KEYS = (
    "authority_rows",
    "code_manifest_id",
    "code_manifest_sha256",
    "dependency_rows",
    "dependency_watermark",
    "environment_digest",
    "feature_cutoff_ts",
    "feature_schema_hash",
    "identity_bundle_id",
    "identity_bundle_sha256",
    "local_resource_digest",
    "product_contract_digest",
    "role_context_id",
    "role_context_state",
    "role_context_version",
    "schema_bundle_digest",
    "schema_version",
    "selected_lock_closure_digest",
    "source_manifest_id",
    "source_manifest_sha256",
    "tenant_club_id",
    "tenant_id",
    "window_definition_id",
    "window_end_utc",
    "window_start_utc",
)
POST_HASH_INVOCATION_KEYS = (
    "authority_rows",
    "build_id",
    *PRE_BUILD_PROJECTION_KEYS[1:16],
    *PRE_BUILD_PROJECTION_KEYS[17:],
)

COMPONENT_KEYS = (
    "child_result_contract_digest",
    "editable_root_digest",
    "environment_values_digest",
    "executable_census_digest",
    "extracted_runtime_digest",
    "installed_record_runtime_digest",
    "interpreter_digest",
    "local_launcher_control_digest",
    "local_resource_digest",
    "lock_inputs_digest",
    "process_launch_contract_digest",
    "pyc_policy_source_map_digest",
    "selected_lock_closure_digest",
    "selector",
    "selector_bootstrap_digest",
    "stdlib_digest",
    "uv_physical_sha256",
    "uv_version",
    "venv_bootstrap_digest",
    "wheel_declaration_digest",
)
_DIGEST_COMPONENT_KEYS = frozenset(COMPONENT_KEYS) - {"selector", "uv_version"}
_STABLE_MANIFEST_KEYS = tuple(
    sorted((*COMPONENT_KEYS, "environment_digest", "repository_code_sha256", "schema_version"))
)
ADMISSION_ARGV = (
    "uv",
    "run",
    "--locked",
    "--no-sync",
    "python",
    "-S",
    "-B",
    "scripts/admit_wyscout_v5_runtime.py",
)
REBUILD_ARGV = (*ADMISSION_ARGV[:-1], "scripts/rebuild_wyscout_v5.py")


class ContractModel(BaseModel):
    """Closed immutable strict base for every W04 value."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _normalize_json(value: object) -> object:
    if value is None or type(value) in {bool, int}:
        return value
    if type(value) is float:
        raise TypeError("canonical JSON forbids floats")
    if type(value) is str:
        text = str(value)
        if any(0xD800 <= ord(character) <= 0xDFFF for character in text):
            raise ValueError("canonical JSON forbids surrogates")
        if not is_normalized("NFC", text):
            raise ValueError("canonical JSON strings must already be NFC")
        return text
    if isinstance(value, (list, tuple)):
        return [_normalize_json(item) for item in value]
    if isinstance(value, dict):
        mapping = cast(dict[object, object], value)
        if any(type(key) is not str for key in mapping):
            raise TypeError("canonical JSON object keys must be strings")
        string_mapping = cast(dict[str, object], mapping)
        if any(not is_normalized("NFC", key) for key in string_mapping):
            raise ValueError("canonical JSON object keys must already be NFC")
        return {
            normalize("NFC", key): _normalize_json(string_mapping[key])
            for key in sorted(string_mapping)
        }
    if isinstance(value, BaseModel):
        return _normalize_json(value.model_dump(mode="json"))
    raise TypeError(f"unsupported canonical JSON type: {type(value).__name__}")


def canonical_json_bytes(value: object, *, terminal_lf: bool = False) -> bytes:
    """Encode R20 canonical JSON, optionally adding its sole physical-file LF."""

    normalized = _normalize_json(value)
    raw = json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return raw + (b"\n" if terminal_lf else b"")


def load_canonical_json(raw: bytes, *, terminal_lf: bool = False) -> object:
    """Strictly parse and reproduce canonical JSON bytes."""

    if not isinstance(raw, bytes):
        raise TypeError("canonical JSON input must be bytes")
    body = raw[:-1] if terminal_lf and raw.endswith(b"\n") else raw
    if terminal_lf and (not raw.endswith(b"\n") or body.endswith(b"\n")):
        raise ValueError("physical canonical JSON requires exactly one terminal LF")
    if not terminal_lf and raw.endswith(b"\n"):
        raise ValueError("canonical preimages forbid a terminal LF")
    value = json.loads(body, object_pairs_hook=_reject_duplicate_pairs)
    if raw != canonical_json_bytes(value, terminal_lf=terminal_lf):
        raise ValueError("JSON bytes are not canonical")
    return value


def sha256_json(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.tzinfo != UTC:
        raise ValueError("instant must be UTC")
    return parsed


def _validate_relative_path(value: str) -> None:
    if not is_normalized("NFC", value):
        raise ValueError("relative path must be NFC")
    if (
        value.startswith("/")
        or value.endswith("/")
        or "//" in value
        or "\\" in value
        or "%" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or any(ord(character) < 32 for character in value)
    ):
        raise ValueError("invalid bounded POSIX relative path")


class WindowIdentity(ContractModel):
    match_id: Literal["bad97950-6fac-5cf0-a93c-094f91abbb9b"] = MATCH_ID
    source_manifest_id: Literal["4e16bdb5-afe7-5601-88ad-adc124cfce3b"] = SOURCE_MANIFEST_ID
    window_end_utc: Literal["2017-08-12T00:00:00Z"] = WINDOW_END_UTC
    window_schema_version: Literal["w04-single-match-poc-window-v1"] = WINDOW_SCHEMA_VERSION
    window_start_utc: Literal["2017-08-11T00:00:00Z"] = WINDOW_START_UTC

    @model_validator(mode="after")
    def identity_reproduces_frozen_uuid(self) -> Self:
        raw = canonical_json_bytes(self)
        if len(raw) != 250 or hashlib.sha256(raw).hexdigest() != WINDOW_BYTES_SHA256:
            raise ValueError("window canonical preimage drifted")
        namespace = uuid5(NAMESPACE_URL, WINDOW_NAMESPACE_NAME)
        actual = uuid5(namespace, f"single-match-poc:{WINDOW_BYTES_SHA256}")
        if str(actual) != WINDOW_DEFINITION_ID:
            raise ValueError("window UUID derivation drifted")
        return self


def accepted_window_identity() -> WindowIdentity:
    return WindowIdentity()


def validate_window_clocks(
    *,
    match_start_ts: str,
    snapshot_as_of_ts: str,
    dependency_clocks: tuple[str, ...],
    dependency_watermark: str,
    valid_from: str,
) -> None:
    """Validate the frozen half-open window, cutoff, and valid-from rules."""

    values = (
        match_start_ts,
        snapshot_as_of_ts,
        *dependency_clocks,
        dependency_watermark,
        valid_from,
    )
    for value in values:
        if not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z",
            value,
        ):
            raise ValueError("clock is not canonical UTC")
    if match_start_ts != SELECTED_MATCH_START_TS or snapshot_as_of_ts != SNAPSHOT_AS_OF_TS:
        raise ValueError("selected match/snapshot substitution")
    start = _instant(WINDOW_START_UTC)
    end = _instant(WINDOW_END_UTC)
    match_start = _instant(match_start_ts)
    cutoff = _instant(FEATURE_CUTOFF_TS)
    if not start <= match_start < end or not match_start < cutoff:
        raise ValueError("match violates half-open window or cutoff")
    if not dependency_clocks or any(_instant(clock) >= cutoff for clock in dependency_clocks):
        raise ValueError("every dependency clock must be strictly before cutoff")
    if dependency_watermark != max(dependency_clocks, key=_instant):
        raise ValueError("dependency watermark is not the strict maximum")
    expected_valid_from = max(snapshot_as_of_ts, dependency_watermark, key=_instant)
    if valid_from != expected_valid_from:
        raise ValueError("valid_from is not max(snapshot, dependency watermark)")


def bounded_season_uuid(source_id: object) -> UUID:
    """Return the sole W04 season UUID; reject all other kinds and values."""

    if type(source_id) is not int or source_id != 181150:
        raise ValueError("only strict JSON integer season source ID 181150 is authorised")
    source_namespace = uuid5(NAMESPACE_URL, SOURCE_NAMESPACE_NAME)
    season_namespace = uuid5(source_namespace, "season")
    season_id = uuid5(season_namespace, "figshare-v5:181150")
    if str(season_id) != "4696aa1f-b512-5d18-af79-33cf031455cf":
        raise ValueError("season UUID derivation drifted")
    return season_id


type AuthorityKind = Literal[
    "FIELD",
    "POSSESSION",
    "SUPPORTED_FEATURE",
    "IDENTITY",
    "SEASON_LINEUP_PRODUCT_BINDING",
]


class AuthorityRow(ContractModel):
    acceptance_id: str
    acceptance_sha256: Sha256
    authority_kind: AuthorityKind
    candidate_id: str
    candidate_sha256: Sha256
    review_id: str
    review_sha256: Sha256

    @model_validator(mode="after")
    def equals_accepted_row(self) -> Self:
        expected = _AUTHORITY_VALUES[self.authority_kind]
        if self.model_dump() != expected:
            raise ValueError("authority row differs from accepted immutable reference")
        return self


_AUTHORITY_VALUES: dict[str, dict[str, str]] = {
    "FIELD": {
        "acceptance_id": "w04-wyscout-field-semantic-acceptance-v2",
        "acceptance_sha256": "beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436",
        "authority_kind": "FIELD",
        "candidate_id": "w04-wyscout-field-registry-v2",
        "candidate_sha256": "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959",
        "review_id": "w04-wyscout-field-semantic-independent-review-v2-R1",
        "review_sha256": "76c4744d302b4c6d86f4d537498695e365f0d3c733211bfafcb1e5c2805c0886",
    },
    "POSSESSION": {
        "acceptance_id": "w04-wyscout-possession-semantic-acceptance-v2",
        "acceptance_sha256": "2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1",
        "authority_kind": "POSSESSION",
        "candidate_id": "w04-wyscout-possession-taxonomy-v2",
        "candidate_sha256": "3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881",
        "review_id": "w04-wyscout-possession-semantic-independent-review-v2-R1",
        "review_sha256": "c1e249c377d11258415cea84e83f0d3742436ebcb7aa640b885c44d245cb1e97",
    },
    "SUPPORTED_FEATURE": {
        "acceptance_id": "w04-wyscout-supported-feature-registry-acceptance-v1",
        "acceptance_sha256": "d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c",
        "authority_kind": "SUPPORTED_FEATURE",
        "candidate_id": "w04-wyscout-supported-count-features-v1",
        "candidate_sha256": FEATURE_SCHEMA_HASH,
        "review_id": "w04-wyscout-supported-feature-registry-independent-review-R1",
        "review_sha256": "a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73",
    },
    "IDENTITY": {
        "acceptance_id": "w04-wyscout-identity-ruleset-acceptance-v1",
        "acceptance_sha256": "37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86",
        "authority_kind": "IDENTITY",
        "candidate_id": "w04-wyscout-identity-ruleset-v1",
        "candidate_sha256": "9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c",
        "review_id": "w04-wyscout-identity-ruleset-independent-review-R1",
        "review_sha256": "62295d6a1da681fbec23285ca6c74124e3ef44fe3962c1472f0523ef46fb2a19",
    },
    "SEASON_LINEUP_PRODUCT_BINDING": {
        "acceptance_id": "w04-wyscout-season-lineup-product-binding-acceptance-v1",
        "acceptance_sha256": "6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e",
        "authority_kind": "SEASON_LINEUP_PRODUCT_BINDING",
        "candidate_id": "w04-wyscout-season-lineup-product-binding-decisions-v1",
        "candidate_sha256": "3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e",
        "review_id": "w04-wyscout-season-lineup-product-binding-independent-review-R1",
        "review_sha256": "3f88335db70609e90f0d02cbbc206752479f5300e196329fc48f07154899cf0f",
    },
}


def accepted_authority_rows() -> tuple[AuthorityRow, ...]:
    return tuple(AuthorityRow.model_validate(value) for value in _AUTHORITY_VALUES.values())


type DependencyKind = Literal["source_manifest", "identity_evidence", "feature_schema"]


class DependencyRow(ContractModel):
    kind: DependencyKind
    dependency_id: CanonicalUuid
    digest: Sha256
    observed_at: UtcInstant
    available_at: UtcInstant

    @model_validator(mode="after")
    def clocks_are_ordered(self) -> Self:
        if _instant(self.observed_at) > _instant(self.available_at):
            raise ValueError("dependency observed_at exceeds available_at")
        return self


_DEPENDENCY_VALUES: tuple[dict[str, str], ...] = (
    {
        "kind": "source_manifest",
        "dependency_id": SOURCE_MANIFEST_ID,
        "digest": SOURCE_MANIFEST_SHA256,
        "observed_at": "2020-01-28T14:24:27Z",
        "available_at": "2020-01-28T14:24:27Z",
    },
    {
        "kind": "identity_evidence",
        "dependency_id": IDENTITY_BUNDLE_ID,
        "digest": IDENTITY_BUNDLE_SHA256,
        "observed_at": "2026-07-31T12:44:27Z",
        "available_at": "2026-07-31T14:15:26Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "32351f4a-4c59-567f-87b5-15364a8d4f47",
        "digest": FEATURE_SCHEMA_HASH,
        "observed_at": "2026-07-31T08:37:00Z",
        "available_at": "2026-07-31T10:15:16Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "342eb513-ad1c-5d65-aea5-abc2d9c14383",
        "digest": "3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881",
        "observed_at": "2026-07-30T22:14:21Z",
        "available_at": "2026-07-31T08:28:40Z",
    },
    {
        "kind": "feature_schema",
        "dependency_id": "f65e539c-0021-53b6-9b20-27bc2aefad3d",
        "digest": "93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959",
        "observed_at": "2026-07-30T20:22:17Z",
        "available_at": "2026-07-30T21:21:23Z",
    },
)


def accepted_dependency_rows() -> tuple[DependencyRow, ...]:
    return tuple(DependencyRow.model_validate(value) for value in _DEPENDENCY_VALUES)


def accepted_dependency_lineage_hash() -> str:
    return sha256_json(
        {
            "dependencies": [row.model_dump(mode="json") for row in accepted_dependency_rows()],
            "source_completion_index_sha256": SOURCE_COMPLETION_INDEX_SHA256,
        }
    )


def _accepted_authority_clocks() -> list[dict[str, str]]:
    values = (
        ("FIELD", "2026-07-30T20:22:17Z", "2026-07-30T21:15:45Z", "2026-07-30T21:21:23Z"),
        ("POSSESSION", "2026-07-30T22:14:21Z", "2026-07-31T08:24:02Z", "2026-07-31T08:28:40Z"),
        (
            "SUPPORTED_FEATURE",
            "2026-07-31T08:37:00Z",
            "2026-07-31T10:07:30Z",
            "2026-07-31T10:15:16Z",
        ),
        ("IDENTITY", "2026-07-31T12:44:27Z", "2026-07-31T14:11:16Z", "2026-07-31T14:15:26Z"),
    )
    return [
        {
            "accepted_at": accepted,
            "authority_kind": kind,
            "decided_at": decided,
            "reviewed_at": reviewed,
        }
        for kind, decided, reviewed, accepted in values
    ]


def _accepted_classification() -> dict[str, object]:
    return {
        "attribution_required": True,
        "attribution_text": (
            "Data source: Pappalardo et al., Soccer match event dataset, supplied by "
            "Wyscout, figshare collection v5, licensed CC BY 4.0."
        ),
        "derived_data_allowed": True,
        "export_allowed": False,
        "internal_review_allowed": True,
        "use_class": "restricted",
    }


def code_manifest_id_for_digest(digest: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("code manifest digest must be lowercase SHA-256")
    namespace = uuid5(NAMESPACE_URL, CODE_MANIFEST_NAMESPACE_NAME)
    return str(uuid5(namespace, f"post_integration_code_environment_manifest:{digest}"))


class _ProjectionCommon(ContractModel):
    authority_rows: tuple[AuthorityRow, ...]
    code_manifest_id: UuidV5
    code_manifest_sha256: Sha256
    dependency_rows: tuple[DependencyRow, ...]
    dependency_watermark: Literal["2026-07-31T14:15:26Z"] = DEPENDENCY_WATERMARK
    environment_digest: Sha256
    feature_cutoff_ts: Literal["2026-08-01T00:00:00Z"] = FEATURE_CUTOFF_TS
    feature_schema_hash: Literal[
        "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
    ] = FEATURE_SCHEMA_HASH
    identity_bundle_id: Literal["31638732-5b25-57db-9eb4-8e943a47a387"] = IDENTITY_BUNDLE_ID
    identity_bundle_sha256: Literal[
        "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"
    ] = IDENTITY_BUNDLE_SHA256
    local_resource_digest: Sha256
    product_contract_digest: Sha256
    role_context_id: Literal["3a17850f-5ac4-5ad8-ac9a-b753f10bdf77"] = ROLE_CONTEXT_ID
    role_context_state: Literal["neutral_unscoped"] = ROLE_CONTEXT_STATE
    role_context_version: Literal["w04-neutral-role-context-v1"] = ROLE_CONTEXT_VERSION
    schema_bundle_digest: Sha256

    def _validate_common(self) -> None:
        if self.authority_rows != accepted_authority_rows():
            raise ValueError("authority rows must be the exact ordered five-row authority")
        if self.dependency_rows != accepted_dependency_rows():
            raise ValueError("dependency rows must be the exact accepted canonical five")
        if self.code_manifest_id != code_manifest_id_for_digest(self.code_manifest_sha256):
            raise ValueError("code manifest UUIDv5 does not bind its digest")
        if self.product_contract_digest == PRODUCT_CONTRACT_V1_SHA256:
            raise ValueError("placeholder v1 product-contract digest is forbidden")
        if self.schema_bundle_digest == SCHEMA_BUNDLE_V1_SHA256:
            raise ValueError("placeholder v1 schema-bundle digest is forbidden")


class PreBuildProjection(_ProjectionCommon):
    schema_version: Literal["w04-wyscout-pre-build-projection-v1"] = PROJECTION_SCHEMA_VERSION
    selected_lock_closure_digest: Sha256
    source_manifest_id: Literal["4e16bdb5-afe7-5601-88ad-adc124cfce3b"] = SOURCE_MANIFEST_ID
    source_manifest_sha256: Literal[
        "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
    ] = SOURCE_MANIFEST_SHA256
    tenant_club_id: None = None
    tenant_id: Literal["65a43912-d412-5ff9-a364-7f84d1ad6c5d"] = TENANT_ID
    window_definition_id: Literal["a0af8d56-e41d-5467-b46e-82887c4861e0"] = WINDOW_DEFINITION_ID
    window_end_utc: Literal["2017-08-12T00:00:00Z"] = WINDOW_END_UTC
    window_start_utc: Literal["2017-08-11T00:00:00Z"] = WINDOW_START_UTC

    @model_validator(mode="after")
    def exact_projection(self) -> Self:
        self._validate_common()
        if tuple(type(self).model_fields) != PRE_BUILD_PROJECTION_KEYS:
            raise ValueError("pre-build projection key drift")
        return self


class RebuildInvocation(ContractModel):
    authority_rows: tuple[AuthorityRow, ...]
    build_id: Sha256
    code_manifest_id: UuidV5
    code_manifest_sha256: Sha256
    dependency_rows: tuple[DependencyRow, ...]
    dependency_watermark: Literal["2026-07-31T14:15:26Z"] = DEPENDENCY_WATERMARK
    environment_digest: Sha256
    feature_cutoff_ts: Literal["2026-08-01T00:00:00Z"] = FEATURE_CUTOFF_TS
    feature_schema_hash: Literal[
        "49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f"
    ] = FEATURE_SCHEMA_HASH
    identity_bundle_id: Literal["31638732-5b25-57db-9eb4-8e943a47a387"] = IDENTITY_BUNDLE_ID
    identity_bundle_sha256: Literal[
        "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"
    ] = IDENTITY_BUNDLE_SHA256
    local_resource_digest: Sha256
    product_contract_digest: Sha256
    role_context_id: Literal["3a17850f-5ac4-5ad8-ac9a-b753f10bdf77"] = ROLE_CONTEXT_ID
    role_context_state: Literal["neutral_unscoped"] = ROLE_CONTEXT_STATE
    role_context_version: Literal["w04-neutral-role-context-v1"] = ROLE_CONTEXT_VERSION
    schema_bundle_digest: Sha256
    selected_lock_closure_digest: Sha256
    source_manifest_id: Literal["4e16bdb5-afe7-5601-88ad-adc124cfce3b"] = SOURCE_MANIFEST_ID
    source_manifest_sha256: Literal[
        "8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd"
    ] = SOURCE_MANIFEST_SHA256
    tenant_club_id: None = None
    tenant_id: Literal["65a43912-d412-5ff9-a364-7f84d1ad6c5d"] = TENANT_ID
    window_definition_id: Literal["a0af8d56-e41d-5467-b46e-82887c4861e0"] = WINDOW_DEFINITION_ID
    window_end_utc: Literal["2017-08-12T00:00:00Z"] = WINDOW_END_UTC
    window_start_utc: Literal["2017-08-11T00:00:00Z"] = WINDOW_START_UTC

    @model_validator(mode="after")
    def exact_invocation(self) -> Self:
        if self.authority_rows != accepted_authority_rows():
            raise ValueError("authority rows must be the exact ordered five-row authority")
        if self.dependency_rows != accepted_dependency_rows():
            raise ValueError("dependency rows must be the exact accepted canonical five")
        if self.code_manifest_id != code_manifest_id_for_digest(self.code_manifest_sha256):
            raise ValueError("code manifest UUIDv5 does not bind its digest")
        if self.product_contract_digest == PRODUCT_CONTRACT_V1_SHA256:
            raise ValueError("placeholder v1 product-contract digest is forbidden")
        if self.schema_bundle_digest == SCHEMA_BUNDLE_V1_SHA256:
            raise ValueError("placeholder v1 schema-bundle digest is forbidden")
        if tuple(type(self).model_fields) != POST_HASH_INVOCATION_KEYS:
            raise ValueError("post-hash invocation key drift")
        projection = projection_from_invocation_unchecked(self)
        if build_id_for_projection(projection) != self.build_id:
            raise ValueError("invocation build_id does not reproduce the sole projection hash")
        return self


def build_id_for_projection(projection: PreBuildProjection) -> str:
    return hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


def invocation_from_projection(projection: PreBuildProjection) -> RebuildInvocation:
    values = projection.model_dump()
    del values["schema_version"]
    values["build_id"] = build_id_for_projection(projection)
    return RebuildInvocation.model_validate(values)


def projection_from_invocation_unchecked(invocation: RebuildInvocation) -> PreBuildProjection:
    values = invocation.model_dump()
    del values["build_id"]
    values["schema_version"] = PROJECTION_SCHEMA_VERSION
    return PreBuildProjection.model_validate(values)


def projection_from_invocation(invocation: RebuildInvocation) -> PreBuildProjection:
    projection = projection_from_invocation_unchecked(invocation)
    if invocation_from_projection(projection) != invocation:
        raise ValueError("post-hash invocation is not the strict inverse")
    return projection


type LayerName = Literal["BRONZE", "SILVER", "GOLD"]


@dataclass(frozen=True, slots=True)
class GoldProductReadback:
    """Exact logical Gold content retained while schema authority is unavailable."""

    contract_row_bytes: tuple[bytes, ...]
    physical_bytes: bytes
    temporal_proof_bytes: bytes


class GoldSchemaAuthorityUnavailableError(RuntimeError):
    """Receipt completion is unavailable until the accepted Gold schema exists."""


class TemporalBoundaryReceipt(ContractModel):
    build_id: Sha256
    checked_at: UtcInstant
    dependency_lineage_hash: Sha256
    feature_cutoff_ts: Literal["2026-08-01T00:00:00Z"] = FEATURE_CUTOFF_TS
    gold_manifest_relative_path: RelativePath
    gold_manifest_sha256: Sha256
    gold_product_physical_sha256: Sha256
    gold_product_relative_path: RelativePath
    gold_product_semantic_sha256: Sha256
    gold_relative_path_sha256: Sha256
    row_count: Literal[1] = 1
    run_id: UuidV4
    schema_version: Literal["w04-wyscout-temporal-boundary-receipt-v1"] = (
        "w04-wyscout-temporal-boundary-receipt-v1"
    )
    temporal_proof_sha256: Sha256
    verification_state: Literal["STRICT_BEFORE_CUTOFF_PASS"] = "STRICT_BEFORE_CUTOFF_PASS"

    @model_validator(mode="after")
    def exact_paths(self) -> Self:
        _validate_relative_path(self.gold_manifest_relative_path)
        _validate_relative_path(self.gold_product_relative_path)
        if self.gold_manifest_relative_path != gold_manifest_path(self.build_id):
            raise ValueError("boundary Gold manifest path substitution")
        if not _gold_product_pattern(self.build_id).fullmatch(self.gold_product_relative_path):
            raise ValueError("boundary Gold product path substitution")
        direct = hashlib.sha256(self.gold_product_relative_path.encode()).hexdigest()
        if self.gold_relative_path_sha256 != direct:
            raise ValueError("Gold relative path direct digest mismatch")
        return self


class BoundaryReceiptSummary(ContractModel):
    gold_relative_path: RelativePath
    relative_path: RelativePath
    sha256: Sha256
    size_bytes: Annotated[int, Field(strict=True, ge=1, le=16_777_216)]


class RebuildReceiptSummary(ContractModel):
    relative_path: RelativePath
    sha256: Sha256
    size_bytes: Annotated[int, Field(strict=True, ge=1, le=16_777_216)]


class LayerManifestSummary(ContractModel):
    layer: LayerName
    manifest_relative_path: RelativePath
    manifest_sha256: Sha256
    manifest_size_bytes: Annotated[int, Field(strict=True, ge=1, le=16_777_216)]
    semantic_sha256: Sha256


class RebuildInvocationReceipt(ContractModel):
    boundary_receipts: tuple[BoundaryReceiptSummary, ...]
    build_id: Sha256
    completed_at: UtcInstant
    layer_manifests: tuple[LayerManifestSummary, ...]
    rebuild_invocation: RebuildInvocation
    result_state: Literal["COMPLETE"] = "COMPLETE"
    run_id: UuidV4
    schema_version: Literal["w04-wyscout-rebuild-invocation-receipt-v1"] = (
        "w04-wyscout-rebuild-invocation-receipt-v1"
    )
    started_at: UtcInstant

    @model_validator(mode="after")
    def exact_receipt(self) -> Self:
        if self.build_id != self.rebuild_invocation.build_id:
            raise ValueError("receipt build differs from invocation")
        if _instant(self.started_at) > _instant(self.completed_at):
            raise ValueError("receipt completed before it started")
        if tuple(row.layer for row in self.layer_manifests) != ("BRONZE", "SILVER", "GOLD"):
            raise ValueError("layer summaries must be exactly Bronze, Silver, Gold")
        for row in self.layer_manifests:
            if row.manifest_relative_path != layer_manifest_path(row.layer, self.build_id):
                raise ValueError("layer manifest summary path substitution")
        if len(self.boundary_receipts) != 1:
            raise ValueError("W04 POC requires exactly one boundary summary")
        for boundary_row in self.boundary_receipts:
            _validate_relative_path(boundary_row.gold_relative_path)
            _validate_relative_path(boundary_row.relative_path)
            expected = boundary_receipt_path(
                self.build_id, self.run_id, boundary_row.gold_relative_path
            )
            if boundary_row.relative_path != expected:
                raise ValueError("boundary summary path substitution")
        return self


def gold_manifest_path(build_id: str) -> str:
    return f"data/manifests/wyscout/v5/gold/{build_id}.manifest.json"


def layer_manifest_path(layer: LayerName, build_id: str) -> str:
    return f"data/manifests/wyscout/v5/{layer.lower()}/{build_id}.manifest.json"


def _gold_product_pattern(build_id: str) -> re.Pattern[str]:
    return re.compile(
        rf"data/working/wyscout/v5/gold/build_id={build_id}/player-window/"
        rf"competition_id={COMPETITION_ID}/"
        rf"window_definition_id={WINDOW_DEFINITION_ID}/"
        rf"window_start_utc=20170811T000000000000Z/"
        rf"window_end_utc=20170812T000000000000Z/"
        rf"feature_cutoff_ts=20260801T000000000000Z/part-00000\.parquet"
    )


def boundary_receipt_path(build_id: str, run_id: str, gold_relative_path: str) -> str:
    path_digest = hashlib.sha256(gold_relative_path.encode("utf-8")).hexdigest()
    return (
        f"runs/w04/wyscout-rebuild/{build_id}/{run_id}/boundary/"
        f"{path_digest}.temporal-boundary-receipt.json"
    )


def rebuild_receipt_path(build_id: str, run_id: str) -> str:
    return f"runs/w04/wyscout-rebuild/{build_id}/{run_id}.receipt.json"


def validate_receipt_closure(
    receipt: RebuildInvocationReceipt,
    boundary_population: tuple[tuple[TemporalBoundaryReceipt, bytes], ...],
    manifest_population: tuple[bytes, ...],
    gold_product_readback: GoldProductReadback,
) -> None:
    """Validate composed three-manifest, parent, Gold, boundary, and clock closure.

    Manifest, Gold and temporal inputs are revalidated from their canonical content.
    The function reproduces physical and R4 receipt bindings without defining or
    substituting a second schema or trusting caller-supplied digest claims.
    """

    if len(manifest_population) != 3:
        raise ValueError("manifest population must be exactly Bronze, Silver, Gold")
    parsed_manifests: list[dict[str, object]] = []
    for summary, supplied_manifest in zip(
        receipt.layer_manifests, manifest_population, strict=True
    ):
        physical_bytes = supplied_manifest
        readback = load_canonical_json(physical_bytes, terminal_lf=True)
        if type(readback) is not dict:
            raise TypeError("LayerManifest physical readback must be an object")
        from scouting.contracts.wyscout_data import LayerManifest

        typed_manifest = LayerManifest.model_validate_json(physical_bytes[:-1], strict=True)
        parsed_manifest = cast(dict[str, object], readback)
        if typed_manifest.model_dump(mode="json") != parsed_manifest:
            raise ValueError("typed LayerManifest dump differs from canonical physical readback")
        if summary.manifest_sha256 != hashlib.sha256(physical_bytes).hexdigest():
            raise ValueError("layer manifest physical digest mismatch")
        if summary.manifest_size_bytes != len(physical_bytes):
            raise ValueError("layer manifest physical size mismatch")
        expected_path = layer_manifest_path(summary.layer, receipt.build_id)
        if (
            parsed_manifest.get("manifest_schema_version") != "w04-wyscout-layer-manifest-v1"
            or parsed_manifest.get("construction_authority_state") != "semantic_only_unchecked"
            or parsed_manifest.get("layer") != summary.layer
            or parsed_manifest.get("build_id") != receipt.build_id
            or parsed_manifest.get("complete") is not True
            or parsed_manifest.get("manifest_path")
            != {"path_role": f"{summary.layer}_MANIFEST", "relative_path": expected_path}
        ):
            raise ValueError("layer manifest schema/layer/build/path/completion substitution")
        expected_lineage_hash = accepted_dependency_lineage_hash()
        expected_lineage = {
            "dependencies": [row.model_dump(mode="json") for row in accepted_dependency_rows()],
            "lineage_hash": expected_lineage_hash,
        }
        if (
            parsed_manifest.get("source_manifest_id") != SOURCE_MANIFEST_ID
            or parsed_manifest.get("source_manifest_sha256") != SOURCE_MANIFEST_SHA256
            or parsed_manifest.get("source_completion_index_sha256")
            != SOURCE_COMPLETION_INDEX_SHA256
            or parsed_manifest.get("tenant_context") != {"club_id": None, "tenant_id": TENANT_ID}
            or parsed_manifest.get("classification") != _accepted_classification()
            or parsed_manifest.get("source_available_at") != "2020-01-28T14:24:27Z"
            or parsed_manifest.get("source_acquired_at") != "2026-07-29T15:51:08.598589Z"
            or parsed_manifest.get("authority_clocks") != _accepted_authority_clocks()
            or parsed_manifest.get("feature_schema_hash") != FEATURE_SCHEMA_HASH
            or parsed_manifest.get("dependency_lineage_hash") != expected_lineage_hash
            or parsed_manifest.get("dependency_lineage") != expected_lineage
        ):
            raise ValueError("layer manifest frozen authority/lineage substitution")
        validate_layer_manifest_semantic_binding(summary, parsed_manifest)
        parsed_manifests.append(parsed_manifest)

    bronze, silver, gold = parsed_manifests
    _validate_manifest_parents(bronze, (), receipt.layer_manifests, receipt.build_id)
    _validate_manifest_parents(silver, ("BRONZE",), receipt.layer_manifests, receipt.build_id)
    _validate_manifest_parents(gold, ("SILVER",), receipt.layer_manifests, receipt.build_id)

    gold_entries = gold.get("entries")
    if type(gold_entries) is not list or len(gold_entries) != 1:
        raise ValueError("validated Gold manifest must contain exactly one entry")
    gold_entry = gold_entries[0]
    if type(gold_entry) is not dict or gold_entry.get("complete") is not True:
        raise ValueError("Gold population entry must be a complete parsed object")
    gold_path_value = gold_entry.get("path")
    if type(gold_path_value) is not dict or tuple(gold_path_value) != (
        "path_role",
        "relative_path",
    ):
        raise ValueError("Gold entry path must be the exact closed two-key path object")
    if gold_path_value.get("path_role") != "GOLD_PLAYER_WINDOW":
        raise ValueError("Gold entry role substitution")
    gold_relative_path = gold_path_value.get("relative_path")
    if type(gold_relative_path) is not str or not _gold_product_pattern(receipt.build_id).fullmatch(
        gold_relative_path
    ):
        raise ValueError("Gold manifest entry path substitution")
    (
        dependency_lineage_hash,
        gold_product_physical_sha256,
        gold_product_semantic_sha256,
        gold_product_size_bytes,
        temporal_proof_sha256,
    ) = _validate_gold_product_readback(
        gold_product_readback,
        build_id=receipt.build_id,
        parent_paths=cast(tuple[str, ...], gold_entry.get("ordered_parent_paths")),
    )
    if (
        gold_entry.get("physical_sha256") != gold_product_physical_sha256
        or gold_entry.get("semantic_sha256") != gold_product_semantic_sha256
        or gold_entry.get("size_bytes") != gold_product_size_bytes
        or gold_entry.get("row_count") != 1
    ):
        raise ValueError("Gold manifest entry physical/semantic/row-count substitution")
    if dependency_lineage_hash != accepted_dependency_lineage_hash():
        raise ValueError("receipt closure dependency lineage differs from frozen manifest")

    if len(boundary_population) != len(receipt.boundary_receipts):
        raise ValueError("boundary population cardinality differs")
    if tuple(row.gold_relative_path for row in receipt.boundary_receipts) != (gold_relative_path,):
        raise ValueError("boundary summaries differ from exact Gold manifest sequence")
    for boundary_summary, supplied in zip(
        receipt.boundary_receipts, boundary_population, strict=True
    ):
        boundary, physical_bytes = supplied
        if physical_bytes != canonical_json_bytes(boundary, terminal_lf=True):
            raise ValueError("boundary receipt bytes are not exact canonical readback")
        if boundary_summary.sha256 != hashlib.sha256(physical_bytes).hexdigest():
            raise ValueError("boundary receipt physical digest mismatch")
        if boundary_summary.size_bytes != len(physical_bytes):
            raise ValueError("boundary receipt physical size mismatch")
        if boundary_summary.gold_relative_path != boundary.gold_product_relative_path:
            raise ValueError("boundary summary Gold population mismatch")
        expected_path = boundary_receipt_path(
            receipt.build_id, receipt.run_id, boundary.gold_product_relative_path
        )
        if boundary_summary.relative_path != expected_path:
            raise ValueError("boundary summary/readback path mismatch")
        if boundary.build_id != receipt.build_id or boundary.run_id != receipt.run_id:
            raise ValueError("boundary build/run substitution")
        gold_summary = receipt.layer_manifests[2]
        if (
            boundary.gold_manifest_relative_path != gold_summary.manifest_relative_path
            or boundary.gold_manifest_sha256 != gold_summary.manifest_sha256
        ):
            raise ValueError("boundary Gold manifest substitution")
        if boundary.dependency_lineage_hash != dependency_lineage_hash:
            raise ValueError("boundary dependency-lineage substitution")
        if boundary.gold_product_physical_sha256 != gold_product_physical_sha256:
            raise ValueError("boundary Gold product physical digest substitution")
        if boundary.gold_product_semantic_sha256 != gold_product_semantic_sha256:
            raise ValueError("boundary Gold product semantic digest substitution")
        if boundary.temporal_proof_sha256 != temporal_proof_sha256:
            raise ValueError("boundary temporal-proof substitution")
        if not (
            _instant(receipt.started_at)
            <= _instant(boundary.checked_at)
            <= _instant(receipt.completed_at)
        ):
            raise ValueError("boundary check lies outside invocation interval")
    raise GoldSchemaAuthorityUnavailableError(
        "accepted GOLD_PLAYER_WINDOW schema authority is not yet available"
    )


def _validate_gold_product_readback(
    readback: GoldProductReadback,
    *,
    build_id: str,
    parent_paths: tuple[str, ...],
) -> tuple[str, str, str, int, str]:
    """Revalidate logical Gold content and stop before unavailable schema use."""

    if type(readback) is not GoldProductReadback:
        raise TypeError("Gold content must use the exact content-bearing readback input")
    if len(readback.contract_row_bytes) != 1:
        raise ValueError("Gold readback must contain exactly one contract row")
    row_bytes = readback.contract_row_bytes[0]
    if not row_bytes.endswith(b"\n") or row_bytes[:-1].endswith(b"\n"):
        raise ValueError("Gold contract row requires exactly one terminal LF")
    row_body = row_bytes[:-1]
    if load_canonical_json(row_body) is None:
        raise AssertionError("canonical Gold row unexpectedly decoded to null")
    if not isinstance(readback.physical_bytes, bytes) or not readback.physical_bytes:
        raise ValueError("Gold Parquet readback must be positive nonempty bytes")

    from scouting.contracts.wyscout_data import (
        GoldPlayerWindow,
        W04SemanticTemporalProof,
    )

    gold = GoldPlayerWindow.model_validate_json(row_body, strict=True)
    if canonical_json_bytes(gold) + b"\n" != row_bytes:
        raise ValueError("typed Gold dump differs from canonical contract-row readback")
    proof = W04SemanticTemporalProof.model_validate_json(readback.temporal_proof_bytes, strict=True)
    if canonical_json_bytes(proof) != readback.temporal_proof_bytes:
        raise ValueError("typed temporal-proof dump differs from canonical readback")
    if gold.temporal_proof != proof:
        raise ValueError("Gold row temporal proof differs from supplied proof content")
    expected_season_id = str(bounded_season_uuid(181150))
    if (
        gold.build_id != build_id
        or str(gold.competition_id) != COMPETITION_ID
        or str(gold.season_id) != expected_season_id
        or str(gold.window_definition_id) != WINDOW_DEFINITION_ID
        or gold.window_start_utc.isoformat().replace("+00:00", "Z") != WINDOW_START_UTC
        or gold.window_end_utc.isoformat().replace("+00:00", "Z") != WINDOW_END_UTC
        or gold.feature_cutoff_ts.isoformat().replace("+00:00", "Z") != FEATURE_CUTOFF_TS
        or proof.snapshot_as_of_ts.isoformat().replace("+00:00", "Z") != SNAPSHOT_AS_OF_TS
        or tuple(str(fact.match_id) for fact in gold.contributing_player_match_facts) != (MATCH_ID,)
        or tuple(
            fact.match_start_utc.isoformat().replace("+00:00", "Z")
            for fact in gold.contributing_player_match_facts
        )
        != (SELECTED_MATCH_START_TS,)
    ):
        raise ValueError("Gold readback differs from the exact W04 one-match window")
    raise GoldSchemaAuthorityUnavailableError(
        "accepted GOLD_PLAYER_WINDOW projection descriptor is not yet available"
    )


def _validate_manifest_parents(
    manifest: dict[str, object],
    expected_layers: tuple[LayerName, ...],
    summaries: tuple[LayerManifestSummary, ...],
    build_id: str,
) -> None:
    parents = manifest.get("parent_layer_manifests")
    if type(parents) is not list or len(parents) != len(expected_layers):
        raise ValueError("layer parent cardinality substitution")
    summaries_by_layer = {summary.layer: summary for summary in summaries}
    expected = [
        {
            "build_id": build_id,
            "layer": layer,
            "relative_path": summaries_by_layer[layer].manifest_relative_path,
            "sha256": summaries_by_layer[layer].manifest_sha256,
        }
        for layer in expected_layers
    ]
    if parents != expected:
        raise ValueError("layer parent physical identity/order substitution")


type ChildRole = Literal["PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"]


class EntrypointSourceResult(ContractModel):
    descriptor_cloexec: Literal[False] = False
    descriptor_inheritable: Literal[True] = True
    descriptor_number: Annotated[int, Field(strict=True, ge=3, le=2_147_483_647)]
    device: JsonInteger
    inode: StrictPositiveInt
    link_count: Literal[1] = 1
    mode: Literal[420] = 420
    offset_after: Literal[0] = 0
    offset_before: Literal[0] = 0
    relative_path: RelativePath
    role: ChildRole
    sha256: Sha256
    size_bytes: Annotated[int, Field(strict=True, ge=1, le=16_777_216)]
    source_eof: Literal[True] = True

    @model_validator(mode="after")
    def exact_role_path(self) -> Self:
        expected = ADMISSION_ARGV[-1] if self.role == "PRE_BUILD_ADMISSION" else REBUILD_ARGV[-1]
        if self.relative_path != expected:
            raise ValueError("entrypoint path differs from selected child role")
        return self


type ComponentKey = Literal[
    "child_result_contract_digest",
    "editable_root_digest",
    "environment_values_digest",
    "executable_census_digest",
    "extracted_runtime_digest",
    "installed_record_runtime_digest",
    "interpreter_digest",
    "local_launcher_control_digest",
    "local_resource_digest",
    "lock_inputs_digest",
    "process_launch_contract_digest",
    "pyc_policy_source_map_digest",
    "selected_lock_closure_digest",
    "selector",
    "selector_bootstrap_digest",
    "stdlib_digest",
    "uv_physical_sha256",
    "uv_version",
    "venv_bootstrap_digest",
    "wheel_declaration_digest",
]


class ComponentProofResult(ContractModel):
    component_key: ComponentKey
    evidence_row_count: Annotated[int, Field(strict=True, ge=1, le=10_000_000)]
    value_json_sha256: Sha256


def _decode_admission_manifest(
    encoded: str, expected_sha256: str
) -> tuple[dict[str, object], bytes]:
    padded = encoded + "=" * (-len(encoded) % 4)
    try:
        manifest_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as exc:
        raise ValueError("invalid unpadded base64url manifest") from exc
    if not 1 <= len(manifest_bytes) <= 12_000_000:
        raise ValueError("decoded manifest size outside accepted range")
    if base64.urlsafe_b64encode(manifest_bytes).decode("ascii").rstrip("=") != encoded:
        raise ValueError("manifest base64url is not canonical")
    if hashlib.sha256(manifest_bytes).hexdigest() != expected_sha256:
        raise ValueError("decoded manifest digest mismatch")
    decoded = load_canonical_json(manifest_bytes)
    if type(decoded) is not dict:
        raise ValueError("decoded admission manifest must be an object")
    manifest = cast(dict[str, object], decoded)
    if tuple(manifest) != _STABLE_MANIFEST_KEYS:
        raise ValueError("decoded stable manifest field roster differs from exact v16")
    return manifest, manifest_bytes


def _validated_environment_components(manifest: dict[str, object]) -> dict[str, object]:
    components = {key: manifest[key] for key in COMPONENT_KEYS}
    for key in _DIGEST_COMPONENT_KEYS:
        value = components[key]
        if type(value) is not str or re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise ValueError(f"stable manifest component {key} is not lowercase SHA-256")
    if components["uv_version"] != "uv 0.9.21 (Homebrew 2025-12-30)":
        raise ValueError("stable manifest uv_version differs from accepted exact version")
    selector = components["selector"]
    if type(selector) is not dict or not selector:
        raise ValueError("stable manifest selector must be a nonempty closed canonical object")
    canonical_json_bytes(selector)
    return components


class PreBuildAdmissionResult(ContractModel):
    admission_prefix_relative_path: RelativePath
    admission_run_id: UuidV4
    canonical_manifest_bytes_b64u: Base64Url
    canonical_manifest_sha256: Sha256
    component_proofs: tuple[ComponentProofResult, ...]
    component_proofs_sha256: Sha256
    environment_digest: Sha256
    manifest_schema_version: Literal["w04-code-environment-admission-v16"] = (
        "w04-code-environment-admission-v16"
    )
    repository_code_sha256: Sha256

    @model_validator(mode="after")
    def exact_admission_result(self) -> Self:
        expected_path = (
            "data/working/wyscout/v5/.staging/admission/"
            f"admission_run_id={self.admission_run_id}/runtime-pycache"
        )
        if self.admission_prefix_relative_path != expected_path:
            raise ValueError("admission prefix substitution")
        if tuple(row.component_key for row in self.component_proofs) != COMPONENT_KEYS:
            raise ValueError("component proofs must be the exact ordered twenty")
        proof_values = [row.model_dump(mode="json") for row in self.component_proofs]
        if self.component_proofs_sha256 != sha256_json(proof_values):
            raise ValueError("component proof digest mismatch")
        manifest, _ = _decode_admission_manifest(
            self.canonical_manifest_bytes_b64u, self.canonical_manifest_sha256
        )
        components = _validated_environment_components(manifest)
        required = {
            "schema_version": self.manifest_schema_version,
            "repository_code_sha256": self.repository_code_sha256,
            "environment_digest": self.environment_digest,
        }
        if any(manifest.get(key) != value for key, value in required.items()):
            raise ValueError("decoded manifest/result binding mismatch")
        if self.environment_digest != sha256_json(components):
            raise ValueError("environment digest does not bind the exact twenty components")
        for proof, key in zip(self.component_proofs, COMPONENT_KEYS, strict=True):
            if proof.value_json_sha256 != sha256_json(components[key]):
                raise ValueError(f"component proof does not bind decoded value: {key}")
        return self


def validate_admission_component_authority(
    result: PreBuildAdmissionResult,
    expected_components: dict[str, object],
    expected_evidence_rows: tuple[tuple[str, int], ...],
) -> None:
    """Compare admission output with independently retained components/counts."""

    if tuple(expected_components) != COMPONENT_KEYS:
        raise ValueError("expected component authority must contain the ordered exact twenty")
    _validated_environment_components(expected_components)
    manifest, _ = _decode_admission_manifest(
        result.canonical_manifest_bytes_b64u, result.canonical_manifest_sha256
    )
    actual_components = _validated_environment_components(manifest)
    if actual_components != expected_components:
        raise ValueError("decoded stable components differ from independent authority")
    if tuple(key for key, _ in expected_evidence_rows) != COMPONENT_KEYS:
        raise ValueError("expected evidence rows must use the ordered exact twenty keys")
    expected_counts = tuple(count for _, count in expected_evidence_rows)
    if any(type(count) is not int or not 1 <= count <= 10_000_000 for count in expected_counts):
        raise ValueError("expected evidence counts must be strict bounded positive integers")
    if tuple(row.evidence_row_count for row in result.component_proofs) != expected_counts:
        raise ValueError("component proof counts differ from independent recount")


class RuntimeSubsetObservation(ContractModel):
    """One normalized, RECORD-owned terminal runtime observation."""

    observation_kind: Literal[
        "MODULE_SOURCE", "NATIVE_EXTENSION", "NAMESPACE_LOCATION", "SITE_SHARED_IMAGE"
    ]
    owner_name: Annotated[
        str,
        StringConstraints(
            strict=True,
            min_length=1,
            max_length=256,
            pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        ),
    ]
    owner_version: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=512)]
    site_relative_path: RelativePath
    subject_name: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=1024)]

    @model_validator(mode="after")
    def exact_runtime_observation(self) -> Self:
        owner_version = self.owner_version
        path = self.site_relative_path
        kind = self.observation_kind
        subject_name = self.subject_name
        for value in (owner_version, path, subject_name):
            if not is_normalized("NFC", value) or any(ord(character) < 0x20 for character in value):
                raise ValueError("runtime observation strings must be NFC without controls")
        if (
            path.startswith("/")
            or path.endswith("/")
            or "\\" in path
            or any(part in {"", ".", ".."} for part in path.split("/"))
            or path.lower().endswith((".pyc", ".pyo"))
        ):
            raise ValueError("runtime observation site path is unsafe")
        if kind == "SITE_SHARED_IMAGE":
            if subject_name != "DYLD_IMAGE":
                raise ValueError("site shared images require the DYLD_IMAGE subject")
        elif (
            re.fullmatch(
                r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*",
                subject_name,
            )
            is None
        ):
            raise ValueError("runtime module subject is not a strict sys.modules key")
        return self


class FinalRecheckResult(ContractModel):
    build_id: Sha256
    child_environment_sha256: Sha256
    entrypoint_descriptor_match: Literal[True] = True
    entrypoint_sha256: Sha256
    environment_digest: Sha256
    in_place_pyc_unchanged: Literal[True] = True
    layer_manifest_set_sha256: Sha256
    rebuild_prefix_empty: Literal[True] = True
    rebuild_receipt_sha256: Sha256
    repository_code_sha256: Sha256
    repository_pyc_inventory_sha256: Sha256
    resource_digest: Sha256
    run_id: UuidV4
    runtime_subset_digest: Sha256
    runtime_subset_rows: tuple[RuntimeSubsetObservation, ...]
    schema_version: Literal["w04-rebuild-final-recheck-v2"] = "w04-rebuild-final-recheck-v2"
    selected_prefix_role: Literal["POST_BUILD_ID_REBUILD"] = "POST_BUILD_ID_REBUILD"
    site_pyc_inventory_sha256: Sha256

    @model_validator(mode="after")
    def exact_runtime_subset(self) -> Self:
        rows = self.runtime_subset_rows
        digest = self.runtime_subset_digest
        if not 1 <= len(rows) <= 100_000:
            raise ValueError("runtime subset must contain one to 100000 observations")
        row_values = [row.model_dump(mode="json") for row in rows]
        row_bytes = [canonical_json_bytes(row) for row in row_values]
        if row_bytes != sorted(row_bytes) or len(set(row_bytes)) != len(row_bytes):
            raise ValueError("runtime subset rows must be uniquely canonical-byte sorted")
        owners = {(row.owner_name, row.owner_version) for row in rows}
        if not owners:
            raise ValueError("runtime subset owner projection must be nonempty")
        expected = sha256_json(
            {"algorithm": "w04-normalized-runtime-subset-observations-v1", "rows": row_values}
        )
        if digest != expected:
            raise ValueError("runtime subset digest differs from normalized observations")
        return self


class PostBuildIdRebuildResult(ContractModel):
    build_id: Sha256
    final_recheck: FinalRecheckResult
    layer_manifests: tuple[LayerManifestSummary, ...]
    rebuild_prefix_relative_path: RelativePath
    rebuild_receipt: RebuildReceiptSummary
    run_id: UuidV4

    @model_validator(mode="after")
    def exact_rebuild_result(self) -> Self:
        expected_prefix = (
            f"data/working/wyscout/v5/.staging/{self.build_id}/{self.run_id}/runtime-pycache"
        )
        if self.rebuild_prefix_relative_path != expected_prefix:
            raise ValueError("rebuild prefix substitution")
        if self.rebuild_receipt.relative_path != rebuild_receipt_path(self.build_id, self.run_id):
            raise ValueError("rebuild receipt path substitution")
        if tuple(row.layer for row in self.layer_manifests) != ("BRONZE", "SILVER", "GOLD"):
            raise ValueError("rebuild layer summaries must be exact and ordered")
        for row in self.layer_manifests:
            if row.manifest_relative_path != layer_manifest_path(row.layer, self.build_id):
                raise ValueError("rebuild layer path substitution")
        recheck = self.final_recheck
        if recheck.build_id != self.build_id or recheck.run_id != self.run_id:
            raise ValueError("final recheck build/run substitution")
        if recheck.rebuild_receipt_sha256 != self.rebuild_receipt.sha256:
            raise ValueError("final recheck receipt digest substitution")
        rows = [row.model_dump(mode="json") for row in self.layer_manifests]
        if recheck.layer_manifest_set_sha256 != sha256_json(rows):
            raise ValueError("final recheck layer-set digest mismatch")
        return self


class ChildResultEnvelope(ContractModel):
    child_environment_sha256: Sha256
    child_role: ChildRole
    entrypoint_source: EntrypointSourceResult
    expected_repository_code_sha256: Sha256
    launcher_sha256: Sha256
    nonce: Sha256
    ordered_argv_sha256: Sha256
    payload_kind: Literal["CODE_ENVIRONMENT_MANIFEST", "REBUILD_COMPLETION"]
    result: PreBuildAdmissionResult | PostBuildIdRebuildResult
    schema_version: Literal["w04-child-result-v3"] = "w04-child-result-v3"

    @model_validator(mode="after")
    def exact_role_payload_binding(self) -> Self:
        if self.entrypoint_source.role != self.child_role:
            raise ValueError("entrypoint role differs from envelope role")
        if self.child_role == "PRE_BUILD_ADMISSION":
            if self.payload_kind != "CODE_ENVIRONMENT_MANIFEST" or not isinstance(
                self.result, PreBuildAdmissionResult
            ):
                raise ValueError("admission role requires admission payload")
            if self.result.repository_code_sha256 != self.expected_repository_code_sha256:
                raise ValueError("admission repository digest substitution")
            argv = ADMISSION_ARGV
        else:
            if self.payload_kind != "REBUILD_COMPLETION" or not isinstance(
                self.result, PostBuildIdRebuildResult
            ):
                raise ValueError("rebuild role requires rebuild payload")
            recheck = self.result.final_recheck
            if recheck.repository_code_sha256 != self.expected_repository_code_sha256:
                raise ValueError("rebuild repository digest substitution")
            if recheck.child_environment_sha256 != self.child_environment_sha256:
                raise ValueError("final recheck environment transport digest substitution")
            if recheck.entrypoint_sha256 != self.entrypoint_source.sha256:
                raise ValueError("final recheck entrypoint digest substitution")
            argv = REBUILD_ARGV
        if self.ordered_argv_sha256 != sha256_json(list(argv)):
            raise ValueError("ordered argv digest substitution")
        return self


def layer_manifest_semantic_sha256(layer_manifest: object) -> str:
    """Apply the sole R4 two-key complete-LayerManifest semantic derivation."""

    if type(layer_manifest) is not dict:
        raise TypeError("complete layer manifest must be a parsed object")
    wrapper = {
        "layer_manifest": layer_manifest,
        "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1",
    }
    return hashlib.sha256(canonical_json_bytes(wrapper)).hexdigest()


def validate_layer_manifest_semantic_binding(
    summary: LayerManifestSummary, layer_manifest: object
) -> None:
    """Reject a summary not bound by the sole complete-manifest R4 derivation."""

    derived = layer_manifest_semantic_sha256(layer_manifest)
    if summary.semantic_sha256 != derived:
        raise ValueError("layer summary semantic digest substitution")
