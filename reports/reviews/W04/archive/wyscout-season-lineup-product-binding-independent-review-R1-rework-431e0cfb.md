# W04 season/lineup product-binding independent review R1

Date: 2026-08-01  
Task: `W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R1`  
Reviewer: fresh independent W04 season/lineup product-binding reviewer

## Verdict

`REWORK — AUTHORITY BYTES VALID; PROGRESSION TEST DEFECT`

- Recommendation: `REWORK`
- P0: `0`
- P1: `1`
- P2: `0`
- Immutable decision correction required: `NO`
- Bounded test/progression correction required: `YES`

The additive season and lineup authority is internally sound and reproduces the
authorized one-match, one-row population without widening identity, schema,
feature, Gold, build, or local-only boundaries. The packet cannot receive `PASS`,
however, because both this authority's test and its accepted predecessor's test
encode an unconditional, permanently collected assertion that every intended
downstream product root must not exist. After separately authorized product
implementation creates any Bronze, Silver, Gold, layer-manifest, or rebuild root,
the complete repository gate must fail even when that implementation is correct.

## 1. Fixed-byte admission

Every packet-fixed SHA-256 was independently reproduced before merits analysis:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| authorization | `9802e4ae037593c62db2b52d38acd4133e5a3d50e59e5ad346c982ad8cca47bb` | exact |
| decision | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` | exact |
| decision test | `0b5b933575f22451b5474323188619acec659c7291262c2e457086319fe93e29` | exact |
| producer return | `6bb6f3c70d87034a22487362f688c9f513c22f2d66c2ba9fbae021be01584451` | exact |
| master verification | `d635d3836bf98e46c09d640c89ec1433992836d7951545b81ddd484ef632ffd6` | exact |
| prior decision | `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d` | exact |
| prior acceptance | `9bcd9ef6f61b06f443a4d8f0d590db74559ee739976f285c41127da5ff1f5921` | exact |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | exact |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | exact |
| source manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | exact |
| completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | exact |

The decision is strict canonical JSON with one terminal LF. Its ten ordered
`bound_inputs` were reopened independently and all ten physical digests matched.

## 2. Independent source and identity reconstruction

The strict source manifest binds
`archive-members/matches_England.json` at SHA-256
`620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`,
1,694,720 bytes and 380 rows. Physical ordinal `379` is match `2499719`, has
strict integer `seasonId=181150`, and canonical sorted-record SHA-256
`1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.
The content-addressed completion index binds the same source manifest and member.

The source UUIDv5 namespace independently reproduced as
`89161938-1e8c-53ab-ab52-eba969681833`. From the authorized fixed names, the
independent chains reproduced:

- season namespace `afb775b9-a955-5bfc-80cd-3e941ca2f098` and season UUID
  `4696aa1f-b512-5d18-af79-33cf031455cf`;
- match namespace `20b5206f-dfa5-55b4-84ab-8a336a75073e` and match UUID
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`;
- team UUID `5b353635-819b-5bd1-8ca2-5a7364042a96` and player UUID
  `be8da881-2b15-513f-978f-6bb3865bc8e2`; and
- lineup-stint UUID `591cdf5b-2281-53c4-8225-150313ca2c01` from exact name
  `stint:1631:285508:0:w04-wyscout-lineup-stint-v1` under the match namespace.

The physical match row contains player `285508` exactly once on team `1631`'s
bench, zero times in its starting lineup, and exactly once as `playerIn`, at
minute `82` for `playerOut=192748`. The authority therefore correctly selects one
right-censored stint with interval `[82,83)`, no terminal interval, no elapsed or
bounded minutes, no per-90 eligibility, ordinal zero, and the exact suppression
reason.

## 3. Scope and adversarial attacks

String, Boolean, nonpositive and alternate season values cannot satisfy the
strict integer source binding. Alternate source/season/match namespace names,
canonical names, source IDs, team/player identities, or stint ordinals reproduce
different UUIDs and fail the closed decision. The focused mutation matrix rejects
missing, additional, duplicated, reordered, cross-entity, alternate-ordinal,
terminal/minute-inferred, and per-90-enabled lineup populations, as well as stale
source, index, and prior-authority bindings.

The new authority's projection roster is byte-equal to the predecessor's 25
unique keys. Its only consumption route is the existing `authority_rows` member;
post-hash invocation remains 25 keys, the R20 SHA-256 rule is unchanged, and a
second build hash is forbidden. The decision expressly adds no season identity
kind or bundle row, schema root, supported feature, Gold row, or wider product
population. No runtime, schema, aggregate, product, manifest, receipt, build, or
data byte was created during this review.

## 4. P1 finding: permanent product-absence gate

`tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
lines 800–810 and
`tests/contracts/test_w04_wyscout_build_product_authority.py` lines 679–689 each
define an always-collected test that constructs the intended Bronze, Silver,
Gold, manifest, and rebuild roots and unconditionally requires every
`Path.exists()` result to be false. Neither assertion is conditioned on the
authority lifecycle state, a pre-product phase, or the absence of later product
authorization.

This is currently green only because no product bytes exist. Once a separately
authorized implementation creates even one listed root, at least one generator
element is false and both permanent tests fail during the complete repository
suite. That contradicts the approved progression in which authority acceptance is
followed by product implementation and a complete repository gate. The defect is
bounded to test/progression behavior: retain the frozen decision bytes and retain
pre-implementation absence evidence, but make the repository assertion
lifecycle-aware so it cannot outlaw later authorized products forever.

## 5. Executable verification

All packet acceptance commands passed in the current authority-only state:

- Ruff format: one file already formatted.
- Ruff check: all checks passed.
- mypy: no issues in one source file.
- focused pytest: `157 passed in 3.70s`.
- local-only verification: `PASS`, zero remotes, active `main`, executable
  pre-push guard, Python 3.12.12 root uv environment, and no hosted CI,
  deployment, container, or external service.

These passing focused checks do not discharge the P1 because they execute before
the state transition that deterministically triggers the unconditional absence
assertions.

## 6. Final decision

Return `REWORK` with exactly one P1 finding. Correct only the permanent
test/progression behavior, obtain a fresh independent review, and preserve the
candidate decision and every prior frozen byte. No architecture, population,
schema, feature, provider, dependency, storage, or local-only change is required.

```w04-season-lineup-product-binding-review-v1
{"decision_id":"w04-wyscout-season-lineup-product-binding-decisions-v1","decision_physical_sha256":"3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e","findings":[{"code":"UNCONDITIONAL_PRODUCT_ABSENCE_GATE","severity":"P1","summary":"Both authority test modules permanently require all future product roots to be absent, so the complete repository gate must fail after separately authorized product implementation; preserve authority bytes and make the test progression-aware."}],"recommendation":"REWORK","review_id":"w04-wyscout-season-lineup-product-binding-independent-review-R1","review_schema_version":"w04-season-lineup-product-binding-independent-review-v1","reviewed_at":"2026-08-01T12:33:42Z","reviewed_by":"3d9c3b46-afaa-50ad-a48d-48da4fac0bac"}
```
