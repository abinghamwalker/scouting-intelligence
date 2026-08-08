# W05 role taxonomy independent review — R2

## Verdict

- **PASS — P0: 0; P1: 0; P2: 0**
- R1 finding `W05-ROLES-R1-P1-01` is closed. The accepted full claim-bearing taxonomy is
  now one normally validated `FootballResponsibilityTaxonomy`; its public canonical digest
  is the unchanged accepted `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`.
- No accepted taxonomy/config/fixture byte or contextual-membership behavior changed.

## R1 P1 closure

The exact R1 public-contract probe now succeeds:

- `load_role_taxonomy(...).contract.model_dump(mode="python")` revalidates through
  `FootballResponsibilityTaxonomy.model_validate` and returns an equal contract;
- `digest_for_payload` over both Python-mode and JSON-mode dumps returns `596886...`;
- the contract itself carries all five accepted claim-bearing fields: canonical order,
  expert-validation status, external expert evidence, claim, and exemplar notice;
- `rg -n "model_construct" src/scouting/roles` returned exit 1 with no match;
- the loader uses ordinary `FootballResponsibilityTaxonomy.model_validate` and translates
  validation failures to `RoleTaxonomyError`.

The R1 split identity (`596886...` full config versus `26e90f...` core projection) no
longer exists. The public shared contract and the accepted config have one digest meaning.

## Fully re-signed substitutions

Every mutation recomputed the full private canonical digest, independently recomputed the
same digest through `FootballResponsibilityTaxonomy.digest_for_payload`, and first formed
a valid generic public taxonomy contract. The W05 role loader then rejected it:

| Mutation | Identity handling | Result |
| --- | --- | --- |
| Responsibility label | unchanged accepted pin | rejected: accepted-identity mismatch |
| Role label | unchanged accepted pin | rejected: accepted-identity mismatch |
| Mapping changed to another declared role | unchanged accepted pin | rejected: accepted-identity mismatch |
| Claim changed to `expert_validated` | mutated identity repinned in-memory | rejected: claim must remain synthetic-development-only |
| Expert status changed to `PERFORMED` | mutated identity repinned in-memory | rejected: status must remain `NOT_PERFORMED` |
| External expert evidence changed to a fabricated entry | mutated identity repinned in-memory | rejected: evidence must remain empty |
| Exemplar notice changed to replacement language | mutated identity repinned in-memory | rejected: falsifiability notice must remain exact |

The first three prove content identity closes responsibility/role/mapping substitution.
The latter four prove the exact W05 claim boundary still rejects a fully re-signed generic
taxonomy even if the accepted-identity pin is deliberately moved so validation reaches
the boundary check.

## Accepted bytes and fixture alignment

| Artifact | Physical SHA-256 | Logical digest | Evidence |
| --- | --- | --- | --- |
| Taxonomy config | `70d14a28a4f4198adaea55f04d0753a6a6fc62748e75fb2c5ef86d42ec814812` | `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097` | 3,359 bytes; exact canonical JSON plus newline |
| Role fixture | `e5fc8d127018619805577eb00a7ee2fcfe5f7c15022190f01d4148729929c3f0` | `d087269c83342051fe0274641d91ac1598963af88fda81bf7d5e95916f389b67` | 11,654 bytes; exact canonical JSON plus newline |

These physical hashes equal the pre/post-R2 values recorded by the implementer, and the
logical identities/content are unchanged from the R1 independent readback. The role
fixture still pins feature-fixture digest
`7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545`.

The fixture loader reproduced all 18 rows. Its 18 unique player/cutoff keys exactly equal
the 18 complete feature-fixture keys, remain disjoint from the four edge rows, and every
expected probability tuple reproduced.

## Context and fail-closed behavior

- Repeated calls and reversed evidence-key order returned identical values.
- Memberships remain sorted by all six role codes and Decimal string projection sums
  exactly to `1.0000000000000000`.
- One player with different window evidence produced different contextual distributions.
- Empty context and non-UUID player identity reject.
- Empty/all-zero evidence without a prior, unknown responsibility/prior, negative, NaN,
  infinity, and boolean evidence reject with `RoleTaxonomyError`.
- All-zero evidence with the admitted `CENTRE_FORWARD` prior yields probability 1 only for
  `penalty_area_forward`; no uniform role is invented.
- No permanent/primary role field exists, source mappings remain priors, and exemplars do
  not enter inference.

## Downstream M0 binding boundary

Generic `M0ArtifactManifest` construction remains capable of carrying an arbitrary
well-formed SHA-256 taxonomy string. This is not a residual role-loader blocker because
the master-issued R2 implementation authority explicitly states at
`orchestration/task_packets/W05-ROLES-01-R2.yaml:94` that later model work **must source
its pins from this validated contract object**, while model/artifact/serving implementation
is excluded from R2. The authenticated object now provides one valid ID/version/digest
source tuple.

The future model producer and its independent review must enforce that requirement at the
producer API and substitution tests. An arbitrary raw digest passed directly to the
generic manifest contract is outside the role API; it must not become an admitted model
production path. The currently planned model packet cannot be dispatched unchanged
because its predecessor reference is stale; its revised dispatch must retain the R2
source-pin constraint. This is a downstream packet-integration condition, not a present
P0/P1/P2 defect in the reviewed role implementation.

## Six W05 blocker tests

| Blocker test | Verdict | Evidence |
| --- | --- | --- |
| 1. Admitted feature/artifact/ranking/result-byte change | **PASS in packet scope** | One authenticated taxonomy contract/digest now exists; role-loader re-signed substitutions reject. Future model pins are explicitly constrained to source from it. |
| 2. Temporal leakage or lineage substitution | **PASS** | Exact player/cutoff alignment remains complete and disjoint from edge rows; no temporal path changed. |
| 3. Training-serving or batch-request parity break | **PASS in packet scope** | One deterministic contextual-membership path remains; repeat/order probes agree. |
| 4. False explanation, confidence or claim | **PASS** | Claim, expert status/evidence, and exemplar substitutions reject after full re-signing and identity repinning. |
| 5. Unauthorized code/data or local-only violation | **PASS** | Local-only verifier passed all 25 checks; review wrote only its two authorized reports. |
| 6. Reproducible P0/P1 correctness/security defect | **PASS** | R1 strict revalidation/digest probe now succeeds; no new P0/P1/P2 defect reproduced. |

## Acceptance checks

| Command | Exit | Result |
| --- | ---: | --- |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r2-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_roles.py tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py tests/contracts/test_foundation_contracts.py` | 0 | 102 passed in 0.22s |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r2-uv-cache uv run --no-sync ruff check src/scouting/contracts/m0.py src/scouting/roles tests/contracts/test_w05_m0_contracts.py tests/unit/test_w05_roles.py` | 0 | all checks passed |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r2-uv-cache uv run --no-sync mypy src/scouting/contracts/m0.py src/scouting/roles` | 0 | no issues in 3 source files |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r2-uv-cache uv run --no-sync lint-imports` | 0 | 3 kept, 0 broken; 44 files/83 dependencies |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r2-uv-cache uv run --no-sync python scripts/verify_local_only.py` | 0 | PASS; all 25 checks |

## Scope

No source, config, fixture, test, orchestration, dependency, lock, generated-data, or Git
change was made. No delegation was used. Only this report and the mandatory R2 return were
written.
