# W04 Wyscout schema design independent review R6

## Decision

**REWORK. Do not dispatch the R7 implementation graph.**

R7 contains a strong deterministic lock-closure and installed-file ownership design,
and its fixed unknown-kind partition/digest grammar is collision-resistant. Neither
of the two intended R7 closures is executable as written, however, and several
previously closed temporal and football-product contracts regress.

The independent challenge confirms the six master-reproduced P1 concerns:

1. dependency availability equality is newly allowed although the existing contract
   and R6 require strict-before;
2. the Gold key drops `role_context_version` and `dependency_lineage_hash`;
3. the six Gold coverage dimensions are replaced by mostly source coverage;
4. record dispatch reads a raw top-level `kind` that does not exist in the profiled
   source;
5. the all-groups installed environment has uv-generated console scripts beyond
   `INSTALLER` and `REQUESTED`; and
6. the environment already contains pyc state that R7 newly makes fatal.

The readback also found two direct retained-schema/path regressions: the exact
player-match key changes, and the known Bronze path changes from `records/...` to
`raw/...`. Two additional P2 reproducibility/detail defects remain in the absolute uv
executable path entering the semantic environment input and in replacing the exact
17-path resource allowlist with unnamed categories.

Any one P1 requires REWORK under the packet. This review proposes no architecture,
project-root, dependency, rights, provider, network, migration, local-only, or
ignore-policy change.

## Scope and independent evidence

The review read the R7 producer packet, master R6 review, complete R6 and R7 designs,
the preceding independent review, accepted source profile, existing evidence
contract, root `pyproject.toml` and `uv.lock`, local-only declaration, ignore policy,
both controlling HTML plans, and the mandatory return template.

Actual local evidence was challenged read-only:

- the source profile's complete field tables for competitions, teams, players,
  matches, and events;
- all-groups installed `.dist-info/RECORD` entries, including executable scripts;
- extracted versus installed pytest `RECORD`;
- generated script bytes/shebangs; and
- current `__pycache__` and pyc cardinality.

No raw provider file, excluded payload, network, provider, dependency operation, or
Git mutation was used. Only this review and its return are authored.

## Intended R7 P1 closure table

| R6 returned P1 | R7 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-THIRD-PARTY-TRANSITIVE-CLOSURE-01` | **PARTIAL / REWORK** | The conservative pre-execution set `L`, recursive marker/extra selection, exact equality to installed set `I`, RECORD-derived import/native/namespace ownership, and runtime `R ⊆ L` are strong and close direct-import pruning. But applying the stated installed rules to all groups necessarily fails on uv-generated console scripts and existing pyc, so the closure cannot admit the required environment. |
| `W04-DESIGN-UNKNOWN-RECORD-KIND-PATH-01` | **PARTIAL / REWORK** | The literal `record_kind=unknown`, closed state, full digest, typed canonical original value, collision failure, containment and reconciliation rules solve the path-token problem. The dispatcher takes the kind from a nonexistent raw payload field rather than the source envelope/file group, so every real profiled JSON row is classified `missing` and quarantined. |

Both corrections can remain bounded. The fixed unknown partition and conservative
locked set should be retained; their authority/executable seams need correction.

## Ranked findings

### P1-01 — R7 reverses the strict temporal cutoff boundary

R7 lines 303-306 require maximum dependency `available_at <= feature_cutoff_ts` and
state that equality passes. R6 lines 494-498 required every observed and available
clock to be strictly before cutoff and explicitly made equality fail.

The existing immutable `TemporalEvidence` contract is conclusive:

- `observed_at >= feature_cutoff_ts` fails;
- `available_at >= feature_cutoff_ts` fails; and
- `available_at_watermark >= feature_cutoff_ts` fails.

An R7 proof accepted at equality cannot adapt into the existing contract. Allowing
facts or accepted human authority at the exact upper bound also weakens the
previously reviewed no-future-fact boundary and contradicts the controlling
blueprint's strict upper-bound semantics.

**Bounded correction:** restore `observed_at < feature_cutoff_ts`,
`available_at < feature_cutoff_ts`, and watermark strict-before for all five
dependencies. Tests must reject equality for decision, review, acceptance,
correction, individual dependency, and aggregate watermark.

### P1-02 — raw payload `kind` is not the record-kind authority

R7 lines 448-457 dispatch by reading a raw top-level JSON member named `kind`.
The accepted profile proves that the source is grouped by completion-declared logical
objects/members, while record shapes do not provide this discriminator:

- competitions expose `area`, `format`, `name`, `type`, and `wyId`, not `kind`;
- teams and players expose their measured entity fields, not `kind`;
- matches expose `competitionId`, `teamsData`, `wyId`, and other match fields, not
  `kind`; and
- all 3,071,395 events expose the measured event fields, with no `$.kind`.

The taxonomy CSV rows likewise derive their record family from their declared source
object, not a JSON member. Under R7 every real JSON record is `raw_kind_state=missing`,
goes to rejected-record quarantine, and never reaches Silver or Gold. This makes the
one manifested raw-to-Gold proof impossible.

Record kind is a source-envelope discriminator established before raw-row parsing:
the exact admitted completion path/file group selects competition/team/player,
event-taxonomy/tag-taxonomy, match, or action. Unknown-kind fixture tests must inject
an unknown **envelope discriminator**, not mutate provider payload fields. The raw
record itself remains untouched.

**Bounded correction:** retain R7's fixed safe unknown path and digest envelope, but
apply it to the typed source-envelope `record_kind` presence/value. Define exact
mapping from each admitted direct/member path to a known kind. Missing/null/non-string
and unsafe/unknown fixture envelope values follow the R7 unknown route. Payload
fields called `kind`, if ever present, remain ordinary measured fields and cannot
choose a serializer/path.

### P1-03 — all-groups uv console scripts contradict the installed `RECORD` rules

R7 lines 725-738 parse installed `RECORD` with the same no-`..` rule as extracted
wheel paths, permit only generated `INSTALLER` and `REQUESTED`, and require installed
`RECORD` to differ only by path rewrites and those two rows.

That is false for the required current all-groups environment. Read-only inspection
found 35 `../../../bin/<name>` installed `RECORD` rows owned by 21 distributions,
including Bandit, Coverage, FastAPI, HTTPX, Hypothesis, import-linter, mypy, NumPy,
pip, pip-audit, pip-licenses, Playwright, Pygments, pytest, Ruff, and Uvicorn.

Pytest is a minimal concrete reproduction:

- extracted pytest `RECORD`: 89 rows;
- installed pytest `RECORD`: 93 rows;
- added rows: `../../../bin/py.test`, `../../../bin/pytest`,
  `pytest-9.1.1.dist-info/INSTALLER`, and
  `pytest-9.1.1.dist-info/REQUESTED`;
- no corresponding `.data/scripts` payload exists in the extracted tree; and
- the two 392-byte scripts have an absolute project-root interpreter shebang.

Thus pytest alone violates the no-`..` parser rule, “only two generated payloads,”
installed row-set equation, and mapped-byte equality. The absolute shebang also makes
physical script bytes and hashes differ between two absolute project roots unless an
explicit stable-versus-operational rule exists.

The direct-only R6 examples did not reveal this because Pydantic and the named native
packages have no generated console scripts. Expanding to the all-groups closure makes
the installer rule incomplete.

**Bounded correction:** enumerate uv-generated console scripts as an exact generated
rule based on verified wheel `entry_points.txt`, exact console/gui entry-point
selection, exact installed relative scheme mapping, mode, body and shebang. Treat
controlled `../../../bin/<safe-name>` installed RECORD rows as environment-scheme
paths, not arbitrary traversal. Deny script execution during rebuild unless
explicitly needed. Separate actual root-bearing script bytes/hashes in operational
evidence from a reviewed root-normalized stable representation used for two-root
identity, while continuing to verify actual installed bytes.

### P1-04 — R7's empty-pyc precondition cannot admit the required current environment

R7 lines 739-743 make every pre-existing `*.pyc` or `__pycache__` in a selected
installation root fatal. The required setup is the existing one-root environment
after `uv sync --locked --all-groups`, implementation tests, and normal `uv run`
verification. The current exact site roots contain 130 `__pycache__` directories and
1,075 pyc files.

`-B` and `PYTHONDONTWRITEBYTECODE=1` prevent new bytecode during the admitted rebuild;
they do not remove earlier bytecode. Admission is specified read-only and owns no
environment cleanup. Making pre-existing caches fatal therefore requires an
unapproved destructive cleanup, a freshly replaced root environment after every
test, or permanent avoidance of the approved verification suite.

This is a direct regression from R6, which enumerated actual pyc, required current
magic and a RECORD-owned source mapping, recorded their physical attributes, denied
all reads/execution, and proved the alternate prefix stayed empty.

**Bounded correction:** restore enumerate-and-deny-read behavior. Pre-existing pyc
must be uniquely mapped to a verified owned `.py`, have the current cache tag/magic
and safe regular path, be recorded operationally, and remain unreadable to rebuild.
New pyc generation remains disabled and the alternate prefix remains empty. Because
pyc may embed an absolute source filename, R8 must explicitly keep root-dependent
pyc bytes out of stable semantic/two-root identity while binding their actual
operational hashes and proving they were never opened.

### P1-05 — the retained Gold key loses role and dependency identity

R6's accepted collision-free Gold key was:

```text
(tenant_id, player_id, competition_id, season_id,
 role_context_id, role_context_version,
 window_definition_id, window_start_utc, window_end_utc,
 feature_cutoff_ts, dependency_lineage_hash)
```

R7 lines 328-333 replace `role_context_version` and
`dependency_lineage_hash` with `feature_schema_hash`. These values are not
interchangeable:

- role-context ID and version are separate retained identity fields;
- `feature_schema_hash` describes accepted field/possession/feature/product schemas;
  it does not identify the exact source manifest, identity bundle or their
  availability clocks; and
- two builds may share a feature schema while having different five-dependency
  lineage.

The build-ID directory does not repair the row schema/key contract. Downstream
consumers, proofs, manifests and later concatenation rely on the full row key and its
lineage member.

**Bounded correction:** restore both `role_context_version` and
`dependency_lineage_hash` to the exact R6 Gold grain. Keep
`feature_schema_hash` as a required proof/row field, not a replacement key member.

### P1-06 — source coverage replaces the retained six Gold coverage equations

R7 lines 335-338 say Gold coverage is source objects, admitted members, match
partitions, event partitions, partition alignment, and identity resolution/exact
exclusion. The first five are source-manifest coverage dimensions from Section 2.

R6's retained Gold coverage is instead exactly identity, lineup, action, coordinate,
possession, and temporal, each with integer numerator/denominator, special
zero-denominator policy only for coordinate/possession, overall minimum, suppression,
and `research_only`/`w04_data_ready` behavior.

Conflating these contracts loses lineup/action/coordinate/possession/temporal
eligibility and duplicates source coverage already bound by the source manifest.
It also cannot satisfy the retained player-match/Gold health checks.

**Bounded correction:** preserve the six source `DataCoverage` dimensions unchanged
on the source manifest and separately restore all six exact R6 Gold dimensions and
their zero-denominator/applicability/status rules.

### P1-07 — the exact player-match key also changes

R6 defines player-match identity as:

```text
(tenant_id, source_manifest_id, match_id, player_id,
 player_match_fact_schema_version)
```

Team is match-bound evidence, not an additional identity repair. R7 lines 324-326
instead describe facts at
`(tenant,competition,season,match,player,team)`, dropping source manifest and schema
version while adding contextual values. That regresses the retained
`W04-DESIGN-PLAYER-MATCH-FACT-01` closure and can change deduplication/version
behavior.

**Bounded correction:** restore the exact R6 player-match key. Competition, season
and match-bound team remain reconciled row/context fields with the retained
result-independent constraints.

### P1-08 — the known Bronze raw path is changed outside the correction scope

R6's exact known raw family was:

```text
.../bronze/build_id=<build_id>/
  records/record_kind=<kind>/source_sha256=<source_sha>/part-00000.parquet
```

R7 lines 348-354 change `records/` to `raw/`. The R7 packet authorised a separate
unknown rejected-record path, not redesign of the already accepted known family.
The manifest, staging suffixes, two-root proof, path grammar tests, packet ownership
and downstream readers depend on this literal path.

**Bounded correction:** restore `records/record_kind=<known-kind>/...` unchanged.
Keep the new `quarantine/rejected-record/record_kind=unknown/...` family disjoint.

### P2-09 — the uv executable's absolute path is not separated from semantic identity

R7 lines 580-592 bind `uv executable path/version/physical SHA-256` into the target
environment record, and Section 7 includes environment in `build_id`. The path is
host-absolute, while R6's accepted stable/operational rule excludes host absolute
paths from canonical build identity.

Version and physical digest can attest the uv executable stably. The resolved
absolute path is useful operational association evidence but makes identical bytes
at another host location produce a different semantic build identity.

**Bounded correction:** retain uv version/physical digest in stable environment
identity and move the resolved absolute path to the operational admission receipt.

### P2-10 — the exact local-resource allowlist is no longer standalone

R6 defines exactly 17 resource paths and keeps strict source, identity, installed
runtime and outputs in separate guarded categories. R7 Section 6.4 replaces that
with categories such as “accepted authority/config artifacts,” “exact window/cutoff
config,” and “neutral-role context” without enumerating the paths, while also
including source manifest and identity bundle in “local resources.”

An implementer cannot reproduce one exact resource list or determine whether the
R6 guarded-category separation is retained. Broad or post-closure discovery is
forbidden, but the exact alternative is missing.

**Bounded correction:** restore the exact R6 17-path list and guarded-category
separation. Any additional window or neutral-context file must be named exactly and
must already be an approved resource/build input; otherwise retain their existing
schema-bound values rather than inventing a file.

## Complete locked/installed ownership challenge

The following R7 elements pass and should be retained:

- PEP 503 normalized distribution identity is independent of import-root,
  underscore wheel spelling, `.dist-info` spelling and display case.
- Every root dependency group is selected from the editable root, and marker/extra
  edges close recursively before execution.
- Wheel choice is tied to exact interpreter/platform tags, including CPython native
  and ABI3 cases.
- `pydantic -> pydantic-core` and
  `polars -> polars-runtime-32` are members of `L` before execution.
- `L == I`, frozen RECORD-derived file ownership, normal/namespace/native rules, and
  runtime `R ⊆ L` prevent runtime manifest expansion.
- Actual uv cache selectors may have absolute raw link text only when resolution is
  contained at one `archive-v0/<opaque>` target under the same cache root.
- Lock declarations remain distinct from locally verified extracted/installed bytes;
  absent wheel ZIPs and sidecars are not falsely promoted.

These passing algorithms are blocked only by the incomplete installed generated-file
and pyc policies above. They do not need replacement by direct-import selection.

## Seven R5 P1 retained-closure table

| R5 P1 | R7 disposition |
| --- | --- |
| `W04-DESIGN-IDENTITY-LOCAL-ROOT-01` | **RETAINED CLOSED** — all identity runtime state remains under `data/working/wyscout/v5/identity`. |
| `W04-DESIGN-OFFLINE-EXECUTABLE-ADMISSION-01` | **REGRESSED / REWORK** — original ZIP truth and extracted/native ownership remain strong, but all-groups console scripts and existing pyc make admission fail; stable host-path separation is incomplete. |
| `W04-DESIGN-FEATURE-AUTHORITY-TEMPORAL-01` | **REGRESSED / REWORK** — exactly five accepted dependencies remain, but equality now passes contrary to strict temporal authority. |
| `W04-DESIGN-IDENTITY-METHOD-01` | **RETAINED CLOSED** — classifications, states, match methods and current resolved-only projection remain exact. |
| `W04-DESIGN-RUNTIME-PATH-OWNERSHIP-01` | **REGRESSED / REWORK** — unknown path is safe and sole-owned, but it uses the wrong dispatch authority and the accepted known path changes literal family. |
| `W04-DESIGN-CHECKPOINT-LEDGER-ORDER-01` | **RETAINED CLOSED** — full gate, acceptance commit/tag, registry/certificate ledger commit and final read-only checks remain ordered. |
| `W04-DESIGN-RESOLVED-IDENTITY-CORRECTION-01` | **RETAINED CLOSED at the behavioral boundary** — queue and direct routes remain distinct, immutable, reviewed, versioned and clocked without synthetic queue history. |

## Earlier accepted finding disposition

| Finding | R7 disposition |
| --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | **REGRESSED at cutoff equality**; period-relative event ordering and null action UTC otherwise remain closed. |
| `W04-DESIGN-SOURCE-SEAM-01` | **RETAINED CLOSED** — only completion-declared payloads are readable; ZIP and excluded entries remain evidence-only/denied. |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | **RETAINED CLOSED** — exact 18 rows, tenant/classification and non-circular manifest identity remain. |
| `W04-DESIGN-REBUILD-CLOCK-01` | **REGRESSED / REWORK** — semantic versus receipt clocks remain separate, but root-bearing console scripts/uv path and fatal pyc break executable/two-root admission. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | **RETAINED CLOSED** — project-derived predicates, review/acceptance and no provider-native claim remain. |
| `W04-DESIGN-GOLD-GRAIN-01` | **REGRESSED / REWORK** — two required key members are dropped. |
| `W04-DESIGN-MINUTES-01` | **RETAINED CLOSED** — no exact/elapsed minutes or per-90 is emitted. |
| `W04-DESIGN-COVERAGE-01` | **REGRESSED / REWORK** — source coverage is substituted for Gold coverage. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **REGRESSED / REWORK** — result independence remains, but the exact key changes. |

Rights/restricted classification, attribution, field/possession/feature authority
routes, identity classifications and two correction routes, period-relative actions,
neutral/no-outcome claims, manifest/receipt sole writers, health/card artifacts, the
full gate, and two-local-commit ledger otherwise remain acceptable.

## Required bounded R8 gates

R8 can remain a report-only correction and can be accepted only if it:

1. restores strict-before temporal eligibility and equality-negative tests;
2. takes record kind from an exact source envelope/file-group mapping, retains R7's
   fixed unknown partition, and never uses raw payload content to choose a family;
3. restores the exact known Bronze path, player-match key, Gold key, and separate six
   Gold coverage dimensions from R6;
4. defines exact uv-generated console-script mapping/bytes/ownership and
   stable-versus-operational handling for absolute shebangs;
5. restores safe pyc enumeration plus read denial instead of requiring destructive
   absence, with root-dependent pyc outside stable identity;
6. keeps the conservative all-groups `L == I`, complete ownership map, and
   no-runtime-expansion design;
7. separates uv's absolute executable path from stable semantic identity;
8. restores the exact resource paths and guarded categories; and
9. retains every otherwise passing source, rights, identity, football, path, health,
   card, gate and ledger boundary.

No dependency/lock change, new environment, provider access, architecture decision,
local-root amendment, or ignore change is required.

## Recommendation

Return R7 for one bounded R8 correction. Do not dispatch implementation or perform
real provider acquisition. Another independent read-only review is required after
the corrected standalone design is produced.

## Packet verification

The two required uv checks and their actual results are recorded in the mandatory
return after final authoring. No direct Git command or Git mutation was performed;
the mandated local-only verifier performs its own configured read-only checks.
