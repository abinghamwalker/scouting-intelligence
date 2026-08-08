# W04 Wyscout runtime-control independent review R2

Date: 2026-08-02

## Decision

**REWORK.** Findings are `P0=0`, `P1=2`, `P2=0`.

R2 materially improves the constructive selector, lock, installed RECORD,
executable, stdlib, PYC, environment and separate-launcher paths. The fixed R2
bindings match, and the producer return records a broad green gate. Those
positives do not establish the exact v15 authority: targeted review evidence
shows fail-open counterexamples in both collectors, child-only bootstrap
acceptance gaps, an incomplete editable predicate, and remaining closure/recheck
omissions. No tests were run in this review; producer gate results below are
recorded as producer evidence, not independently reproduced.

## Fixed bindings

| Binding | Independently observed SHA-256 |
| --- | --- |
| admission child | `cd8a12da6b9db08c9041823c8b99fae782cf7ff99a72628970354a105c36ce67` |
| launcher | `c56263cc5c4ba79a7dce5ba3ce3623def04b29933a5fdc8f0f0187d1aaf6332d` |
| runtime-control tests | `3ea58958683ff6d1e244925fc98a8cce77d89e34f2814a9b43f2003b656aac6a` |
| producer return | `a97a8a28e3e0d9f39def99f3614dd1d6e5d507c6ab08c5a5096f8c7be83ed45e` |

The producer bytes were treated as read-only. No Git operation was performed.

## Findings

### W04-RUNTIME-R2-P1-01 — the claimed exact runtime components still admit forbidden states

Severity: **P1**.

The following counterexamples are established review evidence:

- Both the admission child and the separately implemented launcher accept a
  forbidden two-hop selected-wheel cache symlink. The child checks only that the
  association itself is a link and then uses transitive `resolve()`
  (`scripts/admit_wyscout_v5_runtime.py:1155-1163`); the launcher does the same at
  `scripts/launch_wyscout_v5.py:1417-1422`. Neither proves exactly one link hop to
  the contained `archive-v0` directory.
- Both collectors omit the complete PEP 427 `.data` mapping. They map only
  `purelib`, `platlib` and `scripts`, then silently `continue` for every other
  scheme (`scripts/admit_wyscout_v5_runtime.py:1232-1242` and
  `scripts/launch_wyscout_v5.py:1475-1484`). The claimed extracted-runtime
  component therefore lacks exact mappings for all five schemes, including
  `headers` and `data`, as well as complete mapping uniqueness, collision,
  overwrite and destination-escape rejection.
- Both collectors accept a fourth interpreter alias because they inspect the
  three named links but never prove an exact alias/link census
  (`scripts/admit_wyscout_v5_runtime.py:1344-1367` and
  `scripts/launch_wyscout_v5.py:1322-1340`).
- The child accepts arbitrary current bytes for `_virtualenv.pth`,
  `_virtualenv.py`, `a1_coverage.pth`, `scouting_intelligence.pth` and
  `direct_url.json`, and accepts a fourth `.pth`. `_venv_bootstrap_rows()` merely
  hashes the five named paths (`scripts/admit_wyscout_v5_runtime.py:1440-1448`);
  it proves neither their accepted bytes/semantics nor an exact site `.pth`
  roster.
- The child labels lock inputs plus repository `src/` rows as
  `editable_root_digest` (`scripts/admit_wyscout_v5_runtime.py:1619-1625`). That
  is not the exact normalized editable distribution predicate over its RECORD,
  METADATA, `direct_url.json`, bootstrap/path bytes and uv-cache/editable
  association. The launcher repeats the same abbreviated construction at
  `scripts/launch_wyscout_v5.py:1553-1559`.

Concise additional source-inspection omissions are:

- Installed RECORD verification validates declared targets package by package,
  but does not prove exact global installed ownership, singular cross-RECORD
  ownership, absence of unowned installed payloads, or the complete authorized
  generated-file/byte closure. The editable distribution is added to `L == I`
  but omitted from the selected-package RECORD loop
  (`scripts/admit_wyscout_v5_runtime.py:647-722`; launcher equivalent
  `scripts/launch_wyscout_v5.py:611-655`).
- Interpreter authority does not close the exact alias/link metadata and inode
  topology or the frozen loader/ABI/libpython predicates. ABI and extension
  values are copied from the running interpreter, and libpython is optional and
  hashed if present (`scripts/admit_wyscout_v5_runtime.py:1331-1397`; launcher
  equivalent `scripts/launch_wyscout_v5.py:1314-1365`).
- The outer launcher and rebuild boundary lack the complete accepted
  environment/control rechecks. Child environment construction imports outer
  `HOME`, `TMPDIR` and `UV_CACHE_DIR` values
  (`scripts/launch_wyscout_v5.py:1699-1725`), while rebuild execution checks the
  supplied plan/inverse and manifest repository field but does not reconstruct
  and compare the full stable authority, aggregate/lock inputs, exact outer and
  child environments, or pre/post runtime controls immediately around rebuild
  (`scripts/launch_wyscout_v5.py:2192-2258`).

These are semantic exactness failures, not merely missing evidence labels. A
forbidden runtime can produce child/launcher agreement and a new internally
consistent content-addressed manifest rather than failing admission.

Smallest sound correction: retain the fixed component order and digest meanings,
but implement exact one-hop cache association, complete five-scheme PEP 427
mapping with uniqueness/collision/overwrite/escape closure, exact bootstrap and
`.pth` census, the normalized editable RECORD/metadata/direct-url/uv-cache
predicate, global installed ownership/generated-byte closure, exact
alias/link/inode/loader/ABI closure, and complete outer/admission/rebuild
environment and pre/post control rechecks. Add isolated rejection tests for each
predicate.

### W04-RUNTIME-R2-P1-02 — the separate launcher repeats the child's omitted acceptance predicates

Severity: **P1**.

The R1 import-and-call defect is corrected: `_admission_authority()` is now a
separate launcher implementation and does not load the child's collector
(`scripts/launch_wyscout_v5.py:1504-1523`). However, independence of source code
does not supply an independent acceptance oracle when both implementations omit
the same required predicates. The launcher's transitive cache resolution,
partial `.data` mapping, non-exact alias roster and abbreviated editable digest
agree with the child on forbidden states. Its bootstrap path list likewise
digests the same five current files without exact byte/semantic or extra-`.pth`
closure (`scripts/launch_wyscout_v5.py:1528-1535`).

Consequently the retained comparison in `prepare_wyscout_v5_launch()` can accept
the same semantic substitution on both sides. Its publication-time reconstruction
(`scripts/launch_wyscout_v5.py:2127-2135`) repeats that incomplete oracle, and
the rebuild path does not perform a complete retained-authority recheck.

Smallest sound correction: preserve the separate launcher implementation but
make it independently enforce every exact predicate listed in P1-01, including
the complete outer/rebuild rechecks. Add disagreement tests that mutate each
child predicate while retaining the launcher authority, plus direct launcher
mutation tests proving shared omissions cannot agree successfully.

## Positive R2 producer evidence

The hash-matched producer return reports the following positive gates. They were
not rerun by this review:

- Ruff format check: three files already formatted.
- Ruff check: all checks passed.
- mypy: success with no issues in the three producer files.
- bounded pytest: `166 passed in 71.34s`.
- Bandit: exit `0`, no findings.
- import-linter: three contracts kept, zero broken.
- local-only verifier: `PASS`, 25 checks and zero failures.
- fresh child/launcher direct-authority comparison: repository digest, all twenty
  component values and all twenty counts equal.

The return also records exact evidence counts
`(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,5,81)` and the following component
digests: local resource `c62f263346fdb058c88e8bc48512fe976315c468b0c6a134ac9451a58e34f772`,
selected lock closure `71e19fea7a508cfe462c047775e494509813ce7612c16a98d46af57f254d8bfd`,
installed RECORD `d555808bed04421dcb3b1f3999cf290c36fae324ccb811143123db70b7a9d70b`,
executable `3378e7407967128fe37b8569f6e90ecb7b0a3762078fd6156f435f695f6debb3`,
extracted runtime `e785af59b5e1d364535b7205b4707d75e767b5b66241ee1a52514a3c04e2805b`,
and PYC source map `78bb13f1a84114cb711d5c111ec48518370dc55687c463e3e1bd7be45eb2c5c8`.
These gates are useful regression evidence but do not test or prove the fail-open
exactness predicates above.

## Scope and continuation

Only this review and its reviewer return were written. Producer bytes remained
read-only. No test, Python helper, runtime admission, rebuild, network/provider
operation, cleanup, dependency/lock change or Git operation was performed.

Fresh review should verify the fixed hashes, independently exercise every
rejection counterexample, reconstruct the complete child and launcher authority,
and then run the full positive, immutable-publication, projection/inverse and
rebuild-boundary gates after bounded correction.
