# W04 Wyscout v5 schema design — fresh independent review R12

Review task: `W04-SCHEMA-DESIGN-REVIEW-01-R12`  
Candidate: `reports/reviews/W04/wyscout-schema-design-R19.md`  
Candidate revision: R19  
Reviewer role: fresh independent data-architecture reviewer  
Review date: 2026-07-30  
Recommendation: **REWORK**

## 1. Decision

R19 must not receive an independent PASS. I found one P1 candidate defect and no
P0 or P2 defects.

The defect is concrete and reproducible. R19 makes the existing 35-row installed
executable census a mandatory, read-only admission input. It says all 33 Class-E
console/gui wrappers must be byte-for-byte instances of a template whose first
line names the canonical `.venv/bin/python` alias. It explicitly rejects
`.venv/bin/python3`. Four currently installed, singularly RECORD-owned Class-E
wrappers instead name `.venv/bin/python3`: `detect-secrets`,
`detect-secrets-hook`, `httpx`, and `pip-licenses`. Their modes, link counts,
sizes, bytes, hashes, RECORD digests, owners, and entry-point targets are all
otherwise valid and were reproduced below. The bytes after the first LF are
exactly the required deterministic template; the sole byte-level disagreement is
the forbidden `python3` first-line alias.

This is not an incidental operational receipt difference. R19 lines 3089 and
3097 declare `python` to be the canonical generated-wrapper alias and permit only
that alias. Lines 3121–3142 require the complete installed bytes to equal the
reviewed template and explicitly say the first line must use `python`, “not
`python3`.” Lines 3034–3058 make every RECORD `../../../bin/` row part of the
complete admission census and say a changed or nonconforming row fails. The four
affected names are themselves enumerated in the positive Class-E table at lines
3152, 3154, and 3163. Admission is offline/read-only and may not rewrite the
wrappers. R19 also states that a fresh locked sync changing census membership,
ownership, class, or count stops the work rather than updating the design
implicitly. Consequently, a faithful implementation against the current admitted
root cannot pass the executable admission stage.

Recommendation is therefore REWORK even though the no-bytecode review harness
itself remained intact. A passing replacement must make the executable authority
truthful and root-independent without repairing this environment during review.
The bounded correction is to do one of the following under separately controlled
master authority:

1. revise the stable executable contract to bind the exact current per-row
   shebang-alias classes, including the four `python3` rows and the already
   admitted safe `python3 -> python` alias chain; define exact normalization,
   two-root equality, negative tests, manifest preimage impact, and the required
   stable schema-version change; or
2. establish a separately authorized, reproducible environment-construction
   result in which all 35 exact rows satisfy the claimed bytes, then refresh every
   dependent exact digest/evidence and independently review that new state.

R19 cannot merely call the current four bytes valid, post-hoc realpath the
shebang, silently broaden `python` to “any equivalent alias,” run sync, or rewrite
the wrappers. Each of those would contradict the current closed contract or the
packet’s no-repair/no-sync boundary.

## 2. Finding inventory

| ID | Severity | Status | Summary |
| --- | --- | --- | --- |
| R12-P1-01 | P1 | OPEN | Four admitted Class-E wrappers use the explicitly forbidden `.venv/bin/python3` shebang, so R19’s read-only executable admission cannot pass against the current locked root. |

P0 count: **0**  
P1 count: **1**  
P2 count: **0**

No finding is based on the invalid R11 merits conclusion. R11 was used only as
incident provenance for the eleven Packaging pycs, as directed by R12. All merits
checks and the wrapper defect were reproduced afresh.

## 3. Exact P1 evidence

### 3.1 Controlling candidate requirements

The following R19 statements combine to make the mismatch admission-blocking:

- lines 3034–3042 define `B` as every installed RECORD row beginning exactly
  `../../../bin/`, require a singular safe regular mode-`0o755` target and forbid
  unowned, aliased, unsafe, or escaping rows;
- lines 3044–3053 require the disjoint census
  `B = E ∪ P ∪ W`, `|B|=35`, `|E|=33`, `|P|=1`, `|W|=1`, and 21 owners;
- lines 3055–3058 say a missing, changed, or otherwise invalid row fails and a
  fresh locked sync that changes the census stops work rather than changing the
  design implicitly;
- line 3089 says `python` is the canonical uv POSIX wrapper-shebang alias;
- lines 3097–3103 say only `python` is permitted in a generated-wrapper shebang
  and bind that decision into the stable alias topology;
- lines 3121–3136 require every Class-E wrapper’s actual bytes to equal the
  template whose first line is
  `#!<project-root>/.venv/bin/python\n`;
- lines 3138–3142 explicitly reject `python3`, the launch-time executable
  spelling, `/usr/bin/env`, an argument, another root, or another alias;
- lines 3152, 3154, and 3163 positively enumerate the four affected executables
  within the exact 33-name Class-E roster;
- lines 3232–3251 bind all 35 normalized rows into
  `w04-installed-executable-census-v2` and deny reads/executes after guard
  installation; and
- lines 3590–3710 make that executable census part of the immutable stable
  code/environment manifest and admission rechecks.

The separate statement at lines 3090–3096 that the exact uv child launches
operationally report the admitted `python3` alias does not rescue the wrappers.
R19 deliberately distinguishes process launch observation from generated-wrapper
authority, and line 3138 explicitly excludes `python3` in the latter.

### 3.2 Reproduced complete mismatch rows

All four files are regular, non-symlink, link-count-one, mode-`0o755` files. Each
is singularly owned by the named installed RECORD. The RECORD URL-safe unpadded
SHA-256 decodes to the complete-file SHA-256 shown here. The complete bytes after
the first newline equal the R19 deterministic template generated from the listed
entry-point target.

| executable | owner | RECORD row | target | bytes | mode / links | actual SHA-256 | RECORD digest |
| --- | --- | --- | --- | ---: | --- | --- | --- |
| `.venv/bin/detect-secrets` | `detect-secrets==1.5.0` | `../../../bin/detect-secrets` | `detect_secrets.main:main` | 380 | `0o755` / 1 | `16c1dcee3bcc2078fc6d4df7c0c85db6d043ab3bff5b40f8a13eea19e28aff3f` | `sha256=FsHc7jvMIHj8bU33wMhdttBDqzv_W0D4oT7qGeKK_z8` |
| `.venv/bin/detect-secrets-hook` | `detect-secrets==1.5.0` | `../../../bin/detect-secrets-hook` | `detect_secrets.pre_commit_hook:main` | 391 | `0o755` / 1 | `c3535b96dea57e7a88ab48961f74e51c07b019103b89a49c3f71da4cfbda5010` | `sha256=w1Nblt6lfnqIq0iWH3TlHAewGRA7iaScP3HaTPvaUBA` |
| `.venv/bin/httpx` | `httpx==0.28.1` | `../../../bin/httpx` | `httpx:main` | 366 | `0o755` / 1 | `7f7d4f633504d3f62f33335a9630e5bb4240989c9fb777b4a57e9d5c98fa394d` | `sha256=f31PYzUE0_YvMzNaljDlu0JAmJyft3e0pX6dXJj6OU0` |
| `.venv/bin/pip-licenses` | `pip-licenses==5.5.5` | `../../../bin/pip-licenses` | `piplicenses:main` | 372 | `0o755` / 1 | `b563dfd0133f2295a703e09a820fd4b133fd1d2c438150dc6c42ec7d62e8b52f` | `sha256=tWPf0BM_IpWnA-Cagg_UsTP9HSxDgVDcbELsfWLotS8` |

For each row, the actual first line is exactly:

```text
#!/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence/.venv/bin/python3
```

For each row, R19 requires exactly:

```text
#!/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence/.venv/bin/python
```

The mismatch is therefore neither a parser artifact nor a difference in body
generation. The review helper independently:

1. enumerated every `../../../bin/` row from every immediate installed
   `.dist-info/RECORD`;
2. verified safe five-component row grammar;
3. decoded and compared each RECORD SHA-256 and size;
4. verified target regularity, final-component non-symlink status, link count and
   executable mode;
5. parsed installed `entry_points.txt` without importing the owned package;
6. classified the exact row as E, P, or W;
7. generated R19’s complete expected wrapper bytes from owner target; and
8. for the four mismatches, proved that bytes after the first LF are identical to
   the expected template.

The same complete census reproduced the remaining design facts:

```text
total B rows = 35
Class E      = 33
Class P      = 1
Class W      = 1
owners(B)    = 21
Class P      = pip==26.1.2 / pip3.12
Class W      = ruff==0.16.0 / ruff
```

Thus the finding does not dispute membership, ownership, class counts, entry-point
targets, Ruff bytes, pip alias derivation, or target modes. It rejects only R19’s
false assertion that all 33 present Class-E bytes use the sole permitted first
line.

### 3.3 Impact

The impact is P1 because it blocks the required implementation path rather than
merely weakening documentation:

- admission must verify every current `B` row before product execution;
- a byte mismatch is a mandated failure;
- admission cannot edit the wrapper;
- the review packet forbids environment repair or sync;
- the runtime design itself is offline and no-sync;
- treating `python3` as equivalent after reading it is explicitly forbidden;
- the stable executable census digest feeds the environment manifest;
- the environment manifest feeds code-manifest identity;
- the code manifest is required before pre-build projection and build ID;
- without a passing admission manifest, the launcher cannot construct a valid
  build ID or invoke the sole rebuild child.

The defect therefore prevents deterministic Bronze-to-Gold execution from
reaching its first build-authority boundary.

## 4. No-write review harness and chain of custody

### 4.1 Ordering

I followed the R12 ordering:

1. read only `AGENTS.md` and the R12 packet with shell tools;
2. before opening R19 or running Python, performed a shell-only site/repository pyc
   census and inventory;
3. read every `read_first` artifact and all 4,357 R19 lines;
4. ran only root-local `uv run --locked --no-sync` helpers;
5. set `PYTHONDONTWRITEBYTECODE=1` before every uv invocation;
6. used `python -S -B` unless installed packages were needed;
7. where installed packages were needed, used `python -B` and made
   `import os,sys; assert sys.dont_write_bytecode and
   os.environ.get("PYTHONDONTWRITEBYTECODE") == "1"` the first instruction before
   another file-backed import;
8. did not sync, clean, repair, delete, quarantine, recreate, or mutate `.venv`;
9. did not run provider/network, Git, implementation, configuration, data,
   migration, cloud, container, deployment, or public-endpoint actions; and
10. reserved the identical shell postflight for immediately after the last
    bounded review command.

The first attempted uv helper was denied before Python execution because the
sandbox would not permit uv to read an existing local cache path. It produced no
candidate result and no filesystem write. The retry received read permission for
the same local locked/no-sync operation; it did not authorize network, sync, or
mutation. Two later helpers intentionally reached assertions while the local
parsers were being corrected: one used the completion-manifest key name
`archive_members` instead of the actual `admitted_archive_members`, and one
canonicalized the editable-root version inconsistently. Both already had `-B`,
the required environment setting and first-instruction assertion; neither wrote
bytecode or changed candidate/environment state. The executable helper’s first
assertion at `detect-secrets` was the finding event, not a review-procedure
failure. A follow-up read-only helper bounded all four mismatches.

### 4.2 Preflight construction

The shell inventory enumerated:

- every regular `*.pyc` under
  `.venv/lib/python3.12/site-packages`;
- every regular repository `*.pyc` outside `.venv` and `.git`;
- repo-relative traversal role and path;
- size;
- numeric mode;
- hard-link count;
- modification epoch;
- first four bytes in hexadecimal;
- complete SHA-256; and
- deterministic metadata, content, and combined rows.

The inventory was sorted under the same shell locale and hashed separately for
site, repository, and combined sets. No Python import occurred before it.

### 4.3 Exact preflight inventory

```text
site count                         1086
repository count                     58
site total pyc bytes           20,047,587
repository total pyc bytes       1,475,178

site metadata inventory SHA-256
d2222a7b384c9e4c5fe4c6737cba4a072625f5c4d6415ceb405527b31e45be9d

repository metadata inventory SHA-256
64f99e2471b975e734ce86ce4cb340980880508b1755cca92442207e07f29a5b

global metadata inventory SHA-256
b722dd71e920f1012a3a242b0ac8fb7b979b465db9494e3e0b175150bebd9532

site content inventory SHA-256
2eb2707bd4cd81f8776445bdc9161a54abcd9c39402b1bf879c8618c5da855f5

repository content inventory SHA-256
d48422a79784c29c0e88d1a63740aed9baeae5cc3024eee5efcfc56150550e36

global content inventory SHA-256
5753ab3909dea93f8819e0e0aa9f545489d8075b37a19dfcf08abd9199bdf034

site combined inventory SHA-256
f33532cbf1f1dcdc50b47dbdb2e1516b9282118a920d8a94e82a23a947ef9109

repository combined inventory SHA-256
cbe0d8fa43a937721ccf6c58cd20c630f8e92e5b8d3cd81687ee7de08f18ce5c

global combined inventory SHA-256
5a332924c77f4418cee2b1024cca2e235d0f3c837c077de9cc451b666ef92d96
```

The metadata and content inventories are separate on purpose. The combined rows
bind all selected metadata and complete content evidence so that equal counts or
equal content alone cannot hide a path, mode, link, mtime, magic, or byte change.

### 4.4 Postflight

Immediately after the exact local-only verifier—the last bounded review
command—I repeated the identical shell census and inventory construction. It
passed every equality assertion:

```text
postflight status                  PASS_IDENTICAL
site count                         1086
repository count                     58
site total pyc bytes           20,047,587
repository total pyc bytes       1,475,178

site metadata inventory SHA-256
d2222a7b384c9e4c5fe4c6737cba4a072625f5c4d6415ceb405527b31e45be9d

repository metadata inventory SHA-256
64f99e2471b975e734ce86ce4cb340980880508b1755cca92442207e07f29a5b

global metadata inventory SHA-256
b722dd71e920f1012a3a242b0ac8fb7b979b465db9494e3e0b175150bebd9532

site content inventory SHA-256
2eb2707bd4cd81f8776445bdc9161a54abcd9c39402b1bf879c8618c5da855f5

repository content inventory SHA-256
d48422a79784c29c0e88d1a63740aed9baeae5cc3024eee5efcfc56150550e36

global content inventory SHA-256
5753ab3909dea93f8819e0e0aa9f545489d8075b37a19dfcf08abd9199bdf034

site combined inventory SHA-256
f33532cbf1f1dcdc50b47dbdb2e1516b9282118a920d8a94e82a23a947ef9109

repository combined inventory SHA-256
cbe0d8fa43a937721ccf6c58cd20c630f8e92e5b8d3cd81687ee7de08f18ce5c

global combined inventory SHA-256
5a332924c77f4418cee2b1024cca2e235d0f3c837c077de9cc451b666ef92d96
```

Counts, byte totals, metadata rows, first-four-byte/content rows and complete
combined rows are identical. There was no creation, deletion, rename, content or
header mutation, mode/link/mtime drift, or unclassified new file. The review
chain of custody is valid. No cleanup or repair was attempted.

## 5. Complete readback

I read every required artifact completely. R19 was read as the sole
implementation authority, not summarized from its producer/master records. R11
was treated only as invalid-run incident evidence.

| Artifact | Lines | Bytes | SHA-256 |
| --- | ---: | ---: | --- |
| `AGENTS.md` | 215 | 9,874 | `a9bce02e5f162f99838bd3941fc4b041d567baac56fdf4ae3362d0e74fe62f95` |
| `orchestration/task_packets/W04-SCHEMA-DESIGN-REVIEW-01-R12.yaml` | 140 | 6,793 | `0c6e029ce97248f791da2369d8d45fb2306164c0bd67b52e4df48f6c5c1813ef` |
| `reports/reviews/W04/wyscout-schema-design-R19.md` | 4,357 | 236,602 | `8792db725eb65265b6a68ed56ed0d5bae1f20d1704faa8925baeeba29db10ec7` |
| `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R19.md` | 98 | 5,063 | `2cf151294f4530e2b15e7d9bb72aaa6e7541ad80d6bd073064930e475abef913` |
| `orchestration/task_packets/W04-SCHEMA-DESIGN-01-R19.yaml` | 150 | 7,754 | `66ccc09a706594a0c728982928da957f2fb7b4bd572676ee7efe0d6c7cfe7acd` |
| `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R19.yaml` | 69 | 3,297 | `66391167019465537887ea5bcf2f697faa1cc9d36db1d5bdc0a35a73c555d9cc` |
| `reports/verification/W04/wyscout-schema-design-R19-master-verification.md` | 125 | 5,436 | `8ac4416b10bcd809df3e4cab3db52fe088f4fd4ee8bbbf894721a73f8decca78` |
| `orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-REVIEW-01-R11.yaml` | 63 | 2,832 | `93850ea890ecad21cb0a051a7cafa439862f137bc6f8b230d5a42cc6588d5c04` |
| `reports/verification/W04/wyscout-schema-design-independent-review-R11-master-verification.md` | 117 | 5,448 | `aad3345ea65c0733e52b4c75d5cc10f28b004c281a8903a52b80343fca9edd88` |
| `reports/reviews/W04/wyscout-schema-design-independent-review-R11.md` | 819 | 38,008 | `8a7e0a65906aeb24f76d6676ad1daadb5311202b78a5fb6af0be5251082df6f8` |
| `reports/phase-gates/W04/source-schema-profile.md` | 365 | 18,574 | `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649` |
| `data/source/wyscout/v5/completion-manifest.json` | 1 | 6,803 | `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1` |
| `src/scouting/contracts/primitives.py` | 76 | 2,381 | `ee3fa657174cc949a5b7a389d60560abbdef596dbab913060a70516f0b988691` |
| `src/scouting/contracts/evidence.py` | 289 | 10,534 | `ff771aee3c9e23eb9ebe7e3919f75557f919919b232f752c4f708abf6c7cce10` |
| `docs/architecture/threat-model.md` | 71 | 7,722 | `da76328ed066c9f837d3c1ba9593be5ab58447dce54b59573aad8c6da95d6ab4` |
| `pyproject.toml` | 106 | 2,285 | `963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b` |
| `uv.lock` | 1,224 | 134,056 | `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca` |
| `../scouting-ml-production-blueprint.html` | 3,219 | 153,792 | `b55e624d27529761c937291ae1bc5d08de44120ace7739e87e0aad8a1000829a` |
| `../scouting-ml-agent-implementation-workflow.html` | 1,270 | 81,470 | `73fd051a7fb374733c552351d4f4dfe7b603c5cbdd9fdb7c3079895244d5b0d7` |
| `orchestration/templates/subagent_return.md` | 38 | 530 | `2d0d4fa9b706b4a4f7fe20f8f2d9f8813a25314db7de4fe6cd91c150abbf2dd5` |

Total required readback was 12,812 lines and 739,254 bytes. The one-line
completion manifest was read as a complete line, not truncated. The 1,224-line
lock and both parent HTML planning documents were read in bounded chunks through
EOF.

## 6. Reproduced source and rights closure

### 6.1 Exact 18 source-evidence rows

I parsed the candidate’s complete Section 3 table and independently hashed every
named physical file. All 18 path/size/SHA-256 rows match:

```text
completion manifest rows = 1
direct object rows        = 7
admitted member rows      = 10
total rows                = 18
total bytes               = 991,136,406
```

The completion manifest itself declares exactly seven `objects` and ten
`admitted_archive_members`. Their 17 durable paths are unique. The four
`scope_excluded_archive_members` remain directory-only exclusion evidence and are
not silently added to source authority.

The frozen digests independently matched:

```text
completion manifest
69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1

source schema profile
569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649

event taxonomy source
ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842

tag taxonomy source
e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922
```

R19 keeps source `DataCoverage` separate from Gold evidence coverage, retains the
six exact source-integrity dimensions, uses the completion manifest as the sole
strict discovery seam, and does not permit a scan, archive fallback, alternate
extraction, provider call, or newest-file selection. Rights remain restricted,
derived/internal review are allowed, export is false, attribution is required,
and prohibited/unknown rights fail closed. I found no P0–P2 defect in this
closure.

### 6.2 Source-record envelope

The seven admitted record families are project-owned envelope discriminators.
Payload labels or fields cannot choose the family. The fixed family/path mapping
is closed; unknown kinds reject the record rather than becoming generic
quarantine authority. Bronze stores the strict source reference and preserves raw
evidence. This is compatible with the accepted source profile and avoids trusting
provider-owned semantic labels for routing.

## 7. Field semantic authority

### 7.1 Exact roster/profile equality

The normative roster was extracted from R19’s tab-delimited machine block. Its
complete result is:

```text
competition      10
team             11
player           26
match            47
action           18
event-taxonomy    4
tag-taxonomy      3
total           119
```

There are exactly 119 rows and 119 unique `(record_kind,json_path)` pairs. I
independently parsed the seven source-profile sections, normalized the two CSV
families to `$.<column>`, and reproduced exactly 119 unique profile pairs. The two
sets are equal with no omission, extra, or duplicate.

The design’s source-shape requirement is complete: each decision and registry row
must carry the exact ordered positive type/count rows derived from the fixed
profile. The field route does not infer an absent type or treat display labels as
runtime matching authority.

### 7.2 Decision/registry/review/acceptance graph

I inspected the complete four-artifact route:

- fixed decision JSON and fixed master owner;
- fixed parsed-YAML registry restatement;
- independent sole-block review with candidate read-only;
- master-owned acceptance after PASS;
- canonical decision and candidate digests;
- physical YAML resource digest kept separate;
- strict actor and clock ordering;
- seven-field authority row;
- UUIDv5 dependency preimage containing canonical registry and acceptance
  digests;
- dependency `digest` equal to the canonical registry digest rather than physical
  YAML or acceptance digest; and
- Bronze blocked until accepted.

The decision schema has the exact top-level keys, four frozen inputs, five policy
keys, 119 ordered decision rows, strict closed transform union, canonical-field
collision rule, source-support enum, NFC rationale, and explicit
`PRESERVE_UNMAPPED`/`FORBIDDEN` null behavior. Registry rows must equal decisions
byte-for-byte under canonical representation. Negative tests cover every omitted,
extra, duplicate, reordered, mistyped, cross-kind, noncanonical, clock, digest,
review, acceptance, or early-use condition.

Only `tests/contracts/test_wyscout_field_registry_authority.py` is assigned. The
unauthorized alternate path is absent from R19’s ownership graph.

## 8. Actor and common authority behavior

The existing `ActorId` is `StrictUuid`, implemented as a strict Pydantic UUID
primitive. Independent runtime reproduction showed:

- canonical lowercase UUID JSON is accepted;
- Python-mode string, integer, boolean, and null are rejected;
- serialization produces canonical lowercase RFC 4122 spelling;
- an uppercase JSON spelling can be parsed by the UUID layer but serializes to a
  different byte spelling, so R19’s additional raw-input-equals-reserialization
  check is necessary and sufficient to reject it;
- `EvidenceDependency` serializes to exactly five keys; and
- forbidden aliases/extras are rejected by `ContractModel.extra="forbid"`.

The common route protocol requires strict UUID values for `decided_by`,
`reviewed_by`, and `accepted_by`, requires reviewer/acceptor separation from the
decision actor as stated, enforces physical review hashing, PASS-with-no-findings
or REWORK-with-findings consistency, and strictly orders decision, review, and
acceptance clocks. The four FIELD, POSSESSION, SUPPORTED_FEATURE, and IDENTITY
routes use that same authority rather than report-local actor aliases.

Possession adds the row-level actor equality: every predicate has a non-null
strict UUID `decided_by` exactly equal to the top-level decision actor. Identity
reviewed corrections require the accountable UUID at the state transition.
There is no string-name actor escape.

## 9. Possession closure

The possession predicate block mechanically contains exactly 12 required fields:

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

The complete decision union has six rows:

```text
CONTROL
RESTART
DEAD_BALL
CONTESTED
NON_CONTROL_ADMIN
UNMAPPED
```

I verified the exact control-team, opens, closes, dead-ball attachment,
contested-attachment, and null combinations in the six-row table. Only
`subevent_id`, `dead_ball_attachment`, and `contested_attachment` may be null, and
only according to their declared combinations. Required/forbidden tags are sorted,
unique, nonnegative, and disjoint. `UNMAPPED` still explicitly carries all twelve
fields, `NONE/false/false/null/null`, a nonempty rationale, and the equal strict
actor; it cannot open, close, buffer, or attach control.

Decision and taxonomy predicate arrays must be identical under canonical JSON,
including selector arrays, every control/attachment field, rationale and actor.
The field acceptance is an upstream frozen input. Review and acceptance follow
the common exact schemas. Possession construction is blocked until acceptance.
Negative tests cover malformed fields, all invalid union combinations,
overlapping selectors, tag errors, actor mismatch, omitted UNMAPPED values,
candidate inequality, label matching, provider-native claims, clock/digest drift,
and early construction.

The project-defined possession state machine closes at periods, keeps unresolved
actors unassigned, treats equal-clock cross-team events as uncertain, never
crosses periods, and promotes only deterministic resolved sequences. It does not
claim provider-native possessions.

## 10. Supported-feature and identity closure

### 10.1 Supported features

The supported-feature decision has a closed eight-field row:

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

(`applicability` spans lines in the prose block; the parsed object still has the
declared eight keys: aggregation, applicability, denominator, feature_name,
input_fields, output_type, reason, state.)

Every Gold-exposed or explicitly unavailable feature appears once, sorted by
name. SUPPORTED, SUPPRESSED_UNSUPPORTED_DENOMINATOR, and UNAVAILABLE each have a
closed valid combination. Inputs must come from the accepted field registry, and
possession inputs additionally require the accepted taxonomy. The ten policies
deny absence-as-permission and suppress or mark unavailable continuous time,
minutes, rates, per-90, provider possessions, outcome, role-inferred, and value
model families as stated.

The route has exact decision/registry/review/acceptance artifacts, canonical
candidate digest, accepted seven-field authority row, strict dependency preimage,
and Gold/feature-schema use blocked until acceptance.

### 10.2 Identity

The identity ruleset uses four fixed, ordered entity kinds and source-kind UUIDv5
namespaces. Canonical decimal source keys, not names/current teams/external
knowledge, drive deterministic resolution. Player zero is rejected; malformed,
missing, duplicate, collision, conflict, and absent-master cases remain
REVIEW_REQUIRED. Name-only matching is forbidden.

Crosswalk states, classification methods, confidence values, reviewer presence,
version progression, source-valid intervals, availability, supersession digest,
queue transitions, immutable history, and correction decision/review/acceptance
edges are closed. Only current effective RESOLVED rows project to the existing
`IdentityEvidence`. Queue disposition and direct current-resolved supersession
have distinct exact unions. The immutable bundle binds current rows, history,
queue, corrections, counts, accepted authority digests and available-time maximum.

The identity dependency uses the bundle digest and UUIDv5 preimage, not the
ruleset candidate as a recursive substitute. Its observed clock is the ruleset
decision and its available clock is the maximum accepted authority/correction
clock. I found no circular preimage or unbound correction path.

## 11. Temporal, product, coverage, and serializer closure

### 11.1 Exact dependencies and strict cutoff

R19 has exactly five `EvidenceDependency` rows:

```text
one source_manifest
one identity_evidence
three distinct feature_schema rows
```

The existing object was reproduced as exactly:

```text
kind
dependency_id
digest
observed_at
available_at
```

Aliases `dependency_kind`, `manifest_id`, and `manifest_sha256` are rejected.
Dependency kind, UUID, digest and UTC instants retain their existing strict
contract types. Ordering uses enum rank, UUID bytes, digest, observed time and
available time. Duplicate kind/ID fails.

Every observed and available clock is strictly earlier than
`feature_cutoff_ts`; equality fails. The watermark is exactly the maximum of five
availability clocks and is also strictly earlier. Bound decision, review,
acceptance and correction clocks are independently checked, preventing a projected
earlier clock from hiding a late authority event. The lineage hash is canonical
over the exact complete ordered dependency objects.

The semantic proof is clock-free. One injected generation instant adapts it to
the existing `TemporalEvidence` and the same instant is used by
`RetrievalResult.generated_at`. Operational receipt clocks do not enter the
semantic/build preimage.

### 11.2 Football facts and nonclaims

Silver action preserves provider record identity, numeric taxonomy IDs,
period-relative `decimal128(22,18)` event seconds, source scale, sorted tags,
coordinate order, anomaly evidence and authority lineage. The 7,821 string
subevent IDs remain preserved/unmapped. `x=-1` and both `y=101` anomalies are not
clamped.

Lineup stints use interval arithmetic over formation/substitution evidence.
Nominal minute `m` is `[m,m+1)`. Open stints are right-censored. Event maxima,
`Regular`, 90, and substitution maxima cannot invent a terminal. Exact minutes,
elapsed minutes, rate and per-90 stay null/absent and ineligible.

Player-match candidates are the union of the stated nonzero references. Zero
actors remain separate. The exact five-member primary key is retained. Team is
match-bound context rather than a key substitute. Facts contain no score, winner,
points, outcome, current team, minutes, or per-90 leakage.

Gold selects complete matches under a half-open window, start-before-cutoff and
the five strict dependencies. Partial-match/action-instant claims remain
unsupported because only period-relative occurrence is known.

### 11.3 Gold key, role context, and coverage

The exact Gold key binds tenant, player, competition, season, role-context ID and
version, window definition and bounds, cutoff, and dependency lineage hash.
`feature_schema_hash` remains a required reconciled row/proof field without
replacing role version or lineage.

Neutral role context is deterministic UUIDv5 over the fixed version and
`neutral_unscoped`. No inferred role or current-team context enters W04.

The six separate Gold dimensions are identity, lineup, action, coordinate,
possession and temporal. Each has strict integer numerator/denominator, exact
decimal ratio, state and sorted reasons. `N>D`, negative N, or negative D is a
hard failure. Only coordinate and possession may use authority-proven
`not_applicable_zero_denominator`; mandatory dimensions cannot convert a zero
denominator into completeness. Overall coverage is the minimum, with no weighting
or waiver.

Applicability ordering fails closed for rights, authority, identity, lineage,
duplicate, team and cutoff errors; suppresses unsupported mandatory denominator,
minutes/rate/per-90 requests; makes incomplete but non-hard-failing evidence
research-only; and permits `w04_data_ready` only for complete/authority-proven
optional coverage, overall one, and accepted requested features.

### 11.4 Paths and publication

Bronze, rejected-field, Silver, Gold, staging, manifest, receipt and quarantine
paths are exact and build/run partitioned. Path tokens have strict grammars.
Canonical discriminator identity prevents unknown records from being renamed into
known partitions. Staging is separate from final immutable paths. Publication
requires pre-existence/equality or atomic creation with readback; collision with
different bytes fails. There is no newest selection, directory scan, alias, or
alternate root.

## 12. Local resources and future-script absence

The exact local-resource allowlist contains 17 unique repo-relative paths:

- four future configuration candidates;
- twelve future decision/review/acceptance authority artifacts; and
- the accepted source-profile report.

The 16 future authority/configuration outputs are absent, as they should be at
design review. The source profile is present. There is no directory shorthand or
eighteenth resource.

The three future runtime entrypoints are also absent:

```text
scripts/launch_wyscout_v5.py
scripts/admit_wyscout_v5_runtime.py
scripts/rebuild_wyscout_v5.py
```

R19 names their paths, roles, argv, modes, descriptor policies, future accepted
size/digest authority and sole responsibilities without pretending they already
exist. This review created none of them.

## 13. Dependency, Packaging, wheel, and installed closure

### 13.1 Selected lock closure

Using the frozen installed `packaging==26.2` marker/tag implementation after the
required first-instruction bytecode assertion, I traversed:

- the unique editable `scouting-intelligence` root;
- all eight exact dependency groups in declared order;
- production edges when present;
- true/unmarked marker edges;
- requested extras, including `cachecontrol[filecache]`;
- optional edges only when the exact extra was active; and
- unique selected candidates under their resolution markers.

The result:

```text
selected lock rows L = 82
installed rows I     = 82
L minus I            = empty
I minus L            = empty
editable root        = selected
colorama 0.4.6       = not selected on this host
filelock 3.32.0      = selected via filecache
```

Canonical version comparison normalized both lock and installed metadata
consistently. The earlier diagnostic spelling `0.1.0` versus canonical `0.1` was a
review-helper correction, not a candidate mismatch.

### 13.2 Wheel selection

The frozen ordered `sys_tags()` list contained 1,230 tags. Each of the 81
third-party selected members had at least one compatible declared wheel. Selecting
the lowest tag rank produced no tie and no sdist fallback.

The required native examples reproduced exactly:

```text
pydantic_core-2.46.4-cp312-cp312-macosx_11_0_arm64.whl
polars_runtime_32-1.43.0-cp310-abi3-macosx_11_0_arm64.whl
```

The ABI3 Polars wheel is selected by the same ordered tag procedure rather than a
special exception. Lock filename/name/version checks passed.

### 13.3 Packaging bootstrap

R19’s stage-zero bootstrap is source/byte admitted before using Packaging
semantics. Stable authority binds the exact Packaging bytes and ordered selector
keys rather than trusting an ambient import. The later package closure has
`packaging==26.2` in both L and I. The review helper’s installed Packaging import
used `-B`, the environment control and first-instruction assertion, and created no
new pyc.

## 14. `.pth`, editable root, interpreter, and uv closure

### 14.1 `.pth`

The site root contains exactly:

```text
_virtualenv.pth
a1_coverage.pth
scouting_intelligence.pth
```

`_virtualenv.pth` is exactly the 18 bytes `import _virtualenv` with no newline.
The unowned `_virtualenv.py` sibling retains the declared 4,342-byte digest
authority and is never imported. `a1_coverage.pth` is 205 bytes with SHA-256
`ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8`.
The editable `.pth` is exactly the absolute current `<project-root>/src` spelling
with no newline and normalizes only that verified line to the stable project-root
token. None is executed through `site`.

The editable dist-info is singular and excluded from third-party I only after its
root relationship and exact metadata/RECORD/direct-url/cache structure are
verified. Root-bearing direct URL and cache clocks remain operational; normalized
metadata is stable.

### 14.2 Python aliases

The venv contains exactly the three symlinks:

```text
python     -> /Users/adrian/.local/share/uv/python/cpython-3.12.12-macos-aarch64-none/bin/python3.12
python3    -> python
python3.12 -> python
```

All resolve to the same regular mode-`0o755` 49,968-byte Python 3.12.12
executable with SHA-256:

```text
cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79
```

This safe alias topology is why a corrected design could potentially model the
four exact `python3` wrapper rows constructively. It does not make them compliant
with R19, because R19 expressly selects only `python` for generated wrappers.

### 14.3 uv

Current-host admission reproduced exactly:

```text
logical path      /opt/homebrew/bin/uv
logical kind      symlink
raw target        ../Cellar/uv/0.9.21/bin/uv
raw target bytes  26
resolution hops   1
physical path     /opt/homebrew/Cellar/uv/0.9.21/bin/uv
physical kind     regular, non-symlink executable
physical mode     0o555
physical size     41,617,552
physical SHA-256  4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
version            uv 0.9.21 (Homebrew 2025-12-30)
```

The design correctly keeps actual host spellings operational while binding stable
logical/installation-root/physical roles, one relative contained hop, final bytes,
mode, size and version. It forbids direct physical execution, accepting either
spelling, or post-hoc realpath repair.

## 15. Complete bytecode classification

### 15.1 Current site decomposition

Every present site pyc was classified against a source-derived authority map built
from singular RECORD-owned `.py` rows plus the separate uv bootstrap source.
Current magic is `cb0d0d0a`. Every file was a regular non-symlink, mode-`0o644`,
link-count-one file with a supported normal or pytest cache grammar or the exact
optional-six predicate.

```text
SITE_DISTRIBUTION_NORMAL          972
UV_BOOTSTRAP_NORMAL                 1
SITE_PYTEST_REWRITE               112
SITE_SIX_OPTIONAL_INERT_ORPHAN      1
total                            1086
site __pycache__ directories      131
```

The source authority map contained 5,761 singular RECORD-owned `.py` rows,
regardless of whether a cache currently exists. The uv-bootstrap pyc maps only to
the separately admitted `_virtualenv.py`. The optional `six` file has no source or
owner and matches its exact bounded path, magic, size and digest predicate. No
unclassified site pyc was found.

### 15.2 Exact eleven Packaging incident rows

All eleven files have current magic `cb0d0d0a`, mode `0o644`, link count one,
present singular RECORD-owned source siblings, and modification epoch
`1785412176`. They are normal mapped operational files, not stable authority.

| path | source sibling | bytes | SHA-256 |
| --- | --- | ---: | --- |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/__init__.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/__init__.py` | 596 | `2af8dd75b52b02e67d92f2d00f72f93ac1bddf99f785553999292216a0bebd58` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/_elffile.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/_elffile.py` | 4,976 | `26d9fddee205210e1631e6ba06688cd2a7de470d01bc08d92f7ee41223258a8b` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/_manylinux.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/_manylinux.py` | 9,895 | `caf5c738d3974432722a72a4163326b7df9a3db56a1ea7ccbc6987e72af43cea` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/_musllinux.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/_musllinux.py` | 4,604 | `1a83fa91aa59e1607fbbbda2dc6a9fd595237e5ce2520b1a32d8cf86cf62c7ef` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/_parser.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/_parser.py` | 15,613 | `91da8b4288ef1141055033b0385a169fd9ec1cf5d1983506ff197cede9feb584` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/_tokenizer.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/_tokenizer.py` | 8,488 | `1d5b29d5c5d67eddfecd33e4175d6cb10146c46d3ebd96ef9439131f52fa4a94` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/markers.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/markers.py` | 17,487 | `73c47d51abc57ee31e45147ef4b458ad4f41c3a76b9b6ebc21dc0ef738a8c6bd` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/specifiers.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/specifiers.py` | 75,787 | `e384d9c322c39fc43c2b724d757fadfa0a0d5b960d3e51741109b0d3b9e766f3` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/tags.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/tags.py` | 37,392 | `235d0486904373dd141b2c35797dcd06a7c2a5bfd8b9cecf835051668a13fd14` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/utils.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/utils.py` | 11,092 | `b5fd333d2c945ec569dab50e95e63a239982c32f03adedc991446802cef18150` |
| `.venv/lib/python3.12/site-packages/packaging/__pycache__/version.cpython-312.pyc` | `.venv/lib/python3.12/site-packages/packaging/version.py` | 41,813 | `070892ecb7a058ff37c08097fd752e64d4d556fce70f1f4d84ce64e0dc35f5ae` |

Their presence changes only the operational inventory relative to R18’s earlier
snapshot. It does not add a distribution, source row, import authority, build
input, or orphan predicate. R19 truthfully preserves them and forbids cleanup.

### 15.3 Current repository decomposition

Whole-repository traversal outside `.venv` and `.git` reproduced:

```text
REPOSITORY_NORMAL                                      35
REPOSITORY_PYTEST_REWRITE                              20
REPOSITORY_MIGRATIONS_ENV_OPTIONAL_INERT_ORPHAN         1
REPOSITORY_MIGRATIONS_FOUNDATION_OPTIONAL_INERT_ORPHAN  1
REPOSITORY_POSTGRES_OPTIONAL_INERT_ORPHAN               1
total                                                   58
repository __pycache__ directories                     19
```

All 55 mapped rows have their present repository `.py` siblings. The three
source-absent rows match the exact path, source absence, mode, size, magic and
digest predicates:

```text
migrations/__pycache__/env.cpython-312.pyc
migrations/versions/__pycache__/0001_foundation.cpython-312.pyc
src/scouting/storage/__pycache__/postgres.cpython-312.pyc
```

The Foundation SQL file grants no Python authority. There is no fourth
repository orphan.

### 15.4 Stable versus operational rule

R19 correctly derives stable bytecode authority from every admitted source before
observing caches. Actual mapped cache presence/path/count/bytes and optional
orphan presence are operational. Each future bounded run takes its own complete
preflight; it does not require the R19 snapshot count. Nevertheless, every present
file must classify. The identical postflight must bind path, metadata, magic and
complete bytes. A creation, deletion, rename, mutation, mode/link change, or new
unclassified path invalidates the run. Cleanup cannot recover success.

## 16. Closed environments, input/result schemas, and projection

### 16.1 Environment maps

The outer normalized base has exactly 20 stable literals and 9 normalized
operational values:

```text
outer present names = 29
```

The child base has the same 20 literals, 8 normalized operational values (the
outer launcher FD is not inherited), plus role, entrypoint FD, result FD and
nonce:

```text
admission child present names = 32
rebuild child present names   = 32
```

The required-absent arrays close proxy, coverage, dynamic-loader, Python startup,
user-site, uv-index/selector and cross-role transport names. Every unknown
environment name fails. uv input depth zero, exact logical `UV`, no leading venv
component and deterministic uv transformation produce child Python depth one and
exactly one venv prefix. The stable map uses opaque role tokens rather than actual
host paths.

The acyclic H1/H2 construction is sound:

- normalized base object is hashed before inserting its encoded tuple/envelope;
- that digest is placed in the tuple/envelope exactly once;
- the complete transport hash is calculated after insertion;
- the complete hash is returned for equality but never included in its own input;
- the verifier removes only the one inserted value and reconstructs the same
  normalized base; and
- no fixed-point, placeholder, recursive self-digest, or second encoding exists.

The unchanged stable version literals are:

```text
w04-local-control-bootstrap-v4
w04-outer-environment-bootstrap-v2
w04-child-environment-input-v2
w04-code-environment-admission-v14
```

### 16.2 Mechanically reproduced cardinalities

I parsed each closed table rather than relying on the prose count:

| Object | Reproduced keys/rows |
| --- | ---: |
| common child input envelope | 16 |
| admission `inputs` | 8 |
| rebuild `inputs` | 10 |
| rebuild invocation | 25 |
| child-result top level | 10 |
| entrypoint-source observation | 14 |
| admission result | 9 |
| component-proof row | 3 |
| component-proof array | 20 |
| rebuild result | 6 |
| rebuild receipt row | 3 |
| layer-manifest row | 5 |
| final recheck | 17 |
| pre-build projection | 25 |

The 25 pre-build keys are unique and Unicode-code-point sorted. Removing
`schema_version` from the projection and removing `build_id` from the invocation
produces the same exact 24-key set. This reproduces the required
16/8/10/25/25/20 headline cardinalities and the 24-key intersection.

### 16.3 Descriptors and results

The outer launcher source and both child entrypoint sources are master/launcher
opened with contained no-follow descriptor checks. Descriptor positions stay
zero under positional reads. Inheritance and close ownership are exact. Children
receive only entrypoint-source and result writer descriptors; the launcher
descriptor is retained by the launcher. Descriptor numbers/device/inode are
operational while relative path, role, mode, link count, size and bytes/digest are
stable.

The result frame has fixed magic, version, bounded length, payload SHA-256, strict
UTF-8/canonical JSON, exact nonce/role/argv/environment/source bindings, EOF and
timeout checks. Diagnostics are separately bounded and grant no authority.
Admission returns canonical manifest bytes plus proofs; it cannot write the
manifest or compute the build ID. Rebuild returns exact receipt/layer/final-check
evidence and cannot expand authority.

The documented transient same-trust-domain replacement/restore interval remains
truthfully residual. The design does not overclaim that descriptor checkpoints
detect a mutation that begins and ends entirely between checks. Persistent
replacement is detected at the defined checkpoints. This is an accepted local
trust-boundary residual, not an unmentioned guarantee.

## 17. Build identity, two-root proof, and runtime ownership

The code/environment manifest version is v14. Its component object contains the
20 exact values proven by the component-proof array, including selector,
Packaging bootstrap, lock inputs/closure, wheels, extracted and installed bytes,
executable census, pyc source map/predicates, uv bytes/version, launcher/process
contracts, result contract, interpreter/stdlib, local resources and environment
values.

Actual logical/raw uv paths, root-bearing wrapper paths, `.pth` path, cache path,
pyc inventories, prefix/run IDs, descriptors, clocks and output digests remain
operational. Stable normalized roles, relationships, admitted bytes and schemas
remain in the manifest. This supports equal stable digest across two roots without
requiring equal incidental cache inventories.

The pre-build projection is formed only after immutable code-manifest write or
confirm plus readback. It has 25 keys and excludes build ID and all run/output
fields. One SHA-256 produces build ID. Only after that digest exists does the
launcher construct the 25-key post-hash invocation by replacing projection
`schema_version` with `build_id`, then render run/prefix/receipt/layer paths. The
rebuild child reverses exactly that one transformation and recomputes the digest.
There is no circular preimage.

Only the launcher writes/confirms the code manifest and computes build ID.
Admission constructs but cannot write or calculate. Rebuild receives the accepted
immutable identity and calls already named sole product writers. Bronze, rejected,
Silver family, Gold, manifests, receipts, quality, card and review owners are
serial/disjoint as listed. Field, possession, supported-feature and identity
decision/review/acceptance ownership is separated. No future script currently
exists.

The two-local-commit ledger preserves design acceptance separately from later
implementation/product evidence. No commit, tag, Git remote, checkpoint, or
ledger mutation was performed in this review.

## 18. R18-to-R19 bounded replacement check

I performed a read-only unified comparison of R18 and R19 after the independent
R19 read. Differences are bounded to:

- revision/status prose;
- the current site snapshot changing from 1,075 to 1,086 and its mapped-normal
  decomposition;
- the exact eleven-row R11 Packaging incident section;
- explicit future-run operational-cardinality language;
- the closed no-write independent-review harness;
- phase-evidence language carrying the new pre/post inventory;
- R18-to-R19 wording in future-script ledger rows; and
- the required negative/positive review-harness tests.

The semantic, authority, environment, executable, alias, build, product and
ownership sections otherwise remain R18’s stable text. This historical
preservation does not make the wrapper mismatch acceptable: it establishes that
the defect was inherited unchanged and missed by prior merits review.

## 19. Exact review-command results

All Python commands had the prefix and flags required by R12. The substantive
results were:

1. **Field/profile helper — PASS.** Candidate 4,357 lines; roster 119 unique;
   profile 119 unique; sets equal; counts 10/11/26/47/18/4/3; candidate and frozen
   source digests recorded.
2. **Source/resource helper — PASS after correcting the manifest key used by the
   review helper.** Seven objects, ten admitted members, 17 unique durable paths;
   exact 17 local resources; 16 future authority/config artifacts absent; all
   three entrypoints absent.
3. **Actor/evidence helper — PASS.** Strict Python-mode rejections, canonical
   lowercase JSON behavior, explicit uppercase raw spelling mismatch, exact
   five-key dependency, extras forbidden.
4. **Complete pyc-classifier helper — PASS.** Site 1,086 with
   972/1/112/1; repository 58 with 35/20/three exact orphans; 11 incident rows;
   current magic and source ownership verified.
5. **L/I/wheel helper — PASS after consistently canonicalizing the editable
   version.** L=I=82; no differences; correct extras/markers; 81 compatible wheel
   selections; no ties; native examples exact.
6. **Executable/.pth/alias/uv helper — FAIL on candidate executable bytes.** The
   first complete assertion stopped at `detect-secrets`. A bounded follow-up
   classified all 35 rows, verified all RECORD evidence and isolated exactly four
   first-line-only mismatches. All `.pth`, Python alias/physical and uv identity
   assertions passed.
7. **18-source-row helper — PASS.** Every physical path/size/SHA-256 matched;
   991,136,406 bytes hashed.
8. **Closed-schema helper — PASS.** All cardinalities, 25-key ordering,
   24-key projection intersection, 12 possession fields, six possession union
   rows, 20 outer literals and 29/32 environment totals reproduced.
9. **Packet acceptance size/recommendation check — PASS, exit 0.** The review
   existed, exceeded 35,000 bytes, contained a recommendation, and ran with the
   packet’s exact bytecode-disabled locked/no-sync command.
10. **Local-only verifier — PASS, exit 0.** All 25 checks passed with no
    failures: zero remotes, active pre-push guard, one project/lock/venv, correct
    root runtime/pins/groups, no forbidden dependency/package-manager/Node/
    hosted-CI/container/external-service/config URL/outside-root state, approved
    skeleton, no outside-root symlinks, and ignored root venv.
11. **Identical shell postflight — PASS_IDENTICAL.** Exact counts, byte totals
    and all metadata/content/combined digests equal preflight as recorded in
    Section 4.4.

No command ran a sync-capable uv operation. No bare Python ran. No helper imported
installed packages before the bytecode-control assertion. No package executable,
future entrypoint, provider interface, network operation, serializer, product
writer, migration, cloud tool, container tool, or deployment tool was invoked.

## 20. Scope and mutation confirmation

The only created/modified paths are intended to be:

```text
reports/reviews/W04/wyscout-schema-design-independent-review-R12.md
reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R12.md
```

This review did not edit:

- R19 or any candidate/producer/master/R11 artifact;
- `.venv` or any pyc;
- `pyproject.toml` or `uv.lock`;
- `configs`, `orchestration`, `scripts`, `src`, `migrations`, `data`, `runs`, or
  `tests`;
- `.git`, `.gitignore`, Git state, remotes, commits, tags or hooks;
- either parent-workspace HTML document; or
- any provider, network, cloud, container, endpoint or deployment state.

No cleanup, repair, sync, cache purge, environment recreation, executable rewrite,
or wrapper normalization occurred.

## 21. Residual risks and follow-up

The open P1 is the only P0–P2 candidate defect identified. The rest of the design
is unusually exact, but implementation remains future work. Future implementation
must still prove the complete negative suites, safe descriptor operations,
canonical serializers, wheel/cache-to-installed byte mapping, native loaded-image
ownership, source-complete code manifest, prefix emptiness, no pyc reads, atomic
publication, deterministic second-root equality and raw-to-Gold replay. Those are
future acceptance obligations rather than defects in a design that defines them.

The documented same-trust-domain transient replacement/restore residual remains.
It is explicit, local, bounded by descriptor/path checkpoints and does not justify
claiming hostile-kernel or hostile-same-account protection.

Required next action is a bounded R20 design correction for R12-P1-01, followed by
a fresh master verification and a different independent merits review. That work
must not rewrite the current wrappers merely to make an old design appear true.

## 22. Final recommendation

**REWORK**

R19 has one admission-blocking P1 contradiction between its exact Class-E wrapper
template and four current RECORD-owned wrapper byte sequences. PASS is forbidden
because the packet requires zero P0–P2 findings. The no-write review chain is
valid: the terminal shell postflight is exactly identical to preflight. That
procedural PASS preserves, but does not cure, the substantive REWORK verdict.
