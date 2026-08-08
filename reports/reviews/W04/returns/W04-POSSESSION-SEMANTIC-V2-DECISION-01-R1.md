# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R1`
- objective: Materialize only the accepted R21 possession-v2 decision, candidate, progression-safe focused contract, and producer return.

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json`
- `configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml`
- `tests/contracts/test_w04_possession_semantic_v2_authority.py`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-DECISION-01-R1.md`

## Summary

- Materialized the strict canonical possession-v2 decision with exactly the five accepted field-v2/taxonomy inputs and the exact accepted possession-v1 authority carried separately as `prior_authority`.
- Copied all 36 accepted v1 predicates byte-semantically: same order, actors, choices, attachments, tag arrays, and rationales. No predicate was widened, relabelled, or rewritten.
- Added a closed declarative `cross_authority_selector` policy. Its only admitted canonical inputs are `action_event_taxonomy_id`, `action_subevent_taxonomy_id`, `action_team_source_id`, and `action_tag_ids`; coercion and raw/rejected/name/label matching are forbidden.
- Implemented contract evaluation for strict integer/non-boolean taxonomy selectors, exact pair matching, a required sorted-unique strict-integer tag array, tag predicates, and a required positive canonical team for `ACTION_TEAM` predicates. Missing or mistyped inputs return `UNMAPPED`; no empty tag default is synthesized.
- Implemented explicit `possession_eligibility_state` values. The 32 non-`UNMAPPED` exact predicates yield `ELIGIBLE_RESOLVED`; the four accepted `UNMAPPED` predicates and every selector failure yield `INELIGIBLE_UNMAPPED`.
- The candidate is deterministic safe YAML and exactly restates the decision inputs, policies, predicates, prior authority, and source while binding the physical decision bytes.
- The focused contract is progression-safe for absent, PASS-review, REWORK-review, and exact future acceptance states. Later authority is blocked before valid possession-v2 acceptance; product paths remain forbidden.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_possession_semantic_v2_authority.py tests/contracts/test_w04_possession_semantic_authority.py tests/contracts/test_w04_field_semantic_v2_authority.py`
  - exit status: `0`
  - result: `321 passed in 25.80s`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_v2_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; failures empty; all 25 named checks passed

## Artifacts/evidence

- decision physical/canonical SHA-256: `3198178feef14886be3cf65dbc98a0b3b34d87a74102d2c54a470e23079a4973`
- candidate physical SHA-256: `6c739f674894d6c605cbd5beccb0ad074f0b64f2447efe664438764458b84d7c`
- candidate parsed canonical JSON SHA-256: `54c2dcca6e84ef1cdb174a41a4c35f05a224f216513bdf1408422aa7c93f7452`
- focused contract physical SHA-256: `1e19d73952711affbb85707a8b21269a02f0aba6653d9faf319b49eb4b89dbe4`
- exact structure readback: 10 decision keys, 9 candidate keys, 36 predicates, 18 `ACTION_TEAM` predicates, 18 `NONE` predicates
- frozen possession-v1 physical hashes remained exact:
  - decision: `4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71`
  - candidate: `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`
  - review: `1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4`
  - acceptance: `f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112`
- shell-only pre-Python bytecode inventory:
  - `.pyc` files: `1,145`
  - `.pyc` symlinks: `0`
  - `__pycache__` directories: `150`
  - serialized rows: `1,295`
  - serialized bytes: `240,202`
  - SHA-256: `ed6b512981047c8fe45e75e9bd7fa8ba28b5e694fd33835c7185db4ee67827eb`
- terminal post-return inventory reproduced every value above byte-for-byte: `1,295` rows, `240,202` bytes, SHA-256 `ed6b512981047c8fe45e75e9bd7fa8ba28b5e694fd33835c7185db4ee67827eb`.

## Risks

- This producer return is not an independent review or acceptance. No possession construction, feature authority, cross-authority gate, Bronze, Silver, Gold, build, model, or product implementation is authorized here.
- Residual authority progression is intentionally deferred to the separately owned independent review and master acceptance packets.

## Follow-up items

- A separate owner must perform `w04-wyscout-possession-semantic-independent-review-v2-R1`.
- After a valid PASS review, the master must separately materialize and verify `w04-wyscout-possession-semantic-acceptance-v2`, superseding only `w04-wyscout-possession-semantic-acceptance-v1`.

## Scope confirmation

- no Git operations: `confirmed`
- no unauthorised dependency or lockfile changes: `confirmed`
- no edits outside `allowed_paths`: `confirmed`; exactly the four packet-owned paths above were created
- no delegation, provider/network access, review, acceptance, or self-approval: `confirmed`
