"""Stdlib-only W04 code/environment admission child.

The child consumes one canonical closed environment envelope, guard-reads only
explicit paths, constructs the exact ordered twenty stable components, and emits
one framed ``w04-child-result-v3`` value.  It never writes a manifest or computes
a build ID.
"""

from __future__ import annotations

import base64
import configparser
import csv
import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import stat
import subprocess  # nosec B404
import sys
import sysconfig
import tomllib
import urllib.parse
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from types import ModuleType
from typing import Final, cast
from unicodedata import is_normalized

ADMISSION_ARGV: Final = (
    "uv",
    "run",
    "--locked",
    "--no-sync",
    "python",
    "-S",
    "-B",
    "scripts/admit_wyscout_v5_runtime.py",
)
REBUILD_ARGV: Final = (*ADMISSION_ARGV[:-1], "scripts/rebuild_wyscout_v5.py")
OUTER_ARGV: Final = (*ADMISSION_ARGV[:-1], "scripts/launch_wyscout_v5.py")
COMPONENT_KEYS: Final = (
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
FRAME_MAGIC: Final = b"W04CRSLT"
FRAME_VERSION: Final = 1
MAX_INPUT_BYTES: Final = 262_144
MAX_MANIFEST_BYTES: Final = 12_000_000
MAX_SOURCE_BYTES: Final = 16_777_216
MANIFEST_SCHEMA_VERSION: Final = "w04-code-environment-admission-v16"
CHILD_RESULT_SCHEMA_VERSION: Final = "w04-child-result-v3"
CHILD_INPUT_SCHEMA_VERSION: Final = "w04-child-input-v1"
FINAL_RECHECK_SCHEMA_VERSION: Final = "w04-rebuild-final-recheck-v2"
RUNTIME_SUBSET_ALGORITHM: Final = "w04-normalized-runtime-subset-observations-v1"
RUNTIME_SUBSET_POLICY: Final = "operational-R-subset-L-normalized-observation-v2"
RUNTIME_OBSERVATION_FIELDS: Final = (
    "observation_kind",
    "owner_name",
    "owner_version",
    "site_relative_path",
    "subject_name",
)
RUNTIME_OBSERVATION_KINDS: Final = (
    "MODULE_SOURCE",
    "NATIVE_EXTENSION",
    "NAMESPACE_LOCATION",
    "SITE_SHARED_IMAGE",
)
UV_VERSION: Final = "uv 0.9.21 (Homebrew 2025-12-30)"
UV_PHYSICAL_SHA256: Final = "4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f"
PYTHON_PHYSICAL_SHA256: Final = "cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79"
PYPROJECT_SHA256: Final = "963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b"
UV_LOCK_SHA256: Final = "04ca02a3e67b1cdc71ca9de1bef3e4be0d8f1cc448e289892b1c085dfab3dd20"
SHA256_RE: Final = re.compile(r"^[0-9a-f]{64}$")
FD_RE: Final = re.compile(r"^(?:[3-9]|[1-9][0-9]+)$")
UUID4_RE: Final = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)

_OUTER_LITERAL_ENVIRONMENT: Final = {
    "ARROW_NUM_THREADS": "1",
    "LANG": "C",
    "LC_ALL": "C",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "POLARS_MAX_THREADS": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8:strict",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUTF8": "1",
    "RAYON_NUM_THREADS": "1",
    "TZ": "UTC",
    "UV_LOCKED": "1",
    "UV_NO_SYNC": "1",
    "UV_OFFLINE": "1",
    "UV_RUN_RECURSION_DEPTH": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
_OUTER_ENVIRONMENT_TOKENS: Final = {
    "HOME": "<W04_HOME>",
    "PATH": "<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin",
    "PYTHONPYCACHEPREFIX": "<CONTROL_PREFIX>",
    "TMPDIR": "<W04_TMPDIR>",
    "UV": "<W04_UV_LOGICAL_LAUNCH_PATH>",
    "UV_CACHE_DIR": "<W04_UV_CACHE_ROOT>",
    "VIRTUAL_ENV": "<W04_PROJECT_ROOT>/.venv",
    "W04_LAUNCHER_SOURCE_FD": "<LAUNCHER_SOURCE_FD>",
    "__CF_USER_TEXT_ENCODING": "<W04_CF_USER_TEXT_ENCODING>",
}
OUTER_REQUIRED_ABSENT_ENVIRONMENT: Final = (
    "ALL_PROXY",
    "COVERAGE_PROCESS_CONFIG",
    "COVERAGE_PROCESS_START",
    "DYLD_FALLBACK_FRAMEWORK_PATH",
    "DYLD_FALLBACK_LIBRARY_PATH",
    "DYLD_FRAMEWORK_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "HTTPS_PROXY",
    "HTTP_PROXY",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "NO_PROXY",
    "PYTHONBREAKPOINT",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONWARNINGS",
    "UV_DEFAULT_INDEX",
    "UV_EXTRA_INDEX_URL",
    "UV_FIND_LINKS",
    "UV_INDEX",
    "UV_PROJECT_ENVIRONMENT",
    "UV_PYTHON",
    "UV_PYTHON_PREFERENCE",
    "W04_BOOTSTRAP_TUPLE_B64",
    "W04_CHILD_INPUT_B64",
    "W04_CHILD_ROLE",
    "W04_ENTRYPOINT_SOURCE_FD",
    "W04_RESULT_FD",
    "W04_RESULT_NONCE",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
)
OUTER_ENCODING_SOURCE_ROWS: Final = (
    {
        "module": "encodings",
        "path": "encodings/__init__.py",
        "sha256": "78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8",
        "size_bytes": 5_884,
    },
    {
        "module": "encodings.aliases",
        "path": "encodings/aliases.py",
        "sha256": "6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2",
        "size_bytes": 15_677,
    },
    {
        "module": "encodings.utf_8",
        "path": "encodings/utf_8.py",
        "sha256": "ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d",
        "size_bytes": 1_005,
    },
)

REPOSITORY_CODE_PATHS: Final = (
    "scripts/__init__.py",
    "scripts/acquire_wyscout_v5.py",
    "scripts/admit_wyscout_v5_runtime.py",
    "scripts/apply_migrations.py",
    "scripts/control_utils.py",
    "scripts/install_local_git_guards.py",
    "scripts/launch_wyscout_v5.py",
    "scripts/materialize_wyscout_v5_contracts.py",
    "scripts/profile_wyscout_v5.py",
    "scripts/run_w03_protected_gate.py",
    "scripts/validate_w03_governance.py",
    "scripts/verify_local_only.py",
    "scripts/verify_parallel_safety.py",
    "scripts/verify_phase.py",
    "scripts/verify_task_return.py",
    "src/scouting/__init__.py",
    "src/scouting/audit/__init__.py",
    "src/scouting/audit/writer.py",
    "src/scouting/contracts/__init__.py",
    "src/scouting/contracts/audit.py",
    "src/scouting/contracts/evidence.py",
    "src/scouting/contracts/primitives.py",
    "src/scouting/contracts/retrieval.py",
    "src/scouting/contracts/workflow.py",
    "src/scouting/contracts/wyscout_aggregates.py",
    "src/scouting/contracts/wyscout_build.py",
    "src/scouting/contracts/wyscout_data.py",
    "src/scouting/contracts/wyscout_identity.py",
    "src/scouting/contracts/wyscout_schema.py",
    "src/scouting/identity/__init__.py",
    "src/scouting/identity/wyscout.py",
    "src/scouting/operations/__init__.py",
    "src/scouting/operations/telemetry.py",
    "src/scouting/policy/__init__.py",
    "src/scouting/policy/authentication.py",
    "src/scouting/policy/authorization.py",
    "src/scouting/policy/eligibility.py",
    "src/scouting/serving/__init__.py",
    "src/scouting/serving/synthetic.py",
    "src/scouting/sources/__init__.py",
    "src/scouting/sources/synthetic.py",
    "src/scouting/sources/wyscout.py",
    "src/scouting/sources/wyscout_completion_index.py",
    "src/scouting/sources/wyscout_manifest.py",
    "src/scouting/sources/wyscout_vertical_slice.py",
    "src/scouting/storage/__init__.py",
    "src/scouting/storage/embedded.py",
    "src/scouting/storage/formats.py",
    "src/scouting/storage/guarded.py",
    "src/scouting/storage/wyscout_publication.py",
    "src/scouting/web/__init__.py",
    "src/scouting/web/app.py",
    "src/scouting/workflow/__init__.py",
    "src/scouting/workflow/service.py",
)

REPOSITORY_PYC_SOURCE_PATHS: Final = (
    "tests/contracts/test_foundation_contracts.py",
    "tests/contracts/test_w04_field_semantic_v2_authority.py",
    "tests/contracts/test_w04_identity_ruleset_authority.py",
    "tests/contracts/test_w04_logical_arrow_projection_authority.py",
    "tests/contracts/test_w04_possession_semantic_authority.py",
    "tests/contracts/test_w04_possession_semantic_v2_authority.py",
    "tests/contracts/test_w04_r21_control_preimages.py",
    "tests/contracts/test_w04_r21_cross_authority_composability.py",
    "tests/contracts/test_w04_source_temporal_review.py",
    "tests/contracts/test_w04_supported_feature_authority.py",
    "tests/contracts/test_w04_wyscout_build_contract.py",
    "tests/contracts/test_w04_wyscout_build_product_authority.py",
    "tests/contracts/test_w04_wyscout_identity_bundle.py",
    "tests/contracts/test_w04_wyscout_schema_closure.py",
    "tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py",
    "tests/contracts/test_w04_wyscout_v2_aggregates.py",
    "tests/contracts/test_wyscout_data_contracts.py",
    "tests/contracts/test_wyscout_field_registry_authority.py",
    "tests/e2e/test_w03_vertical_journey.py",
    "tests/e2e/test_w04_wyscout_vertical_slice.py",
    "tests/governance/test_w03_policies.py",
    "tests/governance/test_w04_source_authority.py",
    "tests/integration/test_migrations.py",
    "tests/integration/test_w03_local_telemetry.py",
    "tests/security/test_application_authorization.py",
    "tests/security/test_database_boundaries.py",
    "tests/security/test_w03_boundary_audit.py",
    "tests/security/test_w04_real_acquisition_review.py",
    "tests/security/test_w04_source_authority_boundary.py",
    "tests/security/test_w04_wyscout_ingest_review.py",
    "tests/security/test_w04_wyscout_profile_review.py",
    "tests/security/test_w04_wyscout_vertical_slice_publication.py",
    "tests/unit/test_foundation.py",
    "tests/unit/test_guarded_storage.py",
    "tests/unit/test_orchestration_controls.py",
    "tests/unit/test_synthetic_fixture.py",
    "tests/unit/test_w04_staged_product_publisher.py",
    "tests/unit/test_w04_wyscout_product_formats.py",
    "tests/unit/test_w04_wyscout_runtime_control.py",
    "tests/unit/test_w04_wyscout_vertical_slice_context.py",
    "tests/unit/test_wyscout_identity.py",
    "tests/unit/test_wyscout_profile.py",
    "tests/unit/test_wyscout_source.py",
    "tests/unit/test_wyscout_source_completion_index.py",
    "tests/unit/test_wyscout_source_manifest.py",
)

POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES: Final = (
    {
        "authority_class": "REPOSITORY_RETIRED_POST_W04_CACHE_AUDIT_ONLY",
        "cache_path": (
            "tests/integration/__pycache__/"
            "test_w10_expert_relevance_evaluation.cpython-312-pytest-9.1.1.pyc"
        ),
        "denial_policy": "RETIRED_POST_W04_SOURCE_CACHE_DENIED_ZERO_READ",
        "source_path": "tests/integration/test_w10_expert_relevance_evaluation.py",
        "source_required_absent": True,
        "traversal_root_role": "WHOLE_REPOSITORY",
    },
)


def _derive_post_w04_audit_only_pyc_source_paths(
    root: Path,
    stable_repository_sources: frozenset[str],
) -> tuple[str, ...]:
    """Derive non-manifest Python sources without reading source or cache bytes."""

    retired_sources = frozenset(
        cast(str, row["source_path"]) for row in POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES
    )
    discovered: set[str] = set()
    for scope in ("scripts", "services", "src", "tests"):
        scope_root = root / scope
        if not scope_root.exists():
            continue
        for directory, directory_names, filenames in os.walk(scope_root, followlinks=False):
            retained_directories: list[str] = []
            for name in sorted(directory_names):
                if name == "__pycache__":
                    continue
                candidate = Path(directory) / name
                metadata = candidate.lstat()
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                    raise AdmissionError(
                        "post-W04 Python source derivation encountered an unsafe directory"
                    )
                retained_directories.append(name)
            directory_names[:] = retained_directories
            for name in sorted(filenames):
                if not name.endswith(".py"):
                    continue
                candidate = Path(directory) / name
                metadata = candidate.lstat()
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                    raise AdmissionError(
                        "post-W04 Python source derivation encountered an unsafe source"
                    )
                relative = candidate.relative_to(root).as_posix()
                if relative not in stable_repository_sources and relative not in retired_sources:
                    discovered.add(relative)
    return tuple(sorted(discovered))


# These exact downstream code paths are already packet-authorised but intentionally
# absent during this admission-control packet.  Their explicit absent/present state
# is content-addressed without scanning or directory shorthand.
AUTHORIZED_DOWNSTREAM_CODE_PATHS: Final = (
    "scripts/rebuild_wyscout_v5.py",
    "src/scouting/data_products/wyscout/__init__.py",
    "src/scouting/data_products/wyscout/actions.py",
    "src/scouting/data_products/wyscout/bronze.py",
    "src/scouting/data_products/wyscout/gold.py",
    "src/scouting/data_products/wyscout/lineups.py",
    "src/scouting/data_products/wyscout/player_match.py",
    "src/scouting/data_products/wyscout/possessions.py",
    "src/scouting/data_products/wyscout/rebuild.py",
    "src/scouting/data_products/wyscout/silver_manifest.py",
    "src/scouting/data_products/wyscout/temporal_boundary.py",
)

LOCAL_RESOURCE_DIGEST_ALGORITHM: Final = "w04-local-resource-exact-30-v1"
LOCAL_RESOURCE_PATHS: Final = (
    "configs/schema/wyscout-v5-identity-ruleset-v1.yaml",
    "configs/schema/wyscout-v5-field-registry-v1.yaml",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml",
    "configs/features/wyscout-v5-supported-count-features-v1.yaml",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md",
    "reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json",
    "reports/phase-gates/W04/source-schema-profile.md",
    "reports/reviews/W04/wyscout-schema-design-R21.md",
    "reports/reviews/W04/wyscout-schema-design-independent-review-R15.md",
    "configs/schema/wyscout-v5-product-contract-preimage-v1.json",
    "configs/schema/wyscout-v5-schema-bundle-preimage-v1.json",
    "reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json",
    "configs/schema/wyscout-v5-field-registry-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json",
    "configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md",
    "reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json",
    "tests/contracts/test_w04_r21_cross_authority_composability.py",
)

EXECUTABLE_NAMES: Final = (
    "bandit",
    "bandit-baseline",
    "bandit-config-generator",
    "coverage",
    "coverage-3.12",
    "coverage3",
    "detect-secrets",
    "detect-secrets-hook",
    "dmypy",
    "doesitcache",
    "f2py",
    "fastapi",
    "httpx",
    "hypothesis",
    "idna",
    "import-linter",
    "lint-imports",
    "markdown-it",
    "mypy",
    "mypyc",
    "normalizer",
    "numpy-config",
    "pip",
    "pip-audit",
    "pip-licenses",
    "pip3",
    "pip3.12",
    "playwright",
    "py.test",
    "pygmentize",
    "pytest",
    "ruff",
    "stubgen",
    "stubtest",
    "uvicorn",
)

_STATIC_ENVIRONMENT: Final = {
    "ARROW_NUM_THREADS": "1",
    "LANG": "C",
    "LC_ALL": "C",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "POLARS_MAX_THREADS": "1",
    "PYTHONDONTWRITEBYTECODE": "1",
    "PYTHONHASHSEED": "0",
    "PYTHONIOENCODING": "utf-8:strict",
    "PYTHONNOUSERSITE": "1",
    "PYTHONUTF8": "1",
    "RAYON_NUM_THREADS": "1",
    "TZ": "UTC",
    "UV_LOCKED": "1",
    "UV_NO_SYNC": "1",
    "UV_OFFLINE": "1",
    "UV_RUN_RECURSION_DEPTH": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}
_OPERATIONAL_ENVIRONMENT_NAMES: Final = (
    "HOME",
    "PATH",
    "PYTHONPYCACHEPREFIX",
    "TMPDIR",
    "UV",
    "UV_CACHE_DIR",
    "VIRTUAL_ENV",
    "W04_CHILD_INPUT_B64",
    "W04_CHILD_ROLE",
    "W04_ENTRYPOINT_SOURCE_FD",
    "W04_RESULT_FD",
    "W04_RESULT_NONCE",
    "__CF_USER_TEXT_ENCODING",
)
_NORMALIZED_ENVIRONMENT_TOKENS: Final = {
    "HOME": "<W04_HOME>",
    "PATH": "<W04_VENV_BIN>:<W04_UV_BIN_DIR>:/usr/bin:/bin:/usr/sbin:/sbin",
    "PYTHONPYCACHEPREFIX": "<ADMISSION_PREFIX>",
    "TMPDIR": "<W04_TMPDIR>",
    "UV": "<W04_UV_LOGICAL_LAUNCH_PATH>",
    "UV_CACHE_DIR": "<W04_UV_CACHE_ROOT>",
    "VIRTUAL_ENV": "<W04_PROJECT_ROOT>/.venv",
    "W04_ENTRYPOINT_SOURCE_FD": "<ENTRYPOINT_SOURCE_FD>",
    "W04_RESULT_FD": "<RESULT_FD>",
    "W04_RESULT_NONCE": "<RESULT_NONCE>",
    "__CF_USER_TEXT_ENCODING": "<W04_CF_USER_TEXT_ENCODING>",
}
REQUIRED_ABSENT_ENVIRONMENT: Final = (
    "ALL_PROXY",
    "COVERAGE_PROCESS_CONFIG",
    "COVERAGE_PROCESS_START",
    "DYLD_FALLBACK_FRAMEWORK_PATH",
    "DYLD_FALLBACK_LIBRARY_PATH",
    "DYLD_FRAMEWORK_PATH",
    "DYLD_INSERT_LIBRARIES",
    "DYLD_LIBRARY_PATH",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "LD_LIBRARY_PATH",
    "LD_PRELOAD",
    "NO_PROXY",
    "PYTHONBREAKPOINT",
    "PYTHONHOME",
    "PYTHONINSPECT",
    "PYTHONOPTIMIZE",
    "PYTHONPATH",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "PYTHONWARNINGS",
    "UV_DEFAULT_INDEX",
    "UV_EXTRA_INDEX_URL",
    "UV_FIND_LINKS",
    "UV_INDEX",
    "UV_PROJECT_ENVIRONMENT",
    "UV_PYTHON",
    "UV_PYTHON_PREFERENCE",
    "W04_BOOTSTRAP_TUPLE_B64",
    "W04_LAUNCHER_SOURCE_FD",
    "all_proxy",
    "http_proxy",
    "https_proxy",
    "no_proxy",
)


class AdmissionError(RuntimeError):
    """One exact W04 admission predicate failed."""


def canonical_json_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    except (TypeError, ValueError) as error:
        raise AdmissionError("value is not canonical JSON") from error


def load_canonical_json(raw: bytes) -> object:
    if not raw or raw.endswith(b"\n"):
        raise AdmissionError("canonical JSON must be nonempty without terminal LF")

    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        output: dict[str, object] = {}
        for key, value in pairs:
            if key in output:
                raise AdmissionError(f"duplicate JSON key: {key}")
            output[key] = value
        return output

    try:
        decoded = json.loads(
            raw.decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicates
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AdmissionError("invalid canonical JSON") from error
    if canonical_json_bytes(decoded) != raw:
        raise AdmissionError("JSON is not byte-canonical")
    return decoded


def _load_strict_json(raw: bytes) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        output: dict[str, object] = {}
        for key, value in pairs:
            if key in output:
                raise AdmissionError(f"duplicate JSON key: {key}")
            output[key] = value
        return output

    try:
        return json.loads(raw.decode("utf-8", errors="strict"), object_pairs_hook=reject_duplicates)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AdmissionError("invalid strict JSON") from error


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_json(value: object) -> str:
    return _sha256(canonical_json_bytes(value))


def _validate_relative_path(relative_path: str) -> tuple[str, ...]:
    if (
        not relative_path
        or relative_path.startswith("/")
        or relative_path.endswith("/")
        or "\\" in relative_path
        or any(part in {"", ".", ".."} for part in relative_path.split("/"))
    ):
        raise AdmissionError("unsafe explicit repository-relative path")
    return tuple(relative_path.split("/"))


def _guard_read_relative(
    root: Path,
    relative_path: str,
    *,
    expected_mode: int = 0o644,
    max_bytes: int = 128 * 1024 * 1024,
) -> bytes:
    parts = _validate_relative_path(relative_path)
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    descriptors = [root_fd]
    try:
        current = root_fd
        for part in parts[:-1]:
            before = os.stat(part, dir_fd=current, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode) or stat.S_ISLNK(before.st_mode):
                raise AdmissionError("guard path crosses link or non-directory")
            child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=current)
            after = os.fstat(child)
            if (before.st_dev, before.st_ino, before.st_mode) != (
                after.st_dev,
                after.st_ino,
                after.st_mode,
            ):
                os.close(child)
                raise AdmissionError("guard directory changed during open")
            descriptors.append(child)
            current = child
        before = os.stat(parts[-1], dir_fd=current, follow_symlinks=False)
        if (
            not stat.S_ISREG(before.st_mode)
            or stat.S_ISLNK(before.st_mode)
            or stat.S_IMODE(before.st_mode) != expected_mode
            or before.st_nlink != 1
            or not 0 <= before.st_size <= max_bytes
        ):
            raise AdmissionError("guarded file kind, mode, link count, or size differs")
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=current)
        try:
            opened = os.fstat(descriptor)
            stable = (
                opened.st_dev,
                opened.st_ino,
                opened.st_mode,
                opened.st_nlink,
                opened.st_size,
                opened.st_mtime_ns,
                opened.st_ctime_ns,
            )
            if stable[:5] != (
                before.st_dev,
                before.st_ino,
                before.st_mode,
                before.st_nlink,
                before.st_size,
            ):
                raise AdmissionError("guarded file changed during open")
            chunks: list[bytes] = []
            while chunk := os.read(descriptor, 1024 * 1024):
                chunks.append(chunk)
            after = os.fstat(descriptor)
            if stable != (
                after.st_dev,
                after.st_ino,
                after.st_mode,
                after.st_nlink,
                after.st_size,
                after.st_mtime_ns,
                after.st_ctime_ns,
            ):
                raise AdmissionError("guarded file changed during read")
            raw = b"".join(chunks)
            if len(raw) != after.st_size:
                raise AdmissionError("guarded file size differs from complete read")
            return raw
        finally:
            os.close(descriptor)
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def _optional_code_row(root: Path, relative_path: str) -> dict[str, object]:
    _validate_relative_path(relative_path)
    candidate = root / relative_path
    try:
        metadata = os.stat(candidate, follow_symlinks=False)
    except FileNotFoundError:
        return {"path": relative_path, "state": "AUTHORIZED_ABSENT"}
    if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
        raise AdmissionError("authorised downstream code path is unsafe")
    raw = _guard_read_relative(root, relative_path)
    return {
        "mode": 0o644,
        "path": relative_path,
        "sha256": _sha256(raw),
        "size_bytes": len(raw),
        "state": "PRESENT",
    }


def _file_row(
    root: Path,
    relative_path: str,
    *,
    expected_mode: int = 0o644,
    max_bytes: int = 128 * 1024 * 1024,
) -> dict[str, object]:
    raw = _guard_read_relative(
        root,
        relative_path,
        expected_mode=expected_mode,
        max_bytes=max_bytes,
    )
    return {
        "mode": expected_mode,
        "path": relative_path,
        "sha256": _sha256(raw),
        "size_bytes": len(raw),
    }


def _guard_read_absolute_regular(
    path: Path,
    *,
    expected_mode: int,
    expected_size: int | None = None,
    expected_sha256: str | None = None,
) -> bytes:
    before = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_ISLNK(before.st_mode)
        or stat.S_IMODE(before.st_mode) != expected_mode
        or before.st_nlink != 1
        or (expected_size is not None and before.st_size != expected_size)
    ):
        raise AdmissionError("absolute guarded file metadata differs")
    descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        chunks: list[bytes] = []
        while chunk := os.read(descriptor, 1024 * 1024):
            chunks.append(chunk)
        after = os.fstat(descriptor)
        if (before.st_dev, before.st_ino, before.st_mode, before.st_size) != (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_size,
        ) or (opened.st_dev, opened.st_ino, opened.st_mode, opened.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_size,
        ):
            raise AdmissionError("absolute guarded file changed during read")
        raw = b"".join(chunks)
        if len(raw) != after.st_size or (
            expected_sha256 is not None and _sha256(raw) != expected_sha256
        ):
            raise AdmissionError("absolute guarded file bytes differ")
        return raw
    finally:
        os.close(descriptor)


def normalized_child_environment(environment: dict[str, str]) -> dict[str, object]:
    expected_names = frozenset(_STATIC_ENVIRONMENT) | frozenset(_OPERATIONAL_ENVIRONMENT_NAMES)
    if frozenset(environment) != expected_names:
        missing = sorted(expected_names - frozenset(environment))
        additional = sorted(frozenset(environment) - expected_names)
        raise AdmissionError(
            f"closed environment differs: missing={missing}, additional={additional}"
        )
    if any(name in environment for name in REQUIRED_ABSENT_ENVIRONMENT):
        raise AdmissionError("required-absent child environment name is present")
    for key, value in _STATIC_ENVIRONMENT.items():
        if environment.get(key) != value:
            raise AdmissionError(f"closed environment literal differs: {key}")
    normalized = dict(environment)
    del normalized["W04_CHILD_INPUT_B64"]
    for key, token in _NORMALIZED_ENVIRONMENT_TOKENS.items():
        normalized[key] = token
    return {
        "algorithm": "w04-child-environment-input-v2",
        "excluded_until_insertion": ["W04_CHILD_INPUT_B64"],
        "present": {key: normalized[key] for key in sorted(normalized)},
        "required_absent": list(REQUIRED_ABSENT_ENVIRONMENT),
    }


def _repository_rows(root: Path) -> tuple[dict[str, object], ...]:
    required = tuple(
        _file_row(root, path, max_bytes=MAX_SOURCE_BYTES)
        for path in (*REPOSITORY_CODE_PATHS, *REPOSITORY_PYC_SOURCE_PATHS)
    )
    downstream = tuple(_optional_code_row(root, path) for path in AUTHORIZED_DOWNSTREAM_CODE_PATHS)
    return (*required, *downstream)


def _local_resource_rows(root: Path) -> tuple[dict[str, object], ...]:
    return tuple(
        _file_row(root, path, expected_mode=0o600 if index == 16 else 0o644)
        for index, path in enumerate(LOCAL_RESOURCE_PATHS)
    )


def _lock_authority(
    root: Path,
) -> tuple[dict[str, object], tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    pyproject = _guard_read_relative(root, "pyproject.toml")
    lock_raw = _guard_read_relative(root, "uv.lock")
    if _sha256(pyproject) != PYPROJECT_SHA256 or _sha256(lock_raw) != UV_LOCK_SHA256:
        raise AdmissionError("accepted pyproject or uv.lock bytes drifted")
    parsed = tomllib.loads(lock_raw.decode("utf-8", errors="strict"))
    packages = parsed.get("package")
    if type(packages) is not list or len(packages) != 83:
        raise AdmissionError("locked package roster differs")
    closure: list[dict[str, object]] = []
    wheels: list[dict[str, object]] = []
    for item in packages:
        if type(item) is not dict:
            raise AdmissionError("locked package row is malformed")
        package = cast(dict[str, object], item)
        name = package.get("name")
        version = package.get("version")
        if type(name) is not str or type(version) is not str:
            raise AdmissionError("locked package identity is malformed")
        if name in {"colorama", "scouting-intelligence"}:
            continue
        closure.append(
            {
                "name": name,
                "source": package.get("source"),
                "version": version,
            }
        )
        declarations = package.get("wheels", [])
        if type(declarations) is not list:
            raise AdmissionError("locked wheel declaration is malformed")
        for declaration in declarations:
            if type(declaration) is not dict:
                raise AdmissionError("locked wheel row is malformed")
            wheel = cast(dict[str, object], declaration)
            wheels.append(
                {
                    "hash": wheel.get("hash"),
                    "name": name,
                    "size": wheel.get("size"),
                    "url": wheel.get("url"),
                    "version": version,
                }
            )
    if len(closure) != 81:
        raise AdmissionError("selected lock closure cardinality differs")
    return (
        {
            "pyproject_sha256": _sha256(pyproject),
            "uv_lock_sha256": _sha256(lock_raw),
        },
        tuple(closure),
        tuple(sorted(wheels, key=lambda row: canonical_json_bytes(row))),
    )


def _installed_record_rows(
    root: Path, closure: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    site_root = root / ".venv/lib/python3.12/site-packages"
    installed: dict[str, tuple[str, Path]] = {}
    for entry in os.scandir(site_root):
        if not entry.name.endswith(".dist-info"):
            continue
        metadata = entry.stat(follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode) or entry.is_symlink():
            raise AdmissionError("installed dist-info census contains an unsafe entry")
        metadata_raw = _guard_read_absolute_regular(
            Path(entry.path) / "METADATA", expected_mode=0o644
        )
        metadata_headers = metadata_raw.decode().split("\n\n", 1)[0].splitlines()
        name_rows = [line[6:] for line in metadata_headers if line.startswith("Name: ")]
        version_rows = [line[9:] for line in metadata_headers if line.startswith("Version: ")]
        if len(name_rows) != 1 or len(version_rows) != 1:
            raise AdmissionError(f"installed METADATA identity is not singular: {entry.name}")
        normalized = re.sub(r"[-_.]+", "-", name_rows[0]).lower()
        expected_dist_info = f"{normalized.replace('-', '_')}-{version_rows[0]}.dist-info"
        if entry.name != expected_dist_info:
            raise AdmissionError("installed dist-info name/version association differs")
        if normalized in installed:
            raise AdmissionError("installed distribution identity is duplicated")
        installed[normalized] = (version_rows[0], Path(entry.path))
    expected_installed = {cast(str, row["name"]): cast(str, row["version"]) for row in closure}
    expected_installed["scouting-intelligence"] = "0.1.0"
    if {name: version for name, (version, _path) in installed.items()} != expected_installed:
        raise AdmissionError("selected lock closure does not equal installed distributions")
    rows: list[dict[str, object]] = []
    for package in closure:
        name = cast(str, package["name"])
        version = cast(str, package["version"])
        installed_version, dist_info = installed[name]
        if installed_version != version:
            raise AdmissionError("installed distribution version differs from selected lock")
        record_path = dist_info / "RECORD"
        record_raw = _guard_read_absolute_regular(record_path, expected_mode=0o644)
        record_rows = list(csv.reader(record_raw.decode("utf-8", errors="strict").splitlines()))
        if not record_rows or any(len(row) != 3 for row in record_rows):
            raise AdmissionError("installed RECORD row shape differs")
        verified_rows: list[dict[str, object]] = []
        seen: set[str] = set()
        self_path = f"{dist_info.name}/RECORD"
        for record_relative, digest_cell, size_cell in record_rows:
            parsed = PurePosixPath(record_relative)
            raw_parts = tuple(record_relative.split("/"))
            executable_scheme = (
                len(raw_parts) == 5
                and raw_parts[:4] == ("..", "..", "..", "bin")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", raw_parts[4]) is not None
            )
            mapped_external_candidate = ".." in raw_parts and not executable_scheme
            if (
                parsed.is_absolute()
                or "\\" in record_relative
                or any(part in {"", "."} for part in raw_parts)
                or (not executable_scheme and not mapped_external_candidate and ".." in raw_parts)
                or record_relative in seen
            ):
                raise AdmissionError("installed RECORD contains an unsafe or duplicate path")
            seen.add(record_relative)
            if record_relative.lower().endswith((".pyc", ".pyo")):
                raise AdmissionError("installed RECORD must not grant bytecode read authority")
            if record_relative == self_path:
                if digest_cell or size_cell:
                    raise AdmissionError("installed RECORD self row is not empty")
                verified_rows.append({"path": record_relative, "self": True})
                continue
            target = Path(os.path.normpath(os.fspath(site_root / record_relative)))
            if not target.is_relative_to(root / ".venv"):
                raise AdmissionError("installed RECORD path escapes the venv")
            target_metadata = os.stat(target, follow_symlinks=False)
            if not stat.S_ISREG(target_metadata.st_mode) or stat.S_ISLNK(target_metadata.st_mode):
                raise AdmissionError("installed RECORD target is not a regular non-link")
            target_raw = _guard_read_absolute_regular(
                target, expected_mode=stat.S_IMODE(target_metadata.st_mode)
            )
            if not digest_cell.startswith("sha256=") or not size_cell.isdecimal():
                raise AdmissionError("installed RECORD hash/size declaration differs")
            encoded = (
                base64.urlsafe_b64encode(hashlib.sha256(target_raw).digest()).decode().rstrip("=")
            )
            if digest_cell[7:] != encoded or int(size_cell) != len(target_raw):
                raise AdmissionError("installed RECORD target hash/size differs")
            verified_rows.append(
                {
                    "mode": stat.S_IMODE(target_metadata.st_mode),
                    "path": record_relative,
                    "sha256": _sha256(target_raw),
                    "size_bytes": len(target_raw),
                }
            )
        installer = next(
            row for row in verified_rows if row.get("path") == f"{dist_info.name}/INSTALLER"
        )
        requested = next(
            row for row in verified_rows if row.get("path") == f"{dist_info.name}/REQUESTED"
        )
        if installer["sha256"] != _sha256(b"uv") or requested["size_bytes"] != 0:
            raise AdmissionError("installed INSTALLER/REQUESTED generated rows differ")
        rows.append(
            {
                "name": name,
                "record_rows": verified_rows,
                "version": version,
            }
        )
    return tuple(rows)


def _validate_installed_mapping(
    root: Path,
    record_rows: tuple[dict[str, object], ...],
    mapped_destinations: dict[str, dict[str, object]],
) -> None:
    """Close every extracted mapping against singular installed RECORD ownership."""

    site = root / ".venv/lib/python3.12/site-packages"
    venv = root / ".venv"
    installed: dict[str, dict[str, object]] = {}
    for package in record_rows:
        owner = cast(str, package["name"])
        for row in cast(list[dict[str, object]], package["record_rows"]):
            if row.get("self") is True:
                continue
            relative = cast(str, row["path"])
            target = Path(os.path.normpath(os.fspath(site / relative)))
            if not target.is_relative_to(venv):
                raise AdmissionError("installed RECORD destination escapes the environment")
            destination = target.relative_to(venv).as_posix()
            if destination in installed:
                raise AdmissionError("installed RECORD destinations collide across owners")
            installed[destination] = {"owner": owner, "relative": relative, **row}
            parts = tuple(relative.split("/"))
            executable_scheme = (
                len(parts) == 5
                and parts[:4] == ("..", "..", "..", "bin")
                and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", parts[4]) is not None
            )
            if ".." in parts and not executable_scheme:
                mapped = mapped_destinations.get(destination)
                canonical_relative = os.path.relpath(venv / destination, site).replace(os.sep, "/")
                if mapped is None or relative != canonical_relative:
                    raise AdmissionError(
                        "external installed RECORD row lacks exact PEP 427 mapping"
                    )
                if (
                    mapped["owner"] != owner
                    or mapped["sha256"] != row["sha256"]
                    or mapped["size_bytes"] != row["size_bytes"]
                    or mapped["mode"] != row["mode"]
                ):
                    raise AdmissionError(
                        "external installed RECORD mapping owner/bytes/mode differ"
                    )
    for destination, mapped in mapped_destinations.items():
        installed_row = installed.get(destination)
        if installed_row is None:
            raise AdmissionError("extracted payload lacks singular installed RECORD ownership")
        if (
            installed_row["owner"] != mapped["owner"]
            or installed_row["sha256"] != mapped["sha256"]
            or installed_row["size_bytes"] != mapped["size_bytes"]
            or installed_row["mode"] != mapped["mode"]
        ):
            raise AdmissionError("extracted and installed RECORD mapping authority differs")


def _require_global_site_ownership(physical_paths: set[str], owners: dict[str, str]) -> None:
    """Require singular RECORD ownership plus the two exact uv bootstrap files."""

    allowed_unowned = {"_virtualenv.pth", "_virtualenv.py"}
    expected = set(owners) | allowed_unowned
    if physical_paths != expected:
        raise AdmissionError(
            "installed global ownership closure differs: "
            f"unowned={sorted(physical_paths - expected)}, "
            f"missing={sorted(expected - physical_paths)}"
        )


def _site_bootstrap_editable_authority(
    root: Path,
    selected_records: tuple[dict[str, object], ...],
    repository_rows: tuple[dict[str, object], ...],
    lock_inputs: dict[str, object],
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    site = root / ".venv/lib/python3.12/site-packages"
    venv_root = root / ".venv"
    configured = sysconfig.get_paths(
        "venv",
        vars={
            "base": os.fspath(venv_root),
            "installed_base": os.fspath(venv_root),
            "installed_platbase": os.fspath(venv_root),
            "platbase": os.fspath(venv_root),
        },
    )
    if (
        Path(configured["purelib"]).resolve() != site.resolve()
        or Path(configured["platlib"]).resolve() != site.resolve()
        or not site.is_relative_to(root / ".venv")
    ):
        raise AdmissionError("exact contained purelib/platlib site roots differ")
    immediate = tuple(os.scandir(site))
    pth_entries = sorted(entry.name for entry in immediate if entry.name.endswith(".pth"))
    if pth_entries != ["_virtualenv.pth", "a1_coverage.pth", "scouting_intelligence.pth"]:
        raise AdmissionError("exact three-file site PTH census differs")
    if len({name.casefold() for name in pth_entries}) != 3 or any(
        entry.name.endswith((".egg", ".egg-info")) for entry in immediate
    ):
        raise AdmissionError("site PTH census collides or legacy egg authority is present")
    exact_files = {
        "_virtualenv.pth": (18, "69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d"),
        "_virtualenv.py": (
            4_342,
            "6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d",
        ),
        "a1_coverage.pth": (
            205,
            "ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8",
        ),
    }
    bootstrap_rows: list[dict[str, object]] = []
    for relative, (size, digest) in exact_files.items():
        raw = _guard_read_absolute_regular(
            site / relative, expected_mode=0o644, expected_size=size, expected_sha256=digest
        )
        bootstrap_rows.append(
            {
                "mode": 0o644,
                "path": f".venv/lib/python3.12/site-packages/{relative}",
                "sha256": _sha256(raw),
                "size_bytes": len(raw),
            }
        )
    if (
        _guard_read_absolute_regular(site / "_virtualenv.pth", expected_mode=0o644)
        != b"import _virtualenv"
    ):
        raise AdmissionError("uv bootstrap PTH bytes differ")
    if "_virtualenv" in sys.modules or "coverage.process_startup" in sys.modules:
        raise AdmissionError("bootstrap or coverage hook was imported during no-site admission")

    coverage = next(row for row in selected_records if row["name"] == "coverage")
    coverage_rows = cast(list[dict[str, object]], coverage["record_rows"])
    coverage_pth = [row for row in coverage_rows if row["path"] == "a1_coverage.pth"]
    if len(coverage_pth) != 1 or coverage_pth[0]["sha256"] != exact_files["a1_coverage.pth"][1]:
        raise AdmissionError("coverage hook ownership/bytes differ")

    dist_info = site / "scouting_intelligence-0.1.0.dist-info"
    if not dist_info.is_dir() or dist_info.is_symlink():
        raise AdmissionError("editable dist-info authority is absent or unsafe")
    expected_names = (
        "INSTALLER",
        "METADATA",
        "RECORD",
        "REQUESTED",
        "WHEEL",
        "direct_url.json",
        "uv_build.json",
        "uv_cache.json",
    )
    if tuple(sorted(entry.name for entry in os.scandir(dist_info))) != expected_names:
        raise AdmissionError("editable dist-info physical file census differs")
    record_raw = _guard_read_absolute_regular(dist_info / "RECORD", expected_mode=0o644)
    declarations = list(csv.reader(record_raw.decode("utf-8", errors="strict").splitlines()))
    expected_record_paths = {
        *(f"{dist_info.name}/{name}" for name in expected_names),
        "scouting_intelligence.pth",
    }
    if len(declarations) != 9 or {row[0] for row in declarations} != expected_record_paths:
        raise AdmissionError("editable RECORD exact nine-row census differs")
    editable_records: list[dict[str, object]] = []
    for relative, digest_cell, size_cell in declarations:
        if relative == f"{dist_info.name}/RECORD":
            if digest_cell or size_cell:
                raise AdmissionError("editable RECORD self row differs")
            editable_records.append({"path": relative, "self": True})
            continue
        target = site / relative
        metadata = os.stat(target, follow_symlinks=False)
        raw = _guard_read_absolute_regular(target, expected_mode=stat.S_IMODE(metadata.st_mode))
        encoded = base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).decode().rstrip("=")
        if digest_cell != f"sha256={encoded}" or size_cell != str(len(raw)):
            raise AdmissionError("editable RECORD target declaration differs")
        editable_records.append(
            {
                "mode": stat.S_IMODE(metadata.st_mode),
                "path": relative,
                "sha256": _sha256(raw),
                "size_bytes": len(raw),
            }
        )
    exact_metadata = {
        "INSTALLER": (2, "e6184ce10e266134fdcfa401e8f1a95005bcd4f18d16b62b757323e2833fe9a9", b"uv"),
        "METADATA": (
            1_771,
            "ce423e8f2bde3826d54e952bf0c7059cdc426b2d4cd902e72e8dd91e8cd29351",
            None,
        ),
        "REQUESTED": (0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", b""),
        "WHEEL": (79, "45154ba95ba052614ea8179d0450260386ec8057113940624942a51118b41dc8", None),
        "uv_build.json": (
            2,
            "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a",
            b"{}",
        ),
    }
    for name, (size, digest, literal) in exact_metadata.items():
        raw = _guard_read_absolute_regular(
            dist_info / name, expected_mode=0o644, expected_size=size, expected_sha256=digest
        )
        if literal is not None and raw != literal:
            raise AdmissionError("editable generated metadata literal differs")

    pth_raw = _guard_read_absolute_regular(site / "scouting_intelligence.pth", expected_mode=0o644)
    expected_pth = os.fspath(root / "src").encode()
    if pth_raw != expected_pth or not (root / "src").resolve().is_relative_to(root):
        raise AdmissionError("editable root-bearing PTH relation differs")
    normalized_pth = b"<W04_PROJECT_ROOT>/src"
    direct_raw = _guard_read_absolute_regular(dist_info / "direct_url.json", expected_mode=0o644)
    direct = _load_strict_json(direct_raw)
    direct_expected = f'{{"url":"file://{root}","dir_info":{{"editable":true}}}}'.encode()
    if (
        direct_raw != direct_expected
        or type(direct) is not dict
        or direct
        != {
            "url": f"file://{root}",
            "dir_info": {"editable": True},
        }
    ):
        raise AdmissionError("editable direct_url relation differs")
    normalized_direct = b'{"url":"file://<W04_PROJECT_ROOT>","dir_info":{"editable":true}}'
    cache_raw = _guard_read_absolute_regular(dist_info / "uv_cache.json", expected_mode=0o644)
    cache = _load_strict_json(cache_raw)
    if type(cache) is not dict or set(cache) != {
        "timestamp",
        "commit",
        "tags",
        "env",
        "directories",
    }:
        raise AdmissionError("editable uv_cache key roster differs")
    cache_object = cast(dict[str, object], cache)
    if (
        cache_object["commit"] is not None
        or cache_object["tags"] is not None
        or cache_object["env"] != {}
        or set(cast(dict[str, object], cache_object["directories"])) != {"src"}
    ):
        raise AdmissionError("editable uv_cache structural predicate differs")
    for clock in (
        cache_object["timestamp"],
        cast(dict[str, object], cache_object["directories"])["src"],
    ):
        if (
            type(clock) is not dict
            or set(cast(dict[str, object], clock)) != {"secs_since_epoch", "nanos_since_epoch"}
            or any(type(value) is not int for value in cast(dict[str, object], clock).values())
        ):
            raise AdmissionError("editable uv_cache clock shape differs")
    normalized_cache = canonical_json_bytes(
        {
            "commit": None,
            "directories": ["src"],
            "env": {},
            "tags": None,
            "timestamp_policy": "operational-excluded",
        }
    )
    normalization = {
        "scouting_intelligence.pth": normalized_pth,
        f"{dist_info.name}/direct_url.json": normalized_direct,
        f"{dist_info.name}/uv_cache.json": normalized_cache,
    }
    stable_records: list[dict[str, object]] = []
    for row in editable_records:
        normalized = normalization.get(cast(str, row["path"]))
        if normalized is None:
            stable_records.append(row)
        else:
            stable_records.append(
                {
                    "mode": row["mode"],
                    "normalization": "ROOT_OR_CLOCK_EXACT",
                    "path": row["path"],
                    "sha256": _sha256(normalized),
                    "size_bytes": len(normalized),
                }
            )

    owners: dict[str, str] = {}
    for package in selected_records:
        owner = f"{package['name']}=={package['version']}"
        for row in cast(list[dict[str, object]], package["record_rows"]):
            relative = cast(str, row["path"])
            target = Path(os.path.normpath(os.fspath(site / relative)))
            if target.is_relative_to(site):
                key = target.relative_to(site).as_posix()
                if key in owners:
                    raise AdmissionError("installed concrete file has multiple RECORD owners")
                owners[key] = owner
    for row in editable_records:
        key = cast(str, row["path"])
        if key in owners:
            raise AdmissionError("editable concrete file has multiple RECORD owners")
        owners[key] = "scouting-intelligence==0.1.0"
    physical: set[str] = set()
    for directory, names, files in os.walk(site, topdown=True, followlinks=False):
        names[:] = sorted(name for name in names if name != "__pycache__")
        for name in sorted(files):
            if name.lower().endswith((".pyc", ".pyo")):
                continue
            path = Path(directory, name)
            metadata = os.stat(path, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise AdmissionError("installed site closure contains nonregular authority")
            physical.add(path.relative_to(site).as_posix())
    _require_global_site_ownership(physical, owners)
    editable_detail = {
        "algorithm": "w04-editable-root-stable-v2",
        "identity": {"name": "scouting-intelligence", "source": ".", "version": "0.1.0"},
        "lock_inputs": lock_inputs,
        "normalized_record_rows": tuple(stable_records),
        "pyproject_sha256": lock_inputs["pyproject_sha256"],
        "repository_rows": repository_rows,
        "uv_cache_policy": "exact-keys-commit-tags-null-env-empty-src-clock-excluded-v1",
    }
    return tuple(bootstrap_rows), editable_detail


def _darwin_loaded_image_paths() -> tuple[Path, ...]:
    """Observe dyld once without introducing a non-stdlib dependency."""

    if sys.platform != "darwin":
        return ()
    import ctypes

    loader = ctypes.CDLL(None)
    count = loader._dyld_image_count
    count.argtypes = []
    count.restype = ctypes.c_uint32
    image_name = loader._dyld_get_image_name
    image_name.argtypes = [ctypes.c_uint32]
    image_name.restype = ctypes.c_char_p
    paths: list[Path] = []
    for index in range(count()):
        raw = image_name(index)
        if raw is None:
            raise AdmissionError("dyld returned a null loaded-image name")
        spelling = raw.decode("utf-8", errors="strict")
        if not is_normalized("NFC", spelling):
            raise AdmissionError("dyld image path is not NFC")
        candidate = Path(spelling)
        if not candidate.is_absolute():
            raise AdmissionError("dyld image path is not absolute")
        paths.append(candidate)
    return tuple(paths)


def _require_site_ancestry(site: Path, target: Path, *, include_leaf: bool) -> None:
    if not target.is_relative_to(site):
        raise AdmissionError("runtime path escapes the selected site root")
    site_metadata = os.stat(site, follow_symlinks=False)
    if not stat.S_ISDIR(site_metadata.st_mode) or stat.S_ISLNK(site_metadata.st_mode):
        raise AdmissionError("runtime selected site root is unsafe")
    relative = target.relative_to(site)
    parts = relative.parts if include_leaf else relative.parts[:-1]
    current = site
    for part in parts:
        current = current / part
        metadata = os.stat(current, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise AdmissionError("runtime path has an unsafe site parent")


def _require_contained_ancestry(base: Path, target: Path, *, include_leaf: bool) -> None:
    if not target.is_relative_to(base):
        raise AdmissionError("runtime admitted path escapes its authority root")
    base_metadata = os.stat(base, follow_symlinks=False)
    if not stat.S_ISDIR(base_metadata.st_mode) or stat.S_ISLNK(base_metadata.st_mode):
        raise AdmissionError("runtime authority root is unsafe")
    parts = target.relative_to(base).parts
    current = base
    for part in parts if include_leaf else parts[:-1]:
        current = current / part
        metadata = os.stat(current, follow_symlinks=False)
        expected_directory = current != target or include_leaf
        if expected_directory and (
            not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode)
        ):
            raise AdmissionError("runtime admitted path has an unsafe parent")


def _interpreter_image_paths(root: Path, retained_paths: tuple[Path, Path]) -> frozenset[Path]:
    """Revalidate the exact accepted physical interpreter image authority."""

    executable = getattr(sys, "_base_executable", None)
    library_directory = sysconfig.get_config_var("LIBDIR")
    library_name = sysconfig.get_config_var("LDLIBRARY")
    if not all(
        type(value) is str and value for value in (executable, library_directory, library_name)
    ):
        raise AdmissionError("interpreter image authority is unavailable")
    physical = Path(cast(str, executable))
    library_root = Path(cast(str, library_directory))
    library_path = library_root / cast(str, library_name)
    if (
        type(retained_paths) is not tuple
        or len(retained_paths) != 2
        or any(not isinstance(path, Path) or not path.is_absolute() for path in retained_paths)
        or (physical, library_path) != retained_paths
    ):
        raise AdmissionError("retained interpreter image path authority differs")
    if (
        not physical.is_absolute()
        or physical != Path(sys.base_prefix) / "bin/python3.12"
        or library_root != Path(sys.base_prefix) / "lib"
        or Path(sys.executable) != root / ".venv/bin/python3"
        or sys.version_info[:3] != (3, 12, 12)
        or sys.implementation.name != "cpython"
        or sys.implementation.cache_tag != "cpython-312"
        or sys.platform != "darwin"
        or os.uname().machine != "arm64"
        or sysconfig.get_config_var("SOABI") != "cpython-312-darwin"
        or sysconfig.get_config_var("SHLIB_SUFFIX") != ".so"
        or sysconfig.get_config_var("MULTIARCH") != "darwin"
        or sysconfig.get_config_var("MACHDEP") != "darwin"
        or library_name != "libpython3.12.dylib"
        or tuple(importlib.machinery.EXTENSION_SUFFIXES)
        != (".cpython-312-darwin.so", ".abi3.so", ".so")
    ):
        raise AdmissionError("interpreter image path/configuration authority differs")
    physical_raw = _guard_read_absolute_regular(
        physical,
        expected_mode=0o755,
        expected_size=49_968,
        expected_sha256=PYTHON_PHYSICAL_SHA256,
    )
    library_raw = _guard_read_absolute_regular(
        library_path,
        expected_mode=0o755,
        expected_size=17_864_576,
        expected_sha256="e8b85a555061f39891e08783d18bc56f3444fefdde2a5f2ffcdb6b37dd217460",
    )
    if (
        len(physical_raw) != 49_968
        or _sha256(physical_raw) != PYTHON_PHYSICAL_SHA256
        or len(library_raw) != 17_864_576
        or _sha256(library_raw)
        != "e8b85a555061f39891e08783d18bc56f3444fefdde2a5f2ffcdb6b37dd217460"
    ):
        raise AdmissionError("interpreter image byte authority differs")
    return frozenset((physical, library_path))


def _require_admitted_non_site_image(path: Path, interpreter_images: frozenset[Path]) -> None:
    if (
        not path.is_absolute()
        or not is_normalized("NFC", os.fspath(path))
        or any(part in {"", ".", ".."} for part in path.parts[1:])
    ):
        raise AdmissionError("dyld non-site image spelling is unsafe")
    protected = path.is_relative_to(Path("/usr/lib")) or path.is_relative_to(
        Path("/System/Library")
    )
    if path not in interpreter_images and not protected:
        raise AdmissionError("dyld non-site image is outside admitted interpreter/system authority")


def _builtin_frozen_shape(module: object) -> tuple[object, ...]:
    spec = getattr(module, "__spec__", None)
    locations = getattr(spec, "submodule_search_locations", None)
    return (
        getattr(spec, "name", None),
        getattr(spec, "origin", None),
        getattr(spec, "loader", None),
        getattr(spec, "parent", None),
        None if locations is None else tuple(locations),
        getattr(spec, "cached", None),
        getattr(spec, "has_location", None),
        getattr(module, "__loader__", None),
        getattr(module, "__file__", None),
        getattr(module, "__cached__", None),
        getattr(module, "__package__", None),
    )


_BUILTIN_FROZEN_ALIASES: Final = {
    "importlib._bootstrap": "_frozen_importlib",
    "importlib._bootstrap_external": "_frozen_importlib_external",
    "os.path": "posixpath",
}
_BUILTIN_FROZEN_MODULE_NAME_OVERRIDES: Final = {
    "_collections_abc": "collections.abc",
    "_decimal": "decimal",
}
_FROZEN_PACKAGE_OVERRIDES: Final = {
    "_frozen_importlib": "importlib",
    "_frozen_importlib_external": "importlib",
}


class _RuntimeSubsetAuthority:
    """Frozen L/RECORD authority consumed by exactly one terminal R observation."""

    __slots__ = (
        "allowed_repository_files",
        "allowed_namespace_locations",
        "allowed_stdlib_files",
        "builtin_module_names",
        "builtin_importer",
        "_consumed",
        "extension_suffixes",
        "frozen_expected_specs",
        "frozen_importer",
        "frozen_module_names",
        "interpreter_image_paths",
        "owners",
        "repository_root",
        "resident_builtin_frozen",
        "selected_owners",
        "site",
        "stdlib",
    )

    def __init__(
        self,
        *,
        repository_root: Path,
        owners: dict[str, tuple[str, str, int, int, str]],
        selected_owners: frozenset[tuple[str, str]],
        allowed_repository_files: dict[Path, tuple[int, int, str]],
        allowed_stdlib_files: dict[Path, tuple[int, int, str]],
        allowed_namespace_locations: dict[str, dict[Path, tuple[int, int, int, int]]],
        interpreter_image_paths: frozenset[Path],
    ) -> None:
        self._consumed = False
        self.repository_root = repository_root
        self.site = repository_root / ".venv/lib/python3.12/site-packages"
        self.stdlib = Path(sysconfig.get_paths()["stdlib"]).absolute()
        self.extension_suffixes = tuple(importlib.machinery.EXTENSION_SUFFIXES)
        self.owners = owners
        self.selected_owners = selected_owners
        self.allowed_repository_files = allowed_repository_files
        self.allowed_stdlib_files = allowed_stdlib_files
        self.allowed_namespace_locations = allowed_namespace_locations
        self.interpreter_image_paths = interpreter_image_paths
        self.builtin_module_names = frozenset(sys.builtin_module_names)
        self.frozen_module_names = frozenset(__import__("_imp")._frozen_module_names())
        self.builtin_importer = importlib.machinery.BuiltinImporter
        self.frozen_importer = importlib.machinery.FrozenImporter
        frozen_expected_specs: dict[str, tuple[object, ...]] = {}
        for name in self.frozen_module_names:
            spec = self.frozen_importer.find_spec(name)
            if spec is not None:
                locations = spec.submodule_search_locations
                frozen_expected_specs[name] = (
                    spec.name,
                    spec.origin,
                    spec.parent,
                    None if locations is None else tuple(locations),
                    spec.cached,
                    spec.has_location,
                )
        self.frozen_expected_specs = frozen_expected_specs
        resident = tuple(sys.modules.items())
        for alias, canonical_name in _BUILTIN_FROZEN_ALIASES.items():
            if (
                alias not in sys.modules
                or canonical_name not in sys.modules
                or sys.modules[alias] is not sys.modules[canonical_name]
            ):
                raise AdmissionError("resident built-in/frozen alias authority differs")
        classified: dict[str, tuple[object, tuple[object, ...]]] = {}
        for name, module in resident:
            origin = getattr(getattr(module, "__spec__", None), "origin", None)
            if origin is not None and type(origin) is not str:
                raise AdmissionError("resident module origin is not one string")
            if origin == "built-in" or origin == "frozen":
                self._classify_builtin_frozen(name, module, origin)
                classified[name] = (module, _builtin_frozen_shape(module))
        self.resident_builtin_frozen = classified

    def _classify_builtin_frozen(self, module_key: str, module: object, origin: str) -> None:
        if type(module) is not ModuleType:
            raise AdmissionError("resident built-in/frozen claimant is not a module")
        canonical_name = _BUILTIN_FROZEN_ALIASES.get(module_key, module_key)
        spec = getattr(module, "__spec__", None)
        importer = self.builtin_importer if origin == "built-in" else self.frozen_importer
        expected_spec = importer.find_spec(canonical_name)
        locations = getattr(spec, "submodule_search_locations", None)
        expected_locations = (
            None
            if expected_spec is None or expected_spec.submodule_search_locations is None
            else tuple(expected_spec.submodule_search_locations)
        )
        observed_spec = (
            getattr(spec, "name", None),
            getattr(spec, "origin", None),
            getattr(spec, "loader", None),
            getattr(spec, "parent", None),
            None if locations is None else tuple(locations),
            getattr(spec, "cached", None),
            getattr(spec, "has_location", None),
        )
        expected_shape = (
            None if expected_spec is None else expected_spec.name,
            None if expected_spec is None else expected_spec.origin,
            importer,
            None if expected_spec is None else expected_spec.parent,
            expected_locations,
            None if expected_spec is None else expected_spec.cached,
            None if expected_spec is None else expected_spec.has_location,
        )
        loader_state = None if expected_spec is None else expected_spec.loader_state
        expected_module_name = _BUILTIN_FROZEN_MODULE_NAME_OVERRIDES.get(
            canonical_name,
            canonical_name if origin == "built-in" else getattr(loader_state, "origname", None),
        )
        expected_package = _FROZEN_PACKAGE_OVERRIDES.get(
            canonical_name,
            None if expected_spec is None else expected_spec.parent,
        )
        if (
            type(module_key) is not str
            or not is_normalized("NFC", module_key)
            or expected_spec is None
            or observed_spec != expected_shape
            or getattr(module, "__name__", None) != expected_module_name
            or getattr(module, "__loader__", None) is not importer
            or getattr(module, "__cached__", None) is not None
            or getattr(module, "__package__", None) != expected_package
            or (
                module_key != canonical_name
                and _BUILTIN_FROZEN_ALIASES.get(module_key) != canonical_name
            )
        ):
            raise AdmissionError("resident built-in/frozen module authority differs")
        module_file = getattr(module, "__file__", None)
        if origin == "built-in":
            if canonical_name not in self.builtin_module_names or module_file is not None:
                raise AdmissionError("resident built-in module file/name authority differs")
            return
        if canonical_name not in self.frozen_module_names:
            raise AdmissionError("resident frozen module name authority differs")
        expected_filename = getattr(loader_state, "filename", None)
        if type(expected_filename) is not str or not Path(expected_filename).is_absolute():
            raise AdmissionError("resident frozen expected file authority is unavailable")
        expected_path = Path(expected_filename)
        if (
            type(module_file) is not str
            or Path(module_file) != expected_path
            or not expected_path.is_relative_to(self.stdlib)
            or not self._admitted_non_site_file(expected_path)
        ):
            raise AdmissionError("resident frozen module file authority differs")

    def _validate_builtin_frozen(self, module_name: str, module: object, origin: str) -> None:
        resident = self.resident_builtin_frozen.get(module_name)
        if resident is not None:
            if module is not resident[0] or _builtin_frozen_shape(module) != resident[1]:
                raise AdmissionError("resident built-in/frozen module authority differs")
            return
        self._classify_builtin_frozen(module_name, module, origin)

    def _owned_file(self, path: Path) -> tuple[str, str, str]:
        if not path.is_absolute() or not path.is_relative_to(self.site):
            raise AdmissionError("runtime concrete origin is outside selected site authority")
        relative = path.relative_to(self.site).as_posix()
        if not is_normalized("NFC", relative) or relative.lower().endswith((".pyc", ".pyo")):
            raise AdmissionError("runtime concrete origin path is unsafe")
        owner = self.owners.get(relative)
        if owner is None:
            raise AdmissionError("runtime concrete origin is not singularly selected")
        owner_name, owner_version, mode, size, digest = owner
        _require_site_ancestry(self.site, path, include_leaf=False)
        _guard_read_absolute_regular(
            path,
            expected_mode=mode,
            expected_size=size,
            expected_sha256=digest,
        )
        return owner_name, owner_version, relative

    def _admitted_non_site_file(self, path: Path) -> bool:
        frozen = self.allowed_repository_files.get(path)
        authority_root = self.repository_root
        if frozen is None:
            frozen = self.allowed_stdlib_files.get(path)
            authority_root = self.stdlib
        if frozen is None:
            return False
        _require_contained_ancestry(authority_root, path, include_leaf=False)
        mode, size, digest = frozen
        _guard_read_absolute_regular(
            path, expected_mode=mode, expected_size=size, expected_sha256=digest
        )
        return True

    def _admitted_namespace_directory(self, subject: str, path: Path) -> bool:
        expected = self.allowed_namespace_locations.get(subject, {}).get(path)
        if expected is None:
            return False
        metadata = os.stat(path, follow_symlinks=False)
        observed = (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_nlink)
        if (
            not stat.S_ISDIR(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or observed != expected
        ):
            return False
        authority_root = self.repository_root / "src"
        if not path.is_relative_to(authority_root):
            authority_root = self.stdlib
        _require_contained_ancestry(authority_root, path, include_leaf=True)
        return True

    def _namespace_rows(self, subject: str, locations: object) -> list[dict[str, str]]:
        if type(locations) not in {list, tuple} and not hasattr(locations, "__iter__"):
            raise AdmissionError("runtime namespace locations are not iterable paths")
        observed_locations = tuple(cast(Iterable[object], locations))
        if not observed_locations:
            raise AdmissionError("runtime namespace locations are empty")
        rows: list[dict[str, str]] = []
        for location in observed_locations:
            if type(location) is not str or not is_normalized("NFC", location):
                raise AdmissionError("runtime namespace location is not one NFC path string")
            candidate = Path(location)
            if not candidate.is_absolute():
                raise AdmissionError("runtime namespace location is not absolute")
            if not candidate.is_relative_to(self.site):
                if self._admitted_namespace_directory(subject, candidate):
                    continue
                raise AdmissionError("runtime namespace location is external to admitted roots")
            metadata = os.stat(candidate, follow_symlinks=False)
            _require_site_ancestry(self.site, candidate, include_leaf=True)
            if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                raise AdmissionError("runtime namespace location is unsafe")
            relative = candidate.relative_to(self.site).as_posix()
            if not relative or not is_normalized("NFC", relative):
                raise AdmissionError("runtime namespace site path is unsafe")
            if subject != relative.replace("/", "."):
                raise AdmissionError("runtime namespace subject/location binding differs")
            prefix = relative + "/"
            if prefix + "__init__.py" in self.owners:
                raise AdmissionError("ordinary package was represented as a namespace")
            descendant_owners = {
                value[:2]
                for path, value in self.owners.items()
                if path.startswith(prefix) and "/__pycache__/" not in path
            }
            if not descendant_owners:
                raise AdmissionError("runtime namespace lacks a concrete selected descendant")
            for owner_name, owner_version in sorted(descendant_owners):
                rows.append(
                    {
                        "observation_kind": "NAMESPACE_LOCATION",
                        "owner_name": owner_name,
                        "owner_version": owner_version,
                        "site_relative_path": relative,
                        "subject_name": subject,
                    }
                )
        return rows

    def observe(self) -> tuple[tuple[dict[str, str], ...], str]:
        if self._consumed:
            raise AdmissionError("runtime subset authority was already observed")
        self._consumed = True
        if "_virtualenv" in sys.modules or "coverage.process_startup" in sys.modules:
            raise AdmissionError("denied bootstrap module became a runtime origin")
        rows: list[dict[str, str]] = []
        native_owner_by_root: dict[str, tuple[str, str]] = {}
        observed_owner_by_root: dict[str, set[tuple[str, str]]] = {}
        for module_name, module in sorted(tuple(sys.modules.items())):
            if type(module_name) is not str or not is_normalized("NFC", module_name):
                raise AdmissionError("runtime module key is not one NFC string")
            spec = getattr(module, "__spec__", None)
            origin = getattr(spec, "origin", None)
            locations = getattr(spec, "submodule_search_locations", None)
            if origin is None:
                if locations is not None:
                    namespace_rows = self._namespace_rows(module_name, locations)
                    rows.extend(namespace_rows)
                    if namespace_rows:
                        module_root = module_name.split(".", 1)[0]
                        observed_owner_by_root.setdefault(module_root, set()).update(
                            (row["owner_name"], row["owner_version"]) for row in namespace_rows
                        )
                else:
                    fallback = getattr(module, "__file__", None)
                    if fallback is None:
                        raise AdmissionError("runtime originless module has no admitted location")
                    if type(fallback) is not str or not is_normalized("NFC", fallback):
                        raise AdmissionError("runtime spec-less module file is not one NFC path")
                    fallback_path = Path(fallback)
                    if not fallback_path.is_absolute():
                        raise AdmissionError("runtime spec-less module file is not absolute")
                    if fallback_path.is_relative_to(self.site):
                        raise AdmissionError("runtime site module lacks an origin-bearing spec")
                    if not self._admitted_non_site_file(fallback_path):
                        raise AdmissionError("runtime spec-less module file is external")
                continue
            if type(origin) is not str:
                raise AdmissionError("runtime module origin is not one string")
            if origin == "built-in":
                self._validate_builtin_frozen(module_name, module, origin)
                continue
            if origin == "frozen":
                self._validate_builtin_frozen(module_name, module, origin)
                continue
            if not is_normalized("NFC", origin):
                raise AdmissionError("runtime module origin is not one NFC path string")
            path = Path(origin)
            if not path.is_absolute():
                raise AdmissionError("runtime module origin is neither admitted nor absolute")
            if not path.is_relative_to(self.site):
                if self._admitted_non_site_file(path):
                    continue
                raise AdmissionError(f"runtime module origin is external: {module_name}")
            owner_name, owner_version, relative = self._owned_file(path)
            if relative.endswith(".py"):
                kind = "MODULE_SOURCE"
                expected_subject = (
                    relative[: -len("/__init__.py")].replace("/", ".")
                    if relative.endswith("/__init__.py")
                    else relative[:-3].replace("/", ".")
                )
            elif any(relative.endswith(suffix) for suffix in self.extension_suffixes):
                kind = "NATIVE_EXTENSION"
                suffix = next(
                    suffix for suffix in self.extension_suffixes if relative.endswith(suffix)
                )
                expected_subject = relative[: -len(suffix)].replace("/", ".")
                module_root = module_name.split(".", 1)[0]
                existing_native_owner = native_owner_by_root.get(module_root)
                if existing_native_owner is not None and existing_native_owner != (
                    owner_name,
                    owner_version,
                ):
                    raise AdmissionError("native top-level module has conflicting owners")
                native_owner_by_root[module_root] = (owner_name, owner_version)
            else:
                raise AdmissionError("runtime site module origin has an unsupported kind")
            if module_name != expected_subject:
                raise AdmissionError("runtime module subject/path binding differs")
            module_root = module_name.split(".", 1)[0]
            observed_owner_by_root.setdefault(module_root, set()).add((owner_name, owner_version))
            rows.append(
                {
                    "observation_kind": kind,
                    "owner_name": owner_name,
                    "owner_version": owner_version,
                    "site_relative_path": relative,
                    "subject_name": module_name,
                }
            )
        for image_path in _darwin_loaded_image_paths():
            if not image_path.is_absolute():
                raise AdmissionError("dyld image path is not absolute")
            if not image_path.is_relative_to(self.site):
                _require_admitted_non_site_image(image_path, self.interpreter_image_paths)
                continue
            owner_name, owner_version, relative = self._owned_file(image_path)
            module_root = relative.split("/", 1)[0]
            observed_owner_by_root.setdefault(module_root, set()).add((owner_name, owner_version))
            if not relative.endswith((".so", ".dylib")) and not any(
                relative.endswith(suffix) for suffix in self.extension_suffixes
            ):
                raise AdmissionError("dyld site image does not have an admitted image suffix")
            rows.append(
                {
                    "observation_kind": "SITE_SHARED_IMAGE",
                    "owner_name": owner_name,
                    "owner_version": owner_version,
                    "site_relative_path": relative,
                    "subject_name": "DYLD_IMAGE",
                }
            )
        for module_root, required_owner in (
            ("pydantic_core", "pydantic-core"),
            ("_polars_runtime_32", "polars-runtime-32"),
        ):
            observed_owners = observed_owner_by_root.get(module_root, set())
            if module_root in sys.modules or observed_owners:
                observed_owner = native_owner_by_root.get(module_root)
                if (
                    observed_owner is None
                    or observed_owner[0] != required_owner
                    or observed_owners != {observed_owner}
                ):
                    raise AdmissionError(f"native runtime owner mapping differs: {module_root}")
        row_bytes = [(canonical_json_bytes(row), row) for row in rows]
        row_bytes.sort(key=lambda pair: pair[0])
        if not 1 <= len(row_bytes) <= 100_000 or len({raw for raw, _ in row_bytes}) != len(
            row_bytes
        ):
            raise AdmissionError("runtime subset cardinality or uniqueness differs")
        ordered = tuple(row for _, row in row_bytes)
        projection = {(row["owner_name"], row["owner_version"]) for row in ordered}
        if not projection or not projection.issubset(self.selected_owners):
            raise AdmissionError("runtime subset owner projection is not nonempty R subset L")
        digest = _sha256_json({"algorithm": RUNTIME_SUBSET_ALGORITHM, "rows": ordered})
        return ordered, digest


def freeze_runtime_subset_authority(
    root: Path,
    record_rows: tuple[dict[str, object], ...],
    selected_closure: tuple[dict[str, object], ...] | None = None,
    *,
    repository_rows: tuple[dict[str, object], ...] | None = None,
    stdlib_rows: tuple[dict[str, object], ...] | None = None,
    darwin_image_paths: tuple[Path, ...] | None = None,
    retained_interpreter_image_paths: tuple[Path, Path] | None = None,
) -> _RuntimeSubsetAuthority:
    """Freeze selected identities, exact RECORD owners, bytes, and extension suffixes."""

    site = root / ".venv/lib/python3.12/site-packages"
    selected_rows = record_rows if selected_closure is None else selected_closure
    selected = frozenset(
        (cast(str, package["name"]), cast(str, package["version"])) for package in selected_rows
    )
    owners: dict[str, tuple[str, str, int, int, str]] = {}
    for package in record_rows:
        owner_name = cast(str, package["name"])
        owner_version = cast(str, package["version"])
        if (owner_name, owner_version) not in selected:
            continue
        for row in cast(list[dict[str, object]], package["record_rows"]):
            if row.get("self") is True or "sha256" not in row:
                continue
            relative = cast(str, row["path"])
            target = Path(os.path.normpath(os.fspath(site / relative)))
            if not target.is_relative_to(site):
                continue
            key = target.relative_to(site).as_posix()
            if key in owners:
                raise AdmissionError("runtime concrete origin has multiple RECORD owners")
            owners[key] = (
                owner_name,
                owner_version,
                cast(int, row["mode"]),
                cast(int, row["size_bytes"]),
                cast(str, row["sha256"]),
            )
    if not selected or not owners:
        raise AdmissionError("runtime subset freeze lacks selected RECORD authority")
    observed_repository = _repository_rows(root) if repository_rows is None else repository_rows
    observed_stdlib = _stdlib_rows() if stdlib_rows is None else stdlib_rows
    allowed_repository_files = {
        root / cast(str, row["path"]): (
            cast(int, row["mode"]),
            cast(int, row["size_bytes"]),
            cast(str, row["sha256"]),
        )
        for row in observed_repository
        if row.get("state") != "AUTHORIZED_ABSENT"
    }
    stdlib_root = Path(os.__file__).resolve().parent
    allowed_stdlib_files = {
        stdlib_root / cast(str, row["path"]): (
            cast(int, row["mode"]),
            cast(int, row["size_bytes"]),
            cast(str, row["sha256"]),
        )
        for row in observed_stdlib
    }

    allowed_namespace_locations: dict[str, dict[Path, tuple[int, int, int, int]]] = {}
    for authority_root, allowed_files in (
        (root / "src", allowed_repository_files),
        (stdlib_root, allowed_stdlib_files),
    ):
        for allowed_file in allowed_files:
            if not allowed_file.is_relative_to(authority_root):
                continue
            current = allowed_file.parent
            while current != authority_root and current.is_relative_to(authority_root):
                relative_parts = current.relative_to(authority_root).parts
                if (
                    current / "__init__.py" not in allowed_files
                    and relative_parts
                    and all(part.isidentifier() for part in relative_parts)
                ):
                    _require_contained_ancestry(authority_root, current, include_leaf=True)
                    metadata = os.stat(current, follow_symlinks=False)
                    subject = ".".join(relative_parts)
                    allowed_namespace_locations.setdefault(subject, {})[current] = (
                        metadata.st_dev,
                        metadata.st_ino,
                        metadata.st_mode,
                        metadata.st_nlink,
                    )
                current = current.parent
    if darwin_image_paths is None:
        if retained_interpreter_image_paths is None:
            raise AdmissionError("runtime subset freeze lacks retained interpreter image paths")
        observed_images = _darwin_loaded_image_paths()
        interpreter_image_paths = _interpreter_image_paths(root, retained_interpreter_image_paths)
    else:
        # This explicit-image branch exists only for isolated unit authorities;
        # the repository freeze always performs the physical interpreter recheck.
        observed_images = darwin_image_paths
        interpreter_image_paths = frozenset()
    for image_path in observed_images:
        if not image_path.is_absolute():
            raise AdmissionError("frozen dyld authority contains a nonabsolute path")
        if not image_path.is_relative_to(site):
            _require_admitted_non_site_image(image_path, interpreter_image_paths)
    return _RuntimeSubsetAuthority(
        repository_root=root.absolute(),
        owners=owners,
        selected_owners=selected,
        allowed_repository_files=allowed_repository_files,
        allowed_stdlib_files=allowed_stdlib_files,
        allowed_namespace_locations=allowed_namespace_locations,
        interpreter_image_paths=interpreter_image_paths,
    )


def freeze_repository_runtime_subset_authority(
    root: Path, retained_interpreter_image_paths: tuple[Path, Path]
) -> _RuntimeSubsetAuthority:
    """Perform the sole pre-product L/RECORD freeze used by the rebuild child."""

    lock_inputs, preliminary, _declared_wheels = _lock_authority(root)
    if not lock_inputs:
        raise AdmissionError("runtime subset lock authority is empty")
    records = _installed_record_rows(root, preliminary)
    _selector, selected, _wheels = _selector_lock_and_wheels(root, preliminary, records)
    return freeze_runtime_subset_authority(
        root,
        records,
        selected,
        repository_rows=_repository_rows(root),
        stdlib_rows=_stdlib_rows(),
        retained_interpreter_image_paths=retained_interpreter_image_paths,
    )


def _validate_runtime_subset(root: Path, record_rows: tuple[dict[str, object], ...]) -> None:
    """Compatibility-only one-shot validator; stable collection never invokes it."""

    _interpreter, interpreter_paths = _interpreter_authority(root)
    freeze_runtime_subset_authority(
        root,
        record_rows,
        retained_interpreter_image_paths=interpreter_paths,
    ).observe()


def _executable_rows(
    root: Path, record_rows: tuple[dict[str, object], ...]
) -> tuple[dict[str, object], ...]:
    expected_names_by_owner = {
        "bandit": ("bandit", "bandit-baseline", "bandit-config-generator"),
        "cachecontrol": ("doesitcache",),
        "charset-normalizer": ("normalizer",),
        "coverage": ("coverage", "coverage-3.12", "coverage3"),
        "detect-secrets": ("detect-secrets", "detect-secrets-hook"),
        "fastapi": ("fastapi",),
        "httpx": ("httpx",),
        "hypothesis": ("hypothesis",),
        "idna": ("idna",),
        "import-linter": ("import-linter", "lint-imports"),
        "markdown-it-py": ("markdown-it",),
        "mypy": ("dmypy", "mypy", "mypyc", "stubgen", "stubtest"),
        "numpy": ("f2py", "numpy-config"),
        "pip": ("pip", "pip3"),
        "pip-audit": ("pip-audit",),
        "pip-licenses": ("pip-licenses",),
        "playwright": ("playwright",),
        "pygments": ("pygmentize",),
        "pytest": ("py.test", "pytest"),
        "uvicorn": ("uvicorn",),
    }
    direct: dict[str, tuple[str, str, str, str, dict[str, object]]] = {}
    bin_records: dict[str, tuple[str, str, dict[str, object]]] = {}
    for package in record_rows:
        owner = cast(str, package["name"])
        version = cast(str, package["version"])
        package_rows = cast(list[dict[str, object]], package["record_rows"])
        for record in package_rows:
            path = cast(str, record["path"])
            if path.startswith("../../../bin/"):
                name = path.removeprefix("../../../bin/")
                if (
                    re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name) is None
                    or "/" in name
                    or name.casefold() in {key.casefold() for key in bin_records}
                ):
                    raise AdmissionError("installed executable RECORD name is unsafe or colliding")
                bin_records[name] = (owner, version, record)
        entry_point_rows = [
            row
            for row in package_rows
            if cast(str, row["path"]).endswith(".dist-info/entry_points.txt")
        ]
        if len(entry_point_rows) > 1:
            raise AdmissionError("installed distribution has multiple entry-point authorities")
        if not entry_point_rows:
            continue
        entry_path = cast(str, entry_point_rows[0]["path"])
        raw = _guard_read_absolute_regular(
            root / ".venv/lib/python3.12/site-packages" / entry_path,
            expected_mode=cast(int, entry_point_rows[0]["mode"]),
            expected_size=cast(int, entry_point_rows[0]["size_bytes"]),
            expected_sha256=cast(str, entry_point_rows[0]["sha256"]),
        )
        text = raw.decode("utf-8", errors="strict")
        if "\r" in text or any(line[:1].isspace() for line in text.splitlines() if line):
            raise AdmissionError(
                "entry-point metadata has ambiguous continuation or newline syntax"
            )
        parser = configparser.ConfigParser(interpolation=None, strict=True)
        parser.optionxform = lambda option: option  # type: ignore[method-assign,assignment]
        try:
            parser.read_string(text)
        except configparser.Error as error:
            raise AdmissionError("entry-point metadata is not strict INI") from error
        for group in ("console_scripts", "gui_scripts"):
            if not parser.has_section(group):
                continue
            for name, value in parser.items(group):
                if (
                    re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", name) is None
                    or re.fullmatch(
                        r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*:[A-Za-z_][A-Za-z0-9_]*",
                        value,
                    )
                    is None
                    or name in direct
                ):
                    raise AdmissionError(
                        "direct entry-point declaration is malformed or duplicated"
                    )
                module, attribute = value.split(":", 1)
                direct[name] = (owner, version, group, f"{module}:{attribute}", entry_point_rows[0])
    actual_roster: dict[str, tuple[str, ...]] = {}
    for owner in sorted({value[0] for value in direct.values()}):
        actual_roster[owner] = tuple(
            sorted(name for name, value in direct.items() if value[0] == owner)
        )
    expected_roster = {key: tuple(sorted(value)) for key, value in expected_names_by_owner.items()}
    if actual_roster != expected_roster or len(direct) != 33:
        raise AdmissionError("direct executable entry-point census differs")
    if set(bin_records) != set(EXECUTABLE_NAMES) or len(bin_records) != 35:
        raise AdmissionError("total installed executable RECORD census differs")

    python3_tuples = {
        (
            "detect-secrets",
            "1.5.0",
            "detect-secrets",
            "console_scripts",
            "detect_secrets.main:main",
        ),
        (
            "detect-secrets",
            "1.5.0",
            "detect-secrets-hook",
            "console_scripts",
            "detect_secrets.pre_commit_hook:main",
        ),
        ("httpx", "0.28.1", "httpx", "console_scripts", "httpx:main"),
        ("pip-licenses", "5.5.5", "pip-licenses", "console_scripts", "piplicenses:main"),
    }
    rows: list[dict[str, object]] = []
    for name in EXECUTABLE_NAMES:
        owner, version, record = bin_records[name]
        executable_path = root / ".venv/bin" / name
        metadata = os.stat(executable_path, follow_symlinks=False)
        if (
            not stat.S_ISREG(metadata.st_mode)
            or stat.S_ISLNK(metadata.st_mode)
            or metadata.st_nlink != 1
            or stat.S_IMODE(metadata.st_mode) != 0o755
        ):
            raise AdmissionError("installed executable is not a singular mode-0755 regular file")
        raw = _guard_read_absolute_regular(
            executable_path,
            expected_mode=0o755,
            expected_size=cast(int, record["size_bytes"]),
            expected_sha256=cast(str, record["sha256"]),
        )
        if name == "ruff":
            if (
                (owner, version) != ("ruff", "0.16.0")
                or len(raw) != 23_669_488
                or _sha256(raw)
                != "1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52"
            ):
                raise AdmissionError("sole wheel-script executable differs")
            rows.append(
                {
                    "authority_class": "W",
                    "mode": 0o755,
                    "name": name,
                    "owner": f"{owner}=={version}",
                    "record_path": cast(str, record["path"]),
                    "sha256": _sha256(raw),
                    "size_bytes": len(raw),
                    "source": "ruff-0.16.0.data/scripts/ruff",
                }
            )
            continue
        authority_class = "P" if name == "pip3.12" else "E"
        if authority_class == "P":
            if (owner, version) != ("pip", "26.1.2") or direct["pip"][3] != direct["pip3"][3]:
                raise AdmissionError("pip interpreter-version alias authority differs")
            group = "derived-pip-interpreter-version-alias"
            target = "pip._internal.cli.main:main"
            alias = "python"
        else:
            direct_owner, direct_version, group, target, _entry_row = direct[name]
            if (owner, version) != (direct_owner, direct_version):
                raise AdmissionError("entry-point and installed executable owners differ")
            alias = (
                "python3" if (owner, version, name, group, target) in python3_tuples else "python"
            )
        module, attribute = target.split(":", 1)
        body = (
            "# -*- coding: utf-8 -*-\n"
            "import sys\n"
            f"from {module} import {attribute}\n"
            'if __name__ == "__main__":\n'
            '    if sys.argv[0].endswith("-script.pyw"):\n'
            "        sys.argv[0] = sys.argv[0][:-11]\n"
            '    elif sys.argv[0].endswith(".exe"):\n'
            "        sys.argv[0] = sys.argv[0][:-4]\n"
            f"    sys.exit({attribute}())\n"
        ).encode()
        expected = f"#!{root}/.venv/bin/{alias}\n".encode() + body
        if raw != expected:
            raise AdmissionError("installed text wrapper differs from its selected exact template")
        token = "W04_VENV_WRAPPER_PYTHON3" if alias == "python3" else "W04_VENV_WRAPPER_PYTHON"
        normalized = f"#!<{token}>\n".encode() + body
        rows.append(
            {
                "authority_class": authority_class,
                "entry_point_group": group,
                "mode": 0o755,
                "name": name,
                "normalized_sha256": _sha256(normalized),
                "normalized_size_bytes": len(normalized),
                "owner": f"{owner}=={version}",
                "record_path": cast(str, record["path"]),
                "selected_alias": alias,
                "target": target,
            }
        )
    classes = [cast(str, row["authority_class"]) for row in rows]
    aliases = [row.get("selected_alias") for row in rows]
    if (
        classes.count("E") != 33
        or classes.count("P") != 1
        or classes.count("W") != 1
        or len({cast(str, row["owner"]) for row in rows}) != 21
        or aliases.count("python") != 30
        or aliases.count("python3") != 4
    ):
        raise AdmissionError("closed executable class/owner/alias cardinalities differ")
    return tuple(rows)


def _selector_lock_and_wheels(
    root: Path,
    preliminary_closure: tuple[dict[str, object], ...],
    record_rows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], tuple[dict[str, object], ...], tuple[dict[str, object], ...]]:
    packaging_record = next(row for row in record_rows if row["name"] == "packaging")
    if len(cast(list[object], packaging_record["record_rows"])) < 20:
        raise AdmissionError("Packaging bootstrap RECORD is incomplete")
    site_root = root / ".venv/lib/python3.12/site-packages"
    site_spelling = os.fspath(site_root)
    if site_spelling not in sys.path:
        sys.path.insert(0, site_spelling)
    from packaging.markers import Marker, default_environment
    from packaging.tags import sys_tags
    from packaging.utils import canonicalize_name, parse_wheel_filename
    from packaging.version import Version

    marker_environment = cast(dict[str, str], dict(default_environment()))
    ordered_tag_values = tuple(sys_tags())
    ordered_tags = tuple(str(tag) for tag in ordered_tag_values)
    if len(ordered_tags) != 1_230 or len(set(ordered_tags)) != len(ordered_tags):
        raise AdmissionError("Packaging compatible-tag selector is incomplete or duplicated")
    for module_name, module in tuple(sys.modules.items()):
        if module_name == "packaging" or module_name.startswith("packaging."):
            origin = getattr(module, "__file__", None)
            if type(origin) is not str or not Path(origin).is_relative_to(site_root / "packaging"):
                raise AdmissionError("Packaging bootstrap imported an unadmitted origin")
            if origin.endswith(".pyc"):
                raise AdmissionError("Packaging bootstrap loaded operational bytecode")
    imported_packaging_modules = sorted(
        name for name in sys.modules if name == "packaging" or name.startswith("packaging.")
    )
    if imported_packaging_modules != [
        "packaging",
        "packaging._elffile",
        "packaging._manylinux",
        "packaging._musllinux",
        "packaging._parser",
        "packaging._tokenizer",
        "packaging.markers",
        "packaging.specifiers",
        "packaging.tags",
        "packaging.utils",
        "packaging.version",
    ]:
        raise AdmissionError("Packaging bootstrap loaded-module roster differs")
    lock_raw = _guard_read_relative(root, "uv.lock")
    parsed = tomllib.loads(lock_raw.decode("utf-8", errors="strict"))
    packages = cast(list[dict[str, object]], parsed["package"])
    by_name = {cast(str, package["name"]): package for package in packages}
    root_package = by_name["scouting-intelligence"]
    groups = (
        "data",
        "e2e",
        "lint-type",
        "model",
        "orchestration",
        "runtime",
        "security",
        "test",
    )
    dev = cast(dict[str, list[dict[str, object]]], root_package["dev-dependencies"])
    if tuple(sorted(dev)) != groups:
        raise AdmissionError("selected dependency-group roster differs")
    queue: list[tuple[str, str, tuple[str, ...]]] = []
    for group in groups:
        queue.extend(
            (cast(str, edge["name"]), f"scouting-intelligence[{group}]", tuple())
            for edge in dev[group]
        )
    parents: dict[str, set[str]] = {}
    selected_extras: dict[str, set[str]] = {}
    while queue:
        name, parent, extras = queue.pop(0)
        package = by_name.get(name)
        if package is None or "registry" not in cast(dict[str, object], package.get("source", {})):
            raise AdmissionError("selected lock edge does not resolve to one registry package")
        parents.setdefault(name, set()).add(parent)
        newly_added_extras = set(extras) - selected_extras.setdefault(name, set())
        first_visit = len(parents[name]) == 1
        if not first_visit and not newly_added_extras:
            continue
        if first_visit:
            for edge in cast(list[dict[str, object]], package.get("dependencies", [])):
                marker = edge.get("marker")
                if marker is not None and (
                    type(marker) is not str or not Marker(marker).evaluate(marker_environment)
                ):
                    continue
                edge_extras = edge.get("extra", [])
                if type(edge_extras) is not list or any(
                    type(item) is not str for item in edge_extras
                ):
                    raise AdmissionError("selected lock edge extras are malformed")
                queue.append(
                    (
                        cast(str, edge["name"]),
                        name,
                        tuple(cast(list[str], edge_extras)),
                    )
                )
        optional = cast(
            dict[str, list[dict[str, object]]], package.get("optional-dependencies", {})
        )
        for extra in sorted(newly_added_extras):
            if extra not in optional:
                raise AdmissionError("selected lock extra lacks optional-dependency authority")
            queue.extend(
                (cast(str, edge["name"]), f"{name}[{extra}]", tuple()) for edge in optional[extra]
            )
    preliminary_names = {cast(str, row["name"]) for row in preliminary_closure}
    if set(parents) != preliminary_names:
        raise AdmissionError(
            "marker/extra lock traversal differs from installed closure: "
            f"lock_only={sorted(set(parents) - preliminary_names)}, "
            f"installed_only={sorted(preliminary_names - set(parents))}"
        )
    tag_rank = {tag: index for index, tag in enumerate(ordered_tag_values)}
    closure_rows: list[dict[str, object]] = []
    selected_wheels: list[dict[str, object]] = []
    for name in sorted(parents):
        package = by_name[name]
        version = cast(str, package["version"])
        candidates: list[tuple[int, dict[str, object], str, list[str]]] = []
        for wheel in cast(list[dict[str, object]], package.get("wheels", [])):
            url = cast(str, wheel["url"])
            filename = Path(urllib.parse.urlparse(url).path).name
            parsed_name, parsed_version, _build, tags = parse_wheel_filename(filename)
            if canonicalize_name(parsed_name) != name or Version(str(parsed_version)) != Version(
                version
            ):
                raise AdmissionError("locked wheel filename identity differs")
            ranks = [tag_rank[tag] for tag in tags if tag in tag_rank]
            if ranks:
                candidates.append((min(ranks), wheel, filename, sorted(str(tag) for tag in tags)))
        if not candidates:
            raise AdmissionError("selected lock member has no compatible wheel")
        best_rank = min(row[0] for row in candidates)
        best = [row for row in candidates if row[0] == best_rank]
        if len(best) != 1:
            raise AdmissionError("selected lock member has a compatible-wheel rank tie")
        rank, wheel, filename, declared_tags = best[0]
        wheel_row = {
            "declared_tags": declared_tags,
            "filename": filename,
            "lock_hash": wheel["hash"],
            "lock_size": wheel["size"],
            "name": name,
            "rank": rank,
            "version": version,
        }
        selected_wheels.append(wheel_row)
        closure_rows.append(
            {
                "extras": sorted(selected_extras[name]),
                "name": name,
                "parents": sorted(parents[name]),
                "source": package["source"],
                "version": version,
                "wheel": wheel_row,
            }
        )
    selector: dict[str, object] = {
        "algorithm": "w04-packaging-tag-bootstrap-v1",
        "imported_packaging_modules": imported_packaging_modules,
        "marker_environment": {key: marker_environment[key] for key in sorted(marker_environment)},
        "ordered_tags": list(ordered_tags),
        "packaging_record_sha256": _sha256_json(packaging_record),
        "packaging_version": "26.2",
    }
    return selector, tuple(closure_rows), tuple(selected_wheels)


def _stable_installed_record_rows(
    record_rows: tuple[dict[str, object], ...],
    executable_rows: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], ...]:
    """Remove only verified root-bearing wrapper bytes from stable RECORD identity."""

    executable_by_path = {cast(str, row["record_path"]): row for row in executable_rows}
    stable_packages: list[dict[str, object]] = []
    for package in record_rows:
        stable_records: list[dict[str, object]] = []
        for record in cast(list[dict[str, object]], package["record_rows"]):
            executable = executable_by_path.get(cast(str, record["path"]))
            if executable is None or executable["authority_class"] == "W":
                stable_records.append(record)
                continue
            stable_records.append(
                {
                    "mode": record["mode"],
                    "normalization_role": executable["selected_alias"],
                    "path": record["path"],
                    "sha256": executable["normalized_sha256"],
                    "size_bytes": executable["normalized_size_bytes"],
                }
            )
        stable_packages.append(
            {
                "name": package["name"],
                "record_rows": stable_records,
                "version": package["version"],
            }
        )
    return tuple(stable_packages)


def _cache_extracted_rows(
    root: Path,
    wheels: tuple[dict[str, object], ...],
) -> tuple[tuple[dict[str, object], ...], dict[str, dict[str, object]]]:
    cache_root = Path(
        os.environ.get("UV_CACHE_DIR", os.fspath(Path.home() / ".cache/uv"))
    ).absolute()
    archive_root = cache_root / "archive-v0"
    archive_metadata = os.lstat(archive_root)
    if not stat.S_ISDIR(archive_metadata.st_mode) or stat.S_ISLNK(archive_metadata.st_mode):
        raise AdmissionError("uv archive-v0 root is not one physical directory")
    site_root = root / ".venv/lib/python3.12/site-packages"
    rows: list[dict[str, object]] = []
    mapped_destinations: dict[str, dict[str, object]] = {}
    extracted_identities: set[tuple[int, int]] = set()
    for wheel in wheels:
        name = cast(str, wheel["name"])
        version = cast(str, wheel["version"])
        filename = cast(str, wheel["filename"])
        marker = f"-{version}-"
        marker_index = filename.find(marker)
        if marker_index <= 0 or not filename.endswith(".whl"):
            raise AdmissionError("selected wheel filename cannot derive exact cache key")
        cache_key = filename[marker_index + 1 : -4]
        association = cache_root / "wheels-v5" / "pypi" / name / cache_key
        association_metadata = os.lstat(association)
        if not stat.S_ISLNK(association_metadata.st_mode) or association_metadata.st_nlink != 1:
            raise AdmissionError("selected wheel cache association is not one symlink")
        raw_target = os.readlink(association)
        if not raw_target or "\x00" in raw_target:
            raise AdmissionError("selected wheel cache target is empty or malformed")
        raw_path = Path(raw_target)
        extracted_root = (
            raw_path if raw_path.is_absolute() else association.parent / raw_path
        ).absolute()
        extracted_metadata = os.lstat(extracted_root)
        if (
            not extracted_root.is_relative_to(archive_root)
            or not stat.S_ISDIR(extracted_metadata.st_mode)
            or stat.S_ISLNK(extracted_metadata.st_mode)
            or extracted_metadata.st_nlink < 2
        ):
            raise AdmissionError("selected wheel extracted tree escapes archive-v0")
        extracted_identity = (extracted_metadata.st_dev, extracted_metadata.st_ino)
        if extracted_identity in extracted_identities:
            raise AdmissionError("selected wheels ambiguously share one extracted target")
        extracted_identities.add(extracted_identity)
        dist_name = name.replace("-", "_")
        record_relative = f"{dist_name}-{version}.dist-info/RECORD"
        record_path = extracted_root / record_relative
        record_metadata = os.stat(record_path, follow_symlinks=False)
        record_raw = _guard_read_absolute_regular(
            record_path, expected_mode=stat.S_IMODE(record_metadata.st_mode)
        )
        declarations = list(csv.reader(record_raw.decode("utf-8", errors="strict").splitlines()))
        if not declarations or any(len(row) != 3 for row in declarations):
            raise AdmissionError("extracted RECORD row shape differs")
        declared_paths: set[str] = set()
        for declared_path, _digest, _size in declarations:
            parsed_path = PurePosixPath(declared_path)
            if (
                parsed_path.is_absolute()
                or "\\" in declared_path
                or any(part in {"", ".", ".."} for part in parsed_path.parts)
                or declared_path in declared_paths
            ):
                raise AdmissionError("extracted RECORD contains an unsafe or duplicate path")
            declared_paths.add(declared_path)
        physical_paths: set[str] = set()
        tree_rows: list[dict[str, object]] = []
        for directory, directory_names, file_names in os.walk(
            extracted_root, topdown=True, followlinks=False
        ):
            for directory_name in directory_names:
                if Path(directory, directory_name).is_symlink():
                    raise AdmissionError("extracted wheel tree contains a directory symlink")
            directory_names.sort()
            for file_name in sorted(file_names):
                path = Path(directory, file_name)
                metadata = os.stat(path, follow_symlinks=False)
                if not stat.S_ISREG(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
                    raise AdmissionError("extracted wheel tree contains a nonregular entry")
                relative = path.relative_to(extracted_root).as_posix()
                physical_paths.add(relative)
                raw = _guard_read_absolute_regular(
                    path, expected_mode=stat.S_IMODE(metadata.st_mode)
                )
                tree_rows.append(
                    {
                        "mode": stat.S_IMODE(metadata.st_mode),
                        "path": relative,
                        "sha256": _sha256(raw),
                        "size_bytes": len(raw),
                    }
                )
        if physical_paths != declared_paths:
            raise AdmissionError("extracted wheel tree does not equal its RECORD set")
        declaration_by_path = {row[0]: row for row in declarations}
        for tree_row in tree_rows:
            relative = cast(str, tree_row["path"])
            digest_cell, size_cell = declaration_by_path[relative][1:]
            if relative == record_relative:
                if digest_cell or size_cell:
                    raise AdmissionError("extracted RECORD self row is not empty")
                # The installed RECORD is installer-generated authority: it adds
                # INSTALLER/REQUESTED and the generated executable rows.  Both
                # RECORDs are verified independently and are not payload-equal.
                continue
            else:
                expected_digest = (
                    base64.urlsafe_b64encode(bytes.fromhex(cast(str, tree_row["sha256"])))
                    .decode()
                    .rstrip("=")
                )
                if (
                    digest_cell != f"sha256={expected_digest}"
                    or not size_cell.isdecimal()
                    or int(size_cell) != tree_row["size_bytes"]
                ):
                    raise AdmissionError("extracted RECORD target hash/size differs")
            parts = PurePosixPath(relative).parts
            data_marker = next(
                (index for index, part in enumerate(parts) if part.endswith(".data")),
                None,
            )
            if data_marker is None:
                installed_path = site_root / relative
                scheme = "root"
            else:
                if data_marker != 0 or len(parts) < 3:
                    raise AdmissionError("wheel data-scheme path shape differs")
                scheme = parts[data_marker + 1]
                tail = parts[data_marker + 2 :]
                if scheme in {"purelib", "platlib"}:
                    installed_path = site_root.joinpath(*tail)
                elif scheme == "scripts":
                    installed_path = root / ".venv/bin" / Path(*tail)
                elif scheme == "headers":
                    installed_path = root / ".venv/include/site/python3.12" / name / Path(*tail)
                elif scheme == "data":
                    installed_path = root / ".venv" / Path(*tail)
                else:
                    raise AdmissionError("wheel uses an unsupported PEP 427 data scheme")
            if not installed_path.is_relative_to(root / ".venv"):
                raise AdmissionError("PEP 427 mapping escapes the environment")
            destination = installed_path.relative_to(root / ".venv").as_posix()
            mapped = {
                "mode": tree_row["mode"],
                "owner": name,
                "record_path": relative,
                "scheme": scheme,
                "sha256": tree_row["sha256"],
                "size_bytes": tree_row["size_bytes"],
            }
            previous = mapped_destinations.get(destination)
            if previous is not None and previous != mapped:
                raise AdmissionError("PEP 427 mapping collides or overwrites another payload")
            mapped_destinations[destination] = mapped
            installed_metadata = os.stat(installed_path, follow_symlinks=False)
            installed_raw = _guard_read_absolute_regular(
                installed_path,
                expected_mode=stat.S_IMODE(installed_metadata.st_mode),
            )
            if _sha256(installed_raw) != tree_row["sha256"]:
                raise AdmissionError(
                    "PEP 427 extracted-to-installed payload differs: "
                    f"{name}:{relative}->{installed_path.relative_to(root)}"
                )
        rows.append(
            {
                "association_policy": "one-symlink-contained-archive-v0",
                "cache_key": cache_key,
                "name": name,
                "tree_digest": _sha256_json(tree_rows),
                "tree_row_count": len(tree_rows),
                "version": version,
                "wheel": wheel,
            }
        )
    return tuple(rows), mapped_destinations


def _stdlib_rows() -> tuple[dict[str, object], ...]:
    root = Path(os.__file__).resolve().parent
    definitions = (
        (
            "encodings/__init__.py",
            5_884,
            "78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8",
        ),
        (
            "encodings/aliases.py",
            15_677,
            "6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2",
        ),
        (
            "encodings/utf_8.py",
            1_005,
            "ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d",
        ),
    )
    bootstrap_rows = []
    for relative, size, digest in definitions:
        raw = _guard_read_absolute_regular(
            root / relative,
            expected_mode=0o644,
            expected_size=size,
            expected_sha256=digest,
        )
        bootstrap_rows.append({"path": relative, "sha256": _sha256(raw), "size_bytes": len(raw)})
    rows: list[dict[str, object]] = []
    for directory, names, files in os.walk(root, topdown=True, followlinks=False):
        names[:] = sorted(
            name
            for name in names
            if name not in {"__pycache__", "site-packages"}
            and not Path(directory, name).is_symlink()
        )
        for name in sorted(files):
            path = Path(directory, name)
            relative = path.relative_to(root).as_posix()
            metadata = os.stat(path, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                raise AdmissionError("standard-library authority contains a file symlink")
            if not stat.S_ISREG(metadata.st_mode) or name.lower().endswith((".pyc", ".pyo")):
                continue
            mode = stat.S_IMODE(metadata.st_mode)
            if mode not in {0o644, 0o755} or mode & 0o022:
                raise AdmissionError("standard-library authority has an unsafe writable mode")
            raw = _guard_read_absolute_regular(
                path,
                expected_mode=mode,
            )
            rows.append(
                {
                    "mode": mode,
                    "path": relative,
                    "sha256": _sha256(raw),
                    "size_bytes": len(raw),
                }
            )
    if len(rows) != 748:
        raise AdmissionError("complete standard-library authority cardinality differs")
    by_path = {cast(str, row["path"]): row for row in rows}
    if any(by_path.get(cast(str, row["path"])) != {**row, "mode": 420} for row in bootstrap_rows):
        raise AdmissionError("complete stdlib authority differs from bootstrap rows")
    return tuple(rows)


def _interpreter_authority(
    root: Path,
) -> tuple[dict[str, object], tuple[Path, Path]]:
    base_executable = getattr(sys, "_base_executable", None)
    if type(base_executable) is not str or not base_executable:
        raise AdmissionError("interpreter physical executable authority is unavailable")
    physical = Path(base_executable)
    raw = _guard_read_absolute_regular(
        physical,
        expected_mode=0o755,
        expected_size=49_968,
        expected_sha256=PYTHON_PHYSICAL_SHA256,
    )
    if sys.version_info[:3] != (3, 12, 12):
        raise AdmissionError("interpreter version differs from Python 3.12.12")
    aliases: list[dict[str, object]] = []
    bin_root = root / ".venv/bin"
    symlink_census = sorted(
        entry.name
        for entry in os.scandir(bin_root)
        if stat.S_ISLNK(entry.stat(follow_symlinks=False).st_mode)
    )
    if symlink_census != ["python", "python3", "python3.12"]:
        raise AdmissionError("exact three-alias scripts-directory census differs")
    alias_identities: set[tuple[int, int]] = set()
    for name in ("python", "python3", "python3.12"):
        alias = bin_root / name
        metadata = os.lstat(alias)
        if (
            not stat.S_ISLNK(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o755
            or metadata.st_nlink != 1
        ):
            raise AdmissionError("required venv interpreter alias is not a symlink")
        identity = (metadata.st_dev, metadata.st_ino)
        if identity in alias_identities:
            raise AdmissionError("venv interpreter aliases share an lstat identity")
        alias_identities.add(identity)
        target = os.readlink(alias)
        if name in {"python3", "python3.12"} and target != "python":
            raise AdmissionError("relative venv interpreter alias chain differs")
        if name == "python" and target != os.fspath(physical):
            raise AdmissionError("primary venv interpreter alias target differs")
        resolved = alias.resolve(strict=True)
        if resolved != physical.resolve(strict=True):
            raise AdmissionError("venv interpreter aliases do not share physical authority")
        aliases.append(
            {
                "alias": name,
                "raw_target_role": (
                    "<W04_PYTHON_PHYSICAL_EXECUTABLE>" if name == "python" else "python"
                ),
                "resolution_hops": 1 if name == "python" else 2,
            }
        )
    extension_suffixes = tuple(importlib.machinery.EXTENSION_SUFFIXES)
    if (
        sys.implementation.name != "cpython"
        or sys.version != "3.12.12 (main, Dec 17 2025, 21:07:08) [Clang 21.1.4 ]"
        or sys.platform != "darwin"
        or os.uname().machine != "arm64"
        or sys.implementation.cache_tag != "cpython-312"
        or sysconfig.get_config_var("SOABI") != "cpython-312-darwin"
        or extension_suffixes != (".cpython-312-darwin.so", ".abi3.so", ".so")
        or Path(sys.executable) != root / ".venv/bin/python3"
    ):
        raise AdmissionError("interpreter ABI/cache-tag authority differs")
    library_name = sysconfig.get_config_var("LDLIBRARY")
    library_root = sysconfig.get_config_var("LIBDIR")
    if type(library_name) is not str or type(library_root) is not str:
        raise AdmissionError("required loaded libpython authority is absent")
    library_path = Path(library_root) / library_name
    library_raw = _guard_read_absolute_regular(
        library_path,
        expected_mode=0o755,
        expected_size=17_864_576,
        expected_sha256="e8b85a555061f39891e08783d18bc56f3444fefdde2a5f2ffcdb6b37dd217460",
    )
    if (
        library_name != "libpython3.12.dylib"
        or sysconfig.get_config_var("SHLIB_SUFFIX") != ".so"
        or sysconfig.get_config_var("MULTIARCH") != "darwin"
        or sysconfig.get_config_var("MACHDEP") != "darwin"
    ):
        raise AdmissionError("libpython/loader configuration differs")
    loader_raw = _guard_read_absolute_regular(
        Path("/usr/lib/dyld"),
        expected_mode=0o755,
        expected_size=2_374_000,
        expected_sha256="6da2d109f72330d031450f3c0ebea14bfc10f42f844a958858e16a4092c38f12",
    )
    library_row = {
        "mode": 0o755,
        "role": "W04_LIBPYTHON",
        "sha256": _sha256(library_raw),
        "size_bytes": len(library_raw),
    }
    detail = {
        "alias_policy": "w04-venv-wrapper-interpreter-alias-v2",
        "aliases": aliases,
        "abi_flags": sys.abiflags,
        "cache_tag": sys.implementation.cache_tag,
        "extension_suffixes": list(extension_suffixes),
        "full_version": sys.version,
        "implementation": "cpython",
        "launch_alias_observation": "python3",
        "libpython": library_row,
        "loader": {
            "mode": 0o755,
            "role": "W04_DARWIN_DYNAMIC_LOADER",
            "sha256": _sha256(loader_raw),
            "size_bytes": len(loader_raw),
        },
        "loader_configuration": {
            "ldlibrary": "libpython3.12.dylib",
            "machdep": "darwin",
            "multiarch": "darwin",
            "shlib_suffix": ".so",
        },
        "machine": "arm64",
        "physical_sha256": _sha256(raw),
        "physical_size_bytes": len(raw),
        "python_version": "3.12.12",
        "required_aliases": ["python", "python3", "python3.12"],
        "soabi": "cpython-312-darwin",
        "sys_platform": "darwin",
    }
    return detail, (physical, library_path)


def _uv_authority(root: Path) -> dict[str, object]:
    logical = Path("/opt/homebrew/bin/uv")
    metadata = os.lstat(logical)
    if not stat.S_ISLNK(metadata.st_mode) or os.readlink(logical) != "../Cellar/uv/0.9.21/bin/uv":
        raise AdmissionError("current uv logical one-hop link differs")
    physical = Path("/opt/homebrew/Cellar/uv/0.9.21/bin/uv")
    raw = _guard_read_absolute_regular(
        physical,
        expected_mode=0o555,
        expected_size=41_617_552,
        expected_sha256=UV_PHYSICAL_SHA256,
    )
    observation_environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "UV": "/opt/homebrew/bin/uv",
    }
    observation = subprocess.run(  # noqa: S603  # nosec B603
        ("uv", "--version"),
        cwd=root,
        env=observation_environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
        timeout=10,
    )
    if observation.returncode != 0 or observation.stdout != (UV_VERSION + "\n").encode():
        raise AdmissionError("normal logical uv version observation differs")
    if observation.stderr:
        raise AdmissionError("normal logical uv observation emitted diagnostics")
    return {
        "link_policy": "w04-uv-logical-one-hop-relative-link-v1",
        "physical_sha256": _sha256(raw),
        "physical_size_bytes": len(raw),
        "uv_version": UV_VERSION,
        "version_observed_through_literal_" + "token": True,
    }


def _venv_bootstrap_rows(root: Path) -> tuple[dict[str, object], ...]:
    paths = (
        ".venv/lib/python3.12/site-packages/_virtualenv.pth",
        ".venv/lib/python3.12/site-packages/_virtualenv.py",
        ".venv/lib/python3.12/site-packages/a1_coverage.pth",
        ".venv/lib/python3.12/site-packages/scouting_intelligence.pth",
        ".venv/lib/python3.12/site-packages/scouting_intelligence-0.1.0.dist-info/direct_url.json",
    )
    return tuple(_file_row(root, path) for path in paths)


def _foreign_pyc_denial_predicates() -> tuple[dict[str, object], ...]:
    """Return the one exact, metadata-only foreign-cache denial predicate."""

    return (
        {
            "authority_class": "REPOSITORY_FOREIGN_CACHE_TAG_DENIED",
            "cache_path": ("scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc"),
            "cache_tag": "cpython-314",
            "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
            "expected_mode": 0o644,
            "expected_size_bytes": 190_312,
            "source_authority_required": "REPOSITORY_CODE_MANIFEST",
            "source_path": "scripts/admit_wyscout_v5_runtime.py",
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
    )


def _pyc_policy_source_map(
    root: Path,
    record_rows: tuple[dict[str, object], ...],
    repository_rows: tuple[dict[str, object], ...],
    bootstrap_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    """Build stable PYC authority without opening or deriving from any PYC file."""

    source_rows: list[dict[str, object]] = []
    for package in record_rows:
        owner = f"{package['name']}=={package['version']}"
        for record in cast(list[dict[str, object]], package["record_rows"]):
            path = cast(str, record["path"])
            if not path.endswith(".py"):
                continue
            parsed = PurePosixPath(path)
            if parsed.is_absolute() or ".." in parsed.parts:
                raise AdmissionError("third-party PYC source authority escapes site-packages")
            source_rows.append(
                {
                    "authority_class": "SELECTED_DISTRIBUTION_RECORD",
                    "normal_cache_name": f"{parsed.stem}.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
                    "owner": owner,
                    "path": path,
                    "pytest_cache_name": f"{parsed.stem}.cpython-312-pytest-9.1.1.pyc",
                    "sha256": record["sha256"],
                    "size_bytes": record["size_bytes"],
                }
            )
    for record in repository_rows:
        path = cast(str, record["path"])
        if not path.endswith(".py") or record.get("state") == "AUTHORIZED_ABSENT":
            continue
        parsed = PurePosixPath(path)
        source_rows.append(
            {
                "authority_class": "REPOSITORY_CODE_MANIFEST",
                "normal_cache_name": f"{parsed.stem}.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
                "owner": path,
                "path": path,
                "pytest_cache_name": f"{parsed.stem}.cpython-312-pytest-9.1.1.pyc",
                "sha256": record["sha256"],
                "size_bytes": record["size_bytes"],
            }
        )
    bootstrap = next(
        row
        for row in bootstrap_rows
        if row["path"] == ".venv/lib/python3.12/site-packages/_virtualenv.py"
    )
    source_rows.append(
        {
            "authority_class": "UV_VENV_BOOTSTRAP",
            "normal_cache_name": "_virtualenv.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
            "owner": "uv==0.9.21",
            "path": "_virtualenv.py",
            "pytest_cache_name": None,
            "sha256": bootstrap["sha256"],
            "size_bytes": bootstrap["size_bytes"],
        }
    )
    identities = [(row["authority_class"], row["owner"], row["path"]) for row in source_rows]
    if len(identities) != len(set(identities)):
        raise AdmissionError("PYC stable source authority is duplicated")
    source_rows.sort(key=canonical_json_bytes)
    orphan_predicates = (
        {
            "authority_class": "SITE_SIX_OPTIONAL_INERT_ORPHAN",
            "cache_path": "__pycache__/six.cpython-312.pyc",
            "expected_mode": 0o644,
            "expected_sha256": "4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28",
            "expected_size_bytes": 41_388,
            "source_path": "six.py",
            "source_required_absent": True,
            "traversal_root_role": "SELECTED_SITE_PACKAGES",
        },
        {
            "authority_class": "REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN",
            "cache_path": "migrations/__pycache__/env.cpython-312.pyc",
            "expected_mode": 0o644,
            "expected_sha256": "6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2",
            "expected_size_bytes": 2_795,
            "source_path": "migrations/env.py",
            "source_required_absent": True,
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
        {
            "authority_class": "REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN",
            "cache_path": "migrations/versions/__pycache__/0001_foundation.cpython-312.pyc",
            "expected_mode": 0o644,
            "expected_sha256": "b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d",
            "expected_size_bytes": 25_415,
            "source_path": "migrations/versions/0001_foundation.py",
            "source_required_absent": True,
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
        {
            "authority_class": "REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN",
            "cache_path": "src/scouting/storage/__pycache__/postgres.cpython-312.pyc",
            "expected_mode": 0o644,
            "expected_sha256": "ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac",
            "expected_size_bytes": 4_230,
            "source_path": "src/scouting/storage/postgres.py",
            "source_required_absent": True,
            "traversal_root_role": "WHOLE_REPOSITORY",
        },
    )
    site_root = root / ".venv/lib/python3.12/site-packages"
    stable_paths = {cast(str, row["path"]) for row in source_rows}
    for predicate in orphan_predicates:
        source_path = cast(str, predicate["source_path"])
        candidate = (
            site_root / source_path
            if predicate["traversal_root_role"] == "SELECTED_SITE_PACKAGES"
            else root / source_path
        )
        if candidate.exists() or source_path in stable_paths:
            raise AdmissionError("optional inert PYC orphan gained a source authority")
    if (
        importlib.util.MAGIC_NUMBER.hex() != "cb0d0d0a"
        or sys.implementation.cache_tag != "cpython-312"
    ):
        raise AdmissionError("PYC interpreter magic/cache-tag authority differs")
    foreign_predicates = _foreign_pyc_denial_predicates()
    foreign_source = cast(str, foreign_predicates[0]["source_path"])
    foreign_source_rows = [row for row in source_rows if row["path"] == foreign_source]
    if (
        len(foreign_source_rows) != 1
        or foreign_source_rows[0]["authority_class"] != "REPOSITORY_CODE_MANIFEST"
    ):
        raise AdmissionError("foreign-tag denied PYC source authority differs")
    return {
        "algorithm": "w10-preexisting-pyc-enumerate-deny-audit-v1",
        "cache_tag": "cpython-312",
        "foreign_cache_tag_denial_predicates": foreign_predicates,
        "magic_hex": "cb0d0d0a",
        "normal_grammar": "<stem>.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
        "no_cleanup": True,
        "orphan_predicates": orphan_predicates,
        "post_w04_audit_only_source_paths": _derive_post_w04_audit_only_pyc_source_paths(
            root,
            frozenset(
                cast(str, row["path"])
                for row in source_rows
                if row["authority_class"] == "REPOSITORY_CODE_MANIFEST"
            ),
        ),
        "post_w04_retired_audit_only_pyc_predicates": (POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES),
        "pytest_grammar": "<stem>.cpython-312-pytest-9.1.1.pyc",
        "pytest_version": "9.1.1",
        "source_rows": tuple(source_rows),
        "traversal_root_roles": ["SELECTED_SITE_PACKAGES", "WHOLE_REPOSITORY"],
        "zero_in_place_pyc_change": True,
        "zero_python_role_pyc_read": True,
    }


def _operational_pyc_inventory(
    root: Path, policy: dict[str, object]
) -> tuple[dict[str, object], ...]:
    """Independently classify every actual PYC/cache directory without selecting it."""

    site = root / ".venv/lib/python3.12/site-packages"
    source_rows = cast(tuple[dict[str, object], ...], policy["source_rows"])
    site_sources = {
        cast(str, row["path"]): row
        for row in source_rows
        if row["authority_class"] in {"SELECTED_DISTRIBUTION_RECORD", "UV_VENV_BOOTSTRAP"}
    }
    repository_sources = {
        cast(str, row["path"]): row
        for row in source_rows
        if row["authority_class"] == "REPOSITORY_CODE_MANIFEST"
    }
    audit_only_rows = policy.get("post_w04_audit_only_source_paths")
    expected_audit_only_rows = _derive_post_w04_audit_only_pyc_source_paths(
        root,
        frozenset(repository_sources),
    )
    if type(audit_only_rows) is not tuple or canonical_json_bytes(
        audit_only_rows
    ) != canonical_json_bytes(expected_audit_only_rows):
        missing = tuple(
            sorted(
                set(expected_audit_only_rows) - set(cast(tuple[str, ...], audit_only_rows or ()))
            )
        )
        unexpected = tuple(
            sorted(
                set(cast(tuple[str, ...], audit_only_rows or ())) - set(expected_audit_only_rows)
            )
        )
        raise AdmissionError(
            "post-W04 audit-only PYC source roster differs from derived Python sources; "
            f"missing={missing!r}; unexpected={unexpected!r}"
        )
    audit_only_sources = set(cast(tuple[str, ...], audit_only_rows))
    retired_rows = policy.get("post_w04_retired_audit_only_pyc_predicates")
    if type(retired_rows) is not tuple or canonical_json_bytes(
        retired_rows
    ) != canonical_json_bytes(POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES):
        raise AdmissionError("post-W04 retired audit-only PYC predicate differs")
    retired_predicates = cast(tuple[dict[str, object], ...], retired_rows)
    retired_by_path = {cast(str, row["cache_path"]): row for row in retired_predicates}
    if len(retired_by_path) != len(retired_predicates):
        raise AdmissionError("post-W04 retired audit-only PYC predicate is duplicated")
    for predicate in retired_predicates:
        if (root / cast(str, predicate["source_path"])).exists():
            raise AdmissionError("post-W04 retired PYC regained its source path")
    foreign_rows = policy.get("foreign_cache_tag_denial_predicates")
    expected_foreign_rows = _foreign_pyc_denial_predicates()
    if type(foreign_rows) is not tuple or canonical_json_bytes(
        foreign_rows
    ) != canonical_json_bytes(expected_foreign_rows):
        raise AdmissionError("foreign-tag denied PYC predicate differs")
    foreign_predicates = cast(tuple[dict[str, object], ...], foreign_rows)
    foreign_by_path = {cast(str, row["cache_path"]): row for row in foreign_predicates}
    if len(foreign_by_path) != len(foreign_predicates):
        raise AdmissionError("foreign-tag denied PYC predicate is duplicated")
    foreign_source = cast(str, foreign_predicates[0]["source_path"])
    foreign_source_rows = [
        row
        for row in source_rows
        if row.get("path") == foreign_source
        and row.get("authority_class") == "REPOSITORY_CODE_MANIFEST"
    ]
    if len(foreign_source_rows) != 1:
        raise AdmissionError("foreign-tag denied PYC source authority differs")
    foreign_source_row = foreign_source_rows[0]
    if (
        frozenset(foreign_source_row)
        != {
            "authority_class",
            "normal_cache_name",
            "owner",
            "path",
            "pytest_cache_name",
            "sha256",
            "size_bytes",
        }
        or foreign_source_row["owner"] != foreign_source
        or foreign_source_row["normal_cache_name"]
        != "admit_wyscout_v5_runtime.cpython-312[.opt-0|.opt-1|.opt-2].pyc"
        or foreign_source_row["pytest_cache_name"]
        != "admit_wyscout_v5_runtime.cpython-312-pytest-9.1.1.pyc"
        or type(foreign_source_row["sha256"]) is not str
        or SHA256_RE.fullmatch(foreign_source_row["sha256"]) is None
        or type(foreign_source_row["size_bytes"]) is not int
    ):
        raise AdmissionError("foreign-tag denied PYC source row differs")
    try:
        foreign_source_metadata = os.lstat(root / foreign_source)
    except OSError as exc:
        raise AdmissionError("foreign-tag denied PYC source path differs") from exc
    if (
        not stat.S_ISREG(foreign_source_metadata.st_mode)
        or stat.S_ISLNK(foreign_source_metadata.st_mode)
        or stat.S_IMODE(foreign_source_metadata.st_mode) != 0o644
        or foreign_source_metadata.st_nlink != 1
        or foreign_source_metadata.st_size != foreign_source_row["size_bytes"]
    ):
        raise AdmissionError("foreign-tag denied PYC source path differs")
    orphan_rows = cast(tuple[dict[str, object], ...], policy["orphan_predicates"])
    site_orphans = {
        cast(str, row["cache_path"]): row
        for row in orphan_rows
        if row["traversal_root_role"] == "SELECTED_SITE_PACKAGES"
    }
    repository_orphans = {
        cast(str, row["cache_path"]): row
        for row in orphan_rows
        if row["traversal_root_role"] == "WHOLE_REPOSITORY"
    }
    for predicate in orphan_rows:
        source = cast(str, predicate["source_path"])
        candidate = (
            site / source
            if predicate["traversal_root_role"] == "SELECTED_SITE_PACKAGES"
            else root / source
        )
        if candidate.exists():
            raise AdmissionError("optional inert PYC orphan gained a source sibling")
    inventory: list[dict[str, object]] = []
    seen_foreign_paths: set[str] = set()
    normal = re.compile(r"^(?P<stem>.+)\.cpython-312(?:\.opt-[012])?\.pyc$")
    pytest_name = re.compile(r"^(?P<stem>.+)\.cpython-312-pytest-9\.1\.1\.pyc$")
    foreign_normal = re.compile(r"^(?P<stem>.+)\.(?P<tag>cpython-[0-9]+)(?:\.opt-[012])?\.pyc$")
    foreign_pytest = re.compile(
        r"^(?P<stem>.+)\.(?P<tag>cpython-[0-9]+)-pytest-[0-9]+"
        r"(?:\.[0-9]+){1,2}\.pyc$"
    )
    for traversal_root, role, sources, orphans in (
        (site, "SELECTED_SITE_PACKAGES", site_sources, site_orphans),
        (root, "WHOLE_REPOSITORY", repository_sources, repository_orphans),
    ):
        for directory, names, files in os.walk(traversal_root, topdown=True, followlinks=False):
            if role == "WHOLE_REPOSITORY" and Path(directory) == root:
                names[:] = [name for name in names if name != ".venv"]
            for name in names:
                if Path(directory, name).is_symlink():
                    raise AdmissionError("child PYC traversal contains a directory symlink")
            names.sort()
            if Path(directory).name == "__pycache__":
                metadata = os.lstat(directory)
                if (
                    not stat.S_ISDIR(metadata.st_mode)
                    or stat.S_ISLNK(metadata.st_mode)
                    or stat.S_IMODE(metadata.st_mode) != 0o755
                ):
                    raise AdmissionError("child PYC cache-directory metadata differs")
                inventory.append(
                    {
                        "ctime_ns": metadata.st_ctime_ns,
                        "device": metadata.st_dev,
                        "entry_kind": "CACHE_DIRECTORY",
                        "inode": metadata.st_ino,
                        "link_count": metadata.st_nlink,
                        "mode": stat.S_IMODE(metadata.st_mode),
                        "mtime_ns": metadata.st_mtime_ns,
                        "path": Path(directory).relative_to(traversal_root).as_posix(),
                        "role": role,
                        "size_bytes": metadata.st_size,
                    }
                )
            for name in sorted(files):
                if name.endswith(".pyo"):
                    raise AdmissionError(
                        "child PYC traversal contains forbidden optimized bytecode"
                    )
                if not name.endswith(".pyc"):
                    continue
                path = Path(directory, name)
                relative = path.relative_to(traversal_root).as_posix()
                metadata = os.lstat(path)
                if (
                    not stat.S_ISREG(metadata.st_mode)
                    or stat.S_ISLNK(metadata.st_mode)
                    or stat.S_IMODE(metadata.st_mode) != 0o644
                    or metadata.st_nlink != 1
                ):
                    raise AdmissionError("child PYC lstat metadata differs")
                orphan = orphans.get(relative)
                if orphan is not None:
                    if metadata.st_size != orphan["expected_size_bytes"] or metadata.st_size < 16:
                        raise AdmissionError("child optional inert PYC orphan size differs")
                    authority = orphan["authority_class"]
                    source_path = None
                    source_authority = None
                    classification_fields: dict[str, object] = {}
                else:
                    if path.parent.name != "__pycache__":
                        raise AdmissionError("child PYC is outside an exact cache directory")
                    foreign = foreign_by_path.get(relative) if role == "WHOLE_REPOSITORY" else None
                    if foreign is not None:
                        if (
                            metadata.st_size != foreign["expected_size_bytes"]
                            or stat.S_IMODE(metadata.st_mode) != foreign["expected_mode"]
                        ):
                            raise AdmissionError("child foreign-tag denied PYC metadata differs")
                        authority = foreign["authority_class"]
                        source_path = foreign["source_path"]
                        source_authority = None
                        classification_fields = {
                            "denial_policy": foreign["denial_policy"],
                            "foreign_cache_tag": foreign["cache_tag"],
                            "source_authority_required": foreign["source_authority_required"],
                        }
                        seen_foreign_paths.add(relative)
                    else:
                        retired = (
                            retired_by_path.get(relative) if role == "WHOLE_REPOSITORY" else None
                        )
                        if retired is not None:
                            if metadata.st_size < 16:
                                raise AdmissionError("child post-W04 retired PYC metadata differs")
                            authority = retired["authority_class"]
                            source_path = retired["source_path"]
                            source_authority = None
                            classification_fields = {
                                "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                "denial_policy": retired["denial_policy"],
                                "source_required_absent": True,
                            }
                        else:
                            match = pytest_name.fullmatch(name)
                            rewrite = match is not None
                            if match is None:
                                match = normal.fullmatch(name)
                            if match is not None:
                                source_path = (
                                    (path.parent.parent / f"{match.group('stem')}.py")
                                    .relative_to(traversal_root)
                                    .as_posix()
                                )
                                if source_path in sources:
                                    source_authority = cast(
                                        str, sources[source_path]["authority_class"]
                                    )
                                    if source_authority == "UV_VENV_BOOTSTRAP":
                                        authority = "UV_BOOTSTRAP_NORMAL"
                                    elif role == "SELECTED_SITE_PACKAGES":
                                        authority = (
                                            "SITE_PYTEST_REWRITE"
                                            if rewrite
                                            else "SITE_DISTRIBUTION_NORMAL"
                                        )
                                    else:
                                        authority = (
                                            "REPOSITORY_PYTEST_REWRITE"
                                            if rewrite
                                            else "REPOSITORY_NORMAL"
                                        )
                                    classification_fields = {}
                                elif (
                                    role == "WHOLE_REPOSITORY" and source_path in audit_only_sources
                                ):
                                    authority = "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY"
                                    source_authority = None
                                    classification_fields = {
                                        "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                        "denial_policy": "POST_W04_SOURCE_CACHE_DENIED_ZERO_READ",
                                    }
                                else:
                                    raise AdmissionError(
                                        "child PYC lacks stable source or exact orphan authority: "
                                        f"{role}:{relative}->{source_path}"
                                    )
                            else:
                                foreign_match = foreign_pytest.fullmatch(name)
                                if foreign_match is None:
                                    foreign_match = foreign_normal.fullmatch(name)
                                if (
                                    foreign_match is None
                                    or foreign_match.group("tag") == "cpython-312"
                                ):
                                    raise AdmissionError("child PYC filename/tag grammar differs")
                                source_path = (
                                    (path.parent.parent / f"{foreign_match.group('stem')}.py")
                                    .relative_to(traversal_root)
                                    .as_posix()
                                )
                                if role == "WHOLE_REPOSITORY" and source_path == foreign_source:
                                    raise AdmissionError("child PYC filename/tag grammar differs")
                                authority = (
                                    "SITE_FOREIGN_CACHE_TAG_AUDIT_ONLY"
                                    if role == "SELECTED_SITE_PACKAGES"
                                    else "REPOSITORY_FOREIGN_CACHE_TAG_AUDIT_ONLY"
                                )
                                source_authority = None
                                classification_fields = {
                                    "authority_scope": "AUDIT_ONLY_ZERO_READ_USE",
                                    "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
                                    "foreign_cache_tag": foreign_match.group("tag"),
                                }
                row: dict[str, object] = {
                    "authority_class": authority,
                    "entry_kind": "PYC",
                    "mode": 0o644,
                    "path": relative,
                    "role": role,
                    "device": metadata.st_dev,
                    "inode": metadata.st_ino,
                    "mtime_ns": metadata.st_mtime_ns,
                    "ctime_ns": metadata.st_ctime_ns,
                    "size_bytes": metadata.st_size,
                    "source_path": source_path,
                    "source_authority": source_authority,
                }
                row.update(classification_fields)
                inventory.append(row)
    if seen_foreign_paths != set(foreign_by_path):
        raise AdmissionError("foreign-tag denied PYC path is missing")
    inventory.sort(key=canonical_json_bytes)
    return tuple(inventory)


def _pyc_security_projection(
    snapshot: tuple[dict[str, object], ...],
) -> dict[str, object]:
    """Project portable security facts while excluding raw host cache metadata."""

    protected: list[dict[str, object]] = []
    keys = (
        "authority_class",
        "denial_policy",
        "entry_kind",
        "foreign_cache_tag",
        "mode",
        "path",
        "role",
        "size_bytes",
        "source_authority",
        "source_authority_required",
        "source_path",
    )
    for row in snapshot:
        if row.get("authority_class") == "REPOSITORY_FOREIGN_CACHE_TAG_DENIED":
            protected.append({key: row.get(key) for key in keys})
    protected.sort(key=canonical_json_bytes)
    return {
        "algorithm": "w10-pyc-portable-security-projection-v1",
        "audit_only_authority_classes": (
            "REPOSITORY_FOREIGN_CACHE_TAG_AUDIT_ONLY",
            "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY",
            "REPOSITORY_RETIRED_POST_W04_CACHE_AUDIT_ONLY",
            "SITE_FOREIGN_CACHE_TAG_AUDIT_ONLY",
        ),
        "protected_denials": tuple(protected),
        "raw_inventory_authority": "AUDIT_ONLY_ZERO_READ_USE",
        "unsafe_metadata_policy": "FAIL_CLOSED_BEFORE_PROJECTION",
    }


def _collect_stable_authority_with_pyc(
    repository_root: Path,
) -> tuple[
    str,
    dict[str, object],
    tuple[int, ...],
    tuple[dict[str, object], ...],
    tuple[Path, Path],
]:
    """Independently reconstruct the stable v16 manifest inputs from exact paths."""

    root = Path(repository_root).absolute()
    repository_rows = _repository_rows(root)
    resource_rows = _local_resource_rows(root)
    lock_inputs, preliminary_closure, _declared_wheels = _lock_authority(root)
    record_rows = _installed_record_rows(root, preliminary_closure)
    bootstrap_rows, editable_detail = _site_bootstrap_editable_authority(
        root, record_rows, repository_rows, lock_inputs
    )
    selector, closure, wheels = _selector_lock_and_wheels(root, preliminary_closure, record_rows)
    extracted_rows, mapped_destinations = _cache_extracted_rows(root, wheels)
    _validate_installed_mapping(root, record_rows, mapped_destinations)
    executable_rows = _executable_rows(root, record_rows)
    stable_record_rows = _stable_installed_record_rows(record_rows, executable_rows)
    stdlib_rows = _stdlib_rows()
    interpreter, interpreter_image_paths = _interpreter_authority(root)
    uv = _uv_authority(root)
    pyc_policy = _pyc_policy_source_map(root, record_rows, repository_rows, bootstrap_rows)
    pyc_before = _operational_pyc_inventory(root, pyc_policy)
    launcher_row = next(
        row for row in repository_rows if row["path"] == "scripts/launch_wyscout_v5.py"
    )
    component_details: dict[str, object] = {
        "child_result_contract_digest": {
            "frame_magic": "W04CRSLT",
            "frame_version": 1,
            "payload_schema": CHILD_RESULT_SCHEMA_VERSION,
            "roles": ["PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"],
            "runtime_subset": {
                "algorithm": RUNTIME_SUBSET_ALGORITHM,
                "final_recheck_schema": FINAL_RECHECK_SCHEMA_VERSION,
                "observation_fields": list(RUNTIME_OBSERVATION_FIELDS),
                "observation_kinds": list(RUNTIME_OBSERVATION_KINDS),
            },
        },
        "editable_root_digest": editable_detail,
        "environment_values_digest": {
            "algorithm": "w04-child-environment-input-v2",
            "literal_environment": _STATIC_ENVIRONMENT,
            "normalized_tokens": _NORMALIZED_ENVIRONMENT_TOKENS,
            "required_absent": REQUIRED_ABSENT_ENVIRONMENT,
        },
        "executable_census_digest": {
            "algorithm": "w04-installed-executable-census-v3",
            "rows": executable_rows,
        },
        "extracted_runtime_digest": {
            "algorithm": "w04-verified-cache-extracted-pep427-v1",
            "rows": extracted_rows,
        },
        "installed_record_runtime_digest": {
            "algorithm": "w04-installed-record-runtime-v1",
            "ownership_policy": "singular-record-owner-complete-site-closure-v1",
            "rows": stable_record_rows,
            "runtime_subset_policy": RUNTIME_SUBSET_POLICY,
        },
        "interpreter_digest": interpreter,
        "local_launcher_control_digest": {
            "algorithm": "w04-local-control-bootstrap-v4",
            "launcher": launcher_row,
            "ordered_argv": list(ADMISSION_ARGV),
            "source_descriptor_policy": "w04-inherited-source-fd-v1",
            "uv_authority": uv,
        },
        "local_resource_digest": {
            "algorithm": LOCAL_RESOURCE_DIGEST_ALGORITHM,
            "rows": resource_rows,
        },
        "lock_inputs_digest": lock_inputs,
        "process_launch_contract_digest": {
            "admission_argv": list(ADMISSION_ARGV),
            "child_process_observation_policy": "operational-build-excluded-closed-v1",
            "child_roles": ["PRE_BUILD_ADMISSION", "POST_BUILD_ID_REBUILD"],
            "child_input_schema": CHILD_INPUT_SCHEMA_VERSION,
            "projection_schema": "w04-wyscout-pre-build-projection-v1",
            "rebuild_argv": list(REBUILD_ARGV),
        },
        "pyc_policy_source_map_digest": {
            **pyc_policy,
        },
        "selected_lock_closure_digest": {
            "algorithm": "w04-selected-all-groups-lock-closure-v1",
            "groups": [
                "data",
                "e2e",
                "lint-type",
                "model",
                "orchestration",
                "runtime",
                "security",
                "test",
            ],
            "rows": closure,
        },
        "selector": selector,
        "selector_bootstrap_digest": {
            "algorithm": "w04-packaging-tag-bootstrap-v1",
            "packaging_record": next(row for row in record_rows if row["name"] == "packaging"),
            "selector": selector,
        },
        "stdlib_digest": {"algorithm": "w04-stdlib-exact-sources-v1", "rows": stdlib_rows},
        "uv_physical_sha256": UV_PHYSICAL_SHA256,
        "uv_version": UV_VERSION,
        "venv_bootstrap_digest": {
            "algorithm": "w04-uv-venv-bootstrap-deny-v1",
            "rows": bootstrap_rows,
        },
        "wheel_declaration_digest": {
            "algorithm": "w04-complete-wheel-declaration-v1",
            "rows": wheels,
        },
    }
    components: dict[str, object] = {}
    counts: list[int] = []
    for key in COMPONENT_KEYS:
        detail = component_details[key]
        if key == "selector":
            components[key] = detail
        elif key == "uv_version":
            components[key] = UV_VERSION
        elif key == "uv_physical_sha256":
            components[key] = UV_PHYSICAL_SHA256
        else:
            components[key] = _sha256_json(detail)
        if type(detail) is dict and type(detail.get("rows")) is tuple:
            counts.append(max(1, len(cast(tuple[object, ...], detail["rows"]))))
        else:
            counts.append(1)
    repository_digest = _sha256_json(
        {"algorithm": "w04-explicit-repository-code-manifest-v1", "rows": repository_rows}
    )
    pyc_after = _operational_pyc_inventory(root, pyc_policy)
    if _pyc_security_projection(pyc_after) != _pyc_security_projection(pyc_before):
        raise AdmissionError("child portable PYC security projection drifted")
    return repository_digest, components, tuple(counts), pyc_before, interpreter_image_paths


def collect_stable_authority(
    repository_root: Path,
) -> tuple[str, dict[str, object], tuple[int, ...]]:
    """Return only stable authority; operational PYC evidence remains excluded."""

    repository, components, counts, _pyc, _interpreter_paths = _collect_stable_authority_with_pyc(
        repository_root
    )
    return repository, components, counts


def encode_result_frame(payload: bytes) -> bytes:
    if not 1 <= len(payload) <= 16_777_216:
        raise AdmissionError("result payload length is outside the frame bound")
    return (
        FRAME_MAGIC
        + FRAME_VERSION.to_bytes(2, "big")
        + len(payload).to_bytes(4, "big")
        + payload
        + hashlib.sha256(payload).digest()
    )


def _decode_input(value: str) -> tuple[dict[str, object], bytes]:
    if not value or "=" in value or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None:
        raise AdmissionError("child input base64url is malformed")
    padded = value + "=" * (-len(value) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
    except Exception as error:
        raise AdmissionError("child input base64url cannot decode") from error
    if not 1 <= len(raw) <= MAX_INPUT_BYTES:
        raise AdmissionError("child input is outside the size bound")
    if base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=") != value:
        raise AdmissionError("child input base64url is not canonical")
    decoded = load_canonical_json(raw)
    if type(decoded) is not dict:
        raise AdmissionError("child input must be an object")
    return cast(dict[str, object], decoded), raw


def _strict_fd(environment_name: str) -> int:
    value = os.environ.get(environment_name, "")
    if FD_RE.fullmatch(value) is None:
        raise AdmissionError(f"{environment_name} is not a strict descriptor")
    descriptor = int(value)
    if descriptor > 2_147_483_647:
        raise AdmissionError(f"{environment_name} exceeds the descriptor bound")
    return descriptor


def _outer_environment_authority() -> dict[str, object]:
    present = {**_OUTER_LITERAL_ENVIRONMENT, **_OUTER_ENVIRONMENT_TOKENS}
    return {
        "algorithm": "w04-outer-environment-bootstrap-v2",
        "excluded_until_insertion": ["W04_BOOTSTRAP_TUPLE_B64"],
        "present": {key: present[key] for key in sorted(present)},
        "required_absent": list(OUTER_REQUIRED_ABSENT_ENVIRONMENT),
    }


def _bootstrap_tuple(repository_root: Path) -> dict[str, object]:
    launcher = _guard_read_relative(repository_root, "scripts/launch_wyscout_v5.py")
    return {
        "control_prefix_policy": "w04-three-role-runtime-pycache-v1",
        "control_prefix_relative_template": (
            "data/working/wyscout/v5/.staging/control/control_run_id=<uuid>/runtime-pycache/"
        ),
        "encoding_source_rows": [dict(row) for row in OUTER_ENCODING_SOURCE_ROWS],
        "fixed_environment_algorithm": "w04-outer-environment-bootstrap-v2",
        "fixed_environment_digest": _sha256_json(_outer_environment_authority()),
        "launcher_mode": 0o644,
        "launcher_relative_path": "scripts/launch_wyscout_v5.py",
        "launcher_sha256": _sha256(launcher),
        "launcher_size": len(launcher),
        "launcher_source_descriptor_policy": "w04-inherited-source-fd-v1",
        "ordered_argv": list(OUTER_ARGV),
        "process_role": "W04_LOCAL_CONTROL",
        "pyproject_sha256": PYPROJECT_SHA256,
        "python_physical_mode": 0o755,
        "python_physical_sha256": PYTHON_PHYSICAL_SHA256,
        "python_physical_size": 49_968,
        "python_version": "3.12.12",
        "uv_final_entry_kind": "regular_non_symlink_executable",
        "uv_host_spelling_normalization": "w04-uv-host-spelling-normalization-v1",
        "uv_installation_root_role": "<W04_UV_INSTALLATION_ROOT>",
        "uv_link_policy": "w04-uv-logical-one-hop-relative-link-v1",
        "uv_logical_entry_kind": "symlink",
        "uv_logical_launch_role": "<W04_UV_LOGICAL_LAUNCH>",
        "uv_physical_executable_role": "<W04_UV_PHYSICAL_EXECUTABLE>",
        "uv_physical_mode": 0o555,
        "uv_physical_sha256": UV_PHYSICAL_SHA256,
        "uv_physical_size": 41_617_552,
        "uv_raw_target_form": "relative_nonempty_nul_free_posix",
        "uv_raw_target_must_not_be_absolute": True,
        "uv_resolution_containment": "W04_UV_INSTALLATION_ROOT",
        "uv_resolution_hops": 1,
        "uv_version": UV_VERSION,
        "uv_lock_sha256": UV_LOCK_SHA256,
        "working_directory": "<W04_PROJECT_ROOT>",
    }


def _bootstrap_tuple_sha256(repository_root: Path) -> str:
    return _sha256_json(_bootstrap_tuple(repository_root))


def _validate_input(envelope: dict[str, object], source_fd: int, result_fd: int) -> None:
    expected_keys = (
        "base_environment_digest",
        "child_role",
        "entrypoint_relative_path",
        "entrypoint_sha256",
        "entrypoint_size_bytes",
        "expected_repository_code_sha256",
        "inputs",
        "launcher_sha256",
        "nonce",
        "ordered_argv",
        "ordered_argv_sha256",
        "pycache_prefix_absolute",
        "pycache_prefix_relative",
        "result_descriptor_number",
        "schema_version",
        "source_descriptor_number",
    )
    if tuple(envelope) != expected_keys:
        raise AdmissionError("child input common key roster or order differs")
    inputs = envelope.get("inputs")
    if type(inputs) is not dict or tuple(inputs) != (
        "admission_prefix_relative_path",
        "admission_run_id",
        "bootstrap_tuple_sha256",
        "code_manifest_schema_version",
        "pyproject_sha256",
        "repository_code_sha256",
        "selected_dependency_groups",
        "uv_lock_sha256",
    ):
        raise AdmissionError("admission input key roster or order differs")
    admission = cast(dict[str, object], inputs)
    scalar_digests = (
        envelope.get("base_environment_digest"),
        envelope.get("entrypoint_sha256"),
        envelope.get("expected_repository_code_sha256"),
        envelope.get("launcher_sha256"),
        envelope.get("nonce"),
        envelope.get("ordered_argv_sha256"),
        admission.get("bootstrap_tuple_sha256"),
        admission.get("pyproject_sha256"),
        admission.get("repository_code_sha256"),
        admission.get("uv_lock_sha256"),
    )
    if any(
        type(value) is not str or SHA256_RE.fullmatch(value) is None for value in scalar_digests
    ):
        raise AdmissionError("child input contains a malformed digest")
    if (
        envelope["schema_version"] != CHILD_INPUT_SCHEMA_VERSION
        or envelope["child_role"] != "PRE_BUILD_ADMISSION"
        or envelope["entrypoint_relative_path"] != ADMISSION_ARGV[-1]
        or envelope["ordered_argv"] != list(ADMISSION_ARGV)
        or envelope["ordered_argv_sha256"] != _sha256_json(list(ADMISSION_ARGV))
        or envelope["source_descriptor_number"] != source_fd
        or envelope["result_descriptor_number"] != result_fd
        or envelope["nonce"] != os.environ["W04_RESULT_NONCE"]
        or os.environ["W04_CHILD_ROLE"] != "PRE_BUILD_ADMISSION"
        or admission["code_manifest_schema_version"] != MANIFEST_SCHEMA_VERSION
        or admission["bootstrap_tuple_sha256"] != _bootstrap_tuple_sha256(Path.cwd())
        or admission["pyproject_sha256"] != PYPROJECT_SHA256
        or admission["uv_lock_sha256"] != UV_LOCK_SHA256
        or admission["repository_code_sha256"] != envelope["expected_repository_code_sha256"]
        or admission["selected_dependency_groups"]
        != ["data", "e2e", "lint-type", "model", "orchestration", "runtime", "security", "test"]
    ):
        raise AdmissionError("child input exact equality binding differs")
    run_id = admission.get("admission_run_id")
    if type(run_id) is not str or UUID4_RE.fullmatch(run_id) is None:
        raise AdmissionError("admission run ID is not UUIDv4")
    expected_prefix = (
        f"data/working/wyscout/v5/.staging/admission/admission_run_id={run_id}/runtime-pycache"
    )
    if (
        admission["admission_prefix_relative_path"] != expected_prefix
        or envelope["pycache_prefix_relative"] != expected_prefix
    ):
        raise AdmissionError("admission prefix relative path differs")
    prefix = envelope.get("pycache_prefix_absolute")
    if type(prefix) is not str or not prefix.startswith("/"):
        raise AdmissionError("admission prefix absolute path is malformed")
    prefix_metadata = os.stat(prefix, follow_symlinks=False)
    if (
        not stat.S_ISDIR(prefix_metadata.st_mode)
        or stat.S_ISLNK(prefix_metadata.st_mode)
        or stat.S_IMODE(prefix_metadata.st_mode) != 0o700
        or tuple(os.scandir(prefix))
    ):
        raise AdmissionError("admission pycache prefix is unsafe or nonempty")


def _source_observation(envelope: dict[str, object], source_fd: int) -> dict[str, object]:
    if not os.get_inheritable(source_fd):
        raise AdmissionError("entrypoint source descriptor is not inheritable")
    before = os.fstat(source_fd)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o644
        or before.st_nlink != 1
        or not 1 <= before.st_size <= MAX_SOURCE_BYTES
        or os.lseek(source_fd, 0, os.SEEK_CUR) != 0
    ):
        raise AdmissionError("entrypoint source descriptor metadata differs")
    chunks: list[bytes] = []
    offset = 0
    while offset < before.st_size:
        chunk = os.pread(source_fd, min(1024 * 1024, before.st_size - offset), offset)
        if not chunk:
            raise AdmissionError("entrypoint source ended before declared size")
        chunks.append(chunk)
        offset += len(chunk)
    if os.pread(source_fd, 1, before.st_size) != b"":
        raise AdmissionError("entrypoint source lacks exact EOF")
    after = os.fstat(source_fd)
    raw = b"".join(chunks)
    if (
        (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size)
        != (after.st_dev, after.st_ino, after.st_mode, after.st_nlink, after.st_size)
        or os.lseek(source_fd, 0, os.SEEK_CUR) != 0
        or len(raw) != before.st_size
        or _sha256(raw) != envelope["entrypoint_sha256"]
        or len(raw) != envelope["entrypoint_size_bytes"]
    ):
        raise AdmissionError("entrypoint source bytes differ from envelope")
    return {
        "descriptor_cloexec": False,
        "descriptor_inheritable": True,
        "descriptor_number": source_fd,
        "device": before.st_dev,
        "inode": before.st_ino,
        "link_count": 1,
        "mode": 420,
        "offset_after": 0,
        "offset_before": 0,
        "relative_path": ADMISSION_ARGV[-1],
        "role": "PRE_BUILD_ADMISSION",
        "sha256": _sha256(raw),
        "size_bytes": len(raw),
        "source_eof": True,
    }


def _write_all(descriptor: int, payload: bytes) -> None:
    view = memoryview(payload)
    while view:
        written = os.write(descriptor, view)
        if written <= 0:
            raise AdmissionError("result frame write made no progress")
        view = view[written:]


def run_admission() -> None:
    source_fd = _strict_fd("W04_ENTRYPOINT_SOURCE_FD")
    result_fd = _strict_fd("W04_RESULT_FD")
    if source_fd == result_fd or not os.get_inheritable(result_fd):
        raise AdmissionError("source/result descriptors are equal or noninheritable")
    environment = dict(os.environ)
    normalized_environment = normalized_child_environment(environment)
    envelope, _input_raw = _decode_input(environment["W04_CHILD_INPUT_B64"])
    _validate_input(envelope, source_fd, result_fd)
    if envelope["base_environment_digest"] != _sha256_json(normalized_environment):
        raise AdmissionError("child base environment digest differs")
    entrypoint = _source_observation(envelope, source_fd)
    root = Path.cwd().absolute()
    repository_digest, components, counts, pyc_inventory, interpreter_paths = (
        _collect_stable_authority_with_pyc(root)
    )
    final_repository, final_components, final_counts, final_pyc_inventory, final_paths = (
        _collect_stable_authority_with_pyc(root)
    )
    if (final_repository, final_components, final_counts, final_paths) != (
        repository_digest,
        components,
        counts,
        interpreter_paths,
    ) or _pyc_security_projection(final_pyc_inventory) != _pyc_security_projection(pyc_inventory):
        raise AdmissionError("stable authority or portable PYC security projection drifted")
    if normalized_child_environment(dict(os.environ)) != normalized_environment:
        raise AdmissionError("closed child environment drifted across admission")
    if _source_observation(envelope, source_fd) != entrypoint:
        raise AdmissionError("entrypoint descriptor drifted across admission")
    prefix = cast(str, envelope["pycache_prefix_absolute"])
    if tuple(os.scandir(prefix)):
        raise AdmissionError("admission pycache prefix became nonempty")
    inputs = cast(dict[str, object], envelope["inputs"])
    if (
        repository_digest != envelope["expected_repository_code_sha256"]
        or repository_digest != inputs["repository_code_sha256"]
    ):
        raise AdmissionError("repository code authority differs from input")
    environment_digest = _sha256_json(components)
    manifest = {
        **components,
        "environment_digest": environment_digest,
        "repository_code_sha256": repository_digest,
        "schema_version": MANIFEST_SCHEMA_VERSION,
    }
    manifest_bytes = canonical_json_bytes(manifest)
    if not 1 <= len(manifest_bytes) <= MAX_MANIFEST_BYTES:
        raise AdmissionError("stable manifest bytes are outside the size bound")
    proofs = [
        {
            "component_key": key,
            "evidence_row_count": count,
            "value_json_sha256": _sha256_json(components[key]),
        }
        for key, count in zip(COMPONENT_KEYS, counts, strict=True)
    ]
    admission_run_id = cast(str, inputs["admission_run_id"])
    result = {
        "admission_prefix_relative_path": inputs["admission_prefix_relative_path"],
        "admission_run_id": admission_run_id,
        "canonical_manifest_bytes_b64u": base64.urlsafe_b64encode(manifest_bytes)
        .decode("ascii")
        .rstrip("="),
        "canonical_manifest_sha256": _sha256(manifest_bytes),
        "component_proofs": proofs,
        "component_proofs_sha256": _sha256_json(proofs),
        "environment_digest": environment_digest,
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "repository_code_sha256": repository_digest,
    }
    payload = {
        "child_environment_sha256": _sha256_json(environment),
        "child_role": "PRE_BUILD_ADMISSION",
        "entrypoint_source": entrypoint,
        "expected_repository_code_sha256": repository_digest,
        "launcher_sha256": envelope["launcher_sha256"],
        "nonce": envelope["nonce"],
        "ordered_argv_sha256": envelope["ordered_argv_sha256"],
        "payload_kind": "CODE_ENVIRONMENT_MANIFEST",
        "result": result,
        "schema_version": CHILD_RESULT_SCHEMA_VERSION,
    }
    payload_bytes = canonical_json_bytes(payload)
    if load_canonical_json(payload_bytes) != payload:
        raise AdmissionError("result payload does not reproduce canonically")
    _write_all(result_fd, encode_result_frame(payload_bytes))
    os.close(source_fd)
    os.close(result_fd)


def main() -> int:
    run_admission()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"W04 admission rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
