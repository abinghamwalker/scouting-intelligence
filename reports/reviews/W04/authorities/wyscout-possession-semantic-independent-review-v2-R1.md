# W04 Wyscout possession-semantic v2 independent review R3

## Recommendation

`PASS`.

I found zero P0, P1, or P2 findings in the frozen R21 possession-v2 authority
after the bounded R4 correction. The candidate is internally closed, preserves
all accepted possession-v1 predicate semantics, applies the strict four-field
selector boundary, resolves same-period sequences deterministically, and uses
the sole fixed R21 review route with fail-closed progression.

This is an independent review recommendation only. It does not accept the
candidate, create possession-v2 acceptance, dispatch feature authority, or
authorize Bronze, Silver, Gold, build, model, or product work.

## Fixed reviewed authority

- review ID: `w04-wyscout-possession-semantic-independent-review-v2-R1`
- reviewer actor: `b4b3e91b-d13b-53c4-95d4-a6019f6faa98`
- decision ID: `w04-wyscout-possession-semantic-decisions-v2`
- decision physical and canonical SHA-256:
  `8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425`
- candidate ID: `w04-wyscout-possession-taxonomy-v2`
- candidate physical SHA-256:
  `24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187`
- candidate parsed canonical JSON SHA-256:
  `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`
- focused executable contract SHA-256:
  `dd4167747b71203390ba04d7c0899dc98099e203368ba5b3c3942b1b9a6e3116`
- decision time: `2026-07-30T22:14:21Z`
- review time: `2026-07-31T08:24:02Z`

The reviewer actor is a canonical RFC 4122 UUIDv5 and differs from the master
decision actor `4efe5691-8903-5148-8275-30d2e7e8aed0`. The review clock is
fresh canonical UTC and is later than the decision clock.

## Independent authority reconstruction

I read the complete immutable R20 and frozen R21 design authorities, the R15
independent design review, the accepted field-v2 and possession-v1 authority
chains, both possession-v2 structured artifacts, both possession contract
files, the corrected producer return and master evidence, both earlier failed
review generations and their master evidence, the R3 packet, and the return
template.

Independent reconstruction established:

- exactly five bound inputs, equal to the frozen event/tag evidence and accepted
  field-v2 registry and acceptance evidence;
- exactly seventeen prior-authority members, equal to the accepted
  possession-v1 record plus its required physical and canonical acceptance
  digests;
- exactly ten decision keys and nine candidate keys;
- an exact decision-to-candidate restatement of source, bound inputs, prior
  authority, policies, and predicates;
- all 36 predicates byte-semantically equal to possession v1 and in the same
  order;
- four contested, eleven control, eight dead-ball, two
  non-control-administration, seven restart, and four unmapped predicates;
- eighteen `ACTION_TEAM` and eighteen `NONE` control-team-source predicates;
- physical and parsed canonical digests equal to the fixed values above.

The candidate and decision form an acyclic digest contract: the candidate binds
the physical decision digest, while canonical candidate identity is computed
from the complete parsed candidate. No artifact is required to embed its own
digest or a digest whose preimage recursively includes that digest.

## Selector challenge

The selector reads only:

- `action_event_taxonomy_id`
- `action_subevent_taxonomy_id`
- `action_team_source_id`
- `action_tag_ids`

I independently exercised all 36 exact event/subevent pairs and reproduced each
unchanged v1 predicate. Every non-`UNMAPPED` row produced only
`PREDICATE_ADMITTED`; the four explicit `UNMAPPED` rows remained
`PREDICATE_UNMAPPED`. Predicate lookup never emitted final possession
eligibility.

Independent negative challenges confirmed that missing fields, booleans,
strings, numeric-looking strings, non-integers, unknown pairs, absent or
mistyped tags, boolean/string tag members, duplicate or unsorted tag arrays,
missing or invalid required teams, missing required tags, and present forbidden
tags fail closed. Raw event/subevent fields, rejected values, names, labels, and
unrelated fields cannot influence predicate selection. No string value is
coerced to an integer.

## Same-period sequence challenge

I reconstructed the exact scope
`(action_match_source_id, action_period_code)` and exact order
`(period_rank, period_elapsed_seconds, source_record_ordinal,
source_event_record_id)`.

Executable challenges confirmed:

- control opens a scope-local possession;
- same-team control continues it;
- opposing-team control opens a new possession;
- restart closes and opens a new possession;
- predecessor-attached dead-ball actions attach once to the last resolved
  possession and close active control when specified;
- contested actions configured for following attachment buffer only until the
  next resolved possession in the same period;
- administration and unmapped actions remain unassigned;
- cross-team control at an equal clock is an uncertain boundary and remains
  unassigned;
- period closure drops active and buffered state, forbidding cross-period
  attachment;
- invalid context and duplicate ordering contexts fail closed;
- duplicate source record IDs are rejected;
- final `ELIGIBLE_RESOLVED` appears only after exactly one possession
  assignment.

I additionally evaluated all 24 input permutations of a four-action,
two-match/two-period fixture. Complete per-record results and scope-local
possession IDs were invariant in every permutation. A cross-team equal-clock
boundary cleared prior active state, and the next resolved control opened the
next ordinal deterministically.

## Progression and boundary challenge

The fixed current path and ID ending in `v2-R1` are the sole R21 review route.
The two exact earlier failed review generations were verified with their
corresponding returns from master-supplied operational evidence:

- failed R1 review SHA-256:
  `71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a`
- failed R1 return SHA-256:
  `fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90`
- failed R2 review SHA-256:
  `609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a`
- failed R2 return SHA-256:
  `974d8418a7408eca3be338b0f8ae9211fb5df37eb9827c70251843051d404a23`

Only those two exact historical physical hashes are treated as transitional
non-authority. Every other present review byte sequence follows normal strict
validation: malformed fences, noncanonical records, wrong clocks, non-UUIDv5
actors, self-review, wrong digests, incorrect IDs, recommendation/finding
inconsistency, and unknown invalid bytes fail closed. Valid fixed-route `PASS`
and `REWORK` reviews enter their corresponding review state. Acceptance remains
separately master-owned and must bind the exact review physical and record
digests, candidate and decision digests, UUIDv5 master actor, clock order,
recommendation, and possession-v1 supersession.

No possession-v2 acceptance or later authority exists in this review scope.
Every enumerated product path remains absent. The repository local-only,
single-root-uv, container-free boundary passed without a remote, hosted CI,
cloud service, public endpoint, or deployment.

## Verification evidence

The independent reconstruction challenge passed for all 36 selector
predicates, strict negative cases, sequence boundary cases, all 24 multi-scope
input permutations, duplicate-ID rejection, exact digests, historical
transition, and unknown-review fail-closed behavior.

The required locked focused suite passed with `332 passed`. Ruff format and
lint checks passed. The local-only verifier passed all 25 checks with no
failure. Every Python command used the root uv environment with `--locked
--no-sync`, `PYTHONDONTWRITEBYTECODE=1`, and bytecode disabled for direct Python
execution.

## Findings and residual risk

- P0: 0
- P1: 0
- P2: 0

No semantic contradiction or broader architecture/product change is required.
Residual risk is limited to later master-owned acceptance and implementation
correctly consuming this authority; those later actions are outside this
review.

## Canonical review authority record

The following is the sole machine-readable authority record in this report. Its
body is strict compact canonical JSON with sorted keys and one terminal LF.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-possession-taxonomy-v2","candidate_physical_sha256":"24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187","candidate_sha256":"3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881","decision_id":"w04-wyscout-possession-semantic-decisions-v2","decision_physical_sha256":"8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425","decision_sha256":"8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-possession-semantic-independent-review-v2-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T08:24:02Z","reviewed_by":"b4b3e91b-d13b-53c4-95d4-a6019f6faa98"}
```

## Conclusion

`PASS`. The corrected possession-v2 authority is fit for master acceptance.
Acceptance and all downstream work remain blocked until the master independently
verifies this exact review and creates the separate accepted authority.
