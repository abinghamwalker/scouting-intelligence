# W06 evaluation protocol card

## Frozen protocol

The frozen preregistration is `w06-protected-preregistration-v1`, digest `13d26404f788466993d7cd3663c787e6da182005dd68c0dd48c70783f7c20ae5`. Its protocol digest is `b4836c928df5696d1b33e38d25095409958e459d55f92d3928626621e6422217`; claim boundary is `resemblance_only` and evidence boundary is `GOVERNED_HUMAN_EXPERT_REQUIRED`.

The protected partition is `PROTECTED_TEST`. Primary metric: `ndcg@10`. Secondary roster: precision@5/10, recall@5/10, ndcg@5, coverage@5/10, pair preference, and agreement only when multiple real reviewers exist. Query-level percentile bootstrap is frozen at seed `20260804`, 2,000 resamples and 0.95 confidence. The minimum useful effect is `ndcg@10_delta_vs_best_control>=0.05;lower>0.0`.

Metadata and raw-Euclidean are the preregistered baselines. Nulls are shuffled-label and shuffled-pair only when governed pair evidence exists. `k=25` is explicitly unsupported because the W05 candidate universe has 18 members.

## Partition and rubric boundary

No governed human relevance evidence exists for FIT, TUNE, CALIBRATION or PROTECTED_TEST. Public W06 fixtures are `IMPLEMENTATION_FIXTURE_ONLY`: they witness deterministic metric, rejection, robustness and control implementation behavior, never expert relevance, calibration, transfer, prospective, recommendation, outcome, value or empirical applicability.

## Exact stop algorithm

The first failed prerequisite yields `NO_GO`, in this order: authentic governed expert evidence; nonempty protected population; valid partition access; temporal and source lineage; primary effect and interval; null controls; mandatory slices and applicability; unchanged explanation and serving parity. If governed expert evidence or protected population is absent, protected outputs are not opened; after the one-use invocation there is no retuning or rerun.

Source: `configs/evaluation/w06-protected-preregistration-v1.json`; `reports/readiness/W06/evaluation-readiness.md`; `docs/architecture/evaluation-contract.md`.
