# W04 build/receipt closure audit independent review R1

Date: 2026-07-31

Verdict: `REWORK`

Open findings: `P0=0`, `P1=3`, `P2=1`.

The predecessor audit is correct that accepted R20/R21 bytes do not authorize final
product publication: the exact 25-key projection and one-hash build algorithm are
implementable, but the concrete POC window/cutoff authority, product-authorized
aggregate bytes, and closed receipt-content schemas are not derivable from the
accepted bytes alone. A bounded user authorization is therefore genuinely required.

The proposed question is not yet sufficient, however. Its snapshot choice contradicts
a retained accepted temporal rule, its proposed schema aggregate does not expressly
bind every implemented schema required by R20, and its receipt-clock ordering remains
open. Those defects must be corrected before the question is put to the user or any
authoritative build/receipt implementation is dispatched.

## Fixed-binding verification

Every fixed input was verified before merits analysis.

| Binding | Expected SHA-256 | Observed | Result |
| --- | --- | --- | --- |
| closure audit | `2d0fd4c6a797c6f04879772075d068560ccbca23456cc559160eb259c5d7ef18` | same | PASS |
| R20 design | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` | same | PASS |
| R21 correction | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` | same | PASS |
| source-completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | same | PASS |

The two accepted v1 preimages were also reproduced as
`0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
and `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`.
The immutable source manifest reproduced as
`8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`.

## What accepted bytes do and do not close

### Already closed and implementable

- R20 fixes exactly 25 Unicode-code-point-ordered pre-build projection keys,
  `schema_version="w04-wyscout-pre-build-projection-v1"`, Section 8.0.6 canonical
  JSON, and exactly one `SHA256(canonical_json(projection))` build calculation.
- The post-hash invocation removes only projection `schema_version`, inserts only
  `build_id`, and copies the other 24 values unchanged. No 26th build key is needed
  by the bounded correction.
- R20 fixes receipt paths, sole writers, build/run/path equality requirements,
  the three-field child-result receipt summary, three ordered layer summaries, and
  the rule that receipt instances and clocks are operational rather than build
  inputs.
- The later accepted completion index is content addressed and binds source manifest
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b`, England member digest
  `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`,
  match `2499719`, and exact period populations `901` and `867` with membership
  digests `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`
  and `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`.

### Not derivable without a product/build decision

- R21's product preimage says `control_plane_only=true` and
  `product_bytes_forbidden=true`.
- Every one of R21's sixteen schema descriptors, including both receipts, has
  `surface_kind=CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`.
- R20/R21 contain no closed receipt-file key set, nullability, complete operational
  clock predicates, or canonical receipt-file encoding.
- R20 requires an exact accepted window and strict cutoff but supplies only types,
  inequalities, and projection positions. Concrete values in existing tests are
  fixtures, not invocation authority.
- The post-R21 completion-index digest is not an explicit member of R20's fixed
  projection. It must be committed through corrected existing aggregate values; a
  26th key is forbidden and unnecessary.

Using the v1 preimage digests as final-publication authority, omitting receipts,
treating the child result summary as receipt content, or inventing a fixture build ID
would contradict accepted bytes. There is no narrower accepted-byte-only route to
authoritative publication.

## Independent checks on the recommended bounded values

The proposed half-open window
`[2017-08-11T00:00:00Z, 2017-08-12T00:00:00Z)` contains the authentic selected match
at `2017-08-11T18:45:00Z`. A direct read of the verified England match member found
exactly one England match in that day: source match `2499719`, competition `364`,
season `181150`, teams `1609/1631`.

The proposed cutoff `2026-08-01T00:00:00Z` is strictly later than source acquisition
`2026-07-29T15:51:08.598589Z` and all current dependency-bound decision, review, and
acceptance clocks. The latest is identity acceptance at
`2026-07-31T14:15:26Z`. Equality is not used.

The proposed publication graph is acyclic in shape:

```text
product Parquet -> layer manifest -> temporal-boundary receipt(s)
  -> rebuild invocation receipt -> child result summary
```

No product or manifest points forward to a receipt; no receipt contains its own path
digest or content digest; the invocation receipt summarizes already closed boundary
receipts; and the child result hashes the already closed invocation receipt. Direct
SHA-256 of strict UTF-8 NFC Gold relative-path bytes is a non-recursive preimage for
the boundary filename.

## Findings

### P1 — Proposed snapshot authority contradicts retained accepted temporal semantics

The audit recommends `snapshot_as_of_ts=SOURCE_ACQUIRED_AT`. R20's opening merge
statement expressly retains every earlier passing temporal closure without
substitution. The retained W04 temporal proof rule in R4 Section 7 and restated in R5
requires `snapshot_as_of_ts` to equal the maximum selected match-start UTC, or the
single match-start UTC at player-match grain. R20 does not supersede that rule, and
R21 leaves temporal inequalities and non-replaced R20 clauses unchanged.

For this exact one-match proof the only conformant value is therefore:

```text
snapshot_as_of_ts = 2017-08-11T18:45:00Z
valid_from_ts = max(snapshot_as_of_ts, dependency_watermark)
```

Using source acquisition would misstate the semantic snapshot even though the later
identity watermark happens to leave the final `valid_from_ts` unchanged. Snapshot is
already derivable authority; it is not a new user choice.

### P1 — Proposed v2 schema aggregate does not close every implemented schema

R20 requires `schema_bundle_digest` to bind every already-authorized
Bronze/Silver/Gold/result/receipt schema. R21 deliberately labels all sixteen rows,
not only the two receipt rows, as descriptor-only and says those bytes do not prove an
implemented row schema or serializer exists.

The audit's proposed v2 aggregate explicitly adds the two receipt schemas while
retaining the descriptor-only v1 digest. That does not, by itself, content-bind the
exact implemented Bronze, Silver, Gold, layer-manifest, and result schemas that final
publication will use. Code-manifest coverage is a separate build input and cannot be
silently substituted for `schema_bundle_digest`.

The corrected authority must define an acyclic v2 schema-bundle preimage that binds
the immutable v1 descriptor digest plus canonical closed schema identities/digests for
every implemented product, manifest, result, and receipt surface required by R20. It
must be frozen and independently reviewed before its digest enters the unchanged
projection field.

### P1 — Boundary/invocation receipt clock ordering is still open

The recommended invocation receipt requires only `started_at <= completed_at`; the
boundary receipt independently carries `checked_at`. No proposed invariant requires
an accepted boundary receipt to have been checked during the invocation that later
summarizes it. Under the proposed text, `checked_at < started_at` or
`checked_at > completed_at` can remain schema-valid while all paths/digests agree.

The closed cross-receipt rule must be:

```text
for every summarized boundary receipt:
    invocation.started_at <= boundary.checked_at <= invocation.completed_at
```

The invocation reader must reopen the exact summarized boundary bytes, reproduce
their hashes/sizes/paths, and enforce this relation before writing its own canonical
receipt. These operational clocks stay excluded from build and product semantics.

### P2 — Window-definition preimage is not byte-exact yet

The audit gives a namespace and describes a closed object but does not enumerate the
object's exact key names, JSON types, and canonical wire values. Phrases such as
"accepted source-manifest ID" and "canonical match ID" admit more than one plausible
field name. The later authority packet must fix the exact five-key object, for example
`match_id`, `source_manifest_id`, `window_end_utc`, `window_schema_version`, and
`window_start_utc`, with the exact canonical UTC strings, before deriving the UUIDv5
name. It must also call the completion index by its existing content address/path and
digest rather than inventing a separate unapproved index-ID namespace.

## Required bounded rework

1. Amend the closure audit's recommended question/authority surface so snapshot is
   the exact selected match start, not source acquisition.
2. Require a complete canonical v2 schema bundle over every implemented R20 product,
   manifest, result, and receipt schema; retain the v1 descriptor digest as history.
3. Add the exact boundary-versus-invocation clock relation and readback predicate.
4. Enumerate the exact window-definition preimage keys and wire values.
5. Retain the otherwise sound values: one-day window, strict 2026-08-01 cutoff,
   accepted index/source/member/match/period binding, exact 25-key projection, and
   acyclic publication order.

After those corrections, the exact bounded user decision is to authorize the master
to freeze the additive product-authorized aggregates, concrete one-match window and
cutoff, and complete receipt schemas while preserving all R20/R21/index bytes. It is
not an architecture, provider, rights, dependency, storage, local-only, cloud,
container, endpoint, hosted-CI, deployment, or Git decision.

## Commands and results

- Complete `sed` reads of `AGENTS.md`, the packet, both predecessor audits, all
  4,516 R20 lines, all 1,254 R21 lines, all 3,256 `wyscout_data.py` lines, and the
  return template: exit `0`.
- `shasum -a 256` over all four fixed bindings, both v1 preimages, and the immutable
  source manifest: exit `0`; all expected digests reproduced.
- Bounded `rg` scan for receipt content classes/schema IDs across `src`, `scripts`,
  `tests`, `configs`, and accepted reports: exit `0` for report references; no
  executable receipt-content model or schema ID was found.
- `jq` extraction of the accepted England completion-index scope: exit `0`; exact
  member digest, `643150` member rows, match `2499719`, and `901/867` period rows and
  membership digests reproduced.
- `jq` read of the verified England match member for the proposed UTC day: exit `0`;
  exactly one match, authentic start `2017-08-11T18:45:00Z`.
- `jq`/`rg` extraction of all four accepted authority decision, review, and
  acceptance clocks: exit `0`; latest dependency-bound clock
  `2026-07-31T14:15:26Z`, strictly before the proposed cutoff.
- No Python helper, import, test, implementation, product, receipt, manifest, data,
  provider, network, Git, cloud, container, CI, remote, endpoint, or deployment
  action was performed.

## Review conclusion

User authorization remains genuinely necessary for final publication, and the
25-key/one-hash/index/acyclic strategy is sound. The current recommendation must be
returned for the bounded corrections above before it is presented as a sufficient
decision surface or used to dispatch downstream build/receipt implementation.
