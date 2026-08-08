# W04 supported feature registry independent review R1 — fresh R2 execution

## Recommendation

`REWORK`.

The decision and candidate reproduce the frozen R21 authority exactly: ten
accepted inputs, fifteen ordered eight-field rows, the exact `4/4/7` state split,
and only `action_count`, `coordinate_known_action_count`, `match_count`, and
`resolved_possession_action_count` as supported. Physical and canonical digests,
predecessor bindings, policy closure, candidate restatement, actor/clock order,
and the pre-acceptance no-product boundary all reproduce.

R2 closes the R1 key-presence defect for source identifiers, positions, selector
types, team identifiers, and the exact eligibility-state string. One bounded P2
remains. The corrected helper still treats any strict-integer event/subevent pair
as accepted canonical evidence when the context claims `ELIGIBLE_RESOLVED`.
Independent composition against the accepted possession-v2 selector showed that
pairs `(0,0)`, `(7,999)`, `(999999,999999)`, and accepted-but-`UNMAPPED` pair
`(9,90)` all produce `PREDICATE_UNMAPPED`, while the feature helper returns
applicable for every one. Such values cannot be the accepted field-v2 and
possession-v2 evidence required by R21. The focused helper and negative cases
must bind this applicability proof to an exact admitted, resolution-capable
possession predicate without adding a hidden fourth feature input or changing
any frozen authority byte.

The retained no-write inventory remained stable throughout this fresh review:
1,150 `.pyc` paths and 150 `__pycache__` directories reproduced both packet
digests. The archived failed review remains byte-identical at its required hash,
and the fixed route was replaced only after all R2 challenges completed.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-supported-count-features-v1","candidate_physical_sha256":"8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95","candidate_sha256":"49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f","decision_id":"w04-wyscout-supported-feature-registry-decisions-v1","decision_physical_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","decision_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","findings":[{"code":"POSSESSION_SELECTOR_ACCEPTANCE_GAP","severity":"P2","summary":"The corrected applicability helper still accepts impossible possession selector evidence when the context claims ELIGIBLE_RESOLVED. Independent execution returned true for strict-integer pairs (0,0), (7,999), and (999999,999999), plus accepted-but-UNMAPPED pair (9,90), while the accepted possession-v2 selector returned PREDICATE_UNMAPPED for each. Preserve every frozen authority byte and strengthen only the focused helper and negative cases so the three declared inputs compose with an exact admitted, resolution-capable possession predicate without adding a hidden fourth input."}],"recommendation":"REWORK","review_id":"w04-wyscout-supported-feature-registry-independent-review-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T09:20:28Z","reviewed_by":"0cb1d025-bd15-5c06-9ebb-7b70e195192f"}
```

No feature acceptance, cross-authority composition, identity, Bronze, Silver,
Gold, build, model, product, network, cloud, container, endpoint, hosted CI,
deployment, or Git operation was performed.
