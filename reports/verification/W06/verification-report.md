# W06 final verification report

Status: **VERIFIED**
G-W06 model decision: **NO_GO**

## Terminal checks

- locked offline environment: PASS, 83 packages resolved and 82 audited;
- repository formatting: PASS, 881 files globally checked; all seven security-correction paths rechecked;
- repository lint: PASS;
- typing: PASS, 82 source files globally and three corrected files rechecked;
- import contracts: PASS, 3 kept and 0 broken;
- security scan: PASS after explicit optimized-mode guards; zero Bandit findings in `scripts` and `src`;
- local Git guard: PASS, executable with simulated exit 1;
- local-only verifier: PASS, 25/25;
- focused W06 evaluation/protected/security suite: PASS, 25 tests; and
- frozen preregistration, public fixtures and retained protected outputs: byte-identical.

## Complete repository test evidence

The valid outside-sandbox complete invocation ran all 2,719 then-existing tests:
2,715 passed and four W04 cache-sensitive controls rejected the in-place
`evaluation.cpython-312.pyc` before their logical assertions. The master recoverably
quarantined exactly 15 later-wave PYC files at
`/private/tmp/w06-pyc-quarantine.ijxUT8`; the exact four failed node IDs then passed 4/4
in 85.73 seconds. Thus every one of the 2,719 tests passed in the terminal evidence set,
with no W04 byte or authority change. The complete invocation duration was 1,884.94
seconds and retained one unrelated deprecation warning.

An earlier sandboxed attempt is excluded from the valid gate because a task-local uv
cache lacked `archive-v0` and sandboxed child `uv` processes were denied the locked user
cache. It retained 2,679 passes and 40 environmental failures. No product correction was
made for that attempt. These cache/PYC observations remain the already deferred W10
host-state class and do not affect a W06 metric, interval, partition, protected decision
or claim.

The terminal security scan initially found seven W06 runtime asserts and three
statistical PRNG calls. The accepted bounded correction replaced the asserts with
explicit guards, scoped `B311` only to deterministic bootstrap/null randomness, and
passed independent optimized-Python review with 0 P0/P1. The post-correction focused
suite passed 25/25 in 0.54 seconds and the full Bandit scan passed.

The W06 phase verifier is retained at
`reports/verification/W06/phase-verifier-candidate.json`. W07 remains PLANNED and was
not begun.
