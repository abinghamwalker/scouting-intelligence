"""Validate a bounded task packet and its structured/Markdown subagent return."""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.control_utils import (  # noqa: E402
    ROOT,
    load_yaml_mapping,
    resolve_inside_root,
    write_json_inside_root,
)

REQUIRED_PACKET_FIELDS = {
    "schema_version",
    "task_id",
    "phase_id",
    "revision",
    "state",
    "objective",
    "depends_on",
    "assigned_role",
    "risk",
    "read_first",
    "allowed_paths",
    "forbidden_paths",
    "deliverables",
    "definition_of_done",
    "acceptance_checks",
    "stop_conditions",
    "return_template",
    "delegation",
    "git_operations",
}
REQUIRED_RETURN_FIELDS = {
    "task",
    "files_changed",
    "summary",
    "tests_run",
    "artifacts_evidence",
    "risks",
    "follow_up_items",
    "scope_confirmation",
}
REQUIRED_HEADINGS = {
    "## Task",
    "## Files changed",
    "## Summary",
    "## Tests run",
    "## Artifacts/evidence",
    "## Risks",
    "## Follow-up items",
    "## Scope confirmation",
}
SCOPE_FIELDS = {
    "git_operations_performed",
    "dependency_or_lockfile_changes",
    "edits_outside_allowed_paths",
}


def add_failure(failures: list[dict[str, str]], code: str, detail: str) -> None:
    """Append one stable, machine-readable failure."""
    failures.append({"code": code, "detail": detail})


def matches_allowed_path(path: str, patterns: list[str]) -> bool:
    """Return whether a path is covered by at least one declared write scope."""
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def validate(
    packet_path: Path,
    structured_return_path: Path,
    handback_path: Path,
) -> dict[str, Any]:
    """Return a machine-readable validation result."""
    failures: list[dict[str, str]] = []
    packet = load_yaml_mapping(packet_path)
    returned = load_yaml_mapping(structured_return_path)

    missing_packet_fields = sorted(REQUIRED_PACKET_FIELDS - set(packet))
    if missing_packet_fields:
        add_failure(
            failures,
            "PACKET_FIELDS_MISSING",
            f"missing packet fields: {missing_packet_fields}",
        )

    missing_return_fields = sorted(REQUIRED_RETURN_FIELDS - set(returned))
    if missing_return_fields:
        add_failure(
            failures,
            "RETURN_FIELDS_MISSING",
            f"missing return fields: {missing_return_fields}",
        )

    packet_task_id = packet.get("task_id")
    task = returned.get("task")
    returned_task_id = task.get("task_id") if isinstance(task, dict) else None
    if returned_task_id != packet_task_id:
        add_failure(
            failures,
            "RETURN_TASK_MISMATCH",
            f"packet task {packet_task_id!r}, return task {returned_task_id!r}",
        )

    allowed_paths_raw = packet.get("allowed_paths")
    allowed_paths = (
        [str(item) for item in allowed_paths_raw] if isinstance(allowed_paths_raw, list) else []
    )
    changed_paths_raw = returned.get("files_changed")
    changed_paths = (
        [str(item) for item in changed_paths_raw] if isinstance(changed_paths_raw, list) else []
    )
    if not changed_paths:
        add_failure(failures, "RETURN_CHANGED_PATHS_EMPTY", "files_changed must not be empty")
    for changed_path in changed_paths:
        try:
            resolve_inside_root(changed_path, must_exist=True)
        except ValueError as error:
            add_failure(failures, "RETURN_CHANGED_PATH_INVALID", str(error))
            continue
        if not matches_allowed_path(changed_path, allowed_paths):
            add_failure(
                failures,
                "RETURN_SCOPE_VIOLATION",
                f"changed path is not allowed: {changed_path}",
            )

    expected_paths = {
        str(structured_return_path.relative_to(ROOT)),
        str(handback_path.relative_to(ROOT)),
    }
    if set(changed_paths) != expected_paths:
        add_failure(
            failures,
            "RETURN_CHANGED_PATHS_INCOMPLETE",
            f"expected exactly {sorted(expected_paths)}, got {sorted(changed_paths)}",
        )

    tests_run = returned.get("tests_run")
    if not isinstance(tests_run, list) or not tests_run:
        add_failure(failures, "RETURN_TESTS_MISSING", "tests_run must be a non-empty list")
    else:
        for index, test in enumerate(tests_run):
            if not isinstance(test, dict):
                add_failure(failures, "RETURN_TEST_INVALID", f"tests_run[{index}] is not a mapping")
                continue
            command = test.get("command")
            exit_status = test.get("exit_status")
            if not isinstance(command, str) or not command.startswith("uv run "):
                add_failure(
                    failures,
                    "RETURN_TEST_NOT_UV",
                    f"tests_run[{index}] must use uv run",
                )
            if isinstance(command, str) and command.strip().startswith("git "):
                add_failure(
                    failures,
                    "RETURN_GIT_COMMAND_RECORDED",
                    f"tests_run[{index}] records a forbidden Git command",
                )
            if type(exit_status) is not int:
                add_failure(
                    failures,
                    "RETURN_TEST_STATUS_TYPE",
                    f"tests_run[{index}].exit_status must be an integer",
                )

    scope = returned.get("scope_confirmation")
    if not isinstance(scope, dict):
        add_failure(
            failures,
            "RETURN_SCOPE_MISSING",
            "scope_confirmation must be a mapping",
        )
    else:
        missing_scope = sorted(SCOPE_FIELDS - set(scope))
        if missing_scope:
            add_failure(
                failures,
                "RETURN_SCOPE_FIELDS_MISSING",
                f"missing scope fields: {missing_scope}",
            )
        for field in sorted(SCOPE_FIELDS):
            value = scope.get(field)
            if type(value) is not bool:
                add_failure(
                    failures,
                    f"RETURN_{field.upper()}_TYPE",
                    f"{field} must be a boolean, got {type(value).__name__}",
                )
            elif value:
                add_failure(
                    failures,
                    f"RETURN_{field.upper()}_VIOLATION",
                    f"{field} must be false",
                )

    handback = handback_path.read_text(encoding="utf-8")
    missing_headings = sorted(heading for heading in REQUIRED_HEADINGS if heading not in handback)
    if missing_headings:
        add_failure(
            failures,
            "HANDBACK_HEADINGS_MISSING",
            f"missing headings: {missing_headings}",
        )
    if not isinstance(packet_task_id, str) or packet_task_id not in handback:
        add_failure(
            failures,
            "HANDBACK_TASK_MISSING",
            "Markdown handback does not name the packet task",
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "schema_version": 1,
        "validator": "verify_task_return",
        "task_id": packet_task_id,
        "packet": str(packet_path.relative_to(ROOT)),
        "structured_return": str(structured_return_path.relative_to(ROOT)),
        "handback": str(handback_path.relative_to(ROOT)),
        "status": status,
        "failures": failures,
    }


def main() -> int:
    """Parse arguments, validate, optionally retain JSON evidence, and set exit status."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--packet", required=True)
    parser.add_argument("--structured-return", required=True)
    parser.add_argument("--handback", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        packet_path = resolve_inside_root(args.packet, must_exist=True)
        structured_return_path = resolve_inside_root(args.structured_return, must_exist=True)
        handback_path = resolve_inside_root(args.handback, must_exist=True)
        result = validate(packet_path, structured_return_path, handback_path)
        if args.output:
            write_json_inside_root(args.output, result)
    except (OSError, ValueError) as error:
        result = {
            "schema_version": 1,
            "validator": "verify_task_return",
            "status": "FAIL",
            "failures": [{"code": "VALIDATOR_INPUT_ERROR", "detail": str(error)}],
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
