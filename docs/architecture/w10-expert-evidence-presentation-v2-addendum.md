# W10 addendum — expert assessment evidence and presentation v2

- Addendum ID: `W10-A01-EXPERT-EVIDENCE-PRESENTATION-V2`
- Authorised: 2026-08-06
- Status: **ACTIVE W10 REWORK AUTHORITY**
- Supersedes for human collection: `w10-expert-relevance-protocol-v1` and
  `w10-expert-study-presentation-v1`
- Preserves: accepted W09 retrieval authority, W10 runtime hardening, protected-label separation,
  local-only operation and the non-recruitment claim boundary

## Decision and pilot finding

The first mechanics-pilot session showed the exemplar and candidate name, position, competition,
club and evidenced minutes, but no substantive playing evidence. Minutes establish the amount of
available evidence; they do not describe role or style. An expert therefore cannot make the
intended football judgement from the participant presentation alone.

Protocol v1 was explicitly approved on 2026-08-06, but no formal participant session, judgement,
submission or result was created. The user has withdrawn v1 as authority for formal collection
after observing the mechanics-pilot defect. The incomplete v1 pilot remains retained as product
research evidence and never counts toward G-RW4. The immutable v1 approval is not deleted or
rewritten; it is superseded by this later explicit authority before formal collection.

The defect is construct validity, not cosmetic usability. The participant projection was
correctly blinded to retrieved/control origin, rank, score, repeat identity and expected outcome,
but incorrectly blinded to the football evidence required to assess the stated construct.

## Required v2 research design

The v2 task must let an expert answer: “Is this candidate a credible historical role/style
comparison to the exemplar, given the football evidence presented?” It must not ask the expert to
infer style from exposure, reputation or a model verdict.

Every exemplar and candidate must receive the same participant-safe evidence structure:

1. **Context:** historical season/window, competition, team, declared position and governed
   minutes, including the minute-evidence state and relevant coverage limitations.
2. **Model-input profile:** all 16 W09 per-90 features with football-readable labels, exact values
   and within-position reference percentiles. The interface must identify these as the attributes
   used by the frozen W09 scorer without showing an aggregate distance or recommendation.
3. **Independent descriptive evidence:** position-appropriate descriptors derived from retained
   canonical events but not used by the W09 ranking. The capability inventory must test at least
   action-location/territory, passing distribution, chance creation/shooting, defensive-action and
   goalkeeper-specific evidence. Unsupported descriptors must be marked unavailable, never
   imputed or inferred.
4. **Evidence glossary:** plain-language definitions, denominator, direction, coverage and known
   limitations for every displayed metric or visual.
5. **Assessment basis:** the participant records whether the judgement used the supplied profile,
   prior professional knowledge, both, or remained unable to assess. Evidence sufficiency and
   confidence are retained separately from relevance.

The existing 16 scorer inputs are passes, accurate passes, crosses, smart passes, shots, shots on
target, goals, key passes, assists, duels, duels won, interceptions, clearances, accelerations,
fouls and touches, all per 90 governed minutes. They are necessary transparency, but showing only
them risks a circular “similar because the similarity inputs look similar” evaluation. The v2
primary football-relevance judgement must therefore have independent descriptive evidence or a
recorded professional-knowledge basis. If the retained source cannot support an adequate
position-specific evidence pack—especially for goalkeepers—the affected query population must be
redesigned before v2 approval, not papered over with generic metrics.

## Blinding boundary

V2 continues to hide from participants:

- retrieved versus control origin;
- W09 rank, distance, aggregate similarity score and expected answer;
- control-selection rule, evidence band and frozen difficulty label;
- repeat identity and linkage;
- aggregate or previous-participant outcomes.

V2 must not hide football evidence merely because that evidence makes similarity visible. Both
arms receive the same evidence schema and rendering. No visual may label one player as “closer”,
“recommended” or “better”.

## Phased implementation

| Phase | Work package | Deliverable | Gate to continue |
|---|---|---|---|
| A0 | Suspend and preserve | Stop the v1 service; retain its approval and incomplete pilot; prove zero formal v1 sessions/responses. | Formal collection is technically and procedurally disabled; evidence status is recorded without deletion. |
| A1 | Construct and capability design | Position-by-position assessment rubric plus inventory of every retained field/event needed for model-input and independent descriptors. | A football judgement is answerable for each retained position; unsupported evidence is explicit. If GK evidence is inadequate, redesign or remove GK queries before freeze. |
| A2 | Versioned evidence contracts | Participant-safe v2 evidence bundle, glossary, coverage schema and deterministic builder. Every field states whether it was used by W09 ranking. | Exact reconstruction, lineage, temporal, identity, missingness, substitution and leakage tests pass; v1 bytes remain unchanged. |
| A3 | V2 comparison interface | Side-by-side evidence panels, accessible profile visualisation, value/percentile toggle, definitions, assessment-basis and sufficiency controls. | Desktop/mobile/keyboard journeys work; retrieved/control provenance, scores and repeats remain absent from browser payloads. |
| A4 | Scientific and adversarial verification | Master-rerun tests for circularity, position appropriateness, insufficient evidence, label leakage, chart parity, stale authority and protected evaluation separation. | The bounded verification suite passes before any pilot participant is approached. |
| A5 | Separate mechanics pilot | A new pilot-only query pack, disjoint from the future formal pack, reviewed by at least two eligible domain reviewers. | At least 80% of pilot tasks are assessable from the supplied evidence, median confidence is at least 3/5, and no reviewer reports that minutes/name recognition are the only usable basis. Pilot evidence still cannot enter G-RW4. |
| A6 | Freeze, independently review and approve v2 | Fresh protocol, query pack and presentation versions/digests; refreshed burden and decision page; independent review; explicit product-owner approval. | The independent review has no open finding and the product owner approves the exact v2 digests after seeing the successful pilot report. V1 approval cannot unlock v2. |
| A7 | Formal study and evaluation | Authentic eligible experts complete the newly frozen study; protected v2 evaluator produces one tri-state result. | Required coverage and integrity checks produce retained `PASS`, `FAIL` or `INSUFFICIENT_EVIDENCE`; no outcome-driven tuning occurs. |
| A8 | W10 closure | Updated verification, independent review, phase gate and checkpoint evidence. | `checkpoint/w10-accepted` may be created only after the v2 formal result and all retained W10 checks pass. W11 remains blocked until then. |

## Planned task decomposition

- `W10-V2-EVIDENCE-DESIGN-08A`: construct definition, position rubric and source capability audit.
- `W10-V2-DATA-CONTRACTS-08B`: evidence bundle, glossary, deterministic builder and tests.
- `W10-V2-STUDY-CONSOLE-08C`: participant-safe rendering and response-contract changes.
- `W10-V2-MECHANICS-PILOT-08D`: disjoint pilot pack, pilot execution and sufficiency report.
- `W10-V2-PROTOCOL-FREEZE-08E`: v2 authority, fresh digests and explicit approval boundary.
- `W10-V2-INDEPENDENT-REVIEW-08F`: post-freeze construct, leakage, accessibility and end-to-end review before approval.
- `W10-FORMAL-EXPERT-STUDY-02B-R2`: formal collection only after every preceding gate passes.

Shared contracts, formal authority and evaluator changes remain serial master-controlled work.
Implementation packets may be made path-disjoint only after A1 fixes the evidence contract.

## Verification requirements

The correction must prove all of the following:

- the v1 approval, pilot session and pilot judgements are retained but cannot unlock v2;
- there are no v1 formal sessions, judgements, submissions, receipts or evaluator claims;
- every displayed metric resolves to governed historical evidence and a readable definition;
- raw values, percentiles and visuals reconstruct deterministically from the same versioned rows;
- model-input and independent-descriptor fields are distinguishable in contract and UI;
- a missing or unsupported position-specific descriptor fails visibly and cannot become zero;
- candidate origin, rank, score, repeat linkage and expected result never reach participant bytes;
- pilot and formal query/player authorities are disjoint enough to prevent rehearsal contamination;
- the formal evaluator accepts only the exact v2 protocol/query/presentation/approval chain;
- W09 features, weights, scaler, index and rankings remain unchanged by protected responses.

## Estimate

The bounded engineering estimate is 16–30 hours: 2–4 hours for capability/construct design, 6–10
hours for versioned evidence contracts and derivation, 4–8 hours for the interface, and 4–8 hours
for adversarial tests and independent review. The separate v2 mechanics pilot is normally one
working day subject to reviewer availability. Formal-study calendar time remains additional.

## Non-authority

This addendum does not authorise a new provider, network/credential access, current-market data,
deployment, publication, recruitment recommendation, transfer prediction, outcome claim, model
tuning from W10 labels or W11 start. Any new descriptor must derive from already authorised local
historical source data under explicit versioned semantics and review.
