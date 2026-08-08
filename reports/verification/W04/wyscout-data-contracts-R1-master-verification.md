# W04 Wyscout data contracts R1 — master verification

## Decision

`REWORK`.

The producer's six prescribed checks pass, but master readback and executable
constructor mutation probes independently reproduce fail-open contract states.
The corrected fresh independent review reports the same disposition with ten P1
finding families and no P0/P2 finding. All failures are bounded implementation,
test, and evidence defects inside the frozen W04 data-contract scope. No R22
architecture revision is justified.

## Reviewed artifact identity

| Artifact | SHA-256 |
|---|---|
| `src/scouting/contracts/wyscout_data.py` | `9d90641965ef6d9351d76785d5729cc932ed7ea3cae11ff931dcef3279148452` |
| `tests/contracts/test_wyscout_data_contracts.py` | `568859f5879766c0470169e480177c3089b26788456c3133294e86ba2b0dc69a` |
| producer return | `abc9418fa0e61187097a6ff7ed11345f7e265703116aff1ad2a5ce30e200176a` |
| corrected independent review | `862fa5513cd261fd95bcd921fb52631c90af56ff930ce968682059879761dee2` |
| corrected reviewer return | `8f4e5259690fda1456b903564fd244f5e174fe4a108adf100b596f125f9532d5` |

All packet-fixed source, identity, field-v2, possession-v2, supported-feature,
product-preimage, and schema-preimage digests reproduce exactly.

## Master-reproduced prescribed checks

```text
uv run ruff format --check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS — 2 files already formatted

uv run ruff check src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS

uv run mypy src/scouting/contracts/wyscout_data.py \
  tests/contracts/test_wyscout_data_contracts.py
PASS

uv run lint-imports
PASS — 30 files, 46 dependencies, 3 contracts kept, 0 broken

uv run pytest -q tests/contracts/test_wyscout_data_contracts.py \
  tests/contracts/test_foundation_contracts.py \
  tests/contracts/test_w04_r21_cross_authority_composability.py \
  tests/unit/test_wyscout_source_manifest.py
PASS — 225 passed in 67.50s

uv run python scripts/verify_local_only.py
PASS — 25/25

git diff --check
PASS

git remote
PASS — empty
```

## Master-reproduced fail-open probes

Local `uv run python` constructor probes accepted:

- a canonical competition source ID of zero;
- an unadmitted `(event_id=7, subevent_id=999)` pair marked
  `ELIGIBLE_RESOLVED`;
- a Bronze manifest filename digest unequal to its `build_id`;
- a Bronze row with an unrelated tenant and non-null club;
- restricted classification with export enabled and attribution disabled;
- arbitrary manifest schema role and empty partition metadata;
- a row-lineage hash unrelated to its attached dependencies; and
- backdated accepted-authority dependency clocks after recomputing the lineage
  hash.

The independent review additionally reproduced raw-kind direct-constructor
forgery, decimal128 positive-exponent overflow, incomplete coverage/failure
states, Gold/fact reconciliation gaps, and incomplete source/provenance
evidence.

## Required disposition

Return only the W04 data contract implementation, its focused tests, and a new
producer return for bounded R2 correction. Bronze, identity runtime, Silver,
Gold, build, and product execution remain blocked until R2 passes fresh
independent review, master acceptance, and the complete repository master gate.

No provider, authority, architecture, dependency, network, cloud, container,
hosted CI, public endpoint, or deployment change is authorized.
