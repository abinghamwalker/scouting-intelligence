# W04 supported feature registry decision R4 — master verification

## Decision

`ACCEPT_FOR_FRESH_INDEPENDENT_REVIEW`.

R4 corrects the final known sequence-capability gap in the focused proof. It
derives capability from the accepted possession-v2 predicate's exact opening
and attachment fields and directly composes representative sequences with the
accepted same-period resolver.

Every frozen authority, candidate, predecessor, preimage, acceptance, archived
review, and product boundary remains byte unchanged.

## Independent master reconstruction

The master independently reproduced:

```text
accepted predicate pairs: 36
potentially resolution-capable: 28
structurally ineligible: 8
```

The structurally ineligible set is exactly:

```text
(2,23) (2,24) (2,25) (2,26)
(4,40) (5,51) (9,90) (9,91)
```

Direct master outcomes:

```text
CONTROL (7,70): applicable
attachable DEAD_BALL (2,20): applicable
UNASSIGNED DEAD_BALL (2,23): ineligible
NON_CONTROL_ADMIN (2,24): ineligible
UNMAPPED (9,90): ineligible
unknown (7,999): ineligible
```

The focused contract also directly executes accepted resolver cases for
`CONTROL`, `RESTART`, attachable `DEAD_BALL`, and buffered `CONTESTED`, and
executes all four additional structurally ineligible pairs between valid
control actions.

The feature row still contains exactly its three frozen selector inputs.

## Integrity

```text
focused contract SHA-256:
77c8da171d1f6dfdd19b9a9e09eeaf05a05b9ba9cd8c9ff905442c1d143beef4
R4 return SHA-256:
b7c2f11a8be98f76bdef5bb7d046345b81ce26c95eca64079ca5562872ca999e
decision SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate canonical SHA-256:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
```

All three archived failed-review hashes reproduce exactly.

## Master reproduction

```text
complete R21/R4 focused authority/resolver/preimage suite:
371 passed in 32.41s
focused Ruff format:
PASS
focused Ruff lint:
PASS
local-only verifier:
25/25 PASS (producer result retained)
git remote:
empty
```

Retained inventory:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

## Gate

Only `W04-FEATURE-REGISTRY-REVIEW-01-R4` may start. Feature acceptance,
cross-authority composition, and all product work remain blocked.
