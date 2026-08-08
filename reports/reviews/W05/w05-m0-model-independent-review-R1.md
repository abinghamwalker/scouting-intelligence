# W05 M0 model independent review R1

## Verdict

**REWORK.** No P0 was reproduced. Four bounded P1 defect classes reproduce under the six controlling W05 blocker tests. The frozen fixtures, six numeric payloads and six development scores reproduce, but the current R5 implementation does not fail closed at every typed authority boundary, does not canonicalize an exactly degenerate PCA subspace, admits noncanonical/duplicate-key manifest bytes, and writes through an ancestor-symlinked fitting path.

The controlling tests are: (1) changes admitted features, fitted artifacts, rankings, or result bytes; (2) causes temporal leakage or lineage substitution; (3) breaks training-serving or batch-request parity; (4) produces a false explanation, confidence statement, or claim boundary; (5) admits unauthorised code/data or violates local-only controls; (6) demonstrates a reproducible P0/P1 correctness or security defect.

## P0/P1/P2 findings

### P1-1 — Public typed objects are trusted by class identity rather than fully revalidated

**Blocker tests:** 1, 2, 3, 4, 6.

Direct `dataclasses.replace` construction retained accepted IDs/digests while changing nested behavior-bearing values:

- `M0Configuration(role_aware_minimum_overlap=0.0)` built and loaded a self-consistent role-aware artifact. The runtime exposed threshold `0.0` and returned cross-archetype candidates that the frozen `0.75` authority excludes.
- `selected_model_family=pca` under the accepted configuration digest built and loaded a raw-Euclidean artifact and exposed the substituted selected-family claim.
- A directly constructed `FeatureRegistry` admitted schema hash `00…00`; a separate attack admitted metadata feature name `substituted_position_code` in the manifest.
- A directly constructed `M0DevelopmentCandidates` admitted changed contextual probabilities `0.1918181818181818` / `0.1718181818181818` in a metadata artifact while retaining the accepted fixture identity.
- A directly constructed candidate authority admitted dependency `observed_at=2024-01-01T00:00:00Z` and recomputed lineage `392aa4a018fea3fa364639ff81a83a33e17fcd5c4f502a22898c4fc6d69f0e28`; artifact UUID `38c1635b-17a5-5885-bbb4-c2538da8b942` loaded successfully.

Direct query relevance/order mutation and a nested taxonomy-contract mutation did fail closed. That does not close the admitted configuration, registry, candidate probability, or lineage paths.

Smallest bounded correction: add normal public revalidation functions for every typed authority and call them at every fit/load/check boundary. Revalidate every frozen configuration field and canonical digest; the exact accepted registry/schema roster and hashes; and the full accepted six-feature candidate projection for every family, including metadata. Do not let family-specific metadata projection bypass the accepted full candidate authority. Keep the existing query/taxonomy rejection behavior.

### P1-2 — PCA canonicalization is not invariant to valid tied-subspace basis ambiguity

**Blocker tests:** 1, 3, 4, 6.

The sign/permutation rule operates component-by-component. With three exactly equal variances, two valid orthonormal bases of the same subspace (one axis basis, one 45-degree rotation of the first two axes) canonicalized to different component and transformed-index arrays. `rotated_valid_basis_invariant=false`. This can change payload bytes, distances and original-feature contribution evidence when a valid SVD implementation returns a different basis within a degenerate eigenspace.

The actual frozen PCA artifact otherwise passed: indexed and sorted-exemplar-mean results each returned six contributions and `distance == 1 + fsum(contributions)` with maximum error `0.0`.

Smallest bounded correction: canonicalize each exactly tied explained-variance subspace from its invariant projector using deterministic original-feature-axis Gram-Schmidt (then apply the existing pivot sign/order rule), and apply the same transform to components and index vectors. Add a direct rotated-basis equality test.

### P1-3 — Manifest JSON is not an exact canonical/duplicate-key boundary

**Blocker tests:** 1, 3, 6.

Replacing `manifest.json` with pretty-printed/reordered JSON loaded successfully. Prefixing a second `schema_version` key also loaded successfully. Configuration and universe use `_read_canonical_json`, but the manifest goes directly through `M0ArtifactManifest.model_validate_json`, so physical artifact bytes are substitutable without changing the self digest.

All mandatory NPZ mutations were rejected: member name/order/path, duplicate member, comment, compression, timestamp, external attributes, object dtype, float32 dtype, shape, Fortran order, raw value bytes, re-signed descriptor digest, and truncated ZIP integrity.

Smallest bounded correction: parse `manifest.json` with the duplicate-key rejecting exact-canonical JSON reader, compare canonical bytes, then perform contract validation.

### P1-4 — Fitting writes through an ancestor symlink

**Blocker tests:** 5, 6.

Fitting to `/private/tmp/.../parent-link/artifact`, where `parent-link` was a symlink to another directory, succeeded and produced artifact `09d3296a-0d5a-5892-bfdd-5820073fe792`. A root symlink was rejected, and loading through root/ancestor symlinks was rejected. The fitting boundary checks only the destination itself after `mkdir`, not the resolved ancestor chain.

Smallest bounded correction: before creating or opening files, require the absolute destination and every existing ancestor to equal their resolved paths and reject every symlink component. Retain exclusive immutable writes.

### P2 — Strict query collection representation is incomplete

Lists were admitted for exemplar and exclusion collections, and a query ID duplicated in exclusions was admitted. Duplicate exemplars, unknown query/exemplar IDs, and exclusion/exemplar overlap were rejected. These admitted representations did not independently change scoring semantics in the probe, so they are P2 hardening rather than a controlling blocker. Enforce actual tuple types and all declared overlaps in the bounded correction because the packet requires it.

### P2 — Producer test evidence is materially incomplete

`tests/unit/test_w05_m0_models.py` contains five tests. It does not directly execute most mandatory archive mutations, direct-authority attacks, tied-basis ambiguity, ancestor-symlink fitting, or exact ranking lists. Independent probes found the P1s above. This is an evidence-completeness gap, not a separate W10 concern.

## Fresh deterministic reproduction

Two fresh roots were built at `/private/tmp/w05-review-a-z3r19acd` and `/private/tmp/w05-review-b-o5a9vbto`. For every family, all four file bytes were identical, and complete reloaded scores/distances/contributions were exactly equal.

| family | artifact UUID | manifest digest | array payload digest | precision@3 | complete result digest |
|---|---|---|---|---:|---|
| metadata_control | `5c3a6171-a333-5bd9-b500-82a0b24106f1` | `be1e17efdf4d614dc25bca9085b75d59144f8e18b34f313b94418b0e31ad5f6a` | `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee` | `0.1111111111111111` | `b6d5db1fb81fbc76ec70d47b1f2eb6a6d7347db87f8311f5f49b09c21df33944` |
| raw_euclidean_control | `09d3296a-0d5a-5892-bfdd-5820073fe792` | `b277d26404a7010b0c0bb7440daef20242e9575df64efaed0ffc317f21db2f68` | `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36` | `0.3333333333333333` | `f41c2e76416f4f5fbc608eda6295478814f7da635edb4ab0f92674efb75071a0` |
| robust_scaled_cosine | `e4ab4661-faf4-5065-b43d-0d8fe8ba3c7d` | `069beffefba0ead2fd8c55515f75fe98a65c1085ba64f32367ee09faa56830e2` | `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc` | `1.0` | `9ad261e05cea55ec1c4029ea3568529c1ec1ab4ab7d38ef5de60e1e75f3916d7` |
| weighted_cosine | `33c7fd4b-21f6-52d7-be69-95277c0691b3` | `968f7f3b2d5b77578320851dccb00c7287e10bfcb39220ca8b9f9a022cbd12b8` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` | `bac1349c90342394f1968a3c6813e67ece37c827b44629cc060a0609b542cded` |
| pca | `c648fc03-4eec-510c-bf41-0b50515c1f47` | `d3970a614859ae98e285e47c1b2473c60a1f8743f563e68c85e4f6aa53cab035` | `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971` | `1.0` | `8063300bab8503a4182ae1a95b7a762dfdb386ef71414da533d0a41debc15592` |
| role_aware_restriction | `9a0d43c6-d177-51be-8280-3bf02bedbc99` | `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` | `17ec4065897b6eade2472c8d81c464d1f0e16dce292b10865775e114ffd6ef26` |

The selected fresh role-aware files exactly matched the checked-in selected files: arrays `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`, manifest `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`, configuration `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`, universe `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

Ranking digests for robust cosine, weighted cosine, PCA and role-aware were identical:

`a0ed83ee80b9447534ceb033f27459cd1c403eeae21c56fadd716accde1eadf5`, `ab313239e97b484f85bc13a0566532ba46b5a3c88a697431f51223224465714c`, `bd45d530b14272c350db04c554399fbfe32be52a9dee1bd4752aabf4988bbd63`, `bf35fd0adbe6468bf5063242c9a58ad7d86fa5f2b0573bd6e00af6ee5f6a1924`, `f993359a83bb7cd584e5125a418f8f7b26aaf82eef3ee71cd4ccd0b46b624576`, `15635fd6a44d6a03520498287721004c284302ea4da1c3ce9b3285543509fb8c`, `c1f12a735a710073951b61e2c84b0d7fa7b942e056b5cd3b700d0801781967d4`, `e1ded08d97507ffab1674cb384bd1b8e043f0eaf705990a7b3311d504ed4325f`, `80d07c6a1515ffab5c50c3ea93087cd4a3ca00b3658fa3f7299e0c74e7da1a18`, `3d325c633ebb2ce229112b2c9f0318ce4196637a65ff584dbbe9d86f709805d8`, `dae4ea7bff9956bb355ebb9f25a5d823a9a99f4a901f3b5c5fe9bdcb1ad5f1de`, `7b48087c009ba041ff12ea301257e4747b8250fb7f611262613b2f8be3a11c17`, `089dfd92bb48eb60f89b02ee4a19b83ab53919731545329a9d8cb5d69e02597f`, `2261c6571a139a751f94ad3a525147552ac8daf03eda9b85d067d1779617f657`, `721db055470ea8eb611f0a5919661b38174624a730ce14a91b85985ba8e6ec97`, `f50cecad7f207508a173890b036b151e163040f420a53bf48fd36d562eb7c23d`, `27c90a8c002daa243965ae048c9901e84641cc9243148e510fb4e132fa90868c`, `f0d4b01931be2b26b76638308409e7e31755aa21f5bf15e959e9566d8d488e70`.

Metadata ranking digests:

`3724f895afdeaf000d7e53b22f1b5e6c2429dace7db3067e48ddce6423943226`, `697d4fde20af41aa58cfbaba83a9528649e3254654776f64bb1aef7873fccb5e`, `897ffc66f8850ff694682495440690de90f261b48736e8dacd80d9feaccaccfb`, `81c76ac02e2f0234d7080ec91fc76638981e0238ddd197eca296d24bbba583c2`, `040ea427b0b6f4b6b8171ff1af3b2b08373a24129cc45afc63a055c6a06f8f8d`, `ba7faa4ccff945efd5b796b6359afa6dd4a7daf42630b0bb3bef5727c9b0a221`, `03056e537864a31fbf21db57ea44f07c126d0c5110aee3457c71887cb7d60c18`, `c9809e2d4d42b44a13fc70970063e0dcecffb2318291abbbc5b6acb807011d72`, `eda80340631d5b59c5cb149a3a8d2856c34c5835130a975af7d8af62d2a18413`, `c96df990779ab05e26e27e5b2fc4ea5e54b0dbb2cbd79df8e6f5de8da40815f8`, `bb435b78f54cc19daf28e2126adffa6f77b16f740f09e4a5ecfd53c5836e0a01`, `286c6e6935cb0b8007fbb8b23dabac5557e4f5f109c9827c8fbf1a0df7157cb7`, `d517dc261456bb564e57cca73c89403dc35ca0c09ac61aa7c7fbcaf982c85621`, `35ddf8f846f0f928de60f0959dfe6238f2fcb9d83e3600431e2a81c76223773e`, `b568712dcbde3c29ade76c72382d7dcb5f7446701827228773a2b65e35a4e89f`, `46d844bd61e72c42d5e3630130012bc9207275319e1a1973bd25157e951d8aa3`, `d7fb3702afa9cf4bf0590f29a92e52904b8d01fa2f6de19b850bfeaf59281e5a`, `f9357a7cfc37d7504fa74bef33e90e6f76d5549b3539e767e25c4f2d46d2e671`.

Raw-Euclidean ranking digests:

`3724f895afdeaf000d7e53b22f1b5e6c2429dace7db3067e48ddce6423943226`, `697d4fde20af41aa58cfbaba83a9528649e3254654776f64bb1aef7873fccb5e`, `897ffc66f8850ff694682495440690de90f261b48736e8dacd80d9feaccaccfb`, `d128cda704ecbf89189a52adb7717398b6555474fc96c5834761c9d6dd9c7051`, `040ea427b0b6f4b6b8171ff1af3b2b08373a24129cc45afc63a055c6a06f8f8d`, `ba7faa4ccff945efd5b796b6359afa6dd4a7daf42630b0bb3bef5727c9b0a221`, `71098451c5c6f025b1d03eaab59d45c9d8ec2f3ab201c32f0d8e31cd520cc391`, `e947ca44ac129bf416aad65761d244830452039c385d04919f44234dc06ffa99`, `d8bc2e2e616810d19c839a2a04fff3aff5704777564efdda8dc201a1c24b99d5`, `4b28d60a3af5ef5004af985c7753d7ca951688a0cdf2975514906ba939fe9b8e`, `216acee63d4aa03a1cb4cd07952dbb4d06568c4f84fba4795c01ebd589a9deb0`, `9a1bb8ae79d21a9d42564acbfaab7470e25ddc5c3b506c729ac1b522634763fc`, `7a372a8b5ddc48c2cd3d03df40883272c4e599e11e5c5e80f4b8c669a728e8f6`, `31dc7eb693b183fb6acb097ec9d892b93d7ba2edad85d10e5ba0250b23a61d95`, `0a8a326d865c4f1b6ff0bcbc47d827c2b3baa62c8200b5cc7e48ab479c4e1c74`, `db26d0c6c3d85315cd80e6aaf1e2b77d387c80f487ce31054be29210685a4423`, `1e9d6e499a95ced25964ba0a61d3b743a0e00b2ea2295d128292dd146ba163cf`, `7bfca8e5b06474270bc5f65891ed6e11651ca675da1307ddca902f9ac07d8e00`.

## Authority and claim identities

- configuration logical digest: `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`; physical SHA-256: `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`.
- candidate fixture logical/physical digests: `710c38554f33f8f650d814df1fee3c8bac7a8a2bc22804f93e3b9a8dfd1e50d9` / `5c6f4c26c2f9c71bacb1b13e80d5872b556001f55462a9cc359bf24be06317fc`.
- query fixture logical/physical digests: `fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900` / `1352ed759db30b4c430644893e558aa089e24153193f934cd124373cb6e29157`.
- full selected candidate projection: `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`; metadata projection: `b5efb54c2c30524ae5483a5082d32c391cff68be398e02a54506772b4b29fe21`; query projection: `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`.

The selected baseline strictly clears both declared controls on this frozen fixture (`1.0 > 0.1111111111111111` and `1.0 > 0.3333333333333333`). This is deliberately constructed synthetic-development readiness only. It is not validation, protected evaluation, W06 evidence, expert evidence, recruitment outcome/effectiveness, robustness, transfer, Wyscout/provider, or production evidence. R1 negative evidence remains metadata/raw `0.8518518518518519`, other four families `0.7777777777777778`, with the 729-vector lattice and eight fixed variants unable to improve that prior construction.

## Commands and statuses

- `uv run pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py` — exit 0, `65 passed in 1.20s`.
- `uv run ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && uv run mypy src/scouting/m0 src/scouting/modeling && uv run lint-imports && uv run python scripts/verify_local_only.py` — exit 2 before execution because the sandbox denied `/Users/adrian/.cache/uv/sdists-v9/.git`.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync ruff check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync mypy src/scouting/m0 src/scouting/modeling && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync lint-imports && UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python scripts/verify_local_only.py` — exit 0; lint, mypy, three import contracts, local-only all pass.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py` — exit 0, five files formatted.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<fresh two-root six-family build/load/check script>'` — first attempt exit 1 because macOS `/var` resolves through `/private/var` and the runtime correctly rejected that path; exact rerun with `tempfile.mkdtemp(..., dir="/private/tmp")` exited 0 and emitted the identities, ranking lists, byte equality and complete-result digests above.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<direct typed configuration/registry/candidate/query/taxonomy attack script>'` — exit 0; admissions and rejections are recorded in P1-1.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<PCA tied-basis, contribution, zero-norm/tie, exemplar/exclusion attack script>'` — exit 0; `rotated_valid_basis_invariant=false`, contribution errors `0.0`, zero-norm distance/tie behavior passed.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<NPZ/manifest/root-and-ancestor-symlink attack script>'` — exit 0; all NPZ attacks rejected, noncanonical/duplicate-key manifests and fitting ancestor symlink admitted.
- `UV_CACHE_DIR=/tmp/w05-model-review-uv-cache uv run --no-sync python -c '<fully re-signed manifest/universe/model/index/schema/taxonomy/population/lineage/descriptor/artifact UUID attack script>'` — exit 0; all those disk substitutions rejected.
- `shasum -a 256 configs/models/w05-m0-baselines-v1.json tests/fixtures/w05/m0-development-candidates-v1.json tests/fixtures/w05/m0-development-queries-v1.json runs/w05/m0-baseline-v1/arrays.npz runs/w05/m0-baseline-v1/manifest.json runs/w05/m0-baseline-v1/configuration.json runs/w05/m0-baseline-v1/candidate-universe.json` — exit 0; physical digests recorded above.

The inline scripts were read-only against repository authorities and wrote only bounded `/private/tmp/w05-*` roots. No repository artifact/source/test/config/orchestration path was changed.

## W10 boundary

No host cache, inode, link-count, timestamp, pyc, performance, or equivalent W10-only observation is used in this verdict. The four P1s above each have a direct path through at least one controlling blocker test.
