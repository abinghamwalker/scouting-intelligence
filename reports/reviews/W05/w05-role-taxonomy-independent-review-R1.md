# W05 role taxonomy independent review — R1

## Verdict

- **REWORK — P0: 0; P1: 1; P2: 0**
- The football-language content, accepted-identity substitution rejection, deterministic
  contextual probability behaviour, fail-closed inputs, claim boundary, and exact
  18-row fixture alignment reproduce.
- One P1 contract-truth blocker remains: `RoleTaxonomy.contract` is not a valid
  `FootballResponsibilityTaxonomy`. The loader knowingly admits it only through
  `model_construct`, and the digest it exposes cannot presently serve as a semantically
  authenticated public-taxonomy digest for downstream M0 manifests/results.

## P1 finding

### W05-ROLES-R1-P1-01 — The public taxonomy projection is invalid and downstream M0 binding authenticates only an unchecked string

`load_role_taxonomy` validates the full JSON with its private loader, then bypasses the
shared strict contract validator at `src/scouting/roles/taxonomy.py:249-261`. The full
config digest binds the five claim-boundary fields that the shared
`FootballResponsibilityTaxonomy` does not declare. Consequently:

- accepted full-config digest: `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`;
- strict shared-contract canonical digest over the projected contract payload:
  `26e90f5780f6be45d1e94c13089e3f15d6c10667d5d15f64f0678450d127794c`;
- `FootballResponsibilityTaxonomy.model_validate(
  loaded.contract.model_dump(mode="python"))` rejects with
  `taxonomy_digest must equal canonical taxonomy SHA-256 digest`;
- replacing the projected digest with `26e90f...` makes that core payload valid, proving
  that the content closure/order is sound and the blocker is specifically the incompatible
  public schema/digest definition;
- strict validation of the raw full config also rejects its undeclared claim-boundary
  fields (and its JSON lists do not satisfy strict Python tuple inputs).

Downstream exact equality is internally consistent but not semantic authentication.
A normally constructed, fully re-signed `M0ArtifactManifest` and `M0RetrievalResult`
accepted the invalid config digest, and the same normal constructors also accepted
`ffffffff...ffffffff` as the taxonomy digest when all containing digests were recomputed.
The pinned request then exactly equalled the manifest, as designed. Thus the M0 surface
proves string equality but does not prove that the string is the canonical digest of a
valid `FootballResponsibilityTaxonomy`. The current invalid origin therefore cannot safely
bind downstream M0 taxonomy semantics or claim boundaries.

Impact: a consumer using the public strict taxonomy contract cannot reconstruct or
validate the taxonomy named by an otherwise valid M0 manifest/result. Different consumers
can treat `596886...` as the full claim-bearing taxonomy identity or require `26e90f...`
as the shared-contract identity. This is a reproducible cross-boundary identity and claim
ambiguity, not a hash collision or a failure of the private accepted-config pin.

Smallest bounded correction:

1. Make the shared strict taxonomy representation declare the full accepted semantic
   surface (`canonical_order`, expert status/evidence, claim, and exemplar notice), with
   one canonical digest algorithm that reproduces the accepted full-config digest.
2. Replace `model_construct` with normal strict validation and add a regression asserting
   that the returned `RoleTaxonomy.contract` revalidates and recomputes its own digest.
3. At the M0 producer/binding boundary, require the authenticated valid taxonomy object
   (or an equivalent validated taxonomy identity object) as the source of the three
   taxonomy pins; add a re-signed arbitrary-digest rejection probe. Exact pin comparisons
   can remain unchanged.

This correction requires shared-contract/M0 ownership outside this review packet; no
implementation change was made.

## Direct taxonomy substitution probes

| Probe | Result |
| --- | --- |
| Same ID/version, changed role label, full config re-signed | Rejected: `taxonomy accepted-identity mismatch`. |
| Reordered roles, full config re-signed, identity repinned in-memory so structure is reached | Rejected: roles must be unique and ordered by code. |
| Dangling mapped role, full config re-signed, identity repinned in-memory | Rejected: mappings must reference declared roles. |
| Claim changed to `expert_validated`, full config re-signed, identity repinned in-memory | Rejected: claim must remain synthetic-development-only. |
| Public strict revalidation of the actual loaded projection | Rejected because `596886... != 26e90f...`. |

The accepted identity pin and structural checks therefore reject same-ID changed content,
order ambiguity, dangling references, and claim substitution. They do not cure the invalid
shared-contract projection.

## Context, probability, and fail-closed probes

- Repeated calls and differently ordered evidence mappings returned identical membership.
- Memberships were ordered by all six role codes and their decimal string projections
  summed exactly to `1.0000000000000000`.
- The same player under two explicit context IDs with different responsibility evidence
  returned different distributions. Context remained mandatory and present in the output.
- All-zero or empty evidence without a prior rejected; all-zero evidence with the admitted
  `CENTRE_FORWARD` prior produced probability `1.0` only for
  `penalty_area_forward`, not a uniform distribution.
- Unknown responsibility, unknown source prior, negative, `NaN`, infinity, and boolean
  evidence all rejected with `RoleTaxonomyError`.
- No permanent/primary role is produced or persisted. The source-label mapping contributes
  one declared prior unit only, and no exemplar enters inference.

## Football language and claim boundary

The eight responsibilities are readable football actions/responsibilities, and the six
role labels describe contextual responsibility bundles rather than quality, recruitment
outcome, or permanent identity. The config fixes `expert_validation_status=NOT_PERFORMED`,
empty external expert evidence, a synthetic-development-only claim, and the exemplar
non-replacement notice. The role fixture is synthetic-development-only. The implementation
return expressly disclaims expert, provider, production-validity, and permanent-label
claims. No Wyscout-derived role evidence or W06 protected evidence is claimed.

## Fixture alignment

- Role fixture digest independently recomputed:
  `d087269c83342051fe0274641d91ac1598963af88fda81bf7d5e95916f389b67`.
- Feature fixture digest independently recomputed and matched the role fixture pin:
  `7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545`.
- Loaded role rows: 18; unique player/cutoff keys: 18; complete feature rows: 18.
- The two key sets were exactly equal and disjoint from the four feature edge rows.
- Every expected membership reproduced through the public role-fixture loader.

## Six W05 blocker tests

| Blocker test | Verdict | Evidence |
| --- | --- | --- |
| 1. Admitted feature/artifact/ranking/result-byte change | **FAIL — P1** | Fully re-signed M0 manifest/result accepted both the invalid config digest and an arbitrary taxonomy digest. Exact containing hashes do not authenticate a valid taxonomy origin. |
| 2. Temporal leakage or lineage substitution | **PASS in packet scope** | Player/cutoff alignment is exact; no temporal or lineage path is added by the role implementation. |
| 3. Training-serving or batch-request parity break | **PASS in packet scope** | Membership has one deterministic path and repeated/order-variant calls agree. The finding is taxonomy contract truth, not a reproduced second scoring path. |
| 4. False explanation, confidence or claim | **FAIL — P1** | The full digest binds claim fields but is invalid under the public contract; the valid core digest omits those fields. Downstream cannot unambiguously validate which claim-bearing taxonomy the pin denotes. |
| 5. Unauthorized code/data or local-only violation | **PASS** | Local-only verification passed all 25 checks; only the two authorized reports were written. |
| 6. Reproducible P0/P1 correctness/security defect | **FAIL — P1** | Public strict validation and normal re-signed M0 construction reproduce W05-ROLES-R1-P1-01. |

## Acceptance checks

| Command | Exit | Result |
| --- | ---: | --- |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_roles.py tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py` | 0 | 56 passed. |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync ruff check src/scouting/roles tests/unit/test_w05_roles.py` | 0 | All checks passed. |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync mypy src/scouting/roles` | 0 | No issues in 2 source files. |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync lint-imports` | 0 | 3 contracts kept, 0 broken; 44 files/83 dependencies. |
| `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python scripts/verify_local_only.py` | 0 | PASS, all 25 checks. |

Passing candidate tests do not cover the invalid `RoleTaxonomy.contract`: the role tests
assert the private full-config digest and use the constructed object, while the shared
contract tests build a different valid taxonomy through the public constructor.

## Scope

No source, config, fixture, test, orchestration, dependency, lock, generated-data, or Git
change was made. No delegation was used. Only this report and the mandatory return were
written.
