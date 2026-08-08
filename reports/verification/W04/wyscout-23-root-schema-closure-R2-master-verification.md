# W04 23-root schema closure R2 master verification

Date: 2026-08-01

Verdict: **REWORK — INDEPENDENT REVIEW NOT DISPATCHED**

Findings: **P0 0 / P1 4 / P2 0**

## Candidate admitted for inspection

| Artifact | Reproduced SHA-256 |
| --- | --- |
| `src/scouting/contracts/wyscout_schema.py` | `a7066f9e7cd97ead2fabe9410cd3507fc8a497bfc86fcaafd7182fbcd2704c95` |
| `tests/contracts/test_w04_wyscout_schema_closure.py` | `ce1af49ec56d48073979a3f178aa15d5336bb6aa7ff78bd6adaff5fb04167cb1` |
| producer return | `9294582ddf8a2d26df047f86690c13837a27e3e4b524c2fc08dae814c268f8d1` |
| corrected independent constraint oracle R2 | `3ac167f4a63f26d930abe039ec7417637d204f984db6f0cc578dd322526c2120` |

The candidate preserved its three assigned paths, contains no contracts-to-storage
or PyArrow production import, exports 23 roots/rows, retains the accepted dependency
order, and uses the corrected four whole-value tagged UTF-8 paths. Those passing
properties do not cure the findings below.

## P1-01 — emitted validator predicates are not executable descriptions of their owners

The candidate treats matching the number of Pydantic validator names as closure,
but nine emitted predicates name operands that do not exist on the owning runtime
model:

```text
ActionPosition: in_unit_interval
DependencyRow: valid_from, feature_cutoff_ts
PossessionPeriodSequence: completion_index_sha256, match_source_id,
  action_count, ordered_membership_sha256
PossessionSequenceAction: action_source_id, match_source_id, raw_record_sha256
RawKindEvidence: state, envelope_sha256, witness
SourceUseClassification: licence_use_class, commercial_use_allowed,
  redistribution_allowed
WyscoutAuthorityClock: available_at, valid_from
WyscoutRawSourceRowReference: raw_record_sha256
WyscoutSourceAuthority: provider
```

The independent master probe enumerated every reachable runtime model and rejected
exactly these nine invalid predicate records. Other records use real field names but
wrong constants or relations: coordinates are declared `0..1` instead of `0..100`;
the boundary state is `VERIFIED` instead of
`STRICT_BEFORE_CUTOFF_PASS`; DependencyRow uses a cutoff relation instead of
`observed_at <= available_at`; entrypoint descriptor number is falsely fixed to 3;
and four-row data authorities/clocks are described as a five-row roster.

The generic SilverMatch predicate also claims the season `181150` binding that its
runtime validator does not perform, while the generic lineup-stint predicate claims
the single authorized POC row/ID. Those composed admission/population authorities
must be represented separately from runtime-object validation; otherwise the schema
both overstates the model and obscures where source authenticity is actually proven.

## P1-02 — frozen predicate constants are omitted or replaced by labels

The root content does not contain the complete constants needed to execute its
claimed predicates. Across all 23 canonical contents, master search found zero
occurrences of, among others:

- `archive-members/events_England.json`, its accepted member digest, and its row
  count;
- the accepted field-review digest and the exact 119-row registry;
- the exact subevent reason values and admitted event/subevent pairs;
- the 1H/2H completion-index membership digests and counts; and
- the independently reproduced season UUID.

Values such as `FROZEN_W04_COMPLETION_MEMBER_KIND_MAP`,
`EXACT_PERIOD_POPULATION`, `W04_WYSCOUT_UUIDV5`, or a roster count are labels, not
the exact structured operands/constants required by the readiness authority. The
accepted source/member map, authority rows/clocks, field registry, strict subevent
maps, possession sets/order rules, dependency rows, completion-index populations,
season binding, one-lineup population, layer semantic formula, and receipt/readback
composition must be emitted as exact structured runtime or external-admission
predicates without adding a root or semantic derivation.

## P1-03 — executable Decimal-domain contradiction blocks descriptor acceptance

The candidate maps every Decimal to `decimal128(22,18)`. That width/scale is exact
for event seconds and coordinates because their validators enforce that capacity.
It is not exact for `GoldCoverageDimension.coverage` or
`GoldCoverage.coverage_overall`.

The accepted runtime contract computes positive-denominator coverage with Decimal
context precision 38 and requires byte-semantic equality to `N / D`. Master
constructed the valid logical value `N=1, D=3`, which validates as:

```text
0.33333333333333333333333333333333333333
```

PyArrow then rejects that value under the candidate descriptor:

```text
ArrowInvalid: Rescaling Decimal value would cause data loss
```

No single Decimal128 precision/scale represents both the contract's exact repeating
fractions and exact `1` without rounding. Fixing this by quantizing or narrowing the
logical model would change the frozen R20 exact-coverage semantics. Fixing it by
canonical UTF-8 requires an additional reversible logical-to-Arrow rule for these
unbounded-scale coverage Decimal fields. That rule is not part of the currently
accepted projection authority, so the master will not invent it.

## P1-04 — focused tests prove self-consistency, not complete acceptance

The test named for every runtime validator asserts only predicate count, nonempty
strings/lists, and object shape; it does not resolve operands or reproduce
constants. The end-to-end encoder test exercises only three of twelve Parquet roots.
Consequently all 22 focused tests pass while P1-01, P1-02, and the valid 1/3
serialization failure remain undetected.

Rework tests must independently validate every runtime predicate operand/constant,
distinguish runtime from guarded-reader/composed authority, reproduce the frozen
constant corpora, and execute descriptor-led encode/inverse equality for all twelve
roots, including required logical-null fields and both constrained and coverage
Decimal paths.

## Master command evidence

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- Ruff format/lint and mypy on the candidate: PASS.
- focused schema tests: `22 passed`.
- complete candidate/adjacent suite: `474 passed in 112.49s`.
- authority/composability suite: `179 passed in 3.93s`.
- local-only verifier: PASS `25/25`; zero remotes.
- predicate operand probe: PASS as a rejection proof; exactly `9` invalid emitted
  predicate records reproduced.
- Decimal-domain probe: valid runtime coverage reproduced; PyArrow lossless write
  failed with `ArrowInvalid` under `decimal128(22,18)`.

## Gate decision

The R2 candidate is preserved as failed implementation evidence. No independent
candidate review, v2 aggregate, Gold receipt closure, product implementation, or
publication may proceed.

P1-01, P1-02, and P1-04 are bounded schema-producer rework. P1-03 requires an
explicit additive projection decision before the master can issue a complete R3
packet. The smallest safe correction is a descriptor-owned canonical Decimal UTF-8
projection for only the unconstrained exact Gold coverage Decimal fields, with
strict Decimal parsing, canonical re-encoding and byte equality; event seconds,
coordinates, roots, fields, semantics, digest path, features, population,
dependencies and local-only boundaries remain unchanged.
