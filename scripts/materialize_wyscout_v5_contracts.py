"""Materialize or check the exact W04 Wyscout v2 aggregate preimages."""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

from scouting.contracts.wyscout_aggregates import (
    aggregate_physical_bytes,
    build_product_contract_v2,
    build_schema_bundle_v2,
    product_contract_v2_sha256,
    schema_bundle_v2_sha256,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "configs/schema/wyscout-v5-schema-bundle-preimage-v2.json"
PRODUCT_PATH = ROOT / "configs/schema/wyscout-v5-product-contract-preimage-v2.json"


class AggregateMaterializationError(RuntimeError):
    """A physical aggregate file is absent, unsafe or unequal."""


def _expected_files() -> tuple[tuple[Path, bytes], tuple[Path, bytes]]:
    schema = build_schema_bundle_v2()
    schema_digest = schema_bundle_v2_sha256(schema)
    product = build_product_contract_v2(schema_digest)
    return (
        (SCHEMA_PATH, aggregate_physical_bytes(schema)),
        (PRODUCT_PATH, aggregate_physical_bytes(product)),
    )


def _check_regular(path: Path) -> bytes:
    try:
        before = path.stat(follow_symlinks=False)
    except FileNotFoundError as error:
        raise AggregateMaterializationError(f"required aggregate is absent: {path}") from error
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise AggregateMaterializationError(f"aggregate is not one regular file: {path}")
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise AggregateMaterializationError(f"aggregate cannot be read: {path}") from error
    after = path.stat(follow_symlinks=False)
    stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size", "st_mtime_ns")
    if any(getattr(before, key) != getattr(after, key) for key in stable):
        raise AggregateMaterializationError(f"aggregate changed during read: {path}")
    return raw


def check() -> None:
    """Require both existing physical files to equal the accepted bytes."""

    for path, expected in _expected_files():
        if _check_regular(path) != expected:
            raise AggregateMaterializationError(f"aggregate bytes differ: {path}")


def write() -> None:
    """Create absent files atomically; exact existing files are idempotent."""

    for path, expected in _expected_files():
        if path.exists() or path.is_symlink():
            if _check_regular(path) != expected:
                raise AggregateMaterializationError(f"refusing unequal existing file: {path}")
            continue
        path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        try:
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except OSError as error:
            raise AggregateMaterializationError(f"aggregate creation failed: {path}") from error
        try:
            view = memoryview(expected)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise AggregateMaterializationError(f"aggregate write stalled: {path}")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        if _check_regular(path) != expected:
            raise AggregateMaterializationError(f"aggregate readback differs: {path}")


def main() -> int:
    """Run the selected deterministic materialization mode."""

    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()
    print(
        "W04 v2 aggregates PASS "
        f"schema={schema_bundle_v2_sha256()} product={product_contract_v2_sha256()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
