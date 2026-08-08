# Subagent return

## Task

- task_id: W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R2
- objective: Remove only the master-found R1 test-only semantic digest derivation, replace it with an explicitly rejected fixed caller-claim sentinel from existing test constants, and prove that claim cannot authorize Gold receipt closure.

## Files changed

- tests/contracts/test_w04_wyscout_build_contract.py
- reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R2.md

## Summary

- Removed the `w04-gold-schema-authority-unavailable` domain/preimage and its SHA-256 derivation from the unavailable-Gold test fixture.
- Reused existing digest constant `H1` through the explicitly non-authoritative name `REJECTED_CALLER_GOLD_SEMANTIC_CLAIM`; no new semantic digest formula, placeholder authority, descriptor, schema, table, encoder call, or product byte was introduced.
- Added a focused test that confirms the rejected caller claim is carried by both the Gold manifest entry and boundary receipt, then proves receipt closure terminates with `GoldSchemaAuthorityUnavailableError`.
- Preserved the R1 serializer candidate, serializer tests, runtime build contract, accepted authority bytes, and R1 return byte-identically.

## Tests run

- command: `uv run ruff format --check tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: 0
  - result: 1 file already formatted
- command: `uv run ruff check tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: 0
  - result: All checks passed
- command: `uv run mypy tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: 0
  - result: Success; no issues found in 1 source file
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: 0
  - result: 135 passed in 3.01s
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: 0
  - result: 179 passed in 3.94s
- command: `uv run python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; 25 checks, zero failures, zero configured Git remotes

## Artifacts/evidence

- `tests/contracts/test_w04_wyscout_build_contract.py` SHA-256: `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692`
- Preserved `src/scouting/storage/formats.py` SHA-256: `d1827127ce36a67dc49993f5cdb4cd18a5ab5bc62f3b753808529f66dba9f2c9`
- Preserved `tests/unit/test_w04_wyscout_product_formats.py` SHA-256: `b5fe5aa5831755abe83cd8fd812538dbfbb091190a42430fb09c9141d7e33cce`
- Preserved `src/scouting/contracts/wyscout_build.py` SHA-256: `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`
- Preserved R1 implementation packet SHA-256: `b36793b729561521203ddb507161326340e2a14e73cc5616a59ae2eb18c6b6e5`
- Preserved R1 return SHA-256: `197bb99e4fe6a6328a709f4af946166429e97aa8fed5858df2b6b954806e8372`
- Preserved authority decision SHA-256: `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`
- Preserved authority acceptance SHA-256: `647ce58093485717a50037eeb6e46d09c2dfad88a8f60bdef7bce8d35f8d31c3`

## Risks

- Independent review and master acceptance remain required; this return does not self-approve the correction.
- No runtime behavior changed. Gold closure remains deliberately fail-closed until the accepted projection descriptor is supplied by a separately authorized 23-root producer.

## Follow-up items

- Fresh independent R2 review followed by master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
