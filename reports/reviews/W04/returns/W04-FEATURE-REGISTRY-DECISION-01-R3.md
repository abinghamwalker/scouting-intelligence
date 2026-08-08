# Subagent return

## Task

- task_id: `W04-FEATURE-REGISTRY-DECISION-01-R3`
- objective: Correct only the focused resolved-possession applicability proof so the exact three selector fields compose with the accepted, resolution-capable possession-v2 predicates while preserving every frozen authority byte.

## Files changed

- `tests/contracts/test_w04_supported_feature_authority.py`
- `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-DECISION-01-R3.md`

## Summary

- Added a fail-closed focused derivation that reads the accepted possession-v2 candidate, reproduces its accepted canonical lineage, requires exactly 36 unique strict-integer event/subevent pairs, and partitions those pairs solely by the candidate's exact `decision`.
- Derived exactly 32 resolution-capable pairs whose decision is not `UNMAPPED` and exactly four `UNMAPPED` pairs: `(2,25)`, `(4,40)`, `(9,90)`, and `(9,91)`.
- Strengthened `resolved_possession_action_count` applicability so it additionally requires exact membership in the derived resolution-capable pair set. Exact `ELIGIBLE_RESOLVED`, strict integer event/subevent selectors, and a strict positive integer team source ID remain mandatory.
- Preserved the feature row's exact three inputs. `possession_eligibility_state`, tags, raw IDs, names, labels, and other hidden values were not added to `input_fields`; no runtime label lookup was introduced.
- Added positive cases spanning `CONTESTED`, `CONTROL`, `DEAD_BALL`, `NON_CONTROL_ADMIN`, and `RESTART`, plus negative cases for all four exact `UNMAPPED` pairs, `(0,0)`, `(7,999)`, `(999999,999999)`, additional zero/negative pairs, and `Decimal` event/subevent selectors. Existing wrong scalar, team, and eligibility-state cases remain active.

## Tests run

- command: shell-only recursive preflight `.pyc` / `__pycache__` inventory
  - exit status: `0`
  - result: exact retained baseline reproduced: `1,150` `.pyc`; sorted `.pyc` path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`; `150` `__pycache__`; sorted cache-directory path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `1`
  - result: identified two deterministic line-wrapping differences. Both were corrected with `apply_patch`; the formatter was not permitted to edit the file.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_supported_feature_authority.py tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_w04_r21_control_preimages.py`
  - exit status: `0`
  - result: complete packet-focused R21/R3 authority/preimage suite `370 passed in 31.04s`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_supported_feature_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all `25` checks passed, failures empty, configured remotes zero.
- command: locked/no-sync, bytecode-disabled R3 pair-partition and digest helper
  - exit status: `0`
  - result: derived `32` resolution-capable pairs and exact `4` `UNMAPPED` pairs; reproduced feature decision `bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941`, feature candidate physical `8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95`, feature candidate canonical `49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f`, and possession taxonomy canonical `3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881`.
- command: shell-only recursive terminal `.pyc` / `__pycache__` inventory after this return
  - exit status: `0`
  - result: exact retained baseline equality: `1,150` `.pyc`; sorted `.pyc` path-list SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`; `150` `__pycache__`; sorted cache-directory path-list SHA-256 `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

## Artifacts/evidence

- corrected focused contract: `tests/contracts/test_w04_supported_feature_authority.py`
  - bytes before return creation: `58,543`
  - physical SHA-256: `b1dea886128861eff5d2873c4d1edad8a5b5d5d89ddd6eb2348ac0bb3b95740e`
- derived resolution-capable pairs:
  - `(1,10)`, `(1,11)`, `(1,12)`, `(1,13)`, `(2,20)`, `(2,21)`, `(2,22)`, `(2,23)`, `(2,24)`, `(2,26)`, `(2,27)`, `(3,30)`, `(3,31)`, `(3,32)`, `(3,33)`, `(3,34)`, `(3,35)`, `(3,36)`, `(5,50)`, `(5,51)`, `(6,60)`, `(7,70)`, `(7,71)`, `(7,72)`, `(8,80)`, `(8,81)`, `(8,82)`, `(8,83)`, `(8,84)`, `(8,85)`, `(8,86)`, `(10,100)`.
- derived exact `UNMAPPED` pairs:
  - `(2,25)`, `(4,40)`, `(9,90)`, `(9,91)`.
- frozen possession-v2 acceptance physical SHA-256: `2438fb0255641b02c0631b6a42e727a033fbe58e759bdf4c61e0e09692eda0a1`.
- preserved archived failed-review physical SHA-256 values:
  - R1: `3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47`.
  - R2: `31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac`.
- terminal bytecode inventory: exact equality with the retained R3 baseline; no creation, deletion, or mutation observed.

## Risks

- No unresolved selector-composition, authority-lineage, applicability, local-only, retained-inventory, or bounded-scope risk was found in this producer packet.
- This is producer evidence only. Fresh independent R3 review and master acceptance remain required before cross-authority, identity, Bronze, Silver, Gold, or product implementation may proceed.

## Follow-up items

- Fresh independent R3 review by an actor distinct from this producer.
- Master independently reads every changed byte and reproduces the complete packet evidence before accepting or returning the correction.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no sync, install, dependency, `pyproject.toml`, or `uv.lock` change occurred.
- no edits outside `allowed_paths`: confirmed; exactly the two packet-owned paths were edited or created.
- no delegation: confirmed.
- no self-approval: confirmed; this is a producer return only.
- no authority/candidate/review/archive/predecessor/preimage/acceptance/product edit: confirmed.
- no network/provider/cross-authority/identity/Bronze/Silver/Gold/build/model/product/cloud/container/endpoint/hosted-CI/deployment work: confirmed.
