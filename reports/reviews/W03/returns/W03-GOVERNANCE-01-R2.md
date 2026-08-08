# Subagent return

## Task

- task_id: W03-GOVERNANCE-01
- objective: Correct the missing workflow state-machine boundary and add semantic
  enforcement for the accepted W03 governance YAML.

## Files changed

- docs/architecture/workflow-state-machines.md
- scripts/validate_w03_governance.py
- tests/governance/test_w03_policies.py
- reports/reviews/W03/returns/W03-GOVERNANCE-01-R2.md

## Summary

- Defined normative role-brief and shortlist state machines with stable ownership,
  immutable versions, optimistic locking, legal/denied transitions, explicit human
  approvals, controlled rejection/hold reasons, tenant-aware visibility, non-fabricated
  retention, and append-only material-action audit semantics.
- Marked persisted collaboration, local users/sessions, assignments, comments,
  observation UI, notifications, evidence packs, concurrency UX and full workflow tests
  as W08 implementation. W03 retains only the normative boundary and minimal synthetic
  seam.
- Added a read-only semantic validator for the three accepted W03 control files. It
  reports actionable field-level failures for missing policy IDs/roles/actions/global
  denies, permissive defaults, widened data rights, enabled exports, non-loopback binds,
  or remote/cloud/external settings.
- Added 34 focused tests covering the accepted baseline plus adversarial mutations for
  all four roles, action mappings, defaults, global denies, synthetic-only rights,
  prohibited uses, every export flag, required services, network/service binding,
  remote/cloud settings, read-only file behaviour and absence of network calls.
- Did not change any accepted R1 YAML policy.

## Tests run

- command: `uv run python scripts/validate_w03_governance.py`
  - exit status: 0
  - result: Final acceptance run `PASS`; zero semantic failures.
- command: `uv run pytest -q tests/governance/test_w03_policies.py`
  - exit status: 2 on first attempt
  - result: Test collection exposed that this repository's pytest path did not include
    the root; corrected the test-only import bootstrap within the allowed file.
- command: `uv run pytest -q tests/governance/test_w03_policies.py`
  - exit status: 0 after correction
  - result: Initial corrected suite passed 29 tests; final expanded acceptance suite
    passed 34 tests in 0.28 seconds.
- command: `uv run ruff format --check scripts/validate_w03_governance.py tests/governance/test_w03_policies.py`
  - exit status: 1 on first attempt
  - result: Validator required mechanical Ruff formatting.
- command: `uv run ruff format scripts/validate_w03_governance.py tests/governance/test_w03_policies.py`
  - exit status: 0
  - result: First correction formatted one file; the final pre-acceptance invocation
    reported both files unchanged.
- command: `uv run ruff format --check scripts/validate_w03_governance.py tests/governance/test_w03_policies.py`
  - exit status: 0 after formatting
  - result: Two files already formatted.
- command: `uv run ruff check scripts/validate_w03_governance.py tests/governance/test_w03_policies.py`
  - exit status: 0
  - result: All checks passed.
- command: `uv run mypy scripts/validate_w03_governance.py`
  - exit status: 0
  - result: No issues found in one source file.
- command: `uv run bandit -q scripts/validate_w03_governance.py`
  - exit status: 2 on first attempt
  - result: Workspace sandbox denied uv access to its external package cache; no code
    finding was produced.
- command: `uv run bandit -q scripts/validate_w03_governance.py`
  - exit status: 0 when rerun with approved uv cache access
  - result: No Bandit findings.
- command: `uv run python scripts/validate_w03_governance.py`
  - exit status: 0 on final post-format rerun
  - result: `PASS`; zero semantic failures.
- command: `uv run pytest -q tests/governance/test_w03_policies.py`
  - exit status: 0 on final post-format rerun
  - result: 34 tests passed in 0.28 seconds.

## Artifacts/evidence

- docs/architecture/workflow-state-machines.md
- scripts/validate_w03_governance.py
- tests/governance/test_w03_policies.py
- reports/reviews/W03/returns/W03-GOVERNANCE-01-R2.md
- validator identifier: `validate_w03_governance`, schema version 1

## Risks

- The validator proves the frozen YAML's semantic configuration, not runtime
  authorisation, database isolation, security assurance or workflow implementation.
- The workflow retention duration remains intentionally unset until an approved
  retention/data-rights policy supplies one; W03 permits no hard-delete transition.
- A future accepted policy-schema change must update this validator and its negative
  tests in a separately bounded packet.

## Follow-up items

- Master: read back the four R2 files and independently rerun all six packet acceptance
  checks.
- W08 owners: implement the full collaborative state machines without weakening these
  ownership, approval, visibility, versioning, retention or audit invariants.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
