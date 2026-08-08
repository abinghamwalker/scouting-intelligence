# W04 EXACT_DECIMAL128_WITH_EXPONENT R2 master acceptance

- Date: 2026-08-02
- Master: `/root`
- Decision: `ACCEPT`
- Findings after fresh review: `P0 0 / P1 0 / P2 0`

The master accepts the exact R2 reversible physical Decimal projection primitive
for downstream R5 schema adoption. This acceptance grants no aggregate, product,
publication or checkpoint authority.

## Accepted candidate

| Artifact | SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9` |
| focused serializer tests | `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89` |
| R2 producer return | `d06ff314c83c17964e96e6ea877e78187b9c7411d1b1ee12259f4f49b5e2556a` |
| fresh R2 independent review | `ecabf15644ae295ebad6e6decab03a02f7c9d0ada9ccaad09974848353c1ab17` |
| fresh R2 reviewer return | `b9efe2cb6e3b79cba4a513a9895f620dd2fc299df00547a40d7cd5989f1b227e` |

## Acceptance basis

- The only new projection kind is `EXACT_DECIMAL128_WITH_EXPONENT`, represented by
  exact ordered, metadata-free, non-null children `value: decimal128(22,18)`,
  `exponent: int8`, and `negative_zero: bool`.
- Forward projection accepts only exact finite built-in `Decimal` values, reruns
  the accepted lexical capacity/source-scale rule, traps rounding, preserves the
  exact tuple exponent and records signed zero separately.
- Inverse projection requires the exact struct and runtime child values, rejects a
  nonzero negative-zero claim, traps exponent reconstruction that would round,
  explicitly sets rather than toggles the Boolean-authorized zero sign, reruns the
  same capacity/source-scale rule, and remains subject to the existing exact
  logical-row JSON-byte equality before semantic hashing or writing.
- Fresh review independently passed 13 success/byte vectors, all four incoming-zero
  sign/Boolean combinations, and 57 forward/inverse/descriptor/schema/metadata/
  alias attacks with semantic-hash calls `0` and Parquet writes `0` on invalid
  paths.
- Coverage remains on `CANONICAL_DECIMAL_UTF8`; digest meaning/formula, generic
  storage behavior, dependencies and the local-only boundary are unchanged.

## Master reproduction

- `uv sync --locked --all-groups`: exit `0`, 83 resolved / 82 audited.
- Ruff format/check and mypy on the two candidate paths: exit `0`.
- focused serializer plus guarded-storage suite: exit `0`, `297 passed`.
- Bandit on `src/scouting/storage/formats.py`: exit `0`, no findings.
- import-linter: exit `0`, `3 kept / 0 broken`.
- local-only verifier: exit `0`, 25 controls PASS and zero remotes.
- `git diff --check`: exit `0`; `git remote`: empty.

R1's single independent P1 signed-zero finding remains retained as rework evidence.
The preserved partial R5 23-root closure may now adopt this accepted projection only
for non-coverage Decimal fields that were scalar `decimal128(22,18)`.
