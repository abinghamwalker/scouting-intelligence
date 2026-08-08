# W10 expert relevance validation and research hardening

- Status: **REWORK — 2026-08-06 presentation-v2 addendum active**
- Authorised: 2026-08-05
- Depends on: accepted and Unicode-corrected W09 historical research workbench
- Formal human gate: required before G-RW4 can pass

## Active addendum

The 2026-08-06 mechanics pilot established that participant presentation v1 exposes minutes and
identity context but not the substantive playing evidence required for a role/style judgement.
Protocol/presentation v1 is therefore withdrawn as authority for formal collection before any
formal session or response occurred. The controlling corrective authority is
`docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`.

W10 is back in `REWORK`. Formal collection is suspended until the addendum's evidence design,
versioned participant bundle, interface, disjoint mechanics pilot, independent review and fresh v2
approval gates pass. The v1 approval and incomplete pilot are retained honestly and cannot unlock
v2 or count toward G-RW4.

## Outcome

W10 builds the measurement layer around the accepted W09 resemblance engine. It must determine,
without changing the frozen baseline after outcome inspection, whether football-domain experts
judge its retrieved players to be meaningfully relevant. W10 also completes the deferred local
runtime host-state hardening retained from W04.

The intended path is:

`frozen real-player queries → blinded expert judgements → deterministic relevance metrics →`
`PASS, FAIL or INSUFFICIENT_EVIDENCE → retained reproducible report`

W10 does not build a recruitment decision system, connect current provider data or promote a
challenger model. A governed expert evidence set and failure taxonomy may support a separately
authorised future baseline/challenger programme with disjoint development and evaluation data.

## Implementation sequence

1. **Preflight and reuse surveys:** reconcile the W09 authority; inspect reusable W06 evaluation
   controls and the W04 host-state backlog; map the simplest W10 study-console seam.
2. **Expert-relevance protocol:** freeze the research question, expert eligibility, query pack,
   presentation rules, rating/abstention semantics, denominators, metrics, thresholds and negative
   result policy before formal responses are accepted.
3. **Study console and persistence:** provide one coherent local browser journey with pseudonymous
   participant identity, progress/resume, immutable submission and completion receipt. Do not
   recreate W08 role switching, revision administration, synthetic personas or manual audit entry.
4. **Relevance evaluation:** compute only preregistered metrics, agreement and subgroup evidence;
   retain missingness, abstentions and negative results; return exactly PASS, FAIL or
   INSUFFICIENT_EVIDENCE.
5. **Runtime host-state hardening:** make incidental cache and filesystem metadata audit-only where
   it has no executable or product authority, while retaining fail-closed W04 source, executable,
   product, rights, identity and temporal controls.
6. **Integrated verification and independent review:** verify contracts, browser journey, storage,
   concurrency, replay, protected-label separation, metrics, claim boundaries and the complete
   repository before any accepted W10 checkpoint.

The master may decompose these objectives into smaller path-disjoint packets. Packet numbering is
an orchestration detail; it does not create additional product authority.

## Protocol freeze and human approval

Engineering may prepare a digest-bound protocol and query pack without human responses. The formal
study cannot begin until the user approves a concise decision page that states:

- expert eligibility and required participant population;
- frozen query and candidate counts;
- expected participant time;
- rating, confidence and abstention semantics;
- control/blinding design;
- retained data and privacy treatment;
- metrics, denominators and PASS/FAIL/INSUFFICIENT_EVIDENCE rules.

Counts and thresholds are not authorised by this architecture document. They belong to the frozen
protocol and must be justified before the first formal response. They must not be selected or
changed after inspecting formal outcomes.

Approval binds one exact presentation as well as the protocol and query pack. An approval of a
superseded presentation cannot authorise a corrected version. A mechanics-pilot finding may stop
collection before formal evidence and require a new version and approval; it must never silently
mutate the approved authority.

## Mechanics pilot versus formal evidence

A bounded mechanics pilot may verify the console, wording, progress, persistence and recovery with
fewer queries or test participant records. Pilot state must be physically or logically separate
from formal state and can never count toward G-RW4.

Only real, eligible human expert responses bound to the approved protocol, frozen query pack and
exact W09 dataset/matrix/index authority may enter the formal G-RW4 result. The user's successful
informal W09 browser walkthrough is retained as product smoke feedback, not expert relevance data.

A mechanics pilot must also prove that a participant has enough football evidence to answer the
question. Identity, competition, team, position and minutes alone are insufficient. Presentation
v2 must follow the evidence and blinding contract in the active addendum before another pilot or
formal study begins.

## Gate semantics

- **PASS:** every preregistered positive condition is satisfied by complete eligible formal
  evidence.
- **FAIL:** complete eligible formal evidence fails one or more preregistered positive conditions.
- **INSUFFICIENT_EVIDENCE:** participation, coverage, agreement, completion or another declared
  denominator condition is inadequate for either positive or negative adjudication.

A poor result is evidence, not an implementation failure. Pilot success, synthetic tests and a
working console cannot produce a formal PASS.

## Checkpoint semantics

- Start: `checkpoint/w10-start`
- Engineering-ready milestone: `checkpoint/w10-engineering-ready`
- Accepted W10 checkpoint: `checkpoint/w10-accepted`

The engineering-ready milestone may be created after implementation, verification and independent
review when human participation remains. It does not close W10 or pass G-RW4. W10 may be marked
CHECKPOINTED/CLOSED only after the formal tri-state result, runtime-hardening gate, complete
verification and independent review are retained. W11 must not begin before that closure.

## Planning estimate

The historical v1 engineering-ready estimate has been superseded by the active addendum. The v2
corrective estimate is 16–30 engineering hours plus normally one working day for its separate
evidence-sufficiency pilot, subject to reviewer availability. Formal study calendar time is
additional and remains governed by the freshly approved participant/query design.

## Non-authority

W10 does not authorise provider/network access, credentials, cloud services, deployment,
publication, current-market coverage, recruitment recommendations, future-performance/value/
availability/fit claims, W08 reactivation or learning from protected formal-study labels. Those
changes require their own explicit authority and, where applicable, disjoint model-development and
protected-evaluation partitions.
