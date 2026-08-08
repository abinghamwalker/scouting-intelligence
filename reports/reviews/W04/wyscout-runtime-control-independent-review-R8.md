# W04 Wyscout runtime-control independent review R8

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=1`, `P2=0`.

R8 correctly removes every launcher-side PYC byte read, reproduces the frozen
admission child's complete metadata rows, preserves unconditional in-process PYC
read denial, and admits the exact declared 23-name startup order. The exact
`257`-test final-hash population and every static, security, import-boundary and
local-only check pass. PASS is nevertheless unavailable because a permitted
registered built-in name is still authenticated only by name registration plus
mutable module/spec metadata. A distinct replacement object carrying those
fields passes the first-user verifier. The same branch also omits the frozen
per-row `__package__`, spec parent, and submodule-location shapes required by the
review packet.

## Frozen bindings and read-only chain of custody

Every fixed binding matched before merits work and again after the complete
gate:

| Binding | Independently observed SHA-256 |
| --- | --- |
| R8 review packet | `bb7211210edff4cfe4a801f5ceb4e9eb615bba4fa10e3624df98e83f72a013bc` |
| R8 producer packet | `6a16ff130a802dafe924a4a47011bc08b6e1eed3f7c7e6b30ebf4df32f8c00d8` |
| admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| launcher | `e7cf10d5f11871bc48911a5dc9ea8b58ce9a6477e6df0935475f053874b6e2d5` |
| runtime-control tests | `01007463ac8cb52d67bdfb2b6784f36fab9cdf7a8ddf35c24a9149512d3707e0` |
| producer return | `40a877805b20e4ca9cdd6d8489c3b1074e81de19efbc3c8975abbebf4ef01446` |
| R7 review | `d6ef3e0d3930dd212f53cee51ad33802279707f3fc828e52e776822388913ea1` |
| disclosed launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |

No producer, source, test, dependency, lock, PYC, product, manifest, receipt,
real-root, or orchestration byte was edited. Only this review and its mandatory
return were written. Review fixtures remained under `/private/tmp`.

The complete shell-only preflight and postflight inventories were byte-identical:

- selected site-packages: `1,087` PYC files and `131` cache directories;
  complete path/class/source/mode/link/size/device/inode/clock/header/content
  inventory SHA-256
  `d579cb89cfd3665928eda9e3d6663bcbe64cd74633d6250b163881d01ed9d0c4`;
- repository excluding `.venv`: `111` PYC files and `21` cache directories;
  complete inventory SHA-256
  `8101925c6f3b9359c0a27d3e309a42ad6731b4dbae1c6079af1833a075b9729e`.

The current class decomposition is site `973` distribution-normal, `112`
pytest-rewrite, one uv-bootstrap-normal, and the optional six orphan; repository
`63` normal, `45` pytest-rewrite, and the exact three optional inert orphans.
There were zero unsafe or unclassified rows. The disclosed launcher PYC remained
one repository-normal row with mode `0644`, link count `1`, size `199,084`, device
`16777231`, inode `91632142`, first sixteen bytes
`cb0d0d0a00000000cf9e6f6a47c90200`, and the frozen digest above.

Every Python-backed review command used locked/no-sync uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B`, disabled pytest bytecode/cache output,
and a review-only cache prefix under `/private/tmp`. The first sandboxed metadata
shape probe exited `2` because access to the already admitted local uv cache was
denied; it executed no probe and changed no repository file. The same offline,
locked/no-sync command was then run with read-only cache access.

## R8 PYC correction retained on its merits

The launcher collector at `scripts/launch_wyscout_v5.py:2774-2913` is now
structurally byte-read-free for PYC files. Its PYC branch takes one no-follow
`os.stat` snapshot and records only class, role, path/source mapping, mode,
device, inode, size, mtime and ctime. It contains no PYC `open`, `read`, `pread`,
hash, header or magic access. Cache-directory rows retain their complete
no-follow metadata shape.

The launcher and byte-identical admission child independently build the same
site/repository source maps and orphan predicates. On identical site,
repository, mapped, orphan and empty-cache fixtures their complete ordered rows
are byte-for-byte equal. Creation, deletion, mode, link, identity, size and clock
changes either reject or change the snapshot. Content/header changes in the
ordinary filesystem path change bound ctime and fail equality. A hypothetical
metadata-equality substitution remains intentionally outside Python authority:
only the mandatory shell pre/post header/content census can distinguish it. R8
does not weaken that residual or move operational PYC bytes into stable identity.

The isolated audit proof completed with classified site and repository rows,
zero PYC open events, and the unconditional denial active. The direct exact-uv
fixture then loaded an isolated launcher through the exact argv with a classified
site PYC plus a read-only `/bin/cp` copy of the disclosed repository PYC. It
completed the metadata census and reached the deliberate later control marker;
the denial never observed a PYC open and no real root was published. The focused
R8 population passed `47` tests with `55` deselected.

## Exact resident roster merits retained

R8 freezes the exact ordered 23 names, rejects every extra/missing/reordered row,
and requires 23 distinct non-null objects. The built-in rows require membership
in the resident `sys.builtin_module_names`, exact resident `BuiltinImporter`,
name/origin/location/cache/file/loader shapes; frozen rows require resident
`_imp.is_frozen`, exact `FrozenImporter`, and their exact file/cache shapes.
The three encoding source rows and `__main__` remain separately and tightly
closed. The producer's unregistered extra/alias, forged origin, loader, file,
cache, encoding owner/parent/leaf, tuple, environment, argv and FD cases all
reject as intended.

## Finding

### W04-RUNTIME-R8-P1-01 — registered resident object and complete metadata shape are not bound

Severity: **P1**.

At `scripts/launch_wyscout_v5.py:560-566`, object handling proves only that the
23 current values are distinct. At lines `617-644`, built-in/frozen admission
then trusts name registration plus each current object's mutable `__spec__`,
`__loader__`, `__file__`, and `__cached__` fields. It does not preserve the
original resident object identities before later launcher statements can run.
It also does not compare `module.__package__`, `spec.parent`, or
`spec.submodule_search_locations` for any built-in/frozen row, even though the
R8 review packet explicitly requires complete parent/location/package shape.

The existing R8 cases at
`tests/unit/test_w04_wyscout_runtime_control.py:1479-1538` cover an unregistered
extra, an unregistered alias, and individual loader/file/cache changes. They do
not replace an already registered roster name with a distinct, fully shaped
object and do not change a built-in/frozen parent/package/location field.

Two fresh exact-uv cases reproduced the gap over an isolated launcher whose
descriptor, source digest and bootstrap tuple were recomputed over the reviewed
case bytes:

1. `sys.modules["time"]` was replaced by a distinct `ModuleType("time")` with
   an exact resident `BuiltinImporter`, `ModuleSpec(name="time",
   origin="built-in")`, empty package and absent file/cache. `time` remains in
   `sys.builtin_module_names`, every implemented row predicate passes, and all
   23 objects remain distinct. Execution failed only after the guard when
   `threading` requested the absent `time.monotonic`; it did not emit a
   pre-guard resident/built-in rejection.
2. The genuine `time` object's `__package__` was changed to `"w04.attacker"`
   and its spec gained empty submodule search locations, changing its package,
   parent and package-location shape. The first-user verifier accepted the row
   and reached the deliberately later isolated repository rejection
   `No such file or directory: '__init__.py'`.

This is not a roster-cardinality defect; it is a missing provenance/shape
predicate inside the exact first-user trust boundary. An admitted registered
name is not sufficient evidence that the current object is the startup object,
and mutable loader/spec text cannot authenticate its own container.

Smallest bounded correction:

1. At the earliest executable point, before any later launcher body can alter
   `sys.modules`, freeze the exact 23 startup object identities and resident
   importer authorities using only the already permitted built-in/frozen
   capabilities; compare those exact identities again in the full verifier.
2. Freeze and compare the exact per-row `__package__`, `spec.parent`, and
   `spec.submodule_search_locations` shapes for every built-in and frozen row,
   alongside the existing fields.
3. Add direct exact-uv registered-name replacement plus built-in/frozen
   package/parent/location cases. Retain every R8 case and the metadata-only PYC
   correction unchanged.

This correction is bounded startup authentication/test completeness. It changes
no logical model, root roster, product, digest meaning, dependency, local-only
boundary, data right, PYC bytes, or real-root output.

## Gate evidence

| Command/evidence | Exit | Result |
| --- | ---: | --- |
| locked/no-sync Ruff format check over admission, launcher and runtime tests | 0 | `3 files already formatted` |
| locked/no-sync Ruff check with cache disabled | 0 | `All checks passed!` |
| locked/no-sync mypy with review-only cache | 0 | no issues in three files |
| focused R8 roster/PYC population | 0 | `47 passed, 55 deselected in 7.50s` |
| exact required six-file final-hash pytest population, preserved process session `3929` | 0 | `257 passed in 1483.18s (0:24:43)` |
| registered-name exact-uv conformance case | 0 (review helper) | verifier accepted replacement; later `time.monotonic` import failed |
| package/parent/location exact-uv conformance case | 0 (review helper) | verifier accepted mutation and reached later isolated-repository rejection |
| locked/no-sync Bandit | 0 | no findings |
| locked/no-sync import-linter, cache disabled | 0 | three kept, zero broken |
| locked/no-sync local-only verifier | 0 | PASS, 25 checks, zero failures, main and zero remotes |
| complete shell PYC preflight/postflight | 0 | both inventory files byte-identical |
| final eight-binding SHA-256 recheck | 0 | all exact |

The packet also lists direct `git diff --check` and `git remote`, while governing
subagent authority and the resumed master instruction prohibit Git commands.
No direct Git command was run. The required local-only verifier performed its
embedded read-only branch/remote/guard checks and reported branch `main`, zero
configured remotes, and all 25 checks passing.

## Disclosed operational-PYC incident

The previously disclosed launcher-PYC rewrite remains a frozen operational row,
not source or stable build authority. It was never deleted, restored, rewritten,
cleaned, imported, or read through Python during this review. Its complete shell
row and content digest stayed byte-identical across the final gate. The incident
therefore does not add a separate finding, weaken the P1 above, or grant any
Python PYC read exception.

## Disposition

R8's metadata-only PYC correction and most of its 23-row authentication are
valuable and retained. The exact acceptance threshold remains unmet because the
registered startup object and complete built-in/frozen parent/package/location
shapes are not closed.

Decision: **REWORK — `P0/P1/P2 = 0/1/0`.**
