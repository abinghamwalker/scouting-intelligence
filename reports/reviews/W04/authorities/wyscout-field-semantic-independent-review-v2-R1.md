# W04 Wyscout field-semantic v2 independent review R1

## Recommendation

PASS.

I found no P0, P1, or P2 defect in the bounded W04 field-semantic v2 decision, registry candidate, or focused authority contract. The v2 artifacts are a closed, deterministic, digest-linked progression from the accepted v1 authority. They introduce exactly one semantic change: the action `$.subEventId` row now permits a canonical subevent taxonomy identifier only when both the event identifier and raw subevent value are strict JSON integers and their ordered pair occurs in the frozen event taxonomy. The design does not parse strings, treat booleans as integers, use labels at runtime, guess unknown pairs, or discard rejected raw evidence.

This recommendation is limited to the field-semantic v2 authority packet. It is not acceptance, does not create an acceptance record, does not convert the already accepted inert product-contract or schema-bundle control preimages into product authority, and does not authorize staging, identity, bronze, silver, gold, manifests, admission code, rebuild code, launch code, or any downstream product claim.

## Review identity and fixed bindings

The reviewed authority is bound as follows:

- review ID: `w04-wyscout-field-semantic-independent-review-v2-R1`
- review schema: `w04-authority-independent-review-v1`
- independent reviewer actor: `03a65770-02f6-5eb0-9bd2-e2ebb44b62bd`
- decision ID: `w04-wyscout-field-semantic-decisions-v2`
- decision physical and canonical SHA-256: `cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736`
- candidate ID: `w04-wyscout-field-registry-v2`
- candidate physical SHA-256: `15023556072f90b1e956277f255dc4a1df0bea78a5dcbb14b4863346ff9b5193`
- candidate parsed canonical JSON SHA-256: `93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959`
- decision time: `2026-07-30T20:22:17Z`
- review time: `2026-07-30T21:15:45Z`

The reviewer actor is a canonical RFC 4122 version-5 UUID and differs from the master decision actor `4efe5691-8903-5148-8275-30d2e7e8aed0`. The review clock is canonical UTC, is not earlier than the decision clock, and was recorded from the review environment after the merits work completed.

## Scope and method

I reviewed the complete authority chain and did not rely on the producer return or master verification as a substitute for inspection. The read set included the controlling R20 design, the R21 delta, the earlier independent design review, the control-preimage independent review, the schema-bundle and product-contract preimages, the complete v1 decision/registry/review/acceptance chain, the complete v2 decision and registry, the producer return, master review and verification evidence, both focused contract files, the measured source-schema profile, the completion manifest, and both taxonomy CSVs.

The review method had six independent layers:

1. Bind every fixed input and predecessor artifact by physical SHA-256.
2. Parse and deterministically rerender the v2 decision and registry, checking both physical and parsed canonical identities.
3. Reconstruct the v2 authority from the immutable v1 decision plus the single R21 row replacement rather than accepting the candidate as its own oracle.
4. Reconstruct the frozen event/subevent pair set directly from the taxonomy CSV and challenge the strict-integer projection boundary with positive and negative values.
5. Inspect the focused suites in full, then run them in the locked, no-sync environment with bytecode generation disabled.
6. Audit authority progression, premature paths, local-only boundaries, and pre-existing bytecode/cache hygiene without deleting or normalizing any pre-existing state.

No network or provider access was used. No dependency synchronization or installation occurred. No Git operation was performed. No candidate, test, orchestration, decision, acceptance, downstream, or product file was edited.

## Fixed evidence and digest closure

The decision contains exactly ten bound-input members. I independently hashed the referenced files and confirmed the complete object:

| Bound input | Independently observed value |
| --- | --- |
| completion manifest SHA-256 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| event taxonomy source SHA-256 | `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842` |
| product contract preimage ID | `w04-wyscout-product-contract-preimage-v1` |
| product contract preimage SHA-256 | `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293` |
| R20 design SHA-256 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 design SHA-256 | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| schema-bundle preimage ID | `w04-wyscout-schema-bundle-preimage-v1` |
| schema-bundle preimage SHA-256 | `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f` |
| source-schema profile SHA-256 | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` |
| tag taxonomy source SHA-256 | `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922` |

The v2 decision is strict compact canonical JSON with sorted keys, UTF-8 encoding, NFC-compatible values, one trailing LF, no BOM, and no duplicate member admitted by the contract loader. Its physical bytes equal its canonical bytes and hash to the fixed decision digest.

The registry is strict deterministic YAML. Scanning found no aliases, anchors, directives, or explicit tags. Parsing found the expected single mapping document and safe scalar classes. Deterministic rerendering with fixed insertion order, no aliases, Unicode enabled, block style, no document markers, and width 4096 reproduced all `66,221` physical bytes exactly. The physical digest and the canonical JSON digest of the parsed registry both match the packet bindings.

The registry is an exact semantic restatement of the decision:

- `bound_inputs` equals the decision object.
- `decision_id` equals `w04-wyscout-field-semantic-decisions-v2`.
- `decision_sha256` equals the physical/canonical decision digest.
- `fields` equals the decision `decisions` array as parsed.
- `policies` equals the decision policies.
- `prior_authority` equals the decision predecessor object.
- registry ID, registry schema version, and source ID are exact.

During independent renderer calibration, I also verified an intentional serialization detail that could otherwise conceal a false-positive comparison. Canonical JSON sorts each source-shape mapping as `count`, then `json_type`. The deterministic YAML row replacement is physically rendered as `json_type`, then `count`. Parsed semantics are identical, and reconstruction using the authority-prescribed YAML insertion order reproduces the candidate byte-for-byte. This is serialization discipline, not semantic drift.

## Immutable v1 predecessor

The v1 chain was rehashed rather than assumed:

| v1 artifact | Physical SHA-256 |
| --- | --- |
| field-semantic decision v1 | `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999` |
| field registry v1 | `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2` |
| independent review R1 | `e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861` |
| acceptance v1 | `fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365` |
| frozen v1 contract test | `d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3` |

The parsed v1 registry canonical digest remains `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`. The v1 acceptance object is strict canonical JSON, so its physical and canonical digests are identical. Adding only the two explicitly required physical/canonical acceptance digest bindings to that accepted record reconstructed the v2 `prior_authority` object exactly.

The predecessor object has exactly seventeen members. It binds the v1 acceptance ID/schema/time/actor, v1 candidate ID and both candidate digests, v1 decision ID and both decision digests, v1 review ID, physical review digest, canonical review-record digest, PASS recommendation, and a null predecessor-acceptance reference. Missing, extra, changed, or candidate-drifted predecessor members are rejected by the v2 contract.

The v1 bytes are unchanged. No back-edit to the accepted decision, registry, review, acceptance, or test was required or observed.

## Roster reconstruction and sole delta

The R20 normative machine roster contains exactly 119 unique ordered `(record_kind, json_path)` pairs. The profile and roster agree without omission or addition. The per-kind counts are:

| Record kind | Rows |
| --- | ---: |
| competition | 10 |
| team | 11 |
| player | 26 |
| match | 47 |
| action | 18 |
| event-taxonomy | 4 |
| tag-taxonomy | 3 |

Every decision row has exactly the eight required members: canonical field, decision, JSON path, rationale, record kind, measured source shape, source support, and transform. Every row’s shape agrees with the measured profile. Decisions are limited to `TRANSFORM`, `PRESERVE_UNMAPPED`, and `FORBIDDEN`. Source support is limited to the four closed support classes. Transformed rows have a valid governed canonical field and a closed transform member set. Non-transform rows have exact null canonical-field and transform members.

I compared the v1 and v2 decision arrays positionally with strict equal length. The difference-index vector is exactly `[106]`. There are 118 equal rows and one changed row. Replacing v1 row 106 with the R21 row and preserving every other v1 member reconstructs the complete v2 decision and registry.

No row was omitted, added, duplicated, reordered, or reassigned to another record kind. No unrelated rationale, transform, policy, support class, source shape, identifier, or canonical field changed.

## Review of the `$.subEventId` semantic

The sole changed row is correctly bounded:

- record kind: `action`
- JSON path: `$.subEventId`
- canonical field: `action_subevent_taxonomy_id`
- decision: `TRANSFORM`
- source support: `PROFILE_AND_EVENT_TAXONOMY`
- measured integer observations: `3,063,574`
- measured string observations: `7,821`
- transform kind: `EVENT_SUBEVENT_TAXONOMY_ID_V2`

The source profile reports all `3,071,395` action rows at this path and explicitly separates `3,063,574` integers from `7,821` strings. It reports the string observations as invalid/missing for the older event-to-subevent membership measurement; it does not justify parsing them. The v2 choice therefore increases safe canonical coverage only for the already numeric population admitted by a frozen pair, while preserving the complete mixed-type boundary.

The transform has exactly the required members and values:

- accepted JSON type is `STRICT_INTEGER`.
- the admitted key is the ordered pair of `action_event_taxonomy_id` and `raw_subevent_integer`.
- `boolean_is_integer` is false.
- non-integer policy is `PRESERVE_UNMAPPED`.
- string policy is `PRESERVE_UNMAPPED_NO_COERCION`.
- unknown-integer policy is `PRESERVE_UNMAPPED`.
- runtime label matching is `FORBIDDEN`.
- taxonomy digest is the frozen event taxonomy SHA-256.

These clauses jointly close the common coercion gaps. A string such as `"10"`, `" 10"`, `"+10"`, or `"010"` cannot emit a canonical value. Neither `true` nor `false` can exploit the host-language relationship between booleans and integers. A floating value such as `10.0`, null, array, or object cannot emit. An integer paired with an unknown event, an unknown subevent for a known event, or a noncanonical event value cannot emit. The original raw value remains available as rejected-field evidence with a stable reason category.

The admitted key is deliberately pair-valued. A subevent integer is not treated as globally sufficient merely because that integer appears somewhere in the taxonomy. This prevents a subevent from being attached to the wrong event family. The rule also requires the already canonical strict-integer event identifier; it does not reconstruct an event key from `eventName` or any other display label.

## Frozen taxonomy reconstruction

I parsed `eventid2name.csv` directly with the exact columns `event`, `subevent`, `event_label`, and `subevent_label`. The file contains 36 unique integer `(event, subevent)` pairs:

- event 1: subevents 10, 11, 12, 13
- event 2: subevents 20 through 27
- event 3: subevents 30 through 36
- event 4: subevent 40
- event 5: subevents 50, 51
- event 6: subevent 60
- event 7: subevents 70, 71, 72
- event 8: subevents 80 through 86
- event 9: subevents 90, 91
- event 10: subevent 100

The reconstructed set exactly matches the contract’s frozen set and the taxonomy digest bound by the transform. I challenged every one of the 36 pairs as a strict-integer positive: all and only those values emitted their subevent integer.

The pair membership rule uses integer columns only. Labels are evidence in the source file but have no role in runtime projection. `eventName`, `subEventName`, `event_label`, and `subevent_label` remain forbidden as matching authority. Case, whitespace, spelling, localization, or label revision therefore cannot silently change identity.

## Raw-preservation and reason behavior

The focused contract requires stable rejected-field reason categories for arrays, booleans, unknown integers, null, non-integer numbers, objects, and strings. My independent challenge exercised fourteen negative runtime cases:

- four numeric-looking strings with plain, leading-space, explicit-sign, and leading-zero representations;
- a boolean subevent and a boolean event;
- null;
- a floating number;
- an array;
- an object;
- a known event with an unknown subevent integer;
- an unknown event with an otherwise known subevent integer;
- a null event with an integer subevent;
- a string event with an integer subevent.

None emitted a canonical subevent. The contract additionally asserts exact raw value and exact raw type preservation for representative non-integer inputs. The reason-code set is closed to:

- `ACTION_SUBEVENT_ARRAY_UNMAPPED`
- `ACTION_SUBEVENT_BOOLEAN_NOT_INTEGER`
- `ACTION_SUBEVENT_INTEGER_NOT_IN_FROZEN_PAIR_TAXONOMY`
- `ACTION_SUBEVENT_NULL_UNMAPPED`
- `ACTION_SUBEVENT_NONINTEGER_NUMBER_UNMAPPED`
- `ACTION_SUBEVENT_OBJECT_UNMAPPED`
- `ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`

This behavior is consistent with R21: raw evidence survives rejection, while canonical projection remains limited to explicitly admitted strict-integer pairs. The `7,821` measured strings are therefore neither lost nor upgraded.

## Policies and transform closure

The v2 policies are unchanged from v1:

- known profile pairs require an explicit decision.
- provider-native semantic claim is false.
- runtime label matching is forbidden.
- unknown envelope kinds reject the record.
- unknown fields remain unmapped.

The contract validates each transform as a tagged closed union. Unknown transform kinds and cross-kind keys reject. Strict integer bounds require actual integers rather than booleans or floats. Decimal precision/scale, UTC formats, source-ID entity kinds, period-relative seconds, position arrays, sorted tags, event/tag taxonomy transforms, and composed-object rules remain constrained to their frozen shapes.

Canonical-field collisions reject unless all colliding producers are valid, disjoint-member `COMPOSE_OBJECT` transforms for one output object. The new subevent canonical field has a single producer and creates no collision.

The registry does not claim review, acceptance, dependency closure, bronze readiness, or another later state. The decision’s exact top-level key set prevents those premature additions.

## Mutation challenges

In addition to the suite’s parameterized negative tests, I made independent in-memory mutations against the reconstructed authority. I did not write mutated artifacts to disk.

| Mutation | Expected result | Observed result |
| --- | --- | --- |
| accepted type changed to integer-or-string | reject | reject |
| admitted key reduced to raw subevent alone | reject | reject |
| boolean treated as integer | reject | reject |
| non-integer policy changed to drop | reject | reject |
| runtime label matching allowed | reject | reject |
| string policy changed to parse | reject | reject |
| taxonomy digest replaced | reject | reject |
| unknown integer policy changed to guess | reject | reject |
| predecessor recommendation changed to REWORK | reject exact reconstruction | reject |
| registry decision digest replaced | reject exact reconstruction | reject |

The focused suite separately challenges roster omissions, additions, duplicates, reordering, wrong counts, source-shape drift, bound-input changes, unknown decisions, unknown supports, illegal nulls, illegal non-null transforms, policy drift, actor mutations, noncanonical clocks, noncanonical JSON/YAML, unsafe YAML classes, digest substitution, canonical-field collision, premature authority claims, review mutations, acceptance mutations, malformed review fences, and downstream paths.

The positive side is also present. The test does not merely prove that mutations fail: it reconstructs both artifacts from fixed evidence, validates all 119 rows, admits all 36 frozen pairs, admits valid review states, and simulates the one valid future acceptance progression.

## Focused-suite quality

I read both focused files in full before execution:

- `tests/contracts/test_w04_field_semantic_v2_authority.py`, 2,149 lines
- `tests/contracts/test_wyscout_field_registry_authority.py`, 1,869 lines

The v1 suite remains a frozen regression anchor. It reconstructs the original 119-row authority from R20 and the measured profile, validates serialization and closed transforms, and validates the original review/acceptance progression. The v2 suite layers the R21 progression rather than weakening or replacing the v1 guard.

The v2 suite independently hashes all ten inputs, enforces all seventeen predecessor fields, verifies the exact v1 physical bytes, and requires the difference vector `[106]`. It strictly parses canonical decision JSON and deterministic registry YAML. It rejects BOMs, duplicate JSON keys, duplicate YAML keys, aliases, anchors, directives, explicit tags, merge keys, non-string keys, implicit timestamps, and floats. It verifies candidate physical and canonical digests separately, preventing substitution of one digest class for the other.

Review parsing requires exactly one `w04-authority-review-v1` fence with a canonical JSON body. It rejects extra fenced blocks, wrong information strings, extra body records, BOMs, and unclosed fences. The review record has an exact key set, a UUID actor distinct from the decision actor, a non-backdated clock, a closed P0/P1/P2 finding schema, and consistent PASS/REWORK semantics.

Future acceptance parsing has an exact key set and binds the candidate, decision, physical review file, and canonical review record separately. It requires a valid PASS review, the master acceptance actor, clock order, and `supersedes_acceptance_id` equal to the accepted v1 authority. It rejects acceptance without review, acceptance after REWORK, self-acceptance, digest substitutions, malformed canonical JSON, and premature downstream paths.

The complete focused execution result was `271 passed in 36.69s`. There were no skips, expected failures, warnings presented as success, or flaky reruns in the observed output.

## Local-only and environmental controls

All Python commands used `PYTHONDONTWRITEBYTECODE=1`. The locked runtime check confirmed both the environment variable and `sys.dont_write_bytecode=True` before importing the YAML dependency. All project commands used `uv run --locked --no-sync`; no lockfile or environment synchronization was authorized.

The packet-mandated local-only verifier returned PASS with no failures. It confirmed:

- zero configured remotes;
- the root uv project, lockfile, and root virtual environment;
- Python 3.12 runtime and pin;
- no Git or direct-URL dependency declarations;
- no alternate package-manager or Node manifests;
- no hosted CI/deployment, container, or external-service definitions;
- structured configuration parses;
- no outside-root config or prohibited config URLs;
- no outside-root symlinks;
- the approved directory skeleton;
- the local virtual environment is ignored.

The uv invocation required read access to the existing user cache under the managed filesystem boundary. That access was granted only to run the packet-mandated locked/no-sync commands. It did not authorize network, synchronization, package installation, or writes to authority inputs.

## Bytecode/cache hygiene inventory

Before reading the candidate or running Python, I took the packet-required shell-only recursive inventory of every `__pycache__` directory, `.pyc` file, and `.pyc` symlink under the repository. Each inventory row bound path, kind, byte size, mode, link target or absence, mtime epoch, first 16 bytes for files, and full file SHA-256. Directory rows bound path and metadata; their descendant files were individually byte-bound.

The baseline comprised:

- 1,145 `.pyc` files;
- 150 `__pycache__` directories;
- 1,295 total serialized inventory rows;
- 317,665 serialized inventory bytes;
- whole-inventory SHA-256 `90075607ab7f6330fce681af63ae0c3c9a618e287a544eb34469a1f392bca6bc`.

These are pre-existing repository/work-environment artifacts. The review neither deletes nor normalizes them. The identical shell inventory is repeated after the final report and return edit and all checks. Equality of row count, serialized byte count, and whole-inventory SHA-256 is a validity condition for this review.

## Progression and absence audit

At corrected-review time, the field-v2 acceptance JSON was absent. The not-yet-reached possession-v2 decision/candidate/review/acceptance, exact feature decision/candidate/review/acceptance, cross-authority test/review/master-gate, complete-repository gate, downstream data, manifest, admission, rebuild, and launch paths were absent. The accidental parent-workspace `reports` and `configs` chains were also absent.

The accepted R21 progression already includes the R21 design independent review and master acceptance; sibling control-preimage materialization, independent review, and master acceptance; and field-v2 decision/candidate producer master verification. The product-contract and schema-bundle preimages are inert sibling control artifacts. They have no future acceptance JSON packet, are not later candidates, and confer no product authority.

The corrected current review remains subject to field-v2 independent-review master acceptance and the separately owned field-v2 acceptance JSON. That acceptance must validate this review’s physical digest and canonical record digest, require the master actor, enforce decision ≤ review ≤ acceptance clock order, and supersede `w04-wyscout-field-semantic-acceptance-v1`.

The exact remaining serial gates after field-v2 review are: field-v2 independent-review master acceptance and acceptance JSON; possession-v2 decision, independent review, and acceptance; the exact feature decision, independent review, and acceptance; the cross-authority test, independent review, and master gate; and the complete repository plus R21-specific gate. Only the complete final gate can close the correction. No focused review or acceptance authorizes product implementation.

## Findings

### P0

None.

### P1

None.

### P2

None.

There are zero review findings. Under the fixed rule, zero P0-P2 findings yields PASS; any remaining P0-P2 finding would require REWORK.

## Canonical review authority record

The following is the sole machine-readable authority record in this report. Its body is strict compact canonical JSON with sorted keys and one trailing LF.

```w04-authority-review-v1
{"candidate_id":"w04-wyscout-field-registry-v2","candidate_physical_sha256":"15023556072f90b1e956277f255dc4a1df0bea78a5dcbb14b4863346ff9b5193","candidate_sha256":"93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959","decision_id":"w04-wyscout-field-semantic-decisions-v2","decision_physical_sha256":"cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736","decision_sha256":"cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-field-semantic-independent-review-v2-R1","review_schema_version":"w04-authority-independent-review-v1","reviewed_at":"2026-07-30T21:15:45Z","reviewed_by":"03a65770-02f6-5eb0-9bd2-e2ebb44b62bd"}
```

## Command evidence

The acceptance-focused contract command was:

`PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q tests/contracts/test_w04_field_semantic_v2_authority.py tests/contracts/test_wyscout_field_registry_authority.py`

Result: exit 0; 271 passed in 36.69 seconds.

The local-only command was:

`PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`

Result: exit 0; status PASS; failures empty; all 25 named checks passed.

The independent reconstruction produced:

- ten exact bound inputs;
- seventeen exact predecessor-authority members;
- 119 rows with counts `[10, 11, 26, 47, 18, 4, 3]`;
- sole difference index `[106]`;
- exact decision physical/canonical digest;
- exact registry physical digest;
- exact parsed registry canonical digest;
- 36 positive frozen taxonomy pairs;
- 14 representative negative runtime cases;
- ten independent mutation rejections;
- 7,821 measured strings retained as preserve-unmapped evidence.

The report-structure check requires this file to exceed 12,000 bytes, contain exactly one authority fence, and name the recommendation and all three finding severities. That check is run after the final report edit.

## Residual risk and conclusion

The source profile is aggregate evidence, not raw-record reinspection in this packet. That is intentional: the authority binds the measured profile, completion manifest, and taxonomy bytes, and does not broaden the evidence class. The semantic rule remains conservative under that evidence. It emits only strict integer pairs present in the frozen taxonomy and retains everything else.

No unresolved ambiguity permits a string-to-integer coercion, boolean admission, label lookup, pair-free subevent admission, unknown-pair guess, raw-evidence loss, canonical-field collision, predecessor drift, digest substitution, actor self-review, backdated review, premature acceptance, or downstream path creation.

On the reviewed bytes and fixed evidence, the W04 field-semantic v2 authority is complete, closed, deterministic, independently reconstructable, mutation-resistant, and progression-safe within the corrected accepted R21 graph above. Recommendation: PASS with zero P0-P2 findings.
