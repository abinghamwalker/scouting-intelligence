# Subagent return

## Task

- task_id: `W04-REPOSITORY-PROGRESSION-GUARD-01-R1`
- objective: Correct only the two stale lower-authority repository progression fixtures so present governed downstream paths require direct validation of the exact accepted R21 gate evidence.

## Files changed

- `tests/contracts/test_w04_field_semantic_v2_authority.py`
- `tests/contracts/test_w04_possession_semantic_v2_authority.py`
- `reports/reviews/W04/returns/W04-REPOSITORY-PROGRESSION-GUARD-01-R1.md`

## Summary

- Preserved both lower-authority lifecycle validators and their synthetic pre-gate fail-closed behaviour unchanged.
- Added one closed four-path R21 gate-evidence validator to each owned test module. Each validator requires the exact gate report, canonical gate record, complete independent review and gate return paths; non-empty bytes; an exact canonical five-key gate record; `decision=PASS`; the exact gate and review paths; `review_recommendation=PASS`; and the SHA-256 of the complete supplied review bytes.
- Changed only each actual-repository progression test: when a governed identity/runtime/product path is present, it must first validate the exact accepted R21 gate evidence. The field validator is still invoked with its lower-authority downstream block disabled only after that direct gate validation; possession acceptance alone still cannot establish the gate.
- Added adversarial coverage in both modules for every missing evidence path, an additional path, a partial record, changed decision/path/recommendation/digest, changed review bytes and noncanonical gate JSON.
- Removed no governed paths and changed no R20/R21 authority, source, data, runtime or product bytes.

## Tests run

- command: `uv run ruff format --check tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run pytest -q tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `353 passed in 22.91s`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 of 25 checks; zero configured remotes and local pre-push guard intact

## Artifacts/evidence

- superseded field test SHA-256: `12a93afb72019f36e2c775a8e2898029fac8a26466e57114430edcc39e575d2f`
- corrected field test SHA-256: `47644d44fa846fb467742f0f094264d22333fa6d22f9ea07fe3f2618ce012f46`
- superseded possession test SHA-256: `dd4167747b71203390ba04d7c0899dc98099e203368ba5b3c3942b1b9a6e3116`
- corrected possession test SHA-256: `c4c7a25947ec84a5b2ecf9b80279f5b6fd410a9b98247defe74d5de7d4a32294`
- accepted R21 gate bindings were verified before editing: gate record `980303642f5c58876ed157698a5ea8f25ee79acef3c9faeaf015266cf547f168`; review `e9eca309986140ddfe40c66645a3f640777ff700e6a7187d43f020060d35c070`; gate report `656769e7e9fe894421056230344ed9e976d583895cabe42600d1a2294042e14e`; gate return `8f45128b4609b2a575a9f7da5e147dd95c5ef83f203812d27ac97e6fbd9eb051`
- failed-gate evidence: 13 adversarial cases in each module fail closed for missing report/record/review/return, additional path, partial record, wrong decision/gate path/review path/recommendation/review digest, changed review bytes and noncanonical record; the complete focused suite passes.
- return: `reports/reviews/W04/returns/W04-REPOSITORY-PROGRESSION-GUARD-01-R1.md`

## Risks

- The two lower-authority tests intentionally prove only the bounded transition from their own accepted authority to an already-accepted R21 gate. The central R21 lifecycle test remains the sole complete product-progression authority.
- Independent master inspection and fresh review remain required; this return is not self-approval.

## Follow-up items

- Master independently inspect the exact changes, rerun the packet checks and dispatch a path-disjoint independent review if the evidence reproduces.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
