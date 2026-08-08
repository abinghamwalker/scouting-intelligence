"""Frozen post-build-id W04 rebuild child.

This entrypoint consumes only the launcher's inherited source/result descriptors
and canonical closed envelope, executes the accepted local vertical slice, and
returns one framed ``w04-child-result-v3`` completion value.
"""

from __future__ import annotations

import os
import stat
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast
from uuid import UUID

# ``python -S -B scripts/rebuild_wyscout_v5.py`` starts with only the scripts
# directory on sys.path.  Establish the exact containing repository root using
# stdlib only before importing the sibling admission module as a package.
_BOOTSTRAP_ROOT = Path(__file__).resolve().parents[1]
if os.fspath(_BOOTSTRAP_ROOT) not in sys.path:
    sys.path.insert(0, os.fspath(_BOOTSTRAP_ROOT))

from scripts import admit_wyscout_v5_runtime as admission  # noqa: E402


class RebuildChildError(RuntimeError):
    """One frozen rebuild-child predicate failed."""


_REBUILD_INVOCATION_JSON_KEYS = (
    "authority_rows",
    "build_id",
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
    "selected_lock_closure_digest",
    "source_manifest_id",
    "source_manifest_sha256",
    "tenant_club_id",
    "tenant_id",
    "window_definition_id",
    "window_end_utc",
    "window_start_utc",
)


def _reconstruct_rebuild_invocation_json(value: object) -> dict[str, object]:
    """Reconstruct only the two tuple fields from canonical JSON arrays."""

    if type(value) is not dict or tuple(value) != _REBUILD_INVOCATION_JSON_KEYS:
        raise RebuildChildError("rebuild invocation JSON key roster or order differs")
    invocation_json = cast(dict[str, object], value)
    authority_rows = invocation_json["authority_rows"]
    dependency_rows = invocation_json["dependency_rows"]
    if type(authority_rows) is not list or type(dependency_rows) is not list:
        raise RebuildChildError("rebuild invocation tuple field is not a JSON array")
    return {
        key: (
            tuple(authority_rows)
            if key == "authority_rows"
            else tuple(dependency_rows)
            if key == "dependency_rows"
            else invocation_json[key]
        )
        for key in _REBUILD_INVOCATION_JSON_KEYS
    }


def _install_runtime_import_roots(root: Path) -> None:
    for candidate in reversed((root / "src", root / ".venv/lib/python3.12/site-packages")):
        spelling = os.fspath(candidate)
        if spelling not in sys.path:
            sys.path.insert(0, spelling)


def _strict_fd(name: str) -> int:
    raw = os.environ.get(name)
    if raw is None or admission.FD_RE.fullmatch(raw) is None:
        raise RebuildChildError(f"{name} is not one strict inherited descriptor")
    return int(raw)


def _validate_input(
    envelope: dict[str, object], source_fd: int, result_fd: int
) -> dict[str, object]:
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
        raise RebuildChildError("child input common key roster or order differs")
    inputs = envelope.get("inputs")
    expected_input_keys = (
        "build_id",
        "code_manifest_id",
        "code_manifest_relative_path",
        "code_manifest_sha256",
        "environment_digest",
        "layer_manifest_relative_paths",
        "rebuild_invocation",
        "rebuild_prefix_relative_path",
        "rebuild_receipt_relative_path",
        "run_id",
    )
    if type(inputs) is not dict or tuple(inputs) != expected_input_keys:
        raise RebuildChildError("rebuild input key roster or order differs")
    values = cast(dict[str, object], inputs)
    digest_values = (
        envelope.get("base_environment_digest"),
        envelope.get("entrypoint_sha256"),
        envelope.get("expected_repository_code_sha256"),
        envelope.get("launcher_sha256"),
        envelope.get("nonce"),
        envelope.get("ordered_argv_sha256"),
        values.get("build_id"),
        values.get("code_manifest_sha256"),
        values.get("environment_digest"),
    )
    if any(
        type(value) is not str or admission.SHA256_RE.fullmatch(value) is None
        for value in digest_values
    ):
        raise RebuildChildError("rebuild input contains a malformed digest")
    run_id = values.get("run_id")
    if type(run_id) is not str or admission.UUID4_RE.fullmatch(run_id) is None:
        raise RebuildChildError("rebuild run ID is not UUIDv4")
    build_id = cast(str, values["build_id"])
    expected_prefix = f"data/working/wyscout/v5/.staging/{build_id}/{run_id}/runtime-pycache"
    expected_receipt = f"runs/w04/wyscout-rebuild/{build_id}/{run_id}.receipt.json"
    expected_layers = [
        f"data/manifests/wyscout/v5/{layer}/{build_id}.manifest.json"
        for layer in ("bronze", "silver", "gold")
    ]
    if (
        envelope["schema_version"] != admission.CHILD_INPUT_SCHEMA_VERSION
        or envelope["child_role"] != "POST_BUILD_ID_REBUILD"
        or envelope["entrypoint_relative_path"] != admission.REBUILD_ARGV[-1]
        or envelope["ordered_argv"] != list(admission.REBUILD_ARGV)
        or envelope["ordered_argv_sha256"] != admission._sha256_json(list(admission.REBUILD_ARGV))
        or envelope["source_descriptor_number"] != source_fd
        or envelope["result_descriptor_number"] != result_fd
        or envelope["nonce"] != os.environ.get("W04_RESULT_NONCE")
        or os.environ.get("W04_CHILD_ROLE") != "POST_BUILD_ID_REBUILD"
        or values["rebuild_prefix_relative_path"] != expected_prefix
        or envelope["pycache_prefix_relative"] != expected_prefix
        or values["rebuild_receipt_relative_path"] != expected_receipt
        or values["layer_manifest_relative_paths"] != expected_layers
    ):
        raise RebuildChildError("rebuild child exact equality binding differs")
    prefix = envelope.get("pycache_prefix_absolute")
    if type(prefix) is not str or not prefix.startswith("/"):
        raise RebuildChildError("rebuild prefix absolute path is malformed")
    metadata = os.stat(prefix, follow_symlinks=False)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
        or tuple(os.scandir(prefix))
    ):
        raise RebuildChildError("rebuild pycache prefix is unsafe or nonempty")
    return values


def _source_observation(envelope: dict[str, object], source_fd: int) -> dict[str, object]:
    if not os.get_inheritable(source_fd):
        raise RebuildChildError("entrypoint source descriptor is not inheritable")
    before = os.fstat(source_fd)
    if (
        not stat.S_ISREG(before.st_mode)
        or stat.S_IMODE(before.st_mode) != 0o644
        or before.st_nlink != 1
        or not 1 <= before.st_size <= admission.MAX_SOURCE_BYTES
        or os.lseek(source_fd, 0, os.SEEK_CUR) != 0
    ):
        raise RebuildChildError("entrypoint source descriptor metadata differs")
    offset = 0
    chunks: list[bytes] = []
    while offset < before.st_size:
        chunk = os.pread(source_fd, min(1024 * 1024, before.st_size - offset), offset)
        if not chunk:
            raise RebuildChildError("entrypoint source ended before declared size")
        chunks.append(chunk)
        offset += len(chunk)
    raw = b"".join(chunks)
    after = os.fstat(source_fd)
    if (
        os.pread(source_fd, 1, before.st_size) != b""
        or (before.st_dev, before.st_ino, before.st_mode, before.st_nlink, before.st_size)
        != (after.st_dev, after.st_ino, after.st_mode, after.st_nlink, after.st_size)
        or os.lseek(source_fd, 0, os.SEEK_CUR) != 0
        or admission._sha256(raw) != envelope["entrypoint_sha256"]
        or len(raw) != envelope["entrypoint_size_bytes"]
    ):
        raise RebuildChildError("entrypoint source bytes differ from envelope")
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
        "relative_path": admission.REBUILD_ARGV[-1],
        "role": "POST_BUILD_ID_REBUILD",
        "sha256": admission._sha256(raw),
        "size_bytes": len(raw),
        "source_eof": True,
    }


def _normalized_rebuild_environment(environment: dict[str, str]) -> dict[str, object]:
    normalized = admission.normalized_child_environment(environment)
    present = cast(dict[str, object], normalized["present"])
    present["PYTHONPYCACHEPREFIX"] = "<REBUILD_PREFIX>"
    return normalized


def _safe_directory(path: Path) -> None:
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        pass
    metadata = os.stat(path, follow_symlinks=False)
    if (
        not stat.S_ISDIR(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or stat.S_IMODE(metadata.st_mode) != 0o700
    ):
        raise RebuildChildError("publication root or staging directory is unsafe")


def _publication_roots(root: Path, build_id: str, run_id: str) -> Any:
    from scouting.data_products.wyscout import WyscoutProductRoots

    working = root / "data/working/wyscout/v5"
    manifests = root / "data/manifests/wyscout/v5"
    _safe_directory(working)
    _safe_directory(manifests)
    runs_parent = root / "runs/w04"
    if not runs_parent.parent.exists():
        raise RebuildChildError("repository runs root is absent")
    _safe_directory(runs_parent)
    runs = runs_parent / "wyscout-rebuild"
    _safe_directory(runs)
    staging_parent = working / ".staging" / build_id / run_id
    metadata = os.stat(staging_parent, follow_symlinks=False)
    if not stat.S_ISDIR(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o700:
        raise RebuildChildError("launcher-owned rebuild staging parent is unsafe")
    stages = tuple(staging_parent / name for name in ("products", "manifests", "receipts"))
    for stage in stages:
        _safe_directory(stage)
    return WyscoutProductRoots(
        working_final_root=working,
        working_staging_root=stages[0],
        manifest_final_root=manifests,
        manifest_staging_root=stages[1],
        runs_final_root=runs,
        runs_staging_root=stages[2],
    )


def _require_retained_snapshot(
    *,
    expected_repository: str,
    expected_components: dict[str, object],
    expected_counts: tuple[int, ...],
    expected_pyc: tuple[dict[str, object], ...],
    expected_interpreter_paths: tuple[Path, Path],
    expected_code_manifest: bytes,
    observed_repository: str,
    observed_components: dict[str, object],
    observed_counts: tuple[int, ...],
    observed_pyc: tuple[dict[str, object], ...],
    observed_interpreter_paths: tuple[Path, Path],
    observed_code_manifest: bytes,
) -> None:
    """Reject any code, component/resource, PYC, or code-manifest drift."""

    if (
        observed_repository != expected_repository
        or observed_components != expected_components
        or observed_counts != expected_counts
        or observed_pyc != expected_pyc
        or observed_interpreter_paths != expected_interpreter_paths
        or observed_code_manifest != expected_code_manifest
    ):
        raise RebuildChildError(
            "retained repository/component/resource/PYC/code-manifest authority drifted"
        )


def run_rebuild() -> None:
    source_fd = _strict_fd("W04_ENTRYPOINT_SOURCE_FD")
    result_fd = _strict_fd("W04_RESULT_FD")
    if source_fd == result_fd or not os.get_inheritable(result_fd):
        raise RebuildChildError("source/result descriptors are equal or noninheritable")
    environment = dict(os.environ)
    envelope, _raw = admission._decode_input(environment["W04_CHILD_INPUT_B64"])
    inputs = _validate_input(envelope, source_fd, result_fd)
    normalized_environment = _normalized_rebuild_environment(environment)
    if envelope["base_environment_digest"] != admission._sha256_json(normalized_environment):
        raise RebuildChildError("child base environment digest differs")
    entrypoint = _source_observation(envelope, source_fd)
    root = Path.cwd().absolute()
    repository, components, counts, pyc_before, interpreter_paths = (
        admission._collect_stable_authority_with_pyc(root)
    )
    if repository != envelope["expected_repository_code_sha256"]:
        raise RebuildChildError("repository code authority differs from input")
    code_manifest_path = root / cast(str, inputs["code_manifest_relative_path"])
    code_manifest = admission._guard_read_absolute_regular(
        code_manifest_path,
        expected_mode=0o600,
        expected_sha256=cast(str, inputs["code_manifest_sha256"]),
    )
    expected_manifest = {
        **components,
        "environment_digest": admission._sha256_json(components),
        "repository_code_sha256": repository,
        "schema_version": admission.MANIFEST_SCHEMA_VERSION,
    }
    if admission.load_canonical_json(code_manifest) != expected_manifest:
        raise RebuildChildError("code manifest differs from fresh stable authority")

    runtime_subset_authority = admission.freeze_repository_runtime_subset_authority(
        root, interpreter_paths
    )
    _install_runtime_import_roots(root)
    from scouting.contracts.wyscout_build import (
        ChildResultEnvelope,
        EntrypointSourceResult,
        FinalRecheckResult,
        PostBuildIdRebuildResult,
        RebuildInvocation,
        RuntimeSubsetObservation,
        sha256_json,
    )
    from scouting.data_products.wyscout.rebuild import rebuild_wyscout_v5

    invocation_json = _reconstruct_rebuild_invocation_json(inputs["rebuild_invocation"])
    invocation = RebuildInvocation.model_validate(invocation_json, strict=True)
    build_id = cast(str, inputs["build_id"])
    run_id = cast(str, inputs["run_id"])
    if invocation.build_id != build_id:
        raise RebuildChildError("rebuild invocation build differs from envelope")
    roots = _publication_roots(root, build_id, run_id)
    pycache_prefix = cast(str, envelope["pycache_prefix_absolute"])

    def retained_recheck() -> None:
        if (
            _normalized_rebuild_environment(dict(os.environ)) != normalized_environment
            or _source_observation(envelope, source_fd) != entrypoint
            or tuple(os.scandir(pycache_prefix))
        ):
            raise RebuildChildError("retained child authority drifted during publication")
        (
            observed_repository,
            observed_components,
            observed_counts,
            observed_pyc,
            observed_interpreter_paths,
        ) = admission._collect_stable_authority_with_pyc(root)
        observed_manifest = admission._guard_read_absolute_regular(
            code_manifest_path,
            expected_mode=0o600,
            expected_sha256=cast(str, inputs["code_manifest_sha256"]),
        )
        if admission.load_canonical_json(observed_manifest) != expected_manifest:
            raise RebuildChildError("retained code manifest semantic authority drifted")
        _require_retained_snapshot(
            expected_repository=repository,
            expected_components=components,
            expected_counts=counts,
            expected_pyc=pyc_before,
            expected_interpreter_paths=interpreter_paths,
            expected_code_manifest=code_manifest,
            observed_repository=observed_repository,
            observed_components=observed_components,
            observed_counts=observed_counts,
            observed_pyc=observed_pyc,
            observed_interpreter_paths=observed_interpreter_paths,
            observed_code_manifest=observed_manifest,
        )

    clock = datetime.now(UTC)
    result = rebuild_wyscout_v5(
        invocation=invocation,
        run_id=UUID(run_id),
        roots=roots,
        source_root=(root / "data/source/wyscout/v5"),
        source_manifest_root=(root / "data/manifests"),
        identity_root=(root / "data/working/wyscout/v5/identity"),
        started_at=clock,
        checked_at=clock,
        completed_at=clock,
        final_recheck=retained_recheck,
    )
    retained_recheck()
    final_repository, final_components, final_counts, pyc_after, final_interpreter_paths = (
        admission._collect_stable_authority_with_pyc(root)
    )
    final_manifest = admission._guard_read_absolute_regular(
        code_manifest_path,
        expected_mode=0o600,
        expected_sha256=cast(str, inputs["code_manifest_sha256"]),
    )
    _require_retained_snapshot(
        expected_repository=repository,
        expected_components=components,
        expected_counts=counts,
        expected_pyc=pyc_before,
        expected_interpreter_paths=interpreter_paths,
        expected_code_manifest=code_manifest,
        observed_repository=final_repository,
        observed_components=final_components,
        observed_counts=final_counts,
        observed_pyc=pyc_after,
        observed_interpreter_paths=final_interpreter_paths,
        observed_code_manifest=final_manifest,
    )
    summaries = tuple(manifest.summary for manifest in result.manifests)
    site_pyc = [row for row in pyc_after if row["role"] == "SELECTED_SITE_PACKAGES"]
    repository_pyc = [row for row in pyc_after if row["role"] == "WHOLE_REPOSITORY"]
    runtime_subset_rows, runtime_subset_digest = runtime_subset_authority.observe()
    validated_runtime_subset_rows = tuple(
        RuntimeSubsetObservation.model_validate(row, strict=True) for row in runtime_subset_rows
    )
    final_recheck = FinalRecheckResult(
        build_id=build_id,
        child_environment_sha256=admission._sha256_json(environment),
        entrypoint_sha256=cast(str, entrypoint["sha256"]),
        environment_digest=invocation.environment_digest,
        layer_manifest_set_sha256=sha256_json([row.model_dump(mode="json") for row in summaries]),
        rebuild_receipt_sha256=result.rebuild_receipt.summary.sha256,
        repository_code_sha256=repository,
        repository_pyc_inventory_sha256=admission._sha256_json(repository_pyc),
        resource_digest=invocation.local_resource_digest,
        run_id=run_id,
        runtime_subset_digest=runtime_subset_digest,
        runtime_subset_rows=validated_runtime_subset_rows,
        site_pyc_inventory_sha256=admission._sha256_json(site_pyc),
    )
    post_build = PostBuildIdRebuildResult(
        build_id=build_id,
        final_recheck=final_recheck,
        layer_manifests=summaries,
        rebuild_prefix_relative_path=cast(str, inputs["rebuild_prefix_relative_path"]),
        rebuild_receipt=result.rebuild_receipt.summary,
        run_id=run_id,
    )
    output = ChildResultEnvelope(
        child_environment_sha256=admission._sha256_json(environment),
        child_role="POST_BUILD_ID_REBUILD",
        entrypoint_source=EntrypointSourceResult.model_validate(entrypoint, strict=True),
        expected_repository_code_sha256=repository,
        launcher_sha256=cast(str, envelope["launcher_sha256"]),
        nonce=cast(str, envelope["nonce"]),
        ordered_argv_sha256=cast(str, envelope["ordered_argv_sha256"]),
        payload_kind="REBUILD_COMPLETION",
        result=post_build,
    )
    payload = admission.canonical_json_bytes(output.model_dump(mode="json"))
    admission._write_all(result_fd, admission.encode_result_frame(payload))
    os.close(source_fd)
    os.close(result_fd)


def main() -> int:
    run_rebuild()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"W04 rebuild rejected: {error}", file=sys.stderr)
        raise SystemExit(2) from error
