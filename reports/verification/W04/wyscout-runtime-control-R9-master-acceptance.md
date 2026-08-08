# W04 Wyscout runtime-control R9 master acceptance

- Date: `2026-08-03`
- Task: `W04-WYSCOUT-RUNTIME-CONTROL-01-R9`
- Review: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R9`
- Decision: **MASTER_ACCEPTED**
- Independent findings: `P0/P1/P2 = 0/0/0`

## Accepted correction

R9 is accepted under the standing bounded-correction authority dated
`2026-08-02`. It closes `W04-RUNTIME-R8-P1-01` without changing the logical
model, 23-root roster, product population, intended output, dependency set,
data-rights authority, digest meaning/formula, or local-only boundary.

The direct-execution branch now captures, before its first helper definition,
the exact ordered 23 startup names and object references, the exact resident
`BuiltinImporter` and `FrozenImporter` objects, and immutable normalized
package/parent/submodule-location shapes for all 19 governed built-in/frozen
rows. The full first-user verifier requires the live objects and importer
authorities to be those exact captured objects and rechecks every complete
shape alongside all retained R8 registration, frozen, loader, source, cache,
location, encoding, `__main__`, order, distinctness, environment, argv,
descriptor, prefix, chronology, child-result, and product predicates.

The R8 launcher PYC collector remains strictly metadata-only and byte-for-byte
compatible in meaning with the unchanged admission child. Python roles retain
unconditional PYC/PYO read denial. Complete PYC header/content authority remains
solely in the shell pre/post inventories.

## Frozen accepted bindings

| Artifact | SHA-256 |
| --- | --- |
| R9 producer packet | `d09461cc3c48191f977282c6aaf23c0ea983ea49c917054bc8390925b96634c7` |
| R9 review packet | `8502de2743e5d48e035ed7fc93e4e6e9b3522bad644306f0d03301e03635435c` |
| admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| launcher | `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb` |
| runtime-control tests | `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf` |
| producer return | `b814babcd6465e537d4d545b794ba2cc2b5037a60e18e08a0d00867527110ff5` |
| independent review | `cf4d4df85c4960930fd02d653636358d705dd8b05e8b343e349480197561b02a` |
| reviewer return | `003f8c3fa0163a8e6c39deef63d58a9f4f336f6d013455bbd13a5f076dfe933e` |
| disclosed operational launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |
| shell PYC census helper | `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d` |

## Producer and independent-review evidence

- Producer retained gate session `37785`: Ruff/mypy/Bandit/import/local-only
  green; exact population `268 passed in 1485.40s`.
- Independent review retained gate session `10474`, pytest PID `31543`: exact
  population `268 passed in 1505.74s`; focused exact-uv population `32 passed`;
  canonical five-case add/remove/reorder/alias/duplicate harness `5/5` rejected;
  direct-import audit recorded zero mutations.
- Independent review decision: **PASS**, `P0/P1/P2 = 0/0/0`.
- The review's optional first roster harness used a noncanonical `/var` spelling
  after the mandatory gate and closed its `set -e` shell on an earlier prefix
  precondition. The master classified this as bounded review-harness procedural
  rework, prohibited repeating pytest, and required only the canonical
  `/private/tmp` harness plus final postflight. Sealing session `78303`, PID
  `40432`, completed those steps successfully. This is not a producer finding.

## Fresh master reproduction

The master began with locked all-groups offline sync. The first sandboxed sync
and first gate-shell preflight were denied read access to the already admitted
local uv-cache `.git` entry and executed no project check. The master then used
approved read-only local-cache access; no network, dependency, lock, or
environment mutation occurred.

| Master check | Result |
| --- | --- |
| `uv sync --locked --all-groups --offline` | exit `0`; `83` resolved, `82` audited |
| Ruff format check | exit `0`; three files formatted |
| Ruff check | exit `0`; all checks passed |
| mypy over admission/launcher/runtime tests | exit `0`; no issues in three files |
| exact six-file pytest population, retained session `4304` | exit `0`; `268 passed in 1487.21s` |
| Bandit over admission/launcher | exit `0`; no findings |
| import-linter | exit `0`; `3 kept, 0 broken` |
| local-only verifier | exit `0`; `25` checks, zero failures, `main`, zero remotes |
| `git diff --check` | exit `0`; empty output |
| `git remote` | exit `0`; empty output |

Every Python-backed master command used locked/no-sync uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B` where applicable, and disabled or
redirected tool caches under `/tmp`.

## Master PYC pre/post evidence

The master reproduced the exact shell-only helper before and after its complete
gate:

- selected site-packages: `1,087` PYC files plus `131` cache directories,
  `1,218` rows, byte-identical pre/post SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`;
- repository excluding `.venv`: `111` PYC files plus `21` cache directories,
  `132` rows, byte-identical pre/post SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`.

The disclosed launcher PYC remained mode `0644`, link count `1`, size
`199084`, device `16777231`, inode `91632142`, mtime/ctime `1785700057`, first
16 bytes `cb0d0d0a00000000cf9e6f6a47c90200`, and the frozen digest above. It was not
deleted, restored, rewritten, imported, or read through Python.

## Residual and disposition

The accepted same-trust-domain residual is unchanged: a hypothetical PYC
replace-and-restore event preserving every Python-observed metadata field
between shell inventory endpoints cannot be excluded by Python. Endpoint
header/content inventories and unconditional Python PYC denial remain the
controlling evidence boundary.

R9 is **MASTER_ACCEPTED**. The runtime-control gate is released for the exact
master-owned two-real-root invocation packet; no root has been published by
this acceptance.
