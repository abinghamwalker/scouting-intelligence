"""Build one exact participant-safe W10 v2 comparison from accepted W09."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scouting.contracts.expert_relevance import MdEvidenceSubrubricV2
from scouting.data_products.wyscout.expert_evidence import (
    ExpertEvidenceBuildError,
    build_expert_evidence_bundles_v2,
    build_participant_evidence_comparison_v2,
    load_production_evidence_inputs_v2,
    participant_safe_comparison_bytes_v2,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--exemplar-grain-id", required=True)
    parser.add_argument("--candidate-grain-id", required=True)
    parser.add_argument(
        "--md-subrubric",
        choices=tuple(MdEvidenceSubrubricV2),
        type=MdEvidenceSubrubricV2,
    )
    parser.add_argument("--output", type=Path)
    return parser


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace incompatible evidence bytes: {path}")
        return
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        matrix, action_paths = load_production_evidence_inputs_v2()
        grain_ids = (arguments.exemplar_grain_id, arguments.candidate_grain_id)
        branches = (
            {}
            if arguments.md_subrubric is None
            else {grain_id: arguments.md_subrubric for grain_id in grain_ids}
        )
        bundles = build_expert_evidence_bundles_v2(
            matrix,
            action_paths=action_paths,
            selected_grain_ids=grain_ids,
            md_subrubrics=branches,
        )
        payload = participant_safe_comparison_bytes_v2(
            build_participant_evidence_comparison_v2(*bundles)
        )
        if arguments.output is None:
            sys.stdout.buffer.write(payload)
        else:
            _write_once(arguments.output, payload)
    except (ExpertEvidenceBuildError, FileExistsError, OSError, ValueError) as exc:
        print(f"W10 v2 evidence build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
