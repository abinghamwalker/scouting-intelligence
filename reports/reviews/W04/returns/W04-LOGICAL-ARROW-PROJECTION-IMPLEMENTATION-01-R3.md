# Subagent return

## Task

- task_id: `W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R3`
- objective: Close only finding `W04-LAP-IMPL-R1-P1-01` by strictly revalidating raw direct and nested `CanonicalJsonValue` runtime state before serialization, semantic hashing, or Parquet writing.

## Files changed

- `src/scouting/storage/formats.py`
- `tests/unit/test_w04_wyscout_product_formats.py`
- `reports/reviews/W04/returns/W04-LOGICAL-ARROW-PROJECTION-IMPLEMENTATION-01-R3.md`

## Summary

- Added recursive raw-state recovery for every exact `CanonicalJsonValue` union arm and `CanonicalJsonMember`. It reads exact Pydantic field dictionaries without dumping, rejects missing/additional model fields, forbidden extra or field-set state, wrong discriminators, and non-exact nested model classes.
- Enforced exact raw primitive and container types before fresh validation: Boolean, integer, finite `Decimal`, NFC Unicode scalar text, tuple-only arrays and objects, and exact typed object members.
- Converted the accepted raw state into a new plain discriminated-union mapping and strictly validated that mapping as a fresh `CanonicalJsonValue` before the first Pydantic JSON-mode dump. The fresh result must retain the exact original union arm.
- Added 81 direct/recursive matrix cases: 27 malformed copy/construct cases, each also nested through a copied array and a constructed object. The matrix covers Boolean/float/string-as-integer, integer-as-Boolean, list-as-tuple, bare-dict child, wrong discriminator, extra value/member state, duplicate and unsorted members, non-finite `Decimal`, non-NFC text, and surrogate text.
- Added copied and constructed end-to-end P1 tripwires proving zero semantic-hash calls and zero `pq.write_table` calls, plus an exact probe proving malformed state is rejected before `model_dump`.
- Preserved descriptor APIs, Arrow schema generation, semantic framing, build behavior, authority bytes, R2 rejected-sentinel correction, and the accepted physical/semantic identity vectors.

## Tests run

- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py -k 'copied_constructed or bypassed'`
  - exit status: `0`
  - result: `84 passed, 91 deselected in 0.21s`.
- command: `uv run ruff format --check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: two files already formatted.
- command: `uv run ruff check src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: all checks passed.
- command: `uv run mypy src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py`
  - exit status: `0`
  - result: no issues found in two source files.
- command: `uv run pytest -q tests/unit/test_w04_wyscout_product_formats.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `219 passed in 3.05s`.
- command: `uv run pytest -q tests/contracts/test_w04_logical_arrow_projection_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`
  - exit status: `0`
  - result: `179 passed in 3.88s`.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; 25 checks, zero failures, zero configured Git remotes.

## Artifacts/evidence

- `src/scouting/storage/formats.py` SHA-256: `309ee2821913022c3ce82b713a53e74dd4ac3190af0047a621ba4ab2cd0f7209`.
- `tests/unit/test_w04_wyscout_product_formats.py` SHA-256: `0d6acf199d230257656f91c0c191c3bbef5dfb23c5cf49e6f731da4d57c8f317`.
- Preserved build contract SHA-256: `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`.
- Preserved build-contract test SHA-256: `f39e34daac144369444e1701003efdec0c1a97f83ba5fb0beecaf844c21e4692`.
- Preserved authority decision SHA-256: `460f06833e87d6304f6e638588a64981b62f6c8c73d999d7da462629b4e69ef1`.
- Preserved authority acceptance SHA-256: `647ce58093485717a50037eeb6e46d09c2dfad88a8f60bdef7bce8d35f8d31c3`.
- Preserved failed-review packet SHA-256: `f4afbf9ae5996e76d79fafb7c8a9744955f4daa5da77ac0c4c6cb2d040500856`.
- Preserved failed review SHA-256: `8b40285f742be1434670fecca743c9d94c3513b1edc7e583ab073d913c9db9eb`.
- Preserved failed-review return SHA-256: `1a7db7673711a6fa3e824661ccb9a748c06daf62e769f328142c7f170b2eba32`.
- Preserved implementation R1 return SHA-256: `197bb99e4fe6a6328a709f4af946166429e97aa8fed5858df2b6b954806e8372`.
- Preserved implementation R2 return SHA-256: `4f8cde34645c8cc5c9ab19cf05a1c9a3c5b50290615df352e551bda5b8caa934`.
- Passing frozen-vector assertions retain physical SHA-256 `889b525bcda3e11ff710112fd4095089935d8274c375cf3d6bed9636c8b63d2b` and semantic SHA-256 `6ac5879732257cb40bfd6480c7605ddddd1df430e44fc41cc642d3874c0205e7`.

## Risks

- Fresh independent implementation review and master acceptance remain required; this return does not self-approve the R3 candidate.
- The 23-root producer remains paused. No root descriptor, product bytes, or wider build behavior was introduced.

## Follow-up items

- Fresh independent review of the exact R3 serializer and unit-test bytes, followed by separate master acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
