# W05 M0 independent model review R2

## Verdict

**PASS.** No W05 P0 or P1 reproduced. R6 closes each of the four R1 P1 classes, the re-signed descriptor attacks also fail closed, and the frozen six-family identities, payloads, complete 18-query rankings, scores, and selected four-file bytes remain exact. The unchanged list-collection and redundant query/exclusion-overlap representations remain the packet-declared nonblocking P2 boundary.

## Independent attack results

### 1. Typed authority substitution — closed

Fresh direct-dataclass attacks were exercised independently, not only through the producer tests.

- configuration `role_aware_minimum_overlap=0.0`: rejected at fit, load, and development-check boundaries;
- configuration `selected_model_family=pca`: rejected at fit, load, and development-check boundaries;
- registry first feature renamed while retaining accepted carried IDs/digests: rejected at fit, load, and development-check boundaries;
- candidate contextual role probabilities changed while retaining accepted fixture identity: rejected at fit, load, and development-check boundaries;
- candidate dependency `observed_at` changed to a different pre-cutoff value while retaining accepted fixture identity: rejected at fit, load, and development-check boundaries;
- truncated query projection retaining accepted fixture identity: rejected at load and development-check boundaries.

The public boundaries reconstruct and pin the complete configuration mapping, semantic registry projection, candidate projection, query projection, taxonomy contract, and taxonomy wrapper claims before artifact I/O. The fit boundary wrapped these failures as `M0TrainingError`; runtime/check boundaries rejected them as `M0RuntimeError`/`M0TrainingError` as appropriate.

### 2. Exactly tied PCA basis — closed

A genuine orthonormal 45-degree rotation of the first two axes, plus a sign/permutation variant, canonicalized byte-exactly to the axis-basis result. Both canonical components and a transformed identity index were equal. The implementation derives a canonical basis from the rounded invariant projector and leaves the frozen non-tied PCA payload unchanged.

### 3. Manifest physical substitution — closed

Both independently rewritten pretty/noncanonical manifest bytes and a duplicate `schema_version` key failed before contract acceptance. The exact selected canonical manifest continued to load. Re-signed first descriptors claiming `endianness=big` or `memory_order=fortran`, with recomputed descriptor-bundle and manifest digests, were also rejected.

### 4. Fitting root/ancestor symlinks — closed

An artifact-root symlink and a symlinked ancestor of a new artifact directory were both rejected before write. Both real targets remained empty. Ordinary bounded roots reproduced successfully.

## Frozen reproduction

Two fresh roots, `/private/tmp/w05-r2-a-jojasqce` and `/private/tmp/w05-r2-b-k7cjlv3z`, were built independently. For every family all four files were byte-identical across roots, and complete reloaded results for all 18 indexed queries at `limit=17`—player order, distances, and every contribution—were exactly equal. The following R1-frozen identities and scores remain unchanged:

| family | artifact UUID | manifest digest | array payload digest | precision@3 | R2 complete-result projection |
|---|---|---|---|---:|---|
| metadata_control | `5c3a6171-a333-5bd9-b500-82a0b24106f1` | `be1e17efdf4d614dc25bca9085b75d59144f8e18b34f313b94418b0e31ad5f6a` | `19a29423c6ee03b0439e94950d344f854e0b54633682354d1433ee328790a5ee` | `0.1111111111111111` | `dcdfc5de66138a666d801fdc2f678681f9420676dd222ba7a52b01413927674a` |
| raw_euclidean_control | `09d3296a-0d5a-5892-bfdd-5820073fe792` | `b277d26404a7010b0c0bb7440daef20242e9575df64efaed0ffc317f21db2f68` | `3915f96a1c494de7745e2a336576ce806e02b101ea9522e03a1ef1a154065d36` | `0.3333333333333333` | `4a1f17831b06188129b28436ee745005b361b2e910c96910eb753b679c7d2bcf` |
| robust_scaled_cosine | `e4ab4661-faf4-5065-b43d-0d8fe8ba3c7d` | `069beffefba0ead2fd8c55515f75fe98a65c1085ba64f32367ee09faa56830e2` | `ece7da1a9458a495ef3dbe7faaae2a5bd5684ae3eb617f85fe32edcf61da4bbc` | `1.0` | `924e7f0db93186aa8bfd18d290ea836d4dd788b8e5dee783d9fbb05c1b11d602` |
| weighted_cosine | `33c7fd4b-21f6-52d7-be69-95277c0691b3` | `968f7f3b2d5b77578320851dccb00c7287e10bfcb39220ca8b9f9a022cbd12b8` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` | `39e7b018f73bb651a7e9fd431b244efb2fb68f9b04fd6c33fe7ba33e197ff311` |
| pca | `c648fc03-4eec-510c-bf41-0b50515c1f47` | `d3970a614859ae98e285e47c1b2473c60a1f8743f563e68c85e4f6aa53cab035` | `90e90a145282cd9f6b6374fd3df1b8db2d24616d3d54395484fd20d4e1538971` | `1.0` | `6b6151e284ab94a4f88efcc4b9f2742edc4c006cd5fdc871b054d3f4367be690` |
| role_aware_restriction | `9a0d43c6-d177-51be-8280-3bf02bedbc99` | `2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9` | `c2bd7a9939e45e0217e891a9a80b2dcabd120106ad9d67e0d5fd831caaba4801` | `1.0` | `df822cf1f932175c6b5c19720d56c67a6f2a97e08fd802fb144cc5cb3ffbf69c` |

The R2 complete-result projection is SHA-256 over canonical JSON containing every returned player ID, distance, and contribution for every query. It is a newly named R2 projection and is used only to prove exact equality between the two fresh roots; the R1 report used a differently shaped digest projection. The before/after identity comparison is instead anchored by the unchanged artifact UUIDs, logical manifests, array payloads, all 18 ranking digests per family, and scores. Metadata, raw-Euclidean, and the shared similarity ranking lists each matched all 18 R1 values exactly.

The selected fresh file SHA-256 values exactly match the checked-in selected artifact:

- arrays: `73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`;
- manifest: `c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`;
- configuration: `d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`;
- candidate universe: `2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`.

## Producer evidence and scope

The expanded producer suite directly covers typed-authority substitutions, duplicate manifest keys, ancestor symlinks, re-signed descriptor layout claims, and genuine tied-basis invariance. It uses the runtime scorer for ranking/score checks; no duplicate scoring implementation, authority/config tuning, selection retry, or W06 behavior was introduced. The review found no source, fixture, config, artifact, orchestration, dependency, or accepted-predecessor drift within the bounded R6 correction.

## Commands and statuses

- `UV_CACHE_DIR=/private/tmp/w05-review-r2-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_m0_models.py tests/unit/test_w05_features.py tests/unit/test_w05_roles.py tests/contracts/test_w05_m0_contracts.py` — exit 0, `69 passed in 0.98s`.
- `... uv run --no-sync ruff format --check src/scouting/m0 src/scouting/modeling tests/unit/test_w05_m0_models.py` — exit 0, five files already formatted.
- `... uv run --no-sync ruff check ...` — exit 0.
- `... uv run --no-sync mypy src/scouting/m0 src/scouting/modeling` — exit 0, no issues in four files.
- `... uv run --no-sync lint-imports` — exit 0, three contracts kept.
- `... uv run --no-sync python scripts/verify_local_only.py` — exit 0, status PASS with no failures.
- `... uv run --no-sync python /private/tmp/w05_r2_probe.py` — exit 0; all bounded attacks rejected and all-six/two-root reproduction exact.

## Residual boundary

List collection acceptance and redundant query/exclusion overlap remain P2 as explicitly classified by the R2 packet. Neither produced a new direct ranking, result, authority, leakage, or claim-boundary blocker effect. No follow-up is required for the R2 PASS.
