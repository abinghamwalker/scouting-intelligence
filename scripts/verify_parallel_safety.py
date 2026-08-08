"""Demonstrate and verify the W02 path-disjoint parallel-dispatch rules."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.control_utils import (  # noqa: E402
    load_yaml_mapping,
    resolve_inside_root,
    write_json_inside_root,
)


def literal_prefix(pattern: str) -> str:
    """Return the non-glob prefix used for conservative overlap detection."""
    parts = []
    for part in PurePosixPath(pattern).parts:
        if any(character in part for character in "*?["):
            break
        parts.append(part)
    return "/".join(parts).rstrip("/")


def scopes_overlap(left: str, right: str) -> bool:
    """Conservatively detect overlapping exact or glob write scopes."""
    left_prefix = literal_prefix(left)
    right_prefix = literal_prefix(right)
    if not left_prefix or not right_prefix:
        return True
    return (
        left_prefix == right_prefix
        or left_prefix.startswith(f"{right_prefix}/")
        or right_prefix.startswith(f"{left_prefix}/")
    )


def pattern_is_serial(pattern: str, serial_patterns: list[str]) -> bool:
    """Return whether a declared write pattern touches a serial-owned path."""
    prefix = literal_prefix(pattern)
    probes = {pattern, prefix, f"{prefix}/sentinel" if prefix else pattern}
    return any(
        fnmatch.fnmatchcase(probe, serial_pattern)
        or fnmatch.fnmatchcase(serial_pattern, pattern)
        or scopes_overlap(pattern, serial_pattern)
        for probe in probes
        for serial_pattern in serial_patterns
    )


def evaluate(
    left_paths: list[str],
    right_paths: list[str],
    serial_patterns: list[str],
) -> dict[str, Any]:
    """Return ALLOW only for two disjoint scopes that avoid every serial path."""
    reasons: list[str] = []
    for path in [*left_paths, *right_paths]:
        if pattern_is_serial(path, serial_patterns):
            reasons.append(f"serial path: {path}")
    for left in left_paths:
        for right in right_paths:
            if scopes_overlap(left, right):
                reasons.append(f"overlap: {left} <> {right}")
    return {
        "decision": "ALLOW" if not reasons else "DENY",
        "reasons": sorted(set(reasons)),
    }


def scenario_suite(serial_patterns: list[str]) -> dict[str, Any]:
    """Exercise the controlling allow/deny cases."""
    scenarios: list[dict[str, Any]] = [
        {
            "id": "disjoint-fixture-and-readme",
            "left": ["tests/fixtures/orchestration/parallel/a/**"],
            "right": ["docs/architecture/parallel-b/**"],
            "expected": "ALLOW",
        },
        {
            "id": "dependency-lock-is-serial",
            "left": ["uv.lock"],
            "right": ["tests/fixtures/orchestration/parallel/b/**"],
            "expected": "DENY",
        },
        {
            "id": "contracts-are-serial",
            "left": ["src/scouting/contracts/**"],
            "right": ["docs/architecture/parallel-c/**"],
            "expected": "DENY",
        },
        {
            "id": "migrations-are-serial",
            "left": ["migrations/**"],
            "right": ["tests/fixtures/orchestration/parallel/d/**"],
            "expected": "DENY",
        },
        {
            "id": "overlapping-scopes-are-serial",
            "left": ["tests/fixtures/orchestration/shared/**"],
            "right": ["tests/fixtures/orchestration/shared/result.yaml"],
            "expected": "DENY",
        },
    ]
    results = []
    for scenario in scenarios:
        evaluation = evaluate(scenario["left"], scenario["right"], serial_patterns)
        results.append(
            {
                **scenario,
                **evaluation,
                "status": "PASS" if evaluation["decision"] == scenario["expected"] else "FAIL",
            }
        )
    return {
        "schema_version": 1,
        "validator": "verify_parallel_safety",
        "status": "PASS" if all(result["status"] == "PASS" for result in results) else "FAIL",
        "scenarios": results,
    }


def main() -> int:
    """Run the scenario suite against the reviewed ownership policy."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--ownership", default="orchestration/ownership.yaml")
    parser.add_argument("--output")
    args = parser.parse_args()

    ownership_path = resolve_inside_root(args.ownership, must_exist=True)
    ownership = load_yaml_mapping(ownership_path)
    serial_raw = ownership.get("serial_paths")
    if not isinstance(serial_raw, list) or not all(isinstance(item, str) for item in serial_raw):
        result: dict[str, Any] = {
            "schema_version": 1,
            "validator": "verify_parallel_safety",
            "status": "FAIL",
            "failures": ["ownership.serial_paths must be a list of strings"],
        }
    else:
        result = scenario_suite(serial_raw)

    if args.output:
        write_json_inside_root(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
