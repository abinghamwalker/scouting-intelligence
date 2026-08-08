# W04 Wyscout schema design independent review R15

## Review identity and recommendation

- review ID: `w04-wyscout-schema-design-independent-review-R15`
- task ID: `W04-SCHEMA-DESIGN-REVIEW-01-R15`
- candidate: `reports/reviews/W04/wyscout-schema-design-R21.md`
- candidate physical SHA-256:
  `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
- immutable base: `reports/reviews/W04/wyscout-schema-design-R20.md`
- immutable-base physical SHA-256:
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- reviewer role: independent design reviewer, distinct from the R21 producer
- recommendation: `PASS`
- finding cardinality: `P0=0`, `P1=0`, `P2=0`

The exact final R21 bytes merit `PASS`. I found no P0, P1, or P2 defect in the
bounded design when it is merged with immutable R20 using R21's exact six-family
replacement rule. The correction is complete enough to authorize only the next
master readback and, if the master independently accepts this review, the later
serial control-plane packets specified by R21. This recommendation does not
self-accept R21, materialize either control preimage, produce a v2 authority,
create a feature candidate, create data-product bytes, or authorize product
implementation.

## Scope and review method

I reviewed all 4,516 lines and 245,957 bytes of immutable R20 and all 1,254
lines and 59,565 bytes of final R21. I also read every authority and control
artifact named by the R15 packet: the final R21 R3 producer return and packet,
its master review and verification, failed R14 and its return/master
review/master verification, the immutable R21 R2 return, both accepted v1
semantic routes and their decision/review/acceptance evidence, the source
schema profile, completion manifest, return template, and both controlling
planning HTML documents.

The review was performed as a design-merits challenge rather than a
producer-summary check. I independently reconstructed:

- the physical SHA-256 of R20, R21, the accepted v1 authority artifacts, and
  the preserved R14 evidence;
- canonical JSON bytes with sorted keys, compact separators, UTF-8, and exactly
  one terminal LF for the two accepted YAML candidates and their review
  records;
- the 17-key field and possession `prior_authority` records from the immutable
  15-key acceptance files plus their acceptance physical/canonical digests;
- the proposed 119-row field-v2 roster by replacing exactly one v1 row;
- the 36-row possession predicate set and its pair, order, tag-set, and team
  source invariants;
- every count-bearing R21 table and ordered roster: 17 product paths, 10
  serializer owners, 16 schema descriptors, 15 feature rows, 30 resources,
  five temporal dependencies, 16 serial packets, 12 repository gate commands,
  and 18 additive gate checks;
- the preserved immutable R20 17-resource prefix and R15's unique active
  position in the expanded roster;
- the sibling-preimage graph and its convergence on field v2;
- the strict-integer/no-coercion behavior and typed quarantine outcome for each
  rejected JSON type.

The packet-mandated bytecode baseline was captured before any design read or
Python helper. It covers all repository bytecode, including installed
site-packages, with path, size, mode, link target, mtime, first sixteen bytes,
and full SHA-256 for each `.pyc`. It contains 1,145 `.pyc` rows and 150
`__pycache__` directories. Its inventory digest is
`5eb20aec62648a0afb344574f8f37a171d69796aa267826abe3d4a2cbd04bed8`.
All Python reconstruction helpers used the packet's locked, no-sync,
no-bytecode command form and asserted both environment and interpreter
bytecode controls before importing file-backed modules.

## Severity findings

### P0

None.

### P1

None.

### P2

None.

There are no omitted lower-severity observations that alter the recommendation.
Future materializers and implementers still have substantial proof obligations,
but those are explicitly retained as later gate requirements rather than
defects in this bounded design.

## 1. Merge rule and bounded change surface

R21 defines a deterministic merge rather than asking a later actor to infer
which R20 clauses survive. The complete R20 bytes remain the base, and only
these six named families are replaced:

1. `FIELD_AUTHORITY_ROUTE`;
2. `POSSESSION_AUTHORITY_ROUTE`;
3. `SUPPORTED_FEATURE_AUTHORITY_ROUTE`;
4. `LOCAL_RESOURCE_ROSTER`;
5. `TEMPORAL_DEPENDENCY_BINDINGS`;
6. `W04_FINAL_GATE`.

Everything outside those families remains R20 authority. That is important
because R20 contains extensive contracts for identity, source admission,
runtime boundaries, product layer semantics, temporal eligibility, rebuild
receipts, and local-only operation. R21 neither restates those thousands of
lines incompletely nor opens them to producer interpretation. Its rule also
states that a contradiction outside the named families is a stop condition,
which prevents a later packet from silently treating R21 as a full
replacement design.

The R21 changes are cohesive. Field v2 closes the previously unmapped action
subevent semantic; possession v2 consumes that new canonical output; the
feature route binds both accepted v2 semantic routes; the two preimages close
digestable control surfaces needed by the corrected authorities; the resource
and dependency rosters retain the corresponding evidence; and the final gate
proves the complete chain before product work can resume. I found no
architecture expansion hidden inside this sequence.

R21 also preserves the distinction between a control-plane description and an
implemented product. Path templates remain strings, descriptor rows remain
descriptors, feature rows remain authority declarations, and later output
paths remain forbidden. No database, serializer, product schema, materialized
feature, provider acquisition, runtime invocation, or deployment is authorized
by the correction.

## 2. Physical bytes, canonical bytes, clocks, and actors

The final candidate hash independently reproduces as
`faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`.
The immutable R20 base independently reproduces as
`8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`.
These are complete physical-file hashes, not hashes of selected sections or
normalized Markdown.

R21 correctly keeps physical and canonical digest roles separate:

- immutable Markdown and review evidence use complete physical bytes;
- structured JSON/YAML candidates use canonical JSON bytes for semantic
  identity;
- where an authority acceptance binds both, the physical and canonical fields
  are named separately;
- a physical candidate digest cannot be substituted where a canonical
  candidate digest is required;
- the materialized preimages use canonical JSON with exactly one terminal LF.

The existing field v1 candidate independently reconstructs as:

- physical SHA-256:
  `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2`;
- canonical SHA-256:
  `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`.

The existing possession v1 candidate independently reconstructs as:

- physical SHA-256:
  `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`;
- canonical SHA-256:
  `6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa`.

The field review physical digest is
`e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861`,
and its fenced canonical review-record digest is
`8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0`.
The possession review physical digest is
`1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4`,
and its fenced canonical review-record digest is
`40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962`.
Both fenced records parse as closed 12-key review records and recommend
`PASS`.

R21 does not invent clocks or actors for the already accepted v1 records. It
copies the accepted values exactly, keeps future decision/review/acceptance
actors distinct, and leaves the strict-before temporal rules to immutable R20.
The future five-dependency set therefore cannot become eligible merely because
its digests are correct; every bound decision, review, acceptance, and
correction clock must also be strictly before the feature cutoff.

## 3. Immutable prior-authority records

The two embedded `prior_authority` objects each have exactly 17
lexicographically ordered keys. In particular,
`review_recommendation` precedes `review_record_sha256`, closing the ordering
defect that an implementation might otherwise conceal through a generic map
serializer.

I reconstructed each object from the corresponding immutable v1 acceptance
file. The result is an exact copy of all 15 acceptance keys plus:

- `acceptance_physical_sha256`; and
- `acceptance_sha256`.

For the field route, both added values equal
`fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365`.
For the possession route, both equal
`f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112`.
In each case the immutable acceptance file is already canonical JSON with one
terminal LF, so equality of its physical and canonical hashes is expected and
was independently verified.

The v2 decision is required to embed the complete prior object. A v2 candidate
may repeat it only byte-semantically, and the v2 acceptance does not add an
unknown key to the closed 15-key acceptance schema. Instead, each v2 acceptance
binds the v2 decision/candidate/review digests and sets the exact v1
`supersedes_acceptance_id`. This is a sound evidence-preserving design: it
avoids mutating v1, avoids weakening the accepted acceptance schema, and still
makes the supersession chain complete.

The objects reject wrong key order, missing values, nulls where a value is
fixed, additional keys, wrong physical/canonical digest roles, and a wrong
supersession identifier. I found no ambiguous pointer or mutable
"current-authority" lookup.

## 4. Acyclic authority graph

The corrected authority graph is acyclic and implementable:

1. immutable R20 bytes precede immutable R21 bytes;
2. R21 is the common parent of the product-contract and schema-bundle
   preimages;
3. the two preimages are siblings and neither contains or depends on the
   other's digest;
4. both preimages converge as required inputs to field v2;
5. accepted field v2 precedes possession v2;
6. accepted field v2, accepted possession v2, and both preimages precede the
   supported-feature route;
7. accepted supported-feature evidence precedes the later five-dependency set;
8. only the complete accepted dependency set can precede later build identity
   and product implementation.

The sibling property matters. A design that hashed the product preimage into
the schema preimage, or vice versa, would create an unnecessary ordering
choice and could become a cycle when the downstream route binds both. R21
expressly forbids sibling digests, self-digests, future authority digests,
feature digests, clocks, roots, hosts, mutable runtime observations, build/run
IDs, output bytes, and generated manifest/receipt bytes in either preimage.
The two sibling nodes can therefore be presented in either topological order
without changing semantics.

The schema preimage retains a typed unresolved feature hash rather than
claiming a concrete value before feature acceptance. The feature route consumes
both accepted v2 routes and both preimages, so resolving a feature hash inside
an ancestor would reverse the dependency. R21 explicitly rejects that reversal
and requires the concrete feature digest only in later Gold evidence after
independent feature review and acceptance.

I found no self-edge, reverse edge, sibling edge, feature-to-preimage edge, or
implicit runtime edge. The graph closes design authority without claiming
materialized descendants.

## 5. Field semantic authority v2

The proposed field-v2 route has fixed decision, candidate, independent-review,
and acceptance IDs and paths. It uses new v2 decision and registry schema
versions while retaining the closed v1 acceptance schema. Its acceptance
supersedes exactly `w04-wyscout-field-semantic-acceptance-v1`.

The decision `bound_inputs` object has exactly ten named keys. It retains the
four immutable source digests:

- completion manifest:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- event taxonomy:
  `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`;
- source schema profile:
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- tag taxonomy:
  `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`.

I independently reproduced each of those physical digests. The remaining
bindings name immutable R20, the exact final R21 physical digest, and the IDs
and accepted canonical digests of both control preimages. Bare or ambiguous
`product_contract_digest` and `schema_bundle_digest` keys are forbidden.

The v1 field candidate contains exactly 119 rows, each with the same eight
keys. R21 retains their source-profile sequence rather than imposing a lexical
sort. Independent reconstruction of the proposed v2 roster changed only
one-based position 107:
`(record_kind="action", json_path="$.subEventId")`. The other 118 rows remain
byte-semantic copies of v1.

The changed row preserves the measured source shape exactly:

- JSON integer: 3,063,574 values;
- JSON string: 7,821 values.

Those counts agree with the immutable source schema profile. The row emits
`action_subevent_taxonomy_id` only when the raw subevent has measured JSON type
integer, is not boolean, and forms an exact admitted pair with the already
derived canonical integer event ID in the frozen event taxonomy.

The transformation is conservative:

- it does not parse or trim strings;
- it does not treat Python `bool` as an integer;
- it does not admit decimals, exponent numbers, arrays, objects, or null;
- it does not guess unknown integer pairs;
- it does not consult event/subevent names or labels at runtime;
- it emits the accepted raw integer unchanged rather than remapping it through
  label text;
- it retains every non-emitting raw value in the existing rejected-field
  evidence shape.

R21 closes seven typed rejection reasons: string, boolean, null,
non-integer number, array, object, and a strict integer missing an admitted
canonical event/pair. The exact 7,821 strings remain
`PRESERVE_UNMAPPED` with
`ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`. No raw evidence is discarded and
no rejected value can silently enter possession matching.

This is a legitimate semantic supersession rather than an ungoverned repair.
The evidence establishes a frozen numeric pair taxonomy, the measured input
type distribution is retained, and the runtime selector is numeric and
digest-bound. I found no unsupported semantic inference in the proposed
field-v2 change.

## 6. Possession semantic authority v2

The possession-v2 route also has fixed decision, candidate, review, and
acceptance IDs/paths and exact v2 decision/candidate schema versions. Its
acceptance retains the closed v1 schema and supersedes exactly
`w04-wyscout-possession-semantic-acceptance-v1`.

Its `bound_inputs` has exactly five keys:

- accepted field-v2 registry ID;
- accepted field-v2 candidate canonical digest;
- accepted field-v2 acceptance canonical digest;
- immutable event taxonomy physical digest;
- immutable tag taxonomy physical digest.

The v1 possession candidate independently parses to 36 unique predicate rows
in sorted `(event_id, subevent_id)` order. Every pair exists in the frozen
event taxonomy. All 36 required-tag arrays and all 36 forbidden-tag arrays are
empty. `control_team_source` is evenly split: 18 `ACTION_TEAM` and 18 `NONE`.
R21 requires all predicate rows, choices, actors, attachments, tag sets, and
rationales to be copied byte-semantically. It changes selector authority, not
possession meaning.

The CROSS_AUTHORITY selector may read only:

- `action_event_taxonomy_id`;
- `action_subevent_taxonomy_id`;
- `action_team_source_id`;
- `action_tag_ids`.

It fails to `UNMAPPED` on an absent event or subevent, a mistyped/boolean
taxonomy value, a missing exact pair, a required/forbidden tag mismatch, a
missing or mistyped tag array, or a missing team where the accepted predicate
requires `ACTION_TEAM`. It does not synthesize an empty tag array even though
the current 36 predicates happen to have empty sets. It cannot read raw event
fields, raw/rejected subevent evidence, names, labels, or coerced
representations.

This selector discipline closes the main cross-authority risk. A raw string
`"10"` cannot match integer `10`; a boolean cannot match integer `0` or `1`;
and a predicate cannot be reinterpreted merely because its label appears
familiar. If the v1 predicate cannot be evaluated from the accepted canonical
field-v2 outputs, the action is explicitly ineligible rather than guessed.

The explicit output
`possession_eligibility_state = ELIGIBLE_RESOLVED |
INELIGIBLE_UNMAPPED` makes feature applicability reviewable. It is project
inference under the unchanged R20 same-period sequence rules, not a
provider-native possession claim. I found no widening of the accepted 36-row
taxonomy and no hidden label dependency.

## 7. Product-contract preimage

The product-contract preimage has a fixed path, ID, schema version, and exactly
nine top-level keys. Its `authority_links` names R20 and final R21, and the
materializer must replace the explanatory R21 placeholder with this exact
candidate physical SHA before canonicalization. Angle-bracket notation is
forbidden in materialized JSON.

The design closes:

- three ordered layers: `BRONZE`, `SILVER`, `GOLD`;
- 17 exact path-template rows;
- 10 serializer-owner rows;
- exactly one owner for every path role;
- two and only two primary-key contracts;
- five manifest/receipt templates corresponding to path roles 13–17;
- a three-key policy object that is control-plane-only and forbids product
  bytes before the complete R21 gate.

I mechanically counted 17 path rows and 10 owner rows. The path roles cover
known and rejected Bronze records, six Silver products, one Gold product,
three layer manifests, and two receipts. They remain relative template
strings; none is an observed output or permission to create a directory.

The serializer names are ownership tokens describing the immutable R20
surface, not executable files claimed to exist. The two primary keys apply
only to `SILVER_PLAYER_MATCH_FACT` and `GOLD_PLAYER_WINDOW`; R21 correctly
does not invent keys for other products. The five manifest/receipt rows reuse
the identical templates and corresponding owners, avoiding a second
inconsistent path vocabulary.

The object cannot contain its own digest, the schema-preimage digest, a feature
digest, build/run IDs, clocks, mutable roots, hosts, absolute paths, output
observations, or product bytes. This produces a stable canonical preimage
without confusing a contract description with an implementation.

## 8. Schema-bundle preimage

The schema-bundle preimage has a fixed path, ID, schema version, and exactly six
top-level keys. It shares an authority-link object byte-semantically with the
product-contract preimage but has no digest edge to that sibling.

I mechanically counted 16 ordered descriptor rows. Each row has exactly:

- `depends_on`;
- `descriptor_id`;
- `descriptor_version`;
- `role`;
- `surface_kind`.

Every `depends_on` target is an earlier descriptor, so the descriptor roster is
topologically ordered. `dependency_order` is the identical descriptor-ID list.
The surface kind is always the exact literal
`CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`. That deliberately
long token is valuable: a consumer cannot reasonably interpret these rows as
proof that a Pydantic model, Parquet schema, serializer, table, file, manifest,
or receipt exists.

The descriptors cover the source envelope, three Bronze roles, seven Silver
roles, one Gold role, a layer manifest, and two receipt roles. Their
dependencies are consistent with the immutable R20 layer flow. The manifest
descriptor depends on all described layer surfaces; rebuild and temporal
receipts depend only on earlier manifest/Gold descriptors.

The five-key `feature_schema_hash_placeholder` is well typed:

- `concrete_value` is null;
- `json_type` says the eventual value is a string;
- `pattern` requires lowercase 64-hex;
- `resolution_source` names the accepted supported-feature candidate digest;
- `state` says resolution is deferred until supported-feature acceptance.

This does not use null as a feature hash and does not insert a future digest
into an ancestor. I found no implemented-schema overclaim or cyclic feature
binding.

## 9. Supported-feature authority

The feature route retains the fixed v1 route IDs and paths because no feature
authority has yet been accepted. R21 does not fabricate an acceptance; it
closes the exact future decision/candidate inputs and roster.

The feature `bound_inputs` object has exactly ten keys. It binds:

- accepted field-v2 registry ID, candidate canonical digest, and acceptance
  digest;
- accepted possession-v2 taxonomy ID, candidate canonical digest, and
  acceptance digest;
- both control-preimage IDs and canonical digests.

It rejects v1 semantic digests, physical candidate digests in canonical fields,
bare product/schema digests, and any unaccepted candidate.

I mechanically reconstructed the 15 sorted feature rows and their state split:

- four `SUPPORTED`;
- four `SUPPRESSED_UNSUPPORTED_DENOMINATOR`;
- seven `UNAVAILABLE`.

The four supported rows are exactly:

1. `action_count`;
2. `coordinate_known_action_count`;
3. `match_count`;
4. `resolved_possession_action_count`.

The four suppressed rows are `action_rate`, `actions_per_90`,
`minutes_lower`, and `minutes_upper`. They have no accepted elapsed-minutes
denominator. The seven unavailable rows cover continuous time, outcome
dependence, provider-native possession, lineup-stint count, role inference,
unresolved action evidence, and an action-value model.

Every row has exactly eight fields. Supported features have closed canonical
inputs and concrete `int64` outputs. Suppressed/unavailable rows have empty
inputs, `NONE` aggregation/applicability as specified, and null output.
Absence never grants permission and no sixteenth feature is allowed.

`resolved_possession_action_count` consumes canonical field-v2 outputs and is
applicable only when the accepted possession-v2 eligibility state is
`ELIGIBLE_RESOLVED`. R21 correctly describes eligibility as an explicit
possession-authority predicate rather than hiding it as an unlisted fourth raw
input. A missing canonical subevent cannot satisfy that predicate.

The feature candidate's canonical digest becomes `feature_schema_hash` only
after its separate decision, independent review, acceptance, and master
verification. Before then the hash remains unavailable. This is conservative
and consistent with the preimage DAG.

## 10. Evidence-preserving resource roster

R21 derives, rather than merely asserts, the exact resource cardinality:

- 17 immutable R20 resources;
- one R21 design;
- one R15 independent review;
- two control preimages;
- four field-v2 route artifacts;
- four possession-v2 route artifacts;
- one cross-authority contract test.

The total is exactly 30. I extracted all 30 numbered paths mechanically:
cardinality is 30 and uniqueness is 30. I separately extracted the R20
17-path allowlist and compared it with R21 positions 1–17; the sequences are
exactly equal.

This prefix preservation is significant. R21 does not replace historical v1
resources with v2 or omit the existing feature route. The supported-feature
candidate and its three future authority artifacts were already R20 positions
4 and 14–16, so R21 correctly adds zero paths for them. Double-counting those
four paths would produce an erroneous 34-resource roster.

R15 is the sole active design review and occupies position 19:
`reports/reviews/W04/wyscout-schema-design-independent-review-R15.md`.
Failed R14 remains historical control evidence outside the runtime resource
roster. The remaining additions are in the exact downstream order described by
the authority graph.

Every later resource row must retain exact path, physical digest, size, mode,
purpose, parser/schema version, and authority link. Directory shorthand, globs,
optional paths, duplicate paths, product outputs, generated manifests,
receipts, runtime evidence, and returns are not local resources. The design
therefore expands evidence without weakening R20's guarded-resource model.

## 11. Temporal dependencies

R21 retains immutable R20's exact `EvidenceDependency` wire schema, enum,
UUIDv5 construction, sort key, cardinality, lineage-hash algorithm,
strict-before predicates, and watermark rule. It changes only the semantic
authority bindings.

The set remains exactly five:

1. strict source manifest;
2. accepted identity evidence;
3. accepted field-v2 registry;
4. accepted possession-v2 taxonomy;
5. accepted supported-feature registry.

The source and identity routes remain as authorized by R20. Field and possession
use their accepted v2 candidate canonical digests and decision/acceptance
clocks. Feature uses its accepted v1-route candidate canonical digest and
decision/acceptance clocks. The identity route remains v1 because R21 does not
supersede accepted identity semantics; its later correction decision must bind
field v2 rather than create a second field authority.

Actual ordering remains R20's sort over enum rank, UUID bytes, digest,
`observed_at`, and `available_at`; the explanatory R21 table does not replace
that sort. Every dependency still has only `kind`, `dependency_id`, `digest`,
`observed_at`, and `available_at`.

R21 explicitly rejects field-v1/possession-v2, possession-v1/feature-v1-under-
R21, and every other mixed generation. It also retains strict `<` rather than
`<=` for every dependency and authority clock. I found no version hybrid or
temporal relaxation.

## 12. Packet order, ownership, and independent review

I mechanically counted 16 serial packets. Their order is coherent:

1. final R21 producer artifact;
2. this fresh R15 review;
3. control-preimage materialization;
4. independent preimage review;
5–7. field-v2 decision, independent review, acceptance;
8–10. possession-v2 decision, independent review, acceptance;
11–13. feature decision, independent review, acceptance;
14. returned cross-authority test;
15. fixed independent cross-authority review;
16. master cross-authority gate.

Every packet has exhaustive sole-write paths. Candidate producers cannot review
or accept their own work. The test producer is distinct from the fixed
cross-authority reviewer, and that reviewer is distinct from every authority
producer. The master gate binds the complete physical digest of the fixed
review and requires `PASS`.

The cross-authority test, independent review, and master gate are three separate
packets. Combining their write scopes or running the gate before the review
passes is explicitly rejected. Shared contracts, candidates, acceptances,
orchestration state, and the cross-authority test are never parallel write
scopes. Packet YAML and orchestration state remain master-owned.

This review owns only its fixed report and return. It performs no Git operation,
does not edit R21 or any predecessor, does not materialize descendants, and
does not accept itself. The master must independently read back the exact R21
and R15 bytes before any successor packet starts.

## 13. Composability suite and final gate

R21 specifies 14 positive cross-authority cases. They cover strict admitted
pairs, byte-semantic preservation of all 36 predicates, canonical selector
flow, missing-subevent ineligibility, feature applicability, exact feature
cardinality, canonical preimages, sibling DAG behavior, immutable resource
prefix, v2 supersession, digest propagation, distinct independent review,
master review binding, and absence of product paths.

I also counted 30 negative-case bullets. They reject the important failure
classes:

- numeric-looking strings, whitespace/sign/leading-zero strings, booleans,
  null, decimal numbers, arrays, and objects;
- language bool-as-int behavior and any loss of the 7,821 string evidence;
- unknown pairs, raw-field selectors, label/name lookup, and runtime taxonomy
  label matching;
- missing canonical subevents and missing/mistyped tags;
- v1/v2 hybrids and malformed prior-authority records;
- v1 mutation and physical/canonical digest substitution;
- preimage self/sibling/future/runtime edges or values;
- concrete premature feature hashes and implemented-schema overclaims;
- feature roster/state/input drift;
- use of any unaccepted semantic or feature authority;
- resource drift;
- missing, wrong-path, non-PASS, or self-authored independent review;
- collapsed test/review/gate scopes;
- any product path created before the complete gate.

The complete final gate retains the exact 12-command repository suite, in
order:

1. locked all-group sync;
2. Ruff format check;
3. Ruff lint;
4. mypy over `src/scouting scripts`;
5. import-linter;
6. full pytest;
7. Bandit;
8. local Git-guard check;
9. local-only verification;
10. W04 phase verification;
11. empty short Git status;
12. empty Git remote list.

Focused checks are not treated as sufficient. R21 then adds exactly 18
correction-specific checks covering the candidate hash/base binding, R15,
preimages, graph restrictions, both v2 routes, strict typing, possession
selectors, feature authority, supersession, dependencies, resources,
cross-authority three-packet order, full composability tests, forbidden product
paths, bytecode equality, master readback, and a machine-readable `PASS` gate.

This is appropriately stronger than a design-only test. A passing R15 review
does not skip materialization tests, v2 authority reviews, full repository
checks, or master verification.

## 14. Preserved R14 evidence and active R15 chain

Failed R14 is preserved rather than rewritten. I independently reproduced its
four recorded physical hashes:

- R14 review:
  `8c2c78276191b67ff074d1f405306ed811b92d36319a5c0e7b119807a3a611d3`;
- R14 return:
  `716a21919eabb9bc1b5c6e8227c4b056a18f41da8f7cdbf0ef4def6c8a9274f9`;
- R14 master review:
  `fda346d0cfd5a4e8af719395612b981d6ba896727e6c9ec5c8214b91d63f8900`;
- R14 master verification:
  `cfd65a59d6579b0335bbaae7b14034f48052b11196783716a7e2ea71bd686513`.

The immutable R21 R2 return remains 6,675 bytes, 141 lines, and SHA-256
`82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10`.
The R3 successor evidence records that exact cardinality and preserves the
failed R14 chain. R14's earlier P2 was therefore answered through additive
successor evidence rather than mutation.

R21 now names only R15 as the active design review ID/path, local-resource
member, serial packet, and final-gate requirement. Its R14 references are
explicitly historical, failed, immutable, outside the 30-resource roster, and
not implementation authority. There is no recency scan or ambiguous
"latest review" rule.

The final R21 R3 producer return, producer packet, master review, and master
verification all route to R15. Their role is admission to fresh independent
review, not final acceptance. This report supplies that independent merits
recommendation; the next state change remains master-owned.

## 15. No-product and local-only boundary

R21 ends at the correction gate. It expressly forbids, until a later separately
authorized master packet:

- Bronze, Silver, or Gold implementation;
- feature materialization;
- serializer implementation;
- manifest or receipt generation;
- runtime/build invocation;
- model or product implementation;
- network/provider acquisition;
- cloud, container, endpoint, hosted CI, or deployment work;
- any Git remote.

The design is consistent with the controlling blueprint and execution workflow:
one local uv environment, master-owned Git/checkpoints, bounded serial
authority work, independent review, and no remote deployment. It does not
change the provider, source rights, root layout, dependency set, storage model,
service topology, or product claim.

The preimage materialization packets remain future control-plane work. Their
path strings are not filesystem authorization. The feature roster is not
computed output. The schema descriptors are not implemented schemas. The
resource allowlist does not create any listed path. The final gate's product
scan is therefore both meaningful and enforceable.

## 16. Independent challenge matrix

| challenge | reconstructed evidence | result |
|---|---|---|
| Exact candidate | 59,565 physical bytes hash to `faff34cc...7020` | PASS |
| Immutable base | 245,957 physical bytes hash to `8cb2f0d4...8047` | PASS |
| Complete readback | 4,516 R20 lines and 1,254 R21 lines read in full | PASS |
| Six-family merge | exact six replacement names; every other R20 clause retained | PASS |
| Field prior object | exact 17-key copy plus acceptance digests | PASS |
| Possession prior object | exact 17-key copy plus acceptance digests | PASS |
| Accepted field v1 | physical `805fcc...81f2`, canonical `fb133d...1034` | PASS |
| Accepted possession v1 | physical `e45637...78d`, canonical `6a598d...fdfa` | PASS |
| Review records | field `8beb74...7fa0`, possession `40aa25...0962` | PASS |
| Field rows | 119 total; only one-based row 107 changes | PASS |
| Measured shape | integer 3,063,574; string 7,821 | PASS |
| Typed quarantine | seven closed non-emitting conditions/reasons | PASS |
| Possession predicates | 36 unique sorted pairs, all in frozen taxonomy | PASS |
| Possession tag sets | all required and forbidden arrays empty | PASS |
| Team source | 18 `NONE`, 18 `ACTION_TEAM` | PASS |
| Canonical selector | only four field-v2 outputs; raw/name/label reads forbidden | PASS |
| Product paths | 17 exact descriptor strings | PASS |
| Serializer owners | 10 rows; exact once-only role ownership | PASS |
| Schema descriptors | 16 ordered rows; earlier-only dependencies | PASS |
| Descriptor literal | exact non-implementation surface-kind guard | PASS |
| Feature roster | 15 sorted rows, eight keys each | PASS |
| Feature states | 4 supported, 4 suppressed, 7 unavailable | PASS |
| Resources | 30 unique paths | PASS |
| R20 resource retention | positions 1–17 exactly equal R20 allowlist | PASS |
| Active review | R15 at resource position 19; R14 historical only | PASS |
| Dependencies | exact cardinality five with anti-mixing rule | PASS |
| Serial packets | exact cardinality 16 with distinct reviewers | PASS |
| Positive cases | exact cardinality 14 | PASS |
| Negative bullets | 30 enumerated failure classes | PASS |
| Repository commands | exact ordered cardinality 12 | PASS |
| Additive checks | exact cardinality 18 | PASS |
| Immutable R14 chain | four current hashes equal retained successor evidence | PASS |
| Local-only boundary | no product/materialization/deployment authorization | PASS |

## 17. Residual obligations, not findings

The following remain deliberately unresolved until their named packets execute:

- the accepted physical/canonical digests of the two materialized preimages;
- the decision, candidate, review, and acceptance digests/clocks for field v2;
- the corresponding possession-v2 evidence;
- the feature decision, candidate, review, acceptance, and eventual canonical
  `feature_schema_hash`;
- the returned cross-authority test digest and its packet-return digest;
- the fixed independent cross-authority review digest;
- the complete machine gate report and final checkpoint evidence;
- any later product implementation.

These are not P2 omissions because R21 gives each a fixed ID/path, closed input
contract, serial predecessor, distinct review actor, test obligations, and
master gate. Filling those values in this design would be premature and, for
the feature/preimage chain, cyclic.

Implementers must not use this PASS recommendation as evidence that a future
artifact passed. Each descendant remains unavailable until its own packet,
independent review where required, acceptance, and master verification are
complete.

## Final recommendation

`PASS`.

The exact R21 candidate at
`faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`
is bounded, acyclic, evidence-preserving, conservative, and composable with
immutable R20. It resolves the action-subevent/possession/feature authority
gap without coercion, label lookup, v1 mutation, resource loss, temporal
relaxation, product creation, architecture expansion, or self-approval.

Finding count remains `P0=0`, `P1=0`, `P2=0`. The master may independently
read back this review and decide whether to accept R21 into the next serial
control-preimage packet. No broader authority is granted.
