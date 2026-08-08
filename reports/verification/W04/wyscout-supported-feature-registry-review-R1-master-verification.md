# W04 supported feature registry review R1 — master verification

## Decision

`REWORK`.

The independent reviewer correctly preserved the frozen decision and candidate
and identified one bounded executable-proof defect. The focused helper treated
input key presence as accepted evidence, so malformed values could make a
supported feature applicable. The finding is reproducible and must be corrected
in the focused contract only.

The second P2 is also valid: the review's bytecode inventory changed while the
review was running. The master caused that drift by running an early complete
repository pytest diagnostic without bytecode suppression. The reviewer
correctly failed closed and did not clean or alter the retained files.

Neither finding demonstrates an architecture contradiction. The exact R21
decision and candidate remain unchanged and valid.

## Evidence readback

```text
review recommendation: REWORK
P0 findings: 0
P1 findings: 0
P2 findings: 2
review physical SHA-256:
3b5738da3a3905f253aaca037e94c8d8ab421bc1c5b17db9f5226f098b9efb47
review record SHA-256:
3801373f9b1da81d59a578d933ba011118a9694c6abbeb10b6d84d1334f99254
review return SHA-256:
63ecba6c9b8f2f8e15369ab75fd4047e4ec9fcaa3cbfa7cb748e0c5ff339fad0
decision SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate canonical SHA-256:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
```

The early repository diagnostic itself completed successfully:

```text
1031 passed, 1 warning in 159.34s
```

It was diagnostic only, not the required terminal repository gate, because R21
acceptance and cross-authority evidence were not yet complete.

## Bounded rework

R2 may modify only the focused feature contract and its producer return. It
must:

- require strict positive integer source IDs, excluding booleans;
- require strict integer canonical taxonomy selector IDs, excluding booleans,
  and a strict positive team source ID;
- require an action-position list of cardinality one or two, with exact `x` and
  `y` members, accepted finite numeric values, and both axes within inclusive
  `0..100`;
- preserve exact `ELIGIBLE_RESOLVED` possession applicability;
- add negative challenges for all invalid cases reproduced by the reviewer;
- leave every decision, candidate, predecessor, preimage, review, and product
  byte untouched.

The retained post-diagnostic inventory becomes the next packet's honest
preflight:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

No cleanup is authorized.

## Gate

Only `W04-FEATURE-REGISTRY-DECISION-01-R2` may start. Feature acceptance,
cross-authority composition, and every product path remain blocked.
