# W04 Wyscout data contracts independent review R3

## Review identity and disposition

- Task: `W04-DATA-CONTRACTS-REVIEW-01`, revision `R3`
- Role: fresh independent reviewer
- Disposition: **REWORK**
- Open findings: P0 `0`, P1 `3`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

All three requested public-constructor probes reproduced. The packet checks pass,
but the R3 contracts still admit proof-bearing values contrary to frozen R20/R21
authority. These are bounded contract/test defects; they do not require or authorise
an architecture, product, provider-rights, storage, dependency, or scope revision.

## Frozen-input identity

The packet bindings and governing bytes were recomputed unchanged:

| Material | SHA-256 | Result |
|---|---|---|
| `src/scouting/contracts/wyscout_data.py` | `53abc69b85a1a60c13107a8b0a09ee6e066e792b1667c866cf9a9c3f5fd242ff` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `f13b5ccb8930bef22c94f74feeda1b66c87224704458c0460de022e66af3764b` | match |
| R3 producer return | `338c01c40b1913db384b6e0c02ea3d1bdbb01f581f6c3de84baabe54769b36a9` | match |
| R2 independent review | `38f2bb9fd6971bf1e9a38aed44dd2acd59b3187124204b69152ad43c80bfcd8a` | match |
| identity acceptance v1 | `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86` | match |
| source snapshot manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | match |
| field acceptance v2 | `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436` | match |
| possession acceptance v2 | `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1` | match |
| supported-feature acceptance v1 | `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c` | match |
| product-contract preimage v1 | `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` | match |
| schema-bundle preimage v1 | `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f` | match |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | unchanged |
| R21 design | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | unchanged |

The accepted supported roster remains exactly `action_count`,
`coordinate_known_action_count`, `match_count`, and
`resolved_possession_action_count`.

## Independent public-constructor probe

Command: `uv run python -c '<inline validated-constructor matrix using the focused test fixtures>'`

Exit status: `0`. No `model_construct` or unchecked copy/update path was used. Exact
mutations and results:

```text
PROBE1: replace all six SilverPlayerMatchFact coverage dimensions 1/1 -> 2/2;
        validate the fact; pass it to Gold with exact aggregate coverage 2/2.
PROBE1_ACCEPTED [('identity', 2, 2), ('lineup', 2, 2),
 ('action', 2, 2), ('coordinate', 2, 2), ('possession', 2, 2),
 ('temporal', 2, 2)] in both Fact and Gold

PROBE2: ActionPosition(x=-1, y=60, within_accepted_bounds=False);
        validate Action, singleton Possession, Fact, and Gold.
PROBE2_ACCEPTED False 1 1
  (Fact coordinate_known_action_count=1; Gold coordinate_known_action_count=1)

PROBE3: exact pair (1,10), state ELIGIBLE_RESOLVED, one action only;
        validate Action, singleton Possession, and Fact.
PROBE3_ACCEPTED ELIGIBLE_RESOLVED 1 1
  (one possession action; Fact resolved_possession_action_count=1)
```

## Open findings

### W04DCR3-P1-001 — fact coverage is forgeable and Gold aggregates the forgery

`SilverPlayerMatchFact` accepts internally consistent `GoldCoverage` but never derives
its six numerators and denominators from the fact's closed action, possession, lineup,
identity, and temporal evidence (`wyscout_data.py:1853-1973`). Changing every fixture
dimension from `1/1` to `2/2` therefore validates. `_aggregate_fact_coverage` then sums
the fact-declared values (`wyscout_data.py:1986-2090`), so `GoldPlayerWindow` accepts
the forged `2/2` values as an exact aggregate (`wyscout_data.py:2203-2205`). This
violates R20 section 6.3, where coverage integers are authority and each denominator/
numerator has an evidence-derived population.

Required bounded correction: derive or validate every fact coverage dimension against
its closed evidence before Gold aggregation. Add the coordinated Fact-and-Gold `1/1`
to `2/2` public-constructor regression, not only a Gold-only drift test.

### W04DCR3-P1-002 — out-of-bounds position is counted as accepted coordinate evidence

`ActionPosition` correctly preserves `x=-1` with `within_accepted_bounds=False`
(`wyscout_data.py:1205-1217`), but the fact count uses
`sum(bool(action.action_positions) ...)` (`wyscout_data.py:1950-1953`). The invalid
position consequently produces `coordinate_known_action_count=1`, which Gold then
sums (`wyscout_data.py:2193-2200`). Frozen field v2 specifies inclusive `0..100` and
`anomaly_policy: PRESERVE_AND_INELIGIBLE`; R20 section 6.3 counts only applicable
actions whose required axes are numeric and within bounds.

Required bounded correction: preserve the anomalous position as evidence but exclude
it from accepted coordinate coverage/count eligibility; add out-of-bounds and mixed-
position direct-constructor regressions through Fact and Gold.

### W04DCR3-P1-003 — contested `(1,10)` is promoted without following resolved control

`SilverAction` treats every admitted pair except the eight statically ineligible pairs
as immediately `ELIGIBLE_RESOLVED` when a team exists (`wyscout_data.py:1225-1309`).
`SilverPossession` then accepts any such action as a singleton sequence
(`wyscout_data.py:1375-1440`), and the fact counts its single membership as resolved
(`wyscout_data.py:1924-1960`). Frozen possession v2 classifies `(1,10)` as
`CONTESTED`, with no control team and
`BUFFER_UNTIL_FOLLOWING_RESOLVED_POSSESSION`; R20 requires contested attachment only
under that sequence rule. The singleton has no following resolved control.

Required bounded correction: derive final eligibility from the possession-v2
predicate plus same-period sequence state, retaining contested actions buffered or
unassigned until a following deterministic possession exists. Add singleton, period-
end, and following-control public-constructor regressions.

## Prescribed check results

| Command | Exit/result |
|---|---|
| `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; all checks passed |
| `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; no issues in 2 files |
| `uv run lint-imports` | `0`; 30 files, 46 dependencies, 3 contracts kept, 0 broken |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` | `0`; 437 passed in 88.83s |
| `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` | `0`; no findings |
| `uv run python scripts/verify_local_only.py` | `0`; PASS, 25/25, zero configured remotes |

The first sandboxed `lint-imports` and `bandit` attempts exited `2` because the
workspace sandbox denied reads of the shared uv cache `.git`; the exact commands were
rerun with approved read access and passed as reported. No dependency or environment
state changed.

## Recommendation and scope confirmation

Recommendation: **REWORK**. Stop product implementation from relying on this contract
revision until all three P1 findings fail closed and a fresh review passes.

- Frozen authorities, preimages, source evidence, R20/R21, implementation, tests,
  dependencies, lock state, product bytes, manifests, serializers, receipts, runtime,
  and build configuration were not modified.
- No architecture revision, provider access, network/cloud/container/external-service
  action, endpoint, deployment, or hosted CI was needed or performed.
- Review scope remained the three requested direct-constructor failures plus the
  packet's focused checks; no broader feature or product claim was introduced.
- Only this review and its return artifact were written. No Git operation,
  delegation, or self-approval was performed.
