# Wyscout schema design independent review — R4

## Decision

**REWORK. Do not dispatch the R5 implementation graph.**

R5 closes substantial parts of the four R4 P1 defects, and it retains the accepted
source, football-product, temporal-adapter, and coverage decisions. It is nevertheless
not ready for W04 implementation or `G-W04`. Seven independently substantiated P1
defects remain:

1. the new `data/identity/...` runtime family is outside every declared generated or
   committed local root and is not ignored by the repository's enumerated ignore
   rules;
2. the offline executable-admission algorithm requires lock-named wheel archive bytes
   that the current uv cache does not contain and that no packet owns acquiring;
3. the supported-feature registry is a behavior-affecting semantic authority without
   an independent decision/review/acceptance route or a truthful temporal dependency;
4. mandatory unresolved and rejected identity rows have no defined
   `IdentityMatchMethod`;
5. Bronze, Silver, Gold, rejected-field/quarantine, and boundary-receipt runtime paths
   are not exact despite the graph's claim of exact ownership; and
6. registry/checkpoint/clean-tree order contradicts the controlling workflow; and
7. the correction schema requires a queue item even when correcting an accepted
   resolved identity that never entered the unresolved queue.

No P0 defect was found. No separate P2 defect is reported: each issue above can make
the build unavailable, temporally false, locally ungoverned, or multi-interpretation,
so each is P1. The packet definition of done and stop conditions require REWORK when
any P0–P2 local-only, executable-truth, temporal, identity, ownership, or gate defect
remains.

This review used no Git operation, no delegation, no provider or network access, and
made no architecture, dependency, configuration, data, migration, or source change.

## Scope and authority

The review read every `read_first` authority in
`orchestration/task_packets/W04-SCHEMA-DESIGN-REVIEW-01-R4.yaml`, including the
standalone R5 design, the R4 master review, the prior independent review, the current
strict evidence and retrieval contracts, the W04 source card, and both controlling
HTML plans. It also challenged R5 against the existing local-only declaration,
repository ignore rules, local verifier skeleton, current uv cache shape, installed
distribution metadata, and root interpreter layout without modifying them.

The controlling requirements are material:

- W04.3/P2.3 requires all four identity kinds, a durable review queue, corrections,
  versioning, and fail-closed consumption.
- W04.5/P2.5 requires every behavior-affecting dependency to be strict-before cutoff.
- W04.2–W04.6/P2.2–P2.8 requires actual Bronze/Silver/Gold and health artifacts, not
  only their code and manifest names.
- `G-W04` requires all data to remain inside guarded local roots.
- The implementation workflow is controlling and says checkpoint accepted integration
  after the full gate, then update the registry and clean-tree proof.

## Ranked findings

### P1-01 — `data/identity/...` is outside the frozen local-only storage boundary and is unignored

R5 introduces three generated runtime families:

```text
data/identity/wyscout/v5/review-queues/<digest>.identity-review-queue.json
data/identity/wyscout/v5/bundles/<digest>.identity-bundle.json
data/identity/wyscout/v5/corrections/<id>.identity-correction.json
```

These are specified at R5 lines 377–426 and 490–500 and assigned to rows 14/14D at
lines 1151–1153. They are not within a declared local path. The exact
`configs/environments/local-only.yaml` declaration lists generated data only as
`data/source`, `data/reference`, and `data/working`; generated runs as `runs`; and
committed evidence as `data/manifests` and `reports` (lines 29–38). The W03 local
review environment and `scripts/verify_local_only.py` expected-directory skeleton
likewise enumerate `data/source`, `data/reference`, `data/working`,
`data/manifests`, and `runs`, but not `data/identity`.

The repository `.gitignore` is enumerated rather than a `data/**` catch-all. It ignores
only `data/source/*`, `data/reference/*`, `data/working/*`, and `runs/*` at lines
19–27. Therefore the proposed identity bundles, queues, and normalized corrections
have no project ignore rule. They contain restricted source identities, row references,
review dispositions, and canonical mappings and are generated runtime data, not
reviewed committed manifests.

This is not merely a missing directory. R5 says no local-only change is introduced,
the current review packet forbids `configs/**`, `scripts/**`, and `.gitignore` edits,
and no row in the ownership graph owns a boundary amendment. Implementing row 14 as
written would either write outside the declared guarded roots, fail guard
configuration, or leave restricted generated identity state eligible to appear as
untracked repository content. Any outcome violates `G-W04`.

**Exact correction required:** place queue/bundle/correction payloads under an
already-declared generated root, preferably an exact subtree of
`data/working/wyscout/v5/identity/`, and update every path, guard, reader category,
manifest reference, test, packet scope, and owner consistently. If the producer
instead wants a new `data/identity` root, R5 must declare a separately reviewed
local-only/configuration and ignore-rule amendment with exact owner and gate; it
cannot claim no boundary change.

### P1-02 — exact lock-wheel admission cannot execute offline from the present uv cache

R5 lines 825–839 require the admission task to select one compatible lock wheel and
then find the exact lock-named archive bytes by filename, SHA-256, and size inside
the read-only `uv cache dir`. The bytes must already exist; downloads and index
lookups are forbidden. Lines 847–864 then require parsing the wheel archive's
`RECORD` and comparing wheel members to installed files.

The local evidence contradicts the availability premise. The lock contains, among
other W04-relevant artifacts:

```text
pydantic-2.13.4-py3-none-any.whl
  sha256 45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba
  size 472262
pyarrow-23.0.1-cp312-cp312-macosx_12_0_arm64.whl
  sha256 f4b0dbfa124c0bb161f8b5ebb40f1a680b70279aa0c9901d44a2b5a20806039f
  size 34214575
pyyaml-6.0.3-cp312-cp312-macosx_11_0_arm64.whl
  sha256 fc09d0aa354569bc501d4e787133afc08552722d3ab34836a80547331bb5d4a0
  size 173973
```

A read-only search of `/Users/adrian/.cache/uv` found no `pydantic*.whl`,
`pyarrow*.whl`, `polars*.whl`, `packaging*.whl`, or `pyyaml*.whl`. The relevant
`wheels-v5` entries are symlinks to extracted `archive-v0` directories plus small
`.http`/`.msgpack` metadata files. For example,
`wheels-v5/pypi/pydantic/2.13.4-py3-none-any` resolves to an extracted directory and
its `.http` sidecar is 637 bytes; the lock wheel is 472,262 bytes. The corresponding
pyarrow entry is also a symlink to an extracted directory; its sidecar is 669 bytes,
not the 34,214,575-byte archive. An extracted member tree cannot reproduce or verify
the original ZIP-container byte hash.

The installed distributions do exist and have usable `RECORD` data, but installation
has added `INSTALLER` and `REQUESTED` entries to the installed `RECORD`. R5 allows
installer-generated metadata only when the exact filename and rule are enumerated in
the manifest schema, yet it does not enumerate those rules. That is an additional
multi-interpretation point inside the same admission defect.

The interpreter/stdlib portion itself survived the bounded challenge: the root venv
resolves to uv CPython 3.12.12, `libpython3.12.dylib` exists, and the resolved stdlib
tree produced no symlink or multiply-linked regular-file result. The defect is not a
general objection to executable closure; it is the unavailable wheel-archive premise
and incomplete generated-file rule needed by the exact algorithm R5 mandates.

No row in R5's graph owns materializing an immutable offline wheelhouse before code
admission. Row 25 cannot satisfy its own precondition, and the current review is
forbidden from downloading or changing dependencies.

**Exact correction required:** define one owned, pre-admission, local-only wheelhouse
artifact containing every selector-chosen lock wheel under an approved generated or
manifested root; bind exact filename/hash/size; prove it is populated before offline
admission; and make the wheelhouse path/retention/ignore status exact. Alternatively,
replace the archive-byte premise with a reviewed algorithm that admits uv's actual
extracted-cache representation without claiming verification of unavailable ZIP
bytes. In either case enumerate exact allowed generated metadata such as
`INSTALLER`/`REQUESTED`, its content rule, and installed-`RECORD` treatment. The
independent code-manifest review must reproduce the corrected algorithm.

### P1-03 — the supported-feature registry lacks semantic acceptance and temporal lineage

R5 lines 711–721 make
`configs/features/wyscout-v5-supported-count-features-v1.yaml` the normative
allowlist for every supported, suppressed, and unavailable feature. The registry
controls Gold applicability, the feature-schema hash (lines 628–636), the local
resource digest (lines 886–923), and the build identity (lines 999–1017). It is
therefore behavior-affecting semantic authority, not incidental configuration.

Unlike field, possession, and identity semantics, row 19 at line 1160 assigns only a
single master-authored registry/config/test packet. There is no decision artifact,
independent semantic review, master acceptance artifact, decision/review/acceptance
clock, or acceptance digest. The local-resource record nevertheless requires an
`authority link` (line 907), which this registry cannot supply.

The temporal omission is equally concrete. Section 7 lists source, identity, field,
and possession dependencies only. Section 9 requires exactly those dependencies while
including the supported-feature registry inside `feature_schema_hash`. A registry
authored after a historical cutoff can therefore alter what Gold emits without its
own `observed_at`/`available_at` being checked strict-before cutoff. Binding bytes in a
build hash proves identity, not knowability.

Post-Gold dataset-card and rebuild reviews cannot retroactively serve as independent
pre-use semantic acceptance: Gold has already consumed the registry, and those
reviews do not own its decisions.

**Exact correction required:** add serial master-decision, independent-review, and
master-acceptance packets and artifacts for the exact registry; bind the registry
bytes and all supported/suppressed definitions; record truthful ordered clocks and
digests; add the acceptance artifact to local resources and build identity; add the
accepted registry as an exact `feature_schema` dependency; update the proof's exact
dependency cardinality/order, watermark, tests, owners, and all cutoff-negative
cases. Gold must be blocked until registry acceptance.

### P1-04 — unresolved and rejected identity rows cannot be constructed without inventing `method`

The strict `W04IdentityCrosswalkRow` at R5 lines 284–317 requires
`method: existing IdentityMatchMethod` for every row. The existing enum has only
`exact`, `deterministic`, and `reviewed`
(`src/scouting/contracts/evidence.py` lines 153–158).

R5 exhaustively specifies `method=deterministic` only for initial resolved rows
(lines 353–357). It does not specify a method for initial `REVIEW_REQUIRED` rows or
the provider-zero `REJECTED` row (lines 358–362), even though the bundle must include
every referenced unresolved key. It similarly specifies `method=reviewed` for a
resolved correction but omits the method for a reviewed reject (lines 509–512).
Those rows have null canonical IDs and were not “linked to a canonical entity,” so
silently choosing any existing match method also changes the meaning of the enum.

The omission affects canonical row bytes, evidence digests, row UUIDs, bundle digest,
queue/bundle reconciliation, dependency ID, and build ID. Two conforming implementers
can choose different values; a fail-closed implementer cannot emit the mandatory
backlog at all.

**Exact correction required:** define a semantically valid method representation for
all four state transitions. Either extend the W04 row with an exact classification
method enum that includes unresolved/provider-rejected states while keeping the
existing `IdentityEvidence` projection unchanged, or state and justify an exact
existing enum value for every initial/corrected state. Bind it in the identity
ruleset decision/review/acceptance, digest rules, queue/bundle validators, and
positive/negative tests. No runtime implementer may choose it.

### P1-05 — required data products and quarantine evidence do not have exact output paths

R5 calls Section 15 an “ownership-complete graph” whose scopes are exact. They are not
exact for the central runtime products:

- row 13 names only “Bronze product” plus its manifest;
- rows 15A–15C, 16, and 17 name code/tests/returns but no Silver entity, action,
  lineup, possession, or player-match product paths;
- row 20 names Gold code, a Gold manifest, and unspecified “boundary receipts,” but
  no Gold data path or exact receipt path;
- row 27 grants the broad `data/working/wyscout/v5/**` runtime subtree; and
- R5 contains no rejected-field or quarantine artifact schema/path/owner at all.

This leaves W04.2/P2.2 raw preservation, field admission and quarantine incomplete and
does not establish collision-free sole writers for the physical Bronze/Silver/Gold
Parquet products required by W04.4–W04.6/P2.4–P2.7. Exact manifest paths do not locate
the payloads they describe. The broad row-27 glob cannot substitute for a product
contract and conflicts with the claim that every path has one owner.

The omission also makes two-empty-root relative-path equality under-specified: there
is no authoritative relative-path set to compare. A rebuild orchestrator can call
module writers, but that does not define where each writer writes.

**Exact correction required:** enumerate exact content-addressed roots and deterministic
relative-path formulas for raw-preserved Bronze, every Silver product, Gold partitions,
rejected/quarantined records and fields, temporal boundary receipts, and layer
manifests. Assign each runtime path family to exactly one serializer; constrain row 27
to invocation/receipts rather than a broad shared data subtree; define atomic
completion order and manifest-to-payload references; and add no-overlap/unknown-field
quarantine/two-root path tests.

### P1-06 — R5's registry/checkpoint order contradicts the controlling workflow

R5 row 34 updates `orchestration/phase_registry.yaml` before row 35 creates the
acceptance commit/tag, and row 35 says the commit occurs only after the accepted
registry update (lines 1175–1176). The controlling implementation workflow says the
opposite at line 1103: commit/tag after the full wave gate, **then** update the registry
and clean-tree proof. It also defines the phase registry as recording checkpoint
SHAs/tags.

R5 does not acknowledge or supersede that controlling sequence. Its row-32
clean-tree report is written before the gate, registry change, and checkpoint; row 35
then says “reruns clean-tree verification” without naming whether the committed report
is replaced, whether a second commit is required, or which commit the accepted tag
names. The current registry's W04 commit message also differs from R5's exact message,
so an exact registry mutation is required, not implied.

This is a gate-ledger defect: following R5 violates the controlling workflow, while
following the workflow violates R5's declared serial graph. The accepted registry,
clean-tree evidence, commit, and tag cannot all be identified from the standalone
design.

**Exact correction required:** choose the controlling order explicitly and amend R5
to match it. Define the pre-gate verification artifact, acceptance commit, annotated
tag, post-checkpoint registry mutation, checkpoint-SHA resolution rule, final
clean-tree proof, and whether a final ledger commit/tag update exists. Every emitted
artifact must name the exact checkpoint it verifies without self-referential commit
hash construction. The workflow/registry/design must agree before dispatch.

### P1-07 — the correction contract cannot supersede an accepted resolved identity

R5 says manual correction binds the prior row's old state and canonical ID and may
propose a new canonical ID or reviewed rejection. That necessarily includes the case
where a previously `RESOLVED` deterministic mapping is later found to be wrong.
However, the normalized correction schema at R5 lines 521–535 requires both
`prior_queue_sha256` and a non-null `queue_item_id`, and the next queue snapshot must
record the disposition. Initial resolved rows never enter the unresolved review
queue, and R5 defines no reviewed transition that first adds a resolved row to that
queue. Consequently a correction can normalize an already queued unresolved item,
but cannot construct the claimed versioned correction/supersession for a resolved
mapping.

This is not cured by retaining historical row digests. The correction bytes,
supersession edge, next bundle, dependency availability, and build identity all
depend on a normalized correction that the schema cannot represent. Allowing the
runtime owner to invent a queue item after acceptance would bypass the separately
reviewed correction decision and alter queue history.

**Exact correction required:** define two explicit reviewed correction routes:
queue-bound disposition for an existing unresolved item and direct supersession of a
current resolved row. Make queue identifiers nullable only for the direct route (or
define a separately reviewed immutable escalation snapshot before correction), bind
the exact route in decision/review/acceptance artifacts, and specify the resulting
queue transition, new crosswalk row, supersession edge, clocks, bundle regeneration,
and tests. Both routes must preserve prior bytes and advance availability.

## Four R4 P1 closure table

| R4 P1 defect | R5 result | Independent basis |
| --- | --- | --- |
| Identity clocks | **CLOSED narrowly** | Initial identity `valid_from` is separated from truthful ruleset `available_at`; decision observation and acceptance/correction watermark are distinct; equality to cutoff fails; corrections advance bundle digest/ID/lineage/build. |
| W04.3 identity lifecycle | **PARTIAL / REWORK** | Four kinds, states, queue, bundle, correction authority, immutable supersession and dependency-ID equality are strong, but mandatory unresolved/rejected rows and reviewed rejects have no exact `method`, accepted resolved rows cannot enter the mandatory queue-bound correction schema, and identity runtime paths violate local-only policy. |
| Runtime/phase ownership | **PARTIAL / REWORK** | Source manifest, identity templates, health, transformed card/review, independent rebuild, master/gate reports and master-only ledger work are named. Actual Bronze/Silver/Gold/quarantine/receipt paths are not exact, and checkpoint order conflicts with the controlling workflow. |
| Executable/resource closure | **PARTIAL / REWORK** | Selector, installed bytes, interpreter/libpython/stdlib, resource allowlist, non-circular digests and tamper tests are materially improved. Exact lock-wheel archive bytes are absent from the current uv cache, installer-generated rules are not enumerated, and the feature registry has no authority link. |

None of these partial results satisfies the packet definition of done.

## Six returned-defect closure table

| Returned defect | R5 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-CODE-CHECKPOINT-01` | **PARTIAL / REWORK** | Repository, installed runtime, interpreter/stdlib and local resources are designed in detail, but the required wheel archives are unavailable offline and no pre-admission owner exists. |
| `W04-DESIGN-SEMANTIC-TEMPORAL-BOUNDARY-01` | **CLOSED for identity; REWORK for retained global invariant** | The identity clock defect is closed and the adapter remains exact. The newly normative supported-feature registry is missing from dependency clocks, so the full Gold proof is still incomplete. |
| `W04-DESIGN-SEMANTIC-AUTHORITY-SOURCE-01` | **CLOSED** | Field and possession decisions retain exact independent review and acceptance, truthful clocks, unknown preservation, and project-derived possession labeling. |
| `W04-DESIGN-PACKET-GRAPH-01` | **PARTIAL / REWORK** | Many omitted review/health/card/gate owners were added, but physical data/quarantine/receipt paths and checkpoint sequence remain incomplete. |
| `W04-DESIGN-MANIFEST-FILE-COUNT-01` | **CLOSED** | Exact ordered completion + 7 objects + 10 archive members = 18 remains required. |
| `W04-DESIGN-SOURCE-COVERAGE-CONTRACT-01` | **CLOSED** | Strict source coverage remains field/type/count exact and separate from Gold coverage. |

## Retained closure table

| Previously accepted finding | R5 disposition |
| --- | --- |
| `W04-DESIGN-SOURCE-SEAM-01` | **RETAINED CLOSED** — only completion-declared direct/member bytes are admitted; ZIP/downstream and escape/symlink boundaries remain fail closed. |
| `W04-DESIGN-GOLD-GRAIN-01` | **RETAINED CLOSED** — deterministic neutral context/version remains in the exact key and UUID input. |
| `W04-DESIGN-MINUTES-01` | **RETAINED CLOSED** — nominal bounds/right-censoring remain explicit; elapsed minutes, exact minutes and per-90 remain suppressed. |
| `W04-DESIGN-COVERAGE-01` | **RETAINED CLOSED** — six integer numerator/denominator dimensions, zero-denominator rules, minimum overall and applicability ordering remain exact. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **RETAINED CLOSED AS ROW SCHEMA** — result independence, match-bound team, evidence counts/flags, proof and lineage remain exact; runtime dispatch is blocked by P1-01/P1-04/P1-05. |

## Original nine-finding disposition after R5

| Original finding | Disposition |
| --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | **CLOSED** — period-relative occurrence, Decimal ordering, null action UTC, match-only cutoff, identity decision/acceptance clocks and truthful generation adapter now agree. |
| `W04-DESIGN-SOURCE-SEAM-01` | **CLOSED** |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | **CLOSED** — non-circular IDs, tenant/classification, 18 rows and strict coverage agree. |
| `W04-DESIGN-REBUILD-CLOCK-01` | **PARTIAL / REWORK** — semantic/operational clock separation is correct, but exact offline executable admission cannot start without wheel archives. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | **CLOSED** |
| `W04-DESIGN-GOLD-GRAIN-01` | **CLOSED** |
| `W04-DESIGN-MINUTES-01` | **CLOSED** |
| `W04-DESIGN-COVERAGE-01` | **CLOSED** |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **CLOSED AS SCHEMA; IMPLEMENTATION BLOCKED** by the identity-row method, local-root, and runtime-path defects. |

## Boundary challenges that pass

The following material decisions remain acceptable and must not regress in R6:

- exact 18-row source manifest construction and literal strict `DataCoverage`;
- non-circular manifest, identity-bundle, dependency, code-manifest, and build IDs;
- conservative restricted-use classification, internal derivation/review, export
  denial, and attribution requirement;
- project-defined field and possession authority with independent review and master
  acceptance;
- immutable four-kind identity history, content-addressed queue/bundle,
  correction decision/review/acceptance, supersession edges, and equality of bundle
  external ID/dependency ID/build field;
- identity valid/availability clock separation and correction-driven watermark;
- period-relative action ordering without fabricated UTC, partial-match claim denial,
  result-independent facts, minute/per-90 suppression, neutral Gold context, and exact
  coverage equations;
- clock-free semantic proof plus one truthful serving generation clock;
- exact interpreter, loaded-libpython, and stdlib byte-enumeration concept on the
  observed root runtime; and
- distinct P2.8 machine/human health outputs, transformed P2.9 card, independent card
  review, independent two-root rebuild review, master verification, and machine
  `gate-report.json`.

These passing boundaries do not override any open P1.

## Required R6 acceptance gates

An R6 design can be accepted only if it:

1. moves identity runtime artifacts into an already-declared generated root or owns a
   separately reviewed local-only and ignore-boundary amendment;
2. replaces the unavailable uv-cache wheel premise with an offline artifact route
   that actually exists and has one pre-admission owner, including exact generated
   installed-metadata rules;
3. gives the supported-feature registry decision, independent review, master
   acceptance, authority link, truthful clocks, dependency lineage, and pre-Gold
   ordering;
4. defines identity `method` for every state and correction disposition without
   runtime invention;
5. makes both queued-item correction and direct resolved-row supersession exact,
   reviewed, immutable, and clocked without inventing a queue item;
6. enumerates exact non-overlapping payload, quarantine, and receipt paths and sole
   writers for Bronze/Silver/Gold;
7. reconciles registry, gate, acceptance commit, tag, and clean-tree sequencing with
   the controlling workflow;
8. retains every closure and pass listed above; and
9. obtains another independent read-only review before any implementation packet is
   dispatched.

## Recommendation

Return R5 for bounded R6 correction. The current graph must not be dispatched and
`G-W04` cannot pass as designed. No self-approval is granted.

## Packet verification

- `uv run python -c "from pathlib import Path;
  p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R4.md');
  assert p.is_file() and p.stat().st_size > 8000"`: exit `0`; report size
  `26,393` bytes at execution.
- `uv run python scripts/verify_local_only.py`: exit `0`; repository validator
  `PASS`, 25 checks passed, zero failures. This verifies the current repository
  state; it does not authorise R5's proposed undeclared `data/identity` root.
