"""Deterministic source-code digest framing shared by governed builders."""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from pathlib import Path


def governed_code_digest(paths: Iterable[Path]) -> str:
    """Hash this framing authority and each exact source path once."""

    framed_paths = {Path(__file__).resolve(), *(path.resolve() for path in paths)}
    digest = hashlib.sha256()
    for path in sorted(framed_paths, key=lambda item: (item.name, item.as_posix())):
        if path.is_symlink() or not path.is_file():
            raise OSError(f"governed code source is absent or unsafe: {path.name}")
        payload = path.read_bytes()
        name = path.name.encode("utf-8")
        digest.update(len(name).to_bytes(8, "big"))
        digest.update(name)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


__all__ = ["governed_code_digest"]
