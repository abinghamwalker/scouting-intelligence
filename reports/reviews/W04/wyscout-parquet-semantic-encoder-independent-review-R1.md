# W04 Parquet semantic encoder independent review — R1

Date: 2026-07-31

Verdict: **REWORK**

Finding counts: **P0 0 / P1 1 / P2 0**

This is an independent byte/security review of the exact candidate fixed by
`W04-PARQUET-SEMANTIC-ENCODER-REVIEW-01-R1`. It grants no publication or product
authority.

## Fixed candidate

All fixed bindings matched before analysis and matched again immediately before
this review was written:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `2737a4b67eef492b4a5809d302c726470670c0ef2c14a2a7f5fae7d11453c49a` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `271925b89532080dc302abd4d75ee6a78e1382ae67f619bcc26a58c8ac796d05` |
| producer return | `5bd75fafe20ae09f01b03563706e20b8cfcf675352afe840ec3d2e4240cc330c` |

The fixed physical vector reproduced as
`889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b`.
The independently reconstructed length-framed semantic preimage reproduced
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

## P1 — physical Arrow rows are not bound to the claimed semantic rows

Code: `W04_ENCODER_ARROW_CONTRACT_ROW_BINDING_MISSING`

The encoder validates the Arrow schema and row count, then hashes the caller's
`contract_row_bytes`. Its only row-level comparison is between fields read from
those same supplied contract bytes and the separately supplied `primary_keys`.
It never compares the Arrow table's values with the contract row values, and it
does not derive or strictly compare primary keys from the Arrow columns.

The mandatory independent probe kept the two supplied primary keys and both
contract rows unchanged while changing only Arrow row 2's non-key `label` from
`bravo` to `UNCLAIMED-ARROW-VALUE`. The API accepted the candidate and emitted a
Parquet payload containing `UNCLAIMED-ARROW-VALUE`. Its physical SHA-256 changed,
but its semantic SHA-256 remained exactly the baseline
`6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

The same missing boundary binding admitted two related strict-key bypasses:

- an `int64` Arrow `record_id` column was accepted with supplied string keys and
  contract JSON string IDs (`"1"`, `"2"`); and
- contract JSON Boolean `true` was accepted against supplied integer key `1`
  because the comparison uses Python value equality, where `True == 1`.

This is a false semantic binding: exact physical bytes can be paired with a digest
claiming different semantic rows. R20 requires semantic digests to cover the exact
schema, ordered rows, and parents. No accepted later mandatory correspondence
checker exists in this candidate; the separately proposed publisher is not an
implemented or accepted substitute for a fail-closed encoder boundary. The packet
therefore requires P1 `REWORK`.

### Bounded correction required

Before this encoder can be accepted, it must fail closed unless every Arrow row is
proved to be the exact typed representation of its corresponding canonical
contract row. The correction must also:

1. require every primary-key field to exist in the Arrow schema;
2. derive or strictly compare each key against the Arrow column value with exact
   type identity, so Boolean/integer and string/integer confusion cannot pass;
3. compare all non-key values, including null/list/decimal/UUID/UTC forms under an
   explicit accepted canonical projection, not Python loose equality; and
4. add adversarial tests for unchanged-key/non-key divergence, Arrow-key
   divergence, string-versus-integer keys, Boolean-versus-integer keys, and a
   contract key absent from the Arrow schema.

The valid fixed vectors and generic serializer API should remain unchanged unless
the master issues a separate authority to change them.

## Passing evidence outside the finding

- Exact Parquet 2.6 bytes, stored schema, ZSTD encoding, statistics, no dictionary,
  no byte-stream split, no column/offset indexes, and deterministic readback
  reproduced. The source explicitly supplies ZSTD level 9, data-page 2.0, page
  index off, microsecond coercion without truncation, and stored schema; the fixed
  physical vector binds that complete call.
- Independent 65,535/65,536/65,537 probes produced row-group sizes `(65535)`,
  `(65536)`, and `(65536, 1)`.
- Nanosecond timestamps failed before encoding as required.
- Independent preimage construction reproduced the semantic vector. Two parent
  sequences with the same unframed concatenation, `("a", "bc")` and
  `("ab", "c")`, produced distinct semantic digests. Unsigned-64-bit overflow
  failed closed.
- The focused suite exercised schema/row/parent mutations, noncanonical and
  duplicate JSON, duplicate rows/keys, unsafe/reordered/duplicate parent paths,
  schema metadata, nullability, inference and coercion denials.
- The unchanged generic guarded-storage suite passed. Local-only verification
  passed all 25 controls and reported zero configured remotes.

## Commands and results

- `shasum -a 256 src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/returns/W04-PARQUET-SEMANTIC-ENCODER-01-R1.md`
  - exit `0`; all three fixed hashes matched, both before analysis and before
    review rendering.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent fixed-vector, framing, non-key divergence, string-key and Boolean-key probe>`
  - initial sandbox attempt exited `2` because the sandbox denied the existing uv
    cache `.git` path; no probe or repository/product write ran;
  - identical approved read-boundary rerun exited `0` and printed
    `non_key_divergence_accepted=true`, `same_false_semantic=true`,
    `different_physical=true`, `string_primary_key_type_divergence_accepted=true`,
    and `bool_int_primary_key_confusion_accepted=true`, together with both fixed
    vectors, Parquet `2.6`, statistics present, framing separation and uint64
    rejection.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <independent 65535/65536/65537 and timestamp probe>`
  - exit `0`; row groups were `[65535]`, `[65536]`, `[65536,1]`; nanosecond
    timestamp rejected.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `50 passed in 1.74s`.
- `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25/25 local-only controls.

No product, manifest, receipt, source, provider, network, cloud, container, hosted
CI, endpoint, remote or deployment action occurred. No Git command was run.
