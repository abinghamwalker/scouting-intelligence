# W04 possession semantic v2 decision R3 — master verification

## Decision

`ACCEPT_FOR_INDEPENDENT_REVIEW`. R3 corrects the sole R2 master finding without
changing any declarative authority byte. The producer changed exactly its
focused executable contract and R3 return.

This is not possession-v2 acceptance. It releases only the fresh independent
review packet.

## Complete bounded readback

The only executable change moves `possession_ordinal = 0` inside each exact
`(action_match_source_id, action_period_code)` group. The new regression uses
two match-period scopes, interleaves their actions, reverses the full
presentation, and requires complete per-record result equality with exact
scope-local identifiers.

Frozen authority and evidence hashes remain:

```text
decision physical/canonical SHA-256:
8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425
candidate physical SHA-256:
24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187
candidate canonical SHA-256:
3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881
R2 focused contract SHA-256:
abe342c9cdec1ea35fd799a1205a9e99b1f4a2fdd2ac6dd2ae30f26b40f1dc98
R3 focused contract SHA-256:
1a2bd111c046781c3e4fe6ebff58a716f1bf793a3df29ea2aaf073fc9896100c
R2 return SHA-256:
80c86eeb2cef54b84ccc5b9c64e8dc08c4dfdbabdea061ef45c8b95134e5e3a7
R3 return SHA-256:
9a8afaed03a01760f3e352c5bd45c060cff3c07537a34ff7bdbdc09ac59c1bde
```

The failed R1 review and its return remain byte-exact at their durable paths
and in the retained `/private/tmp` archive:

```text
review SHA-256:
71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a
return SHA-256:
fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90
```

## Independent master reproduction

The master began with:

```text
uv sync --locked --all-groups
PASS: 83 resolved, 82 audited
```

The exact R2 counterexample was rerun without the producer helper assertions.
Forward and reversed presentations now both produced:

```text
100:1H -> 100:1H:possession:1
200:1H -> 200:1H:possession:1
PASS_MULTISCOPE_INPUT_ORDER_INVARIANT
```

The complete focused suite then passed:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_possession_semantic_v2_authority.py
  tests/contracts/test_w04_possession_semantic_authority.py
  tests/contracts/test_w04_field_semantic_v2_authority.py
PASS: 328 passed
```

Additional master checks:

```text
focused Ruff format/check: PASS
local-only verifier: 25/25 PASS
retained pyc files: 1,145
retained __pycache__ directories: 150
pyc symlinks: 0
git diff --check: PASS
git remote: empty
```

The producer's terminal inventory reproduced its preflight exactly: 1,295
serialized rows, 222,755 bytes, SHA-256
`13fcf204919e60067fa57a0d4c5032b039875872a442f165593484cf6e3a8f52`.

## Review challenge

The fresh reviewer must reconstruct the decision/candidate rather than trust
the focused tests and must challenge:

- exact selector/sequence separation;
- strict type, tag, team, raw/name/label boundaries;
- control/restart transitions, dead-ball attachment, contested buffering,
  equal-clock uncertainty, period closure, and no cross-period state;
- multi-scope input-order invariance and exactly-one assignment;
- all frozen v1 predicates and evidence bytes;
- review/acceptance progression and no-product boundaries.

Any P0-P2 finding is `REWORK`; `PASS` requires zero findings.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R2` may start. Possession
acceptance, feature authority, cross-authority work, and all product
implementation remain blocked.
