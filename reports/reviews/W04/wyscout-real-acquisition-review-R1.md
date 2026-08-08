# W04 Wyscout real acquisition review — R1

## Review decision

**Recommendation to master: ACCEPT.**

This is an independent-verifier recommendation, not task or phase approval. The master
retains gate authority.

The ignored local acquisition snapshot was present, so the tracked verifier executed
fully rather than skipping. Every completion/config object, admitted member, raw ZIP
directory, scope exclusion, guarded sidecar, temporal/right claim, signed-delivery
leakage boundary, and exact replay condition reconciled. No P0-P2 defect or packet stop
condition was reproduced.

## Scope and method

The review treated `data/source/wyscout/v5/**` and
`data/working/wyscout/v5/**` as read-only. It opened persisted payloads only for
streaming reads and opened only the ten admitted ZIP entries, never the four excluded
entry payloads.

Before verification, the test captured type, mode, size, and nanosecond modification
time for every snapshot and working-root entry. Replay ran with:

- an opener that raises on any call;
- a socket creation denial;
- `GuardedStorage.write_bytes` replaced by a raising sentinel;
- read and ZIP-member-open spies.

The snapshot and working-root inventories were byte-for-byte metadata-identical after
replay. No Git operation, provider/network access, data write, protected fixture,
profile/design work, or external service was used.

## Completion identity

- Manifest path: `data/source/wyscout/v5/completion-manifest.json`
- Recomputed SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
- Supplied candidate SHA-256: exact match
- Canonical JSON: exact
- State: `complete`
- Source ID: `wyscout-soccer-match-events-figshare-v5`
- Provider: `Wyscout`
- Classification: `wyscout_figshare_v5_cc_by_4`
- Objects: `7`
- Admitted archive members: `10`
- Directory-only scope exclusions: `4`

The snapshot has exactly 36 files: 18 durable payload/completion files and their 18
guarded sidecars. It contains no unknown durable file. Every file is mode `0600` and
every directory is mode `0700`.

## Object reconciliation

All object records match the strict loaded configuration for article DOI/ID, file ID,
name, stable source URL, exact object path, byte count, reviewed MD5, computed MD5, and
recomputed SHA-256.

| Object | Bytes | MD5 | SHA-256 |
| --- | ---: | --- | --- |
| `competitions.json` | 1,209 | `3dc210a4805dda5337b0ff9f7eaa407a` | `39a738d2bc97638502e1ead01d661b54c623d6d6b37f77de3846f9a94db7a3a1` |
| `teams.json` | 27,404 | `1381ff9449f21105090729cf0e086b5b` | `9f7a4a3b3d92c0be33f40613ad6e6eb4316c3b9771ec74c61a22c9b8ece23a4d` |
| `players.json` | 1,737,347 | `f28ddf6326281efeda6488b2169f5609` | `877a111cb1005b73df5645e9338bd74fb4b496bace2fbc545a72abb3b73efa2e` |
| `matches.zip` | 645,097 | `51d80beb17480919f69a53a0152c2d71` | `c8f92bb7533e5c127e043cee764c991b5c25b4f5e70a65be931baae0b1765ce9` |
| `events.zip` | 77,323,413 | `7c20e8647e7eda58d7838a0c7b1ec6ab` | `877e015b716ffdeea18f04418e3f24fed307ed03c37ff305cabe1f47c4822a45` |
| `eventid2name.csv` | 1,001 | `46daf16100ece0c743eedc9adcfea162` | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` |
| `tags2name.csv` | 1,754 | `e7acb14918d00e40c80a898b1da8fc39` | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` |

Total reviewed compressed object bytes: `79,737,225`.

## Archive and admitted-member reconciliation

Each raw ZIP directory has exactly seven unique, safe, regular, unencrypted entries:
the five configured domestic-league members and two configured scope exclusions. No
unknown, duplicate, absolute, traversing, linked, special, encrypted, oversized, or
over-ratio entry was observed.

Every admitted entry was streamed independently from its raw ZIP and reconciled with
its separately persisted durable member and completion record:

| Archive/member | Bytes | SHA-256 |
| --- | ---: | --- |
| `matches.zip` / `matches_England.json` | 1,694,720 | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` |
| `matches.zip` / `matches_France.json` | 1,707,222 | `851fad20616a99383ec8a6ef2136c141700cd44af235a3da6c10008dbac37cea` |
| `matches.zip` / `matches_Germany.json` | 1,377,328 | `6f962a20f50b174939c7b24d51169aaee10ae896b05dca89fc33aa81b585c0a9` |
| `matches.zip` / `matches_Italy.json` | 2,019,196 | `afb21c3fa8bd4b1d30af158fa3edfae1e61127825b481e49b32bd7d1d3b99725` |
| `matches.zip` / `matches_Spain.json` | 1,705,380 | `9787475e64c496d44dc394f98def2610cc31809637fc10c13ec151b37b6118ce` |
| `events.zip` / `events_England.json` | 188,888,614 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` |
| `events.zip` / `events_France.json` | 186,374,196 | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` |
| `events.zip` / `events_Germany.json` | 152,916,631 | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` |
| `events.zip` / `events_Italy.json` | 190,544,685 | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` |
| `events.zip` / `events_Spain.json` | 184,164,406 | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` |

Total admitted member bytes: `911,392,378`.

The four excluded entries were not opened. Their compressed size, declared size, CRC32,
archive/name identity, and directory-only disposition match completion evidence:

| Archive/member | Compressed | Declared | CRC32 |
| --- | ---: | ---: | --- |
| `matches.zip` / `matches_European_Championship.json` | 19,805 | 312,151 | `9e64a3d4` |
| `matches.zip` / `matches_World_Cup.json` | 25,498 | 395,677 | `649719a9` |
| `events.zip` / `events_European_Championship.json` | 1,869,471 | 22,954,338 | `13c071be` |
| `events.zip` / `events_World_Cup.json` | 2,440,430 | 29,981,214 | `053e0ae8` |

No excluded member payload or sidecar exists under `archive-members/`.

## Guarded sidecars

All 18 sidecars are canonical, complete schema-v1 documents whose payload path,
byte count, and SHA-256 match their durable target.

- Object sidecars have exact media type, stable Figshare source URL, collection DOI,
  source ID, local-retention allowance, and raw-export prohibition.
- Admitted-member sidecars have exact archive name, parent archive SHA-256, collection
  DOI, source ID, JSON media type, local-retention allowance, and raw-export
  prohibition.
- The completion sidecar binds the supplied completion digest and exact size to the
  collection/source lineage with immutable retention and raw-export prohibition.

## Temporal, rights, and signed-delivery evidence

- Frozen source availability and collection publication:
  `2020-01-28T14:24:27Z`
- Actual acquisition: `2026-07-29T15:51:08.598589Z`
- Availability basis: `frozen_collection_release_time`
- Licence: exact `CC-BY-4.0` name, URL, attribution text, and change notice from the
  reviewed configuration

The verifier found no `X-Amz-`, `AWS4-HMAC-SHA256`, or `X-Amz-Signature` token in the
completion document, any sidecar, any persisted object byte stream, or any admitted
member byte stream. Object URLs are exact stable Figshare URLs with no query. Excluded
member payloads were deliberately not opened.

## Exact replay

Replay read exactly, in order:

1. the completion manifest;
2. all seven configured durable objects;
3. all ten configured durable admitted members.

Both archives were re-admitted, and the ZIP-open spy observed exactly the ten admitted
member names and none of the four excluded names. The opener call list stayed empty,
the write sentinel was not reached, `manifest_created` was `false`, and replay returned
the identical manifest bytes and SHA-256.

## Verification

- `uv run pytest -q tests/security/test_w04_real_acquisition_review.py`
  - exit status: `0`
  - result: `1 passed in 6.33s`; the snapshot was present and the test did not skip
- `uv run ruff format --check tests/security/test_w04_real_acquisition_review.py`
  - exit status: `0`
  - result: `1 file already formatted`
- `uv run ruff check tests/security/test_w04_real_acquisition_review.py`
  - exit status: `0`
  - result: `All checks passed!`
- `uv run mypy tests/security/test_w04_real_acquisition_review.py`
  - exit status: `0`
  - result: `Success: no issues found in 1 source file`
- `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: status `PASS`; failures `[]`

## Residual risk

- The verifier intentionally performed no provider request, so current provider
  availability is not assessed.
- The review establishes acquisition identity, integrity, archive scope, rights and
  temporal evidence, and replay behavior; it does not assert the semantic correctness
  of individual football-event records.
- On a checkout without the intentionally ignored snapshot root, the tracked test
  skips with an explicit absence reason. It fails—not skips—if the root exists but its
  contents are incomplete or conflicting.
- The master retains task acceptance, integration, phase-gate, and checkpoint
  authority.

## Recommendation

**ACCEPT.** The complete durable snapshot matches the reviewed configuration and
canonical completion evidence, all guarded sidecars and exclusions reconcile, replay
is exact and network/write-free, and no P0-P2 defect was reproduced. This remains an
independent recommendation, not self-approval.
