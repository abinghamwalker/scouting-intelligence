# W04 staged immutable publisher R3 master verification

Date: 2026-08-01

Decision: `PASS_TO_MASTER_ACCEPTANCE`

The master independently inspected the complete R3 publisher correction, its
adversarial tests, the retained failed review, and the fresh zero-finding review.
The exact R1 replay race now fails closed after the validator, final recheck and
fresh immutable-final readback: an exact `.partial` that exists at the final
identity-bound checkpoint cannot accompany a success result.

## Frozen chain

- R3 packet:
  `8253d13832db1eb0fdb4d8cedb7829768524ebe9028ed2964591ec53068fa2cf`;
- publisher:
  `01b56c0400af0a4fba1adbf06b53b4e94a8571be66c7e0770ca6d72b4c740c13`;
- tests:
  `639503018a5528ad8463d21e68fbfd0133e09c9884838a2422daf911173f709e`;
- producer return:
  `e218ad99c9323aef57f2dfa50fef219afff6686f0bc89c2d84fe3d0f1aaab69a`;
- retained failed review / return:
  `6e574fde38eefba002db7568596f10346beb7d6e16c7149bdda2af6cb402a7d3` /
  `bdb9826137d6b094b8e19d79e6480c5f2fcfb792df51534e5ab9f022b453ceb7`;
- fresh PASS review / return:
  `77516478c9dd386f0e44179c1cf8219fd925f26b0460a73c771fb4f5e409d1c5` /
  `984cac01350e39f8641b02d67eaed079e29bd8304a4d5dc62dc2b4a8fc7c0cff`.

## Master checks

- `uv sync --locked --all-groups`: 83 resolved, 82 audited.
- Ruff format/check: PASS.
- mypy: PASS.
- full publisher/format/guarded-storage matrix: `155 passed in 2.27s`.
- targeted regular, nonregular and parent replay matrix: `8 passed in 0.22s`.
- Bandit: PASS, zero findings.
- local-only verifier: PASS, 25/25.
- exact `.partial` census under the real W04 working root: empty.
- `git remote`: empty.

The master read back the exact descriptor-relative staging checkpoint: it reopens
the fixed staging root without following links, requires the original parent
device/inode, and checks only the exact serializer-owned name. Regular evidence
raises a race error; symlink, hardlink, FIFO, directory and unsafe mode/link states
raise a path-security error; disappeared or replaced parents raise a race error.
No path is repaired, removed, chmodded or replaced.

## Accepted residual and scope

The accepted same-trust-domain residual is unchanged: a staged name that appears
and disappears wholly between filesystem checkpoints is not cryptographically
excluded. Removing that residual requires a different primitive/trust boundary and
is not claimed here.

This verification creates no product publication permission. No real Bronze,
Silver, Gold, manifest, receipt, run or staged byte was created; no dependency,
provider access, Git remote, cloud, container, hosted CI, endpoint or deployment was
introduced.
