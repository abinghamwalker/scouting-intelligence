# Subagent return

## Task

- task_id: `W09-RESEARCH-CONTRACTS-02A-REVIEW`
- objective: Independently adversarially review the W09 research contracts for strictness, digest coherence, stale-version safety, query-mode ambiguity, result explanations, replayability and the historical-resemblance-only claim boundary.

## Files changed

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R1.md`

## Summary

- recommendation: **REWORK**
- highest severity: **P1**
- finding count: **8 P1, 1 P2**
- The implementation has useful foundations: all models inherit frozen/strict/extra-forbid behaviour, NaN and infinities are rejected on the new numeric aliases, query modes are mutually exclusive, at least one positive weight is required, exact pin equality fails closed, result/comparison/experiment digests self-validate, and the literal `historical_resemblance_research_only` boundary cannot be replaced by a positive recruitment claim.
- Those controls are not yet sufficient for a shared cross-boundary contract. The current surface can encode contradictory eligibility records, impossible full-population counts, negative or unordered distance rankings, explanations unrelated to scores, stale/method-mismatched experiments and comparisons, and replay receipts not bound to the saved experiment. It also lacks the typed matrix/index manifest needed to prove the inventory reconciliation.

## Severity-ranked findings

### [P1] The eligibility decision cannot represent the required reconciliation and still accepts contradictory outcomes

`EligibilityDecision` requires a canonical `player_id`, `competition_id` and `season_id` for every outcome (`src/scouting/contracts/research.py:126-142`), even for `IDENTITY_UNRESOLVED`, `NO_LINEUP_EVIDENCE` and `INVALID_HISTORICAL_MEMBERSHIP`. The retained 15 absent-master IDs have no canonical player ID, and 607 resolved catalogue players have no lineup/event evidence from which a competition-season can be assigned. The contract therefore forces either a guessed canonical/grain value or omission, while the inventory requires explicit auditable exclusion and mutually exclusive reconciliation (`reports/verification/W09/data-inventory-and-coverage.md:348-357`).

The validator at `src/scouting/contracts/research.py:144-157` checks only eligible/reason equality, minute presence by broad state, the eligible threshold and unresolved-ID uniqueness. It accepts, among other contradictions:

- `reason=BELOW_MINIMUM_MINUTES` when minutes meet or exceed the threshold;
- `reason=UNUSABLE_MINUTES` with `minute_state=EXACT` and usable minutes;
- `eligible=True` with non-empty `unresolved_source_player_ids`;
- `reason=IDENTITY_UNRESOLVED` with a supposedly canonical resolved player ID and an empty unresolved-ID set.

Required correction: introduce a source-population decision shape that can truthfully represent pre-canonical/pre-competition exclusions, or make grain fields conditional with exhaustive reason-specific validation. Enforce exact reason/minute/identity combinations, link each outcome to the eligibility policy, and prove included plus mutually exclusive exclusions equals the 3,603 resolved catalogue baseline while separately retaining the 15 unresolved IDs and zero sentinel evidence.

### [P1] There is no typed matrix/index manifest, and a matrix row omits mandatory lineage, coverage, window and exposure state

`FeatureMatrixRow` carries a label, grain fields, teams, one numeric minute total, features, cutoff and action count (`src/scouting/contracts/research.py:203-220`). It does not carry or bind:

- exact versus conservative-lower-bound minute state;
- the eligibility decision/policy identity;
- window start/end or window definition;
- coverage and missingness summary;
- source/canonical dependency lineage;
- dataset, identity, feature-registry or canonical-build identity.

No `FeatureMatrixManifest` or `ResearchIndexManifest` contract exists. `ResearchVersionPins` at `src/scouting/contracts/research.py:235-250` merely stores opaque labels/digests; there is no typed manifest whose canonical digest binds the required source snapshot, source completion, identity bundle, canonical build, feature schema, policy, code, files, row counts, physical/semantic checksums and no-synthetic evidence. This leaves the inventory requirements at `reports/verification/W09/data-inventory-and-coverage.md:338-343` and `:372-377` unrepresentable at the cross-boundary layer.

Required correction: add self-verifying matrix and index manifest contracts, complete row temporal/coverage/lineage/minute-state fields, manifest population/count invariants and exact file/checksum identities. Pins should reference those typed manifest identities and include the scorer/model configuration/code identity they transitively prove.

### [P1] Dataset and query temporal contracts permit cutoff equality and do not bind a query cutoff to its matrix/index

`ResearchDatasetDescriptor.authority_is_coherent` rejects authority availability only when it is *after* the cutoff (`src/scouting/contracts/research.py:91-99`), so source or identity evidence available exactly at `feature_cutoff_ts` passes. The accepted `TemporalEvidence` rule is strict-before, and the W09 inventory explicitly requires every authority to satisfy the chosen cutoff (`reports/verification/W09/data-inventory-and-coverage.md:367-369`).

`ResearchQueryRequest` checks only `feature_cutoff_ts <= requested_at` (`src/scouting/contracts/research.py:316-320`). `ResearchVersionPins` carries no matrix/index cutoff or temporal-manifest digest that the contract can compare, so a request may claim a different cutoff from the loaded feature matrix while all pins compare equal.

Required correction: use strict-before authority availability consistently, bind the immutable matrix/index cutoff in typed manifests/pins, and require the query cutoff to equal the selected dataset/matrix/index cutoff. Add equality-at-cutoff and mismatched-cutoff rejection tests.

### [P1] Result contracts accept rankings and explanations that cannot be reproduced from the declared method

`ResearchCandidate.score` is only finite, not non-negative (`src/scouting/contracts/research.py:351-365`), although both methods are distances. Contributions need only have unique names (`:367-374`); the contract does not require their ordered names and weights to equal the request, prevent overlap with `missing_features`, or reconcile their signed terms to the candidate score under Euclidean/cosine rules.

`ResearchQueryResult.result_is_coherent` checks contiguous ranks, returned count and the self-digest only (`src/scouting/contracts/research.py:416-425`). It does not reject duplicate grain/player candidates, incorrect competition, negative scores, rank order inconsistent with `(score, canonical identity, grain)`, contribution-order drift, or missing active features in returned candidates. A syntactically valid digest therefore authenticates semantically impossible output.

Required correction: bind a result to the exact request/query digest, enforce candidate uniqueness and deterministic score/tie order, non-negative bounded method-appropriate scores, exact active-feature contribution order/weights, contribution-to-score reconciliation and an explicit policy for missing active features.

### [P1] Population counts can be internally impossible and do not prove full-population execution

`RetrievalPopulationCounts.counts_reconcile` enforces only `filter_admitted = missing + scored`, `returned <= scored` and `competition <= matrix` (`src/scouting/contracts/research.py:377-395`). It accepts `filter_admitted_rows > competition_rows`, `scored_rows > matrix_rows`, and no accounting for competition rows removed by position/minutes/exclusions. Consequently the result can claim full-population scoring while its counts cannot descend from the matrix.

Required correction: add mutually exclusive filter-exclusion counts (including exemplar/self and explicit exclusions as applicable), require `competition_rows = filter_exclusions + filter_admitted_rows`, enforce every child count within its parent, and require the final returned count to equal `min(limit, scored_rows)` unless an explicit reason states otherwise.

### [P1] Saved experiments and comparisons are not cross-bound tightly enough for immutable replay

`SavedResearchExperiment.experiment_is_coherent` checks query ID, request/result pins and comparison result ID (`src/scouting/contracts/research.py:476-487`). It does not require:

- `request.method == result.method`;
- result generation at or after the request;
- comparison pins equal result/request pins;
- comparison ID/rows equal the submitted comparison request and candidates from the result;
- report bytes/contract to bind the exact saved experiment projection.

Thus a Euclidean request can be saved with a cosine result, or a comparison from a stale matrix can be attached to a current result, and the experiment's self-digest will bless the mismatch.

Required correction: bind method, query digest, result timing, comparison request/digest/pins/candidate membership and a canonical report contract before computing `experiment_digest`.

### [P1] Replay receipts prove only two equalities, not replay of the named saved experiment

`ResearchReplayReceipt` contains only an experiment ID, two pin sets, two result digests, a boolean and free-text reason (`src/scouting/contracts/research.py:490-511`). Its validator derives `reproduced` from pin/result equality, but it does not bind the saved `experiment_digest`, original query/request digest, loaded artifact/index manifest digest beyond the supplied pin object, code/scorer identity, replay query/result identity or a receipt digest. A caller can construct a `reproduced=True` receipt for any experiment UUID by supplying matching arbitrary pins and digests.

Required correction: bind the exact saved experiment digest, query/request digest, original result identity, loaded manifest/code/scorer identity and replay result identity; use a closed reason/status vocabulary and a self-verifying receipt digest.

### [P1] The package-level state exports are cross-wired between M0 and W09

The root package exports M0 `FeatureValue` (`src/scouting/contracts/__init__.py:81-87`) but imports M0 `FeatureValueState` under the name `ResearchFeatureValueState` (`:115-117`). It then imports the W09 enum as the generic `FeatureValueState` (`:140-147`) and exports all three names (`:268-269`, `:343-345`). This creates two intuitive but wrong pairs:

- `FeatureValue` + `FeatureValueState` combines the M0 model with the W09 enum;
- `ResearchFeatureValue` + `ResearchFeatureValueState` combines the W09 model with the M0 enum.

Because the contracts are strict, these similarly valued but distinct enum classes are not a safe public pairing. The tests import directly from `scouting.contracts.research` and never exercise the package exports (`tests/contracts/test_w09_research_contracts.py:11-24`).

Required correction: provide unambiguous paired names such as `M0FeatureValue`/`M0FeatureValueState` and `ResearchFeatureValue`/`ResearchFeatureValueState`, preserving any accepted compatibility alias deliberately, and add package-root identity/construction tests.

### [P2] Feature-value semantics allow non-canonical and contradictory evidence payloads

The finite aliases reject NaN/infinity, which is good, but they do not reject negative zero. `ResearchFeatureValue.value_matches_state` (`src/scouting/contracts/research.py:180-200`) accepts `ZERO` with `-0.0`, `VALUE` with `0.0`, observed states with a reason, and missing/suppressed/unavailable states that still carry numeric numerator/denominator evidence. These representations undermine the stated distinction between observed zero and absence and create different digests for semantically equivalent zero values.

Required correction: canonicalize/reject negative zero, require nonzero `VALUE` if `ZERO` is the zero state, forbid reasons on observed states, define valid numerator/denominator pairings, and forbid numeric calculation fields on absence states. Apply the same canonical-number rule to weights, filters, scores and contributions.

## Test-evidence gap

The six current tests all pass, but they instantiate only dataset, query, pins and one eligibility rejection. They do not construct or adversarially mutate `ResearchFeatureValue`, `FeatureMatrixRow`, `ResearchCandidate`, `RetrievalPopulationCounts`, `ResearchQueryResult`, `ResearchComparisonRequest`, `ResearchComparison`, `SavedResearchExperiment`, `ResearchReplayReceipt`, any package-root export pairing, or any valid full nested result/experiment digest (`tests/contracts/test_w09_research_contracts.py:69-147`). Rework needs positive round-trip tests plus one-field substitution and contradiction attacks for every digest-bearing and cross-bound contract.

## Explicit review conclusions

- fail-closed pins: **partial** — exact object equality is sound, but the pin set lacks typed manifest/cutoff/model-code authority and cross-object enforcement.
- temporal rules: **rework** — equality at cutoff and request/matrix cutoff drift are admitted.
- digest projections: **partial** — result/comparison/experiment self-digests are coherent; query, manifests and replay receipt lack equivalent binding, and nested semantic mismatches are not rejected before digesting.
- finite numeric validation: **partial** — NaN/infinity rejection passes; negative zero, negative result distance and contribution reconciliation remain open.
- uniqueness: **partial** — local feature/filter tuples are checked; result candidates, canonical order and population-wide matrix uniqueness are not.
- query-mode exclusivity: **pass with ordering residual** — exemplar/profile exclusivity and positive weights are enforced, but profile/weight sets may use different orders and collection filters are not canonicalized.
- population reconciliation: **rework** — the eligibility shape cannot truthfully represent all inventory branches and retrieval counts can be impossible.
- immutable experiment/replay binding: **rework** — method/comparison/report/experiment/replay identities are under-bound.
- naming/export collisions: **rework** — package-root feature value/state aliases pair the wrong strict enum types.
- claim boundary: **pass for the current models** — the literal historical-resemblance-only value, mandatory limitations and absence of recruitment outcome fields preserve the approved non-claim. Rights classification is still free text and should be bound by the typed dataset manifest rather than trusted as a label.

## Tests run

- command: `uv run ruff check src/scouting/contracts/research.py src/scouting/contracts/__init__.py tests/contracts/test_w09_research_contracts.py`
  - exit status: `0`
  - result: PASS — `All checks passed!`
- command: `uv run mypy src/scouting/contracts/research.py`
  - exit status: `0`
  - result: PASS — `Success: no issues found in 1 source file`
- command: `uv run pytest -q tests/contracts/test_w09_research_contracts.py`
  - exit status: `0`
  - result: PASS — 6 tests passed in 0.16s.
- command: `test -s reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R1.md`
  - exit status: `0`
  - result: PASS — the required review artifact is non-empty.

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-RESEARCH-CONTRACTS-02A-REVIEW-R1.md`
- Reviewed implementation: `src/scouting/contracts/research.py`
- Reviewed public export surface: `src/scouting/contracts/__init__.py`
- Reviewed tests: `tests/contracts/test_w09_research_contracts.py`
- Controlling population evidence: `reports/verification/W09/data-inventory-and-coverage.md`

## Risks

- Accepting the current contracts would make later matrix, retrieval, API and persistence code depend on ambiguous or under-bound shared semantics. Fixing those after artifacts are generated would change manifests and result/experiment digests.
- No football relevance, current-market coverage, recruitment usefulness or recommendation claim was used in this review. W06 remains `NO_GO` and G-RW4 remains absent.

## Follow-up items

- Issue bounded contracts rework for all P1 findings and the numeric P2, expand adversarial/positive nested tests, then obtain a fresh independent review before matrix or retrieval producers freeze these shapes.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither dependency file was changed.
- no edits outside `allowed_paths`: confirmed; only this review report was created.
- no implementation, test or orchestration edits: confirmed.
