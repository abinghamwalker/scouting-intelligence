# W04 Wyscout schema design independent review R14

## Recommendation

**REWORK**

The merged R20 plus R21 design merits are acyclic, exact, conservative,
evidence-preserving, and implementable within the bounded R21 control-plane
scope. I found no P0, P1, or P2 defect in the R21 design text itself.

The review chain nevertheless has one objective P2 evidence-integrity defect:
the immutable R2 producer return is 141 lines, while both required master R2
evidence artifacts claim a complete readback of 132 lines. Because this packet
permits a PASS recommendation only with zero P0, P1, or P2 findings, the
recommendation is REWORK. The correction is bounded to predecessor master
evidence; it does not require or authorize a change to R20, R21, any accepted v1
authority, architecture, product contract, dependency, source, provider, right,
root, storage boundary, or local-only policy.

This is an independent review recommendation. It is not acceptance, does not
self-accept R21, and grants no authority to materialize either preimage or any
field, possession, feature, Bronze, Silver, Gold, manifest, receipt, build,
model, or product artifact.

## Finding summary

| severity | count | result |
|---|---:|---|
| P0 | 0 | no P0 defect found |
| P1 | 0 | no P1 defect found |
| P2 | 1 | immutable master R2 evidence states the wrong return line count |

### R14-EVIDENCE-R2-RETURN-LINE-COUNT — P2

The exact immutable R2 return at
`reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21-R2.md` is:

- 6,675 complete physical bytes;
- 141 lines by `wc -l`;
- SHA-256
  `82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10`.

That SHA-256 is the same digest recorded by the master, so the discrepancy is
not a different-file or mutable-path ambiguity. It is a false cardinality claim
about the exact bytes the master says it read.

The contradictory evidence is explicit in two required authorities:

1. `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R21-R2.yaml:25-26`
   records `PASS_1242_DESIGN_LINES_132_RETURN_LINES`, and lines 40-43 state that
   the master read all 132 R2-return lines.
2. `reports/verification/W04/wyscout-schema-design-R21-R2-master-verification.md:8-11`
   states that the master read all 132 lines of the R2 producer return.

The 132-line count is instead the exact cardinality of the original R21 R1
return:
`reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21.md` is 6,692 bytes,
132 lines, and has SHA-256
`3d53c23e3028c635f75b303f67a9fc027a96b76ed030909cbfd7b5a7567bc545`.
The evidence appears to have carried that predecessor cardinality into the R2
readback.

Impact: this does not change the R21 candidate bytes or any design conclusion,
but it makes the asserted *complete R2 readback* mechanically false. Complete
readback is an explicit high-risk review control and a dependency of this R14
packet. The defect is P2 rather than P1 because the immutable R2 return hash,
size, and contents are available, the independent R14 review read all 141
lines, and the design merits can still be reconstructed without ambiguity.

Required bounded correction: a master-owned rework artifact must accurately
bind the immutable R2 return as 6,675 bytes / 141 lines / SHA-256
`82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10`,
preserve the erroneous predecessor evidence rather than rewrite it, and rerun
the dependent master readback decision. R14 does not edit either predecessor.

## Review scope and independence

I performed a fresh merits review of the effective authority:

```text
immutable R20
+ the six and only six R21 replacement clause families
```

The six replacement families are:

1. `FIELD_AUTHORITY_ROUTE`;
2. `POSSESSION_AUTHORITY_ROUTE`;
3. `SUPPORTED_FEATURE_AUTHORITY_ROUTE`;
4. `LOCAL_RESOURCE_ROSTER`;
5. `TEMPORAL_DEPENDENCY_BINDINGS`;
6. `W04_FINAL_GATE`.

No producer or master conclusion was treated as proof. I read and reconstructed
the candidate, accepted authorities, frozen source evidence, prior returns,
packets, reviews, and verifications directly. I performed no delegation and no
Git operation. The only repository writes are this review and its mandatory
return.

The review does not reinterpret R21 as a product implementation. R21 remains a
bounded authority/control design. Its exact path strings, schema descriptors,
serializer-owner tokens, primary keys, feature rows, and tests do not assert
that a product schema, serializer, output, manifest, receipt, build, or runtime
exists.

## Exact readback

The required authorities were read completely in the packet-prescribed order:

1. `AGENTS.md`;
2. `orchestration/task_packets/W04-SCHEMA-DESIGN-REVIEW-01-R14.yaml`;
3. R20, all 4,516 lines;
4. R21, all 1,242 lines;
5. original R21 producer return, all 132 lines;
6. R21 R2 producer return, all 141 lines;
7. original producer packet;
8. R2 producer packet;
9. R1 master review;
10. R2 master review;
11. R1 master verification;
12. R2 master verification;
13. accepted field registry v1 YAML, all 1,330 lines;
14. accepted possession taxonomy v1 YAML, all 451 lines;
15. accepted field decision v1 JSON;
16. accepted field acceptance v1 JSON;
17. accepted possession decision v1 JSON;
18. accepted possession acceptance v1 JSON;
19. fixed source schema profile, all 365 lines;
20. fixed completion manifest;
21. production blueprint, all 3,219 lines;
22. implementation workflow, all 1,270 lines;
23. mandatory subagent return template, all 38 lines.

I additionally read the two accepted v1 independent-review Markdown artifacts
and the frozen 36-row event taxonomy CSV because the prior-authority and
selector checks require their physical bytes and record digests.

Key frozen physical evidence reproduced:

| artifact | lines/bytes where relevant | physical SHA-256 |
|---|---:|---|
| R20 | 4,516 lines | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 | 1,242 lines / 58,986 bytes | `08f64de257d32dafc0e47030025a22644acb1ab793e34a443bca34d18d154969` |
| R21 R1 return | 132 lines / 6,692 bytes | `3d53c23e3028c635f75b303f67a9fc027a96b76ed030909cbfd7b5a7567bc545` |
| R21 R2 return | 141 lines / 6,675 bytes | `82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10` |
| field v1 decision | 64,375 bytes | `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999` |
| field v1 candidate | 63,963 bytes | `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2` |
| field v1 review | 1,299 bytes | `e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861` |
| field v1 acceptance | 980 bytes | `fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365` |
| possession v1 decision | 22,148 bytes | `4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71` |
| possession v1 candidate | 22,189 bytes | `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d` |
| possession v1 review | 1,729 bytes | `1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4` |
| possession v1 acceptance | 1,000 bytes | `f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112` |
| event taxonomy CSV | 37 physical lines / 36 data rows | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` |
| source profile | 365 lines | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` |
| completion manifest | canonical one-line JSON | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| production blueprint | 3,219 lines | `b55e624d27529761c937291ae1bc5d08de44120ace7739e87e0aad8a1000829a` |
| implementation workflow | 1,270 lines | `73fd051a7fb374733c552351d4f4dfe7b603c5cbdd9fdb7c3079895244d5b0d7` |
| return template | 38 lines | `2d0d4fa9b706b4a4f7fe20f8f2d9f8813a25314db7de4fe6cd91c150abbf2dd5` |

The R20 and R21 physical hashes are exact. No mandatory input was missing,
unreadable, or observed at a different frozen digest.

## Merge boundary and broader-scope review

The R21 merge operator is closed to six clause families. The text explicitly
retains R20 source/provider/right/acquisition, project root, storage, identity
semantics, temporal inequalities, product layer architecture, path templates,
serializer ownership, primary keys, build identity, environment admission,
local-only, uv, Git, and product-claim clauses. Every R21 repetition of a
retained value is either an exact preimage member or a test input.

The correction is additive:

- accepted field and possession v1 files remain immutable resources;
- field and possession v2 routes supersede future semantic use without
  rewriting history;
- the feature v1 route retains its already fixed IDs and paths because it has
  no accepted candidate;
- the immutable first 17 resources remain positions 1 through 17;
- no control artifact grants a product write.

I found no R21 dependency addition, lockfile change, new source/provider/right,
storage redesign, root change, network action, cloud/container/endpoint/hosted
CI/deployment surface, or product implementation authorization.

## Canonical bytes and acyclic digest graph

The canonicalization contract is internally consistent:

```text
canonical_bytes(P) =
  UTF8(canonical_json(P_without_any_own_digest)) || LF
canonical_sha256(P) = SHA256(canonical_bytes(P))
```

It preserves explicit array order, Unicode-code-point object-key order, strict
UTF-8/NFC strings, lowercase UUID and digest spelling, strict integer typing,
and one terminal LF. Both materialized preimages must be canonical JSON files,
so their physical and canonical digests are equal. Neither preimage contains
its own digest.

The reconstructed DAG is:

```text
R20 physical bytes
  -> R21 physical bytes
       |-> product-contract preimage --|
       |-> schema-bundle preimage -----|
                                       v
                                  field v2
                                    -> possession v2
                                      -> feature v1
                                        -> five dependencies
                                          -> later build/product work
```

The two preimages are siblings. Each binds R20 and R21; neither binds the other.
Their presentation order does not create an edge. Both converge only because
field v2 binds both accepted preimage digests.

The forbidden-cycle review found no own digest, sibling digest, downstream
field/possession/feature authority digest, concrete feature hash, build ID, run
ID, product output, generated manifest/receipt, clock, root, host, absolute
path, environment observation, or mutable runtime value in either preimage.
The feature digest remains a typed unresolved placeholder. No reverse,
self, sibling, or feature-to-preimage edge is specified.

## Immutable prior-authority reconstruction

Each embedded `prior_authority` object has exactly 17 keys and those keys occur
in Unicode lexical order:

```text
acceptance_id
acceptance_physical_sha256
acceptance_schema_version
acceptance_sha256
accepted_at
accepted_by
candidate_id
candidate_physical_sha256
candidate_sha256
decision_id
decision_physical_sha256
decision_sha256
review_id
review_physical_sha256
review_recommendation
review_record_sha256
supersedes_acceptance_id
```

The important corrected ordering is
`review_recommendation` before `review_record_sha256`.

For field v1, I reconstructed the prior object as the complete 15-key accepted
acceptance plus:

- `acceptance_physical_sha256 =
  fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365`;
- `acceptance_sha256` equal to that digest because the acceptance is canonical
  JSON bytes.

Every embedded field value equals the actual accepted file. The candidate
physical digest is
`805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2`;
its canonical parsed-YAML-with-terminal-LF digest is
`fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`.
The review physical digest is
`e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861`;
the exact canonical fenced record including its terminal LF hashes to
`8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0`.
The recommendation is PASS and v1 supersession is null.

For possession v1, the reconstructed acceptance physical/canonical digest is
`f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112`.
The candidate physical digest is
`e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`;
its canonical digest is
`6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa`.
The review physical digest is
`1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4`;
its exact canonical fenced record including LF hashes to
`40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962`.
The recommendation is PASS and v1 supersession is null.

Both embedded objects also reproduce exact candidate/decision/review IDs,
canonical UUID actors, canonical UTC clocks, decision physical/canonical
digests, and acceptance schema version. No field is absent, additional, or
incorrect.

## Field v2 reconstruction

The accepted field v1 YAML and decision each contain exactly 119 rows. Their
field arrays, policies, and bound inputs compare equal, and the accepted
candidate physical and canonical digests reproduce its acceptance record.

R21 retains the exact source-profile roster sequence across competition, team,
player, match, action, event-taxonomy, and tag-taxonomy. It expressly forbids
re-sorting by `(record_kind, json_path)`.

The exact R21 `$.subEventId` row has the same eight-field key set as its v1
predecessor. Mechanical comparison shows only these members change:

- `canonical_field`;
- `decision`;
- `rationale`;
- `transform`.

The unchanged members are:

- `record_kind = action`;
- `json_path = $.subEventId`;
- `source_support = PROFILE_AND_EVENT_TAXONOMY`;
- measured source shape
  `integer:3,063,574` and `string:7,821`, in that order.

Thus the design changes exactly one of 119 rows and retains the measured string
evidence count.

The new transform is closed. It reads the already derived strict
`action_event_taxonomy_id`, inspects the raw subevent JSON type without
truthiness or numeric conversion, and emits only when both event and subevent
are strict integers and the exact pair occurs in the frozen taxonomy. Python
`bool` and JSON booleans are expressly excluded from integer admission.

The following never emit a canonical subevent:

- numeric or whitespace/sign/leading-zero strings, including `"10"`,
  `" 10"`, `"+10"`, and `"010"`;
- all other strings;
- booleans;
- null;
- decimal/exponent JSON numbers;
- arrays and objects;
- strict integers with an absent canonical event;
- strict integers whose event/subevent pair is absent from the frozen taxonomy.

The design forbids runtime event/subevent label or name lookup. It never reads
`$.subEventName` to recover an ID.

Every non-emitting value remains exact typed raw rejected-field evidence. The
reason-code partition is complete and disjoint:

- strings:
  `ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`;
- booleans:
  `ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER`;
- null:
  `ACTION_SUBEVENT_NULL_UNMAPPED`;
- noninteger numbers:
  `ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED`;
- arrays:
  `ACTION_SUBEVENT_ARRAY_UNMAPPED`;
- objects:
  `ACTION_SUBEVENT_OBJECT_UNMAPPED`;
- unknown strict integer/absent canonical event:
  `ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY`.

I found no coercion, evidence loss, arithmetic guess, neighbor inference,
default ID, label fallback, or unpartitioned measured type.

## Possession v2 reconstruction

The accepted possession v1 decision and YAML each have exactly 36 predicates.
The arrays, policies, and bound inputs compare byte-semantically under canonical
JSON. The 36 `(event_id, subevent_id)` pairs are unique and equal the 36 pairs
in the frozen event taxonomy CSV. All accepted required/forbidden tag sets are
empty. Eighteen predicates require `ACTION_TEAM`; eighteen use `NONE`.

R21 v2 copies every v1 predicate, choice, actor, attachment, tag set, and
rationale without widening any predicate. It binds the accepted field v2
candidate and acceptance and separately retains complete possession v1 history
through its 17-key prior object.

Possession v2 can consume only:

```text
action_event_taxonomy_id
action_subevent_taxonomy_id
action_team_source_id
action_tag_ids
```

The selector fails closed when event or subevent is absent, mistyped, boolean,
or not an exact predicate pair. It fails closed on a missing/mistyped canonical
tag array, a failed required/forbidden tag predicate, or a missing team where
the accepted predicate requires `ACTION_TEAM`. It does not synthesize an empty
tag array. `control_team_source=NONE` does not permit a team value to invent
control.

The selector cannot read raw event/subevent fields, rejected evidence, event or
subevent names, or taxonomy labels. A string subevent remains ineligible even
when its characters resemble an accepted integer.

The explicit output is closed to:

```text
ELIGIBLE_RESOLVED
INELIGIBLE_UNMAPPED
```

Eligibility is an accepted project-owned possession inference under unchanged
same-period sequence rules, not a provider-native possession claim.

## Exact feature authority

The R21 feature table reconstructs to exactly 15 unique rows sorted by
`feature_name`. State cardinalities are:

- four `SUPPORTED`;
- four `SUPPRESSED_UNSUPPORTED_DENOMINATOR`;
- seven `UNAVAILABLE`.

Each row has exactly eight fields:
`aggregation`, `applicability`, `denominator`, `feature_name`, `input_fields`,
`output_type`, `reason`, and `state`.

The four exact supported rows are:

| feature | exact inputs | aggregation | applicability | denominator | output |
|---|---|---|---|---|---|
| `action_count` | `["action_source_id"]` | `COUNT` | `ACTION_PRESENT` | `NONE` | `int64` |
| `coordinate_known_action_count` | `["action_positions"]` | `COUNT` | `POSITION_PRESENT` | `NONE` | `int64` |
| `match_count` | `["match_source_id"]` | `DISTINCT_COUNT` | `ALWAYS` | `NONE` | `int64` |
| `resolved_possession_action_count` | `["action_event_taxonomy_id","action_subevent_taxonomy_id","action_team_source_id"]` | `COUNT` | `POSSESSION_ELIGIBLE` | `NONE` | `int64` |

`POSSESSION_ELIGIBLE` additionally requires the explicit accepted possession-v2
state `ELIGIBLE_RESOLVED`; an absent canonical subevent cannot satisfy it.

The four suppressed rows are exactly `action_rate`, `actions_per_90`,
`minutes_lower`, and `minutes_upper`. Each has empty inputs, `aggregation=NONE`,
`applicability=NEVER`, `denominator=UNSUPPORTED_MINUTES`, null output, and the
fixed no-accepted-elapsed-minutes reason.

The seven unavailable rows are exactly `continuous_time_seconds`,
`outcome_dependent_count`, `provider_native_possession_count`,
`resolved_lineup_stint_count`, `role_inferred_count`,
`unresolved_action_count`, and `value_model_sum`. Each has empty inputs,
`aggregation=NONE`, `applicability=NEVER`, `denominator=NONE`, null output, and
its exact conservative reason.

The ten-key policy object closes absence, continuous time, minutes, outcome,
per-90, provider-native possession, rate, role, unsupported, and value-model
behavior. There is no hidden or sixteenth feature and no feature hash before
independent feature review and acceptance.

## Product-contract preimage

The product-contract preimage has the exact nine top-level keys:
`authority_links`, `layer_order`, `manifest_receipt_templates`,
`path_templates`, `policy`, `preimage_id`, `preimage_schema_version`,
`primary_key_contracts`, and `serializer_ownership`.

The 17 path descriptors are unique and ordered:

- three Bronze known/rejected roles;
- eight Silver product roles;
- one Gold player-window role;
- three layer-manifest roles;
- rebuild invocation receipt;
- temporal boundary receipt.

They reproduce the R20 repo-relative templates. No descriptor creates a path.

The ten serializer owners are sorted. Their role arrays assign all 17 path roles
exactly once: `bronze.py` owns known/rejected Bronze plus Bronze manifest,
`entities.py` owns the four entity Silver roles, the five remaining product
owners are exact, `silver_manifest.py` owns only Silver manifest, `gold.py`
owns Gold plus Gold manifest, `rebuild.py` owns only the invocation receipt,
and `temporal_boundary.py` owns only the boundary receipt.

The two primary-key rows reproduce the exact R20 player-match and Gold
player-window keys. The five manifest/receipt templates repeat path roles
13-17, their exact owners, and exact templates. `layer_order` is exactly
`BRONZE`, `SILVER`, `GOLD`.

The policy is closed to control-plane-only, product-bytes-forbidden, and
no-product-before-complete-R21-gate.

## Schema-bundle preimage

The schema-bundle preimage has exactly six top-level keys:
`authority_links`, `dependency_order`, `descriptors`,
`feature_schema_hash_placeholder`, `preimage_id`, and
`preimage_schema_version`.

There are exactly 16 unique schema descriptors. Their orders are 1 through 16,
`dependency_order` equals the descriptor ID sequence, and every `depends_on`
entry points only to an earlier descriptor. The dependency graph is therefore
acyclic by construction.

Every descriptor uses the exact surface kind
`CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`. The version tokens
describe R20 contract surfaces only. They are not row models or implemented
Parquet schemas.

The feature placeholder is closed to:

- `concrete_value = null`;
- JSON type `string`;
- lowercase 64-hex pattern;
- the accepted supported-feature candidate digest as resolution source;
- unresolved-until-acceptance state.

It requires a later hash while correctly refusing to invent one now.

## Resources and temporal dependencies

The resource formula reconstructs exactly:

```text
17 immutable R20 resources
+ R21
+ R14
+ two preimages
+ four field-v2 route artifacts
+ four possession-v2 route artifacts
+ one cross-authority test
= 30
```

The 30 paths are unique. Positions 1-17 are byte-equal as strings and order to
the immutable R20 allowlist. The supported-feature candidate and three
authority artifacts remain old members 4 and 14-16, so R21 correctly adds zero
duplicate feature paths. The cross-authority independent review is control
evidence rather than a 31st runtime local resource.

Each later resource row remains obligated to bind the exact path, physical
digest, size, mode, purpose, parser/schema version, and authority link. No
directory shorthand, glob, optional path, output, manifest/receipt output, or
runtime evidence is admitted.

The temporal dependency cardinality remains five:

- one source manifest;
- one identity evidence dependency;
- field v2 feature schema;
- possession v2 feature schema;
- supported-feature v1 feature schema.

R20 wire schema, UUIDv5 derivation, ordering, lineage hash, strict-before
inequalities, and watermark remain unchanged. Identity stays route v1 and its
future unmaterialized decision binds accepted field v2. Field, possession, and
feature candidates use canonical rather than physical candidate digests.
Hybrid field-v1/possession-v2 or possession-v1/feature-v1-under-R21
combinations are explicitly rejected.

## Serial packet and ownership reconstruction

The packet table contains exactly 16 unique serial packet IDs in order. The
exhaustive ownership expansion contains 44 exact paths, all unique across
packets. Candidate producer, independent reviewer, and master acceptance/gate
ownership is separated.

The final cross-authority sequence is correctly split:

1. `W04-R21-CROSS-AUTHORITY-TEST-01-R1`;
2. `W04-R21-CROSS-AUTHORITY-REVIEW-01-R1`;
3. `W04-R21-CROSS-AUTHORITY-GATE-01-R1`.

The review binds the complete physical test and return digests and uses an actor
distinct from every authority/test producer. The master gate later binds the
fixed review's complete physical digest and requires PASS. A combined
test/review/gate scope is forbidden.

Packet YAML and orchestration-state changes remain master-only outside producer
scopes. Shared contracts, candidate configs, acceptances, orchestration state,
and the cross-authority test are never parallel write scopes. No intermediate
checkpoint or subagent Git action is permitted.

## Composability and gate review

The positive test plan covers accepted pair admission, all 36 copied
predicates, exact canonical selector flow, missing-subevent rejection, exact
possession-feature applicability, 15/4 feature cardinality, reproducible
preimages, sibling DAG, 17/30 resources, v2 supersession, digest propagation,
review/test producer separation, master binding, and no product path before the
gate.

The negative plan covers all required high-risk boundaries:

- string/bool/null/noninteger/container subevent rejection;
- language bool-as-int rejection;
- preservation of all 7,821 strings and exact reason;
- no unknown-integer or label/name admission;
- no raw selector fallback;
- no v1/v2 hybrid;
- exact prior values, order, cardinality, digests, and supersession;
- v1 immutability;
- decision/candidate/review/acceptance digest stability;
- no preimage self/sibling/downstream/runtime/output material;
- no cycle or concrete premature feature hash;
- descriptor-only enforcement;
- exact 15-row feature closure and no unsupported input;
- no use before upstream acceptance;
- no product/schema digest substitution;
- canonical-versus-physical digest distinction;
- exact 30-resource closure;
- fixed independent review integrity and actor separation;
- no combined scope or premature gate;
- no product, serializer, manifest, receipt, or build before complete gate.

The final R21 gate lists all twelve AGENTS commands in exact order, with the
phase placeholder correctly resolved to W04:

```text
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src/scouting scripts
uv run lint-imports
uv run pytest -q
uv run bandit -q -r scripts src
uv run python scripts/install_local_git_guards.py --check
uv run python scripts/verify_local_only.py
uv run python scripts/verify_phase.py --phase W04
git status --short
git remote
```

The 18 additive checks retain independent review, both preimages, all authority
routes, exact cardinalities, anti-mixing, cross-authority flow, forbidden
product scan, bytecode equality, full readback, and a machine PASS gate.
Focused tests never replace the shared suite.

## Local-only and no-product boundary

R21 ends at a control-plane gate. It expressly forbids Bronze, Silver, Gold,
feature materialization, serializers, generated manifests/receipts,
runtime/build invocation, model/product implementation, provider/network
acquisition, cloud/container/endpoint/hosted CI/deployment, and any Git remote.

This review created no config, orchestration, script, source, migration, data,
run, test, environment, dependency, lock, authority, preimage, product, build,
manifest, or receipt artifact. It used no network and no Git operation.

## Commands and reconstruction evidence

All Python reconstruction commands set `PYTHONDONTWRITEBYTECODE=1` before `uv`
started and used `uv run --locked --no-sync python -B`; standard-library-only
commands also used `-S -B`. The first Python statements asserted
`sys.dont_write_bytecode` and the environment value before other file-backed
imports.

Read-only checks independently reproduced:

- R20/R21 bytes, lines, and physical digests;
- both 17-key prior objects against actual v1 artifacts;
- physical and canonical YAML digests including terminal LF;
- exact fenced-review record digests including terminal LF;
- accepted decision/candidate array equality;
- field row cardinality 119 and one-row change surface;
- possession predicate cardinality/pair uniqueness 36/36;
- exact equality to the frozen 36-row event taxonomy;
- feature cardinality/state split 15/4/4/7;
- path-role cardinality/uniqueness 17/17;
- serializer assignment 17 roles exactly once;
- descriptor cardinality 16 and earlier-only dependency edges;
- resource cardinality/uniqueness 30 and immutable first 17;
- temporal dependency cardinality five;
- packet cardinality 16 and 44 disjoint sole-write paths;
- all twelve final gate commands after resolving `<Wxx>` to W04;
- immutable return bytes, line counts, and digests.

The packet acceptance checks were run after the final authorized edits:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c \
  "<review exists, >15000 bytes, recommendation, R21 digest, P0/P1/P2 assertions>"
```

Result: PASS.

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B \
  scripts/verify_local_only.py
```

Result: PASS; all local-only checks passed.

## Bytecode inventory evidence

The shell-only preflight ran before either design was read and before any
Python invocation. It inventoried every existing repository `.pyc`, including
lexical and physical path, size, mode, link count, mtime epoch, first sixteen
bytes, and complete SHA-256; it also counted every `__pycache__` directory.

Exact preflight:

```text
cache_directory_count=150
pyc_count=1145
inventory_line_count=1149
inventory_sha256=9c734eb70eab9a8c39798639b37ba4caf18307fd46d1ce4b14b72e1c36abc3fc
inventory_path=/tmp/W04-SCHEMA-DESIGN-REVIEW-01-R14-preflight.txt
```

An intermediate identical reconstruction after all read-only merits helpers
also had 1,149 lines and SHA-256
`9c734eb70eab9a8c39798639b37ba4caf18307fd46d1ce4b14b72e1c36abc3fc`;
`cmp` returned zero.

The terminal postflight used the identical shell algorithm after the final
review edit and acceptance commands:

```text
cache_directory_count=150
pyc_count=1145
inventory_line_count=1149
inventory_sha256=9c734eb70eab9a8c39798639b37ba4caf18307fd46d1ce4b14b72e1c36abc3fc
inventory_path=/tmp/W04-SCHEMA-DESIGN-REVIEW-01-R14-postflight.txt
preflight_postflight_cmp=IDENTICAL
```

No bytecode was created, deleted, replaced, mutated, relinked, or
metadata-drifted by this review.

## Residual risks and disposition

The only observed P0-P2 finding is the P2 master-evidence cardinality mismatch.
The R21 design merits have no residual P0-P2 defect after the stated
reconstruction. Future implementation risk remains intentionally gated:
preimages, v2 authorities, feature authority, cross-authority tests/review, and
the complete master gate do not yet exist and must be produced in their exact
serial packets.

The P2 correction must preserve:

- immutable R20;
- immutable R21 at
  `08f64de257d32dafc0e47030025a22644acb1ab793e34a443bca34d18d154969`;
- both immutable producer returns;
- the inaccurate R2 predecessor evidence as historical evidence;
- all accepted v1 artifacts.

It must add accurate master-owned successor evidence rather than rewrite history.
After that bounded evidence correction, a master should rerun the dependent
review-chain gate. This R14 recommendation remains REWORK until that happens.
