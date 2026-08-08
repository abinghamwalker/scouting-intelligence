# W04 Wyscout schema design R12 — master verification

## Decision

`REWORK`. The master read all 2,379 R12 design lines, the complete 103-line
return, and the full R11-to-R12 delta after a fresh locked all-groups sync. R12
correctly classifies the two omitted migration pycs and gives the local launcher
an explicit path, role, channel family, manifest/build ownership, and stable
identity. Three new launcher-contract defects remain. Independent review and
implementation stay blocked.

## Integrity

- R12 design: `127,477` bytes; SHA-256
  `f265b0761d8d7830b7c75d7b45e6d156837b8555f0d9c269df96f3a074306fd5`.
- R12 return: `5,314` bytes; SHA-256
  `721d912cc906fa8db4ffe7183eb2f59b13d5aee43ddf6b4b08ee5321210f79b0`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.
- Producer ownership remained limited to the R12 design and return.
- The future launcher, admission entry point, and rebuild entry point are absent.

## Closures accepted

R12 now truthfully specifies 58 repository pycs in 19 cache directories:
35 mapped normal, 20 mapped pytest, and the exact migrations-env,
migrations-foundation, and PostgreSQL source-absent inert orphans. Each predicate
has the reproduced absent source, path, magic, tag, mode, size, and digest and
grants no code/import/build authority. Health, stable/operational identity,
negative tests, required test 14, and two-root optional presence are updated
together.

The future `scripts/launch_wyscout_v5.py` is transient local control only. R12
assigns its two child launches, prefix checks, result channels, code-manifest
publication, and build-ID calculation without granting product or receipt writes.
It retains both exact child argv and the passing R11 source, rights, temporal,
identity, product, environment, resource, gate, ownership, and ledger contracts.

## P1 — pre-first-instruction runtime claim is false

R12 says the launcher begins with built-in/frozen modules only and requires zero
in-place pyc reads before its first-instruction guard. Under its exact
`uv run --locked --no-sync python -S -B` startup, the master reproduced three
already-loaded file-backed modules:

| Module | Source size | Source SHA-256 |
| --- | ---: | --- |
| `encodings` | 5,884 | `78c4744d407690f321565488710b5aaf6486b5afa8d185637aa1e7633ab59cd8` |
| `encodings.aliases` | 15,677 | `6fdcc49ba23a0203ae6cf28e608f8e6297d7c4d77d52e651db3cb49b9564c6d2` |
| `encodings.utf_8` | 1,005 | `ba0cac060269583523ca9506473a755203037c57d466a11aa89a30a5f6756f3d` |

Verbose startup proves CPython reads each existing stdlib pyc before user code.
`-B` prevents writes; it does not prevent reads. A constructive probe with an
exact empty `PYTHONPYCACHEPREFIX` instead loads the three verified sources and
leaves that prefix empty. R13 must give the outer control process a distinct,
master-created contained empty prefix, bind its operational ownership, and state
the truthful pre-guard encoding bootstrap rather than claiming only frozen
modules. This is a transient control prefix, not an architecture or product
runtime change.

## P1 — the claimed original launcher descriptor cannot reach the launcher

The master invocation owner opens the launcher before `uv run`, and the launcher
later claims to keep that original descriptor through both children. R12 defines
no inherited descriptor variable, descriptor number, inheritable/CLOEXEC rule,
uv-to-Python preservation requirement, or close ownership. The launcher can only
reopen its path after Python has already executed it, which is not the stated
prelaunch descriptor and does not close the claimed handoff.

R13 must define one exact inherited read-only launcher-source descriptor, bind it
to the accepted bootstrap tuple, transport it through uv/Python, and require
positive preservation tests with no fallback. Child entry-point source
descriptors need equally explicit inheritance/self-observation, or the design
must narrow its race claim to the deterministic pre/post guarantees supported by
the local threat model rather than claiming impossible path-execution identity.

## P1 — role-specific result payloads are not closed schemas

The top-level frame is useful, but each `result` remains “role-specific closed
object” followed by prose such as “complete component-proof digest.” Exact field
names, types, cardinalities, encoding constraints, and nested row schemas are
missing for both admission and rebuild. Different implementations could emit
different canonical JSON while satisfying that prose.

R13 must give both result objects exhaustive field-name/type grammars, including
the exact manifest-bytes key, component-proof key, rebuild receipt row, ordered
layer rows, and final recheck record. Unknown or missing fields must fail.

## Checks

- Fresh `uv sync --locked --all-groups`: PASS; 83 resolved, 82 audited.
- Full R12/return/delta readback: PASS.
- R12 size and future-script absence: PASS.
- Current repository census: PASS; 58 pycs, 19 directories.
- Exact no-site startup module probe: FAIL R12 claim; three file-backed encoding
  modules precede user code.
- Verbose bytecode probe: FAIL R12 claim; all three encoding pycs are read.
- Empty-prefix constructive probe: PASS; source loads and no prefix contents.
- Local-only verification: PASS; 25 checks, zero failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider, network, cloud, hosted CI, public endpoint, remote, container, or
deployment was created.
