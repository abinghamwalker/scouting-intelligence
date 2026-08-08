"""End-to-end evidence for the exact isolated W04 Wyscout vertical slice."""

from __future__ import annotations

import hashlib
import os
import socket
import stat
import urllib.request
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest

from scouting.contracts.wyscout_build import (
    PreBuildProjection,
    RebuildInvocation,
    accepted_authority_rows,
    accepted_dependency_rows,
    code_manifest_id_for_digest,
    invocation_from_projection,
)
from scouting.contracts.wyscout_data import Layer, W04Applicability
from scouting.data_products.wyscout import WyscoutProductRoots, guarded_read
from scouting.data_products.wyscout.rebuild import (
    WyscoutRebuildResult,
    _validate_complete_receipt_closure,
    rebuild_wyscout_v5,
)
from scouting.storage.formats import read_parquet_bytes

RUN_ID = UUID("12345678-1234-4123-8123-123456789abc")
DIFFERENT_RUN_ID = UUID("87654321-4321-4321-8321-cba987654321")
CLOCK = datetime(2026, 8, 2, 12, tzinfo=UTC)


@dataclass(frozen=True, slots=True)
class SliceEvidence:
    roots: WyscoutProductRoots
    mirror_roots: WyscoutProductRoots
    result: WyscoutRebuildResult
    mirror_result: WyscoutRebuildResult
    different_run_result: WyscoutRebuildResult
    identical_file_sets: tuple[dict[str, bytes], dict[str, bytes], dict[str, bytes]]


def _roots(parent: Path, name: str) -> WyscoutProductRoots:
    base = (parent / name).resolve()
    base.mkdir(mode=0o700)
    values = tuple(
        base / token
        for token in (
            "working",
            "working-stage",
            "manifests",
            "manifest-stage",
            "runs",
            "runs-stage",
        )
    )
    for path in values:
        path.mkdir(mode=0o700)
    return WyscoutProductRoots(*values)


def _new_staging_roots(
    parent: Path, existing: WyscoutProductRoots, name: str
) -> WyscoutProductRoots:
    stages = tuple(
        (parent / f"{name}-{token}").resolve() for token in ("working", "manifest", "runs")
    )
    for path in stages:
        path.mkdir(mode=0o700)
    return WyscoutProductRoots(
        working_final_root=existing.working_final_root,
        working_staging_root=stages[0],
        manifest_final_root=existing.manifest_final_root,
        manifest_staging_root=stages[1],
        runs_final_root=existing.runs_final_root,
        runs_staging_root=stages[2],
    )


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


def _files(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _real_root_inventory(root: Path) -> tuple[tuple[object, ...], ...]:
    """Inventory every exact real-root descendant without following any link."""

    try:
        root_metadata = os.stat(root, follow_symlinks=False)
    except FileNotFoundError:
        return (("ABSENT", os.fspath(root)),)
    if not stat.S_ISDIR(root_metadata.st_mode) or stat.S_ISLNK(root_metadata.st_mode):
        raise AssertionError("real output root is a link or non-directory")

    def stable(row: os.stat_result) -> tuple[int, ...]:
        return (
            row.st_dev,
            row.st_ino,
            row.st_mode,
            row.st_nlink,
            row.st_size,
            row.st_mtime_ns,
            row.st_ctime_ns,
        )

    rows: list[tuple[object, ...]] = []
    pending = [(root, ".")]
    while pending:
        directory, relative = pending.pop()
        metadata = os.stat(directory, follow_symlinks=False)
        if not stat.S_ISDIR(metadata.st_mode) or stat.S_ISLNK(metadata.st_mode):
            raise AssertionError("real output inventory crossed a link or non-directory")
        rows.append(
            (
                relative,
                "DIRECTORY",
                stat.S_IMODE(metadata.st_mode),
                metadata.st_dev,
                metadata.st_ino,
                metadata.st_nlink,
                metadata.st_size,
                metadata.st_mtime_ns,
                metadata.st_ctime_ns,
            )
        )
        entries = sorted(os.scandir(directory), key=lambda entry: entry.name)
        for entry in reversed(entries):
            child_relative = entry.name if relative == "." else f"{relative}/{entry.name}"
            child = Path(entry.path)
            child_metadata = entry.stat(follow_symlinks=False)
            if stat.S_ISLNK(child_metadata.st_mode):
                raise AssertionError("real output inventory contains a link")
            if stat.S_ISDIR(child_metadata.st_mode):
                pending.append((child, child_relative))
                continue
            if not stat.S_ISREG(child_metadata.st_mode):
                raise AssertionError("real output inventory contains a nonregular entry")
            descriptor = os.open(child, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            try:
                before = os.fstat(descriptor)
                digest = hashlib.sha256()
                while chunk := os.read(descriptor, 1024 * 1024):
                    digest.update(chunk)
                after = os.fstat(descriptor)
            finally:
                os.close(descriptor)
            if stable(before) != stable(after) or stable(before) != stable(child_metadata):
                raise AssertionError("real output file changed during inventory")
            rows.append(
                (
                    child_relative,
                    "FILE",
                    stat.S_IMODE(before.st_mode),
                    before.st_dev,
                    before.st_ino,
                    before.st_nlink,
                    before.st_size,
                    before.st_mtime_ns,
                    before.st_ctime_ns,
                    digest.hexdigest(),
                )
            )
    return tuple(sorted(rows))


def _execute(
    invocation: RebuildInvocation, run_id: UUID, roots: WyscoutProductRoots
) -> WyscoutRebuildResult:
    return rebuild_wyscout_v5(
        invocation=invocation,
        run_id=run_id,
        roots=roots,
        source_root=Path("data/source/wyscout/v5").resolve(),
        source_manifest_root=Path("data/manifests").resolve(),
        identity_root=Path("data/working/wyscout/v5/identity").resolve(),
        started_at=CLOCK,
        checked_at=CLOCK,
        completed_at=CLOCK,
        final_recheck=lambda: None,
    )


@pytest.fixture(scope="module")
def slice_evidence(tmp_path_factory: pytest.TempPathFactory) -> SliceEvidence:
    parent = tmp_path_factory.mktemp("w04-vertical-slice").resolve()
    roots = _roots(parent, "first")
    mirror = _roots(parent, "second")
    real_roots = (
        Path("data/working/wyscout/v5").resolve(),
        Path("data/manifests/wyscout/v5").resolve(),
        Path("runs/w04/wyscout-rebuild").resolve(),
    )
    real_before = tuple(_real_root_inventory(path) for path in real_roots)
    monkeypatch = pytest.MonkeyPatch()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("vertical slice attempted provider or network access")

    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(urllib.request, "urlopen", forbidden)
    try:
        invocation = _invocation()
        result = _execute(invocation, RUN_ID, roots)
        mirror_result = _execute(invocation, RUN_ID, mirror)
        identical_file_sets = (
            _files(mirror.working_final_root),
            _files(mirror.manifest_final_root),
            _files(mirror.runs_final_root),
        )
        different_roots = _new_staging_roots(parent, mirror, "different-run")
        different_run_result = _execute(invocation, DIFFERENT_RUN_ID, different_roots)
    finally:
        monkeypatch.undo()
    real_after = tuple(_real_root_inventory(path) for path in real_roots)
    assert real_before == real_after
    return SliceEvidence(
        roots=roots,
        mirror_roots=mirror,
        result=result,
        mirror_result=mirror_result,
        different_run_result=different_run_result,
        identical_file_sets=identical_file_sets,
    )


def test_exact_checked_populations_and_feature_vector(slice_evidence: SliceEvidence) -> None:
    result = slice_evidence.result
    assert len(result.bronze_population.known_actions) == 1_768
    assert len(result.bronze_population.rejected_fields) == 3_544
    assert len(result.actions.ordered_values) == 13
    assert len(result.possessions.values) == 2
    assert [product.encoding.row_count for product in result.products] == [
        1_768,
        3_544,
        13,
        1,
        2,
        1,
        1,
    ]
    assert result.gold.value.features.model_dump() == {
        "action_count": 2,
        "coordinate_known_action_count": 2,
        "match_count": 1,
        "resolved_possession_action_count": 2,
    }
    assert result.gold.value.applicability.state is W04Applicability.RESEARCH_ONLY
    assert result.gold.value.applicability.reason_codes == ("RIGHT_CENSORED_OR_UNCERTAIN",)


def test_complete_manifest_and_receipt_chain(slice_evidence: SliceEvidence) -> None:
    result = slice_evidence.result
    assert tuple(manifest.value.layer for manifest in result.manifests) == (
        Layer.BRONZE,
        Layer.SILVER,
        Layer.GOLD,
    )
    assert tuple(len(manifest.value.entries) for manifest in result.manifests) == (2, 4, 1)
    assert tuple(
        tuple(parent.layer for parent in manifest.value.parent_layer_manifests)
        for manifest in result.manifests
    ) == ((), (Layer.BRONZE,), (Layer.SILVER,))
    assert result.rebuild_receipt.value.boundary_receipts == (result.boundary_receipt.summary,)
    assert result.rebuild_receipt.value.started_at <= result.boundary_receipt.value.checked_at
    assert result.boundary_receipt.value.checked_at <= result.rebuild_receipt.value.completed_at


def test_every_parquet_reopens_and_independent_mirrors_are_identical(
    slice_evidence: SliceEvidence,
) -> None:
    working, manifests, runs = slice_evidence.identical_file_sets
    assert _files(slice_evidence.roots.working_final_root) == working
    assert _files(slice_evidence.roots.manifest_final_root) == manifests
    assert _files(slice_evidence.roots.runs_final_root) == runs
    assert tuple(product.encoding.payload for product in slice_evidence.result.products) == tuple(
        product.encoding.payload for product in slice_evidence.mirror_result.products
    )
    assert tuple(manifest.payload for manifest in slice_evidence.result.manifests) == tuple(
        manifest.payload for manifest in slice_evidence.mirror_result.manifests
    )
    assert slice_evidence.result.boundary_receipt.payload == (
        slice_evidence.mirror_result.boundary_receipt.payload
    )
    assert slice_evidence.result.rebuild_receipt.payload == (
        slice_evidence.mirror_result.rebuild_receipt.payload
    )
    for product in slice_evidence.result.products:
        path = slice_evidence.roots.working_final_root / product.relative_path.removeprefix(
            "data/working/wyscout/v5/"
        )
        assert len(read_parquet_bytes(guarded_read(path))) == product.encoding.row_count


def test_different_run_keeps_products_and_manifests_stable_but_scopes_receipts(
    slice_evidence: SliceEvidence,
) -> None:
    same = slice_evidence.mirror_result
    different = slice_evidence.different_run_result
    assert tuple(product.encoding.payload for product in same.products) == tuple(
        product.encoding.payload for product in different.products
    )
    assert tuple(manifest.payload for manifest in same.manifests) == tuple(
        manifest.payload for manifest in different.manifests
    )
    assert same.boundary_receipt.payload != different.boundary_receipt.payload
    assert same.rebuild_receipt.payload != different.rebuild_receipt.payload


@pytest.mark.parametrize("attack", ("temporal", "manifest", "receipt"))
def test_local_receipt_closure_rejects_targeted_mutations(
    slice_evidence: SliceEvidence, attack: str
) -> None:
    result = slice_evidence.result
    boundary = result.boundary_receipt
    manifests = result.manifests
    receipt = result.rebuild_receipt.value
    if attack == "temporal":
        boundary = replace(
            boundary,
            value=boundary.value.model_copy(update={"checked_at": "2026-08-03T00:00:00Z"}),
        )
    elif attack == "manifest":
        manifests = (
            replace(manifests[0], payload=manifests[0].payload + b"\n"),
            manifests[1],
            manifests[2],
        )
    else:
        receipt = receipt.model_copy(update={"boundary_receipts": ()})
    with pytest.raises((TypeError, ValueError)):
        _validate_complete_receipt_closure(
            receipt=receipt,
            products=result.products,
            manifests=manifests,
            boundary=boundary,
            gold=result.gold,
            roots=slice_evidence.roots,
        )
