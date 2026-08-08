# W04 Wyscout v5 bounded schema correction R21

Status: **CANDIDATE FOR INDEPENDENT REVIEW — NOT ACCEPTED — NO PRODUCT AUTHORITY**

Authority ID: `w04-wyscout-schema-design-R21`

Frozen predecessor:

```text
path = reports/reviews/W04/wyscout-schema-design-R20.md
physical_sha256 = 8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047
```

This document is the bounded additive correction authorized in
`W04-SCHEMA-DESIGN-01-R21`. It is a control-plane design authority only. It
does not create, claim, or authorize a Bronze, Silver, Gold, feature, receipt,
manifest, runtime, endpoint, container, cloud service, hosted CI job, deployment,
or public product. Implementation remains prohibited until every authority and
test in the final R21 gate has independently passed.

## 1. Exact merge rule and scope boundary

The merge operator is:

```text
effective_W04_authority =
  immutable_R20
  with only the following R20 clause families replaced by R21:
    FIELD_AUTHORITY_ROUTE
    POSSESSION_AUTHORITY_ROUTE
    SUPPORTED_FEATURE_AUTHORITY_ROUTE
    LOCAL_RESOURCE_ROSTER
    TEMPORAL_DEPENDENCY_BINDINGS
    W04_FINAL_GATE
```

All other R20 clauses remain byte-bound and authoritative. In particular, R21
does not change the source, provider, rights, acquisition, root, storage,
identity semantics, temporal inequalities, layer architecture, product path
templates, serializer ownership, primary keys, build identity, environment
admission, local-only boundary, uv policy, Git policy, or product claim. Where
this document repeats an R20 value, the repetition closes an R21 preimage or
test input; it does not silently rewrite R20.

The replacement is additive and evidence-preserving:

1. every v1 field and possession artifact remains immutable;
2. new v2 routes supersede their accepted v1 routes for future implementation;
3. the existing supported-feature v1 route has no prior accepted feature
   authority, so its IDs and paths remain unchanged;
4. the old 17 resources remain present in the new resource roster;
5. no accepted v1 artifact is deleted, renamed, rewritten, or reinterpreted;
6. no product write is permitted by a design, preimage, decision, candidate,
   review, acceptance, return, verification, or passing focused test alone.

If an implementer finds that the exact contracts below require a new product
schema, different storage, different path, changed provider, changed rights,
dependency or lock change, project-root change, network, cloud, container,
endpoint, hosted CI, deployment, or mutation of v1 evidence, the packet must
stop. That is a broader decision and is not authorized by R21.

The fresh design review has fixed ID
`w04-wyscout-schema-design-independent-review-R15` and fixed path
`reports/reviews/W04/wyscout-schema-design-independent-review-R15.md`. The
master records independent readback of this design at
`reports/verification/W04/wyscout-schema-design-R21-master-verification.md`
and readback of the review at
`reports/verification/W04/wyscout-schema-design-independent-review-R15-master-verification.md`.
Neither a producer return nor the independent review self-accepts R21.

R14 remains immutable failed control evidence. Its review at
`reports/reviews/W04/wyscout-schema-design-independent-review-R14.md`, return
at
`reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R14.md`, master
review at
`orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-REVIEW-01-R14.yaml`, and
master verification at
`reports/verification/W04/wyscout-schema-design-independent-review-R14-master-verification.md`
remain preserved byte-for-byte. R14 is not an accepted R21 resource or
implementation authority and remains outside the exact 30-resource runtime
roster.

## 2. Canonical bytes, digests, clocks, and actors

All canonical JSON in this correction uses the unchanged R20 rules:

- strict UTF-8;
- Unicode strings in NFC;
- object keys sorted by Unicode code point;
- arrays retained in their explicitly declared order;
- no insignificant whitespace;
- lowercase canonical UUID strings;
- lowercase 64-hex SHA-256 strings;
- JSON integer means the JSON lexical integer type and excludes boolean;
- no NaN or infinity;
- exactly one terminal LF in a materialized canonical JSON file.

For any materialized preimage `P`:

```text
canonical_bytes(P) =
  UTF8(canonical_json(P_without_any_own_digest)) || 0x0a

canonical_sha256(P) =
  lowercase_hex(SHA256(canonical_bytes(P)))
```

The terminal LF is part of the digest. Parsing and canonical reserialization
must reproduce identical bytes. A physical file digest must equal the canonical
digest for both preimages. No digest field naming the preimage itself is
permitted inside that preimage.

Decision, review, and acceptance actors remain canonical UUIDs and their clocks
remain canonical UTC instants. All R20 strict-before-cutoff rules remain
unchanged. A future R21 decision, review, or acceptance at or after a feature
cutoff is ineligible.

## 3. Immutable prior-authority records

Each v2 decision contains a `prior_authority` object. The object is closed and
has exactly these seventeen keys:

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

It is not a mutable pointer. It is a complete copy of the accepted v1 acceptance
record plus the acceptance file's physical/canonical digest. Unknown, omitted,
null where not fixed, or additional keys fail. The candidate may repeat this
same object for direct audit, but it must be byte-equal to the decision object.
The v2 acceptance does not embed the object because the unchanged closed
`w04-authority-acceptance-v1` schema has fifteen keys; instead it binds the v2
decision digest and sets the required supersession field.

### 3.1 Exact field v1 prior authority

```json
{
  "acceptance_id": "w04-wyscout-field-semantic-acceptance-v1",
  "acceptance_physical_sha256": "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365",
  "acceptance_schema_version": "w04-authority-acceptance-v1",
  "acceptance_sha256": "fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365",
  "accepted_at": "2026-07-30T15:45:59Z",
  "accepted_by": "4efe5691-8903-5148-8275-30d2e7e8aed0",
  "candidate_id": "w04-wyscout-field-registry-v1",
  "candidate_physical_sha256": "805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2",
  "candidate_sha256": "fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034",
  "decision_id": "w04-wyscout-field-semantic-decisions-v1",
  "decision_physical_sha256": "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
  "decision_sha256": "e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999",
  "review_id": "w04-wyscout-field-semantic-independent-review-R1",
  "review_physical_sha256": "e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861",
  "review_recommendation": "PASS",
  "review_record_sha256": "8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0",
  "supersedes_acceptance_id": null
}
```

### 3.2 Exact possession v1 prior authority

```json
{
  "acceptance_id": "w04-wyscout-possession-semantic-acceptance-v1",
  "acceptance_physical_sha256": "f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112",
  "acceptance_schema_version": "w04-authority-acceptance-v1",
  "acceptance_sha256": "f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112",
  "accepted_at": "2026-07-30T16:55:47Z",
  "accepted_by": "4efe5691-8903-5148-8275-30d2e7e8aed0",
  "candidate_id": "w04-wyscout-possession-taxonomy-v1",
  "candidate_physical_sha256": "e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d",
  "candidate_sha256": "6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa",
  "decision_id": "w04-wyscout-possession-semantic-decisions-v1",
  "decision_physical_sha256": "4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71",
  "decision_sha256": "4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71",
  "review_id": "w04-wyscout-possession-semantic-independent-review-R1",
  "review_physical_sha256": "1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4",
  "review_recommendation": "PASS",
  "review_record_sha256": "40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962",
  "supersedes_acceptance_id": null
}
```

## 4. Expressly acyclic authority graph

The only valid dependency graph is the following directed acyclic graph:

```text
R20 complete physical bytes/SHA-256
  -> R21 complete frozen Markdown physical bytes/SHA-256
       |-> product-contract preimage canonical JSON bytes/SHA-256 --|
       |-> schema-bundle preimage canonical JSON bytes/SHA-256 -----|
                                                                   v
                    field v2 decision/candidate/review/acceptance
                      -> possession v2 decision/candidate/review/acceptance
                        -> supported-feature v1 decision
                          -> supported-feature v1 candidate/review/acceptance
                            -> later five-dependency set
                              -> later build identity and product implementation
```

The product-contract and schema-bundle preimages are sibling nodes. Each depends
directly on R21; neither depends on the other. Both sibling digests are required
by field v2 and therefore converge on the field v2 node. The topological
presentation order of the two sibling preimages does not create a dependency
between them. Neither contains:

- its own physical or canonical digest;
- the other preimage's digest;
- any field v2 decision, candidate, review, or acceptance digest;
- any possession v2 decision, candidate, review, or acceptance digest;
- any supported-feature decision, candidate, review, acceptance, or feature
  schema digest;
- a concrete `feature_schema_hash`;
- a build ID, run ID, product output byte, generated manifest byte, generated
  receipt byte, clock, root, host, absolute path, environment observation, or
  mutable runtime value.

The field v2 route binds both preimages, so the preimages precede field v2.
Possession v2 binds field v2 acceptance, so it follows field v2. The feature
route binds both accepted v2 routes and both preimages. Reversing any edge,
substituting a digest, inserting a self-digest, or resolving the feature
placeholder before feature acceptance is a hard cycle/substitution failure.

## 5. Field semantic authority v2

### 5.1 Fixed IDs and paths

| role | fixed ID | exact path |
|---|---|---|
| decision | `w04-wyscout-field-semantic-decisions-v2` | `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json` |
| candidate | `w04-wyscout-field-registry-v2` | `configs/schema/wyscout-v5-field-registry-v2.yaml` |
| independent review | `w04-wyscout-field-semantic-independent-review-v2-R1` | `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md` |
| acceptance | `w04-wyscout-field-semantic-acceptance-v2` | `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json` |

The decision schema version is `w04-field-semantic-decision-v2`. The registry
schema version is `w04-field-registry-v2`. The acceptance schema remains
`w04-authority-acceptance-v1`, and its
`supersedes_acceptance_id` is exactly
`w04-wyscout-field-semantic-acceptance-v1`.

### 5.2 Closed route bindings

The field v2 decision `bound_inputs` object has exactly these ten keys:

```text
completion_manifest_sha256
event_taxonomy_source_sha256
product_contract_preimage_id
product_contract_preimage_sha256
r20_design_sha256
r21_design_sha256
schema_bundle_preimage_id
schema_bundle_preimage_sha256
source_schema_profile_sha256
tag_taxonomy_source_sha256
```

The four source digests equal v1:

```text
completion_manifest_sha256 =
  69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1
event_taxonomy_source_sha256 =
  ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842
source_schema_profile_sha256 =
  569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649
tag_taxonomy_source_sha256 =
  e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922
r20_design_sha256 =
  8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047
product_contract_preimage_id =
  w04-wyscout-product-contract-preimage-v1
schema_bundle_preimage_id =
  w04-wyscout-schema-bundle-preimage-v1
```

`r21_design_sha256` is the SHA-256 of the complete frozen physical bytes of this
R21 Markdown file. The two preimage SHA fields are their accepted canonical JSON
byte digests. No bare `product_contract_digest` or `schema_bundle_digest` key is
allowed.

The v2 decision has exactly:

```text
authority_class
bound_inputs
decided_at
decided_by
decision_id
decision_schema_version
decisions
policies
prior_authority
source_id
```

The v2 candidate parses to exactly:

```text
bound_inputs
decision_id
decision_sha256
fields
policies
prior_authority
registry_id
registry_schema_version
source_id
```

The candidate repeats the decision's `bound_inputs`, `fields`, `policies`,
`prior_authority`, and `source_id` byte-semantically. It contains exactly 119
rows in the exact R20 source-profile roster sequence: `competition`, `team`,
`player`, `match`, `action`, `event-taxonomy`, and `tag-taxonomy`, with every
kind retaining its declared profile order. This is not a lexical
`(record_kind, json_path)` sort. Exactly 118 rows are semantically identical to
v1. Only `(record_kind="action", json_path="$.subEventId")` changes.

### 5.3 Exact strict action subevent row

The changed row is:

```yaml
canonical_field: action_subevent_taxonomy_id
decision: TRANSFORM
json_path: $.subEventId
rationale: >-
  action field $.subEventId has measured shape integer:3063574,
  string:7821. Emit action_subevent_taxonomy_id only from a strict JSON
  integer admitted by the exact frozen (event_id,subevent_id) taxonomy pair.
  Boolean is not integer. Strings and every other type are never parsed or
  coerced. Non-admitted values remain raw PRESERVE_UNMAPPED rejected-field
  evidence. Runtime label/name lookup is forbidden.
record_kind: action
source_shape:
  - json_type: integer
    count: 3063574
  - json_type: string
    count: 7821
source_support: PROFILE_AND_EVENT_TAXONOMY
transform:
  accepted_json_type: STRICT_INTEGER
  admitted_key: [action_event_taxonomy_id, raw_subevent_integer]
  boolean_is_integer: false
  kind: EVENT_SUBEVENT_TAXONOMY_ID_V2
  non_integer_policy: PRESERVE_UNMAPPED
  runtime_label_matching: FORBIDDEN
  string_policy: PRESERVE_UNMAPPED_NO_COERCION
  taxonomy_sha256: ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842
  unknown_integer_policy: PRESERVE_UNMAPPED
```

`EVENT_SUBEVENT_TAXONOMY_ID_V2` is a closed transform. Its algorithm is:

1. Read the already field-v2-derived `action_event_taxonomy_id`.
2. Inspect the measured JSON type of the raw `$.subEventId` without language
   truthiness or numeric conversion.
3. If the measured type is not strict JSON integer, emit no
   `action_subevent_taxonomy_id`.
4. If the measured type is strict JSON integer but the exact integer pair
   `(action_event_taxonomy_id, raw_subevent_integer)` is absent from the frozen
   taxonomy rows, emit no canonical value.
5. Only when both values are strict admitted integers emit the raw subevent
   integer unchanged as `action_subevent_taxonomy_id`.

Python `bool` is explicitly rejected even though it is a subclass of `int`.
JSON `true` and `false`, null, decimal/exponent numbers, arrays, objects, numeric
strings such as `"10"`, signed/whitespace strings such as `" 10"` or `"+10"`,
all other strings, and unknown integers never produce a canonical value.
`$.subEventName`, `event_label`, and `subevent_label` remain forbidden and
cannot be consulted at runtime.

### 5.4 Exact rejected-field outcomes

Every non-emitting value is retained in the unchanged rejected-field product
shape as exact typed raw evidence. The mapping from measured condition to exact
reason is closed:

| measured condition | decision | exact reason code |
|---|---|---|
| JSON string, including all measured 7,821 strings | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED` |
| JSON boolean | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER` |
| JSON null | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_NULL_UNMAPPED` |
| JSON non-integer number | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED` |
| JSON array | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_ARRAY_UNMAPPED` |
| JSON object | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_OBJECT_UNMAPPED` |
| strict integer with absent canonical event or absent exact pair | `PRESERVE_UNMAPPED` | `ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY` |

No string is rewritten to an integer. No raw value is discarded. No unknown
integer is guessed by arithmetic, label, name, neighboring row, or default.

## 6. Possession semantic authority v2

### 6.1 Fixed IDs and paths

| role | fixed ID | exact path |
|---|---|---|
| decision | `w04-wyscout-possession-semantic-decisions-v2` | `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json` |
| candidate | `w04-wyscout-possession-taxonomy-v2` | `configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml` |
| independent review | `w04-wyscout-possession-semantic-independent-review-v2-R1` | `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md` |
| acceptance | `w04-wyscout-possession-semantic-acceptance-v2` | `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json` |

The decision schema version is `w04-possession-semantic-decision-v2`. The
candidate schema version is `w04-possession-taxonomy-v2`. The acceptance schema
remains `w04-authority-acceptance-v1`, and
`supersedes_acceptance_id` is exactly
`w04-wyscout-possession-semantic-acceptance-v1`.

### 6.2 Exact possession bindings

The possession v2 `bound_inputs` object has exactly these five keys:

```text
event_taxonomy_source_sha256
field_acceptance_sha256
field_registry_canonical_sha256
field_registry_id
tag_taxonomy_source_sha256
```

Values are:

```text
field_registry_id = w04-wyscout-field-registry-v2
field_registry_canonical_sha256 = accepted field v2 candidate canonical SHA-256
field_acceptance_sha256 = accepted field v2 acceptance canonical SHA-256
event_taxonomy_source_sha256 =
  ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842
tag_taxonomy_source_sha256 =
  e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922
```

There is no field v1 ID/digest, bare design digest, preimage digest, name
taxonomy, or other input in this object. The complete v1 possession route is
bound separately through the exact `prior_authority` object in Section 3.2.

The v2 decision has exactly:

```text
authority_class
bound_inputs
decided_at
decided_by
decision_id
decision_schema_version
policies
predicates
prior_authority
source_id
```

The v2 candidate parses to exactly:

```text
bound_inputs
decision_id
decision_sha256
policies
predicates
prior_authority
source_id
taxonomy_id
taxonomy_schema_version
```

All 36 v1 predicate rows, their sorted order, decision actors, choices,
attachments, tag sets, and rationales are copied byte-semantically. The v2
route does not widen a predicate. If an exact v1 predicate cannot be evaluated
from the canonical v2 selector fields, the runtime outcome for that action is
`UNMAPPED`; the predicate row itself is not guessed, rewritten, or matched by a
label.

### 6.3 CROSS_AUTHORITY selector contract

Possession v2 may consume only these field-v2 canonical outputs:

```text
action_event_taxonomy_id
action_subevent_taxonomy_id
action_team_source_id
action_tag_ids
```

Selector evaluation is:

```text
if action_event_taxonomy_id is absent:
    outcome = UNMAPPED
elif action_subevent_taxonomy_id is absent:
    outcome = UNMAPPED
elif either taxonomy value is not strict integer or is boolean:
    outcome = UNMAPPED
elif no exact (event_id, subevent_id) predicate exists:
    outcome = UNMAPPED
elif any required_tag_id is absent from action_tag_ids:
    outcome = UNMAPPED
elif any forbidden_tag_id is present in action_tag_ids:
    outcome = UNMAPPED
elif predicate.control_team_source == ACTION_TEAM
     and action_team_source_id is absent:
    outcome = UNMAPPED
else:
    outcome = exact accepted predicate decision
```

The selector cannot read raw `$.subEventId`, `$.eventId`, `$.subEventName`,
`$.eventName`, taxonomy labels, rejected-field values, or a coerced
representation. A string `"10"` remains string evidence and makes the action
possession-ineligible even where integer `10` would match. A boolean never
matches integer `0` or `1`.

`action_tag_ids` must be the field-v2 sorted unique strict-integer array. A
missing or mistyped tag array is `UNMAPPED`; no empty default is synthesized.
For the accepted 36 predicates both tag sets are empty, so an admitted tag array
passes those two set predicates without changing the v1 result. Where
`control_team_source=ACTION_TEAM`, the canonical action team is mandatory.
Where `control_team_source=NONE`, team presence does not alter the exact
predicate decision and cannot be used to invent control.

The explicit possession-v2 evaluation output is:

```text
possession_eligibility_state =
  ELIGIBLE_RESOLVED | INELIGIBLE_UNMAPPED
```

`ELIGIBLE_RESOLVED` means the exact accepted predicate participates in a
deterministically resolved same-period possession under the unchanged R20
sequence rules. All other cases are `INELIGIBLE_UNMAPPED`. This state is an
explicit accepted possession output, not a provider-native field and not a
name-derived guess.

## 7. Product-contract preimage

### 7.1 Identity and exact top-level schema

```text
path = configs/schema/wyscout-v5-product-contract-preimage-v1.json
preimage_id = w04-wyscout-product-contract-preimage-v1
preimage_schema_version = w04-product-contract-preimage-v1
```

The top-level JSON object has exactly these nine keys:

```text
authority_links
layer_order
manifest_receipt_templates
path_templates
policy
preimage_id
preimage_schema_version
primary_key_contracts
serializer_ownership
```

`authority_links` has exactly:

```json
{
  "r20_authority_id": "w04-wyscout-schema-design-R20",
  "r20_authority_sha256": "8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047",
  "r21_authority_id": "w04-wyscout-schema-design-R21",
  "r21_authority_sha256": "<accepted-R21-physical-sha256>"
}
```

The materializer replaces the angle-bracket notation with the accepted lowercase
R21 SHA-256 before canonicalization. Angle brackets are explanatory notation and
are forbidden in the materialized file. `layer_order` is exactly
`["BRONZE","SILVER","GOLD"]`.

### 7.2 Exact path-template rows

Every `path_templates` row has exactly `path_role` and `relative_template`.
Rows are in this exact order:

| order | `path_role` | `relative_template` |
|---:|---|---|
| 1 | `BRONZE_KNOWN_RECORD` | `data/working/wyscout/v5/bronze/build_id=<build_id>/records/record_kind=<known-kind>/source_sha256=<source_sha>/part-00000.parquet` |
| 2 | `BRONZE_REJECTED_RECORD` | `data/working/wyscout/v5/bronze/build_id=<build_id>/quarantine/rejected-record/record_kind=unknown/raw_kind_state=<closed-state-token>/raw_kind_sha256=<64-lowercase-hex>/source_sha256=<source_sha>/part-00000.parquet` |
| 3 | `BRONZE_REJECTED_FIELD` | `data/working/wyscout/v5/bronze/build_id=<build_id>/quarantine/rejected-field/record_kind=<known-kind>/source_sha256=<source_sha>/part-00000.parquet` |
| 4 | `SILVER_COMPETITION` | `data/working/wyscout/v5/silver/build_id=<build_id>/competition/source_partition=global/part-00000.parquet` |
| 5 | `SILVER_TEAM` | `data/working/wyscout/v5/silver/build_id=<build_id>/team/source_partition=global/part-00000.parquet` |
| 6 | `SILVER_PLAYER` | `data/working/wyscout/v5/silver/build_id=<build_id>/player/source_partition=global/part-00000.parquet` |
| 7 | `SILVER_MATCH` | `data/working/wyscout/v5/silver/build_id=<build_id>/match/source_partition=<country>/part-00000.parquet` |
| 8 | `SILVER_ACTION` | `data/working/wyscout/v5/silver/build_id=<build_id>/action/source_partition=<country>/part-00000.parquet` |
| 9 | `SILVER_LINEUP_STINT` | `data/working/wyscout/v5/silver/build_id=<build_id>/lineup-stint/source_partition=<country>/part-00000.parquet` |
| 10 | `SILVER_POSSESSION` | `data/working/wyscout/v5/silver/build_id=<build_id>/possession/source_partition=<country>/part-00000.parquet` |
| 11 | `SILVER_PLAYER_MATCH_FACT` | `data/working/wyscout/v5/silver/build_id=<build_id>/player-match-fact/source_partition=<country>/part-00000.parquet` |
| 12 | `GOLD_PLAYER_WINDOW` | `data/working/wyscout/v5/gold/build_id=<build_id>/player-window/competition_id=<uuid>/window_definition_id=<uuid>/window_start_utc=<utc>/window_end_utc=<utc>/feature_cutoff_ts=<utc>/part-00000.parquet` |
| 13 | `BRONZE_MANIFEST` | `data/manifests/wyscout/v5/bronze/<build_id>.manifest.json` |
| 14 | `SILVER_MANIFEST` | `data/manifests/wyscout/v5/silver/<build_id>.manifest.json` |
| 15 | `GOLD_MANIFEST` | `data/manifests/wyscout/v5/gold/<build_id>.manifest.json` |
| 16 | `REBUILD_INVOCATION_RECEIPT` | `runs/w04/wyscout-rebuild/<build_id>/<run_id>.receipt.json` |
| 17 | `TEMPORAL_BOUNDARY_RECEIPT` | `runs/w04/wyscout-rebuild/<build_id>/<run_id>/boundary/<sha256-of-exact-gold-relative-path>.temporal-boundary-receipt.json` |

These are descriptor strings, not created paths. The preimage materialization
must not create any listed destination.

### 7.3 Exact serializer ownership

Every `serializer_ownership` row has exactly `owner` and `path_roles`. Rows are
ordered by `owner`, and each `path_roles` array has the exact order below:

| `owner` | `path_roles` |
|---|---|
| `actions.py` | `["SILVER_ACTION"]` |
| `bronze.py` | `["BRONZE_KNOWN_RECORD","BRONZE_REJECTED_RECORD","BRONZE_REJECTED_FIELD","BRONZE_MANIFEST"]` |
| `entities.py` | `["SILVER_COMPETITION","SILVER_TEAM","SILVER_PLAYER","SILVER_MATCH"]` |
| `gold.py` | `["GOLD_PLAYER_WINDOW","GOLD_MANIFEST"]` |
| `lineups.py` | `["SILVER_LINEUP_STINT"]` |
| `player_match.py` | `["SILVER_PLAYER_MATCH_FACT"]` |
| `possessions.py` | `["SILVER_POSSESSION"]` |
| `rebuild.py` | `["REBUILD_INVOCATION_RECEIPT"]` |
| `silver_manifest.py` | `["SILVER_MANIFEST"]` |
| `temporal_boundary.py` | `["TEMPORAL_BOUNDARY_RECEIPT"]` |

Every path role occurs exactly once. This is the already approved R20 ownership
surface only; it does not claim any file exists or define serializer code.

### 7.4 Exact primary keys and manifest/receipt templates

Every `primary_key_contracts` row has exactly `key_fields` and `schema_role`.
There are exactly two rows:

```json
[
  {
    "key_fields": [
      "tenant_id",
      "source_manifest_id",
      "match_id",
      "player_id",
      "player_match_fact_schema_version"
    ],
    "schema_role": "SILVER_PLAYER_MATCH_FACT"
  },
  {
    "key_fields": [
      "tenant_id",
      "player_id",
      "competition_id",
      "season_id",
      "role_context_id",
      "role_context_version",
      "window_definition_id",
      "window_start_utc",
      "window_end_utc",
      "feature_cutoff_ts",
      "dependency_lineage_hash"
    ],
    "schema_role": "GOLD_PLAYER_WINDOW"
  }
]
```

R21 does not invent keys for other products. Every
`manifest_receipt_templates` row has exactly `artifact_role`, `owner`, and
`relative_template`. It contains path roles 13 through 17 from Section 7.2 in
that order, with the corresponding owner in Section 7.3 and identical template.

`policy` has exactly:

```json
{
  "control_plane_only": true,
  "no_product_before_gate": "R21_COMPLETE_GATE_PASS",
  "product_bytes_forbidden": true
}
```

This preimage closes a digestable contract surface; it is not a product schema,
an implemented serializer, or permission to create output bytes.

## 8. Schema-bundle preimage

### 8.1 Identity and exact top-level schema

```text
path = configs/schema/wyscout-v5-schema-bundle-preimage-v1.json
preimage_id = w04-wyscout-schema-bundle-preimage-v1
preimage_schema_version = w04-schema-bundle-preimage-v1
```

The top-level object has exactly:

```text
authority_links
dependency_order
descriptors
feature_schema_hash_placeholder
preimage_id
preimage_schema_version
```

`authority_links` is byte-equal to Section 7.1. Each `descriptors` row has
exactly:

```text
depends_on
descriptor_id
descriptor_version
role
surface_kind
```

`surface_kind` is always exactly
`CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`. This wording is a
machine-checked guard: a descriptor cannot be mistaken for an implemented row
schema. `depends_on` is an ordered array of earlier descriptor IDs.

### 8.2 Exact descriptor roster and order

`dependency_order` is exactly the ordered `descriptor_id` list below, and
`descriptors` is in the same order:

| order | `descriptor_id` | `descriptor_version` | `role` | `depends_on` |
|---:|---|---|---|---|
| 1 | `w04-source-record-envelope` | `w04-source-record-envelope-v1` | `SOURCE_RECORD_ENVELOPE` | `[]` |
| 2 | `w04-wyscout-bronze-known-record` | `w04-wyscout-bronze-known-record-descriptor-v1` | `BRONZE_KNOWN_RECORD` | `["w04-source-record-envelope"]` |
| 3 | `w04-wyscout-bronze-rejected-record` | `w04-raw-kind-v1` | `BRONZE_REJECTED_RECORD` | `["w04-source-record-envelope"]` |
| 4 | `w04-wyscout-bronze-rejected-field` | `w04-wyscout-bronze-rejected-field-descriptor-v1` | `BRONZE_REJECTED_FIELD` | `["w04-wyscout-bronze-known-record"]` |
| 5 | `w04-wyscout-silver-competition` | `w04-wyscout-silver-competition-descriptor-v1` | `SILVER_COMPETITION` | `["w04-wyscout-bronze-known-record"]` |
| 6 | `w04-wyscout-silver-team` | `w04-wyscout-silver-team-descriptor-v1` | `SILVER_TEAM` | `["w04-wyscout-bronze-known-record"]` |
| 7 | `w04-wyscout-silver-player` | `w04-wyscout-silver-player-descriptor-v1` | `SILVER_PLAYER` | `["w04-wyscout-bronze-known-record"]` |
| 8 | `w04-wyscout-silver-match` | `w04-wyscout-silver-match-descriptor-v1` | `SILVER_MATCH` | `["w04-wyscout-bronze-known-record","w04-wyscout-silver-competition","w04-wyscout-silver-team"]` |
| 9 | `w04-wyscout-silver-action` | `w04-wyscout-silver-action-descriptor-v1` | `SILVER_ACTION` | `["w04-wyscout-bronze-known-record","w04-wyscout-silver-match","w04-wyscout-silver-player","w04-wyscout-silver-team"]` |
| 10 | `w04-wyscout-silver-lineup-stint` | `w04-wyscout-silver-lineup-stint-descriptor-v1` | `SILVER_LINEUP_STINT` | `["w04-wyscout-silver-match","w04-wyscout-silver-player","w04-wyscout-silver-team"]` |
| 11 | `w04-wyscout-silver-possession` | `w04-wyscout-silver-possession-descriptor-v1` | `SILVER_POSSESSION` | `["w04-wyscout-silver-action"]` |
| 12 | `w04-wyscout-silver-player-match-fact` | `w04-wyscout-silver-player-match-fact-descriptor-v1` | `SILVER_PLAYER_MATCH_FACT` | `["w04-wyscout-silver-action","w04-wyscout-silver-lineup-stint","w04-wyscout-silver-match","w04-wyscout-silver-player","w04-wyscout-silver-possession"]` |
| 13 | `w04-wyscout-gold-player-window` | `w04-wyscout-gold-player-window-descriptor-v1` | `GOLD_PLAYER_WINDOW` | `["w04-wyscout-silver-player-match-fact"]` |
| 14 | `w04-wyscout-layer-manifest` | `w04-wyscout-layer-manifest-descriptor-v1` | `LAYER_MANIFEST` | `["w04-wyscout-bronze-known-record","w04-wyscout-bronze-rejected-record","w04-wyscout-bronze-rejected-field","w04-wyscout-silver-competition","w04-wyscout-silver-team","w04-wyscout-silver-player","w04-wyscout-silver-match","w04-wyscout-silver-action","w04-wyscout-silver-lineup-stint","w04-wyscout-silver-possession","w04-wyscout-silver-player-match-fact","w04-wyscout-gold-player-window"]` |
| 15 | `w04-wyscout-rebuild-invocation-receipt` | `w04-rebuild-invocation-v1` | `REBUILD_INVOCATION_RECEIPT` | `["w04-wyscout-layer-manifest"]` |
| 16 | `w04-wyscout-temporal-boundary-receipt` | `w04-wyscout-temporal-boundary-receipt-descriptor-v1` | `TEMPORAL_BOUNDARY_RECEIPT` | `["w04-wyscout-gold-player-window","w04-wyscout-layer-manifest"]` |

The `*-descriptor-v1` tokens version only the already approved R20 contract
surface description. They do not assert that row models, Parquet schemas, files,
serializers, manifests, or receipts exist. Their only permitted use is this
control preimage and later verification that an implementation, if separately
authorized, matches R20/R21.

### 8.3 Typed unresolved feature hash

`feature_schema_hash_placeholder` has exactly:

```json
{
  "concrete_value": null,
  "json_type": "string",
  "pattern": "^[0-9a-f]{64}$",
  "resolution_source": "accepted:w04-wyscout-supported-count-features-v1:candidate_sha256",
  "state": "TYPED_UNRESOLVED_UNTIL_SUPPORTED_FEATURE_ACCEPTANCE"
}
```

A lowercase 64-hex feature digest is required in later Gold evidence, but a
concrete value cannot exist until the feature candidate is independently
reviewed and accepted. Inserting a feature digest in this preimage, hashing a
feature authority into it, or treating null as an actual schema hash fails.

## 9. Exact conservative POC feature authority

### 9.1 Existing fixed route

The following R20 route IDs and paths remain unchanged because no feature
authority has yet been accepted:

| role | fixed ID | exact path |
|---|---|---|
| decision | `w04-wyscout-supported-feature-registry-decisions-v1` | `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json` |
| candidate | `w04-wyscout-supported-count-features-v1` | `configs/features/wyscout-v5-supported-count-features-v1.yaml` |
| independent review | `w04-wyscout-supported-feature-registry-independent-review-R1` | `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md` |
| acceptance | `w04-wyscout-supported-feature-registry-acceptance-v1` | `reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json` |

The decision/candidate schemas and policies remain as closed in R20 except that
R21 fixes the exact roster and bound inputs below.

### 9.2 Exact bound inputs

`bound_inputs` has exactly these ten keys:

```text
field_acceptance_sha256
field_registry_canonical_sha256
field_registry_id
possession_acceptance_sha256
possession_taxonomy_canonical_sha256
possession_taxonomy_id
product_contract_preimage_id
product_contract_preimage_sha256
schema_bundle_preimage_id
schema_bundle_preimage_sha256
```

The IDs are exactly:

```text
field_registry_id = w04-wyscout-field-registry-v2
possession_taxonomy_id = w04-wyscout-possession-taxonomy-v2
product_contract_preimage_id = w04-wyscout-product-contract-preimage-v1
schema_bundle_preimage_id = w04-wyscout-schema-bundle-preimage-v1
```

The four authority digests are the accepted field v2 candidate canonical and
acceptance digests and the accepted possession v2 candidate canonical and
acceptance digests. The two preimage digests are their canonical file digests.
No v1 field/possession digest, physical candidate digest in place of canonical
digest, bare product/schema digest, or unaccepted candidate is allowed.

### 9.3 Exact eight-field feature rows

Every feature row contains exactly these eight fields:

```text
aggregation
applicability
denominator
feature_name
input_fields
output_type
reason
state
```

The exact roster is sorted by `feature_name`, has cardinality fifteen, and is:

| feature_name | state | input_fields | aggregation | applicability | denominator | output_type | reason |
|---|---|---|---|---|---|---|---|
| `action_count` | `SUPPORTED` | `["action_source_id"]` | `COUNT` | `ACTION_PRESENT` | `NONE` | `int64` | `SUPPORTED_EXACT_SOURCE_ACTION_ID_COUNT` |
| `action_rate` | `SUPPRESSED_UNSUPPORTED_DENOMINATOR` | `[]` | `NONE` | `NEVER` | `UNSUPPORTED_MINUTES` | `null` | `POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR` |
| `actions_per_90` | `SUPPRESSED_UNSUPPORTED_DENOMINATOR` | `[]` | `NONE` | `NEVER` | `UNSUPPORTED_MINUTES` | `null` | `POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR` |
| `continuous_time_seconds` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `POC_SOURCE_SUPPORTS_PERIOD_RELATIVE_TIME_ONLY` |
| `coordinate_known_action_count` | `SUPPORTED` | `["action_positions"]` | `COUNT` | `POSITION_PRESENT` | `NONE` | `int64` | `SUPPORTED_ACCEPTED_POSITION_EVIDENCE_COUNT` |
| `match_count` | `SUPPORTED` | `["match_source_id"]` | `DISTINCT_COUNT` | `ALWAYS` | `NONE` | `int64` | `SUPPORTED_DISTINCT_ACCEPTED_MATCH_ID_COUNT` |
| `minutes_lower` | `SUPPRESSED_UNSUPPORTED_DENOMINATOR` | `[]` | `NONE` | `NEVER` | `UNSUPPORTED_MINUTES` | `null` | `POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR` |
| `minutes_upper` | `SUPPRESSED_UNSUPPORTED_DENOMINATOR` | `[]` | `NONE` | `NEVER` | `UNSUPPORTED_MINUTES` | `null` | `POC_SOURCE_HAS_NO_ACCEPTED_ELAPSED_MINUTES_DENOMINATOR` |
| `outcome_dependent_count` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `OUTCOMES_EXCLUDED_FROM_W04_RESULT_INDEPENDENT_POC` |
| `provider_native_possession_count` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `PROVIDER_NATIVE_POSSESSION_NOT_PRESENT_OR_AUTHORIZED` |
| `resolved_lineup_stint_count` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `LINEUP_STINT_COUNT_NOT_ACCEPTED_IN_CONSERVATIVE_POC_ROSTER` |
| `resolved_possession_action_count` | `SUPPORTED` | `["action_event_taxonomy_id","action_subevent_taxonomy_id","action_team_source_id"]` | `COUNT` | `POSSESSION_ELIGIBLE` | `NONE` | `int64` | `SUPPORTED_ACCEPTED_POSSESSION_ELIGIBLE_ACTION_COUNT` |
| `role_inferred_count` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `ROLE_INFERENCE_OUTSIDE_W04_AUTHORITY` |
| `unresolved_action_count` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `UNRESOLVED_ACTION_EVIDENCE_REMAINS_QUARANTINED_NOT_FEATURED` |
| `value_model_sum` | `UNAVAILABLE` | `[]` | `NONE` | `NEVER` | `NONE` | `null` | `NO_ACCEPTED_ACTION_VALUE_MODEL_IN_W04` |

No sixteenth row is permitted. Absence does not grant permission. The supported
features use only field-v2 outputs. `POSSESSION_ELIGIBLE` additionally requires
the accepted possession-v2 `possession_eligibility_state` to equal
`ELIGIBLE_RESOLVED`; applicability is not a hidden fourth input field. A row
with a missing canonical subevent cannot satisfy it.

The exact policy object remains:

```text
absence_grants_permission = false
continuous_time_features = UNAVAILABLE
minutes_features = SUPPRESSED_UNSUPPORTED_DENOMINATOR
outcome_dependent_features = UNAVAILABLE
per90_features = SUPPRESSED_UNSUPPORTED_DENOMINATOR
provider_native_possession_features = UNAVAILABLE
rate_features = SUPPRESSED_UNSUPPORTED_DENOMINATOR
role_inferred_features = UNAVAILABLE
unsupported_feature_policy = UNAVAILABLE
value_model_features = UNAVAILABLE
```

The candidate canonical digest becomes `feature_schema_hash` only after its
independent review and acceptance pass. Before then it is unavailable.

## 10. Exact evidence-preserving 30-resource roster

The cardinality is mechanically derived:

```text
17 immutable R20 resources
+ 1 R21 design
+ 1 R21 independent review
+ 2 control preimages
+ 4 field v2 route artifacts
+ 4 possession v2 route artifacts
+ 1 cross-authority contract test
= 30 exact resources
```

The supported-feature v1 candidate and three authority artifacts are already
members 4 and 14–16 of the immutable 17. Their R21 status changes from planned
ambiguity to an exact future route, but they add zero new paths. This prevents
double counting and proves both retention and exact cardinality.

The deterministic roster order is exactly:

1. `configs/schema/wyscout-v5-identity-ruleset-v1.yaml`
2. `configs/schema/wyscout-v5-field-registry-v1.yaml`
3. `configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml`
4. `configs/features/wyscout-v5-supported-count-features-v1.yaml`
5. `reports/reviews/W04/authorities/wyscout-identity-ruleset-decisions-v1.json`
6. `reports/reviews/W04/authorities/wyscout-identity-ruleset-independent-review-R1.md`
7. `reports/reviews/W04/authorities/wyscout-identity-ruleset-acceptance-v1.json`
8. `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`
9. `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
10. `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json`
11. `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json`
12. `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`
13. `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json`
14. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`
15. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
16. `reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json`
17. `reports/phase-gates/W04/source-schema-profile.md`
18. `reports/reviews/W04/wyscout-schema-design-R21.md`
19. `reports/reviews/W04/wyscout-schema-design-independent-review-R15.md`
20. `configs/schema/wyscout-v5-product-contract-preimage-v1.json`
21. `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`
22. `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json`
23. `configs/schema/wyscout-v5-field-registry-v2.yaml`
24. `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md`
25. `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json`
26. `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json`
27. `configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml`
28. `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
29. `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json`
30. `tests/contracts/test_w04_r21_cross_authority_composability.py`

Each resource row in later admission retains R20's exact `path`, physical
SHA-256, size, mode, purpose, parser/schema version, and authority link. No
directory shorthand, glob, optional 31st path, substitution of v1 by v2, or
omission is allowed. Resource digest is the stable digest of all thirty exact
rows in this order. Product outputs, generated manifests/receipts, runtime
evidence, and returns are not local resources.

## 11. Exact five temporal dependencies after R21

The R20 `EvidenceDependency` wire schema, UUIDv5 construction, sort, cardinality
five, lineage hash, strict-before inequalities, and watermark remain unchanged.
Only authority bindings are corrected:

| order by existing sort | evidence | kind | digest/clock authority |
|---|---|---|---|
| derived | strict source manifest | `source_manifest` | unchanged accepted source manifest |
| derived | accepted identity bundle | `identity_evidence` | unchanged identity v1 route, whose future decision must bind field v2 rather than create a second field authority |
| derived | accepted field registry | `feature_schema` | field v2 candidate canonical digest; field v2 decision/acceptance clocks |
| derived | accepted possession taxonomy | `feature_schema` | possession v2 candidate canonical digest; possession v2 decision/acceptance clocks |
| derived | accepted supported-feature registry | `feature_schema` | supported-feature v1 candidate canonical digest; supported-feature decision/acceptance clocks |

The displayed table is explanatory; actual order remains R20's exact sort by
`(DependencyKind enum rank, dependency_id.bytes, digest, observed_at,
available_at)`. Feature dependency UUIDv5 values use their exact corrected
candidate ID, canonical digest, and acceptance digest. Mixing a field v1
dependency with possession v2, possession v1 with feature bound to v2, or any
other v1/v2 hybrid fails.

Identity remains route v1 because no accepted identity authority is superseded
here. Its future decision packet must consume the accepted field v2 route under
R21's dependency clause. This is not mutation of an accepted identity artifact
and creates no new identity semantics.

## 12. Serial packets, ownership, and review separation

All packets below are serial. A packet may start only after the preceding
acceptance/review listed in its dependency column is complete. Candidate
producers cannot review or accept their own work. Subagents perform no Git
operation and cannot delegate.

The cross-authority independent review has fixed ID
`w04-wyscout-r21-cross-authority-composability-independent-review-R1` and fixed
path
`reports/reviews/W04/wyscout-r21-cross-authority-composability-independent-review-R1.md`.
It must bind the complete physical SHA-256 of both the returned cross-authority
test file and its packet return. Its reviewer is distinct from all authority and
test producers. The later master gate must bind the complete physical SHA-256 of
that fixed review and require its recommendation to be `PASS`.

| order | packet | sole write ownership | requires independent actor |
|---:|---|---|---|
| 1 | `W04-SCHEMA-DESIGN-01-R21` | this R21 report and its return | master reviews |
| 2 | `W04-SCHEMA-DESIGN-REVIEW-01-R15` | fresh R15 review and return | reviewer distinct from producer |
| 3 | `W04-CONTROL-PREIMAGE-01-R1` | the two preimage JSON files, one contract test, return | independent reviewer next |
| 4 | `W04-CONTROL-PREIMAGE-REVIEW-01-R1` | preimage review and return | reviewer distinct from materializer |
| 5 | `W04-FIELD-SEMANTIC-V2-DECISION-01-R1` | field v2 decision/candidate, focused tests, return | independent reviewer next |
| 6 | `W04-FIELD-SEMANTIC-V2-REVIEW-01-R1` | field v2 independent review and return | reviewer distinct from producer |
| 7 | `W04-FIELD-SEMANTIC-V2-ACCEPT-01-R1` | field v2 acceptance, master verification/return | master only |
| 8 | `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R1` | possession v2 decision/candidate, focused tests, return | independent reviewer next |
| 9 | `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1` | possession v2 independent review and return | reviewer distinct from producer |
| 10 | `W04-POSSESSION-SEMANTIC-V2-ACCEPT-01-R1` | possession v2 acceptance, master verification/return | master only |
| 11 | `W04-FEATURE-REGISTRY-DECISION-01-R1` | existing feature decision/candidate, focused tests, return | independent reviewer next |
| 12 | `W04-FEATURE-REGISTRY-REVIEW-01-R1` | feature independent review and return | reviewer distinct from producer |
| 13 | `W04-FEATURE-REGISTRY-ACCEPT-01-R1` | feature acceptance, master verification/return | master only |
| 14 | `W04-R21-CROSS-AUTHORITY-TEST-01-R1` | cross-authority composability test and return | after feature acceptance; implementation evidence only |
| 15 | `W04-R21-CROSS-AUTHORITY-REVIEW-01-R1` | fixed independent review and return | reviewer distinct from every authority/test producer |
| 16 | `W04-R21-CROSS-AUTHORITY-GATE-01-R1` | master verification, machine gate evidence, return | master only; after passing independent review |

The sole-write cells expand to the following exhaustive paths; there is no
packet-author choice:

1. `W04-SCHEMA-DESIGN-01-R21`:
   `reports/reviews/W04/wyscout-schema-design-R21.md` and
   `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21.md`.
2. `W04-SCHEMA-DESIGN-REVIEW-01-R15`:
   `reports/reviews/W04/wyscout-schema-design-independent-review-R15.md` and
   `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R15.md`.
3. `W04-CONTROL-PREIMAGE-01-R1`:
   `configs/schema/wyscout-v5-product-contract-preimage-v1.json`,
   `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`,
   `tests/contracts/test_w04_r21_control_preimages.py`, and
   `reports/reviews/W04/returns/W04-CONTROL-PREIMAGE-01-R1.md`.
4. `W04-CONTROL-PREIMAGE-REVIEW-01-R1`:
   `reports/reviews/W04/wyscout-r21-control-preimage-independent-review-R1.md`
   and
   `reports/reviews/W04/returns/W04-CONTROL-PREIMAGE-REVIEW-01-R1.md`.
5. `W04-FIELD-SEMANTIC-V2-DECISION-01-R1`:
   `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v2.json`,
   `configs/schema/wyscout-v5-field-registry-v2.yaml`,
   `tests/contracts/test_w04_field_semantic_v2_authority.py`, and
   `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-V2-DECISION-01-R1.md`.
6. `W04-FIELD-SEMANTIC-V2-REVIEW-01-R1`:
   `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-v2-R1.md`
   and
   `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-V2-REVIEW-01-R1.md`.
7. `W04-FIELD-SEMANTIC-V2-ACCEPT-01-R1`:
   `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v2.json`,
   `reports/verification/W04/wyscout-field-semantic-v2-acceptance-R1-master-verification.md`,
   and
   `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-V2-ACCEPT-01-R1.md`.
8. `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R1`:
   `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v2.json`,
   `configs/taxonomies/wyscout-v5-possession-taxonomy-v2.yaml`,
   `tests/contracts/test_w04_possession_semantic_v2_authority.py`, and
   `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-DECISION-01-R1.md`.
9. `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1`:
   `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-v2-R1.md`
   and
   `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1.md`.
10. `W04-POSSESSION-SEMANTIC-V2-ACCEPT-01-R1`:
    `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v2.json`,
    `reports/verification/W04/wyscout-possession-semantic-v2-acceptance-R1-master-verification.md`,
    and
    `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-V2-ACCEPT-01-R1.md`.
11. `W04-FEATURE-REGISTRY-DECISION-01-R1`:
    `reports/reviews/W04/authorities/wyscout-supported-feature-registry-decisions-v1.json`,
    `configs/features/wyscout-v5-supported-count-features-v1.yaml`,
    `tests/contracts/test_w04_supported_feature_authority.py`, and
    `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-DECISION-01-R1.md`.
12. `W04-FEATURE-REGISTRY-REVIEW-01-R1`:
    `reports/reviews/W04/authorities/wyscout-supported-feature-registry-independent-review-R1.md`
    and
    `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-REVIEW-01-R1.md`.
13. `W04-FEATURE-REGISTRY-ACCEPT-01-R1`:
    `reports/reviews/W04/authorities/wyscout-supported-feature-registry-acceptance-v1.json`,
    `reports/verification/W04/wyscout-supported-feature-registry-acceptance-R1-master-verification.md`,
    and
    `reports/reviews/W04/returns/W04-FEATURE-REGISTRY-ACCEPT-01-R1.md`.
14. `W04-R21-CROSS-AUTHORITY-TEST-01-R1`:
    `tests/contracts/test_w04_r21_cross_authority_composability.py`,
    and
    `reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-TEST-01-R1.md`.
15. `W04-R21-CROSS-AUTHORITY-REVIEW-01-R1`:
    `reports/reviews/W04/wyscout-r21-cross-authority-composability-independent-review-R1.md`
    and
    `reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-REVIEW-01-R1.md`.
16. `W04-R21-CROSS-AUTHORITY-GATE-01-R1`:
    `reports/verification/W04/wyscout-r21-cross-authority-gate-R1-master-verification.md`,
    `reports/phase-gates/W04/wyscout-r21-correction-gate.json`, and
    `reports/reviews/W04/returns/W04-R21-CROSS-AUTHORITY-GATE-01-R1.md`.

Packet YAML creation and orchestration-state changes remain master-only and
outside these producer scopes. Shared contracts, config candidates, acceptance
files, orchestration state, and the cross-authority test are never parallel
write scopes. The cross-authority test packet starts only after feature
acceptance; the independent cross-authority review starts only after the test
packet returns; and the master gate starts only after that fixed review returns
`PASS`. The fixed independent-review artifact is control evidence, not a runtime
local resource, and therefore does not change the exact 30-resource roster. No
checkpoint commit or tag is required between packets. Only the master may
checkpoint after the complete R21 gate.

## 13. CROSS_AUTHORITY composability tests

The final exact test path is:

```text
tests/contracts/test_w04_r21_cross_authority_composability.py
```

It supplements, not replaces, the field, possession, feature, preimage, and
R20 suites.

### 13.1 Positive cases

Tests must prove:

1. accepted strict integer event/subevent pairs emit
   `action_subevent_taxonomy_id`;
2. all 36 copied possession predicates are byte-semantically equal to v1;
3. a canonical field-v2 action with accepted integer pair/team/tags can produce
   the exact possession-v2 result;
4. missing canonical subevent produces `INELIGIBLE_UNMAPPED`;
5. a resolved accepted possession action makes only
   `resolved_possession_action_count` applicable;
6. the feature candidate has exactly the 15 ordered rows and four supported
   rows;
7. the two preimages canonicalize reproducibly with one terminal LF;
8. the preimage graph has the exact Section 4 branch and convergence edges,
   has no edge between the sibling preimages, and remains valid with either
   sibling presented first in a topological ordering;
9. all 17 v1 resources appear at positions 1–17 and all 30 paths are unique;
10. each v2 acceptance names its exact v1 acceptance;
11. accepted v2 candidate and acceptance digests flow unchanged into the
    feature authority and five dependencies;
12. the independent cross-authority review binds the complete physical
    SHA-256 of the returned cross-authority test artifact, uses the fixed review
    ID/path, and has a reviewer distinct from the test and authority producers;
13. the master gate binds that fixed review's complete physical SHA-256 and
    requires its recommendation to be `PASS`;
14. no product path exists while the R21 gate state is not complete.

### 13.2 Required negative cases

Tests reject:

- `"10"`, `" 10"`, `"+10"`, `"010"`, `true`, `false`, null, `10.0`,
  arrays, and objects as action subevent integers;
- language-level bool-as-int behavior;
- any loss or change of the 7,821 string evidence count or its exact reason;
- unknown integers producing a canonical subevent;
- selector reads from raw subevent/event fields or any name/label;
- runtime taxonomy label lookup;
- possession matching with missing canonical subevent;
- field v1 candidate/acceptance combined with possession v2;
- possession v1 candidate/acceptance combined with feature v1 under R21;
- wrong prior-authority key, value, digest, cardinality, or supersession ID;
- a prior-authority key order in which `review_record_sha256` precedes
  `review_recommendation`;
- mutation of any v1 file;
- decision/candidate/review/acceptance physical or canonical digest drift;
- a preimage containing its own digest, the sibling preimage digest, a feature
  digest, build/run ID, clock, root, host, product byte, output path
  observation, or mutable runtime observation;
- a preimage self-edge, reverse edge, feature-to-preimage edge, or any cycle;
- a concrete `feature_schema_hash` in the schema preimage;
- descriptor surface kind other than
  `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`;
- any descriptor being treated as proof that a row schema or serializer exists;
- a sixteenth feature, missing feature, duplicate feature, wrong sort, unknown
  row field, or omitted row field;
- any supported feature other than the four exact supported rows;
- a supported row using an unaccepted, name-only, guessed, possession-internal,
  or unlisted input;
- a suppressed/unavailable row with nonempty inputs or a non-null output;
- feature candidate/review/use before field v2 and possession v2 acceptance;
- feature hash use before feature acceptance;
- product-contract digest substituted for schema-bundle digest or vice versa;
- physical candidate digest substituted where canonical digest is required;
- resource cardinality other than 30, any changed position 1–17, duplicate,
  directory shorthand, or product output in resources;
- missing, mutated, wrong-path, wrong-ID, non-`PASS`, or self-authored
  independent cross-authority review evidence;
- a combined test/review/gate write scope or any gate run before the independent
  review has passed;
- any Bronze, Silver, Gold, manifest, receipt, serializer, data-product, build,
  or product path created before the complete R21 gate passes.

## 14. Complete final R21 gate

Focused checks are necessary but never sufficient. The master must independently
run the complete `AGENTS.md` repository suite in exactly this order and retain
exact output:

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

Every command must pass, `git status --short` must be empty at the final
checkpoint, and `git remote` must print nothing. The final gate then adds all of
the following R21-specific checks:

1. R21 physical digest and immutable R20 binding;
2. passing fresh independent R15 design review;
3. both canonical preimage materializations and independent review;
4. preimage no-self-hash/no-cycle/no-feature-hash tests;
5. field v2 decision/candidate/review/acceptance and master verification;
6. exact strict-integer/no-coercion/rejected-evidence tests;
7. possession v2 decision/candidate/review/acceptance and master verification;
8. exact 36-predicate and canonical-selector tests;
9. exact 15-feature decision/candidate/review/acceptance and master
    verification;
10. v1 immutability and v2 supersession tests;
11. exact five-dependency and v1/v2 anti-mixing tests;
12. exact 30-resource order/cardinality/digest tests;
13. the returned cross-authority test, fixed independent review, and master
    gate in their exact three-packet serial order;
14. the complete CROSS_AUTHORITY positive and negative suite;
15. forbidden product-path scan proving no Bronze, Silver, Gold, generated
    manifest/receipt, build, or product implementation exists;
16. bytecode inventory equality under the repository's pyc policy;
17. master readback of every changed file and every retained evidence artifact;
18. a final machine-readable gate report whose decision is `PASS`.

Any failure is `REWORK` or `BLOCK`, never partial acceptance. No product
implementation resumes after a focused pass. Only the complete final gate can
close this correction.

## 15. No-product and local-only terminal boundary

R21 authorization ends after the complete correction gate. Until a later
master packet is separately authorized:

```text
Bronze implementation = FORBIDDEN
Silver implementation = FORBIDDEN
Gold implementation = FORBIDDEN
feature materialization = FORBIDDEN
product serializer implementation = FORBIDDEN
manifest/receipt generation = FORBIDDEN
runtime/build invocation = FORBIDDEN
model/product implementation = FORBIDDEN
network/provider acquisition = FORBIDDEN
cloud/container/endpoint/hosted CI/deployment = FORBIDDEN
Git remote = FORBIDDEN
```

The two preimages are inert canonical control contracts. Their path strings,
descriptor IDs, serializer-owner tokens, primary keys, and placeholder do not
create data or executable behavior. The four supported feature rows are an
authority roster, not a computation. The v2 routes supersede future semantic
use, not historical evidence.

R21 is therefore bounded, acyclic, evidence-preserving, conservative, and
implementable without a broader architecture or product change.
