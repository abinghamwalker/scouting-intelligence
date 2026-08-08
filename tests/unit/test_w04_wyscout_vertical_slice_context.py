"""Adversarial tests for the read-only W04 selected-match context adapter."""

from __future__ import annotations

import hashlib
import json
import os
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from scouting.contracts.wyscout_identity import (
    WyscoutIdentityEntityKind,
    WyscoutIdentityState,
)
from scouting.identity import wyscout as identity_runtime
from scouting.sources import wyscout_completion_index as completion
from scouting.sources import wyscout_vertical_slice as context

REAL_MATCH_MEMBER = Path("data/source/wyscout/v5/archive-members/matches_England.json").read_bytes()


@pytest.fixture(scope="module")
def accepted_event_population() -> completion.VerifiedMatchPopulation:
    return completion.load_verified_match_population(
        source_root=Path("data/source/wyscout/v5"),
        manifest_root=Path("data/manifests"),
        index_sha256=context.SOURCE_COMPLETION_INDEX_SHA256,
        source_member_path=context.EVENT_MEMBER_PATH,
        match_source_id=context.MATCH_SOURCE_ID,
    )


def _identity_row(
    entity_kind: WyscoutIdentityEntityKind,
    source_id: int,
    canonical_id: object,
) -> SimpleNamespace:
    return SimpleNamespace(
        entity_kind=entity_kind,
        source_identity=SimpleNamespace(source_id=f"{entity_kind.value.lower()}:{source_id}"),
        state=WyscoutIdentityState.RESOLVED,
        canonical_id=canonical_id,
    )


def _identity_build(*, player_id: object = context.TARGET_PLAYER_ID) -> SimpleNamespace:
    rows = (
        _identity_row(
            WyscoutIdentityEntityKind.COMPETITION,
            context.COMPETITION_SOURCE_ID,
            context.COMPETITION_ID,
        ),
        _identity_row(
            WyscoutIdentityEntityKind.TEAM,
            context.TEAM_SOURCE_IDS[0],
            context.TEAM_IDS[0],
        ),
        _identity_row(
            WyscoutIdentityEntityKind.TEAM,
            context.TEAM_SOURCE_IDS[1],
            context.TEAM_IDS[1],
        ),
        _identity_row(
            WyscoutIdentityEntityKind.PLAYER,
            context.TARGET_PLAYER_SOURCE_ID,
            player_id,
        ),
        _identity_row(
            WyscoutIdentityEntityKind.MATCH,
            context.MATCH_SOURCE_ID,
            context.MATCH_ID,
        ),
    )
    return SimpleNamespace(
        bundle_sha256=context.IDENTITY_BUNDLE_SHA256,
        bundle_id=context.IDENTITY_BUNDLE_ID,
        bundle=SimpleNamespace(
            source_manifest_id=context.SOURCE_MANIFEST_ID,
            source_manifest_sha256=context.SOURCE_MANIFEST_SHA256,
            current_rows=rows,
        ),
    )


def _exact_mirror(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Path]:
    repository = tmp_path / "repository"
    source = repository / context._SOURCE_ROOT_RELATIVE
    manifests = repository / context._MANIFEST_ROOT_RELATIVE
    identities = repository / context._IDENTITY_ROOT_RELATIVE
    (source / "archive-members").mkdir(parents=True, mode=0o700)
    manifests.mkdir(parents=True, mode=0o700)
    identities.mkdir(parents=True, mode=0o700)
    target = source / context.MATCH_MEMBER_PATH
    target.write_bytes(REAL_MATCH_MEMBER)
    os.chmod(target, 0o600)
    monkeypatch.setattr(context, "_PROJECT_ROOT", repository)
    return source, manifests, identities


def _load(
    source: Path,
    manifests: Path,
    identities: Path,
) -> context.VerifiedMatchContext:
    return context.load_verified_match_context(
        source_root=source,
        manifest_root=manifests,
        identity_root=identities,
        source_manifest_sha256=context.SOURCE_MANIFEST_SHA256,
        source_completion_index_sha256=context.SOURCE_COMPLETION_INDEX_SHA256,
        identity_bundle_sha256=context.IDENTITY_BUNDLE_SHA256,
    )


def _patch_accepted_joins(
    monkeypatch: pytest.MonkeyPatch,
    accepted_event_population: completion.VerifiedMatchPopulation,
    *,
    identity_build: object | None = None,
) -> None:
    monkeypatch.setattr(
        identity_runtime,
        "load_initial_identity_bundle",
        lambda **_kwargs: identity_build or _identity_build(),
    )
    monkeypatch.setattr(
        completion,
        "load_verified_match_population",
        lambda **_kwargs: accepted_event_population,
    )


def _selected_rows() -> list[dict[str, object]]:
    return context._decode_match_member(REAL_MATCH_MEMBER)


def _selected_row() -> dict[str, object]:
    return deepcopy(_selected_rows()[context.MATCH_SOURCE_RECORD_ORDINAL])


def _bind_mutated_raw_digest(monkeypatch: pytest.MonkeyPatch, row: dict[str, object]) -> None:
    monkeypatch.setattr(
        context,
        "MATCH_RAW_RECORD_SHA256",
        hashlib.sha256(completion._canonical_value_bytes(row)).hexdigest(),
    )


def test_exact_positive_context_reproduces_every_fixed_binding_and_is_immutable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    accepted_event_population: completion.VerifiedMatchPopulation,
) -> None:
    source, manifests, identities = _exact_mirror(tmp_path, monkeypatch)
    _patch_accepted_joins(monkeypatch, accepted_event_population)

    before = tuple(sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*")))
    loaded = _load(source, manifests, identities)
    after = tuple(sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*")))

    assert before == after
    assert loaded.source_manifest_id == context.SOURCE_MANIFEST_ID
    assert loaded.source_manifest_sha256 == context.SOURCE_MANIFEST_SHA256
    assert loaded.identity_bundle_id == context.IDENTITY_BUNDLE_ID
    assert loaded.identity_bundle_sha256 == context.IDENTITY_BUNDLE_SHA256
    assert loaded.match_source_row.source_record_ordinal == 379
    assert loaded.match_source_row.raw_record_sha256 == context.MATCH_RAW_RECORD_SHA256
    assert loaded.match.canonical_id == context.MATCH_ID
    assert loaded.competition.canonical_id == context.COMPETITION_ID
    assert loaded.season_source_id == 181_150
    assert loaded.season_id == context.SEASON_ID
    assert tuple(team.source_id for team in loaded.teams) == (1_609, 1_631)
    assert loaded.target_team.canonical_id == context.TEAM_IDS[1]
    assert loaded.target_player.canonical_id == context.TARGET_PLAYER_ID
    assert loaded.match_start_utc == "2017-08-11T18:45:00Z"
    assert loaded.target_substitution_minute == 82
    assert loaded.period_action_counts == (("1H", 901), ("2H", 867))
    assert loaded.period_membership_sha256 == tuple(row[2] for row in context._EXPECTED_PERIODS)
    assert hashlib.sha256(loaded.canonical_raw_match).hexdigest() == (
        context.MATCH_RAW_RECORD_SHA256
    )
    with pytest.raises(TypeError):
        cast(Any, loaded.raw_match)["wyId"] = 1
    with pytest.raises(TypeError):
        cast(Any, loaded.raw_match["teamsData"])["1631"] = {}
    target_bench = cast(Any, loaded.raw_match["teamsData"])["1631"]["formation"]["bench"]
    with pytest.raises(TypeError):
        target_bench[0]["playerId"] = 1
    with pytest.raises(FrozenInstanceError):
        loaded.match_start_utc = "2017-08-12T00:00:00Z"  # type: ignore[misc]


@pytest.mark.parametrize("root_name", ("source", "manifests", "identities"))
@pytest.mark.parametrize("attack", ("relative", "alternate"))
def test_loader_rejects_every_nonexact_or_nonabsolute_root_before_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    root_name: str,
    attack: str,
) -> None:
    source, manifests, identities = _exact_mirror(tmp_path, monkeypatch)
    roots = {"source": source, "manifests": manifests, "identities": identities}
    relative_roots = {
        "source": context._SOURCE_ROOT_RELATIVE,
        "manifests": context._MANIFEST_ROOT_RELATIVE,
        "identities": context._IDENTITY_ROOT_RELATIVE,
    }
    roots[root_name] = (
        relative_roots[root_name] if attack == "relative" else tmp_path / f"alternate-{root_name}"
    )
    with pytest.raises(context.WyscoutVerticalSliceContextPathError, match="exact absolute"):
        _load(roots["source"], roots["manifests"], roots["identities"])


@pytest.mark.parametrize(
    ("argument", "value"),
    (
        ("source_manifest_sha256", "f" * 64),
        ("source_completion_index_sha256", "f" * 64),
        ("identity_bundle_sha256", "f" * 64),
        ("source_manifest_sha256", True),
    ),
)
def test_loader_rejects_digest_drift_before_authority_load(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    argument: str,
    value: object,
) -> None:
    source, manifests, identities = _exact_mirror(tmp_path, monkeypatch)
    invoked = False

    def forbidden(**_kwargs: object) -> None:
        nonlocal invoked
        invoked = True
        raise AssertionError("drift reached identity authority")

    monkeypatch.setattr(identity_runtime, "load_initial_identity_bundle", forbidden)
    values: dict[str, object] = {
        "source_root": source,
        "manifest_root": manifests,
        "identity_root": identities,
        "source_manifest_sha256": context.SOURCE_MANIFEST_SHA256,
        "source_completion_index_sha256": context.SOURCE_COMPLETION_INDEX_SHA256,
        "identity_bundle_sha256": context.IDENTITY_BUNDLE_SHA256,
    }
    values[argument] = value
    with pytest.raises(context.WyscoutVerticalSliceContextError, match="digest argument"):
        context.load_verified_match_context(**cast(Any, values))
    assert invoked is False


@pytest.mark.parametrize("attack", ("truncated", "additional", "unsafe_mode"))
def test_exact_member_reader_rejects_physical_byte_or_mode_attack(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    source, _manifests, _identities = _exact_mirror(tmp_path, monkeypatch)
    target = source / context.MATCH_MEMBER_PATH
    if attack == "truncated":
        target.write_bytes(REAL_MATCH_MEMBER[:-1])
    elif attack == "additional":
        target.write_bytes(REAL_MATCH_MEMBER + b" ")
    else:
        os.chmod(target, 0o644)
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._read_exact_match_member(source)


@pytest.mark.parametrize("attack", ("symlink", "directory", "hardlink"))
def test_exact_member_reader_rejects_link_nonregular_and_nonunique_inode(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    source, _manifests, _identities = _exact_mirror(tmp_path, monkeypatch)
    target = source / context.MATCH_MEMBER_PATH
    target.unlink()
    if attack == "directory":
        target.mkdir()
    else:
        alternate = source / "archive-members" / "alternate.json"
        alternate.write_bytes(REAL_MATCH_MEMBER)
        os.chmod(alternate, 0o600)
        if attack == "symlink":
            target.symlink_to(alternate.name)
        else:
            os.link(alternate, target)
    with pytest.raises(context.WyscoutVerticalSliceContextPathError):
        context._read_exact_match_member(source)


@pytest.mark.parametrize("row_delta", (-1, 1))
def test_decoder_rejects_match_member_row_omission_or_addition(row_delta: int) -> None:
    rows = json.loads(REAL_MATCH_MEMBER)
    if row_delta < 0:
        rows.pop()
    else:
        rows.append(deepcopy(rows[0]))
    payload = json.dumps(rows, separators=(",", ":")).encode()
    with pytest.raises(context.WyscoutVerticalSliceContextError, match="cardinality"):
        context._decode_match_member(payload)


def test_decoder_rejects_duplicate_keys_and_nonobject_rows() -> None:
    with pytest.raises(context.WyscoutVerticalSliceContextError, match="repeats key"):
        context._decode_match_member(b'[{"wyId":1,"wyId":2}]')
    rows: list[object] = [{} for _ in range(context.MATCH_MEMBER_ROW_COUNT)]
    rows[-1] = 1
    with pytest.raises(context.WyscoutVerticalSliceContextError, match="array of objects"):
        context._decode_match_member(json.dumps(rows).encode())


@pytest.mark.parametrize("attack", ("wrong_ordinal", "duplicate_selected", "raw_addition"))
def test_selected_match_rejects_ordinal_duplicate_and_raw_digest_drift(attack: str) -> None:
    rows = _selected_rows()
    if attack == "wrong_ordinal":
        rows[-1], rows[-2] = rows[-2], rows[-1]
    elif attack == "duplicate_selected":
        rows[0] = deepcopy(rows[-1])
    else:
        rows[-1]["invented"] = 1
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._validate_selected_match(rows)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("wyId", "2499719"),
        ("wyId", True),
        ("competitionId", 365),
        ("competitionId", "364"),
        ("competitionId", True),
        ("seasonId", 181_151),
        ("seasonId", "181150"),
        ("seasonId", True),
        ("dateutc", "2017-08-11T18:45:00Z"),
    ),
)
def test_selected_match_rejects_strict_identity_or_clock_drift(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    rows = _selected_rows()
    row = rows[-1]
    row[field] = value
    _bind_mutated_raw_digest(monkeypatch, row)
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._validate_selected_match(rows)


@pytest.mark.parametrize(
    "attack",
    (
        "team_key",
        "team_id_string",
        "target_bench_omission",
        "target_bench_duplicate",
        "target_bench_cross_team",
        "target_in_lineup",
        "substitution_omission",
        "substitution_duplicate",
        "substitution_minute",
        "substitution_minute_string",
        "substitution_player_string",
        "substitution_out",
        "substitution_extra_key",
    ),
)
def test_selected_match_rejects_team_bench_and_substitution_drift(
    monkeypatch: pytest.MonkeyPatch,
    attack: str,
) -> None:
    rows = _selected_rows()
    row = rows[-1]
    teams = cast(dict[str, Any], row["teamsData"])
    target_formation = teams["1631"]["formation"]
    bench = target_formation["bench"]
    substitutions = target_formation["substitutions"]
    target_bench = next(item for item in bench if item["playerId"] == 285_508)
    target_sub = next(item for item in substitutions if item["playerIn"] == 285_508)
    if attack == "team_key":
        teams["1632"] = teams.pop("1631")
    elif attack == "team_id_string":
        teams["1631"]["teamId"] = "1631"
    elif attack == "target_bench_omission":
        bench.remove(target_bench)
    elif attack == "target_bench_duplicate":
        bench.append(deepcopy(target_bench))
    elif attack == "target_bench_cross_team":
        teams["1609"]["formation"]["bench"].append(deepcopy(target_bench))
    elif attack == "target_in_lineup":
        target_formation["lineup"].append(deepcopy(target_bench))
    elif attack == "substitution_omission":
        substitutions.remove(target_sub)
    elif attack == "substitution_duplicate":
        substitutions.append(deepcopy(target_sub))
    elif attack == "substitution_minute":
        target_sub["minute"] = 83
    elif attack == "substitution_minute_string":
        target_sub["minute"] = "82"
    elif attack == "substitution_player_string":
        target_sub["playerIn"] = "285508"
    elif attack == "substitution_out":
        target_sub["playerOut"] = 285_508
    else:
        target_sub["invented"] = 1
    _bind_mutated_raw_digest(monkeypatch, row)
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._validate_selected_match(rows)


def test_identity_join_rejects_missing_duplicate_unresolved_or_canonical_drift() -> None:
    build = _identity_build()
    player_rows = [
        row
        for row in build.bundle.current_rows
        if row.entity_kind is WyscoutIdentityEntityKind.PLAYER
    ]
    assert len(player_rows) == 1
    player = player_rows[0]
    for rows in (
        tuple(row for row in build.bundle.current_rows if row is not player),
        (*build.bundle.current_rows, player),
        tuple(
            SimpleNamespace(**{**row.__dict__, "state": WyscoutIdentityState.REVIEW_REQUIRED})
            if row is player
            else row
            for row in build.bundle.current_rows
        ),
        _identity_build(player_id=context.MATCH_ID).bundle.current_rows,
    ):
        mutated = SimpleNamespace(bundle=SimpleNamespace(current_rows=rows))
        with pytest.raises(context.WyscoutVerticalSliceContextError, match="does not resolve"):
            context._identity_binding(
                cast(Any, mutated),
                entity_kind=WyscoutIdentityEntityKind.PLAYER,
                source_id=context.TARGET_PLAYER_SOURCE_ID,
                canonical_id=context.TARGET_PLAYER_ID,
            )


@pytest.mark.parametrize("attack", ("missing", "additional", "duplicate", "reordered"))
def test_event_population_rejects_incomplete_additional_duplicate_or_reordered_actions(
    accepted_event_population: completion.VerifiedMatchPopulation,
    attack: str,
) -> None:
    actions = list(accepted_event_population.actions)
    if attack == "missing":
        actions.pop()
    elif attack == "additional":
        actions.append(actions[-1])
    elif attack == "duplicate":
        actions[-1] = actions[-2]
    else:
        actions[0], actions[1] = actions[1], actions[0]
    mutated = replace(accepted_event_population, actions=tuple(actions))
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._validate_event_population(mutated)


@pytest.mark.parametrize("attack", ("cross_match", "cross_member", "identity_digest"))
def test_event_population_rejects_cross_scope_and_raw_identity_drift(
    accepted_event_population: completion.VerifiedMatchPopulation,
    attack: str,
) -> None:
    actions = list(accepted_event_population.actions)
    first = actions[0]
    if attack == "identity_digest":
        first = replace(first, canonical_raw_record=b"{}")
    elif attack == "cross_match":
        first = replace(first, evidence=replace(first.evidence, match_source_id=1))
    else:
        first = replace(first, evidence=replace(first.evidence, source_member_path="other"))
    actions[0] = first
    mutated = replace(accepted_event_population, actions=tuple(actions))
    with pytest.raises(context.WyscoutVerticalSliceContextError):
        context._validate_event_population(mutated)


def test_full_loader_rejects_identity_bundle_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    accepted_event_population: completion.VerifiedMatchPopulation,
) -> None:
    source, manifests, identities = _exact_mirror(tmp_path, monkeypatch)
    forged = _identity_build(player_id=context.MATCH_ID)
    _patch_accepted_joins(
        monkeypatch,
        accepted_event_population,
        identity_build=forged,
    )
    with pytest.raises(context.WyscoutVerticalSliceContextError, match="player:285508"):
        _load(source, manifests, identities)
