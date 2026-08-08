# W09 semantic-uplift preregistered baseline

Status: **FROZEN BEFORE METHODOLOGY CHANGE**

This record freezes the Package A comparison authority before the feature predicate is changed.
It is engineering and ranking-sensitivity evidence only. It contains no expert-relevance labels
and supports no football-relevance or recruitment claim.

## Authority

- Configuration: `configs/evaluation/w09-semantic-uplift-evaluation-v1.json`
- Configuration digest: `6340ec28d24150b3fe16174fb01c07c383119331f622fe6b9fad3582eb602fb6`
- Machine-readable baseline: `reports/verification/W09/uplift-semantic-baseline-v1.json`
- Baseline evaluation digest: `8f9f7ebde22029912483a9ea54e5f9d127d713419a5fe5c9f46e08d78e755429`
- Query cases: 12
- Matrix: `w09-historical-player-window-v1-ad74298cf718d6f6`
- Matrix digest: `49bf6f72d2e564fa5c421c2eb36f70ceb57810a44c1442da9e14a3db6b799bb9`
- Index manifest digest: `f4a9e692336d152938319193a5f5c7cf28cb406da4aa71ca881eae5e0c8fe7c0`
- Scorer digest: `535e244720b7abd46ac25e7de6f3ac387247d4213a00b4857e08acc19e19fc1c`

## Frozen semantic counts

The current matrix has 9,436 goal numerators: GK 4,738, DF 532, MD 1,508 and FW 2,658.
The retained-source audit records 4,741 event-9 save-attempt rows inside that total. Package A must
produce exactly 4,695 non-event-9 goal numerators. The event-10-only negative control would retain
only 4,177 and incorrectly lose 518 retained set-piece goal rows.

## Frozen representative evidence

Every case uses the explicit target position and a 900-minute lower-bound floor. Candidate counts
are Sirigu 23, Van Dijk 123, Kanté 123, Salah 59 and Messi-to-France 72 for both methods.

- Sirigu Euclidean begins Perin, Strakosha and Donnarumma. The goal-term squared-distance shares
  for those three are 40.84%, 36.23% and 68.45%; among the top ten the median is 68.84%.
- Van Dijk Euclidean begins Koscielny, Vertonghen and Mustafi.
- Kanté equal-weight Euclidean begins Doucouré, Cook and Sissoko.
- The frozen defensive reweight uses attack weights 0.5 and defensive-event weights 1.5. It retains
  8/10 equal-weight Euclidean names and introduces Matić and Dier.
- Salah Euclidean and cosine both rank Agüero first.
- Messi-to-France Euclidean begins Thauvin, Neymar, Depay, Mbappé and Malcom.

Exact ordered candidates, query/result digests, population reconciliation, scores and goal
contributions are retained in the machine-readable baseline.

## Frozen rejection rules

- Post-uplift goal numerators must equal 4,695 and contain no event-9 save-attempt evidence.
- Canonical authority, population, eligibility, catalogue, minutes and every non-goal feature value
  remain unchanged.
- Each non-GK scenario/method/weight-profile must retain at least 8/10 names. This is a churn guard,
  not a relevance threshold.
- Candidate admission counts, explanation reconstruction, deterministic artifacts, report bytes,
  exact pin compatibility and local-only checks remain green.
- No W10 threshold moves, no human evidence is consulted, and no result is selected because its
  names look preferable.

Failure of any rule rejects the live method change while retaining this baseline and the negative
result. W10 remains `REWORK`, 08E/08F remain unstarted and G-RW4 remains
`INSUFFICIENT_EVIDENCE`.
