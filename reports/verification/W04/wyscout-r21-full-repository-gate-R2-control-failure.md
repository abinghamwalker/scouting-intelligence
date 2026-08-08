# W04 R21 complete repository gate R2 — control failure evidence

## Decision

`REWORK`.

On 2026-07-30 the master ran the complete repository suite in the exact
`AGENTS.md` order. The first nine commands produced:

```text
uv sync --locked --all-groups
PASS — resolved 83 packages; audited 82 packages

uv run ruff format --check .
PASS — 355 files already formatted

uv run ruff check .
PASS — all checks passed

uv run mypy src/scouting scripts
PASS — no issues found in 40 source files

uv run lint-imports
PASS — 28 files, 41 dependencies, 3 contracts kept, 0 broken

uv run pytest -q
PASS — 1219 passed, 1 known Starlette deprecation warning in 164.47s

uv run bandit -q -r scripts src
PASS

uv run python scripts/install_local_git_guards.py --check
PASS — executable pre-push guard; simulated exit 1

uv run python scripts/verify_local_only.py
PASS — 25 checks, zero failures
```

The complete pytest result includes the corrected
`credential_separator_encoding` security authority fixture and all 107 R21
cross-authority cases. The former stale fixture is therefore resolved in the
repository-wide execution environment.

The tenth command failed:

```text
uv run python scripts/verify_phase.py --phase W04
FAIL
```

Exact failure codes:

```text
PHASE_GATE_READY
  state must be one of ['CHECKPOINTED', 'CLOSED', 'VERIFIED'], got 'READY'

TASKS_ACCEPTED_AND_EVIDENCED
  the accepted feature authority and reviewed R21 cross-authority tasks still
  carried pre-gate lifecycle states; two master-owned historical tasks also
  intentionally have no delegated subagent return

DECLARED_CHECKS_PASS
  no declared checks
```

This is an executable control-cycle defect, not an R21 authority or product
contradiction. The mandatory repository command must be usable during a
truthful in-progress `READY` phase, but the verifier admits only terminal
states. The R21 tasks and declared check cannot truthfully become accepted
until the fixed master gate evidence is materialized, while the gate packet
requires the complete repository verifier to pass before product work.

The final read-only commands were still executed:

```text
git status --short
expected retained W03/W04 working-tree changes listed; no unexplained external path

git remote
PASS — no output
```

No R21 PASS gate or product path was created by this failed attempt. The bounded
correction is limited to:

1. permitting `READY` as a repository-verifiable state without relaxing any
   dependency, task, evidence, declared-check, checkpoint, or zero-remote gate;
2. deriving master ownership from existing task packets so only master-owned
   tasks may omit a delegated subagent return; and
3. materializing the already-reviewed R21 acceptance and declared check before
   a fresh complete repository rerun.

No frozen semantic authority, product behavior, dependency policy, local-only
boundary, or approved architecture is changed.
