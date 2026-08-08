"""Build the governed W09 historical player feature matrix locally."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from scouting.features.historical import (
    DEFAULT_CANONICAL_ARTIFACT_ROOT,
    DEFAULT_FEATURE_MANIFEST_ROOT,
    DEFAULT_FEATURE_ROOT,
    DEFAULT_REGISTRY_PATH,
    HistoricalFeatureBuildError,
    HistoricalFeatureBuildMode,
    build_historical_feature_matrix,
    discover_canonical_manifest,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canonical-manifest",
        type=Path,
        help="Exact accepted canonical manifest; production auto-discovery requires one.",
    )
    parser.add_argument(
        "--canonical-artifact-root", type=Path, default=DEFAULT_CANONICAL_ARTIFACT_ROOT
    )
    parser.add_argument("--feature-root", type=Path, default=DEFAULT_FEATURE_ROOT)
    parser.add_argument("--feature-manifest-root", type=Path, default=DEFAULT_FEATURE_MANIFEST_ROOT)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument(
        "--test-fixture",
        action="store_true",
        help="Admit only a canonical test-fixture manifest and explicitly supplied temp roots.",
    )
    parser.add_argument(
        "--verification-output",
        action="store_true",
        help="Read exact production authority but write only to explicitly supplied temp roots.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    if arguments.test_fixture and arguments.verification_output:
        print(
            "W09 historical feature build failed: build modes are mutually exclusive",
            file=sys.stderr,
        )
        return 1
    mode = HistoricalFeatureBuildMode.PRODUCTION
    if arguments.test_fixture:
        mode = HistoricalFeatureBuildMode.TEST_FIXTURE
    elif arguments.verification_output:
        mode = HistoricalFeatureBuildMode.VERIFICATION
    try:
        canonical_manifest = arguments.canonical_manifest
        if canonical_manifest is None:
            if mode is HistoricalFeatureBuildMode.TEST_FIXTURE:
                raise HistoricalFeatureBuildError(
                    "fixture mode requires an explicit canonical manifest"
                )
            canonical_manifest = discover_canonical_manifest()
        result = build_historical_feature_matrix(
            canonical_manifest_path=canonical_manifest,
            canonical_artifact_root=arguments.canonical_artifact_root,
            feature_root=arguments.feature_root,
            feature_manifest_root=arguments.feature_manifest_root,
            registry_path=arguments.registry,
            mode=mode,
        )
    except (OSError, HistoricalFeatureBuildError) as exc:
        print(f"W09 historical feature build failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "catalogue_player_count": result.manifest.catalogue_player_count,
                "eligibility_decision_count": result.manifest.eligibility_decision_count,
                "manifest": str(result.matrix_manifest_path),
                "manifest_sha256": result.matrix_manifest_sha256,
                "matrix_row_count": result.manifest.matrix_row_count,
                "matrix_version": result.matrix_version,
                "state": "confirmed",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
