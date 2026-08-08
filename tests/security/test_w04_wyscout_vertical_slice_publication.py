"""Adversarial local-only publication checks for the W04 vertical slice."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest
from pydantic import ValidationError

from scouting.contracts.wyscout_build import (
    PreBuildProjection,
    RebuildInvocation,
    accepted_authority_rows,
    accepted_dependency_rows,
    canonical_json_bytes,
    code_manifest_id_for_digest,
    invocation_from_projection,
    load_canonical_json,
    projection_from_invocation,
)
from scouting.data_products.wyscout import WyscoutProductRoots, guarded_read, staged_publisher
from scouting.storage.wyscout_publication import (
    PublicationConfigurationError,
    PublicationRecheckError,
)


def _safe_roots(parent: Path) -> WyscoutProductRoots:
    values = tuple((parent / name).resolve() for name in ("wf", "ws", "mf", "ms", "rf", "rs"))
    for path in values:
        path.mkdir(mode=0o700)
    return WyscoutProductRoots(*values)


def _invocation() -> RebuildInvocation:
    code_digest = "1" * 64
    return invocation_from_projection(
        PreBuildProjection(
            authority_rows=accepted_authority_rows(),
            code_manifest_id=code_manifest_id_for_digest(code_digest),
            code_manifest_sha256=code_digest,
            dependency_rows=accepted_dependency_rows(),
            environment_digest="2" * 64,
            local_resource_digest="3" * 64,
            product_contract_digest="4" * 64,
            schema_bundle_digest="5" * 64,
            selected_lock_closure_digest="6" * 64,
        )
    )


def test_staged_publisher_rejects_symlinked_or_aliased_roots(tmp_path: Path) -> None:
    parent = tmp_path.resolve()
    roots = _safe_roots(parent)
    link = parent / "working-link"
    link.symlink_to(roots.working_final_root, target_is_directory=True)
    attacked = WyscoutProductRoots(
        working_final_root=link,
        working_staging_root=roots.working_staging_root,
        manifest_final_root=roots.manifest_final_root,
        manifest_staging_root=roots.manifest_staging_root,
        runs_final_root=roots.runs_final_root,
        runs_staging_root=roots.runs_staging_root,
    )
    with pytest.raises(PublicationConfigurationError, match="non-directory or link"):
        staged_publisher(attacked)
    aliased = WyscoutProductRoots(
        working_final_root=roots.working_final_root,
        working_staging_root=roots.working_final_root,
        manifest_final_root=roots.manifest_final_root,
        manifest_staging_root=roots.manifest_staging_root,
        runs_final_root=roots.runs_final_root,
        runs_staging_root=roots.runs_staging_root,
    )
    with pytest.raises(PublicationConfigurationError, match="distinct"):
        staged_publisher(aliased)


@pytest.mark.parametrize("attack", ("mode", "symlink"))
def test_guarded_read_rejects_mutable_or_linked_evidence(tmp_path: Path, attack: str) -> None:
    target = tmp_path / "evidence.json"
    target.write_bytes(b"{}\n")
    os.chmod(target, 0o600)
    candidate = target
    if attack == "mode":
        os.chmod(target, 0o644)
    else:
        candidate = tmp_path / "evidence-link.json"
        candidate.symlink_to(target)
    with pytest.raises((OSError, ValueError)):
        guarded_read(candidate)


def test_build_identity_substitution_is_rejected_by_strict_inverse() -> None:
    from scouting.contracts.wyscout_build import RebuildInvocation

    payload = _invocation().model_dump()
    payload["build_id"] = "f" * 64
    with pytest.raises(ValidationError, match="projection hash"):
        RebuildInvocation.model_validate(payload, strict=True)


def test_owned_runtime_has_no_provider_network_or_publication_client_imports() -> None:
    root = Path("src/scouting/data_products/wyscout")
    payload = "\n".join(path.read_text() for path in sorted(root.glob("*.py")))
    payload += Path("scripts/rebuild_wyscout_v5.py").read_text()
    for forbidden in (
        "import requests",
        "import httpx",
        "import socket",
        "boto3",
        "databricks",
        "subprocess.Popen",
        "create_connection",
        "urlopen(",
    ):
        assert forbidden not in payload


def test_rebuild_child_rejects_incomplete_or_reordered_common_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(os.fspath(Path.cwd()))
    from scripts import rebuild_wyscout_v5 as child

    with pytest.raises(child.RebuildChildError, match="common key roster"):
        child._validate_input({"schema_version": "w04-child-input-v1"}, 3, 4)


def _canonical_invocation_json() -> tuple[RebuildInvocation, bytes, dict[str, object]]:
    invocation = _invocation()
    raw = canonical_json_bytes(invocation)
    decoded = load_canonical_json(raw)
    assert type(decoded) is dict
    return invocation, raw, cast(dict[str, object], decoded)


def test_rebuild_child_reconstructs_only_json_arrays_and_preserves_logical_bytes() -> None:
    from scripts import rebuild_wyscout_v5 as child

    invocation, raw, decoded = _canonical_invocation_json()
    authority_rows = decoded["authority_rows"]
    dependency_rows = decoded["dependency_rows"]
    assert type(authority_rows) is list
    assert type(dependency_rows) is list

    reconstructed = child._reconstruct_rebuild_invocation_json(decoded)
    assert type(reconstructed["authority_rows"]) is tuple
    assert type(reconstructed["dependency_rows"]) is tuple
    assert (
        cast(tuple[object, ...], reconstructed["authority_rows"])[0]
        is cast(list[object], authority_rows)[0]
    )
    assert (
        cast(tuple[object, ...], reconstructed["dependency_rows"])[0]
        is cast(list[object], dependency_rows)[0]
    )

    validated = RebuildInvocation.model_validate(reconstructed, strict=True)
    projection = projection_from_invocation(validated)
    assert validated == invocation
    assert invocation_from_projection(projection) == validated
    assert projection_from_invocation(invocation_from_projection(projection)) == projection
    assert canonical_json_bytes(validated) == raw


def test_rebuild_child_rejects_tuple_already_present_at_json_boundary() -> None:
    from scripts import rebuild_wyscout_v5 as child

    payload = _invocation().model_dump()
    assert type(payload["authority_rows"]) is tuple
    assert type(payload["dependency_rows"]) is tuple
    with pytest.raises(child.RebuildChildError, match="not a JSON array"):
        child._reconstruct_rebuild_invocation_json(payload)


@pytest.mark.parametrize("mutation", ("missing", "extra", "reordered"))
def test_rebuild_child_rejects_invocation_json_key_roster_and_order(mutation: str) -> None:
    from scripts import rebuild_wyscout_v5 as child

    _invocation_value, _raw, decoded = _canonical_invocation_json()
    if mutation == "missing":
        del decoded["build_id"]
    elif mutation == "extra":
        decoded["unexpected"] = None
    else:
        items = list(decoded.items())
        items[0], items[1] = items[1], items[0]
        decoded = dict(items)
    with pytest.raises(child.RebuildChildError, match="key roster or order"):
        child._reconstruct_rebuild_invocation_json(decoded)


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        ("authority_rows", {}),
        ("authority_rows", "not-an-array"),
        ("dependency_rows", {}),
        ("dependency_rows", "not-an-array"),
    ),
)
def test_rebuild_child_rejects_non_array_tuple_fields(field: str, replacement: object) -> None:
    from scripts import rebuild_wyscout_v5 as child

    _invocation_value, _raw, decoded = _canonical_invocation_json()
    decoded[field] = replacement
    with pytest.raises(child.RebuildChildError, match="not a JSON array"):
        child._reconstruct_rebuild_invocation_json(decoded)


@pytest.mark.parametrize(
    "mutation",
    (
        "authority_order",
        "authority_cardinality",
        "authority_value",
        "dependency_order",
        "dependency_cardinality",
        "dependency_value",
        "nested_extra",
        "nested_mistyped",
        "model_field_mistyped",
    ),
)
def test_rebuild_child_rejects_reconstructed_invocation_semantic_drift(mutation: str) -> None:
    from scripts import rebuild_wyscout_v5 as child

    _invocation_value, _raw, decoded = _canonical_invocation_json()
    authority_rows = cast(list[object], decoded["authority_rows"])
    dependency_rows = cast(list[object], decoded["dependency_rows"])
    if mutation == "authority_order":
        authority_rows.reverse()
    elif mutation == "authority_cardinality":
        authority_rows.pop()
    elif mutation == "authority_value":
        first = cast(dict[str, object], authority_rows[0])
        authority_rows[0] = {**first, "candidate_sha256": "0" * 64}
    elif mutation == "dependency_order":
        dependency_rows.reverse()
    elif mutation == "dependency_cardinality":
        dependency_rows.pop()
    elif mutation == "dependency_value":
        first = cast(dict[str, object], dependency_rows[0])
        dependency_rows[0] = {**first, "digest": "0" * 64}
    elif mutation == "nested_extra":
        first = cast(dict[str, object], authority_rows[0])
        authority_rows[0] = {**first, "unexpected": "forbidden"}
    elif mutation == "nested_mistyped":
        first = cast(dict[str, object], dependency_rows[0])
        dependency_rows[0] = {**first, "available_at": 1}
    else:
        decoded["build_id"] = 1

    reconstructed = child._reconstruct_rebuild_invocation_json(decoded)
    with pytest.raises(ValidationError):
        RebuildInvocation.model_validate(reconstructed, strict=True)


@pytest.mark.parametrize(
    "drift_key",
    ("repository", "components", "counts", "pyc", "interpreter_paths", "code_manifest"),
)
def test_retained_authority_mutation_prevents_local_publication(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, drift_key: str
) -> None:
    monkeypatch.syspath_prepend(os.fspath(Path.cwd()))
    from scripts import rebuild_wyscout_v5 as child

    roots = _safe_roots(tmp_path.resolve())
    publisher = staged_publisher(roots)
    expected = {
        "repository": "1" * 64,
        "components": {"local_resource_digest": "2" * 64},
        "counts": (1,),
        "pyc": ({"role": "WHOLE_REPOSITORY"},),
        "interpreter_paths": (Path("/accepted/python"), Path("/accepted/libpython")),
        "code_manifest": b"manifest",
    }
    observed = dict(expected)
    observed[drift_key] = {
        "repository": "f" * 64,
        "components": {"local_resource_digest": "f" * 64},
        "counts": (2,),
        "pyc": ({"role": "SELECTED_SITE_PACKAGES"},),
        "interpreter_paths": (Path("/attacker/python"), Path("/attacker/libpython")),
        "code_manifest": b"mutated",
    }[drift_key]

    def drifted() -> None:
        child._require_retained_snapshot(
            expected_repository=cast(str, expected["repository"]),
            expected_components=cast(dict[str, object], expected["components"]),
            expected_counts=cast(tuple[int, ...], expected["counts"]),
            expected_pyc=cast(tuple[dict[str, object], ...], expected["pyc"]),
            expected_interpreter_paths=cast(tuple[Path, Path], expected["interpreter_paths"]),
            expected_code_manifest=cast(bytes, expected["code_manifest"]),
            observed_repository=cast(str, observed["repository"]),
            observed_components=cast(dict[str, object], observed["components"]),
            observed_counts=cast(tuple[int, ...], observed["counts"]),
            observed_pyc=cast(tuple[dict[str, object], ...], observed["pyc"]),
            observed_interpreter_paths=cast(tuple[Path, Path], observed["interpreter_paths"]),
            observed_code_manifest=cast(bytes, observed["code_manifest"]),
        )

    with pytest.raises(PublicationRecheckError, match="final code/environment/resource"):
        publisher.publish_bytes(
            "wyscout-working",
            "bounded/product.bin",
            b"product",
            validator=lambda _candidate: None,
            final_recheck=drifted,
        )
    assert not (roots.working_final_root / "bounded/product.bin").exists()


def test_exact_retained_authority_snapshot_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(os.fspath(Path.cwd()))
    from scripts import rebuild_wyscout_v5 as child

    components: dict[str, object] = {"local_resource_digest": "2" * 64}
    pyc: tuple[dict[str, object], ...] = ({"role": "WHOLE_REPOSITORY"},)
    interpreter_paths = (Path("/accepted/python"), Path("/accepted/libpython"))
    child._require_retained_snapshot(
        expected_repository="1" * 64,
        expected_components=components,
        expected_counts=(1,),
        expected_pyc=pyc,
        expected_interpreter_paths=interpreter_paths,
        expected_code_manifest=b"manifest",
        observed_repository="1" * 64,
        observed_components=components,
        observed_counts=(1,),
        observed_pyc=pyc,
        observed_interpreter_paths=interpreter_paths,
        observed_code_manifest=b"manifest",
    )


def test_frozen_python_s_b_argv_reaches_closed_envelope_guard() -> None:
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    process = subprocess.run(  # noqa: S603
        [sys.executable, "-S", "-B", "scripts/rebuild_wyscout_v5.py"],
        cwd=Path.cwd(),
        env=environment,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
        timeout=30,
    )
    assert process.returncode == 2
    assert b"W04 rebuild rejected" in process.stderr
    assert b"W04_ENTRYPOINT_SOURCE_FD" in process.stderr
    assert b"ModuleNotFoundError" not in process.stderr
