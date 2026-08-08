# W10 master engineering review

> **Post-checkpoint disposition, 2026-08-06:** a mechanics pilot found that participant
> presentation v1 supplied minutes and identity context but no substantive playing evidence for
> the intended role/style judgement. No formal response exists. This historical engineering-ready
> decision is reopened for bounded rework under
> `docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`; it no longer authorises
> formal v1 collection.

Decision: **ACCEPT FOR ENGINEERING READINESS**

This decision accepts the implemented W10 engineering candidate and authorises only the
`checkpoint/w10-engineering-ready` milestone. It does not approve the human protocol, recruit a
participant, create formal evidence, pass G-RW4, close W10 or authorise W11.

## Finding disposition

- Open P0/P1/P2/P3: `0/0/0/0`.
- The independent review originally identified five P1 and three P2 findings. Bounded remediation
  corrected the retained runtime cache roster, blinded-repeat scheduling, repeat denominator,
  loopback peer enforcement, authority-global one-use claim, chronology, metric evidence and
  pre-submit response correction.
- A first re-review left one P1 schedule-integrity gap and one P2 lift-evidence gap. Candidate
  `f07224c` bound the exact schedule into the frozen presentation, made the evaluator reconstruct
  it, and retained signed exact two-arm lift evidence.
- The final independent re-review accepts the engineering candidate with no open finding at any
  severity.

## Accepted engineering invariants

1. The frozen protocol binds eight real W09 exemplars, 80 primary candidate assessments, five
   retrieved and five governed controls per query, two blinded repeats, expert eligibility,
   completion rules, metrics, thresholds and tri-state decision semantics.
2. Protocol `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`,
   query pack `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`
   and participant presentation
   `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`
   reconstruct deterministically from accepted W09 authority.
3. The participant projection excludes candidate origin, rank, score, evidence band, difficulty
   and internal W09 identities. Collection uses a digest-bound participant-keyed schedule with a
   ten-primary minimum repeat delay, nonadjacent repeats and a primary terminal task.
4. The evaluator reconstructs every formal schedule before metric access, enforces chronology and
   denominators, retains negative outcomes, exposes exact precision/lift evidence, and claims each
   protocol/query/presentation/approval authority once before protected input is opened.
5. Pilot, test-only and formal stores are physically and semantically separated. Formal export
   rejects ineligible evidence; pre-submit corrections are append-only; sealed submissions are
   immutable.
6. The local web boundary requires both loopback transport and an allowed Host. No provider,
   network, credential, remote, deployment or public-serving authority was introduced.
7. Retained W04 runtime controls pass in the naturally materialised W10 repository state. Later
   source-backed bytecode remains audit-only and cannot become executable or product authority.
8. W10 labels have no path into W09 feature construction, retrieval, ranking, serving or model
   selection. The claim remains historical football-relevance research only, never recruitment
   advice or an outcome claim.

## Formal boundary

No human approval or formal study occurred. `G-RW4-PROTOCOL` awaits the user's exact approval;
`G-RW4-STUDY` and `G-RW4-RESULT` are `INSUFFICIENT_EVIDENCE`. The engineering-ready checkpoint is
therefore a truthful pause point. `checkpoint/w10-accepted` must not exist and W11 must not start.

Primary evidence is retained in `reports/reviews/W10/independent-review.md` and the W10
verification reports under `reports/verification/W10/`.
