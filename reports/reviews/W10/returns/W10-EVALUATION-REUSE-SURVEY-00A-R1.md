# W10 evaluation reuse survey and subagent return

## Task

- task_id: `W10-EVALUATION-REUSE-SURVEY-00A`
- objective: Map the accepted W06 evaluation contracts, deterministic metrics, protected-evidence controls, one-use gate behaviour and negative-result retention that W10 should reuse, without opening protected outputs or changing implementation code.

## Files changed

- `reports/reviews/W10/returns/W10-EVALUATION-REUSE-SURVEY-00A-R1.md`

## Summary

- W10 can reuse W06's canonical metric result, interval, access/run lineage, reviewer/rubric/evidence, gate, rank-comparison and failure-register semantics, but it cannot reuse the exact W06 protected preregistration or missing-population broker as a W10 authority. Those objects are deliberately frozen to the W05 candidate, a zero protected population and the 2026-08-04 protocol.
- The accepted W09 research evaluation remains engineering evidence only. It supplies exact replay, explanation, filter, sensitivity and population witnesses, but deliberately contains no relevance label or relevance metric.
- A compatible W10 evaluation should therefore have two explicit lanes: a replayable unprotected engineering lane and a sealed one-use expert-relevance lane. Only the latter may decide a relevance claim, and absent governed expert evidence must remain `INSUFFICIENT_EVIDENCE` with no protected bundle/run or invented metric.
- The authoritative relevance metric remains macro query-level `nDCG@10` against the best preregistered control, with a paired query bootstrap and the W06 minimum-useful-effect rule: point delta at least `0.05` and lower confidence bound greater than `0.0`. Existing W06 calculation code computes arm-level intervals, not the required paired delta interval, so that delta calculation needs a W10-owned contract/function before a positive gate is possible.

## Exact W06 reuse map

### Reuse directly when W10 supplies compatible identities and frozen inputs

From `src/scouting/contracts/evaluation.py`:

- `RubricAuthority`, `ReviewerIdentity`, `EvaluationEvidence`, `PairPreferenceEvidence`, `HardNegativeEvidence`, `Adjudication`, `PartitionMembership` and the associated authority, rights, availability and canonical-order checks. These prevent reviewer/rubric substitution, prohibit unusable rights, reject post-cutoff evidence and require governed humans in governed partitions.
- `EvaluatedQueryRoster`, `MetricResult`, `BootstrapInterval`, `EvaluationAccessRecord`, `EvaluationRun`, `SliceResult` and `FailureResult`. Their digest links bind protocol, input, evaluated-query denominator, candidate manifest, partition, access and run. `MetricResult` also enforces value = numerator / denominator and prevents unavailable results from carrying invented numbers.
- `GateDecision` and `GateDecisionKind` as structural gate semantics. Positive or narrowed decisions require a linked bundle and run, complete primary results and intervals, exact protected-population coverage and governed non-abstaining evidence. A complete negative evaluation may retain both bundle and run; a missing-population negative retains neither.
- `RankComparisonResult` and `derive_rank_comparison` for deterministic label-free rank stability. Top-k overlap, overlap rate, Jaccard, churn and disagreements remain valid even when Spearman is unavailable because fewer than two candidates intersect.
- `FailureCase`, `FailureCaseRegister` and `register_failures` for a worst-first, content-addressed register that retains ten cases or all available cases plus the exact shortfall.
- Canonical content identity semantics from `_digest` and `_sequence_digest`. W10 should expose a public helper rather than making new code depend on private underscored functions.

From `src/scouting/contracts/evaluation_calculations.py` and `src/scouting/evaluation/core.py`:

- `canonical_score`, `derive_ranking_metric_children`, `evaluate_ranking` and `bootstrap_interval` for complete, label-bearing ranking rows. The shared primitive calculation is the accepted cross-surface authority for precision, recall, nDCG, coverage and deterministic query-level percentile bootstrap.
- `rank_comparison` for the label-free rank comparison above.
- `pair_preference_accuracy` and `inter_rater_agreement` only when authentic governed pair/rater evidence exists. They already preserve explicit abstained/missing states, rubric identity and reviewer authority.

From `src/scouting/evaluation/robustness.py`:

- `evaluate_stress_test`, `evaluate_control`, `register_failures` and their embedded-input/digest pattern are reusable only for a label-bearing population that satisfies the current contracts.
- The typed-deficit pattern is reusable: insufficient observations, windows, groups, intersections, coherent labels or common candidates must produce `UNSUPPORTED_INSUFFICIENT_EVIDENCE` without numeric values.
- The complete mandatory-roster pattern is reusable, but the existing `ApplicabilityAssessment` result is not a W10 applicability authority because it is hard-coded to implementation fixtures and missing expert evidence.

From `src/scouting/evaluation/gate.py`:

- Reuse the control pattern, not `broker_missing_population_no_go` itself: caller/preregistration digest equality, no protected-input parameter on the missing-population path, exclusive creation, canonical JSON bytes, file SHA-256s, a receipt that binds the access outcome and gate decision, and refusal when any output already exists.

### Reuse as upstream W09 engineering evidence, never as relevance evidence

From `src/scouting/evaluation/research.py`:

- `research_version_pins` and the frozen suite authority checks bind dataset, canonical build, identity, matrix, feature registry, eligibility policy, model/scorer and index versions.
- `QueryReproducibilityWitness`, `ExplanationConsistencyWitness`, `FilterBehaviourWitness`, `WeightStabilityWitness`, `EvaluationCoverage` and `ResearchRetrievalEvaluationResult` give W10 accepted engineering inputs for deterministic replay, explanation arithmetic, filter reconciliation, bounded weight sensitivity and descriptive population coverage.
- `load_frozen_evaluation_suite`, `run_research_evaluation` and `render_evaluation_payload` provide strict canonical-JSON loading, exact live-authority binding, twice-executed replay and canonical output bytes for the accepted W09 suite.
- Preserve their express boundary: historical resemblance research only; no relevance labels, ranking-quality validation or recruitment-usefulness evidence.

## W06 assumptions that are incompatible with W10 as-is

1. `FrozenW05Candidate` and `FrozenProtectedPreregistration` require one exact W05 artifact and its fixed digests. W10 must bind the accepted historical matrix/index, scorer, query suite, controls and code versions instead.
2. `FrozenProtectedProtocol` fixes the W06 metric roster, seed `20260804`, 2,000 resamples, W05 baselines, minimum effect text, unsupported `k=25` reason and exact fail-closed strings. It is evidence, not a configurable W10 protocol.
3. `GovernedEvidenceInventory` contains literal zeros, and `ProtectedAccessOutcome` admits only `NOT_ACCESSED_MISSING_POPULATION`. They correctly describe W06 but cannot represent a future nonempty W10 protected population.
4. `broker_missing_population_no_go` rejects any nonzero population and can only emit W06's missing-population `NO_GO`. W10 may use it only as the design reference for an absent-population route.
5. W06 `EvaluationProtocol.claim_boundary` is the literal `resemblance_only`; W09/W10 research pins use `historical_resemblance_research_only`. W10 needs one canonical claim-boundary mapping rather than silently treating the literals as interchangeable.
6. `EvaluationQuery` requires a role brief and `EvaluationId`-shaped string identifiers, while the W09 product supports exemplar and weighted-profile queries with UUIDs, grain IDs, filters and `ResearchVersionPins`. W10 needs an explicit immutable adapter or a versioned query contract; IDs must never be lossy aliases.
7. W06's candidate example has only 18 members and therefore marks `k=25` unsupported. W10 must derive supported k values per frozen historical query after exclusions; it must not carry that W05 reason forward.
8. W06 ranking calculations require a complete candidate roster and reject any `UNJUDGED` or `ABSTAIN` label anywhere in the row. This is safe, but a full 1,975-row historical universe is not thereby labelled. W10 must freeze a fully judged evaluation roster/pool before using these functions; it must not treat unjudged players as irrelevant.
9. W06 `coverage@k` is exactly `k / candidate_universe_size`. It is an exposure fraction, not label coverage, population reconciliation or quality. W10 should report it under an unambiguous name and separately report judgement coverage and returned-population coverage.
10. `derive_ranking_metric_children` macro-averages complete per-query values and bootstraps those values. It does not compute a paired challenger-minus-control delta interval. Independent arm intervals do not establish the preregistered lower bound on a paired effect.
11. `evaluate_control` always computes precision, including for metadata, raw-Euclidean and shuffled-label controls. It cannot establish the `nDCG@10` primary delta without a W10 metric-parameterised control result.
12. Label-dependent `StressTestSpecification` and cohort aggregation cannot be used to imply relevance from W09's unlabeled historical ranks. For current engineering stability, reuse label-free rank comparisons or W09 sensitivity witnesses.
13. `ApplicabilityAssessment` is statically `UNSUPPORTED`, `IMPLEMENTATION_FIXTURE_ONLY` and `NO_EMPIRICAL_TRANSFER_OR_EXPERT_EVIDENCE`. That is the correct W06 fixture conclusion, not W10 historical-population applicability.
14. `FrozenResearchEvaluationSuite` fixes W09 version text, timestamps, counts (`1,975` rows, `1,965` players, `3,603` source players, five competitions), limitations and weaknesses. It may be replayed as accepted evidence but must not become a generic W10 protocol or survive a governed rebuild by silently changing constants.

## Proposed authoritative W10 metric system

### Lane A: unprotected engineering evaluation

All thresholds and the exact case denominator must be frozen before execution. These measures support engineering acceptance only:

| Measure | Exact numerator / denominator | Status rule | Claim use |
| --- | --- | --- | --- |
| Query execution rate | frozen cases producing a valid result / all admitted frozen cases | `PASS` only at 1.0; execution or contract error is `FAIL`; zero admitted cases is `INSUFFICIENT_EVIDENCE` | Engineering only |
| Exact replay rate | cases reproducing result ID/digest, candidate order, scores, explanations, population and warnings / all successfully executed frozen cases | `PASS` only at 1.0; any mismatch is `FAIL`; no cases is `INSUFFICIENT_EVIDENCE` | Engineering only |
| Explanation reconstruction rate | returned candidates whose score and every contribution reproduce / all returned scored candidates | `PASS` only at 1.0; any mismatch/missing active feature is `FAIL`; zero returned candidates is `INSUFFICIENT_EVIDENCE` except for an explicitly preregistered empty-admission witness | Engineering only |
| Mandatory filter-witness rate | passed declared witness instances / all declared mandatory witness instances | `PASS` only at 1.0; any failed invariant is `FAIL`; missing witness roster is `INSUFFICIENT_EVIDENCE` | Engineering only |
| Score admission rate | `scored_rows / filter_admitted_rows` per query | descriptive; `filter_admitted_rows = missing_feature_exclusions + scored_rows`; zero denominator is reported as not applicable, never `0.0` | Engineering only |
| Returned matrix coverage | unique returned grain IDs / eligible matrix rows | descriptive, never a relevance threshold | Engineering only |
| Top-k overlap | `|baseline_top_k intersection perturbed_top_k| / k` | computed only when both lists contain at least k unique items; otherwise `INSUFFICIENT_EVIDENCE` | Sensitivity only |
| Top-k Jaccard | `intersection / (2k - intersection)` | same denominator prerequisite | Sensitivity only |
| Candidate churn | `1 - intersection / k` | same denominator prerequisite | Sensitivity only |
| Mean absolute rank displacement | sum of absolute rank changes over the top-k union / union size, assigning absent candidates rank `k+1` | zero union is `INSUFFICIENT_EVIDENCE` | Sensitivity only |
| Spearman rank correlation | W06 canonical formula over the full common-candidate intersection | fewer than two common candidates is `INSUFFICIENT_EVIDENCE`; retain valid top-k set measures | Sensitivity only |

Population counts, unique-player counts, competition coverage, total scored-row evaluations and lower-bound-minute prevalence remain explicit descriptive evidence. No threshold on these quantities is a football relevance claim.

### Lane B: sealed governed expert-relevance evaluation

The proposed primary metric and decision authority are:

- primary: macro query-level `nDCG@10` challenger minus the best preregistered eligible control;
- required effect: paired point delta `>= 0.05` and the lower bound of the preregistered paired 95% query-bootstrap interval `> 0.0`;
- controls: at minimum metadata and raw Euclidean, plus deterministic shuffled-label and shuffled-pair controls when their exact governed evidence exists;
- secondary, non-substituting metrics: `precision@5`, `precision@10`, `recall@5`, `recall@10`, `nDCG@5`, exposure fraction at 5 and 10, pair preference, and agreement when multiple governed reviewers exist;
- exact protected query roster, k values, baseline choice rule, slice roster, seed, resample count, confidence, tie policy, partial-label gain, partial precision/recall policy and missingness policy must be preregistered.

Denominator rules:

1. A query enters any aggregate only if it belongs to the exact frozen protected roster, its candidate/evaluation pool is frozen and unique, and every label needed by the declared missingness policy is concrete and pre-cutoff. No post-access query dropping is allowed.
2. `precision@k`: relevant gain in the first k ranks divided by exactly k. A ranking shorter than k or missing required labels is `INSUFFICIENT_EVIDENCE`, not zero. `PARTIAL` counts only if the frozen protocol says so.
3. `recall@k`: relevant gain in the first k ranks divided by all relevant gain in the fully judged frozen evaluation pool. A zero relevant-gain denominator or incomplete pool is `INSUFFICIENT_EVIDENCE`.
4. `nDCG@k`: discounted observed gain divided by ideal discounted gain from the same fully judged frozen pool. A zero ideal gain or incomplete pool is `INSUFFICIENT_EVIDENCE`.
5. Query aggregation is an unweighted macro mean: sum of valid per-query values divided by the exact frozen query count. If any frozen protected query lacks a required primary result, the aggregate is `INSUFFICIENT_EVIDENCE`; it is not recomputed on the remaining queries.
6. Bootstrap resampling unit is the query. Challenger and control values for a query travel together in every paired resample. The effect numerator is the sum of per-query deltas and the denominator is the frozen protected query count.
7. Pair preference denominator includes only governed non-abstaining preferences with an actual prediction. Any `MISSING` prediction makes the declared metric `INSUFFICIENT_EVIDENCE`; an all-abstain/no-eligible set is also insufficient.
8. Agreement denominator includes only paired concrete labels from two distinct governed reviewers on the same query, candidate and rubric. No eligible paired labels is insufficient.
9. Judgement coverage must be reported separately as concrete, rights-valid, pre-cutoff judgements / required judgements. W06 exposure fraction (`k / candidate-universe size`) must not stand in for it.

### Deterministic `PASS` / `FAIL` / `INSUFFICIENT_EVIDENCE` ordering

Evaluate in this order and stop at the first terminal class:

1. **Integrity and access controls.** A stale/substituted digest, wrong partition, noncanonical or mutable artifact, unauthorised accessor, label leakage, already-consumed invocation, concurrent/replayed invocation, post-cutoff evidence, rights violation, roster mismatch or serving/explanation parity failure is `FAIL`. Seal the failure; do not continue or reopen protected evidence.
2. **Evidence authority and population.** Missing governed reviewer/rubric authority, absent protected population, empty protected query roster, missing required labels/pairs/slices or no valid denominator is `INSUFFICIENT_EVIDENCE`. On an absent-population route, the broker must have no protected-input parameter and must emit no bundle/run or metric.
3. **Primary computation completeness.** Any unavailable primary per-query result, aggregate, paired control result or paired interval is `INSUFFICIENT_EVIDENCE`. Secondary metrics cannot substitute.
4. **Predeclared performance and controls.** With complete valid evidence, failure of the `nDCG@10` point-delta or lower-bound rule, a mandatory null/control, or a preregistered robustness/applicability threshold is `FAIL` and remains retained negative evidence.
5. **Positive decision.** `PASS` is permitted only when every prior prerequisite and all mandatory thresholds pass. Passing engineering Lane A never promotes Lane B from `INSUFFICIENT_EVIDENCE`.

This tri-state vocabulary should map to existing W06 objects without rewriting history: W06's retained missing-population `NO_GO` maps to W10 `INSUFFICIENT_EVIDENCE`, while a complete protected run below threshold maps to W10 `FAIL`. Existing W06 gate artifacts remain unchanged and authoritative for W06.

## Protected-label, one-use, immutability and replay controls

1. Freeze before access: claim boundary, protected roster, candidate/evaluation pools, reviewer roster, rubric, partition membership, source/canonical/matrix/feature/model/index/code pins, baseline and challenger, k, metrics, slice roster, partial-label policy, missingness policy, seed, resamples, confidence, effect threshold and stop rule. Bind all fields in a preregistration digest.
2. Separate processes and interfaces: the normal research service receives no protected label object, path or parameter. The missing-population broker likewise has no protected-input parameter. A nonempty protected broker reads only the sealed protected partition and frozen ranking outputs; it must not call training, tuning or product-serving mutation paths.
3. Minimise outputs: public/review artifacts contain the preregistration identity, access outcome, aggregate/slice statuses, gate decision, reason codes and file/content digests. They do not contain row-level protected labels, reviewer free text or a recoverable label permutation. Logs and exceptions must contain identifiers/digests only.
4. Claim the invocation before opening labels with an exclusive, concurrency-safe marker keyed by preregistration digest, protected-population digest, candidate digest and invocation ID. Any existing full or partial marker means consumed; a crash after claim is a sealed incomplete/negative execution, not permission to rerun.
5. Preserve W06's exact link chain: one-use `EvaluationAccessRecord` consumed by one exact `EvaluationRun`; run binds protocol, bundle, candidate manifest, evaluated roster and protected partition; receipt binds preregistration, candidate, access outcome, gate and file SHA-256s.
6. Write canonical JSON with exclusive creation and verify contract digest plus file digest after write. Never overwrite, update in place or delete a negative result. A partial output set fails closed and requires a separately authorised new preregistration, not cleanup followed by replay.
7. Protected access is not deterministic replay. Unprotected W09/W10 engineering queries may be rerun to prove reproducibility; a protected expert gate is one-use. After the one-use decision, no retuning, control replacement, threshold change, query dropping or rerun is allowed.
8. Retain every negative shape:
   - absent authority/population: evidence inventory + `NOT_ACCESSED` outcome + gate + receipt, with `bundle = null`, `run = null`, no metrics and `protected_outputs_opened = false`;
   - integrity/access failure: consumed marker + sealed failure outcome/reason + receipt, with no further access;
   - denominator insufficiency after authorised access: linked access/run with unavailable metric statuses and reasons, plus an `INSUFFICIENT_EVIDENCE` gate;
   - complete below-threshold evidence: full linked bundle/run, controls, intervals, slices, failures and `FAIL` decision.
9. A later attempt requires explicit new authority, a newly frozen protocol and a new protected partition or prospectively collected evidence. It must never reuse the old one-use invocation or learn from its protected result.

## Tests run

- command: `uv run pytest -q tests/contracts/test_w06_evaluation_contracts.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/unit/test_w06_robustness.py`
  - exit status: `0`
  - result: `20 passed in 0.59s`
- command: `test -s reports/reviews/W10/returns/W10-EVALUATION-REUSE-SURVEY-00A-R1.md`
  - exit status: `0`
  - result: deliverable exists and is non-empty

## Artifacts/evidence

- Survey and handback: `reports/reviews/W10/returns/W10-EVALUATION-REUSE-SURVEY-00A-R1.md`
- W06 retained decision identifier: `missing-population-w06-gate-20260804-missing-population-01`
- W06 retained gate digest: `e9db63fb875fec48223ee7800d5ccbc22a11088e1787773010c82c9217d8be48`
- W06 frozen protocol digest: `b4836c928df5696d1b33e38d25095409958e459d55f92d3928626621e6422217`
- No protected bundle, protected run, protected labels or protected metric was accessed or created by this survey.

## Risks

- W10 cannot make a positive relevance or recruitment-usefulness claim while governed expert labels remain absent. Lane B therefore remains `INSUFFICIENT_EVIDENCE` unless separately authorised authentic evidence is collected and preregistered.
- The accepted W06 code lacks a paired challenger-minus-control interval and metric-parameterised nDCG control result. Reusing independent arm intervals would overstate evidence and is not acceptable.
- Mapping W09 UUID/grain/query identities into W06 `EvaluationId` strings is a substitution risk unless a versioned, reversible adapter is frozen and digested.
- Full-universe label completeness may be impractical. Any smaller judged pool must be frozen prospectively and its applicability narrowed; unjudged candidates cannot be converted to irrelevant labels.
- W09 engineering stability and coverage are sensitivity/descriptive evidence only. They do not validate football relevance.

## Follow-up items

- Define a W10 versioned evaluation query adapter that binds `ResearchQueryRequest`, `ResearchVersionPins`, exact candidate/evaluation pools and reversible identities.
- Define a paired query-level challenger-minus-best-control metric/interval contract and canonical calculation for `nDCG@10`.
- Define a W10 protected preregistration, evidence-inventory and broker contract that preserves the W06 one-use patterns without importing W05 literals or zero-only population types.
- Define W10 applicability contracts that distinguish historical engineering coverage from governed expert relevance and keep missing evidence typed.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
