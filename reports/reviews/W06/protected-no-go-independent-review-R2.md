# W06 protected NO_GO independent review R2

## Verdict

- Task: `W06-PROTECTED-NO-GO-REVIEW-05-R2`
- Verdict: `ACCEPT`
- P0: `0`
- P1: `0`

The exact two-field R1 defect is closed. The independently reconstructed and re-signed
fail-order/stop-rule witness retained protocol digest
`0315215e86788e773050637a2ac6d6cda70464efbdc4297f28c2cac3b27a3f4e` and
preregistration digest
`5f71bc77d1ea5430e3663ac5e0f0f84697b07c00776a4f3a1ce678a24cb3dffe`, but validation
now rejected it before broker invocation or output-directory creation. Both fields also
rejected when mutated and re-signed individually.

The accepted config identity remains preregistration digest
`13d26404f788466993d7cd3663c787e6da182005dd68c0dd48c70783f7c20ae5`; the frozen
candidate, inventory, claim boundary and missing-population behavior are unchanged.

## Exact R1 witness

- Swapped the first two `fail_closed_order` entries:
  `AUTHENTIC_GOVERNED_EXPERT_EVIDENCE` and `NONEMPTY_PROTECTED_POPULATION`.
- Replaced `stop_rule` with `Proceed despite missing expert evidence.`.
- Recomputed `protocol_digest` and `preregistration_digest` independently.
- Literally asserted both R1 identities above.
- Result: `REJECTED_BEFORE_BROKER`; the temporary broker-output directory remained absent.

## Candidate substitution matrix

Every mutation was re-signed at candidate and preregistration layers.

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
| unsigned `candidate_digest` replacement | REJECTED |

## Protocol substitution matrix

Every substantive mutation was re-signed at protocol and preregistration layers.

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
| `fail_closed_order` mutation, independently re-signed | REJECTED |
| `stop_rule` replacement, independently re-signed | REJECTED |
| unsigned `protocol_digest` replacement | REJECTED |
| exact combined R1 mutation, re-signed | REJECTED BEFORE BROKER |

The retained roster is primary `ndcg@10`; secondary precision at 5/10, recall at 5/10,
NDCG at 5, coverage at 5/10, pair preference, and conditional real-reviewer agreement;
unsupported `k=25`; metadata and raw-Euclidean baselines; shuffled-label and conditional
shuffled-pair nulls; query bootstrap seed 20260804, 2000 percentile resamples at 0.95
confidence; and the exact minimum useful effect.

## Inventory substitution matrix

Every substantive mutation was re-signed at inventory and preregistration layers.

| Inventory field | Result |
| --- | --- |
| authentic governed human relevance reviewers `0 -> 1` | REJECTED |
| governed relevance judgements `0 -> 1` | REJECTED |
| governed pair preferences `0 -> 1` | REJECTED |
| protected queries `0 -> 1` | REJECTED |
| reordered `missing_evidence` | REJECTED |
| unsigned `inventory_digest` replacement | REJECTED |

The retained inventory remains four zero counts and, in order,
`MISSING_EXPERT_RELEVANCE_EVIDENCE` and `MISSING_PROTECTED_POPULATION`.

## One-use and broker matrix

All invocations used newly created operating-system temporary directories.

| Case | Result |
| --- | --- |
| Broker parameters | only preregistration, caller digest, invocation ID, output directory; no protected/bundle/run/access input |
| First invocation | exactly three files; `NOT_ACCESSED_MISSING_POPULATION`; protected outputs false; `NO_GO`; sole reason `MISSING_EXPERT_RELEVANCE_EVIDENCE`; claim `resemblance_only` |
| Bundle/run objects | both absent |
| Receipt lineage | preregistration, candidate, outcome, gate, access-file and gate-file digests all match |
| Second invocation with all outputs present | REJECTED; all bytes preserved |
| Only access-outcome file pre-existing | REJECTED; marker preserved; no other file created |
| Only gate-decision file pre-existing | REJECTED; marker preserved; no other file created |
| Only execution-receipt file pre-existing | REJECTED; marker preserved; no other file created |
| Caller digest disagreement | REJECTED before output-directory creation |
| Exact re-signed R1 mutation | REJECTED before broker/output-directory creation |

## Commands and results

- `uv run --no-sync pytest -p no:cacheprovider -q tests/contracts/test_w06_evaluation_contracts.py tests/unit/test_w06_evaluation_metrics.py tests/contracts/test_w06_robustness_contracts.py tests/unit/test_w06_robustness.py tests/unit/test_w06_missing_population_gate.py`
  - initial sandbox status `2`: existing local uv cache `.git` was unreadable;
  - authorised local-cache rerun status `0`: `24 passed in 0.46s`.
- `uv run --no-sync ruff check src/scouting/contracts/evaluation.py tests/unit/test_w06_missing_population_gate.py`
  - initial sandbox status `2`; authorised local-cache rerun status `0`: all checks passed.
- `uv run --no-sync mypy src/scouting/contracts/evaluation.py`
  - initial sandbox status `2`; authorised local-cache rerun status `0`: no issues in one source file.
- `shasum -a 256 configs/evaluation/w06-protected-preregistration-v1.json tests/fixtures/w06/public-missing-population-gate-v1.json`
  - status `0`: config `dc2fdc1ec4178f1d913cf58268aca5d48eb699f7135b0e627975ef8d89de2410`;
    fixture `495f8148f68f36c1e98c3aff0f255a1009949d3ffcef583bdaaeda72dbc692eb`.
- `uv run --no-sync python /tmp/w06_r2_review_matrix.py`
  - initial sandbox status `2`; corrected authorised local-cache run status `0`; exact witness and all matrices above passed.

## Remaining risk and scope

No P0/P1 capable of changing the protected decision or claim was identified. Final
acceptance remains with the master.

Changed repository files are this report and the mandatory return only. No Git operation,
dependency change or installation, protected expected-output access, repository
production-output invocation, external/provider/credential access, or edit to source,
tests, configs, orchestration, data, runs, docs, readiness, phase-gate or verification
outputs was performed. The review harness and broker outputs were confined to `/tmp` and
are not production evidence.
