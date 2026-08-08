# W04 phase verifier READY correction independent review R1

## Decision

`REWORK`.

The `READY` eligibility correction itself is appropriately narrow, and the R2
task-ID binding closes the borrowed-master-packet defect. One fail-closed defect
remains in the master-owned empty-return exemption: a syntactically valid YAML
mapping that is not a complete task packet can grant the exemption when it
contains only a matching `task_id` and `assigned_role: master`.

This finding is bounded to `scripts/verify_phase.py` and its focused unit tests.
It does not require an R21 authority change, product implementation, dependency
change, local-only boundary change, or architecture revision.

## Fixed binding verification

All packet-specified physical SHA-256 bindings were verified before analysis:

| Artifact | Required SHA-256 | Observed SHA-256 | Result |
| --- | --- | --- | --- |
| `scripts/verify_phase.py` | `07e989a0bc454b6d45c671d5cc7dafecf9ac92fed86ce13fefb0be85c1ba2953` | `07e989a0bc454b6d45c671d5cc7dafecf9ac92fed86ce13fefb0be85c1ba2953` | PASS |
| `tests/unit/test_orchestration_controls.py` | `14045e33e0e34778706cb2395d8257b9e47c0deec3d84e8c5b136deca8c5ac8a` | `14045e33e0e34778706cb2395d8257b9e47c0deec3d84e8c5b136deca8c5ac8a` | PASS |
| R1 producer return | `2f50887ae1ae07e6103d974a7617ae7671e45aef402a10ddab68ffde296036a0` | `2f50887ae1ae07e6103d974a7617ae7671e45aef402a10ddab68ffde296036a0` | PASS |
| R2 producer return | `d7cf4fc9ddf653c86ed3ba117cd9384d33063f1f343d23f58ec8cd9174d3483c` | `d7cf4fc9ddf653c86ed3ba117cd9384d33063f1f343d23f58ec8cd9174d3483c` | PASS |

## READY lifecycle review

Static inspection shows that `READY` was added only to
`GATE_READY_STATES`. The verifier continues to execute and require:

- an allowed phase state;
- closed dependencies;
- accepted and evidenced tasks;
- required phase evidence;
- passing declared checks with retained evidence;
- zero Git remotes; and
- an existing start checkpoint, plus the unchanged accepted-checkpoint and
  clean-tree behavior for `CLOSED`.

An independent no-Git harness reproduced this behavior with local Git calls
replaced by fixed in-memory results. A fully evidenced `READY` fixture passed.
Separate mutations failed with the exact respective codes
`DEPENDENCIES_CLOSED`, `TASKS_ACCEPTED_AND_EVIDENCED`, `EVIDENCE_PRESENT`,
`DECLARED_CHECKS_PASS`, and `CHECKPOINT_STATE`. States outside the exact set
`READY`, `VERIFIED`, `CHECKPOINTED`, and `CLOSED` remain ineligible.

The correction therefore makes an in-progress phase eligible for repository
verification; it does not treat `READY` as phase completion, R21 acceptance, or
product authorization.

## Empty-return authority review

The R2 implementation correctly requires a non-empty string registry task ID,
at least one string packet path, a resolvable string-keyed YAML mapping, exact
`assigned_role: master`, and an exact packet/registry `task_id` match for every
referenced packet. The focused suite and independent targeted reproduction
reject borrowed, delegated, mixed, absent, malformed-YAML, missing-task-ID, and
non-string-task-ID cases.

### Finding 1 — schema-incomplete packet evidence grants the exemption

`packets_are_all_master_assigned()` does not validate that a loaded mapping is
a task packet. It checks only `assigned_role` and `task_id`. The following
schema-incomplete mapping omits every other mandatory packet field defined by
`verify_task_return.REQUIRED_PACKET_FIELDS`:

```yaml
task_id: W04-SKELETAL-01
assigned_role: master
```

Independent execution returned:

```text
(True, 'all referenced packets are master-assigned and task-ID matched')
```

Consequently, semantically invalid packet evidence can waive the retained
return requirement. That contradicts the review definition of done requiring
invalid packet evidence to fail closed. It also means the success detail
overstates what was proved: ownership and identity were found in a mapping,
but a valid packet was not established.

The smallest correction is to require each exemption-supporting mapping to
satisfy the repository's mandatory task-packet field contract before accepting
its ownership and matching identity. Focused coverage should prove that a
mapping with matching `task_id` and `assigned_role: master` but any missing
mandatory packet field is rejected. Existing positive W04 master packets and
all current negative cases must remain covered.

## Independent execution evidence

- `uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  passed: 2 files already formatted.
- `uv run ruff check scripts/verify_phase.py tests/unit/test_orchestration_controls.py`
  passed: all checks passed.
- `uv run mypy scripts/verify_phase.py` passed: no issues in 1 source file.
- `uv run pytest -q tests/unit/test_orchestration_controls.py` passed: 14 tests
  in 0.39 seconds.
- The targeted borrowed, delegated, mixed, missing/malformed, and invalid-ID
  selection passed: 5 tests in 0.06 seconds.
- The independent READY harness passed its complete fixture and produced the
  expected failure code for each dependency, task, evidence, declared-check,
  and checkpoint mutation.
- The independent skeletal-packet adversarial case reproduced the remaining
  exemption defect exactly.

## Scope and authorization boundary

This review does not accept the correction, the R21 gate, or any Bronze,
Silver, Gold, or product path. No implementation, test, orchestration,
dependency, lock, authority, registry, data, or product file was changed. No
Git operation, external service, remote, deployment, or delegation was used.

