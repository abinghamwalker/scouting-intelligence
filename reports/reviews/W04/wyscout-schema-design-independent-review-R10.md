# W04 Wyscout schema design independent review R10

## Decision

**REWORK. Do not begin the W04 implementation graph from R16.**

R16 truthfully corrects the logical-launch defect returned by independent R9.
Normal resolution of the visible literal `uv` token through the exact closed
`PATH` selects `/opt/homebrew/bin/uv`; uv 0.9.21 preserves that logical spelling
in `UV` while incrementing `UV_RUN_RECURSION_DEPTH` and prepending the venv bin
directory. The exact 29-name outer map and both exact 32-name child maps were
reproduced. The logical entry is one symlink with the exact 26-byte raw target
`../Cellar/uv/0.9.21/bin/uv`, which takes one contained hop to the admitted
regular physical file. That final file has the required mode, size, digest, and
version. A negative control also proves that direct physical execution changes
`UV` to the forbidden Cellar spelling. R16 therefore closes the R9 launch-spelling
defect without accepting either spelling or using post-hoc `realpath`
normalization.

The complete 3,322-line standalone design nevertheless has two P1 defects:

1. R16's non-negotiable invariant says stable environment identity contains no
   host path, but the stable code/environment manifest, target record,
   environment digest, code-manifest identity, and therefore build identity now
   bind the absolute host paths `/opt/homebrew/bin/uv` and
   `/opt/homebrew/Cellar/uv/0.9.21/bin/uv`. The document explicitly calls both
   paths stable. This is a direct stable/operational classification contradiction,
   not merely an operational receipt detail.
2. R16 calls itself standalone and says earlier field-semantics closures are
   retained without compression, but its first field decision/review/acceptance
   route only names four future artifacts and states high-level behavior. R16
   does not provide the exact closed decision, registry, independent-review, or
   acceptance schemas; their artifact IDs and version rules; digest preimages and
   canonicalization; exact clock fields and bindings; candidate/review/acceptance
   equality rules; or exact task IDs/owners. The generic downstream seven-field
   authority row cannot create those missing upstream authorities. Implementing
   the first route would require consulting superseded prose or inventing
   normative structure.

No P0 defect was found. No other P1 or P2 defect was found after the complete
source, rights, temporal, identity, football-product, coverage, quarantine,
serializer, environment, resource, executable, bytecode, ownership, gate,
two-root, and two-local-commit design was read back and challenged. Both findings
have bounded design-only corrections. Neither requires provider access,
dependency or lock change, network, cloud, deployment, container, Git,
architecture, storage-root, or local-only policy change.

## Review boundary and method

The independent review read and challenged the complete R16 artifact, not only
its correction summary. It also read the complete R15-to-R16 delta, the producer
packet and master review/verification for R16, the independent R9 artifact and
its master review/verification, the accepted source profile, the current evidence
contract and threat model, `pyproject.toml`, `uv.lock`, both controlling HTML
plans, `AGENTS.md`, and the return template. R16 is exactly 3,322 lines and
185,625 bytes with SHA-256:

```text
c36eaca5ed2d803ae495e26d24413f6a86baf60e7732f24770a2e9f59787386d
```

R15 is 179,095 bytes with SHA-256:

```text
bf448cfc8478515dab760d119f6b89509e576fc24cfc44e3de473202224ae73e
```

The complete delta is confined to the R9 correction and corresponding version,
environment, stable-manifest, verification, and lineage language. Passing R15
projection, dependency, result-schema, packaging, executable, pyc, source, and
product text remains present in R16. R16 does not retroactively call the R9
`REWORK` decision accepted and does not self-approve.

Material current-environment and schema claims were reproduced read-only. No
provider object was parsed for this review, no excluded source path was opened,
and no provider acquisition, network request, download, dependency resolution,
sync, installation, cleanup, migration, product implementation, prefix creation,
data mutation, environment repair, cloud action, deployment, or Git operation
was performed. The three future implementation entry points remain absent:

```text
scripts/launch_wyscout_v5.py             absent
scripts/admit_wyscout_v5_runtime.py      absent
scripts/rebuild_wyscout_v5.py            absent
```

The only authored paths are this review and its assigned return. This verdict is
independent of the producer and master decisions.

## Ranked findings

### P1-01 — absolute host paths enter stable environment and build identity despite the invariant forbidding them

R16 Section 1 invariant 7 is categorical:

```text
Bronze, Silver, Gold, semantic manifests, stable environment identity,
and semantic proofs contain no ... host path ...
```

The R16 correction then makes the following bootstrap values explicitly stable:

```text
uv_logical_launch_path = /opt/homebrew/bin/uv
uv_physical_path =
  /opt/homebrew/Cellar/uv/0.9.21/bin/uv
```

Section 8.0.2 says the logical link path, raw target, exact one-hop
relationship, final physical path, mode, size, digest, and version are stable.
Section 8.1's stable target record binds the exact logical launch path and exact
final physical path. Section 8.9's `stable code/environment manifest` expressly
contains the exact `/opt/homebrew/bin/uv` logical path and equality to the
admitted physical uv path. Its exclusion paragraph says the stable one-hop
authority and exact final physical identity are retained even though operational
paths are otherwise excluded.

This classification propagates into identity:

1. `local_launcher_control_digest` binds the exact
   logical-link-to-physical tuple.
2. `process_launch_contract_digest` binds normal selection of only the exact
   logical path and denials of alternate paths.
3. `environment_values_digest` binds the sole logical launch-path substitution.
4. Those components enter `environment_digest`.
5. The canonical code/environment manifest contains those components and obtains
   `code_manifest_sha256` and `code_manifest_id`.
6. The stable pre-build projection contains both the code-manifest identity and
   `environment_digest`.
7. Its sole SHA-256 is the W04 `build_id`.

The absolute Homebrew paths are therefore not confined to an operational
admission receipt. Changing only the host installation prefix or Cellar path
changes stable environment identity, the immutable code manifest, and build
identity even if the admitted uv bytes, version, mode, link relationship, lock,
repository code, source evidence, and product semantics are identical.

The normalized environment-map value does not resolve the contradiction.
`<W04_UV_LOGICAL_LAUNCH_PATH>` replaces the actual `UV` value only inside the
normalized map. The stable bootstrap tuple and stable target record separately
retain both absolute paths, and Section 8.9 explicitly includes them.

This is P1 because the contradiction affects the sole admitted stable
environment identity and sole build-ID preimage. An implementer cannot both:

- obey invariant 7 and omit every host path from stable identity; and
- obey Sections 8.0.2, 8.1, 8.9, and 9 and include the two exact absolute paths
  in stable components.

Silently choosing one side changes a non-negotiable identity rule. It also makes
the claimed root-independent stable/operational boundary ambiguous. The
current-host launch proof still passes; the defect is the classification and its
transitive identity effect.

#### Bounded required correction

A standalone R17 must choose one coherent rule and apply it everywhere:

- keep invariant 7 and classify the actual absolute logical and physical
  spellings as operational admission controls while stable identity binds a
  root-independent logical-launch role, exact raw link relationship, admitted
  physical bytes/version/mode/size/digest, and deterministic normalization; or
- explicitly narrow invariant 7 with one precise, reviewed exception for this uv
  installation coordinate and explain how that exception participates in the
  two-root proof and why other host paths remain forbidden.

Whichever rule is selected must be applied consistently to the bootstrap tuple,
stable target record, code/environment manifest, component digest preimages,
projection exclusions, two-root proof, negative tests, and verification matrix.
The normal literal launch, exact logical `UV` value, constructive one-hop proof,
direct-physical denial, and rejection of alternate/either spellings must remain.
No implementation may decide this classification implicitly.

Acceptance evidence must mechanically show that the stable manifest contains
exactly the path representation authorized by the corrected invariant and that
changing only an operational host spelling has the documented effect, or no
effect, on `environment_digest`, `code_manifest_sha256`, and `build_id`.

### P1-02 — the first field-semantics authority is not a standalone implementable contract

R16 says it replaces R15 in full and retains earlier closures “without
compression or substitution.” It also states that implementation begins only
after the standalone design is accepted. The first authority work in the exact
ownership sequence is the field-semantics route, before Bronze.

R16 Section 4.1 names these paths:

```text
reports/reviews/W04/authorities/
  wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
reports/reviews/W04/authorities/
  wyscout-field-semantic-independent-review-R1.md
reports/reviews/W04/authorities/
  wyscout-field-semantic-acceptance-v1.json
```

It says the authority binds the completion/profile, two taxonomy-map digests,
and every `(record_kind,json_path)`. It defines the three decision outcomes
`TRANSFORM`, `PRESERVE_UNMAPPED`, and `FORBIDDEN`; requires unknown fields to be
`UNMAPPED`; rejects unknown envelope kinds; and forbids runtime label matching
and provider-native semantic claims. Those are useful semantic constraints, but
they are not the closed artifact contracts needed to create and independently
verify the first accepted authority.

Within R16 itself, the following normative data is absent:

1. The exact top-level key set, JSON types, nullability, grammars, and ordering
   for `wyscout-field-semantic-decisions-v1.json`.
2. The exact row key set and value schema for one
   `(record_kind,json_path)` decision, including how paths, transform identifiers,
   reasons, source evidence, and exhaustive field coverage are represented.
3. The exact YAML document/row schema for the field registry, including schema
   version, field ordering, duplicate handling, allowed transform parameters,
   canonical parsed representation, and the equality relationship to every
   decision row.
4. The exact independent-review artifact contract. A Markdown filename and the
   generic statement “reviewer cannot edit the candidate” do not specify review
   ID, reviewed candidate ID/digest, recommendation grammar, finding set, reviewer
   identity, review clock, or canonical review digest authority.
5. The exact acceptance JSON contract: acceptance ID, schema version, accepted
   candidate/registry/review IDs and digests, accepting actor, accepted clock,
   required `PASS` equality, and fail-closed cross-field checks.
6. Exact artifact-ID algorithms and their namespaces/preimages. R16 later
   requires `candidate_id`, `review_id`, and `acceptance_id`, but never defines
   how the first field artifacts acquire those IDs or whether each is a UUID or
   fixed string.
7. Exact digest rules for candidate, registry, review, and acceptance, including
   which physical/canonical bytes are hashed and whether any self ID/digest,
   path, actor, or clock is excluded.
8. Exact field names and types for `decided_at`, `reviewed_at`, and
   `accepted_at`, and their equality with the field dependency's `observed_at`
   and `available_at`. The high-level inequality
   `decided_at <= reviewed_at <= accepted_at` does not define where those values
   live or which bytes bind them.
9. The exact `feature_schema` dependency UUIDv5 namespace and canonical preimage.
   Section 5 only says it is “over artifact type, fixed artifact ID, artifact
   digest, and acceptance digest”; it does not define the namespace, field
   framing, encoding, or ordering.
10. Exact packet IDs and bounded path ownership for the decision, review, and
    acceptance tasks. The ownership table gives only generic rows `2–4` as
    “field decision/review/accept packets,” unlike the exact task IDs supplied
    later for supported-feature registry work.

The later `authority_rows` schema does not fill this gap. It defines exactly
seven downstream strings:

```text
acceptance_id
acceptance_sha256
authority_kind
candidate_id
candidate_sha256
review_id
review_sha256
```

That is a reference row for already accepted artifacts. It does not define the
four upstream artifact schemas, does not include the registry as a separately
identified/digested field, and cannot establish which candidate digest includes
or binds registry bytes. Likewise, the 17-resource allowlist states that each
resource binds path, physical digest, size, mode, purpose, parser/schema version,
and authority link, but it does not define those field-authority artifact
schemas or values.

The gap is observable from R16 alone. Section 4.1 contains paths and behavioral
prose, while the document provides exhaustive key/type tables for child
envelopes, child results, rebuild invocation, and build projection. There is no
corresponding exact field decision, registry, review, or acceptance table. The
ownership sequence assigns generic packet classes rather than exact packets.
The document's assertion that earlier closure is retained cannot substitute for
normative text in a document that replaces earlier revisions in full.

This is P1 because rows 2–4 precede Bronze and are required dependencies of every
later field, feature, temporal, manifest, and build proof. A bounded subagent
cannot implement the first packet from R16 without making choices about IDs,
canonical bytes, clocks, review binding, and accepted registry equality. A
reviewer cannot independently prove an artifact against an absent schema, and
the master cannot construct the five-field `EvidenceDependency` or downstream
authority row deterministically. Importing unstated rules from R4/R5 would
contradict the standalone replacement claim and would make superseded text
silently normative.

#### Bounded required correction

A standalone R17 must include, rather than cite by lineage, the exact first
field-semantics authority protocol:

- closed decision JSON schema and exhaustive decision-row schema;
- closed registry YAML schema plus exact parsed canonical representation;
- closed independent-review artifact schema;
- closed acceptance JSON schema;
- schema/version literals, ID namespaces/preimages, digest inputs and
  canonicalization for all four artifacts;
- exact clock fields, actor fields, ordering, and dependency-clock bindings;
- exact candidate/registry/review/acceptance cross-equalities and `PASS` rule;
- the exact construction of the field `EvidenceDependency` and downstream
  seven-field authority row; and
- exact decision, independent-review, and master-acceptance task IDs with
  disjoint allowed paths and no self-approval.

It must also state whether the candidate digest directly includes canonical
registry bytes or carries a separate registry digest, and then bind that choice
without ambiguity through the acceptance, resource row, dependency digest, and
build projection. Tests must reject missing/extra keys, duplicate decisions,
uncovered profiled paths, registry/candidate drift, review of the wrong
candidate, acceptance of non-`PASS`, clock or actor mismatch, digest/ID mismatch,
and a reviewer-authored candidate change.

The same standalone standard should be checked for possession, identity, and
supported-feature authorities because R16 claims all four routes are retained.
The first field route is already sufficient to return the design: it is the
earliest implementation packet and proves the standalone claim false as written.

## Passing R15-to-R16 logical uv correction

The following current-host observations independently reproduce R16:

```text
normal command resolution:
  /opt/homebrew/bin/uv

logical lstat:
  kind = symlink
  mode = 0o755
  size = 26

uninterpreted readlink bytes:
  ../Cellar/uv/0.9.21/bin/uv
  byte length = 26

one relative contained hop:
  /opt/homebrew/Cellar/uv/0.9.21/bin/uv

final lstat/stat:
  kind = regular non-symlink
  mode = 0o555
  size = 41,617,552
  link count = 1

physical SHA-256:
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f

version through the logical command:
  uv 0.9.21 (Homebrew 2025-12-30)
```

The raw target resolves relative to `/opt/homebrew/bin`, remains within
`/opt/homebrew`, and ends after exactly one symlink hop at the same admitted
physical bytes. The final target is not itself a symlink. The current path does
not require an alternate link, cycle, escape, or extra hop.

### Exact outer transformation

A complete `env -i` probe supplied the exact twenty stable literal values, the
nine normalized values, `UV_RUN_RECURSION_DEPTH="0"`, the non-venv input `PATH`,
and literal:

```text
UV=/opt/homebrew/bin/uv
```

It invoked the visible literal command:

```text
uv run --locked --no-sync python -S -B -c <observation>
```

The Python first-instruction observation contained exactly 29 names and:

```json
{
  "UV": "/opt/homebrew/bin/uv",
  "UV_RUN_RECURSION_DEPTH": "1",
  "PATH": "<project-root>/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
}
```

Every other supplied value was preserved. There was exactly one venv-bin prefix.
No physical Cellar spelling appeared in `UV`.

### Exact child transformations

Separate complete closed probes for `PRE_BUILD_ADMISSION` and
`POST_BUILD_ID_REBUILD` each supplied the twenty literals, eight normalized
values, and four role/bootstrap values. Each child first-instruction observation
had exactly 32 names and the correct role. Both had:

```json
{
  "UV": "/opt/homebrew/bin/uv",
  "UV_RUN_RECURSION_DEPTH": "1",
  "PATH": "<project-root>/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
}
```

The role, source descriptor decimal, distinct result descriptor decimal, nonce,
and role-specific prefix values were present. The outer-only launcher descriptor
and bootstrap tuple were absent. `W04_CHILD_INPUT_B64` was intentionally absent
from the base map before its one post-digest insertion.

### Negative direct-physical control

Executing the physical path directly with the same logical input `UV` produced:

```text
UV=/opt/homebrew/Cellar/uv/0.9.21/bin/uv
UV_RUN_RECURSION_DEPTH=1
```

That observation demonstrates why the direct physical exec target must remain
forbidden and why logical and physical spellings cannot be accepted
interchangeably. R16's negative rule is testable and correct.

### Versioned contract closure

R16 contains the corrected algorithms:

```text
w04-local-control-bootstrap-v3
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
w04-code-environment-admission-v13
```

The superseded `v2`, `v1`, `v1`, and `v12` spellings for those respective
contracts are absent. `<W04_UV_PHYSICAL_PATH>` is absent and the sole
`<W04_UV_LOGICAL_LAUNCH_PATH>` token is used across outer and child
normalization. The three ordered argv arrays remain exact eight-token
locked/no-sync/no-site invocations with literal `uv`, `python`, `-S`, and `-B`.

Subject to P1-01's stable/operational classification, the R9 correction passes.

## Projection, invocation, and build-ID review

Mechanical extraction of the Section 9 projection and Section 8.0.5 rebuild
invocation produced:

```text
pre-build projection:
  25 keys
  25 unique
  already in Unicode code-point order

post-hash rebuild invocation:
  25 keys
  25 unique

intersection:
  24 keys

projection-only:
  schema_version

invocation-only:
  build_id
```

Removing only projection `schema_version` and invocation `build_id` yields equal
key sets. R16 requires the remaining 24 values to be copied byte-for-byte, not
recomputed or normalized. `build_id` is one SHA-256 of canonical bytes of the
complete 25-key projection. Only after that digest exists is the 25-key
invocation constructed.

The rebuild child removes only `build_id`, inserts only
`schema_version="w04-wyscout-pre-build-projection-v1"`, retains the 24 common
values, canonical-encodes, and performs the same one SHA-256. Completed
projection/invocation instances, run IDs, prefixes, descriptors, nonces,
diagnostics, transport hashes, clocks, output digests, and Git state are excluded
from the preimage. No placeholder, fixed point, second build algorithm,
completed-instance self-dependency, or post-hash path entered the projection.

Mechanical table extraction also reproduced unique cardinalities:

```text
common child input envelope: 16 / 16
admission inputs:              8 / 8
rebuild inputs:               10 / 10
rebuild invocation:           25 / 25
```

The three layer paths are ordered Bronze, Silver, Gold. The source/result
descriptor, nonce, role, argv, environment, prefix, code, manifest, layer,
receipt, and final-recheck equalities remain exhaustive. The result frame remains
bounded by exact magic, version, 1..16,777,216 payload length, canonical UTF-8
JSON, raw payload SHA-256, and EOF. Stdout and stderr are distinct operational
pipes capped at 1,048,576 bytes each, and the one 21,600-second monotonic deadline
is not reset.

Subject to P1-01's environment component and P1-02's upstream authority creation,
the projection/invocation cycle correction passes.

## EvidenceDependency and temporal review

The current accepted model was imported through locked/no-sync uv and reproduced
with exact fields:

```text
kind
dependency_id
digest
observed_at
available_at
```

The canonical sample JSON retained exactly those five keys. The existing
`DependencyKind` wire values are, in enum order:

```text
source_manifest
identity_evidence
feature_schema
model_artifact
retrieval_index
```

The report-local aliases `dependency_kind`, `manifest_id`, and
`manifest_sha256` were each rejected as extra fields. R16 uses one
`source_manifest`, one `identity_evidence`, and three distinct
`feature_schema` dependencies. It preserves the exact canonical ordering by enum
rank, UUID bytes, digest, observed clock, and available clock.

The source release, decision/review/acceptance availability, strict
`observed_at < feature_cutoff_ts`, strict
`available_at < feature_cutoff_ts`, strict watermark-before-cutoff, watermark as
the exact maximum availability, and canonical ordered-lineage SHA-256 rules are
present. Equality with the cutoff fails. Source validity and project
knowability remain separate, and no acceptance clock is backdated to release.

P1-02 prevents deterministic construction of the field dependency's artifact
identity/digest/clocks from R16 alone. Apart from that upstream schema gap, R16
uses the accepted five-field model directly and introduces no adapter or alias.

## Locked/no-sync, descriptor, packaging, executable, and bytecode evidence

The exact `uv run --locked --no-sync python -S -B` probe reported:

```text
site imported: false
sys.flags.no_site: 1
sys.dont_write_bytecode: true
```

Its `sys.path` contained only the empty invocation entry and the admitted
Python 3.12.12 standard-library roots; site-packages was absent. A descriptor
opened at offset zero and inherited as descriptor 9 through the exact uv launch
arrived regular, inheritable, and with `FD_CLOEXEC` clear. Positional reading
preserved offset zero and reproduced the source size and digest. This positively
supports the required source-descriptor transport; a direct-python shortcut was
not used.

### Lock and installed closure

The platform-selected lock set and installed dist-info set each contained 82
normalized name/version rows including the editable root. Their set difference
was empty. The lock's additional `colorama==0.4.6` row is guarded by
`sys_platform == 'win32'` and is not selected on the admitted macOS platform.
The editable root is the unique `scouting-intelligence==0.1.0` lock row with
source `{editable = "."}`.

### Packaging bootstrap and three denied `.pth` classes

The installed Packaging distribution is exactly `packaging==26.2` with its
verified package directory and dist-info/RECORD. The no-site launch does not
import it implicitly. R16 retains the byte-admit-first bootstrap, exact
`packaging.tags.sys_tags()` one-time selector freeze, restricted manual
site-root insertion, origin equality, audit proof, and later equality with the
full `L == I` admission.

Exactly three site-root `.pth` files remain:

```text
_virtualenv.pth
a1_coverage.pth
scouting_intelligence.pth
```

They represent the uv bootstrap import, conditional coverage import, and
root-bearing editable source path. All are excluded by `-S` and are denied as
authority until their respective explicit verification. The editable
`direct_url.json` is present and states the exact root-bearing editable file URL;
R16 correctly treats its actual root spelling as operational and uses normalized
stable evidence.

### Complete executable and interpreter closure

Parsing every installed dist-info RECORD row beginning `../../../bin/`
reproduced:

```text
total rows: 35
distinct owners: 21
Class E: 33
Class P: 1
Class W: 1
```

All 33 class-E basenames are declared console/gui entry points of their owners.
The only non-entry-point pip row is `pip==26.1.2` `pip3.12`, correctly class P.
The only wheel-script row is `ruff==0.16.0` `ruff`, correctly class W and absent
from console/gui entry points. The `pip` and `pip3` rows remain E. The design
retains exact owner, target, wrapper template, shebang normalization, mode, size,
digest, collision, and no-read/no-execution rules.

The venv bin directory contains exactly three `python*` alias symlinks:

```text
python     -> /Users/adrian/.local/share/uv/python/
              cpython-3.12.12-macos-aarch64-none/bin/python3.12
python3    -> python
python3.12 -> python
```

Their lstat identities are distinct. Both relative links remain contained and
all three resolve to the same regular physical Python file with:

```text
mode: 0o755
size: 49,968
SHA-256:
  cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79
```

The exact three-alias topology, canonical wrapper `python` role, physical
interpreter/libpython/loader/stdlib closure, and root-independent stable
normalization remain specified.

### Source-complete pyc authority

The current operational census still reproduces:

```text
site pyc files:       1,075
repository pyc files:    58
repository cache dirs:   19
pytest-tagged site pycs: 112
```

The repository has exactly the three present source-absent inert orphan rows
named by R16:

```text
migrations/__pycache__/env.cpython-312.pyc
migrations/versions/__pycache__/0001_foundation.cpython-312.pyc
src/scouting/storage/__pycache__/postgres.cpython-312.pyc
```

Each is a regular mode-`0o644` file and each corresponding `.py` sibling remains
absent. The site `six.cpython-312.pyc` optional orphan and exact uv bootstrap pyc
are present as observed. R16 builds stable authority from every admitted source
irrespective of pyc presence, classifies actual pyc only as operational state,
forbids reads/imports/cleanup/mutation, and permits another root to omit any
optional orphan or have different mapped pyc paths/counts without changing stable
source authority.

The packaging, `.pth`, executable, alias, and pyc design passes subject only to
P1-01's separate uv host-path classification.

## Source, rights, identity, product, coverage, quarantine, and publication review

The completion file still has exact size 6,803 and SHA-256:

```text
69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1
```

The accepted source profile SHA-256 is:

```text
569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649
```

R16 retains the exact completion-first, contained, regular, non-symlink,
size-and-digest-checked source seam. Direct objects are the five named object
files; the five match and five event archive members are exact, and the ZIPs are
hash evidence only. Directory scanning, fallback extraction, aliases, and reads
of the four excluded directory-only scopes remain forbidden.

The provider payload cannot select record family. The strict project envelope
owns the exact seven kinds:

```text
competition
team
player
event-taxonomy
tag-taxonomy
match
action
```

Absent, null, non-string, safe unknown, and unsafe unknown envelope
discriminators go only to the fixed unknown rejected-record family. Payload
`kind`, names, labels, taxonomy IDs, table shape, and filename are not dispatch
authority. Provider event `id` and taxonomy `eventId` remain distinct.

The exact 18-row source evidence table, restricted rights classification,
attribution, no export, six-dimensional source coverage, and separation from
Gold coverage remain closed. The five match/event partitions, row counts,
digests, partition alignment, and scope exclusion dimensions are explicit.

The design retains:

- strict `Decimal` number parsing and period-relative action occurrence;
- no invented half-time, continuous, terminal, UTC, elapsed-minute, per-90, or
  unsupported denominator evidence;
- canonical UUID identities based only on admitted numeric source keys;
- zero-player exclusion and fail-closed duplicates/conflicts/missing masters;
- four-kind identity state, queue, bundles, accepted corrections, versioning,
  history, and later availability;
- exact Bronze, Silver, and neutral Gold keys and product paths;
- named serializers, stable schemas, boundary receipts, manifests, and
  reconciliation equations;
- separate six-dimensional source and six-dimensional Gold coverage;
- unsupported/suppressed/unavailable feature states instead of invented values;
- strict temporal evidence and neutral role context;
- known-field rejection and unknown-record quarantine without promotion;
- staged writes, fsync/rename/publication checks, immutable final outputs, and
  no serializer bypass.

P1-02 means the first field authority needed by those consumers is not yet
constructible from the standalone text. The product and source contracts
themselves have no additional P0-P2 defect.

## Resources, ownership, gate, and local ledger

Mechanical readback reproduced exactly 17 local-resource paths: four registries,
twelve decision/review/acceptance artifacts, and the source profile. There is no
directory shorthand or eighteenth resource. Each path remains disjoint from
strict source, identity runtime, runtime admission, parent products, and outputs.

The serial ownership graph preserves distinct authority candidate, independent
review, and master acceptance owners; disjoint Bronze/Silver/Gold/product writers;
the launcher's sole code-manifest and build-ID authority; admission's
constructor-only role; rebuild's invocation-receipt role; and serializer-specific
product ownership. Runtime, health, card, independent rebuild, quality, master
verification, and gate checks precede acceptance.

The full `G-W04` gate retains source/rights, identity, reconciliation, strict
temporal, environment, no-site/Packaging, editable-root, executable, bytecode,
quarantine, manifest, card, independent review, exact path, resource, and
deterministic rebuild requirements. Every independent recommendation must be
`PASS`.

The local checkpoint sequence remains two distinct commits: the acceptance
integration commit and annotated tag only after the full gate, followed by a
separate local registry/checkpoint ledger commit and clean-tree proof. No remote,
hosted CI, cloud, endpoint, deployment, or provider access is introduced.

The ownership table's generic field packets are part of P1-02. Apart from those
missing exact first-route packet identities/contracts, the later ownership, gate,
and ledger sequence passes.

## Required rework and gate condition

R16 cannot be accepted while P1-01 and P1-02 remain. Dispatch one bounded
standalone R17 design correction that:

1. makes the uv logical/physical path stable-versus-operational classification
   coherent with invariant 7 and every transitive identity/digest use; and
2. embeds the exact first field-semantics decision, registry, independent-review,
   acceptance, clock, ID/digest, dependency, and task-ownership contracts needed
   to implement rows 2–4 without superseded prose or invention.

R17 must preserve the passing R16 logical launch proof, 29/32 maps, direct
physical denial, algorithm bumps, 25/25 projection, five-field
`EvidenceDependency`, no-site/descriptor/result contracts, packaging and
`L == I`, 35-row executable census, three aliases, source-complete pyc authority,
17 resources, source/rights/product/coverage/quarantine/publication rules, sole
writers, full gate, two-root proof, and two-local-commit ledger.

After master reproduction, a separate independent reviewer must re-read the
complete standalone replacement and rerun the exact launcher and schema
challenges. No W04 implementation packet should be dispatched until both
findings are closed and the independent verdict is `PASS`.

