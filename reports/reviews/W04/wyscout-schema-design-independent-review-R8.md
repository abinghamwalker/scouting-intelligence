# W04 Wyscout schema design independent review R8

## Decision

**REWORK. Do not begin the W04 implementation graph from R11.**

R11 retains the previously accepted source, rights, temporal, football-product,
coverage, path, environment, resource, gate, and ledger contracts, and it closes
the narrow R10 defect by naming both future Python entry points and requiring
locked/no-sync no-site launches. The independent read-only challenge nevertheless
finds two P1 defects:

1. the claimed exhaustive repository-bytecode policy cannot classify two present
   source-absent migration pycs, so the required current environment fails
   admission unless it is cleaned, which R11 and this packet both forbid; and
2. the external launcher performs every security-critical pre-interpreter and
   inter-process transition but has no exact implementation path, bytes,
   admission root, result-channel grammar, sole owner, or stable/operational
   manifest row.

The first defect is a directly reproduced current-state contradiction. The second
is an implementation and authority gap: the two named Python scripts cannot
perform work that R11 explicitly requires before either interpreter exists.
Implementing that work in an improvised shell command, an unnamed master routine,
or one of the two already-started Python processes would contradict the reviewed
ordering and code-authority claims.

No P0 issue was found. Both P1 issues are bounded design corrections and require no
change to architecture, project root, dependency policy, provider, rights,
storage roots, network boundary, local-only boundary, or Git policy.

## Review boundary and method

The complete 2,058-line R11 design was read and challenged against its R11 producer
packet, the R10 and R11 master review records, both master verification reports,
the complete retained R10 design, the preceding independent R6 review, the source
profile, the existing evidence contract, `pyproject.toml`, `uv.lock`, both
controlling HTML plans, `AGENTS.md`, and the mandatory return template.

Material environment claims were reproduced read-only. No provider object or
excluded archive payload was opened. No network request, dependency resolution,
sync, installation, cleanup, migration, data write, environment mutation, Git
operation, or candidate repair was performed. The two future entry points remain
absent, as R11 requires at design time:

```text
scripts/admit_wyscout_v5_runtime.py   absent
scripts/rebuild_wyscout_v5.py         absent
```

Only this review and its packet return are authored.

## Ranked findings

### P1-01 — the exhaustive repository-pyc policy omits two present migration orphans

R11 Section 8.6 says the external launcher traverses the whole repository before
each Python process and that every actual repository pyc must classify exactly
once as:

1. normal bytecode mapped to an admitted repository `.py` source;
2. pytest-rewrite bytecode mapped to an admitted repository `.py` source; or
3. the one exact optional source-absent PostgreSQL inert orphan.

R11 then records a current first-root repository observation of 56 pycs in 17
`__pycache__` directories: 35 mapped normal, 20 mapped pytest, and the PostgreSQL
orphan. Section 10 requires that same `35 normal + 20 pytest + PostgreSQL orphan`
inventory in health evidence. Required test 14 again mandates 56 files in 17
directories. Section 8.6.3 explicitly rejects every repository pyc outside the
admitted source map or exact PostgreSQL predicate, and the final stop rule forbids
cleanup as a remedy.

The current whole-repository inventory is instead:

```text
58 pyc files in 19 __pycache__ directories
38 normal-name pycs
20 cpython-312-pytest-9.1.1 pycs

normal-name classification:
35 map to present sibling .py sources
3 have no sibling .py source
```

The three source-absent normal-name files are:

| Repository path | Sibling source required by the normal grammar | Mode | Size | SHA-256 |
| --- | --- | ---: | ---: | --- |
| `migrations/__pycache__/env.cpython-312.pyc` | `migrations/env.py` — absent | `0o644` | 2,795 | `6d93fd4b51bfcfaed59e59358f6694fef65bf04be088e7ff8377340389990ff2` |
| `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc` | `migrations/versions/0001_foundation.py` — absent; only `0001_foundation.sql` exists | `0o644` | 25,415 | `b10987536a062b17702b1fdb5dbb94ca0b2293f8c6d91e43a9fd4042dfeea84d` |
| `src/scouting/storage/__pycache__/postgres.cpython-312.pyc` | `src/scouting/storage/postgres.py` — absent | `0o644` | 4,230 | `ee3ae9a1dd7a942474cf6442c414d1d046aa8532d0e6702698bd19da46ff40ac` |

All three begin with the current Python 3.12 magic `cb0d0d0a`. Only the third has
an R11 optional-inert-orphan predicate. The first two cannot enter the
source-complete authority map because their `.py` sources do not exist, do not
match the exact PostgreSQL path, and cannot derive Python authority from
`migrations/.gitkeep`, `migrations/__init__.py`, or the SQL migration. They are
therefore unclassified under the exhaustive policy.

This is not merely an outdated informational count. Applying R11 literally makes
admission fail before either W04 Python process. R11 forbids deletion, repair, or
environment cleanup and requires the existing one-root environment, so there is no
permitted implementation path to the required positive test. Treating the files
as normal mapped bytecode would falsely grant source authority that does not
exist. Silently ignoring the two migration paths would contradict whole-repository
enumeration and the rule that every actual pyc classifies exactly once.

**Bounded correction:** issue a standalone R12 that truthfully records 58 pycs in
19 directories and the `35 mapped normal + 20 mapped pytest + 3 source-absent`
split. Give each of the two migration files an exact, non-authoritative,
optional-inert-orphan predicate parallel to the existing PostgreSQL predicate,
including exact path, absent-source condition, current magic/tag, mode, size, and
digest, or define another equally exact reviewed denial class that cannot add
source/import/build/semantic authority. Update the operational inventory, health
requirements, negative tests, required test 14, and two-root optional-presence
rule together. Do not delete or import either file, broaden the class to arbitrary
orphans, or convert the SQL file into Python authority.

### P1-02 — the external launcher is unnamed and outside the admitted ownership graph

R11 correctly distinguishes two Python processes and binds their exact ordered
argv:

```text
uv run --locked --no-sync python -S -B scripts/admit_wyscout_v5_runtime.py
uv run --locked --no-sync python -S -B scripts/rebuild_wyscout_v5.py
```

Those entry points are named future repository code and are assigned implementation
rows 22 and 23. The separate “external admitted launcher,” however, performs all of
the following before, between, and after those processes:

- resolves and hashes `uv`, all interpreter aliases, the physical interpreter,
  environment controls, and each entry-point path/bytes before execution;
- safely samples the two run UUIDs;
- creates, contains, proves empty, and selects each alternate bytecode prefix;
- sets `PYTHONPYCACHEPREFIX`, `PYTHONDONTWRITEBYTECODE`, fixed environment, and
  no-network controls before interpreter creation;
- traverses and classifies every site and repository pyc before each process;
- launches the exact locked/no-sync argv from the repository root;
- receives canonical code-manifest bytes and component proofs over a “bounded
  result channel”;
- proves the admission prefix unchanged and empty after exit;
- atomically writes or confirms the immutable code manifest;
- enforces the code-manifest-before-build-ID transition;
- computes or invokes the build-ID boundary;
- creates the post-build rebuild prefix and starts the second process; and
- performs final no-read/no-change/empty-prefix checks.

None of those operations can be implemented inside
`scripts/admit_wyscout_v5_runtime.py`: the prefix and environment must exist, and
the entry point, interpreter, aliases, uv binary, and repository pycs must already
have been admitted, before that Python interpreter is created. They also cannot be
implemented inside `scripts/rebuild_wyscout_v5.py`, which runs only after the code
manifest and build ID exist.

Despite this controlling role, R11 provides no exact repository path, executable
kind, command grammar, implementation bytes, authority input, bootstrap trust
root, sole-writer row, or code-manifest component for the launcher itself. The
17-path resource allowlist does not include it. The ownership-complete sequence
names only the two inner Python scripts. The stable
`process_launch_contract_digest` binds the two argv, process roles, uv identity,
and inner entry-point rows, but not the code that chooses and launches them.

The “bounded result channel” is also unspecified. There is no exact file
descriptor, framing, canonical encoding, maximum size, message schema,
authentication/binding to the child identity, error grammar, or rule preventing
operational logs from being interpreted as manifest bytes. The launcher is the
sole writer of the immutable code manifest, yet no ownership row grants that
write. An implementation would have to invent whether the channel is stdout, a
pipe, a temporary file, or another mechanism and invent how the manifest is
separated from diagnostics.

This leaves a circular authority statement. R11 calls the launcher “admitted,” but
does not say what admitted its bytes before it measured the entry point that will
later construct the repository code manifest. If the launcher is repository code,
its own exact path and bytes must enter a pre-execution trust/admission rule and
the eventual stable manifest. If it is intentionally outside repository code, the
design must name that trust boundary and explain why its behavior is not part of
the reproducible launch and sole-writer proof. Calling it “master” or “external”
does not provide executable semantics.

There is also no exact anti-mutation handoff between the launcher's entry-point
hash and Python's later path open. R11 requires mutation after freeze to fail, but
the reviewed command opens a path rather than a previously verified descriptor.
At minimum the design needs exact pre/post identity and digest rechecks, bounded
file-identity rules, and a fail-closed statement covering replacement between
measurement and process execution. The future implementation must not improvise a
TOCTOU policy.

The result is implementation-blocking. Any chosen launcher would be
security-critical code that is absent from the admitted code/environment
manifest, and different reasonable implementations could have different path,
mutation, environment, result-channel, and write semantics while producing the
same two visible inner argv. The claimed complete standalone design therefore does
not yet determine the implementation.

**Bounded correction:** name the exact launcher implementation and invocation
boundary; bind its repository-relative path and bytes or explicitly define and
justify a different reviewed trust root; assign sole ownership for prefix
creation, child launch, result-channel handling, code-manifest publication, and
build-ID handoff; specify the exact result-channel framing/schema and diagnostics
separation; bind launcher identity and normalized stable bytes into the code/
environment and build identity where appropriate; and define fail-closed
pre/post file-identity and digest checks for entry-point replacement. Preserve the
two exact inner Python argv and do not add site startup, sync, generated-wrapper
execution, network, or a third product-writing interpreter.

## Required challenge results

### Locked/no-sync no-site launch and uv identity

A read-only probe using the exact reviewed uv/Python prefix plus `-c` reproduced:

```json
{
  "coverage_loaded": false,
  "dont_write_bytecode": true,
  "executable": "<project-root>/.venv/bin/python3",
  "no_site": 1,
  "pycache_prefix": null,
  "site_paths": [],
  "src_paths": [],
  "virtualenv_loaded": false,
  "virtual_env": "<project-root>/.venv"
}
```

`pycache_prefix` is null in this probe because the external launcher's
process-specific `PYTHONPYCACHEPREFIX` was intentionally not created or set during
this read-only design review. The important current-runtime claims pass: `-S`
prevents site and editable-root startup, `_virtualenv` and Coverage are absent,
and `-B` disables bytecode writes.

The current uv observation is:

```text
logical path: /opt/homebrew/bin/uv
raw link: ../Cellar/uv/0.9.21/bin/uv
version: uv 0.9.21 (Homebrew 2025-12-30)
physical mode: 0o555
physical size: 41,617,552
physical SHA-256:
4f0c0c002bb4702c1bd6792edc15f7ae3948b5f19509c8d73cd5c9a26298097f
```

R11 correctly makes the uv version and physical digest stable while keeping the
root-bearing executable spelling operational. It also correctly rejects missing,
reordered, duplicated, or extra tokens, plain `uv run`, a sync/reconciliation
attempt, alternate interpreter or entry point, generated wrapper execution, and
site startup. The future entry-point paths are exact and presently absent; their
future bytes cannot be reproduced until implementation and must be admitted before
execution as R11 says.

This part passes except for the launcher authority and handoff defect P1-02.

### Prefix, code-manifest, build-ID, and rebuild ordering

The semantic order is otherwise sound:

1. a pre-build admission run ID selects only
   `.staging/admission/admission_run_id=<uuid>/runtime-pycache/`;
2. stage 0 constructs canonical code/environment manifest bytes without a build
   ID;
3. the immutable content-addressed code manifest is frozen;
4. only then is the build ID available;
5. a distinct rebuild run ID selects only
   `.staging/<build_id>/<run_id>/runtime-pycache/`; and
6. a new no-site interpreter runs the rebuild entry point.

The design excludes both run IDs, absolute prefixes, clocks, and operational paths
from stable identity, prohibits prefix reuse and cleanup, and requires empty-before
and empty-after proofs. It denies in-place pyc reads and prevents an unknown-build
stage-0 placeholder. Those rules close the original build-ID/prefix cycle.

The sequence still cannot be executed from R11 alone because the unnamed launcher
owns every transition. P1-01 additionally makes the first whole-repository pyc
classification fail before stage 0.

### Source envelope, temporal boundary, product keys, and coverage

The source and product contracts pass independent readback:

- the completion manifest is 6,803 bytes with SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`;
- the source profile is 18,574 bytes with SHA-256
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
- exactly 18 source evidence rows are specified: completion, seven objects, and
  ten admitted archive members;
- record family comes only from the strict completion-path-to-envelope map;
  payload `kind`, shape, names, taxonomy labels, or filenames cannot dispatch;
- missing, null, non-string, safe unknown, and unsafe unknown envelope values route
  only to the fixed rejected-record family with full typed canonical digest;
- the known Bronze literal remains
  `records/record_kind=<known-kind>/source_sha256=<source_sha>/...`;
- the player-match key remains
  `(tenant_id, source_manifest_id, match_id, player_id,
  player_match_fact_schema_version)`;
- the Gold key retains role-context version and dependency-lineage hash while
  `feature_schema_hash` remains a required non-key field;
- the six source coverage dimensions remain separate from the six Gold dimensions
  `identity`, `lineup`, `action`, `coordinate`, `possession`, and `temporal`;
- only coordinate and possession may use authority-proven zero-denominator
  non-applicability; and
- all Bronze, Silver, Gold, quarantine, staging, manifest, and receipt paths are
  exact and have named serializers/owners.

The existing `TemporalEvidence` implementation independently confirms that
dependency `observed_at >= cutoff`, `available_at >= cutoff`, and aggregate
watermark `>= cutoff` all fail. R11 retains strict `<` for every one of the five
dependencies and every bound decision, review, acceptance, and correction clock.
No equality waiver was found.

### All-groups closure, Packaging bootstrap, installed set, and editable root

`uv tree --locked --all-groups --depth 100` resolved 83 packages including the
editable root. `uv pip list --python .venv/bin/python --format json` also reported
83 installed distributions including the editable root. An exact normalized
name/version `comm -3` comparison emitted nothing. The current third-party sets
therefore match at 82 members, with the editable
`scouting-intelligence==0.1.0` verified separately.

All eight declared groups remain selected:

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

The Packaging bootstrap declaration is still exactly
`packaging==26.2`, wheel `packaging-26.2-py3-none-any.whl`, size 100,195, SHA-256
`5fc45236b9446107ff2415ce77c807cee2862cb6fac22b8a73826d0693b0980e`.
R11 admits its extracted and installed bytes before importing only the required
Packaging-owned source modules to obtain the ordered compatible-tag selector.
This breaks the former selector/admission cycle without granting general site
startup.

The exact three `.pth` classes reproduce:

| Class/file | Mode | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `_virtualenv.pth` | `0o644` | 18 | `69ac3d8f27e679c81b94ab30b3b56e9cd138219b1ba94a1fa3606d5a76a1433d` |
| `a1_coverage.pth` | `0o644` | 205 | `ef2ed06d19867ec669c09a804060666a9cd5e383af0a9d11aa2de79b77d448e8` |
| `scouting_intelligence.pth` | `0o644` | 81 | `3dc417212f5f46b7399aa8e13c8bd999c4e0cef30f012f8a9412bf8a54f59fba` |

The unowned bootstrap sibling `_virtualenv.py` is mode `0o644`, 4,342 bytes, and
has SHA-256
`6cf30c56faf2a55228914dbbd17f8088ed371ebb08f5e7fa6fd931f913fcaf1d`.
No fourth `.pth` exists.

Editable metadata also reproduces:

| File | Size | SHA-256 | Stable/operational result |
| --- | ---: | --- | --- |
| `direct_url.json` | 123 | `2361d905ac1e0a9300426cb6a2ab39e0ddec56d3c20e9eb967966ff19a053243` | exact current root URL; root token is stable-normalized |
| `uv_cache.json` | 194 | `a4bf7fb0887dc0b05c0f8286f841340f7dfac4a70ff2b5fec9da26275f9fdd8a` | exact structural keys; timestamps operational only |

The denied `.pth` files are never executed in the no-site processes, the editable
source root is appended only after verification, and root-bearing bytes are
separated from stable normalized evidence. This portion passes.

### Executable census and interpreter aliases

Installed RECORD inspection reproduces exactly 35 `../../../bin/` rows across 21
owners. Parsing verified installed `entry_points.txt` files without importing the
distributions yields 33 direct console/gui names across 20 owners. Pip declares
only `pip` and `pip3` for its target; `pip3.12` is the one derived P member. Ruff
declares no entry point and remains the one wheel `.data/scripts` W member.

The measured `33 E / 1 P / 1 W` details pass:

- `pip`, `pip3`, and `pip3.12` are each mode `0o755`, 382 bytes, and
  byte-identical with SHA-256
  `d371b253cc444af2efa4c2f1f41ff3030f5cc10a912807de94a35629dc0bc3ff`;
- Ruff is mode `0o755`, 23,669,488 bytes, and SHA-256
  `1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52`;
  and
- generated wrappers use the exact project-root
  `.venv/bin/python` shebang that R11 stable-normalizes only after actual-byte
  verification.

The exact three interpreter aliases reproduce:

```text
.venv/bin/python
  -> /Users/adrian/.local/share/uv/python/
     cpython-3.12.12-macos-aarch64-none/bin/python3.12
.venv/bin/python3 -> python
.venv/bin/python3.12 -> python
```

All are distinct mode-`0o755` symlinks and resolve to the same physical executable,
which is mode `0o755`, 49,968 bytes, and SHA-256
`cf450e6bc0b00adecd12b7b13024de7000c7350801addc802bd3b45782104e79`.
The operational uv launch reports `python3`, while wrapper authority correctly
uses canonical `python`. This portion passes.

### Site and repository bytecode

The site observation still matches R11:

```text
1,075 pycs in 130 __pycache__ directories
963 normal-name pycs = 961 distribution mappings + 1 uv-bootstrap mapping
                         + 1 exact optional six orphan
112 pytest-rewrite pycs
```

The exact site bootstrap and optional-six rows reproduce:

| File | Mode | Size | SHA-256 |
| --- | ---: | ---: | --- |
| `_virtualenv.cpython-312.pyc` | `0o644` | 4,159 | `08765615dd291d8a643581c2e7a0d3f891284aed32dd38a3940675488579f5f6` |
| `six.cpython-312.pyc` | `0o644` | 41,388 | `4e59431b1d92fe443cbdb1f76e065ece05b1c4f6cb4925168be8e9321f390e28` |

Both use current magic. `six.py` is absent, so the exact optional-six predicate
holds.

The repository observation does not match, for the reasons in P1-01. The design's
stable principle remains good: admitted source, not incidental pyc inventory,
defines code authority; present bytecode is operational, denied, unchanged, and
may differ across roots. The defect is that exhaustive operational classification
still requires every present file to match a constructive class, and R11 omits
two actual files. A source-complete stable map cannot itself classify a pyc whose
source is absent.

### Resources, ownership, health/card/gate, two roots, and local ledger

R11 retains exactly 17 local resource paths: four configuration authorities,
twelve decision/review/acceptance artifacts, and the source profile. It keeps
strict source, identity runtime, runtime admission, local resources, parent
products, and outputs as disjoint guard categories. No directory shorthand or
eighteenth resource is introduced.

The product sole-writer graph remains explicit:

- Bronze owns known records and both quarantine families;
- entity, action, lineup, possession, and player-match serializers own disjoint
  Silver families;
- the Silver manifest has its own writer;
- Gold/temporal owns Gold, the Gold manifest, and boundary receipts;
- rebuild invokes named serializers and writes only its invocation receipt; and
- health, card, independent review, master verification, gate, Git acceptance,
  and ledger are serial later owners.

The health/card/gate artifact paths and complete `G-W04` conditions remain exact.
The stable/operational split excludes roots, run IDs, clocks, operational pyc
inventories, root-bearing wrapper/editable bytes, uv/cache paths, and output
digests from stable identity while retaining their operational verification.
Two-root equality is correctly required for semantic products, stable environment
evidence, source-derived authority, normalized wrappers, and optional-orphan
predicates rather than actual incidental pyc bytes.

The two-local-commit acceptance ledger also remains intact: full gate first,
integration commit, annotated accepted tag, registry plus clean-tree certificate,
then one ledger commit and final local-only/remote/guard verification. Registry
self-reference, tag movement, a third cleanup commit, stash/reset/history rewrite,
and remote use remain forbidden.

These retained controls pass design readback, subject to:

- updating health and two-root orphan predicates for P1-01; and
- adding the launcher to the ownership/code-authority graph for P1-02.

## Required disposition

R11 cannot be accepted for implementation while either P1 remains. The bounded R12
must:

1. truthfully classify both migration pycs without importing, deleting, or granting
   source authority to them, and update every affected operational count/test;
2. define the exact external launcher implementation, authority, channel,
   ownership, manifest/build handoff, and mutation checks;
3. preserve the exact locked/no-sync inner argv and all passing R11 contracts
   enumerated above; and
4. return for new master and independent review before implementation starts.

There is no recommendation to change Wyscout source selection, CC-BY-4.0 handling,
the one-root uv environment, dependency groups, Python version, storage roots,
container-free policy, local-only boundary, or checkpoint model.

## Scope confirmation

- No Git command or operation was performed.
- No provider acquisition, network request, cloud resource, hosted CI, public
  endpoint, remote, container, or deployment was created.
- No dependency, lockfile, environment, data, source, configuration, migration,
  script, orchestration, or candidate-design path was mutated.
- No pyc or `__pycache__` path was deleted, rewritten, imported, or repaired.
- Only
  `reports/reviews/W04/wyscout-schema-design-independent-review-R8.md` and its
  packet return are in this reviewer's write scope.
