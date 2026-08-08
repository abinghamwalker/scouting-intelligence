# W04 Wyscout build-contract conformance review R2

Date: 2026-08-01

Review ID: `w04-wyscout-build-contract-conformance-review-R2`

Candidate: frozen W04 build-contract R4 fail-closed receipt composition

Recommendation: **PASS**

Finding counts: **P0=0, P1=0, P2=0**

## Scope and independence

This was a fresh independent review under packet
`W04-WYSCOUT-BUILD-CONTRACT-CONFORMANCE-REVIEW-01-R2`. The reviewer did not
produce the R4 candidate, did not edit implementation or tests, did not delegate,
performed no Git operation, and does not approve its own work. The only outputs are
this report and its required return.

The verdict accepts R4 only as the bounded Packet-1 contract and fail-closed
composition state. It does not claim executable receipt completion. That remains
unavailable until the already-planned exact 23-root implemented-schema authority,
v2 aggregate gates, and later bounded composition have independently passed.

## Fixed-binding verification

Every packet-fixed artifact reproduced exactly before analysis:

| Artifact | Required and observed SHA-256 | Result |
| --- | --- | --- |
| R2 conformance-review packet | `6a9fbb1e198df038c851b8f46d59eebec34f5c4ff15aea811ebf00ac64531a66` | PASS |
| R4 producer packet | `d55ed40ea24d8fff680a2fa4eadefbb5bfa32394b8fc562b2ca1bb7b45fc01ee` | PASS |
| R4 contract | `f4433ebeaadee2f1d17f7f5f286f6eee21656c7408338e972270b9237ee8bce6` | PASS |
| R4 tests | `c6a50ffc7963c15ace11d68d78a9a5abd0e80953e52696a765ac2a4e259da229` | PASS |
| R4 producer return | `4e4bf858fec11d3cff40052f579164ddeae426f9ad70cc69852f1eb73f9b5db1` | PASS |
| retained failed R3 review | `82cc1b09111b9236d51578a25ab525f81c2dd79cdd9014ff042b222b06d26592` | PASS |
| retained failed-review return | `e25d5802c55b33f64f720ff461f31a93c861b869dc9385eb62d888b7463ba4ef` | PASS |
| schema-composition boundary audit | `e1d3597b5331705d030a25be7ffc7fd390a5c0fe4b7c84000a25ec744b30517b` | PASS |
| boundary-audit return | `df20a183a608b0b9ac84d5791298f473de4e7d15405fb98401a9a7ffd5662623` | PASS |
| R4 build/receipt authority audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | PASS |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | PASS |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | PASS |

No fixed binding drifted.

## Dedicated unavailable-authority state

Static and executable evidence proves that R4 has no successful receipt-closure
path:

- `validate_receipt_closure` has exactly four inputs: `receipt`,
  `boundary_population`, `manifest_population`, and `gold_product_readback`.
- Its parsed function body contains zero `return` nodes. After all retained
  validations it unconditionally raises the exact non-serialized
  `GoldSchemaAuthorityUnavailableError` with message
  `accepted GOLD_PLAYER_WINDOW schema authority is not yet available`.
- The error is a plain exception state, not a Pydantic field, receipt value, result
  value, callback result, or serialized claim.
- Representative fifth inputs consisting of a Boolean, callback, descriptor,
  digest, and arbitrary object were all rejected by Python with `TypeError`.
  Therefore no caller argument can satisfy, suppress, or replace the state.
- No claim-only product, semantic, or temporal-proof digest parameter has returned.
  Exact product bytes, typed contract-row bytes, temporal-proof bytes, Arrow table,
  and Arrow schema remain content-bearing validation inputs only.

## Independent coherent-schema matrix

The reviewer reconstructed the exact baseline and independently formed the three
supported R1 variations from its Arrow schema. For every variation the exact Gold
contract row and temporal proof were retained; Parquet bytes and semantic digest
were regenerated; the Gold manifest entry, all layer-summary physical/semantic
values, boundary receipt, and enclosing receipt were then consistently re-derived.

| Composition | Gold physical SHA-256 | Gold semantic SHA-256 | Gold manifest SHA-256 | Boundary SHA-256 | Result |
| --- | --- | --- | --- | --- | --- |
| exact baseline | exact frozen fixture | exact frozen fixture | exact frozen fixture | exact frozen fixture | `GoldSchemaAuthorityUnavailableError` |
| `role_context_version` top-level nullability `false -> true` | `a57573ac66a9b34c29b5a1aff89d92d4bb0d15c3a46daea65a8a70735e533f64` | `bf50c562e0da76274cd39b0bf8b887d2b1b6f02702245d3412903bb7e54923d9` | `7565cb1e5390116cf1aec7d0fd82bd61c2bade0e05cbebca27570a432e4cac05` | `836a0a2244a616a620926d9eb37b4603d5416831b615d9d5370d3e94c04c4d78` | exact dedicated state |
| swap adjacent top-level role-context fields | `b7aef9afa4b660915e7b18f488d982a1ee27c7960b7ac5a2926acbd5e132725f` | `a1e7c79540b0d12faf935bee89829ab9ee5d51ac7f73da71f2d7bc40b57e293c` | `f9267678e0f0734024c307f23ae7782adaed55cc59526325f7e57c636363bf3c` | `2169c2c6d6e07efec16d6501b2070f238d5a71b83018c3cf82547b08684bdb97` | exact dedicated state |
| `features.action_count` nested width `int64 -> int32` | `a193b778b9a52b44d3ca66a95a9dc189a272e1686a1ce2ce637fe4ca0d539a4a` | `b4c7532369a0768d6ec9ec86c20ba142031f1077b2a45ded82293b4690d46323` | `ba5bd25446c979145112cfca9158cee9b566b72dab14b205dae6b95e43170bdb` | `3fef6f9197ff37bf628943ef09e3431a0745879a2fdc837bc2ff75c040e7a783` | exact dedicated state |

The changed physical and semantic identities prove the variants were genuinely
re-encoded rather than routed through the baseline. None returned successful
completion.

## Earlier validation ordering

Independent malformed-input probes established that retained validations execute
before the dedicated final state:

| Input defect | Observed earlier state |
| --- | --- |
| malformed complete-manifest content | `ValidationError` from accepted `LayerManifest` |
| malformed Gold contract-row content | `ValidationError` from accepted Gold contract |
| changed boundary physical bytes | `ValueError` |
| coherently reserialized wrong parent identity | `ValueError` |
| omitted boundary population | `ValueError` |
| boundary check after invocation completion | `ValueError` |

Every manifest is strictly parsed from exact canonical JSON-plus-LF bytes,
revalidated with `LayerManifest.model_validate_json(..., strict=True)`, compared
with its typed dump, and then checked for physical digest, size, sole R4 semantic
derivation, parent, frozen authority, lineage, build, path, layer, and completion
equality. The former locally shaped manifest route remains closed.

## Frozen contract and product limits

The focused and complete suites confirm the following unchanged bindings:

- the exact 25-key pre-build projection, exact 25-key inverse invocation, and sole
  projection hash;
- five ordered authority rows and the exact window, source-manifest, completion-index,
  one-match, competition, tenant, role-context, cutoff, and clock bindings;
- season source ID `181150` reproducing
  `4696aa1f-b512-5d18-af79-33cf031455cf`;
- the sole lineup stint `591cdf5b-2281-53c4-8225-150313ca2c01` for match
  `2499719`, team `1631`, player `285508`, ordinal `0`, represented as `[82,83)`,
  right-censored, without terminal interval, elapsed minutes, or per-90 eligibility,
  and with reason `suppressed_unsupported_denominator`;
- one Gold row and only the four supported count features: action count,
  coordinate-known action count, match count, and resolved-possession action count;
  and
- exact receipt and eight result-surface key rosters, all-three complete-manifest
  semantic reproduction, manifest-derived one-Gold/one-boundary population, and
  cross-clock closure.

R4 defines, infers, copies, hashes, or accepts no canonical Gold Arrow schema. Its
supplied Arrow schema is checked only for mutual content consistency during retained
readback validation. Successful schema authority remains deliberately absent.

## Verification

| Command | Exit | Result |
| --- | ---: | --- |
| fixed-binding `shasum -a 256` checks | 0 | every packet-fixed digest reproduced |
| `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | all checks passed |
| `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | no issues in 2 source files |
| packet-focused five-path `uv run pytest -q` matrix | 0 | 268 passed in 6.59s |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py` | 0 | 233 passed in 107.05s |
| independent `uv run python -B -` conformance probe | 0 | baseline and three variants reached exact dedicated state; five extra argument forms rejected; six malformed classes failed earlier |
| `uv run python scripts/verify_local_only.py` | 0 | PASS, 25/25 checks and zero Git remotes |

## Residual state and verdict

The remaining unavailable receipt-completion state is intentional and required,
not a defect. No runtime, aggregate consumer, product writer, receipt writer, or
publication path may treat R4 as executable completion. The planned exact 23-root
schema closure must next be implemented and independently accepted; only after the
existing aggregate gates may a later bounded composition bind the accepted Gold
schema and restore a successful closure path.

**PASS**, with `P0/P1/P2 = 0/0/0`, for the frozen R4 Packet-1 contract and
fail-closed behavior only. No architecture, schema-root roster, projection,
population, feature, dependency, provider, rights, storage, deployment, or
local-only boundary change is required.
