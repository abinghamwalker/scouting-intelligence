# W04 Wyscout 23-root schema closure R8 master acceptance

- Date: 2026-08-02
- Producer: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R8`
- Independent review: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R8`
- Status: **MASTER_ACCEPTED**
- Findings: **P0 0 / P1 0 / P2 0**

## Accepted artifacts

| Artifact | SHA-256 |
| --- | --- |
| `src/scouting/contracts/wyscout_schema.py` | `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4` |
| `tests/contracts/test_w04_wyscout_schema_closure.py` | `5daaa32082cc0f82ed9b8b0b61cc06fe9d2db633cb15ed9c9837e491f2b9a5b8` |
| R8 producer return | `2d92e13e53a2d8a8aa3104145c1947da882ef85eeb57bfcefc4acad4310a9a99` |
| R8 independent review | `abdbe28dd2d7c57abc32a310db741e12af52c22172cd0039a6b9b16fa6dbcd35` |
| R8 reviewer return | `afe2c315731359cd688847c2a698269eb18835dcb593101a6482417ca6482bde` |

The earlier R6 and R7 reviews remain retained as exact REWORK evidence. R8 changed
only the test-owned SilverAction matrix; the R7 schema bytes remained unchanged.

## Master reproduction

The master inspected the candidate, R8 matrix correction, independent review and
all fixed hashes, then reproduced:

- schema/build/data/format suite: `595 passed in 125.93s`;
- authority/composability suite: `179 passed in 3.91s`;
- Ruff format/lint, mypy strict, Bandit and import-linter: PASS;
- local-only verifier: PASS, 25 checks, zero failures, branch `main`, zero remotes.

The accepted closure contains exactly 23 ordered implemented roots, 12 executable
descriptor roots, 11 explicit JSON-only roots and earlier-only dependencies. The
runtime predicate ledger reproduces the frozen 56 JSONL rows and SHA-256
`c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`;
all C1-C11 references resolve to material frozen constants and E1-E8 remain
separate external authorities.

Exactly 30 reachable non-coverage Decimal paths use the ordered
`EXACT_DECIMAL128_WITH_EXPONENT` struct (`value: decimal128(22,18)`,
`exponent: int8`, `negative_zero: bool`), while six coverage paths remain
`CANONICAL_DECIMAL_UTF8`. Exact inverse logical-byte reproduction, exponent and
signed-zero preservation, nonzero-negative-zero rejection and capacity validation
all pass.

The frozen 29-row matrix now includes the exact distinct NULL/CONTROL/RESTART
SilverAction variants, scales `(0,18,18)`, no-rounding capacity value
`9999.999999999999999999`, exact lineages/sequences and descriptor-led logical
byte reproduction.

## Acceptance decision

The W04 23-root implemented-schema closure is accepted for downstream master-only
v2 aggregate materialization. Logical models, root roster, features, product
population, authority, digest meaning/formula and local-only boundaries are
unchanged.
