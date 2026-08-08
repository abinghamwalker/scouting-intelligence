# W04 Wyscout runtime-control independent review R6

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=1`, `P2=0`.

The frozen R6 bindings, complete `237`-test final-hash population, direct exact-uv
bootstrap probes, isolated outer chronology, whole-review PYC equality, and all
static/security/local-only gates pass. PASS is nevertheless unavailable. The
first-user-code encoding verifier does not prove the R20 admitted standard-library
parent or exact source owner, and it does not enforce the exact pre-guard
file-backed-module census. It reopens each encoding source by an absolute path
with leaf-only `O_NOFOLLOW`, then validates only the final file. This is a
fail-open gap at the boundary whose purpose is to prove which file-backed code ran
before the audit guard.

## Fixed bindings and read-only chain of custody

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| launcher | `ecfb3b1714b7a6caf607d9ae4393b3130e04045c717f5965207a804356b580f7` |
| runtime-control tests | `ad6027133eccb451fd9ab9d7135e60ccab50335d7acfdd25b008565bba323116` |
| producer return | `092421174a1c19bc9ccb4ca2fbc5bb610d2c237c318940b516ddbf92aa7edc54` |
| producer packet | `6a900a2232443006b62580a4f815e476c941181ca0ad1e0d83021603cade87a5` |

All five R6 bindings matched before merits work and again after the final bounded
review command. The packet's historical R5 hashes were also recovered exactly
from the accepted R5 master acceptance:

| Historical binding | Accepted SHA-256 |
| --- | --- |
| R5 admission child | `cba67d6a143951cbeefa2e63063f5f09aab73f6ec435a1378fb2451d59950cb5` |
| R5 launcher | `d3ac8c84995c8475b0a4df983899ebf6b364f047dcbba45c411d55b62c808740` |
| R5 runtime-control tests | `61f1d770d1b662df0f30c6d4bc54aace9f0fa1069d32501c7d466be908b66fb4` |
| R5 master acceptance | `a08d2a429c45a52cd7839c41ee3429f91fef227e9e9f41992c8f3a9fdbe8c24c` |
| accepted four-feature product master acceptance | `984fa64e75717decfe2048337655f00805dcf59543f8d083d006be794b8dec98` |

No producer, source, test, configuration, dependency, lock, product, manifest,
receipt, run, real-root, or orchestration byte was edited. Only this review and
the mandatory reviewer return were written.

The identical shell-only preflight and postflight inventories established:

- selected site-packages: `1,087` pycs and `131` cache directories; complete
  path/mode/link/size/device/inode/header/content digest
  `5459cbafa61d1f2c58a1313d008fd068bef9d15e5e30e47700d66ebed0dd1598`;
- repository excluding `.venv`: `111` pycs and `21` cache directories; complete
  digest `e930505226115d5e9f6ddfb7de200dafe504632e603251fa84a6280640081167`.

Both counts and both digests were byte-for-byte equal after the final Python-backed
gate. Every such gate used locked/no-sync root uv,
`PYTHONDONTWRITEBYTECODE=1`, and pytest's cache provider was disabled. Ruff,
mypy, and import-linter caches were disabled or directed to `/tmp`. No cleanup or
repair was used.

## Finding

### W04-RUNTIME-R6-P1-01 — pre-guard encoding proof omits admitted-parent, owner, and exact-module-census predicates

Severity: **P1**.

R20 Section 8.0.1 requires each of the three encoding rows to be a contained
regular non-link source with the exact admitted standard-library mode **and
owner**. It then requires the first user-code verifier to no-follow read each row
**through its admitted stdlib parent** and to require exactly the three expected
file-backed encoding modules before installing the guard.

The launcher does less at `scripts/launch_wyscout_v5.py:515-549`:

1. It derives a string `stdlib_root = system.base_prefix + "/lib/python3.12"` and
   appends each relative source spelling.
2. It compares `__spec__.origin` and `__file__` only to that string for each named
   module. It never constructs an exact census of all pre-guard file-backed
   modules, so an additional source-backed module is not rejected by this check.
3. It executes `posix.open(source, O_NOFOLLOW)` on the complete absolute path.
   `O_NOFOLLOW` protects only the final path component; it does not reject a
   symlinked or replaced intermediate stdlib/`encodings` parent.
4. Its `fstat` predicates cover final-file kind, mode, link count, size, and
   digest. They do not check `st_uid`/owner, do not validate or retain any parent
   directory descriptor/identity, and do not relate the already executed module
   to the newly opened descriptor beyond mutable origin strings.

The exact bytes and final-file checks are valuable but do not imply the missing
predicates. An intermediate parent alias can resolve to a singular mode-`0644`
file containing the accepted bytes and pass even though the required admitted
parent was not traversed. More importantly for the pre-guard trust boundary, a
same-trust actor able to replace that parent/source between master admission,
interpreter preload, and the verifier can let different encoding code execute,
then restore an accepted final path before the absolute reopen. The verifier sees
the accepted origin spelling and bytes but has no parent or loaded-file identity
with which to reject the substitution. A preloaded encoding module can likewise
load a fourth file-backed module; the presence-only three-name checks do not
detect the extra module.

This is not merely a test naming issue. The launcher is the only control that can
reject this state before later file-backed imports and child admission. Passing
all current tests therefore does not close the authority gap.

Smallest bounded R7 correction:

1. In the inline built-in/frozen verifier, open and retain the admitted stdlib
   directory using directory/no-follow semantics, validate its exact safe
   mode/owner and identity, walk `encodings` by descriptor-relative no-follow
   opens, and open each source relative to the retained parent. Require stable
   parent and leaf `fstat` snapshots around the complete reads. Do not fall back
   to an absolute or `Path` reopen.
2. Include the exact admitted owner predicate for the three source rows and
   reject any intermediate link, parent replacement, owner drift, escape, or
   identity drift. Keep device/inode observations operational if required by the
   root-independent authority model.
3. Before guard installation, enumerate file-backed entries in `sys.modules` and
   require the exact three reviewed source modules, with all other resident
   entries built-in/frozen as allowed. Reject a fourth file-backed module.
4. Add direct-launch attacks for an intermediate `encodings` parent link/
   replacement, source-owner drift where the platform permits it, and a fourth
   pre-guard file-backed module. Retain the current source byte/digest, absent
   cache, environment, tuple, argv, descriptor, FD, and prefix attacks.
5. Freeze new producer hashes, rerun the exact complete gate plus shell pre/post
   PYC equality, and obtain a fresh independent review. Do not publish to real
   roots during rework.

## Retained R6 predicates

The direct launcher branch is the first executable statement and obtains only
resident `sys`, `posix`, and `_io` before its inline canonical JSON, base64url,
and SHA-256 implementation. Source review and the fixed tests confirmed the
closed 30-name outer environment after tuple insertion, complete sorted 34-field
v4 tuple, exact cwd/`sys.argv`/`sys.orig_argv`/Python identity, strict inherited
launcher descriptor grammar, initial inheritable state and zero offset, full
descriptor bytes/digest/identity, exact `[0,1,2,source_fd]` census, mode-`0700`
empty control prefix, audit transition, and noninheritable retained descriptor
through both children.

The launcher and admission child independently reconstruct the same complete
tuple and normalized environment. The fixed attacks reject missing, extra,
reordered, or substituted argv; unknown/missing environment names; tuple
mutation; source-descriptor offset, missing/extra FD, and inheritability drift;
control-prefix content/replacement; cwd and UUID replay; child failure; retained
launcher/PYC drift; result-frame malleability; and noncanonical completion.

The isolated full-orchestration test proves admission before build-ID/rebuild,
distinct control/admission/rebuild UUIDs, exact cwd-bound roots, retained authority
rechecks, empty role prefixes, and one canonical
`w04-local-control-completion-v1` value. It substitutes the two child executors.
The exact uv direct-launch positive probe proves that the complete first-user-code
bootstrap passes on the admitted host by reaching the deliberately incomplete
isolated repository's later runtime rejection. Its negative variants reject
environment, tuple, argv, descriptor-offset, missing-FD, and extra-FD changes.

Those bounded facts must not be overclaimed. Neither producer nor reviewer
evidence proves an unmocked full real-root completion. The later master-owned
two-real-run packet remains the sole authority for real publication.

The six-file end-to-end fixture inventories the real working, manifest, and run
roots before and after its isolated product builds and requires exact equality.
It produced only pytest-temporary product roots. No producer or reviewer test
published under the real roots.

## Gate evidence

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run --locked --no-sync ruff format --check ...` | 0 | `3 files already formatted` |
| `uv run --locked --no-sync ruff check ...` | 0 | `All checks passed!` |
| `uv run --locked --no-sync mypy ...` | 0 | no issues in three source files |
| exact required six-file pytest population | 0 | `237 passed in 1476.22s (0:24:36)` |
| `uv run --locked --no-sync bandit -q -r ...` | 0 | no findings |
| `uv run --locked --no-sync lint-imports --no-cache` | 0 | three contracts kept, zero broken |
| `uv run --locked --no-sync python -B scripts/verify_local_only.py` | 0 | PASS, 25 checks, zero failures |
| identical shell preflight/postflight PYC inventory | 0 | counts and both complete digests equal |
| final five-binding SHA-256 recheck | 0 | all exact |

The first sandboxed static attempts exited `2` because the sandbox denied read
access to `/Users/adrian/.cache/uv/sdists-v9/.git`; no gate executed and no file
changed. The same locked/no-sync commands were then approved for read-only access
to the already admitted local cache and all exited `0` as recorded above.

The packet lists `git diff --check` and `git remote`, but the same packet states
`git_operations: forbidden`. No direct Git command was run. The required
`verify_local_only.py` policy verifier performed its own embedded read-only checks
and reported zero configured remotes and active branch `main` among its 25 passes.

## Disposition

The R6 functionality and evidence outside the finding are retained. The missing
pre-guard admitted-parent/owner/census proof is a P1 runtime-admission defect, so
the packet's `0/0/0` PASS threshold is not met.

Decision: **REWORK — `P0/P1/P2 = 0/1/0`.**
