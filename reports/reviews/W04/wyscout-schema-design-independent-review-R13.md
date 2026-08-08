# W04 Wyscout schema design — fresh independent review R13

## Decision

**Recommendation: PASS.**

I found zero P0, zero P1, and zero P2 defects in
`reports/reviews/W04/wyscout-schema-design-R20.md`.

This recommendation is limited to the R20 design as a standalone implementation
authority. It is not an implementation acceptance, provider acquisition,
deployment approval, Git checkpoint, or permission to create the future runtime
scripts. R20 is internally closed enough for bounded implementation packets, and
its exact current-root claims reproduced under the packet's locked/no-sync,
bytecode-denying review harness.

## Review identity and scope

- Task: `W04-SCHEMA-DESIGN-REVIEW-01-R13`
- Role: fresh independent data-architecture reviewer
- Candidate: `reports/reviews/W04/wyscout-schema-design-R20.md`
- Candidate bytes: `245957`
- Candidate physical lines: `4516`
- Candidate SHA-256:
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- Review date: `2026-07-30`
- Owned outputs:
  `reports/reviews/W04/wyscout-schema-design-independent-review-R13.md`
  and
  `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R13.md`
- Git operations: none
- Dependency/lock/environment mutation: none
- Provider/network/cloud/container/public-endpoint activity: none
- Delegation: none

I read all 4,516 candidate lines and treated R20 itself as the sole proposed
implementation authority. Producer, master, and prior independent-review records
were mandatory context and chronology, not evidence that a candidate assertion
was true. Every current-root assertion reported below was independently
recomputed.

## Mandatory readback

The following mandatory inputs were read completely through EOF:

| Input | Bytes | Lines | SHA-256 or readback note |
| --- | ---: | ---: | --- |
| `AGENTS.md` | complete | complete | read before candidate/Python |
| `orchestration/task_packets/W04-SCHEMA-DESIGN-REVIEW-01-R13.yaml` | complete | complete | read before candidate/Python |
| `reports/reviews/W04/wyscout-schema-design-R20.md` | 245957 | 4516 | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R20.md` | complete | 123 | complete readback |
| `orchestration/task_packets/W04-SCHEMA-DESIGN-01-R20.yaml` | complete | 171 | complete readback |
| `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R20.yaml` | complete | 76 | complete readback |
| `reports/verification/W04/wyscout-schema-design-R20-master-verification.md` | complete | 167 | complete readback |
| `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-REVIEW-01-R12.yaml` | complete | 70 | complete readback |
| `reports/verification/W04/wyscout-schema-design-independent-review-R12-master-verification.md` | complete | 125 | complete readback |
| `reports/reviews/W04/wyscout-schema-design-independent-review-R12.md` | complete | 1182 | complete readback |
| `reports/phase-gates/W04/source-schema-profile.md` | 18574 | 365 | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` |
| `data/source/wyscout/v5/completion-manifest.json` | 6803 | 1 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| `src/scouting/contracts/primitives.py` | 2381 | 76 | `ee3fa657174cc949a5b7a389d60560abbdef596dbab913060a70516f0b988691` |
| `src/scouting/contracts/evidence.py` | 10534 | 289 | `ff771aee3c9e23eb9ebe7e3919f75557f919919b232f752c4f708abf6c7cce10` |
| `docs/architecture/threat-model.md` | 7722 | 71 | `da76328ed066c9f837d3c1ba9593be5ab58447dce54b59573aad8c6da95d6ab4` |
| `pyproject.toml` | 2285 | 106 | `963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b` |
| `uv.lock` | 134056 | 1224 | `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca` |
| `../scouting-ml-production-blueprint.html` | 153792 | 3219 | `b55e624d27529761c937291ae1bc5d08de44120ace7739e87e0aad8a1000829a` |
| `../scouting-ml-agent-implementation-workflow.html` | 81470 | 1270 | `73fd051a7fb374733c552351d4f4dfe7b603c5cbdd9fdb7c3079895244d5b0d7` |
| `orchestration/templates/subagent_return.md` | 530 | 38 | `2d0d4fa9b706b4a4f7fe20f8f2d9f8813a25314db7de4fe6cd91c150abbf2dd5` |

The workflow HTML was reread in bounded line chunks after one mistyped path and
one truncated combined display; the final read covered every line 1–1270 without
an omitted interval. The 3,219-line blueprint and 1,224-line lock were likewise
read in bounded chunks through EOF.

## No-write review harness

### Preflight

Before opening R20 and before invoking Python or an installed helper, I ran a
shell-only recursive inventory from the physical repository root. `.git` and
`.venv` were pruned from the repository inventory; the site inventory used the
exact `.venv/lib/python3.12/site-packages` root. For every pyc the canonical
metadata row bound:

```text
path
size
mode
link_count
mtime
first_16_bytes
first_4_byte_magic
```

The content row bound `path` plus the complete file SHA-256. Canonical rows were
lexically sorted and then SHA-256 hashed. No file was deleted, repaired,
truncated, touched, recreated, quarantined, or moved.

Exact preflight evidence:

```text
repository_root =
  /Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence
site_root = .venv/lib/python3.12/site-packages

repository_pyc_count = 58
repository_metadata_inventory_sha256 =
  9612b600045c20c762a6c1a6d4354e464015dc8eeb176bb039147d9f9edefada
repository_content_inventory_sha256 =
  17758a1286ab5af30683fb51458e282be9b73d7cc1d91dd914f9470aa8561c49

site_pyc_count = 1086
site_metadata_inventory_sha256 =
  d1ae2d14dcdaa2f49fe6f43ed968aee272658fbe9ccff914e1545643729a95bf
site_content_inventory_sha256 =
  c6e5ece54b7b49f6177833fe569882bd06da4155cce30b28d758642076301147
```

The later complete classifier independently counted 131 site cache directories,
19 repository cache directories, 20,047,587 site-pyc bytes, and 1,475,178
repository-pyc bytes.

### Python discipline

Every Python helper used repository-root uv with `--locked --no-sync`, exported
`PYTHONDONTWRITEBYTECODE=1` before uv started, and invoked Python with `-B`.
Helpers that needed only the standard library also used `-S`. Installed-package
helpers asserted both denial controls as their first instruction before importing
another file-backed module:

```text
assert sys.dont_write_bytecode
assert os.environ["PYTHONDONTWRITEBYTECODE"] == "1"
```

The environment sandbox initially denied uv's read of external cache metadata.
The same packet-mandated command was rerun with read authority; no sync, download,
install, or cache mutation was requested or performed.

### Terminal postflight

The terminal postflight repeats the identical shell inventory program after the
last review check. Its evidence is:

```text
repository_pyc_count = 58
repository_metadata_inventory_sha256 =
  9612b600045c20c762a6c1a6d4354e464015dc8eeb176bb039147d9f9edefada
repository_content_inventory_sha256 =
  17758a1286ab5af30683fb51458e282be9b73d7cc1d91dd914f9470aa8561c49

site_pyc_count = 1086
site_metadata_inventory_sha256 =
  d1ae2d14dcdaa2f49fe6f43ed968aee272658fbe9ccff914e1545643729a95bf
site_content_inventory_sha256 =
  c6e5ece54b7b49f6177833fe569882bd06da4155cce30b28d758642076301147

comparison = PASS_IDENTICAL
```

These are the original preflight values. The final shell command is retained as
the terminal chain-of-custody check; no Python or report edit follows it.

## Findings

### P0

None.

### P1

None.

### P2

None.

## Exact source, scope, rights, and coverage review

R20 opens the completion document first, binds its complete digest, and derives
the readable source set only from exact declared paths. Its discriminator is an
envelope field selected by a closed completion-path map rather than a payload
label, filename heuristic, table shape, or inferred semantic. That removes the
record-family confusion present in designs that allow a payload `kind` or label to
select a parser. Unknown discriminators have a single rejected-record route.

I independently hashed all 18 admitted physical rows:

```text
completion-manifest.json
objects/competitions.json
objects/teams.json
objects/players.json
objects/matches.zip
objects/events.zip
objects/eventid2name.csv
objects/tags2name.csv
archive-members/matches_England.json
archive-members/matches_France.json
archive-members/matches_Germany.json
archive-members/matches_Italy.json
archive-members/matches_Spain.json
archive-members/events_England.json
archive-members/events_France.json
archive-members/events_Germany.json
archive-members/events_Italy.json
archive-members/events_Spain.json
```

Results:

- exact row count: 18;
- unique exact paths: 18;
- aggregate physical bytes: 991,136,406;
- every size equals the completion/candidate declaration;
- every complete SHA-256 equals the completion/candidate declaration;
- symlink count: zero;
- scope-excluded archive payload reads: zero.

The design keeps the seven completion objects and ten admitted durable members
distinct. It does not claim that hashing a ZIP object verifies an absent original
wheel-like/member container or vice versa. The four directory-declared excluded
members remain excluded and are not relabelled source resources.

The source `DataCoverage` object is separate from Gold eligibility. Its six exact
dimensions are source object integrity, admitted-member integrity, match
partition presence, event partition presence, partition match-ID alignment, and
directory-only exclusion. All current values are strict Python floats `1.0`, with
non-negative strict counts and empty `missing_dimensions`. The candidate rejects
zero expected counts, 17/19-row substitutes, duplicate/reordered paths, and an
attempt to use downstream Gold dimensions as source-integrity evidence.

The rights boundary agrees with the completion evidence:

- source ID `wyscout-soccer-match-events-figshare-v5`;
- classification `wyscout_figshare_v5_cc_by_4`;
- licence `CC-BY-4.0`;
- attribution required;
- derived and internal-review use permitted;
- export false in the W04 source-manifest use context;
- source release and local acquisition remain different truthful clocks.

Nothing in R20 silently broadens the source permission into deployment,
redistribution, provider reacquisition, a network lookup, or external knowledge.

## Field authority and exact 119-pair closure

I parsed the normative tab-separated roster directly from R20 and the measured
profile tables independently, normalizing CSV columns only to the candidate's
declared `$.<column>` member-path convention. The ordered arrays were identical:

| Record kind | Exact count |
| --- | ---: |
| `competition` | 10 |
| `team` | 11 |
| `player` | 26 |
| `match` | 47 |
| `action` | 18 |
| `event-taxonomy` | 4 |
| `tag-taxonomy` | 3 |
| **Total** | **119** |

The exact 119 pairs are unique, their source-profile order equals the R20 roster
order, the first pair is `(competition,$)`, and the last is
`(tag-taxonomy,$.Tag)`. The source-shape rule is constructive: it retains only
positive measured type rows in the fixed
`array,boolean,integer,number,null,object,string` order. A semantic decision cannot
guess a type/count or revise the measured profile.

The field route has a complete acyclic artifact graph:

```text
fixed inputs
  -> decision canonical bytes/digest
  -> registry parsed canonical bytes/digest
  -> independent review physical bytes/digest
  -> acceptance canonical bytes/digest
```

Candidate, review, and acceptance ownership are disjoint. The master can accept
only `PASS`; the reviewer cannot edit the decision/registry; an acceptance binds
the already frozen physical review digest. No artifact contains its own digest.

Every decision row is closed over eight keys, preserves the exact roster order,
binds measured source shape, and selects only `TRANSFORM`,
`PRESERVE_UNMAPPED`, or `FORBIDDEN`. The transform union is closed over eleven
specified kinds with exact keys and values. The collision rule permits a shared
canonical object only through distinct `COMPOSE_OBJECT` members with the same
declared output object; all other duplicate canonical producers fail.

The approved field contract-test path is exactly:

```text
tests/contracts/test_wyscout_field_registry_authority.py
```

It is named in the field decision packet rather than left to implementer choice.

## Strict ActorId and evidence primitives

The existing primitives read:

```text
type StrictUuid = Annotated[UUID, Strict()]
type ActorId = StrictUuid
```

Using the installed contract implementation, I validated canonical JSON actor
`123e4567-e89b-42d3-a456-426614174000`. The in-memory value was `uuid.UUID`, and
`str(value)` reproduced the input byte-for-byte. Seven negative forms were
rejected either by strict UUID validation or by the required canonical
reserialization comparison: uppercase, braced, URN, compact, surrounding
whitespace, `master.agent`, and a numeric JSON value.

I also instantiated `EvidenceDependency` from the exact five keys:

```text
kind
dependency_id
digest
observed_at
available_at
```

The model retained exactly those keys and rejected an extra key. R20 correctly
uses the existing enum/UUID/digest/UTC contracts rather than defining a report
alias. The four semantic routes require the same strict actor behavior,
`accepted_by == decided_by`, a distinct reviewer, and truthful ordered clocks.

## Possession semantic closure

The possession predicate schema mechanically parsed to exactly twelve required
fields:

```text
closes_control
contested_attachment
control_team_source
dead_ball_attachment
decided_by
decision
event_id
forbidden_tag_ids
opens_control
rationale
required_tag_ids
subevent_id
```

The valid-combination table has exactly six rows:

```text
CONTROL
RESTART
DEAD_BALL
CONTESTED
NON_CONTROL_ADMIN
UNMAPPED
```

This is a true closed union, not a set of examples. Required/forbidden tag sets are
sorted, unique, and disjoint; selectors are deterministically ordered and cannot
overlap. Every row, including `UNMAPPED`, carries a strict actor and explicit
nonempty rationale. Nullability is limited to `subevent_id` and the two attachment
fields where the decision row permits it. `UNMAPPED` cannot acquire control,
close control, buffer, or attach. The bounded contested-action buffer ends at the
next resolved same-period possession or becomes unassigned at the period
boundary; it cannot cross periods.

## Supported-feature, identity, temporal, and product clauses

The supported-feature authority is complete over Gold-exposed and explicitly
unavailable features. Provider-native possession, minutes, per-90, and inferred
period-terminal claims remain suppressed unless a later accepted authority
changes the closed registry. The candidate keeps count features, denominators,
and eligibility predicates separate.

Identity is numeric-source-key based. Zero is not a player identity. Names,
current-team labels, and external knowledge cannot repair an absent, malformed,
duplicate, or conflicting key. Crosswalk rows retain match method, confidence,
source-valid interval, observed/available clocks, evidence digest, state, review
queue linkage, and version. Corrections are an explicit union between queue
disposition and direct current-resolved supersession. Both retain prior evidence,
advance availability/version/bundle identity, and prohibit invented queue history.

W04 has exactly five complete temporal dependencies:

```text
one source_manifest
one identity_evidence
three distinct feature_schema rows
```

The strict dependency watermark is the maximum `available_at`; every admitted
fact and authority must be available strictly before the feature cutoff. The
candidate distinguishes observed, valid, available, decided, reviewed, accepted,
acquired, generated, and output clocks. File mtimes, Git metadata, report clocks,
and source release cannot impersonate another clock.

The Bronze/Silver/Gold contracts have closed paths, schemas, serializers, unique
keys, partition order, reconciliation, coverage, quarantine, and receipt rules.
Quarantine preserves evidence but grants no Gold eligibility. There is exactly one
sampled serving-generation clock and it equals `RetrievalResult.generated_at`;
build identity contains no generation clock.

Unsupported exact minutes/per-90 remain absent. The profile's period maxima are
observed lower bounds, not evidence of exact terminal duration. Coordinates
outside `0..100` are preserved as anomaly evidence rather than clamped. Zero actor
IDs remain measured separately. The product claim stays role-aware discovery and
evidence rather than autonomous recruitment or guaranteed success.

## Exact 17-resource set

The candidate's local-resource block mechanically parsed to exactly 17 unique
repo-relative paths:

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

There is no directory shorthand and no eighteenth resource. Source objects,
identity runtime objects, code/runtime bytes, output destinations, window values,
cutoffs, and neutral role context remain in their own guard categories.

## Current uv and interpreter topology

Normal shell lookup selected:

```text
/opt/homebrew/bin/uv
```

Current uv evidence reproduced exactly:

```text
version = uv 0.9.21 (Homebrew 2025-12-30)
logical kind = symlink
logical raw target = ../Cellar/uv/0.9.21/bin/uv
raw target bytes = 26
physical path = /opt/homebrew/Cellar/uv/0.9.21/bin/uv
physical mode = 0o555
physical size = 41617552
physical SHA-256 =
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
```

The one-hop target remains inside `/opt/homebrew` and ends at a regular
non-symlink executable. R20 correctly makes the current absolute spellings
operational only. Stable authority keeps logical/installation/physical roles,
relative-target grammar, one-contained-hop policy, final-kind predicate, and
exact physical bytes/version/mode/size.

The three venv aliases reproduced:

```text
python ->
  /Users/adrian/.local/share/uv/python/
  cpython-3.12.12-macos-aarch64-none/bin/python3.12
python3 -> python
python3.12 -> python
```

All lstat modes are `0o755`; both relative links are one hop inside `.venv/bin`;
all resolve to the same physical leaf. The physical CPython evidence is:

```text
version = 3.12.12
implementation = CPython
cache tag = cpython-312
size = 49968
mode = 0o755
SHA-256 =
  cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79
```

The operational `uv run --locked --no-sync python -S -B` process reported
`.venv/bin/python3`. That observation supports R20's explicit distinction between
the command token, wrapper-selected aliases, and the launch-time executable
spelling. R20 does not use `sys.executable` or realpath equality as the wrapper
selector.

The exact no-site standard-library bootstrap rows also reproduced:

| Source | Bytes | SHA-256 |
| --- | ---: | --- |
| `encodings/__init__.py` | 5884 | `78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8` |
| `encodings/aliases.py` | 15677 | `6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2` |
| `encodings/utf_8.py` | 1005 | `ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d` |

No site-packages path appeared under `-S`.

## Outer and child environment closure

The outer stable literal block parsed to exactly twenty names:

```text
ARROW_NUM_THREADS
LANG
LC_ALL
MKL_NUM_THREADS
NUMEXPR_NUM_THREADS
OMP_NUM_THREADS
OPENBLAS_NUM_THREADS
POLARS_MAX_THREADS
PYTHONDONTWRITEBYTECODE
PYTHONHASHSEED
PYTHONIOENCODING
PYTHONNOUSERSITE
PYTHONUTF8
RAYON_NUM_THREADS
TZ
UV_LOCKED
UV_NO_SYNC
UV_OFFLINE
UV_RUN_RECURSION_DEPTH
VECLIB_MAXIMUM_THREADS
```

The nine normalized outer entries are:

```text
HOME
PATH
PYTHONPYCACHEPREFIX
TMPDIR
UV_CACHE_DIR
UV
VIRTUAL_ENV
W04_LAUNCHER_SOURCE_FD
__CF_USER_TEXT_ENCODING
```

Therefore the outer map is exactly 29 names. Both child base maps are the same
twenty literals, exactly eight inherited normalized values (the outer list except
the launcher FD), and:

```text
W04_CHILD_ROLE
W04_ENTRYPOINT_SOURCE_FD
W04_RESULT_FD
W04_RESULT_NONCE
```

Each child base is therefore exactly 32 names. `W04_CHILD_INPUT_B64` is excluded
until the one-time canonical-envelope insertion, so its complete transport digest
is nonrecursive. The launcher FD and bootstrap tuple are absent from children.
Every proxy, coverage, dynamic-loader, Python startup/path, uv selector/index, and
lowercase proxy name in the closed absence array stays absent.

The uv input-to-first-instruction transformation is exact: input depth zero,
normal PATH lookup through the admitted logical uv directory, output depth one,
one venv-bin prepend, same logical `UV`, and no other mutation. Actual paths are
operational; stable tokens are role-specific and complete-value substitutions.

The three prefix roles are ordered:

```text
W04_LOCAL_CONTROL
PRE_BUILD_ADMISSION
POST_BUILD_ID_REBUILD
```

Each uses a distinct fresh UUID, descriptor-contained path creation, empty-before
and empty-after evidence, and no cleanup. Prefixes, UUIDs, descriptor numbers,
nonces, device/inode values, and complete actual transport hashes are operational.
The role/order/policy/templates, `-S`, `-B`, and both bytecode controls are stable.

## Child input/result and build cardinalities

Mechanical table parsing produced the exact sequence required by the packet:

```text
common child-input keys       = 16
admission input keys           = 8
rebuild input keys             = 10
rebuild-invocation keys        = 25
pre-build-projection keys      = 25
component-proof rows           = 20
```

The invocation/projection intersection is exactly 24 keys. Invocation uniquely
adds post-hash `build_id`; projection uniquely adds
`schema_version=w04-wyscout-pre-build-projection-v1`. The child reconstructs the
projection by removing only `build_id`, inserting only that schema version, and
retaining every other value byte-for-byte.

The top-level result is closed at ten keys. Its entrypoint descriptor observation
has fourteen keys. Admission has nine result keys and twenty ordered component
proofs. Rebuild has six result keys, three ordered layer rows, a closed receipt,
and a seventeen-key final recheck. Descriptor numbers, device/inode values, run
IDs, nonces, operational prefix spellings, and diagnostics cannot enter stable
identity.

Canonical JSON is fully specified: sorted Unicode-code-point object keys,
duplicate-key rejection, NFC scalar strings, exact control escapes, UTF-8,
shortest permitted integers, no floats, no BOM/whitespace, exact nullability, and
canonical unpadded base64url. Relative paths reject absolute, empty, dot,
dot-dot, backslash, NUL, control, percent-encoded, and alternate-separator forms.

The build graph is acyclic:

```text
immutable code manifest readback
  -> exact 25-key projection
  -> one SHA-256 build_id
  -> post-hash 25-key invocation
  -> run/prefix/receipt/layer path rendering
```

No completed invocation is an input to its own build ID. There is no placeholder,
fixed-point search, iterative hash, prior-build digest, path-derived digest, or
second algorithm.

## Stable schema versions and proof closure

The exact version family is:

```text
w04-local-control-bootstrap-v4
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
w04-installed-executable-census-v3
w04-code-environment-admission-v15
```

Literal search found zero occurrences of:

```text
w04-installed-executable-census-v2
w04-code-environment-admission-v14
```

Thus R20 contains no stale literal acceptance route. It requires the v3/v15
values throughout input, result, immutable readback, health, test, projection,
recheck, two-root proof, gate, and ledger evidence. Only the executable census
and enclosing environment-manifest authority change stable schema version; the
v4/v2/v2 process/environment schemas and the 24-field projection intersection
remain unchanged.

The twenty component proof keys parsed in exact sorted order:

```text
child_result_contract_digest
editable_root_digest
environment_values_digest
executable_census_digest
extracted_runtime_digest
installed_record_runtime_digest
interpreter_digest
local_launcher_control_digest
local_resource_digest
lock_inputs_digest
process_launch_contract_digest
pyc_policy_source_map_digest
selected_lock_closure_digest
selector
selector_bootstrap_digest
stdlib_digest
uv_physical_sha256
uv_version
venv_bootstrap_digest
wheel_declaration_digest
```

Every proof binds the canonical JSON of the manifest's value plus an independently
recounted positive evidence-row cardinality. The proof array and its digest must
agree with decoded manifest bytes and the immutable readback.

## All-groups lock, installed equality, and wheel selection

I evaluated the complete lock graph against the current marker environment, not
an import/AST subset. The selected groups were exactly:

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

Exact result:

```text
lock package rows total = 83
selected rows including editable root = 82
selected third-party rows = 81
installed dist-info rows including editable root = 82
installed third-party rows = 81
lock_only = {}
installed_only = {}
platform-omitted row = colorama
```

`cachecontrol[filecache]` was activated only through its selected edge. Markers
were evaluated with the frozen current environment. The editable
`scouting-intelligence==0.1.0` row was verified separately and excluded from the
third-party equality.

Packaging reproduced:

```text
Packaging version = 26.2
ordered sys_tags cardinality = 1230
uniquely selected compatible third-party wheels = 81
```

For every selected registry package, wheel name/version matched the selected lock
member; compatible tags were ranked by the frozen ordered `sys_tags()` sequence;
each best rank had exactly one winner. No sdist/build fallback was needed.
Mandatory native examples reproduced:

```text
pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl
  best rank 30
  sha256:962ccbab7b642487b1d8b7df90ef677e03134cf1fd8880bf698649b22a69371f
  size 1951724

polars_runtime_32-1.43.0-cp310-abi3-macosx_11_0_arm64.whl
  best rank 210
  sha256:78ca2f97740b2a6beb36eb112749280b5e08750c60f53c08d2feffebdba9d35a
  size 47499586
```

The design truthfully says the original wheel archive hash is not reverified when
the archive is absent. Lock declarations, cache associations, extracted trees,
installed files, and mapping evidence are individually attested; absence does not
become an invented ZIP verification.

## Bootstrap, `.pth`, and editable-root closure

The exact three `.pth` files reproduced:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `_virtualenv.pth` | 18 | `69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d` |
| `a1_coverage.pth` | 205 | `ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8` |
| `scouting_intelligence.pth` | 81 | `3dc417212f5f46b7399aa8e13c8bd999c4e0cef30f012f8a9412bf8a54f59fba` |

All are regular non-symlink mode-`0o644`, link count one. `_virtualenv.pth` is
exact no-newline `b"import _virtualenv"`; it is retained and denied rather than
executed. Its unowned sibling `_virtualenv.py` is 4,342 bytes with SHA-256
`6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d`.
The coverage hook is exact RECORD-owned opaque content and is not evaluated.

The editable dist-info RECORD has nine rows. Exact generated values reproduced:

```text
INSTALLER = b"uv"
REQUESTED = b""
uv_build.json = b"{}"

direct_url.json:
  bytes = 123
  SHA-256 =
    2361d905ac1e0a9300426cb6a2ab39e0ddec56d3c20e9eb967966ff19a053243

uv_cache.json:
  bytes = 194
  SHA-256 =
    a4bf7fb0887dc0b05c0f8286f841340f7dfac4a70ff2b5fec9da26275f9fdd8a
  exact keys = timestamp, commit, tags, env, directories
  commit = null
  tags = null
  env = {}
  directories = only src
```

R20 normalizes only the complete verified editable-root values and excludes cache
clocks. It does not execute `.pth` files, use `site`, trim arbitrary content, or
accept an alternate editable root.

## Complete installed executable census

I enumerated immediate installed RECORD rows of exact form `../../../bin/<name>`,
required singular ownership, parsed verified `entry_points.txt` without importing
the distribution, and read every actual target completely. For every row:

- target is a regular non-symlink file;
- mode is `0o755`;
- link count is one;
- size equals RECORD;
- URL-safe unpadded RECORD SHA-256 equals the complete actual digest;
- E/P text bytes equal the exact selected deterministic template;
- W is exact unchanged Ruff bytes.

Summary:

```text
total rows = 35
owners = 21
Class E = 33
Class P = 1
Class W = 1
Class-E python = 29
Class-P python = 1
Class-E python3 = 4
total text wrappers = 34 = 30 python + 4 python3
binary wheel script = Ruff only
```

The complete enumeration follows. `RECORD` is the URL-safe unpadded digest from
the owning installed RECORD. Every listed row had mode `0o755` and link count one.

| Name | Owner | C | Alias | Group/authority | Target | Bytes | SHA-256 | RECORD |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- |
| `bandit` | `bandit==1.9.4` | E | python | `console_scripts` | `bandit.cli.main:main` | 375 | `b1e2a141c4062af357a1c2127215fbcf8948b3f6bc0ba2f9cd97676b8974446d` | `seKhQcQGKvNXocISchX7z4lIs_a8C6L5zZdna4l0RG0` |
| `bandit-baseline` | `bandit==1.9.4` | E | python | `console_scripts` | `bandit.cli.baseline:main` | 379 | `566680a808a15c1072812f628c0e9fb7fda75e8918c47c7b267bfd86ab335ee4` | `VmaAqAihXBBygS9ijA6ft_2nXokYxHx7Jnv9hqszXuQ` |
| `bandit-config-generator` | `bandit==1.9.4` | E | python | `console_scripts` | `bandit.cli.config_generator:main` | 387 | `09e76cf6323d53ec8ee12e2979c860068cab633c56b293ff291eed068307c55b` | `Ceds9jI9U-yO4S4pechgBoyrYzxWspP_KR7tBoMHxVs` |
| `coverage` | `coverage==7.15.2` | E | python | `console_scripts` | `coverage.cmdline:main` | 376 | `18ac722343a52b5f46714e85fe4e67e7db68f41fb5999a126c56749a39dd601f` | `GKxyI0OlK19GcU6F_k5n59to9B-1mZoSbFZ0mjndYB8` |
| `coverage-3.12` | `coverage==7.15.2` | E | python | `console_scripts` | `coverage.cmdline:main_deprecated` | 398 | `275d065508e6c5b38c3c2c3e325a04c6f641a60d35bb0e3e2eadb780c0c4cf25` | `J10GVQjmxbOMPCw-MloExvZBpg01uw4-Lq23gMDEzyU` |
| `coverage3` | `coverage==7.15.2` | E | python | `console_scripts` | `coverage.cmdline:main_deprecated` | 398 | `275d065508e6c5b38c3c2c3e325a04c6f641a60d35bb0e3e2eadb780c0c4cf25` | `J10GVQjmxbOMPCw-MloExvZBpg01uw4-Lq23gMDEzyU` |
| `detect-secrets` | `detect-secrets==1.5.0` | E | python3 | `console_scripts` | `detect_secrets.main:main` | 380 | `16c1dcee3bcc2078fc6d4df7c0c85db6d043ab3bff5b40f8a13eea19e28aff3f` | `FsHc7jvMIHj8bU33wMhdttBDqzv_W0D4oT7qGeKK_z8` |
| `detect-secrets-hook` | `detect-secrets==1.5.0` | E | python3 | `console_scripts` | `detect_secrets.pre_commit_hook:main` | 391 | `c3535b96dea57e7a88ab48961f74e51c07b019103b89a49c3f71da4cfbda5010` | `w1Nblt6lfnqIq0iWH3TlHAewGRA7iaScP3HaTPvaUBA` |
| `dmypy` | `mypy==1.20.2` | E | python | `console_scripts` | `mypy.dmypy.client:console_entry` | 395 | `fd7c02a78b07678f1c9cf1b3392a8ffefcddaa46ca831cd78733e17bf9068fbd` | `_XwCp4sHZ48cnPGzOSqP_vzdqkbKgxzXhzPhe_kGj70` |
| `doesitcache` | `cachecontrol==0.14.4` | E | python | `console_scripts` | `cachecontrol._cmd:main` | 377 | `f288d5ba410797480b644dd64d26337b655499bb8b8c3b70c23cd8f23a715309` | `8ojVukEHl0gLZE3WTSYze2VUmbuLjDtwwjzY8jpxUwk` |
| `f2py` | `numpy==2.5.1` | E | python | `console_scripts` | `numpy.f2py.f2py2e:main` | 377 | `0137d35b5f0891f0770bf4db3cda003a1439ea9c21cf8a207c6c737f0d8c7ecb` | `ATfTW18IkfB3C_TbPNoAOhQ56pwhz4ogfGxzfw2Mfss` |
| `fastapi` | `fastapi==0.140.0` | E | python | `console_scripts` | `fastapi.cli:main` | 371 | `9595059b752b9075a02dff83bc529a8285762142e3c3d4971b5a90dc583356cf` | `lZUFm3UrkHWgLf-DvFKagoV2IULjw9SXG1qQ3FgzVs8` |
| `httpx` | `httpx==0.28.1` | E | python3 | `console_scripts` | `httpx:main` | 366 | `7f7d4f633504d3f62f33335a9630e5bb4240989c9fb777b4a57e9d5c98fa394d` | `f31PYzUE0_YvMzNaljDlu0JAmJyft3e0pX6dXJj6OU0` |
| `hypothesis` | `hypothesis==6.161.6` | E | python | `console_scripts` | `hypothesis.extra.cli:main` | 380 | `c8f3ffb86e391c775672059c10786dc267be6126be137cb29ae689ca5c04b6ba` | `yPP_uG45HHdWcgWcEHhtwme-YSa-E3yymuaJylwEtro` |
| `idna` | `idna==3.18` | E | python | `console_scripts` | `idna.cli:main` | 368 | `edadc1a09e819cc2707aaac68adce777fcf0c9493f645059130c9835afcf545e` | `7a3BoJ6BnMJweqrGitznd_zwyUk_ZFBZEwyYNa_PVF4` |
| `import-linter` | `import-linter==2.13` | E | python | `console_scripts` | `importlinter.cli:import_linter` | 394 | `a3991b17c2155907b3ef60a9724dca0a1b60cb44b02c3c27aac67305694b6911` | `o5kbF8IVWQez72Cpck3KChtgy0SwLDwnqsZzBWlLaRE` |
| `lint-imports` | `import-linter==2.13` | E | python | `console_scripts` | `importlinter.cli:lint_imports_command` | 408 | `79cad6de5a3591f2405e72728e5f67b8f9080ef0ef1ebdea8089691fcabb5bd1` | `ecrW3lo1kfJAXnJyjl9nuPkIDvDvHr3qgIlpH8q7W9E` |
| `markdown-it` | `markdown-it-py==4.2.0` | E | python | `console_scripts` | `markdown_it.cli.parse:main` | 381 | `23b968a336213c719ab7404b335cc4558eadc81142576f95ab1bb3c576cbd3b9` | `I7loozYhPHGat0BLM1zEVY6tyBFCV2-VqxuzxXbL07k` |
| `mypy` | `mypy==1.20.2` | E | python | `console_scripts` | `mypy.__main__:console_entry` | 391 | `7eece607a418335f32f66b6461c7ccf5341f9ad20cecc93294cbf03311446a3c` | `fuzmB6QYM18y9mtkYcfM9TQfmtIM7MkylMvwMxFEajw` |
| `mypyc` | `mypy==1.20.2` | E | python | `console_scripts` | `mypyc.__main__:main` | 374 | `0df5892a23eb02e32b455ec227bde1099aa62dd6f28584f5d11c9daa19f1ea6d` | `DfWJKiPrAuMrRV7CJ73hCZqmLdbyhYT10Rydqhnx6m0` |
| `normalizer` | `charset-normalizer==3.4.9` | E | python | `console_scripts` | `charset_normalizer.cli:cli_detect` | 394 | `592547366337496b4179d5a707c97d30c103664e807b4ba93cf1ac4a89eb4d62` | `WSVHNmM3SWtBedWnB8l9MMEDZk6Ae0upPPGsSonrTWI` |
| `numpy-config` | `numpy==2.5.1` | E | python | `console_scripts` | `numpy._configtool:main` | 377 | `782d8ad5f261c53a000c95cb436ed3c6389ecff3af36fda32f310fe1982229da` | `eC2K1fJhxToADJXLQ27Txjiez_OvNv2jLzEP4ZgiKdo` |
| `pip` | `pip==26.1.2` | E | python | `console_scripts` | `pip._internal.cli.main:main` | 382 | `d371b253cc444af2efa4c2f1f41ff3030f5cc10a912807de94a35629dc0bc3ff` | `03GyU8xESvLvpMLx9B_zAw9cwQqRKAfelKNWKdwLw_8` |
| `pip-audit` | `pip-audit==2.10.1` | E | python | `console_scripts` | `pip_audit._cli:audit` | 376 | `4e019d96932f0cc76efa3982a43aef6461b9146493fb8b90ef3d493091399773` | `TgGdlpMvDMdu-jmCpDrvZGG5FGST-4uQ7z1JMJE5l3M` |
| `pip-licenses` | `pip-licenses==5.5.5` | E | python3 | `console_scripts` | `piplicenses:main` | 372 | `b563dfd0133f2295a703e09a820fd4b133fd1d2c438150dc6c42ec7d62e8b52f` | `tWPf0BM_IpWnA-Cagg_UsTP9HSxDgVDcbELsfWLotS8` |
| `pip3` | `pip==26.1.2` | E | python | `console_scripts` | `pip._internal.cli.main:main` | 382 | `d371b253cc444af2efa4c2f1f41ff3030f5cc10a912807de94a35629dc0bc3ff` | `03GyU8xESvLvpMLx9B_zAw9cwQqRKAfelKNWKdwLw_8` |
| `pip3.12` | `pip==26.1.2` | P | python | pip derivation | `pip._internal.cli.main:main` | 382 | `d371b253cc444af2efa4c2f1f41ff3030f5cc10a912807de94a35629dc0bc3ff` | `03GyU8xESvLvpMLx9B_zAw9cwQqRKAfelKNWKdwLw_8` |
| `playwright` | `playwright==1.61.0` | E | python | `console_scripts` | `playwright.__main__:main` | 379 | `daa41356f431ac113b8116e10e27512dd837604aa4145d483c801acc74a4f43a` | `2qQTVvQxrBE7gRbhDidRLdg3YEqkFF1IPIAazHSk9Do` |
| `py.test` | `pytest==9.1.1` | E | python | `console_scripts` | `_pytest.config:_console_main` | 392 | `a413d2e64432e6767816f90bcd322955e4da933182f0e4c8ac81465f4ba4f15c` | `pBPS5kQy5nZ4FvkLzTIpVeTakzGC8OTIrIFGX0uk8Vw` |
| `pygmentize` | `pygments==2.20.0` | E | python | `console_scripts` | `pygments.cmdline:main` | 376 | `b295a5c62e55ab90aa54c5febb337e44610abe921a72cdd5d23fe163a11242f3` | `spWlxi5Vq5CqVMX-uzN-RGEKvpIacs3V0j_hY6ESQvM` |
| `pytest` | `pytest==9.1.1` | E | python | `console_scripts` | `_pytest.config:_console_main` | 392 | `a413d2e64432e6767816f90bcd322955e4da933182f0e4c8ac81465f4ba4f15c` | `pBPS5kQy5nZ4FvkLzTIpVeTakzGC8OTIrIFGX0uk8Vw` |
| `ruff` | `ruff==0.16.0` | W | — | wheel `.data/scripts` | — | 23669488 | `1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52` | `GsGQ8j2aaQ11s-dOuIoH4C9kFCJ6QboZIGCa-Yns7FI` |
| `stubgen` | `mypy==1.20.2` | E | python | `console_scripts` | `mypy.stubgen:main` | 372 | `700e4f3f664b8e1bdf8aea64499eef47e0c37228abe5e63acabb06190f9eda2f` | `cA5PP2ZLjhvfiupkSZ7vR-DDciir5eY6yrsGGQ-e2i8` |
| `stubtest` | `mypy==1.20.2` | E | python | `console_scripts` | `mypy.stubtest:main` | 373 | `a294bf140d3e5b8fb056dac68ba91c27703312729f3e146c65c83608e43ef886` | `opS_FA0-W4-wVtrGi6kcJ3AzEnKfPhRsZcg2COQ--IY` |
| `uvicorn` | `uvicorn==0.51.0` | E | python | `console_scripts` | `uvicorn.main:main` | 372 | `b76b0d4a630e1435cf64948bbaa5f9ed830e760658df8d2150798c992adad1cf` | `t2sNSmMOFDXPZJSLuqX57YMOdgZY340hUHmMmSra0c8` |

## Four-tuple selector proof

The selected alias function is equality over:

```text
(normalized owner name/version,
 exact entry-point name,
 exact group,
 exact module:attribute target)
```

The reproduced `python3` set was exactly:

```text
detect-secrets==1.5.0 / detect-secrets /
  console_scripts / detect_secrets.main:main

detect-secrets==1.5.0 / detect-secrets-hook /
  console_scripts / detect_secrets.pre_commit_hook:main

httpx==0.28.1 / httpx /
  console_scripts / httpx:main

pip-licenses==5.5.5 / pip-licenses /
  console_scripts / piplicenses:main
```

Their exact actual evidence:

| Name | Bytes | SHA-256 | First line |
| --- | ---: | --- | --- |
| `detect-secrets` | 380 | `16c1dcee3bcc2078fc6d4df7c0c85db6d043ab3bff5b40f8a13eea19e28aff3f` | exact `.venv/bin/python3` |
| `detect-secrets-hook` | 391 | `c3535b96dea57e7a88ab48961f74e51c07b019103b89a49c3f71da4cfbda5010` | exact `.venv/bin/python3` |
| `httpx` | 366 | `7f7d4f633504d3f62f33335a9630e5bb4240989c9fb777b4a57e9d5c98fa394d` | exact `.venv/bin/python3` |
| `pip-licenses` | 372 | `b563dfd0133f2295a703e09a820fd4b133fd1d2c438150dc6c42ec7d62e8b52f` | exact `.venv/bin/python3` |

For each tuple I changed each field independently and required selection to fall
back to `python`. I also swapped the two detect-secrets targets. All 17 negative
selector mutations selected `python`; no incomplete/permuted tuple selected
`python3`. The remaining body bytes continued to equal the deterministic template
for the verified target.

This establishes constructiveness and exclusivity. Generic alias equivalence,
owner-only, basename-only, target-only, first-existing, `sys.executable`,
realpath-only selection, fallback, repair, `python3.12`, a changed body, changed
owner/group/target, or a swapped tuple cannot pass the design.

The `python3 -> python -> physical interpreter` chain is contained and exact.
Stable normalization uses two distinct complete-line tokens:

```text
<W04_VENV_WRAPPER_PYTHON>
<W04_VENV_WRAPPER_PYTHON3>
```

It occurs only after the complete physical row passes. Equal final physical
resolution therefore cannot collapse the two selected roles.

## Complete pyc classification

I enumerated every current site and repository pyc and classified it by reversing
only the exact admitted cache-name grammars to a present authoritative source,
plus the four exact optional inert-orphan predicates. Every file was a regular
non-symlink, link count one, mode `0o644`, current magic `cb0d0d0a`.

Site result:

| Class | Count |
| --- | ---: |
| `SITE_DISTRIBUTION_NORMAL` | 972 |
| `SITE_PYTEST_REWRITE` | 112 |
| `UV_BOOTSTRAP_NORMAL` | 1 |
| `SITE_SIX_OPTIONAL_INERT_ORPHAN` | 1 |
| **Total** | **1086** |

Additional site facts:

```text
__pycache__ directories = 131
total pyc bytes = 20047587
```

The exact six orphan is 41,388 bytes with SHA-256
`4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28`
and absent sibling/owner. The uv bootstrap pyc is 4,159 bytes with SHA-256
`08765615dd291d8a643581c2e7a0d3f891284aed32dd38a3940675488579f5f6`.
All eleven preserved Packaging incident files mapped to current
Packaging RECORD-owned `.py` sources and were normal distribution caches; none
needed an exception.

Repository result:

| Class | Count |
| --- | ---: |
| `REPOSITORY_NORMAL` | 35 |
| `REPOSITORY_PYTEST_REWRITE` | 20 |
| `REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN` | 1 |
| `REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN` | 1 |
| `REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN` | 1 |
| **Total** | **58** |

Additional repository facts:

```text
__pycache__ directories = 19
total pyc bytes = 1475178
```

Exact source-absent orphan evidence:

| Path | Bytes | SHA-256 |
| --- | ---: | --- |
| `migrations/__pycache__/env.cpython-312.pyc` | 2795 | `6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2` |
| `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc` | 25415 | `b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d` |
| `src/scouting/storage/__pycache__/postgres.cpython-312.pyc` | 4230 | `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac` |

R20 correctly makes the source-authority map stable and the actual pyc inventory
operational. A future preflight may contain another count if allowed mapped caches
were created or omitted before that preflight; every file then present must still
map to an authoritative source or one exact optional predicate. No hardcoded
1,086/58 admission rule, broad orphan class, cleanup, import, or pyc-based source
selection exists.

## H1/H2 host-spelling and two-root proof

I constructed two synthetic operational receipts whose logical path,
installation root, relative raw target, and physical path were all unequal. Both
had:

```text
logical kind = symlink
raw form = relative nonempty NUL-free POSIX
resolution hops = 1
final kind = regular non-symlink executable
mode = 0o555
size = 41617552
SHA-256 =
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
version = uv 0.9.21 (Homebrew 2025-12-30)
```

Complete validated values were replaced by exact roles, not substrings. All nine
required equalities held:

```text
normalized_uv_authority(H1) == normalized_uv_authority(H2)
normalized_outer_environment(H1) == normalized_outer_environment(H2)
normalized_admission_environment(H1) == normalized_admission_environment(H2)
normalized_rebuild_environment(H1) == normalized_rebuild_environment(H2)
environment_digest(H1) == environment_digest(H2)
canonical_code_manifest_bytes(H1) == canonical_code_manifest_bytes(H2)
code_manifest_sha256(H1) == code_manifest_sha256(H2)
pre_build_projection_bytes(H1) == pre_build_projection_bytes(H2)
build_id(H1) == build_id(H2)
```

The independent constructed values were:

```text
environment_digest =
  a398174dbb614d35de2759e48bcc30e7153b7c94c912b9b6b3b513bfb1b6909d
canonical manifest SHA-256 =
  ea27b4b74ec85b423d0e6ed1c2f8a3d64028fdc3532a09401fb2afd14294ef5c
build_id =
  b4cb845a55b580637ce1c88950da2aece95aa7c75d1336b8aa73d0374d575e6b
```

Seven mutations failed: empty raw target, absolute target, NUL, root escape,
inconsistent physical path, second hop, and changed physical mode. The synthetic
receipts do not broaden current-host admission; only normal lookup of the exact
live logical uv path is the live positive.

## Ownership, races, result transport, and writer review

R20 names sole owners for prefix creation, source descriptors, child result
writers, manifest write/build calculation, Bronze/Silver/Gold serialization,
receipts, acceptance, gate, and ledger. The launcher retains its source
descriptor, passes only each child's source descriptor and result writer, uses
bounded length-framed channels, validates nonce/role/digest/EOF/reap, and keeps
diagnostics separate from the canonical result. Children cannot write the code
manifest or calculate a competing build ID.

Path checks combine contained directory descriptors, `lstat`, no-follow open,
`fstat`, exact positional reads/EOF, identity comparison, and repeated postchecks.
The design accurately describes checkpoint detection and retains the residual
same-trust-domain race in the threat model; it does not claim cryptographic
prevention or descriptor-based execution when CPython executes by a path.

Every output rename and manifest write is preceded by a recheck of code,
environment, lock/install/extracted state, all executables, aliases,
interpreter/stdlib, pyc inventories/no-read/no-change state, selected empty
prefix, source descriptors, resources, and ownership. Existing unequal
destinations fail. There is no repair/retry/rescan that broadens authority.

## Gate, health, ledger, and implementation boundary

R20's packet chain is serial where shared authority requires it and disjoint where
an independent reviewer must own only review/return. Decision, review, acceptance,
source, identity, schema, launcher, admission, rebuild, quality, gate, and ledger
steps have explicit prerequisites and path ownership.

The full gate precedes the acceptance integration commit and annotated tag.
Registry/checkpoint ledger evidence is a later distinct local commit. A task
completion cannot substitute for the evidence gate. Recommendation `REWORK`,
missing review, candidate drift, clock/actor mismatch, schema mismatch, stale
v2/v14 evidence, or a digest disagreement fails closed.

R20 names but does not create:

```text
scripts/launch_wyscout_v5.py
scripts/admit_wyscout_v5_runtime.py
scripts/rebuild_wyscout_v5.py
```

The relevant future runtime scripts are absent. The candidate and this review are
design/report only. No source/config/data/runtime implementation, provider
access, network call, Git operation, container action, cloud action, public
endpoint, deployment, or parent-workspace report was created.

## Mechanical checks and results

All Python commands used this prefix:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
```

Standard-library-only helpers additionally used `-S`.

1. Candidate and mandatory-input readback:
   exit 0; R20 245,957 bytes, 4,516 lines, exact digest; mandatory input
   sizes/lines/digests recorded.
2. Field/profile parser:
   exit 0; 119 unique ordered pairs; exact profile equality;
   10/11/26/47/18/4/3.
3. Actor/evidence helper:
   exit 0; canonical UUID roundtrip, seven bad forms rejected, closed five-key
   dependency, extra-key rejection.
4. Possession/field-path parser:
   exit 0; twelve required fields, six valid decision rows, exact approved field
   test path.
5. Complete executable helper:
   exit 0; 35 rows, 21 owners, 33E+1P+1W, every RECORD/hash/size/mode/link/body,
   exact 29E python + one P python + four E python3.
6. Four-tuple negatives:
   exit 0; 16 single-field mutations plus one swapped-target tuple rejected from
   the exceptional selector.
7. Current uv/interpreter:
   exit 0; normal uv selection, version, one-hop link, physical identity, three
   alias chains, CPython 3.12.12 physical bytes, launch-time python3 observation.
8. Schema/environment parser:
   exit 0; outer 29, both child base 32, 16/8/10/25/25/20, 24-key intersection,
   20 sorted proof keys, exact 17 resources, required versions, zero stale
   v2/v14 literals.
9. Lock/install/wheel helper:
   exit 0; selected/installed 82 including editable root, 81 third-party,
   no difference, 1,230 Packaging tags, 81 unique compatible wheel choices.
10. `.pth`/editable/bootstrap helper:
    exit 0; exact three files, unexecuted bootstrap/hook, nine editable RECORD
    rows, direct URL and uv cache exact.
11. Complete pyc classifier:
    exit 0; site 1,086/131 directories/20,047,587 bytes; repository 58/19
    directories/1,475,178 bytes; every file classified; exact orphan facts.
12. Source evidence helper:
    exit 0; all 18 declared physical rows and 991,136,406 bytes; zero excluded
    payload reads.
13. Standard-library helper:
    exit 0; exact three encoding sources under no-site Python.
14. H1/H2 helper:
    exit 0; nine equalities, four unequal host fields, seven negative cases.
15. Packet report-size/recommendation acceptance:
    exit 0; report exists, size exceeds 40,000 bytes, recommendation present.
16. Local-only verifier:
    exit 0; PASS.
17. Identical terminal shell inventory:
    exit 0; `PASS_IDENTICAL` for both counts and all four inventory digests.

## Residual risks

The following are residual implementation/operation risks, not candidate defects:

1. The future launcher/admission/rebuild implementations are security-sensitive.
   They must implement the exact descriptor, canonicalization, environment,
   no-site, pyc, process, timeout, framing, and recheck algorithms rather than a
   simplified interpretation.
2. Same-trust-domain mutation between checkpoints cannot be cryptographically
   prevented by the proposed local process. R20 explicitly preserves that
   residual and detects persistent mutations at declared checkpoints.
3. The exact current uv, CPython, Packaging, wheel, RECORD, executable, and
   bootstrap values are intentionally frozen. A legitimate environment upgrade
   must fail this admission and receive a newly reviewed authority; operators
   must not repair or normalize drift.
4. The current 1,086/58 pyc counts are operational evidence, not stable future
   cardinalities. Future reviewers must rerun a full source-derived preflight and
   cannot compare only totals.
5. Semantic field, possession, supported-feature, and identity candidates remain
   future artifacts. Their independently owned review and acceptance packets
   must pass before Bronze or downstream products can use them.
6. Source rights and local-only restrictions remain binding. PASS does not grant
   network reacquisition, external distribution, cloud use, or deployment.
7. Exact source minutes and per-90 denominators are unsupported; implementing
   them without a new accepted authority would violate R20.

## Final recommendation

**PASS.**

R20 is a standalone, constructive, fail-closed W04 schema/data/environment design.
The prior four-wrapper mismatch is truthfully closed by an exact full-tuple
selector, contained distinct alias roles, complete-byte template verification, and
two-token stable normalization. All current executable, lock/install, Packaging,
interpreter, source, editable, resource, environment, schema-cardinality,
projection, H1/H2, and pyc assertions independently reproduced. No contradiction,
ambiguous authority, circular preimage, stale schema route, host leakage into
stable identity, unverifiable current fact, or incomplete P0–P2 schema remained.

P0: **0**. P1: **0**. P2: **0**.
