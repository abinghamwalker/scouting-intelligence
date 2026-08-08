# W04 supported feature registry independent review R1 — fresh R3 execution

## Recommendation

`REWORK`.

The frozen decision and candidate reproduce the exact R21 authority: ten accepted
inputs, fifteen ordered eight-field rows, the exact `4/4/7` state split, and only
`action_count`, `coordinate_known_action_count`, `match_count`, and
`resolved_possession_action_count` as supported. The decision/candidate physical
and canonical digests, predecessor bindings, policy closure, candidate restatement,
actor/clock progression, and no-product boundary all reproduce.

Both archived predecessor reviews are byte-identical at their packet-bound hashes.
R3 closes the R1 accepted-evidence checks for source IDs and coordinates and closes
R2's rejection of unknown and accepted-`UNMAPPED` predicate pairs. A bounded P2
remains in R3's definition of resolution capability. It classifies every one of the
32 non-`UNMAPPED` predicate pairs as capable of producing
`ELIGIBLE_RESOLVED`. The accepted same-period resolver proves four of those pairs
can never be assigned: `(2,23)` and `(5,51)` are `DEAD_BALL` with attachment
`UNASSIGNED`, while `(2,24)` and `(2,26)` are `NON_CONTROL_ADMIN`, whose sequence
policy is unassigned. Direct composition returned feature applicability `true` for
all four inconsistent contexts while the possession-v2 resolver returned
`INELIGIBLE_UNMAPPED` for the same actions. The exact capability split is therefore
28 potentially resolution-capable pairs and eight structurally ineligible pairs,
including the four accepted `UNMAPPED` pairs. Frozen feature and possession
authority bytes need no change; only the focused derivation, challenges, and
successor packet evidence require bounded correction.

The retained no-write inventory remained stable throughout this review: 1,150
`.pyc` paths and 150 `__pycache__` directories reproduced both packet digests.
The fixed route was written only after both archived reviews, all authority hashes,
the full focused suite, and the direct composition challenge were complete.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-supported-count-features-v1","candidate_physical_sha256":"8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95","candidate_sha256":"49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f","decision_id":"w04-wyscout-supported-feature-registry-decisions-v1","decision_physical_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","decision_sha256":"bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941","findings":[{"code":"POSSESSION_SEQUENCE_RESOLUTION_CAPABILITY_GAP","severity":"P2","summary":"R3 treats all 32 non-UNMAPPED accepted pairs as resolution-capable. Independent composition returned feature applicable=true while the accepted same-period resolver returned INELIGIBLE_UNMAPPED for DEAD_BALL/UNASSIGNED pairs (2,23) and (5,51) plus NON_CONTROL_ADMIN pairs (2,24) and (2,26). The accepted sequence policy admits only 28 pairs that can ever attach to or open a deterministic possession; preserve all authority bytes and correct only the focused derivation, negative cases, and successor packet evidence."}],"recommendation":"REWORK","review_id":"w04-wyscout-supported-feature-registry-independent-review-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-31T09:42:35Z","reviewed_by":"c37f72f6-508b-5eaf-bf70-65d727287f7b"}
```

No feature acceptance, cross-authority composition, identity, Bronze, Silver,
Gold, build, model, product, network, cloud, container, endpoint, hosted CI,
deployment, or Git operation was performed.
