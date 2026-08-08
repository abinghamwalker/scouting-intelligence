# W04 Wyscout identity-ruleset decision R3 — master verification

## Decision

`ACCEPT_FOR_FRESH_INDEPENDENT_REVIEW`.

The master inspected the complete R3 correction and independently reproduced
strict master-key behavior. Candidate/upstream/R21 bytes, both archived failed
review generations, and all R2 clock/lifecycle corrections remain unchanged.

## Correction evidence

| artifact | SHA-256 |
|---|---|
| corrected identity focused contract | `bcc9ae2675a33c5e08859ae57fc2f97977ecfec4fcc5925a052662622e139071` |
| R3 producer return | `e3d75f56808d5a913cde8d9c66fe82ee672a698310db6ee274e00d54d62f3391` |

Master-table equality now counts only exact positive Python integers. Boolean,
integral-float, non-integral-float, string, numeric-looking-string, negative,
and zero values cannot satisfy equality. Exactly one valid matching key
resolves; duplicate valid matches and absent valid matches remain
`REVIEW_REQUIRED`; player reference zero remains `REJECT`.

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
PASS — 156 passed in 6.25s

git diff --check
PASS

git remote
PASS — empty
```

No acceptance or product work is authorized by this candidate readback.
