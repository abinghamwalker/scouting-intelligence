# W04 Wyscout schema design independent review R5

## Decision

**REWORK. Do not dispatch the R6 implementation graph.**

R6 materially closes all seven P1 defects returned from the R5 design and retains the
previously accepted source, temporal, football, coverage, rights, identity-history,
resource, and gate boundaries. The cache/install correction is also substantially
truthful against the current machine: the `wheels-v5` selectors are symlinks to
`archive-v0` extracted trees, hyphenated PEP 503 directory names coexist correctly
with underscore-normalized wheel and `.dist-info` names, native tags are present,
only extracted `RECORD` is unhashed, and uv's installed `RECORD` adds exactly the
observed `INSTALLER` and `REQUESTED` rows for the samples challenged.

The design nevertheless has two new independently reproducible P1 defects:

1. repository AST closure selects direct external distribution owners but never
   closes over their locked/runtime distribution dependencies, even though actual
   admitted packages immediately import separately owned distributions and R6 rejects
   any import from an unadmitted owner; and
2. unknown record kinds are required to produce rejected-record rows, but the exact
   quarantine path permits only the seven known `record_kind=<kind>` values.

Both defects are execution blockers in mandatory positive/negative tests, rather than
documentation polish. The packet requires REWORK whenever any P0-P2 executable-truth
or path/ownership defect remains. No implementation packet, provider acquisition,
architecture change, or self-approval is authorised by this review.

## Scope, authority, and method

This was an independent read-only challenge of the standalone R6 design against:

- the R6 producer packet and its R5 master review;
- the R4 independent review, including all seven returned P1 findings;
- the current `local-only` declaration and `.gitignore`;
- the existing `EvidenceDependency` contract;
- both controlling HTML plans; and
- the actual local uv cache and `.venv` state needed to test the claims made in
  Sections 9.1-9.3.

No direct Git command, Git mutation, network access, provider acquisition,
dependency operation, configuration change, code change, or data mutation was
performed. The mandatory local-only verifier executed its own configured read-only
Git checks. The only authored paths are this review and the mandatory packet return.

The review treated a stated mandatory test as executable only when its complete input
domain, deterministic path, authority, writer, temporal clocks, and failure behavior
are constructible from the design. Passing prose elsewhere does not waive a
contradiction at one of those boundaries.

## Ranked findings

### P1-01 — external executable admission is direct-only, not a distribution closure

R6 Section 9.1 defines an AST traversal over reachable **repository-local** modules
and package `__init__.py` files (lines 768-772). It then selects one compatible lock
wheel “for every external distribution owning a closure import” (lines 774-777).
There is no subsequent rule that expands selected external owners through selected
`uv.lock` dependency edges, verified `Requires-Dist` metadata, or the actual imported
owner set.

That omission conflicts with the fail-closed runtime rule at lines 878-883: an import
from an unadmitted distribution fails. It also conflicts with the code-manifest
objective, because an admitted repository import normally executes package code whose
native or Python dependencies are separately distributed.

This is observable in the current root environment without executing provider code:

- `pydantic/__init__.py` imports `.version`; `pydantic/version.py` imports
  `pydantic_core`, and many Pydantic modules import it directly. The separately owned
  `pydantic_core-2.46.4.dist-info` and its native extension are present.
- `polars/_plr.py` imports `_polars_runtime_32` and
  `_polars_runtime_32._polars_runtime`. The separately owned
  `polars_runtime_32-1.43.0.dist-info` and native extension are present.
- The actual cache selectors for both transitive/native distributions exist under
  `wheels-v5/pypi/pydantic-core/...` and
  `wheels-v5/pypi/polars-runtime-32/...`, but R6's selection algorithm has no step
  that necessarily selects them when repository code imports only `pydantic` or
  `polars`.

The problem is not solved by runtime monitoring. Monitoring can detect the
unadmitted owner, but R6 explicitly requires that condition to fail. Nor is it solved
by the root all-groups environment: Section 9 is intentionally an exact admitted
closure, and no statement admits every installed distribution.

As specified, the mandatory positive rebuild can therefore fail before data
processing merely by importing an approved direct dependency. Conversely, silently
admitting the newly observed owner at runtime would make the canonical code manifest
and build identity depend on execution order and would violate pre-execution
admission.

**Exact bounded correction required:** define one deterministic pre-execution
distribution closure. A valid correction may start from the repository AST external
import owners and recursively close selected, marker-applicable dependency edges from
`uv.lock`, cross-checking each edge against verified extracted `METADATA`
`Requires-Dist`; or it may conservatively admit the exact locked all-groups
environment. In either case R7 must:

1. define distribution-name/import-root ownership, including underscore/hyphen and
   namespace cases;
2. select marker branches and compatible wheel records for every closure member
   before hashing;
3. apply the existing cache, extracted-tree, installed-file, interpreter and guarded
   read rules to every member;
4. require the runtime loaded third-party owner set to be a subset of that
   precomputed set; and
5. test at least the concrete `pydantic -> pydantic-core` and
   `polars -> polars-runtime-32` native edges plus an unowned negative import.

No network or new dependency is needed for this correction.

### P1-02 — the unknown-record quarantine path is unconstructible

R6 gives one exact token grammar: `kind` is exactly one of `competition`, `team`,
`player`, `event-taxonomy`, `tag-taxonomy`, `match`, or `action` (lines 609-615).
Both quarantine families then require `record_kind=<kind>` (lines 621-631).

The same section requires unknown record kinds to produce rejected-record rows
(lines 633-640), and the mandatory test list explicitly requires unknown-record
quarantine and manifest reconciliation (lines 1119-1122). An unknown value is, by
definition, not one of the seven allowed path tokens. R6 specifies neither a fixed
`unknown` partition nor a safe canonical encoding/digest of the rejected raw kind.

An implementer must therefore choose one of three unauthorised behaviors:

- violate the exact path grammar by placing the raw unknown label in `<kind>`;
- collapse it into one of the known tokens and misstate the rejected record's kind;
  or
- omit the required rejected-record artifact.

Using the raw provider value directly would additionally conflict with the path rules
that reject empty, dot, dot-dot, percent-encoded, or case-folded segments. This cannot
be repaired as a mere test implementation detail because the path is part of the
manifest bytes and the two-root deterministic contract.

**Exact bounded correction required:** define a deterministic fail-closed unknown
partition, for example `record_kind=unknown` plus an in-row canonical raw-kind value
and SHA-256, or define a reviewed collision-free safe-token mapping and include its
version/digest in the manifest and build inputs. Specify empty/null/non-string/unsafe
labels, keep the original value in the rejected row, assign the existing Bronze sole
writer, and test two distinct unsafe unknown values for non-confusion and two-root
equality.

## Seven R5 P1 closure table

| R5 returned P1 | R6 result | Independent basis |
| --- | --- | --- |
| `W04-DESIGN-IDENTITY-LOCAL-ROOT-01` | **CLOSED** | All queue, bundle and correction runtime outputs move beneath `data/working/wyscout/v5/identity/...`, which is covered by the existing ignored generated-data boundary. No new local root or `.gitignore` amendment is claimed. |
| `W04-DESIGN-OFFLINE-EXECUTABLE-ADMISSION-01` | **CLOSED for the returned archive/cache and generated-file defect; new P1-01 remains** | R6 truthfully distinguishes lock-declared archive metadata from absent locally verified wheel ZIP bytes; uses an exact `wheels-v5` symlink to an `archive-v0` extracted tree; verifies extracted `RECORD`; and enumerates uv-generated `INSTALLER`, `REQUESTED`, rewritten installed `RECORD`, and denied pyc. Actual cache/install challenge supports those rules. The newly found distribution-closure omission is separate and is not counted as failure to close the earlier false-archive premise. |
| `W04-DESIGN-FEATURE-AUTHORITY-TEMPORAL-01` | **CLOSED** | Decision, candidate registry, independent review and master acceptance are serial and digest-bound. Gold has exactly five dependencies, including three `feature_schema` entries for field, possession and supported-feature authority. Decision/review/acceptance clocks are explicit, and cutoff before or equal to any of them fails. |
| `W04-DESIGN-IDENTITY-METHOD-01` | **CLOSED** | Section 5.2 defines the complete classification/state/match-method matrix: deterministic exact composite or reviewed exact alias may resolve; ambiguous collision, orphan parent and conflict require review; invalid structure is rejected; only resolved rows enter the valid projection; all other combinations fail. Runtime invention is forbidden. |
| `W04-DESIGN-RUNTIME-PATH-OWNERSHIP-01` | **CLOSED for every previously omitted product family; new P1-02 remains** | Bronze, both quarantine families, every Silver product, Gold, staging, layer manifests, invocation receipts and boundary receipts have exact formulas and sole writers. The new contradiction exists only for the required unknown-kind instance of the rejected-record family. |
| `W04-DESIGN-CHECKPOINT-LEDGER-ORDER-01` | **CLOSED** | R6 follows gate -> local acceptance integration commit -> annotated accepted tag -> registry plus predicate certificate -> separate ledger commit -> final read-only clean/remote/guard/local-only checks. Exact messages and the stable tag target are stated; the registry does not contain the later ledger SHA. |
| `W04-DESIGN-RESOLVED-IDENTITY-CORRECTION-01` | **CLOSED** | Queue-bound correction and direct correction are distinct reviewed routes. The direct route binds a current resolved row and requires no queue ID/snapshot/history; both routes preserve prior bytes, create a new row and supersession edge, advance truthful availability, regenerate the bundle, and cover resolved/rejected dispositions. |

The closure of all seven returned defects is material. It does not permit acceptance
while a fresh P1 is present.

## Focused boundary challenges

### Actual uv selector naming, symlinks, and extracted `RECORD`

The current uv cache supports R6's corrected association premise:

| Distribution | PEP 503 selector directory and suffix | Observed target property |
| --- | --- | --- |
| Pydantic 2.13.4 | `pydantic/2.13.4-py3-none-any` | symlink to one `archive-v0` extracted tree |
| pydantic-core 2.46.4 | `pydantic-core/2.46.4-cp312-cp312-macosx_11_0_arm64` | hyphenated selector plus underscore `.dist-info`; one native arm64 tree |
| Polars 1.43.0 | `polars/1.43.0-py3-none-any` | symlink to one extracted tree |
| polars-runtime-32 1.43.0 | `polars-runtime-32/1.43.0-cp310-abi3-macosx_11_0_arm64` | hyphenated selector plus underscore wheel/runtime owner; one native ABI3 tree |
| PyArrow 23.0.1 | `pyarrow/23.0.1-cp312-cp312-macosx_12_0_arm64` | one native extracted tree |
| PyYAML 6.0.3 | `pyyaml/6.0.3-cp312-cp312-macosx_11_0_arm64` | PEP 503 name is lowercase `pyyaml`; native extracted tree |
| DuckDB 1.5.5 | `duckdb/1.5.5-cp312-cp312-macosx_11_0_arm64` | one native extracted tree |

The raw symlink text on this machine is absolute, not the abbreviated relative arrow
shown in R6's examples. R6 remains executable because it separately records raw link
text and requires the resolved target to normalize to exactly one
`archive-v0/<opaque-key>` beneath the same resolved cache root. R7 must not change
that into a literal relative-link-text requirement.

For the seven challenged extracted trees:

- no target-tree symlink was found;
- exactly one `.dist-info/RECORD` was found;
- the only row with empty hash or size was `RECORD` itself; and
- native and pure-Python wheel suffixes match the observed selector names.

This closes the R5 archive-availability defect truthfully: original wheel ZIP hashes
and sizes remain unverified and sidecars remain operational evidence only.

### Installed metadata, native payload, and pyc rules

Installed Pydantic, pydantic-core, Polars, polars-runtime-32, PyArrow, PyYAML, DuckDB,
and NumPy each contained:

- `INSTALLER` with exactly bytes `75 76` hexadecimal (`b"uv"`, no newline);
- `REQUESTED` with zero bytes; and
- installed `RECORD` rows for those files with the expected URL-safe unpadded
  SHA-256 values and sizes 2 and 0.

For four representative pure/native distributions, extracted versus installed
`RECORD` line counts were respectively `111 -> 113` (Pydantic), `10 -> 12`
(pydantic-core), `7 -> 9` (polars-runtime-32), and `750 -> 752` (PyArrow), consistent
with exactly the two generated rows. The current installed files were not observed as
hardlink aliases to the challenged cache members. R6's separate actual-pyc
enumeration, current magic/source mapping, read denial, alternate empty bytecode
prefix, `-B`, and `PYTHONDONTWRITEBYTECODE=1` are coherent.

The generated rules pass this review. They do not repair P1-01, because exact bytes
can still belong to a distribution the selection phase never admits.

### Stable versus operational digest domains

R6 correctly keeps resolved host cache paths, raw symlink text, opaque `archive-v0`
keys, lstat details and `.http`/`.msgpack` sidecar locations in the operational
admission receipt. The canonical code manifest instead binds stable selector
identity, association basis, extracted tree/file/metadata/`RECORD` digests, and the
truthful false archive-verification flags. Semantic products and `build_id` exclude
host absolute paths, cache keys, receipt run IDs and receipt clocks.

The stable digest therefore follows verified executable content while the operational
receipt proves how this machine associated that content. No circular build-ID or
host-path dependency was found.

### Five temporal dependencies and feature clocks

R6 has exactly five ordered dependencies:

1. identity bundle with identity availability;
2. source manifest with source availability;
3. field registry with field acceptance;
4. possession taxonomy with possession acceptance; and
5. supported-feature registry with feature acceptance.

The three authority dependencies use the existing `feature_schema` enum with stable
rank then ID order. `feature_schema_hash` binds all three decision, artifact,
independent-review, acceptance and clock domains. A cutoff before or equal to
decision, review or acceptance is required to fail, while a later cutoff still
passes the contract's strict `observed_at < cutoff` and `available_at < cutoff`
rules. The Gold manifest binds all five dependencies and feature schema. No clock
cycle or feature-registry self-digest was found.

### Identity classifications and the two correction routes

The R6 classification matrix is closed over accepted states and methods. Deterministic
resolution is limited to exact provider-ID composite matches; reviewed exact alias is
authority-bound; ambiguous collision, orphan parent and conflict are review-required;
invalid structure is rejected; only resolved rows project validly. Tests reject every
other combination.

The queue route binds an existing immutable queue item and its prior row. The direct
route binds a currently resolved row, explicitly forbids a queue item, and creates no
synthetic queue snapshot/history. Both routes require decision, independent review
and master acceptance; preserve prior crosswalk bytes; add a correction record, new
crosswalk row and supersession edge; advance availability; and regenerate the
content-addressed bundle. Identity bundle/dependency/build equality remains exact.

### Physical paths, staging, quarantine, receipts, and sole writers

Known-kind Bronze raw paths, all eight Silver products, Gold player-window
partitions, payload staging, the empty alternate pycache, three layer manifests,
invocation receipts and per-Gold temporal receipts are deterministic and non-overlap
is mandatory. Sole serializers and sole manifest/receipt writers are named, and
`rebuild.py` may invoke them but cannot serialize products or manifests.

Layer manifest sibling staging is operationally precise, and final manifests remain
committed evidence. Successful atomic rename removes the sibling partial. This review
does not elevate interrupted-run cleanup to a separate finding, but implementation
must still prove that partials are rejected by readers and cannot survive a passing
clean-tree gate.

The one failed path case is the mandatory unknown-record family in P1-02.

### Gate, acceptance commit/tag, and ledger

The R6 sequence matches the controlling workflow: all implementation and independent
reviews pass first; master emits candidate verification, machine gate and acceptance
evidence; full `G-W04` passes while the registry remains pre-checkpoint; the master
creates `C_accept` with exact message `phase(w04): accept governed data spine`; the
annotated `checkpoint/w04-accepted` tag points permanently to it; only then are the
registry and clean predicate certificate written and committed with exact ledger
message `orchestration(w04): record accepted checkpoint ledger`.

The registry records `C_accept`, not the future ledger commit. The predicate
certificate avoids its own digest/tree/future SHA. Final clean/empty-remote/active
guard/registry/local-only checks are read-only and cannot create a third cleanup
commit. No registry-before-checkpoint cycle or tag movement remains.

## Retained R4 closure table

| R4 area | R6 disposition |
| --- | --- |
| Identity clocks | **RETAINED CLOSED** — valid time, decision observation, acceptance availability and correction watermark remain distinct; equality to cutoff fails and correction changes bundle/dependency/build identity. |
| W04.3 identity lifecycle | **CLOSED** — four kinds, exact classifications/methods, three states, immutable queue/bundle/corrections, both correction routes and generated-root ownership are complete. |
| Runtime/phase ownership | **CLOSED for returned scope** — all prior products, manifests, receipts, card, health, review, master, gate and ledger owners are exact. P1-02 is a new unknown-token instance. |
| Executable/resource closure | **CLOSED for returned scope** — extracted-cache truth, installed generated rules, interpreter/libpython/stdlib and 17 exact local resources are specified. P1-01 is a new selection-closure defect. |

## Six returned-defect disposition table

| Earlier returned defect | R6 disposition |
| --- | --- |
| `W04-DESIGN-CODE-CHECKPOINT-01` | **CLOSED for prior requirements; implementation blocked by new P1-01** — code/cache/install/interpreter/resource admission is pre-Gold and independently reviewed, but its distribution seed set is not transitively closed. |
| `W04-DESIGN-SEMANTIC-TEMPORAL-BOUNDARY-01` | **CLOSED** — identity plus all three feature authorities have truthful clocks; the serving adapter remains operational and is excluded from Gold identity. |
| `W04-DESIGN-SEMANTIC-AUTHORITY-SOURCE-01` | **RETAINED CLOSED** — field and possession authorities have decision, independent review, master acceptance, project-derived semantics and conservative unknown handling. |
| `W04-DESIGN-PACKET-GRAPH-01` | **CLOSED for previously omitted graph rows; implementation blocked by P1-01/P1-02** — serial authority/shared/gate work and disjoint Silver writers are explicit. |
| `W04-DESIGN-MANIFEST-FILE-COUNT-01` | **RETAINED CLOSED** — ordered completion, seven objects and ten archive members remain exactly 18. |
| `W04-DESIGN-SOURCE-COVERAGE-CONTRACT-01` | **RETAINED CLOSED** — strict source member/field/type/count coverage remains distinct from downstream Gold coverage. |

## Previously accepted findings retained

| Finding | R6 disposition |
| --- | --- |
| `W04-DESIGN-SOURCE-SEAM-01` | **RETAINED CLOSED** — completion-declared direct/member bytes only; ZIP/downstream duplication, symlink and escape paths fail. |
| `W04-DESIGN-GOLD-GRAIN-01` | **RETAINED CLOSED** — deterministic neutral context and schema/window versions remain in key and UUID identity. |
| `W04-DESIGN-MINUTES-01` | **RETAINED CLOSED** — nominal lower/upper bounds and censoring are explicit; elapsed/exact minutes and per-90 are suppressed. |
| `W04-DESIGN-COVERAGE-01` | **RETAINED CLOSED** — six integer dimensions, zero-denominator behavior, applicability and overall minimum remain exact. |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **RETAINED CLOSED AS ROW SCHEMA** — match-bound team, result independence, evidence counts/flags, proof and lineage remain exact; dispatch is blocked only by the new admission/path findings. |

## Original nine-finding disposition after R6

| Original finding | Disposition |
| --- | --- |
| `W04-DESIGN-EVENT-CLOCK-01` | **CLOSED** — period-relative Decimal ordering, nullable action UTC, match-only cutoff and strict dependency availability agree. |
| `W04-DESIGN-SOURCE-SEAM-01` | **CLOSED** |
| `W04-DESIGN-MANIFEST-BRIDGE-01` | **CLOSED** — non-circular IDs, tenant/classification, 18 rows and strict source coverage agree. |
| `W04-DESIGN-REBUILD-CLOCK-01` | **CLOSED for semantic/operational clocks; implementation blocked by P1-01** — rebuild/run receipt clocks remain outside semantic identity. |
| `W04-DESIGN-POSSESSION-AUTHORITY-01` | **CLOSED** |
| `W04-DESIGN-GOLD-GRAIN-01` | **CLOSED** |
| `W04-DESIGN-MINUTES-01` | **CLOSED** |
| `W04-DESIGN-COVERAGE-01` | **CLOSED** |
| `W04-DESIGN-PLAYER-MATCH-FACT-01` | **CLOSED AS SCHEMA; IMPLEMENTATION BLOCKED** only by P1-01/P1-02. |

## Required bounded R7 gates

An R7 candidate can be accepted only if it:

1. adds a deterministic pre-execution transitive distribution closure, exact
   import-root ownership and runtime-owner-subset test, including the observed
   Pydantic and Polars native edges;
2. defines the safe deterministic `record_kind` partition for unknown record kinds
   and proves distinct unsafe values cannot collide or escape;
3. retains all seven R5 P1 closures without changing project root, dependency policy,
   local-only boundary, rights, or provider state;
4. retains exact extracted-cache and installed-file truth, including absolute raw
   symlink text handling, original-wheel absence, stable/operational separation and
   generated metadata/pyc rules;
5. retains exactly five temporal dependencies and all decision/review/accept clocks;
6. retains both identity correction routes and all physical sole-writer boundaries;
7. retains the gate -> acceptance commit/tag -> registry/certificate ledger sequence;
   and
8. receives another independent read-only review before implementation dispatch.

## Recommendation

Return R6 for bounded R7 correction of P1-01 and P1-02 only. The architecture,
project root, local-only boundary, dependency set, rights decision and provider
state do not need to change. No real provider acquisition or W04 implementation
should begin from this candidate.

## Packet verification

The packet acceptance checks are recorded in the mandatory return. Review-evidence
inspection used only read-only shell commands; the two required uv commands were run
after both owned artifacts were authored. No direct Git command or Git mutation was
performed; the mandatory local-only verifier performed its internal read-only Git
checks.
