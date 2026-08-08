# Subagent return

## Task

- task_id: `W04-POST-AUTHORITY-BUILD-SCHEMA-AUDIT-01`
- objective: Audit the current accepted identity/Parquet repository and return the
  smallest exact path-owned sequence for the W04 build contract, complete 23-root
  schema closure, and acyclic v2 aggregate materialization.

## Files changed

- `reports/reviews/W04/returns/W04-POST-AUTHORITY-BUILD-SCHEMA-AUDIT-01-R1.md`

## Summary

### Verdict

**PASS_TO_PACKET, conditional on fresh build/product authority review and master
acceptance.** The bounded implementation is possible with the current architecture,
dependency set, accepted source/index/identity/Parquet foundations, four-feature
scope, and local-only boundary. No product, manifest, receipt, build, aggregate, or
placeholder digest may be written while the authority decision is still unreviewed.

At the final audit snapshot,
`reports/reviews/W04/authorities/wyscout-build-product-authority-decisions-v1.json`
had appeared as an in-progress parallel authority output, while its independent
review and master acceptance were absent. That expected path-disjoint activity does
not change this audit's hard dependency gate.

### Fixed bindings

Every packet-fixed physical digest was reproduced twice and remained stable:

| Artifact | Exact SHA-256 | Result |
|---|---|---|
| R4 build/receipt audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | PASS |
| Wyscout data contracts | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` | PASS |
| W04 Parquet encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` | PASS |
| Wyscout identity runtime | `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd` | PASS |

No fixed binding, architecture boundary, dependency, source scope, or product scope
change is required.

### Exact current executable inventory

The following prerequisites now exist and are reusable:

- `src/scouting/contracts/wyscout_data.py` implements strict runtime validators for
  the 13 product/layer-manifest roots listed below, exact 17 path roles, the accepted
  five-dependency lineage, source/index/authority/tenant bindings, four Gold
  features, strict integer-only subevent mapping, product path templates, and layer
  parent ordering.
- `src/scouting/sources/wyscout_completion_index.py` supplies the accepted
  source-completion reader, exact match-period population validation, checked
  Silver/Gold builders, checked manifest builder, and `require_checked_product`.
- `src/scouting/identity/wyscout.py` supplies the accepted exact source-derived,
  content-addressed identity bundle/runtime. The frozen bundle and queue are present
  under `data/working/wyscout/v5/identity/`.
- `src/scouting/storage/formats.py` supplies the accepted explicit-schema W04
  Parquet encoder with the R20 physical settings and semantic preimage. It does not
  supply a 23-root contract-schema exporter.
- `WyscoutProductPath`, `LayerManifestEntry`, and `LayerManifest` already close
  product/manifest paths, owners, partition values, physical/semantic claims and
  same-build layer-parent shape. They do not close receipt content.

The following surfaces are genuinely absent:

- no executable exact five-key window object/UUID constructor;
- no `WyscoutPreBuildProjection`, `WyscoutRebuildInvocation`, exact 25-to-25
  conversion, single build-hash helper, or inverse reconstruction;
- no content model for the nine-key rebuild invocation receipt or 15-key temporal
  boundary receipt;
- no executable model for any of the eight R20 child-result roots;
- no canonical closed-schema exporter, no complete 23-row implemented-schema
  roster, and no accepted canonical schema bytes/content digests;
- no v2 schema-bundle or product-contract preimage, materializer, or accepted v2
  digest;
- no admission, launcher, or rebuild script. Those runtime/product surfaces remain
  downstream of this build/schema chain and are not silently included here.

Exact absent-path inspection found none of:

```text
src/scouting/contracts/wyscout_build.py
src/scouting/contracts/wyscout_schema.py
src/scouting/contracts/wyscout_aggregates.py
scripts/materialize_wyscout_v5_contracts.py
scripts/admit_wyscout_v5_runtime.py
scripts/launch_wyscout_v5.py
scripts/rebuild_wyscout_v5.py
configs/schema/wyscout-v5-schema-bundle-preimage-v2.json
configs/schema/wyscout-v5-product-contract-preimage-v2.json
```

### Exact 23-root reconciliation

“Executable runtime contract” and “accepted canonical closed-schema bytes” are
different claims. Thirteen roots have runtime models today; all 23 still require the
separate R4/R2 canonical closed-schema export and review. The ten rows marked
`MODEL MISSING` are the only genuine missing runtime root models.

| # | Required root role | Current runtime model | Current state |
|---:|---|---|---|
| 1 | `BRONZE_KNOWN_RECORD` | `BronzeKnownRecord` (10 fields) | model exists; closed-schema bytes absent |
| 2 | `BRONZE_REJECTED_RECORD` | `BronzeRejectedRecord` (10 fields) | model exists; closed-schema bytes absent |
| 3 | `BRONZE_REJECTED_FIELD` | `BronzeRejectedField` (15 fields) | model exists; closed-schema bytes absent |
| 4 | `SILVER_COMPETITION` | `SilverCompetition` (9 fields) | model exists; closed-schema bytes absent |
| 5 | `SILVER_TEAM` | `SilverTeam` (9 fields) | model exists; closed-schema bytes absent |
| 6 | `SILVER_PLAYER` | `SilverPlayer` (9 fields) | model exists; closed-schema bytes absent |
| 7 | `SILVER_MATCH` | `SilverMatch` (15 fields) | model exists; closed-schema bytes absent |
| 8 | `SILVER_ACTION` | `SilverAction` (28 fields) | model exists; closed-schema bytes absent |
| 9 | `SILVER_LINEUP_STINT` | `SilverLineupStint` (19 fields) | model exists; closed-schema bytes absent |
| 10 | `SILVER_POSSESSION` | `SilverPossession` (17 fields) | model exists; closed-schema bytes absent |
| 11 | `SILVER_PLAYER_MATCH_FACT` | `SilverPlayerMatchFact` (27 fields) | model exists; closed-schema bytes absent |
| 12 | `GOLD_PLAYER_WINDOW` | `GoldPlayerWindow` (25 fields) | model exists; closed-schema bytes absent |
| 13 | `LAYER_MANIFEST` | `LayerManifest` (19 fields), with `LayerManifestEntry` and parent definitions | model exists; closed-schema bytes absent |
| 14 | `TEMPORAL_BOUNDARY_RECEIPT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 15 | `REBUILD_INVOCATION_RECEIPT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 16 | `ENTRYPOINT_SOURCE_RESULT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 17 | `COMPONENT_PROOF_RESULT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 18 | `PRE_BUILD_ADMISSION_RESULT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 19 | `REBUILD_RECEIPT_SUMMARY` | none | **MODEL MISSING**; closed-schema bytes absent |
| 20 | `LAYER_MANIFEST_SUMMARY` | none | **MODEL MISSING**; closed-schema bytes absent |
| 21 | `FINAL_RECHECK_RESULT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 22 | `POST_BUILD_ID_REBUILD_RESULT` | none | **MODEL MISSING**; closed-schema bytes absent |
| 23 | `CHILD_RESULT_ENVELOPE` | none | **MODEL MISSING**; closed-schema bytes absent |

The eight result roots are not optional merely because they are nested in the child
result. R2 explicitly makes them independently validated roots and orders them
before `CHILD_RESULT_ENVELOPE`. The two receipt roots remain ordered boundary before
invocation. No source-envelope, identity, Parquet-descriptor, projection, window,
aggregate-preimage, or code-manifest surface is appended to the exact 23-role array.

For the 13 existing models, emitting `model_json_schema()` alone is insufficient:
their `model_validator` equality, ordering, completeness, lineage, coverage,
temporal and authority constraints are part of the required transitive closure.
The canonical exporter must explicitly encode those constraints; a symbol name,
source digest, serializer digest, or Pydantic structural projection is not complete
schema content.

### Smallest safe path-owned packet sequence

The chain below is path-disjoint between producer packets and remains authority-
serial. Review packets own only their two report files. No packet may edit a prior
accepted producer path, either v1 preimage, R20/R21/index/identity/Parquet byte, or
any product/data/run path.

#### Gate 0 — finish the in-progress authority chain

`W04-BUILD-PRODUCT-AUTHORITY-DECISION-01-R1` must first produce its canonical
decision and tests, receive a fresh independent `PASS`, and receive master
acceptance. The accepted decision/review/acceptance physical hashes become fixed
inputs to every packet below. A malformed or absent review/acceptance is a hard
stop, not a reason to begin implementation.

#### Packet 1 — `W04-WYSCOUT-BUILD-CONTRACT-01-R1`

Owner: one contract producer, no delegation or Git.

Exact owned files:

```text
src/scouting/contracts/wyscout_build.py
tests/contracts/test_w04_wyscout_build_contract.py
reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-01-R1.md
```

Implement only:

- the exact five-key window value/preimage/UUID rule and fixed window/cutoff/
  snapshot values;
- the exact closed 25-key pre-build projection and exact 25-key post-hash
  invocation, copying the same 24 values and replacing only `schema_version` with
  `build_id`;
- the sole SHA-256 build calculator and exact inverse reconstruction;
- the exact nine-key invocation receipt and 15-key boundary receipt content models;
- the exact eight independently validated child-result root models; and
- canonical value/closed-key validators needed by those models, without filesystem,
  output, runtime launcher, schema aggregate, or publication writes.

The packet must test missing/extra/mistyped/reordered authority and dependency rows,
cutoff equality, 26th keys, alternate hashes, placeholder IDs, cross-build/run/path
drift, empty/additional/reordered boundary summaries, receipt clocks, direct Gold
path hash, result cardinalities and every exact inverse equality. It must bind the
fresh accepted authority bytes and preserve the R4 sole two-key layer-semantic rule
as a referenced requirement, not create a second derivation.

Acceptance commands:

```text
uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py
uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py
uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py
uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py
uv run python scripts/verify_local_only.py
```

#### Review 1 — `W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1`

Exact owned files:

```text
reports/reviews/W04/wyscout-build-contract-independent-review-R1.md
reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1.md
```

Fix the producer file/test/return hashes. Independently reconstruct window bytes and
UUID, projection/invocation bytes and inverse, every receipt/result key/type/order,
and all adversarial mutations. Verdict must be `PASS` with P0/P1/P2 = `0/0/0`
before Packet 2.

#### Packet 2 — `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R1`

Owner: one schema producer after Review 1, no delegation or Git.

Exact owned files:

```text
src/scouting/contracts/wyscout_schema.py
tests/contracts/test_w04_wyscout_schema_closure.py
reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R1.md
```

Implement an in-memory canonical schema exporter only. It must export exactly the
23 roles above, in exact order, each with complete transitive named/anonymous
definitions, unions, enums, nullability, cardinality, array/object ordering and
cross-field constraints. Each six-key implemented-schema row must bind an actual
canonical schema ID/version/content digest and ordered unique earlier-only
dependencies. It must reject missing, extra, duplicate, reordered, forward or cyclic
roots and any self/product/build/run/output/clock/digest reference forbidden by R2.
It may expose the complete schema-bundle-v2 preimage in memory for review, but must
not write either v2 preimage file or advertise a bundle/product digest as accepted.

Acceptance commands:

```text
uv run ruff format --check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py
uv run ruff check src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py
uv run mypy src/scouting/contracts/wyscout_schema.py tests/contracts/test_w04_wyscout_schema_closure.py
uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_wyscout_data_contracts.py
uv run python scripts/verify_local_only.py
```

The master may split test execution to keep the known real-match checked-path case
observable, but it may not omit that case from the later complete repository gate.

#### Review 2 — `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R1`

Exact owned files:

```text
reports/reviews/W04/wyscout-23-root-schema-closure-independent-review-R1.md
reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R1.md
```

Fix every producer hash and independently regenerate all 23 canonical schema byte
streams and content digests. Audit the complete transitive closure against the 13
existing and ten new models, including cross-field constraints; attack omission,
aliasing, forward edges, cycles, descriptor/code/serializer substitution and any
placeholder. Verdict must be `PASS` with P0/P1/P2 = `0/0/0` before Packet 3.

#### Packet 3 — `W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-01-R1`

Owner: **master-only serial gate**, after Review 2.

Exact owned files:

```text
src/scouting/contracts/wyscout_aggregates.py
scripts/materialize_wyscout_v5_contracts.py
tests/contracts/test_w04_wyscout_v2_aggregates.py
configs/schema/wyscout-v5-schema-bundle-preimage-v2.json
configs/schema/wyscout-v5-product-contract-preimage-v2.json
reports/verification/W04/wyscout-v2-aggregate-materialization-R1.md
```

First regenerate and compare all 23 accepted schema bytes. Then materialize the
exact eight-key schema-bundle-v2 preimage, hash its R20-canonical no-LF bytes once,
insert that real digest into the exact ten-key product-contract-v2 preimage, and
hash that preimage once. The product preimage must incorporate R3/R4 Gold-manifest-
derived one-product/one-boundary population/readback, all-three layer summary
physical/sole-semantic reproduction and parent-summary reconciliation. Physical
config files must be strict canonical JSON plus one terminal LF; aggregate digests
must cover the defined no-LF preimages, not their physical file LF. The script must
support deterministic write and read-only `--check`, fail on existing unequal bytes,
and never scan, substitute, infer, or write a product/data/run artifact.

Acceptance commands:

```text
uv run ruff format --check src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py tests/contracts/test_w04_wyscout_v2_aggregates.py
uv run ruff check src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py tests/contracts/test_w04_wyscout_v2_aggregates.py
uv run mypy src/scouting/contracts/wyscout_aggregates.py scripts/materialize_wyscout_v5_contracts.py
uv run python scripts/materialize_wyscout_v5_contracts.py --check
uv run pytest -q tests/contracts/test_w04_wyscout_v2_aggregates.py tests/contracts/test_w04_wyscout_schema_closure.py tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py
uv run python scripts/verify_local_only.py
```

#### Review 3 — `W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-REVIEW-01-R1`

Exact owned files:

```text
reports/reviews/W04/wyscout-v2-aggregate-materialization-independent-review-R1.md
reports/reviews/W04/returns/W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-REVIEW-01-R1.md
```

Independently reproduce all 23 schema content digests, schema-bundle-v2 preimage and
digest, then product-contract-v2 preimage and digest. Prove exact v1/R20/R21/index/
authority inheritance, the one-way graph, no self-reference, no second
LayerManifest semantic derivation, no placeholder, exact 23/8/10/25/9/15 rosters,
and substitution rejection after downstream rehash. Only a fresh `PASS` permits the
master to bind the two real v2 digests into later runtime admission/build work.

After Review 3, the master must independently inspect every byte and run the complete
repository gate. Only then may separate runtime-admission/launcher and raw-to-Gold
publication packets be dispatched. They are deliberately absent from this packet
sequence because this audit was scoped to build/schema/aggregate closure and no
publication is yet permitted.

### Dependency graph

```text
fresh R4 authority decision -> independent review -> master acceptance
  -> build/window/receipt/result contract -> independent review
  -> exact 23-root canonical schema closure -> independent review
  -> master-only schema-bundle-v2 then product-contract-v2 materialization
  -> independent aggregate review -> complete repository gate
  -> later runtime admission/launcher/product publication packets
```

The three producer write sets above do not overlap. Their dependencies are semantic,
so adding agents cannot safely make these three gates concurrent. Review work can be
prepared promptly, but no reviewer may approve work it produced and no later writer
may consume an unaccepted digest.

## Tests run

- complete reads of `AGENTS.md`, the full packet, every `read_first` artifact, and
  the incorporated R2/R3 closure sections: exit `0`.
- fixed SHA-256 reproduction with `shasum -a 256`: exit `0`; all four packet values
  matched on both checks.
- exact file/symbol inventory with bounded `rg`, `test`, `stat`, `wc`, and
  read-only source inspection: exit `0`; all absent/present surfaces above were
  reproduced.
- locked/no-sync uv model introspection:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c <13-root field inventory>`:
  exit `0`; exactly 13 existing runtime roots and the field counts in the table were
  reproduced.
- optional broad diagnostic:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider tests/contracts/test_wyscout_data_contracts.py tests/unit/test_w04_wyscout_product_formats.py`:
  manually stopped with exit `130` after `232 passed in 105.04s`; it was executing
  the known full real-match checked-path reconstruction, not reporting a failure.
  This optional audit diagnostic is not substituted for any packet or repository
  gate.

## Artifacts/evidence

- this audit:
  `reports/reviews/W04/returns/W04-POST-AUTHORITY-BUILD-SCHEMA-AUDIT-01-R1.md`
- exact controlling closure:
  `reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md`
- existing 13 runtime roots:
  `src/scouting/contracts/wyscout_data.py`
- accepted W04 Parquet encoding:
  `src/scouting/storage/formats.py`
- accepted identity runtime:
  `src/scouting/identity/wyscout.py`

## Risks

- P1: treating any of the 13 Pydantic model JSON schemas as the complete R2 closed
  schema would omit executable cross-field authority and falsely materialize v2.
- P1: starting Packet 1 before the fresh authority review/master acceptance would
  convert an unreviewed decision into implementation authority.
- P1: collapsing the eight nested result roots into only the child envelope, or
  swapping boundary/invocation order, breaks exact 23-root closure.
- P1: writing either aggregate file before all 23 canonical schema bytes are
  independently accepted creates a placeholder/anticipated digest.
- P1: any second LayerManifest semantic formula, product-derived schema digest, or
  receipt self-digest introduces ambiguity or a cycle.
- P2: the complete real-match checked-path test is intentionally expensive; its
  duration must not be used to omit it from independent or repository verification.

## Follow-up items

- Finish the currently in-progress authority producer, fresh independent review,
  and master acceptance; then issue Packet 1 with the resulting exact fixed hashes.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no implementation, authority, orchestration, config, data, product, aggregate,
  manifest, receipt, build, run, provider, network, cloud, container, CI, endpoint,
  deployment, or publication write: confirmed
