# W10 protected expert-relevance evaluation

Status: **ENGINEERING VERIFIED — NO FORMAL INPUT CONSUMED**

## Frozen authority

- Protocol digest: `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`
- Query-pack digest: `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`
- Participant-safe presentation digest:
  `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`
- Query count: 8; candidate depth: 10; retrieved/control depth: 5/5.

The evaluator revalidates canonical bytes, all W09 pins, approval identity, eligibility, consent,
session/submission chronology, the complete 80-primary/two-repeat presentation roster and every
judgement digest before metric access. It reconstructs the exact participant-keyed schedule from
the frozen rule, participant-code digest and session UUID, then requires byte-equivalent contract
values. Evaluation time cannot precede approval or any included formal submission.

## Preregistered calculation

Primary gains are mean 0–4 expert ratings. Retrieved and governed-control NDCG@5 are calculated
per query against the pooled ten-candidate ideal and macro-averaged over eight queries. Precision
macro-averages the 40 retrieved candidate relevant-rating rates and reports the exact rational
numerator/denominator, including under variable abstention. Lift uses pooled retrieved and control
relevant-rating rates and retains both arms' relevant/rated counts, both resulting rates and the
exact signed reduced fraction of their difference. Positive, zero, negative and unequal-arm
denominator cases are reconstructable from the retained evidence. The paired NDCG delta uses a
deterministic 2,000-resample query bootstrap with seed `10202608` and a paired 95% percentile
interval.

The remaining thresholds are retrieved precision at least 0.60, mean retrieved NDCG at least
0.65, relevant-rate lift at least 0.20, paired delta at least 0.05 with lower bound above zero,
ordinal agreement at least 0.40, repeat MAD at most 1.0 and repeat within-one at least 0.80. At
least 80% of expected repeat pairs must contain two ratings; repeat abstention is not silently
turned into a 100% completion rule. A fully rated all-zero pooled query is retained as complete
negative evidence with both NDCGs equal to zero.

## One-use boundary

Before opening protected input, the runner atomically claims a fixed authority-owned namespace
keyed by protocol, query pack, presentation and approval. Selecting a second empty output
directory cannot reset consumption. The immutable authority claim and receipt bind the aggregate
run, result, report and output receipt. Row labels, ratings and free text are excluded from safe
artifacts, logs and exceptions. A complete threshold miss is retained as `FAIL`; missing
denominators return `INSUFFICIENT_EVIDENCE`.

Synthetic implementation fixtures cover PASS, FAIL, all-zero negative evidence, repeat
consistency, 9/10 valid repeat pairs, insufficient repeat denominator, variable-abstention exact
precision, exact signed lift evidence, seven schedule substitutions, impossible chronology,
deterministic bootstrap, stale authority and two-directory replay. They are tests only and are not
formal G-RW4 evidence.

The pure status route reports `FORMAL_APPROVAL_ABSENT`, creates no claim/run/result/receipt and
accepts no protected-input argument. No formal evaluation ran.
