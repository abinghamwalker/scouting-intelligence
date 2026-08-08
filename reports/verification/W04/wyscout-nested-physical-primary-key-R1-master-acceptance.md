# W04 nested physical primary-key R1 master acceptance

- Date: 2026-08-02
- Producer packet: `W04-NESTED-PHYSICAL-PRIMARY-KEY-01-R1`
- Review packet: `W04-NESTED-PHYSICAL-PRIMARY-KEY-REVIEW-01-R1`
- Master verdict: **ACCEPTED**
- Independent findings: **P0 0 / P1 0 / P2 0**

## Accepted correction

The master accepts the bounded descriptor-owned nested physical-primary-key
correction. It changes no logical model, root roster, row population, Arrow field,
semantic-digest formula or accepted aggregate byte. The exported twelve-role path
roster retains complete Bronze source-row identity, adds `json_path` for rejected
fields, binds nested `tenant_context.tenant_id` for Fact and Gold, and retains every
accepted top-level Fact/Gold logical key field.

`encode_w04_wyscout_product_parquet` now admits exact dotted paths while retaining
simple top-level compatibility. It validates every segment against both the frozen
projection descriptor and generated Arrow schema, descends only through non-null
named `OBJECT_STRUCT` nodes, resolves the identical path in the inverse-projected
canonical row, and requires exact supplied-key runtime type and value. Arity,
per-position type stability, uniqueness, canonical ordering, row equality and both
digest formulas remain unchanged.

The three accepted Gold timestamp key fields remain physical
`TIMESTAMP_US_UTC`. Their inverse-projected canonical key values are strict UTC
strings; raw timestamps and string/type drift fail. This is a physical/logical
boundary reconciliation, not a model or descriptor change.

## Frozen bindings

| Artifact | Accepted SHA-256 |
| --- | --- |
| `src/scouting/contracts/wyscout_schema.py` | `b76ff6d55f841594a337929c382137d27d841b37e49f0f40c1961b9af743bb54` |
| `src/scouting/storage/formats.py` | `d5e6690f4b2467baeb364e2f8339b2b091f18bc01f8e18a96e8d770da66af9b6` |
| schema closure tests | `e6d14e9fb8787990716796b1e9031013a7386fae4d7637ccc77b28d746bb9817` |
| product-format tests | `8fe2d3b587541ee4fd80c6e5604e788b48ef78ba4bdc608a9245b64b30afd345` |
| producer return | `287faf0eec55582e16d5e3354304e82f62e1ec3d337c41a6b0af2eefc23a7c91` |
| independent review | `24d0e1ff6a35655de1c7f49b36560d042237fb43a4965e136c776e5531411dcf` |
| reviewer return | `c237ee0e9f2a9d19dbb7aebadcdda522ea5bdfcc4542b1ab4b87bbfd284e9323` |

The producer and reviewer each rechecked the two aggregate files. The master also
reproduced them without writing:

| Aggregate | Logical SHA-256 | Bytes | Physical SHA-256 |
| --- | --- | ---: | --- |
| schema bundle v2 | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` | 12295 | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |
| product contract v2 | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` | 6386 | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |

## Independent and master verification

The independent reviewer kept producer bytes read-only, accepted two valid public
Fact/Gold encodes, rejected 26 malformed/drift/bypass probes, reproduced both
aggregate identities and returned PASS with zero findings. Its locked/no-sync gate
passed 360 tests in 57.45 seconds.

The master then independently reran the complete packet gate with
`PYTHONDONTWRITEBYTECODE=1`, `--locked --no-sync`, no pytest cache provider and an
isolated temporary uv cache:

- Ruff format and lint: PASS for all four owned implementation/test files.
- Mypy: PASS, no issues in four files.
- Focused schema/format/aggregate pytest: **360 passed in 52.93 seconds**.
- Bandit: PASS, zero findings.
- Import-linter: PASS, `3 kept / 0 broken`.
- Aggregate materialization `--check`: PASS with the exact logical digests above.
- Local-only verifier: PASS, all 25 checks; branch `main`, zero remotes and active
  rejecting pre-push guard.
- `git diff --check`: PASS.

## Acceptance boundary

No dependency, lockfile, provider/network, credential, external service, cloud,
container, deployment, publication, real-root product write or Git mutation was
performed by this correction loop. The product producer may consume the accepted
role-path API. Remaining W04 product, repository, phase-gate and checkpoint work
continues separately.
