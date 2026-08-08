# W04 23-root schema closure R4 master verification

- Date: 2026-08-01
- Master: `/root`
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R4`
- Verdict: `REWORK_P1_01_TO_P1_02`
- Findings: `P0 0 / P1 2 / P2 0`

## Independent review binding

The master read the complete fresh report-only review and reproduced its final bytes:

| Artifact | SHA-256 |
|---|---|
| independent review | `676f911ad8e2ad4bff9900e7b53b7d57408a69b51f35f3dc61dc865666abed65` |
| reviewer return | `43919ae91e483fe7534cf5cf4479092dfddd7f58e75d1b1bc035b7df33ea4639` |

The review verdict is `REWORK`, with two bounded P1 findings and no P0/P2 findings. The candidate implementation hashes remained frozen throughout review.

## Master reproduction

### P1-01 — incomplete predicate operands

The master independently parsed the actual frozen validator bodies and compared every direct `self.<model field>` read with the top-level fields advertised by each emitted runtime predicate. The candidate has 56 exact reachable owner/validator bindings, but **26 bindings omit one or more directly read fields**.

Examples independently reproduced include:

- Bronze known/rejected predicates omit source-row, lineage, tenant and rights inputs;
- `GoldCoverageDimension.coverage_is_exact` omits `name` and `zero_denominator_authority`;
- `SilverAction.action_is_strict_and_orderable` omits source/event/team/player, scale, state and lineage inputs;
- player-match, Gold-window and LayerManifest predicates omit material build/source/lineage/rights/coverage inputs;
- all nine effective product-row tenant validators omit index, source-row and lineage inputs;
- the temporal proof predicate omits source/index/authority/feature inputs.

This fails the frozen executable-predicate closure. Counting and resolving a subset of operands is not sufficient.

### P1-02 — incomplete 29-row variant roster

The master independently executed the acceptance matrix builders and observed:

- both Bronze-known rows have recursive tagged kind sets exactly `{integer, object}`;
- all five Bronze-rejected records have one unique raw-record shape;
- all three Silver-action rows retain non-null player/team and event/subevent IDs and use source scale `18`;
- the empty-position action remains predicate-admitted rather than exercising the required null/unmapped arm.

The row cardinality is exactly 29 and the valid model mechanics are sound, but the frozen variant coverage is not met.

## Passing families frozen for R5

The following R4 families passed independent and master review and must remain byte/behavior stable through rework:

1. all nine frozen authority subobjects and E1-E8 composition;
2. bounded canonical-Decimal UTF-8 serialization for the two authorized logical owners;
3. retained `decimal128(22,18)` behavior for event seconds, coordinates and possession-order positions;
4. 23 roots, 12/11 split, logical fields, semantic paths, features, population, dependencies and local-only boundary.

## Executed gates

Before independent review the master ran formatting, lint and typing successfully, `249` focused tests, `526` implementation/adjacent tests, `179` authority/composability tests and local-only `25/25`. The reviewer independently reran the required checks with the same passing results. These regression passes do not override the two acceptance defects.

No complete repository gate, aggregate materialization, product implementation, provider access, dependency change, Git operation, cloud/container/CI action, publication or deployment is authorized from this R4 result.

R4 is returned for bounded R5 rework only.
