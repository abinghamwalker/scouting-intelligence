# W04 possession semantic v2 decision R1 — master verification

## Decision

`ACCEPT_FOR_INDEPENDENT_REVIEW`. The producer changed exactly its four
absolute owned paths. The returned decision, candidate, focused contract, and
return reproduce under master control.

This decision is not possession-v2 acceptance. It releases only the fixed
independent-review packet.

## Complete readback

The master read the full decision, all 485 candidate lines, all 1,084 focused
test lines, and all 76 return lines. Independent parsing and reconstruction
produced:

```text
decision keys: 10
candidate keys: 9
bound inputs: 5
prior-authority keys: 17
predicates: 36
unique event/subevent pairs: 36
predicate semantic difference from v1: none

decision SHA-256:
3198178feef14886be3cf65dbc98a0b3b34d87a74102d2c54a470e23079a4973
candidate physical SHA-256:
6c739f674894d6c605cbd5beccb0ad074f0b64f2447efe664438764458b84d7c
candidate canonical SHA-256:
54c2dcca6e84ef1cdb174a41a4c35f05a224f216513bdf1408422aa7c93f7452
focused test SHA-256:
1e19d73952711affbb85707a8b21269a02f0aba6653d9faf319b49eb4b89dbe4
```

The five inputs bind the accepted field-v2 candidate and acceptance, plus the
two frozen taxonomy sources. The complete accepted possession-v1 route is
carried separately as the exact 17-key predecessor. Decision counts remain:
4 contested, 11 control, 8 dead-ball, 2 non-control administration, 7 restart,
and 4 unmapped.

The closed selector names only the four R21 canonical action fields. It forbids
coercion and raw/rejected/name/label matching, requires strict integer
event/subevent values, a sorted unique strict-integer tag array, an exact
predicate pair, and a canonical positive team when the predicate requires the
action team. Missing or mistyped input is unmapped.

## Master checks

```text
uv sync --locked --all-groups
PASS: 83 resolved, 82 audited

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
  tests/contracts/test_w04_possession_semantic_v2_authority.py
  tests/contracts/test_w04_possession_semantic_authority.py
  tests/contracts/test_w04_field_semantic_v2_authority.py
PASS: 321 passed in 26.05s

ruff format/check, focused v2 contract
PASS

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
  scripts/verify_local_only.py
PASS: 25/25

git diff --check
PASS

git remote
PASS: empty
```

The master matched the retained complete baseline exactly: 1,145 `.pyc` files
and 150 `__pycache__` directories, with identical path and file-content sets
against baseline SHA-256
`b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777`.

## Required independent challenge

Independent review must not treat focused green tests as proof. In particular,
it must determine whether the declarative selector and test helper use
`ELIGIBLE_RESOLVED` only when the exact accepted predicate participates in a
deterministically resolved same-period possession under the unchanged R20
sequence rules. A mere exact predicate lookup must not silently overclaim
sequence resolution. Any such overclaim is `REWORK`.

The review must also reconstruct canonical bytes and digests, challenge all
strict integer/tag/team cases, prove raw/name/label isolation, preserve all v1
bytes, and verify progression safety.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1` may now start. Review,
acceptance, feature, cross-authority, and product work remain blocked.
