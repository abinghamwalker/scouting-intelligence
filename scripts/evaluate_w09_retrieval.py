"""Evaluate the frozen retained-data W09 retrieval suite into immutable local JSON."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from scouting.evaluation.research import (
    DEFAULT_EVALUATION_CONFIG_PATH,
    ResearchEvaluationError,
    load_frozen_evaluation_suite,
    render_evaluation_payload,
    research_version_pins,
    run_research_evaluation,
)
from scouting.modeling.research import (
    DEFAULT_FEATURE_MANIFEST_ROOT,
    DEFAULT_INDEX_ROOT,
    DEFAULT_MATRIX_ARTIFACT_ROOT,
    ResearchIndexBuildError,
    ResearchIndexBuildMode,
    discover_feature_matrix_manifest,
    load_feature_matrix,
    load_research_index,
)
from scouting.serving.research import ResearchServingError, ResearchServingService


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=DEFAULT_EVALUATION_CONFIG_PATH)
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
    parser.add_argument("--index-root", type=Path, default=DEFAULT_INDEX_ROOT)
    parser.add_argument(
        "--output-root",
        type=Path,
        required=True,
        help="Master-owned local destination; tests must pass a temporary root.",
    )
    return parser


def _write_immutable(root: Path, name: str, payload: bytes) -> Path:
    absolute = root.absolute()
    for ancestor in (absolute, *absolute.parents):
        if not ancestor.exists():
            continue
        if ancestor.is_symlink() or ancestor.resolve(strict=True) != ancestor:
            raise ResearchEvaluationError("evaluation output root contains an unsafe ancestor")
    absolute.mkdir(mode=0o700, parents=True, exist_ok=True)
    if absolute.is_symlink() or not absolute.is_dir() or absolute.resolve(strict=True) != absolute:
        raise ResearchEvaluationError("evaluation output root is unsafe")
    destination = absolute / name
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise ResearchEvaluationError("evaluation output conflicts with a non-file")
        if destination.read_bytes() != payload:
            raise ResearchEvaluationError("immutable evaluation output conflicts")
        return destination
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        view = memoryview(payload)
        while view:
            written = os.write(descriptor, view)
            if written <= 0:
                raise ResearchEvaluationError("evaluation output write made no progress")
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    return destination


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        manifest_path = discover_feature_matrix_manifest(arguments.feature_manifest_root)
        matrix = load_feature_matrix(
            manifest_path,
            artifact_root=arguments.matrix_artifact_root,
            mode=ResearchIndexBuildMode.PRODUCTION,
        )
        index = load_research_index(
            arguments.index_root,
            matrix_manifest=matrix.manifest,
            mode=ResearchIndexBuildMode.PRODUCTION,
        )
        service = ResearchServingService(
            matrix=matrix,
            index=index,
            pins=research_version_pins(matrix.manifest, index.manifest),
        )
        suite = load_frozen_evaluation_suite(arguments.suite, service=service)
        result = run_research_evaluation(suite, service=service)
        payload = render_evaluation_payload(result)
        name = f"{result.result_digest}.evaluation.json"
        destination = _write_immutable(arguments.output_root, name, payload)
    except (
        OSError,
        ResearchEvaluationError,
        ResearchIndexBuildError,
        ResearchServingError,
    ) as exc:
        print(f"W09 retrieval evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "evaluation_result_digest": result.result_digest,
                "output": str(destination),
                "query_case_count": len(result.query_witnesses),
                "state": "confirmed",
                "suite_digest": result.suite_digest,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
