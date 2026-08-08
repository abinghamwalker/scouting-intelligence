# W04 Parquet semantic encoder R1 master verification

Date: 2026-07-31

Disposition: `MASTER_FOCUSED_CHECKS_PASS_AWAITING_INDEPENDENT_REVIEW`

The master inspected the complete additive encoder candidate and independently
reproduced its packet suite. This freezes the exact candidate for fresh byte/security
review; it is not final acceptance or publication authority.

## Exact candidate

- format implementation: `2737a4b67eef492b4a5809d302c726470670c0ef2c14a2a7f5fae7d11453c49a`
- focused tests: `271925b89532080dc302abd4d75ee6a78e1382ae67f619bcc26a58c8ac796d05`
- producer return: `5bd75fafe20ae09f01b03563706e20b8cfcf675352afe840ec3d2e4240cc330c`
- physical fixed vector: `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`
- semantic fixed vector: `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`

## Master inspection

- Existing generic JSON/JSONL/Parquet APIs remain present and the legacy guarded-
  storage suite passes unchanged.
- The additive encoder requires a non-empty explicit metadata-free Arrow schema and
  exactly equal table schema, rejects timestamp precision above microseconds and
  non-nullable nulls, and performs no table casting or inference.
- Physical encoding explicitly supplies every R20 Parquet control, including the
  65,536 row-group boundary; the 65,535/65,536/65,537 tests prove `(65535)`,
  `(65536)` and `(65536,1)`.
- Semantic hashing is domain separated and unsigned-64-bit length framed across the
  exact schema descriptor, ordered canonical contract-row bytes and sorted unique
  parent paths. Primary-key tuples are exact, homogeneous, unique and ordered, and
  each is checked against its contract row.
- The fresh review must specifically test whether any non-key divergence between the
  explicit Arrow row and its claimed exact checked contract row can cross this API
  without a later mandatory verifier. Such divergence must either be impossible by
  this accepted boundary or receive bounded REWORK before publication use.
- No product, manifest, receipt, staged, source, provider or deployment byte was
  created.

## Independently reproduced checks

- focused Ruff format/check: PASS.
- focused mypy: PASS.
- focused encoder plus legacy guarded-storage suite: PASS, `50 passed in 1.67s`.
- focused Bandit: PASS.
- import-linter: PASS, 3/3 contracts kept.
- local-only verifier: PASS, 25/25 controls.
- `git diff --check`: PASS.
- `git remote`: PASS, empty output.

Fresh independent review is required before master acceptance or publisher dispatch.
