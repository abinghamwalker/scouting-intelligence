"""Build the fresh, isolated historical-player-comparison pilot authority."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import duckdb

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scouting.contracts.expert_relevance import MdEvidenceSubrubricV2
from scouting.data_products.wyscout.expert_evidence import (
    build_expert_evidence_bundles_v2,
    build_participant_evidence_comparison_v2,
    load_expert_evidence_policy_v2,
    load_production_evidence_inputs_v2,
    participant_safe_comparison_bytes_v2,
)
from scouting.storage.expert_study import (
    HISTORICAL_COMPARISON_AUTHORITY_VERSION,
    HISTORICAL_COMPARISON_DEBRIEF_VERSION,
    HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
    HISTORICAL_COMPARISON_RESPONSE_VERSION,
)
from scouting.storage.formats import canonical_json_bytes

ROOT = Path(__file__).resolve().parents[1]
PILOT_ROOT = ROOT / "data/working/w10/study/v2/pilot"
STOPPED_AUTHORITY = PILOT_ROOT / "mechanics-pilot-authority-v1.json"
STOPPED_SEPARATION = PILOT_ROOT / "pilot-pack-separation-v1.json"
STOPPED_DATABASE = PILOT_ROOT / "mechanics-pilot-v2.sqlite3"
WITHDRAWN_QUERY_PACK = ROOT / "configs/evaluation/w10-frozen-query-pack-v1.json"
DEFAULT_AUTHORITY = PILOT_ROOT / "historical-player-comparison-pilot-authority-v1.json"
DEFAULT_SEPARATION = PILOT_ROOT / "pilot-pack-separation-v2.json"
DEFAULT_DATABASE = PILOT_ROOT / "historical-player-comparison-pilot-v1.sqlite3"
SELECTION_SALT = "historical-player-comparison-pilot-pack-v1-deterministic-selection"
EXPECTED_STOPPED_HASHES = {
    STOPPED_AUTHORITY: "33684b88c683b8e565757972ab78e558a0e29dfad7ddcb94fd659dfb631a4791",
    STOPPED_SEPARATION: "559a40c5adc7f803dfb017e26ec35d3cfdcd7f3c3de4ba4dd3e4b04c5f31c1e4",
    STOPPED_DATABASE: "b5e5f35bdbd8acf6ef1827cb2480f65440ce74b44b924418cac6d7553ad393a2",
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-output", type=Path, default=DEFAULT_AUTHORITY)
    parser.add_argument("--separation-output", type=Path, default=DEFAULT_SEPARATION)
    parser.add_argument("--database-path", type=Path, default=DEFAULT_DATABASE)
    return parser


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _write_once(path: Path, payload: bytes) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to replace incompatible authority bytes: {path}")
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


def _eligible_grains(action_paths: Sequence[Path]) -> dict[str, dict[str, bool]]:
    query = """
        SELECT player_id::VARCHAR player_id,
               competition_id::VARCHAR competition_id,
               season_id::VARCHAR season_id,
               count(*) total,
               count(*) FILTER (WHERE coordinate_evidence_state='valid') valid_starts,
               count(*) FILTER (WHERE event_id=8) passes,
               count(*) FILTER (WHERE event_id=1) duels,
               count(*) FILTER (WHERE event_id=1 AND sub_event_id=12
                                AND coordinate_evidence_state='valid') defending_duels,
               count(*) FILTER (WHERE list_contains(tag_ids,1401)
                                AND coordinate_evidence_state='valid') interceptions,
               count(*) FILTER (WHERE sub_event_id=71
                                AND coordinate_evidence_state='valid') clearances,
               count(*) FILTER (WHERE event_id=10
                                AND coordinate_evidence_state='valid') shots,
               count(*) FILTER (WHERE event_id=9 AND sub_event_id IN (90,91)) saves,
               count(*) FILTER (WHERE event_id=4 AND sub_event_id=40) leaves,
               count(*) FILTER (WHERE event_id=3 AND sub_event_id=34) kicks
        FROM read_parquet(?)
        WHERE player_id IS NOT NULL
        GROUP BY ALL
    """
    cursor = duckdb.connect().execute(query, [[str(path) for path in action_paths]])
    columns = [item[0] for item in cursor.description]
    result: dict[str, dict[str, bool]] = {}
    for values in cursor.fetchall():
        row = dict(zip(columns, values, strict=True))
        grain_id = (
            f"player={row['player_id']}|competition={row['competition_id']}|"
            f"season={row['season_id']}"
        )
        total = int(row["total"])
        valid = int(row["valid_starts"])
        common = valid >= 100 and total > 0 and valid / total >= 0.95 and int(row["passes"]) >= 25
        result[grain_id] = {
            "common": common,
            "duel": int(row["duels"]) >= 20,
            "defensive": (
                int(row["defending_duels"]) >= 5
                and int(row["interceptions"]) >= 5
                and int(row["clearances"]) >= 3
            ),
            "shooting": int(row["shots"]) >= 10,
            "goalkeeper": (
                int(row["saves"]) >= 10 and int(row["leaves"]) >= 3 and int(row["kicks"]) >= 20
            ),
        }
    return result


def _select(
    matrix: Any,
    eligible: Mapping[str, Mapping[str, bool]],
    *,
    excluded_grains: set[str],
    excluded_players: set[str],
) -> tuple[tuple[str, str, MdEvidenceSubrubricV2 | None], ...]:
    specifications = (
        ("GK", "GK", None),
        ("DF", "DF", None),
        ("MD_DEFENSIVE", "MD", MdEvidenceSubrubricV2.DEFENSIVE),
        ("MD_SHOOTING", "MD", MdEvidenceSubrubricV2.SHOOTING),
        ("FW", "FW", None),
    )
    selected: list[tuple[str, str, MdEvidenceSubrubricV2 | None]] = []
    used_players: set[str] = set()
    for stratum, position, branch in specifications:
        candidates = []
        for row in matrix.rows:
            flags = eligible.get(row.grain_id)
            if (
                row.position_code != position
                or row.grain_id in excluded_grains
                or str(row.player_id) in excluded_players
                or str(row.player_id) in used_players
                or flags is None
                or not flags["common"]
            ):
                continue
            admitted = (
                flags["goalkeeper"]
                if position == "GK"
                else flags["duel"] and flags["defensive"]
                if position == "DF" or branch is MdEvidenceSubrubricV2.DEFENSIVE
                else flags["duel"] and flags["shooting"]
            )
            if admitted:
                order = hashlib.sha256(
                    f"{SELECTION_SALT}\0{stratum}\0{row.grain_id}".encode()
                ).digest()
                candidates.append((order, row.grain_id, str(row.player_id)))
        chosen = sorted(candidates)[:2]
        if len(chosen) != 2:
            raise ValueError(f"fresh {stratum} pilot stratum has fewer than two eligible rows")
        for _order, _grain, player_id in chosen:
            used_players.add(player_id)
        selected.append((chosen[0][1], chosen[1][1], branch))
    return tuple(selected)


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        for path, expected in EXPECTED_STOPPED_HASHES.items():
            if _sha256(path) != expected:
                raise ValueError(f"preserved stopped-pilot identity differs: {path}")
        if arguments.database_path.exists():
            raise FileExistsError(
                "new participant database must be absent before pilot handoff: "
                f"{arguments.database_path}"
            )
        old_separation = json.loads(STOPPED_SEPARATION.read_bytes())
        withdrawn_pack = json.loads(WITHDRAWN_QUERY_PACK.read_bytes())
        withdrawn_grains, withdrawn_players = _withdrawn_roster(withdrawn_pack)
        stopped_grains = set(old_separation["future_formal_excluded_grain_ids"])
        stopped_players = set(old_separation["future_formal_excluded_player_ids"])
        matrix, action_paths = load_production_evidence_inputs_v2()
        policy = load_expert_evidence_policy_v2()
        selections = _select(
            matrix,
            _eligible_grains(action_paths),
            excluded_grains=withdrawn_grains | stopped_grains,
            excluded_players=withdrawn_players | stopped_players,
        )
        grain_ids = tuple(grain for pair in selections for grain in pair[:2])
        branches = {
            grain: branch
            for exemplar, candidate, branch in selections
            if branch is not None
            for grain in (exemplar, candidate)
        }
        bundles = build_expert_evidence_bundles_v2(
            matrix,
            action_paths=action_paths,
            selected_grain_ids=grain_ids,
            md_subrubrics=branches,
        )
        by_grain = dict(zip(grain_ids, bundles, strict=True))
        comparisons = tuple(
            build_participant_evidence_comparison_v2(by_grain[exemplar], by_grain[candidate])
            for exemplar, candidate, _branch in selections
        )
        authority = {
            "schema_version": 3,
            "authority_version": HISTORICAL_COMPARISON_AUTHORITY_VERSION,
            "participant_contract_version": HISTORICAL_COMPARISON_PARTICIPANT_VERSION,
            "response_contract_version": HISTORICAL_COMPARISON_RESPONSE_VERSION,
            "debrief_contract_version": HISTORICAL_COMPARISON_DEBRIEF_VERSION,
            "lane": "MECHANICS_PILOT",
            "comparisons": [item.model_dump(mode="json") for item in comparisons],
        }
        authority_bytes = canonical_json_bytes(authority)
        authority_digest = hashlib.sha256(authority_bytes).hexdigest()
        rows = {row.grain_id: row for row in matrix.rows}
        new_grains = set(grain_ids)
        new_players = {str(rows[grain].player_id) for grain in grain_ids}
        if new_grains & (withdrawn_grains | stopped_grains) or new_players & (
            withdrawn_players | stopped_players
        ):
            raise ValueError("fresh pilot selection intersects protected historical exposure")
        strata = []
        labels = ("GK", "DF", "MD_DEFENSIVE", "MD_SHOOTING", "FW")
        for label, (exemplar, candidate, _branch), comparison in zip(
            labels, selections, comparisons, strict=True
        ):
            strata.append(
                {
                    "stratum": label,
                    "exemplar_grain_id": exemplar,
                    "exemplar_player_id": str(rows[exemplar].player_id),
                    "exemplar_display_name": rows[exemplar].display_name,
                    "candidate_grain_id": candidate,
                    "candidate_player_id": str(rows[candidate].player_id),
                    "candidate_display_name": rows[candidate].display_name,
                    "participant_comparison_digest": comparison.comparison_digest,
                }
            )
        separation = {
            "schema_version": 2,
            "pack_id": "historical-player-comparison-pilot-pack-v1",
            "purpose": "OPERATOR_ONLY_PILOT_FORMAL_SEPARATION_AUTHORITY_NOT_PARTICIPANT_BYTES",
            "must_not_be_served_to_participants": True,
            "mechanics_pilot_counts_toward_g_rw4": False,
            "selection_salt": SELECTION_SALT,
            "selection_rule": (
                "Exclude every withdrawn-v1-pack and stopped-pilot grain and canonical player; "
                "within GK, DF, MD defensive, MD shooting and FW, retain rows meeting the exact "
                "accepted evidence-availability floors, order by SHA-256 of the fixed salt, "
                "stratum and grain ID, and take two without player reuse."
            ),
            "canonical_build_id": policy.canonical_build_id,
            "matrix_version": policy.matrix_version,
            "matrix_digest": policy.matrix_digest,
            "evidence_policy_digest": policy.policy_digest,
            "participant_authority_path": str(arguments.authority_output.relative_to(ROOT)),
            "participant_authority_sha256": authority_digest,
            "new_database_path": str(arguments.database_path.relative_to(ROOT)),
            "new_database_required_state_at_handoff": "ABSENT",
            "stopped_database_sha256": EXPECTED_STOPPED_HASHES[STOPPED_DATABASE],
            "stopped_authority_sha256": EXPECTED_STOPPED_HASHES[STOPPED_AUTHORITY],
            "superseded_separation_authority_sha256": EXPECTED_STOPPED_HASHES[STOPPED_SEPARATION],
            "withdrawn_v1_query_pack_digest": withdrawn_pack["query_pack_digest"],
            "withdrawn_v1_grain_intersection": [],
            "stopped_pilot_grain_intersection": [],
            "stopped_pilot_player_intersection": [],
            "future_formal_pack_status": "ABSENT_AND_UNSTARTED",
            "future_formal_excluded_grain_ids": sorted(stopped_grains | new_grains),
            "future_formal_excluded_player_ids": sorted(stopped_players | new_players),
            "future_formal_exclusion_rule": (
                "Every listed canonical player ID and grain ID exposed in either mechanics "
                "pilot is prohibited from every future formal exemplar or candidate pack."
            ),
            "strata": strata,
        }
        separation_bytes = canonical_json_bytes(separation)
        if any(
            participant_safe_comparison_bytes_v2(item)
            != canonical_json_bytes(item.model_dump(mode="json"))
            for item in comparisons
        ):
            raise ValueError("participant comparison bytes failed safe reconstruction")
        _write_once(arguments.authority_output, authority_bytes)
        _write_once(arguments.separation_output, separation_bytes)
        print(
            json.dumps(
                {
                    "authority_sha256": authority_digest,
                    "authority_bytes": len(authority_bytes),
                    "separation_sha256": hashlib.sha256(separation_bytes).hexdigest(),
                    "separation_bytes": len(separation_bytes),
                    "comparison_count": len(comparisons),
                    "database_absent": not arguments.database_path.exists(),
                },
                sort_keys=True,
            )
        )
    except (FileExistsError, OSError, ValueError, duckdb.Error) as exc:
        print(f"Historical comparison pilot build failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
