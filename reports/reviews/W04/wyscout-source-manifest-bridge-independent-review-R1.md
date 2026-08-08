# W04 Wyscout source-manifest bridge — independent review R1

## Recommendation

- task ID: `W04-SOURCE-MANIFEST-BRIDGE-REVIEW-01-R1`
- reviewed at: `2026-07-31T12:41:08Z`
- recommendation: `PASS`
- findings: `P0=0`, `P1=0`, `P2=0`

I recommend `PASS` for the exact producer bytes bound by the review packet. The
bridge independently reproduces the frozen R20 source evidence and creates or
confirms only the one strict `SourceSnapshotManifest`. I found no correctness,
rights, temporal, path, mutation, idempotency, network, or product-scope defect.

This recommendation is independent review evidence, not self-acceptance. It grants
no identity, Bronze, Silver, Gold, build, model, endpoint, deployment, or other
downstream authority. Master readback and acceptance remain required.

## Scope and immutable bindings

I read the packet, `AGENTS.md`, the complete R20 and R21 authorities, the producer
packet and return, all 984 bridge lines, all 307 focused-test lines, both complete
canonical manifests, and the return template before deciding the merits.

Every fixed producer binding reproduced before testing:

| artifact | physical SHA-256 |
|---|---|
| `src/scouting/sources/wyscout_manifest.py` | `ef16a489a13dffab7cf2b609f81d2a229a012ec5b92ba4debee0f628b35e721c` |
| `tests/unit/test_wyscout_source_manifest.py` | `c7c71cf5abc9b996b7c93ed9b7005b1469f5614ba9d2653a74dc135310e038d1` |
| producer return | `eb3e7e8cfee728c0fdcaa6747079f48f998d033a56cac21a98425b4ce6368dc9` |
| source snapshot manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` |

The source manifest is exactly 4,199 bytes, mode `0600`, link count one, and has
the fixed identities:

```text
manifest_id = 4e16bdb5-afe7-5601-88ad-adc124cfce3b
trace_id = 2c441714-d968-5495-8339-c85ecaf5f596
tenant_id = 65a43912-d412-5ff9-a364-7f84d1ad6c5d
club_id = null
```

The immutable R20 and R21 design digests also reproduced as
`8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
and
`faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`.

## Independent real-source reconstruction

I recomputed SHA-256 and byte size directly for all 18 fixed evidence paths. Every
row matched R20 exactly, in order:

```text
completion-manifest.json                         6803 / null
objects/competitions.json                        1209 / 7
objects/teams.json                              27404 / 142
objects/players.json                          1737347 / 3603
objects/matches.zip                            645097 / null
objects/events.zip                           77323413 / null
objects/eventid2name.csv                         1001 / 36
objects/tags2name.csv                            1754 / 59
archive-members/matches_England.json          1694720 / 380
archive-members/matches_France.json           1707222 / 380
archive-members/matches_Germany.json          1377328 / 306
archive-members/matches_Italy.json            2019196 / 380
archive-members/matches_Spain.json            1705380 / 380
archive-members/events_England.json         188888614 / 643150
archive-members/events_France.json          186374196 / 632807
archive-members/events_Germany.json         152916631 / 519407
archive-members/events_Italy.json           190544685 / 647372
archive-members/events_Spain.json           184164406 / 628659
```

The first value is the exact physical byte size and the second is the independently
parsed row count. `jq` parsed every admitted JSON array rather than relying on the
producer counter; the two CSV files independently reproduced their exact headers
and `36/59` data-row counts. The completion manifest independently reproduced its
6,803-byte SHA-256
`69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`.

## Contract, identity, rights, and temporal evidence

Strict `SourceSnapshotManifest` parsing followed by canonical reserialization was
byte-identical to the physical source-manifest file. An independent stdlib UUIDv5
calculation using the R20 namespace and terminal-LF canonical identity preimage
reproduced both fixed UUIDs.

The parsed contract has exactly 18 ordered file rows and six ordered coverage
dimensions. Every dimension is exact `1.0`, observed and expected counts are
`7/7`, `10/10`, `5/5`, `5/5`, `5/5`, and `4/4`, overall is exact `1.0`, and
`missing_dimensions` is empty.

Rights are exactly `restricted`, derived-data and internal-review use are allowed,
export is false, attribution is required, and the fixed attribution text is
present. Clocks are exactly source availability `2020-01-28T14:24:27Z` and local
acquisition `2026-07-29T15:51:08.598589Z`; no current or filesystem clock enters
the contract.

## Fail-closed behavior and scope

Line-by-line inspection and the executable negative suite show that the bridge:

- opens only the closed 18-path roster using contained descriptor-relative,
  no-follow reads and checks exact size, SHA-256, and declared row count;
- rejects missing, extra, reordered, wrong-path, wrong-size, wrong-digest, and
  wrong-row-count evidence;
- rejects completion identity, clock, rights, collection, object, admitted-member,
  exclusion, duplicate-key, and canonical-byte drift;
- rejects tenant/club changes, root aliases, source symlinks, unsafe manifest
  destinations, noncanonical UUIDs, and unequal pre-existing manifest bytes;
- retains exact canonical bytes on equal existing content and uses no discovery,
  provider access, payload dispatch, current-time input, or metadata-time input;
- imports no network/process client and contains no Bronze, Silver, Gold, receipt,
  rebuild, or product destination authority.

The exact Wyscout working root contained no Bronze, Silver, or Gold descendant
during review. The producer-owned manifest path was the sole Wyscout artifact
materialized by this packet.

## Reproduced checks

All corrected packet checks passed:

```text
uv run ruff format --check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py
PASS — 2 files already formatted

uv run ruff check src/scouting/sources/wyscout_manifest.py tests/unit/test_wyscout_source_manifest.py
PASS — All checks passed

uv run mypy src/scouting/sources/wyscout_manifest.py
PASS — no issues in 1 source file

uv run pytest -q tests/unit/test_wyscout_source_manifest.py tests/contracts/test_w04_r21_cross_authority_composability.py
PASS — 139 passed in 67.99s

uv run python -m scouting.sources.wyscout_manifest --source-root data/source/wyscout/v5 --manifest-root data/manifests --tenant-id 65a43912-d412-5ff9-a364-7f84d1ad6c5d
PASS — confirmed exact 4,199-byte manifest and expected SHA-256
```

I repeated the exact CLI confirmation. Before and after, the target retained inode
`90901756`, size `4199`, mode `0600`, link count `1`, modification epoch
`1785500625`, and the same SHA-256. This independently demonstrates byte-idempotent
existing-artifact behavior with no second artifact or byte replacement.

Per the master's corrected packet and `AGENTS.md`, I did not run Git commands or
`verify_local_only.py`, whose implementation invokes Git. Those boundary checks
remain master-owned and do not weaken the reproduced source-manifest evidence.

## Findings and residual boundary

### P0

None.

### P1

None.

### P2

None.

The bridge intentionally validates evidence only. Identity resolution and every
product layer remain unavailable until their separately gated packets. This is the
correct bounded residual, not a review finding.
