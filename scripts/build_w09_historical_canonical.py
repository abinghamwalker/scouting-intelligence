"""Build the governed W09 full historical canonical projection locally."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

from scouting.data_products.wyscout.historical import (
    DEFAULT_FEATURE_CUTOFF,
    HistoricalCanonicalBuildError,
    build_historical_canonical,
)
from scouting.sources.wyscout_historical import (
    IDENTITY_ROOT,
    PROJECT_ROOT,
    SOURCE_MANIFEST_ROOT,
    SOURCE_ROOT,
    WyscoutHistoricalAdapter,
    WyscoutHistoricalError,
)

DEFAULT_RESEARCH_ROOT = PROJECT_ROOT / "data/working/wyscout/v5/research"
DEFAULT_RESEARCH_MANIFEST_ROOT = PROJECT_ROOT / "data/manifests/wyscout/v5/research"


def _utc_instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("cutoff must be an ISO-8601 UTC instant") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != UTC.utcoffset(parsed):
        raise argparse.ArgumentTypeError("cutoff must be timezone-aware UTC")
    return parsed.astimezone(UTC)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, default=SOURCE_ROOT)
    parser.add_argument("--source-manifest-root", type=Path, default=SOURCE_MANIFEST_ROOT)
    parser.add_argument("--identity-root", type=Path, default=IDENTITY_ROOT)
    parser.add_argument("--research-root", type=Path, default=DEFAULT_RESEARCH_ROOT)
    parser.add_argument(
        "--research-manifest-root",
        type=Path,
        default=DEFAULT_RESEARCH_MANIFEST_ROOT,
    )
    parser.add_argument(
        "--feature-cutoff-ts",
        type=_utc_instant,
        default=DEFAULT_FEATURE_CUTOFF,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    adapter = WyscoutHistoricalAdapter(
        source_root=arguments.source_root,
        manifest_root=arguments.source_manifest_root,
        identity_root=arguments.identity_root,
    )
    try:
        result = build_historical_canonical(
            adapter=adapter,
            research_root=arguments.research_root,
            research_manifest_root=arguments.research_manifest_root,
            feature_cutoff_ts=arguments.feature_cutoff_ts,
        )
    except (OSError, WyscoutHistoricalError, HistoricalCanonicalBuildError) as exc:
        print(f"W09 historical canonical build failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "artifact_count": len(result.artifacts),
                "build_id": result.build_id,
                "canonical_root": result.canonical_root_relative_path,
                "manifest": result.manifest_relative_path,
                "manifest_sha256": result.manifest_sha256,
                "state": "confirmed",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
