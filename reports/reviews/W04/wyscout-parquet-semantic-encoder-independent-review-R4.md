# W04 Parquet semantic encoder independent review — R4

Date: 2026-08-01

Verdict: **PASS**

Finding counts: **P0 0 / P1 0 / P2 0**

This is a fresh independent byte/security review of the exact R4 candidate fixed by
`W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R4`. It closes the bounded R3 metadata-
presence finding and recommends this exact candidate for master acceptance. It
grants no product or publication authority.

## Fixed candidate and chain of custody

All packet-fixed bindings matched before analysis and again immediately before
review rendering:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `c0afb390ef44f19d4759b62495bc0125a14fb80ac0f1e4376972a798702e3a9f` |
| R4 producer return | `b043cc215a3df053152798e46b1e2e819bdc36473da45a623b5439c90adb810b` |

The frozen R20 authority remained
`8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`.
The fixed physical vector reproduced as
`889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`;
the independently reconstructed semantic preimage reproduced
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

The preflight and final postflight read-only bytecode inventories were identical:
1,162 `.pyc` files in 150 `__pycache__` directories, content-stream digest
`baea9f7375d0848d91205ac4038b804e5416bff6cc6ebe1b044fba769f8d0791`
and path/mode/link-count/size stream digest
`6742e35ab6b34330378847901f36cbd77db27c1c82c6887f4c710e0d8bd916fc`.

## R3 finding closure

The shared closed schema validator now tests metadata presence with `is not None`
at the schema, top-level field, struct-child field and all list-family value-field
boundaries. The same recursive path covers list, large-list, fixed-size-list,
nested-list, list-under-struct and struct-under-list schemas.

An independent attack matrix first admitted nine metadata-absent controls, then
applied explicit empty `{}` and non-empty `{b"hidden": b"value"}` maps to each of
those nine boundaries. All 18 altered schemas were rejected through both the
encoder and public semantic helper: 36/36 rejection paths. Instrumented digest and
Parquet-writer call counters both remained zero. Thus neither direct descriptor
construction nor the public helper provides a metadata alias around encoder
validation.

An independent raw PyArrow differential confirmed why the presence distinction is
security-relevant. Absent and explicit-empty schema metadata serialize differently.
With the same R20 physical controls, their in-memory Parquet bytes also differed:

| Variant | Physical SHA-256 | Bytes |
| --- | --- | ---: |
| metadata absent (`None`) | `c4860fb36155968ca678f1a1ace30f2469c2eab113e502daf679c5a50ddc774f` | 472 |
| explicit empty (`{}`) | `7fa92ee32a81ce6aa07a3442a9e14f782dd6d04babef6021e291a6652e4e449e` | 492 |

Those raw bytes demonstrate the alternate physical representation; the R4
candidate admits neither altered representation and reaches neither hashing nor
writing for it.

## Preserved R1–R3 guarantees

- The public helper rejected omitted schema, fabricated type text, serializer,
  field name/order/nullability and role mismatches, an actual binary schema,
  naive/non-UTC/nanosecond timestamps, a non-canonical list child name, malformed,
  duplicate-key and non-finite JSON, and unsorted parents. All 16 cases failed
  before any digest construction.
- Exact recursive decimal, list, large-list, fixed-list, struct and UTC-microsecond
  projection encoded successfully. Unchanged-contract non-key divergence,
  Arrow/supplied-key divergence, string/integer and Boolean/integer confusion,
  missing Arrow keys, decimal divergence, forbidden list nulls, binary fields and
  non-finite floats all failed closed: 9/9 attacks rejected.
- Independent semantic framing separated parent sequences `("a", "bc")` and
  `("ab", "c")` despite equal unframed concatenation.
- Exact Parquet 2.6 output, stored Arrow schema, ZSTD compression, statistics, no
  dictionary, no byte-stream split, no column/offset indexes and deterministic
  fixed vectors reproduced. Row-group probes produced `[65535]`, `[65536]` and
  `[65536, 1]` for 65,535, 65,536 and 65,537 rows respectively.
- The unchanged generic guarded-storage suite passed together with the focused
  encoder suite. No generic serializer regression was observed.

## Commands and results

- packet-fixed and frozen-authority `shasum -a 256` checks
  - exit `0`; all fixed hashes matched before analysis; all R4 candidate hashes
    matched again immediately before rendering.
- read-only shell `.pyc` census plus complete content and metadata streams
  - exit `0` preflight and final postflight; counts and both digests were identical.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <recursive metadata-presence attack matrix>`
  - exit `0`; nine absent-metadata controls accepted, all 36 empty/non-empty
    encoder/helper paths rejected, writer calls `0`, digest calls `0`; absent and
    empty schema serializations were distinct.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <raw in-memory metadata physical differential>`
  - exit `0`; serialized schemas and Parquet bytes differed; exact physical hashes
    and sizes are recorded above.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <public-helper and descriptor attack probe>`
  - exit `0`; all 16 schema, descriptor, JSON and parent attacks rejected before
    hashing.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <row/key congruence and recursive-value attack probe>`
  - exit `0`; the complete valid recursive row encoded; all 9 divergence,
    type-confusion, missing-key, forbidden-null, unsupported and non-finite cases
    rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent fixed-vector, framing, Parquet-control and row-group probe>`
  - exit `0`; both fixed vectors, independent semantic preimage, framing
    separation, exact physical controls and all three row-group boundaries
    reproduced.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `81 passed in 2.06s`.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25/25 controls and zero configured remotes.

No Git command or product, manifest, receipt, source, provider, network, cloud,
container, hosted-CI, endpoint, remote or deployment action occurred.
