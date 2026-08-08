"""Closed tests for the bounded W04 logical-to-Arrow projection authority."""

from __future__ import annotations

import json
import re
import unicodedata
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from typing import Any, Never

import pytest

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_PATH = (
    ROOT / "reports/reviews/W04/authorities/wyscout-logical-arrow-projection-decisions-v1.json"
)
AUTHORITY_SHA256 = "460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1"
DECISION_ID = "w04-wyscout-logical-arrow-projection-decisions-v1"
DECISION_SCHEMA_VERSION = "w04-wyscout-logical-arrow-projection-decision-v1"
MASTER_ACTOR_ID = "4efe5691-8903-5148-8275-30d2e7e8aed0"
DECIDED_AT = "2026-08-01T15:44:40Z"

EXPECTED_BOUND_INPUTS = [
    {
        "path": "reports/verification/W04/wyscout-logical-arrow-projection-authorization-R1.md",
        "sha256": "eeb28f62b631b70e6c7046f3e8a6cdba74c1a7a4996c7024e98c471b08b8dd69",
    },
    {
        "path": "reports/reviews/W04/wyscout-23-root-schema-readiness-audit-R1.md",
        "sha256": "f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0",
    },
    {
        "path": ("reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-READINESS-AUDIT-01-R1.md"),
        "sha256": "227801dd267622b2d4fae868d4e1f6648d4c35ada3f9b9aac9edc4b34e3e9819",
    },
    {
        "path": (
            "reports/verification/W04/"
            "wyscout-23-root-schema-readiness-blocker-R1-master-verification.md"
        ),
        "sha256": "d33eedb889c3b916e509a27d9a3383862793b16002639cf559ebe0f2fbc1af71",
    },
    {
        "path": "reports/reviews/W04/wyscout-schema-design-R20.md",
        "sha256": "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047",
    },
    {
        "path": "reports/reviews/W04/wyscout-schema-design-R21.md",
        "sha256": "faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020",
    },
    {
        "path": ("reports/reviews/W04/wyscout-parquet-semantic-encoder-independent-review-R4.md"),
        "sha256": "eb5928d0bc06be4ecbe8317d9d3387e2db5d6d8631d08ac3dacbc45583c5ad9d",
    },
    {
        "path": (
            "reports/verification/W04/wyscout-parquet-semantic-encoder-R4-master-acceptance.md"
        ),
        "sha256": "1cfcd5bde3128a7736c75360460e61f73cc9910772d80d5e0b062abb606ce519",
    },
    {
        "path": "reports/verification/W04/wyscout-build-contract-R4-master-acceptance.md",
        "sha256": "26026181020650779bd7319c0672abf5dc5e78313fd38a33aff385bcb65c3449",
    },
]

CANONICAL_JSON_VALUE_PROJECTION = {
    "arrow_scalar": {
        "arrow_type": "utf8",
        "present_value_must_be_non_null": True,
        "utf8_codec": "strict",
    },
    "canonical_encoding": {
        "canonical_rules": [
            "STRICT_UTF8",
            "NO_BOM",
            "UNICODE_NFC",
            "OBJECT_KEYS_UNICODE_CODE_POINT_SORTED",
            "NO_DUPLICATE_OBJECT_KEYS",
            "NO_INVALID_JSON_CONSTANTS",
            "NO_INSIGNIFICANT_WHITESPACE",
            "R20_CANONICAL_NUMBER_FORMS",
            "EXACT_TAG_AND_CONTENT",
            "NO_TERMINAL_LF",
        ],
        "logical_dump_mode": "json",
        "tagged_content": "EXACT_CANONICAL_JSON_VALUE_MODEL_DUMP",
        "terminal_lf": False,
        "typed_validation_before_encoding": "EXACT_DISCRIMINATED_CANONICAL_JSON_VALUE",
    },
    "inverse_decoding": [
        "REQUIRE_NON_NULL_ARROW_UTF8_SCALAR",
        "RECOVER_EXACT_UTF8_BYTES_WITH_STRICT_DECODING",
        "PARSE_JSON_REJECTING_DUPLICATE_KEYS_AT_EVERY_DEPTH",
        "REJECT_INVALID_JSON_CONSTANTS",
        "STRICTLY_VALIDATE_EXACT_DISCRIMINATED_CANONICAL_JSON_VALUE",
        "DUMP_IN_JSON_MODE_AND_R20_CANONICAL_REENCODE_WITHOUT_TERMINAL_LF",
        "REQUIRE_REENCODED_BYTES_EQUAL_RECOVERED_BYTES_BYTE_FOR_BYTE",
    ],
    "logical_type": "CanonicalJsonValue",
    "nullability": {
        "canonical_json_null_arrow_representation": (
            "NON_NULL_UTF8_SCALAR_CONTAINING_EXACT_TAGGED_NULL_VALUE"
        ),
        "outer_absence_arrow_representation": (
            "ARROW_NULL_ONLY_WHEN_ACCEPTED_LOGICAL_FIELD_IS_OPTIONAL"
        ),
        "outer_optionality_remains_authoritative": True,
        "present_value_arrow_null_forbidden": True,
    },
}

FIXED_TUPLE_PROJECTION = {
    "arrow_type": "struct",
    "descriptor_children": {
        "child_descriptor_keys": ["name", "logical_position", "physical_type", "nullable"],
        "exact_child_names_required": True,
        "exact_child_nullability_required": True,
        "exact_child_order_required": True,
        "exact_child_physical_types_required": True,
        "logical_positions_are_zero_based_and_contiguous": True,
        "source": "INDEPENDENTLY_ACCEPTED_CANONICAL_DESCRIPTOR_CONTENT",
    },
    "encoding": [
        "REQUIRE_EXACT_LOGICAL_TUPLE_ARITY",
        "REQUIRE_EACH_POSITION_MATCH_ITS_DESCRIPTOR_CHILD",
        "PROJECT_EACH_POSITION_TO_ITS_EXACT_NAMED_STRUCT_CHILD",
        "REQUIRE_GENERATED_STRUCT_EQUAL_DESCRIPTOR_NAME_TYPE_ORDER_AND_NULLABILITY",
    ],
    "inverse_decoding": [
        "REQUIRE_EXACT_STRUCT_SCHEMA_EQUALITY",
        "REJECT_CHILD_OMISSION_ADDITION_REORDERING_RENAMING_TYPE_OR_NULLABILITY_DRIFT",
        "DECODE_EACH_CHILD_UNDER_ITS_DESCRIPTOR_RULE",
        "RESTORE_EXACT_LOGICAL_TUPLE_POSITION_ORDER",
        "REQUIRE_EXACT_LOGICAL_TUPLE_VALIDATION",
    ],
    "logical_shape": "HETEROGENEOUS_FIXED_TUPLE",
    "outer_optionality": "ARROW_STRUCT_NULL_ONLY_WHEN_ACCEPTED_LOGICAL_FIELD_IS_OPTIONAL",
}

HOMOGENEOUS_SEQUENCE_PROJECTION = {
    "arrow_type": "list",
    "descriptor_child": {
        "child_descriptor_keys": ["name", "physical_type", "nullable"],
        "exact_child_name_required": True,
        "exact_child_nullability_required": True,
        "exact_child_physical_type_required": True,
        "source": "INDEPENDENTLY_ACCEPTED_CANONICAL_DESCRIPTOR_CONTENT",
    },
    "encoding": [
        "REQUIRE_EVERY_ELEMENT_MATCH_THE_ONE_DESCRIPTOR_CHILD",
        "PRESERVE_LOGICAL_SEQUENCE_ORDER",
        "ENFORCE_DESCRIPTOR_OWNED_CARDINALITY",
    ],
    "inverse_decoding": [
        "REQUIRE_EXACT_LIST_SCHEMA_EQUALITY",
        "REJECT_CHILD_NAME_TYPE_OR_NULLABILITY_DRIFT",
        "DECODE_EVERY_ELEMENT_UNDER_THE_ONE_DESCRIPTOR_CHILD_RULE",
        "PRESERVE_LOGICAL_SEQUENCE_ORDER",
        "REQUIRE_DESCRIPTOR_OWNED_CARDINALITY_AND_LOGICAL_VALIDATION",
    ],
    "logical_shapes": [
        "VARIABLE_HOMOGENEOUS_SEQUENCE",
        "FIXED_HOMOGENEOUS_SEQUENCE",
    ],
    "schema_independence": (
        "EMPTY_AND_NONEMPTY_SEQUENCES_USE_IDENTICAL_ACCEPTED_DESCRIPTOR_SCHEMA"
    ),
}

LIFECYCLE = {
    "current_state": "AUTHORITY_ONLY_NO_SCHEMA_OR_PRODUCT_BYTES",
    "product_bytes_permitted_by_this_authority": False,
    "required_progression": [
        "AUTHORITY_DECISION_FROZEN",
        "FRESH_INDEPENDENT_AUTHORITY_REVIEW_PASS",
        "MASTER_AUTHORITY_ACCEPTANCE",
        "SERIALIZER_IMPLEMENTATION_CANDIDATE",
        "FRESH_INDEPENDENT_SERIALIZER_REVIEW_PASS",
        "MASTER_SERIALIZER_ACCEPTANCE",
        "RESUME_23_ROOT_PRODUCER",
    ],
}

PROHIBITIONS = [
    "FIXTURE_ROW_OBSERVED_VALUE_OR_EMPTY_SEQUENCE_SCHEMA_INFERENCE",
    "CALLER_SELECTED_ALTERNATE_DESCRIPTOR_OR_SCHEMA",
    "CALLER_CALLBACK_BOOLEAN_DIGEST_OR_EQUIVALENT_LOOKING_OBJECT_AS_AUTHORITY",
    "ARROW_NULL_FOR_PRESENT_CANONICAL_JSON_NULL",
    "LOSSY_OR_ONE_WAY_TRANSFORM",
    "ARROW_UNION_AS_PARQUET_AUTHORITY",
    "SECOND_SEMANTIC_DIGEST_VERSION_PREIMAGE_FORMULA_OR_DERIVATION",
    "NEW_ROOT_LOGICAL_FIELD_FEATURE_POPULATION_OR_DEPENDENCY",
    "SCHEMA_OR_PRODUCT_BYTES_BEFORE_REQUIRED_ACCEPTANCE",
    "PROVIDER_OR_NETWORK_ACCESS",
    "PRODUCT_PUBLICATION",
    "CLOUD_CONTAINER_HOSTED_CI_PUBLIC_ENDPOINT_OR_DEPLOYMENT",
    "GIT_OR_REMOTE_OPERATION",
]

SCHEMA_GENERATION = {
    "accepted_authority_requirement": (
        "INDEPENDENT_REVIEW_PASS_AND_MASTER_ACCEPTANCE_OF_EXACT_CANONICAL_DESCRIPTOR_CONTENT"
    ),
    "descriptor_content_requirements": [
        "EXACT_LOGICAL_TYPE_OR_SHAPE",
        "EXACT_PHYSICAL_TYPE",
        "EXACT_RECURSIVE_CHILD_NAMES",
        "EXACT_RECURSIVE_CHILD_ORDER",
        "EXACT_RECURSIVE_NULLABILITY",
        "EXACT_CARDINALITY_WHERE_LOGICALLY_FIXED",
        "EXACT_FORWARD_PROJECTION_RULE",
        "EXACT_INVERSE_DECODING_RULE",
        "RECURSIVE_METADATA_ABSENT",
    ],
    "exact_generated_schema_equality_required": True,
    "inference_sources_forbidden": [
        "ROW",
        "FIXTURE",
        "OBSERVED_VALUE",
        "EMPTY_SEQUENCE",
        "CALLER_SCHEMA",
        "CALLER_CALLBACK",
        "CALLER_BOOLEAN",
        "CALLER_DIGEST",
        "ALTERNATE_DESCRIPTOR",
        "EQUIVALENT_LOOKING_OBJECT",
    ],
    "schema_source": "ONLY_INDEPENDENTLY_ACCEPTED_CANONICAL_DESCRIPTOR_CONTENT",
}

SCOPE = {
    "arrow_projection_change": "BOUNDED_ADDITIVE_ONLY",
    "dependency_change": False,
    "digest_path_change": False,
    "feature_change": False,
    "logical_field_change": False,
    "logical_semantics_change": False,
    "population_change": False,
    "publication_or_deployment_authority": False,
    "root_change": False,
}

SEMANTIC_DIGEST_BINDING = {
    "algorithm": "SHA256_OF_EXACT_FRAMED_PREIMAGE",
    "parent_path_rules": "EXACT_SORTED_UNIQUE_SAFE_NFC_REPOSITORY_RELATIVE_UTF8",
    "preimage_components": [
        "UTF8(w04-wyscout-parquet-semantic-v1)",
        "0x00",
        "ASCII(S)",
        "UINT64_BE(LENGTH(schema_descriptor_bytes))",
        "schema_descriptor_bytes",
        "ASCII(R)",
        "UINT64_BE(row_count)",
        "FOR_EACH_ORDERED_LOGICAL_CONTRACT_ROW:UINT64_BE(LENGTH(row_bytes))||row_bytes",
        "ASCII(P)",
        "UINT64_BE(parent_count)",
        "FOR_EACH_ORDERED_PARENT_PATH:UINT64_BE(LENGTH(parent_path_utf8))||parent_path_utf8",
    ],
    "projection_effect": (
        "PHYSICAL_ARROW_SCHEMA_MAY_CHANGE_ONLY_THROUGH_THE_EXISTING_SCHEMA_DESCRIPTOR_INPUT"
    ),
    "row_bytes_rules": (
        "EXACT_ORDERED_UNIQUE_R20_CANONICAL_LOGICAL_CONTRACT_JSON_OBJECT_BYTES_WITH_ONE_TERMINAL_LF"
    ),
    "schema_descriptor_rules": (
        "EXACT_EXISTING_WYSCOUT_PARQUET_SCHEMA_DESCRIPTOR_CANONICAL_BYTES_WITH_ONE_TERMINAL_LF"
    ),
    "semantic_version": "w04-wyscout-parquet-semantic-v1",
    "unchanged": True,
}

TOP_LEVEL_KEYS = [
    "authority_class",
    "bound_inputs",
    "canonical_json_value_projection",
    "decided_at",
    "decided_by",
    "decision_id",
    "decision_schema_version",
    "fixed_tuple_projection",
    "homogeneous_sequence_projection",
    "lifecycle",
    "prohibitions",
    "schema_generation",
    "scope",
    "semantic_digest_binding",
]


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_float(value: str) -> Never:
    raise ValueError(f"float is forbidden: {value}")


def _reject_constant(value: str) -> Never:
    raise ValueError(f"invalid JSON constant: {value}")


def _assert_nfc_tree(value: object) -> None:
    if isinstance(value, str):
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non-NFC string")
        return
    if isinstance(value, list):
        for item in value:
            _assert_nfc_tree(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_nfc_tree(key)
            _assert_nfc_tree(item)
        return
    if value is not None and type(value) not in {bool, int}:
        raise ValueError("unsupported JSON scalar")


def _canonical_bytes(value: object) -> bytes:
    _assert_nfc_tree(value)
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
    ).encode("utf-8")


def _strict_load(raw: bytes) -> dict[str, Any]:
    if raw.startswith(b"\xef\xbb\xbf") or b"\r" in raw:
        raise ValueError("invalid physical JSON encoding")
    value = json.loads(
        raw.decode("utf-8", errors="strict"),
        object_pairs_hook=_reject_duplicate_pairs,
        parse_float=_reject_float,
        parse_constant=_reject_constant,
    )
    if type(value) is not dict:
        raise ValueError("authority must be one JSON object")
    _assert_nfc_tree(value)
    if raw != _canonical_bytes(value):
        raise ValueError("authority is not exact R20-canonical JSON plus one LF")
    return value


def _validate_authority(value: dict[str, Any]) -> None:
    if list(value) != TOP_LEVEL_KEYS:
        raise ValueError("wrong top-level key roster or order")
    exact_values: dict[str, object] = {
        "authority_class": "LOGICAL_ARROW_PROJECTION",
        "bound_inputs": EXPECTED_BOUND_INPUTS,
        "canonical_json_value_projection": CANONICAL_JSON_VALUE_PROJECTION,
        "decided_at": DECIDED_AT,
        "decided_by": MASTER_ACTOR_ID,
        "decision_id": DECISION_ID,
        "decision_schema_version": DECISION_SCHEMA_VERSION,
        "fixed_tuple_projection": FIXED_TUPLE_PROJECTION,
        "homogeneous_sequence_projection": HOMOGENEOUS_SEQUENCE_PROJECTION,
        "lifecycle": LIFECYCLE,
        "prohibitions": PROHIBITIONS,
        "schema_generation": SCHEMA_GENERATION,
        "scope": SCOPE,
        "semantic_digest_binding": SEMANTIC_DIGEST_BINDING,
    }
    for key in TOP_LEVEL_KEYS:
        if value[key] != exact_values[key]:
            raise ValueError(f"authority value drift: {key}")

    if (
        re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
            value["decided_by"],
        )
        is None
    ):
        raise ValueError("noncanonical actor UUID")
    if value["decided_at"] != "2026-08-01T15:44:40Z":
        raise ValueError("decision clock drift")


def test_authority_is_exact_canonical_and_binds_immutable_evidence() -> None:
    raw = AUTHORITY_PATH.read_bytes()
    assert sha256(raw).hexdigest() == AUTHORITY_SHA256
    authority = _strict_load(raw)
    _validate_authority(authority)
    assert _canonical_bytes(authority) == raw

    for binding in EXPECTED_BOUND_INPUTS:
        bound_raw = (ROOT / binding["path"]).read_bytes()
        assert sha256(bound_raw).hexdigest() == binding["sha256"]


def test_authority_freezes_exact_projection_and_unchanged_digest_path() -> None:
    authority = _strict_load(AUTHORITY_PATH.read_bytes())
    projection = authority["canonical_json_value_projection"]
    assert projection["arrow_scalar"] == {
        "arrow_type": "utf8",
        "present_value_must_be_non_null": True,
        "utf8_codec": "strict",
    }
    assert projection["canonical_encoding"]["terminal_lf"] is False
    assert projection["nullability"]["present_value_arrow_null_forbidden"] is True
    assert authority["fixed_tuple_projection"]["arrow_type"] == "struct"
    assert authority["homogeneous_sequence_projection"]["arrow_type"] == "list"
    assert authority["semantic_digest_binding"] == SEMANTIC_DIGEST_BINDING
    assert authority["semantic_digest_binding"]["unchanged"] is True
    assert authority["scope"]["digest_path_change"] is False


def test_authority_is_progression_safe_and_grants_no_product_bytes() -> None:
    authority = _strict_load(AUTHORITY_PATH.read_bytes())
    lifecycle = authority["lifecycle"]
    assert lifecycle == LIFECYCLE
    assert lifecycle["required_progression"][-1] == "RESUME_23_ROOT_PRODUCER"
    assert lifecycle["product_bytes_permitted_by_this_authority"] is False
    assert "SCHEMA_OR_PRODUCT_BYTES_BEFORE_REQUIRED_ACCEPTANCE" in authority["prohibitions"]
    assert "PERMANENT_PRODUCT_PATH_ABSENCE" not in authority["prohibitions"]


@pytest.mark.parametrize(
    ("mutator", "expected_message"),
    [
        (lambda value: value.update({"extra": True}), "top-level"),
        (
            lambda value: value["canonical_json_value_projection"]["arrow_scalar"].update(
                {"arrow_type": "large_utf8"}
            ),
            "canonical_json_value_projection",
        ),
        (
            lambda value: value["fixed_tuple_projection"]["descriptor_children"].update(
                {"exact_child_order_required": False}
            ),
            "fixed_tuple_projection",
        ),
        (
            lambda value: value["homogeneous_sequence_projection"].update({"arrow_type": "struct"}),
            "homogeneous_sequence_projection",
        ),
        (
            lambda value: value["schema_generation"].update({"schema_source": "ROW"}),
            "schema_generation",
        ),
        (
            lambda value: value["semantic_digest_binding"].update(
                {"semantic_version": "w04-wyscout-parquet-semantic-v2"}
            ),
            "semantic_digest_binding",
        ),
        (
            lambda value: value["lifecycle"].update(
                {"product_bytes_permitted_by_this_authority": True}
            ),
            "lifecycle",
        ),
    ],
)
def test_authority_rule_drift_fails_closed(
    mutator: Any,
    expected_message: str,
) -> None:
    authority = deepcopy(_strict_load(AUTHORITY_PATH.read_bytes()))
    mutator(authority)
    with pytest.raises(ValueError, match=expected_message):
        _validate_authority(authority)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"a":1,"a":2}\n',
        b'{"value":NaN}\n',
        b'{"value":1.0}\n',
        b'{ "value":1}\n',
        b'{"value":1}',
        b'\xef\xbb\xbf{"value":1}\n',
        b'{"value":"e\xcc\x81"}\n',
        b"\xff",
    ],
)
def test_strict_authority_loader_rejects_noncanonical_bytes(raw: bytes) -> None:
    with pytest.raises((UnicodeDecodeError, ValueError)):
        _strict_load(raw)
