# W04 Wyscout runtime-control independent review R9

Date: 2026-08-03

## Decision

**PASS.** Findings are `P0=0`, `P1=0`, `P2=0`.

R9 closes the R8 registered-object and complete built-in/frozen shape finding.
The exact 23 startup name/object pairs, exact resident importer objects, and all
19 normalized package/parent/location shapes are captured in the first direct
execution branch before the first helper definition. The full first-user
verifier compares those object references with `is`, compares the importer
authorities with `is`, and requires each current normalized shape to equal its
captured startup shape alongside every retained R8 row predicate.

Fresh direct exact-uv attacks against a registered built-in replacement, a
registered frozen replacement, each built-in/frozen package, parent and search
location field, both importer authorities, and add/remove/reorder/alias/duplicate
roster cases all reject before continuation. The R8 metadata-only PYC correction,
admission-child row equality, unconditional PYC denial, encoding and transport
closure, local-only boundary, and disclosed operational-PYC evidence are retained.
The exact required `268`-test final-hash population and all static/security/local-
only checks pass.

## Frozen bindings and read-only chain of custody

Every fixed binding matched before merits work and again after the complete gate:

| Binding | Independently observed SHA-256 |
| --- | --- |
| R9 review packet | `8502de2743e5d48e035ed7fc93e4e6e9b3522bad644306f0d03301e03635435c` |
| R9 producer packet | `d09461cc3c48191f977282c6aaf23c0ea983ea49c917054bc8390925b96634c7` |
| admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| launcher | `6211ff1cd0b51bdd3ab24fe26358077f46f1ad0526ff60126776606ca01243eb` |
| runtime-control tests | `12924b9905a8334c4a6f83bb00b170059be0bb965a1d3d6b4f0c09d364a95abf` |
| producer return | `b814babcd6465e537d4d545b794ba2cc2b5037a60e18e08a0d00867527110ff5` |
| R8 review | `0f4a023fc55c7800f91e9e1f7247059c747d42dd69108e86266ba4e34b7f645c` |
| R8 reviewer return | `a99d9a24b59b46d3132cc6ef3f15a291246ffa469307b5c4a0e88bd87a43d650` |
| disclosed launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |
| shell PYC census helper | `2702b38453c95e428e9289cfc0bd6a9d0f1a748aeb33f1bad1e1c7033eaf4a6d` |

No producer, source, test, dependency, lock, PYC, product, manifest, receipt,
real-root, data, run, configuration, or orchestration byte was edited. Only this
review and its mandatory return were written in the repository. Independent
fixtures and review caches remained under `/private/tmp` or `/tmp`.

The final shell-only preflight and postflight inventories were byte-identical:

- selected site-packages: `1,087` PYC files and `131` cache directories, `1,218`
  complete rows, inventory SHA-256
  `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e`;
- repository excluding `.venv`: `111` PYC files and `21` cache directories,
  `132` complete rows, inventory SHA-256
  `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2`.

Both final `cmp` operations returned zero. The disclosed launcher PYC remained
one repository row with mode `0644`, link count `1`, size `199,084`, device
`16777231`, inode `91632142`, mtime/ctime `1785700057`, first sixteen bytes
`cb0d0d0a00000000cf9e6f6a47c90200`, and the frozen digest above.

Every Python-backed merits command used locked/no-sync offline uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B`, disabled pytest cache output where
applicable, and review-only cache prefixes. The initial sandboxed focused command
could not read an existing uv-cache `.git` path and exited `2` before collection;
it executed no test and changed no repository byte. The same command then ran
with read-only local-cache access and passed.

## Earliest startup binding and direct-import trace

The first executable launcher statement is the direct-execution branch at
`scripts/launch_wyscout_v5.py:5`. That branch binds `sys`, requires the literal
ordered 23-name roster, captures the 23 ordered `(name, object)` references,
captures the exact `BuiltinImporter` and `FrozenImporter` objects, and captures
the ordered 19-row immutable normalized shape tuple at lines `5-91`. The first
helper definition does not begin until line `93`. Therefore no later helper,
file-backed import, launcher body, guard, UUID sample, child operation, or
publication path precedes those captures.

The first-user verifier at lines `620-773` independently reconstructs the exact
23 live pairs and compares every live name and object to the startup pair using
object identity. It separately requires 23 distinct non-null live objects. It
requires the two live importer attributes to be the captured importer objects.
It reconstructs all 19 live `(__package__, spec.parent,
normalized-submodule-search-locations)` triples and requires equality to the
captured tuple. It also requires the closed empty-package/empty-parent/no-location
shape, so merely substituting a differently typed or mutable equivalent does not
weaken the comparison.

A fresh audit-hook direct import ran in an isolated `python -B` process. It
confirmed that the direct-execution branch was skipped, `_W04_EARLY_BOOTSTRAP`
remained `None`, and the import emitted zero audited write opens, filesystem
mutations, child processes, or product operations. The final PYC inventory after
that audit was still byte-identical to preflight.

## Independent adversarial merits

The focused exact-uv population passed `32` cases. It included fully shaped
distinct replacements at registered built-in and frozen names; one-field-at-a-
time built-in/frozen package, spec-parent and search-location changes; both
resident importer replacements; structural earliest-capture order; disguised
resident authorities; pre-guard encoding substitutions; exact admission-child
PYC-row equality; metadata-only PYC collection; and the present-PYC exact-uv
control-flow case.

The two registered-name replacements reject with `outer resident startup object
binding differs`; the six normalized-shape mutations reject with the applicable
built-in/frozen authority error; and both importer substitutions reject with
`outer resident importer authority differs`. In every case stdout is empty and
the rejection occurs inside the first-user verifier before guard installation,
child launch, UUID sampling, or real-root output.

A separate fresh exact-uv harness injected five independently constructed roster
mutations after the startup captures and before `_w04_early_bootstrap`: one added
name, one removed name, the same `time` object reordered by remove/reinsert, an
extra alias to `time`, and the existing `abc` name rebound to the `time` object.
All five rejected before first-user continuation. This covers cardinality,
ordered keys, aliases, and duplicate-object identity independently of the
producer's new object/shape cases.

The retained R8 predicates remain present and exercised: built-in registration,
frozen registration and `is_frozen`, exact names, origins, loaders, files,
caches and locations; source-backed encoding owner/parent/leaf and canonical
source paths; exact `__main__`; order and distinctness; closed environment and
argv; inherited FD, prefix and chronology; exact bootstrap tuple; child result;
product paths; and the exact admission child.

## Metadata-only PYC proof retained

The launcher collector at `scripts/launch_wyscout_v5.py:2900-3039` and the frozen
admission child build the same ordered metadata rows. Python performs no PYC/PYO
open, read, pread, hash, header, magic, or content access. The structural source
test, audit fixtures, admission/launcher complete-row equality cases, and exact-
uv present-PYC case all pass while unconditional PYC/PYO denial remains active.

PYC byte/header/content authority remains exclusively in the fresh shell
pre/post inventories. The selected site and repository inventories cover path,
entry kind, source role, mode, link count, size, device, inode, mtime, ctime,
first sixteen bytes and SHA-256 for every applicable row. The disclosed launcher
PYC was never imported, deleted, restored, rewritten, or read through Python.

## Gate evidence

| Command/evidence | Exit | Result |
| --- | ---: | --- |
| locked/no-sync Ruff format check over admission, launcher and runtime tests | 0 | `3 files already formatted` |
| locked/no-sync Ruff check with cache disabled | 0 | `All checks passed!` |
| locked/no-sync mypy with review-only cache | 0 | no issues in three files |
| focused earliest-binding/shape/PYC exact-uv population | 0 | `32 passed in 9.28s` |
| independent add/remove/reorder/alias/duplicate exact-uv harness | 0 | five of five rejected before continuation |
| direct-import mutation audit | 0 | branch skipped; zero audited mutations |
| exact required six-file final-hash pytest population, retained session `10474`, pytest PID `31543` | 0 | `268 passed in 1505.74s (0:25:05)` |
| locked/no-sync Bandit | 0 | no findings |
| locked/no-sync import-linter, cache disabled | 0 | three kept, zero broken |
| locked/no-sync local-only verifier | 0 | PASS, 25 checks, zero failures, main and zero remotes |
| complete shell PYC preflight/postflight | 0 | both inventory files byte-identical |
| final ten-binding SHA-256 recheck | 0 | all exact |

The packet also lists direct `git diff --check` and `git remote`, while governing
subagent authority and the master instruction prohibit this reviewer from
running Git commands. No direct Git command was run. The local-only verifier
performed its embedded read-only branch, remote and guard checks and reported
branch `main`, zero configured remotes, and all 25 checks passing. The master
retains the direct Git checkpoint boundary.

## Review-harness procedural rework

The mandatory exact gate and static/local-only checks completed successfully in
retained shell session `10474` (shell PID `30617`). An optional first run of the
independent roster harness then used a `/var/folders/...` fixture spelling that
canonicalized to `/private/var/...` in the child. The child correctly rejected
the bootstrap earlier at `outer control-prefix spelling differs`; the harness's
target-message assertion exited nonzero. Because that shell had `set -e`, the
assertion closed session `10474` after the required gate had completed.

This attempt did not reach a target predicate, did not alter producer or
repository bytes, and is not a producer finding. The master adjudicated it as
bounded review-harness procedural rework and expressly prohibited repeating the
exact pytest gate. Fresh sealing shell session `78303` (shell PID `40432`) reran
only the corrected optional harness with canonical `/private/tmp` fixtures,
performed the direct-import audit, recomputed both final shell inventories,
compared them to the original preflight, and rechecked every fixed hash. The
corrected harness passed and the final inventories remained byte-identical.

## Residual risk and disposition

The accepted operational residual remains unchanged: a hypothetical PYC
replacement that preserves every Python-observed metadata field between shell
inventory endpoints is outside Python authority. The complete shell header/hash
inventories bind both endpoints, while unconditional in-process byte access
prevents Python from claiming content authority. R9 neither broadens this
residual nor moves PYC bytes into stable build identity.

No P0, P1 or P2 defect remains in the reviewed R9 startup-binding, complete
built-in/frozen shape closure, retained runtime predicates, metadata-only PYC
control, tests, or local-only gate.

Decision: **PASS — `P0/P1/P2 = 0/0/0`.**
