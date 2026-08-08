# W04 Wyscout data contracts R2 — master verification

## Decision

`REWORK`.

The R2 producer checks and the fresh independent review suite pass, but the
independent reviewer and master direct-constructor probes reproduce nine bounded
P1 contract gaps. Seven are reported by the independent reviewer; two additional
master findings cover the full rejected-field authority surface and the missing
Silver-action basis for the four Gold counts. These are contract/test defects
inside the frozen R20/R21 scope. No executable evidence supports an R22
architecture revision.

Bronze, Silver, Gold, identity-runtime product projection, manifests, receipts,
and downstream product implementation remain blocked.

## Reviewed artifact identity

| Artifact | SHA-256 |
|---|---|
| `src/scouting/contracts/wyscout_data.py` | `87dc13ada636e018ff9dfc17b548942a1d93132db8a615248cc8be3b23ebe99d` |
| `tests/contracts/test_wyscout_data_contracts.py` | `1b5aafbd127cda6703dce8de358b10c6f4c467de0821601b6b358564a5dabd47` |
| R2 producer return | `b855798a3be49093e0ceff78122bde3b2dcd893d99a1cafef43275f6138ad34c` |
| R2 independent review | `38f2bb9fd6971bf1e9a38aed44dd2acd59b3187124204b69152ad43c80bfcd8a` |
| R2 reviewer return | `665ffc80ad31f20e6ddff523c71a0b7960923c808aec476df8fd68b8387be331` |

All packet-fixed R20/R21, source, identity, field-v2, possession-v2,
supported-feature, product-contract-preimage, and schema-bundle-preimage
digests reproduce exactly.

## Master-reproduced prescribed checks

```text
uv run ruff format --check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS — 2 files already formatted

uv run ruff check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS

uv run mypy src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS

uv run lint-imports
PASS — 30 files, 46 dependencies, 3 contracts kept, 0 broken

uv run pytest -q tests/contracts/test_wyscout_data_contracts.py \
  tests/contracts/test_foundation_contracts.py \
  tests/contracts/test_w04_identity_ruleset_authority.py \
  tests/contracts/test_w04_r21_cross_authority_composability.py \
  tests/unit/test_wyscout_source_manifest.py
PASS — 370 passed

uv run bandit -q -r src/scouting/contracts/wyscout_data.py
PASS

uv run python scripts/verify_local_only.py
PASS — 25/25 and git remote empty

git diff --check
PASS

git remote
PASS — empty
```

The independent reviewer separately reproduced the exact packet suite as
370 passed in 77.84 seconds and the selected R1 closure matrix as 95 passed,
45 deselected.

## Master-reproduced fail-open probes

Validated public-constructor probes independently produced:

```text
forged_subevent_outcome ACCEPTED
unmapped_pair_eligible ACCEPTED
duplicate_physical_source_row ACCEPTED
match_partition_drift ACCEPTED france
identity_pair_substitution ACCEPTED
gold_coverage_drift ACCEPTED
applicability_reason_drift ACCEPTED
zero_row_zero_byte_entry ACCEPTED
unproven_fact_gold_action_count ACCEPTED
generic_registry_rejected_field REJECTED:
  rejected subevent fields require an action source row
```

The last result is fail-closed in the wrong direction: the shared rejected-field
product cannot represent the accepted field-v2 `competition/$.name/FORBIDDEN`
row. R20 requires rejected-field evidence across all known record kinds, while
R21 changes only the strict `action/$.subEventId` transform and reason matrix.

The player-match probe changed `action_count` to `999`, changed Gold
`action_count` to the same value, and was accepted because the fact does not
carry a closed set of contributing `SilverAction`/possession evidence from which
the three action-based features can be recomputed. Gold-to-fact equality is not
raw-to-Gold reconciliation.

## Required bounded R3 correction

R3 is limited to the existing data-contract module, its focused tests, and a
producer return. It must close:

1. forged public `ActionSubeventOutcome`;
2. possession-v2 eligibility/state drift;
3. ambiguous physical source rows and partition selection;
4. identity dependency UUIDv5/digest substitution;
5. the complete 119-row rejected-field authority surface, retaining R21's
   special strict subevent matrix;
6. player-match action/position/possession counts not derived from closed
   contributing Silver evidence;
7. Gold coverage not aggregated from contributing facts;
8. arbitrary applicability reason codes; and
9. zero-row or zero-byte Parquet manifest entries.

The identity bundle remains a dynamic content-addressed runtime authority:
R3 must validate its exact UUIDv5 preimage from its digest and accepted clocks,
not invent a fixed bundle digest or architecture change.

After R3 producer return, a new fresh independent review and master acceptance
are mandatory. Only then will the master run the complete repository gate
required before the raw-to-Gold vertical slice.

No provider, rights, source, authority, architecture, feature roster, project
root, dependency, storage, network, cloud, container, hosted CI, endpoint, or
deployment change is authorized.
