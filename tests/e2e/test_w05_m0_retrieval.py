"""End-to-end fail-closed boundary assertions for W05 M0 retrieval serving."""

from __future__ import annotations

from pathlib import Path

import pytest

from scouting.serving.m0 import M0ServingCore, M0ServingError


def test_m0_core_rejects_an_unregistered_artifact_root(tmp_path: Path) -> None:
    """A copied, escaped, or incomplete bundle cannot become a serving authority."""
    with pytest.raises(M0ServingError, match="exact registered bundle"):
        M0ServingCore(
            registry=object(),
            taxonomy=object(),
            configuration=object(),
            candidates=object(),
            queries=object(),
            artifact_root=tmp_path,
        )
