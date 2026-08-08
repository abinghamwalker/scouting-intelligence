# W06 evaluation readiness inventory

Status: `MISSING_EXPERT_RELEVANCE_EVIDENCE`.

This bounded inventory uses only retained local bytes named below. It does not inspect
protected expected outputs, W03 protected-attempt evidence, test paths, source code, or
the data/run directories beyond the packet's named W05 run manifest inputs.

## Expert-relevance evidence

No valid governed human football-expert judgement is retained in the inspected inputs.
Accordingly there is no reviewer identity or pseudonymous key, credential/authority
record, judgement rubric, judgement time, item-to-judgement provenance, use-rights
record, or FIT/TUNE/CALIBRATION/PROTECTED_TEST partition assignment to inventory.

This conclusion is affirmative rather than an inference from model scores:

- `configs/roles/w05-football-responsibility-taxonomy-v1.json` declares
  `expert_validation_status: NOT_PERFORMED` and `external_expert_evidence: []`.
- `reports/phase-gates/W05/gate-report.json` repeats external expert validation as
  `NOT_PERFORMED`.
- `runs/w05/m0-baseline-v1/candidate-universe.json` declares
  `external_expert_label: false`, `protected: false`, `development_only: true`, and
  `recruitment_outcome: false`.
- `docs/architecture/evaluation-contract.md` says W03 has no real expert labels,
  calibration partition, or prospective outcome. W03 protected synthetic fixtures
  cannot be relabelled as W06 relevance evidence.

Therefore no local evidence supports a relevance metric, a threshold, a human-agreement
claim, calibration, model promotion, or recruitment claim. Codex agents are not human
football experts and are not evidence producers for this purpose.

## Retained populations and boundaries

| Population | Retained identity / size | What is executable now | W06 status |
| --- | --- | --- | --- |
| W04 governed source snapshot | Wyscout figshare v5 snapshot `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`; five 2017/18 domestic top-flight partitions, 1,826 matches and 3,071,395 actions | Not inspected directly by this packet; only its documented derived boundary is available | Not a W06 relevance population; broader league/time/source transfer is unsupported |
| W04 materialised product | build `b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`; exactly one authorised English window, 2017-08-11 to 2017-08-12, cutoff 2026-08-01; one Gold player-window row / one player-match fact | Four exact count features only: `action_count`, `coordinate_known_action_count`, `match_count`, `resolved_possession_action_count` | Executable reconstruction evidence only; cannot form a held-out, team, time, competition, or expert-judged retrieval evaluation |
| W05 development fitting/candidate universe | `w05-synthetic-development-complete-rows-v1` / `w05-synthetic-development-candidate-universe-v1`; 18 / 18 rows; candidate projection digest `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086` | Deterministic M0 reconstruction/comparison at k=3 | Constructed synthetic-development-only; no expert labels, outcome labels, protected partition, or production claim |
| W05 development queries | `w05-m0-development-queries-v1`, digest `fb027563b3f99f563d43f1b909c535f860f3d04d2d8aa0ed44e902fd2a37e900`, query projection digest `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c` | Deterministic fixed comparison only | Not a governed relevance test set |

The accepted M0 identity is artifact `9a0d43c6-d177-51be-8280-3bf02bedbc99`, family
`role_aware_restriction`, model/index version `v1`, artifact-manifest digest
`2ed113a19acec3a3bbd80038ecc0b639a4a587111b35af2d4d7b0edd651c8fa9`, configuration
digest `5f847a5b57393dd1a0bb9007c7e89f38305fc5d4be9bfbe3a12285b6783e382a`, taxonomy
`w05-football-responsibility-taxonomy-v1`/`v1`, and synthetic feature schema
`1f713272907731b5c8b486275333976934b58ad4c7e622b192d26e2db39e642f`.

The W04 exact-four feature schema is
`cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127`.
Minutes, rates and per-90 remain suppressed for lack of an accepted elapsed-minutes
denominator. This one-match exact-four boundary is explicit and must not be widened.

## Partition and test feasibility

Available executable evidence is limited to the already accepted local W05 baseline
and parity evidence: deterministic constructed comparison, all-six-family reconstruction,
18 fixed queries, and direct/single/batch/replay/fresh-core parity as documented in
`reports/verification/W05/model-baseline-evidence.md` and
`reports/verification/W05/training-serving-parity-report.md`. The W05 terminal report
records 2,695 passing repository tests, but this packet deliberately did not inspect
or execute forbidden `tests/**` paths.

Unsupported, and not simulated or duplicated:

- authentic human-expert relevance, pair-preference, agreement, or adjudication;
- rights-proven expert-label FIT/TUNE/CALIBRATION/PROTECTED_TEST partitions;
- protected W06 query/candidate expected outputs or brokered comparison;
- independent teams, matches, time windows, competitions/leagues, providers, seasons,
  youth/women/current populations, or recruitment outcomes;
- time/league/source transfer, stability/churn, split-half reliability, bootstrap
  intervals, null/shuffle controls, calibration, and prospective workflow outcomes.

No metric, threshold, effect size, or gate choice is proposed as accepted authority.

## Smallest conservative W06 task graph

1. **Serial — evaluation contract and evidence schema.** Define the governed human
   judgement record, pseudonymous reviewer key, rubric/version, timing/as-of rules,
   provenance, rights/permitted-use and partition states; freeze candidate/query IDs and
   leakage controls. This cannot begin by inventing labels.
2. **Serial — protocol and metric authority.** After valid evidence exists, preregister
   metrics, null/robustness controls, split unit and acceptance authority; retain the
   W04 and W05 claim boundaries.
3. **Serial — protected broker.** Master-owned protected inputs/expected outputs and
   execution against a preregistered candidate only. Implementers must not access those
   bytes.
4. **Serial — closure evidence.** Independently reproduce the brokered run, record
   leakage/rights/schema results, limitations and a GO/NO-GO decision. Integration and
   all protected/shared surfaces remain serial.

No path-disjoint implementation task is ready before steps 1–2 have valid governed
inputs; no human-judgement collection, external/provider access, or rights decision is
authorised by this inventory.

## Evidence paths

- `docs/architecture/evaluation-contract.md`
- `docs/architecture/product-claim.md`
- `docs/dataset-cards/w04-wyscout-transformed-v1.md`
- `configs/features/wyscout-v5-supported-count-features-v1.yaml`
- `configs/features/w05-m0-feature-registry-v1.json`
- `configs/roles/w05-football-responsibility-taxonomy-v1.json`
- `configs/models/w05-m0-baselines-v1.json`
- `runs/w05/m0-baseline-v1/manifest.json`
- `runs/w05/m0-baseline-v1/configuration.json`
- `runs/w05/m0-baseline-v1/candidate-universe.json`
- `reports/phase-gates/W05/acceptance-report.md`
- `reports/phase-gates/W05/gate-report.json`
- `reports/reviews/W05/master-review.md`
- `reports/verification/W05/model-baseline-evidence.md`
- `reports/verification/W05/training-serving-parity-report.md`
- `reports/verification/W05/limitations.md`
