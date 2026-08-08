# W04 Wyscout build-contract conformance review R1

Date: 2026-08-01

Review ID: `w04-wyscout-build-contract-conformance-review-R1`

Candidate: frozen W04 build-contract R3 receipt composition

Recommendation: **REWORK**

Finding counts: **P0=0, P1=1, P2=0**

## Scope and independence

This was a read-only independent review under packet
`W04-WYSCOUT-BUILD-CONTRACT-CONFORMANCE-REVIEW-01-R1`. The reviewer did not
produce the candidate, did not edit implementation or tests, did not delegate and
does not approve its own work. The only outputs are this report and its return.

Every packet-fixed binding reproduced exactly before analysis:

| Artifact | Reproduced SHA-256 |
| --- | --- |
| R3 packet | `cefa3360dd9466c797abbaf2187e9c8c23edc5fe5a5b03d2b61e7593f6934048` |
| R3 contract | `ea0a5f4cd474a081d97b529e3ecf87f0e3852dccef0041f712544420c85d55fd` |
| R3 tests | `c153c7a41120a88128301b18f6ee50f1721d0c65431eed1cc8136b5761d9d040` |
| R3 return | `dd50227ed1c9ab6fa8f21603a015a1d12a7a15f73da0fccadb6467a9ea38fb54` |
| retained failed review | `71191b27210014bf5767cad542f2f66d090a6868aa01290aba7583f4aac8e05c` |
| retained failed-review return | `57b489e147b3df3ec4d9fa57dff0386bfdb4a080d6fd0e3aaf028168e80e49fd` |
| R4 audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` |
| R20 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| accepted data contract | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |
| accepted Parquet encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` |

The season/lineup decision and acceptance also remain byte-identical at
`3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e`
and `6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e`.

## Finding

### W04-BUILD-R3-P1-UNBOUND-GOLD-SCHEMA-IDENTITY — P1

R3 validates the exact typed Gold JSON row and temporal proof, then passes
`readback.schema` straight back to the accepted encoder
(`src/scouting/contracts/wyscout_build.py:997-1046`). The encoder proves that the
table equals that supplied schema and includes its descriptor in the physical and
semantic derivations, but the receipt seam never compares the descriptor with the
accepted v2 canonical `GOLD_PLAYER_WINDOW` schema identity required by the
incorporated R3 audit at
`reports/reviews/W04/wyscout-build-receipt-closure-audit-R3.md:172-184`.

An independent matrix kept the exact authorized Gold contract row, temporal proof,
primary key, parent path, one-match population, and all content values unchanged.
It varied one supported Arrow schema property, deterministically re-encoded the
table, updated the Gold manifest entry, rebuilt all three layer summaries, and
rebuilt the Gold-bound boundary and receipt values. Receipt closure accepted every
following non-identical schema:

| One-property variation | Result | Schema-descriptor SHA-256 | Gold semantic SHA-256 | Gold physical SHA-256 |
| --- | --- | --- | --- | --- |
| `role_context_version` nullable `false -> true` | **ACCEPTED** | `d6857b539d1cf9d3091c82094a77da4e7ecd3c461dada2a4456053139787a068` | `bf50c562e0da76274cd39b0bf8b887d2b1b6f02702245d3412903bb7e54923d9` | `a57573ac66a9b34c29b5a1aff89d92d4bb0d15c3a46daea65a8a70735e533f64` |
| swap one adjacent top-level field order | **ACCEPTED** | `cfd53d2fd7bf6cf43373df0d14a362ee33f03eac05b89ddeba86d8633bdaf033` | `a1e7c79540b0d12faf935bee89829ab9ee5d51ac7f73da71f2d7bc40b57e293c` | `b7aef9afa4b660915e7b18f488d982a1ee27c7960b7ac5a2926acbd5e132725f` |
| nested `features.action_count` `int64 -> int32` | **ACCEPTED** | `44339f1d502bf9d127cc44e77d8cf14b8f113b85ac9d6a50a6d7ae8a422cace1` | `b4c7532369a0768d6ec9ec86c20ba142031f1077b2a45ded82293b4690d46323` | `a193b778b9a52b44d3ca66a95a9dc189a272e1686a1ce2ce637fe4ca0d539a4a` |

This is not a product-row or semantic-value substitution. It demonstrates that the
R3 seam treats a caller-selected supported Arrow schema as its own authority. A
consistent downstream re-derivation therefore selects among multiple schema
identities, contrary to the exact accepted-schema readback rule.

## Smallest correction boundary

The correction is bounded composition, not an architecture, root, population,
feature, dependency, provider, storage or local-only change. It cannot truthfully be
completed from the currently implemented inputs alone:

- `GoldPlayerWindow` closes the JSON contract row but does not define Arrow field
  order, widths or nullability.
- The accepted R21 schema-bundle preimage explicitly labels every descriptor
  `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA` and states that it does
  not establish an implemented row or Parquet schema
  (`reports/reviews/W04/wyscout-schema-design-R21.md:713-757`).
- A new fixed digest, a caller digest, the test fixture's inferred schema, or a
  locally copied schema would be an unauthorized placeholder or second authority.

Therefore the candidate must remain `REWORK` until the already-planned canonical
23-root schema-bundle authority materializes and independently accepts the exact
`GOLD_PLAYER_WINDOW` Arrow/schema descriptor. The subsequent bounded receipt
composition correction must consume that accepted content-bound identity, require
byte-exact equality before deterministic product re-encoding, and prove nullability,
field-order and integer-width substitutions fail even after every dependent value is
re-derived. This is a serial sequencing dependency within the approved design; it
does not require a new root or broader architecture.

## Passing conformance evidence

- All three formerly locally shaped manifest fixtures are now rejected by the
  accepted `LayerManifest` validator (`ValidationError` for Bronze, Silver and Gold).
- `validate_receipt_closure` has only `receipt`, `boundary_population`,
  `manifest_population`, and `gold_product_readback`; the three former claim-only
  digest parameters are absent. Changed content cannot be authorized by digest-only
  arguments.
- The focused suite retains the exact one-match, one-Gold-row, four-feature,
  competition, season and exact one-stint lineup authorities and passes 265 tests.
- The complete accepted Wyscout data-contract suite passes 233 tests.
- Static inspection and execution showed no product/data/run write, provider/network
  action, process launch, dependency change, cloud, container, hosted CI, endpoint or
  deployment. Local-only verification passes all 25 checks with zero Git remotes.

## Checks

| Command | Exit | Result |
| --- | ---: | --- |
| fixed-binding `shasum -a 256` checks | 0 | every required digest reproduced |
| `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | 2 files already formatted |
| `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | all checks passed |
| `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py` | 0 | no issues in 2 files |
| packet focused `uv run pytest -q` five-path matrix | 0 | 265 passed in 6.49s |
| `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py` | 0 | 233 passed in 107.69s |
| independent `uv run python -B -c` schema matrix | 0 | 3 alternate supported schema identities accepted; 3 invalid manifests rejected; digest-only parameters absent |
| `uv run python scripts/verify_local_only.py` | 0 | PASS, 25/25 checks |

## Verdict

`REWORK`, with `P0/P1/P2 = 0/1/0`. No schema aggregate consumer, product
implementation, receipt completion or publication should rely on R3 until the
planned canonical schema authority exists, the bounded composition correction is
implemented, and fresh independent review plus master acceptance pass.
