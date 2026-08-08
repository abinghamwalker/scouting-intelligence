# W04 foreign-cache denial and derived-preimage correction authorization R1

- Date: `2026-08-03`
- Governing authority: standing bounded-correction authority dated `2026-08-02`
- Effective design: R20 with R21's declared replacements and the accepted loaded-runtime correction
- Decision: **AUTHORIZED_FOR_PRODUCER_REVIEW_MASTER_REWORK**

## Failed-gate evidence

The first mandatory loaded-runtime correction gate completed with exit `1` after
`507 passed, 6 failed` in `1561.85s`. Four failures occurred before admission
because the complete repository PYC census correctly rejected the previously
unclassified retained file
`scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc`. The retained file
is a regular no-follow path with mode `0o644`, link count `1`, size `190312`, and
shell-observed SHA-256
`d4ede22d1299579ab0d9728da574e0ab02eb403ea8954b0413748b34a7e33e90`.
It was present in the pre-gate census and remains immutable incident evidence.
Neither admission nor the launcher may read, import, execute, delete, repair,
rename, truncate, quarantine, or otherwise mutate it.

The complete pre/post failed-gate inventories remained identical:

- selected-site PYC: `1218` rows, SHA-256
  `bd0b8036ffff7542a4216db800622c9379e953d7cbd38b45ab464636ca4001dd`;
- repository PYC: `133` rows, SHA-256
  `d3f27229f8b43fd3fc1aba948462b6fb8a872790f4def522e494090ff444ff8d`; and
- retained `data/` and `runs/`: `272` rows, SHA-256
  `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`.

The remaining two failures were exact aggregate physical/config preimage tests.
They showed that the accepted R12 physical result descriptors changed four
implemented-schema content hashes while the descriptor-only v2 schema and product
preimages still bound stale v1 source bytes. This is a mechanical derived-byte
defect, not a logical aggregate, product, root, or digest-formula change.

## Smallest sound correction

The producer is authorized to extend both independently implemented metadata-only
PYC collectors and their existing tests with one exact foreign-cache-tag denial
predicate:

```text
path: scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc
source: scripts/admit_wyscout_v5_runtime.py (must be present and stable-authoritative)
cache tag: cpython-314
mode: 0o644
size: 190312
class: REPOSITORY_FOREIGN_CACHE_TAG_DENIED
policy: FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ
```

The predicate grants no source, import, owner, component, environment, build,
schema, product, or execution authority. Classification is by safe contained
`lstat` metadata only under the already-installed unconditional PYC execution
denial. Any other foreign tag or path, missing/wrong source, non-regular file,
symlink, hardlink, changed mode or size, duplicate, path escape, attempted PYC
open/read/hash/header/magic access, or attempted use remains a hard failure. The
current file's shell-observed digest is incident evidence only and must not be
recomputed inside admission or launcher execution.

The master is separately authorized to regenerate only the two existing
descriptor-only canonical JSON v2 preimages from the accepted v1 preimage bytes
and accepted aggregate algorithms:

- `configs/schema/wyscout-v5-schema-bundle-preimage-v2.json`; and
- `configs/schema/wyscout-v5-product-contract-preimage-v2.json`.

The refresh may change their physical bytes and unaccepted root-content digests,
including the product preimage's mechanically inherited schema-v2 digest. It may
not change either canonical algorithm, key order, DAG, logical schema, 23-root
roster, feature/product population, source authority, rights authority, intended
output, or digest meaning/formula. Exact canonical reconstruction and both
aggregate contracts must pass.

## Required proof and progression

The producer must add positive exact classification and adversarial tests in both
collectors, preserve zero PYC reads and the immutable incident file, and rerun all
focused/static checks before freezing a new return. The independent reviewer must
verify the final producer hashes, the no-read/no-authority property, predicate
exactness, adversarial matrix, mechanical v2 preimage derivation, and complete
failed-gate preservation. A failed producer or review remains bounded rework.

Only after fresh independent PASS and master acceptance may the mandatory complete
gate be rerun. The rerun must use a fresh shell-only PYC and retained-tree
preflight/postflight and must prove exact preservation. This authorization changes
no logical contract or user-boundary item.
