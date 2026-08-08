# W10 expert-relevance study console

> **Post-verification disposition, 2026-08-06:** the v1 mechanics pilot showed that the console
> withheld substantive playing evidence as well as protected provenance. No formal response was
> collected. V1 is suspended pending the evidence-presentation v2 addendum.

> **Presentation-v2 disposition, 2026-08-06:** 08C is accepted after master A4 verification and
> fresh bounded pre-pilot reviews with no open P0-P3. The separate five-task v2 mechanics pilot is
> prepared but has no human session or response. Formal v2 remains disabled.

Status: **V2 A4 VERIFIED — PILOT_READY — HUMAN REVIEWERS REQUIRED**

## Presentation-v2 pilot boundary

The local v2 app exposes only `/w10/v2` on loopback port 8771. Its prepared pilot authority contains
five symmetric side-by-side comparisons covering GK, DF, MD defensive, MD shooting and FW. The
interface presents exact W09 inputs separately from independent evidence, records sufficiency and
assessment basis, and hides protected retrieval provenance. The operator-only separation authority
reserves all pilot players and grains out of the future formal pack.

No v2 database, participant session, judgement or completion exists at this checkpoint. The exact
human procedure and GO/REWORK rule are retained in
`reports/verification/W10/v2-mechanics-pilot.md`. At least two authentic eligible football-domain
reviewers must complete it before any A6 freeze or 08F review.

## Historical v1 participant journey

The local `/w10` console presents one decision page and two physically separate lanes:

- a 22-presentation mechanics pilot that can never create formal evidence; and
- an 82-presentation formal lane bound to an explicit human approval, five or more eligible
  experts, 80 primary judgements and two delayed blinded repeats.

The participant supplies only a pseudonymous code. Eligibility, consent, conflict declaration,
progress, responses and completion state are persisted in local SQLite. The browser receives an
opaque HttpOnly capability, never a participant identity, rank, retrieval score, candidate origin,
W09 grain identifier or expected result. Both the Host header and the actual transport peer must
be loopback. Forms are CSRF-bound, byte-digested, allowlisted and revision checked.

Formal repeat anchors are exact frozen participant-safe candidates. Their schedule is bound into
the participant-presentation digest and derived from the participant-code digest plus session UUID.
Their tasks are interleaved, nonadjacent, at least ten primary presentations after their anchors
and never terminal, so ordinal 81/82 does not reveal repeat identity. The evaluator reconstructs
and compares all 82 presentations exactly before metric access. The review page exposes only
blinded assessment ordinals and response values. Before sealing, a participant may make
corrections; every correction is an append-only SQLite revision linked to the superseded judgement
digest. The final submit is immutable and idempotent.

## Evidence separation

- Pilot captures live only under the pilot/test-only namespaces and carry
  `formal_evidence_recorded=false`.
- Test-only formal captures cannot create `FormalStudySubmission` or formal completion receipts.
- A real formal store writes canonical immutable submissions and receipts only after the exact
  approval and all 82 explicit responses.
- Formal evidence export rejects pilot and test-only stores.
- No real approval, formal participant session, formal submission or mechanics-pilot result was
  created during W10 engineering verification.

## Verification

The focused W10 contracts, evaluator, store, web and Playwright suite passed 54/54 after
independent-review remediation. It covers resume, idempotency, concurrent submit, replay
rejection, strict form shape, actual-peer loopback rejection, narrow-screen accessibility,
append-only correction history, pilot/formal isolation, exact keyed/interleaved repeats and seven
distinct schedule-substitution failures.

At the historical v1 engineering checkpoint, the stated remaining action was formal approval and
expert recruitment. That path is superseded. The current human action is only the separate v2
mechanics pilot; formal approval and recruitment remain prohibited. The formal evidence state is
still `INSUFFICIENT_EVIDENCE`.
