"""Master-invoked local acquisition CLI for the frozen Wyscout Figshare v5 source."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from scouting.sources import acquire_wyscout_v5, load_wyscout_source_config


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/sources/w04-provider.yaml"),
    )
    parser.add_argument("--timeout-seconds", type=float, default=30.0)
    parser.add_argument("--max-attempts", type=int, default=3)
    return parser


def _inside_project(project_root: Path, path: Path, *, context: str) -> Path:
    root = project_root.resolve(strict=True)
    candidate = path if path.is_absolute() else root / path
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(root):
        raise ValueError(f"{context} must remain beneath the project root")
    return resolved


def main() -> int:
    """Acquire only when explicitly invoked; importing this module performs no I/O."""
    arguments = _parser().parse_args()
    project_root = arguments.project_root.resolve(strict=True)
    config_path = _inside_project(
        project_root,
        arguments.config,
        context="source config",
    )
    config = load_wyscout_source_config(config_path)
    destination_root = _inside_project(
        project_root,
        Path(config.destination_root),
        context="destination root",
    )
    working_root = _inside_project(
        project_root,
        Path(config.working_root),
        context="working root",
    )
    result = acquire_wyscout_v5(
        config,
        destination_root=destination_root,
        working_root=working_root,
        acquired_at=datetime.now(UTC),
        timeout_seconds=arguments.timeout_seconds,
        max_attempts=arguments.max_attempts,
    )
    print(
        json.dumps(
            {
                "manifest_created": result.manifest_created,
                "manifest_path": result.manifest_relative_path,
                "manifest_sha256": result.manifest_sha256,
                "source_id": config.source_id,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
