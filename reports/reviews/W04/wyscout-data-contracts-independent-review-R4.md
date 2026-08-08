# W04 Wyscout data contracts independent review R4

## Review identity and disposition

- Task: `W04-DATA-CONTRACTS-REVIEW-01`, revision `R4`
- Role: fresh independent reviewer
- Disposition: **REWORK**
- Open findings: P0 `0`, P1 `2`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

R4 closes the three R3 finding families at the submitted, caller-selected evidence
boundary. It does not close the packet's deeper source-completeness and simultaneous-
action challenges. A consistent truncated period still validates through Gold, and
two cross-team CONTROL actions at the same period-relative clock leave the first
action resolved. Both are material fail-open routes into supported Gold counts and
coverage.

The needed corrections are bounded executable-contract and regression-test work.
**No finding genuinely requires an architecture revision**, changed frozen authority,
new feature, product byte, serializer, provider access, dependency, storage surface,
runtime, or broader scope.

## Frozen-input identity

All packet fixed bindings were recomputed from the reviewed bytes:

| Material | SHA-256 | Result |
|---|---|---|
| `src/scouting/contracts/wyscout_data.py` | `2ca2862550c48a8db899f25c26612d694a7ca8041416cf0aae4dcd39b5a2bb5e` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `0ddb9e2bd31dded899a68b7b6344cf17321dffe947ab6dffc98267eb918bdc69` | match |
| R4 producer return | `f66c4ea9133a23394d67d81d4f7badf989be39594eb2fec7165f9928a429be68` | match |
| R3 independent review | `a86e30a1d56ae1c88f9bbb36e067f74f4fb234664a4ba08e9e05589b2e2bb066` | match |
| identity acceptance v1 | `37764392cdaf9626ffaff26e119fb142218d36489e87a8b1d55402e3e2dc7f86` | match |
| source snapshot manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | match |
| field acceptance v2 | `beb66d3a8f07e41fe0fa5fe82fee06e3602f3c3045f48d2a11ca6fa9f20cc436` | match |
| possession acceptance v2 | `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1` | match |
| supported-feature acceptance v1 | `d3b3c552784f4734f6b002569d9add1b4dd2d2eaaed57643a8ca4d5226fca78c` | match |
| product-contract preimage v1 | `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` | match |
| schema-bundle preimage v1 | `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f` | match |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | unchanged |
| R21 design | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | unchanged |

After the independent probes and disposition were complete, supplemental master
context was supplied and read at SHA-256
`cd6243bc96081281230a4c8b60161ad5d191904a6b19f57ffc84b24ee524a95f`.
It is consistent with, but was not a substitute for, this review's reproduction.

The accepted Gold roster remains exactly:

1. `action_count`
2. `coordinate_known_action_count`
3. `match_count`
4. `resolved_possession_action_count`

No outcome, rate, minutes, per-90, role, or fifth feature was introduced.

## R3 finding closure reproduction

Command: `uv run python -c '<inline public-constructor R4 adversarial matrix>'`

The matrix used `model_validate` and ordinary checked constructors only; it used no
`model_construct`, unchecked copy/update, serializer, or product write.

```text
R3_SIX_DIM_FACT_FORGERY REJECTED
R3_SIX_DIM_GOLD_FORGERY REJECTED
R3_COORDINATE out_of_bounds VALID_ZERO 0 0 FORGERY_REJECTED True True
R3_COORDINATE mixed VALID_ZERO 0 0 FORGERY_REJECTED True True
R3_COORDINATE three_position VALID_ZERO 0 0 FORGERY_REJECTED True True
R3_SINGLETON_CONTESTED VALID_ZERO 0 0 FORGERY_REJECTED True True
```

Results:

- W04DCR3-P1-001 is closed at the selected Fact/Gold evidence boundary: all six
  internally consistent `1/1 -> 2/2` dimension mutations are rejected at Fact, and
  coordinated Gold mutations are rejected.
- W04DCR3-P1-002 is closed: out-of-bounds, mixed-validity, and three-position
  evidence remains preserved but produces coordinate count `0` in both Fact and
  Gold; forged count `1` is rejected at both boundaries.
- W04DCR3-P1-003 is closed for singleton/period-end contested evidence: the valid
  Fact and Gold resolved count is `0`, and forged count/state promotion is rejected.
  The submitted following-control positive case also validates in the focused suite.

These closures are necessary but insufficient because the constructors can still
select the evidence population from which those exact values are derived.

## Independent R4 adversarial probes

### Period truncation through Gold

Starting from the submitted two-action following-control fixture, the probe retained
both physical ACTION rows in lineage but removed the contested ordinal `0` from the
period sequence, lowered `period_action_count` from `2` to `1`, and consistently
rebuilt the remaining `SilverAction`, singleton `SilverPossession`,
`SilverPlayerMatchFact`, and `GoldPlayerWindow`.

```text
TRUNCATION_THROUGH_GOLD ACCEPTED lineage_action_ordinals= (0, 1) sequence_action_ordinals= (1,) fact_source_ordinals= (1,) fact_action_count= 1 gold_action_count= 1
```

The same root was challenged by giving another sequence entry an arbitrary UUID
that is not `canonical_source_uuid(ACTION, source_event_record_id)`:

```text
UNBOUND_OTHER_SEQUENCE_ID ACCEPTED fake_id_is_canonical= False own_state= ELIGIBLE_RESOLVED groups= ((UUID('cc8d822e-a0f5-50e0-a290-a324f9aaff14'), (UUID('f6298526-f978-58fb-890a-cedd787f338f'), UUID('00000000-0000-4000-8000-000000000001'))),)
```

### Equal-clock cross-team CONTROL through Gold

The probe built two CONTROL actions at identical `period_rank` and
`period_elapsed_seconds`, with different teams, players, source ordinals, and source
event IDs. The canonical source ordinal merely serialized simultaneous evidence; it
did not establish football order.

```text
EQUAL_CLOCK_CROSS_TEAM_GROUPS ((UUID('cc8d822e-a0f5-50e0-a290-a324f9aaff14'), (UUID('f6298526-f978-58fb-890a-cedd787f338f'),)),)
EQUAL_CLOCK_THROUGH_GOLD ACCEPTED states= ('ELIGIBLE_RESOLVED', 'INELIGIBLE_UNMAPPED') possession_ids= (UUID('f6298526-f978-58fb-890a-cedd787f338f'),) sequence_ordinals= (0, 1) fact_source_ordinals= (0,) gold_resolved_count= 1
```

The second, causally decisive other-player row at ordinal `1` is also absent from the
Fact and Gold source-row closure. This is recorded under W04DCR4-P1-001 because the
same source-population/provenance correction closes it; it is not counted as a third
finding.

## Open findings

### W04DCR4-P1-001 — complete period and six coverage populations remain caller-selected

`PossessionPeriodSequence` labels evidence complete with `Literal[True]` and checks
only that `period_action_count == len(actions)` plus uniqueness/order/scope
(`wyscout_data.py:1344-1374`). It never reconciles the tuple with an independently
admitted Bronze/source action population. `PossessionSequenceAction` checks the
physical row family and ordinal but does not bind `action_id` to its provider event
ID or the remaining predicate/order fields to exact Bronze evidence
(`wyscout_data.py:1305-1332`). `SilverAction` requires sequence rows merely to occur
somewhere in lineage and binds only its own entry (`wyscout_data.py:1524-1552`).

The incompleteness then composes upward. A Fact discovers period sequences only from
the caller-selected row-player actions and asks those selected sequences to cover
those same selected actions (`wyscout_data.py:2181-2213`). Its source rows derive
only from selected lineups/actions (`wyscout_data.py:2248-2255`). Its six coverage
populations are then calculated from those selected actions and lineups, with lineup
hard-coded to `1/1` and temporal evidence counting only five dependencies, one match,
and selected actions (`wyscout_data.py:2297-2338`). Gold derives source rows,
features, and aggregate coverage only from selected Facts
(`wyscout_data.py:2599-2641`). Every local equality can therefore be true while a
source action, period, candidate fact, identity occurrence, possession-eligible
action, or temporal dependency group has been omitted.

This violates R20's complete deterministic period semantics
(`wyscout-schema-design-R20.md:1428-1434`) and exact occurrence/population equations
(`wyscout-schema-design-R20.md:1494-1510`). The probe demonstrates material impact:
an omitted source action changes the supported Fact and Gold `action_count`, while
the resulting coverage still presents itself as derived and complete.

Required bounded correction: make the complete period, player-match candidate, and
six coverage populations independently recomputable from closed admitted
Bronze/source evidence. A bounded public factory or constructor evidence field may
receive the complete admitted match/action/lineup populations, but validation must
prove exact population equality rather than trust a literal flag, mirrored count,
caller-selected subset, or digest of that same subset. Bind every sequence entry's
action identity and predicate/order inputs to its admitted source evidence. Carry all
causal sequence source rows into possession, Fact, and Gold provenance. Add direct
regressions for truncation through Gold, whole-period omission, other-player causal
entries, noncanonical sequence action IDs, and all six R20 source populations.

### W04DCR4-P1-002 — equal-clock cross-team uncertainty leaves the first action resolved

When a CONTROL action encounters an active different team at the same clock,
`_resolved_possession_groups` clears only `active_index`, `active_team`,
`active_clock`, and the pending contested buffer (`wyscout_data.py:1395-1409`). The
first simultaneous action has already been appended to `groups`, and the branch does
not remove or invalidate it. The function consequently returns the first action as a
resolved possession (`wyscout_data.py:1434`). Silver Action, Possession, Fact, and
Gold faithfully accept that erroneous group and count one resolved action.

R20 says cross-team equal clocks are uncertain and only deterministic sequences are
resolved/Gold-eligible (`wyscout-schema-design-R20.md:1428-1434`). Possession-v2 is
more explicit: `equal_clock_cross_team_policy` is
`UNCERTAIN_BOUNDARY_UNASSIGNED` (`wyscout-v5-possession-taxonomy-v2.yaml:32-52`), and
R21 permits `ELIGIBLE_RESOLVED` only for a deterministically resolved same-period
possession (`wyscout-schema-design-R21.md:536-547`). Source ordinal is an ordering
tiebreaker, not authority to resolve simultaneous football control.

Required bounded correction: when different-team CONTROL actions share a clock,
unassign every action at that ambiguous clock and any contested buffer whose
resolution depends on it. Preserve only genuinely deterministic pre-clock group
members, and do not let source ordinal choose a team. Ensure possession and Fact/Gold
source provenance retains every causal sequence row even when it is ineligible.
Add direct two-action and pre-existing-possession equal-clock regressions through
Action, Possession, Fact, and Gold.

## Prescribed check results

| Command | Exit/result |
|---|---|
| `uv run ruff format --check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; all checks passed |
| `uv run mypy src/scouting/contracts/wyscout_data.py tests/contracts/test_wyscout_data_contracts.py` | `0`; no issues in 2 source files |
| `uv run lint-imports` | `0`; 30 files, 46 dependencies, 3 contracts kept, 0 broken |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py` | `0`; 452 passed in 73.68s |
| `uv run bandit -q -r src/scouting/contracts/wyscout_data.py` | `0`; no findings |
| `uv run python scripts/verify_local_only.py` | `0`; PASS, 25/25 and zero configured remotes |

The first sandboxed `lint-imports` and Bandit attempts exited `2` solely because the
workspace sandbox denied shared uv-cache metadata reads. The exact commands were
rerun with approved read access and passed as reported; no dependency or environment
state changed.

The complete implementation and focused test module were read. The passing submitted
suite is necessary but does not exercise either accepted adversarial chain above.

## Recommendation and scope confirmation

Recommendation: **REWORK**. Do not allow product implementation to rely on R4 until
both P1 findings fail closed, fresh independent review passes with zero P0-P2, and
the master gate accepts the corrected bytes.

- No architecture revision is needed or opened. The frozen contracts already require
  complete source-bound evidence and conservative equal-clock unassignment; the
  correction fits the existing in-memory contract/factory surface.
- No implementation, test, config, authority, preimage, R20/R21, source, prior
  review, producer return, dependency, lockfile, product, manifest, receipt, runtime,
  serializer, build, or verification byte was modified.
- No provider access, network, cloud service, container, endpoint, hosted CI,
  deployment, external service, or product write was used or created.
- Only this review and its return artifact were written. No Git operation,
  delegation, or self-approval was performed.
