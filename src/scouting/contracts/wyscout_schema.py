"""Deterministic in-memory W04 implemented closed-schema authority.

This module owns only canonical logical-schema and Arrow projection descriptor
content.  It deliberately does not import PyArrow or the storage layer.  The
accepted storage primitive can mechanically instantiate the descriptor content
after this closure has passed its independent authority gates.
"""

# ruff: noqa: E501  # Frozen compact R5 JSONL oracle rows are byte-exact.

from __future__ import annotations

import hashlib
import inspect
import json
import re
import types
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import datetime
from decimal import Decimal
from enum import Enum
from functools import cache
from typing import Literal, TypeAliasType, Union, cast, get_args, get_origin
from uuid import UUID

from pydantic import BaseModel

from . import evidence, primitives, wyscout_build, wyscout_data

W04_CANONICAL_SCHEMA_VERSION = "w04-wyscout-implemented-closed-schema-v2"
W04_SCHEMA_LANGUAGE_VERSION = "w04-closed-logical-schema-language-v1"
W04_IMPLEMENTED_SCHEMA_SURFACE = "IMPLEMENTED_CLOSED_SCHEMA"
W04_JSON_ONLY_PROJECTION_STATE = "NOT_APPLICABLE_JSON_ONLY"
W04_PARQUET_SERIALIZER_VERSION = "w04-wyscout-parquet-v1"

W04_SCHEMA_ROOT_ROLES = (
    "BRONZE_KNOWN_RECORD",
    "BRONZE_REJECTED_RECORD",
    "BRONZE_REJECTED_FIELD",
    "SILVER_COMPETITION",
    "SILVER_TEAM",
    "SILVER_PLAYER",
    "SILVER_MATCH",
    "SILVER_ACTION",
    "SILVER_LINEUP_STINT",
    "SILVER_POSSESSION",
    "SILVER_PLAYER_MATCH_FACT",
    "GOLD_PLAYER_WINDOW",
    "LAYER_MANIFEST",
    "TEMPORAL_BOUNDARY_RECEIPT",
    "REBUILD_INVOCATION_RECEIPT",
    "ENTRYPOINT_SOURCE_RESULT",
    "COMPONENT_PROOF_RESULT",
    "PRE_BUILD_ADMISSION_RESULT",
    "REBUILD_RECEIPT_SUMMARY",
    "LAYER_MANIFEST_SUMMARY",
    "FINAL_RECHECK_RESULT",
    "POST_BUILD_ID_REBUILD_RESULT",
    "CHILD_RESULT_ENVELOPE",
)

_W04_PHYSICAL_PRIMARY_KEY_PATHS: dict[str, tuple[tuple[str, ...], ...]] = {
    "BRONZE_KNOWN_RECORD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
    ),
    "BRONZE_REJECTED_RECORD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
    ),
    "BRONZE_REJECTED_FIELD": (
        ("source_row", "source_manifest_id"),
        ("source_row", "completion_relative_path"),
        ("source_row", "source_record_ordinal"),
        ("json_path",),
    ),
    "SILVER_COMPETITION": (("competition_id",),),
    "SILVER_TEAM": (("team_id",),),
    "SILVER_PLAYER": (("player_id",),),
    "SILVER_MATCH": (("match_id",),),
    "SILVER_ACTION": (("action_id",),),
    "SILVER_LINEUP_STINT": (("lineup_stint_id",),),
    "SILVER_POSSESSION": (("possession_id",),),
    "SILVER_PLAYER_MATCH_FACT": (
        ("tenant_context", "tenant_id"),
        ("source_manifest_id",),
        ("match_id",),
        ("player_id",),
        ("player_match_fact_schema_version",),
    ),
    "GOLD_PLAYER_WINDOW": (
        ("tenant_context", "tenant_id"),
        ("player_id",),
        ("competition_id",),
        ("season_id",),
        ("role_context_id",),
        ("role_context_version",),
        ("window_definition_id",),
        ("window_start_utc",),
        ("window_end_utc",),
        ("feature_cutoff_ts",),
        ("dependency_lineage_hash",),
    ),
}

W04_CANONICAL_CONTENT_KEY_ORDER = (
    "canonical_schema_id",
    "canonical_schema_version",
    "schema_language_version",
    "root_role",
    "root_definition_id",
    "definitions",
    "parquet_projection",
)

W04_IMPLEMENTED_ROW_KEY_ORDER = (
    "canonical_schema_content_sha256",
    "canonical_schema_id",
    "canonical_schema_version",
    "closure_dependencies",
    "root_role",
    "surface_kind",
)

_ROOT_MODELS: tuple[type[BaseModel], ...] = (
    wyscout_data.BronzeKnownRecord,
    wyscout_data.BronzeRejectedRecord,
    wyscout_data.BronzeRejectedField,
    wyscout_data.SilverCompetition,
    wyscout_data.SilverTeam,
    wyscout_data.SilverPlayer,
    wyscout_data.SilverMatch,
    wyscout_data.SilverAction,
    wyscout_data.SilverLineupStint,
    wyscout_data.SilverPossession,
    wyscout_data.SilverPlayerMatchFact,
    wyscout_data.GoldPlayerWindow,
    wyscout_data.LayerManifest,
    wyscout_build.TemporalBoundaryReceipt,
    wyscout_build.RebuildInvocationReceipt,
    wyscout_build.EntrypointSourceResult,
    wyscout_build.ComponentProofResult,
    wyscout_build.PreBuildAdmissionResult,
    wyscout_build.RebuildReceiptSummary,
    wyscout_build.LayerManifestSummary,
    wyscout_build.FinalRecheckResult,
    wyscout_build.PostBuildIdRebuildResult,
    wyscout_build.ChildResultEnvelope,
)

_DEPENDENCY_ROLE_GRAPH: tuple[tuple[str, ...], ...] = (
    (),
    (),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD",),
    ("BRONZE_KNOWN_RECORD", "SILVER_COMPETITION", "SILVER_TEAM"),
    ("BRONZE_KNOWN_RECORD", "SILVER_MATCH", "SILVER_PLAYER", "SILVER_TEAM"),
    ("SILVER_MATCH", "SILVER_PLAYER", "SILVER_TEAM"),
    ("SILVER_ACTION",),
    (
        "SILVER_ACTION",
        "SILVER_LINEUP_STINT",
        "SILVER_MATCH",
        "SILVER_PLAYER",
        "SILVER_POSSESSION",
    ),
    ("SILVER_PLAYER_MATCH_FACT",),
    W04_SCHEMA_ROOT_ROLES[:12],
    ("GOLD_PLAYER_WINDOW", "LAYER_MANIFEST"),
    ("LAYER_MANIFEST", "TEMPORAL_BOUNDARY_RECEIPT"),
    (),
    (),
    ("COMPONENT_PROOF_RESULT",),
    (),
    ("LAYER_MANIFEST",),
    ("REBUILD_RECEIPT_SUMMARY", "LAYER_MANIFEST_SUMMARY"),
    (
        "REBUILD_RECEIPT_SUMMARY",
        "LAYER_MANIFEST_SUMMARY",
        "FINAL_RECHECK_RESULT",
    ),
    (
        "ENTRYPOINT_SOURCE_RESULT",
        "PRE_BUILD_ADMISSION_RESULT",
        "POST_BUILD_ID_REBUILD_RESULT",
    ),
)

_FIELD_NAME = re.compile(r"[a-z][a-z0-9_]{0,127}")
_SCHEMA_ROLE = re.compile(r"[a-z][a-z0-9-]{0,127}")
_JSON_ONLY_START_INDEX = 12
_CANONICAL_JSON_TYPES = (
    wyscout_data.CanonicalJsonNull,
    wyscout_data.CanonicalJsonBoolean,
    wyscout_data.CanonicalJsonInteger,
    wyscout_data.CanonicalJsonNumber,
    wyscout_data.CanonicalJsonString,
    wyscout_data.CanonicalJsonArray,
    wyscout_data.CanonicalJsonObject,
)


class W04SchemaClosureError(ValueError):
    """The in-memory W04 implemented-schema closure is not exact."""


def w04_canonical_schema_id(root_role: str) -> str:
    """Return the one frozen canonical schema ID for a root role."""

    if type(root_role) is not str or root_role not in W04_SCHEMA_ROOT_ROLES:
        raise W04SchemaClosureError("root role is outside the exact W04 roster")
    return "w04-wyscout-" + root_role.lower().replace("_", "-") + "-implemented-closed-schema-v2"


def _validate_json_value(value: object, *, location: str = "$") -> None:
    if value is None or type(value) in {bool, int}:
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value or any(
            0xD800 <= ord(character) <= 0xDFFF for character in value
        ):
            raise W04SchemaClosureError(f"{location} contains non-canonical Unicode")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_json_value(item, location=f"{location}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                raise W04SchemaClosureError(f"{location} contains a non-string key")
            _validate_json_value(key, location=f"{location}.<key>")
            _validate_json_value(item, location=f"{location}.{key}")
        return
    raise W04SchemaClosureError(f"{location} contains an unsupported JSON runtime type")


def _canonical_json_bytes(value: object) -> bytes:
    _validate_json_value(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def canonical_w04_schema_content_bytes(content: Mapping[str, object]) -> bytes:
    """Encode one candidate root content under the exact no-LF digest preimage."""

    if type(content) is not dict:
        raise W04SchemaClosureError("schema content must be one exact dictionary")
    if tuple(content) != W04_CANONICAL_CONTENT_KEY_ORDER:
        raise W04SchemaClosureError("schema content key order is not exact")
    return _canonical_json_bytes(content)


def _predicate(
    owner_model: str,
    declared_owner_model: str,
    validator_name: str,
    predicate_id: str,
    operation: str,
    operands: tuple[str, ...],
    constants: tuple[str, ...],
) -> dict[str, object]:
    return {
        "owner_model": owner_model,
        "declared_owner_model": declared_owner_model,
        "validator_name": validator_name,
        "predicate_id": predicate_id,
        "predicate_classification": "RUNTIME_MODEL_VALIDATOR",
        "authority_sources": [],
        "operation": operation,
        "operands": list(operands),
        "constants": list(constants),
    }


_TENANT_CONSTANTS = {
    "club_id": None,
    "tenant_id": str(wyscout_data.TENANT_ID),
}
_SOURCE_CONSTANTS = {
    "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
    "source_manifest_sha256": wyscout_data.SOURCE_MANIFEST_SHA256,
}


def _source_member_corpus() -> list[dict[str, object]]:
    return [
        {
            "completion_relative_path": path,
            "country_partition": country.value if country is not None else None,
            "record_kind": record_kind.value,
            "row_count": row_count,
            "source_sha256": source_sha256,
        }
        for path, (record_kind, source_sha256, country, row_count) in sorted(
            wyscout_data._SOURCE_PATH_ROWS.items()
        )
    ]


def _field_registry_corpus() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for text in wyscout_data._FIELD_REGISTRY_ROWS_TEXT.splitlines():
        record_kind, json_path, decision, kinds = text.split("|")
        rows.append(
            {
                "admitted_json_kinds": kinds.split(","),
                "decision": decision,
                "json_path": json_path,
                "record_kind": record_kind,
            }
        )
    if len(rows) != 119:
        raise W04SchemaClosureError("frozen field-registry corpus is not exactly 119 rows")
    return rows


def _pair_rows(values: object) -> list[list[int]]:
    return [list(pair) for pair in sorted(cast(frozenset[tuple[int, int]], values))]


_DATA_AUTHORITY_ROWS = [
    row.model_dump(mode="json") for row in wyscout_data.accepted_authority_references()
]
_DATA_AUTHORITY_CLOCKS = [
    row.model_dump(mode="json") for row in wyscout_data.accepted_authority_clocks()
]
_BUILD_AUTHORITY_ROWS = [
    row.model_dump(mode="json") for row in wyscout_build.accepted_authority_rows()
]
_BUILD_DEPENDENCY_ROWS = [
    row.model_dump(mode="json") for row in wyscout_build.accepted_dependency_rows()
]
_SOURCE_MEMBER_CORPUS = _source_member_corpus()
_FIELD_REGISTRY_CORPUS = _field_registry_corpus()

_FROZEN_CONSTANT_CORPUS: dict[str, object] = {
    "authority_composition": {
        "build_authority_row_count": 5,
        "build_authority_rows": _BUILD_AUTHORITY_ROWS,
        "data_authority_clock_count": 4,
        "data_authority_clocks": _DATA_AUTHORITY_CLOCKS,
        "data_authority_row_count": 4,
        "data_authority_rows": _DATA_AUTHORITY_ROWS,
    },
    "completion_index": {
        "aggregate_action_count": 3_071_395,
        "completion_manifest_sha256": (
            "69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1"
        ),
        "content_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        "indexed_source_member": {
            "indexed_action_count": 643_150,
            "path": "archive-members/events_England.json",
            "source_sha256": ("301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad"),
        },
        "one_match_scope": {
            "canonical_match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
            "periods": [
                {
                    "action_count": 901,
                    "action_period_code": "1H",
                    "membership_sha256": (
                        "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b"
                    ),
                    "period_rank": 1,
                },
                {
                    "action_count": 867,
                    "action_period_code": "2H",
                    "membership_sha256": (
                        "b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16"
                    ),
                    "period_rank": 2,
                },
            ],
            "provider_match_id": 2_499_719,
            "wider_completeness_implied": False,
        },
        "relative_path": (
            "data/manifests/wyscout/v5/source-completion/"
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
            "source-completion-index.json"
        ),
        "schema_version": "w04-wyscout-source-completion-index-v1",
        "source_completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        **_SOURCE_CONSTANTS,
    },
    "completion_index_binding": {
        "canonical_match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
        "completion_reader_requirements": [
            "VERIFY_INDEX_CONTENT_ADDRESS",
            "VERIFY_SOURCE_MANIFEST_AND_MEMBER_BINDING",
            "VERIFY_CANONICAL_ORDERING",
            "VERIFY_ACTION_IDENTITY_UNIQUENESS",
            "VERIFY_AGGREGATE_SOURCE_ROW_COUNT_RECONCILIATION",
            "VERIFY_EXACT_PERIOD_POPULATION_SEQUENCE_AND_SET_EQUALITY",
            "REJECT_MISSING_ADDITIONAL_DUPLICATED_REORDERED_STALE_OR_CROSS_PERIOD_ACTIONS",
            "REJECT_CALLER_BOOLEAN_COUNT_WITNESS_OR_SUBMITTED_POPULATION_ONLY_DIGEST",
        ],
        "periods": [
            {
                "action_count": 901,
                "ordered_membership_sha256": (
                    "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b"
                ),
                "period_code": "1H",
                "period_rank": 1,
            },
            {
                "action_count": 867,
                "ordered_membership_sha256": (
                    "b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16"
                ),
                "period_code": "2H",
                "period_rank": 2,
            },
        ],
        "provider_match_id": 2_499_719,
        "scope": "ONLY_AUTHORIZED_W04_ONE_MATCH_FOUR_FEATURE_POC_PARTITIONS",
        "source_completion_index_path": (
            "data/manifests/wyscout/v5/source-completion/"
            "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
            "source-completion-index.json"
        ),
        "source_completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
        "source_manifest_path": (
            "data/manifests/wyscout/v5/source/"
            "4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
        ),
        "source_manifest_sha256": wyscout_data.SOURCE_MANIFEST_SHA256,
        "source_member_path": "archive-members/events_England.json",
        "source_member_row_count": 643_150,
        "source_member_sha256": (
            "301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad"
        ),
    },
    "build_identity": {
        "algorithm": "SHA256_OF_R20_CANONICAL_JSON_WITHOUT_TERMINAL_LF",
        "inverse_reconstruction": "REMOVE_ONLY_BUILD_ID_INSERT_ONLY_SCHEMA_VERSION",
        "post_hash_invocation_key_count": 25,
        "pre_build_projection_key_count": 25,
        "pre_build_projection_keys": list(wyscout_build.PRE_BUILD_PROJECTION_KEYS),
        "projection_schema_version": "w04-wyscout-pre-build-projection-v1",
        "replacement_rule": (
            "REMOVE_ONLY_SCHEMA_VERSION_INSERT_ONLY_BUILD_ID_AND_COPY_OTHER_24_VALUES_"
            "BYTE_SEMANTICALLY"
        ),
        "second_build_hash": "FORBIDDEN",
    },
    "dependency_rows": _BUILD_DEPENDENCY_ROWS,
    "field_registry": {
        "acceptance_sha256": wyscout_data.FIELD_ACCEPTANCE_SHA256,
        "candidate_sha256": wyscout_data.FIELD_CANDIDATE_SHA256,
        "review_sha256": "76c4744d302b4c6d86f4d537498695e365f0d3c733211bfafcb1e5c2805c0886",
        "row_count": 119,
        "rows": _FIELD_REGISTRY_CORPUS,
    },
    "layer_manifest_receipt_composition": {
        "complete_layer_manifest_semantic": {
            "canonical_json_terminal_lf": False,
            "digest_algorithm": "SHA256",
            "wrapper_exact_key_order": ["layer_manifest", "semantic_schema_version"],
            "wrapper_fixed_member": {
                "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1"
            },
            "wrapper_variable_member": "layer_manifest=complete_typed_canonical_readback",
        },
        "gold_population": {
            "complete_entry_count": 1,
            "row_count": 1,
            "source_match_id": 2_499_719,
            "source_season_id": 181_150,
        },
        "layer_order": ["BRONZE", "SILVER", "GOLD"],
        "parent_edges": [
            {"child": "BRONZE", "parents": []},
            {"child": "SILVER", "parents": ["BRONZE"]},
            {"child": "GOLD", "parents": ["SILVER"]},
        ],
        "operational_clock_relation": "started_at<=checked_at<=completed_at",
        "readback_bindings": [
            "canonical_physical_bytes_with_terminal_lf",
            "typed_layer_manifest_exact_dump_equality",
            "physical_sha256_and_size",
            "frozen_source_authority_and_five_dependency_lineage",
            "sole_two_key_layer_manifest_semantic_sha256",
            "bronze_to_silver_to_gold_parent_summary_equality",
            "one_complete_gold_product_physical_semantic_size_row_count",
            "gold_logical_row_temporal_proof_one_match_season_population",
            "boundary_physical_digest_size_path_and_clock_equality",
        ],
    },
    "layer_manifest_authority": {
        "complete_layer_manifest_fields": list(wyscout_data.LayerManifest.model_fields),
        "gold_population": {
            "boundary_receipt_count": 1,
            "boundary_sequence_policy": (
                "EXACT_GOLD_MANIFEST_ENTRY_PATH_SEQUENCE_AND_SET_EQUALITY_WITHOUT_SORT_FILTER_"
                "DEDUP_OR_RECOVERY"
            ),
            "gold_entry_count": 1,
            "population_source": (
                "EVERY_AND_ONLY_GOLD_PLAYER_WINDOW_ENTRY_FROM_EXACT_VALIDATED_GOLD_MANIFEST_"
                "IN_MANIFEST_ORDER"
            ),
            "product_count": 1,
            "readback_requirements": [
                "GUARD_READ_GOLD_PRODUCT_FROM_VALIDATED_GOLD_MANIFEST_ENTRY",
                (
                    "REPRODUCE_PRODUCT_PATH_ROLE_BUILD_PARTITIONS_PHYSICAL_HASH_SIZE_SCHEMA_"
                    "SERIALIZER_ROW_COUNT_SEMANTIC_HASH_PARENTS_RIGHTS_WINDOW_CLOCKS_FEATURE_"
                    "INDEX_LINEAGE_APPLICABILITY_AND_TEMPORAL_PROOF"
                ),
                (
                    "REQUIRE_GOLD_PROVENANCE_AND_DEPENDENCY_LINEAGE_BIND_ACCEPTED_SOURCE_"
                    "COMPLETION_INDEX_SHA256"
                ),
                "GUARD_READ_MATCHING_BOUNDARY_RECEIPT",
                (
                    "REPRODUCE_BOUNDARY_PATH_HASH_BUILD_RUN_PRODUCT_MANIFEST_PHYSICAL_"
                    "SEMANTIC_ROW_COUNT_LINEAGE_CUTOFF_TEMPORAL_PROOF_AND_VERIFICATION_STATE"
                ),
            ],
        },
        "layer_summary_keys": list(wyscout_build.LayerManifestSummary.model_fields),
        "layer_summary_order": ["BRONZE", "SILVER", "GOLD"],
        "manifest_semantic_derivation": {
            "canonical_encoding": (
                "R20_CANONICAL_JSON_UTF8_NFC_WITHOUT_BOM_WHITESPACE_OR_TERMINAL_LF"
            ),
            "formula": "SHA256_OF_R20_CANONICAL_JSON_OF_EXACT_TWO_KEY_WRAPPER",
            "layer_manifest_value": (
                "COMPLETE_EXACT_PARSED_GUARD_READ_CLOSED_SCHEMA_VALIDATED_OBJECT"
            ),
            "preimage_key_count": 2,
            "preimage_keys": ["layer_manifest", "semantic_schema_version"],
            "semantic_schema_version": "w04-wyscout-layer-manifest-semantic-v1",
            "terminal_lf": False,
        },
        "parent_chain": {"BRONZE": [], "GOLD": ["SILVER"], "SILVER": ["BRONZE"]},
        "required_validation_order": [
            "DERIVE_EXACT_SAME_BUILD_MANIFEST_PATH",
            "GUARD_READ_COMPLETE_PHYSICAL_BYTES",
            "REPRODUCE_PHYSICAL_SHA256_AND_SIZE",
            "REQUIRE_CANONICAL_JSON_PLUS_ONE_TERMINAL_LF",
            "VALIDATE_COMPLETE_CLOSED_LAYER_MANIFEST_SCHEMA",
            (
                "RECONCILE_LAYER_BUILD_SOURCE_INDEX_TENANT_RIGHTS_CLOCKS_AUTHORITIES_FEATURE_"
                "SCHEMA_AND_LINEAGE"
            ),
            "DERIVE_SOLE_TWO_KEY_COMPLETE_MANIFEST_SEMANTIC_SHA256",
            "COMPARE_DIRECTLY_TO_SAME_LAYER_SUMMARY",
            "RECONCILE_EXACT_BRONZE_SILVER_GOLD_PARENT_SUMMARY_CHAIN",
            "DERIVE_EXACT_GOLD_PRODUCT_AND_BOUNDARY_POPULATION",
        ],
        "substitution_failures": [
            "REPLACE_ONLY_BRONZE_SUMMARY_SEMANTIC_SHA256",
            "REPLACE_ONLY_SILVER_SUMMARY_SEMANTIC_SHA256",
            "REPLACE_ONLY_GOLD_SUMMARY_SEMANTIC_SHA256",
            "COPY_ANY_MANIFEST_ENTRY_SEMANTIC_SHA256",
            "COPY_PHYSICAL_MANIFEST_SHA256",
            "COPY_ANOTHER_LAYER_SEMANTIC_SHA256",
            "SWAP_LAYER_SUMMARY_SEMANTIC_VALUES",
            "REHASH_ALL_DOWNSTREAM_SUMMARY_RECEIPT_AND_CHILD_WRAPPERS",
        ],
    },
    "receipt_contracts": {
        "rebuild_invocation_receipt": {
            "boundary_summary_keys": [
                "gold_relative_path",
                "relative_path",
                "sha256",
                "size_bytes",
            ],
            "keys": list(wyscout_build.RebuildInvocationReceipt.model_fields),
            "result_state": "COMPLETE",
            "rules": [
                "EXACT_POST_HASH_25_KEY_REBUILD_INVOCATION",
                "EXACT_THREE_LAYER_SUMMARIES_IN_BRONZE_SILVER_GOLD_ORDER",
                "EXACT_GOLD_MANIFEST_DERIVED_BOUNDARY_POPULATION",
                "GUARD_READ_EVERY_BOUNDARY_AND_REPRODUCE_PATH_HASH_SIZE_BUILD_RUN_AND_GOLD",
                "REQUIRE_STARTED_AT_LE_BOUNDARY_CHECKED_AT_LE_COMPLETED_AT",
                "CANONICAL_JSON_PLUS_EXACTLY_ONE_TERMINAL_LF",
                "NO_OWN_PATH_DIGEST_OR_SIZE_IN_CONTENT",
            ],
            "schema_version": "w04-wyscout-rebuild-invocation-receipt-v1",
        },
        "temporal_boundary_receipt": {
            "keys": list(wyscout_build.TemporalBoundaryReceipt.model_fields),
            "row_count": 1,
            "rules": [
                ("DIRECT_SHA256_OF_EXACT_UTF8_NFC_GOLD_RELATIVE_PATH_WITHOUT_BOM_OR_TERMINAL_LF"),
                "EXACT_ACCEPTED_GOLD_PRODUCT_AND_GOLD_MANIFEST_EQUALITIES",
                "EXACT_R20_CANONICAL_TEMPORAL_PROOF_DIGEST",
                "CANONICAL_JSON_PLUS_EXACTLY_ONE_TERMINAL_LF",
                "NO_OWN_PATH_OR_PHYSICAL_DIGEST_IN_CONTENT",
            ],
            "schema_version": "w04-wyscout-temporal-boundary-receipt-v1",
            "verification_state": "STRICT_BEFORE_CUTOFF_PASS",
        },
    },
    "possession_semantics": {
        "canonical_action_order_fields": [
            "period_rank",
            "period_elapsed_seconds",
            "source_record_ordinal",
            "source_event_record_id",
        ],
        "contested_pairs": _pair_rows(wyscout_data._CONTESTED_PAIRS),
        "control_pairs": _pair_rows(wyscout_data._CONTROL_PAIRS),
        "dead_ball_preceding_pairs": _pair_rows(wyscout_data._DEAD_BALL_PRECEDING_PAIRS),
        "dead_ball_unassigned_pairs": _pair_rows(wyscout_data._DEAD_BALL_UNASSIGNED_PAIRS),
        "equal_clock": {
            "group_key": ["period_rank", "period_elapsed_seconds"],
            "multiple_controlling_teams_effect": [
                "clear_dependent_contested_buffer",
                "clear_current_active_group_for_clock",
                "preserve_strictly_earlier_completed_group",
            ],
            "resolution_order": "group-first",
        },
        "explicit_unmapped_pairs": _pair_rows(wyscout_data._EXPLICIT_UNMAPPED_PAIRS),
        "non_control_admin_pairs": _pair_rows(wyscout_data._NON_CONTROL_ADMIN_PAIRS),
        "restart_pairs": _pair_rows(wyscout_data._RESTART_PAIRS),
    },
    "season_and_lineup": {
        "build_projection_binding": {
            "allowed_consumption_member": "authority_rows",
            "build_hash_rule": "UNCHANGED_SHA256_OF_R20_CANONICAL_JSON_WITHOUT_TERMINAL_LF",
            "integration_policy": (
                "APPEND_ACCEPTED_AUTHORITY_REFERENCE_ONLY_WITHIN_EXISTING_AUTHORITY_ROWS_MEMBER"
            ),
            "post_hash_invocation_key_count": 25,
            "pre_build_projection_key_count": 25,
            "pre_build_projection_keys": list(wyscout_build.PRE_BUILD_PROJECTION_KEYS),
            "projection_schema_version": "w04-wyscout-pre-build-projection-v1",
            "second_build_hash": "FORBIDDEN",
        },
        "lineup_population": {
            "complete_population_policy": [
                "REJECT_OMISSION",
                "REJECT_ADDITION",
                "REJECT_DUPLICATION",
                "REJECT_REORDERING",
                "REJECT_ALTERNATE_STINT_ORDINAL",
                "REJECT_INFERRED_TERMINAL_INTERVAL",
                "REJECT_INFERRED_MINUTES",
                "REJECT_PER90_ELIGIBILITY",
                "REJECT_ANOTHER_SEASON_MATCH_TEAM_PLAYER_OR_STINT",
            ],
            "ordered_population": [
                {
                    "elapsed_minutes": None,
                    "end_interval": None,
                    "lineup_stint_id": "591cdf5b-2281-53c4-8225-150313ca2c01",
                    "lineup_stint_uuid_name": ("stint:1631:285508:0:w04-wyscout-lineup-stint-v1"),
                    "lineup_stint_uuid_namespace": {
                        "algorithm": "UUIDV5",
                        "kind_name": "match",
                        "match_namespace": "20b5206f-dfa5-55b4-84ab-8a336a75073e",
                        "source_namespace": "89161938-1e8c-53ab-ab52-eba969681833",
                        "source_namespace_name": wyscout_build.SOURCE_NAMESPACE_NAME,
                    },
                    "lower_bound_minutes": None,
                    "match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
                    "match_source_id": 2_499_719,
                    "per90_eligible": False,
                    "player_id": "be8da881-2b15-513f-978f-6bb3865bc8e2",
                    "player_source_id": 285_508,
                    "right_censored": True,
                    "ruleset_version": "w04-wyscout-lineup-stint-v1",
                    "start_interval": {"lower": 82, "upper": 83},
                    "stint_ordinal": 0,
                    "suppression_reason": "suppressed_unsupported_denominator",
                    "team_id": "5b353635-819b-5bd1-8ca2-5a7364042a96",
                    "team_source_id": 1_631,
                    "upper_bound_minutes": None,
                }
            ],
            "population_cardinality": 1,
            "population_scope": "ONLY_EXACT_AUTHORIZED_W04_SELECTED_MATCH_PLAYER_LINEUP_STINT",
        },
        "season_binding": {
            "canonical_name": "figshare-v5:181150",
            "canonical_season_id": "4696aa1f-b512-5d18-af79-33cf031455cf",
            "derivation": {
                "algorithm": "UUIDV5",
                "season_namespace": "afb775b9-a955-5bfc-80cd-3e941ca2f098",
                "season_namespace_name": "season",
                "source_namespace": "89161938-1e8c-53ab-ab52-eba969681833",
                "source_namespace_name": wyscout_build.SOURCE_NAMESPACE_NAME,
            },
            "identity_bundle_kind_added": False,
            "season_source_id": 181_150,
            "season_source_json_type": "integer",
            "second_derivation": "FORBIDDEN",
        },
        "source_binding": {
            "completion_index_path": (
                "data/manifests/wyscout/v5/source-completion/"
                "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
                "source-completion-index.json"
            ),
            "completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
            "match_member_path": "archive-members/matches_England.json",
            "match_member_row_count": 380,
            "match_member_sha256": (
                "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29"
            ),
            "match_member_size_bytes": 1_694_720,
            "match_raw_record_sha256": (
                "1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86"
            ),
            "match_source_id": 2_499_719,
            "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
            "source_manifest_path": (
                "data/manifests/wyscout/v5/source/"
                "4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json"
            ),
            "source_manifest_sha256": wyscout_data.SOURCE_MANIFEST_SHA256,
            "source_record_ordinal": 379,
        },
    },
    "source_authority": wyscout_data.accepted_source_authority().model_dump(mode="json"),
    "source_members": _SOURCE_MEMBER_CORPUS,
    "subevent_semantics": {
        "admitted_integer_pairs": _pair_rows(wyscout_data._ADMITTED_EVENT_SUBEVENT_PAIRS),
        "coercion_permitted": False,
        "emitting_runtime_type": "exact_int_excluding_bool",
        "quarantine_reasons_by_union_arm": {
            member.name: member.value for member in wyscout_data.ActionSubeventReason
        },
        "strings_remain_unmapped": True,
    },
    "window_authority": {
        "canonical_match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
        "feature_cutoff_predicate": (
            "EVERY_BOUND_DEPENDENCY_CLOCK_AND_SELECTED_MATCH_START_STRICTLY_BEFORE_"
            "FEATURE_CUTOFF_TS"
        ),
        "feature_cutoff_ts": wyscout_build.FEATURE_CUTOFF_TS,
        "provider_match_id": 2_499_719,
        "selected_match_start_ts": wyscout_build.SELECTED_MATCH_START_TS,
        "snapshot_as_of_ts": wyscout_build.SNAPSHOT_AS_OF_TS,
        "valid_from_rule": "MAX_OF_SNAPSHOT_AS_OF_TS_AND_DEPENDENCY_WATERMARK",
        "window_definition_id": wyscout_build.WINDOW_DEFINITION_ID,
        "window_definition_namespace_algorithm": "UUIDV5_NAMESPACE_URL",
        "window_definition_namespace_name": (
            "urn:scouting-intelligence:w04:wyscout:window-definition:v1"
        ),
        "window_end_utc": wyscout_build.WINDOW_END_UTC,
        "window_identity_byte_length": 250,
        "window_identity_bytes_sha256": (
            "3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327"
        ),
        "window_identity_encoding": (
            "R20_CANONICAL_JSON_UTF8_NFC_WITHOUT_BOM_WHITESPACE_OR_TERMINAL_LF"
        ),
        "window_identity_object": {
            "match_id": "bad97950-6fac-5cf0-a93c-094f91abbb9b",
            "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
            "window_end_utc": wyscout_build.WINDOW_END_UTC,
            "window_schema_version": "w04-single-match-poc-window-v1",
            "window_start_utc": wyscout_build.WINDOW_START_UTC,
        },
        "window_membership_predicate": ("WINDOW_START_UTC_LE_MATCH_START_UTC_LT_WINDOW_END_UTC"),
        "window_schema_version": "w04-single-match-poc-window-v1",
        "window_start_utc": wyscout_build.WINDOW_START_UTC,
    },
}

_PREDICATE_CONSTANT_RESOLVER: dict[str, object] = {
    "C1": {
        "feature_schema_hash": wyscout_data.FEATURE_SCHEMA_HASH,
        "identity_bundle_id": wyscout_build.IDENTITY_BUNDLE_ID,
        "identity_bundle_sha256": wyscout_build.IDENTITY_BUNDLE_SHA256,
        "source_completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        "source_manifest_id": str(wyscout_data.SOURCE_MANIFEST_ID),
        "source_manifest_sha256": wyscout_data.SOURCE_MANIFEST_SHA256,
        "tenant_context": _TENANT_CONSTANTS,
    },
    "C2": _SOURCE_MEMBER_CORPUS,
    "C3": {
        "build_authority_rows": _BUILD_AUTHORITY_ROWS,
        "data_authority_clocks": _DATA_AUTHORITY_CLOCKS,
        "data_authority_rows": _DATA_AUTHORITY_ROWS,
        "source_classification": wyscout_data.accepted_source_classification().model_dump(
            mode="json"
        ),
    },
    "C4": _FROZEN_CONSTANT_CORPUS["field_registry"],
    "C5": {
        "admitted_event_subevent_pairs": _pair_rows(wyscout_data._ADMITTED_EVENT_SUBEVENT_PAIRS)
    },
    "C6": {
        "possession_semantics": _FROZEN_CONSTANT_CORPUS["possession_semantics"],
        "subevent_quarantine_reasons": {
            member.name: member.value for member in wyscout_data.ActionSubeventReason
        },
    },
    "C7": _FROZEN_CONSTANT_CORPUS["completion_index_binding"],
    "C8": {
        "dependency_lineage_hash": wyscout_build.accepted_dependency_lineage_hash(),
        "dependency_rows": _BUILD_DEPENDENCY_ROWS,
    },
    "C9": _FROZEN_CONSTANT_CORPUS["season_and_lineup"],
    "C10": {
        "admission_argv": list(wyscout_build.ADMISSION_ARGV),
        "build_identity": _FROZEN_CONSTANT_CORPUS["build_identity"],
        "component_keys": list(wyscout_build.COMPONENT_KEYS),
        "layer_manifest_authority": _FROZEN_CONSTANT_CORPUS["layer_manifest_authority"],
        "post_hash_invocation_keys": list(wyscout_build.POST_HASH_INVOCATION_KEYS),
        "pre_build_projection_keys": list(wyscout_build.PRE_BUILD_PROJECTION_KEYS),
        "rebuild_argv": list(wyscout_build.REBUILD_ARGV),
        "stable_manifest_keys": list(wyscout_build._STABLE_MANIFEST_KEYS),
        "window_authority": _FROZEN_CONSTANT_CORPUS["window_authority"],
    },
    "C11": {
        "layer_manifest_receipt_composition": _FROZEN_CONSTANT_CORPUS[
            "layer_manifest_receipt_composition"
        ],
        "receipt_contracts": _FROZEN_CONSTANT_CORPUS["receipt_contracts"],
    },
}

_EXTERNAL_AUTHORITY_SOURCES: dict[str, list[dict[str, str]]] = {
    "build_product": [
        {
            "path": (
                "reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json"
            ),
            "sha256": "3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d",
        },
    ],
    "build_receipt": [
        {
            "path": "reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md",
            "sha256": "a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222",
        },
        {
            "path": "src/scouting/contracts/wyscout_build.py",
            "sha256": "e77efd1d11b8ca3b873dee79511142f5fdf12092d9a455eeba0001e9c3faa34f",
        },
    ],
    "completion_reader": [
        {
            "path": (
                "data/manifests/wyscout/v5/source-completion/"
                "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df."
                "source-completion-index.json"
            ),
            "sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        },
        {
            "path": "reports/reviews/W04/wyscout-source-completion-index-correction-R1.md",
            "sha256": "b9b9f8e1c0166f7ca7aecf0c716445d0b8d78e0618bae92db72f1a476394a1e3",
        },
    ],
    "constraint_census": [
        {
            "path": "reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R2.md",
            "sha256": "3ac167f4a63f26d930abe039ec7417637d204f984db6f0cc578dd322526c2120",
        }
    ],
    "season_lineup": [
        {
            "path": (
                "reports/reviews/W04/authorities/"
                "wyscout-season-lineup-product-binding-decisions-v1.json"
            ),
            "sha256": "3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e",
        },
        {
            "path": (
                "reports/reviews/W04/authorities/"
                "wyscout-season-lineup-product-binding-acceptance-v1.json"
            ),
            "sha256": "6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e",
        },
    ],
    "schema_acceptance": [
        {
            "path": "reports/reviews/W04/wyscout-23-root-schema-readiness-audit-R1.md",
            "sha256": "f9961082a27b949da6b9c1647b50f9ce18b6862c66fb8c104826c4b20ca746a0",
        },
        {
            "path": "reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R2.md",
            "sha256": "3ac167f4a63f26d930abe039ec7417637d204f984db6f0cc578dd322526c2120",
        },
        {
            "path": "reports/verification/W04/wyscout-canonical-decimal-arrow-authorization-R1.md",
            "sha256": "cddc7fae1ac256b2312a34dc1291dddebdff35162321b0215580103ba6569b5e",
        },
    ],
}

_EXTERNAL_AUTHORITY_PREDICATES: list[dict[str, object]] = [
    {
        "predicate_id": "E1-source-completion",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["completion_reader"],
        "operation": "GUARDED_INDEX_CONTENT_SOURCE_SCOPE_ORDER_AND_POPULATION_EQUALITY",
        "operands": [
            "frozen_raw_source_bytes",
            "source_completion_index_bytes",
            "supplied_match_period_population",
        ],
        "constants": _FROZEN_CONSTANT_CORPUS["completion_index_binding"],
    },
    {
        "predicate_id": "E2-season-and-lineup",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["season_lineup"],
        "operation": "STRICT_SEASON_UUID_AND_EXACT_ONE_LINEUP_SOURCE_POPULATION_EQUALITY",
        "operands": [
            "guarded_match_source_row",
            "strict_integer_provider_season_id",
            "canonical_season_id",
            "silver_lineup_population",
        ],
        "constants": _FROZEN_CONSTANT_CORPUS["season_and_lineup"],
    },
    {
        "predicate_id": "E3-checked-product-issuance",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["completion_reader"],
        "operation": "ISSUE_CHECKED_SILVER_AND_GOLD_ONLY_AFTER_EXACT_E1_POPULATION_EQUALITY",
        "operands": [
            "semantic_only_unchecked_runtime_rows",
            "accepted_completion_reader_result",
            "causal_source_rows_including_other_player_possession_actions",
        ],
        "constants": {
            "caller_boolean_count_witness_or_digest_is_sufficient": False,
            "required_construction_authority_state": "semantic_only_unchecked",
            "source_completion_index_sha256": wyscout_data.SOURCE_COMPLETION_INDEX_SHA256,
        },
    },
    {
        "predicate_id": "E4-build-projection-composition",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["build_product"],
        "operation": "EXACT_25_KEY_SINGLE_BUILD_HASH_AND_POST_HASH_INVERSE_COMPOSITION",
        "operands": [
            "five_build_authority_rows",
            "five_dependency_rows",
            "pre_build_projection",
            "post_hash_rebuild_invocation",
        ],
        "constants": {
            "authority_composition": _FROZEN_CONSTANT_CORPUS["authority_composition"],
            "build_identity": _FROZEN_CONSTANT_CORPUS["build_identity"],
            "post_hash_invocation_keys": list(wyscout_build.POST_HASH_INVOCATION_KEYS),
            "window_authority": _FROZEN_CONSTANT_CORPUS["window_authority"],
        },
    },
    {
        "predicate_id": "E5-layer-semantic-closure",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["build_receipt"],
        "operation": "GUARD_READ_THREE_COMPLETE_MANIFESTS_AND_DERIVE_SOLE_TWO_KEY_SEMANTIC",
        "operands": [
            "bronze_complete_manifest_physical_bytes",
            "silver_complete_manifest_physical_bytes",
            "gold_complete_manifest_physical_bytes",
            "same_layer_manifest_summaries",
        ],
        "constants": _FROZEN_CONSTANT_CORPUS["layer_manifest_authority"],
    },
    {
        "predicate_id": "E6-parent-and-population-closure",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["build_receipt"],
        "operation": "EXACT_PARENT_CHAIN_GOLD_PRODUCT_AND_BOUNDARY_POPULATION_READBACK",
        "operands": [
            "three_complete_layer_manifests",
            "one_ordered_gold_product_population",
            "one_boundary_population",
            "reopened_gold_and_boundary_bytes",
        ],
        "constants": {
            "layer_manifest_authority": _FROZEN_CONSTANT_CORPUS["layer_manifest_authority"],
            "receipt_contracts": _FROZEN_CONSTANT_CORPUS["receipt_contracts"],
        },
    },
    {
        "predicate_id": "E7-receipt-clocks-and-results",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["build_receipt"],
        "operation": "EXACT_RECEIPT_CLOCK_SUMMARY_BOUNDARY_AND_CHILD_RESULT_COMPOSITION",
        "operands": [
            "three_layer_summaries",
            "one_boundary_receipt",
            "rebuild_invocation_receipt",
            "child_result_envelope",
        ],
        "constants": {
            "clock_relation": "started_at<=checked_at<=completed_at",
            "receipt_contracts": _FROZEN_CONSTANT_CORPUS["receipt_contracts"],
            "substitution_failures": cast(
                dict[str, object], _FROZEN_CONSTANT_CORPUS["layer_manifest_authority"]
            )["substitution_failures"],
        },
    },
    {
        "predicate_id": "E8-schema-acceptance",
        "predicate_classification": "EXTERNAL_COMPOSED_AUTHORITY",
        "authority_sources": _EXTERNAL_AUTHORITY_SOURCES["schema_acceptance"],
        "operation": "EXACT_23_ROOT_DESCRIPTOR_ONLY_SCHEMA_AND_INVERSE_ACCEPTANCE",
        "operands": [
            "twenty_three_canonical_root_contents",
            "twelve_accepted_projection_descriptors",
            "eleven_json_only_roots",
            "valid_model_serialization_matrix",
        ],
        "constants": {
            "canonical_decimal_owner_fields": [
                "GoldCoverageDimension.coverage",
                "GoldCoverage.coverage_overall",
            ],
            "dependency_direction": "EARLIER_ROOTS_ONLY",
            "json_only_root_count": 11,
            "parquet_root_count": 12,
            "root_count": 23,
            "schema_source": "ONLY_ACCEPTED_DESCRIPTOR_NEVER_FIXTURE_OR_ROW_INFERENCE",
            "strict_inverse_before_logical_equality": True,
        },
    },
]

_RUNTIME_PREDICATE_ORACLE_JSONL = r"""
{"constants":["C1","C3"],"declared_owner":"BronzeKnownRecord","operation":"P01","operands":["raw_record","raw_record_sha256","source_row","lineage","measured_raw_fields","tenant_context","classification"],"owner":"BronzeKnownRecord","validator":"raw_record_is_preserved_once"}
{"constants":["L:U+D800..U+DFFF"],"declared_owner":"CanonicalJsonMember","operation":"P02","operands":["key"],"owner":"CanonicalJsonMember","validator":"key_is_unicode_scalar_text"}
{"constants":["L:finite Decimal"],"declared_owner":"CanonicalJsonNumber","operation":"P03","operands":["value"],"owner":"CanonicalJsonNumber","validator":"number_is_finite"}
{"constants":["L:Unicode lexical sort"],"declared_owner":"CanonicalJsonObject","operation":"P04","operands":["value"],"owner":"CanonicalJsonObject","validator":"members_are_unique_and_sorted"}
{"constants":["C8"],"declared_owner":"DependencyLineage","operation":"P05","operands":["dependencies"],"owner":"DependencyLineage","validator":"dependencies_are_unique"}
{"constants":["C3"],"declared_owner":"SourceUseClassification","operation":"P06","operands":["use_class","derived_data_allowed","internal_review_allowed","export_allowed","attribution_required","attribution_text"],"owner":"SourceUseClassification","validator":"prohibit_unlicensed_use"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityClock","operation":"P07","operands":["decided_at","reviewed_at","accepted_at","authority_kind"],"owner":"WyscoutAuthorityClock","validator":"clocks_are_the_accepted_authority_clocks"}
{"constants":["C3"],"declared_owner":"WyscoutAuthorityReference","operation":"P08","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"WyscoutAuthorityReference","validator":"reference_is_the_accepted_authority"}
{"constants":["C1","C3","C8"],"declared_owner":"WyscoutRowLineage","operation":"P09","operands":["source_manifest_id","source_manifest_sha256","source_completion_index_sha256","authority_references","authority_clocks","source_authority","source_rows","dependency_lineage"],"owner":"WyscoutRowLineage","validator":"lineage_is_closed"}
{"constants":["C1","C3"],"declared_owner":"WyscoutSourceAuthority","operation":"P10","operands":["source_manifest_id","source_manifest_sha256","tenant_context","available_at","acquired_at","classification"],"owner":"WyscoutSourceAuthority","validator":"source_authority_is_exact"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P11","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C2"],"declared_owner":"WyscoutSourceRowReference","operation":"P12","operands":["completion_relative_path","record_kind"],"owner":"WyscoutSourceRowReference","validator":"record_kind_matches_completion_path"}
{"constants":["C1","C3"],"declared_owner":"BronzeRejectedRecord","operation":"P13","operands":["raw_record_sha256","raw_record","tenant_context","classification","lineage","source_row"],"owner":"BronzeRejectedRecord","validator":"rejected_record_is_closed"}
{"constants":["L:w04-raw-kind-v1\\x00","L:uint64-be","L:^[A-Za-z][A-Za-z0-9_-]{0,63}$"],"declared_owner":"RawKindEvidence","operation":"P14","operands":["value_present","value","raw_kind_state","envelope_bytes","raw_kind_sha256"],"owner":"RawKindEvidence","validator":"evidence_matches_state_and_framed_digest"}
{"constants":["C1","C2"],"declared_owner":"WyscoutRawSourceRowReference","operation":"P15","operands":["source_manifest_id","completion_relative_path","source_sha256","source_record_ordinal"],"owner":"WyscoutRawSourceRowReference","validator":"source_row_is_manifested"}
{"constants":["C1","C3","C4","C5","C6"],"declared_owner":"BronzeRejectedField","operation":"P16","operands":["source_row","record_kind","original_value","measured_json_type","original_value_sha256","field_authority","json_path","decision","reason_code","action_event_taxonomy_id","classification","tenant_context","lineage"],"owner":"BronzeRejectedField","validator":"rejected_value_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P17","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverCompetition","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(competition)"],"declared_owner":"SilverCompetition","operation":"P18","operands":["source_rows","competition_id","competition_source_id"],"owner":"SilverCompetition","validator":"competition_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P19","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverTeam","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(team)"],"declared_owner":"SilverTeam","operation":"P20","operands":["source_rows","team_id","team_source_id"],"owner":"SilverTeam","validator":"team_identity_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P21","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayer","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:canonical_source_uuid(player)"],"declared_owner":"SilverPlayer","operation":"P22","operands":["source_rows","player_id","player_source_id"],"owner":"SilverPlayer","validator":"player_identity_is_exact_and_nonzero"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P23","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverMatch","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C2","L:canonical_source_uuid(match)","L:UUID.bytes sort"],"declared_owner":"SilverMatch","operation":"P24","operands":["source_rows","source_partition","match_id","match_source_id","team_ids"],"owner":"SilverMatch","validator":"match_identity_and_teams_are_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P25","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverAction","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:decimal128(22,18)"],"declared_owner":"SilverAction","operation":"P26","operands":["source_rows","action_id","action_source_id","source_event_record_id","source_record_ordinal","period_elapsed_seconds","event_sec_source_scale","action_tag_ids","action_subevent_taxonomy_id","action_event_taxonomy_id","team_id","possession_predicate_state","possession_period_sequence","match_id","action_period_code","lineage","player_id","period_rank","possession_eligibility_state"],"owner":"SilverAction","validator":"action_is_strict_and_orderable"}
{"constants":["L:decimal128(22,18)","L:[0,100]"],"declared_owner":"ActionPosition","operation":"P27","operands":["x","y","within_accepted_bounds"],"owner":"ActionPosition","validator":"bound_flag_preserves_anomalies_without_clamping"}
{"constants":["C1"],"declared_owner":"PossessionPeriodSequence","operation":"P28","operands":["source_completion_index_sha256","period_action_count","actions","match_id","action_period_code"],"owner":"PossessionPeriodSequence","validator":"period_sequence_is_complete_unique_and_ordered"}
{"constants":["L:canonical_source_uuid(action)","L:canonical action order"],"declared_owner":"PossessionSequenceAction","operation":"P29","operands":["source_row","source_record_ordinal","action_id","source_event_record_id","period_elapsed_seconds","action_tag_ids"],"owner":"PossessionSequenceAction","validator":"sequence_action_is_exact"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P30","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverLineupStint","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["L:half-open nominal minute"],"declared_owner":"SilverLineupStint","operation":"P31","operands":["source_rows","start_interval","end_interval","right_censored","lower_bound_minutes","upper_bound_minutes"],"owner":"SilverLineupStint","validator":"stint_bounds_are_interval_derived"}
{"constants":["L:upper=lower+1"],"declared_owner":"NominalMinuteInterval","operation":"P32","operands":["upper","lower"],"owner":"NominalMinuteInterval","validator":"interval_is_one_nominal_minute"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P33","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPossession","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C5","C6","L:equal-clock group-first"],"declared_owner":"SilverPossession","operation":"P34","operands":["contributing_actions","team_id","build_id","tenant_context","lineage","match_id","action_period_code","source_rows","action_ids","first_action_order","last_action_order"],"owner":"SilverPossession","validator":"possession_is_one_ordered_same_period_sequence"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P35","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"SilverPlayerMatchFact","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","L:fact derivations"],"declared_owner":"SilverPlayerMatchFact","operation":"P36","operands":["source_manifest_id","contributing_lineup_stints","build_id","tenant_context","lineage","match_id","player_id","match_team_id","lineup_evidence_present","contributing_actions","competition_id","contributing_possessions","source_rows","action_count","coordinate_known_action_count","resolved_possession_action_count","temporal_proof","match_start_utc","coverage","right_censored_or_uncertain","applicability"],"owner":"SilverPlayerMatchFact","validator":"player_match_key_and_state_are_exact"}
{"constants":["L:six CoverageDimensionName values"],"declared_owner":"GoldCoverage","operation":"P37","operands":["dimensions","missing_dimensions","coverage_overall"],"owner":"GoldCoverage","validator":"six_dimensions_are_exact"}
{"constants":["C3","L:precision-38 exact division"],"declared_owner":"GoldCoverageDimension","operation":"P38","operands":["numerator","denominator","reason_codes","state","coverage","zero_denominator_authority","name"],"owner":"GoldCoverageDimension","validator":"coverage_is_exact"}
{"constants":["L:W04_DATA_READY"],"declared_owner":"W04ApplicabilityAssessment","operation":"P39","operands":["reason_codes","state"],"owner":"W04ApplicabilityAssessment","validator":"reasons_are_sorted_unique"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"W04SemanticTemporalProof","operation":"P40","operands":["dependency_lineage","source_completion_index_sha256","source_authority","authority_clocks","feature_cutoff_ts","available_at_watermark","valid_from_ts","snapshot_as_of_ts","dependency_lineage_hash","source_manifest_ids","feature_schema_hash"],"owner":"W04SemanticTemporalProof","validator":"proof_has_exact_five_strict_dependencies"}
{"constants":["C1"],"declared_owner":"WyscoutProductRow","operation":"P41","operands":["tenant_context","source_completion_index_sha256","lineage","source_rows"],"owner":"GoldPlayerWindow","validator":"tenant_is_the_fixed_poc_context"}
{"constants":["C1","C8","C10","L:four-feature sums"],"declared_owner":"GoldPlayerWindow","operation":"P42","operands":["role_context_id","role_context_version","role_context_state","window_start_utc","window_end_utc","feature_cutoff_ts","temporal_proof","dependency_lineage_hash","lineage","feature_schema_hash","contributing_player_match_facts","contributing_player_match_keys","build_id","tenant_context","player_id","competition_id","season_id","source_rows","features","coverage","applicability"],"owner":"GoldPlayerWindow","validator":"gold_key_and_feature_state_are_exact"}
{"constants":["L:component<=action"],"declared_owner":"GoldFeatureValues","operation":"P43","operands":["coordinate_known_action_count","action_count","resolved_possession_action_count"],"owner":"GoldFeatureValues","validator":"component_counts_cannot_exceed_actions"}
{"constants":["C1","C3","C8","C10"],"declared_owner":"LayerManifest","operation":"P44","operands":["manifest_path","layer","source_manifest_id","source_manifest_sha256","source_completion_index_sha256","build_id","tenant_context","classification","source_available_at","source_acquired_at","authority_clocks","feature_schema_hash","dependency_lineage","dependency_lineage_hash","entries","parent_layer_manifests"],"owner":"LayerManifest","validator":"layer_order_and_entries_are_exact"}
{"constants":["C3","C10"],"declared_owner":"LayerManifestEntry","operation":"P45","operands":["serializer","path","schema_role","partition_values","classification","ordered_parent_paths"],"owner":"LayerManifestEntry","validator":"entry_binds_owner_rights_and_partition_order"}
{"constants":["C10"],"declared_owner":"ParentLayerManifest","operation":"P46","operands":["layer","build_id","relative_path"],"owner":"ParentLayerManifest","validator":"parent_path_is_exact_and_safe"}
{"constants":["C10","L:NFC","L:canonical UUID/UTC"],"declared_owner":"WyscoutProductPath","operation":"P47","operands":["relative_path","path_role"],"owner":"WyscoutProductPath","validator":"path_is_the_exact_role_template"}
{"constants":["C10","L:SHA256(path UTF-8)"],"declared_owner":"TemporalBoundaryReceipt","operation":"P48","operands":["gold_manifest_relative_path","gold_product_relative_path","build_id","gold_relative_path_sha256"],"owner":"TemporalBoundaryReceipt","validator":"exact_paths"}
{"constants":["C10","C11"],"declared_owner":"RebuildInvocationReceipt","operation":"P49","operands":["build_id","rebuild_invocation","started_at","completed_at","layer_manifests","boundary_receipts","run_id"],"owner":"RebuildInvocationReceipt","validator":"exact_receipt"}
{"constants":["C3"],"declared_owner":"AuthorityRow","operation":"P50","operands":["acceptance_id","acceptance_sha256","authority_kind","candidate_id","candidate_sha256","review_id","review_sha256"],"owner":"AuthorityRow","validator":"equals_accepted_row"}
{"constants":["C8"],"declared_owner":"DependencyRow","operation":"P51","operands":["observed_at","available_at"],"owner":"DependencyRow","validator":"clocks_are_ordered"}
{"constants":["C3","C8","C10","L:single build hash"],"declared_owner":"RebuildInvocation","operation":"P52","operands":["authority_rows","dependency_rows","code_manifest_id","code_manifest_sha256","product_contract_digest","schema_bundle_digest","build_id"],"owner":"RebuildInvocation","validator":"exact_invocation"}
{"constants":["C10"],"declared_owner":"EntrypointSourceResult","operation":"P53","operands":["role","relative_path"],"owner":"EntrypointSourceResult","validator":"exact_role_path"}
{"constants":["C10","L:SHA256 canonical JSON","L:base64url"],"declared_owner":"PreBuildAdmissionResult","operation":"P54","operands":["admission_run_id","admission_prefix_relative_path","component_proofs","component_proofs_sha256","canonical_manifest_bytes_b64u","canonical_manifest_sha256","manifest_schema_version","repository_code_sha256","environment_digest"],"owner":"PreBuildAdmissionResult","validator":"exact_admission_result"}
{"constants":["C10","C11","L:SHA256 canonical JSON"],"declared_owner":"PostBuildIdRebuildResult","operation":"P55","operands":["build_id","run_id","rebuild_prefix_relative_path","rebuild_receipt","layer_manifests","final_recheck"],"owner":"PostBuildIdRebuildResult","validator":"exact_rebuild_result"}
{"constants":["C10","L:SHA256 ordered argv"],"declared_owner":"ChildResultEnvelope","operation":"P56","operands":["entrypoint_source","child_role","payload_kind","result","expected_repository_code_sha256","child_environment_sha256","ordered_argv_sha256"],"owner":"ChildResultEnvelope","validator":"exact_role_payload_binding"}
{"constants":["L:NFC without controls","L:safe root-independent non-PYC site path","L:strict sys.modules key or DYLD_IMAGE"],"declared_owner":"RuntimeSubsetObservation","operation":"P57","operands":["owner_version","site_relative_path","observation_kind","subject_name"],"owner":"RuntimeSubsetObservation","validator":"exact_runtime_observation"}
{"constants":["L:w04-normalized-runtime-subset-observations-v1","L:canonical-byte sorted unique cardinality 1..100000","L:SHA256 canonical JSON and nonempty owner projection"],"declared_owner":"FinalRecheckResult","operation":"P58","operands":["runtime_subset_rows","runtime_subset_digest"],"owner":"FinalRecheckResult","validator":"exact_runtime_subset"}
""".removeprefix("\n")
_RUNTIME_PREDICATE_ORACLE_SHA256 = (
    "5a787de72cdad220a6e609c9ca713df33830e4afa7845b4b2e5de3df87d57d2b"
)


def _load_runtime_predicate_oracle() -> tuple[dict[str, object], ...]:
    encoded = _RUNTIME_PREDICATE_ORACLE_JSONL.encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != _RUNTIME_PREDICATE_ORACLE_SHA256:
        raise W04SchemaClosureError("runtime predicate oracle bytes do not reproduce")
    rows = tuple(json.loads(line) for line in _RUNTIME_PREDICATE_ORACLE_JSONL.splitlines())
    if len(rows) != 58:
        raise W04SchemaClosureError("runtime predicate oracle is not exactly 58 rows")
    keys: set[tuple[str, str]] = set()
    for index, row in enumerate(rows, start=1):
        if type(row) is not dict or tuple(row) != (
            "constants",
            "declared_owner",
            "operation",
            "operands",
            "owner",
            "validator",
        ):
            raise W04SchemaClosureError("runtime predicate oracle row shape differs")
        if row["operation"] != f"P{index:02d}":
            raise W04SchemaClosureError("runtime predicate oracle operation order differs")
        if type(row["operands"]) is not list or not row["operands"]:
            raise W04SchemaClosureError("runtime predicate oracle operands are empty")
        if type(row["constants"]) is not list or not row["constants"]:
            raise W04SchemaClosureError("runtime predicate oracle constants are empty")
        key = (cast(str, row["owner"]), cast(str, row["validator"]))
        if key in keys:
            raise W04SchemaClosureError("runtime predicate oracle binding is duplicated")
        keys.add(key)
    return cast(tuple[dict[str, object], ...], rows)


@cache
def _runtime_predicate_oracle() -> tuple[dict[str, object], ...]:
    return _load_runtime_predicate_oracle()


@cache
def _runtime_predicate_oracle_by_binding() -> dict[tuple[str, str], dict[str, object]]:
    return {
        (cast(str, row["owner"]), cast(str, row["validator"])): row
        for row in _runtime_predicate_oracle()
    }


@cache
def _model_registry() -> dict[str, type[BaseModel]]:
    registry: dict[str, type[BaseModel]] = {}
    for module in (primitives, evidence, wyscout_data, wyscout_build):
        for value in vars(module).values():
            if inspect.isclass(value) and issubclass(value, BaseModel):
                registry.setdefault(value.__name__, value)
    for model in _ROOT_MODELS:
        registry[model.__name__] = model
    return registry


def _declared_validator_owner(model: type[BaseModel], validator_name: str) -> str:
    for candidate in model.__mro__:
        if (
            inspect.isclass(candidate)
            and issubclass(candidate, BaseModel)
            and validator_name in candidate.__dict__
        ):
            return candidate.__name__
    raise W04SchemaClosureError(
        f"runtime validator {model.__name__}.{validator_name} has no declaring model"
    )


def _model_predicates(model: type[BaseModel]) -> list[dict[str, object]]:
    predicates: list[dict[str, object]] = []
    for index, validator_name in enumerate(model.__pydantic_decorators__.model_validators):
        try:
            oracle_row = _runtime_predicate_oracle_by_binding()[(model.__name__, validator_name)]
        except KeyError as error:
            raise W04SchemaClosureError(
                f"runtime validator {model.__name__}.{validator_name} has no declarative predicate"
            ) from error
        declared_owner = _declared_validator_owner(model, validator_name)
        if oracle_row["declared_owner"] != declared_owner:
            raise W04SchemaClosureError(
                f"runtime validator {model.__name__}.{validator_name} declaring model differs"
            )
        predicates.append(
            _predicate(
                model.__name__,
                declared_owner,
                validator_name,
                f"{model.__name__.lower()}-predicate-{index:02d}",
                cast(str, oracle_row["operation"]),
                tuple(cast(list[str], oracle_row["operands"])),
                tuple(cast(list[str], oracle_row["constants"])),
            )
        )
    return predicates


def _normalize_logical_schema(value: object) -> object:
    if type(value) is list:
        return [_normalize_logical_schema(item) for item in value]
    if type(value) is not dict:
        return value
    normalized: dict[str, object] = {}
    for key, item in value.items():
        if key in {"title", "default"}:
            continue
        normalized[key] = _normalize_logical_schema(item)
    properties = normalized.get("properties")
    if type(properties) is dict:
        field_order = list(properties)
        normalized["serialized_field_order"] = field_order
        normalized["required"] = field_order
        normalized["additionalProperties"] = False
    return normalized


def _augment_definition(definition_id: str, schema: dict[str, object]) -> None:
    model_registry = _model_registry()
    if definition_id in model_registry:
        schema["predicates"] = _model_predicates(model_registry[definition_id])
    if schema.get("type") == "string":
        schema["unicode_normalization"] = "NFC"
        schema["unicode_scalar_values_only"] = True
    if definition_id == "UtcInstant":
        schema["canonical_timestamp"] = {
            "timezone": "UTC",
            "unit": "MICROSECOND",
            "suffix": "Z",
        }
    elif definition_id == "StrictDecimal":
        schema["decimal_rules"] = {
            "finite": True,
            "json_representation": "CANONICAL_DECIMAL_STRING",
        }
    elif definition_id in {"StrictUuid", "TenantId"}:
        schema["canonical_uuid_text"] = "LOWERCASE_HYPHENATED_RFC4122"


def _logical_definitions(root_model: type[BaseModel]) -> dict[str, object]:
    generated = root_model.model_json_schema(mode="serialization")
    raw_definitions = generated.pop("$defs", {})
    generated.pop("title", None)
    if set(generated) == {"$ref"}:
        root_ref = generated["$ref"]
        if type(root_ref) is not str or not root_ref.startswith("#/$defs/"):
            raise W04SchemaClosureError("root schema reference is not local and exact")
        root_schema = raw_definitions.pop(root_ref.removeprefix("#/$defs/"))
    else:
        root_schema = generated
    schemas: dict[str, object] = {root_model.__name__: _normalize_logical_schema(root_schema)}
    for definition_id, definition in raw_definitions.items():
        schemas[definition_id] = _normalize_logical_schema(definition)
    for definition_id, schema in schemas.items():
        if type(schema) is not dict:
            raise W04SchemaClosureError(f"definition {definition_id} is not one object")
        _augment_definition(definition_id, schema)
    return {
        "constant_corpus": _FROZEN_CONSTANT_CORPUS,
        "definition_order": list(schemas),
        "external_authority_predicates": _EXTERNAL_AUTHORITY_PREDICATES,
        "predicate_constant_resolver": _PREDICATE_CONSTANT_RESOLVER,
        "schemas": schemas,
        "serialization_contract": {
            "additional_fields": "FORBIDDEN",
            "canonical_json": "R20_CANONICAL_JSON_WITHOUT_TERMINAL_LF",
            "defaulted_fields": "REQUIRED_IN_SERIALIZED_FORM",
            "object_key_order": "UNICODE_CODE_POINT_ASCENDING_IN_CANONICAL_BYTES",
            "string_normalization": "NFC_UNICODE_SCALAR_VALUES_ONLY",
        },
    }


def _unwrap_alias(annotation: object) -> tuple[object, str | None]:
    alias_name: str | None = None
    while isinstance(annotation, TypeAliasType):
        alias_name = annotation.__name__
        annotation = annotation.__value__
    while get_origin(annotation) is getattr(__import__("typing"), "Annotated"):
        annotation = get_args(annotation)[0]
    return annotation, alias_name


def _split_nullable(annotation: object) -> tuple[object, bool]:
    annotation, _alias_name = _unwrap_alias(annotation)
    origin = get_origin(annotation)
    if origin in {Union, types.UnionType}:
        arguments = get_args(annotation)
        non_null = tuple(argument for argument in arguments if argument is not type(None))
        if len(non_null) == 1 and len(non_null) != len(arguments):
            return non_null[0], True
    if annotation is type(None):
        return annotation, True
    return annotation, False


def _scalar_node(
    scalar_type: str,
    *,
    projection_kind: str = "IDENTITY",
    decimal_precision: int | None = None,
    decimal_scale: int | None = None,
) -> dict[str, object]:
    return {
        "node_kind": "SCALAR",
        "scalar_type": scalar_type,
        "projection_kind": projection_kind,
        "decimal_precision": decimal_precision,
        "decimal_scale": decimal_scale,
    }


def _exact_decimal128_with_exponent_node() -> dict[str, object]:
    return {
        "node_kind": "STRUCT",
        "projection_kind": "EXACT_DECIMAL128_WITH_EXPONENT",
        "children": [
            {
                "name": "value",
                "nullable": False,
                "node": _scalar_node(
                    "DECIMAL128",
                    decimal_precision=22,
                    decimal_scale=18,
                ),
                "logical_position": None,
            },
            {
                "name": "exponent",
                "nullable": False,
                "node": _scalar_node("INT8"),
                "logical_position": None,
            },
            {
                "name": "negative_zero",
                "nullable": False,
                "node": _scalar_node("BOOL"),
                "logical_position": None,
            },
        ],
    }


def _projection_field(
    name: str,
    annotation: object,
    *,
    logical_position: int | None = None,
    owner_model: type[BaseModel] | None = None,
) -> dict[str, object]:
    if (owner_model, name) in {
        (wyscout_data.GoldCoverageDimension, "coverage"),
        (wyscout_data.GoldCoverage, "coverage_overall"),
    }:
        base, nullable = _split_nullable(annotation)
        if base is not Decimal and not (
            isinstance(base, TypeAliasType) and base.__name__ == "StrictDecimal"
        ):
            unwrapped, alias_name = _unwrap_alias(base)
            if unwrapped is not Decimal or alias_name != "StrictDecimal":
                raise W04SchemaClosureError("canonical coverage Decimal logical type drifted")
        return {
            "name": name,
            "nullable": nullable,
            "node": _scalar_node("UTF8", projection_kind="CANONICAL_DECIMAL_UTF8"),
            "logical_position": logical_position,
        }
    if annotation is wyscout_data.CanonicalJsonValue or annotation in _CANONICAL_JSON_TYPES:
        return {
            "name": name,
            "nullable": False,
            "node": _scalar_node("UTF8", projection_kind="CANONICAL_JSON_VALUE_UTF8"),
            "logical_position": logical_position,
        }
    base, nullable = _split_nullable(annotation)
    return {
        "name": name,
        "nullable": nullable,
        "node": _projection_node(base),
        "logical_position": logical_position,
    }


def _projection_node(annotation: object) -> dict[str, object]:
    if annotation is wyscout_data.CanonicalJsonValue or annotation in _CANONICAL_JSON_TYPES:
        return _scalar_node("UTF8", projection_kind="CANONICAL_JSON_VALUE_UTF8")
    annotation, alias_name = _unwrap_alias(annotation)
    if alias_name == "UtcInstant":
        return _scalar_node("TIMESTAMP_US_UTC")
    if alias_name == "StrictDecimal":
        return _exact_decimal128_with_exponent_node()
    if alias_name in {"StrictPositiveInt", "StrictNonNegativeInt", "CanonicalTeamId"}:
        base, _nullable = _split_nullable(annotation)
        return _projection_node(base)
    if alias_name in {"StrictUuid", "TenantId"}:
        return _scalar_node("UTF8")

    origin = get_origin(annotation)
    if origin in {Union, types.UnionType}:
        arguments = tuple(
            argument for argument in get_args(annotation) if argument is not type(None)
        )
        if len(arguments) == 1:
            return _projection_node(arguments[0])
        raise W04SchemaClosureError(f"unrecognized heterogeneous Arrow union {annotation!r}")
    if origin is Literal:
        values = get_args(annotation)
        if values and all(isinstance(value, Enum) for value in values):
            values = tuple(value.value for value in values)
        value_types = {type(value) for value in values}
        if value_types == {str}:
            return _scalar_node("UTF8")
        if value_types == {bool}:
            return _scalar_node("BOOL")
        if value_types == {int}:
            return _scalar_node("INT64")
        if values == (None,):
            return _scalar_node("NULL")
        raise W04SchemaClosureError(f"unrecognized literal Arrow type {annotation!r}")
    if origin in {tuple, list, Sequence}:
        arguments = get_args(annotation)
        if not arguments:
            raise W04SchemaClosureError("untyped sequences are forbidden")
        if origin is tuple and arguments[-1:] != (Ellipsis,):
            if all(argument == arguments[0] for argument in arguments):
                item = _projection_field("item", arguments[0])
                return {
                    "node_kind": "LIST",
                    "projection_kind": "HOMOGENEOUS_LIST",
                    "list_kind": "FIXED_SIZE_LIST",
                    "item": item,
                    "fixed_size": len(arguments),
                }
            children = [
                _projection_field(
                    f"position_{index}",
                    argument,
                    logical_position=index,
                )
                for index, argument in enumerate(arguments)
            ]
            return {
                "node_kind": "STRUCT",
                "projection_kind": "POSITIONAL_TUPLE_STRUCT",
                "children": children,
            }
        item_annotation = arguments[0]
        return {
            "node_kind": "LIST",
            "projection_kind": "HOMOGENEOUS_LIST",
            "list_kind": "LIST",
            "item": _projection_field("item", item_annotation),
            "fixed_size": None,
        }
    if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
        return {
            "node_kind": "STRUCT",
            "projection_kind": "OBJECT_STRUCT",
            "children": [
                _projection_field(name, field.annotation, owner_model=annotation)
                for name, field in annotation.model_fields.items()
            ],
        }
    if inspect.isclass(annotation) and issubclass(annotation, Enum):
        value_types = {type(member.value) for member in annotation}
        if value_types == {str}:
            return _scalar_node("UTF8")
        if value_types == {int}:
            return _scalar_node("INT64")
        raise W04SchemaClosureError(f"unrecognized enum Arrow type {annotation!r}")
    if annotation is type(None):
        return _scalar_node("NULL")
    if annotation is bool:
        return _scalar_node("BOOL")
    if annotation is int:
        return _scalar_node("INT64")
    if annotation is float:
        return _scalar_node("FLOAT64")
    if annotation in {str, UUID, bytes}:
        return _scalar_node("UTF8")
    if annotation is Decimal:
        return _exact_decimal128_with_exponent_node()
    if annotation is datetime:
        return _scalar_node("TIMESTAMP_US_UTC")
    raise W04SchemaClosureError(f"unrecognized Arrow logical type {annotation!r}")


def _parquet_projection(root_role: str, root_model: type[BaseModel]) -> dict[str, object]:
    descriptor = {
        "schema_role": w04_canonical_schema_id(root_role),
        "serializer_version": W04_PARQUET_SERIALIZER_VERSION,
        "fields": [
            _projection_field(name, field.annotation, owner_model=root_model)
            for name, field in root_model.model_fields.items()
        ],
    }
    return {
        "descriptor": descriptor,
        "forward_projection": {
            "CANONICAL_DECIMAL_UTF8": (
                "EXACT_FINITE_DECIMAL_FIXED_POINT_CANONICAL_UTF8_WITHOUT_TERMINAL_LF"
            ),
            "CANONICAL_JSON_VALUE_UTF8": ("EXACT_TAGGED_CANONICAL_JSON_UTF8_WITHOUT_TERMINAL_LF"),
            "EXACT_DECIMAL128_WITH_EXPONENT": (
                "EXACT_FINITE_DECIMAL_TO_ORDERED_DECIMAL128_22_18_INT8_BOOL_STRUCT_WITHOUT_ROUNDING"
            ),
            "HOMOGENEOUS_LIST": "ORDER_PRESERVING_EXACT_CARDINALITY_LIST",
            "IDENTITY": "EXACT_LOGICAL_SCALAR_OR_OBJECT_VALUE",
            "OBJECT_STRUCT": "EXACT_NAMED_FIELD_ORDER_TYPE_AND_NULLABILITY",
            "POSITIONAL_TUPLE_STRUCT": "ZERO_BASED_POSITION_TO_EXACT_NAMED_CHILD",
        },
        "inverse_decoding": {
            "CANONICAL_DECIMAL_UTF8": [
                "STRICT_UTF8_DECODE",
                "DIRECT_DECIMAL_PARSE",
                "REJECT_NONFINITE",
                "CANONICAL_FIXED_POINT_REENCODE_WITHOUT_TERMINAL_LF",
                "BYTE_FOR_BYTE_EQUALITY",
            ],
            "CANONICAL_JSON_VALUE_UTF8": [
                "STRICT_UTF8_DECODE",
                "REJECT_DUPLICATE_KEYS_AND_INVALID_CONSTANTS",
                "STRICT_TYPED_DISCRIMINATED_VALIDATION",
                "CANONICAL_REENCODE_WITHOUT_TERMINAL_LF",
                "BYTE_FOR_BYTE_EQUALITY",
            ],
            "EXACT_DECIMAL128_WITH_EXPONENT": [
                "REQUIRE_EXACT_ORDERED_NON_NULL_METADATA_FREE_CHILDREN",
                "REJECT_NONZERO_NEGATIVE_ZERO",
                "TRAPPING_NO_ROUNDING_EXPONENT_RECONSTRUCTION",
                "RERUN_DECIMAL128_22_18_CAPACITY_AND_SOURCE_SCALE_VALIDATION",
                "EXACT_LOGICAL_JSON_BYTE_REPRODUCTION",
            ],
            "HOMOGENEOUS_LIST": "EXACT_CHILD_DECODE_PRESERVING_ORDER_AND_CARDINALITY",
            "IDENTITY": "EXACT_LOGICAL_TYPE_VALIDATION",
            "OBJECT_STRUCT": "EXACT_CHILD_DECODE_BY_ACCEPTED_FIELD_ORDER",
            "POSITIONAL_TUPLE_STRUCT": "EXACT_CHILD_DECODE_TO_LOGICAL_POSITION_ORDER",
        },
        "metadata_policy": "ABSENT_AT_SCHEMA_FIELD_STRUCT_AND_LIST_LEVELS",
        "schema_source": "ONLY_THIS_CANONICAL_ROOT_CONTENT",
    }


def _build_content(root_role: str, root_model: type[BaseModel], index: int) -> dict[str, object]:
    return {
        "canonical_schema_id": w04_canonical_schema_id(root_role),
        "canonical_schema_version": W04_CANONICAL_SCHEMA_VERSION,
        "schema_language_version": W04_SCHEMA_LANGUAGE_VERSION,
        "root_role": root_role,
        "root_definition_id": root_model.__name__,
        "definitions": _logical_definitions(root_model),
        "parquet_projection": (
            _parquet_projection(root_role, root_model)
            if index < _JSON_ONLY_START_INDEX
            else W04_JSON_ONLY_PROJECTION_STATE
        ),
    }


def _iter_refs(value: object) -> Sequence[str]:
    refs: list[str] = []
    if type(value) is dict:
        for key, item in value.items():
            if key == "$ref" and type(item) is str:
                refs.append(item)
            else:
                refs.extend(_iter_refs(item))
    elif type(value) is list:
        for item in value:
            refs.extend(_iter_refs(item))
    return refs


def _validate_projection_field_content(field: object, *, tuple_position: int | None) -> None:
    if type(field) is not dict or tuple(field) != (
        "name",
        "nullable",
        "node",
        "logical_position",
    ):
        raise W04SchemaClosureError("projection field content keys are not exact")
    if type(field["name"]) is not str or not _FIELD_NAME.fullmatch(field["name"]):
        raise W04SchemaClosureError("projection field name is not canonical")
    if type(field["nullable"]) is not bool:
        raise W04SchemaClosureError("projection field nullability is not Boolean")
    if tuple_position is None:
        if field["logical_position"] is not None:
            raise W04SchemaClosureError("non-tuple field has a logical position")
    elif type(field["logical_position"]) is not int or field["logical_position"] != tuple_position:
        raise W04SchemaClosureError("tuple logical position is not exact")
    _validate_projection_node_content(field["node"])


def _validate_projection_node_content(node: object) -> None:
    if type(node) is not dict:
        raise W04SchemaClosureError("projection node is not one exact object")
    kind = node.get("node_kind")
    if kind == "SCALAR":
        if tuple(node) != (
            "node_kind",
            "scalar_type",
            "projection_kind",
            "decimal_precision",
            "decimal_scale",
        ):
            raise W04SchemaClosureError("scalar node keys are not exact")
        admitted = {
            "NULL",
            "BOOL",
            "INT8",
            "INT16",
            "INT32",
            "INT64",
            "UINT8",
            "UINT16",
            "UINT32",
            "UINT64",
            "FLOAT16",
            "FLOAT32",
            "FLOAT64",
            "UTF8",
            "DECIMAL128",
            "TIMESTAMP_US_UTC",
        }
        if node["scalar_type"] not in admitted:
            raise W04SchemaClosureError("scalar width/type is not admitted")
        if node["projection_kind"] not in {
            "IDENTITY",
            "CANONICAL_JSON_VALUE_UTF8",
            "CANONICAL_DECIMAL_UTF8",
        }:
            raise W04SchemaClosureError("scalar projection kind is not admitted")
        if (
            node["projection_kind"]
            in {
                "CANONICAL_JSON_VALUE_UTF8",
                "CANONICAL_DECIMAL_UTF8",
            }
            and node["scalar_type"] != "UTF8"
        ):
            raise W04SchemaClosureError("canonical logical text must project to UTF8")
        if node["scalar_type"] == "DECIMAL128":
            if (node["decimal_precision"], node["decimal_scale"]) != (22, 18):
                raise W04SchemaClosureError("decimal precision/scale is not exact")
        elif node["decimal_precision"] is not None or node["decimal_scale"] is not None:
            raise W04SchemaClosureError("non-decimal scalar has decimal state")
        return
    if kind == "STRUCT":
        if tuple(node) != ("node_kind", "projection_kind", "children"):
            raise W04SchemaClosureError("struct node keys are not exact")
        if node["projection_kind"] not in {
            "EXACT_DECIMAL128_WITH_EXPONENT",
            "OBJECT_STRUCT",
            "POSITIONAL_TUPLE_STRUCT",
        }:
            raise W04SchemaClosureError("struct projection kind is not admitted")
        children = node["children"]
        if type(children) is not list or not children:
            raise W04SchemaClosureError("struct children are empty or malformed")
        if node["projection_kind"] == "EXACT_DECIMAL128_WITH_EXPONENT":
            if node != _exact_decimal128_with_exponent_node():
                raise W04SchemaClosureError("exact Decimal struct requires exact ordered children")
            for child in children:
                _validate_projection_field_content(child, tuple_position=None)
            return
        positional = node["projection_kind"] == "POSITIONAL_TUPLE_STRUCT"
        for index, child in enumerate(children):
            _validate_projection_field_content(child, tuple_position=index if positional else None)
        names = [child["name"] for child in children]
        if len(set(names)) != len(names):
            raise W04SchemaClosureError("struct child names are not unique")
        return
    if kind == "LIST":
        if tuple(node) != (
            "node_kind",
            "projection_kind",
            "list_kind",
            "item",
            "fixed_size",
        ):
            raise W04SchemaClosureError("list node keys are not exact")
        if node["projection_kind"] != "HOMOGENEOUS_LIST":
            raise W04SchemaClosureError("list projection kind is not exact")
        if node["list_kind"] not in {"LIST", "LARGE_LIST", "FIXED_SIZE_LIST"}:
            raise W04SchemaClosureError("list kind is not admitted")
        if node["list_kind"] == "FIXED_SIZE_LIST":
            if type(node["fixed_size"]) is not int or node["fixed_size"] <= 0:
                raise W04SchemaClosureError("fixed list cardinality is not exact")
        elif node["fixed_size"] is not None:
            raise W04SchemaClosureError("variable list has fixed-size state")
        _validate_projection_field_content(node["item"], tuple_position=None)
        return
    raise W04SchemaClosureError("projection node kind is unrecognized")


def _validate_predicate_constant_resolver(resolver: object) -> None:
    expected_keys = tuple(f"C{index}" for index in range(1, 12))
    if type(resolver) is not dict or tuple(resolver) != expected_keys:
        raise W04SchemaClosureError("predicate constant resolver keys or order differ")
    for key, material in resolver.items():
        if type(material) not in {dict, list} or not material:
            raise W04SchemaClosureError(f"predicate constant resolver {key} is empty")
        _validate_json_value(material, location=f"$.predicate_constant_resolver.{key}")

    referenced: set[str] = set()
    for row in _runtime_predicate_oracle():
        constants = cast(list[str], row["constants"])
        if len(constants) != len(set(constants)):
            raise W04SchemaClosureError("runtime predicate constants contain a duplicate")
        constant_refs = [constant for constant in constants if constant.startswith("C")]
        literal_refs = [constant for constant in constants if constant.startswith("L:")]
        if len(constant_refs) + len(literal_refs) != len(constants):
            raise W04SchemaClosureError("runtime predicate constant reference is unrecognized")
        if constants != constant_refs + literal_refs:
            raise W04SchemaClosureError("runtime predicate constants are not C-before-L ordered")
        try:
            ordered_refs = sorted(constant_refs, key=lambda value: int(value[1:]))
        except ValueError as error:
            raise W04SchemaClosureError(
                "runtime predicate constant reference is malformed"
            ) from error
        if constant_refs != ordered_refs:
            raise W04SchemaClosureError("runtime predicate C references are reordered")
        if any(reference not in resolver for reference in constant_refs):
            raise W04SchemaClosureError("runtime predicate constant reference is unresolved")
        if any(len(literal) == 2 for literal in literal_refs):
            raise W04SchemaClosureError("runtime predicate literal is empty")
        referenced.update(constant_refs)
    external_materials = [predicate["constants"] for predicate in _EXTERNAL_AUTHORITY_PREDICATES]
    for reference, material in resolver.items():
        if any(material == external_material for external_material in external_materials):
            referenced.add(reference)
    if referenced != set(expected_keys):
        raise W04SchemaClosureError("predicate constant resolver has missing or unused material")


def _validate_runtime_predicate_ledger(contents: tuple[dict[str, object], ...]) -> None:
    observed: dict[tuple[str, str], dict[str, object]] = {}
    for content in contents:
        definitions = cast(dict[str, object], content["definitions"])
        schemas = cast(dict[str, dict[str, object]], definitions["schemas"])
        for schema in schemas.values():
            for predicate in cast(list[dict[str, object]], schema.get("predicates", [])):
                if tuple(predicate) != (
                    "owner_model",
                    "declared_owner_model",
                    "validator_name",
                    "predicate_id",
                    "predicate_classification",
                    "authority_sources",
                    "operation",
                    "operands",
                    "constants",
                ):
                    raise W04SchemaClosureError("runtime predicate shape differs")
                if predicate["predicate_classification"] != "RUNTIME_MODEL_VALIDATOR":
                    raise W04SchemaClosureError("runtime predicate classification differs")
                if predicate["authority_sources"] != []:
                    raise W04SchemaClosureError("runtime predicate authority source differs")
                row = {
                    "constants": predicate["constants"],
                    "declared_owner": predicate["declared_owner_model"],
                    "operation": predicate["operation"],
                    "operands": predicate["operands"],
                    "owner": predicate["owner_model"],
                    "validator": predicate["validator_name"],
                }
                key = (cast(str, row["owner"]), cast(str, row["validator"]))
                if key in observed and observed[key] != row:
                    raise W04SchemaClosureError("repeated runtime predicate binding differs")
                observed[key] = row
    expected_keys = [
        (cast(str, row["owner"]), cast(str, row["validator"]))
        for row in _runtime_predicate_oracle()
    ]
    if set(observed) != set(expected_keys):
        raise W04SchemaClosureError("runtime predicate binding roster differs")
    rows = tuple(observed[key] for key in expected_keys)
    encoded = b"".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        for row in rows
    )
    if encoded != _RUNTIME_PREDICATE_ORACLE_JSONL.encode("utf-8"):
        raise W04SchemaClosureError("runtime predicate ledger bytes differ")


def _validate_generated_contents(contents: tuple[dict[str, object], ...]) -> None:
    if len(contents) != 23:
        raise W04SchemaClosureError("implemented schema content roster is not exactly 23")
    for index, (content, role, model) in enumerate(
        zip(contents, W04_SCHEMA_ROOT_ROLES, _ROOT_MODELS, strict=True)
    ):
        if tuple(content) != W04_CANONICAL_CONTENT_KEY_ORDER:
            raise W04SchemaClosureError("canonical content key order differs")
        if content["root_role"] != role:
            raise W04SchemaClosureError("root content order differs")
        if content["canonical_schema_id"] != w04_canonical_schema_id(role):
            raise W04SchemaClosureError("canonical schema ID does not reproduce")
        if content["canonical_schema_version"] != W04_CANONICAL_SCHEMA_VERSION:
            raise W04SchemaClosureError("canonical schema version differs")
        if content["schema_language_version"] != W04_SCHEMA_LANGUAGE_VERSION:
            raise W04SchemaClosureError("schema language version differs")
        if content["root_definition_id"] != model.__name__:
            raise W04SchemaClosureError("root definition owner differs")
        definitions = content["definitions"]
        if type(definitions) is not dict or tuple(definitions) != (
            "constant_corpus",
            "definition_order",
            "external_authority_predicates",
            "predicate_constant_resolver",
            "schemas",
            "serialization_contract",
        ):
            raise W04SchemaClosureError("definitions closure shape differs")
        _validate_predicate_constant_resolver(definitions["predicate_constant_resolver"])
        schemas = definitions["schemas"]
        order = definitions["definition_order"]
        if type(schemas) is not dict or type(order) is not list or order != list(schemas):
            raise W04SchemaClosureError("definition order differs from named schemas")
        if order[0] != model.__name__ or len(set(order)) != len(order):
            raise W04SchemaClosureError("root definition order or uniqueness differs")
        for reference in _iter_refs(schemas):
            if (
                not reference.startswith("#/$defs/")
                or reference.removeprefix("#/$defs/") not in schemas
            ):
                raise W04SchemaClosureError("logical definition reference is unresolved")
        if index < _JSON_ONLY_START_INDEX:
            projection = content["parquet_projection"]
            if type(projection) is not dict or tuple(projection) != (
                "descriptor",
                "forward_projection",
                "inverse_decoding",
                "metadata_policy",
                "schema_source",
            ):
                raise W04SchemaClosureError("Parquet projection content shape differs")
            descriptor = projection["descriptor"]
            if type(descriptor) is not dict or tuple(descriptor) != (
                "schema_role",
                "serializer_version",
                "fields",
            ):
                raise W04SchemaClosureError("projection descriptor keys differ")
            if not _SCHEMA_ROLE.fullmatch(descriptor["schema_role"]):
                raise W04SchemaClosureError("projection schema role is not canonical")
            if descriptor["schema_role"] != content["canonical_schema_id"]:
                raise W04SchemaClosureError("projection schema role is not root-owned")
            if descriptor["serializer_version"] != W04_PARQUET_SERIALIZER_VERSION:
                raise W04SchemaClosureError("projection serializer version differs")
            fields = descriptor["fields"]
            if type(fields) is not list or not fields:
                raise W04SchemaClosureError("projection fields are empty or malformed")
            for field in fields:
                _validate_projection_field_content(field, tuple_position=None)
            if [field["name"] for field in fields] != list(model.model_fields):
                raise W04SchemaClosureError("projection field order differs from runtime model")
        elif content["parquet_projection"] != W04_JSON_ONLY_PROJECTION_STATE:
            raise W04SchemaClosureError("JSON-only projection state differs")
        encoded = canonical_w04_schema_content_bytes(content)
        if encoded.endswith(b"\n") or json.loads(encoded) != content:
            raise W04SchemaClosureError("schema content is not canonical no-LF JSON")
    _validate_runtime_predicate_ledger(contents)


def _validate_physical_primary_key_paths(
    contents: tuple[dict[str, object], ...],
) -> None:
    if tuple(_W04_PHYSICAL_PRIMARY_KEY_PATHS) != W04_SCHEMA_ROOT_ROLES[:12]:
        raise AssertionError("physical primary-key roles differ from serialized roots")
    projected_scalar_types = {
        "INT8",
        "INT16",
        "INT32",
        "INT64",
        "UINT8",
        "UINT16",
        "UINT32",
        "UINT64",
        "UTF8",
        "TIMESTAMP_US_UTC",
    }
    for content in contents[:12]:
        role = cast(str, content["root_role"])
        projection = cast(dict[str, object], content["parquet_projection"])
        descriptor = cast(dict[str, object], projection["descriptor"])
        root_fields = cast(list[dict[str, object]], descriptor["fields"])
        paths = _W04_PHYSICAL_PRIMARY_KEY_PATHS[role]
        if not paths or len(paths) != len(set(paths)):
            raise AssertionError("physical primary-key paths must be nonempty and unique")
        for path in paths:
            if not path or any(not _FIELD_NAME.fullmatch(segment) for segment in path):
                raise AssertionError("physical primary-key path is not canonical")
            fields = root_fields
            for index, segment in enumerate(path):
                matches = [field for field in fields if field["name"] == segment]
                if len(matches) != 1:
                    raise AssertionError("physical primary-key path is absent or ambiguous")
                field = matches[0]
                if field["nullable"] is not False:
                    raise AssertionError("physical primary-key path contains a nullable field")
                node = cast(dict[str, object], field["node"])
                if index < len(path) - 1:
                    if node["node_kind"] != "STRUCT" or node["projection_kind"] != "OBJECT_STRUCT":
                        raise AssertionError(
                            "physical primary-key path descends through a non-object struct"
                        )
                    fields = cast(list[dict[str, object]], node["children"])
                elif (
                    node["node_kind"] != "SCALAR"
                    or node["projection_kind"] != "IDENTITY"
                    or node["scalar_type"] not in projected_scalar_types
                ):
                    raise AssertionError(
                        "physical primary-key path does not end at an exact str/int scalar"
                    )


@cache
def _internal_export_bytes() -> tuple[tuple[bytes, ...], tuple[bytes, ...]]:
    contents = tuple(
        _build_content(role, model, index)
        for index, (role, model) in enumerate(zip(W04_SCHEMA_ROOT_ROLES, _ROOT_MODELS, strict=True))
    )
    _validate_generated_contents(contents)
    _validate_physical_primary_key_paths(contents)
    content_bytes = tuple(canonical_w04_schema_content_bytes(content) for content in contents)
    rows = tuple(
        {
            "canonical_schema_content_sha256": hashlib.sha256(encoded).hexdigest(),
            "canonical_schema_id": w04_canonical_schema_id(role),
            "canonical_schema_version": W04_CANONICAL_SCHEMA_VERSION,
            "closure_dependencies": [
                w04_canonical_schema_id(dependency) for dependency in dependencies
            ],
            "root_role": role,
            "surface_kind": W04_IMPLEMENTED_SCHEMA_SURFACE,
        }
        for role, dependencies, encoded in zip(
            W04_SCHEMA_ROOT_ROLES,
            _DEPENDENCY_ROLE_GRAPH,
            content_bytes,
            strict=True,
        )
    )
    return content_bytes, tuple(_canonical_json_bytes(row) for row in rows)


def _copies(values: tuple[bytes, ...]) -> tuple[dict[str, object], ...]:
    return tuple(json.loads(value) for value in values)


def export_w04_implemented_schema_contents() -> tuple[dict[str, object], ...]:
    """Export fresh copies of the exact 23 canonical root content objects."""

    content_bytes, _ = _internal_export_bytes()
    contents = _copies(content_bytes)
    # Canonical decoding sorts object keys; restore the controlling outer order.
    ordered = tuple(
        {key: content[key] for key in W04_CANONICAL_CONTENT_KEY_ORDER} for content in contents
    )
    validate_w04_implemented_schema_exports(ordered, export_w04_implemented_schema_rows())
    return ordered


def export_w04_implemented_schema_rows() -> tuple[dict[str, object], ...]:
    """Export fresh copies of the exact 23 six-key implemented-schema rows."""

    _, row_bytes = _internal_export_bytes()
    rows = _copies(row_bytes)
    return tuple({key: row[key] for key in W04_IMPLEMENTED_ROW_KEY_ORDER} for row in rows)


def w04_parquet_projection_content(root_role: str) -> dict[str, object]:
    """Return one root-owned descriptor content object; JSON-only roots fail closed."""

    if type(root_role) is not str or root_role not in W04_SCHEMA_ROOT_ROLES[:12]:
        raise W04SchemaClosureError("root role has no W04 Parquet projection descriptor")
    content = export_w04_implemented_schema_contents()[W04_SCHEMA_ROOT_ROLES.index(root_role)]
    projection = content["parquet_projection"]
    if type(projection) is not dict:
        raise W04SchemaClosureError("Parquet projection descriptor is unavailable")
    return cast(dict[str, object], json.loads(_canonical_json_bytes(projection)))


def w04_physical_primary_key_paths(root_role: str) -> tuple[tuple[str, ...], ...]:
    """Return the exact descriptor-owned physical key paths for one Parquet role."""

    if type(root_role) is not str or root_role not in _W04_PHYSICAL_PRIMARY_KEY_PATHS:
        raise W04SchemaClosureError("root role has no W04 physical primary-key paths")
    return _W04_PHYSICAL_PRIMARY_KEY_PATHS[root_role]


def validate_w04_implemented_schema_exports(
    contents: Sequence[Mapping[str, object]],
    rows: Sequence[Mapping[str, object]],
) -> None:
    """Fail closed unless a candidate is the exact internally owned 23-root closure."""

    if type(contents) is not tuple or type(rows) is not tuple:
        raise W04SchemaClosureError("schema exports must be exact immutable rosters")
    if len(contents) != 23 or len(rows) != 23:
        raise W04SchemaClosureError("schema exports must contain exactly 23 roots")
    expected_contents, expected_rows = _internal_export_bytes()
    role_positions = {role: index for index, role in enumerate(W04_SCHEMA_ROOT_ROLES)}
    for index, (content, row, expected_content, expected_row) in enumerate(
        zip(contents, rows, expected_contents, expected_rows, strict=True)
    ):
        if type(content) is not dict or tuple(content) != W04_CANONICAL_CONTENT_KEY_ORDER:
            raise W04SchemaClosureError("candidate content shape or key order differs")
        if canonical_w04_schema_content_bytes(content) != expected_content:
            raise W04SchemaClosureError("candidate canonical schema content differs")
        if type(row) is not dict or tuple(row) != W04_IMPLEMENTED_ROW_KEY_ORDER:
            raise W04SchemaClosureError("candidate implemented row shape or key order differs")
        if _canonical_json_bytes(row) != expected_row:
            raise W04SchemaClosureError("candidate implemented schema row differs")
        digest = hashlib.sha256(expected_content).hexdigest()
        if row["canonical_schema_content_sha256"] != digest:
            raise W04SchemaClosureError("content digest does not reproduce")
        dependencies = row["closure_dependencies"]
        if type(dependencies) is not list or len(dependencies) != len(set(dependencies)):
            raise W04SchemaClosureError("closure dependencies are malformed or duplicated")
        for dependency_id in dependencies:
            dependency_role = next(
                (
                    role
                    for role in W04_SCHEMA_ROOT_ROLES
                    if w04_canonical_schema_id(role) == dependency_id
                ),
                None,
            )
            if dependency_role is None or role_positions[dependency_role] >= index:
                raise W04SchemaClosureError("closure dependency is forward, cyclic or unknown")


__all__ = [
    "W04_CANONICAL_CONTENT_KEY_ORDER",
    "W04_CANONICAL_SCHEMA_VERSION",
    "W04_IMPLEMENTED_ROW_KEY_ORDER",
    "W04_IMPLEMENTED_SCHEMA_SURFACE",
    "W04_JSON_ONLY_PROJECTION_STATE",
    "W04_PARQUET_SERIALIZER_VERSION",
    "W04_SCHEMA_LANGUAGE_VERSION",
    "W04_SCHEMA_ROOT_ROLES",
    "W04SchemaClosureError",
    "canonical_w04_schema_content_bytes",
    "export_w04_implemented_schema_contents",
    "export_w04_implemented_schema_rows",
    "validate_w04_implemented_schema_exports",
    "w04_canonical_schema_id",
    "w04_physical_primary_key_paths",
    "w04_parquet_projection_content",
]
