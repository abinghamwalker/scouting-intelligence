# W04 Wyscout schema design — independent review R1

Review task: `W04-SCHEMA-DESIGN-REVIEW-01-R1`  
Target: `reports/reviews/W04/wyscout-schema-design-R2.md`  
Role: independent architecture verifier  
Recommendation: **REWORK**

This is a review recommendation, not approval. The R2 design closes all three defects
recorded in `REVIEW-W04-SCHEMA-DESIGN-01-R1`: each ZIP has exactly five admitted and
two directory-only excluded members; generic source clocks permit every truthful
ordering while the Wyscout adapter has a release floor; and the duplicate Gold
identity row is removed. Those corrections are internally clear. The design is not
yet safe to implement, however, because the following P1/P2 defects remain.

## Ranked findings

### P1 — `W04-DESIGN-EVENT-CLOCK-01`: second-half event UTC is fabricated

Evidence:

- Section 7.6 defines second-half `match_elapsed_us` as exactly
  `2_700_000_000 + period_elapsed_us`.
- The next row defines `event_observed_at` as exactly
  `match_start_utc + match_elapsed_us`.
- Section 3 says timestamps are exact UTC microsecond instants and that unknown
  semantics fail closed.
- The packet definition of done expressly requires that event/match clock derivation
  not fabricate an exact occurrence instant.

`eventSec` is a clock within `matchPeriod`. Adding a fixed 45-minute offset to the
second-half clock omits the half-time interval and any first-half stoppage between
kickoff and the second-half restart. Therefore a second-half event cannot truthfully be
assigned that exact wall-clock UTC instant from the declared inputs. This is a
temporal-evidence defect even though the frozen 2020 availability timestamp will
normally dominate W04 feature eligibility.

Bounded correction:

1. Retain `period_code`, exact decimal `period_elapsed_us`, and deterministic
   within-match ordering as provider-relative evidence.
2. Do not expose an exact second-half `event_observed_at` unless a source-backed
   period-start UTC exists.
3. Freeze a precision-aware occurrence representation, such as an explicit
   source-backed interval or `period_relative` precision state. Define how that
   representation feeds strict cutoff logic without converting a lower bound into an
   exact instant.
4. Add boundary cases proving that 2H event ordering is deterministic while no
   unobserved half-time duration is invented.

### P1 — `W04-DESIGN-SOURCE-SEAM-01`: proposed durable paths do not match the source adapter

Evidence:

- Section 4.3 proposes
  `objects/<file_id>/<configured_name>` and
  `members/<archive_file_id>/<admitted_member_name>`.
- The current adapter writes `objects/<configured_name>` and
  `archive-members/<admitted_member_name>` in
  `src/scouting/sources/wyscout.py`.
- The current adapter writes its completion payload at
  `completion-manifest.json`, whereas Section 4.3 proposes layer manifests under
  `data/manifests/wyscout/v5/<layer>/<content_digest>.manifest.json`.

No alias or resolution rule reconciles these layouts. A Bronze reader implemented from
R2 would look for paths that acquisition does not create. This fails the packet's
physical-path compatibility requirement and blocks an end-to-end rebuild.

Bounded correction: choose one exact durable source layout, update either the design
or a separately reviewed source packet, and specify the completion-manifest-to-layer-
manifest relationship. The downstream boundary should consume paths recorded by the
accepted acquisition manifest rather than reconstructing a second path convention.

### P1 — `W04-DESIGN-MANIFEST-BRIDGE-01`: `source_manifest_id` has no defined producer

Evidence:

- Bronze, every Silver row, Gold, identity lineage, and the deterministic rebuild all
  require a canonical UUID `source_manifest_id`.
- `SourceSnapshotManifest` requires a manifest UUID plus tenant context, trace,
  classification, file evidence and coverage.
- The Wyscout adapter currently returns the SHA-256 of a provider-specific completion
  document. That document does not contain a `manifest_id`, tenant context, trace ID,
  `DataCoverage`, or a mapping to the strict `SourceSnapshotManifest` classification.
- R2 supplies neither a deterministic ID derivation nor an explicit construction
  boundary.

Implementers would have to invent the principal lineage identity or use the completion
SHA where a canonical UUID is required. That prevents exact lineage reconciliation and
historical lookup by manifest ID.

Bounded correction: define one serial, reviewed manifest-admission step. It must state
how the provider completion document becomes a strict `SourceSnapshotManifest`, how
its UUID is derived or allocated, which immutable digest it binds, how tenant/trace and
coverage are supplied, and which single manifest artifact downstream products read.
Avoid a circular ID where the UUID depends on bytes that themselves contain the UUID.

### P1 — `W04-DESIGN-REBUILD-CLOCK-01`: generated timestamps contradict byte determinism

Evidence:

- Section 3 requires identical inputs and versions to produce byte-identical semantic
  outputs.
- Bronze includes `generated_at`, all Silver rows include `generated_at`, and Gold
  includes `generated_at_ts`.
- Section 11 says semantic digests exclude `generated_at` and operational metadata is
  put in a separate receipt, but the schemas still place generated timestamps inside
  the products being rebuilt.
- Section 11 also uses `<build_id>` in physical paths without defining it as a stable
  function of the rebuild input.

Two runs using truthful wall-clock generation times cannot produce byte-identical row
payloads or Parquet files. Excluding a field from one digest does not make the
serialized product deterministic, and a run-derived build ID can also change the
physical manifest references.

Bounded correction: remove run-clock fields from semantic Bronze/Silver/Gold payloads
and keep them only in a separately compared operational receipt, or freeze a declared
generation instant as an input with explicit semantics. Define `build_id` as a stable
content identity. State separately whether the gate compares canonical semantic
digests, physical Parquet bytes, or both, and configure the writer deterministically
for any claimed byte comparison.

### P1 — `W04-DESIGN-POSSESSION-AUTHORITY-01`: the possession taxonomy is referenced but not frozen

Evidence:

- Section 8 depends on an event/subevent/tag mapping to `CONTROL`, `CONTESTED`,
  `DEAD_BALL`, `RESTART`, and `NON_CONTROL_ADMIN`.
- Section 12 schedules possession implementation “after 5B and reviewed taxonomy
  map”, but there is no preceding taxonomy-map packet, exact path, schema, version,
  digest rule, or listed owner.
- W04.4 in the controlling workflow requires possessions and reconciliation; W05 then
  expects possession-adjusted features.

The state machine cannot be implemented reproducibly from category names alone. With
no authoritative mapping, an implementer must either guess football semantics or mark
everything unmapped, neither of which proves the intended W04 possession product.

Bounded correction: add a serial, master-owned taxonomy authority packet before action
and possession implementation. Freeze the exact ID-to-class mapping, handling of every
reviewed subevent/tag combination, tie/dead-ball attachment rules, schema version,
canonical digest, unknown behavior, and synthetic challenge cases. If possession must
remain unavailable for this POC, narrow W04 and the W05 feature promise explicitly
rather than implying a reviewed map exists.

### P2 — `W04-DESIGN-GOLD-GRAIN-01`: Gold omits role context from its grain

Evidence:

- The controlling blueprint defines Gold as player × window × role-context rows.
- R2 Section 9.1 defines a uniqueness key with player, competition, season, window,
  cutoff and lineage, but no role-context identity or version.
- The schema contains only `role_context_state=unavailable_until_w05`.

A state flag does not distinguish role-context rows and does not satisfy the approved
Gold grain. It also leaves W05 unable to tell whether it is enriching an unscoped W04
row or replacing its identity.

Bounded correction: introduce a versioned, deterministic neutral W04 role-context
identity in the logical key and document how W05 expands or supersedes it, or obtain a
master-approved narrowing of the Gold grain. Do not use a nullable/implicit role
context as a hidden uniqueness rule.

### P2 — `W04-DESIGN-MINUTES-01`: match-end and minutes semantics are not executable

Evidence:

- Lineup substitutions have defensible minute intervals, but unchanged starters and
  late substitutes need a terminal match boundary.
- Section 7.5 says maximum event time is only a lower bound and an unprovable final
  boundary makes minutes an unavailable interval.
- Gold nevertheless exposes `minutes_lower`/`minutes_upper`, and W05's accepted model
  ladder depends on per-90 features.
- No stoppage/minutes convention, terminal-evidence rule set, interval aggregation
  algorithm, or Gold eligibility threshold is frozen.

Different agents could legitimately produce null minutes, nominal 90-minute values, or
event-max lower bounds. Those are materially different products and gates.

Bounded correction: freeze the first-pass minutes convention separately from exact
wall-clock occurrence. Define terminal evidence, nominal versus elapsed minutes,
lower/upper aggregation over stints, treatment of missing upper bounds, match/player
eligibility, and reconciliation totals. If Wyscout cannot support the required
denominator, explicitly suppress per-90 W05 features.

### P2 — `W04-DESIGN-COVERAGE-01`: coverage and applicability formulas are underspecified

Evidence:

- Gold lists six ordered coverage dimensions plus `coverage_overall`,
  `missing_dimensions`, and `applicability_state`.
- The gates name some zero/100% invariants but do not define denominators, weighting,
  the overall aggregation, or the exact transition to `w04_data_ready`.

This is deterministic within one implementation but not reproducible from the design,
and it prevents an independent verifier from recomputing the gate.

Bounded correction: freeze each numerator/denominator, zero-denominator behavior,
overall aggregation, missing-dimension rule, and the exact applicability decision
table. Coverage must remain descriptive; a weighted overall must not waive mandatory
identity, temporal, rights, or reconciliation failures.

## Required readback

- **Authority fidelity:** PASS for five admitted plus two directory-only excluded
  members per archive. Excluded payload streams remain unopened and every other member
  fails closed.
- **Generic/Wyscout clocks:** PASS for source release versus acquisition ordering.
- **Event occurrence clock:** FAIL; 2H exact UTC is fabricated.
- **Adapter/path compatibility:** FAIL.
- **Bronze/identity/Silver/Gold lineage:** FAIL at the missing strict manifest bridge.
- **Two-root rebuild:** FAIL because semantic rows retain wall-clock generation fields
  and `build_id` is not defined.
- **Gold grain:** FAIL against the controlling role-context grain.
- **Possession/minutes implementability:** FAIL pending frozen semantics.
- **Local-only/rights boundary:** PASS; no cloud, provider account, deployment,
  external model, or public endpoint is introduced by R2.

## Recommendation

**REWORK.** The archive-scope, source-clock, and duplicate-field R1 defects are closed,
but the P1 findings above meet the packet stop condition. A bounded R3 design can
correct them without changing the approved project root, uv policy, local-only
boundary, or source-rights decision. Independent acceptance should be repeated only
against a stable source-adapter interface after those corrections.

