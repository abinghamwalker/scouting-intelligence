# W04 R21 control preimages R1 — master verification

## Decision

`ACCEPT FOR FRESH INDEPENDENT REVIEW`. This is not final acceptance and does not
release field v2 or any downstream implementation.

## Complete readback

The master read both complete canonical JSON files, all 569 focused-test lines,
and all 98 producer-return lines.

Exact materialized preimages:

```text
product contract
path: configs/schema/wyscout-v5-product-contract-preimage-v1.json
bytes: 5473
lines: 1
physical/canonical SHA-256:
0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293

schema bundle
path: configs/schema/wyscout-v5-schema-bundle-preimage-v1.json
bytes: 6104
lines: 1
physical/canonical SHA-256:
a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f
```

Both bind immutable R20 and accepted R21 SHA-256
`faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`.

## Independent contract reconstruction

The master confirmed:

- compact sorted-key UTF-8 JSON and exactly one terminal LF;
- product top-level key closure;
- exact 17 path templates, ten owners, each role owned once, two primary keys,
  five manifest/receipt rows, three-layer order, and no-product policy;
- schema top-level key closure;
- exact 16 descriptors, identical dependency order, unique IDs, and
  earlier-only dependencies;
- exact descriptor-only surface literal and typed unresolved feature placeholder
  with null concrete value;
- byte-equal authority links and sibling-only DAG edges;
- no own/sibling/downstream digest, concrete feature hash, clock, host, root,
  absolute path, build/run ID, output observation, or product byte; and
- all seven described Bronze/Silver/Gold/manifest/rebuild roots remain absent.

## Checks and inventory

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The focused suite passes `6 passed in 0.07s`; focused Ruff format and lint pass;
all 25 local-only checks pass; `git diff --check` passes; and `git remote` is
empty.

Producer preflight/postflight evidence is byte-identical:

```text
repository pycs/cache dirs: 59/19
site pycs/cache dirs: 1086/131
total pycs/cache dirs: 1145/150
inventory SHA-256:
0ace64f09a0c3de3564355a72d8171c3fbd14d6f771b9c4e44c420582c8958f9
```

The master regenerated the split inventory after all checks and matched the
retained baseline exactly.

No Git mutation, dependency/lock change, provider/network action, cloud,
container, endpoint, hosted CI, deployment, semantic authority, data layer,
serializer, manifest, receipt, build, model, or product implementation occurred.

## Gate

The two control preimages and focused test are eligible for fresh independent
review under `W04-CONTROL-PREIMAGE-REVIEW-01-R1`.
