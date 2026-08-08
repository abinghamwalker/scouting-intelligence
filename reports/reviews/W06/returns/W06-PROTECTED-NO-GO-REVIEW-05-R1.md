# Subagent return

## Task

- task_id: `W06-PROTECTED-NO-GO-REVIEW-05-R1`
- objective: Independently review exact frozen candidate/protocol/inventory substitution resistance and one-use missing-population NO_GO behavior.

## Files changed

- reports/reviews/W06/protected-no-go-independent-review-R1.md
- reports/reviews/W06/returns/W06-PROTECTED-NO-GO-REVIEW-05-R1.md

## Summary

- verdict: `REWORK`
- exact severities: P0 `0`; P1 `1`
- The exact master mutation is accepted after re-signing and reaches broker persistence:
  protocol `0315215e86788e773050637a2ac6d6cda70464efbdc4297f28c2cac3b27a3f4e`,
  preregistration `5f71bc77d1ea5430e3663ac5e0f0f84697b07c00776a4f3a1ce678a24cb3dffe`.
- Sole P1: `fail_closed_order` and `stop_rule` are not compared to their frozen constants.
  Smallest correction is to add both exact comparisons to `FrozenProtectedProtocol.valid`
  plus the exact re-signed regression.

## Exact frozen/substitution matrices

- Candidate, all REJECTED after applicable re-signing: `selected_family`, `artifact_id`,
  `manifest_digest`, `configuration_digest`, `taxonomy_digest`,
  `feature_registry_digest`, `feature_schema_hash`, `accepted_result_digest`,
  `lineage_hash`, `candidate_digest`.
- Protocol, REJECTED after applicable re-signing: `claim_boundary`, `evidence_boundary`,
  `protected_partition`, `primary_metric`, ordered `secondary_metrics`,
  `explicitly_unsupported_k`, `baselines`, `nulls`, `bootstrap_seed`,
  `bootstrap_resamples`, `bootstrap_confidence`, `bootstrap_method`,
  `minimum_useful_effect`, unsigned `protocol_digest`.
- Protocol, ACCEPTED after re-signing: first-two `fail_closed_order` swap; `stop_rule`
  replacement; exact combined master mutation. The combined mutation was also brokered
  successfully in `/tmp` and persisted both substitutions.
- Inventory, all REJECTED after applicable re-signing: each of the four zero counts to
  one, reordered `missing_evidence`, unsigned `inventory_digest`.

## Exact one-use matrix

- Initial invocation: exactly access outcome, gate decision and receipt; outcome
  `NOT_ACCESSED_MISSING_POPULATION`; protected opened `false`; decision `NO_GO`; sole
  reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`; claim `resemblance_only`; bundle/run absent;
  receipt bindings and predecessor file digests exact.
- Second invocation: REJECTED; bytes unchanged.
- Each single partial pre-existing output (access, gate, or receipt): REJECTED; marker
  unchanged; no additional output.
- Caller digest disagreement: REJECTED before output-directory creation.
- Broker inputs: preregistration, caller digest, invocation ID and output directory only;
  no protected, bundle, run, or access object input.

## Tests run

- packet pytest command: initial sandbox status `2` (uv cache read denied); authorised
  local-cache rerun status `0`, `23 passed in 0.27s`.
- packet ruff command: status `0`, all checks passed.
- packet mypy command: status `0`, no issues in 6 source files.
- `uv run --no-sync lint-imports`: status `0`, 3 kept and 0 broken.
- packet SHA-256 command: status `0`, config
  `dc2fdc1ec4178f1d913cf58268aca5d48eb699f7135b0e627975ef8d89de2410`, fixture
  `495f8148f68f36c1e98c3aff0f255a1009949d3ffcef583bdaaeda72dbc692eb`.
- temporary matrix harness: final status `0`; exact master digests and all matrices
  reproduced. Detailed command text and result matrix are in the independent report.

## Artifacts/evidence

- reports/reviews/W06/protected-no-go-independent-review-R1.md
- reports/reviews/W06/returns/W06-PROTECTED-NO-GO-REVIEW-05-R1.md

## Risks

- Remaining P0: none.
- Remaining P1: one, exact stop-rule/fail-closed-order substitution described above.

## Follow-up items

- Enforce the exact fail-closed order and complete stop rule, then independently rerun
  the exact re-signed master mutation.

## Scope confirmation

- no Git operations: confirmed.
- no dependency changes or installation: confirmed.
- no protected expected-output access: confirmed.
- no repository production-output invocation: confirmed.
- no external/provider/credential access: confirmed.
- no source, test, config, orchestration, run, data, docs, phase-gate, readiness, or
  verification edits: confirmed.
- no edits outside the two allowed report paths: confirmed.
