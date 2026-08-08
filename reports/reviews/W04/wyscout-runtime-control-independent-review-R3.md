# W04 Wyscout runtime-control independent review R3

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=2`, `P2=0`.

The frozen R3 bindings match and the static gates are green, but the required
final-hash gate is not: `168 passed, 10 failed`. The final narrow installed-RECORD
hardening rejects two legitimate, hash-verified five-scheme PEP 427 destinations
in the live frozen environment, so retained authority reconstruction fails before
the admission child and the required two-run admission cannot execute. A separate
targeted attack also proves that the launcher accepts a repository pyc whose source
is outside the repository code manifest and all exact orphan predicates. The child
does not independently enumerate actual site/repository pycs at all. These are one
false-rejecting admission break and one fail-open authority break; PASS is not
available.

## Fixed bindings and no-write chain of custody

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `10b70fadc0f6eae5b6df463afda08413d810f5a4d8b46c4688a7dafee6d1cd34` |
| launcher | `3bfb912b9a1bf011248d2ad39e91947f176ba03b421cfb77a468458c858632cf` |
| runtime-control tests | `17757be5f2db591b81fd2e13201d27c75bd095e3da536b67216463844aae74b7` |
| producer return | `8d39fb2238851dfe9568debfd03905fe12d19edd32528cef2451d337de8aef71` |
| R2 review | `4a8ac98ba094499ec38f41e2196b24f412fd355f7d0efc9dce81e2b0cd69f704` |
| R2 reviewer return | `0ffcb9793a54a7ed0e867660eb4c664709a2a30af2e8f3a782d736cafddc8bfe` |

The producer bytes were read-only throughout and all six hashes were rechecked
unchanged after the last bounded command. The read-only preflight and postflight
inventories were identical:

- site pycs: `1087`; complete pyc/cache-directory inventory digest
  `2f36c7b70cf5946f60f3595a673bdc9a771e46266403ddd331cabb46436e8fcb`;
- repository pycs excluding `.venv`: `98`; complete pyc/cache-directory inventory
  digest `a19d7ec64519ca895895e4953c09de26e6d826562d36fa4d96487d4382f7e1d3`.

No real-root code manifest, admission prefix, rebuild prefix, product, receipt, or
rebuild execution was produced by this review. No cleanup, sync, dependency/lock
change, provider/network operation, or Git operation was performed.

## Findings

### W04-RUNTIME-R3-P1-01 — final RECORD hardening rejects the accepted live five-scheme installation

Severity: **P1**.

Both collectors permit an installed RECORD path containing `..` only when it is
exactly `../../../bin/<safe-name>`
(`scripts/admit_wyscout_v5_runtime.py:684-701` and
`scripts/launch_wyscout_v5.py:647-661`). The frozen installation also contains
two legitimate, hash/size-declared paths produced by the already required PEP 427
`data` and `headers` mappings:

- `bandit-1.9.4.dist-info/RECORD` row
  `../../../share/man/man1/bandit.1`;
- `greenlet-3.5.4.dist-info/RECORD` row
  `../../../include/site/python3.12/greenlet/greenlet.h`.

The full fixed-hash gate therefore fails at the launcher retained collector's
line 661 before admission. Ten tests fail through this common predicate, including
the twenty-component positive reconstruction, corrected bootstrap/editable/wrapper
attacks, child-versus-launcher retained-oracle test, actual two-run admission, and
immutable replay. The final summary is exactly `10 failed, 168 passed in 35.95s`.
The actual two-run admission did not start, so the required twenty component
values/counts, repository identity equality, immutable publication, and
projection/inverse admission evidence were not established against these hashes.

Smallest exact correction: in both collectors, replace the bin-only external-row
exception with a closed installed-path validator derived from the singular selected
wheel's complete PEP 427 mapping. Continue to admit the exact controlled
`../../../bin/<safe-name>` executable rows, and admit an external `headers` or
`data` row only when the same owner has one verified extracted RECORD payload whose
five-scheme mapping produces that exact contained venv destination with identical
bytes, hash, size, mode, and no collision/overwrite/escape. Keep every unrelated
`..` path rejected. Restructure collection if necessary so installed RECORD
validation can compare to the already-required complete extracted mapping. Add
positive tests for the exact Bandit data and Greenlet headers rows plus negative
unmapped/owner-substituted/colliding/escaping external rows in both collectors,
then rerun all 178 tests and the actual two-run admission from the new fixed hashes.

### W04-RUNTIME-R3-P1-02 — repository pyc ownership is fail-open and not independently enforced by the child

Severity: **P1**.

The launcher inventory accepts a pyc absent from the stable repository source map
whenever a same-named ordinary repository source file exists. It reads that source,
labels it `OPERATIONAL_NON_STABLE_SOURCE_DENIED`, and then classifies the pyc as
`REPOSITORY_NORMAL` or `REPOSITORY_PYTEST_REWRITE`
(`scripts/launch_wyscout_v5.py:1521-1542`). This contradicts the R20 closed rule
that every repository pyc must map to a repository-code-manifest-owned source or
one of the three exact repository orphan predicates.

The candidate test at
`tests/unit/test_w04_wyscout_runtime_control.py:554-572` is itself a complete
counterexample: it creates unmanifested `tests/test_present.py` and
`tests/__pycache__/test_present.cpython-312-pytest-9.1.1.pyc`, calls the inventory,
and asserts successful `REPOSITORY_PYTEST_REWRITE` classification with
`OPERATIONAL_NON_STABLE_SOURCE_DENIED`. Independently running only that attack
returns `1 passed in 0.06s`, proving acceptance rather than rejection.

The child constructs the stable source map and four orphan predicates at
`scripts/admit_wyscout_v5_runtime.py:1934-2041`, but
`collect_stable_authority()` merely includes that policy at lines 2044-2065; it
never enumerates or classifies actual site/repository pycs. Calling the collector
twice at lines 2389-2396 compares stable values, not the actual pyc inventory.
Thus a child-only or shared coherent repository pyc substitution is not closed by
independent actual-byte census/no-change enforcement.

Smallest exact correction: remove the `OPERATIONAL_NON_STABLE_SOURCE_DENIED`
acceptance branch. In the launcher, a non-orphan pyc whose derived source path is
absent from the exact stable source map must fail even if an unmanifested `.py`
exists. In the child, independently enumerate the complete site and whole-repository
pyc/cache-directory inventory from the stable source map and four exact orphan
predicates, reject every unowned source/pyc, and require identical complete
pre-result inventory immediately before framing without adding operational rows to
stable identity. Replace the current acceptance test with launcher and child
rejection attacks, plus creation/deletion/content/header/mode/link drift tests.
Then repeat the no-write pre/post review inventory and full gate.

## Gate evidence

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py` | 0 | `3 files already formatted` |
| `uv run ruff check scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py` | 0 | all checks passed |
| `uv run mypy scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py tests/unit/test_w04_wyscout_runtime_control.py` | 0 | no issues in three files |
| required 178-test pytest population | 1 | `168 passed, 10 failed in 35.95s`; actual two-run test failed before child launch |
| `uv run bandit -q -r scripts/admit_wyscout_v5_runtime.py scripts/launch_wyscout_v5.py` | 0 | no findings |
| `uv run lint-imports` | 0 | three contracts kept, zero broken |
| `uv run python -B scripts/verify_local_only.py` | 0 | PASS, 25 checks, zero failures |
| targeted source-present unowned repository-pyc attack | 0 | `1 passed in 0.06s`, confirming fail-open acceptance |

Every Python gate ran with `PYTHONDONTWRITEBYTECODE=1` and `UV_NO_SYNC=1`. The
initial sandbox denial was retried with permission to read the existing uv cache;
it made no repository or environment mutation.

## Positive corrected-predicate evidence retained

The passing portion of the fixed-hash suite includes direct rejection of the R2
two-hop cache link, `.data/data` byte drift, mapping collision, fourth interpreter
alias, bootstrap-byte drift, fourth PTH, editable metadata/direct-url/uv-cache
drift, unowned installed site payload, unselected runtime origin, inherited
operational environment values, and child-collector substitution. Those useful
corrections do not offset either P1 above or establish the blocked positive
admission path.

## Required re-review

Freeze new child, launcher, test, and producer-return hashes after the two bounded
corrections. A fresh reviewer must rerun the no-write inventory, all acceptance
checks, the complete corrected-predicate attacks, actual two-run admission,
twenty-component/count and repository-identity comparison, immutable publication,
projection/inverse checks, no-real-root-write proof, and rebuild non-execution.
PASS remains permitted only at `P0/P1/P2=0/0/0`.
