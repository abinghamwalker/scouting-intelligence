"""Build the governed W09 historical-player retrieval index locally."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from scouting.modeling.research import (
    DEFAULT_FEATURE_MANIFEST_ROOT,
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    DEFAULT_MODEL_CONFIG_PATH,
    ResearchIndexBuildError,
    ResearchIndexBuildMode,
    build_research_index,
    discover_feature_matrix_manifest,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--feature-manifest-root",
        type=Path,
        default=DEFAULT_FEATURE_MANIFEST_ROOT,
    )
    parser.add_argument(
        "--matrix-artifact-root",
        type=Path,
        default=DEFAULT_MATRIX_ARTIFACT_ROOT,
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_INDEX_ROOT)
    parser.add_argument("--model-config", type=Path, default=DEFAULT_MODEL_CONFIG_PATH)
    parser.add_argument(
        "--verification-input",
        action="store_true",
        help="Read a clean-root verification matrix and write a clean-root verification index.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    mode = (
        ResearchIndexBuildMode.VERIFICATION
        if arguments.verification_input
        else ResearchIndexBuildMode.PRODUCTION
    )
    try:
        manifest_path = discover_feature_matrix_manifest(
            arguments.feature_manifest_root,
            mode=mode,
        )
        manifest = build_research_index(
            matrix_manifest_path=manifest_path,
            matrix_artifact_root=arguments.matrix_artifact_root,
            output_root=arguments.output_root,
            model_config_path=arguments.model_config,
            mode=mode,
        )
    except (OSError, ResearchIndexBuildError) as exc:
        print(f"W09 research index build failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "candidate_count": manifest.candidate_count,
                "index_id": str(manifest.index_id),
                "index_version": manifest.index_version,
                "manifest_digest": manifest.manifest_digest,
                "output_root": str(arguments.output_root),
                "state": "confirmed",
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
