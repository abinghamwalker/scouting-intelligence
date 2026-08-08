# W04 Wyscout four-feature vertical-slice independent review R1

- Date: 2026-08-02
- Task: `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-REVIEW-01-R1`
- Candidate: `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1`
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**

## Fixed bindings

All sixteen packet-fixed artifacts matched before any test execution and matched
again after the complete review matrix.

| Artifact | Required and observed SHA-256 |
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
| end-to-end evidence | `5ce8de532124869eb7e88c55a5504db4d153222525cfa46eb897dc9232a4b83c` |
| security evidence | `59e1f8837313690d38132442f789aa4ab4994291e2ef7455705347c1215d2e3e` |
| producer return | `865b3246746b57cc3240b091b63182e01471eadabeca7519cdddd3a14df9adcc` |
| nested-key master acceptance | `5d346c183ac97078a3c9bd2ebe8373ae68ca491487f3ff5ad3403d623cced9ec` |
| runtime-control R5 master acceptance | `a08d2a429c45a52cd7839c41ee3429f91fef227e9e9f41992c8f3a9fdbe8c24c` |

No producer, source, test, configuration, aggregate, dependency, lock, product,
manifest, receipt or orchestration byte was edited by this review.

## Independent source and authority reconstruction

The accepted source was read directly, independently of the product modules.
The observed England event member is 188,888,614 bytes with SHA-256
`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`.
The match member is 1,694,720 bytes with SHA-256
`620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`.

The direct reconstruction found exactly match source ID `2499719`, match row
ordinal `379`, season source ID `181150`, and match raw-record digest
`1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.
The season UUID is `4696aa1f-b512-5d18-af79-33cf031455cf`.

The selected event population is exactly 1,768 Actions: 901 in `1H` and 867 in
`2H`. Every row has both forbidden name fields, producing 3,536 retained
rejected-field rows, and exactly eight rows have string `subEventId=""`,
producing the remaining eight strict no-coercion rejections. The exact total is
therefore 3,544. No rejected-record population is required.

An independent source-order implementation of the accepted integer-pair
possession algorithm found 359 resolved groups. The two groups containing the
target source Actions were exactly:

- team `1631`, seven source Actions:
  `177960876,177960877,177960881,177960883,177960884,177960885,177960888`;
- team `1631`, six source Actions:
  `177961009,177960992,177961013,177961298,177961017,177961018`.

The two target Actions both belong to player source ID `285508`, have accepted
coordinates, and occur in canonical order. The match row independently shows
that player on team `1631`'s bench and entering at nominal minute 82. This
reconciles exactly to lineup-stint ID
`591cdf5b-2281-53c4-8225-150313ca2c01`, start interval `[82,83)`, null end and
minute bounds, right-censored true, and per-90 ineligible.

## Product, schema, key and temporal closure

The implementation consumes the accepted checked-capability APIs at every
checked Action, possession, player-match, Gold and manifest boundary. The
independent run reproduced the complete nonempty product roster with row counts:

```text
Bronze known Action       1768
Bronze rejected field     3544
Silver Action               13
Silver lineup stint          1
Silver possession             2
Silver player-match fact      1
Gold player window            1
```

Every row is projected from the accepted root-owned descriptor, every complete
nested physical key is resolved through the descriptor and Arrow schema, and
every Parquet payload reopens with exact row count. The inverse projection and
canonical contract-row bytes reproduce the logical JSON bytes exactly,
including exact decimal exponent/signed-zero handling and canonical coverage
decimal UTF-8. Semantic and physical digests, primary-key order, parent paths,
and immutable readback all remain closed.

The Silver graph is exactly `13/2/1/1`. The single Fact has complete nested
tenant/source/match/player/schema key and exact target counts `2/2/2`. The one
Gold row has the complete accepted eleven-field nested key, five dependencies,
strict-before temporal proof, `RESEARCH_ONLY` applicability with
`RIGHT_CENSORED_OR_UNCERTAIN`, and feature vector `(2,2,1,2)`. No rate, per-90,
outcome, value, inferred-role or provider-native-possession feature is emitted.

Publication order is products before manifests, with exact manifest entry counts
`(2,4,1)` and exact parent-layer chains `(), (BRONZE), (SILVER)`. All seven
product paths occur exactly once across the manifests. The one 15-key boundary
receipt reopens the Gold product and complete Gold manifest binding. The one
nine-key invocation receipt binds all three manifest summaries and the boundary
summary with `started_at <= checked_at <= completed_at`. Targeted temporal,
manifest and receipt mutations fail before acceptance.

## Genuine rebuild determinism and adversarial review

The reviewed fixture performs three genuine calls to `rebuild_wyscout_v5`; it
does not copy an output tree. It built the same invocation and run ID in two
independently created exact-root mirrors, then rebuilt with a distinct run ID
and fresh staging roots. The two same-run mirrors had identical product,
manifest, boundary-receipt and invocation-receipt file sets and bytes. The
different-run rebuild retained identical product and manifest bytes while both
run-scoped receipt payloads changed.

The complete 734-test matrix challenged source membership/count/digest/type,
strict field transformation, checked-product capability ownership, exact
descriptors and nested keys, Parquet semantic reconstruction, temporal
inequalities, aggregate and manifest completeness, parent chains, receipt
closure, unsafe paths/kinds/links/modes, staged-race/final-recheck failure,
build-identity substitution, provider/network use, and real-root writes.

The frozen child starts as `python -S -B scripts/rebuild_wyscout_v5.py` and
reaches the closed inherited-descriptor/envelope guard without site startup or a
`ModuleNotFoundError`. Source, result, nonce, argv, root and environment fields
are closed. Code installation occurs only after the stdlib guard. Before each
atomic publication and again at completion, the child rechecks normalized child
environment, entrypoint descriptor bytes/metadata, repository digest, complete
component/resource/count tuple, PYC inventory, and code-manifest bytes and
semantics. Independent equality attacks against repository, components,
counts, PYC and code-manifest state each raise before final promotion, leaving
no destination file.

## Complete no-follow inventory and execution boundary

Before tests, complete no-follow content-and-metadata inventories were taken for
the exact real working, manifest and run roots. The working inventory contained
six nodes, the manifest inventory five nodes, and the run root was absent.
Separate inventories covered 110 repository and 1,087 selected-site PYC files.
The same shell procedure after all gates produced byte-identical digests:

| Inventory | Preflight SHA-256 | Postflight SHA-256 |
| --- | --- | --- |
| three exact real output roots | `b34b7de40d75c7599510557196efe3f5b630e2e880dfe0c1f3bd0cc2e2308e66` | `b34b7de40d75c7599510557196efe3f5b630e2e880dfe0c1f3bd0cc2e2308e66` |
| repository PYC | `d24205b3bd137720e2b0d5a95ea1600c9dd8d7eb7bbae45b0b8c1e9c389f6cb7` | `d24205b3bd137720e2b0d5a95ea1600c9dd8d7eb7bbae45b0b8c1e9c389f6cb7` |
| selected-site PYC | `f7c17e604677fd58c61732eec8f8a80ba8547b5c14ee7802bb28845dda30a2c0` | `f7c17e604677fd58c61732eec8f8a80ba8547b5c14ee7802bb28845dda30a2c0` |

Thus no descendant was added, deleted, mutated, relinked, retyped or
metadata-drifted. No cleanup or repair was performed.

All Python-facing commands used `PYTHONDONTWRITEBYTECODE=1`, isolated
`UV_CACHE_DIR=/tmp/w04-vertical-slice-review-uv-cache`, locked/no-sync uv, and
pytest used `-p no:cacheprovider`. Ruff and mypy caches were redirected to
`/tmp`.

- Ruff format: PASS, 13 files already formatted.
- Ruff lint: PASS.
- Mypy: PASS, no issues in 11 source files.
- Pytest: PASS, `734 passed in 1509.58s (0:25:09)`.
- Bandit: PASS, no findings.
- Import-linter: PASS, 39 files, 74 dependencies, `3 kept / 0 broken`.
- Local-only verifier: PASS, zero failures, main branch and zero remotes.

No Git operation, network/provider access, credential use, dependency or lock
change, real-root publication, cleanup, deployment, container/cloud action, or
write outside the two reviewer-owned artifacts occurred.

Verdict: **PASS — P0 0 / P1 0 / P2 0**.
