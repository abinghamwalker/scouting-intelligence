"""Focused acceptance tests for the W04 source-completion index."""

from __future__ import annotations

import hashlib
import json
import pickle
from copy import copy, deepcopy
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any, cast

import pytest

from scouting.contracts.wyscout_data import SOURCE_COMPLETION_INDEX_SHA256, SourceRecordKind
from scouting.sources import wyscout_completion_index as completion

INDEX_SHA256 = "46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df"
INDEX_PATH = Path(
    f"data/manifests/wyscout/v5/source-completion/{INDEX_SHA256}.source-completion-index.json"
)


@pytest.fixture(scope="module")
def frozen_index() -> completion.SourceCompletionIndex:
    return completion.load_source_completion_index(
        manifest_root=Path("data/manifests"),
        index_sha256=INDEX_SHA256,
    )


def self_consistent_forged_index(
    accepted: completion.SourceCompletionIndex,
) -> completion.SourceCompletionIndex:
    members = list(accepted.members)
    periods = list(members[0].periods)
    periods[0] = replace(periods[0], membership_sha256="f" * 64)
    members[0] = replace(members[0], periods=tuple(periods))
    return completion._build_index_value(tuple(members))


def _closure_value(function: object, name: str) -> object:
    inspected = cast(Any, function)
    values = dict(
        zip(
            inspected.__code__.co_freevars,
            (cell.cell_contents for cell in inspected.__closure__),
            strict=True,
        )
    )
    return cast(object, values[name])


@pytest.fixture(scope="module")
def first_period_population(
    frozen_index: completion.SourceCompletionIndex,
) -> tuple[completion.CompletionActionEvidence, ...]:
    expected = frozen_index.members[0].periods[0]
    spec = completion._EVENT_MEMBERS[0]
    payload = Path("data/source/wyscout/v5", spec.path).read_bytes()
    records = completion._decode_action_member(payload, context=spec.path)
    actions = tuple(
        completion.completion_action_evidence(
            source_member_path=spec.path,
            source_member_sha256=spec.sha256,
            source_record_ordinal=ordinal,
            raw_record=record,
        )
        for ordinal, record in enumerate(records)
        if record["matchId"] == expected.match_source_id
        and record["matchPeriod"] == expected.action_period_code
    )
    return tuple(sorted(actions, key=lambda action: action.order_key))


@pytest.fixture(scope="module")
def first_match_population(
    frozen_index: completion.SourceCompletionIndex,
) -> tuple[completion.CompletionActionEvidence, ...]:
    match_source_id = frozen_index.members[0].periods[0].match_source_id
    spec = completion._EVENT_MEMBERS[0]
    records = completion._decode_action_member(
        Path("data/source/wyscout/v5", spec.path).read_bytes(), context=spec.path
    )
    return tuple(
        sorted(
            (
                completion.completion_action_evidence(
                    source_member_path=spec.path,
                    source_member_sha256=spec.sha256,
                    source_record_ordinal=ordinal,
                    raw_record=record,
                )
                for ordinal, record in enumerate(records)
                if record["matchId"] == match_source_id
            ),
            key=lambda action: action.order_key,
        )
    )


@pytest.fixture(scope="module")
def verified_vertical_slice() -> completion.VerifiedMatchPopulation:
    return completion.load_verified_match_population(
        source_root=Path("data/source/wyscout/v5"),
        manifest_root=Path("data/manifests"),
        index_sha256=INDEX_SHA256,
        source_member_path="archive-members/events_England.json",
        match_source_id=2_499_719,
    )


@pytest.fixture(scope="module")
def reconstructed_vertical_slice_member(
    verified_vertical_slice: completion.VerifiedMatchPopulation,
) -> list[dict[str, object]]:
    filler: dict[str, object] = {"matchId": 1}
    records = [filler] * completion._EVENT_MEMBERS[0].row_count
    for action in verified_vertical_slice.actions:
        decoded = json.loads(
            action.canonical_raw_record,
            parse_float=Decimal,
            object_pairs_hook=completion._reject_duplicate_keys,
        )
        assert type(decoded) is dict
        records[action.evidence.source_record_ordinal] = cast(dict[str, object], decoded)
    return records


def test_exact_content_address_and_five_member_reconciliation(
    frozen_index: completion.SourceCompletionIndex,
) -> None:
    assert INDEX_PATH.stat().st_size == 644_037
    assert hashlib.sha256(INDEX_PATH.read_bytes()).hexdigest() == INDEX_SHA256
    assert frozen_index.sha256 == INDEX_SHA256
    assert frozen_index.aggregate_action_count == 3_071_395
    assert tuple(member.path for member in frozen_index.members) == tuple(
        spec.path for spec in completion._EVENT_MEMBERS
    )
    assert tuple(member.indexed_action_count for member in frozen_index.members) == (
        643_150,
        632_807,
        519_407,
        647_372,
        628_659,
    )


def test_index_load_rejects_payload_address_drift() -> None:
    payload = bytearray(INDEX_PATH.read_bytes())
    payload[-2] = ord("x")
    with pytest.raises(completion.WyscoutCompletionIndexError):
        completion._parse_index_payload(bytes(payload))


def test_self_consistent_forged_index_is_rejected_by_accepted_address_pin(
    frozen_index: completion.SourceCompletionIndex,
) -> None:
    forged = self_consistent_forged_index(frozen_index)
    assert hashlib.sha256(forged.canonical_bytes).hexdigest() == forged.sha256
    assert forged.sha256 != INDEX_SHA256
    with pytest.raises(completion.WyscoutCompletionIndexError, match="address is not accepted"):
        completion.validate_index(forged)


def test_accepted_stored_address_still_requires_independent_content_recomputation(
    frozen_index: completion.SourceCompletionIndex,
) -> None:
    forged = self_consistent_forged_index(frozen_index)
    address_spoofed = replace(forged, sha256=INDEX_SHA256)
    with pytest.raises(completion.WyscoutCompletionIndexError, match="canonical address drifted"):
        completion.validate_index(address_spoofed)


def test_unaccepted_load_argument_is_rejected_before_any_file_open(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    opened = False

    def forbidden_open(*_args: object, **_kwargs: object) -> None:
        nonlocal opened
        opened = True
        raise AssertionError("unaccepted index address reached the file-open boundary")

    monkeypatch.setattr(
        "scouting.sources.wyscout_completion_index.bridge._open_regular_beneath",
        forbidden_open,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="address is not accepted"):
        completion.load_source_completion_index(
            manifest_root=Path("data/manifests"),
            index_sha256="f" * 64,
        )
    assert opened is False


def test_materialization_rejects_forged_index_before_path_access(
    frozen_index: completion.SourceCompletionIndex,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_root(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("forged index reached the materialization path boundary")

    monkeypatch.setattr(
        "scouting.sources.wyscout_completion_index.bridge._exact_root_argument",
        forbidden_root,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="address is not accepted"):
        completion.materialize_source_completion_index(
            manifest_root=Path("data/manifests"),
            index=self_consistent_forged_index(frozen_index),
        )


@pytest.mark.parametrize(
    "boundary",
    (
        "period_validator",
        "match_validator",
        "period_factory",
        "match_factory",
    ),
)
def test_population_boundaries_inherit_the_accepted_index_pin(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
    boundary: str,
) -> None:
    forged = self_consistent_forged_index(frozen_index)
    with pytest.raises(completion.WyscoutCompletionIndexError, match="address is not accepted"):
        if boundary == "period_validator":
            completion.validate_match_period_population(
                index=forged,
                actions=first_period_population,
            )
        elif boundary == "match_validator":
            completion.validate_match_population(index=forged, actions=first_match_population)
        elif boundary == "period_factory":
            completion.build_possession_period_sequence(
                index=forged,
                actions=first_period_population,
            )
        else:
            completion.build_match_period_sequences(index=forged, actions=first_match_population)


@pytest.mark.parametrize(
    "mutation",
    ("member_count", "aggregate_count", "member_order", "period_order", "period_duplicate"),
)
def test_index_rejects_count_order_uniqueness_and_aggregate_drift(
    frozen_index: completion.SourceCompletionIndex,
    mutation: str,
) -> None:
    members = list(frozen_index.members)
    aggregate = frozen_index.aggregate_action_count
    if mutation == "member_count":
        members[0] = replace(members[0], indexed_action_count=members[0].indexed_action_count - 1)
    elif mutation == "aggregate_count":
        aggregate -= 1
    elif mutation == "member_order":
        members[0], members[1] = members[1], members[0]
    elif mutation == "period_order":
        periods = list(members[0].periods)
        periods[0], periods[1] = periods[1], periods[0]
        members[0] = replace(members[0], periods=tuple(periods))
    else:
        periods = list(members[0].periods)
        periods[1] = periods[0]
        members[0] = replace(members[0], periods=tuple(periods))
    mutated = replace(frozen_index, aggregate_action_count=aggregate, members=tuple(members))
    with pytest.raises(completion.WyscoutCompletionIndexError):
        completion.validate_index(mutated)


def test_exact_real_period_population_validates(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    period = completion.validate_match_period_population(
        index=frozen_index,
        actions=first_period_population,
    )
    assert len(first_period_population) == period.action_count
    assert completion.period_membership_sha256(first_period_population) == (
        period.membership_sha256
    )


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "additional",
        "duplicate",
        "reordered",
        "stale",
        "cross_member",
        "cross_match",
        "cross_period",
    ),
)
def test_public_population_boundary_rejects_every_membership_drift(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
    mutation: str,
) -> None:
    actions = list(first_period_population)
    if mutation == "missing":
        actions.pop()
    elif mutation == "additional":
        actions.append(
            replace(actions[-1], source_record_ordinal=actions[-1].source_record_ordinal + 1)
        )
    elif mutation == "duplicate":
        actions[-1] = actions[-2]
    elif mutation == "reordered":
        actions[0], actions[1] = actions[1], actions[0]
    elif mutation == "stale":
        actions[0] = replace(actions[0], raw_record_sha256="0" * 64)
    elif mutation == "cross_member":
        actions[0] = replace(actions[0], source_member_path=completion._EVENT_MEMBERS[1].path)
    elif mutation == "cross_match":
        actions[0] = replace(actions[0], match_source_id=actions[0].match_source_id + 1)
    else:
        actions[0] = replace(
            actions[0],
            action_period_code="2H" if actions[0].action_period_code == "1H" else "1H",
            period_rank=2 if actions[0].period_rank == 1 else 1,
        )
    with pytest.raises(completion.WyscoutCompletionIndexError):
        completion.validate_match_period_population(index=frozen_index, actions=actions)


def test_public_population_boundary_rejects_whole_period_omission(
    frozen_index: completion.SourceCompletionIndex,
) -> None:
    with pytest.raises(completion.WyscoutCompletionIndexError, match="whole-period"):
        completion.validate_match_period_population(index=frozen_index, actions=())


def test_match_boundary_rejects_one_whole_indexed_period_omission(
    frozen_index: completion.SourceCompletionIndex,
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    periods = completion.validate_match_population(
        index=frozen_index,
        actions=first_match_population,
    )
    assert len(periods) == 2
    truncated = tuple(
        action
        for action in first_match_population
        if action.action_period_code == periods[0].action_period_code
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="omits or adds"):
        completion.validate_match_population(index=frozen_index, actions=truncated)


def test_public_match_factory_builds_every_exact_source_bound_period(
    frozen_index: completion.SourceCompletionIndex,
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    sequences = completion.build_match_period_sequences(
        index=frozen_index,
        actions=first_match_population,
    )
    assert len(sequences) == 2
    assert sum(sequence.period_action_count for sequence in sequences) == len(
        first_match_population
    )
    assert all(
        sequence.source_completion_index_sha256 == SOURCE_COMPLETION_INDEX_SHA256
        for sequence in sequences
    )
    expected_memberships = {
        period.membership_sha256 for period in frozen_index.members[0].periods[:2]
    }
    assert {sequence.source_completion_membership_sha256 for sequence in sequences} == (
        expected_memberships
    )
    assert all(
        entry.source_row.record_kind is SourceRecordKind.ACTION
        and entry.source_row.raw_record_sha256
        for sequence in sequences
        for entry in sequence.actions
    )


def test_exact_match_comparison_issues_opaque_nonreplayable_capability(
    frozen_index: completion.SourceCompletionIndex,
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    checked = completion.validate_checked_match_population(
        index=frozen_index,
        actions=first_match_population,
    )
    assert checked.sequences == completion.build_match_period_sequences(
        index=frozen_index,
        actions=first_match_population,
    )
    with pytest.raises(TypeError, match="issued only"):
        completion.CheckedCompletionPopulation()
    with pytest.raises(TypeError, match="cannot be copied"):
        copy(checked)
    with pytest.raises(TypeError, match="cannot be copied"):
        deepcopy(checked)
    with pytest.raises(TypeError, match="cannot be serialized"):
        pickle.dumps(checked)


def test_unregistered_capability_substitution_is_rejected() -> None:
    substituted = object.__new__(completion.CheckedCompletionPopulation)
    with pytest.raises(completion.WyscoutCompletionIndexError, match="not issued"):
        _ = substituted.sequences


def test_introspected_completion_issuer_cannot_assert_false_complete_match(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    issuer = cast(
        completion._IssueCompletion,
        _closure_value(completion.validate_checked_match_population, "issuer"),
    )
    forged = issuer(
        completion._CheckedCompletionRecord(
            index=frozen_index,
            actions=first_period_population,
            scope_kind="match",
        )
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="omits or adds"):
        _ = forged.sequences


def test_completion_registry_mutation_cannot_confer_population_authority(
    frozen_index: completion.SourceCompletionIndex,
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    registry = cast(
        Any,
        _closure_value(completion._get_checked_completion, "completion_records"),
    )
    malformed = object.__new__(completion.CheckedCompletionPopulation)
    registry[malformed] = object()
    with pytest.raises(completion.WyscoutCompletionIndexError, match="record is malformed"):
        _ = malformed.sequences

    cross_scope = object.__new__(completion.CheckedCompletionPopulation)
    registry[cross_scope] = completion._CheckedCompletionRecord(
        index=frozen_index,
        actions=first_match_population,
        scope_kind="period",
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="crosses"):
        _ = cross_scope.sequences


def test_checked_manifest_rejects_two_independently_issued_overlapping_scopes(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    first = completion.validate_checked_period_population(
        index=frozen_index,
        actions=first_period_population,
    )
    detached_reissue = completion.validate_checked_period_population(
        index=frozen_index,
        actions=first_period_population,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="overlap"):
        completion.build_checked_layer_manifest(
            payload={},
            completions=(first, detached_reissue),
            contributing_products=(),
        )


def test_copied_real_membership_digest_cannot_replace_exact_population_comparison(
    frozen_index: completion.SourceCompletionIndex,
    first_period_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    checked = completion.validate_checked_period_population(
        index=frozen_index,
        actions=first_period_population,
    )
    exact_sequence = checked.sequences[0]
    copied_payload = exact_sequence.model_dump()
    copied_payload["actions"] = copied_payload["actions"][:-1]
    copied_payload["period_action_count"] -= 1
    copied_digest_sequence = type(exact_sequence).model_validate(copied_payload)
    assert copied_digest_sequence.source_completion_membership_sha256 == (
        exact_sequence.source_completion_membership_sha256
    )
    assert copied_digest_sequence.construction_authority_state == "semantic_only_unchecked"
    with pytest.raises(completion.WyscoutCompletionIndexError, match="population count"):
        completion.validate_checked_period_population(
            index=frozen_index,
            actions=first_period_population[:-1],
        )


def test_public_match_factory_rejects_truncated_match_population(
    frozen_index: completion.SourceCompletionIndex,
    first_match_population: tuple[completion.CompletionActionEvidence, ...],
) -> None:
    truncated = tuple(
        action for action in first_match_population if action.action_period_code == "1H"
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="omits or adds"):
        completion.build_match_period_sequences(index=frozen_index, actions=truncated)


def test_action_projection_preserves_string_subevent_as_unmapped_and_rejects_coercion() -> None:
    raw = {
        "eventId": 1,
        "eventSec": 1,
        "id": 2,
        "matchId": 3,
        "matchPeriod": "1H",
        "playerId": 4,
        "subEventId": "10",
        "tags": [{"id": 5}, {"id": 5}],
        "teamId": 6,
    }
    evidence = completion.completion_action_evidence(
        source_member_path=completion._EVENT_MEMBERS[0].path,
        source_member_sha256=completion._EVENT_MEMBERS[0].sha256,
        source_record_ordinal=0,
        raw_record=raw,
    )
    assert evidence.action_subevent_taxonomy_id is None
    assert evidence.raw_tags == ({"id": 5}, {"id": 5})
    assert evidence.possession_tag_ids == (5,)
    with pytest.raises(TypeError):
        cast(Any, evidence.raw_tags[0])["id"] = 6
    frame = completion.action_frame(evidence)
    assert len(frame) == 595
    assert hashlib.sha256(frame).hexdigest() == (
        "5b94fec338d67564aa16e37b8eb60ec70995182c8a7dc1bd5d02c1e32b83ca4e"
    )
    assert completion.period_membership_sha256((evidence,)) == (
        "c245045382071ae38bf26557b2acb16282db1997e0fbaf50a9a9faafc8ba6d21"
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="strict tag ID"):
        completion._canonical_value_bytes(MappingProxyType({"other": 5}))
    with pytest.raises(completion.WyscoutCompletionIndexError, match="strict integer"):
        completion.completion_action_evidence(
            source_member_path=completion._EVENT_MEMBERS[0].path,
            source_member_sha256=completion._EVENT_MEMBERS[0].sha256,
            source_record_ordinal=0,
            raw_record={**raw, "id": "2"},
        )


def test_materialization_is_byte_idempotent(frozen_index: completion.SourceCompletionIndex) -> None:
    result = completion.materialize_source_completion_index(
        manifest_root=Path("data/manifests"),
        index=frozen_index,
    )
    assert result.created is False
    assert result.index.sha256 == INDEX_SHA256
    assert INDEX_PATH.read_bytes() == frozen_index.canonical_bytes


def test_completion_reader_has_no_provider_or_product_authority() -> None:
    source = Path(completion.__file__).read_text(encoding="utf-8")
    forbidden = (
        "urllib",
        "requests",
        "httpx",
        "European_Championship",
        "World_Cup",
        "data/working/wyscout/v5/bronze",
        "data/working/wyscout/v5/silver",
        "data/working/wyscout/v5/gold",
    )
    assert all(token not in source for token in forbidden)


def test_verified_match_adapter_returns_exact_immutable_raw_evidence_pairs(
    verified_vertical_slice: completion.VerifiedMatchPopulation,
) -> None:
    assert verified_vertical_slice.index.sha256 == INDEX_SHA256
    assert verified_vertical_slice.source_member_path == "archive-members/events_England.json"
    assert verified_vertical_slice.match_source_id == 2_499_719
    assert len(verified_vertical_slice.actions) == 1_768
    assert tuple(
        (sequence.action_period_code, sequence.period_action_count)
        for sequence in verified_vertical_slice.completion.sequences
    ) == (("1H", 901), ("2H", 867))
    assert tuple(
        sequence.source_completion_membership_sha256
        for sequence in verified_vertical_slice.completion.sequences
    ) == (
        "473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b",
        "b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16",
    )
    assert all(
        hashlib.sha256(action.canonical_raw_record).hexdigest() == action.evidence.raw_record_sha256
        for action in verified_vertical_slice.actions
    )
    selected_player = tuple(
        action
        for action in verified_vertical_slice.actions
        if action.evidence.player_source_id == 285_508
    )
    assert len(selected_player) == 2
    assert all(
        type(action.raw_record["positions"]) is tuple and action.raw_record["positions"]
        for action in selected_player
    )
    with pytest.raises(TypeError):
        cast(Any, verified_vertical_slice.actions[0].raw_record)["matchId"] = 1
    with pytest.raises(TypeError):
        cast(Any, selected_player[0].raw_record["positions"])[0]["x"] = 1
    tagged_action = next(
        action for action in verified_vertical_slice.actions if action.evidence.raw_tags
    )
    with pytest.raises(TypeError):
        cast(Any, tagged_action.evidence.raw_tags[0])["id"] = 999_999
    assert tuple(
        (sequence.action_period_code, sequence.period_action_count)
        for sequence in verified_vertical_slice.completion.sequences
    ) == (("1H", 901), ("2H", 867))


@pytest.mark.parametrize(
    ("index_sha256", "source_member_path", "match_source_id", "message"),
    (
        ("f" * 64, "archive-members/events_England.json", 2_499_719, "not accepted"),
        (INDEX_SHA256, "archive-members/events_France.json", 2_499_719, "not admitted"),
        (
            INDEX_SHA256,
            cast(Any, Path("archive-members/events_England.json")),
            2_499_719,
            "exact string",
        ),
        (INDEX_SHA256, "archive-members/events_England.json", cast(Any, True), "strict positive"),
        (
            INDEX_SHA256,
            "archive-members/events_England.json",
            cast(Any, "2499719"),
            "strict positive",
        ),
        (INDEX_SHA256, "archive-members/events_England.json", 0, "strict positive"),
        (INDEX_SHA256, "archive-members/events_England.json", 2_499_720, "not admitted"),
    ),
)
def test_verified_match_adapter_rejects_unpinned_inputs_before_member_read(
    monkeypatch: pytest.MonkeyPatch,
    index_sha256: str,
    source_member_path: str,
    match_source_id: int,
    message: str,
) -> None:
    def forbidden_member_read(*_args: object, **_kwargs: object) -> bytes:
        raise AssertionError("invalid adapter input reached the source-member read")

    monkeypatch.setattr(completion, "_read_verified_member", forbidden_member_read)
    with pytest.raises(completion.WyscoutCompletionIndexError, match=message):
        completion.load_verified_match_population(
            source_root=Path("data/source/wyscout/v5"),
            manifest_root=Path("data/manifests"),
            index_sha256=index_sha256,
            source_member_path=source_member_path,
            match_source_id=match_source_id,
        )


@pytest.mark.parametrize("row_delta", (-1, 1))
def test_verified_match_adapter_rejects_truncated_or_additional_member_rows(
    monkeypatch: pytest.MonkeyPatch,
    row_delta: int,
) -> None:
    filler: dict[str, object] = {"matchId": 1}
    records = [filler] * (completion._EVENT_MEMBERS[0].row_count + row_delta)
    monkeypatch.setattr(completion, "_read_verified_member", lambda *_args, **_kwargs: b"[]")
    monkeypatch.setattr(
        completion,
        "_decode_action_member",
        lambda *_args, **_kwargs: records,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="row count"):
        completion.load_verified_match_population(
            source_root=Path("data/source/wyscout/v5"),
            manifest_root=Path("data/manifests"),
            index_sha256=INDEX_SHA256,
            source_member_path="archive-members/events_England.json",
            match_source_id=2_499_719,
        )


def test_verified_match_adapter_rejects_non_strict_row_match_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    filler: dict[str, object] = {"matchId": 1}
    records = [{"matchId": "2499719"}, *([filler] * (643_150 - 1))]
    monkeypatch.setattr(completion, "_read_verified_member", lambda *_args, **_kwargs: b"[]")
    monkeypatch.setattr(
        completion,
        "_decode_action_member",
        lambda *_args, **_kwargs: records,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError, match="strict integer"):
        completion.load_verified_match_population(
            source_root=Path("data/source/wyscout/v5"),
            manifest_root=Path("data/manifests"),
            index_sha256=INDEX_SHA256,
            source_member_path="archive-members/events_England.json",
            match_source_id=2_499_719,
        )


@pytest.mark.parametrize("mutation", ("omitted", "additional", "duplicate", "reordered"))
def test_verified_match_adapter_rejects_selected_population_membership_drift(
    monkeypatch: pytest.MonkeyPatch,
    reconstructed_vertical_slice_member: list[dict[str, object]],
    verified_vertical_slice: completion.VerifiedMatchPopulation,
    mutation: str,
) -> None:
    records = reconstructed_vertical_slice_member.copy()
    first = verified_vertical_slice.actions[0].evidence.source_record_ordinal
    second = verified_vertical_slice.actions[1].evidence.source_record_ordinal
    filler: dict[str, object] = {"matchId": 1}
    if mutation == "omitted":
        records[first] = filler
    elif mutation == "additional":
        admitted_ordinals = {
            action.evidence.source_record_ordinal for action in verified_vertical_slice.actions
        }
        extra = next(ordinal for ordinal in range(len(records)) if ordinal not in admitted_ordinals)
        records[extra] = records[first]
    elif mutation == "duplicate":
        records[second] = records[first]
    else:
        records[first], records[second] = records[second], records[first]
    monkeypatch.setattr(completion, "_read_verified_member", lambda *_args, **_kwargs: b"[]")
    monkeypatch.setattr(
        completion,
        "_decode_action_member",
        lambda *_args, **_kwargs: records,
    )
    with pytest.raises(completion.WyscoutCompletionIndexError):
        completion.load_verified_match_population(
            source_root=Path("data/source/wyscout/v5"),
            manifest_root=Path("data/manifests"),
            index_sha256=INDEX_SHA256,
            source_member_path="archive-members/events_England.json",
            match_source_id=2_499_719,
        )


def test_verified_member_reader_rejects_source_mutation(tmp_path: Path) -> None:
    payload = b'[{"matchId":2499719}]'
    target = tmp_path / "member.json"
    target.write_bytes(payload)
    spec = completion.EventMemberSpec(
        path="member.json",
        sha256=hashlib.sha256(payload).hexdigest(),
        size_bytes=len(payload),
        row_count=1,
    )
    target.write_bytes(b'[{"matchId":2499720}]')
    with pytest.raises(completion.WyscoutCompletionIndexError, match="conflicts"):
        completion._read_verified_member(tmp_path, spec)
