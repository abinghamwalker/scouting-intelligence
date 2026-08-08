# W10 expert-relevance protocol verification

> **Post-verification disposition, 2026-08-06:** protocol/presentation v1 is retained but
> withdrawn before formal collection after the mechanics pilot found insufficient participant
> playing evidence. See `docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`.

- Verification date: `2026-08-05`
- Protocol version: `w10-expert-relevance-protocol-v1`
- Protocol digest: `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`
- Query-pack version: `w10-frozen-query-pack-v1`
- Query-pack digest: `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`
- Participant presentation version: `w10-expert-study-presentation-v1`
- Presentation digest: `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`
- Approval state: **frozen draft awaiting explicit human approval**
- Claim boundary: football relevance of historical resemblance only; never recruitment advice

## Frozen authority

The protocol, evaluator-only query pack and participant-safe presentation are canonical JSON
artifacts under `configs/evaluation/`. The builder reconstructs all three from the accepted W09
matrix/index authority and refuses to replace an existing file with different bytes.

The accepted W09 pins include:

- dataset version `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`;
- canonical build digest `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`;
- matrix version `w09-historical-player-window-v1-a31511705ac15a5d`;
- matrix digest `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1`;
- matrix manifest digest `dda2588f7ad81443aac614a359fbda1fcb60e533ca0d56db5d59e4669a754692`;
- index manifest digest `30c2b6c1e0d65c8214860131f690b8b6cac05fe317ffa208a2785e11160eb0bc`.

The builder executes the accepted W09 weighted-Euclidean scorer over all 16 frozen features with
equal weights. It changes neither the W09 scorer nor any accepted W09 artifact.

## Query and control design

The pack contains eight real historical exemplars and exactly two queries for each of `GK`,
`DF`, `MD` and `FW`. It covers all five retained competitions, four lower and four higher
1,800-minute evidence bands, and four preregistered straightforward plus four difficult cases.

Each query contains:

- the accepted W09 top five same-competition, same-position retrieved rows;
- five governed controls selected without replacement from the same competition and position;
- a control at each rank whose frozen minute/evidence band matches the retrieved row at that rank;
- canonical salted-hash control selection independent of W09 score;
- no synthetic rows.

The protected query pack retains origins, ranks, scores and W09 identifiers for evaluation. The
exact W09 request digest, result UUID, result digest and generation time are bound per query. The
physically separate participant file retains only the scientifically necessary historical player,
competition, team, position and minute context plus opaque study UUIDs. It contains no origin,
rank, score, control rule, W09 player/grain/competition identifier, evidence band or difficulty.
The two frozen opaque repeat-anchor candidate UUIDs are included so the web process can construct
the exact formal task roster without reading the evaluator pack. The presentation digest binds the
`w10-participant-keyed-interleaved-v1` schedule rule, ten-primary minimum repeat delay,
nonterminal requirement and nonadjacency requirement. Collection and evaluation independently
invoke the same pure authority derivation from the participant-code digest and session UUID;
terminal, reordered, adjacent, under-delayed, wrong-ID, wrong-reference and
participant-substituted schedules fail closed. Repeat identity is never sent to the browser.

## Participant and judgement design

- Minimum sample: five eligible football-domain experts.
- Eligibility: at least two years in an accepted professional football role and recent player
  assessment within five years; a material displayed-player/club conflict is ineligible.
- Task: rate all 80 primary candidates on relevance `0..4` and confidence `1..5`, with explicit
  `ABSTAIN` and `UNABLE_TO_ASSESS` states and an optional bounded football explanation/category.
- Consistency: two delayed blinded repeats, for 82 total presentations and an estimated 30–35
  minutes per participant. At least 80% of expected repeat pairs must contain two ratings for
  consistency metrics to be authoritative.
- Coverage: all eight queries and all 80 primary candidates remain in denominators; every
  candidate needs at least three non-abstaining ratings.
- Privacy: the participant supplies an uppercase pseudonymous code; only its one-way digest and a
  deterministic UUID are retained. No name or contact field exists.
- Pilot/formal separation: development fixtures, mechanics pilot and `FORMAL_G_RW4` are distinct
  modes. Pilot data can never instantiate formal evidence or unlock the gate.

## Preregistered decision

Candidate mean `0..4` primary ratings are graded gains. Retrieved and control NDCG@5 use their
respective frozen ranks against the ideal top five gains pooled across all ten candidates, with an
unweighted macro mean over all eight queries. A fully rated all-zero query is NDCG `0.0` for both
arms and is retained as complete negative evidence.

`PASS` requires every authority/completion check plus all of:

- macro retrieved precision@5 at least `0.60`;
- macro retrieved NDCG@5 at least `0.65`;
- retrieved-minus-control relevant-rating-rate lift at least `0.20`;
- paired macro NDCG@5 delta at least `0.05`;
- lower bound of the paired 95% query-bootstrap interval greater than `0.0`, using exactly 2,000
  resamples and seed `10202608`;
- mean pairwise ordinal agreement at least `0.40`, defined as mean
  `1 - |rating_a - rating_b| / 4` over concrete same-candidate reviewer pairs;
- repeat mean absolute difference at most `1.0` and repeat within-one-point rate at least `0.80`.

A complete compatible study missing any threshold is immutable `FAIL` evidence. Absent approval,
fewer than five complete eligible experts, insufficient per-candidate/query coverage, fewer than
80% valid rated repeat pairs, or another required metric without a valid denominator is
`INSUFFICIENT_EVIDENCE`. A stale/substituted authority, protected-label leak/reuse or integrity
violation is `FAIL`. No threshold or population can change after formal approval/access, and
protected labels may never train or tune W09.

## Verification performed

`tests/contracts/test_w10_expert_relevance_contracts.py` proves:

- strict parsing and semantic self-digests for all three authorities;
- deterministic reconstruction from the accepted W09 runtime;
- exact query/position/competition/evidence/difficulty balance;
- exactly 40 retrieved and 40 control candidates;
- retrieved/control evidence-band pairing by frozen rank;
- participant-safe/evaluator-only physical separation and forbidden-key absence;
- decision-bearing mutation changes the corresponding semantic digest and stale digests fail;
- the exact participant-keyed schedule is authority-bound and reconstructable before metric access.

Focused result on the frozen draft: `8 passed`.

## Human boundary

No `ProtocolApproval`, formal participant, formal judgement, formal submission or formal result has
been created. `G-RW4-PROTOCOL` remains awaiting the user's explicit approval of the exact protocol
and query-pack digests above. `G-RW4-STUDY` and `G-RW4-RESULT` remain
`INSUFFICIENT_EVIDENCE`; the document and engineering fixtures do not claim football relevance.
