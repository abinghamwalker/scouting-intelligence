# W10 preflight: expert relevance validation and research hardening

- Date: `2026-08-05`
- Phase: `W10`
- State at preflight: `READY`
- Starting commit: `603cba2c23fc3a5c72f1ccd57073c500ce6a0061`
- Start tag: `checkpoint/w10-start` (annotated; resolves to the starting commit)
- Accepted W09 corrective tag: `checkpoint/w09-unicode-correction-accepted`
- Accepted W09 corrective commit: `04c95ee08a79d3515ba20b20f5085929f16c3fd6`
- Git remotes: none
- Dedicated guard: `caffeinate -d -i`, verified PID `25230`

## Scope and claim analysis

W10 validates whether the accepted W09 historical resemblance rankings are relevant to
football-domain experts. It does not change the W09 feature population, baseline scorer,
index, ranking method, eligibility policy or accepted authority. The protected outcome is
one of `PASS`, `FAIL` or `INSUFFICIENT_EVIDENCE`; a negative result remains valid evidence.

The user's W09 functional walkthrough is retained as **informal product smoke feedback**:
the reported front-end features worked. It is not an expert judgement, is not a participant
record, does not enter any metric denominator and cannot unlock G-RW4.

W10 also implements the retained W04 host-state backlog. Product identities must ignore
incidental inode, timestamp, directory-link-count, empty-directory, temporary-path and
non-authoritative foreign-PYC variation, while source, executable, product-byte, data-rights,
temporal, identity and truthful-completion substitution continues to fail closed.

## Frozen study design proposed for approval

- Formal query set: 8 accepted W09 real-player exemplar queries, two per position group.
- Balance: all four position groups, all five retained competitions, lower and higher
  evidence/minute bands, and four straightforward plus four difficult profiles.
- Candidate depth: 10 blinded candidates per query: 5 accepted W09 retrieved candidates and
  5 deterministic same-position governed controls, interleaved without origin disclosure.
- Repeats: 2 blinded repeated candidate judgements per participant, excluded from retrieval
  quality denominators and used only for within-reviewer consistency.
- Participants: at least 5 eligible football experts; every formal query must have at least
  3 non-abstaining expert ratings for every candidate.
- Estimated participant time: 30–35 minutes for 82 judgements plus eligibility, consent and
  completion review.
- Rating: ordinal relevance `0..4`, confidence `1..5`, explicit `ABSTAIN` and
  `UNABLE_TO_ASSESS`, plus an optional football explanation and governed failure category.
- Relevance threshold: ratings `3` and `4` are relevant for precision/lift calculations.

These values remain a draft until the protocol and query-pack digests are generated and the
user approves the decision page. After approval, any decision-bearing change must create a
new version and digest; the approved formal authority remains immutable.

## Human-evidence boundary

Engineering may produce the contracts, query pack, console, storage, evaluator, fixtures,
replay, security controls and an `INSUFFICIENT_EVIDENCE` no-submission witness. It may not:

1. approve the protocol on the user's behalf;
2. invent eligible experts, consent, judgements, confidence or completion;
3. copy mechanics-pilot responses into formal storage;
4. tune W09 with formal labels or inspect protected expected outcomes in participant views;
5. claim relevance unless the immutable formal result is `PASS` under the approved protocol.

Formal mode remains locked until the user records explicit approval for the exact protocol
and query-pack digests. Real participants then self-attest eligibility and consent using
pseudonymous codes only. Formal submissions are immutable and are evaluated whether positive
or negative.

## Pilot versus formal separation

| Property | `MECHANICS_PILOT` | `FORMAL_G_RW4` |
| --- | --- | --- |
| Purpose | Test forms, resume, duplicate handling and accessibility | Produce protected expert relevance evidence |
| Participants | Clearly synthetic pilot codes allowed | Real eligible football experts only |
| Query scope | Smaller explicit subset | Exact approved frozen query pack |
| Persistence | Dedicated pilot SQLite and pilot receipt root | Dedicated formal SQLite and content-addressed formal evidence root |
| Gate authority | None; evaluator must reject | Eligible only when protocol/query/W09 pins and approval match |
| UI label | Persistent mechanics-only warning | Formal protected-study warning and approval identity |

`DEVELOPMENT` fixtures are test-process values only and are rejected by both operational
stores as gate evidence.

## Data flow

```text
accepted W09 matrix/index/pins
  -> deterministic query-pack builder
  -> canonical protocol + frozen query-pack digests
  -> user approval bound to both digests
  -> local participant eligibility/consent
  -> blinded query/candidate presentation
  -> immutable formal submission + completion receipt
  -> deterministic evaluator and subgroup/denominator report
  -> PASS | FAIL | INSUFFICIENT_EVIDENCE
```

No step reads a provider over a network, discloses retrieved/control origin to participants,
or changes the accepted W09 model/index.

## Threat model

| Threat | Required control and witness |
| --- | --- |
| Pilot/synthetic evidence promoted as formal | Separate modes, stores and roots; mode-literal contracts; evaluator rejection |
| Stale protocol/query or substituted W09 authority | Exact semantic digests plus all corrected W09 pins; fail-closed load and submission |
| Threshold selection after results | Thresholds inside approved protocol digest; evaluator consumes, never accepts overrides |
| Protected-label tuning/leakage | No training import/path; no expected result in UI/API; result partition immutable |
| Candidate-origin cueing | Blinded interleave; provenance retained only in protected query pack/evaluator |
| Fabricated or duplicated participants | Pseudonymous codes, eligibility attestations, one immutable formal submission per participant/protocol; deterministic retry |
| Concurrent/double submission | SQLite immediate transaction, uniqueness constraints, idempotent byte-identical retry, conflict on mismatch |
| Post-submit mutation | Append-only tables/triggers and content-addressed guarded bytes |
| Missingness hidden by aggregates | Participant/query/candidate denominators, abstentions and missing fields retained explicitly |
| Privacy overcollection | No names, emails, clubs or free-text identity requirement; pseudonymous code and minimum eligibility facts |
| Unsupported recruitment claim | Exact claim-boundary literals in protocol, UI, result and reports |
| Host metadata reopens W04/W09 | Audit-only inventory projection distinct from security/product digest projection |
| Source/executable/product substitution hidden as metadata | Authority-class allowlist; executable/source/product byte checks and W04 zero-read/use witnesses remain fail closed |

## Dependency-ordered execution graph

1. `W10-PREFLIGHT-00`: authority, reuse surveys, scope, threat model, data flow and matrix.
2. `W10-EXPERT-RELEVANCE-PROTOCOL-01`: master-owned shared contracts, protocol, frozen
   query pack, semantic digests and user decision page.
3. `W10-EXPERT-RELEVANCE-STUDY-03`: master-owned migration plus path-scoped operational
   persistence, immutable receipts and stale-authority rejection.
4. `W10-RELEVANCE-EVALUATION-04`: deterministic metrics, agreement, subgroup denominators,
   three-way gate and content-addressed result/replay.
5. `W10-EXPERT-STUDY-CONSOLE-02`: local browser journey against frozen contracts and store;
   pilot and formal mode remain visibly and physically separate.
6. `W10-RUNTIME-HOST-STATE-HARDENING-05`: independent W04 runtime seam and regression
   fixtures; may run in parallel only after its survey confirms no shared W10 contract paths.
7. `W10-INTEGRATED-VERIFICATION-06`: focused, full, browser, security, concurrency,
   mutation, replay and W04 witness verification.
8. `W10-INDEPENDENT-REVIEW-07`: genuinely fresh reviewer; every P0–P3 finding is fixed or
   retained as a genuine user/external blocker.

The master owns all contracts, migrations, query/protocol freezing, orchestration authority,
evidence integration, dependency decisions and Git operations. Implementer write scopes are
path-disjoint and subagents may not self-approve or run Git.

## Evidence and acceptance matrix

| Gate | Engineering evidence | Human evidence | Honest pre-study state |
| --- | --- | --- | --- |
| `G-RW4-PROTOCOL` | Versioned parsed protocol, frozen real query pack, mutation digests, leakage controls | User approval binds exact digests | Awaiting user approval |
| `G-RW4-STUDY` | Console, eligibility/consent, immutable formal store, replay and pilot separation | At least 5 eligible real experts and coverage rules | `INSUFFICIENT_EVIDENCE` |
| `G-RW4-RESULT` | Deterministic metrics/report and three-way decision | Completed accepted formal submissions | `INSUFFICIENT_EVIDENCE` |
| `RUNTIME-HARDENING` | Portable host variants plus every protected W04 substitution/zero-read witness | None | Must pass before engineering checkpoint |

## Preflight stop decision

No data-rights, dependency, user-change, remote, credential, destructive-action or product
conflict was found. W10 engineering may proceed. The only expected human boundary is exact
protocol approval followed by real football-expert participation.
