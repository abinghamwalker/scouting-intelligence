# W04 supported feature registry independent review R1 — fresh R4 execution

## Recommendation

`PASS`.

The frozen R4 decision and candidate reproduce the exact R21 authority: fifteen
ordered rows, the exact `4/4/7` state split, and only `action_count`,
`coordinate_known_action_count`, `match_count`, and
`resolved_possession_action_count` as supported. The last feature has exactly
three inputs and no hidden applicability input. Unsupported features remain
closed; raw, name, and label fields do not grant feature applicability.

All three archived `REWORK` reviews are byte-identical at their packet-bound
hashes. R4 closes their findings. Accepted-value challenges reject null, Boolean,
zero, malformed, and structurally invalid source identifiers and coordinates.
Unknown and accepted-`UNMAPPED` predicate pairs remain ineligible. Independent
derivation from the possession opening and attachment fields produced exactly 36
accepted predicate pairs, 28 potentially resolution-capable pairs, and these exact
eight structurally ineligible pairs: `(2,23)`, `(2,24)`, `(2,25)`, `(2,26)`,
`(4,40)`, `(5,51)`, `(9,90)`, and `(9,91)`. Direct same-period sequence
composition returned `ELIGIBLE_RESOLVED` for all 28 capable pairs and
`INELIGIBLE_UNMAPPED` for all eight ineligible pairs. Feature applicability agreed
for every pair, including when the ineligible rows were challenged with a forged
eligible state.

The decision/candidate physical and canonical digests, predecessor and preimage
bindings, actor separation, clock progression, policy closure, and no-product
boundary all reproduce. The focused suite passed 371 tests; Ruff format and lint
checks passed; the local-only verifier passed all 25 checks with zero remotes. No
P0-P2 finding remains.

The retained no-write inventory stayed exact: 1,150 `.pyc` paths with path-list
SHA-256 `7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44`
and 150 `__pycache__` directories with path-list SHA-256
`79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-supported-count-features-v1","candidate_physical_sha256":"8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95","candidate_sha256":"49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f","decision_id":"w04-wyscout-supported-feature-registry-decisions-v1","decision_physical_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","decision_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-supported-feature-registry-independent-review-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T10:07:30Z","reviewed_by":"234b8590-33d6-563c-a77e-57b6a43303e9"}
```

No acceptance, downstream cross-authority implementation, identity, Bronze,
Silver, Gold, build, model, product, network, cloud, container, endpoint, hosted
CI, deployment, dependency, or Git operation was performed.
