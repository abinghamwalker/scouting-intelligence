# W04 Wyscout four-feature vertical-slice R1 master acceptance

- Date: 2026-08-02
- Producer packet: `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1`
- Review packet: `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-REVIEW-01-R1`
- Master verdict: **ACCEPTED**
- Independent findings: **P0 0 / P1 0 / P2 0**

## Accepted product slice

The master accepts the exact local one-match Wyscout v5 raw-to-Gold product
implementation. The accepted nonempty product population is:

| Product | Rows |
| --- | ---: |
| Bronze known Action | 1768 |
| Bronze rejected field | 3544 |
| Silver Action | 13 |
| Silver lineup stint | 1 |
| Silver possession | 2 |
| Silver player-match fact | 1 |
| Gold player window | 1 |

The rejected-field population is exactly two forbidden name fields for every
Action plus eight strict string `subEventId` transformation failures. No entity,
rejected-record, zero-row quarantine, provider-possession, fifth-feature, rate,
per-90, outcome, value or inferred-role product is emitted.

The checked Silver graph is exactly `13 Action / 2 Possession / 1 Fact / 1 Gold`,
with the accepted right-censored minute-82 lineup. Gold is research-only with
reason `RIGHT_CENSORED_OR_UNCERTAIN` and exact feature vector `(2,2,1,2)`.

Every row is encoded from the accepted root-owned descriptor and descriptor-owned
physical key paths. Seven products precede three complete manifests with entry
counts `(2,4,1)` and parent chains `(), (BRONZE), (SILVER)`. One 15-key temporal
boundary receipt and one nine-key invocation receipt are published only after
complete immutable readback and temporal closure.

The exact no-site rebuild child consumes the frozen closed envelope and inherited
descriptors. Before every atomic publication and again at completion it rechecks
normalized environment, entrypoint source, repository digest, complete
component/resource/count tuple, PYC inventory and code-manifest bytes/semantics.

## Frozen implementation and evidence

| Artifact | Accepted SHA-256 |
| --- | --- |
| product package initializer | `93efbee9739a38cb1c19e43013263fab4e73d0e839117f150464f23c1f430a08` |
| Bronze producer | `672f2c88c6e43b154fd7e26710f5a3ba9d7712441a34d87397e926f90556cf36` |
| Action producer | `34c2ef74b564713c4f0255574d071453aa1ef5d6eb8cb4df5813aa6b62b57087` |
| lineup producer | `4c90c3a97b80cacea5046b945b797d6103c05888fca2dbbecf72c7bd49495b87` |
| possession producer | `197a6883c03c7e7ea26854c75aa3813d5f606cefed396984e7d4f95593f30e84` |
| player-match producer | `784d6a50d6b2f455ed749839814a4c44e79895cd5094be1b2ab6f1ac3e6a75fd` |
| Silver manifest producer | `56628bb9b5b4595f429a487383f35bb659a60728537abad419474417d20c423a` |
| Gold producer | `176495ded91497eca4ae8234889a7079d871eb65180b12fb0570cae4a62d4c04` |
| temporal-boundary producer | `c6a18363799cd714b38829412a0c5acda1fddd3b7c017e5135d6e8e41c1c2478` |
| rebuild composition | `b5e9c5a2e37d3c3190e26496b78fca7deab5f31779d79ecea34113e920f74e55` |
| no-site rebuild child | `82d7a22cc9d48bca19e0f4a6d05f60995f7486df829585fa7bf0b9ab7434ba99` |
| end-to-end tests | `5ce8de532124869eb7e88c55a5504db4d153222525cfa46eb897dc9232a4b83c` |
| security tests | `59e1f8837313690d38132442f789aa4ab4994291e2ef7455705347c1215d2e3e` |
| producer return | `865b3246746b57cc3240b091b63182e01471eadabeca7519cdddd3a14df9adcc` |
| independent review | `109fbcf78972d2cd9c452017b655b672d60470698a8c333d9271385a092e10d0` |
| reviewer return | `a15753aa0817c1f625251a46a5636e65f2d8a2fa32d22bb9acdab0d73935dcd3` |

The independent reviewer directly reconstructed the source oracle, including the
901/867 Action split, match ordinal 379, season source ID 181150, target groups of
seven and six, target team 1631 and minute-82 substitution. It performed three
genuine rebuilds rather than copying producer output, returned 734 passing tests
in 1509.58 seconds, and found no P0-P2 defect. Its pre/post inventories were exact:

- real product roots:
  `b34b7de40d75c7599510557196efe3f5b630e2e880dfe0c1f3bd0cc2e2308e66`;
- repository PYC:
  `d24205b3bd137720e2b0d5a95ea1600c9dd8d7eb7bbae45b0b8c1e9c389f6cb7`;
- selected-site PYC:
  `f7c17e604677fd58c61732eec8f8a80ba8547b5c14ee7802bb28845dda30a2c0`.

## Master reproduction

The master first ran `uv sync --locked --all-groups --offline`: 83 packages
resolved from local state and 82 audited with no change or network access. The
master then ran the complete packet matrix with an isolated temporary uv cache,
`--locked --no-sync`, `PYTHONDONTWRITEBYTECODE=1`, and no pytest cache provider:

- Ruff format: PASS, 13 files formatted.
- Ruff lint: PASS.
- Mypy: PASS, no issues in 11 product/child source files.
- Complete context/publisher/format/completion/contracts/E2E/security pytest:
  **734 passed in 1520.54 seconds (25:20)**.
- Bandit: PASS, no findings.
- Import-linter: PASS, `3 kept / 0 broken`.
- Local-only verifier: PASS, all 25 checks; `main`, zero remotes and active
  rejecting pre-push guard.
- `git diff --check`: PASS.

The master reviewed every producer file, the child envelope/result path, exact
product and manifest ownership, temporal/receipt closure, the complete no-follow
real-root inventory test, independent source reconstruction and every retained
review artifact. No implementation byte changed after producer freeze.

## Acceptance boundary

The producer/reviewer/master loop performed no provider/network operation,
credential access, dependency or lock change, external service, cloud/container,
deployment, real-root product publication, cleanup, or Git mutation. Operational
cache evidence remains preserved. Real local launcher execution, full repository
verification, health/card evidence, `G-W04`, checkpoint and ledger closure remain
master-owned subsequent gates.
