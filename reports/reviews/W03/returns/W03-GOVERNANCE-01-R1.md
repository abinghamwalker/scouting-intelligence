# Subagent return

## Task

- task_id: W03-GOVERNANCE-01
- objective: Materialise the approved P0 claim, evaluation, synthetic-data-rights,
  security and W03 architecture boundaries as local control documents.

## Files changed

- docs/architecture/product-claim.md
- docs/architecture/evaluation-contract.md
- docs/architecture/threat-model.md
- docs/architecture/w03-synthetic-spine.md
- docs/adr/0003-local-postgres-pgvector.md
- configs/policies/authorization.yaml
- configs/policies/data-rights.yaml
- configs/environments/w03-local-review.yaml
- reports/reviews/W03/returns/W03-GOVERNANCE-01-R1.md

## Summary

- Defined the evidence-only role-aware discovery claim, analyst/scout/approver jobs,
  resemblance-not-outcome boundary, explicit non-claims and R0/R1/R2 cut lines.
- Froze a synthetic-only W03 evaluation contract with strict replay eligibility,
  protected-fixture access, required fail-closed negatives, exact acceptance metrics
  and a no-partial-pass minimum gate.
- Recorded a design-stage local threat model for identity mismatch, future leakage,
  path escape, tenant/authZ failure, confidential evidence, audit tampering, secrets,
  misuse, rights misclassification, cache confusion and local service exposure. It
  explicitly does not claim completed security verification.
- Defined the modular-monolith topology, import direction and one synthetic role
  brief → policy-safe retrieval → shortlist → append-only audit journey, keeping model
  evidence, product policy and human decisions separate.
- Accepted local PostgreSQL/pgvector and Redis Compose services, rejected premature
  vector/streaming/cloud/service splits and named evidence-based revisit triggers.
- Added deny-by-default analyst, scout, approver and admin permissions; a generated,
  local, non-personal, non-exported synthetic data-rights class; and a loopback-only
  local-review environment with external identity, telemetry, model calls and
  deployment disabled.
- Used only the two approved local HTML plans as decision authority. No user research,
  provider licence, real-data, pilot, model-performance or security-test evidence was
  invented.

## Tests run

- command: `uv run python -c "from pathlib import Path; import yaml; [yaml.safe_load(path.read_text()) for path in [Path('configs/policies/authorization.yaml'), Path('configs/policies/data-rights.yaml'), Path('configs/environments/w03-local-review.yaml')]]"`
  - exit status: 0
  - result: All three new YAML control files parsed successfully.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: `PASS`; all 21 local-only, one-root-uv, configuration, path and Git-safety
    checks passed with no failures.

## Artifacts/evidence

- docs/architecture/product-claim.md
- docs/architecture/evaluation-contract.md
- docs/architecture/threat-model.md
- docs/architecture/w03-synthetic-spine.md
- docs/adr/0003-local-postgres-pgvector.md
- configs/policies/authorization.yaml
- configs/policies/data-rights.yaml
- configs/environments/w03-local-review.yaml
- reports/reviews/W03/returns/W03-GOVERNANCE-01-R1.md

## Risks

- These are normative plan-derived controls, not evidence that runtime enforcement,
  real-data rights, security assurance, user research or a pilot exists.
- The role/action vocabulary, protected fixture and fail-closed cases must be
  implemented and independently tested by their owning W03 packets before the W03 gate.
- Single-tenant synthetic checks cannot establish multi-tenant isolation, real provider
  identity quality or confidential real-data handling.

## Follow-up items

- Master: read back the nine owned files and independently rerun both packet acceptance
  checks.
- Downstream W03 owners: implement and test these frozen policy, temporal, storage,
  audit and journey boundaries without widening the evidence claims.

## Scope confirmation

- no Git operations: confirmed; no direct or state-changing Git command was run
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

