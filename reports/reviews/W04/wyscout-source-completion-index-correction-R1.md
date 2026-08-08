# W04 source-completion-index correction R1

Status: `AUTHORIZED_FOR_IMPLEMENTATION`

## Authority and preservation boundary

The user authorized this one additive, bounded correction on 2026-07-31 after
executable R4/R5 evidence proved that a caller-selected in-memory Bronze population
could omit source actions without contradicting the frozen whole-file source manifest.
This correction does not replace or mutate R20, R21, their accepted preimages, the
`checkpoint/w04-r21-accepted` commit, or any failed-review evidence. Those bytes remain
historical and controlling except for the narrow source-population completeness defect
and equal-clock defect superseded here for implementation.

Frozen inputs:

- R20 SHA-256: `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- R21 SHA-256: `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
- R21 checkpoint commit: `82a9f05`
- source-manifest ID: `4e16bdb5-afe7-5601-88ad-adc124cfce3b`
- source-manifest SHA-256:
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
- completion-manifest SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`

No provider access, dependency change, product feature, cloud, container, hosted CI,
public endpoint, remote, or deployment is authorized.

## Exact correction contract

The completion reader shall derive one deterministic, local, immutable source-
completion index from only the five admitted event archive members already named by
the frozen source snapshot. Before reading any event for index derivation it shall
reverify the canonical completion document and the exact whole-file manifest size,
SHA-256, and declared top-level row count. The index scope is exactly `England`,
`France`, `Germany`, `Italy`, and `Spain`; it makes no completeness claim outside
those five admitted W04 product partitions.

For every match-period present in those authorized event members, the index shall
contain the exact action count and a canonical ordered membership digest. Each member
preimage shall bind all of:

1. source-member path and source-member SHA-256;
2. zero-based physical source ordinal;
3. strict integer provider event identity;
4. strict integer provider match identity;
5. exact period code;
6. exact period-relative clock plus the physical/provider ordering tie-breaks;
7. strict integer-or-null player and team identities;
8. strict integer event identity and strict integer-or-null subevent identity, with no
   string coercion;
9. the exact ordered raw tag evidence and the canonical strict-integer tag projection
   used by possession semantics; and
10. the canonical raw-record SHA-256 used by Bronze/source lineage.

The index payload shall reconcile exactly to every authorized member's manifested row
count and to the aggregate authorized event row count. Its canonical bytes shall be
addressed by their SHA-256. Source-manifest ID/digest and every scoped member
path/digest/row-count binding are part of the index payload.

On every accepted product path, the completion reader shall:

- load only the exact content-addressed local index;
- recompute and verify its canonical bytes and content address;
- verify the source-manifest and source-member bindings;
- verify canonical partition/period ordering, identity and physical-row uniqueness,
  period counts, and aggregate reconciliation;
- require the supplied period population to be in exact canonical order and recompute
  exact equality to the indexed count and membership digest; and
- reject missing, additional, duplicated, reordered, stale, cross-member,
  cross-match, or cross-period actions.

A Boolean completeness claim, a caller-supplied count, an unbound witness, or a digest
computed only from the caller's submitted subset is not authority.

Every accepted Silver possession/player-match fact and Gold player-window provenance
and dependency lineage shall bind the accepted completion-index SHA-256. Causal
other-player and ineligible rows used by possession resolution remain in the exact
source provenance. Gold remains limited to exactly:

- `action_count`
- `coordinate_known_action_count`
- `match_count`
- `resolved_possession_action_count`

## Equal-clock correction

All CONTROL/RESTART actions at one `(period_rank, period_elapsed_seconds)` clock are
evaluated as a group before a possession transition. Different canonical teams at the
same clock leave the entire same-clock control group and its dependent contested buffer
unassigned. Possessions completed strictly before that clock remain deterministic;
physical ordinal or provider identity must not choose a team within the ambiguous
clock.

## Acceptance boundary

Fresh independent review must reproduce the content-address, truncation, whole-period
omission, additional/duplicate/reorder/stale/cross-period failures, aggregate
reconciliation, provenance/lineage binding, and equal-clock behavior. Only after that
review and the complete repository master gate pass may the raw-to-Bronze-to-Silver-to-
Gold four-feature vertical slice resume.
