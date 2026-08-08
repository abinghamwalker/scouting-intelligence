# W04 possession semantic v2 decision R2 — master verification

## Decision

`REWORK`. R2 closes the prior selector/sequence overclaim, but the master found
one bounded deterministic-resolution defect in the test-owned executable
contract evidence:

```text
MULTISCOPE_POSSESSION_ID_INPUT_ORDER_DEPENDENCE
```

No architecture revision is required. The declarative authority remains within
the frozen R21 scope, and no product work is authorized.

## Reproduced R2 evidence

Fresh locked environment synchronization resolved 83 packages and audited 82.
The producer's returned bytes and master digest reconstruction are:

```text
decision physical/canonical SHA-256:
8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425
candidate physical SHA-256:
24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187
candidate canonical SHA-256:
3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881
focused test SHA-256:
abe342c9cdec1ea35fd799a1205a9e99b1f4a2fdd2ac6dd2ae30f26b40f1dc98
R2 return SHA-256:
80c86eeb2cef54b84ccc5b9c64e8dc08c4dfdbabdea061ef45c8b95134e5e3a7
```

The selector now returns only `PREDICATE_ADMITTED` or
`PREDICATE_UNMAPPED`; it no longer emits final possession eligibility.
The policy retains the exact five field-v2 inputs, complete 17-key accepted-v1
predecessor, all 36 v1 predicates, and the R20 same-period resolution clauses.

The master reproduced:

```text
focused authority suite: 327 passed
focused Ruff format/check: PASS
local-only verifier: 25/25 PASS
retained pyc files: 1,145
retained __pycache__ directories: 150
pyc symlinks: 0
git diff --check: PASS
git remote: empty
```

The failed R1 independent review and return remain byte-exact:

```text
review SHA-256:
71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a
return SHA-256:
fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90
```

## Master challenge and defect

The executable helper groups actions by `(action_match_source_id,
action_period_code)`, but iterates those groups in first-seen dictionary order
while incrementing one global `possession_ordinal`. Consequently identical
match-period groups receive different resolved possession IDs when only the
input list order changes.

The master executed the same two accepted control actions twice:

```text
forward:
100:1H -> 100:1H:possession:1
200:1H -> 200:1H:possession:2

reversed:
200:1H -> 200:1H:possession:1
100:1H -> 100:1H:possession:2
```

The equality assertion failed with
`AssertionError: input-order-dependent possession IDs`. This contradicts the
declared deterministic per-match/per-period sequence contract even though the
existing 327 tests pass.

## Bounded correction

R3 must change only the focused executable contract and its new return. It must
make possession numbering local to each match-period scope (or use an equally
strict deterministic construction) and add a regression that reverses
interleaved multi-scope inputs while requiring identical per-record outputs.

R3 must not change the decision, candidate, five inputs, predecessor,
predicates, selector, policy, R1/R2 evidence, architecture, or any product
path.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R3` may start. Independent
corrected review, possession acceptance, feature authority, cross-authority
composition, and all Bronze/Silver/Gold work remain blocked.
