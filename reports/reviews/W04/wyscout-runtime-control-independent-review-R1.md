# W04 Wyscout runtime-control independent review R1

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=2`, `P2=0`.

The fixed producer bytes, v2 logical aggregate bindings, locked/no-sync child
argv, canonical result framing, immutable publisher replay, 25-key projection,
sole contract build hash and strict invocation inverse all reproduced. Two actual
admission subprocesses under two distinct direct mode-`0700`, non-symlink isolated
root sets returned byte-identical manifests, build IDs and invocations, and did
not create a rebuild prefix or execute the absent rebuild child. Those positive
results do not establish v15 admission because the implementation does not perform
the predicates represented by several component digests, and the launcher's
retained authority is delegated to the child implementation itself.

## Fixed bindings and immutable inputs

Every review-packet binding matched before merits review:

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `dc162985e6bccaa4ea4161d22ddf89c2b2017968c4703e65dc1c37645e78602a` |
| launcher | `4e97bb9828453c184dca14c78c71e2659df628d6aec6b459e41faf5e5da719a1` |
| runtime-control tests | `f596c5f353f162f16bc9e43cc0cb43e2c8d9553271ccb979075e98613e750422` |
| producer return | `7f7782368b5191119372bab4cee70632518944387ab67aac82797cda026c030b` |
| aggregate master acceptance | `3b9cd3810aa453c3d6470ce5ee4d54f6ea0d4f825fb95812af9f5fbac66f005e` |
| implemented-schema bundle v2 logical no-LF | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` |
| product contract v2 logical no-LF | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` |

The implementation packet's additional fixed bindings also reproduced:
build contract `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16`,
publisher `01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13`,
R20 design `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`,
`pyproject.toml` `963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b`,
and `uv.lock` `1c4d3408f3fd900443356f8387a1fed3554f9e0b69e74d9997cd99b60be134ca`.
No producer byte was edited.

## Findings

### W04-RUNTIME-R1-P1-01 — claimed v15 components are not backed by their required admission predicates

Severity: **P1**.

`collect_stable_authority()` in
`scripts/admit_wyscout_v5_runtime.py:694` constructs the twenty component values,
but multiple values are digests of abbreviated declarations rather than results of
the R20 checks whose meanings they claim:

- `_lock_authority()` at line 521 takes all lock packages except the literal
  `colorama`, retains only name/source/version, and copies every wheel declaration.
  It does not select the marker/extra closure, compute actual ordered compatible
  tags, select one compatible wheel per member, or prove parent edges.
- `_installed_record_rows()` at line 579 hashes only 82 `RECORD` files. It never
  parses their rows, proves `L == I`, verifies singular ownership, validates mapped
  installed payload bytes, validates extracted trees/cache association, or proves
  PEP 427 equality. Nevertheless lines 746 and 750 issue
  `extracted_runtime_digest` and `installed_record_runtime_digest`.
- `_executable_rows()` at line 601 accepts whatever 35 same-named mode-`0755`
  files currently exist and records only name/hash/size. It does not validate the
  33-E/one-P/one-W partition, 21 owners, entry-point group/target, RECORD values,
  exact four-tuple `python3` selector, 30/4 wrapper split, alias chain, deterministic
  bodies, or frozen wrapper/Ruff byte identities before issuing
  `executable_census_digest`.
- `_interpreter_authority()` at line 641 lists three alias names but does not
  inspect any alias link or topology, libpython, loader, or ABI closure.
  `_stdlib_rows()` at line 610 hashes only the three encoding bootstrap sources,
  then labels that result `stdlib_digest`; it does not close the standard library.
- `pyc_policy_source_map_digest` at line 773 contains only repository source rows.
  No site source-authority map, four orphan predicates, preflight classification,
  read denial, audit observation, or pre/post inventory comparison is performed.
- the selector is a four-field declarative object rather than the complete ordered
  `packaging.tags.sys_tags()` result after byte-admitted Packaging bootstrap; uv
  version is copied as a constant rather than observed through the accepted normal
  logical launch; and both normalized environment objects use
  `required_absent=[]` instead of the R20 closed required-absent roster.

This is fail-open with respect to accepted-environment drift: changed installed,
wrapper, alias, stdlib, pyc or wheel state can become a new content-addressed
manifest/build rather than being rejected against the accepted authority. The
resulting canonical manifest is internally self-consistent, but its component names
do not have the accepted v15 meanings. Determinism and content addressing cannot
substitute for the omitted predicates.

Smallest sound correction: implement the exact R20 constructive checks and retained
evidence in `scripts/admit_wyscout_v5_runtime.py`; do not change digest meanings,
component order, projection, root roster, logical model or dependencies. Extend
`tests/unit/test_w04_wyscout_runtime_control.py` with isolated mutations for every
omitted selector/lock/extracted/installed/executable/alias/stdlib/pyc/environment
predicate and require rejection rather than a different successful manifest.

### W04-RUNTIME-R1-P1-02 — launcher retained authority is the admission child's own collector

Severity: **P1**.

The launcher does not independently reconstruct or retain the twenty component
values and counts. `_load_admission_module()` at
`scripts/launch_wyscout_v5.py:388` imports the admission child source in-process;
`_admission_authority()` at line 403 obtains that module's
`collect_stable_authority` at line 407 and uses its return as the expected authority.
The admission subprocess calls the same function from the same bytes. The later
component-proof comparison therefore checks the child against a second execution
of the same producer-controlled oracle, not against an independently implemented
retained authority. A shared omission or shared semantic substitution agrees on
both sides, as P1-01 demonstrates.

Smallest sound correction: give the launcher an independently implemented explicit
read-only reconstruction path over the fixed rosters and v15 predicates, or a
separately accepted immutable authority module whose implementation is not imported
from the child entrypoint. Compare every child component value and positive count
to that retained result before publication. Add a test that substitutes the child
collector/manifest construction while retaining the launcher authority and proves
the disagreement fails closed.

## Independent positive reconstruction

Two actual locked/no-sync, no-site, no-bytecode admissions ran under distinct
isolated output-root sets in
`/private/tmp/w04-independent-runtime-apxdo9fa/exact-1` and `exact-2`, with distinct
admission and rebuild UUIDv4 values. Every exact root was a direct non-symlink
directory with mode `0700`.

Observed equal stable results:

- code manifest SHA-256:
  `8650022adb35503e543f21c88dd52c1da223483c5aaa6f16ba430be763765d69`;
- code manifest UUIDv5: `4399f636-4348-5cd8-92be-f1b7bf27ea84`;
- environment digest:
  `6261ace29867acb511835aea52ef06e9abddd1334f7873c9e83eee5e8b126b0d`;
- build ID:
  `f61a6e4360c2a83a6009703985e7893f6408e83bd7d1ccc2187d5db4b62f5fc0`;
- canonical invocation SHA-256:
  `25838f8099504f262e1a988e8b21283f76a55efdf48c624002f1072feb2106bc`;
- manifest size: 2,249 bytes.

The two manifests, build IDs and invocation values were byte/value equal. The
operational run-bound rebuild prefix and receipt paths differed. A separate
readback reconstructed the ordered twenty manifest values, recomputed the
environment digest, UUIDv5, exact 25-key projection and build ID, constructed the
25-key invocation only through `invocation_from_projection()`, and reproduced the
strict `projection_from_invocation()` inverse. Immutable replay retained one final
manifest per isolated root with no `.partial` residue. No build-scoped rebuild
prefix existed and `scripts/rebuild_wyscout_v5.py` remained absent; no rebuild,
product, layer, boundary, receipt or run writer was invoked.

The positive and producer suites also rejected malformed/truncated/extra-byte frame
data, noncanonical payloads, logical-config terminal drift, unsafe relative paths,
symlink/hardlink/unsafe-mode files, UUID drift, repository identity substitution,
prefix reuse, missing build ID, and unequal existing immutable manifest bytes.
These checks remain valid but do not close the two findings above.

## Review chain of custody

Before the first Python helper, the read-only shell inventory observed 1,087 site
pyc files and 98 repository pyc files. Complete content-list digests were
`d19297713dbb881748135bd510d788df9fc0eb87368789e74f64feda2ddf86ee`
and `17fa94b358a1fc92d39b322ce85e3b68abd7c691f91931b58e74ad6d75319a23`;
metadata-list digests were
`beb14c198f4a489ef6c769657047398e6a3e274a343224de12ec053ed77b5c26`
and `49eadfc4b06e13ebad9973426a569d310250351d082fff7390c18d55aa3b26e1`.
Every Python/test command used `PYTHONDONTWRITEBYTECODE=1`, locked/no-sync uv
controls and Python `-B` where directly invoked. Postflight counts and all four
digests were byte-identical. No cleanup or repair was performed.

## Packet acceptance checks

All seven packet checks passed under locked/no-sync and bytecode-denial controls:

- Ruff format: `3 files already formatted`.
- Ruff check: all checks passed.
- mypy: no issues in three source files.
- bounded pytest: `161 passed in 35.86s`.
- Bandit: exit `0`, no findings.
- import-linter: three contracts kept, zero broken.
- local-only verifier: `PASS`, 25 checks and zero failures.

These are conformance regressions, not evidence that the omitted runtime predicates
were implemented.

## Scope and continuation

Producer bytes stayed immutable. Only this review and its reviewer return were
written. No Git operation, dependency/lock change, real W04 data/manifests/runs
write, network call, provider access, rebuild execution, product write, cleanup or
edit outside the review packet's two allowed paths occurred.

Fresh review should rerun the fixed hashes, full v15 reconstruction, two actual
isolated admissions, immutable replay, shared-oracle disagreement test, complete
mutation matrix, exact projection/build/inverse and all packet checks after the
bounded correction.
