"""Verify phase dependency, task, evidence, state, and local checkpoint gates."""

from __future__ import annotations

import argparse
import json
import shutil

# Subprocess use is limited to fixed local Git inspection commands.
import subprocess  # nosec B404
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
from scripts.verify_task_return import REQUIRED_PACKET_FIELDS  # noqa: E402

GIT_EXECUTABLE = shutil.which("git")
GATE_READY_STATES = {"READY", "VERIFIED", "CHECKPOINTED", "CLOSED"}


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Run a fixed local Git inspection command."""
    if GIT_EXECUTABLE is None:
        raise RuntimeError("Git executable is unavailable")
    return subprocess.run(  # nosec B603
        [GIT_EXECUTABLE, *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


def path_exists(path_text: str) -> tuple[bool, str]:
    """Check a registry path without allowing root escape."""
    try:
        path = resolve_inside_root(path_text, must_exist=True)
    except ValueError as error:
        return False, str(error)
    if not path.is_file() or path.stat().st_size == 0:
        return False, f"evidence is not a non-empty file: {path_text}"
    return True, path_text


def packets_are_all_master_assigned(
    packet_paths: object,
    expected_task_id: object,
) -> tuple[bool, str]:
    """Prove that every referenced packet belongs to one master-assigned task."""
    if not isinstance(expected_task_id, str) or not expected_task_id:
        return False, "master-owned return exemption requires a non-empty string task ID"
    if not isinstance(packet_paths, list) or not packet_paths:
        return False, "master-owned return exemption requires at least one packet"

    for packet_path in packet_paths:
        if not isinstance(packet_path, str):
            return False, "master-owned return exemption requires string packet paths"
        try:
            resolved_packet = resolve_inside_root(packet_path, must_exist=True)
            packet = load_yaml_mapping(resolved_packet)
        except (OSError, ValueError) as error:
            return False, f"master-owned packet is invalid: {packet_path}: {error}"
        missing_fields = sorted(REQUIRED_PACKET_FIELDS - set(packet))
        if missing_fields:
            return False, f"packet is missing mandatory fields: {packet_path}: {missing_fields}"
        if packet.get("assigned_role") != "master":
            return False, f"packet is not master-assigned: {packet_path}"
        packet_task_id = packet.get("task_id")
        if not isinstance(packet_task_id, str):
            return False, f"packet has no string task ID: {packet_path}"
        if packet_task_id != expected_task_id:
            return False, (
                f"packet task ID mismatch: {packet_path}: "
                f"expected {expected_task_id!r}, got {packet_task_id!r}"
            )

    return True, "all referenced packets are complete, master-assigned and task-ID matched"


def task_returns_are_evidenced(task: dict[str, Any]) -> tuple[bool, str]:
    """Require retained returns unless every packet proves master ownership."""
    returns = task.get("returns")
    if not isinstance(returns, list):
        return False, "returns must be a list"
    if not returns:
        return packets_are_all_master_assigned(task.get("packets"), task.get("task_id"))

    for return_path in returns:
        exists, detail = path_exists(str(return_path))
        if not exists:
            return False, detail
    return True, f"{len(returns)} retained return(s)"


def conditional_dependency_gate_passes(
    gate_config: object,
    dependency_id: str,
) -> tuple[bool, str]:
    """Validate a narrow, retained gate that conditionally satisfies one dependency."""
    if not isinstance(gate_config, dict):
        return False, "dependency is not CLOSED and has no conditional gate"

    required_strings = (
        "gate_id",
        "evidence",
        "accepted_status",
        "accepted_decision",
        "authorized_scope",
    )
    for field_name in required_strings:
        if not isinstance(gate_config.get(field_name), str) or not gate_config[field_name]:
            return False, f"conditional dependency gate has invalid {field_name}"

    evidence_path = gate_config["evidence"]
    try:
        resolved = resolve_inside_root(evidence_path, must_exist=True)
        gate_report = json.loads(resolved.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return False, f"conditional dependency gate evidence is invalid: {error}"
    if not isinstance(gate_report, dict):
        return False, "conditional dependency gate evidence must be a JSON object"

    expected = {
        "phase_id": dependency_id,
        "gate_id": gate_config["gate_id"],
        "status": gate_config["accepted_status"],
        "decision": gate_config["accepted_decision"],
        "authorized_scope": gate_config["authorized_scope"],
    }
    mismatches = [
        f"{field_name}={gate_report.get(field_name)!r}"
        for field_name, expected_value in expected.items()
        if gate_report.get(field_name) != expected_value
    ]
    if mismatches:
        return False, "conditional gate not satisfied: " + ", ".join(mismatches)
    return True, (
        f"{gate_config['gate_id']}:{gate_config['accepted_status']} authorizes "
        f"{gate_config['authorized_scope']}"
    )


def tag_commit(tag: str) -> str | None:
    """Return the commit resolved by a local tag, or None when absent."""
    completed = run_git("rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{}}")
    return completed.stdout.strip() if completed.returncode == 0 else None


def verify(
    phase_id: str,
    registry_path: Path,
    *,
    allow_pending_checkpoint: bool,
) -> dict[str, Any]:
    """Return the complete machine-readable phase-gate result."""
    failures: list[dict[str, str]] = []
    checks: list[dict[str, str]] = []

    def record(check_id: str, passed: bool, detail: str) -> None:
        checks.append({"id": check_id, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            failures.append({"code": check_id, "detail": detail})

    registry = load_yaml_mapping(registry_path)
    phases = registry.get("phases")
    if not isinstance(phases, dict) or phase_id not in phases:
        return {
            "schema_version": 1,
            "validator": "verify_phase",
            "phase_id": phase_id,
            "status": "FAIL",
            "checks": [],
            "failures": [{"code": "PHASE_NOT_FOUND", "detail": f"phase not found: {phase_id}"}],
        }
    phase = phases[phase_id]
    if not isinstance(phase, dict):
        raise ValueError(f"phase entry must be a mapping: {phase_id}")

    allowed_states = registry.get("allowed_states")
    state = phase.get("state")
    record(
        "PHASE_STATE_ALLOWED",
        isinstance(allowed_states, list) and state in allowed_states,
        f"state: {state!r}",
    )
    record(
        "PHASE_GATE_READY",
        state in GATE_READY_STATES,
        f"state must be one of {sorted(GATE_READY_STATES)}, got {state!r}",
    )

    dependencies = phase.get("depends_on")
    conditional_dependency_gates = phase.get("conditional_dependency_gates")
    dependency_details = []
    dependencies_passed = isinstance(dependencies, list)
    if isinstance(dependencies, list):
        for dependency_id in dependencies:
            dependency = phases.get(dependency_id) if isinstance(dependency_id, str) else None
            dependency_state = dependency.get("state") if isinstance(dependency, dict) else None
            if dependency_state == "CLOSED":
                dependency_details.append(f"{dependency_id}:{dependency_state}")
                continue
            gate_config = (
                conditional_dependency_gates.get(dependency_id)
                if isinstance(conditional_dependency_gates, dict) and isinstance(dependency_id, str)
                else None
            )
            gate_passed, gate_detail = conditional_dependency_gate_passes(
                gate_config,
                str(dependency_id),
            )
            dependency_details.append(f"{dependency_id}:{dependency_state} via {gate_detail}")
            if not gate_passed:
                dependencies_passed = False
    record(
        "DEPENDENCIES_CLOSED",
        dependencies_passed,
        ", ".join(dependency_details) or "no dependencies",
    )

    tasks = phase.get("tasks")
    task_checks_passed = isinstance(tasks, list) and bool(tasks)
    task_details = []
    if isinstance(tasks, list):
        for task in tasks:
            if not isinstance(task, dict):
                task_checks_passed = False
                continue
            task_id = task.get("task_id")
            task_state = task.get("state")
            returns_passed, returns_detail = task_returns_are_evidenced(task)
            task_details.append(f"{task_id}:{task_state}:{returns_detail}")
            if task_state != "ACCEPTED":
                task_checks_passed = False
            if not returns_passed:
                task_checks_passed = False
            for key in ("packets", "reviews"):
                paths = task.get(key)
                if not isinstance(paths, list) or not paths:
                    task_checks_passed = False
                    continue
                for path_text in paths:
                    exists, _ = path_exists(str(path_text))
                    if not exists:
                        task_checks_passed = False
    record(
        "TASKS_ACCEPTED_AND_EVIDENCED",
        task_checks_passed,
        ", ".join(task_details) or "no task records",
    )

    evidence = phase.get("evidence")
    evidence_passed = isinstance(evidence, list) and bool(evidence)
    evidence_details = []
    if isinstance(evidence, list):
        for entry in evidence:
            if not isinstance(entry, dict):
                evidence_passed = False
                continue
            path_text = entry.get("path")
            required = entry.get("required", True)
            exists, detail = path_exists(str(path_text))
            evidence_details.append(detail)
            if required and not exists:
                evidence_passed = False
    record(
        "EVIDENCE_PRESENT",
        evidence_passed,
        ", ".join(evidence_details) or "no evidence records",
    )

    declared_checks = phase.get("checks")
    declared_checks_passed = isinstance(declared_checks, list) and bool(declared_checks)
    declared_details = []
    if isinstance(declared_checks, list):
        for check in declared_checks:
            if not isinstance(check, dict):
                declared_checks_passed = False
                continue
            check_id = check.get("id")
            check_status = check.get("status")
            evidence_path = check.get("evidence")
            evidence_exists, _ = path_exists(str(evidence_path))
            declared_details.append(f"{check_id}:{check_status}")
            if check_status != "PASS" or not evidence_exists:
                declared_checks_passed = False
    record(
        "DECLARED_CHECKS_PASS",
        declared_checks_passed,
        ", ".join(declared_details) or "no declared checks",
    )

    remotes = run_git("remote")
    remote_names = [line for line in remotes.stdout.splitlines() if line.strip()]
    record(
        "ZERO_GIT_REMOTES",
        remotes.returncode == 0 and not remote_names,
        "zero remotes" if not remote_names else f"configured: {remote_names}",
    )

    checkpoint = phase.get("checkpoint")
    checkpoint_passed = isinstance(checkpoint, dict)
    checkpoint_detail = "checkpoint mapping missing"
    if isinstance(checkpoint, dict):
        start_tag = checkpoint.get("start_tag")
        accepted_tag = checkpoint.get("accepted_tag")
        commit_message = checkpoint.get("commit_message")
        start_commit = tag_commit(str(start_tag)) if start_tag else None
        accepted_commit = tag_commit(str(accepted_tag)) if accepted_tag else None
        checkpoint_passed = start_commit is not None
        checkpoint_detail = f"start={start_tag}:{start_commit or 'MISSING'}"
        if state == "CLOSED":
            if accepted_commit is None and allow_pending_checkpoint:
                checkpoint_detail += f", accepted={accepted_tag}:PENDING_ALLOWED"
            elif accepted_commit is None:
                checkpoint_passed = False
                checkpoint_detail += f", accepted={accepted_tag}:MISSING"
            else:
                subject = run_git("show", "-s", "--format=%s", accepted_commit).stdout.strip()
                if subject != commit_message:
                    checkpoint_passed = False
                checkpoint_detail += (
                    f", accepted={accepted_tag}:{accepted_commit}, subject={subject!r}"
                )
    record("CHECKPOINT_STATE", checkpoint_passed, checkpoint_detail)

    if state == "CLOSED" and not allow_pending_checkpoint:
        tree_status = run_git("status", "--porcelain=v1")
        record(
            "CLEAN_CHECKPOINT_TREE",
            tree_status.returncode == 0 and not tree_status.stdout.strip(),
            "clean" if not tree_status.stdout.strip() else tree_status.stdout.strip(),
        )

    status = "PASS" if not failures else "FAIL"
    return {
        "schema_version": 1,
        "validator": "verify_phase",
        "phase_id": phase_id,
        "registry": str(registry_path.relative_to(ROOT)),
        "allow_pending_checkpoint": allow_pending_checkpoint,
        "state": state,
        "status": status,
        "checks": checks,
        "failures": failures,
    }


def main() -> int:
    """Verify one registry phase and optionally retain the JSON report."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--registry", default="orchestration/phase_registry.yaml")
    parser.add_argument("--allow-pending-checkpoint", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        registry_path = resolve_inside_root(args.registry, must_exist=True)
        result = verify(
            args.phase,
            registry_path,
            allow_pending_checkpoint=args.allow_pending_checkpoint,
        )
        if args.output:
            write_json_inside_root(args.output, result)
    except (OSError, RuntimeError, ValueError) as error:
        result = {
            "schema_version": 1,
            "validator": "verify_phase",
            "phase_id": args.phase,
            "status": "FAIL",
            "checks": [],
            "failures": [{"code": "PHASE_VALIDATOR_ERROR", "detail": str(error)}],
        }

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
