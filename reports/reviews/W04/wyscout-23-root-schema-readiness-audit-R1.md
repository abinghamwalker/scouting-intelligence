# W04 23-root schema readiness audit R1

- Task packet: `W04-WYSCOUT-23-ROOT-SCHEMA-READINESS-AUDIT-01-R1`
- Packet SHA-256: `d4cf275698e38aea0e0883f1f34255e972395e10a6eff27c913d4e210cad1062`
- Audit type: report-only readiness audit
- Verdict: **NOT READY FOR SCHEMA PRODUCER — BOUNDED REPRESENTATION AUTHORITY REQUIRED**

## Executive result

All 23 required root roles have a runtime Pydantic model. No root model is missing. The earlier-only dependency graph can be frozen without a cycle, and the smallest eventual producer surface is one new contract module plus one focused contract test module.

The producer cannot yet truthfully emit an executable, non-fixture-derived Arrow identity for every Parquet root. The frozen logical models include recursive heterogeneous `CanonicalJsonValue` values and heterogeneous fixed tuples. The current generic Arrow validator has no union representation, and Parquet cannot write Arrow dense unions. Choosing a reversible physical representation for those values would be a new serialization rule, not a mechanical transcription of the existing authority. The audit therefore stops before producing schema bytes, schema digests, or a second authority.

## Exact root inventory

The role order below is the required implemented-schema order.

| # | Root role | Runtime model | Surface | Missing? |
|---:|---|---|---|---|
| 1 | `BRONZE_KNOWN_RECORD` | `BronzeKnownRecord` | Parquet | No |
| 2 | `BRONZE_REJECTED_RECORD` | `BronzeRejectedRecord` | Parquet | No |
| 3 | `BRONZE_REJECTED_FIELD` | `BronzeRejectedField` | Parquet | No |
| 4 | `SILVER_COMPETITION` | `SilverCompetition` | Parquet | No |
| 5 | `SILVER_TEAM` | `SilverTeam` | Parquet | No |
| 6 | `SILVER_PLAYER` | `SilverPlayer` | Parquet | No |
| 7 | `SILVER_MATCH` | `SilverMatch` | Parquet | No |
| 8 | `SILVER_ACTION` | `SilverAction` | Parquet | No |
| 9 | `SILVER_LINEUP_STINT` | `SilverLineupStint` | Parquet | No |
| 10 | `SILVER_POSSESSION` | `SilverPossession` | Parquet | No |
| 11 | `SILVER_PLAYER_MATCH_FACT` | `SilverPlayerMatchFact` | Parquet | No |
| 12 | `GOLD_PLAYER_WINDOW` | `GoldPlayerWindow` | Parquet | No |
| 13 | `LAYER_MANIFEST` | `LayerManifest` | JSON | No |
| 14 | `TEMPORAL_BOUNDARY_RECEIPT` | `TemporalBoundaryReceipt` | JSON | No |
| 15 | `REBUILD_INVOCATION_RECEIPT` | `RebuildInvocationReceipt` | JSON | No |
| 16 | `ENTRYPOINT_SOURCE_RESULT` | `EntrypointSourceResult` | JSON | No |
| 17 | `COMPONENT_PROOF_RESULT` | `ComponentProofResult` | JSON | No |
| 18 | `PRE_BUILD_ADMISSION_RESULT` | `PreBuildAdmissionResult` | JSON | No |
| 19 | `REBUILD_RECEIPT_SUMMARY` | `RebuildReceiptSummary` | JSON | No |
| 20 | `LAYER_MANIFEST_SUMMARY` | `LayerManifestSummary` | JSON | No |
| 21 | `FINAL_RECHECK_RESULT` | `FinalRecheckResult` | JSON | No |
| 22 | `POST_BUILD_ID_REBUILD_RESULT` | `PostBuildIdRebuildResult` | JSON | No |
| 23 | `CHILD_RESULT_ENVELOPE` | `ChildResultEnvelope` | JSON | No |

## Canonical content required for every root

Each root content document should have one exact, canonical JSON object with these sections, in this order:

1. `canonical_schema_id`
2. `canonical_schema_version`
3. `schema_language_version`
4. `root_role`
5. `root_definition_id`
6. `definitions`
7. `parquet_projection`

The content must not contain its own digest. Its digest is computed from the canonical bytes as the R20/R21 acyclic preimage contract requires.

`definitions` must close the complete transitive model graph. It must use structured definitions for scalars, literals, enums, objects, lists, fixed tuples and unions. For every object it must record the exact serialized field order, required presence (including fields with runtime defaults), additional-field prohibition, JSON type, nullability, string grammar, numeric bounds and timestamp/decimal rules. For every list or tuple it must record ordered element definitions, exact or bounded cardinality, uniqueness and sorting rules where applicable.

Cross-field and whole-object validators must be represented as structured declarative predicates, not Python symbol names, source-code hashes, prose-only notes, or serializer hashes. The predicates must carry their operands and constants and cover, where present:

- equality, implication and mutually exclusive state fields;
- identifier reproduction and namespace/name inputs;
- digest preimages and digest equality;
- exact path and classification constraints;
- interval ordering, censoring, elapsed-minute and per-90 suppression rules;
- source-row, source-member and completion-index binding;
- action, possession and player-match population completeness;
- temporal cutoff and availability ordering;
- lineage parent/child equality and complete-manifest semantics;
- exact count, ordered membership, uniqueness and aggregate reconciliation.

The six-key implemented-schema row remains separate from root content and has exactly this order:

1. `canonical_schema_content_sha256`
2. `canonical_schema_id`
3. `canonical_schema_version`
4. `closure_dependencies`
5. `root_role`
6. `surface_kind`

`surface_kind` is exactly `IMPLEMENTED_CLOSED_SCHEMA`.

## Arrow identity boundary

The 12 product roots numbered 1–12 require an Arrow descriptor. Roots 13–23 are JSON-only and must carry the exact explicit `NOT_APPLICABLE_JSON_ONLY` projection state, not `null`, omission, or a placeholder digest.

For every Parquet root, `parquet_projection` must be an exact ordered recursive descriptor of the Arrow schema, including:

- top-level and nested field order;
- exact integer and floating widths and signedness;
- decimal precision and scale;
- timestamp unit and timezone;
- field, list-child and struct-child nullability;
- exact list child names and fixed-tuple position mapping;
- logical-to-physical projection and inverse decoding rule;
- schema, field, list and struct metadata absent at every recursive node.

The runtime `pyarrow.Schema` must be generated solely from the accepted root content. It must not be inferred from rows, fixtures, observed values, empty lists, or caller-supplied schemas. Serialization must validate exact schema equality before write; reading must apply the same accepted inverse projection before validating equality with the logical contract row. The Gold schema/hash path must consume this same accepted content and may not introduce a callback, parallel constant table, or second semantic authority.

### Executable representation gap

The logical `CanonicalJsonValue` used by all three Bronze roots is a recursive heterogeneous union of null, boolean, integer, decimal, string, array and object variants. The current storage format validator does not accept Arrow union types. Independently, PyArrow/Parquet does not serialize a dense union to Parquet. Some contract tuples also contain heterogeneous positions and cannot be encoded as a homogeneous Arrow list without an explicit projection.

Consequently, a schema producer that merely describes a dense union would not be executable, while selecting canonical JSON text, tagged structs, or another reversible representation would add a serialization rule that the frozen authorities do not currently choose. That choice must be authorized before bytes are frozen.

## Earlier-only closure dependencies

These rows are acyclic and preserve the conceptual R21 graph while inlining non-root support definitions.

| Root role | Ordered closure dependencies |
|---|---|
| `BRONZE_KNOWN_RECORD` | `[]` |
| `BRONZE_REJECTED_RECORD` | `[]` |
| `BRONZE_REJECTED_FIELD` | `[BRONZE_KNOWN_RECORD]` |
| `SILVER_COMPETITION` | `[BRONZE_KNOWN_RECORD]` |
| `SILVER_TEAM` | `[BRONZE_KNOWN_RECORD]` |
| `SILVER_PLAYER` | `[BRONZE_KNOWN_RECORD]` |
| `SILVER_MATCH` | `[BRONZE_KNOWN_RECORD, SILVER_COMPETITION, SILVER_TEAM]` |
| `SILVER_ACTION` | `[BRONZE_KNOWN_RECORD, SILVER_MATCH, SILVER_PLAYER, SILVER_TEAM]` |
| `SILVER_LINEUP_STINT` | `[SILVER_MATCH, SILVER_PLAYER, SILVER_TEAM]` |
| `SILVER_POSSESSION` | `[SILVER_ACTION]` |
| `SILVER_PLAYER_MATCH_FACT` | `[SILVER_ACTION, SILVER_LINEUP_STINT, SILVER_MATCH, SILVER_PLAYER, SILVER_POSSESSION]` |
| `GOLD_PLAYER_WINDOW` | `[SILVER_PLAYER_MATCH_FACT]` |
| `LAYER_MANIFEST` | roots 1–12 in their exact implemented-schema order |
| `TEMPORAL_BOUNDARY_RECEIPT` | `[GOLD_PLAYER_WINDOW, LAYER_MANIFEST]` |
| `REBUILD_INVOCATION_RECEIPT` | `[LAYER_MANIFEST, TEMPORAL_BOUNDARY_RECEIPT]` |
| `ENTRYPOINT_SOURCE_RESULT` | `[]` |
| `COMPONENT_PROOF_RESULT` | `[]` |
| `PRE_BUILD_ADMISSION_RESULT` | `[COMPONENT_PROOF_RESULT]` |
| `REBUILD_RECEIPT_SUMMARY` | `[]` |
| `LAYER_MANIFEST_SUMMARY` | `[LAYER_MANIFEST]` |
| `FINAL_RECHECK_RESULT` | `[REBUILD_RECEIPT_SUMMARY, LAYER_MANIFEST_SUMMARY]` |
| `POST_BUILD_ID_REBUILD_RESULT` | `[REBUILD_RECEIPT_SUMMARY, LAYER_MANIFEST_SUMMARY, FINAL_RECHECK_RESULT]` |
| `CHILD_RESULT_ENVELOPE` | `[ENTRYPOINT_SOURCE_RESULT, PRE_BUILD_ADMISSION_RESULT, POST_BUILD_ID_REBUILD_RESULT]` |

Support structures such as source envelopes, lineage objects, authority clocks, `RebuildInvocation`, and boundary summaries are transitive definitions inside their owning roots. They are not additional root rows.

## Smallest implementable producer contract

After the representation choice is authorized and independently reviewed, the producer packet should own only:

- `src/scouting/contracts/wyscout_schema.py`
- `tests/contracts/test_w04_wyscout_schema_closure.py`
- its assigned return report

The implementation must produce exactly 23 root documents and 23 six-key rows, in the order above. It must not create v2 schema files, accepted digests, product rows, manifests, provider access, new dependencies, deployment assets, or product publication.

Focused acceptance checks should prove:

1. exactly the 23 roles, exact order, exact six keys and exact surface token;
2. every referenced definition resolves and all dependency edges point strictly earlier;
3. every runtime serialized field appears exactly once and in exact order;
4. each runtime cross-field validator has a declarative predicate with exact operands/constants;
5. all 12 Parquet roots carry complete recursive Arrow descriptors; JSON-only roots carry the explicit non-applicable state;
6. two materially different valid logical values for each variant-bearing root generate the same Arrow schema;
7. serialization and inverse decoding round-trip exact canonical logical values;
8. metadata is absent recursively and width/nullability mutations fail closed;
9. Gold uses only the accepted schema content/hash path and alternative schema inputs fail closed;
10. fixture inference, caller-supplied schema/digest/callbacks and unrecognized variants fail closed.

## Blocker classification and bounded next decision

Classification: **genuine bounded authority gap; clarification/authorization required before producer implementation**.

The smallest decision is to authorize one additive schema-aware, reversible logical-to-Arrow projection rule for only the existing 12 Parquet root roles. It must specify the physical representation and inverse decoding of recursive heterogeneous JSON values and heterogeneous fixed tuples, remain inside the sole existing serializer path, and add no root, feature, population, provider access, dependency, cloud, container, CI, deployment, or second semantic derivation. That correction should receive fresh independent review before the 23-root schema producer is dispatched.

No schema bytes or digests were frozen by this audit.
