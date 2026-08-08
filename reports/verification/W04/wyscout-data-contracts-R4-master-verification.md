# W04 Wyscout data contracts R4 — master verification

## Disposition

`REWORK`

The R4 candidate directly closes the three narrow R3 examples in its submitted
matrix, and its full focused packet suite passes. Master readback found that the
new completeness proof is still caller-declared, however, and that the frozen
equal-clock cross-team uncertainty rule leaves one simultaneous action
resolved. Product progression therefore remains blocked.

Current master findings: `P0=0`, `P1=2`, `P2=0`.

## Fixed candidate bytes

```text
src/scouting/contracts/wyscout_data.py
2ca2862550c48a8db899f25c26612d694a7ca8041416cf0aae4dcd39b5a2bb5e

tests/contracts/test_wyscout_data_contracts.py
0ddb9e2bd31dded899a68b7b6344cf17321dffe947ab6dffc98267eb918bdc69

reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R4.md
f66c4ea9133a23394d67d81d4f7badf989be39594eb2fec7165f9928a429be68
```

The master read the complete R4 return and every new possession-sequence,
accepted-position, fact-evidence, fact-coverage, and regression section. No
accepted authority, preimage, source, dependency, lockfile, or R20/R21 byte
changed.

## Independently reproduced packet suite

```text
uv run ruff format --check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
2 files already formatted

uv run ruff check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
All checks passed

uv run mypy src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
Success: no issues found in 2 source files

uv run lint-imports
3 contracts kept, 0 broken

uv run pytest -q tests/contracts/test_wyscout_data_contracts.py \
  tests/contracts/test_foundation_contracts.py \
  tests/contracts/test_w04_identity_ruleset_authority.py \
  tests/contracts/test_w04_r21_cross_authority_composability.py \
  tests/unit/test_wyscout_source_manifest.py
452 passed in 75.87s

uv run bandit -q -r src/scouting/contracts/wyscout_data.py
PASS

uv run python scripts/verify_local_only.py
PASS: 25 checks, 0 failures

git diff --check
PASS

git remote
PASS: empty output
```

The passing suite confirms the submitted cases, but it does not prove the
following two public-boundary properties.

## W04DCR4-P1-001 — complete-period evidence can be truncated consistently

The master started with the R4 positive two-action sequence: contested `(1,10)`
followed by CONTROL `(7,70)`. The lineage retained both physical action rows.
The probe then:

1. removed the contested action from `PossessionPeriodSequence.actions`;
2. changed caller-supplied `period_action_count` from two to one;
3. rebuilt the remaining `SilverAction` with that sequence;
4. rebuilt a singleton `SilverPossession`;
5. rebuilt `SilverPlayerMatchFact` and its derived coverage/counts; and
6. rebuilt `GoldPlayerWindow` with the exact shortened Fact.

Every public constructor accepted:

```text
self_declared_incomplete_period ACCEPTED 1 1 1
```

The literal `complete_period_evidence=true` and equality between
`period_action_count` and the supplied tuple only prove internal consistency.
They do not bind the tuple to all admitted source actions for the match/period.
The lineage still contained the omitted physical action, yet the shortened
Fact and Gold vector promoted `action_count=1`.

Consequences:

- final possession membership is still derived from a caller-selected subset;
- action, identity, possession, and temporal coverage denominators are derived
  from that same subset rather than the full source population; and
- the original fact-coverage and sequence-completeness P1 families are not
  closed at the public boundary.

A bounded correction must bind period completeness to independently
recomputable Bronze/source evidence or move the proof to a public factory that
receives and validates the complete admitted population. Another mirrored
count, Boolean, or digest calculated only from the supplied subset is
insufficient.

## W04DCR4-P1-002 — equal-clock cross-team uncertainty resolves the first action

The master created two admitted CONTROL actions at the same period rank and
elapsed clock, with distinct teams and distinct physical ordinals. The frozen
possession-v2 policy is `UNCERTAIN_BOUNDARY_UNASSIGNED`; source ordinal cannot
invent a deterministic football ordering for simultaneous cross-team control.

R4 returned:

```text
equal_clock_cross_team_groups
((3d8a77c2-4cd2-592e-a200-f59c044d54e5,
  (f6298526-f978-58fb-890a-cedd787f338f,)),)
```

The second action is unassigned, but the first simultaneous action remains in
a resolved group. The group was created before the equal-clock conflict was
seen and is not invalidated when the conflict is detected.

The correction must treat the entire same-clock cross-team control boundary as
uncertain and unassigned, including any pending contested evidence attached at
that clock, while preserving deterministic groups completed before that
boundary.

## Scope and progression gate

- No architecture revision has been opened; a fresh reviewer must classify
  whether compact public-constructor completeness can be corrected within the
  frozen contract or requires explicit source-bound factory evidence.
- No source/provider access or acquisition occurred.
- No raw, Bronze, Silver, Gold, manifest, receipt, serializer, build, or runtime
  product byte was created or modified by this review.
- No dependency, lockfile, remote, cloud service, container, hosted CI, public
  endpoint, or deployment was changed or created.
- Downstream implementation remains blocked pending bounded correction, fresh
  independent PASS, master acceptance, and the complete repository gate.

