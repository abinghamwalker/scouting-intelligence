# W04 exact Decimal128-with-exponent independent review — R1

Date: 2026-08-02

Verdict: **REWORK**

Finding counts: **P0 0 / P1 1 / P2 0**

This is a fresh independent review of the exact candidate fixed by
`W04-EXACT-DECIMAL128-WITH-EXPONENT-REVIEW-01-R1`. It grants no schema-adoption,
product, checkpoint, or publication authority.

## Fixed candidate and chain of custody

All packet-fixed bindings matched before analysis and again immediately before
this review was rendered:

| Binding | Observed SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `8fc57c2ceb8ac714cb2573802d7bc745afb05e67e2c14d302b6b06cd911086d6` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `f529ca1c87795e67ed17b62285e1df50fe5d85757e85de45a14a704d39a56660` |
| R1 producer return | `369f3cdeed2a4424cf36146608e5fdfbcfeb15be52f13281f0e36f47d8b629eb` |
| bounded authorization | `57ef5ce132f732457df6dac4bfd99c554ba5497a9759bd322d0093a5af8b3131` |

## P1 — inverse signed-zero Boolean toggles rather than sets the sign

Code: `W04_EXACT_DECIMAL_SIGN_BOOLEAN_NOT_AUTHORITATIVE`

`_decode_exact_decimal128_with_exponent` applies `restored.copy_negate()` when
`negative_zero` is true and makes no sign correction when it is false. That logic
depends on the numeric zero child's incoming sign. It does not make the Boolean
authoritative as required.

A fresh exact-typed scalar probe supplied each Boolean with both possible numeric
zero signs. The results were:

| Numeric child sign | `negative_zero` | Actual logical token | Required token |
| --- | ---: | --- | --- |
| positive zero | `true` | `-0` | `-0` |
| negative zero | `true` | `0` | `-0` |
| positive zero | `false` | `0` | `0` |
| negative zero | `false` | `-0` | `0` |

The two failures prove that true toggles an already-negative child to positive and
false allows an already-negative child to leak through. Present PyArrow table
construction normalizes the decimal child to positive zero, so the existing
round-trip tests exercise only the two passing rows and mask the defect. The
authorized inverse explicitly requires the Boolean to determine the restored sign
even when the numeric child arrives with either zero sign. This candidate therefore
cannot pass strict signed-zero reconstruction.

### Bounded correction required

For a reconstructed numeric zero, first clear the incoming sign and then set the
sign solely from `negative_zero`; retain the existing rejection of
`negative_zero=true` for nonzero values. Add a direct inverse adversarial matrix
covering both numeric zero signs crossed with both Boolean values, independent of
PyArrow's current normalization. Preserve all logical contracts, descriptor shape,
capacity/source-scale validation, byte equality, digest formula, and coverage
projection behavior.

## Passing evidence outside the finding

- The generated physical schema was exactly the ordered, non-null,
  metadata-absent struct `value: decimal128(22,18)`, `exponent: int8`,
  `negative_zero: bool`; alternate child order/count/nullability and wrong runtime
  exponent/sign schemas failed closed.
- An independent 11-value success matrix covered exponents `-18`, `0`, and `+3`,
  significant trailing zeros, positive/negative zero, positive/negative minimum
  magnitude, and exact lower/upper signed capacity edges. Forward child values and
  Pydantic JSON-mode logical tokens were exact, and all current PyArrow-normalized
  rows reproduced their logical JSON bytes.
- Eight malformed inverse/alias cases, two wrong-child runtime schemas, four
  alternate descriptors, and nine forward type/finite/scale/capacity cases were
  rejected. Instrumented semantic-hash and Parquet-write counters remained `0`.
- Coverage remains `CANONICAL_DECIMAL_UTF8`; the accepted semantic version and
  length-framed digest formula remain present. The unchanged focused/generic
  storage suite passed `293` tests, including its fixed physical and semantic
  vectors.
- Ruff, Mypy, Bandit, import boundaries, formatting, and all 25 local-only controls
  passed. No dependency, provider/network, product, or local-only boundary change
  was observed.

## Commands and results

- packet-fixed `shasum -a 256` checks before review and immediately before rendering
  - exit `0`; all four fixed hashes matched exactly both times.
- `uv run python -c '<independent four-way signed-zero inverse probe>'`
  - exit `1` by design; 2/4 cases failed exactly as recorded above, confirming P1.
- `uv run python -c '<independent exact Decimal success/schema/JSON-byte matrix>'`
  - exit `0`; 11/11 current-normalization vectors passed with exact physical
    children and logical byte reproduction.
- `uv run python -c '<independent inverse, schema, descriptor, forward and zero-call attack matrix>'`
  - exit `0`; 8 inverse, 2 runtime-schema, 4 descriptor, and 9 forward attacks
    rejected; semantic hash calls `0`, Parquet writes `0`.
- `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/unit/test_guarded_storage.py`
  - exit `0`; `293 passed in 2.48s`.
- `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit `0`; all checks passed.
- `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit `0`; no issues in 2 source files.
- `uv run bandit -q -r src/scouting/storage/formats.py`
  - initial sandbox exit `2` because access to the existing uv-cache `.git` path
    was denied; identical approved read-boundary rerun exit `0`, no findings.
- `uv run lint-imports`
  - initial sandbox exit `2` for the same uv-cache read denial; identical approved
    rerun exit `0`, `3 kept, 0 broken`.
- `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit `0`; 2 files already formatted.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25 controls and zero configured remotes.

No Git command, implementation/test edit, dependency/lock change, delegation,
product, manifest, source, provider, network, cloud, container, hosted-CI,
deployment, or publication action occurred.
