# W04 supported feature registry acceptance R1 — master verification

## Decision

`ACCEPT`.

The master accepts the frozen R21 supported-feature authority after four
independent review passes through the bounded rework loop. The final fixed-route
review is `PASS` with zero findings. All three earlier `REWORK` review bytes are
preserved in the review archive.

## Accepted authority

```text
decision ID:
w04-wyscout-supported-feature-registry-decisions-v1
candidate ID:
w04-wyscout-supported-count-features-v1
review ID:
w04-wyscout-supported-feature-registry-independent-review-R1
acceptance ID:
w04-wyscout-supported-feature-registry-acceptance-v1
```

The accepted roster is exactly fifteen ordered rows, with four supported:

```text
action_count
coordinate_known_action_count
match_count
resolved_possession_action_count
```

State split:

```text
SUPPORTED: 4
SUPPRESSED_UNSUPPORTED_DENOMINATOR: 4
UNAVAILABLE: 7
```

The final proof enforces accepted value shapes and the exact possession
sequence-capability partition:

```text
accepted predicate pairs: 36
potentially resolution-capable: 28
structurally ineligible: 8
```

## Bound integrity

```text
decision SHA-256:
bf46f42585adfdec48f5e3670c70d9e517b9f542645089ba63b91dd218d33941
candidate physical SHA-256:
8901e09c8b0cd9ab2bfce9f6855702e518e36efa98c7f7653082eee52fcc2d95
candidate canonical SHA-256 / accepted feature_schema_hash:
49065bcfe762caa7585082d897d845d82c9a9ef2f57a84a5312e55a12ffea10f
review physical SHA-256:
a692cc4aaa002882f92209256f1bdecb96b3eb6bdba8a9bc3f645569daa31c73
review record SHA-256:
039a3a0e8cbd68e6bdb7a1a8871c20f6af8095aac754e2ef1e0fb913c81a84e2
```

The canonical acceptance binds the master UUIDv5 actor, exact candidate,
decision, zero-finding PASS review, and ordered clock. No prior feature
acceptance exists, so `supersedes_acceptance_id` is null.

## Verification before materialization

```text
complete focused authority/resolver/preimage suite:
371 passed in 35.04s
local-only verifier:
25/25 PASS
review recommendation/findings:
PASS / []
retained pyc paths:
1,150
retained __pycache__ directories:
150
git remote:
empty
```

## Gate

Feature acceptance releases only `W04-R21-CROSS-AUTHORITY-TEST-01-R1`.
Identity, Bronze, Silver, Gold, build, manifest, receipt, model, and product
implementation remain blocked until the complete R21 machine gate and full
repository master gate pass.
