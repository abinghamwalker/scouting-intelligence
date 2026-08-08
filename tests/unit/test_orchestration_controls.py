"""W02 orchestration schema, packet, and parallel-safety tests."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.control_utils import load_yaml_mapping  # noqa: E402
from scripts.verify_parallel_safety import evaluate, scenario_suite  # noqa: E402
from scripts.verify_phase import (  # noqa: E402
    GATE_READY_STATES,
    packets_are_all_master_assigned,
    task_returns_are_evidenced,
)
from scripts.verify_task_return import (  # noqa: E402
    REQUIRED_PACKET_FIELDS,
    matches_allowed_path,
)


def load(relative_path: str) -> dict[str, Any]:
    """Load one reviewed orchestration mapping."""
    return load_yaml_mapping(ROOT / relative_path)


def test_all_orchestration_yaml_parses() -> None:
    """Every committed orchestration YAML file has a mapping root."""
    yaml_paths = sorted((ROOT / "orchestration").rglob("*.yaml"))
    assert yaml_paths
    for yaml_path in yaml_paths:
        loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
        assert isinstance(loaded, dict), yaml_path


def test_yaml_loader_reports_invalid_input_as_a_validation_error(tmp_path: Path) -> None:
    """Malformed orchestration YAML becomes a bounded verifier failure."""
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("broken: [\n", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid YAML"):
        load_yaml_mapping(invalid)


def test_master_plan_and_registry_define_continuous_authority_chain() -> None:
    """The control plane records the authorised research-workbench pivot exactly."""
    plan = load("orchestration/master_plan.yaml")
    registry = load("orchestration/phase_registry.yaml")

    assert plan["approval"]["highest_authorised_wave"] == "W11"
    assert plan["approval"]["continuous_phase_progression"] is True
    assert plan["approval"]["checkpoint_review_pause_required"] is False
    assert set(registry["phases"]) == {f"W{number:02d}" for number in range(12)}
    assert registry["phases"]["W01"]["state"] == "CLOSED"
    assert registry["phases"]["W02"]["depends_on"] == ["W01"]

    active_phase = plan["active_wave"]["phase_id"]
    last_closed_phase = plan["last_closed_wave"]
    next_phase = plan["next_wave"]["phase_id"]
    assert active_phase == "W10"
    assert last_closed_phase == "W09"
    assert next_phase == "W11"
    assert plan["active_wave"]["state"] == registry["phases"][active_phase]["state"]
    assert registry["phases"][last_closed_phase]["state"] == "CLOSED"
    assert registry["phases"][active_phase]["depends_on"] == [last_closed_phase]
    assert registry["phases"][next_phase]["depends_on"] == [active_phase]
    assert plan["approval"]["research_workbench_pivot_authorised_at"] == "2026-08-05"
    assert plan["approval"]["w08_product_path"] == "dormant_optional_module"
    assert registry["phases"]["W08"]["disposition"] == ("DORMANT_BY_RESEARCH_WORKBENCH_PIVOT")
    assert registry["phases"]["W09"]["entry_authority"] == {
        "decision": "RESEARCH_WORKBENCH_PIVOT",
        "authorised_at": "2026-08-05",
        "evidence": "docs/architecture/research-workbench-pivot.md",
    }


def test_task_and_rework_templates_define_every_validator_field() -> None:
    """Both packet formats are complete inputs to the task-return verifier."""
    for path in (
        "orchestration/templates/task_packet.yaml",
        "orchestration/templates/rework_packet.yaml",
    ):
        assert REQUIRED_PACKET_FIELDS <= set(load(path)), path


def test_task_packet_is_bounded_and_deliberately_injects_one_defect() -> None:
    """The drill packet owns only fixture/handback paths and no Git authority."""
    packet = load("orchestration/task_packets/W02-SYNTH-01-R1.yaml")

    assert packet["delegation"] == "forbidden"
    assert packet["git_operations"] == "forbidden"
    assert packet["allowed_paths"] == [
        "tests/fixtures/orchestration/W02-SYNTH-01-subagent-return.yaml",
        "orchestration/reviews/W02-SYNTH-01-return-R1.md",
    ]
    injected = packet["drill_control"]["injected_defect"]
    assert injected["field"] == "scope_confirmation.git_operations_performed"
    assert injected["first_return_value"] == "false"
    assert injected["required_type_after_rework"] == "boolean"


def test_allowed_path_matching_is_exactly_packet_scoped() -> None:
    """Path matching accepts declared writes and rejects adjacent paths."""
    patterns = [
        "tests/fixtures/orchestration/*.yaml",
        "orchestration/reviews/W02-*.md",
    ]
    assert matches_allowed_path(
        "tests/fixtures/orchestration/example.yaml",
        patterns,
    )
    assert matches_allowed_path("orchestration/reviews/W02-return.md", patterns)
    assert not matches_allowed_path("pyproject.toml", patterns)
    assert not matches_allowed_path("orchestration/phase_registry.yaml", patterns)


def test_phase_verifier_keeps_existing_gate_states_and_admits_ready() -> None:
    """READY is eligible for in-progress verification without admitting other states."""
    assert GATE_READY_STATES == {"READY", "VERIFIED", "CHECKPOINTED", "CLOSED"}


def test_empty_task_returns_require_every_packet_to_be_master_assigned() -> None:
    """Only wholly master-owned tasks may omit a delegated return artifact."""
    master_packets = [
        "orchestration/task_packets/W04-SOURCE-AUTHORITY-01-R1.yaml",
        "orchestration/task_packets/W04-SOURCE-AUTHORITY-01-R2.yaml",
    ]
    delegated_packets = [
        "orchestration/task_packets/W04-SOURCE-INGEST-01-R1.yaml",
    ]

    assert packets_are_all_master_assigned(master_packets, "W04-SOURCE-AUTHORITY-01") == (
        True,
        "all referenced packets are complete, master-assigned and task-ID matched",
    )
    assert task_returns_are_evidenced(
        {
            "task_id": "W04-SOURCE-AUTHORITY-01",
            "packets": master_packets,
            "returns": [],
        }
    ) == (
        True,
        "all referenced packets are complete, master-assigned and task-ID matched",
    )
    assert task_returns_are_evidenced(
        {
            "task_id": "W04-SOURCE-ACQUIRE-01",
            "packets": ["orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml"],
            "returns": [],
        }
    ) == (
        True,
        "all referenced packets are complete, master-assigned and task-ID matched",
    )
    delegated_passed, delegated_detail = task_returns_are_evidenced(
        {
            "task_id": "W04-SOURCE-INGEST-01",
            "packets": delegated_packets,
            "returns": [],
        }
    )
    assert delegated_passed is False
    assert delegated_detail == (
        "packet is not master-assigned: orchestration/task_packets/W04-SOURCE-INGEST-01-R1.yaml"
    )


def test_master_return_exemption_fails_closed_for_missing_or_invalid_packets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The exemption cannot be derived from an absent or malformed packet."""
    missing_passed, missing_detail = packets_are_all_master_assigned(
        ["orchestration/task_packets/DOES-NOT-EXIST.yaml"],
        "W04-MISSING-01",
    )
    assert missing_passed is False
    assert "required path does not exist" in missing_detail

    invalid_packet = tmp_path / "invalid-packet.yaml"
    invalid_packet.write_text("assigned_role: [\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.verify_phase.resolve_inside_root",
        lambda _path, *, must_exist: invalid_packet,
    )
    invalid_passed, invalid_detail = packets_are_all_master_assigned(
        ["orchestration/task_packets/INVALID.yaml"],
        "W04-INVALID-01",
    )
    assert invalid_passed is False
    assert "invalid YAML" in invalid_detail


def test_master_return_exemption_rejects_borrowed_packet_task_identity() -> None:
    """A valid master packet for another registry task cannot grant the exemption."""
    borrowed_packet = ["orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml"]

    borrowed_passed, borrowed_detail = task_returns_are_evidenced(
        {
            "task_id": "W04-SOURCE-AUTHORITY-01",
            "packets": borrowed_packet,
            "returns": [],
        }
    )
    assert borrowed_passed is False
    assert borrowed_detail == (
        "packet task ID mismatch: "
        "orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml: "
        "expected 'W04-SOURCE-AUTHORITY-01', got 'W04-SOURCE-ACQUIRE-01'"
    )


def test_master_return_exemption_rejects_invalid_task_id_types(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Registry and packet task identifiers must both be non-empty strings."""
    master_packet = ["orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml"]
    registry_passed, registry_detail = task_returns_are_evidenced(
        {"task_id": 404, "packets": master_packet, "returns": []}
    )
    assert registry_passed is False
    assert registry_detail == ("master-owned return exemption requires a non-empty string task ID")

    missing_task_id_packet = tmp_path / "missing-task-id.yaml"
    missing_task_id_packet.write_text("assigned_role: master\n", encoding="utf-8")
    monkeypatch.setattr(
        "scripts.verify_phase.resolve_inside_root",
        lambda _path, *, must_exist: missing_task_id_packet,
    )
    packet_passed, packet_detail = packets_are_all_master_assigned(
        ["orchestration/task_packets/MISSING-TASK-ID.yaml"],
        "W04-EXPECTED-01",
    )
    assert packet_passed is False
    assert packet_detail.startswith(
        "packet is missing mandatory fields: orchestration/task_packets/MISSING-TASK-ID.yaml:"
    )
    assert "'task_id'" in packet_detail


def test_master_return_exemption_rejects_mixed_packet_ownership(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One delegated packet makes an otherwise matching master packet set ineligible."""
    complete_packet = {field: None for field in REQUIRED_PACKET_FIELDS}
    complete_packet["task_id"] = "W04-MIXED-01"
    master_packet = tmp_path / "master.yaml"
    master_packet.write_text(
        yaml.safe_dump({**complete_packet, "assigned_role": "master"}), encoding="utf-8"
    )
    delegated_packet = tmp_path / "delegated.yaml"
    delegated_packet.write_text(
        yaml.safe_dump({**complete_packet, "assigned_role": "producer"}), encoding="utf-8"
    )
    packet_paths = {
        "orchestration/task_packets/MASTER.yaml": master_packet,
        "orchestration/task_packets/DELEGATED.yaml": delegated_packet,
    }
    monkeypatch.setattr(
        "scripts.verify_phase.resolve_inside_root",
        lambda path, *, must_exist: packet_paths[path],
    )

    mixed_passed, mixed_detail = packets_are_all_master_assigned(
        list(packet_paths),
        "W04-MIXED-01",
    )
    assert mixed_passed is False
    assert mixed_detail == (
        "packet is not master-assigned: orchestration/task_packets/DELEGATED.yaml"
    )


def test_master_return_exemption_rejects_two_field_skeletal_packet(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Matching identity and master role do not make a skeletal mapping a packet."""
    skeletal_packet = tmp_path / "skeletal.yaml"
    skeletal_packet.write_text(
        "task_id: W04-SKELETAL-01\nassigned_role: master\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.verify_phase.resolve_inside_root",
        lambda _path, *, must_exist: skeletal_packet,
    )

    skeletal_passed, skeletal_detail = packets_are_all_master_assigned(
        ["orchestration/task_packets/SKELETAL.yaml"],
        "W04-SKELETAL-01",
    )
    assert skeletal_passed is False
    assert skeletal_detail.startswith(
        "packet is missing mandatory fields: orchestration/task_packets/SKELETAL.yaml:"
    )
    assert "'schema_version'" in skeletal_detail


@pytest.mark.parametrize("missing_field", sorted(REQUIRED_PACKET_FIELDS))
def test_master_return_exemption_requires_each_canonical_packet_field(
    missing_field: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every field in the shared packet contract is mandatory for the exemption."""
    packet = load("orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml")
    packet.pop(missing_field)
    incomplete_packet = tmp_path / f"missing-{missing_field}.yaml"
    incomplete_packet.write_text(yaml.safe_dump(packet), encoding="utf-8")
    packet_path = f"orchestration/task_packets/MISSING-{missing_field}.yaml"
    monkeypatch.setattr(
        "scripts.verify_phase.resolve_inside_root",
        lambda _path, *, must_exist: incomplete_packet,
    )

    passed, detail = packets_are_all_master_assigned(
        [packet_path],
        "W04-SOURCE-ACQUIRE-01",
    )
    assert passed is False
    assert detail == f"packet is missing mandatory fields: {packet_path}: [{missing_field!r}]"


def test_parallel_safety_scenario_suite() -> None:
    """Disjoint work is allowed while shared integration paths are denied."""
    ownership = load("orchestration/ownership.yaml")
    report = scenario_suite(ownership["serial_paths"])

    assert report["status"] == "PASS"
    decisions = {case["id"]: case["decision"] for case in report["scenarios"]}
    assert decisions == {
        "disjoint-fixture-and-readme": "ALLOW",
        "dependency-lock-is-serial": "DENY",
        "contracts-are-serial": "DENY",
        "migrations-are-serial": "DENY",
        "overlapping-scopes-are-serial": "DENY",
    }


def test_parallel_safety_rejects_overlap_even_outside_named_serial_paths() -> None:
    """Two otherwise low-risk scopes cannot overlap."""
    report = evaluate(
        ["docs/architecture/shared/**"],
        ["docs/architecture/shared/result.md"],
        [],
    )
    assert report["decision"] == "DENY"
    assert report["reasons"]
