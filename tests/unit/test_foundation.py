"""W01 package and project-boundary smoke tests."""

from __future__ import annotations

import tomllib
from pathlib import Path

import scouting

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_GROUPS = {
    "runtime",
    "data",
    "model",
    "orchestration",
    "test",
    "e2e",
    "lint-type",
    "security",
}


def test_package_import_smoke() -> None:
    """The root package is importable from the uv-managed project."""
    assert scouting.__version__ == "0.1.0"


def test_python_boundary_and_dependency_groups() -> None:
    """The root project declares the approved interpreter and group boundaries."""
    with (ROOT / "pyproject.toml").open("rb") as project_file:
        project = tomllib.load(project_file)

    assert project["project"]["requires-python"] == ">=3.12,<3.13"
    assert set(project["dependency-groups"]) == EXPECTED_GROUPS
