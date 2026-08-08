# W04 Wyscout runtime-control independent review R7

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=2`, `P2=0`.

The frozen R7 bindings, the corrected retained descriptor walk, source owner and
identity predicates, the producer's fourteen direct exact-uv attacks, the exact
`244`-test final-hash population, the complete shell PYC preflight/postflight,
and all static/security/local-only gates pass. PASS is nevertheless unavailable.

First, the pre-guard module census authenticates a remainder only by the mutable
value of `module.__spec__.origin`. A fourth module can therefore claim
`"built-in"` while retaining an unrelated `__file__` and pass the supposed exact
census. Second, direct execution installs an unconditional in-place-PYC open
denial and then immediately calls an outer Python inventory that opens every
in-place PYC to hash its bytes. CPython presents the `Path` operand to this audit
event as a string, so the current real outer authority reconstruction is
constructively rejected before admission. These are independent P1 trust/control
defects at the boundary R7 is required to close.

## Frozen bindings and read-only chain of custody

Every fixed binding matched before merits work, after the complete gate, and
before this report was written:

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `f6dbce7ffd48320155ab0562ef27a4f79c99e80aa1b122e5f0b039c493048f05` |
| launcher | `7f49b838dd9298997dceb298f40c02a7a647f0373b56b1e3784f28b2633d36be` |
| runtime-control tests | `9ff4b47bd00c963652140ede0474e388d8b553234e5269b892e0cf84b9336927` |
| producer return | `44566dba6acb7506bbf31d9714f2f4cda58a113c8b15c773196df3940172cd17` |
| producer packet | `db313fecc2389d34bfd387b6649ed3d919c6497610d475853fd3704e985ed05b` |
| R6 independent review | `6ba86ce454aee332b66bde6db0a1141511a33404054910996e521745ea8200bf` |
| R7 review packet | `1387a5be98911c908a767903f3e91e8f69988203e0d6394afe227910d93055be` |
| disclosed launcher PYC | `b1c8fbd8e5de10d6251995b9dc0fbbcb7457ba0bdaffd669e6e58c86d280b52e` |

No producer, source, test, configuration, dependency, lock, PYC, product,
manifest, receipt, run, real-root, or orchestration byte was edited. Only this
review and the mandatory reviewer return were written. Review attack artifacts
were confined to `/tmp` and pytest temporary roots.

The identical shell-only preflight and postflight inventories established:

- selected site-packages: `1,087` PYC files and `131` cache directories;
  complete path/kind/mode/link/size/device/inode/magic/content inventory SHA-256
  `901abd68c87e15406f70097884dbeb093647bf815a0a05b8ba0c976efdb9bb91`;
- repository excluding `.venv`: `111` PYC files and `21` cache directories;
  complete inventory SHA-256
  `033830d929d1c55cd1dd08884d0a017da28b475a35f9878264b4d2abe8e5b0fc`.

The disclosed launcher PYC remained mode `0644`, link count `1`, size `199,084`,
device `16777231`, inode `91632142`, and the exact frozen digest above. Every
Python-backed review command used locked/no-sync uv,
`PYTHONDONTWRITEBYTECODE=1`, `-B` for reviewer helpers/pytest, disabled pytest
cache, and disabled or redirected tool caches. The inventories were byte-for-byte
identical after the last Python-backed command. No cleanup or repair was used.

## R7 correction retained on its merits

The R7 descriptor correction closes the concrete R6 path/owner gap:

- the first executable branch still obtains only resident built-in/frozen
  capabilities before the guard;
- `/` is opened and retained, every stdlib component is opened descriptor-
  relatively with `O_DIRECTORY|O_NOFOLLOW`, every path/fstat identity and safe
  mode/owner transition is checked, and every retained binding is rechecked;
- the admitted stdlib and `encodings` directories require the current UID/GID
  and exact mode `0755`;
- `__init__.py`, `aliases.py`, and `utf_8.py` are opened only relative to the
  retained encodings descriptor, with exact UID/GID, regular mode `0644`, link
  count one, size, full positional bytes, EOF, digest and stable pre/post
  identity;
- the three encoding module objects are distinct, use the exact origin/file
  spellings, and the expected source rows and absent selected-cache candidates
  remain exact; and
- all R6 tuple, closed-environment, ordered-argv, source-FD, prefix, chronology,
  child and product predicates remain frozen. The admission child is
  byte-identical.

The producer's focused direct exact-uv population independently reran as `14
passed, 75 deselected in 3.48s`. It rejects a candid fourth file-backed module,
encoding-object alias, accepted-origin alias, linked/replaced encodings parent,
replaced leaf, source-owner drift, environment/tuple/argv substitution, source
offset drift, missing source FD and extra inherited FD. The positive isolated
launch reaches only its deliberately incomplete later repository authority; it
does not constitute a real-root completion.

## Findings

### W04-RUNTIME-R7-P1-01 — mutable origin text can disguise an unpermitted remainder as built-in

Severity: **P1**.

At `scripts/launch_wyscout_v5.py:538-565`, the census validates the exact three
encoding rows and some aliases, but accepts every other non-`__main__` object when
`getattr(module.__spec__, "origin", None)` equals `"built-in"` or `"frozen"`.
It does not authenticate that the name is actually a resident built-in/frozen
module using the already resident interpreter authority, and it does not reject
an unrelated non-null `__file__` on such a claimed row.

The independent exact-uv attack injected, before `_w04_early_bootstrap()`:

1. one distinct `ModuleType` object at `sys.modules["w04_extra"]`;
2. a distinct synthetic spec with `origin="built-in"`; and
3. `__file__="/tmp/w04-extra.py"`.

The exact launcher descriptor and bootstrap tuple were rebuilt over the attacked
isolated launcher, so source-digest checks were not bypassed. The expected test
assertion failed: the process did **not** emit `outer pre-guard file-backed module
census differs`. It passed the census and reached the deliberately later isolated
repository rejection:

```text
W04 runtime control rejected: [Errno 2] No such file or directory: '__init__.py'
```

The existing candid fourth-file attack passes because it leaves its origin as a
path. That does not prove the packet's stronger requirement that all remaining
entries are authentic permitted built-in/frozen cases. Mutable metadata cannot
serve as its own authenticity proof at this trust boundary.

Smallest bounded correction:

1. Authenticate every `"built-in"`/`"frozen"` remainder against the exact
   resident interpreter built-in/frozen authority available before guard
   installation, not only its mutable spec text.
2. Freeze and enforce the permitted file/cached attribute shape for those cases,
   including the real CPython frozen-module cases, without broadening the three
   source-backed allowance.
3. Add the disguised fourth-module attack above and attacks for a forged frozen
   claim and an unregistered alias. Retain every current direct exact-uv attack.

### W04-RUNTIME-R7-P1-02 — outer PYC byte inventory is constructively denied by the installed guard

Severity: **P1**.

The launcher declares `zero_python_role_pyc_read=true` at
`scripts/launch_wyscout_v5.py:2658`, but `_independent_pyc_inventory()` opens and
hashes every actual PYC at lines `2662-2747`. Direct outer execution first
installs the unconditional non-prefix `.pyc`/`.pyo` open rejection at lines
`834-854`, then `_execute_outer_control()` immediately invokes
`_admission_authority_with_pyc()` at line `4150`; that reconstruction invokes the
byte-reading inventory at line `3191`.

The independent locked/no-sync `python -B` audit probe called `os.open()` with a
`Path("/tmp/...pyc")` and observed the audit target as type `str`, not `Path`:

```text
[('str', "'/tmp/w04-r7-nonexistent-audit-probe.pyc'")]
```

Therefore this is not a PathLike escape. The installed condition at lines
`839-843` rejects before `_absolute_regular()` can read the first in-place PYC.
The admitted actual inventory contains `1,198` PYC files, so a real outer launch
cannot reach admission or publication. The `244`-test gate stays green because
the exact-uv probe's isolated repository contains no admitted PYC closure and
fails later, while the full outer chronology test substitutes the authority
collector and the preparation tests import the launcher without executing its
first-user guard.

Smallest bounded correction:

1. Keep every Python role at zero in-place-PYC byte reads.
2. Replace the outer Python byte-reading inventory with the exact lstat-only
   classified observation needed for equality, or pass and strictly reconstruct
   the master-owned shell preflight evidence without granting Python read
   authority. Do not weaken the installed denial.
3. Add an exact direct outer attack/positive fixture containing at least one
   classified present site PYC and the disclosed repository launcher PYC, proving
   zero Python PYC opens and continued control flow through admission.
4. Preserve actual PYC bytes/digests as operational shell/master evidence only;
   do not add them to stable identity or digest meaning.

## Disclosed pre-baseline operational-PYC rewrite

The producer's accidental rewrite remains a process/scope defect: it modified an
existing untracked byte outside the producer's allowed paths before the declared
final baseline. It was fully disclosed, never hidden, restored, deleted, cleaned,
or touched again. The current launcher PYC still classifies as a repository
source-backed operational row, is excluded from the stable code/environment
components, and remained byte-identical across this complete review.

The incident did not itself change an accepted source, logical contract, product,
dependency, lock, digest formula, or real root. It therefore does not add a
separate P2 finding. It also cannot be used to grant read authority or excuse the
constructive PYC-control defect above. R20's actual bounded-run preflight rule
permits the disclosed current bytes to be the operational baseline only after
they classify and the complete postflight is identical, which this review proved.

## Gate evidence

| Command/evidence | Exit | Result |
| --- | ---: | --- |
| `uv run --locked --no-sync ruff format --check ...` | 0 | `3 files already formatted` |
| `uv run --locked --no-sync ruff check --no-cache ...` | 0 | `All checks passed!` |
| `uv run --locked --no-sync mypy --cache-dir=/tmp/... ...` | 0 | no issues in three files |
| exact required six-file pytest population, locked/no-sync `python -B`, cache provider disabled | 0 | `244 passed in 1474.71s (0:24:34)` |
| producer's focused direct exact-uv R7 population | 0 | `14 passed, 75 deselected in 3.48s` |
| disguised built-in/file-backed reviewer attack | 1 | expected review assertion failed; attack bypass reproduced |
| CPython `os.open(Path)` audit-target helper | 0 | target observed as exact `str` |
| `uv run --locked --no-sync bandit -q -r ...` | 0 | no findings |
| `uv run --locked --no-sync lint-imports --no-cache` | 0 | three contracts kept, zero broken |
| `uv run --locked --no-sync python -B scripts/verify_local_only.py` | 0 | PASS, 25 checks, zero failures |
| identical shell preflight/postflight PYC inventory | 0 | both counts and complete inventory digests equal |
| final eight-binding SHA-256 recheck | 0 | all exact |

The first sandboxed custom-probe attempt exited `2` because the sandbox denied
read access to the already admitted local uv cache; no probe executed and no
repository file changed. The locked/no-sync offline command was then approved for
read-only cache access and reproduced the finding. No network, sync, resolution,
dependency change, provider access, credential, secret, cost, or real publication
occurred.

The packet lists `git diff --check` and `git remote`, but also states
`git_operations: forbidden`. No direct Git command was run. The required
`verify_local_only.py` verifier performed its embedded read-only checks and
reported zero configured remotes, branch `main`, and all 25 local-only checks
passing.

## Disposition

The R7 retained-parent/owner/stability implementation and its current attacks are
valuable but do not meet the `0/0/0` acceptance threshold. The module remainder
is not authentically classified, and the real outer path is constructively
blocked by its own PYC denial/inventory contradiction.

Decision: **REWORK — `P0/P1/P2 = 0/2/0`.**
