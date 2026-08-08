# W04 Wyscout runtime-control independent review R5

Date: 2026-08-02

## Decision

**PASS.** Findings are `P0=0`, `P1=0`, `P2=0`.

The sole R5 correction is complete. Both independently implemented PYC
inventories bind one no-follow `lstat` snapshot for every cache directory as the
exact ten-field row `ctime_ns`, `device`, `entry_kind`, `inode`, `link_count`,
`mode`, `mtime_ns`, `path`, `role`, and `size_bytes`. Complete rows differ for
same-path replacement, same-inode clock drift, and entry/link/size drift; directory
symlink and unsafe-mode substitutions reject. The rows remain operational, are
compared at the retained reconstruction boundaries, do not enter stable identity,
and add no PYC content read to the child.

The fixed-hash 203-test population, an isolated actual two-run admission, all
static/security/local-only gates, independently reconstructed child-versus-launcher
authority, both exact external PEP 427 mappings, live PYC ownership semantics,
immutable replay, projection/inverse, no-rebuild, and no-real-root publication all
pass.

## Fixed bindings and read-only chain of custody

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `cba67d6a143951cbeefa2e63063f5f09aab73f6ec435a1378fb2451d59950cb5` |
| launcher | `d3ac8c84995c8475b0a4df983899ebf6b364f047dcbba45c411d55b62c808740` |
| runtime-control tests | `61f1d770d1b662df0f30c6d4bc54aace9f0fa1069d32501c7d466be908b66fb4` |
| producer return | `f6a75dc396672fc64a67c5a39579b4cbd11d46df6d85e3d728d7e247128989bd` |
| R4 review | `74e5ff009bac72196739551f4c1aca724f9710636cce39ab429da1394d4514ab` |
| R4 reviewer return | `926bfbb77f6f3561e94f2f75f3e5113266748d02e55a01d36505ec5e8cf4156f` |

All six bindings matched before merits work. The four R5 producer paths were
read-only throughout and all six bindings matched again after the last bounded
review command.

Identical shell-only preflight and postflight inventories established:

- site: `1,087` pycs, `131` cache directories, `112` pytest rewrites, and the
  one optional six orphan; lstat/header/content digest
  `65008a9a79e39e50ca20f01c917c3ddf1554f0cf35eb27c523efeed204a0815d`;
- repository excluding `.venv`: `98` pycs, `20` cache directories, `43` pytest
  rewrites, and all three exact optional repository orphans;
  lstat/header/content digest
  `d39602d310be5fb5ccd8f2e86715a468e8502996b87d74b2fd32dfadec9822d2`.

Every Python-backed review command used locked/no-sync root uv,
`PYTHONDONTWRITEBYTECODE=1`, `python -B` where Python was invoked directly, and an
isolated `PYTHONPYCACHEPREFIX` under
`/private/tmp/w04-r5-review.Gbyf1z`. No sync, cleanup, provider/network operation,
dependency/lock change, producer edit, or Git mutation was performed. The packet-
required local-only verifier performed only its embedded read-only policy checks.
The real code-manifest and admission roots were absent after the final bounded
command:

```text
data/manifests/wyscout/v5/code
data/working/wyscout/v5/.staging/admission
```

## R5 directory-row correction

Source review confirmed both collectors perform exactly one `os.lstat(directory)`
for each encountered `__pycache__`, require a real non-link mode-`0755` directory,
and construct the complete row only from that snapshot. The fields are exact, not
derived defaults:

```text
ctime_ns, device, entry_kind=CACHE_DIRECTORY, inode, link_count,
mode, mtime_ns, path, role, size_bytes
```

The child compares the complete inventory around each stable-authority
reconstruction and again across its two complete pre-result reconstructions. The
launcher independently compares the complete inventory around each retained
authority reconstruction, including the pre-publication recheck. Equality is on
the entire tuples, so no enriched field is projected away at a comparison boundary.

The stable component named `pyc_policy_source_map_digest` is constructed before
the operational inventory and contains the source map, four orphan predicates,
grammars, traversal roles, and denial policy only. The inventory is returned as a
separate operational value and `collect_stable_authority()` explicitly discards
it. Cache-directory device, inode, links, size, and clocks therefore do not enter
the manifest, environment digest, projection, or build ID.

The child collector body contains no `_guard_read_absolute_regular`, `os.open`,
`read_bytes`, content hash, header read, or launcher collector call. It uses only
no-follow metadata for actual PYC rows and cache directories. The launcher remains
the separately implemented content-reading retained oracle.

## Independent cache-directory attacks

A separate no-site review helper, independent of the producer tests, constructed
fresh isolated roots for both collectors. Its exact-row assertion and all attacks
passed:

| Attack | Launcher evidence | Child evidence | Result |
| --- | --- | --- | --- |
| exact complete row | exact ten-key row equals one `os.lstat` snapshot | exact ten-key row equals one `os.lstat` snapshot | PASS |
| same-path mode-`0755` replacement | inode `91606265 -> 91606266`; ctime changed | inode `91606310 -> 91606311`; ctime changed | unequal snapshots |
| same-inode clock drift | inode `91606273` retained; mtime and ctime changed | inode `91606318` retained; mtime and ctime changed | unequal snapshots |
| link/size/entry drift | links `2 -> 3`; size `64 -> 96` | links `2 -> 3`; size `64 -> 96` | unequal snapshots |
| directory symlink | rejected | rejected | PASS |
| unsafe mode `0700` | rejected | rejected | PASS |

The full fixed suite also exercises both collectors through the parameterised
twelve-case cache-directory population. The persistent replacement attacks retain
the same relative path and accepted mode, so their rejection is specifically due
to the newly bound identity/clock row rather than path creation or mode failure.

## Independent authority, mapping, and PYC ownership reconstruction

A no-site helper separately executed the child and launcher implementations and
required exact equality of selectors, closure rows, wheel rows, extracted rows,
the complete destination map, stable PYC policy, repository digest, twenty stable
components, and component counts. It passed with:

```text
selected wheels: 81
mapped destinations: 9,595
PYC stable source rows: 5,859
optional orphan predicates: 4
live PYC rows: 1,185
live cache-directory rows: 151
component/count sequence:
(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,3,81)
```

The live inventories use intentionally different PYC operational detail: the
launcher binds PYC bytes while the child binds metadata without reading content.
After projecting the common ownership/classification fields and sorting those
projections canonically, all `1,185` PYC and `151` cache-directory rows were equal.

The exact external mappings reproduced independently:

| Installed destination | Owner / scheme | Extracted row evidence |
| --- | --- | --- |
| `share/man/man1/bandit.1` | `bandit` / `data` | 6,545 bytes, mode `0o644`, SHA-256 `935728a5192792b9d7ccec8e02f76f0ba8b097e4006141b51ce591b00b647562` |
| `include/site/python3.12/greenlet/greenlet.h` | `greenlet` / `headers` | 4,755 bytes, mode `0o644`, SHA-256 `b33e69611490a9e7603add80320c4b65d4e33bea9caff24cbe0884251f48009f` |

Both required exact canonical external RECORD spelling, singular same-owner
mapping, and equal mode/hash/size. The fixed tests retain rejection of missing,
owner-swapped, colliding, and escaping mappings.

One reviewer-only helper initially exited `1` at its final live semantic tuple
comparison because it preserved the two collectors' intentionally different
full-row sort orders after projecting away their different operational fields.
All preceding authority, mapping, policy, and count assertions had passed. The
corrected helper canonically sorted the common projections, exited `0`, and proved
semantic equality. This was a review-helper assertion defect, not a producer
finding, and caused no repository or producer write.

## Retained R2-R4 predicates and actual admission

The complete final-hash population passed exactly `203 passed in 114.29s`. It
retains attacks for frame/header/digest/EOF handling, v2 aggregate terminal drift,
guarded link/hardlink/mode/path escape, prefix reuse and early rebuild, canonical
child input, strict UUIDs, two-hop wheel cache links, `.data/data` byte drift,
mapping collision/escape/owner swap, fourth interpreter alias, bootstrap byte
drift, a fourth PTH, editable metadata/direct-url/uv-cache drift, unowned site
payload, unselected runtime origin, inherited environment values, child-collector
substitution, unmanifested source plus pytest pyc, PYC creation/deletion/content/
header/mode/link drift, wrapper digest drift, repository identity substitution,
immutable conflict, staged publication, build contracts, and v2 aggregate closure.

The isolated actual admission separately passed `1 passed in 30.38s`. Its two
runs proved equal build ID, code-manifest ID/digest, invocation, immutable manifest
inode, twenty-component/count validation, repository identity, strict 25-field
projection/inverse, three ordered layer paths, no rebuild entrypoint execution,
and no real-root code/admission publication. Operational run IDs and future
rebuild paths remained distinct as required.

## Gate evidence

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run --locked --no-sync ruff format --check ...` | 0 | three files already formatted |
| `uv run --locked --no-sync ruff check ...` | 0 | all checks passed |
| `uv run --locked --no-sync mypy ...` | 0 | no issues in three files |
| required four-file pytest population | 0 | exactly `203 passed in 114.29s` |
| isolated actual two-run admission | 0 | `1 passed in 30.38s` |
| independent no-site directory attacks | 0 | exact rows and all six attack classes passed for both collectors |
| corrected no-site authority/map/PYC reconstruction | 0 | exact authorities; 81 wheels / 9,595 mappings; live ownership equal |
| `uv run --locked --no-sync bandit -q -r ...` | 0 | no findings |
| `uv run --locked --no-sync lint-imports` | 0 | three contracts kept, zero broken |
| `uv run --locked --no-sync python -B scripts/verify_local_only.py` | 0 | PASS, 25 checks, zero failures |
| shell preflight/postflight inventory | 0 | counts and both complete digests identical |
| final six-binding SHA-256 recheck | 0 | all exact |

The initial sandboxed static-check attempts exited `2` because the sandbox denied
read access to `/Users/adrian/.cache/uv/sdists-v9/.git`. They made no change. The
same locked/no-sync commands were then approved for read-only existing-cache
access and all exited `0` as recorded above.

## Residual risk and disposition

No P0, P1, or P2 defect remains within the R5 packet. The already documented
same-trust-domain transient replace-and-restore residual is unchanged; R5 closes
the required persistent identity/clock changes at every retained equality boundary
without claiming an atomic filesystem transaction.

Decision: **PASS — `P0/P1/P2 = 0/0/0`.**
