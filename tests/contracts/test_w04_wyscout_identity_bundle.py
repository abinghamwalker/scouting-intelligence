"""Source-complete executable acceptance tests for the initial W04 identity bundle."""

from __future__ import annotations

import hashlib
from dataclasses import replace
from pathlib import Path
from typing import cast
from uuid import UUID

import pytest
from pydantic import ValidationError

from scouting.contracts.wyscout_identity import (
    WyscoutIdentityBundle,
    WyscoutIdentityEntityKind,
    WyscoutIdentityReviewQueue,
    WyscoutIdentityState,
    identity_bundle_id,
)
from scouting.identity import wyscout

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = ROOT / "data/source/wyscout/v5"
MANIFEST_ROOT = ROOT / "data/manifests"
IDENTITY_ROOT = ROOT / "data/working/wyscout/v5/identity"

EXPECTED_QUEUE_SHA256 = "e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51"
EXPECTED_BUNDLE_SHA256 = "4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80"
EXPECTED_BUNDLE_ID = UUID("31638732-5b25-57db-9eb4-8e943a47a387")
EXPECTED_COUNTS = {
    "COMPETITION:RESOLVED": 7,
    "TEAM:RESOLVED": 142,
    "PLAYER:RESOLVED": 3_603,
    "PLAYER:REVIEW_REQUIRED": 15,
    "PLAYER:REJECTED": 1,
    "MATCH:RESOLVED": 1_826,
}
EXPECTED_QUEUE_REFS = {
    "player:3689": ("matches_Spain.json#88",),
    "player:298776": ("matches_Spain.json#77",),
    "player:302605": ("matches_Germany.json#50",),
    "player:379199": ("matches_England.json#56", "matches_England.json#69"),
    "player:381235": ("matches_France.json#235",),
    "player:447214": ("matches_England.json#68",),
    "player:470819": ("matches_England.json#65",),
    "player:471582": ("matches_France.json#21",),
    "player:475356": ("matches_Italy.json#59",),
    "player:488648": ("matches_Italy.json#59",),
    "player:497353": ("matches_Germany.json#44",),
    "player:503366": (
        "matches_Spain.json#40",
        "matches_Spain.json#46",
        "matches_Spain.json#55",
        "matches_Spain.json#61",
        "matches_Spain.json#71",
        "matches_Spain.json#85",
        "matches_Spain.json#95",
        "matches_Spain.json#104",
    ),
    "player:530062": ("matches_France.json#57",),
    "player:531447": ("matches_Italy.json#83",),
    "player:532900": ("matches_England.json#59",),
}
EXPECTED_TARGETS = {
    (WyscoutIdentityEntityKind.COMPETITION, "competition:364"): (
        "objects/competitions.json",
        1,
        "6a5916b3e5cf86d73a6409f159804eaa62dcef27614129a2e15a52b67207b36a",
        UUID("cb5c5317-fa4a-571e-93dc-ef6ce482eab7"),
    ),
    (WyscoutIdentityEntityKind.TEAM, "team:1609"): (
        "objects/teams.json",
        84,
        "82dbdc6c1ec0ae9da8d63078b3815cb7e2ef84fc29bacac18c85e65b011d9d96",
        UUID("b5f2dd3c-0166-5384-99fa-0ed47cc7e44c"),
    ),
    (WyscoutIdentityEntityKind.TEAM, "team:1631"): (
        "objects/teams.json",
        54,
        "be9e47831f6d86450cd3fa9fb7471e26da691fa793bdc0d06ffb929a757b8a10",
        UUID("5b353635-819b-5bd1-8ca2-5a7364042a96"),
    ),
    (WyscoutIdentityEntityKind.PLAYER, "player:285508"): (
        "objects/players.json",
        757,
        "c6f2f4c5b74563a12cdb78fa49ae295622f5f730ff980fdb220448a4b404e1ac",
        UUID("be8da881-2b15-513f-978f-6bb3865bc8e2"),
    ),
    (WyscoutIdentityEntityKind.MATCH, "match:2499719"): (
        "archive-members/matches_England.json",
        379,
        "1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86",
        UUID("bad97950-6fac-5cf0-a93c-094f91abbb9b"),
    ),
}


@pytest.fixture(scope="module")
def materialized() -> wyscout.WyscoutIdentityMaterialization:
    first = wyscout.materialize_initial_identity_bundle(
        source_root=SOURCE_ROOT,
        manifest_root=MANIFEST_ROOT,
        identity_root=IDENTITY_ROOT,
    )
    second = wyscout._materialize_identity_build(IDENTITY_ROOT, first.build)
    assert second.queue_created is False
    assert second.bundle_created is False
    assert second.build.queue_bytes == first.build.queue_bytes
    assert second.build.bundle_bytes == first.build.bundle_bytes
    return first


def test_exact_source_complete_counts_and_effective_index(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    build = materialized.build
    assert len(build.bundle.current_rows) == 5_594
    assert build.bundle.counts_by_entity_kind_and_effective_state == EXPECTED_COUNTS
    assert len(build.bundle.effective_state_index) == 5_594
    assert tuple(item.evidence_digest for item in build.bundle.effective_state_index) == tuple(
        sorted(item.evidence_digest for item in build.bundle.effective_state_index)
    )
    assert len(build.queue.items) == 15
    assert sum(len(item.source_row_refs) for item in build.queue.items) == 23
    zero = next(
        row for row in build.bundle.current_rows if row.source_identity.source_id == "player:0"
    )
    assert zero.state is WyscoutIdentityState.REJECTED
    assert len(zero.source_row_refs) == 226_041
    assert sum(ref.record_kind.value == "match" for ref in zero.source_row_refs) == 3


def test_exact_target_rows_ordinals_raw_digests_and_canonical_ids(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    rows = {
        (row.entity_kind, row.source_identity.source_id): row
        for row in materialized.build.bundle.current_rows
    }
    for key, (path, ordinal, raw_digest, canonical_id) in EXPECTED_TARGETS.items():
        row = rows[key]
        assert row.state is WyscoutIdentityState.RESOLVED
        assert row.canonical_id == canonical_id
        assert len(row.source_row_refs) == 1
        reference = row.source_row_refs[0]
        assert reference.completion_relative_path == path
        assert reference.source_record_ordinal == ordinal
        assert reference.raw_record_sha256 == raw_digest


def test_queue_is_exact_23_to_15_aggregation(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    actual = {
        item.source_identity.source_id: tuple(
            f"{Path(ref.completion_relative_path).name}#{ref.source_record_ordinal}"
            for ref in item.source_row_refs
        )
        for item in materialized.build.queue.items
    }
    assert actual == EXPECTED_QUEUE_REFS
    assert all(
        item.source_identity.source_id != "player:0" for item in materialized.build.queue.items
    )


def test_eight_substitution_zero_occurrences_are_rejected_not_queued(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    zero_occurrences = 0
    zero_parent_refs: set[tuple[str, int]] = set()
    for spec in wyscout._MATCH_MEMBERS:
        for ordinal, row in wyscout._iter_verified_rows(SOURCE_ROOT, spec):
            teams_data = cast(dict[str, object], row["teamsData"])
            for team_key, team_value in teams_data.items():
                team = cast(dict[str, object], team_value)
                if team.get("formation") is None and team.get("hasFormation") == 0:
                    continue
                player_ids = wyscout._formation_player_ids(
                    team["formation"],
                    context=f"{spec.path}[{ordinal}].teamsData[{team_key}]",
                )
                count = player_ids.count(0)
                zero_occurrences += count
                if count:
                    zero_parent_refs.add((spec.path, ordinal))
    assert zero_occurrences == 8
    assert len(zero_parent_refs) == 3
    zero = next(
        row
        for row in materialized.build.bundle.current_rows
        if row.source_identity.source_id == "player:0"
    )
    assert zero_parent_refs <= {
        (ref.completion_relative_path, ref.source_record_ordinal) for ref in zero.source_row_refs
    }


def test_addresses_bytes_and_recursive_readback_are_exact(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    build = materialized.build
    assert build.queue_sha256 == EXPECTED_QUEUE_SHA256
    assert build.bundle_sha256 == EXPECTED_BUNDLE_SHA256
    assert build.bundle_id == EXPECTED_BUNDLE_ID == identity_bundle_id(build.bundle_sha256)
    assert hashlib.sha256(build.queue_bytes).hexdigest() == build.queue_sha256
    assert hashlib.sha256(build.bundle_bytes).hexdigest() == build.bundle_sha256
    assert build.queue_bytes.endswith(b"\n") and not build.queue_bytes.endswith(b"\n\n")
    assert build.bundle_bytes.endswith(b"\n") and not build.bundle_bytes.endswith(b"\n\n")
    assert (IDENTITY_ROOT / build.queue_relative_path).read_bytes() == build.queue_bytes
    assert (IDENTITY_ROOT / build.bundle_relative_path).read_bytes() == build.bundle_bytes
    assert build.bundle.review_queue_sha256 == build.queue_sha256
    assert build.bundle.review_queue_path == build.queue_relative_path
    wyscout._verify_reopened(IDENTITY_ROOT, build)


def test_bundle_and_queue_omission_duplication_reorder_stale_and_clock_fail(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    build = materialized.build
    bundle = build.bundle.model_dump(mode="python")
    rows = build.bundle.current_rows
    queue = build.queue.model_dump(mode="python")

    bundle_mutations = (
        {"current_rows": rows[:-1]},
        {"current_rows": rows[:-1] + (rows[-2], rows[-1])},
        {"current_rows": (rows[1], rows[0], *rows[2:])},
        {"prior_identity_bundle_sha256": "f" * 64},
        {"identity_accepted_at": build.bundle.identity_accepted_at.replace(second=25)},
        {"identity_ruleset_sha256": "f" * 64},
    )
    for mutation in bundle_mutations:
        with pytest.raises(ValidationError):
            WyscoutIdentityBundle.model_validate(dict(bundle, **mutation))

    queue_mutations = (
        {"items": build.queue.items[:-1]},
        {"items": build.queue.items + (build.queue.items[-1],)},
        {"items": (build.queue.items[1], build.queue.items[0], *build.queue.items[2:])},
        {"prior_queue_sha256": "f" * 64},
    )
    for mutation in queue_mutations:
        with pytest.raises(ValidationError):
            WyscoutIdentityReviewQueue.model_validate(dict(queue, **mutation))


def test_wrong_root_path_scan_and_immutable_conflict_fail_closed(
    materialized: wyscout.WyscoutIdentityMaterialization,
    tmp_path: Path,
) -> None:
    with pytest.raises(wyscout.WyscoutIdentityPathError):
        wyscout.build_initial_identity_bundle(
            source_root=tmp_path,
            manifest_root=MANIFEST_ROOT,
        )
    unequal = replace(materialized.build, bundle_bytes=b"unequal\n")
    with pytest.raises(wyscout.WyscoutIdentityConflictError):
        wyscout._materialize_identity_build(IDENTITY_ROOT, unequal)


def test_only_the_two_content_addressed_sidecar_free_files_exist(
    materialized: wyscout.WyscoutIdentityMaterialization,
) -> None:
    build = materialized.build
    assert wyscout._identity_inventory(IDENTITY_ROOT) == {
        "review-queues": (Path(build.queue_relative_path).name,),
        "bundles": (Path(build.bundle_relative_path).name,),
    }
