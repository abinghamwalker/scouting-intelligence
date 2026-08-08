# W04 derived v2 preimage correction R1 — master verification

## Decision

`MECHANICALLY_REGENERATED_FOR_FRESH_INDEPENDENT_REVIEW`. This is not runtime
acceptance and does not release a real-root run.

## Authorized scope

The standing bounded-correction authority and
`wyscout-runtime-foreign-pyc-and-derived-preimage-correction-authorization-R1.md`
authorize only the descriptor-derived refresh required by the accepted loaded-R
physical correction. The master changed these two unaccepted descriptor-only
files and no v1 input:

- `configs/schema/wyscout-v5-schema-bundle-preimage-v2.json`
- `configs/schema/wyscout-v5-product-contract-preimage-v2.json`

The accepted builders in `scouting.contracts.wyscout_aggregates` reconstructed the
schema preimage first and the product preimage second. The product binds the
actual new schema body digest. Both files are canonical JSON with exactly one
physical terminal LF and no aggregate self-digest.

## Exact derived identities

```text
schema v2 canonical body SHA-256:
a0daa1a22619bf2719ff67d1a22f4495a8de0ea8884f53bb5f05276c9b71ddc0
schema v2 physical bytes: 12295
schema v2 physical SHA-256:
c760710eacbb6575b4af46b31ae5f69c1b16ef702d14630c84597a118a40911e

product v2 canonical body SHA-256:
a50dd67b5ab989c783d67cda3cc0fe15229b6991de342d74bbdc3c40a465c832
product v2 physical bytes: 6386
product v2 physical SHA-256:
465a2abf9e72eb25cc6717cfc656304ae9bb208e4ed0e08d54a46420e3db23ce
```

The schema physical file changed from
`8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45`
to the value above. The product physical file changed from
`7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af`
to the value above. The v1 schema and product inputs remain respectively
`a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
and `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`.

## Reproduction

The complete aggregate contract file passes `17 passed in 35.35s` with exit `0`.
It independently checks the exact serial two-node DAG, all 23 ordered roots and
earlier-only edges, every implemented content digest, exact authority and receipt
composition, canonical physical bytes, product-to-schema binding, no self-digest,
and adversarial missing/reordered/substituted/extra cases. Focused `git diff
--check` is clean.

No logical model, root roster, feature or product population, source or rights
authority, intended output, digest formula/meaning, dependency, lock state,
provider access, retained data/run artifact, or PYC was changed by this master
derivation. The files remain frozen for independent review together with the
producer's foreign-cache denial correction.
