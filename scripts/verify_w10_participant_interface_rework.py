"""Verify preserved and fresh W10 participant-pilot identities without creating study state."""

from __future__ import annotations

import hashlib
import json
import socket
import sqlite3
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from scouting.contracts.expert_relevance import ParticipantEvidenceComparisonV2
from scouting.data_products.wyscout.expert_evidence import participant_safe_comparison_bytes_v2
from scouting.storage.expert_study import (
    HISTORICAL_COMPARISON_SCHEMA_SQL_DIGEST,
    HistoricalComparisonPilotStore,
)
from scouting.storage.formats import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = ROOT / "data/working/w10/study/v2/pilot"
STOPPED_DATABASE = PILOT_ROOT / "mechanics-pilot-v2.sqlite3"
STOPPED_AUTHORITY = PILOT_ROOT / "mechanics-pilot-authority-v1.json"
STOPPED_SEPARATION = PILOT_ROOT / "pilot-pack-separation-v1.json"
NEW_DATABASE = PILOT_ROOT / "historical-player-comparison-pilot-v1.sqlite3"
NEW_AUTHORITY = PILOT_ROOT / "historical-player-comparison-pilot-authority-v1.json"
NEW_SEPARATION = PILOT_ROOT / "pilot-pack-separation-v2.json"
WITHDRAWN_PACK = ROOT / "configs/evaluation/w10-frozen-query-pack-v1.json"
EXPECTED_STOPPED_HASHES = {
    STOPPED_DATABASE: "b5e5f35bdbd8acf6ef1827cb2480f65440ce74b44b924418cac6d7553ad393a2",
    STOPPED_AUTHORITY: "33684b88c683b8e565757972ab78e558a0e29dfad7ddcb94fd659dfb631a4791",
    STOPPED_SEPARATION: "559a40c5adc7f803dfb017e26ec35d3cfdcd7f3c3de4ba4dd3e4b04c5f31c1e4",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _canonical_object(path: Path) -> Mapping[str, Any]:
    raw = path.read_bytes()
    decoded = json.loads(raw)
    if type(decoded) is not dict or canonical_json_bytes(decoded) != raw:
        raise AssertionError(f"not exact canonical JSON: {path}")
    return decoded


def _withdrawn_roster(payload: Mapping[str, Any]) -> tuple[set[str], set[str]]:
    grains: set[str] = set()
    players: set[str] = set()
    for query in payload["queries"]:
        grains.add(query["exemplar_grain_id"])
        players.add(query["exemplar_player_id"])
        for candidate in query["candidates"]:
            grains.add(candidate["grain_id"])
            players.add(candidate["player_id"])
    return grains, players


def _port_is_closed(port: int) -> bool:
    with socket.socket() as probe:
        probe.settimeout(0.2)
        return probe.connect_ex(("127.0.0.1", port)) != 0


def main() -> int:
    for path, expected in EXPECTED_STOPPED_HASHES.items():
        _require(_sha256(path) == expected, f"preserved identity changed: {path}")
    _require(not NEW_DATABASE.exists(), "new human-study database must remain absent")
    _require(
        all(_port_is_closed(port) for port in (8770, 8771)),
        "study port remains open",
    )

    with sqlite3.connect(STOPPED_DATABASE) as connection:
        stopped_state = {
            "integrity": connection.execute("PRAGMA integrity_check").fetchone()[0],
            "sessions": connection.execute("SELECT count(*) FROM v2_sessions").fetchone()[0],
            "completed_sessions": connection.execute(
                "SELECT count(*) FROM v2_sessions WHERE complete=1"
            ).fetchone()[0],
            "current_judgements": connection.execute(
                "SELECT count(*) FROM v2_judgements"
            ).fetchone()[0],
            "revision_rows": connection.execute(
                "SELECT count(*) FROM v2_judgement_revisions"
            ).fetchone()[0],
            "completion_receipts": connection.execute(
                "SELECT count(*) FROM v2_completions"
            ).fetchone()[0],
        }
    _require(
        stopped_state
        == {
            "integrity": "ok",
            "sessions": 1,
            "completed_sessions": 0,
            "current_judgements": 2,
            "revision_rows": 2,
            "completion_receipts": 0,
        },
        "stopped pilot aggregate state changed",
    )

    stopped_separation = _canonical_object(STOPPED_SEPARATION)
    new_separation = _canonical_object(NEW_SEPARATION)
    withdrawn_pack = _canonical_object(WITHDRAWN_PACK)
    authority = _canonical_object(NEW_AUTHORITY)
    authority_sha256 = _sha256(NEW_AUTHORITY)
    separation_sha256 = _sha256(NEW_SEPARATION)
    _require(
        new_separation["participant_authority_sha256"] == authority_sha256,
        "separation authority does not bind the participant authority",
    )
    _require(
        new_separation["new_database_required_state_at_handoff"] == "ABSENT",
        "new database handoff state is not ABSENT",
    )
    _require(
        new_separation["future_formal_pack_status"] == "ABSENT_AND_UNSTARTED",
        "future formal pack is not absent and unstarted",
    )

    old_grains = set(stopped_separation["future_formal_excluded_grain_ids"])
    old_players = set(stopped_separation["future_formal_excluded_player_ids"])
    new_grains = {
        value
        for row in new_separation["strata"]
        for value in (row["exemplar_grain_id"], row["candidate_grain_id"])
    }
    new_players = {
        value
        for row in new_separation["strata"]
        for value in (row["exemplar_player_id"], row["candidate_player_id"])
    }
    withdrawn_grains, withdrawn_players = _withdrawn_roster(withdrawn_pack)
    _require(
        not new_grains.intersection(old_grains | withdrawn_grains),
        "new pilot grains overlap a stopped or withdrawn pack",
    )
    _require(
        not new_players.intersection(old_players | withdrawn_players),
        "new pilot players overlap a stopped or withdrawn pack",
    )
    _require(
        set(new_separation["future_formal_excluded_grain_ids"]) == old_grains | new_grains,
        "future formal grain exclusion roster is incomplete",
    )
    _require(
        set(new_separation["future_formal_excluded_player_ids"]) == old_players | new_players,
        "future formal player exclusion roster is incomplete",
    )
    _require(
        [row["stratum"] for row in new_separation["strata"]]
        == ["GK", "DF", "MD_DEFENSIVE", "MD_SHOOTING", "FW"],
        "pilot strata do not cover the required position groups",
    )

    comparisons = tuple(
        ParticipantEvidenceComparisonV2.model_validate_json(canonical_json_bytes(item))
        for item in authority["comparisons"]
    )
    _require(len(comparisons) == 5, "participant authority must contain five comparisons")
    for raw, comparison in zip(authority["comparisons"], comparisons, strict=True):
        _require(
            participant_safe_comparison_bytes_v2(comparison) == canonical_json_bytes(raw),
            "participant-safe comparison reconstruction changed authority bytes",
        )
        left_schema = tuple(
            (
                family.family_id,
                family.mandatory_for_selected_rubric,
                tuple(metric.metric_id for metric in family.metrics),
            )
            for family in comparison.exemplar.independent_descriptors
        )
        right_schema = tuple(
            (
                family.family_id,
                family.mandatory_for_selected_rubric,
                tuple(metric.metric_id for metric in family.metrics),
            )
            for family in comparison.candidate.independent_descriptors
        )
        _require(left_schema == right_schema, "player evidence schemas are not identical")

    store = HistoricalComparisonPilotStore(
        database_path=NEW_DATABASE,
        authority_path=NEW_AUTHORITY,
        allowed_root=PILOT_ROOT,
    )
    _require(store.authority_digest == authority_sha256, "store authority digest changed")
    _require(
        not NEW_DATABASE.exists(),
        "authority verification created human-study state",
    )
    result = {
        "stopped_hashes": {path.name: value for path, value in EXPECTED_STOPPED_HASHES.items()},
        "stopped_state": stopped_state,
        "new_authority_sha256": authority_sha256,
        "new_separation_sha256": separation_sha256,
        "new_database_absent": True,
        "new_comparisons": len(comparisons),
        "new_exposed_grains": len(new_grains),
        "new_exposed_players": len(new_players),
        "future_formal_excluded_grains": len(old_grains | new_grains),
        "future_formal_excluded_players": len(old_players | new_players),
        "sqlite_schema_digest": HISTORICAL_COMPARISON_SCHEMA_SQL_DIGEST,
        "ports_closed": [8770, 8771],
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
