"""Run the W06 missing-population broker exactly once."""

from __future__ import annotations

import argparse
from pathlib import Path

from scouting.evaluation.gate import broker_missing_population_no_go, load_preregistration


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--preregistration-digest", required=True)
    parser.add_argument("--invocation-id", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    arguments = parser.parse_args()
    preregistration = load_preregistration(arguments.preregistration)
    broker_missing_population_no_go(
        preregistration,
        caller_preregistration_digest=arguments.preregistration_digest,
        invocation_id=arguments.invocation_id,
        output_directory=arguments.output_directory,
    )


if __name__ == "__main__":
    main()
