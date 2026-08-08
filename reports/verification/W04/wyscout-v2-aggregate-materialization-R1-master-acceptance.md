# W04 Wyscout v2 aggregate materialization R1 — master acceptance

Date: 2026-08-02

## Decision

**ACCEPTED.** The exact eight-key implemented-schema-bundle v2 preimage and the
dependent ten-key product-contract v2 preimage are independently verified and may
now be consumed by W04 runtime admission and product construction.

Findings are `P0=0`, `P1=0`, `P2=0`. The logical model, 23-root roster, product
population, 25-key build projection, digest meanings/formulas, reversibility,
validation, temporal safety, evidence guarantees, and local-only boundary remain
unchanged.

## Accepted identities

| Artifact | Logical no-LF SHA-256 | Physical one-LF SHA-256 |
| --- | --- | --- |
| implemented-schema bundle v2 | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |
| product contract v2 | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |

Candidate identities remained fixed through review:

- aggregate implementation: `6cdbb9eaa7d18c5f07d42d6be33d91b014a34824610319f3e55cf5b383c07851`
- deterministic materializer: `f42ce353382b08171c4495e36c0db00d2ea558b4ef8ca081821b13c3e18a4481`
- adversarial tests: `6f44bea5569d95a21930f06031e0e78c7d789468d95b780c263f9be0506bc95e`
- producer verification: `8b881b680816a320b56487d616c1464b0381d3da694d3fd7fc87298b98ac21c1`
- independent review: `40c22ea0f2c6efc4b6e793aecf3992bb32beb1f188a50bbb2e48441853ca1c34`
- reviewer return: `25e825f5a9b34c2e822e94536a1fb3966ec1b430a6e0d54a1b7cec48933b454c`

## Independent evidence accepted

The reviewer independently reconstructed all 23 unique root-content digests and
47 earlier-only dependency edges, then reproduced the schema bundle without using
the candidate config as authority. Only after that digest existed, the reviewer
reconstructed the product contract from the frozen completion/window/receipt and
complete-LayerManifest composition authorities. Twenty-three logical, nine
physical, four unsafe-path, and two write/idempotency attacks behaved fail-closed.

## Fresh master complete-repository gate

- `uv sync --locked --all-groups`: PASS, 83 packages resolved and 82 audited.
- `uv run ruff format --check .`: PASS, 634 files formatted.
- `uv run ruff check .`: PASS.
- `uv run mypy src/scouting scripts`: PASS, 52 source files and 0 issues.
- `uv run lint-imports`: PASS, 3 contracts kept and 0 broken.
- `uv run pytest -q`: PASS, 2255 tests in 400.03 seconds; one pre-existing
  Starlette/httpx deprecation warning only.
- `uv run bandit -q -r scripts src`: PASS.
- local Git guard check: PASS, simulated push rejected.
- `uv run python scripts/verify_local_only.py`: PASS, 25 checks and 0 failures.
- deterministic aggregate `--check`: PASS with both accepted logical identities.
- `git diff --check`: PASS.
- `git remote`: PASS, empty.

The full formatting gate exposed one unaccepted Markdown Python block in the R3
schema-closure acceptance-oracle report. Its code-block indentation was corrected
mechanically; no executable, authority value, accepted candidate, or digest
formula changed.

## Continuation authority

Downstream work must bind exactly these two logical v2 identities. It may not use
either physical one-LF hash, either v1 predecessor, a placeholder, anticipated
digest, rehash, self-reference, or product-derived substitute. Runtime admission
and raw-to-Gold publication remain subject to their own producer, independent
review, master acceptance, and complete repository gates.
