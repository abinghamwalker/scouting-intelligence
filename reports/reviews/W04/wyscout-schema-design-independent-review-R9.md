# W04 Wyscout schema design independent review R9

## Decision

**REWORK. Do not begin the W04 implementation graph from R15.**

R15 closes the three defects returned from R14: it gives the stable pre-build
projection and post-hash rebuild invocation exact, non-recursive schemas; it uses
the accepted five-field `EvidenceDependency` wire object rather than report-local
aliases; and it truthfully records R13 and R14 as master-returned `REWORK`
revisions rather than accepted revisions. Mechanical comparison reproduced the
claimed 25/25 schemas, exactly 24 common stable values, projection-only
`schema_version`, and invocation-only `build_id`. No build-ID self-dependency,
placeholder, fixed point, second build algorithm, or operational value in the
preimage was found.

The complete 3,234-line standalone design nevertheless has one P1 defect in its
closed process environment. The visible, repeatedly mandated command resolution
of `uv run --locked --no-sync ...` through the design's exact `PATH` changes
`UV` to the Homebrew logical executable spelling:

```text
/opt/homebrew/bin/uv
```

R15 instead requires uv to change `UV` to the resolved physical Cellar spelling:

```text
/opt/homebrew/Cellar/uv/0.9.21/bin/uv
```

The mismatch was reproduced twice from a closed `env -i` map, including once with
literal `uv` command resolution. It persists even when the physical path is
supplied as the input value of `UV`, because uv overwrites it. It affects the
outer and both child expected environments, their canonical base digests, the
bootstrap tuple/envelope comparisons, and every first-instruction closed-map
check. Under the documented visible launch semantics, all three roles therefore
fail before admission, manifest construction, or build identity.

An additional control probe showed that uv produces the physical `UV` value when
the operating-system executable target is separately forced to the Cellar binary
while the visible `argv[0]` remains `uv`. That is a viable bounded correction, but
R15 does not specify this distinct exec target or make it part of the launch
authority. The implementation may not silently choose between that behavior and
the normal `PATH`-resolved behavior. R16 must either bind the separately admitted
physical exec target while preserving the exact visible argv, or truthfully
admit the logical symlink value and bind its no-follow/resolution relationship to
the already admitted physical uv bytes. It must update the outer and child map,
normalization token, digest/equality rules, negative tests, and two-root evidence
consistently.

No P0 defect was found. No other P1 or P2 defect was found. This correction does
not require a provider, rights, architecture, root, dependency, lock, storage,
network, cloud, container, Git, or local-only policy change.

## Review boundary and method

The independent review read and challenged the complete R15 design, its producer
packet and master candidate decision, the R14 design and master return, the R8
independent return and master reproduction, the complete source profile, accepted
evidence contract, threat model, `pyproject.toml`, `uv.lock`, both controlling HTML
plans, `AGENTS.md`, and the required return template. R15 is 179,095 bytes and has
SHA-256:

```text
bf448cfc8478515dab760d119f6b89509e576fc24cfc44e3de473202224ae73e
```

Material current-environment and schema claims were reproduced read-only. No
provider object, excluded archive member, or directory-only exclusion was opened.
No provider access, network request, download, dependency resolution, sync,
installation, cleanup, migration, product implementation, prefix creation, data
write, environment repair, cloud action, deployment, or Git operation was
performed. The only authored paths are this review and its task return.

The three design-stage scripts remain absent, as required:

```text
scripts/launch_wyscout_v5.py             absent
scripts/admit_wyscout_v5_runtime.py      absent
scripts/rebuild_wyscout_v5.py            absent
```

The independent verdict is based on the complete standalone design and direct
observations. It does not inherit the producer's or master's acceptance decision.

## Ranked finding

### P1-01 — the exact uv environment transformation names the wrong executable spelling

R15 Section 8.0.2 makes the outer environment a closed map. Its operational
entries say:

```text
UV = <actual resolved admitted uv physical path>
stable token = <W04_UV_PHYSICAL_PATH>
```

It further requires the exact uv 0.9.21 transformation to overwrite `UV` with its
“resolved physical spelling,” while incrementing `UV_RUN_RECURSION_DEPTH` from
`0` to `1` and prepending the project venv bin directory to `PATH`. Section
8.0.5 carries the same accepted actual `UV` value and
`<W04_UV_PHYSICAL_PATH>` token into both child base environments. Unknown or
unequal values fail before either role imports project code.

The read-only reproduction constructed the 20 exact stable literal entries, the
nine outer operational entries, the exact required `PATH`, an inherited regular
descriptor, `UV_RUN_RECURSION_DEPTH="0"`, `VIRTUAL_ENV`, offline/locked/no-sync
controls, and no ambient environment. It supplied the physical Cellar path as the
input `UV` value and invoked:

```text
uv run --locked --no-sync python -S -B -c <environment observation>
```

The actual first-instruction environment had exactly 29 names. The values
reproduced:

```json
{
  "UV": "/opt/homebrew/bin/uv",
  "UV_RUN_RECURSION_DEPTH": "1",
  "PATH": "<project-root>/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
}
```

The intended depth increment, one venv prefix, closed name count, and unchanged
other values pass. Only the claimed physical `UV` spelling fails. A second minimal
closed-map control produced the same logical spelling. Supplying
`UV=/opt/homebrew/Cellar/uv/0.9.21/bin/uv` does not preserve it: the invoked uv
process overwrites it with `/opt/homebrew/bin/uv`.

The distinction is real in this admitted environment:

```text
logical executable: /opt/homebrew/bin/uv
raw link:           ../Cellar/uv/0.9.21/bin/uv
physical executable:
  /opt/homebrew/Cellar/uv/0.9.21/bin/uv
physical SHA-256:
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
```

This is not a cosmetic report field. The expected actual outer-Python
`E_outer_base` is hashed after its nine substitutions. The first user-code
verifier requires exact equality with that expected map and reconstructs
`fixed_environment_digest`. Both child expected base maps copy the accepted outer
`UV` actual value and their base digests substitute the named token. A physical
versus logical disagreement therefore causes:

1. outer closed-map comparison failure;
2. outer base-digest/tuple reconstruction failure if comparison were bypassed;
3. child base-map failure for admission and rebuild;
4. child envelope `base_environment_digest` disagreement;
5. complete transport-environment hash disagreement; and
6. failure of the stable environment-values and process-launch proof.

R15 explicitly rejects normalization, an undeclared substitution, and a changed
`UV` path. The implementation cannot treat the paths as interchangeable merely
because they resolve to the same bytes.

A separate read-only control used a low-level process launch with:

```text
visible argv[0] = "uv"
executable target =
  /opt/homebrew/Cellar/uv/0.9.21/bin/uv
```

That process yielded the physical Cellar spelling in `UV` and depth `1`. This
demonstrates that R15's desired value is implementable, but only by adding an
exec-target rule not presently stated in the standalone design. The design
currently names the ordered argv, `PATH`, uv physical identity, and expected
transformation, but it never says that the OS executable parameter differs from
the `uv` token or binds that distinction into the master and launcher spawn
algorithms. Normal `PATH` resolution of the mandated token yields the failing
logical value.

The defect is P1 because R15 demands exact implementation, makes the map closed,
and requires all environment comparisons to pass before authority exists. An
implementer must currently improvise a security- and identity-relevant process
launch detail to make the stated positive test pass.

**Bounded correction:** issue standalone R16 and choose exactly one reviewed
route:

- bind the actual exec target for outer and child uv processes to the already
  admitted physical executable while retaining literal `uv` as the ordered
  `argv[0]`; specify the exact OS/subprocess semantics, equality observations,
  descriptor preservation, and stable/operational classification; or
- admit `/opt/homebrew/bin/uv` as the actual current uv-set environment value,
  rename its normalization token so it does not falsely claim physical spelling,
  and separately require that the contained logical symlink resolves through the
  exact raw link to the already hashed physical executable.

Whichever route is selected must update Sections 8.0.2, 8.0.5, 8.9, 9, 12 and all
outer/admission/rebuild environment tests together. It must retain the physical
uv version/mode/size/digest authority, exact visible argv, locked/no-sync/offline
behavior, acyclic environment digest, one-time tuple/envelope insertion,
descriptor pass sets, and two-root stable/operational split. It must not relax
closed-map equality, accept either spelling, use `realpath` as an after-the-fact
normalization, or add a broad path exception.

## Build projection, invocation, and dependency challenge

### Exact 25/25 build schema

Mechanical parsing, independent of the prose count, found 25 unique
Unicode-code-point-sorted keys in the stable pre-build projection and 25 unique
Unicode-code-point-sorted keys in the rebuild invocation.

Projection:

```text
authority_rows
code_manifest_id
code_manifest_sha256
dependency_rows
dependency_watermark
environment_digest
feature_cutoff_ts
feature_schema_hash
identity_bundle_id
identity_bundle_sha256
local_resource_digest
product_contract_digest
role_context_id
role_context_state
role_context_version
schema_bundle_digest
schema_version
selected_lock_closure_digest
source_manifest_id
source_manifest_sha256
tenant_club_id
tenant_id
window_definition_id
window_end_utc
window_start_utc
```

Invocation:

```text
authority_rows
build_id
code_manifest_id
code_manifest_sha256
dependency_rows
dependency_watermark
environment_digest
feature_cutoff_ts
feature_schema_hash
identity_bundle_id
identity_bundle_sha256
local_resource_digest
product_contract_digest
role_context_id
role_context_state
role_context_version
schema_bundle_digest
selected_lock_closure_digest
source_manifest_id
source_manifest_sha256
tenant_club_id
tenant_id
window_definition_id
window_end_utc
window_start_utc
```

The intersection has exactly 24 members. The set differences are exactly:

```text
projection only: schema_version
invocation only: build_id
```

R15 hashes canonical bytes of the closed projection once. Only after the digest
exists does the launcher remove the schema marker from the runtime representation
and insert the resulting `build_id`. The child performs the inverse
schema-directed reconstruction, retaining the same 24 values, then hashes the
projection once and compares the digest to all enclosing identities. The stable
process contract binds the projection and invocation schemas and algorithm, not a
completed instance containing the future code-manifest or build digest. This
removes the R14 cycle.

The 24 common fields cover the complete tenant context, exact source manifest,
identity bundle, four authority triples, accepted products/schemas, neutral role
context, exact window/cutoff, five dependency rows and watermark, code manifest,
environment, selected lock closure, and 17-resource digest. The lineage hash is
derived from the included complete ordered dependency objects and is required to
reconcile before construction; omitting that duplicate representation does not
omit semantic authority. Run IDs, prefix/receipt/layer paths, descriptors,
nonces, diagnostics, clocks, host/root spellings, output digests, and actual pyc
inventories remain outside the preimage.

No second preimage, placeholder, convergence, path-parsed identity, completed
invocation self-hash, or second build algorithm was found. Subject to P1-01's
environment correction, this part passes.

### Accepted five-field dependency objects

The existing `EvidenceDependency` contract was reproduced through its JSON wire
validation path. It exposes exactly:

```text
kind
dependency_id
digest
observed_at
available_at
```

A sample canonical JSON object round-tripped as:

```json
{
  "kind": "source_manifest",
  "dependency_id": "123e4567-e89b-42d3-a456-426614174000",
  "digest": "0000000000000000000000000000000000000000000000000000000000000000",
  "observed_at": "2025-01-01T00:00:00Z",
  "available_at": "2025-01-02T00:00:00Z"
}
```

The accepted `ContractModel.extra="forbid"` behavior independently rejected each
of `dependency_kind`, `manifest_id`, and `manifest_sha256`. R15 uses no adapter or
report-local alias. The accepted `DependencyKind` declaration order reproduced:

```text
source_manifest
identity_evidence
feature_schema
model_artifact
retrieval_index
```

R15 admits exactly one `source_manifest`, one `identity_evidence`, and three
distinct `feature_schema` records, sorted by the referenced enum order, UUID
bytes, digest, observed clock, and available clock. It binds UUIDv5 feature
identities, complete lowercase digests, both clocks, unique kind/ID pairs, a
maximum availability watermark, and SHA-256 over the complete five canonical
ordered objects.

The existing temporal validator was exercised with a valid five-row lineage and
then with equality mutations. `observed_at == feature_cutoff_ts`,
`available_at == feature_cutoff_ts`, and
`available_at_watermark == feature_cutoff_ts` all failed. R15 separately extends
that same strict-before rule to authority decisions, independent reviews,
acceptances, and identity corrections. No `<=` waiver or backdating route was
found.

This part passes.

## Process, environment, descriptor, and result challenge

### Closed inputs and exact roles

Mechanical table parsing reproduced unique cardinalities:

```text
common child envelope:       16
admission inputs:             8
rebuild inputs:              10
rebuild invocation:          25
```

The three ordered visible argv are exact and distinct:

```text
uv run --locked --no-sync python -S -B scripts/launch_wyscout_v5.py
uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py
uv run --locked --no-sync python -S -B scripts/rebuild_wyscout_v5.py
```

They bind `W04_LOCAL_CONTROL`, `PRE_BUILD_ADMISSION`, and
`POST_BUILD_ID_REBUILD`; retain eight tokens; prohibit value argv, stdin, generic
config, newest-file selection, provider access, and alternate entry points; and
use only one canonical base64url input envelope per child.

The outer and child digest graphs are acyclic. Each hashes a closed base map before
inserting its tuple or envelope. The complete actual transport hash is calculated
after insertion and is returned for independent comparison; it never appears
inside the map being hashed. The common nonce and actual descriptors are
operational and tokenized in the stable base. Apart from the incorrect uv spelling
in P1-01, the name counts, absent-name closure, one venv `PATH` prefix, depth
increment, and value preservation reproduced.

The no-site runtime probe reported:

```json
{
  "coverage_loaded": false,
  "dont_write_bytecode": 1,
  "no_site": 1,
  "pycache_prefix": null,
  "site_paths": [],
  "src_paths": [],
  "virtualenv_loaded": false
}
```

`pycache_prefix` is null only because this design review did not create a role
prefix or mutate `data/working`; the implementation contract still requires all
three exact empty prefixes. The probe confirms `-S`, `-B`, absence of `.pth`
execution, and absence of editable-root startup.

### Descriptor and TOCTOU closure

A read-only descriptor probe passed descriptor 9 through the exact
locked/no-sync uv/Python prefix. At the child it remained a regular file,
inheritable, `FD_CLOEXEC` clear, offset zero, and readable from the expected first
bytes. This reproduces the core uv pass-through property. R15 additionally
requires the master/launcher to use explicit close/pass sets, descriptor-relative
no-follow opening, exact fstat/path/digest equality, positional reads that preserve
offset zero, re-arming of `FD_CLOEXEC` for the retained launcher descriptor, and
exactly two distinct child descriptors for source and result.

The launcher retains the launcher source descriptor; neither child receives it.
The children receive only their source descriptor and result writer. Both child
and launcher recheck descriptor identity and full bytes. Persistent replacement
at each checkpoint fails. R15 honestly documents the same-trust-domain
replace-and-restore residual rather than claiming the path checks observe an
unobservable transient. No reopen-by-path fallback or result-only child authority
remains.

The selected descriptor integer must be one positively reproduced by the final
implementation. The independent probe established one valid nonstandard choice;
it does not authorize arbitrary untested descriptor values.

### Bounded result frames and sole authority

The frame is closed by eight-byte magic `W04CRSLT`, version, bounded payload
length, canonical JSON bytes, SHA-256, exact EOF, nonce, timeout, diagnostics
limits, process exit, and role schema. Admission returns the canonical immutable
manifest bytes and its component proofs but cannot write the manifest or calculate
the build ID. The launcher alone writes/confirms and reopens the content-addressed
manifest, constructs the stable projection, performs the one build-ID SHA-256,
creates the post-hash invocation, renders run-bound paths, and launches rebuild.
The rebuild child calls named product writers and writes only its invocation
receipt; it cannot publish the code manifest or calculate an alternate build ID.

Result payloads are exhaustive rather than descriptive. R15 binds all admission
result keys and component proofs, all rebuild result keys, three ordered layer
rows, receipt evidence, and the 17-field final recheck. Stdout and stderr are
diagnostic only and capped independently; neither can be interpreted as
authority. Truncation, oversized length, replay, extra bytes, noncanonical JSON,
unknown fields, unequal environment/input/result values, nonzero exit, and
timeout all fail.

The chronology is singular:

```text
admission result
immutable manifest write/confirm/readback
closed pre-build projection
one build-ID SHA-256
post-hash invocation
run-bound paths and rebuild prefix
rebuild envelope/environment
rebuild child
```

No competing manifest writer, build calculator, early prefix, or early output
authority was found. This part passes subject to P1-01.

## Packaging, installed bytes, executables, aliases, and pyc

### Locked closure and installed equality

The locked all-groups tree and installed environment were compared as normalized
name/version sets. `uv tree --locked --all-groups --depth 100` reported resolution
of 83 lock graph packages. The actual unique selected distribution nodes and
`uv pip list` each contained 82 members including the editable project, and
`comm -3` emitted no difference. The editable
`scouting-intelligence==0.1.0` row was present exactly once. All eight groups
remain selected:

```text
data
e2e
lint-type
model
orchestration
runtime
security
test
```

R15 retains byte-admitted `packaging==26.2` as the sole compatible-tag bootstrap,
then requires selected lock, wheel declaration, cache association, extracted tree,
installed mapping, and RECORD ownership before general import. It does not claim
the absent original wheel ZIP was verified. `L == I`, marker selection, wheel
compatibility, no sdist fallback, singular ownership, and runtime
`R subset-of L` remain fail-closed.

### Three denied `.pth` classes and editable metadata

The current site root contains exactly three `.pth` files:

| file | mode | bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `_virtualenv.pth` | `0o644` | 18 | `69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d` |
| `a1_coverage.pth` | `0o644` | 205 | `ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8` |
| `scouting_intelligence.pth` | `0o644` | 81 | `3dc417212f5f46b7399aa8e13c8bd999c4e0cef30f012f8a9412bf8a54f59fba` |

The exact `_virtualenv.py` bootstrap sibling remains mode `0o644`, 4,342 bytes,
SHA-256
`6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d`.
The editable `direct_url.json` remains 123 bytes with SHA-256
`2361d905ac1e0a9300426cb6a2ab39e0ddec56d3c20e9eb967966ff19a053243`;
`uv_cache.json` remains 194 bytes with SHA-256
`a4bf7fb0887dc0b05c0f8286f841340f7dfac4a70ff2b5fec9da26275f9fdd8a`.
R15 admits actual root-bearing bytes operationally, then uses exact root tokens in
stable evidence. No `.pth` executes in any no-site role.

### Exact 35-row executable census

Independent RECORD and `entry_points.txt` parsing found:

```text
35 unique ../../../bin rows
21 RECORD owners
33 direct console/gui entry-point names
20 entry-point owners
RECORD minus entry points = pip3.12, ruff
entry points minus RECORD = empty
```

This is exactly 33 Class E members, one derived Class P member
`pip3.12`, and one Class W member `ruff`. Pip's `pip` and `pip3` declarations,
identical three-wrapper bytes, Ruff's verified `.data/scripts` origin,
root-normalized canonical wrapper shebang, modes, hashes, targets, owners, and
collision rules remain constructive and exhaustive. No basename rule can invent
another pip alias and no wheel script can be treated as an entry point.

### Interpreter and encoding-source bootstrap

The three venv aliases reproduce:

```text
.venv/bin/python
  -> /Users/adrian/.local/share/uv/python/
     cpython-3.12.12-macos-aarch64-none/bin/python3.12
.venv/bin/python3 -> python
.venv/bin/python3.12 -> python
```

All resolve to the same 49,968-byte mode-`0o755` Python 3.12.12 executable with
SHA-256
`cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79`.
The physical uv executable is mode `0o555`, 41,617,552 bytes, version
`uv 0.9.21 (Homebrew 2025-12-30)`, with the digest reported in P1-01.

The exact encoding sources independently reproduce:

| source | mode | bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `encodings/__init__.py` | `0o644` | 5,884 | `78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8` |
| `encodings/aliases.py` | `0o644` | 15,677 | `6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2` |
| `encodings/utf_8.py` | `0o644` | 1,005 | `ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d` |

R15 accurately separates these pre-guard verified source opens from later audit
observations and requires positive implementation tracing of zero installed-pyc
opens and zero alternate-prefix writes.

### Source-complete pyc authority

The site observation remains:

```text
1,075 pycs in 130 __pycache__ directories
112 pytest-rewrite names
963 other names =
  961 mapped distribution normal
  + 1 mapped uv-bootstrap normal
  + 1 optional source-absent six orphan
```

The exact site bootstrap pyc remains 4,159 bytes, mode `0o644`, SHA-256
`08765615dd291d8a643581c2e7a0d3f891284aed32dd38a3940675488579f5f6`.
The optional `six` orphan remains 41,388 bytes, mode `0o644`, SHA-256
`4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28`,
with `six.py` absent.

The repository observation remains:

```text
58 pycs in 19 __pycache__ directories
20 pytest-rewrite pycs mapped to admitted sources
38 other lexical names =
  35 mapped normal pycs
  + 3 exact source-absent inert orphans
```

The three exact present repository orphans reproduce:

| path | bytes | SHA-256 |
| --- | ---: | --- |
| `migrations/__pycache__/env.cpython-312.pyc` | 2,795 | `6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2` |
| `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc` | 25,415 | `b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d` |
| `src/scouting/storage/__pycache__/postgres.cpython-312.pyc` | 4,230 | `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac` |

All are mode `0o644`; their exact `.py` siblings remain absent. R15 correctly
keeps the Foundation SQL file outside Python authority and gives each orphan an
independent, optional, non-authoritative predicate. Stable authority derives from
every admitted source, not from present pyc. Actual pyc paths/counts/hashes are
operational, every present file must classify exactly once, all remain unread and
unchanged in guarded roles, and two roots may differ only as documented. This
closes the R8 pyc finding.

## Source, rights, products, paths, writers, gate, and ledger

The source completion and profile integrity reproduce without reading provider
payloads:

```text
completion manifest:
  6,803 bytes
  69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1
source profile:
  18,574 bytes
  569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649
```

Mechanical design parsing found 18 unique source evidence paths and 17 unique
local-resource paths. R15 preserves the completion-only readable seam, five
direct JSON/CSV objects, ten durable archive members, hash-only ZIP rows, four
directory-only exclusions, CC-BY-4.0 attribution, restricted local project use,
derived/internal-review permission, and export denial. It does not authorize a
new provider acquisition.

Record family comes only from the strict completion-path-to-envelope map. Payload
`kind`, shape, name, taxonomy, and filename inference cannot dispatch. Missing,
null, typed, safe-unknown, and unsafe-unknown discriminator states preserve their
typed canonical evidence and route only to fixed rejected-record partitions.
Known Bronze, rejected fields, Silver, Gold, unknown quarantine, staging,
manifests, and receipts have exact path templates and named serializers.

The player-match key remains:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

The Gold key remains:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

`feature_schema_hash` is required and non-key. Neutral role context is fixed.
Period-relative occurrence does not become action UTC; lineup intervals remain
bounded/right-censored; minutes and per-90 remain suppressed; field anomalies and
unmapped taxonomy values remain evidence rather than silently repaired.

Source coverage and Gold coverage remain separate six-dimensional contracts.
Gold uses integer numerators/denominators for identity, lineup, action,
coordinate, possession, and temporal coverage. Only coordinate and possession may
use authority-proven zero-denominator non-applicability. Overall coverage is the
minimum, and rights/authority/identity/lineage/cutoff failures suppress rather
than waive.

Publication is staging-first and atomic, collisions fail before rename, and
ownership is serial. Bronze, identity, each Silver family, Silver manifest,
Gold/temporal, quality, launcher, admission, rebuild, independent reviewers,
health, card, gate, Git acceptance, and ledger have distinct responsibilities.
The launcher cannot write product/layer/invocation receipts; the rebuild child
cannot write the code manifest or calculate another build ID.

The full `G-W04` gate remains before local acceptance. The two-local-commit ledger
is exact:

1. full gate while registry is pre-checkpoint;
2. local integration commit `phase(w04): accept governed data spine`;
3. immutable annotated `checkpoint/w04-accepted` tag on that commit;
4. registry and clean-tree certificate update;
5. local ledger commit
   `orchestration(w04): record accepted checkpoint ledger`; and
6. final clean/local-only/guard/empty-remote verification.

There is no self hash, future ledger SHA, tag movement, third cleanup commit,
stash/reset/history rewrite, remote, hosted CI, public endpoint, cloud, container,
or deployment route.

These source/product/gate controls pass. P1-01 is confined to the process
environment contract but blocks the implementation graph that would enforce
them.

## Required disposition

R15 cannot be accepted for implementation while P1-01 remains. Dispatch one
bounded standalone R16 correction that:

1. freezes the actual OS uv exec target separately from visible `argv[0]`, or
   truthfully admits the logical Homebrew uv spelling and its exact resolution;
2. reproduces the corrected value through all three exact locked/no-sync uv
   launches from their closed input maps;
3. updates every outer/child environment, base digest, bootstrap/envelope,
   stable/operational, negative-test, and two-root reference consistently;
4. preserves the exact physical uv bytes/digest, no-site behavior, descriptors,
   roles, argv, schemas, one-SHA build identity, and all other passing R15
   controls; and
5. returns for new master and independent review before implementation.

No architecture, project root, Python/uv dependency policy, source selection,
rights decision, storage root, provider/network boundary, local-only policy,
container policy, or Git policy change is needed.

## Scope confirmation

- No Git command or operation was performed.
- No dependency, lockfile, environment, source, configuration, migration, script,
  data, orchestration, or candidate-design path was changed.
- No provider payload, excluded archive, network, cloud, hosted CI, public
  endpoint, remote, container, or deployment was accessed or created.
- No pyc, cache, prefix, data, manifest, receipt, or product path was written,
  deleted, repaired, or imported as authority.
- Only
  `reports/reviews/W04/wyscout-schema-design-independent-review-R9.md` and its
  packet return are in this reviewer's write scope.
