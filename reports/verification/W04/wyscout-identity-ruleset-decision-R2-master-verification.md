# W04 Wyscout identity-ruleset decision R2 — master verification

## Decision

`ACCEPT_FOR_FRESH_INDEPENDENT_REVIEW`.

The master inspected the complete two-file correction and independently
reproduced closure of all three failed-review findings. Candidate, upstream,
R21, and archived failed-evidence bytes remain unchanged.

## Correction evidence

| artifact | SHA-256 |
|---|---|
| corrected identity focused contract | `760bac798093a9e3072b4de608610a71ae6638dacac08d11e6c0a5b84a57c4b0` |
| R2 producer return | `74c8f3ff611434f619c3fc958e0bd3f4c4449a09c7d7dc9638d8e03b80abaad3` |

The parser accepts exact-second and exact-six-fraction canonical UTC values,
rejects all other fraction widths/offsets/unreal dates, and round-trips the
authorized spelling byte-for-byte. Decision, review, and acceptance validators
share a five-minute truthful-current-time tolerance. Far-future review and
acceptance clocks now fail independently. Live progression derives
`REVIEW_PASS` or `REVIEW_REWORK` from the valid machine recommendation, while
acceptance still requires independent `PASS`.

## Master-reproduced checks

```text
uv run ruff format --check tests/contracts/test_w04_identity_ruleset_authority.py
PASS — 1 file already formatted

uv run ruff check tests/contracts/test_w04_identity_ruleset_authority.py
PASS — All checks passed

uv run mypy tests/contracts/test_w04_identity_ruleset_authority.py
PASS — no issues in 1 source file

uv run pytest -q tests/contracts/test_w04_identity_ruleset_authority.py \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS — 146 passed in 6.21s

git diff --check
PASS

git remote
PASS — empty
```

## Preservation

Decision SHA-256 remains
`6df848be8462af0747d4be4469a07ecca75c0e3d83c497eeddc0a764452b6192`;
ruleset physical SHA-256 remains
`8027321bda566188019850f9f9031e684d2d81d8df7851ba3c71b1685ae4f547`;
ruleset canonical SHA-256 remains
`9c34783214d084ce8fde42be771850e8f9332fa9fb9a1529b011a8600e34e87c`.
Both archived failed-evidence digests also remain exact.

No acceptance or product work is authorized by this candidate readback.
