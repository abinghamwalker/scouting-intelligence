# W04 Wyscout data contracts R3 — master verification

## Disposition

`REWORK`

R3 closes the nine R2/master finding families covered by its submitted test
matrix, but master readback and direct public-constructor probes found three
remaining P1 failures. These failures are bounded to the executable data
contracts and tests. They do not require an R22 authority, a changed feature
roster, a changed project/dependency/storage boundary, or product bytes.

Open findings: `P0=0`, `P1=3`, `P2=0`.

## Fixed reviewed bytes

```text
src/scouting/contracts/wyscout_data.py
53abc69b85a1a60c13107a8b0a09ee6e066e792b1667c866cf9a9c3f5fd242ff

tests/contracts/test_wyscout_data_contracts.py
f13b5ccb8930bef22c94f74feeda1b66c87224704458c0460de022e66af3764b

reports/reviews/W04/returns/W04-DATA-CONTRACTS-01-R3.md
338c01c40b1913db384b6e0c02ea3d1bdbb01f581f6c3de84baabe54769b36a9
```

The master read the complete implementation, complete focused test module, and
producer return. Accepted R20/R21, field-v2, possession-v2, feature-v1,
identity-v1, source-manifest, and preimage bytes were not changed.

## Reproduced producer checks

The complete R3 packet suite passed:

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
437 passed in 77.64s

uv run bandit -q -r src/scouting/contracts/wyscout_data.py
PASS

uv run python scripts/verify_local_only.py
PASS: 25 checks, 0 failures

git diff --check
PASS

git remote
PASS: empty output
```

The passing submitted suite is necessary but not sufficient because the
following public-constructor probes remain fail-open.

## W04DCR3-P1-001 — player-match coverage remains caller-forgeable

Starting from the accepted in-memory one-action fact, the master changed every
coverage dimension from `numerator=1, denominator=1` to
`numerator=2, denominator=2`, leaving the embedded action, lineup, possession,
identity, and temporal evidence unchanged.

```text
forged_fact_coverage ACCEPTED
[(2, 2), (2, 2), (2, 2), (2, 2), (2, 2), (2, 2)]
```

`SilverPlayerMatchFact.model_validate` accepted the forged values. Gold then
faithfully aggregates those unproven fact values. R20 section 6.3 defines the
six integer numerators and denominators from concrete identity, lineup, action,
coordinate, possession, and temporal evidence; caller-supplied dimension
objects are not authority.

R4 must make the fact boundary derive all six dimensions from closed evidence.
Constraining the fixture to `1/1`, adding duplicate caller-supplied counters, or
validating only Gold aggregation is insufficient.

## W04DCR3-P1-002 — invalid positions count as the supported coordinate feature

The master replaced the valid position with preserved anomaly
`x=-1, y=50, within_accepted_bounds=false` and rebuilt the action, possession,
and fact without changing `coordinate_known_action_count=1`.

```text
out_of_bounds_coordinate_known ACCEPTED 1 False
```

The fact derives the count through `bool(action.action_positions)`. The accepted
feature-v1 applicability contract requires one or two accepted positions with
both finite axes within inclusive `0..100`; the anomaly must remain evidence
but must not count.

R4 must use the exact accepted-position predicate, including cardinality, axes,
finite numeric values, and bounds, for fact and Gold feature derivation.

## W04DCR3-P1-003 — contested possession is resolved before sequence evidence

The accepted possession-v2 predicate for strict pair `(1,10)` is `CONTESTED`
with `BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION`. R3 derives
`ELIGIBLE_RESOLVED` from the admitted pair and a team before evaluating the
same-period sequence. A singleton contested `SilverPossession` and a fact with
`resolved_possession_action_count=1` are therefore accepted without the
required following resolved control.

R4 must bind possession resolution to the complete ordered same-match,
same-period action evidence required by the frozen selector and sequence
policies. It must distinguish predicate admission from final deterministic
resolution and derive possession membership and the supported resolved count
from the final sequence. A caller-selected same-team subset is insufficient.

## Scope and progression gate

- No architecture revision is opened.
- No source/provider acquisition was performed.
- No raw, Bronze, Silver, Gold, manifest, receipt, or runtime product byte was
  created or modified by this review.
- No dependency or lockfile was changed.
- No remote, cloud service, container, hosted CI, public endpoint, or
  deployment was created.
- Downstream implementation remains blocked until bounded R4 implementation,
  fresh independent review, master acceptance, and the complete repository
  master gate all pass.

