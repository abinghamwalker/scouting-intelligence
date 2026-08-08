# W04 identity-bundle runtime independent review R1

Date: 2026-07-31

Disposition: **REWORK — REVIEW CHAIN INVALIDATED**

This fresh review examined the fixed candidate named by
`W04-IDENTITY-BUNDLE-RUNTIME-REVIEW-01-R1`. The candidate itself did not drift,
and every completed semantic, source-recomputation, recursive-readback, namespace,
inventory-adjudication and focused acceptance probe passed. The review cannot issue
`PASS`, however, because the complete repository bytecode inventory changed between
the required preflight and postflight observations. R20 Section 8.6.5 explicitly
states that any such creation or mutation invalidates the entire independent review,
must be preserved, and cannot be cleaned or repaired into success.

## Finding counts

| Severity | Count |
| --- | ---: |
| P0 | 0 |
| P1 | 1 |
| P2 | 0 |

### P1 — `REVIEW_REPOSITORY_PYC_INVENTORY_DRIFT`

The complete repository pyc inventory retained count `76`, but both its byte digest
and its path/size/mode/link digest changed during the bounded review:

| Observation | Preflight | Postflight |
| --- | --- | --- |
| repository pyc count | `76` | `76` |
| sorted path plus file SHA-256 digest | `14cbf20f9523f00baa52520fa5fb19bf1512a3f9a22d16c24781ecf4c7d886b8` | `414cae97f7353a69b8e105efe2f9e6bb6e2205d6b0f4766396b1baf956eaa1bd` |
| sorted path/size/mode/link digest | `1f37e9d29e31ecedb2e71ac310e275228ea92dcb6b22eb8e4f72c1e36ffd3754` | `5c0507083d323465ddf74b153313b7a892bb31437d6f99226f656b860c37a754` |

The recent postflight files were:

- `src/scouting/storage/__pycache__/formats.cpython-312.pyc`, SHA-256
  `79cbec277422d1ed1d67050a7066a546d9d3797cda8dd157b1f4f484f826e059`;
- `tests/unit/__pycache__/test_w04_wyscout_product_formats.cpython-312-pytest-9.1.1.pyc`,
  SHA-256
  `2ac3afc005b582741dfeff5ca2c8b08519e2170ddfdf368f614ae75ce858da4b`.

Both are outside this identity candidate. The evidence is consistent with concurrent
repository activity, but this review does not attribute causation. R20 makes the
inventory equality predicate unconditional, so concurrent unrelated mutation is
still review-invalidating.

The site inventory remained byte-identical: count `1,086`, file digest
`a58b6915d692b5871b2d4aa807ee88523277b46b7e5fd1b99e80a63c6d3c0f46`,
and metadata digest
`e941b23be1702227c5ebb3d7195a691dceb27dcca5bc6594115f12a5d8d6a765`.
The preflight classifier found zero unsafe or unclassified files and reproduced:

- site: `972` distribution-normal, `112` pytest-rewrite, one uv-bootstrap-normal,
  and one exact optional inert orphan;
- repository: `41` mapped normal, `32` mapped pytest-rewrite, and the three exact
  optional inert orphans.

The repository count is permitted to differ from R20's dated 58-file evidence
snapshot because all additional files classified against present admitted sources.
The defect is only the within-review mutation.

## Frozen candidate verification

Every fixed binding was verified before merits work:

- contracts:
  `8040279c825fc246900a07b257bab71b9ead3ff9850c4e7994501bd9d13d272f`;
- runtime:
  `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd`;
- contract tests:
  `13ce12bb54ccd0880ab0865e3b33982bba1b0cfeb4fc59f070bde710e5dbc030`;
- runtime tests:
  `47e4f4aa0868e987fdc5961e6960b85456edcfa1a394b634664dff587225ae60`;
- producer return:
  `813b83bc5641f7a6322a529d3e513e284eca02302e3bfec5f6b2b20bac4e70b5`;
- additive namespace binding:
  `d28e808a91864156b479aa02647859aea8e08ad55b36e9b726192cd9413c84dd`.

The two artifacts remained unchanged after all probes:

- queue: SHA-256
  `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`,
  `17,412` bytes, regular file, mode `0600`;
- bundle: SHA-256
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`,
  `91,420,676` bytes, regular file, mode `0600`;
- derived identity dependency UUID:
  `31638732-5b25-57db-9eb4-8e943a47a387`.

The identity inventory contains exactly those two content-addressed files and the
two required parent directories, with no symlink, sidecar, correction, alias,
partial, stale or extra entry.

## Source recomputation and recursive readback

A locked/no-sync, bytecode-disabled invocation independently called
`build_initial_identity_bundle(...)` and then
`load_initial_identity_bundle(...)` with the exact absolute source, manifest,
identity root and computed bundle address. It exited `0` and asserted complete
object equality after source recomputation plus recursive queue/bundle readback.
It reproduced:

- `5,594` current rows;
- states `7 COMPETITION/RESOLVED`, `142 TEAM/RESOLVED`,
  `3,603 PLAYER/RESOLVED`, `15 PLAYER/REVIEW_REQUIRED`,
  `1 PLAYER/REJECTED`, and `1,826 MATCH/RESOLVED`;
- `23` source occurrences aggregated into `15` open queue items;
- `226,041` unique player-zero source-row references;
- the exact queue and bundle addresses, sizes and derived dependency UUID above.

All five target rows reproduced their exact physical ordinals, canonical raw-row
digests and canonical UUIDs:

| Source identity | Path and ordinal | Raw-row SHA-256 | Canonical UUID |
| --- | --- | --- | --- |
| `competition:364` | `objects/competitions.json#1` | `6a5916b3e5cf86d73a6409f159804eaa62dcef27614129a2e15a52b67207b36a` | `cb5c5317-fa4a-571e-93dc-ef6ce482eab7` |
| `team:1609` | `objects/teams.json#84` | `82dbdc6c1ec0ae9da8d63078b3815cb7e2ef84fc29bacac18c85e65b011d9d96` | `b5f2dd3c-0166-5384-99fa-0ed47cc7e44c` |
| `team:1631` | `objects/teams.json#54` | `be9e47831f6d86450cd3fa9fb7471e26da691fa793bdc0d06ffb929a757b8a10` | `5b353635-819b-5bd1-8ca2-5a7364042a96` |
| `player:285508` | `objects/players.json#757` | `c6f2f4c5b74563a12cdb78fa49ae295622f5f730ff980fdb220448a4b404e1ac` | `be8da881-2b15-513f-978f-6bb3865bc8e2` |
| `match:2499719` | `archive-members/matches_England.json#379` | `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86` | `bad97950-6fac-5cf0-a93c-094f91abbb9b` |

The exact match row independently reconciled competition `364`, season `181150`,
start `2017-08-11 18:45:00`, and teams `{1609,1631}`. Player `285508` is team
`1631` bench index `4` and substitution index `1`, entering for player `192748` at
nominal minute `82`. No lineup or product bytes were created.

## Namespace and preimage review

The implementation and passing adversarial suite bind:

- review-queue namespace `UUIDv5(NAMESPACE_URL,
  "urn:scouting-intelligence:w04:wyscout:identity-review-queue:v1")`;
- the exact sorted-key compact five-field UTF-8 queue preimage without a newline;
- crosswalk namespace `fd7bb3ae-10f7-5856-99fb-3854d794273d` from the additive
  authority;
- the exact colon-separated tenant/kind/source-identity/version/evidence preimage;
- fixed row vector `45b2a06d-e200-5cb3-9c9d-8f429291ed31` and trace vector
  `121e5662-35f6-5f12-8b3b-c458b30cc38a` for `player:379199`.

Alternate namespace, case, newline, reason token and changed semantic/reference
preimages fail. Strict integer helpers reject Boolean, float, `Decimal`, string and
null coercion.

## Persistence, exact-address and inventory adjudication

The `79`-test identity/authority suite passed and exercised truncation/malformed or
trailing JSON, duplicate keys, non-object rows, strict-number coercion, queue and
bundle omission/duplication/reordering/staleness, wrong clocks/authority, partial
inventory, sidecar, symlink, unsafe mode, wrong root, immutable unequal content and
digest-only caller evidence.

Code inspection finds that directory enumeration is reject-only enforcement, not
authority selection:

1. `build_initial_identity_bundle` begins from fixed source, manifest and authority
   paths and derives the one exact queue and bundle address before identity
   inventory inspection.
2. `load_initial_identity_bundle` recomputes that complete build, compares the
   caller-supplied bundle digest to the source-derived address, and only then asks
   `_check_inventory` to require exact set equality.
3. `_check_inventory` never returns an address or chooses newest/first/last. It
   accepts only the already-derived filenames and rejects every other entry.
4. `_verify_reopened` opens only those already-derived exact relative paths and
   recursively proves queue equality with the bundle review-required population.

Therefore the inventory implementation does not violate R20's prohibition on
selection scans. No implementation P0-P2 finding was established before the
review-chain invalidation.

## Commands and results

- fixed SHA-256, size, mode and type checks: exit `0`, exact;
- complete read-only preflight inventory and classification: exit `0`, zero
  unclassified/unsafe files;
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_wyscout_identity_bundle.py
  tests/unit/test_wyscout_identity.py
  tests/contracts/test_w04_identity_ruleset_authority.py`: exit `0`,
  `79 passed in 24.62s`;
- `uv run python scripts/verify_local_only.py`: exit `0`, `PASS`, 25/25 controls;
- locked/no-sync, `python -B` exact source recomputation plus exact-address loader:
  exit `0`, all assertions passed;
- postflight inventory comparison: command exit `0`, predicate **FAIL** due the
  repository digest changes recorded above;
- final candidate and artifact hash/mode recheck: exit `0`, unchanged.

No Git command, provider/network access, build-ID calculation, Bronze/Silver/Gold,
receipt, code-manifest, cloud, container, CI, remote, endpoint or deployment action
was performed.

## Smallest bounded rework

Do not change the frozen identity candidate or its artifacts. After all other
repository-writing agents are idle, dispatch a fresh reviewer against the same
fixed bindings. That review must:

1. take a new complete classified site/repository pyc preflight;
2. run every Python review helper with pre-start
   `PYTHONDONTWRITEBYTECODE=1` and `python -B` (including the local-only verifier,
   preferably as `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
   scripts/verify_local_only.py`);
3. prevent concurrent repository writers for the bounded review window;
4. reproduce the source/readback and packet checks; and
5. require byte-identical full postflight inventories before a merits verdict.

No cleanup, cache deletion, repair, candidate edit, authority edit, product work or
architecture revision is required or permitted by this rework.
