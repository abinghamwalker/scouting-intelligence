# W04 supported feature registry decision R2 — master verification

## Decision

`ACCEPT_FOR_FRESH_INDEPENDENT_REVIEW`.

R2 corrects only the focused applicability proof. The frozen decision,
candidate, predecessors, preimages, and failed independent review remain byte
unchanged. No architecture or product change is required.

## Corrected evidence predicates

The master read the complete changed contract and independently confirmed:

- action and match counts require strict positive integer source IDs and reject
  Python booleans;
- coordinate count requires one or two exact `x`/`y` mappings with finite
  numeric axes in inclusive `0..100`;
- resolved-possession count requires exact `ELIGIBLE_RESOLVED`, strict integer
  event/subevent selectors, and a strict positive integer team source ID;
- null, string, float/decimal source IDs, booleans, zero/negative source IDs,
  empty/oversized/malformed/nonfinite/out-of-range positions, missing
  selectors, mistyped selectors, and non-resolved possession states all fail
  closed.

Direct master challenge:

```text
action_valid=True
action_bool=False
match_null=False
position_valid=True
position_empty=False
position_oob=False
resolved_valid=True
resolved_string=False
```

## Integrity

```text
focused contract SHA-256:
2331bf0bdbc25457e29b9e9a72c6667cc4852711ee55bbcc5d63711b005eca03
R2 return SHA-256:
8e91c591c357a32dacf4346fae71673b2703df6ee665428cd1c4b6327d68d078
decision SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate canonical SHA-256:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
failed review SHA-256:
3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47
```

The failed review is preserved byte-for-byte at
`reports/reviews/W04/archive/wyscout-supported-feature-registry-independent-review-R1-rework-3b5738da.md`
before the fixed R21 review path is reused.

## Master reproduction

```text
complete R21/R2 focused authority/preimage suite:
352 passed in 27.12s
focused Ruff format:
PASS
focused Ruff lint:
PASS
local-only verifier:
25/25 PASS
git remote:
empty
```

The producer and master both reproduced the retained inventory:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

## Gate

Only `W04-FEATURE-REGISTRY-REVIEW-01-R2` may start. Feature acceptance,
cross-authority composition, and every product path remain blocked.
