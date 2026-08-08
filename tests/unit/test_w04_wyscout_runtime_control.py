from __future__ import annotations

import base64
import hashlib
import importlib.util
import json
import os
import py_compile
import stat
import subprocess
import sys
import sysconfig
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "launch_wyscout_v5", _PROJECT_ROOT / "scripts/launch_wyscout_v5.py"
)
assert _SPEC is not None and _SPEC.loader is not None
launcher = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = launcher
_SPEC.loader.exec_module(launcher)

_ADMISSION_SPEC = importlib.util.spec_from_file_location(
    "admit_wyscout_v5_runtime", _PROJECT_ROOT / "scripts/admit_wyscout_v5_runtime.py"
)
assert _ADMISSION_SPEC is not None and _ADMISSION_SPEC.loader is not None
admission = importlib.util.module_from_spec(_ADMISSION_SPEC)
sys.modules[_ADMISSION_SPEC.name] = admission
_ADMISSION_SPEC.loader.exec_module(admission)

_R20_LOCAL_RESOURCE_PREFIX = (
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
)
_R21_LOCAL_RESOURCE_SUFFIX = (
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
_R21_LOCAL_RESOURCE_PATHS = (*_R20_LOCAL_RESOURCE_PREFIX, *_R21_LOCAL_RESOURCE_SUFFIX)
_R21_LOCAL_RESOURCE_ALGORITHM = "w04-local-resource-exact-30-v1"
_R21_LOCAL_RESOURCE_DETAIL_SHA256 = (
    "29d8a7cf4c4acab8a52d6008fc5f8975509cc445f5680e45e5974687e65c7bfb"
)


def _directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    return path


def _frame(payload: bytes) -> bytes:
    return bytes(
        launcher.FRAME_MAGIC
        + launcher.FRAME_VERSION.to_bytes(2, "big")
        + len(payload).to_bytes(4, "big")
        + payload
        + hashlib.sha256(payload).digest()
    )


def _runtime_roots(tmp_path: Path) -> Any:
    root = tmp_path.resolve()
    return launcher.RuntimeControlRoots(
        manifest_final_root=_directory(root / "manifest-final"),
        manifest_staging_root=_directory(root / "manifest-staging"),
        pycache_staging_root=_directory(root / "pycache-staging"),
    )


def _wheel_fixture(
    *,
    root: Path,
    cache: Path,
    name: str,
    version: str,
    payload_relative: str,
    installed_relative: str,
    payload: bytes = b"payload",
) -> tuple[dict[str, object], Path, Path]:
    site = _directory(root / ".venv/lib/python3.12/site-packages")
    archive = _directory(cache / "archive-v0")
    extracted = _directory(archive / f"{name}-{version}")
    payload_path = extracted / payload_relative
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_bytes(payload)
    payload_path.chmod(0o644)
    record_relative = f"{name.replace('-', '_')}-{version}.dist-info/RECORD"
    record_path = extracted / record_relative
    record_path.parent.mkdir(parents=True, exist_ok=True)
    digest = base64.urlsafe_b64encode(hashlib.sha256(payload).digest()).decode().rstrip("=")
    record_path.write_text(
        f"{payload_relative},sha256={digest},{len(payload)}\n{record_relative},,\n"
    )
    record_path.chmod(0o644)
    installed = root / ".venv" / installed_relative
    installed.parent.mkdir(parents=True, exist_ok=True)
    installed.write_bytes(payload)
    installed.chmod(0o644)
    key = f"{version}-py3-none-any"
    association = cache / "wheels-v5/pypi" / name / key
    association.parent.mkdir(parents=True, exist_ok=True)
    association.symlink_to(extracted)
    wheel = {
        "declared_tags": ["py3-none-any"],
        "filename": f"{name}-{version}-py3-none-any.whl",
        "lock_hash": "sha256:" + "0" * 64,
        "lock_size": len(payload),
        "name": name,
        "rank": 0,
        "version": version,
    }
    assert site.is_dir()
    return wheel, association, extracted


def test_exact_argv_and_v2_aggregate_bindings_are_frozen() -> None:
    assert launcher.ADMISSION_ARGV == (
        "uv",
        "run",
        "--locked",
        "--no-sync",
        "python",
        "-S",
        "-B",
        "scripts/admit_wyscout_v5_runtime.py",
    )
    assert launcher.REBUILD_ARGV == (
        *launcher.ADMISSION_ARGV[:-1],
        "scripts/rebuild_wyscout_v5.py",
    )
    assert launcher.SCHEMA_BUNDLE_V2_LOGICAL_SHA256 == (
        "956f5c3cedd9c9e2b36417ad87d8a9f2f97bc54b2720a6835a3cbcde668ff6e5"
    )
    assert launcher.PRODUCT_CONTRACT_V2_LOGICAL_SHA256 == (
        "fa2b28166df02663120f8cf9ca1751c0c32ff75a98b6255baf181bc179088f76"
    )
    assert len(launcher.COMPONENT_KEYS) == 20
    assert tuple(sorted(launcher.COMPONENT_KEYS)) == launcher.COMPONENT_KEYS


def _launcher_resource_rows(paths: tuple[str, ...]) -> tuple[dict[str, object], ...]:
    return tuple(
        launcher._authority_file_row(
            _PROJECT_ROOT,
            resource_path,
            mode=0o600 if index == 16 else 0o644,
        )
        for index, resource_path in enumerate(paths)
    )


def _resource_detail(algorithm: str, rows: tuple[dict[str, object], ...]) -> dict[str, object]:
    return {"algorithm": algorithm, "rows": rows}


def test_r21_runtime_resources_are_the_exact_ordered_thirty_and_digest_identically() -> None:
    assert len(_R20_LOCAL_RESOURCE_PREFIX) == 17
    assert len(_R21_LOCAL_RESOURCE_SUFFIX) == 13
    assert len(_R21_LOCAL_RESOURCE_PATHS) == len(set(_R21_LOCAL_RESOURCE_PATHS)) == 30
    assert admission.LOCAL_RESOURCE_PATHS == _R21_LOCAL_RESOURCE_PATHS
    assert launcher._LOCAL_RESOURCE_PATHS == _R21_LOCAL_RESOURCE_PATHS
    assert admission.LOCAL_RESOURCE_PATHS[:17] == _R20_LOCAL_RESOURCE_PREFIX
    assert admission.LOCAL_RESOURCE_PATHS[17:] == _R21_LOCAL_RESOURCE_SUFFIX
    assert admission.LOCAL_RESOURCE_DIGEST_ALGORITHM == _R21_LOCAL_RESOURCE_ALGORITHM
    assert launcher._LOCAL_RESOURCE_DIGEST_ALGORITHM == _R21_LOCAL_RESOURCE_ALGORITHM

    admission_rows = admission._local_resource_rows(_PROJECT_ROOT)
    launcher_rows = _launcher_resource_rows(launcher._LOCAL_RESOURCE_PATHS)
    assert admission_rows == launcher_rows
    assert tuple(row["path"] for row in admission_rows) == _R21_LOCAL_RESOURCE_PATHS
    assert tuple(row["mode"] for row in admission_rows) == (
        *(0o644 for _ in range(16)),
        0o600,
        *(0o644 for _ in range(13)),
    )
    child_detail = _resource_detail(admission.LOCAL_RESOURCE_DIGEST_ALGORITHM, admission_rows)
    launcher_detail = _resource_detail(launcher._LOCAL_RESOURCE_DIGEST_ALGORITHM, launcher_rows)
    assert child_detail == launcher_detail
    assert admission._sha256_json(child_detail) == launcher._sha256_json(launcher_detail)
    assert admission._sha256_json(child_detail) == _R21_LOCAL_RESOURCE_DETAIL_SHA256


@pytest.mark.parametrize(
    "mutation",
    (
        "omission",
        "insertion",
        "duplicate",
        "reorder",
        "v1-v2-substitution",
        "v2-v1-substitution",
        "algorithm-v1",
        "algorithm-drift",
        "row-content",
    ),
)
def test_r21_runtime_resource_mutations_break_independent_digest_equality(
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    launcher_rows = _launcher_resource_rows(launcher._LOCAL_RESOURCE_PATHS)
    accepted = _resource_detail(launcher._LOCAL_RESOURCE_DIGEST_ALGORITHM, launcher_rows)
    paths = list(admission.LOCAL_RESOURCE_PATHS)
    algorithm = admission.LOCAL_RESOURCE_DIGEST_ALGORITHM
    if mutation == "omission":
        paths.pop()
    elif mutation == "insertion":
        paths.insert(17, "AGENTS.md")
    elif mutation == "duplicate":
        paths[-1] = paths[-2]
    elif mutation == "reorder":
        paths[17], paths[18] = paths[18], paths[17]
    elif mutation == "v1-v2-substitution":
        paths[1] = _R21_LOCAL_RESOURCE_SUFFIX[5]
    elif mutation == "v2-v1-substitution":
        paths[22] = _R20_LOCAL_RESOURCE_PREFIX[1]
    elif mutation == "algorithm-v1":
        algorithm = "w04-local-resource-exact-17-v1"
    elif mutation == "algorithm-drift":
        algorithm = "w04-local-resource-exact-30-v2"

    if mutation == "row-content":
        rows = [dict(row) for row in admission._local_resource_rows(_PROJECT_ROOT)]
        rows[17]["sha256"] = "0" * 64
        attacked = _resource_detail(algorithm, tuple(rows))
    else:
        monkeypatch.setattr(admission, "LOCAL_RESOURCE_PATHS", tuple(paths))
        attacked = _resource_detail(algorithm, admission._local_resource_rows(_PROJECT_ROOT))

    assert attacked != accepted
    assert admission._sha256_json(attacked) != launcher._sha256_json(accepted)
    launcher_source = (_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_text()
    assert "contracts.validate_admission_component_authority(" in launcher_source


def test_result_frame_decodes_exactly_once() -> None:
    payload = b'{"schema_version":"test"}'
    assert launcher.decode_result_frame(_frame(payload)) == payload


@pytest.mark.parametrize(
    ("mutation", "match"),
    [
        (lambda value: b"BADMAGIC" + value[8:], "magic"),
        (lambda value: value[:8] + b"\x00\x02" + value[10:], "version"),
        (lambda value: value[:10] + (0).to_bytes(4, "big") + value[14:], "length"),
        (lambda value: value[:-1], "truncation|truncated"),
        (lambda value: value + b"x", "trailing"),
        (lambda value: value[:-32] + bytes(32), "digest"),
    ],
)
def test_result_frame_rejects_header_digest_eof_attacks(mutation: object, match: str) -> None:
    payload = b'{"schema_version":"test"}'
    changed = mutation(_frame(payload))  # type: ignore[operator]
    with pytest.raises(launcher.ResultFrameError, match=match):
        launcher.decode_result_frame(changed)


@pytest.mark.parametrize(
    "payload",
    [
        b'{"a":1,"a":1}',
        b'{"a": 1}',
        b'{"a":1}\n',
        b"[]",
    ],
)
def test_result_frame_rejects_noncanonical_or_nonobject_payload(payload: bytes) -> None:
    with pytest.raises(launcher.ResultFrameError, match="canonical|object"):
        launcher.decode_result_frame(_frame(payload))


def test_v2_aggregate_guard_accepts_only_logical_no_lf_identities() -> None:
    project_root = Path(__file__).resolve().parents[2]
    assert launcher._guard_v2_aggregates(project_root) == (
        launcher.SCHEMA_BUNDLE_V2_LOGICAL_SHA256,
        launcher.PRODUCT_CONTRACT_V2_LOGICAL_SHA256,
    )


@pytest.mark.parametrize("terminal", [b"", b"\n\n", b" "])
def test_v2_aggregate_guard_rejects_terminal_byte_drift(tmp_path: Path, terminal: bytes) -> None:
    source_root = Path(__file__).resolve().parents[2]
    config_root = _directory(tmp_path / "configs")
    schema_root = _directory(config_root / "schema")
    for relative in (
        launcher.SCHEMA_BUNDLE_RELATIVE_PATH,
        launcher.PRODUCT_CONTRACT_RELATIVE_PATH,
    ):
        source = source_root / relative
        body = source.read_bytes()[:-1]
        target = schema_root / source.name
        target.write_bytes(body + terminal)
        target.chmod(0o644)
    with pytest.raises(launcher.RuntimeControlError, match="terminal LF|logical v2"):
        launcher._guard_v2_aggregates(tmp_path)


def test_guard_read_rejects_symlink_hardlink_and_unsafe_mode(tmp_path: Path) -> None:
    regular = tmp_path / "regular"
    regular.write_bytes(b"authority")
    regular.chmod(0o644)
    symlink = tmp_path / "symlink"
    symlink.symlink_to(regular)
    hardlink = tmp_path / "hardlink"
    os.link(regular, hardlink)
    unsafe = tmp_path / "unsafe"
    unsafe.write_bytes(b"authority")
    unsafe.chmod(0o600)
    for relative in ("symlink", "hardlink", "unsafe"):
        with pytest.raises(launcher.RuntimeControlError, match="kind, mode, link count"):
            launcher._guard_read_relative(tmp_path, relative)


def test_guard_read_rejects_unsafe_paths_before_open(tmp_path: Path) -> None:
    for relative in ("../escape", "/absolute", "a//b", "a/./b", "a\\b", "trailing/"):
        with pytest.raises(launcher.RuntimeControlError, match="unsafe"):
            launcher._guard_read_relative(tmp_path, relative)


def test_prefix_creation_retains_stable_parent_and_rejects_reuse(tmp_path: Path) -> None:
    root = _directory(tmp_path / "pycache")
    first_id = str(uuid4())
    second_id = str(uuid4())
    first = launcher._create_empty_prefix(root, "PRE_BUILD_ADMISSION", first_id, None)
    second = launcher._create_empty_prefix(root, "PRE_BUILD_ADMISSION", second_id, None)
    assert tuple(first.iterdir()) == ()
    assert tuple(second.iterdir()) == ()
    assert first != second
    assert stat.S_IMODE(first.stat().st_mode) == 0o700
    with pytest.raises(launcher.RuntimeControlError, match="already exists"):
        launcher._create_empty_prefix(root, "PRE_BUILD_ADMISSION", first_id, None)


def test_rebuild_prefix_is_unavailable_without_completed_build_id(tmp_path: Path) -> None:
    root = _directory(tmp_path / "pycache")
    with pytest.raises(launcher.RuntimeControlError, match="completed build ID"):
        launcher._create_empty_prefix(root, "POST_BUILD_ID_REBUILD", str(uuid4()), None)
    assert tuple(root.iterdir()) == ()


def test_child_input_encoding_is_canonical_unpadded_and_bounded() -> None:
    value = {"z": 1, "a": [True, False]}
    encoded = launcher._encoded_child_input(value)
    assert "=" not in encoded
    padding = "=" * (-len(encoded) % 4)
    decoded = __import__("base64").urlsafe_b64decode((encoded + padding).encode())
    assert decoded == b'{"a":[true,false],"z":1}'
    assert json.loads(decoded) == value


def test_run_ids_are_strict_uuidv4() -> None:
    accepted = str(uuid4())
    assert launcher._safe_uuid4(accepted, label="run") == accepted
    for value in (accepted.upper(), "00000000-0000-5000-8000-000000000000", "x"):
        with pytest.raises(launcher.RuntimeControlError, match="UUIDv4"):
            launcher._safe_uuid4(value, label="run")


def test_admission_authority_reconstructs_exact_twenty_positive_proofs() -> None:
    repository_digest, components, counts = launcher._admission_authority(_PROJECT_ROOT)
    assert len(repository_digest) == 64
    assert tuple(components) == launcher.COMPONENT_KEYS
    assert len(counts) == 20
    assert all(type(count) is int and count > 0 for count in counts)
    assert counts[3] == 35
    assert counts[8] == 30
    assert components["uv_version"] == "uv 0.9.21 (Homebrew 2025-12-30)"
    assert components["uv_physical_sha256"] == (
        "4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f"
    )
    assert (
        "_validate_runtime_subset"
        not in admission._collect_stable_authority_with_pyc.__code__.co_names
    )
    assert "freeze_runtime_subset_authority" not in (
        admission._collect_stable_authority_with_pyc.__code__.co_names
    )


def test_selected_wheel_cache_rejects_two_symlink_hops(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, cache = tmp_path / "project", tmp_path / "cache"
    wheel, association, extracted = _wheel_fixture(
        root=root,
        cache=cache,
        name="demo",
        version="1.0",
        payload_relative="demo.py",
        installed_relative="lib/python3.12/site-packages/demo.py",
    )
    association.unlink()
    intermediate = cache / "archive-v0/intermediate"
    intermediate.symlink_to(extracted)
    association.symlink_to(intermediate)
    monkeypatch.setenv("UV_CACHE_DIR", os.fspath(cache))
    with pytest.raises(launcher.RuntimeControlError, match="extraction escapes archive"):
        launcher._independent_extracted_rows(root, (wheel,))


def test_pep427_data_payload_is_mapped_and_byte_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, cache = tmp_path / "project", tmp_path / "cache"
    wheel, _association, _extracted = _wheel_fixture(
        root=root,
        cache=cache,
        name="demo",
        version="1.0",
        payload_relative="demo-1.0.data/data/share/demo.txt",
        installed_relative="share/demo.txt",
    )
    monkeypatch.setenv("UV_CACHE_DIR", os.fspath(cache))
    assert len(launcher._independent_extracted_rows(root, (wheel,))) == 1
    installed = root / ".venv/share/demo.txt"
    installed.write_bytes(b"changed")
    with pytest.raises(launcher.RuntimeControlError, match="mapping differs"):
        launcher._independent_extracted_rows(root, (wheel,))


def test_pep427_mapping_collision_is_rejected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, cache = tmp_path / "project", tmp_path / "cache"
    first, _association, _extracted = _wheel_fixture(
        root=root,
        cache=cache,
        name="alpha",
        version="1.0",
        payload_relative="alpha-1.0.data/data/share/collision.txt",
        installed_relative="share/collision.txt",
    )
    second, _association, _extracted = _wheel_fixture(
        root=root,
        cache=cache,
        name="beta",
        version="1.0",
        payload_relative="beta-1.0.data/data/share/collision.txt",
        installed_relative="share/collision.txt",
    )
    monkeypatch.setenv("UV_CACHE_DIR", os.fspath(cache))
    with pytest.raises(launcher.RuntimeControlError, match="collides or overwrites"):
        launcher._independent_extracted_rows(root, (first, second))


def _installed_package(
    owner: str, relative: str, *, digest: str = "a" * 64
) -> tuple[dict[str, object], ...]:
    return (
        {
            "name": owner,
            "record_rows": [
                {
                    "mode": 0o644,
                    "path": relative,
                    "sha256": digest,
                    "size_bytes": 7,
                }
            ],
            "version": "1.0",
        },
    )


@pytest.mark.parametrize(
    ("owner", "relative", "destination", "scheme"),
    [
        ("bandit", "../../../share/man/man1/bandit.1", "share/man/man1/bandit.1", "data"),
        (
            "greenlet",
            "../../../include/site/python3.12/greenlet/greenlet.h",
            "include/site/python3.12/greenlet/greenlet.h",
            "headers",
        ),
    ],
)
@pytest.mark.parametrize(
    ("validator", "error_type"),
    [
        (launcher._independent_validate_installed_mapping, launcher.RuntimeControlError),
        (admission._validate_installed_mapping, admission.AdmissionError),
    ],
)
def test_exact_external_record_destinations_require_owner_specific_mapping(
    tmp_path: Path,
    owner: str,
    relative: str,
    destination: str,
    scheme: str,
    validator: object,
    error_type: type[Exception],
) -> None:
    digest = "a" * 64
    mapping = {
        destination: {
            "mode": 0o644,
            "owner": owner,
            "record_path": f"{owner}-1.0.data/{scheme}/{Path(destination).name}",
            "scheme": scheme,
            "sha256": digest,
            "size_bytes": 7,
        }
    }
    validator(tmp_path, _installed_package(owner, relative, digest=digest), mapping)  # type: ignore[operator]
    with pytest.raises(error_type, match="mapping"):
        validator(tmp_path, _installed_package(owner, relative, digest=digest), {})  # type: ignore[operator]
    swapped = {destination: {**mapping[destination], "owner": "substituted-owner"}}
    with pytest.raises(error_type, match="owner|mapping"):
        validator(tmp_path, _installed_package(owner, relative, digest=digest), swapped)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("validator", "error_type"),
    [
        (launcher._independent_validate_installed_mapping, launcher.RuntimeControlError),
        (admission._validate_installed_mapping, admission.AdmissionError),
    ],
)
def test_external_record_mapping_rejects_collision_and_escape(
    tmp_path: Path, validator: object, error_type: type[Exception]
) -> None:
    collision = (
        *_installed_package("alpha", "../../../share/collision.txt"),
        *_installed_package("beta", "../../../share/collision.txt"),
    )
    first_mapping = {
        "share/collision.txt": {
            "mode": 0o644,
            "owner": "alpha",
            "record_path": "alpha-1.0.data/data/share/collision.txt",
            "scheme": "data",
            "sha256": "a" * 64,
            "size_bytes": 7,
        }
    }
    with pytest.raises(error_type, match="collide"):
        validator(tmp_path, collision, first_mapping)  # type: ignore[operator]
    with pytest.raises(error_type, match="escape"):
        validator(
            tmp_path,
            _installed_package("alpha", "../../../../outside.txt"),
            {},
        )  # type: ignore[operator]


def test_interpreter_alias_census_rejects_a_fourth_alias(tmp_path: Path) -> None:
    bin_root = _directory(tmp_path / ".venv/bin")
    physical = Path(cast(str, getattr(sys, "_base_executable")))
    (bin_root / "python").symlink_to(physical)
    (bin_root / "python3").symlink_to("python")
    (bin_root / "python3.12").symlink_to("python")
    (bin_root / "python4").symlink_to("python")
    with pytest.raises(launcher.RuntimeControlError, match="three-alias census"):
        launcher._independent_interpreter(tmp_path)


def _retained_site_inputs() -> tuple[
    tuple[dict[str, object], ...],
    tuple[dict[str, object], ...],
    dict[str, object],
]:
    closure = launcher._independent_lock_rows(_PROJECT_ROOT)
    installed = launcher._independent_installed_rows(_PROJECT_ROOT, closure)
    repository = launcher._independent_repository_rows(_PROJECT_ROOT)
    lock_inputs = {
        "pyproject_sha256": launcher.PYPROJECT_SHA256,
        "uv_lock_sha256": launcher.UV_LOCK_SHA256,
    }
    return installed, repository, lock_inputs


def test_bootstrap_byte_mutation_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    installed, repository, lock_inputs = _retained_site_inputs()
    original = launcher._absolute_regular

    def changed(path: Path, *, mode: int | None = None) -> bytes:
        raw = cast(bytes, original(path, mode=mode))
        return raw[:-1] + bytes([raw[-1] ^ 1]) if path.name == "_virtualenv.py" else raw

    monkeypatch.setattr(launcher, "_absolute_regular", changed)
    with pytest.raises(launcher.RuntimeControlError, match="bootstrap/coverage bytes"):
        launcher._independent_site_editable_authority(
            _PROJECT_ROOT, installed, repository, lock_inputs
        )


def test_site_pth_census_rejects_a_fourth_file(monkeypatch: pytest.MonkeyPatch) -> None:
    installed, repository, lock_inputs = _retained_site_inputs()
    site = _PROJECT_ROOT / ".venv/lib/python3.12/site-packages"
    original = launcher.os.scandir
    injected = False

    def changed(path: str | os.PathLike[str]) -> object:
        nonlocal injected
        rows = tuple(original(path))
        if Path(path) == site and not injected:
            injected = True
            return iter((*rows, SimpleNamespace(name="fourth.pth")))
        return iter(rows)

    monkeypatch.setattr(launcher.os, "scandir", changed)
    with pytest.raises(launcher.RuntimeControlError, match="three-PTH census"):
        launcher._independent_site_editable_authority(
            _PROJECT_ROOT, installed, repository, lock_inputs
        )


@pytest.mark.parametrize("target_name", ["METADATA", "direct_url.json", "uv_cache.json"])
def test_editable_metadata_relation_drift_is_rejected(
    target_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    installed, repository, lock_inputs = _retained_site_inputs()
    original = launcher._absolute_regular

    def changed(path: Path, *, mode: int | None = None) -> bytes:
        raw = cast(bytes, original(path, mode=mode))
        if path.name == target_name:
            return raw[:-1] + bytes([raw[-1] ^ 1])
        return raw

    monkeypatch.setattr(launcher, "_absolute_regular", changed)
    with pytest.raises(launcher.RuntimeControlError, match="editable RECORD target"):
        launcher._independent_site_editable_authority(
            _PROJECT_ROOT, installed, repository, lock_inputs
        )


def test_global_site_ownership_rejects_unowned_payload() -> None:
    with pytest.raises(launcher.RuntimeControlError, match="unowned=.*rogue"):
        launcher._independent_require_global_site_ownership(
            {"_virtualenv.pth", "_virtualenv.py", "owned.py", "rogue.py"},
            {"owned.py": "demo==1.0"},
        )


def test_runtime_subset_rejects_unselected_site_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    origin = site / "rogue.py"
    origin.parent.mkdir(parents=True)
    origin.write_text("VALUE = 1\n")
    fake = ModuleType("w04_test_rogue")
    fake.__spec__ = SimpleNamespace(origin=os.fspath(origin), submodule_search_locations=None)  # type: ignore[assignment]
    authority = _synthetic_runtime_authority(
        tmp_path,
        (("selected", "1.0", "selected.py", b"VALUE = 2\n"),),
    )
    monkeypatch.setattr(admission.sys, "modules", {fake.__name__: fake})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="not singularly selected"):
        authority.observe()


def _synthetic_runtime_authority(
    tmp_path: Path,
    owned: tuple[tuple[str, str, str, bytes], ...],
    *,
    repository_rows: tuple[dict[str, object], ...] = (),
    darwin_image_paths: tuple[Path, ...] = (),
) -> Any:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site.mkdir(parents=True, exist_ok=True)
    packages: dict[tuple[str, str], list[dict[str, object]]] = {}
    for owner, version, relative, raw in owned:
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        target.chmod(0o644)
        packages.setdefault((owner, version), []).append(
            {
                "mode": 0o644,
                "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size_bytes": len(raw),
            }
        )
    record_rows = tuple(
        {"name": owner, "record_rows": rows, "version": version}
        for (owner, version), rows in packages.items()
    )
    return admission.freeze_runtime_subset_authority(
        tmp_path,
        record_rows,
        repository_rows=repository_rows,
        stdlib_rows=_resident_frozen_stdlib_rows(),
        darwin_image_paths=darwin_image_paths,
    )


def _resident_frozen_stdlib_rows() -> tuple[dict[str, object], ...]:
    stdlib_root = Path(os.__file__).resolve().parent
    resident_stdlib_paths = {
        Path(module_file)
        for module in tuple(sys.modules.values())
        if getattr(getattr(module, "__spec__", None), "origin", None) == "frozen"
        and type(module_file := getattr(module, "__file__", None)) is str
        and Path(module_file).is_relative_to(stdlib_root)
    }
    stdlib_rows = tuple(
        {
            "mode": stat.S_IMODE(path.stat().st_mode),
            "path": path.relative_to(stdlib_root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(resident_stdlib_paths)
    )
    return stdlib_rows


def _runtime_module(name: str, origin: str | None, locations: object = None) -> ModuleType:
    module = ModuleType(name)
    module.__spec__ = SimpleNamespace(  # type: ignore[assignment]
        origin=origin, submodule_search_locations=locations
    )
    return module


def test_runtime_subset_positive_source_digest_and_one_shot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(
        tmp_path, (("demo", "1.0", "demo.py", b"VALUE = 1\n"),)
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    module = _runtime_module("demo", os.fspath(site / "demo.py"))
    monkeypatch.setattr(admission.sys, "modules", {"demo": module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    rows, digest = authority.observe()
    assert rows == (
        {
            "observation_kind": "MODULE_SOURCE",
            "owner_name": "demo",
            "owner_version": "1.0",
            "site_relative_path": "demo.py",
            "subject_name": "demo",
        },
    )
    assert digest == admission._sha256_json(
        {"algorithm": admission.RUNTIME_SUBSET_ALGORITHM, "rows": rows}
    )
    with pytest.raises(admission.AdmissionError, match="already observed"):
        authority.observe()


@pytest.mark.parametrize("attack", ("lock-only", "installed-only"))
def test_runtime_subset_rejects_selected_without_record_and_installed_outside_l(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site.mkdir(parents=True)

    def installed_row(name: str, raw: bytes) -> dict[str, object]:
        target = site / f"{name}.py"
        target.write_bytes(raw)
        target.chmod(0o644)
        return {
            "mode": 0o644,
            "path": f"{name}.py",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
        }

    alpha_row = installed_row("alpha", b"alpha")
    attacked_row = installed_row(attack.replace("-", "_"), b"attacked")
    record_rows = (
        {"name": "alpha", "record_rows": [alpha_row], "version": "1.0"},
        *(
            (
                {
                    "name": "installed-only",
                    "record_rows": [attacked_row],
                    "version": "9.0",
                },
            )
            if attack == "installed-only"
            else ()
        ),
    )
    selected = (
        {"name": "alpha", "version": "1.0"},
        *(({"name": "lock-only", "version": "8.0"},) if attack == "lock-only" else ()),
    )
    authority = admission.freeze_runtime_subset_authority(
        tmp_path,
        record_rows,
        selected,
        repository_rows=(),
        stdlib_rows=_resident_frozen_stdlib_rows(),
        darwin_image_paths=(),
    )
    subject = attack.replace("-", "_")
    attacked_module = _runtime_module(subject, os.fspath(site / f"{subject}.py"))
    monkeypatch.setattr(admission.sys, "modules", {subject: attacked_module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="not singularly selected"):
        authority.observe()


@pytest.mark.parametrize("attack", ("spec-none-site", "external", "repo-root", "stdlib-site"))
def test_runtime_subset_rejects_spec_none_and_unadmitted_absolute_origins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    authority = _synthetic_runtime_authority(
        tmp_path, (("demo", "1.0", "demo.py", b"VALUE = 1\n"),)
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    if attack == "spec-none-site":
        module = ModuleType("demo")
        module.__file__ = os.fspath(site / "demo.py")
    else:
        if attack == "external":
            origin = tmp_path / "outside.py"
        elif attack == "repo-root":
            origin = tmp_path / "unmanifested.py"
        else:
            origin = Path(os.__file__).resolve().parent / "site-packages/rogue.py"
        module = _runtime_module("rogue", os.fspath(origin))
    monkeypatch.setattr(admission.sys, "modules", {module.__name__: module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="spec|external"):
        authority.observe()


def test_runtime_subset_rejects_originless_no_file_and_empty_namespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    location_cases: tuple[object, ...] = (None, [])
    for locations in location_cases:
        with monkeypatch.context() as context:
            authority = _synthetic_runtime_authority(
                tmp_path / ("none" if locations is None else "empty"),
                (("demo", "1.0", "demo.py", b"demo"),),
            )
            module = _runtime_module("originless", None, locations)
            context.setattr(admission.sys, "modules", {module.__name__: module})
            context.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
            with pytest.raises(admission.AdmissionError, match="originless|empty"):
                authority.observe()


@pytest.mark.parametrize("kind", ("built-in", "frozen"))
def test_runtime_subset_rejects_forged_builtin_and_frozen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kind: str
) -> None:
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", "demo.py", b"demo"),))
    forged = ModuleType("forged")
    forged.__spec__ = SimpleNamespace(  # type: ignore[assignment]
        name="forged", origin=kind, loader=None, submodule_search_locations=None
    )
    monkeypatch.setattr(admission.sys, "modules", {"forged": forged})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="built-in|frozen"):
        authority.observe()


def test_runtime_subset_accepts_exact_builtin_and_frozen_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", "demo.py", b"demo"),))
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    demo = _runtime_module("demo", os.fspath(site / "demo.py"))
    monkeypatch.setattr(admission.sys, "modules", {"demo": demo, "os": os, "sys": sys})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    rows, _digest = authority.observe()
    assert len(rows) == 1


def test_runtime_subset_accepts_exact_three_resident_frozen_aliases(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    alias_names = (
        "_frozen_importlib",
        "_frozen_importlib_external",
        "importlib._bootstrap",
        "importlib._bootstrap_external",
        "os.path",
        "posixpath",
    )
    aliases = {name: sys.modules[name] for name in alias_names}
    assert aliases["importlib._bootstrap"] is aliases["_frozen_importlib"]
    assert aliases["importlib._bootstrap_external"] is aliases["_frozen_importlib_external"]
    assert aliases["os.path"] is aliases["posixpath"]
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", "demo.py", b"demo"),))
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    aliases["demo"] = _runtime_module("demo", os.fspath(site / "demo.py"))
    monkeypatch.setattr(admission.sys, "modules", aliases)
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    rows, _digest = authority.observe()
    assert len(rows) == 1


@pytest.mark.parametrize(
    "attack",
    (
        "forged-time",
        "forged-abc",
        "missing-frozen-file",
        "wrong-frozen-file",
        "origin-object",
        "extra-alias",
        "split-alias",
    ),
)
def test_runtime_subset_rejects_prefreeze_forged_resident_builtin_frozen_claimants(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    attacked_modules = dict(sys.modules)
    if attack in {"forged-time", "forged-abc"}:
        name = "time" if attack == "forged-time" else "abc"
        origin = "built-in" if name == "time" else "frozen"
        forged = ModuleType(name)
        forged.__spec__ = SimpleNamespace(  # type: ignore[assignment]
            cached=None,
            has_location=False,
            loader=None,
            name=name,
            origin=origin,
            parent="",
            submodule_search_locations=None,
        )
        forged.__loader__ = None
        forged.__package__ = ""
        attacked_modules[name] = forged
    elif attack in {"missing-frozen-file", "wrong-frozen-file"}:
        original = attacked_modules["abc"]
        forged = ModuleType("abc")
        forged.__spec__ = original.__spec__
        forged.__loader__ = original.__loader__
        forged.__package__ = original.__package__
        setattr(forged, "__cached__", getattr(original, "__cached__", None))
        if attack == "wrong-frozen-file":
            forged.__file__ = os.fspath(Path(os.__file__).resolve())
        attacked_modules["abc"] = forged
    elif attack == "origin-object":

        class OriginObject:
            def __hash__(self) -> int:
                return hash("built-in")

            def __eq__(self, other: object) -> bool:
                return other == "built-in"

        forged = ModuleType("origin_object")
        forged.__spec__ = SimpleNamespace(origin=OriginObject())  # type: ignore[assignment]
        attacked_modules["origin_object"] = forged
    elif attack == "extra-alias":
        attacked_modules["w04_time_alias"] = attacked_modules["time"]
    else:
        split = ModuleType("posixpath")
        original = attacked_modules["posixpath"]
        split.__dict__.update(original.__dict__)
        attacked_modules["os.path"] = split
    with monkeypatch.context() as context:
        context.setattr(admission.sys, "modules", attacked_modules)
        with pytest.raises(admission.AdmissionError, match="built-in/frozen|alias|origin|file"):
            _synthetic_runtime_authority(
                tmp_path / attack,
                (("demo", "1.0", "demo.py", b"demo"),),
            )


def test_runtime_subset_rejects_symlinked_site_parent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(
        tmp_path, (("demo", "1.0", "demo/module.py", b"VALUE = 1\n"),)
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    original = site / "demo"
    displaced = site / "displaced"
    original.rename(displaced)
    original.symlink_to(displaced, target_is_directory=True)
    module = _runtime_module("demo.module", os.fspath(original / "module.py"))
    monkeypatch.setattr(admission.sys, "modules", {module.__name__: module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="unsafe site parent"):
        authority.observe()


@pytest.mark.parametrize(
    "attack",
    ("owned-init", "unowned", "wrong-subject", "unsafe-symlink", "repo-root", "stdlib-root"),
)
def test_runtime_subset_rejects_invalid_namespace_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    owned: tuple[tuple[str, str, str, bytes], ...] = (
        ("demo", "1.0", "demo/child.py", b"VALUE = 1\n"),
    )
    if attack == "owned-init":
        owned += (("demo", "1.0", "demo/__init__.py", b""),)
    authority = _synthetic_runtime_authority(tmp_path, owned)
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    if attack == "unowned":
        location = site / "unowned"
        location.mkdir()
        subject = "unowned"
    elif attack == "repo-root":
        location, subject = tmp_path, "repository"
    elif attack == "stdlib-root":
        location, subject = Path(os.__file__).resolve().parent, "stdlib"
    else:
        location = site / "demo"
        subject = "wrong" if attack == "wrong-subject" else "demo"
        if attack == "unsafe-symlink":
            displaced = site / "displaced-demo"
            location.rename(displaced)
            location.symlink_to(displaced, target_is_directory=True)
    module = _runtime_module(subject, None, [os.fspath(location)])
    monkeypatch.setattr(admission.sys, "modules", {subject: module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(
        admission.AdmissionError, match="namespace|ordinary package|external|unsafe site parent"
    ):
        authority.observe()


def test_runtime_subset_accepts_exact_non_site_namespace_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository_file = tmp_path / "src/scouting/data_products/demo.py"
    repository_file.parent.mkdir(parents=True)
    repository_file.write_bytes(b"VALUE = 1\n")
    repository_file.chmod(0o644)
    repository_rows = (
        {
            "mode": 0o644,
            "path": "src/scouting/data_products/demo.py",
            "sha256": hashlib.sha256(repository_file.read_bytes()).hexdigest(),
            "size_bytes": repository_file.stat().st_size,
        },
    )
    authority = _synthetic_runtime_authority(
        tmp_path,
        (("demo", "1.0", "demo.py", b"VALUE = 2\n"),),
        repository_rows=repository_rows,
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    namespace = _runtime_module("scouting.data_products", None, [os.fspath(repository_file.parent)])
    demo = _runtime_module("demo", os.fspath(site / "demo.py"))
    monkeypatch.setattr(
        admission.sys,
        "modules",
        {"demo": demo, "scouting.data_products": namespace},
    )
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    rows, _digest = authority.observe()
    assert len(rows) == 1


def test_runtime_subset_canonicalizes_namespace_location_iterable_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", "demo/child.py", b"demo"),))
    location = tmp_path / ".venv/lib/python3.12/site-packages/demo"
    iterations = 0

    def locations() -> object:
        nonlocal iterations
        iterations += 1
        if iterations > 1:
            raise AssertionError("namespace location iterable was rescanned")
        yield os.fspath(location)

    namespace = _runtime_module("demo", None, locations())
    monkeypatch.setattr(admission.sys, "modules", {"demo": namespace})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    rows, _digest = authority.observe()
    assert rows[0]["observation_kind"] == "NAMESPACE_LOCATION"
    assert iterations == 1


def test_runtime_subset_rejects_admitted_repo_file_parent_replacement(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repository_file = tmp_path / "src/scouting/data_products/demo.py"
    repository_file.parent.mkdir(parents=True)
    repository_file.write_bytes(b"VALUE = 1\n")
    repository_file.chmod(0o644)
    row = {
        "mode": 0o644,
        "path": "src/scouting/data_products/demo.py",
        "sha256": hashlib.sha256(repository_file.read_bytes()).hexdigest(),
        "size_bytes": repository_file.stat().st_size,
    }
    authority = _synthetic_runtime_authority(
        tmp_path,
        (("demo", "1.0", "demo.py", b"VALUE = 2\n"),),
        repository_rows=(row,),
    )
    parent = repository_file.parent
    displaced = parent.parent / "displaced-data-products"
    parent.rename(displaced)
    parent.symlink_to(displaced, target_is_directory=True)
    module = _runtime_module("scouting.data_products.demo", os.fspath(repository_file))
    monkeypatch.setattr(admission.sys, "modules", {module.__name__: module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="unsafe parent"):
        authority.observe()


@pytest.mark.parametrize("attack", ("unowned", "mutated", "source-relabel", "relative", "external"))
def test_runtime_subset_rejects_shared_image_attacks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, attack: str
) -> None:
    relative = "libdemo.py" if attack == "source-relabel" else "libdemo.dylib"
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", relative, b"binary"),))
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    image = site / relative
    if attack == "unowned":
        image = site / "rogue.dylib"
        image.write_bytes(b"rogue")
    elif attack == "mutated":
        image.write_bytes(b"changed")
    if attack == "relative":
        images = (Path("relative.dylib"),)
    elif attack == "external":
        images = (Path("/tmp/evil.dylib"),)
    else:
        images = (image,)
    monkeypatch.setattr(admission.sys, "modules", {})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: images)
    with pytest.raises(
        admission.AdmissionError, match="image|absolute|selected|bytes|frozen authority"
    ):
        authority.observe()


def test_runtime_subset_accepts_record_owned_shared_image(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(
        tmp_path, (("demo", "1.0", "libdemo.dylib", b"binary"),)
    )
    image = tmp_path / ".venv/lib/python3.12/site-packages/libdemo.dylib"
    monkeypatch.setattr(admission.sys, "modules", {})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: (image,))
    rows, _digest = authority.observe()
    assert rows[0]["observation_kind"] == "SITE_SHARED_IMAGE"
    assert rows[0]["subject_name"] == "DYLD_IMAGE"


def test_runtime_subset_freeze_rejects_external_dyld_and_accepts_protected_system_image(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(admission.AdmissionError, match="interpreter/system authority"):
        _synthetic_runtime_authority(
            tmp_path / "rejected",
            (("demo", "1.0", "demo.py", b"demo"),),
            darwin_image_paths=(Path("/tmp/evil.dylib"),),
        )
    system_image = Path("/usr/lib/libSystem.B.dylib")
    authority = _synthetic_runtime_authority(
        tmp_path / "accepted",
        (("demo", "1.0", "demo.py", b"demo"),),
        darwin_image_paths=(system_image,),
    )
    site = tmp_path / "accepted/.venv/lib/python3.12/site-packages"
    demo = _runtime_module("demo", os.fspath(site / "demo.py"))
    monkeypatch.setattr(admission.sys, "modules", {"demo": demo})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: (system_image,))
    rows, _digest = authority.observe()
    assert len(rows) == 1


def test_runtime_interpreter_image_authority_rechecks_exact_paths_config_and_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(admission.sys, "executable", os.fspath(_PROJECT_ROOT / ".venv/bin/python3"))
    physical = Path(cast(str, getattr(sys, "_base_executable")))
    libpython = Path(cast(str, sysconfig.get_config_var("LIBDIR"))) / cast(
        str, sysconfig.get_config_var("LDLIBRARY")
    )
    retained_paths = (physical, libpython)
    assert admission._interpreter_image_paths(_PROJECT_ROOT, retained_paths) == frozenset(
        retained_paths
    )

    with monkeypatch.context() as context:
        context.setattr(admission.sys, "_base_executable", "/tmp/w04-forged-python")
        with pytest.raises(admission.AdmissionError, match="retained.*path authority"):
            admission._interpreter_image_paths(_PROJECT_ROOT, retained_paths)

    original_get_config_var = admission.sysconfig.get_config_var
    with monkeypatch.context() as context:
        context.setattr(
            admission.sysconfig,
            "get_config_var",
            lambda name: "attacker-soabi" if name == "SOABI" else original_get_config_var(name),
        )
        with pytest.raises(admission.AdmissionError, match="path/configuration"):
            admission._interpreter_image_paths(_PROJECT_ROOT, retained_paths)

    original_guard = admission._guard_read_absolute_regular

    for corrupted_path in retained_paths:

        def corrupt_after_exact_guard(path: Path, **kwargs: object) -> bytes:
            raw = cast(bytes, original_guard(path, **kwargs))
            return raw[:-1] + bytes((raw[-1] ^ 1,)) if path == corrupted_path else raw

        with monkeypatch.context() as context:
            context.setattr(admission, "_guard_read_absolute_regular", corrupt_after_exact_guard)
            with pytest.raises(admission.AdmissionError, match="byte authority"):
                admission._interpreter_image_paths(_PROJECT_ROOT, retained_paths)

    external_prefix = tmp_path / "byte-identical-python"
    external_physical = external_prefix / "bin/python3.12"
    external_library = external_prefix / "lib/libpython3.12.dylib"
    external_physical.parent.mkdir(parents=True)
    external_library.parent.mkdir(parents=True)
    external_physical.write_bytes(physical.read_bytes())
    external_library.write_bytes(libpython.read_bytes())
    external_physical.chmod(0o755)
    external_library.chmod(0o755)
    with monkeypatch.context() as context:
        context.setattr(admission.sys, "base_prefix", os.fspath(external_prefix))
        context.setattr(admission.sys, "_base_executable", os.fspath(external_physical))
        context.setattr(
            admission.sysconfig,
            "get_config_var",
            lambda name: (
                os.fspath(external_library.parent)
                if name == "LIBDIR"
                else original_get_config_var(name)
            ),
        )
        with pytest.raises(admission.AdmissionError, match="retained.*path authority"):
            admission._interpreter_image_paths(_PROJECT_ROOT, retained_paths)


def test_runtime_subset_rejects_uppercase_pyc_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _synthetic_runtime_authority(tmp_path, (("demo", "1.0", "demo.PYC", b"bytecode"),))
    origin = tmp_path / ".venv/lib/python3.12/site-packages/demo.PYC"
    module = _runtime_module("demo", os.fspath(origin))
    monkeypatch.setattr(admission.sys, "modules", {"demo": module})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="unsafe"):
        authority.observe()


def test_runtime_subset_freeze_rejects_ambiguous_concrete_owner(tmp_path: Path) -> None:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site.mkdir(parents=True)
    target = site / "demo.py"
    target.write_bytes(b"demo")
    target.chmod(0o644)
    row = {
        "mode": 0o644,
        "path": "demo.py",
        "sha256": hashlib.sha256(b"demo").hexdigest(),
        "size_bytes": 4,
    }
    packages = (
        {"name": "alpha", "record_rows": [row], "version": "1.0"},
        {"name": "beta", "record_rows": [row], "version": "1.0"},
    )
    with pytest.raises(admission.AdmissionError, match="multiple RECORD owners"):
        admission.freeze_runtime_subset_authority(
            tmp_path,
            packages,
            repository_rows=(),
            stdlib_rows=(),
            darwin_image_paths=(),
        )


def test_runtime_subset_native_positive_and_conflicting_owner_rejection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    suffix = admission.importlib.machinery.EXTENSION_SUFFIXES[0]
    owned = (
        ("pydantic-core", "2.41.5", "pydantic_core/__init__.py", b""),
        ("pydantic-core", "2.41.5", f"pydantic_core/_pydantic_core{suffix}", b"native1"),
        ("polars-runtime-32", "1.38.1", "_polars_runtime_32/__init__.py", b""),
        ("polars-runtime-32", "1.38.1", f"_polars_runtime_32/_polars_runtime{suffix}", b"native2"),
    )
    authority = _synthetic_runtime_authority(tmp_path, owned)
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    modules = {
        "pydantic_core": _runtime_module(
            "pydantic_core", os.fspath(site / "pydantic_core/__init__.py")
        ),
        "pydantic_core._pydantic_core": _runtime_module(
            "pydantic_core._pydantic_core",
            os.fspath(site / f"pydantic_core/_pydantic_core{suffix}"),
        ),
        "_polars_runtime_32": _runtime_module(
            "_polars_runtime_32", os.fspath(site / "_polars_runtime_32/__init__.py")
        ),
        "_polars_runtime_32._polars_runtime": _runtime_module(
            "_polars_runtime_32._polars_runtime",
            os.fspath(site / f"_polars_runtime_32/_polars_runtime{suffix}"),
        ),
    }
    with monkeypatch.context() as context:
        context.setattr(admission.sys, "modules", modules)
        context.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
        rows, _digest = authority.observe()
    native = {row["subject_name"]: row["owner_name"] for row in rows}
    assert native["pydantic_core._pydantic_core"] == "pydantic-core"
    assert native["_polars_runtime_32._polars_runtime"] == "polars-runtime-32"

    conflicting = _synthetic_runtime_authority(
        tmp_path / "conflict",
        (
            ("alpha", "1.0", f"demo/one{suffix}", b"one"),
            ("beta", "1.0", f"demo/two{suffix}", b"two"),
        ),
    )
    conflict_site = tmp_path / "conflict/.venv/lib/python3.12/site-packages"
    with monkeypatch.context() as context:
        context.setattr(
            admission.sys,
            "modules",
            {
                "demo.one": _runtime_module(
                    "demo.one", os.fspath(conflict_site / f"demo/one{suffix}")
                ),
                "demo.two": _runtime_module(
                    "demo.two", os.fspath(conflict_site / f"demo/two{suffix}")
                ),
            },
        )
        context.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
        with pytest.raises(admission.AdmissionError, match="conflicting owners"):
            conflicting.observe()


@pytest.mark.parametrize("module_root", ("pydantic_core", "_polars_runtime_32"))
def test_runtime_subset_rejects_parent_missing_required_native_wrong_owner(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, module_root: str
) -> None:
    suffix = admission.importlib.machinery.EXTENSION_SUFFIXES[0]
    relative = f"{module_root}/_native{suffix}"
    authority = _synthetic_runtime_authority(
        tmp_path,
        (("wrong-owner", "1.0", relative, b"native"),),
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    subject = f"{module_root}._native"
    module = _runtime_module(subject, os.fspath(site / relative))
    monkeypatch.setattr(
        admission.sys,
        "modules",
        {subject: module},
    )
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: ())
    with pytest.raises(admission.AdmissionError, match="native runtime owner mapping"):
        authority.observe()


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
def test_runtime_subset_rejects_required_root_shared_image_without_native_row(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_root: str,
    required_owner: str,
) -> None:
    relative = f"{module_root}/runtime.dylib"
    authority = _synthetic_runtime_authority(
        tmp_path,
        ((required_owner, "1.0", relative, b"shared"),),
    )
    image = tmp_path / ".venv/lib/python3.12/site-packages" / relative
    monkeypatch.setattr(admission.sys, "modules", {})
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: (image,))
    with pytest.raises(admission.AdmissionError, match="native runtime owner mapping"):
        authority.observe()


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
@pytest.mark.parametrize(
    "companion_kind",
    ("source-owner", "source-version", "namespace", "shared-image"),
)
def test_runtime_subset_rejects_wrong_owner_companion_beside_required_native(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module_root: str,
    required_owner: str,
    companion_kind: str,
) -> None:
    suffix = admission.importlib.machinery.EXTENSION_SUFFIXES[0]
    native_relative = f"{module_root}/_native{suffix}"
    companion_relative = f"{module_root}/" + (
        "namespace_child.py"
        if companion_kind == "namespace"
        else "extra.dylib"
        if companion_kind == "shared-image"
        else "extra.py"
    )
    companion_owner = required_owner if companion_kind == "source-version" else "wrong-owner"
    authority = _synthetic_runtime_authority(
        tmp_path,
        (
            (required_owner, "1.0", native_relative, b"native"),
            (companion_owner, "2.0", companion_relative, b"companion"),
        ),
    )
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    native_subject = f"{module_root}._native"
    modules = {native_subject: _runtime_module(native_subject, os.fspath(site / native_relative))}
    images: tuple[Path, ...] = ()
    if companion_kind.startswith("source"):
        companion_subject = f"{module_root}.extra"
        modules[companion_subject] = _runtime_module(
            companion_subject, os.fspath(site / companion_relative)
        )
    elif companion_kind == "namespace":
        modules[module_root] = _runtime_module(module_root, None, [os.fspath(site / module_root)])
    else:
        images = (site / companion_relative,)
    monkeypatch.setattr(admission.sys, "modules", modules)
    monkeypatch.setattr(admission, "_darwin_loaded_image_paths", lambda: images)
    with pytest.raises(admission.AdmissionError, match="native runtime owner mapping"):
        authority.observe()


class _RuntimeRowStub:
    def __init__(self, values: dict[str, object]) -> None:
        self.values = values

    def model_dump(self, *, mode: str) -> dict[str, object]:
        assert mode == "json"
        return dict(self.values)


def _launcher_runtime_authority(
    tmp_path: Path,
    owned: tuple[tuple[str, str, str, bytes], ...],
    *,
    extension_suffixes: tuple[str, ...] = (".so",),
) -> object:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site.mkdir(parents=True)
    owners: dict[str, tuple[str, str, int, int, str]] = {}
    selected: set[tuple[str, str]] = set()
    for owner, version, relative, raw in owned:
        target = site / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        target.chmod(0o644)
        owners[relative] = (owner, version, 0o644, len(raw), hashlib.sha256(raw).hexdigest())
        selected.add((owner, version))
    return launcher._IndependentRuntimeSubsetAuthority(
        extension_suffixes=extension_suffixes,
        owners=owners,
        project_root=tmp_path,
        selected_owners=frozenset(selected),
        site=site,
    )


def _runtime_final_recheck(rows: list[dict[str, object]]) -> object:
    ordered = sorted(rows, key=launcher._canonical_json_bytes)
    return SimpleNamespace(
        runtime_subset_digest=launcher._sha256_json(
            {"algorithm": launcher.RUNTIME_SUBSET_ALGORITHM, "rows": ordered}
        ),
        runtime_subset_rows=tuple(_RuntimeRowStub(row) for row in ordered),
    )


@pytest.mark.parametrize(
    "mutation",
    ("owner", "version", "path", "subject", "insert-unselected", "shared-source"),
)
def test_launcher_runtime_subset_rejects_coherent_returned_row_substitution(
    tmp_path: Path, mutation: str
) -> None:
    authority = _launcher_runtime_authority(
        tmp_path,
        (
            ("alpha", "1.0", "alpha.py", b"alpha"),
            ("beta", "2.0", "beta.py", b"beta"),
        ),
    )
    row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "alpha",
        "owner_version": "1.0",
        "site_relative_path": "alpha.py",
        "subject_name": "alpha",
    }
    if mutation == "owner":
        row["owner_name"] = "beta"
    elif mutation == "version":
        row["owner_version"] = "2.0"
    elif mutation == "path":
        row["site_relative_path"] = "beta.py"
    elif mutation == "subject":
        row["subject_name"] = "beta"
    elif mutation == "insert-unselected":
        row["owner_name"] = "gamma"
    else:
        row["observation_kind"] = "SITE_SHARED_IMAGE"
        row["subject_name"] = "DYLD_IMAGE"
    with pytest.raises(launcher.RuntimeControlError):
        authority.validate(_runtime_final_recheck([row]))  # type: ignore[attr-defined]


@pytest.mark.parametrize("attack", ("lock-only", "installed-only"))
def test_launcher_runtime_subset_rejects_lock_only_and_installed_only_identity(
    tmp_path: Path, attack: str
) -> None:
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site.mkdir(parents=True)
    alpha = site / "alpha.py"
    attacked = site / f"{attack.replace('-', '_')}.py"
    alpha.write_bytes(b"alpha")
    attacked.write_bytes(b"attacked")
    alpha.chmod(0o644)
    attacked.chmod(0o644)
    owners = {"alpha.py": ("alpha", "1.0", 0o644, 5, hashlib.sha256(b"alpha").hexdigest())}
    selected = {("alpha", "1.0")}
    if attack == "lock-only":
        selected.add(("lock-only", "8.0"))
    else:
        owners["installed_only.py"] = (
            "installed-only",
            "9.0",
            0o644,
            8,
            hashlib.sha256(b"attacked").hexdigest(),
        )
    authority = launcher._IndependentRuntimeSubsetAuthority(
        extension_suffixes=(".so",),
        owners=owners,
        project_root=tmp_path,
        selected_owners=frozenset(selected),
        site=site,
    )
    row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": attack,
        "owner_version": "8.0" if attack == "lock-only" else "9.0",
        "site_relative_path": f"{attack.replace('-', '_')}.py",
        "subject_name": attack.replace("-", "_"),
    }
    with pytest.raises(launcher.RuntimeControlError, match="outside frozen|owner/path"):
        authority.validate(_runtime_final_recheck([row]))


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
@pytest.mark.parametrize("attack", ("omitted-native", "wrong-native-owner"))
def test_launcher_runtime_subset_rejects_omitted_or_wrong_required_native(
    tmp_path: Path, module_root: str, required_owner: str, attack: str
) -> None:
    owner = required_owner if attack == "omitted-native" else "wrong-owner"
    relative = (
        f"{module_root}/__init__.py" if attack == "omitted-native" else f"{module_root}/_native.so"
    )
    subject = module_root if attack == "omitted-native" else f"{module_root}._native"
    kind = "MODULE_SOURCE" if attack == "omitted-native" else "NATIVE_EXTENSION"
    authority = _launcher_runtime_authority(
        tmp_path,
        ((owner, "1.0", relative, b"runtime"),),
    )
    row: dict[str, object] = {
        "observation_kind": kind,
        "owner_name": owner,
        "owner_version": "1.0",
        "site_relative_path": relative,
        "subject_name": subject,
    }
    with pytest.raises(launcher.RuntimeControlError, match="native owner mapping"):
        authority.validate(_runtime_final_recheck([row]))  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
def test_launcher_runtime_subset_accepts_exact_required_native_owner(
    tmp_path: Path, module_root: str, required_owner: str
) -> None:
    relative = f"{module_root}/_native.so"
    authority = _launcher_runtime_authority(
        tmp_path,
        ((required_owner, "1.0", relative, b"runtime"),),
    )
    row: dict[str, object] = {
        "observation_kind": "NATIVE_EXTENSION",
        "owner_name": required_owner,
        "owner_version": "1.0",
        "site_relative_path": relative,
        "subject_name": f"{module_root}._native",
    }
    authority.validate(_runtime_final_recheck([row]))  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
def test_launcher_runtime_subset_rejects_required_root_shared_image_without_native_row(
    tmp_path: Path, module_root: str, required_owner: str
) -> None:
    relative = f"{module_root}/runtime.dylib"
    authority = _launcher_runtime_authority(
        tmp_path,
        ((required_owner, "1.0", relative, b"shared"),),
    )
    row: dict[str, object] = {
        "observation_kind": "SITE_SHARED_IMAGE",
        "owner_name": required_owner,
        "owner_version": "1.0",
        "site_relative_path": relative,
        "subject_name": "DYLD_IMAGE",
    }
    with pytest.raises(launcher.RuntimeControlError, match="native owner mapping"):
        authority.validate(_runtime_final_recheck([row]))  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    ("module_root", "required_owner"),
    (
        ("pydantic_core", "pydantic-core"),
        ("_polars_runtime_32", "polars-runtime-32"),
    ),
)
@pytest.mark.parametrize(
    "companion_kind",
    ("source-owner", "source-version", "namespace", "shared-image"),
)
def test_launcher_runtime_subset_rejects_split_identity_beside_required_native(
    tmp_path: Path, module_root: str, required_owner: str, companion_kind: str
) -> None:
    native_relative = f"{module_root}/_native.so"
    companion_relative = f"{module_root}/" + (
        "namespace_child.py"
        if companion_kind == "namespace"
        else "extra.dylib"
        if companion_kind == "shared-image"
        else "extra.py"
    )
    companion_owner = required_owner if companion_kind == "source-version" else "wrong-owner"
    authority = _launcher_runtime_authority(
        tmp_path,
        (
            (required_owner, "1.0", native_relative, b"native"),
            (companion_owner, "2.0", companion_relative, b"companion"),
        ),
    )
    rows: list[dict[str, object]] = [
        {
            "observation_kind": "NATIVE_EXTENSION",
            "owner_name": required_owner,
            "owner_version": "1.0",
            "site_relative_path": native_relative,
            "subject_name": f"{module_root}._native",
        }
    ]
    if companion_kind.startswith("source"):
        rows.append(
            {
                "observation_kind": "MODULE_SOURCE",
                "owner_name": companion_owner,
                "owner_version": "2.0",
                "site_relative_path": companion_relative,
                "subject_name": f"{module_root}.extra",
            }
        )
    elif companion_kind == "namespace":
        rows.append(
            {
                "observation_kind": "NAMESPACE_LOCATION",
                "owner_name": companion_owner,
                "owner_version": "2.0",
                "site_relative_path": module_root,
                "subject_name": module_root,
            }
        )
    else:
        rows.append(
            {
                "observation_kind": "SITE_SHARED_IMAGE",
                "owner_name": companion_owner,
                "owner_version": "2.0",
                "site_relative_path": companion_relative,
                "subject_name": "DYLD_IMAGE",
            }
        )
    with pytest.raises(launcher.RuntimeControlError, match="native owner mapping"):
        authority.validate(_runtime_final_recheck(rows))  # type: ignore[attr-defined]


def test_launcher_runtime_subset_uses_frozen_suffix_and_rejects_native_owner_ambiguity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    authority = _launcher_runtime_authority(
        tmp_path,
        (
            ("alpha", "1.0", "demo/one.frozen", b"one"),
            ("beta", "2.0", "demo/two.frozen", b"two"),
        ),
        extension_suffixes=(".frozen",),
    )
    monkeypatch.setattr(launcher.importlib.machinery, "EXTENSION_SUFFIXES", [".attacker"])
    rows: list[dict[str, object]] = [
        {
            "observation_kind": "NATIVE_EXTENSION",
            "owner_name": owner,
            "owner_version": version,
            "site_relative_path": path,
            "subject_name": subject,
        }
        for owner, version, path, subject in (
            ("alpha", "1.0", "demo/one.frozen", "demo.one"),
            ("beta", "2.0", "demo/two.frozen", "demo.two"),
        )
    ]
    with pytest.raises(launcher.RuntimeControlError, match="ambiguous"):
        authority.validate(_runtime_final_recheck(rows))  # type: ignore[attr-defined]


def test_launcher_runtime_subset_rejects_symlinked_parent(
    tmp_path: Path,
) -> None:
    authority = _launcher_runtime_authority(tmp_path, (("demo", "1.0", "demo/module.py", b"demo"),))
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    parent = site / "demo"
    displaced = site / "displaced"
    parent.rename(displaced)
    parent.symlink_to(displaced, target_is_directory=True)
    row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "demo",
        "owner_version": "1.0",
        "site_relative_path": "demo/module.py",
        "subject_name": "demo.module",
    }
    with pytest.raises(launcher.RuntimeControlError, match="unsafe site parent"):
        authority.validate(_runtime_final_recheck([row]))  # type: ignore[attr-defined]


def _synthetic_process_evidence(role: str = "PRE_BUILD_ADMISSION") -> Any:
    argv = launcher.ADMISSION_ARGV if role == "PRE_BUILD_ADMISSION" else launcher.REBUILD_ARGV
    payload_kind = (
        "CODE_ENVIRONMENT_MANIFEST" if role == "PRE_BUILD_ADMISSION" else "REBUILD_COMPLETION"
    )
    empty_digest = hashlib.sha256(b"").hexdigest()
    nonce = "a" * 64
    transport = "b" * 64
    entrypoint = {
        "descriptor_cloexec": False,
        "descriptor_inheritable": True,
        "descriptor_number": 8,
        "device": 1,
        "inode": 2,
        "link_count": 1,
        "mode": 0o644,
        "offset_after": 0,
        "offset_before": 0,
        "relative_path": argv[-1],
        "role": role,
        "sha256": "c" * 64,
        "size_bytes": 100,
        "source_eof": True,
    }
    payload = launcher._canonical_json_bytes(
        {
            "child_environment_sha256": transport,
            "child_role": role,
            "entrypoint_source": entrypoint,
            "nonce": nonce,
            "payload_kind": payload_kind,
            "schema_version": launcher.CHILD_RESULT_SCHEMA_VERSION,
        }
    )
    identity = {"device": 3, "inode": 4, "link_count": 2, "mode": 0o700}
    observation = {
        "argv": list(argv),
        "argv_sha256": launcher._sha256_json(list(argv)),
        "child_input_schema_version": launcher.CHILD_INPUT_SCHEMA_VERSION,
        "child_role": role,
        "cross_field_binding": True,
        "diagnostics_empty": True,
        "entrypoint_source": entrypoint,
        "exit_code": 0,
        "final_uv_value": "/opt/homebrew/bin/uv",
        "frame_count": 1,
        "frame_eof": True,
        "frame_magic": "W04CRSLT",
        "frame_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "frame_payload_size_bytes": len(payload),
        "frame_version": 1,
        "in_place_pyc_unchanged": True,
        "initial_uv_value": "/opt/homebrew/bin/uv",
        "nonce": nonce,
        "not_timed_out": True,
        "payload_kind": payload_kind,
        "prefix_absolute_path": "/tmp/w04-runtime-pycache",
        "prefix_empty_after": True,
        "prefix_empty_before": True,
        "prefix_identity_after": identity,
        "prefix_identity_before": identity,
        "prefix_identity_unchanged": True,
        "prefix_relative_path": "data/working/wyscout/v5/runtime-pycache",
        "process_id": 100,
        "result_descriptor_inheritable": True,
        "result_descriptor_number": 9,
        "result_descriptor_parent_closed": True,
        "result_schema_version": launcher.CHILD_RESULT_SCHEMA_VERSION,
        "source_descriptor_checkpoint": True,
        "stderr_sha256": empty_digest,
        "stderr_size_bytes": 0,
        "stdout_sha256": empty_digest,
        "stdout_size_bytes": 0,
        "timeout_milliseconds": 1000,
        "transport_environment_sha256": transport,
        "uv_path_resolution": "/opt/homebrew/bin/uv",
        "zero_in_place_pyc_reads": True,
    }
    expected_facts = {
        "entrypoint_source": entrypoint,
        "frame_payload_sha256": hashlib.sha256(payload).hexdigest(),
        "frame_payload_size_bytes": len(payload),
        "nonce": nonce,
        "prefix_absolute_path": "/tmp/w04-runtime-pycache",
        "prefix_identity_after": identity,
        "prefix_identity_before": identity,
        "prefix_relative_path": "data/working/wyscout/v5/runtime-pycache",
        "process_id": 100,
        "result_descriptor_number": 9,
        "timeout_milliseconds": 1000,
        "transport_environment_sha256": transport,
    }
    evidence = launcher.ChildProcessEvidence(
        expected_facts_bytes=launcher._canonical_json_bytes(expected_facts),
        observation_bytes=launcher._canonical_json_bytes(observation),
        payload_bytes=payload,
        role=role,
    )
    evidence.validate()
    return evidence


def test_child_process_evidence_rejects_file_style_link_count_for_empty_directory() -> None:
    evidence = _synthetic_process_evidence()
    observation = json.loads(evidence.observation_bytes)
    expected_facts = json.loads(evidence.expected_facts_bytes)
    for container in (observation, expected_facts):
        container["prefix_identity_after"]["link_count"] = 1
        container["prefix_identity_before"]["link_count"] = 1
    attacked = replace(
        evidence,
        expected_facts_bytes=launcher._canonical_json_bytes(expected_facts),
        observation_bytes=launcher._canonical_json_bytes(observation),
    )
    with pytest.raises(launcher.RuntimeControlError, match="prefix identity binding differs"):
        attacked.validate()


@pytest.mark.parametrize(
    "attack",
    (
        "argv",
        "pid",
        "fd",
        "frame",
        "diagnostic",
        "prefix-absolute",
        "prefix-traversal",
        "prefix-identity",
        "uv",
        "nonce",
        "transport",
        "entry-extra",
        "entry-descriptor",
    ),
)
def test_child_process_evidence_rejects_coherent_cross_field_attacks(attack: str) -> None:
    evidence = _synthetic_process_evidence()
    observation = json.loads(evidence.observation_bytes)
    payload = json.loads(evidence.payload_bytes)
    if attack == "argv":
        observation["argv"].append("--attack")
        observation["argv_sha256"] = launcher._sha256_json(observation["argv"])
    elif attack == "pid":
        observation["process_id"] += 1
    elif attack == "fd":
        observation["result_descriptor_number"] += 1
    elif attack == "frame":
        payload["attacker"] = True
        changed_payload = launcher._canonical_json_bytes(payload)
        observation["frame_payload_sha256"] = hashlib.sha256(changed_payload).hexdigest()
        observation["frame_payload_size_bytes"] = len(changed_payload)
        evidence = replace(evidence, payload_bytes=changed_payload)
    elif attack == "diagnostic":
        observation["stdout_size_bytes"] = 1
        observation["stdout_sha256"] = hashlib.sha256(b"x").hexdigest()
    elif attack == "prefix-absolute":
        observation["prefix_absolute_path"] = "/tmp/substituted"
    elif attack == "prefix-traversal":
        observation["prefix_relative_path"] = "data/../escape"
    elif attack == "prefix-identity":
        observation["prefix_identity_after"]["inode"] += 1
        observation["prefix_identity_before"]["inode"] += 1
    elif attack == "uv":
        observation["final_uv_value"] = "/tmp/uv"
    elif attack == "nonce":
        observation["nonce"] = "d" * 64
        payload["nonce"] = "d" * 64
        evidence = replace(evidence, payload_bytes=launcher._canonical_json_bytes(payload))
    elif attack == "transport":
        observation["transport_environment_sha256"] = "d" * 64
        payload["child_environment_sha256"] = "d" * 64
        evidence = replace(evidence, payload_bytes=launcher._canonical_json_bytes(payload))
    elif attack == "entry-extra":
        observation["entrypoint_source"]["extra"] = True
    else:
        observation["entrypoint_source"]["descriptor_number"] = 9
    attacked = replace(evidence, observation_bytes=launcher._canonical_json_bytes(observation))
    with pytest.raises(launcher.RuntimeControlError):
        attacked.validate()


def test_child_process_evidence_is_immutable_across_decoded_mutation_and_rejects_unknown_role() -> (
    None
):
    evidence = _synthetic_process_evidence()
    decoded = evidence.validate()
    decoded["process_id"] = 999
    assert evidence.validate()["process_id"] == 100
    with pytest.raises(launcher.RuntimeControlError, match="role"):
        replace(evidence, role="UNKNOWN").validate()


def test_child_process_evidence_rejects_whole_valid_runtime_row_envelope_substitution() -> None:
    evidence = _synthetic_process_evidence()
    original = json.loads(evidence.payload_bytes)

    class EnvelopeStub:
        def __init__(self, value: dict[str, object]) -> None:
            self.value = value

        def model_dump(self, *, mode: str) -> dict[str, object]:
            assert mode == "json"
            return self.value

    assert evidence.validate(EnvelopeStub(original))["process_id"] == 100
    substituted = deepcopy(original)
    substituted["result"] = {
        "runtime_subset_rows": [
            {
                "observation_kind": "MODULE_SOURCE",
                "owner_name": "beta",
                "owner_version": "2.0",
                "site_relative_path": "beta.py",
                "subject_name": "beta",
            }
        ]
    }
    with pytest.raises(launcher.RuntimeControlError, match="current child envelope"):
        evidence.validate(EnvelopeStub(substituted))


def test_synthetic_two_root_runtime_subset_mismatch_is_rejected() -> None:
    alpha_row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "alpha",
        "owner_version": "1.0",
        "site_relative_path": "alpha.py",
        "subject_name": "alpha",
    }
    beta_row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "beta",
        "owner_version": "2.0",
        "site_relative_path": "beta.py",
        "subject_name": "beta",
    }

    def evidence(row: dict[str, object]) -> dict[str, object]:
        rows = [row]
        return {
            "runtime_subset_digest": launcher._sha256_json(
                {"algorithm": launcher.RUNTIME_SUBSET_ALGORITHM, "rows": rows}
            ),
            "runtime_subset_rows": rows,
        }

    launcher._require_matching_runtime_subset_evidence(evidence(alpha_row), evidence(alpha_row))
    with pytest.raises(launcher.RuntimeControlError, match="subsets differ"):
        launcher._require_matching_runtime_subset_evidence(evidence(alpha_row), evidence(beta_row))


def test_outer_completion_rejects_stale_v1_at_status_boundary() -> None:
    rows: list[dict[str, object]] = []
    status: dict[str, object] = {
        "admission_run_id": str(uuid4()),
        "build_id": "b" * 64,
        "child_process_observations": [],
        "code_manifest_sha256": "c" * 64,
        "control_run_id": str(uuid4()),
        "outer_transport_environment_sha256": "e" * 64,
        "pyc_inventory_health": {},
        "rebuild_receipt_relative_path": "receipt.json",
        "rebuild_receipt_sha256": "f" * 64,
        "run_id": str(uuid4()),
        "runtime_subset_digest": launcher._sha256_json(
            {"algorithm": launcher.RUNTIME_SUBSET_ALGORITHM, "rows": rows}
        ),
        "runtime_subset_rows": rows,
        "schema_version": "w04-local-control-completion-v1",
        "status": "COMPLETE",
    }
    with pytest.raises(launcher.RuntimeControlError, match="version/status"):
        launcher._validate_outer_completion_status(status)


@pytest.mark.parametrize("attack", ("swapped", "omitted"))
def test_outer_completion_rejects_swapped_or_omitted_process_rows(attack: str) -> None:
    admission_row = _synthetic_process_evidence("PRE_BUILD_ADMISSION").validate()
    rebuild_row = _synthetic_process_evidence("POST_BUILD_ID_REBUILD").validate()
    process_rows = [admission_row, rebuild_row]
    if attack == "swapped":
        process_rows.reverse()
    else:
        process_rows.pop()
    rows: list[dict[str, object]] = []
    status: dict[str, object] = {
        "admission_run_id": str(uuid4()),
        "build_id": "b" * 64,
        "child_process_observations": process_rows,
        "code_manifest_sha256": "c" * 64,
        "control_run_id": str(uuid4()),
        "outer_transport_environment_sha256": "e" * 64,
        "pyc_inventory_health": {},
        "rebuild_receipt_relative_path": "receipt.json",
        "rebuild_receipt_sha256": "f" * 64,
        "run_id": str(uuid4()),
        "runtime_subset_digest": launcher._sha256_json(
            {"algorithm": launcher.RUNTIME_SUBSET_ALGORITHM, "rows": rows}
        ),
        "runtime_subset_rows": rows,
        "schema_version": "w04-local-control-completion-v2",
        "status": "COMPLETE",
    }
    with pytest.raises(launcher.RuntimeControlError, match="role|cardinality"):
        launcher._validate_outer_completion_status(status)


def test_closed_child_environment_does_not_import_outer_operational_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("HOME", "TMPDIR", "UV_CACHE_DIR", "__CF_USER_TEXT_ENCODING"):
        monkeypatch.setenv(name, f"attacker-{name}")
    environment = launcher._closed_child_environment(
        project_root=_PROJECT_ROOT,
        pycache_prefix=tmp_path,
        role="PRE_BUILD_ADMISSION",
        source_fd=7,
        result_fd=8,
        nonce="0" * 64,
    )
    assert environment["HOME"] == "/Users/adrian"
    assert environment["TMPDIR"].startswith("/var/folders/")
    assert environment["UV_CACHE_DIR"] == "/Users/adrian/.cache/uv"
    assert environment["__CF_USER_TEXT_ENCODING"] == "0x1F5:0:2"


def test_launcher_retained_oracle_never_loads_or_calls_child_collector() -> None:
    source = (_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_text()
    assert "_load_admission_module" not in source
    assert "collect_stable_authority" not in source
    assert "importlib.util" not in source
    assert "def _admission_authority" in source


def test_child_collector_substitution_cannot_change_retained_oracle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retained = launcher._admission_authority(_PROJECT_ROOT)
    changed_components = dict(retained[1])
    changed_components["stdlib_digest"] = "0" * 64
    monkeypatch.setattr(
        admission,
        "collect_stable_authority",
        lambda _root: (retained[0], changed_components, retained[2]),
    )
    substituted = admission.collect_stable_authority(_PROJECT_ROOT)
    assert substituted != retained
    assert launcher._admission_authority(_PROJECT_ROOT) == retained


def test_closed_admission_environment_rejects_missing_additional_and_absent_names() -> None:
    environment = dict(admission._STATIC_ENVIRONMENT)
    environment.update(
        {
            name: f"value-{index}"
            for index, name in enumerate(admission._OPERATIONAL_ENVIRONMENT_NAMES)
        }
    )
    assert admission.normalized_child_environment(environment)["required_absent"] == list(
        admission.REQUIRED_ABSENT_ENVIRONMENT
    )
    for mutation in (
        {key: value for key, value in environment.items() if key != "LANG"},
        {**environment, "UNREVIEWED": "1"},
        {**environment, "HTTP_PROXY": "http://example.invalid"},
    ):
        with pytest.raises(admission.AdmissionError, match="environment|absent"):
            admission.normalized_child_environment(mutation)


def _minimal_pyc_policy(root: Path) -> dict[str, object]:
    _directory(root / ".venv/lib/python3.12/site-packages")
    foreign_source = root / "scripts/admit_wyscout_v5_runtime.py"
    foreign_source.parent.mkdir(parents=True, exist_ok=True)
    foreign_source.write_text("VALUE = 'stable-authoritative'\n")
    foreign_source.chmod(0o644)
    foreign_cache = foreign_source.parent / "__pycache__"
    foreign_cache.mkdir(mode=0o755)
    foreign_cache.chmod(0o755)
    foreign_target = foreign_cache / "admit_wyscout_v5_runtime.cpython-314.pyc"
    foreign_target.write_bytes(bytes(190_312))
    foreign_target.chmod(0o644)
    predicates = tuple(
        {
            "authority_class": authority,
            "cache_path": cache_path,
            "expected_mode": 0o644,
            "expected_sha256": digest,
            "expected_size_bytes": size,
            "source_path": source,
            "source_required_absent": True,
            "traversal_root_role": role,
        }
        for authority, cache_path, size, digest, source, role in (
            (
                "SITE_SIX_OPTIONAL_INERT_ORPHAN",
                "__pycache__/six.cpython-312.pyc",
                41_388,
                "4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28",
                "six.py",
                "SELECTED_SITE_PACKAGES",
            ),
            (
                "REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN",
                "migrations/__pycache__/env.cpython-312.pyc",
                2_795,
                "6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2",
                "migrations/env.py",
                "WHOLE_REPOSITORY",
            ),
            (
                "REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN",
                "migrations/versions/__pycache__/0001_foundation.cpython-312.pyc",
                25_415,
                "b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d",
                "migrations/versions/0001_foundation.py",
                "WHOLE_REPOSITORY",
            ),
            (
                "REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN",
                "src/scouting/storage/__pycache__/postgres.cpython-312.pyc",
                4_230,
                "ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac",
                "src/scouting/storage/postgres.py",
                "WHOLE_REPOSITORY",
            ),
        )
    )
    return {
        "foreign_cache_tag_denial_predicates": (
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
        ),
        "post_w04_audit_only_source_paths": (
            admission._derive_post_w04_audit_only_pyc_source_paths(
                root,
                frozenset({"scripts/admit_wyscout_v5_runtime.py"}),
            )
        ),
        "post_w04_retired_audit_only_pyc_predicates": (
            admission.POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES
        ),
        "source_rows": (
            {
                "authority_class": "REPOSITORY_CODE_MANIFEST",
                "normal_cache_name": (
                    "admit_wyscout_v5_runtime.cpython-312[.opt-0|.opt-1|.opt-2].pyc"
                ),
                "owner": "scripts/admit_wyscout_v5_runtime.py",
                "path": "scripts/admit_wyscout_v5_runtime.py",
                "pytest_cache_name": ("admit_wyscout_v5_runtime.cpython-312-pytest-9.1.1.pyc"),
                "sha256": hashlib.sha256(foreign_source.read_bytes()).hexdigest(),
                "size_bytes": foreign_source.stat().st_size,
            },
        ),
        "orphan_predicates": predicates,
    }


def _manifested_pyc_fixture(root: Path) -> tuple[dict[str, object], Path]:
    _directory(root / ".venv/lib/python3.12/site-packages")
    source = root / "tests/test_present.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n")
    source.chmod(0o644)
    cache = source.parent / "__pycache__"
    cache.mkdir(mode=0o755)
    target = cache / "test_present.cpython-312-pytest-9.1.1.pyc"
    py_compile.compile(os.fspath(source), cfile=os.fspath(target), doraise=True)
    target.chmod(0o644)
    policy = _minimal_pyc_policy(root)
    policy["source_rows"] = (
        *cast(tuple[dict[str, object], ...], policy["source_rows"]),
        {
            "authority_class": "REPOSITORY_CODE_MANIFEST",
            "normal_cache_name": "test_present.cpython-312[.opt-0|.opt-1|.opt-2].pyc",
            "owner": "tests/test_present.py",
            "path": "tests/test_present.py",
            "pytest_cache_name": "test_present.cpython-312-pytest-9.1.1.pyc",
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "size_bytes": source.stat().st_size,
        },
    )
    policy["post_w04_audit_only_source_paths"] = ()
    return policy, target


def _empty_cache_directory_fixture(root: Path) -> tuple[dict[str, object], Path]:
    _directory(root / ".venv/lib/python3.12/site-packages")
    cache = root / "tests/__pycache__"
    cache.mkdir(parents=True, mode=0o755)
    cache.chmod(0o755)
    return _minimal_pyc_policy(root), cache


def _inventory_row(
    rows: tuple[dict[str, object], ...], *, path: str, role: str = "WHOLE_REPOSITORY"
) -> dict[str, object]:
    return next(row for row in rows if row["path"] == path and row["role"] == role)


_PYC_INVENTORY_COLLECTORS = (
    (
        "launcher",
        launcher._independent_pyc_inventory,
        launcher.RuntimeControlError,
    ),
    (
        "child",
        admission._operational_pyc_inventory,
        admission.AdmissionError,
    ),
)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_foreign_cache_tag_has_one_exact_denied_zero_read_classification(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    row = _inventory_row(
        collector(tmp_path, policy),
        path="scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc",
    )
    assert row["authority_class"] == "REPOSITORY_FOREIGN_CACHE_TAG_DENIED"
    assert row["denial_policy"] == "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ"
    assert row["foreign_cache_tag"] == "cpython-314"
    assert row["mode"] == 0o644
    assert row["size_bytes"] == 190_312
    assert row["source_path"] == "scripts/admit_wyscout_v5_runtime.py"
    assert row["source_authority"] is None
    assert row["source_authority_required"] == "REPOSITORY_CODE_MANIFEST"
    assert "owner" not in row
    assert "sha256" not in row


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
@pytest.mark.parametrize(
    ("field", "substitute"),
    (
        (
            "authority_class",
            "REPOSITORY_NORMAL",
        ),
        (
            "cache_path",
            "scripts/__pycache__/admit_wyscout_v5_runtime.cpython-313.pyc",
        ),
        ("cache_path", "../admit_wyscout_v5_runtime.cpython-314.pyc"),
        ("cache_tag", "cpython-313"),
        ("denial_policy", "FOREIGN_INTERPRETER_TAG_ALLOWED"),
        ("expected_mode", 0o600),
        ("expected_size_bytes", 190_311),
        ("source_authority_required", "SELECTED_DISTRIBUTION_RECORD"),
        ("source_path", "scripts/launch_wyscout_v5.py"),
        ("traversal_root_role", "SELECTED_SITE_PACKAGES"),
    ),
)
def test_foreign_cache_tag_rejects_every_predicate_substitution(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
    field: str,
    substitute: object,
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    predicate = dict(
        cast(tuple[dict[str, object], ...], policy["foreign_cache_tag_denial_predicates"])[0]
    )
    predicate[field] = substitute
    policy["foreign_cache_tag_denial_predicates"] = (predicate,)
    with pytest.raises(error, match="predicate differs"):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_foreign_cache_tag_rejects_duplicate_predicate(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    predicate = cast(tuple[dict[str, object], ...], policy["foreign_cache_tag_denial_predicates"])[
        0
    ]
    policy["foreign_cache_tag_denial_predicates"] = (predicate, predicate)
    with pytest.raises(error, match="predicate differs|duplicated"):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_foreign_cache_tag_rejects_missing_predicate(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    del policy["foreign_cache_tag_denial_predicates"]
    with pytest.raises(error, match="predicate differs"):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "wrong_class",
        "wrong_owner",
        "wrong_path",
        "wrong_sha",
        "wrong_size",
        "extra_field",
        "duplicate",
        "mode",
        "hardlink",
        "symlink",
    ),
)
def test_foreign_cache_tag_rejects_missing_or_wrong_stable_source(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
    mutation: str,
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    source = tmp_path / "scripts/admit_wyscout_v5_runtime.py"
    source_rows = list(cast(tuple[dict[str, object], ...], policy["source_rows"]))
    if mutation == "missing":
        source.unlink()
    elif mutation == "wrong_class":
        source_rows[0] = {**source_rows[0], "authority_class": "SELECTED_DISTRIBUTION_RECORD"}
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "wrong_owner":
        source_rows[0] = {**source_rows[0], "owner": "scripts/launch_wyscout_v5.py"}
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "wrong_path":
        source_rows[0] = {**source_rows[0], "path": "scripts/launch_wyscout_v5.py"}
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "wrong_sha":
        source_rows[0] = {**source_rows[0], "sha256": "not-a-sha256"}
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "wrong_size":
        source_rows[0] = {
            **source_rows[0],
            "size_bytes": cast(int, source_rows[0]["size_bytes"]) + 1,
        }
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "extra_field":
        source_rows[0] = {**source_rows[0], "unreviewed": True}
        policy["source_rows"] = tuple(source_rows)
    elif mutation == "duplicate":
        policy["source_rows"] = (*source_rows, dict(source_rows[0]))
    elif mutation == "mode":
        source.chmod(0o600)
    elif mutation == "hardlink":
        os.link(source, tmp_path / "source-hardlink.py")
    else:
        substitute = tmp_path / "source-substitute.py"
        substitute.write_bytes(source.read_bytes())
        substitute.chmod(0o644)
        source.unlink()
        source.symlink_to(substitute)
    with pytest.raises(
        error,
        match="source authority|source path|source row|source roster|unsafe source",
    ):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "wrong_path",
        "wrong_tag",
        "extra_foreign_tag",
        "mode",
        "size",
        "hardlink",
        "symlink",
    ),
)
def test_foreign_cache_tag_rejects_every_retained_path_or_lstat_drift(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
    mutation: str,
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    target = tmp_path / "scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc"
    if mutation == "missing":
        target.unlink()
    elif mutation == "wrong_path":
        wrong_parent = tmp_path / "elsewhere/__pycache__"
        wrong_parent.mkdir(parents=True, mode=0o755)
        target.rename(wrong_parent / target.name)
    elif mutation == "wrong_tag":
        target.rename(target.with_name("admit_wyscout_v5_runtime.cpython-313.pyc"))
    elif mutation == "extra_foreign_tag":
        extra = target.with_name("admit_wyscout_v5_runtime.cpython-313.pyc")
        extra.write_bytes(bytes(190_312))
        extra.chmod(0o644)
    elif mutation == "mode":
        target.chmod(0o600)
    elif mutation == "size":
        target.write_bytes(bytes(190_311))
        target.chmod(0o644)
    elif mutation == "hardlink":
        os.link(target, tmp_path / "foreign-pyc-hardlink")
    else:
        substitute = tmp_path / "foreign-pyc-substitute"
        substitute.write_bytes(bytes(190_312))
        substitute.chmod(0o644)
        target.unlink()
        target.symlink_to(substitute)
    with pytest.raises(error, match="metadata|grammar|missing|regular"):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_foreign_cache_tag_collector_never_opens_reads_or_hashes_pyc(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    target = tmp_path / "scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc"
    original_builtin_open = open
    original_os_open = os.open
    original_path_open = Path.open
    original_path_read_bytes = Path.read_bytes

    def deny_builtin_open(path: Any, *args: Any, **kwargs: Any) -> Any:
        if os.fspath(path) == os.fspath(target):
            raise AssertionError("foreign PYC built-in open attempted")
        return original_builtin_open(path, *args, **kwargs)

    def deny_os_open(path: Any, *args: Any, **kwargs: Any) -> int:
        if os.fspath(path) == os.fspath(target):
            raise AssertionError("foreign PYC os.open attempted")
        return original_os_open(path, *args, **kwargs)

    def deny_path_open(path: Path, *args: Any, **kwargs: Any) -> Any:
        if path == target:
            raise AssertionError("foreign PYC Path.open attempted")
        return original_path_open(path, *args, **kwargs)

    def deny_path_read_bytes(path: Path) -> bytes:
        if path == target:
            raise AssertionError("foreign PYC Path.read_bytes attempted")
        return original_path_read_bytes(path)

    monkeypatch.setattr("builtins.open", deny_builtin_open)
    monkeypatch.setattr(os, "open", deny_os_open)
    monkeypatch.setattr(Path, "open", deny_path_open)
    monkeypatch.setattr(Path, "read_bytes", deny_path_read_bytes)
    row = _inventory_row(collector(tmp_path, policy), path=target.relative_to(tmp_path).as_posix())
    assert row["authority_class"] == "REPOSITORY_FOREIGN_CACHE_TAG_DENIED"
    assert row["source_authority"] is None


def test_new_source_pytest_pyc_is_derived_as_audit_only_by_child_and_launcher(
    tmp_path: Path,
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    source = tmp_path / "tests/test_present.py"
    source.parent.mkdir(parents=True)
    source.write_text("VALUE = 1\n")
    source.chmod(0o644)
    cache = source.parent / "__pycache__"
    cache.mkdir(mode=0o755)
    target = cache / "test_present.cpython-312-pytest-9.1.1.pyc"
    py_compile.compile(os.fspath(source), cfile=os.fspath(target), doraise=True)
    target.chmod(0o644)
    policy["post_w04_audit_only_source_paths"] = ("tests/test_present.py",)
    for collector in (
        launcher._independent_pyc_inventory,
        admission._operational_pyc_inventory,
    ):
        row = _inventory_row(
            collector(tmp_path, policy),
            path=target.relative_to(tmp_path).as_posix(),
        )
        assert row["authority_class"] == "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY"
        assert row["source_path"] == "tests/test_present.py"


def _audit_only_pyc_fixture(root: Path) -> tuple[dict[str, object], tuple[Path, Path, Path]]:
    post_w04_source = root / "src/scouting/contracts/evaluation.py"
    post_w04_source.parent.mkdir(parents=True, exist_ok=True)
    post_w04_source.write_text("VALUE = 1\n")
    post_w04_source.chmod(0o644)
    policy = _minimal_pyc_policy(root)
    repository_cache = root / "src/scouting/contracts/__pycache__"
    repository_cache.mkdir(parents=True, mode=0o755)
    repository_cache.chmod(0o755)
    post_w04 = repository_cache / "evaluation.cpython-312.pyc"
    post_w04.write_bytes(bytes(64))
    post_w04.chmod(0o644)
    unrelated_cache = root / "tests/__pycache__"
    unrelated_cache.mkdir(parents=True, mode=0o755)
    unrelated_cache.chmod(0o755)
    unrelated = unrelated_cache / "unrelated.cpython-313.pyc"
    unrelated.write_bytes(bytes(80))
    unrelated.chmod(0o644)
    retired_cache = root / "tests/integration/__pycache__"
    retired_cache.mkdir(parents=True, mode=0o755)
    retired_cache.chmod(0o755)
    retired = retired_cache / ("test_w10_expert_relevance_evaluation.cpython-312-pytest-9.1.1.pyc")
    retired.write_bytes(bytes(96))
    retired.chmod(0o644)
    return policy, (post_w04, unrelated, retired)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_post_w04_and_unrelated_foreign_cache_rows_are_bounded_audit_only(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy, (post_w04, unrelated, retired) = _audit_only_pyc_fixture(tmp_path)
    rows = collector(tmp_path, policy)
    post_w04_row = _inventory_row(rows, path=post_w04.relative_to(tmp_path).as_posix())
    assert post_w04_row["authority_class"] == "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY"
    assert post_w04_row["authority_scope"] == "AUDIT_ONLY_ZERO_READ_USE"
    assert post_w04_row["denial_policy"] == "POST_W04_SOURCE_CACHE_DENIED_ZERO_READ"
    assert post_w04_row["source_path"] == "src/scouting/contracts/evaluation.py"
    assert post_w04_row["source_authority"] is None
    assert "owner" not in post_w04_row
    assert "sha256" not in post_w04_row

    unrelated_row = _inventory_row(rows, path=unrelated.relative_to(tmp_path).as_posix())
    assert unrelated_row["authority_class"] == "REPOSITORY_FOREIGN_CACHE_TAG_AUDIT_ONLY"
    assert unrelated_row["authority_scope"] == "AUDIT_ONLY_ZERO_READ_USE"
    assert unrelated_row["denial_policy"] == "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ"
    assert unrelated_row["foreign_cache_tag"] == "cpython-313"
    assert unrelated_row["source_path"] == "tests/unrelated.py"
    assert unrelated_row["source_authority"] is None
    assert "source_authority_required" not in unrelated_row
    assert "owner" not in unrelated_row
    assert "sha256" not in unrelated_row

    retired_row = _inventory_row(rows, path=retired.relative_to(tmp_path).as_posix())
    assert retired_row["authority_class"] == "REPOSITORY_RETIRED_POST_W04_CACHE_AUDIT_ONLY"
    assert retired_row["authority_scope"] == "AUDIT_ONLY_ZERO_READ_USE"
    assert retired_row["denial_policy"] == "RETIRED_POST_W04_SOURCE_CACHE_DENIED_ZERO_READ"
    assert retired_row["source_path"] == (
        "tests/integration/test_w10_expert_relevance_evaluation.py"
    )
    assert retired_row["source_authority"] is None
    assert retired_row["source_required_absent"] is True


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_post_w04_audit_only_roster_is_exact_and_not_caller_extensible(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    policy["post_w04_audit_only_source_paths"] = ("tests/test_present.py",)
    with pytest.raises(error, match="audit-only PYC source roster differs"):
        collector(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_post_w04_full_suite_live_caches_are_all_bounded_audit_only(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    examples = (
        ("scripts/build_w10_expert_evidence_v2.py", False),
        ("scripts/evaluate_w09_retrieval.py", False),
        ("src/scouting/data_products/wyscout/expert_evidence.py", False),
        ("src/scouting/data_products/wyscout/historical.py", False),
        ("src/scouting/evaluation/research.py", False),
        ("tests/contracts/test_w10_expert_evidence_v2_contracts.py", True),
        ("tests/e2e/test_w09_research_workbench_playwright.py", True),
        ("tests/integration/test_w09_full_canonical_build.py", True),
        ("tests/security/test_w08_web_security.py", True),
        ("tests/unit/test_w10_expert_evidence_v2.py", True),
        ("tests/unit/test_w09_wyscout_historical_adapter.py", True),
    )
    cache_paths: list[Path] = []
    for source_path, pytest_rewrite in examples:
        source = tmp_path / source_path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("VALUE = 1\n")
        source.chmod(0o644)
        cache = source.parent / "__pycache__"
        cache.mkdir(mode=0o755, exist_ok=True)
        cache.chmod(0o755)
        suffix = "-pytest-9.1.1" if pytest_rewrite else ""
        target = cache / f"{source.stem}.cpython-312{suffix}.pyc"
        py_compile.compile(os.fspath(source), cfile=os.fspath(target), doraise=True)
        target.chmod(0o644)
        cache_paths.append(target)

    policy["post_w04_audit_only_source_paths"] = tuple(
        sorted(source_path for source_path, _ in examples)
    )

    rows = collector(tmp_path, policy)

    stable_paths = frozenset(
        cast(str, row["path"])
        for row in cast(tuple[dict[str, object], ...], policy["source_rows"])
        if row["authority_class"] == "REPOSITORY_CODE_MANIFEST"
    )
    assert admission._derive_post_w04_audit_only_pyc_source_paths(
        tmp_path, stable_paths
    ) == launcher._derive_post_w04_audit_only_pyc_source_paths(tmp_path, stable_paths)
    for target, (source_path, _pytest_rewrite) in zip(cache_paths, examples, strict=True):
        row = _inventory_row(rows, path=target.relative_to(tmp_path).as_posix())
        assert row["authority_class"] == "REPOSITORY_POST_W04_CACHE_AUDIT_ONLY"
        assert row["authority_scope"] == "AUDIT_ONLY_ZERO_READ_USE"
        assert row["denial_policy"] == "POST_W04_SOURCE_CACHE_DENIED_ZERO_READ"
        assert row["source_path"] == source_path
        assert row["source_authority"] is None


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_retired_post_w04_cache_predicate_rejects_substitution(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
) -> None:
    policy = _minimal_pyc_policy(tmp_path)
    predicate = dict(
        cast(
            tuple[dict[str, object], ...],
            policy["post_w04_retired_audit_only_pyc_predicates"],
        )[0]
    )
    predicate["source_path"] = "tests/integration/substituted.py"
    policy["post_w04_retired_audit_only_pyc_predicates"] = (predicate,)
    with pytest.raises(error, match="retired audit-only PYC predicate differs"):
        collector(tmp_path, policy)


def test_child_and_launcher_portable_pyc_projections_exclude_raw_host_metadata(
    tmp_path: Path,
) -> None:
    policy, _targets = _audit_only_pyc_fixture(tmp_path)
    raw = admission._operational_pyc_inventory(tmp_path, policy)
    assert raw == launcher._independent_pyc_inventory(tmp_path, policy)
    changed_rows: list[dict[str, object]] = []
    for row in raw:
        changed = {
            **row,
            "ctime_ns": cast(int, row["ctime_ns"]) + 1,
            "device": cast(int, row["device"]) + 1,
            "inode": cast(int, row["inode"]) + 1,
            "mtime_ns": cast(int, row["mtime_ns"]) + 1,
        }
        if row["entry_kind"] == "CACHE_DIRECTORY":
            changed["link_count"] = cast(int, row["link_count"]) + 1
            changed["size_bytes"] = cast(int, row["size_bytes"]) + 1
        elif row["authority_class"] != "REPOSITORY_FOREIGN_CACHE_TAG_DENIED":
            changed["size_bytes"] = cast(int, row["size_bytes"]) + 1
        changed_rows.append(changed)
    changed_raw = tuple(changed_rows)
    assert changed_raw != raw
    child_projection = admission._pyc_security_projection(raw)
    launcher_projection = launcher._independent_pyc_security_projection(raw)
    assert child_projection == launcher_projection
    assert admission._pyc_security_projection(changed_raw) == child_projection
    assert launcher._independent_pyc_security_projection(changed_raw) == launcher_projection

    protected_index = next(
        index
        for index, row in enumerate(changed_raw)
        if row["authority_class"] == "REPOSITORY_FOREIGN_CACHE_TAG_DENIED"
    )
    protected_changed = list(changed_raw)
    protected_changed[protected_index] = {
        **protected_changed[protected_index],
        "size_bytes": cast(int, protected_changed[protected_index]["size_bytes"]) + 1,
    }
    assert admission._pyc_security_projection(tuple(protected_changed)) != child_projection
    assert (
        launcher._independent_pyc_security_projection(tuple(protected_changed))
        != launcher_projection
    )


def test_raw_pyc_health_is_audit_only_while_portable_security_digest_is_stable(
    tmp_path: Path,
) -> None:
    policy, _targets = _audit_only_pyc_fixture(tmp_path)
    raw = launcher._independent_pyc_inventory(tmp_path, policy)
    changed = tuple(
        {
            **row,
            "device": cast(int, row["device"]) + 1,
            "inode": cast(int, row["inode"]) + 1,
        }
        for row in raw
    )
    first = launcher._pyc_inventory_health(raw)
    second = launcher._pyc_inventory_health(changed)
    assert (
        first["inventory_authority"]
        == second["inventory_authority"]
        == ("AUDIT_ONLY_ZERO_READ_USE")
    )
    assert first["inventory_sha256"] != second["inventory_sha256"]
    assert (
        first["portable_security_projection_sha256"]
        == second["portable_security_projection_sha256"]
    )


def test_outer_retained_snapshot_ignores_raw_host_drift_but_not_security_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    protected = {
        "authority_class": "REPOSITORY_FOREIGN_CACHE_TAG_DENIED",
        "denial_policy": "FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ",
        "entry_kind": "PYC",
        "foreign_cache_tag": "cpython-314",
        "mode": 0o644,
        "path": "scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc",
        "role": "WHOLE_REPOSITORY",
        "size_bytes": 190_312,
        "source_authority": None,
        "source_authority_required": "REPOSITORY_CODE_MANIFEST",
        "source_path": "scripts/admit_wyscout_v5_runtime.py",
        "device": 1,
        "inode": 2,
        "ctime_ns": 3,
        "mtime_ns": 4,
    }
    expected = ("a" * 64, {}, tuple(), (protected,))
    raw_changed = {**protected, "device": 5, "inode": 6, "ctime_ns": 7, "mtime_ns": 8}
    monkeypatch.setattr(
        launcher,
        "_admission_authority_with_pyc",
        lambda _root: ("a" * 64, {}, tuple(), (raw_changed,)),
    )
    launcher._require_outer_authority_snapshot(_PROJECT_ROOT, expected)

    security_changed = {**raw_changed, "size_bytes": 190_311}
    monkeypatch.setattr(
        launcher,
        "_admission_authority_with_pyc",
        lambda _root: ("a" * 64, {}, tuple(), (security_changed,)),
    )
    with pytest.raises(launcher.RuntimeControlError, match="portable PYC security"):
        launcher._require_outer_authority_snapshot(_PROJECT_ROOT, expected)


@pytest.mark.parametrize("mutation", ["creation", "deletion", "content", "header"])
def test_child_and_launcher_pyc_snapshots_detect_inventory_drift(
    tmp_path: Path, mutation: str
) -> None:
    policy, target = _manifested_pyc_fixture(tmp_path)
    launcher_before = launcher._independent_pyc_inventory(tmp_path, policy)
    child_before = admission._operational_pyc_inventory(tmp_path, policy)
    assert launcher_before == child_before
    if mutation == "creation":
        extra = target.parent.parent / "extra/__pycache__"
        extra.mkdir(parents=True, mode=0o755)
    elif mutation == "deletion":
        target.unlink()
    else:
        raw = bytearray(target.read_bytes())
        index = 8 if mutation == "header" else len(raw) - 1
        raw[index] ^= 1
        target.write_bytes(raw)
        target.chmod(0o644)
    assert launcher._independent_pyc_inventory(tmp_path, policy) != launcher_before
    assert admission._operational_pyc_inventory(tmp_path, policy) != child_before


@pytest.mark.parametrize("mutation", ["mode", "link"])
def test_child_and_launcher_pyc_census_rejects_mode_and_link_drift(
    tmp_path: Path, mutation: str
) -> None:
    policy, target = _manifested_pyc_fixture(tmp_path)
    if mutation == "mode":
        target.chmod(0o600)
    else:
        substitute = tmp_path / "substitute.bin"
        substitute.write_bytes(target.read_bytes())
        substitute.chmod(0o644)
        target.unlink()
        target.symlink_to(substitute)
    with pytest.raises(launcher.RuntimeControlError, match="regular|metadata"):
        launcher._independent_pyc_inventory(tmp_path, policy)
    with pytest.raises(admission.AdmissionError, match="lstat metadata"):
        admission._operational_pyc_inventory(tmp_path, policy)


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_cache_directory_row_binds_one_complete_no_follow_lstat_snapshot(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy, cache = _empty_cache_directory_fixture(tmp_path)
    metadata = os.lstat(cache)
    rows = collector(tmp_path, policy)
    assert _inventory_row(rows, path="tests/__pycache__") == {
        "ctime_ns": metadata.st_ctime_ns,
        "device": metadata.st_dev,
        "entry_kind": "CACHE_DIRECTORY",
        "inode": metadata.st_ino,
        "link_count": metadata.st_nlink,
        "mode": 0o755,
        "mtime_ns": metadata.st_mtime_ns,
        "path": "tests/__pycache__",
        "role": "WHOLE_REPOSITORY",
        "size_bytes": metadata.st_size,
    }


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_cache_directory_inventory_detects_same_path_mode_0755_replacement(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy, cache = _empty_cache_directory_fixture(tmp_path)
    before = collector(tmp_path, policy)
    parked = tmp_path / ".venv/replaced-cache-directory"
    cache.rename(parked)
    cache.mkdir(mode=0o755)
    cache.chmod(0o755)
    after = collector(tmp_path, policy)
    before_row = _inventory_row(before, path="tests/__pycache__")
    after_row = _inventory_row(after, path="tests/__pycache__")
    assert before_row["mode"] == after_row["mode"] == 0o755
    assert before_row["inode"] != after_row["inode"]
    assert before != after


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_cache_directory_inventory_detects_same_inode_clock_drift(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy, cache = _empty_cache_directory_fixture(tmp_path)
    before = collector(tmp_path, policy)
    metadata = os.lstat(cache)
    os.utime(
        cache,
        ns=(metadata.st_atime_ns, metadata.st_mtime_ns + 1_000_000_000),
        follow_symlinks=False,
    )
    after = collector(tmp_path, policy)
    before_row = _inventory_row(before, path="tests/__pycache__")
    after_row = _inventory_row(after, path="tests/__pycache__")
    assert before_row["inode"] == after_row["inode"]
    assert before_row["mtime_ns"] != after_row["mtime_ns"]
    assert before != after


@pytest.mark.parametrize(
    ("_collector_role", "collector", "_error"),
    _PYC_INVENTORY_COLLECTORS,
)
def test_cache_directory_inventory_detects_link_count_size_and_entry_drift(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    _error: type[Exception],
) -> None:
    policy, cache = _empty_cache_directory_fixture(tmp_path)
    before = collector(tmp_path, policy)
    (cache / "entry").mkdir(mode=0o755)
    after = collector(tmp_path, policy)
    before_row = _inventory_row(before, path="tests/__pycache__")
    after_row = _inventory_row(after, path="tests/__pycache__")
    assert before_row["link_count"] != after_row["link_count"]
    assert before_row["size_bytes"] != after_row["size_bytes"]
    assert before != after


@pytest.mark.parametrize(
    ("_collector_role", "collector", "error"),
    _PYC_INVENTORY_COLLECTORS,
)
@pytest.mark.parametrize("mutation", ["link", "mode"])
def test_cache_directory_inventory_rejects_link_and_mode_attacks(
    tmp_path: Path,
    _collector_role: str,
    collector: Any,
    error: type[Exception],
    mutation: str,
) -> None:
    policy, cache = _empty_cache_directory_fixture(tmp_path)
    if mutation == "mode":
        cache.chmod(0o700)
    else:
        parked = tmp_path / ".venv/linked-cache-directory"
        cache.rename(parked)
        cache.symlink_to(parked, target_is_directory=True)
    with pytest.raises(error, match="directory symlink|cache-directory metadata"):
        collector(tmp_path, policy)


def test_child_pyc_census_is_lstat_only_and_does_not_share_launcher_collector() -> None:
    child_source = (_PROJECT_ROOT / "scripts/admit_wyscout_v5_runtime.py").read_text()
    child_body = child_source.split("def _operational_pyc_inventory(", 1)[1].split(
        "def _collect_stable_authority_with_pyc(", 1
    )[0]
    assert "_guard_read_absolute_regular" not in child_body
    assert "os.open(" not in child_body
    assert "read_bytes(" not in child_body
    assert "_sha256(" not in child_body
    assert "MAGIC_NUMBER" not in child_body
    assert "_independent_pyc_inventory" not in child_source
    assert "_independent_pyc_security_projection" not in child_source
    for mutation_token in ("os.unlink", ".unlink(", ".rename(", "os.rename", "os.replace"):
        assert mutation_token not in child_body

    launcher_source = (_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_text()
    launcher_body = launcher_source.split("def _independent_pyc_inventory(", 1)[1].split(
        "def _independent_stdlib_rows(", 1
    )[0]
    assert "_absolute_regular" not in launcher_body
    assert "os.open(" not in launcher_body
    assert "read_bytes(" not in launcher_body
    assert "_sha256(" not in launcher_body
    assert "MAGIC_NUMBER" not in launcher_body
    assert "raw[" not in launcher_body
    assert "def _pyc_security_projection" not in launcher_source
    for mutation_token in ("os.unlink", ".unlink(", ".rename(", "os.rename", "os.replace"):
        assert mutation_token not in launcher_body


def test_launcher_pyc_census_has_exact_child_rows_and_zero_pyc_open_events(
    tmp_path: Path,
) -> None:
    policy, _target = _manifested_pyc_fixture(tmp_path)
    site = tmp_path / ".venv/lib/python3.12/site-packages"
    site_source = site / "r8_present.py"
    site_source.write_text("VALUE = 2\n")
    site_source.chmod(0o644)
    site_cache = site / "__pycache__"
    site_cache.mkdir(mode=0o755)
    site_cache.chmod(0o755)
    site_target = site_cache / "r8_present.cpython-312.pyc"
    py_compile.compile(os.fspath(site_source), cfile=os.fspath(site_target), doraise=True)
    site_target.chmod(0o644)
    policy["source_rows"] = (
        *cast(tuple[dict[str, object], ...], policy["source_rows"]),
        {
            "authority_class": "SELECTED_DISTRIBUTION_RECORD",
            "path": "r8_present.py",
        },
    )
    assert launcher._independent_pyc_inventory(
        tmp_path, policy
    ) == admission._operational_pyc_inventory(tmp_path, policy)
    code = f"""
import importlib.util
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location(
    'w04_r8_launcher',
    {os.fspath(_PROJECT_ROOT / "scripts/launch_wyscout_v5.py")!r},
)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
pyc_open_events = []
def guard(event, arguments):
    if event == 'open' and arguments:
        target = arguments[0]
        if type(target) is bytes:
            target = target.decode('utf-8', errors='strict')
        if type(target) is str and target.endswith(('.pyc', '.pyo')):
            pyc_open_events.append(target)
            raise RuntimeError('outer guard denied in-place bytecode access')
sys.addaudithook(guard)
rows = module._independent_pyc_inventory(Path({os.fspath(tmp_path)!r}), {policy!r})
if pyc_open_events or len([row for row in rows if row['entry_kind'] == 'PYC']) != 3:
    raise RuntimeError('R8 metadata-only PYC audit proof differs')
print('R8_METADATA_ONLY_PYC_PASS')
"""
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONPYCACHEPREFIX"] = os.fspath(tmp_path / "subprocess-pycache")
    completed = subprocess.run(  # noqa: S603  # nosec B603
        (sys.executable, "-B", "-c", code),
        env=environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    assert completed.stdout == b"R8_METADATA_ONLY_PYC_PASS\n"
    assert completed.stderr == b""


def test_wrapper_digest_mutation_is_rejected_by_retained_reconstruction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    closure = launcher._independent_lock_rows(_PROJECT_ROOT)
    installed = launcher._independent_installed_rows(_PROJECT_ROOT, closure)
    changed = dict(launcher._WRAPPER_AUTHORITY)
    alias, _digest, size = changed["bandit"]
    changed["bandit"] = (alias, "0" * 64, size)
    monkeypatch.setattr(launcher, "_WRAPPER_AUTHORITY", changed)
    with pytest.raises(launcher.RuntimeControlError, match="normalized wrapper"):
        launcher._independent_stable_records(_PROJECT_ROOT, installed)


def test_actual_admission_is_two_run_deterministic_idempotent_and_no_rebuild(
    tmp_path: Path,
) -> None:
    roots = _runtime_roots(tmp_path)
    real_code_root = _PROJECT_ROOT / "data/manifests/wyscout/v5/code"
    real_admission_root = _PROJECT_ROOT / "data/working/wyscout/v5/.staging/admission"
    before = (real_code_root.exists(), real_admission_root.exists())
    first_run_id = str(uuid4())
    second_run_id = str(uuid4())
    first_admission_id = str(uuid4())
    second_admission_id = str(uuid4())

    first = launcher.prepare_wyscout_v5_launch(
        project_root=_PROJECT_ROOT,
        roots=roots,
        run_id=first_run_id,
        admission_run_id=first_admission_id,
        timeout=60,
    )
    manifest = (
        roots.manifest_final_root / "code" / f"{first.code_manifest_sha256}.code-manifest.json"
    )
    first_identity = (manifest.stat().st_dev, manifest.stat().st_ino)
    second = launcher.prepare_wyscout_v5_launch(
        project_root=_PROJECT_ROOT,
        roots=roots,
        run_id=second_run_id,
        admission_run_id=second_admission_id,
        timeout=60,
    )

    assert first.build_id == second.build_id
    assert first.code_manifest_id == second.code_manifest_id
    assert first.code_manifest_sha256 == second.code_manifest_sha256
    assert first.invocation == second.invocation
    assert first.run_id != second.run_id
    assert first.rebuild_prefix_relative_path != second.rebuild_prefix_relative_path
    assert first.rebuild_receipt_relative_path != second.rebuild_receipt_relative_path
    assert (manifest.stat().st_dev, manifest.stat().st_ino) == first_identity
    assert stat.S_IMODE(manifest.stat().st_mode) == 0o600
    assert manifest.stat().st_nlink == 1
    assert tuple((roots.manifest_final_root / "code").iterdir()) == (manifest,)
    assert tuple(roots.manifest_staging_root.rglob("*.partial")) == ()
    assert before == (real_code_root.exists(), real_admission_root.exists())
    assert (_PROJECT_ROOT / launcher.REBUILD_ARGV[-1]).is_file()
    assert not any(roots.pycache_staging_root.glob(f"{first.build_id}/*/runtime-pycache"))
    assert first.rebuild_argv == launcher.REBUILD_ARGV

    contracts, _publication = launcher._runtime_contracts(_PROJECT_ROOT)
    projection = contracts.projection_from_invocation(first.invocation)
    assert contracts.build_id_for_projection(projection) == first.build_id
    assert contracts.invocation_from_projection(projection) == first.invocation
    assert len(projection.model_dump()) == 25
    assert len(first.invocation.model_dump()) == 25
    assert projection.product_contract_digest == launcher.PRODUCT_CONTRACT_V2_LOGICAL_SHA256
    assert projection.schema_bundle_digest == launcher.SCHEMA_BUNDLE_V2_LOGICAL_SHA256
    assert first.layer_manifest_relative_paths == tuple(
        contracts.layer_manifest_path(layer, first.build_id)
        for layer in ("BRONZE", "SILVER", "GOLD")
    )

    decoded = launcher._load_canonical_json(manifest.read_bytes())
    assert type(decoded) is dict
    stable = cast(dict[str, object], decoded)
    assert stable["schema_version"] == launcher.MANIFEST_SCHEMA_VERSION
    assert stable["environment_digest"] == first.invocation.environment_digest
    assert stable["local_resource_digest"] == first.invocation.local_resource_digest
    assert stable["selected_lock_closure_digest"] == (first.invocation.selected_lock_closure_digest)
    assert len(stable) == 23


def test_actual_admission_rejects_repository_identity_substitution(tmp_path: Path) -> None:
    roots = _runtime_roots(tmp_path)
    admission_run_id = str(uuid4())
    prefix = launcher._create_empty_prefix(
        roots.pycache_staging_root,
        "PRE_BUILD_ADMISSION",
        admission_run_id,
        None,
    )
    prefix_relative = (
        "data/working/wyscout/v5/.staging/admission/"
        f"admission_run_id={admission_run_id}/runtime-pycache"
    )
    inputs = launcher._admission_inputs(admission_run_id, prefix_relative, "0" * 64)
    with pytest.raises(launcher.ChildProcessError, match="exited 2"):
        launcher._run_child(
            project_root=_PROJECT_ROOT,
            argv=launcher.ADMISSION_ARGV,
            role="PRE_BUILD_ADMISSION",
            inputs=inputs,
            expected_repository_code_sha256="0" * 64,
            pycache_prefix=prefix,
            timeout=60,
        )
    assert tuple(prefix.iterdir()) == ()


def test_immutable_existing_manifest_conflict_is_not_repaired(tmp_path: Path) -> None:
    roots = _runtime_roots(tmp_path)
    first = launcher.prepare_wyscout_v5_launch(
        project_root=_PROJECT_ROOT,
        roots=roots,
        run_id=str(uuid4()),
        admission_run_id=str(uuid4()),
        timeout=60,
    )
    manifest = (
        roots.manifest_final_root / "code" / f"{first.code_manifest_sha256}.code-manifest.json"
    )
    original_size = manifest.stat().st_size
    manifest.write_bytes(b"x" * original_size)
    manifest.chmod(0o600)
    with pytest.raises(Exception, match="immutable final conflicts|readback differs"):
        launcher.prepare_wyscout_v5_launch(
            project_root=_PROJECT_ROOT,
            roots=roots,
            run_id=str(uuid4()),
            admission_run_id=str(uuid4()),
            timeout=60,
        )
    assert manifest.read_bytes() == b"x" * original_size


def _retained_outer_bootstrap(tmp_path: Path) -> tuple[dict[str, object], int]:
    descriptor = os.open(
        _PROJECT_ROOT / "scripts/launch_wyscout_v5.py", os.O_RDONLY | os.O_NOFOLLOW
    )
    os.set_inheritable(descriptor, False)
    metadata = os.fstat(descriptor)
    control = _directory(tmp_path / "control-prefix")
    control_metadata = os.stat(control, follow_symlinks=False)
    raw = os.pread(descriptor, metadata.st_size, 0)
    bootstrap_tuple = launcher._outer_bootstrap_tuple(
        project_root=_PROJECT_ROOT,
        launcher_sha256=hashlib.sha256(raw).hexdigest(),
        launcher_size=len(raw),
    )
    return (
        {
            "bootstrap_tuple": bootstrap_tuple,
            "control_identity": (
                control_metadata.st_dev,
                control_metadata.st_ino,
                control_metadata.st_mode,
                control_metadata.st_nlink,
            ),
            "control_prefix": os.fspath(control),
            "control_run_id": str(uuid4()),
            "environment_sha256": "e" * 64,
            "launcher_identity": (
                metadata.st_dev,
                metadata.st_ino,
                metadata.st_mode,
                metadata.st_nlink,
                metadata.st_size,
            ),
            "launcher_sha256": hashlib.sha256(raw).hexdigest(),
            "launcher_source_fd": descriptor,
            "project_root": os.fspath(_PROJECT_ROOT),
        },
        descriptor,
    )


def test_complete_outer_bootstrap_tuple_is_independently_reconstructed() -> None:
    launcher_raw = (_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_bytes()
    launcher_tuple = launcher._outer_bootstrap_tuple(
        project_root=_PROJECT_ROOT,
        launcher_sha256=hashlib.sha256(launcher_raw).hexdigest(),
        launcher_size=len(launcher_raw),
    )
    child_tuple = admission._bootstrap_tuple(_PROJECT_ROOT)
    assert launcher_tuple == child_tuple
    canonical_tuple = json.loads(launcher._canonical_json_bytes(launcher_tuple))
    assert tuple(canonical_tuple) == tuple(sorted(canonical_tuple))
    assert len(launcher_tuple) == 34
    assert launcher_tuple["working_directory"] == "<W04_PROJECT_ROOT>"
    assert launcher_tuple["uv_final_entry_kind"] == "regular_non_symlink_executable"
    assert launcher.OUTER_ARGV == (
        "uv",
        "run",
        "--locked",
        "--no-sync",
        "python",
        "-S",
        "-B",
        "scripts/launch_wyscout_v5.py",
    )
    assert hashlib.sha256(launcher._canonical_json_bytes(launcher_tuple)).hexdigest() == (
        admission._bootstrap_tuple_sha256(_PROJECT_ROOT)
    )


def test_master_transport_uses_open_descriptor_without_path_reopen(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    descriptor = os.open(
        _PROJECT_ROOT / "scripts/launch_wyscout_v5.py", os.O_RDONLY | os.O_NOFOLLOW
    )
    os.set_inheritable(descriptor, True)
    control = _directory(tmp_path / "control")
    original = launcher._guard_read_relative
    monkeypatch.setattr(
        launcher,
        "_guard_read_relative",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("path reopen")),
    )
    try:
        environment, bootstrap = launcher.outer_bootstrap_transport(
            project_root=_PROJECT_ROOT,
            control_prefix=control,
            launcher_source_fd=descriptor,
        )
    finally:
        os.close(descriptor)
        monkeypatch.setattr(launcher, "_guard_read_relative", original)
    assert environment["UV_RUN_RECURSION_DEPTH"] == "0"
    assert environment["PATH"] == "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
    assert (
        bootstrap["launcher_sha256"]
        == hashlib.sha256((_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_bytes()).hexdigest()
    )


def test_retained_outer_descriptor_and_control_prefix_reject_drift(
    tmp_path: Path,
) -> None:
    bootstrap, descriptor = _retained_outer_bootstrap(tmp_path)
    try:
        launcher._recheck_outer_bootstrap(bootstrap)
        os.lseek(descriptor, 1, os.SEEK_SET)
        with pytest.raises(launcher.RuntimeControlError, match="descriptor drifted"):
            launcher._recheck_outer_bootstrap(bootstrap)
        os.lseek(descriptor, 0, os.SEEK_SET)
        os.set_inheritable(descriptor, True)
        with pytest.raises(launcher.RuntimeControlError, match="descriptor drifted"):
            launcher._recheck_outer_bootstrap(bootstrap)
        os.set_inheritable(descriptor, False)
        control = Path(cast(str, bootstrap["control_prefix"]))
        (control / "attacker").write_bytes(b"x")
        with pytest.raises(launcher.RuntimeControlError, match="nonempty"):
            launcher._recheck_outer_bootstrap(bootstrap)
    finally:
        os.close(descriptor)


def test_outer_runtime_roots_are_exact_and_admission_run_scoped(tmp_path: Path) -> None:
    admission_run_id = str(uuid4())
    roots = launcher._outer_runtime_roots(tmp_path, admission_run_id)
    assert roots.manifest_final_root == tmp_path / "data/manifests/wyscout/v5"
    assert roots.pycache_staging_root == tmp_path / "data/working/wyscout/v5/.staging"
    assert roots.manifest_staging_root == (
        roots.pycache_staging_root
        / "admission"
        / f"admission_run_id={admission_run_id}"
        / "manifest-staging"
    )


def test_outer_control_full_orchestration_isolated_and_canonical(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap, descriptor = _retained_outer_bootstrap(tmp_path)
    control_run_id = cast(str, bootstrap["control_run_id"])
    admission_run_id = str(uuid4())
    run_id = str(uuid4())
    sampled = iter((UUID(admission_run_id), UUID(run_id)))
    monkeypatch.setattr(launcher, "uuid4", lambda: next(sampled))
    isolated = _runtime_roots(tmp_path / "isolated")
    monkeypatch.setattr(launcher, "_outer_runtime_roots", lambda *_args: isolated)
    pyc_row: dict[str, object] = {
        "authority_class": "REPOSITORY_NORMAL",
        "entry_kind": "PYC",
        "role": "WHOLE_REPOSITORY",
    }
    authority: tuple[str, dict[str, object], tuple[int, ...], tuple[dict[str, object], ...]] = (
        "a" * 64,
        {},
        tuple(),
        (pyc_row,),
    )
    monkeypatch.setattr(launcher, "_admission_authority_with_pyc", lambda _root: authority)
    build_id = "b" * 64
    code_digest = "c" * 64
    receipt_digest = "d" * 64
    admission_evidence = _synthetic_process_evidence("PRE_BUILD_ADMISSION")
    rebuild_evidence = _synthetic_process_evidence("POST_BUILD_ID_REBUILD")
    runtime_row: dict[str, object] = {
        "observation_kind": "MODULE_SOURCE",
        "owner_name": "demo",
        "owner_version": "1.0",
        "site_relative_path": "demo.py",
        "subject_name": "demo",
    }
    runtime_digest = launcher._sha256_json(
        {"algorithm": launcher.RUNTIME_SUBSET_ALGORITHM, "rows": [runtime_row]}
    )
    plan = SimpleNamespace(
        admission_process_evidence=admission_evidence,
        build_id=build_id,
        code_manifest_sha256=code_digest,
        rebuild_receipt_relative_path=f"runs/w04/{build_id}/{run_id}/receipt.json",
    )

    def prepare(**kwargs: object) -> object:
        assert kwargs["project_root"] == _PROJECT_ROOT
        assert kwargs["admission_run_id"] == admission_run_id
        assert kwargs["run_id"] == run_id
        prefix = (
            isolated.pycache_staging_root
            / "admission"
            / f"admission_run_id={admission_run_id}"
            / "runtime-pycache"
        )
        _directory(prefix)
        _directory(isolated.manifest_staging_root)
        return plan

    def rebuild(**kwargs: object) -> object:
        assert kwargs["plan"] is plan
        _directory(isolated.pycache_staging_root / build_id / run_id / "runtime-pycache")
        receipt = SimpleNamespace(sha256=receipt_digest)
        final_recheck = SimpleNamespace(
            runtime_subset_digest=runtime_digest,
            runtime_subset_rows=(_RuntimeRowStub(runtime_row),),
        )

        class EnvelopeStub:
            result = SimpleNamespace(rebuild_receipt=receipt, final_recheck=final_recheck)

            def model_dump(self, *, mode: str) -> dict[str, object]:
                assert mode == "json"
                return cast(dict[str, object], json.loads(rebuild_evidence.payload_bytes))

        envelope = EnvelopeStub()
        return SimpleNamespace(
            envelope=envelope,
            process_evidence=rebuild_evidence,
        )

    monkeypatch.setattr(launcher, "prepare_wyscout_v5_launch", prepare)
    monkeypatch.setattr(launcher, "execute_rebuild_child", rebuild)
    try:
        status_raw = launcher._execute_outer_control(bootstrap)
    finally:
        os.close(descriptor)
    status = json.loads(status_raw)
    assert launcher._canonical_json_bytes(status) == status_raw
    assert status == {
        "admission_run_id": admission_run_id,
        "build_id": build_id,
        "child_process_observations": [
            admission_evidence.validate(),
            rebuild_evidence.validate(),
        ],
        "code_manifest_sha256": code_digest,
        "control_run_id": control_run_id,
        "outer_transport_environment_sha256": "e" * 64,
        "pyc_inventory_health": {
            "authority_class_counts": {"REPOSITORY_NORMAL": 1},
            "entry_kind_counts": {"PYC": 1},
            "inventory_authority": "AUDIT_ONLY_ZERO_READ_USE",
            "inventory_sha256": hashlib.sha256(
                launcher._canonical_json_bytes((pyc_row,))
            ).hexdigest(),
            "portable_security_projection_sha256": launcher._sha256_json(
                launcher._independent_pyc_security_projection((pyc_row,))
            ),
            "role_counts": {"WHOLE_REPOSITORY": 1},
            "row_count": 1,
        },
        "rebuild_receipt_relative_path": plan.rebuild_receipt_relative_path,
        "rebuild_receipt_sha256": receipt_digest,
        "run_id": run_id,
        "runtime_subset_digest": runtime_digest,
        "runtime_subset_rows": [runtime_row],
        "schema_version": "w04-local-control-completion-v2",
        "status": "COMPLETE",
    }


def test_outer_control_child_failure_emits_no_completion(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap, descriptor = _retained_outer_bootstrap(tmp_path)
    sampled = iter((uuid4(), uuid4()))
    monkeypatch.setattr(launcher, "uuid4", lambda: next(sampled))
    monkeypatch.setattr(
        launcher,
        "_admission_authority_with_pyc",
        lambda _root: ("a" * 64, {}, tuple(), tuple()),
    )
    monkeypatch.setattr(
        launcher,
        "prepare_wyscout_v5_launch",
        lambda **_kwargs: (_ for _ in ()).throw(launcher.ChildProcessError("child failed")),
    )
    try:
        with pytest.raises(launcher.ChildProcessError, match="child failed"):
            launcher._execute_outer_control(bootstrap)
    finally:
        os.close(descriptor)


def test_outer_control_rejects_cwd_and_uuid_replay(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    bootstrap, descriptor = _retained_outer_bootstrap(tmp_path)
    changed = dict(bootstrap)
    changed["project_root"] = os.fspath(tmp_path)
    try:
        with pytest.raises(launcher.RuntimeControlError, match="cwd differs"):
            launcher._execute_outer_control(changed)
        monkeypatch.setattr(
            launcher,
            "_admission_authority_with_pyc",
            lambda _root: ("a" * 64, {}, tuple(), tuple()),
        )
        replayed = UUID(cast(str, bootstrap["control_run_id"]))
        monkeypatch.setattr(launcher, "uuid4", lambda: replayed)
        with pytest.raises(launcher.RuntimeControlError, match="distinct UUIDv4"):
            launcher._execute_outer_control(bootstrap)
    finally:
        os.close(descriptor)


def _inject_outer_bootstrap_attack(launcher_path: Path, lines: tuple[str, ...]) -> None:
    marker = b"    try:\n        _W04_EARLY_BOOTSTRAP = _w04_early_bootstrap()\n"
    raw = launcher_path.read_bytes()
    assert raw.count(marker) == 1
    injection = "".join(f"    {line}\n" for line in lines).encode()
    launcher_path.write_bytes(raw.replace(marker, injection + marker, 1))
    launcher_path.chmod(0o644)


def _fake_encoding_stdlib(tmp_path: Path, *, encodings_link: bool = False) -> Path:
    base_prefix = _directory(tmp_path / "fake-python")
    library = _directory(base_prefix / "lib")
    stdlib = _directory(library / "python3.12")
    stdlib.chmod(0o755)
    source_root = Path(sys.base_prefix) / "lib/python3.12/encodings"
    encodings = stdlib / "encodings"
    if encodings_link:
        encodings.symlink_to(source_root, target_is_directory=True)
    else:
        encodings.mkdir(mode=0o755)
        encodings.chmod(0o755)
        for name in ("__init__.py", "aliases.py", "utf_8.py"):
            target = encodings / name
            target.write_bytes((source_root / name).read_bytes())
            target.chmod(0o644)
    return base_prefix


def _encoding_origin_attack(base_prefix: Path) -> tuple[str, ...]:
    return (
        "_w04_attack_system = __import__('sys')",
        "_w04_attack_posix = __import__('posix')",
        f"_w04_attack_system.base_prefix = {os.fspath(base_prefix)!r}",
        "_w04_attack_control = _w04_attack_posix.environ[b'PYTHONPYCACHEPREFIX'].decode('utf-8')",
        "for _w04_attack_name, _w04_attack_relative in "
        "(('_frozen_importlib_external', 'importlib/_bootstrap_external.py'), "
        "('zipimport', 'zipimport.py'), ('codecs', 'codecs.py'), "
        "('abc', 'abc.py'), ('io', 'io.py')):",
        "    _w04_attack_system.modules[_w04_attack_name].__file__ = "
        "(_w04_attack_system.base_prefix + '/lib/python3.12/' + _w04_attack_relative)",
        "for _w04_attack_name, _w04_attack_leaf in "
        "(('encodings', '__init__.py'), ('encodings.aliases', 'aliases.py'), "
        "('encodings.utf_8', 'utf_8.py')):",
        "    _w04_attack_source = (_w04_attack_system.base_prefix + "
        "'/lib/python3.12/encodings/' + _w04_attack_leaf)",
        "    _w04_attack_module = _w04_attack_system.modules[_w04_attack_name]",
        "    _w04_attack_module.__spec__.origin = _w04_attack_source",
        "    _w04_attack_module.__spec__.loader.path = _w04_attack_source",
        "    _w04_attack_module.__spec__._cached = "
        "(_w04_attack_control + _w04_attack_source[:-3] + '.cpython-312.pyc')",
        "    _w04_attack_module.__file__ = _w04_attack_source",
        "    _w04_attack_module.__cached__ = _w04_attack_module.__spec__.cached",
        "_w04_attack_system.modules['encodings'].__spec__.submodule_search_locations = "
        "[_w04_attack_system.base_prefix + '/lib/python3.12/encodings']",
    )


def _inject_outer_runtime_probe(launcher_path: Path, lines: tuple[str, ...]) -> None:
    marker = b'\nif __name__ == "__main__":\n    try:\n        raise SystemExit(main())\n'
    raw = launcher_path.read_bytes()
    assert raw.count(marker) == 1
    injection = ("\n".join(lines) + "\n").encode()
    launcher_path.write_bytes(raw.replace(marker, b"\n" + injection + marker[1:], 1))
    launcher_path.chmod(0o644)


def _isolated_outer_probe(
    tmp_path: Path, *, mutation: str | None = None
) -> subprocess.CompletedProcess[bytes]:
    root = _directory(tmp_path / "outer-probe")
    scripts = _directory(root / "scripts")
    launcher_path = scripts / "launch_wyscout_v5.py"
    launcher_path.write_bytes((_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_bytes())
    launcher_path.chmod(0o644)
    for name in ("pyproject.toml", "uv.lock"):
        target = root / name
        target.write_bytes((_PROJECT_ROOT / name).read_bytes())
        target.chmod(0o644)
    venv = _directory(root / ".venv")
    (venv / "pyvenv.cfg").write_bytes((_PROJECT_ROOT / ".venv/pyvenv.cfg").read_bytes())
    bin_root = _directory(venv / "bin")
    physical = Path(cast(str, getattr(sys, "_base_executable")))
    (bin_root / "python").symlink_to(physical)
    (bin_root / "python3").symlink_to("python")
    (bin_root / "python3.12").symlink_to("python")
    control_run_id = str(uuid4())
    control = _directory(
        root
        / "data/working/wyscout/v5/.staging/control"
        / f"control_run_id={control_run_id}"
        / "runtime-pycache"
    )
    if mutation == "fourth_file_backed_module":
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                "_w04_attack_module = type(_w04_attack_system)('w04_extra')",
                "_w04_attack_spec = type('_W04AttackSpec', (), {})()",
                "_w04_attack_spec.origin = '/tmp/w04-extra.py'",
                "_w04_attack_module.__spec__ = _w04_attack_spec",
                "_w04_attack_module.__file__ = '/tmp/w04-extra.py'",
                "_w04_attack_system.modules['w04_extra'] = _w04_attack_module",
            ),
        )
    elif mutation in {
        "disguised_builtin_file",
        "disguised_builtin_no_file",
        "forged_frozen",
    }:
        origin = "frozen" if mutation == "forged_frozen" else "built-in"
        attack_file = "'/tmp/w04-disguised.py'" if mutation == "disguised_builtin_file" else "None"
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                "_w04_attack_module = type(_w04_attack_system)('w04_disguised')",
                "_w04_attack_spec = type('_W04AttackSpec', (), {})()",
                f"_w04_attack_spec.origin = {origin!r}",
                "_w04_attack_spec.name = 'w04_disguised'",
                "_w04_attack_spec.loader = "
                f"_w04_attack_system.modules['_frozen_importlib']."
                f"{'FrozenImporter' if mutation == 'forged_frozen' else 'BuiltinImporter'}",
                "_w04_attack_module.__spec__ = _w04_attack_spec",
                f"_w04_attack_module.__file__ = {attack_file}",
                "_w04_attack_module.__cached__ = None",
                "_w04_attack_system.modules['w04_disguised'] = _w04_attack_module",
            ),
        )
    elif mutation == "unregistered_builtin_alias":
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                "_w04_attack_system.modules['w04_time_alias'] = _w04_attack_system.modules['time']",
            ),
        )
    elif mutation in {"registered_builtin_replacement", "registered_frozen_replacement"}:
        frozen = mutation == "registered_frozen_replacement"
        module_name = "abc" if frozen else "time"
        importer_name = "FrozenImporter" if frozen else "BuiltinImporter"
        origin = "frozen" if frozen else "built-in"
        replacement_file = (
            "_w04_attack_system.base_prefix + '/lib/python3.12/abc.py'" if frozen else "None"
        )
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                f"_w04_attack_original = _w04_attack_system.modules[{module_name!r}]",
                f"_w04_attack_module = type(_w04_attack_system)({module_name!r})",
                f"_w04_attack_loader = _w04_attack_system.modules['_frozen_importlib']."
                f"{importer_name}",
                "_w04_attack_spec = type(_w04_attack_original.__spec__)("
                f"{module_name!r}, _w04_attack_loader, origin={origin!r})",
                "_w04_attack_module.__spec__ = _w04_attack_spec",
                "_w04_attack_module.__loader__ = _w04_attack_loader",
                "_w04_attack_module.__package__ = ''",
                f"_w04_attack_module.__file__ = {replacement_file}",
                "_w04_attack_module.__cached__ = None",
                f"_w04_attack_system.modules[{module_name!r}] = _w04_attack_module",
            ),
        )
    elif mutation in {
        "builtin_package",
        "builtin_parent",
        "builtin_locations",
        "frozen_package",
        "frozen_parent",
        "frozen_locations",
    }:
        frozen = mutation.startswith("frozen_")
        field = mutation.split("_", 1)[1]
        module_name = "abc" if frozen else "time"
        importer_name = "FrozenImporter" if frozen else "BuiltinImporter"
        origin = "frozen" if frozen else "built-in"
        attack_lines = [
            "_w04_attack_system = __import__('sys')",
            f"_w04_attack_module = _w04_attack_system.modules[{module_name!r}]",
        ]
        if field == "package":
            attack_lines.append("_w04_attack_module.__package__ = 'w04.attacker'")
        else:
            parent = "'w04.attacker'" if field == "parent" else "''"
            locations = "None" if field == "parent" else "[]"
            attack_lines.extend(
                (
                    "_w04_attack_spec = type('_W04AttackSpec', (), {})()",
                    f"_w04_attack_spec.name = {module_name!r}",
                    f"_w04_attack_spec.origin = {origin!r}",
                    "_w04_attack_spec.loader = "
                    f"_w04_attack_system.modules['_frozen_importlib'].{importer_name}",
                    "_w04_attack_spec.cached = None",
                    "_w04_attack_spec.has_location = False",
                    f"_w04_attack_spec.parent = {parent}",
                    f"_w04_attack_spec.submodule_search_locations = {locations}",
                    "_w04_attack_module.__spec__ = _w04_attack_spec",
                )
            )
        _inject_outer_bootstrap_attack(launcher_path, tuple(attack_lines))
    elif mutation in {"builtin_importer_authority", "frozen_importer_authority"}:
        importer_name = (
            "FrozenImporter" if mutation == "frozen_importer_authority" else "BuiltinImporter"
        )
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                f"_w04_attack_system.modules['_frozen_importlib'].{importer_name} = "
                "type('_W04AttackImporter', (), {})",
            ),
        )
    elif mutation in {
        "builtin_loader",
        "frozen_loader",
        "frozen_file",
        "frozen_cached",
        "encoding_loader",
        "encoding_spec",
        "encoding_cached",
    }:
        attack_lines = ["_w04_attack_system = __import__('sys')"]
        if mutation == "builtin_loader":
            attack_lines.append("_w04_attack_system.modules['time'].__spec__.loader = None")
        elif mutation == "frozen_loader":
            attack_lines.append("_w04_attack_system.modules['abc'].__loader__ = None")
        elif mutation == "frozen_file":
            attack_lines.append("_w04_attack_system.modules['abc'].__file__ = '/tmp/abc.py'")
        elif mutation == "frozen_cached":
            attack_lines.append("_w04_attack_system.modules['abc'].__cached__ = '/tmp/abc.pyc'")
        elif mutation == "encoding_loader":
            attack_lines.append("_w04_attack_system.modules['encodings.utf_8'].__loader__ = None")
        elif mutation == "encoding_spec":
            attack_lines.append(
                "_w04_attack_system.modules['encodings.aliases'].__spec__.name = 'aliases'"
            )
        else:
            attack_lines.append(
                "_w04_attack_system.modules['encodings'].__cached__ = '/tmp/encodings.pyc'"
            )
        _inject_outer_bootstrap_attack(launcher_path, tuple(attack_lines))
    elif mutation == "encoding_module_alias":
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                "_w04_attack_system.modules['w04_encoding_alias'] = "
                "_w04_attack_system.modules['encodings']",
            ),
        )
    elif mutation == "encoding_origin_alias":
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_system = __import__('sys')",
                "_w04_attack_module = type(_w04_attack_system)('w04_origin_alias')",
                "_w04_attack_spec = type('_W04AttackSpec', (), {})()",
                "_w04_attack_spec.origin = _w04_attack_system.modules['encodings'].__spec__.origin",
                "_w04_attack_module.__spec__ = _w04_attack_spec",
                "_w04_attack_module.__file__ = '/tmp/w04-origin-alias.py'",
                "_w04_attack_system.modules['w04_origin_alias'] = _w04_attack_module",
            ),
        )
    elif mutation == "encodings_parent_link":
        fake_prefix = _fake_encoding_stdlib(root, encodings_link=True)
        _inject_outer_bootstrap_attack(launcher_path, _encoding_origin_attack(fake_prefix))
    elif mutation == "encodings_parent_replacement":
        fake_prefix = _fake_encoding_stdlib(root)
        stdlib = fake_prefix / "lib/python3.12"
        replacement = stdlib / "replacement-encodings"
        replacement.mkdir(mode=0o755)
        replacement.chmod(0o755)
        for name in ("__init__.py", "aliases.py", "utf_8.py"):
            target = replacement / name
            target.write_bytes((stdlib / "encodings" / name).read_bytes())
            target.chmod(0o644)
        _inject_outer_bootstrap_attack(
            launcher_path,
            _encoding_origin_attack(fake_prefix)
            + (
                "_w04_attack_posix = __import__('posix')",
                "_w04_attack_open_original = _w04_attack_posix.open",
                "_w04_attack_parent_swapped = [False]",
                "def _w04_attack_open(path, flags, mode=0o777, *, dir_fd=None):",
                "    if dir_fd is None:",
                "        descriptor = _w04_attack_open_original(path, flags, mode)",
                "    else:",
                "        descriptor = _w04_attack_open_original(path, flags, mode, dir_fd=dir_fd)",
                "    if (path == 'utf_8.py' and dir_fd is not None "
                "and not _w04_attack_parent_swapped[0]):",
                "        _w04_attack_parent_swapped[0] = True",
                f"        _w04_attack_posix.rename({os.fspath(stdlib / 'encodings')!r}, "
                f"{os.fspath(stdlib / 'parked-encodings')!r})",
                f"        _w04_attack_posix.rename({os.fspath(replacement)!r}, "
                f"{os.fspath(stdlib / 'encodings')!r})",
                "    return descriptor",
                "_w04_attack_posix.open = _w04_attack_open",
            ),
        )
    elif mutation == "encoding_leaf_replacement":
        fake_prefix = _fake_encoding_stdlib(root)
        stdlib = fake_prefix / "lib/python3.12"
        source = stdlib / "encodings/__init__.py"
        replacement = stdlib / "replacement-init.py"
        replacement.write_bytes(source.read_bytes())
        replacement.chmod(0o644)
        _inject_outer_bootstrap_attack(
            launcher_path,
            _encoding_origin_attack(fake_prefix)
            + (
                "_w04_attack_posix = __import__('posix')",
                "_w04_attack_open_original = _w04_attack_posix.open",
                "_w04_attack_leaf_swapped = [False]",
                "def _w04_attack_open(path, flags, mode=0o777, *, dir_fd=None):",
                "    if dir_fd is None:",
                "        descriptor = _w04_attack_open_original(path, flags, mode)",
                "    else:",
                "        descriptor = _w04_attack_open_original(path, flags, mode, dir_fd=dir_fd)",
                "    if (path == 'utf_8.py' and dir_fd is not None "
                "and not _w04_attack_leaf_swapped[0]):",
                "        _w04_attack_leaf_swapped[0] = True",
                f"        _w04_attack_posix.rename({os.fspath(source)!r}, "
                f"{os.fspath(stdlib / 'parked-init.py')!r})",
                f"        _w04_attack_posix.rename({os.fspath(replacement)!r}, "
                f"{os.fspath(source)!r})",
                "    return descriptor",
                "_w04_attack_posix.open = _w04_attack_open",
            ),
        )
    elif mutation == "encoding_source_owner":
        _inject_outer_bootstrap_attack(
            launcher_path,
            (
                "_w04_attack_posix = __import__('posix')",
                "_w04_attack_open_original = _w04_attack_posix.open",
                "_w04_attack_stat_original = _w04_attack_posix.stat",
                "_w04_attack_fstat_original = _w04_attack_posix.fstat",
                "_w04_attack_source_descriptors = set()",
                "_w04_attack_source_names = {'__init__.py', 'aliases.py', 'utf_8.py'}",
                "def _w04_attack_metadata(metadata):",
                "    values = list(metadata)",
                "    values[4] += 1",
                "    return type(metadata)(values)",
                "def _w04_attack_open(path, flags, mode=0o777, *, dir_fd=None):",
                "    if dir_fd is None:",
                "        descriptor = _w04_attack_open_original(path, flags, mode)",
                "    else:",
                "        descriptor = _w04_attack_open_original(path, flags, mode, dir_fd=dir_fd)",
                "    if path in _w04_attack_source_names and dir_fd is not None:",
                "        _w04_attack_source_descriptors.add(descriptor)",
                "    return descriptor",
                "def _w04_attack_stat(path, *args, **kwargs):",
                "    metadata = _w04_attack_stat_original(path, *args, **kwargs)",
                "    if path in _w04_attack_source_names and kwargs.get('dir_fd') is not None:",
                "        return _w04_attack_metadata(metadata)",
                "    return metadata",
                "def _w04_attack_fstat(descriptor):",
                "    metadata = _w04_attack_fstat_original(descriptor)",
                "    if descriptor in _w04_attack_source_descriptors:",
                "        return _w04_attack_metadata(metadata)",
                "    return metadata",
                "_w04_attack_posix.open = _w04_attack_open",
                "_w04_attack_posix.stat = _w04_attack_stat",
                "_w04_attack_posix.fstat = _w04_attack_fstat",
            ),
        )
    elif mutation == "present_pyc_metadata":
        site = _directory(root / ".venv/lib/python3.12/site-packages")
        site_source = site / "r8_present.py"
        site_source.write_text("VALUE = 1\n")
        site_source.chmod(0o644)
        site_cache = site / "__pycache__"
        site_cache.mkdir(mode=0o755)
        site_cache.chmod(0o755)
        site_pyc = site_cache / "r8_present.cpython-312.pyc"
        py_compile.compile(os.fspath(site_source), cfile=os.fspath(site_pyc), doraise=True)
        site_pyc.chmod(0o644)
        repository_cache = scripts / "__pycache__"
        repository_cache.mkdir(mode=0o755)
        repository_cache.chmod(0o755)
        foreign_source = scripts / "admit_wyscout_v5_runtime.py"
        foreign_source.write_text("VALUE = 'stable-authoritative'\n")
        foreign_source.chmod(0o644)
        foreign_pyc = repository_cache / "admit_wyscout_v5_runtime.cpython-314.pyc"
        foreign_pyc.write_bytes(bytes(190_312))
        foreign_pyc.chmod(0o644)
        repository_pyc = repository_cache / "launch_wyscout_v5.cpython-312.pyc"
        subprocess.run(  # noqa: S603  # nosec B603
            (
                "/bin/cp",
                os.fspath(_PROJECT_ROOT / "scripts/__pycache__/launch_wyscout_v5.cpython-312.pyc"),
                os.fspath(repository_pyc),
            ),
            check=True,
        )
        repository_pyc.chmod(0o644)
        policy = {
            "post_w04_audit_only_source_paths": (),
            "post_w04_retired_audit_only_pyc_predicates": (
                launcher._POST_W04_RETIRED_AUDIT_ONLY_PYC_PREDICATES
            ),
            "source_rows": (
                {
                    "authority_class": "SELECTED_DISTRIBUTION_RECORD",
                    "path": "r8_present.py",
                },
                {
                    "authority_class": "REPOSITORY_CODE_MANIFEST",
                    "path": "scripts/launch_wyscout_v5.py",
                },
                {
                    "authority_class": "REPOSITORY_CODE_MANIFEST",
                    "normal_cache_name": (
                        "admit_wyscout_v5_runtime.cpython-312[.opt-0|.opt-1|.opt-2].pyc"
                    ),
                    "owner": "scripts/admit_wyscout_v5_runtime.py",
                    "path": "scripts/admit_wyscout_v5_runtime.py",
                    "pytest_cache_name": ("admit_wyscout_v5_runtime.cpython-312-pytest-9.1.1.pyc"),
                    "sha256": hashlib.sha256(foreign_source.read_bytes()).hexdigest(),
                    "size_bytes": foreign_source.stat().st_size,
                },
            ),
            "orphan_predicates": (),
            "foreign_cache_tag_denial_predicates": (
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
            ),
        }
        _inject_outer_runtime_probe(
            launcher_path,
            (
                f"_W04_R8_PYC_POLICY = {policy!r}",
                "def _w04_r8_probe_authority(project_root):",
                "    rows = _independent_pyc_inventory(project_root, _W04_R8_PYC_POLICY)",
                "    pyc_rows = tuple(row for row in rows if row['entry_kind'] == 'PYC')",
                "    if tuple(row['authority_class'] for row in pyc_rows) != "
                "('REPOSITORY_FOREIGN_CACHE_TAG_DENIED', 'REPOSITORY_NORMAL', "
                "'SITE_DISTRIBUTION_NORMAL'):",
                "        raise RuntimeControlError('R8 present PYC rows differ')",
                "    return ('0' * 64, {}, (), rows)",
                "def _w04_r8_probe_roots(_project_root, _admission_run_id):",
                "    raise RuntimeControlError("
                "'R8 present PYC metadata census completed and control continued')",
                "_admission_authority_with_pyc = _w04_r8_probe_authority",
                "_outer_runtime_roots = _w04_r8_probe_roots",
            ),
        )
    descriptor = os.open(launcher_path, os.O_RDONLY | os.O_NOFOLLOW)
    os.set_inheritable(descriptor, True)
    environment, _bootstrap = launcher.outer_bootstrap_transport(
        project_root=root,
        control_prefix=control,
        launcher_source_fd=descriptor,
    )
    inherited = [descriptor]
    other = -1
    argv = launcher.OUTER_ARGV
    if mutation == "extra_fd":
        other = os.open(root / "uv.lock", os.O_RDONLY | os.O_NOFOLLOW)
        os.set_inheritable(other, True)
        inherited.append(other)
    elif mutation == "environment":
        environment["UNREVIEWED"] = "1"
    elif mutation == "tuple":
        changed = dict(_bootstrap)
        changed["process_role"] = "SUBSTITUTED"
        environment["W04_BOOTSTRAP_TUPLE_B64"] = (
            base64.urlsafe_b64encode(launcher._canonical_json_bytes(changed)).decode().rstrip("=")
        )
    elif mutation == "argv":
        argv = (*launcher.OUTER_ARGV, "unexpected")
    elif mutation == "offset":
        os.lseek(descriptor, 1, os.SEEK_SET)
    elif mutation == "missing_fd":
        os.set_inheritable(descriptor, False)
        inherited.clear()
    try:
        return subprocess.run(  # noqa: S603  # nosec B603
            argv,
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            close_fds=True,
            pass_fds=tuple(inherited),
            timeout=60,
        )
    finally:
        os.close(descriptor)
        if other >= 0:
            os.close(other)


def test_exact_uv_outer_argv_proves_encoding_owner_census_and_reaches_runtime(
    tmp_path: Path,
) -> None:
    completed = _isolated_outer_probe(tmp_path)
    assert completed.returncode == 2
    assert completed.stdout == b""
    assert completed.stderr.startswith(b"W04 runtime control rejected:")
    assert b"outer " not in completed.stderr


def test_exact_uv_outer_argv_rejects_extra_inherited_descriptor(tmp_path: Path) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation="extra_fd")
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert b"outer inherited descriptor census differs" in completed.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("fourth_file_backed_module", b"outer pre-guard resident module roster differs"),
        ("encoding_module_alias", b"outer pre-guard resident module roster differs"),
        ("encoding_origin_alias", b"outer pre-guard resident module roster differs"),
        ("encodings_parent_link", b"outer stdlib no-follow descriptor traversal failed"),
        ("encodings_parent_replacement", b"outer encoding parent identity drifted"),
        ("encoding_leaf_replacement", b"outer encoding source identity drifted"),
        ("encoding_source_owner", b"outer encoding source owner or metadata differs"),
    ],
)
def test_exact_uv_outer_argv_rejects_pre_guard_encoding_substitution(
    tmp_path: Path, mutation: str, message: bytes
) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation=mutation)
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert message in completed.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("disguised_builtin_file", b"outer pre-guard resident module roster differs"),
        ("disguised_builtin_no_file", b"outer pre-guard resident module roster differs"),
        ("forged_frozen", b"outer pre-guard resident module roster differs"),
        ("unregistered_builtin_alias", b"outer pre-guard resident module roster differs"),
        ("builtin_loader", b"outer pre-guard built-in module authority differs"),
        ("frozen_loader", b"outer pre-guard frozen module authority differs"),
        ("frozen_file", b"outer pre-guard frozen module authority differs"),
        ("frozen_cached", b"outer pre-guard frozen module authority differs"),
        ("encoding_loader", b"outer pre-guard encoding module census differs"),
        ("encoding_spec", b"outer pre-guard encoding module census differs"),
        ("encoding_cached", b"outer pre-guard encoding module census differs"),
    ],
)
def test_exact_uv_outer_argv_rejects_disguised_resident_module_authority(
    tmp_path: Path, mutation: str, message: bytes
) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation=mutation)
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert message in completed.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("registered_builtin_replacement", b"outer resident startup object binding differs"),
        ("registered_frozen_replacement", b"outer resident startup object binding differs"),
        ("builtin_package", b"outer pre-guard built-in module authority differs"),
        ("builtin_parent", b"outer pre-guard built-in module authority differs"),
        ("builtin_locations", b"outer pre-guard built-in module authority differs"),
        ("frozen_package", b"outer pre-guard frozen module authority differs"),
        ("frozen_parent", b"outer pre-guard frozen module authority differs"),
        ("frozen_locations", b"outer pre-guard frozen module authority differs"),
        ("builtin_importer_authority", b"outer resident importer authority differs"),
        ("frozen_importer_authority", b"outer resident importer authority differs"),
    ],
)
def test_exact_uv_outer_argv_binds_earliest_resident_objects_and_shapes(
    tmp_path: Path, mutation: str, message: bytes
) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation=mutation)
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert message in completed.stderr


def test_direct_branch_captures_startup_bindings_before_any_helper_definition() -> None:
    source = (_PROJECT_ROOT / "scripts/launch_wyscout_v5.py").read_text()
    direct_branch = source.split('if __name__ == "__main__":\n', 1)[1].split(
        "    def _w04_early_sha256", 1
    )[0]
    assert "def " not in direct_branch
    assert direct_branch.index("_W04_STARTUP_SYSTEM") < direct_branch.index(
        "_W04_STARTUP_MODULE_PAIRS"
    )
    assert direct_branch.index("_W04_STARTUP_MODULE_PAIRS") < direct_branch.index(
        "_W04_STARTUP_BUILTIN_FROZEN_SHAPES"
    )
    assert "tuple(_W04_STARTUP_SYSTEM.modules) != _W04_STARTUP_MODULE_NAMES" in direct_branch


def test_exact_uv_outer_present_pyc_metadata_census_survives_unconditional_denial(
    tmp_path: Path,
) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation="present_pyc_metadata")
    assert completed.returncode == 2
    assert completed.stdout == b""
    assert b"R8 present PYC metadata census completed and control continued" in completed.stderr
    assert b"outer guard denied in-place bytecode access" not in completed.stderr


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("environment", b"outer transport environment is not the exact closed map"),
        ("tuple", b"outer bootstrap tuple differs from complete v4 authority"),
        ("argv", b"outer cwd/argv/interpreter projection differs"),
        ("offset", b"outer launcher source descriptor metadata differs"),
        ("missing_fd", b"outer inherited descriptor census differs"),
    ],
)
def test_exact_uv_outer_argv_rejects_bootstrap_substitution(
    tmp_path: Path, mutation: str, message: bytes
) -> None:
    completed = _isolated_outer_probe(tmp_path, mutation=mutation)
    assert completed.returncode != 0
    assert completed.stdout == b""
    assert message in completed.stderr
