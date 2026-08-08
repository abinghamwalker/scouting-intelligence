# W04 23-root schema closure R4 master pre-review

- Date: 2026-08-01
- Master: `/root`
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4`
- Verdict: `READY_FOR_FRESH_INDEPENDENT_REVIEW`

## Frozen candidate

| Path | SHA-256 |
|---|---|
| `src/scouting/storage/formats.py` | `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `8e68548967293b28e694359509667106951bdc5ba8e1636a541f81f7c3773e1a` |
| `src/scouting/contracts/wyscout_schema.py` | `67b29d6f13228f8e9ba87468545457961c6fdf808831aa1d2ae08ef12d2b7c3b` |
| `tests/contracts/test_w04_wyscout_schema_closure.py` | `c6ae3c4c469c0fec819a18ee3d929ec9cd291f386ff8dae2fb44394173fa7c42` |
| producer return | `be45bfef87e8ad0429434ecef1315eea3db393417764369112eaf02275aeb95e` |

The storage implementation is byte-identical to the already accepted R3 projection implementation. The other three implementation/test files were read in full after their final R4 hashes reproduced. `git diff --check` passed.

## Independent master probes

The master ran two read-only executable probes independently of the producer tests.

1. Authority/projection composability:
   - exactly 23 roots and the exact 12 Parquet / 11 JSON-only split;
   - exact deep equality for the five build/product and four season/lineup accepted authority subobjects;
   - exact E1-E8 roster and physical SHA-256 verification of every cited authority source;
   - accepted raw-record digest present and stale R3 digest absent;
   - `WindowIdentity` and `PreBuildProjection` absent from reachable definition schemas;
   - six repeated physical `CANONICAL_DECIMAL_UTF8` paths, all arising only from the two authorized logical owners;
   - 30 remaining `DECIMAL128(22,18)` paths, including event seconds, coordinates and possession-order positions.
2. Runtime reachability:
   - regenerated every model name reachable from the 23 Pydantic serialization schemas;
   - enumerated effective validators from the frozen contract owners;
   - exact equality with the candidate predicate keys: 56 reachable bindings, no omission or addition;
   - all emitted bindings have runtime classification, non-empty operands and structured constants.

The minimum serialization matrix contains exactly 29 fresh strict Pydantic instances over all twelve Parquet roots. Projection is mechanical from the accepted descriptor, and no `model_construct` is used for acceptance rows. The Decimal rejection families assert zero Parquet writes for aliases, non-finite values, null misuse, invalid UTF-8 and non-string physical values.

## Master-run checks

| Check | Result |
|---|---|
| focused Ruff format/check | PASS |
| focused mypy | PASS |
| focused schema/storage tests | `249 passed` |
| implementation and adjacent contract suite | `526 passed` |
| authority/composability suite | `179 passed` |
| local-only verifier | PASS, `25/25` |
| branch/remotes | `main`; zero remotes |

No provider access, network access, Git operation, dependency change, product/aggregate write, publication, container, CI, cloud or deployment action occurred.

## Finding disposition

The four P1 families returned to R3/R4 rework now have executable candidate evidence:

1. predicate operands/composition: complete reachable runtime ledger plus distinct E1-E8 predicates;
2. frozen constants: exact nine-authority deep equality and cited-source digest reproduction;
3. test coverage: 29 valid model rows plus retained adversarial suites;
4. serialization: bounded two-owner canonical Decimal UTF-8 inverse with zero-write failures, while all other bounded Decimal positions retain `decimal128(22,18)`.

This report is not acceptance. A separate report-only reviewer must verify the frozen candidate and return any P0/P1/P2 finding before the master may run the complete repository gate.
