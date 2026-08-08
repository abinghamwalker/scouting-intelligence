# W04 Wyscout runtime-control independent review R4

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=1`, `P2=0`.

The frozen R4 bindings, all static gates, the complete 191-test final-hash gate,
the actual two-run admission, both external PEP 427 mappings, and the retained
source/PYC attacks pass. PASS is nevertheless unavailable: both independently
implemented PYC collectors omit cache-directory identity and clock metadata from
their pre/post inventory rows. An isolated same-path replacement of a mode-`0755`
`__pycache__` directory changed inode, ctime, and mtime while producing byte-equal
child and launcher snapshots. This is a fail-open violation of the packet's exact
cache-directory identity/clock drift predicate.

## Fixed bindings and no-write chain of custody

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `c91f98c8d02a647d1eada8636f864382c6c7468c2d9b9b61cff51db92ac3f94e` |
| launcher | `5c4c081b5b5049de6f9aad444e95ccf2e4d38fa7484d56add67cd1cb03b193a0` |
| runtime-control tests | `215d4c08af21e2768a98c16defa80c4bfefa44fb690dbe1fbc295cea254f0bad` |
| producer return | `959fbdeb9b5dd3800b4d007227ccfd29c3ed798afbcf187b518736144f2291ee` |
| R3 review | `4a9740bbb55196282481b204dc4ad540fd2baadb82f5af708d37c18e86c02824` |
| R3 reviewer return | `776b16aefb2dd53a3a12d4e1488631267f8e2cd95e75d26b37fab5fcfd1ad7a3` |

The producer bytes were read-only throughout. The fixed hashes were rechecked
unchanged after the last bounded review command. Identical shell-only preflight
and postflight inventories established:

- site: `1,087` pycs and `131` cache directories; complete lstat/header/content
  digest `bb9bbe481f43fdf51ec6628a154e467f4e26f0bc835a3405c3970327266c991f`;
- repository excluding `.venv`: `98` pycs and `20` cache directories; complete
  lstat/header/content digest
  `c8f0019a59afbdfced37c95c7433ab09def222c5635e13792fdafbf5c2b56306`.

Every Python command used `PYTHONDONTWRITEBYTECODE=1`, an isolated empty
`PYTHONPYCACHEPREFIX`, and `UV_NO_SYNC=1`. Required uv-cache reads were performed
with approved read access after the sandbox correctly denied the first attempts.
No real-root code manifest, admission prefix, rebuild prefix, product, receipt, or
rebuild execution was produced. No sync, cleanup, dependency/lock change, provider
or network operation, or Git operation was performed.

## Finding

### W04-RUNTIME-R4-P1-01 — cache-directory identity and clock replacement is invisible to both PYC inventories

Severity: **P1**.

The child `_operational_pyc_inventory()` and launcher
`_independent_pyc_inventory()` validate that each `__pycache__` is a real
mode-`0755` directory, but each appends only this operational row:

```text
{"entry_kind":"CACHE_DIRECTORY","mode":493,
 "path":"<relative __pycache__ path>","role":"<traversal role>"}
```

The row omits the directory's device, inode, link count, size, mtime, and ctime.
Consequently, the repeated child reconstructions and the launcher's retained
pre/post comparison cannot observe same-path replacement when the replacement
keeps the accepted kind and mode. The current test named `creation` adds a new
cache-directory path; it does not replace an existing path with a different
directory identity.

The independent isolated attack created `tests/__pycache__`, took both snapshots,
renamed that directory out of the cache namespace, and created a new mode-`0755`
directory at the exact original path. The actual lstat evidence changed:

```text
old: device=16777231 inode=91601252
     ctime_ns=1785679940105805691 mtime_ns=1785679940105791274
new: device=16777231 inode=91601253
     ctime_ns=1785679940106241771 mtime_ns=1785679940106231563
```

Despite those changes, both results were `True`:

```text
launcher_before == launcher_after
child_before == child_after
```

Both collectors returned the identical sole row shown above. This directly
contradicts the R4 requirement to attack and close cache-directory size, identity,
and clock drift and the producer return's claim that the child census binds exact
cache-directory link/size/identity/clock state. Because the same persistent
replacement is accepted coherently by both independent checks, this is a P1
admission-control defect rather than a test-only P2 omission.

Smallest exact R5 correction:

1. In both collectors, construct each cache-directory inventory row from one
   no-follow lstat snapshot and include at least `device`, `inode`, `mode`,
   `link_count`, `size_bytes`, `mtime_ns`, and `ctime_ns` in addition to exact
   role/path/kind. Preserve the existing real-directory, non-link, mode-`0755`
   rejection.
2. Compare those complete rows in every existing child reconstruction and
   launcher pre/post inventory equality. Keep the rows operational and absent from
   stable identity; do not add any child PYC content read.
3. Add child and launcher attacks for same-path mode-`0755` directory replacement
   and same-inode directory clock drift. Retain/add cache-directory link, mode, and
   size/entry drift attacks so each named lstat predicate is independently proven.
4. Freeze new child, launcher, test, and producer-return hashes, rerun the complete
   gate and actual two-run admission, and obtain a fresh independent review.

## Exact external PEP 427 reconstruction

A final no-site (`python -S -B`) helper independently reconstructed all `81`
selected wheels and `9,595` singular mapped destinations with separate child and
launcher code. The complete maps and stable extracted rows were equal. The two R3
false-rejected live rows reproduced exactly:

| Installed RECORD row | Derived extracted row / scheme | Exact installed evidence |
| --- | --- | --- |
| Bandit `../../../share/man/man1/bandit.1` | `bandit-1.9.4.data/data/share/man/man1/bandit.1` / `data` | mode `0o644`, 6,545 bytes, SHA-256 `935728a5192792b9d7ccec8e02f76f0ba8b097e4006141b51ce591b00b647562` |
| Greenlet `../../../include/site/python3.12/greenlet/greenlet.h` | `greenlet-3.5.4.data/headers/greenlet.h` / `headers` | mode `0o644`, 4,755 bytes, SHA-256 `b33e69611490a9e7603add80320c4b65d4e33bea9caff24cbe0884251f48009f` |

Both installed rows passed only through exact same-owner destination derivation and
equal mode/hash/size. The fixed suite's child and launcher cases reject unmapped,
owner-swapped, colliding, and escaping rows; source review confirmed complete-map
collision/overwrite rejection and exact canonical-relative spelling rejection for
external aliases.

## Retained R2/R3 predicates and actual admission

The complete fixed-hash suite passed `191 passed in 118.18s`. Its retained attacks
cover two-hop cache links, `.data/data` byte drift, mapping collision, fourth
interpreter alias, bootstrap drift, a fourth PTH, editable metadata/direct-url/
uv-cache drift, unowned installed payload, unselected runtime origin, inherited
environment values, child-collector substitution, unmanifested same-named source
plus pytest pyc, PYC creation/deletion/content/header/mode/link drift, wrapper
digest drift, immutable conflict, projection/inverse, and no-rebuild/no-real-root
publication.

Source review confirmed the 43 retained test-source rows are explicit frozen
members of both repository source rosters rather than scan-selected promotions.
It also confirmed the child PYC collector contains no PYC content-open/read/hash
primitive and never calls the launcher collector. Those correct predicates do not
close the cache-directory replacement attack above.

The isolated actual two-run test separately passed `1 passed in 29.83s`. It proved
equal build ID, code-manifest ID/digest, invocation, immutable manifest inode,
twenty-component/count validation, repository identity, strict projection/inverse,
three layer paths, no rebuild entrypoint execution, and no real-root code/admission
publication. The reproduced exact count sequence remained
`(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,3,81)`.

## Gate evidence

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check ...` | 0 | three files already formatted |
| `uv run ruff check ...` | 0 | all checks passed |
| `uv run mypy ...` | 0 | no issues in three source files |
| required fixed-hash pytest population | 0 | exactly `191 passed in 118.18s` |
| isolated actual two-run admission | 0 | `1 passed in 29.83s` |
| `uv run bandit -q -r ...` | 0 | no findings |
| `uv run lint-imports` | 0 | three contracts kept, zero broken |
| `uv run python -B scripts/verify_local_only.py` | 0 | PASS, 25 checks, zero failures |
| no-site live mapped-destination reconstruction | 0 | child and launcher equal over 81 wheels / 9,595 destinations |
| same-path cache-directory replacement attack | 0 | changed lstat identity/clocks, equal child and launcher snapshots |

## Required re-review

R5 must make complete cache-directory lstat rows part of both operational
inventories without adding them to stable identity or reading PYC content in the
child. A fresh reviewer must rerun the exact replacement/clock attacks, complete
fixed-hash gate, actual two-run admission, external mappings, no-write inventory,
and all retained predicates. PASS remains permitted only at `P0/P1/P2=0/0/0`.
