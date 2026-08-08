# W06 protected NO_GO independent review R1

## Verdict

- Task: `W06-PROTECTED-NO-GO-REVIEW-05-R1`
- Verdict: `REWORK`
- P0: `0`
- P1: `1`

The protected preregistration does not freeze every decision-bearing protocol field. A
caller can replace the exact stop rule and reorder the first two fail-closed
prerequisites, recompute both content digests, pass validation, and invoke the broker.
The candidate identity, retained zero inventory, one-use behavior, missing-population
outcome, sole NO_GO reason, and resemblance-only boundary otherwise reproduced exactly.

## P1 finding

`FrozenProtectedProtocol.valid` checks the secondary-metric roster, unsupported k,
baselines, nulls, bootstrap confidence, and canonical digest, but does not compare
`fail_closed_order` or `stop_rule` with their frozen values. Both fields are merely
non-empty tuples/strings at `src/scouting/contracts/evaluation.py:1109-1110`, and the
validator at lines 1113-1131 accepts their re-signed substitutions.

Exact reproduced mutation:

- swap `AUTHENTIC_GOVERNED_EXPERT_EVIDENCE` and
  `NONEMPTY_PROTECTED_POPULATION` in `fail_closed_order`;
- replace `stop_rule` with `Proceed despite missing expert evidence.`;
- recompute `protocol_digest` and `preregistration_digest`.

Result:

- validation: `ACCEPTED`;
- broker: `EXECUTED` in a temporary directory;
- protocol digest: `0315215e86788e773050637a2ac6d6cda70464efbdc4297f28c2cac3b27a3f4e`;
- preregistration digest: `5f71bc77d1ea5430e3663ac5e0f0f84697b07c00776a4f3a1ce678a24cb3dffe`;
- persisted access outcome: `NOT_ACCESSED_MISSING_POPULATION`;
- persisted gate embeds the substituted stop rule and reordered prerequisites.

Smallest correction: extend `FrozenProtectedProtocol.valid` to compare the exact eight
element `fail_closed_order` tuple and the complete exact stop-rule string, and add a
regression test that performs this exact two-field substitution, re-signs both layers,
and requires rejection. No other P0/P1 correction is indicated.

## Candidate substitution matrix

Each mutation was re-signed at the candidate and preregistration layers where
applicable.

| Candidate field | Result |
| --- | --- |
| `selected_family` | REJECTED |
| `artifact_id` | REJECTED |
| `manifest_digest` | REJECTED |
| `configuration_digest` | REJECTED |
| `taxonomy_digest` | REJECTED |
| `feature_registry_digest` | REJECTED |
| `feature_schema_hash` | REJECTED |
| `accepted_result_digest` | REJECTED |
| `lineage_hash` | REJECTED |
| `candidate_digest` | REJECTED |

The frozen values also agree exactly with the W05 gate report, selected manifest, and
configuration readback.

## Protocol substitution matrix

Each substantive mutation was re-signed at both protocol and preregistration layers.

| Protocol field | Result |
| --- | --- |
| `claim_boundary` | REJECTED |
| `evidence_boundary` | REJECTED |
| `protected_partition` | REJECTED |
| `primary_metric` | REJECTED |
| complete ordered `secondary_metrics` | REJECTED |
| `explicitly_unsupported_k` | REJECTED |
| `baselines` | REJECTED |
| `nulls` | REJECTED |
| `bootstrap_seed` | REJECTED |
| `bootstrap_resamples` | REJECTED |
| `bootstrap_confidence` | REJECTED |
| `bootstrap_method` | REJECTED |
| `minimum_useful_effect` | REJECTED |
| `fail_closed_order` first-two swap | **ACCEPTED** |
| `stop_rule` replacement | **ACCEPTED** |
| unsigned `protocol_digest` replacement | REJECTED |
| exact combined master mutation, re-signed | **ACCEPTED and brokered** |

The metric roster retains primary `ndcg@10`; secondary precision at 5/10, recall at
5/10, NDCG at 5, coverage at 5/10, pair preference, and conditional real-reviewer
agreement; unsupported `k=25`; metadata and raw-Euclidean baselines; shuffled-label and
conditional shuffled-pair nulls; query bootstrap seed 20260804, 2000 percentile
resamples at 0.95 confidence; and the exact minimum effect. Only the order and stop rule
remain substitution-permissive.

## Inventory substitution matrix

Each mutation was re-signed at the inventory and preregistration layers where
applicable.

| Inventory field | Result |
| --- | --- |
| authentic governed human relevance reviewers `0 -> 1` | REJECTED |
| governed relevance judgements `0 -> 1` | REJECTED |
| governed pair preferences `0 -> 1` | REJECTED |
| protected queries `0 -> 1` | REJECTED |
| reordered `missing_evidence` | REJECTED |
| unsigned `inventory_digest` replacement | REJECTED |

The exact retained inventory is four zero counts plus, in order,
`MISSING_EXPERT_RELEVANCE_EVIDENCE` and `MISSING_PROTECTED_POPULATION`. No nonzero or
fabricated population passed the contract boundary.

## One-use and broker matrix

All broker invocations used newly created operating-system temporary directories.

| Case | Result |
| --- | --- |
| First invocation | exactly three files; `NOT_ACCESSED_MISSING_POPULATION`; `NO_GO`; sole reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`; claim `resemblance_only` |
| Bundle/run objects | both absent |
| Broker protected/bundle/run/access input parameter | absent; parameters are only preregistration, caller digest, invocation ID, output directory |
| Receipt lineage | preregistration, candidate, outcome, gate and both preceding file digests all match |
| Second invocation with all outputs present | REJECTED; all bytes preserved |
| Only access-outcome file pre-existing | REJECTED; marker preserved; no other file created |
| Only gate-decision file pre-existing | REJECTED; marker preserved; no other file created |
| Only execution-receipt file pre-existing | REJECTED; marker preserved; no other file created |
| Caller digest disagreement | REJECTED before output-directory creation |
| Exact re-signed master mutation | ACCEPTED and brokered, demonstrating the P1 |

## Commands and results

- `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py tests/unit/test_w06_missing_population_gate.py`
  - initial sandboxed status `2`: local uv cache `.git` was unreadable under the sandbox;
  - authorised local-cache rerun status `0`: `23 passed in 0.27s`.
- `uv run --no-sync ruff check src/scouting/contracts/evaluation.py src/scouting/contracts/__init__.py src/scouting/evaluation scripts/run_w06_missing_population_gate.py tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_missing_population_gate.py`
  - status `0`: all checks passed.
- `uv run --no-sync mypy src/scouting/contracts/evaluation.py src/scouting/evaluation scripts/run_w06_missing_population_gate.py`
  - status `0`: no issues in 6 source files.
- `uv run --no-sync lint-imports`
  - status `0`: 3 contracts kept, 0 broken.
- `shasum -a 256 configs/evaluation/w06-protected-preregistration-v1.json tests/fixtures/w06/public-missing-population-gate-v1.json`
  - status `0`: `dc2fdc1ec4178f1d913cf58268aca5d48eb699f7135b0e627975ef8d89de2410` and `495f8148f68f36c1e98c3aff0f255a1009949d3ffcef583bdaaeda72dbc692eb`.
- `uv run --no-sync python /tmp/w06-protected-review.w4SfP1/review_matrix.py`
  - final status `0`: exact matrices above; exact master digests reproduced and broker executed only in a temporary directory.

## Scope confirmation

- Changed repository files: this report and
  `reports/reviews/W06/returns/W06-PROTECTED-NO-GO-REVIEW-05-R1.md` only.
- No Git operation, dependency change, dependency installation, protected expected-output
  access, repository production-output invocation, external/provider/credential access,
  tuning, or edit to source, tests, configs, orchestration, runs, data, docs, phase gates,
  readiness, or verification outputs was performed.
- Temporary harness and broker outputs were confined to `/tmp` and are not production
  evidence.
