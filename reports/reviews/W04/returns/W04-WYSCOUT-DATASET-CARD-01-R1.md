# W04-WYSCOUT-DATASET-CARD-01-R1 return

- Objective: Bind the accepted W04 source, build, product, health, rights,
  temporal, feature, and limitation evidence into the transformed dataset card.
- Owner: master.

## Changed files

- `docs/dataset-cards/w04-wyscout-transformed-v1.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-DATASET-CARD-01-R1.md`

## Result

The card binds build and code-manifest identities, all three layer manifests,
health JSON SHA-256, complete-source versus one-match product populations, the
six separate source and Gold coverage dimensions, correction/quarantine policy,
four supported count features, all material suppressions, temporal boundary,
bias, applicability, rights/attribution, governed offline launch shape, and the
terminal R11/R3/R12 evidence distinction.

Dataset-card SHA-256:
`5e61793da4b160e3bf5bf857217040044e2b84d32774c5cd45801445430c9b30`.

## Checks

- every count and digest compared with the canonical health JSON and immutable
  manifests: PASS;
- local-only/no-deployment/no-publication boundary stated without qualification:
  PASS;
- exact-minutes/per-90 and product-population overclaim prevention: PASS;
- W10 deferred host-state work visible and non-blocking: PASS; and
- `git diff --check`: PASS.

## Residual risks

The accepted research-only, historical, one-match, right-censored, coordinate,
provider-taxonomy, and derived-possession/lineup limitations remain explicit.
No product, manifest, receipt, source, runtime, dependency, lock, or Git operation
occurred while authoring the card.
