# W06 evaluation-readiness independent review — R1

- Task: `W06-PREFLIGHT-REVIEW-01`
- Producer task reviewed: `W06-PREFLIGHT-01-R1`
- Review role: independent verifier
- Decision: **REWORK**
- Severity summary: **P0: 0; P1: 2; P2: 1**

The producer correctly establishes `MISSING_EXPERT_RELEVANCE_EVIDENCE`, keeps W03
protected synthetic evidence outside W06 relevance evidence, and preserves the W04
one-match exact-four and W05 constructed synthetic-development-only boundaries. The
readiness decision is nevertheless not acceptable because it turns absence of
authentic expert judgements into a pause on implementable W06 evaluation machinery and
on the evidence-honest protected `NO_GO` path required by the controlling workflow.

This was a report-only review. It did not read protected expected outputs,
`tests/fixtures/synthetic/protected/domain.json`, or any W03 protected-attempt report.

## Findings

| ID | Severity | Finding and exact evidence | Decision effect | Smallest bounded correction |
| --- | --- | --- | --- | --- |
| W06-PREFLIGHT-R1-F1 | P1 | The executable-versus-unsupported inventory conflates unavailable empirical evidence with implementable deterministic capability. `reports/readiness/W06/evaluation-readiness.md:64-72` puts split-half reliability, bootstrap intervals and null/shuffle controls in one unsupported list, while lines 82 and 92 defer metric authority and every path-disjoint implementation task until valid governed expert evidence exists. The controlling workflow separately requires ranking metrics/intervals and robustness/null implementations at `../scouting-ml-agent-implementation-workflow.html:1009-1010`; W05 closure explicitly assigns protected evaluation and robustness intervals to W06 at `reports/phase-gates/W05/acceptance-report.md:25`. Metric schemas, Precision/Recall/NDCG/rank/overlap functions, bootstrap algorithms, shuffle/null controls, and explicit unavailable/applicability states can be implemented and verified on public implementer-visible deterministic fixtures without treating fixture labels or results as expert evidence. | Incorrectly prevents executable W06 contract/harness work and could erase required distinction among algorithm correctness, public-fixture computation, and decision-supporting expert evidence. | Retain every empirical non-claim, but split the inventory into: (a) implementable deterministic contracts/functions and public-fixture checks; (b) empirical computations possible only as synthetic/development evidence; and (c) W06 relevance, transfer, calibration and prospective conclusions unavailable for lack of governed populations. State that public-fixture values prove implementation correctness only. |
| W06-PREFLIGHT-R1-F2 | P1 | The task graph stops instead of reaching the required negative protected decision. `reports/readiness/W06/evaluation-readiness.md:82-92` says protocol/metric authority waits until valid evidence exists, places the protected broker after that wait, and says no path-disjoint implementation is ready. The controlling W06 task list requires a protected comparison and a gate decision at `../scouting-ml-agent-implementation-workflow.html:1011-1012`; G-W06 explicitly says that when the listed evidence does not support the claim, record `NO-GO` and return to W05 at line 1014. The blueprint likewise requires either an interval-supported win or `NO-GO` at `../scouting-ml-production-blueprint.html:2277-2280`. Missing expert and protected populations are valid fail-closed inputs to a protected gate; they do not require fabricated identities, labels, thresholds, protected-output reads, or external access. | Could incorrectly pause W06, omit retained negative evidence, and leave the model gate undecided instead of producing the evidence-honest `NO_GO` required by the approved workflow. | Replace the blocked graph with a continuous bounded graph: implement/freeze evidence and partition contracts; implement deterministic metrics, intervals, nulls and applicability controls against public fixtures; preregister the exact candidate and gate semantics without inventing a result threshold; run the protected gate with the retained missing-population state; emit `NO_GO` with `MISSING_EXPERT_RELEVANCE_EVIDENCE` and missing governed protected-population reasons; independently review and retain closure evidence. Empirical transfer/stability tests remain unavailable where the exact populations do not exist. |
| W06-PREFLIGHT-R1-F3 | P2 | The producer packet requires exact inventories of available competitions, teams, providers, time windows, and candidate/query populations. The report names Wyscout, aggregate five-partition counts, one English time window, and W05 population IDs/digests, but does not give competition identities, team identities, or the materialised match/player identities, nor explicitly classify those identities as unavailable in the inspected retained inputs (`reports/readiness/W06/evaluation-readiness.md:33-46`). | The existing no-transfer conclusion remains conservative, but an inventory labelled exact is incomplete and is less reproducible for future partition design. | Add the retained exact identities and their evidence paths if locally proven; otherwise state explicitly that named competition/team/match/player identities are not established by the inspected readiness inputs and cannot be used to construct a W06 partition. Do not inspect protected or unauthorised paths to fill the gap. |

## Direct answers to the packet review questions

1. **Is `MISSING_EXPERT_RELEVANCE_EVIDENCE` proved without inventing or
   impersonating an expert? — Yes, within the bounded inspected evidence.**
   `configs/roles/w05-football-responsibility-taxonomy-v1.json` binds taxonomy
   `w05-football-responsibility-taxonomy-v1` / digest
   `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097` to
   `expert_validation_status: NOT_PERFORMED` and an empty
   `external_expert_evidence`. `reports/phase-gates/W05/gate-report.json` repeats
   `external_expert_validation: NOT_PERFORMED`.
   `runs/w05/m0-baseline-v1/candidate-universe.json` binds candidate universe
   `w05-synthetic-development-candidate-universe-v1` to
   `external_expert_label: false`, `protected: false`, `development_only: true`,
   and `recruitment_outcome: false`. The report also correctly says Codex agents
   are not human football experts.

2. **Are W03 protected synthetic fixtures kept outside W06 expert relevance
   evidence? — Yes.** The readiness report explicitly refuses relabelling, consistent
   with `docs/architecture/evaluation-contract.md:59-72`. This review did not access
   the protected fixture files or W03 protected-attempt files.

3. **Are the W04 and W05 populations stated exactly? — Yes for the material claim
   boundary; P2 for identity-level inventory completeness.** W04 remains the single
   materialised authorised English match window with one player-match fact/Gold row and
   the four supported counts under schema
   `cf8847f2b1f70ebf293ce90e48817e80a4e47b78316079bd88e8c2a80bc08127`.
   The wider source snapshot of 1,826 matches and 3,071,395 actions is not represented
   as the materialised evaluation population. W05 remains exactly constructed
   synthetic-development evidence: fitting population and candidate universe counts
   `18`, candidate projection digest
   `60c5a45f5bec8bed911f708cadaed4532759bcfc883b28e91d5d19195301a086`,
   query projection digest
   `1726816886fdd2ab7fefcf6ec661a24f944770bda5853d1ede5f6b9b7e766e5c`,
   and no protected, expert, recruitment-outcome or production claim.

4. **Does the executable-versus-unsupported inventory make the required
   distinction? — No; P1 F1.** Empirical expert relevance, transfer, calibration and
   prospective claims are unavailable. Deterministic contracts, metric functions,
   bootstrap interval algorithms, null/shuffle controls, missingness/applicability
   semantics, and public-fixture verification are implementable now. Their fixture
   outputs must remain labelled contract/development evidence, never expert evidence.

5. **Does the graph continue through an evidence-honest protected `NO_GO`? — No;
   P1 F2.** It pauses for expert evidence. The approved workflow requires the gate to
   close negatively when the required evidence is absent.

6. **Could a report statement change a W06 partition, metric, protected decision,
   applicability claim, or local-only boundary incorrectly? — Yes.** The claim that no
   implementation task is ready and the dependency of metrics/broker work on future
   expert evidence could suppress the W06 executable tasks and required protected
   `NO_GO`. The report does not broaden the local-only boundary and does not currently
   make a false positive applicability or relevance claim.

## Corrected readiness boundary

The smallest evidence-honest interpretation is:

- authentic human-expert relevance evidence, rights-proven expert partitions,
  empirical expert relevance metrics, transfer/generalisation conclusions,
  calibration, and prospective outcomes are unavailable;
- W04 supports only its one-match exact-four research/reconstruction boundary;
- W05 supports only deterministic constructed synthetic-development baseline and
  serving-parity evidence;
- W06 contract, metric, interval, null/control, applicability and missing-population
  gate implementations are ready to build and test on public deterministic fixtures;
- the protected W06 decision must currently resolve to `NO_GO`, not wait, because the
  governed expert/protected population required to support the displayed claim is
  absent;
- no threshold, human judgement, protected expected output, transfer population, or
  external access is to be invented.

## Residual risks after the bounded report correction

- **Leakage:** future protected labels/populations must remain brokered and one-use;
  public fixture values must not become expected protected outputs.
- **Schema:** evidence, partition, metric-result, interval, null-control,
  applicability and gate-reason contracts are not yet implemented or independently
  verified.
- **Rights:** no retained expert judgement has locally proven identity, rubric,
  provenance, timing, partition assignment or permitted-use rights.
- **Scope/population:** W04 has no valid held-out split; W05 is constructed
  synthetic-development-only; team/time/league/provider transfer populations are not
  to be fabricated.
- **Claim:** no W06 expert relevance, calibration, recommendation, transfer,
  prospective, or production claim is supported. The current protected outcome is
  necessarily `NO_GO`.

## Verdict

**REWORK.** No P0 exists and no external, provider, credential, dependency or protected
expected-output access is needed for the smallest correction. Correct the readiness
inventory and graph for F1–F3, then obtain fresh independent review. This reviewer does
not self-approve the producer report or the future W06 gate.
