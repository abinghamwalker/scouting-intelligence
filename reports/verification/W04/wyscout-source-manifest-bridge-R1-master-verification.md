# W04 Wyscout source-manifest bridge R1 — master verification

## Decision

`ACCEPT`.

The master inspected every producer and reviewer change, independently reran the
complete packet checks, and accepts the sole bridge from the frozen Wyscout
completion evidence to the immutable local `SourceSnapshotManifest`.

The accepted surface ends at source evidence. It grants no identity, Bronze,
Silver, Gold, build, model, endpoint, deployment, or other product authority.

## Bound artifacts

| artifact | physical SHA-256 |
|---|---|
| bridge | `ef16a489a13dffab7cf2b609f81d2a229a012ec5b92ba4debee0f628b35e721c` |
| focused tests | `c7c71cf5abc9b996b7c93ed9b7005b1469f5614ba9d2653a74dc135310e038d1` |
| producer return | `eb3e7e8cfee728c0fdcaa6747079f48f998d033a56cac21a98425b4ce6368dc9` |
| source manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` |
| independent review | `620d674e08b6c81bed7a9d6d27651b439b5bcf78ef698b1ac3aaff17f9520392` |
| reviewer return | `ebe95be8db7664f1ae5751154a2a6c323fa7e3955ff22244067cadb0d66fd34c` |

The accepted manifest is exactly 4,199 bytes, mode `0600`, link count one, with:

```text
manifest_id = 4e16bdb5-afe7-5601-88ad-adc124cfce3b
trace_id = 2c441714-d968-5495-8339-c85ecaf5f596
tenant_id = 65a43912-d412-5ff9-a364-7f84d1ad6c5d
club_id = null
```

It contains the exact ordered R20 roster of 18 paths, exact sizes, SHA-256
digests and declared row counts. Its six source-coverage dimensions and overall
coverage are exactly `1.0`, with no missing dimension. Rights are restricted;
derived data and internal review are allowed, export is false, and attribution
is required. Source and acquisition clocks reproduce the frozen completion
evidence and do not use current or filesystem time.

## Independent review

The distinct reviewer returned `PASS` with `P0=0`, `P1=0`, and `P2=0`.
It independently recomputed all 18 physical digests/sizes and parsed every
declared JSON/CSV row count. It also reproduced canonical contract readback,
UUIDv5 derivation, rights, clocks, permissions, immutable idempotency, and
negative fail-closed behavior.

The reviewer edited only its two evidence paths and performed no direct or
indirect Git operation.

## Master-reproduced checks

```text
uv run ruff format --check
PASS — 2 files already formatted

uv run ruff check
PASS — All checks passed

uv run mypy src/scouting/sources/wyscout_manifest.py
PASS — no issues in 1 source file

uv run pytest -q tests/unit/test_wyscout_source_manifest.py \
  tests/contracts/test_w04_r21_cross_authority_composability.py
PASS — 139 passed in 66.76s

uv run python -m scouting.sources.wyscout_manifest \
  --source-root data/source/wyscout/v5 \
  --manifest-root data/manifests \
  --tenant-id 65a43912-d412-5ff9-a364-7f84d1ad6c5d
PASS — confirmed exact path, SHA-256 and 4,199-byte size

uv run python scripts/verify_local_only.py
PASS — 25/25 checks

git diff --check
PASS

git remote
PASS — empty
```

## Scope and next authority

No remote, cloud resource, hosted CI, container, public endpoint, or external
deployment was created. The next serial authority is the master-owned identity
v1 decision/ruleset, which must bind this source manifest and the accepted R21
field v2 route before independent review and master acceptance.
