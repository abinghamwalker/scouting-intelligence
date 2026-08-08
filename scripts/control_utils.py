"""Shared, local-only helpers for orchestration verification commands."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

import yaml  # type: ignore[import-untyped]

ROOT = Path(__file__).resolve().parents[1]


def resolve_inside_root(path_text: str, *, must_exist: bool = False) -> Path:
    """Resolve a project-relative path and reject any escape from the repository."""
    candidate = (ROOT / path_text).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError(f"path escapes project root: {path_text}")
    if must_exist and not candidate.exists():
        raise ValueError(f"required path does not exist: {path_text}")
    return candidate


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    """Load a YAML document and require a string-keyed mapping at its root."""
    try:
        loaded: Any = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ValueError(f"invalid YAML in {path}: {error}") from error
    if not isinstance(loaded, Mapping) or not all(isinstance(key, str) for key in loaded):
        raise ValueError(f"expected a string-keyed YAML mapping: {path}")
    return cast(dict[str, Any], dict(loaded))


def write_json_inside_root(path_text: str, payload: Mapping[str, Any]) -> None:
    """Write deterministic JSON evidence to an approved project-relative path."""
    path = resolve_inside_root(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{json.dumps(payload, indent=2, sort_keys=True)}\n", encoding="utf-8")
