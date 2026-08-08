# W04 Wyscout schema design independent review R11

## Decision

**REWORK — INVALID INDEPENDENT REVIEW RUN. No candidate verdict is issued for
R18.**

This R11 run cannot recommend `PASS`, and it also does not assert that the R18
candidate itself contains a P0, P1, or P2 design defect. The invalidating defect
is in the independent-review procedure: a reviewer command imported
`packaging` without `-B` and without a no-write bytecode environment. That command
created eleven `.pyc` files under the project `.venv`, outside the two paths
assigned to R11. It changed the live site bytecode census from the accepted
1,075-file baseline represented by R18 to 1,086 files before the bytecode
closure could be independently verified.

The master stopped the review immediately after disclosure. No cache file was
deleted, repaired, rewritten, touched, moved, or otherwise cleaned up. The R11
reviewer ran no further uv or Python command after the stop instruction. This
report preserves the invalidation evidence and the bounded work completed before
the incident; none of that partial work is promoted to independent acceptance.

The required disposition is a fresh, independently controlled review after the
master decides how to establish a truthful review baseline without allowing this
reviewer to mutate or clean the environment. The next reviewer must perform a
preflight census before any import and must make every Python observation
bytecode-denying from process start. Until that fresh review is complete, R18
has no valid R11 independent `PASS`.

## Review identity and boundary

| Item | Value |
| --- | --- |
| task | `W04-SCHEMA-DESIGN-REVIEW-01-R11` |
| phase | `W04` |
| role | independent data architecture reviewer |
| candidate | `reports/reviews/W04/wyscout-schema-design-R18.md` |
| candidate lines | 4,260 |
| candidate bytes | 228,182 |
| candidate SHA-256 | `d6f81a663a6e7db46e1059f2fee11521f0afde81a79cca3ec9d003d5954f8396` |
| assigned review output | `reports/reviews/W04/wyscout-schema-design-independent-review-R11.md` |
| assigned return output | `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R11.md` |
| final recommendation | `REWORK` because the independent run is invalid |
| candidate P0-P2 verdict | not issued |

The R11 packet allowed only the review and return paths. It forbade candidate,
configuration, orchestration, script, source, migration, test, data, run, Git,
provider, network, cloud, container, and deployment changes. The newly created
site bytecode is therefore a path-ownership violation even though `.venv` is
local environment state rather than a tracked product source. A reviewer cannot
change the evidence population it is required to recount and then claim that the
recount independently validates the earlier population.

The review did not perform provider acquisition, download, network access,
dependency resolution, `uv sync`, installation, product implementation,
configuration generation, data transformation, migration, local resource
creation, Git operation, remote operation, cloud action, CI action, endpoint
creation, container action, or deployment. It did not invoke any of the future
launcher, admission, or rebuild scripts. The invalidating write was CPython's
implicit bytecode-cache creation while importing already installed
`packaging` modules.

## Complete-read evidence before invalidation

Before the procedural failure was discovered, the reviewer read the full
4,260-line R18 candidate in consecutive chunks and inspected it as a standalone
authority. The read-first set also included:

- `AGENTS.md`;
- the R18 producer return and producer packet;
- the R18 master review packet and master verification;
- the R17 master review packet and master verification;
- the accepted 365-line W04 source schema profile;
- the 6,803-byte completion manifest;
- the current `primitives.py` and `evidence.py` contracts;
- the local-only threat model;
- `pyproject.toml`;
- `uv.lock`;
- both controlling HTML planning documents;
- and the subagent return template.

The controlling documents observed during this run had these identities:

| Artifact | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `reports/reviews/W04/wyscout-schema-design-R18.md` | 4,260 | 228,182 | `d6f81a663a6e7db46e1059f2fee11521f0afde81a79cca3ec9d003d5954f8396` |
| `reports/phase-gates/W04/source-schema-profile.md` | 365 | 18,574 | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` |
| `data/source/wyscout/v5/completion-manifest.json` | 1 | 6,803 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| `uv.lock` | 1,224 | 134,056 | `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca` |
| `pyproject.toml` | — | — | `963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b` |
| `../scouting-ml-production-blueprint.html` | 3,219 | 153,792 | `b55e624d27529761c937291ae1bc5d08de44120ace7739e87e0aad8a1000829a` |
| `../scouting-ml-agent-implementation-workflow.html` | 1,270 | 81,470 | `73fd051a7fb374733c552351d4f4dfe7b603c5cbdd9fdb7c3079895244d5b0d7` |

Complete reading is necessary but is not sufficient for acceptance. The
independent packet also required live mechanical reproduction of the complete
environment and bytecode closure. Because this run changed that live state, the
complete-read evidence cannot be converted into a valid final recommendation.

## Invalidation chronology

The relevant chronology is:

1. The reviewer completed the primary standalone-design read and the semantic
   route inspections.
2. Read-only and bytecode-denying reproductions validated the field roster,
   actor behavior, possession schema, current uv target, closed environment
   transformations, schema cardinalities, H1/H2 normalization, and evidence
   contract.
3. To reproduce `L == I`, the reviewer invoked locked/no-sync uv with a Python
   `-c` observer that imported `packaging.markers` and `packaging.utils`.
4. The command omitted Python `-B` and did not set
   `PYTHONDONTWRITEBYTECODE=1`.
5. The first `L == I` attempt reached its assertion with `L=83`, `I=82`, the
   additional unselected row being Windows-only `colorama==0.4.6`.
6. During import, CPython created eleven normal cache files in
   `.venv/lib/python3.12/site-packages/packaging/__pycache__/`.
7. Two bounded corrections to the dependency-closure parser also ran without
   `-B`; the eleven files already existed by then and retain one shared
   modification second.
8. The corrected closure calculation eventually reproduced `L=I=82`, with
   the editable root selected, `colorama` excluded, and the
   `cachecontrol[filecache]` extra pulling in `filelock`.
9. The later bytecode census reported 1,086 site pycs rather than the 1,075
   R18 current-root baseline. It reported the repository census unchanged at
   58 pycs in 19 cache directories, including 20 pytest-rewrite files.
10. A recent-file listing isolated exactly eleven new `packaging` pycs.
11. The reviewer disclosed the issue to the master and explicitly declined to
    delete or repair the files.
12. The master ordered an immediate stop to all candidate and mechanical probes
    and required R11 to return as an invalid independent review.
13. After that stop, only one essential read-only shell evidence command obtained
    stat metadata and SHA-256 values for the eleven already identified files.
14. No uv or Python command was run after the stop instruction.

There was no pre-probe R11 site census. The truthful “before” value is therefore
the accepted current-root baseline stated in R18 and reproduced by the immediately
preceding independent evidence, not a new R11 measurement made seconds before the
fault. That missing preflight is itself part of the review-procedure defect. The
post-command count of 1,086 and the exact eleven-file delta make the mutation
observable, but R11 must not overstate that it took an independent pre-mutation
snapshot.

## Exact causative command

The first command known to have imported the affected modules without bytecode
denial was:

```text
uv run --locked --no-sync python -c 'from pathlib import Path; import tomllib,sysconfig; from importlib.metadata import distributions; from packaging.markers import Marker; from packaging.utils import canonicalize_name; lock=tomllib.loads(Path("uv.lock").read_text()); env=None; L=set();
for p in lock["package"]:
 m=p.get("resolution-markers",[]); selected=not m or any(Marker(x).evaluate() for x in m);
 if selected: L.add((canonicalize_name(p["name"]),p["version"]))
site=Path(".venv/lib/python3.12/site-packages").resolve(); I={(canonicalize_name(d.metadata["Name"]),d.version) for d in distributions(path=[str(site)])}; print({"L":len(L),"I":len(I),"L_minus_I":sorted(L-I),"I_minus_L":sorted(I-L),"editable_root_in_L":("scouting-intelligence","0.1.0") in L}); assert L==I and len(L)==82'
```

The command was locked and no-sync, but those uv controls do not disable
CPython bytecode writes. The missing controls were `-B` and an already-set
`PYTHONDONTWRITEBYTECODE=1`. Importing `packaging.markers` and
`packaging.utils` loads the affected module family. Every new file has the same
recorded modification epoch, `1785412176`, rendered locally as
`2026-07-30T12:49:36+0100`. That shared second is consistent with the import
event.

The two later dependency-closure commands should also have used `-B`. They are
not needed to explain additional files because the identified set is exactly the
module closure created at the first observed second and no later timestamp is
present in the set. R11 does not claim filesystem audit causality beyond the
known command, imported module names, exact timestamp grouping, and exact
observed delta.

## Exact mutation evidence

All eleven paths are regular mode-`0644`, single-link files. They are:

| # | Path | Size | SHA-256 |
| ---: | --- | ---: | --- |
| 1 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/__init__.cpython-312.pyc` | 596 | `2af8dd75b52b02e67d92f2d00f72f93ac1bddf99f785553999292216a0bebd58` |
| 2 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/_elffile.cpython-312.pyc` | 4,976 | `26d9fddee205210e1631e6ba06688cd2a7de470d01bc08d92f7ee41223258a8b` |
| 3 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/_manylinux.cpython-312.pyc` | 9,895 | `caf5c738d3974432722a72a4163326b7df9a3db56a1ea7ccbc6987e72af43cea` |
| 4 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/_musllinux.cpython-312.pyc` | 4,604 | `1a83fa91aa59e1607fbbbda2dc6a9fd595237e5ce2520b1a32d8cf86cf62c7ef` |
| 5 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/_parser.cpython-312.pyc` | 15,613 | `91da8b4288ef1141055033b0385a169fd9ec1cf5d1983506ff197cede9feb584` |
| 6 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/_tokenizer.cpython-312.pyc` | 8,488 | `1d5b29d5c5d67eddfecd33e4175d6cb10146c46d3ebd96ef9439131f52fa4a94` |
| 7 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/markers.cpython-312.pyc` | 17,487 | `73c47d51abc57ee31e45147ef4b458ad4f41c3a76b9b6ebc21dc0ef738a8c6bd` |
| 8 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/specifiers.cpython-312.pyc` | 75,787 | `e384d9c322c39fc43c2b724d757fadfa0a0d5b960d3e51741109b0d3b9e766f3` |
| 9 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/tags.cpython-312.pyc` | 37,392 | `235d0486904373dd141b2c35797dcd06a7c2a5bfd8b9cecf835051668a13fd14` |
| 10 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/utils.cpython-312.pyc` | 11,092 | `b5fd333d2c945ec569dab50e95e63a239982c32f03adedc991446802cef18150` |
| 11 | `.venv/lib/python3.12/site-packages/packaging/__pycache__/version.cpython-312.pyc` | 41,813 | `070892ecb7a058ff37c08097fd752e64d4d556fce70f1f4d84ce64e0dc35f5ae` |

For every row:

```text
mtime epoch = 1785412176
mtime local = 2026-07-30T12:49:36+0100
mode = 0644
link count = 1
kind = regular file
```

The exact census delta recorded at discovery was:

```text
accepted current-root site baseline in R18: 1,075
R11 post-import site observation:          1,086
difference:                                   +11

site pytest-rewrite files after import:       112
repository pycs after import:                  58
repository __pycache__ directories:            19
repository pytest-rewrite files:               20
```

The new paths are ordinary current-tag names for installed `packaging` sources.
Their appearance does not invent a new source owner, and it does not by itself
demonstrate that R18's source-derived classification algorithm is wrong.
However, classification eligibility is not the issue. The review packet required
the reviewer to inspect and reproduce the current evidence while changing only
two report paths. Creating validly classifiable cache files still changes the
operational evidence population, invalidates an exact current-root observation,
and defeats independence.

No repository pyc changed according to the post-incident census. The 58/19/20
repository values remained exactly the values stated by R18. No evidence was
found of a source, test, configuration, data, report, or Git mutation caused by
the import. R11 nevertheless does not claim a complete no-other-write proof
because it did not take a preflight whole-tree descriptor snapshot. It limits
the claim to the exact detected eleven-file delta and the unchanged repository
pyc counts.

## Why no candidate verdict can be issued

R18 carefully separates stable source authority from operational bytecode state.
That separation does not rescue this review. The independent packet required all
of the following at the same time:

1. independent reproduction of the current environment;
2. inspection of the exact current site and repository pyc census;
3. proof that the candidate remains design-only;
4. changes confined to two report paths;
5. no cleanup or environment repair;
6. and a `PASS` only if no P0-P2 defect remains.

After the import, R11 no longer had an untouched current environment to inspect.
It could inspect the new 1,086-file state, but that would not independently
reproduce the 1,075-file current observation written in R18. It could describe
the eleven-file difference, but it could not know from an R11 preflight snapshot
that no other state had already drifted. It could ask to delete the eleven files,
but deletion would be an unauthorized cleanup and would itself violate the
no-repair boundary. It could ask the candidate to revise the observed count, but
that would turn reviewer-caused state into candidate authority and would require
an edit outside R11 ownership. None is a valid independent-review path.

The correct fail-closed response is therefore procedural invalidation. The
candidate is neither accepted nor rejected on its merits by R11. A subsequent
independent packet may reach `PASS` or find a candidate defect, but it must start
from a master-established baseline and must not rely on R11's changed
environment as unexamined authority.

This distinction is material:

- **Not claimed:** “R18 has a P1 because it says 1,075 and the reviewer now sees
  1,086.”
- **Claimed:** “R11 cannot adjudicate that assertion because R11 itself caused
  the eleven-file delta before taking the required census.”
- **Not claimed:** “The eleven pycs are unsafe or unclassifiable.”
- **Claimed:** “Creating them exceeded reviewer path ownership and changed the
  evidence being independently reviewed.”
- **Not claimed:** “Deleting the eleven files would make the review valid.”
- **Claimed:** “This reviewer has no authority to delete them, and a fresh
  independent run is required even if the master later establishes a clean or
  newly accepted baseline.”

## Work reproduced before invalidation

The following sections record bounded partial results for auditability. They are
not a substitute for a valid final review and do not authorize implementation.

### Exact source and field roster

The R18 normative machine roster was parsed into exactly 119 unique ordered
`(record_kind,json_path)` pairs. The accepted profile's JSON tables and two CSV
tables were parsed independently, normalized only by the design's stated
record-kind names, and regrouped into the R18 category order. Exact equality was
reproduced:

```text
competition       10
team              11
player            26
match             47
action            18
event-taxonomy     4
tag-taxonomy       3
total             119
```

There was no duplicate roster pair and no profile pair outside the roster. The
two CSV categories use the design's `$.<column>` representation. The source
profile and completion-manifest digests matched the frozen values in R18.

The field decision schema contains the exact eight row keys and three decision
states. The registry is a parsed-YAML restatement of the same 119 ordered rows,
not a second decision point. Physical YAML and canonical parsed-JSON digests have
separate names. The review record binds the already frozen decision and registry
and has a sole canonical machine record inside its Markdown; the acceptance
binds both that record digest and the complete physical review digest. The
reviewed dependency uses the canonical registry digest, while the physical YAML
digest remains resource evidence.

The digest graph inspected before invalidation was acyclic:

```text
frozen inputs
  -> decision canonical bytes/digest
  -> registry parsed canonical bytes/digest
  -> independent review record and physical review digest
  -> acceptance canonical bytes/digest
```

No candidate artifact contains its own digest or a future review or acceptance
digest. Acceptance requires an independent `PASS`, unchanged candidate evidence,
the route-fixed IDs, and closed clocks.

### Actor contract and four authority routes

Locked uv validation of the existing `ActorId` reproduced:

```text
type StrictUuid = Annotated[UUID, Strict()]
type ActorId = StrictUuid
```

A canonical lowercase RFC 4122 JSON string validated to an in-memory
`uuid.UUID`. A Python-mode string failed strict validation. `master.agent`,
surrounding whitespace, compact spelling, and braced spelling failed. An
uppercase UUID could be parsed by the JSON UUID parser but reserialized to
lowercase, so the design's required input-bytes equality rejects it. This is why
the explicit canonical reserialization equality is necessary in addition to
the Pydantic primitive.

The common route protocol applies to FIELD, POSSESSION, SUPPORTED_FEATURE, and
IDENTITY. Each `decided_by`, `reviewed_by`, and `accepted_by` is the existing
strict UUID `ActorId`. The required cross-artifact rules are:

```text
accepted_by == decided_by
reviewed_by != decided_by
reviewed_by != accepted_by
decided_at <= reviewed_at <= accepted_at
```

The decision packet chooses the candidate. The reviewer has candidate read-only
authority. The accepting master can accept only an unchanged candidate with a
valid independent `PASS`. No packet self-approves.

### Possession closure

Mechanical extraction of the possession predicate produced exactly twelve
required fields, in the declared order:

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

The closed union contains exactly:

```text
CONTROL
RESTART
DEAD_BALL
CONTESTED
NON_CONTROL_ADMIN
UNMAPPED
```

Every row, including `UNMAPPED`, has all twelve keys. Only the three declared
fields can be null under the combination table. Required and forbidden tags are
sorted, unique, disjoint nonnegative-integer arrays. Each row actor equals the
top-level possession decision actor. The taxonomy predicates reproduce every
complete decision predicate under canonical JSON, including actor, rationale,
tags, control flags, and attachment values.

The explicit `UNMAPPED` combination is `NONE/false/false/null/null` for team
source, open, close, dead-ball attachment, and contested attachment. It retains a
nonempty rationale and strict actor. It cannot open, close, buffer, or attach
control. The taxonomy-byte equality and negative suite reject omission,
defaulting, mistyping, an illegal combination, actor inequality, field-route
drift, label matching, or construction before acceptance.

### Packet paths and ownership

The field decision packet owns exactly:

```text
reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json
configs/schema/wyscout-v5-field-registry-v1.yaml
tests/contracts/test_wyscout_field_registry_authority.py
reports/reviews/W04/returns/W04-FIELD-SEMANTIC-DECISION-01-R1.md
```

The previously rejected alternate test spelling is absent from R18. Field,
possession, supported-feature, and identity decision/review/acceptance paths are
separate. For every route, the decision packet owns candidate and its contract
test, the independent reviewer owns only review and return, and the accepting
master owns only acceptance and return. Later product, admission, launcher,
manifest, and rebuild responsibilities are separately serialized.

### Current uv admission and closed environment maps

Before invalidation, the current uv authority was reproduced:

```text
normal command resolution:
  /opt/homebrew/bin/uv

uninterpreted logical link target:
  ../Cellar/uv/0.9.21/bin/uv
  26 bytes

logical entry:
  symlink
  mode 0755
  one link

resolved physical entry:
  /opt/homebrew/Cellar/uv/0.9.21/bin/uv
  regular non-symlink
  mode 0555
  size 41,617,552
  one link

physical SHA-256:
  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f

normal logical execution version:
  uv 0.9.21 (Homebrew 2025-12-30)
```

The raw target resolves in exactly one contained hop under `/opt/homebrew` and
the final target is not another symlink. Normal literal-token execution preserves
the logical spelling in `UV`; direct physical execution changes `UV` to the
Cellar path. The direct-physical negative control therefore supports the design's
prohibition on accepting logical and physical spellings interchangeably.

The exact outer map reproduction began from twenty literal deterministic values
and nine operational substitutions. At Python first instruction it had exactly
29 names and:

```text
UV=/opt/homebrew/bin/uv
UV_RUN_RECURSION_DEPTH=1
PATH=<project>/.venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin
site imported = false
sys.flags.no_site = 1
sys.dont_write_bytecode = true
```

Separate admission and rebuild child probes each produced exactly 32 names and
the correct role. Both preserved the logical `UV`, incremented recursion depth
to one, and prepended exactly one venv-bin component. The role, entrypoint FD,
result FD, nonce, and role prefix were present. The outer launcher FD,
bootstrap tuple, and pre-insertion `W04_CHILD_INPUT_B64` were absent.

Those map probes used `-S -B` and did not cause the later incident. The incident
was the separate normal-site dependency-closure parser whose exact command is
recorded above.

### Root-independent uv authority and H1/H2

R18's stable tuple is version
`w04-local-control-bootstrap-v4`. It uses logical-launch, installation-root, and
physical-executable roles rather than actual paths. The stable tuple block
contains neither `/opt/homebrew` nor the current raw target. The actual logical
path, installation root, raw target bytes and length, and physical path occur in
the operational current-host receipt only.

A synthetic H1/H2 reproduction constructed two unequal operational receipts:

```text
H1 logical path:       /alpha/tools/bin/uv
H1 installation root: /alpha/tools
H1 raw target:         ../release/uv
H1 physical path:      /alpha/tools/release/uv

H2 logical path:       /beta/local/bin/uv
H2 installation root: /beta/local
H2 raw target:         ../versions/current/uv
H2 physical path:      /beta/local/versions/current/uv
```

Both passed relative-target, one-hop containment, and final-file checks while
sharing the exact physical mode, size, digest, and version authority. Complete
value replacement with the four fixed roles produced equality for:

```text
normalized uv authority
normalized outer environment
normalized admission environment
normalized rebuild environment
environment digest
canonical code-manifest bytes
code-manifest SHA-256
pre-build projection bytes
build ID
```

The synthetic proof build digest was
`01e891965d3dd83858c65f4d63cb9e5d27a6e1400f00a5ec894bfee7afc447b7`.
That value is test-only evidence and not a W04 product build identity. The
important result is equality after complete validated-value substitution and
inequality of the operational path spellings before substitution.

The inspected version sequence was:

```text
w04-local-control-bootstrap-v4
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
w04-code-environment-admission-v14
```

### Input, result, projection, and component cardinalities

Mechanical extraction reproduced unique key sets:

```text
common child input envelope:        16
admission inputs:                    8
rebuild inputs:                     10
rebuild invocation:                 25
stable pre-build projection:        25
admission component proofs:         20
```

The invocation/projection intersection is exactly 24. The projection-only key is
`schema_version`; the invocation-only key is `build_id`. The projection key list
is in Unicode code-point order.

The launcher constructs and hashes the exact projection once. It then copies the
24 common values and inserts the resulting `build_id` into the invocation.
Rebuild reconstructs the projection by removing only `build_id` and inserting
only the projection schema version. Operational run IDs, prefix paths, receipt
paths, layer paths, descriptors, nonces, transport hashes, clocks, and output
digests remain post-hash. No completed invocation is hashed into its own
identity.

### EvidenceDependency and temporal closure

The existing contract was imported with bytecode denial and reproduced exactly:

```text
kind
dependency_id
digest
observed_at
available_at
```

Enum order was:

```text
source_manifest
identity_evidence
feature_schema
model_artifact
retrieval_index
```

The report-local aliases `dependency_kind`, `manifest_id`, and
`manifest_sha256` were rejected. Equality of either `observed_at` or
`available_at` with `feature_cutoff_ts` was rejected. R18 requires one source
manifest, one identity evidence row, and three distinct feature-schema rows in
the accepted enum/UUID/digest/clock ordering. Watermark is the exact maximum
availability and is strictly before cutoff. The accepted lineage hash is
canonical over those exact rows.

### Lock and installed distribution closure

The final dependency reachability calculation, before the incident was detected,
produced:

```text
selected lock rows L = 82
installed rows I     = 82
L minus I            = empty
I minus L            = empty
editable root        = scouting-intelligence==0.1.0, source editable "."
Windows colorama     = not selected on current host
cachecontrol extra   = filecache
```

The first failed parser counted all universal package records and therefore
temporarily included `colorama==0.4.6`; the second omitted the requested
`cachecontrol[filecache]` optional dependency and therefore missed
`filelock==3.32.0`. The third parser traversed the root's eight selected dev
groups, applied dependency markers, and propagated requested extras. It reached
the correct 82-row closure.

This successful logical result does not cure the procedural failure. The parser
that reached it was part of the same invalid run and used the environment after
the first import had created bytecode.

### Installed `.pth`, executable, and interpreter evidence

The site root had exactly the three declared `.pth` files:

```text
_virtualenv.pth
a1_coverage.pth
scouting_intelligence.pth
```

They correspond to uv bootstrap, conditional coverage bootstrap, and the
root-bearing editable path. R18 denies them during no-site startup and verifies
their bytes and normalized authority before any intentional import.

Parsing installed RECORD executable rows reproduced:

```text
total executable rows: 35
distinct owners:       21
class E:               33
class P:                1
class W:                1
```

The class-P row was `pip` owning `pip3.12`. The class-W row was `ruff` owning
`ruff`. Every class-E basename was a declared console or GUI entry point of its
owner.

The venv retained exactly three `python*` aliases:

```text
python     -> /Users/adrian/.local/share/uv/python/
              cpython-3.12.12-macos-aarch64-none/bin/python3.12
python3    -> python
python3.12 -> python
```

All three resolved to the same regular physical interpreter with mode `0755`,
size 49,968, and SHA-256
`cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79`.
The actual root-bearing alias text is operational; the three-role topology and
physical interpreter identity are stable.

### Resource, source, product, and publication inspection

R18 declares exactly seventeen local resource paths: four future candidate
configuration files, twelve future decision/review/acceptance authority files,
and the accepted source profile. Each eventual resource row binds exact path,
physical digest, size, mode, purpose, parser/schema version, and authority link.
There is no directory shorthand or eighteenth resource.

The strict source seam begins from the completion manifest and opens only exact
declared direct objects and separately durable admitted members. Archive objects
are digest evidence rather than runtime fallback containers. Provider payloads
cannot select record family; the project envelope owns the seven record kinds.
The design keeps the four excluded scopes outside authority and forbids directory
scanning, newest-file selection, alternate extraction, or provider/network
fallback.

Identity authority uses fixed source-kind namespaces and canonical decimal source
IDs. Missing, malformed, zero, duplicate, absent-master, and reviewed
supersession states remain explicit. Name-only matching is forbidden. The ruleset
route is accepted before identity projection; the immutable bundle separately
binds queue, accepted corrections, current index, and historical rows.

Football products remain count/evidence based. Player minutes, per-90 rates,
continuous-time features, role-inferred products, provider-native possession,
outcome-dependent features, value-model features, and any unsupported denominator
remain suppressed or unavailable. Gold coverage stays six-dimensional rather
than collapsed into one permissive score. Neutral role context is exact and does
not infer player position or tactical role.

Bronze preserves known raw evidence and quarantines fixed unknown envelopes.
Silver owns exact normalized facts and identity outcomes. Gold uses accepted
feature and product contracts only. Serializers have exact paths, schemas,
partitioning, sort keys, decimal/timestamp rules, and deterministic physical
settings. Unknowns cannot silently become feature permission.

The launcher is sole writer of the immutable code/environment manifest and sole
calculator of build identity. Rebuild owns only the invocation receipt and calls
the named layer writers. The exact ledger serializes semantic decisions,
independent reviews, acceptances, identity corrections, local-control admission,
build projection, rebuild, two-root proof, gates, and two local commits.

These inspections found no candidate P0-P2 before invalidation. That statement
means only “none had emerged yet,” not “none exists.” The remaining bytecode
closure, final integrated contradiction search, packet acceptance commands, and
post-write independent readback were not validly completed.

## Finding

### P1-R11-PROCEDURE-01 — reviewer mutated the operational evidence population outside assigned ownership

**Severity:** P1 for review validity; not classified as a candidate R18 defect.

**Evidence:** The exact command above imported installed `packaging` modules
without bytecode denial. Eleven new regular current-tag pycs share the exact
mtime second `2026-07-30T12:49:36+0100`. Their exact paths, sizes, modes, link
counts, and digests are listed above. The site census observed afterward was
1,086, a delta of eleven from R18's 1,075 current-root baseline. Repository pyc
counts remained 58/19/20.

**Impact:** The reviewer exceeded the two-path ownership boundary and changed the
live evidence required for independent reproduction. R11 lacks a pre-import
snapshot and cannot prove the exact candidate current-root census against an
untouched root. Any `PASS` would therefore be unsupported. Deleting or repairing
the files would be another unauthorized mutation and would not retroactively
restore independent chain of custody.

**Required bounded rework:** The master must close this R11 run as invalid and
establish the baseline for a newly dispatched independent review. The new packet
must:

1. use a reviewer that did not perform the candidate work or this invalid run;
2. take a read-only preflight site/repository pyc census before any Python import;
3. require `-B` and `PYTHONDONTWRITEBYTECODE=1` for every Python observation,
   including helper parsers;
4. prefer `-S -B` where the probe does not require installed packages;
5. if installed packages are required, set no-write controls before interpreter
   startup and verify them at first instruction;
6. use locked/no-sync uv only;
7. compare pre/post environment and pyc inventories;
8. stop on any unexpected write rather than cleaning it;
9. independently rerun every R11 reproduction and the two packet acceptance
   commands;
10. and issue `PASS` only after the entire candidate and current environment
    close with zero candidate P0-P2 findings.

This report intentionally does not tell the master to delete the eleven files,
rebuild `.venv`, change `uv.lock`, update R18's count, or accept 1,086 as the new
baseline. Those are master-level decisions outside R11 ownership. No architecture,
project root, dependency policy, provider/rights authority, or local-only boundary
change is requested.

## Checks not completed after invalidation

The following work must be rerun from the fresh baseline:

- complete site pyc classification against every installed source row;
- exact 962-normal/112-pytest/optional-six current-root decomposition or its
  master-approved truthful replacement;
- source-complete stable pyc map reproduction;
- exact four optional orphan predicates and no fifth orphan;
- first/final in-place byte equality under a valid no-write review harness;
- final review of executable read denial, prefix emptiness, and no-cleanup
  evidence as one integrated closure;
- final cross-document contradiction scan after every mechanical result;
- final design-only absence check for all future launcher/admission/rebuild
  artifacts and parent-workspace report paths;
- proof that only the two R11 report paths changed during the fresh review;
- the report-size/recommendation acceptance command;
- `scripts/verify_local_only.py`;
- and a final independent readback of the report and return.

The invalid R11 report does not run either packet acceptance command. The master
explicitly ordered no more uv or Python commands. Recording an unrun check as
passing would be false.

## No-cleanup statement

R11 did not remove any of the eleven files. It did not truncate them, rewrite
their headers, change their modes, change their times, move them, quarantine them,
or recreate the virtual environment. It did not touch the containing
`__pycache__` directory after the implicit CPython writes, except for read-only
listing/stat/digest operations needed to preserve evidence.

R11 did not run `rm`, `unlink`, `find -delete`, `uv sync`, `uv venv`, a formatter,
a cache purge, a Git restore/reset/checkout, or an environment repair. It did not
ask another agent to perform cleanup. It did not delegate any part of this task.

The files remain available for master inspection. Their continued presence is
not represented as an approved environment state by this report.

## Residual risk

1. R11 did not take a whole-environment preflight snapshot, so its exact
   eleven-file attribution is based on the known command, matching module set,
   one shared timestamp, and count delta rather than a before/after inode ledger.
2. The files are classifiable normal pycs for accepted installed sources, but
   R11 did not complete the source-owner mapping after the stop order.
3. A later review that merely starts from 1,086 without a master decision could
   accidentally convert reviewer-caused state into authority.
4. A later review that deletes the files without authorized provenance could
   erase the evidence and still fail to restore independent chain of custody.
5. R18 is deliberately dense. Although no candidate P0-P2 had emerged before the
   incident, only a full fresh rerun can support a merits verdict.
6. The future same-trust-domain launcher replacement residual documented by R18
   remains a design residual to be re-reviewed; this invalid run does not accept
   it.
7. No provider acquisition or product build occurred, so this invalidation does
   not establish anything about eventual data bytes, serializer output, two-root
   equality, or production gate evidence.

## Recommendation

**REWORK the independent review process. Treat R11 as invalid and non-accepting.**

Do not use this report as evidence that R18 passed or failed on its merits. Keep
the candidate read-only, preserve the incident evidence, and dispatch a fresh
bounded independent review after the master establishes the review baseline and
no-write harness. The fresh reviewer must repeat the complete standalone read and
all semantic, environment, packaging, executable, bytecode, resource, temporal,
projection, H1/H2, design-only, and local-only checks.

R11 reports one P1 review-procedure finding, zero adjudicated candidate findings,
and no candidate recommendation. Its workflow recommendation is `REWORK`.

