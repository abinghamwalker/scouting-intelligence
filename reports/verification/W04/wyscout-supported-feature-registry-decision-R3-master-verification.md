# W04 supported feature registry decision R3 — master verification

## Decision

`ACCEPT_FOR_FRESH_INDEPENDENT_REVIEW`.

R3 closes the R2 possession-selector acceptance gap in the focused contract
only. Every frozen decision, candidate, predecessor, preimage, acceptance,
review archive, and product boundary remains byte unchanged.

## Independent master reconstruction

The corrected proof derives pairs from the accepted possession-v2 candidate
after reproducing its accepted lineage. It independently enforces:

```text
accepted predicate rows: 36
unique event/subevent pairs: 36
resolution-capable pairs: 32
exact UNMAPPED pairs:
(2,25), (4,40), (9,90), (9,91)
```

The master directly reproduced:

```text
accepted (8,80): applicable
unknown (7,999): ineligible
UNMAPPED (9,90): ineligible
zero (0,0): ineligible
```

All non-`UNMAPPED` decision classes are exercised:

```text
CONTESTED
CONTROL
DEAD_BALL
NON_CONTROL_ADMIN
RESTART
```

The exact feature row still has only:

```text
action_event_taxonomy_id
action_subevent_taxonomy_id
action_team_source_id
```

Eligibility state remains a separate applicability predicate; tags remain
possession derivation evidence and are not feature inputs.

## Integrity

```text
focused contract SHA-256:
b1dea886128861eff5d2873c4d1edad8a5b5d5d89ddd6eb2348ac0bb3b95740e
R3 return SHA-256:
6f49d42286d2e27b9a4f68764812a290da3a14775f0a3dcc5eb8ce568f4de967
decision SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate canonical SHA-256:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
failed R1 review SHA-256:
3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47
failed R2 review SHA-256:
31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac
```

## Master reproduction

```text
complete R21/R3 focused authority/preimage suite:
370 passed in 32.13s
focused Ruff format:
PASS
focused Ruff lint:
PASS
local-only verifier:
25/25 PASS (producer result retained)
git remote:
empty
```

The producer and master reproduced the exact retained inventory:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

## Gate

Only `W04-FEATURE-REGISTRY-REVIEW-01-R3` may start. Feature acceptance,
cross-authority composition, and every product path remain blocked.
