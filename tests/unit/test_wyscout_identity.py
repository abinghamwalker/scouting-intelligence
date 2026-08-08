"""Focused fail-closed tests for W04 identity contracts and path controls."""

from __future__ import annotations

import io
import json
import os
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest
from pydantic import ValidationError

from scouting.contracts.evidence import SourceIdentity
from scouting.contracts.primitives import TenantContext
from scouting.contracts.wyscout_data import (
    SOURCE_MANIFEST_ID,
    SourceRecordKind,
    WyscoutSourceRowReference,
)
from scouting.contracts.wyscout_identity import (
    IDENTITY_CROSSWALK_NAMESPACE,
    IDENTITY_REVIEW_QUEUE_NAMESPACE,
    W04IdentityCrosswalkRow,
    WyscoutIdentityEntityKind,
    WyscoutIdentityQueueItem,
    WyscoutIdentityReviewQueue,
    WyscoutIdentityState,
    crosswalk_row_preimage_text,
    queue_item_identity,
    queue_item_preimage_bytes,
)
from scouting.identity import wyscout

MATCH_SHA256 = "620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29"


def _match_ref(ordinal: int = 56, raw_digest: str = "1" * 64) -> WyscoutSourceRowReference:
    return WyscoutSourceRowReference(
        source_manifest_id=SOURCE_MANIFEST_ID,
        completion_relative_path="archive-members/matches_England.json",
        source_sha256=MATCH_SHA256,
        source_record_ordinal=ordinal,
        record_kind=SourceRecordKind.MATCH,
        raw_record_sha256=raw_digest,
    )


def _review_row(source_id: int = 379_199) -> W04IdentityCrosswalkRow:
    return wyscout._initial_crosswalk_row(
        entity_kind=WyscoutIdentityEntityKind.PLAYER,
        source_id=source_id,
        source_refs=(_match_ref(),),
        state=WyscoutIdentityState.REVIEW_REQUIRED,
    )


def _queue() -> WyscoutIdentityReviewQueue:
    return wyscout._queue_from_rows((_review_row(),))


@pytest.mark.parametrize("value", [True, False, 1.0, Decimal("1"), "1", None])
def test_identity_integer_parser_rejects_coercion(value: object) -> None:
    with pytest.raises(wyscout.WyscoutIdentityError, match="strict positive integer"):
        wyscout._strict_positive(value, context="identity")


@pytest.mark.parametrize("value", [True, False, 0.0, Decimal("0"), "0", None, -1])
def test_identity_nonnegative_parser_rejects_coercion(value: object) -> None:
    with pytest.raises(wyscout.WyscoutIdentityError, match="strict non-negative integer"):
        wyscout._strict_nonnegative(value, context="identity")


def test_queue_item_uuid_uses_exact_five_field_no_newline_preimage() -> None:
    item = _queue().items[0]
    payload = queue_item_preimage_bytes(item)
    assert not payload.endswith(b"\n")
    assert tuple(json.loads(payload)) == (
        "entity_kind",
        "reason_family",
        "source_identity",
        "source_manifest_id",
        "tenant_id",
    )
    assert item.queue_item_id == uuid5(IDENTITY_REVIEW_QUEUE_NAMESPACE, payload.decode())
    assert queue_item_identity(item) != uuid5(NAMESPACE_URL, payload.decode())
    assert queue_item_identity(item) != uuid5(
        IDENTITY_REVIEW_QUEUE_NAMESPACE,
        (payload + b"\n").decode(),
    )


def test_crosswalk_uuid_and_trace_match_addendum_fixed_vector() -> None:
    row = _review_row()
    preimage = crosswalk_row_preimage_text(row)
    assert IDENTITY_CROSSWALK_NAMESPACE == UUID("fd7bb3ae-10f7-5856-99fb-3854d794273d")
    assert row.evidence_digest == "abc992ddc65429bd73c530a4103daf0567118856aa2b5f0a0771bea29c0595f9"
    assert preimage == (
        '65a43912-d412-5ff9-a364-7f84d1ad6c5d:PLAYER:{"provider":"Wyscout",'
        '"source_id":"player:379199","source_version":"figshare-v5"}:1:'
        "abc992ddc65429bd73c530a4103daf0567118856aa2b5f0a0771bea29c0595f9"
    )
    assert row.crosswalk_row_id == UUID("45b2a06d-e200-5cb3-9c9d-8f429291ed31")
    assert row.trace_id == UUID("121e5662-35f6-5f12-8b3b-c458b30cc38a")
    assert row.crosswalk_row_id != uuid5(NAMESPACE_URL, preimage)
    assert row.crosswalk_row_id != uuid5(IDENTITY_CROSSWALK_NAMESPACE, preimage + "\n")
    assert row.crosswalk_row_id != uuid5(
        IDENTITY_CROSSWALK_NAMESPACE,
        preimage.replace(":PLAYER:", ":player:"),
    )


def test_queue_rejects_duplicate_reorder_omission_and_wrong_authority() -> None:
    first = _queue().items[0]
    second_row = _review_row(447_214)
    second = wyscout._queue_from_rows((second_row,)).items[0]
    valid = wyscout._queue_from_rows(
        tuple(sorted((_review_row(), second_row), key=lambda row: row.source_identity.source_id))
    )
    payload = valid.model_dump(mode="python")

    for items, counts in (
        ((first, first), {"PLAYER:OPEN": 2}),
        ((second, first), {"PLAYER:OPEN": 2}),
        ((first,), {"PLAYER:OPEN": 2}),
    ):
        candidate = dict(payload, items=items, counts_by_kind_and_status=counts)
        with pytest.raises(ValidationError):
            WyscoutIdentityReviewQueue.model_validate(candidate)

    wrong_authority = dict(payload, identity_acceptance_sha256="f" * 64)
    with pytest.raises(ValidationError, match="authority differs"):
        WyscoutIdentityReviewQueue.model_validate(wrong_authority)


def test_queue_item_rejects_cross_kind_cross_source_cross_tenant_and_clock() -> None:
    item = _queue().items[0]
    base = item.model_dump(mode="python")
    changes: tuple[dict[str, object], ...] = (
        {"entity_kind": WyscoutIdentityEntityKind.TEAM},
        {
            "source_identity": SourceIdentity(
                provider="Other",
                source_id="player:379199",
                source_version="figshare-v5",
            )
        },
        {"tenant_context": TenantContext(tenant_id=UUID(int=1))},
        {"available_at": datetime(2026, 7, 31, 14, 15, 25, tzinfo=UTC)},
    )
    for change in changes:
        candidate = dict(base, **change)
        with pytest.raises(ValidationError):
            WyscoutIdentityQueueItem.model_validate(candidate)


def test_crosswalk_rejects_zero_resolution_digest_only_and_wrong_state() -> None:
    resolved_zero = wyscout._initial_crosswalk_row(
        entity_kind=WyscoutIdentityEntityKind.PLAYER,
        source_id=0,
        source_refs=(_match_ref(),),
        state=WyscoutIdentityState.REJECTED,
    )
    payload = resolved_zero.model_dump(mode="python")
    invalid = dict(
        payload,
        state=WyscoutIdentityState.RESOLVED,
        canonical_id=UUID(int=1),
        confidence=1.0,
    )
    with pytest.raises(ValidationError):
        W04IdentityCrosswalkRow.model_validate(invalid)

    changed_reason = dict(payload, reason_codes=("ALTERED",))
    with pytest.raises(ValidationError, match="reason code differs"):
        W04IdentityCrosswalkRow.model_validate(changed_reason)

    changed_reference = dict(payload, source_row_refs=(_match_ref(raw_digest="2" * 64),))
    with pytest.raises(ValidationError, match="evidence digest differs"):
        W04IdentityCrosswalkRow.model_validate(changed_reference)


def test_streaming_json_rejects_duplicate_rows_trailing_and_non_objects() -> None:
    assert tuple(wyscout._iter_json_values(io.StringIO('[{"wyId":1}]'))) == ({"wyId": 1},)
    for payload in ('[{"wyId":1,"wyId":2}]', "[1]", '[{"wyId":1}] trailing'):
        with pytest.raises(wyscout.WyscoutIdentityError):
            tuple(wyscout._iter_json_values(io.StringIO(payload)))


def test_formation_retains_only_the_measured_unmapped_string_container() -> None:
    formation = {"bench": [], "lineup": [], "substitutions": "null"}
    assert wyscout._formation_player_ids(formation, context="formation") == ()
    with pytest.raises(wyscout.WyscoutIdentityError, match="measured unmapped null token"):
        wyscout._formation_player_ids(
            {"bench": [], "lineup": [], "substitutions": ""},
            context="formation",
        )


def test_inventory_rejects_extra_partial_sidecar_symlink_and_unsafe_modes(tmp_path: Path) -> None:
    queue_name = f"{'a' * 64}.identity-review-queue.json"
    bundle_name = f"{'b' * 64}.identity-bundle.json"
    root = tmp_path / "identity"
    (root / "review-queues").mkdir(parents=True)
    (root / "bundles").mkdir()
    queue_path = root / "review-queues" / queue_name
    bundle_path = root / "bundles" / bundle_name
    queue_path.write_bytes(b"queue\n")
    os.chmod(queue_path, 0o600)

    with pytest.raises(wyscout.WyscoutIdentityPathError, match="partial"):
        wyscout._check_inventory(
            root,
            queue_filename=queue_name,
            bundle_filename=bundle_name,
            allow_absent=False,
        )

    bundle_path.write_bytes(b"bundle\n")
    os.chmod(bundle_path, 0o600)
    wyscout._check_inventory(
        root,
        queue_filename=queue_name,
        bundle_filename=bundle_name,
        allow_absent=False,
    )
    sidecar = root / "bundles" / f"{bundle_name}.sha256"
    sidecar.write_text("forbidden", encoding="utf-8")
    os.chmod(sidecar, 0o600)
    with pytest.raises(wyscout.WyscoutIdentityPathError, match="additional"):
        wyscout._check_inventory(
            root,
            queue_filename=queue_name,
            bundle_filename=bundle_name,
            allow_absent=False,
        )
    sidecar.unlink()

    os.chmod(bundle_path, 0o644)
    with pytest.raises(wyscout.WyscoutIdentityPathError, match="mode"):
        wyscout._identity_inventory(root)
    os.chmod(bundle_path, 0o600)
    bundle_path.unlink()
    bundle_path.symlink_to(queue_path)
    with pytest.raises(wyscout.WyscoutIdentityPathError, match="regular"):
        wyscout._identity_inventory(root)


def test_loader_recomputes_source_before_considering_a_caller_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class SourceRecomputationObserved(RuntimeError):
        pass

    def observe_recomputation(*, source_root: Path, manifest_root: Path) -> None:
        assert source_root == Path("source")
        assert manifest_root == Path("manifests")
        raise SourceRecomputationObserved

    monkeypatch.setattr(wyscout, "build_initial_identity_bundle", observe_recomputation)
    with pytest.raises(SourceRecomputationObserved):
        wyscout.load_initial_identity_bundle(
            source_root=Path("source"),
            manifest_root=Path("manifests"),
            identity_root=wyscout._PROJECT_ROOT / wyscout._IDENTITY_ROOT_RELATIVE,
            identity_bundle_sha256="b" * 64,
        )
