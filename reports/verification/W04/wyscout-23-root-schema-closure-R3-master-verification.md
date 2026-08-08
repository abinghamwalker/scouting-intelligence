# W04 23-root schema closure R3 master verification

Date: 2026-08-01

Verdict: **REWORK — INDEPENDENT CANDIDATE REVIEW NOT DISPATCHED**

Findings: **P0 0 / P1 3 / P2 0**

## Candidate and independent oracle

| Artifact | Reproduced SHA-256 |
| --- | --- |
| `src/scouting/storage/formats.py` | `84c04be89c6d726ab9129326e7815dda2331bf30ade2f8d41852120e2b6d144c` |
| `tests/unit/test_w04_wyscout_product_formats.py` | `19cd38b7d104029f96c98243992fda126f7a448e71ee5c545128acf2699e17a4` |
| `src/scouting/contracts/wyscout_schema.py` | `fa2f0739a617ef112273e8b1010f2a7f81231027b28710198c55934e8363349e` |
| `tests/contracts/test_w04_wyscout_schema_closure.py` | `ef546491d8ad3618f5982f7a68d3ddeae1cf8c1317d8e9f0ead7c3cad97bc4b4` |
| R3 producer return | `2049b2eba26d209a00a36d3bcedff5acb68d44db25433a0087ab244324586671` |
| independent R3 expected-value oracle | `de4a4119cf1a1158156d55f49f26bae8c1c08b46d36f93bb6c6afe102fdd145f` |
| oracle return | `d6c58d4a0259063ace731f28a65e673a35605abb94e2f16cd20526378107e7a2` |

The storage projection correction itself passed inspection and focused execution:
`CANONICAL_DECIMAL_UTF8` is descriptor-owned, strict, finite, no-rounding,
fixed-point, no-LF and byte-reversible; the schema generator applies it by exact
owning model/field identity to the two authorized coverage fields. All other
independently projected Decimal positions remain `decimal128(22,18)`. These passing
properties do not cure the authority and test findings below.

## P1-01 — the frozen season/lineup source digest is wrong

The candidate emits this match raw-record digest:

```text
1cc084583a48055142846f4ee09ce4b5490db93ba26b30dc459c6f81373d4d86
```

The accepted season/lineup authority and independent oracle require:

```text
1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86
```

The master comparison loaded the accepted authority JSON and exported candidate
corpus in one process and reproduced `raw_digest_equal False`. A schema closure
claiming exact one-row source/population equality cannot contain a different source
record digest.

## P1-02 — build, completion and receipt constants remain partial labels/counts

The R3 packet and independent oracle require complete structured operands/constants,
not semantic labels or counts. The candidate still omits material frozen values:

- the completion object has no `completion_reader_requirements`; the accepted
  authority has exactly eight ordered verification/rejection rules;
- the constant corpus has no exact `build_identity` object and therefore no exact
  pre-build/post-hash 25-key orders, replacement rule or second-hash prohibition;
- the build validators reduce the pre-build claim to a count and three conceptual
  operands, and the rebuild claim to only `build_id`, a count and a digest label;
- admission retains only `component_count=20` instead of the exact ordered component
  keys, canonical manifest bounds and proof/equality inputs;
- child-result/entrypoint claims omit the exact admission and rebuild argv arrays and
  their binding rules;
- layer/receipt composition omits the exact 19 complete-manifest fields, required
  validation order, substitution-failure roster, layer-summary keys, Gold readback
  rules and the exact temporal/rebuild receipt key/rule objects; and
- the frozen window identity/preimage constants are not represented in the reachable
  external/composed authority ledger.

The master probe reproduced `completion_reader_requirements_candidate=None`,
`build_identity_candidate=None`, `required_validation_order_candidate=None` and
`substitution_failures_candidate=None`. Labels such as
`SHA256_CANONICAL_PROJECTION`, `group-first`, or readback token names can describe a
rule but cannot replace the exact values needed to execute its equality.

R4 must compare the emitted source-completion, season/lineup, build-identity,
window, layer-manifest and receipt authority subobjects directly and exactly against
their accepted JSON/contract owners. Manual subset assertions are insufficient.

## P1-03 — all-twelve-root tests still prove descriptor self-consistency, not valid rows

The advertised all-root round trip constructs synthetic values recursively from the
descriptor. It never constructs or revalidates any of the twelve owning Pydantic
root models; master search found no root constructor or `model_validate` call in the
focused file. Values such as arbitrary strings in UUID/enum fields are therefore
accepted by the test oracle even though they are not valid logical contract rows.

The test also asserts only selected season/lineup fields and the lineup UUID, which
is why all 540 tests pass while the wrong raw-record digest survives. It does not
implement the independent oracle's 29-row valid variant matrix. Alias tests exercise
Decimal rejection but, except for invalid UTF-8, do not prove zero Parquet writes for
every malformed family.

R4 must build accepted model instances, require fresh strict model validation, dump
their exact logical rows, mechanically project them under the accepted descriptor,
and execute inverse equality for every one of the twelve roots and the oracle's
required variants. Exact authority-object equality and zero-write Decimal rejection
must be explicit tests.

## Independent master command evidence

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- four-file Ruff format/lint and mypy: PASS.
- required implementation/adjacent suite: `540 passed in 119.64s`.
- authority/composability suite: `179 passed in 3.92s`.
- local-only verifier: PASS `25/25`; branch `main`; zero remotes.
- candidate/oracle hash readback and `git diff --check`: PASS.
- independent validator/corpus probe: PASS with 51 distinct bodies, 61 effective
  bindings, 15 source members, 119 field rows, 36 admitted pairs, 4 data authorities,
  5 build authorities and 5 dependencies.
- exact accepted-authority comparison probe: PASS as rejection evidence, reproducing
  the digest inequality and each missing authority subobject above.

The green suites are preserved evidence that the remaining tests are not yet an
adequate acceptance oracle; they are not evidence that the candidate is exact.

## Gate decision

R3 is preserved as failed implementation evidence. No independent candidate review,
schema-bundle aggregate, product contract, Bronze/Silver/Gold implementation,
manifest, receipt or publication may proceed.

The three findings are bounded to the existing schema producer and its tests. The
accepted Decimal projection, roots, logical fields, semantic digests, features,
population, dependencies, provider/local-only boundary and all frozen R20/R21/v1
authority bytes remain unchanged. No broader authorization is required for R4.
