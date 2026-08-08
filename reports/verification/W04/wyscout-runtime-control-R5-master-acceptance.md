# W04 Wyscout runtime-control R5 master acceptance

Date: 2026-08-02

## Decision

`ACCEPTED` with independent findings `P0/P1/P2 = 0/0/0`.

The final R5 runtime-control candidate implements the exact R20 v15 admission
child and a separately reconstructed launcher authority. The complete child and
launcher authorities, twenty component values and counts, repository-code
identity, immutable publication, strict 25-key projection/inverse and no-rebuild
boundary reproduce exactly. No real-root code manifest, admission prefix, product
or receipt was written by producer, reviewer or master acceptance.

## Frozen bindings

| Artifact | SHA-256 |
| --- | --- |
| `scripts/admit_wyscout_v5_runtime.py` | `cba67d6a143951cbeefa2e63063f5f09aab73f6ec435a1378fb2451d59950cb5` |
| `scripts/launch_wyscout_v5.py` | `d3ac8c84995c8475b0a4df983899ebf6b364f047dcbba45c411d55b62c808740` |
| `tests/unit/test_w04_wyscout_runtime_control.py` | `61f1d770d1b662df0f30c6d4bc54aace9f0fa1069d32501c7d466be908b66fb4` |
| producer return | `f6a75dc396672fc64a67c5a39579b4cbd11d46df6d85e3d728d7e247128989bd` |
| independent review | `7578cd604af30e36d1ac801e7df2af93a55dbdfc7f1f2baaccd2f245d4d26f01` |
| reviewer return | `51279c0c522004fddf5fcc83e59514ccc8682e76a4a6fd650532d12488a3b0d8` |

Master no-site reconstruction produced repository-code authority
`9a1956edd669a6e051ec432d9ffdf1b7aeebbe5569d620f2be16b35dc5a2782f`.
Child and launcher repository identity, all twenty component values and the count
sequence below were equal:

```text
(1,1,1,35,81,81,1,1,17,1,1,1,81,1,1,748,1,1,3,81)
```

## Master reproduction

| Check | Result |
| --- | --- |
| complete fixed-hash runtime/build/aggregate/publisher test population | `203 passed in 114.35s` |
| isolated actual two-run admission | `1 passed in 30.08s` |
| no-site child-versus-launcher reconstruction | repository/components/counts all equal |
| independent review | `PASS`, `P0/P1/P2=0/0/0` |
| final artifact hashes | exact frozen bindings |
| local-only boundary | main branch, zero remotes, no provider/network/cloud/container/deployment/publication |
| real product/control roots | unchanged; no rebuild execution or real-root publication |

The master reproduction used locked/no-sync uv, `PYTHONDONTWRITEBYTECODE=1` and
`python -S -B` for the direct authority reconstruction. The first sandboxed uv
test attempt failed only because the existing uv cache was outside the workspace;
the approved read-only-cache rerun passed and changed no dependency, lock or
runtime authority byte.

## Corrected exact predicates

Acceptance includes exact Packaging/lock/wheel selection, singular one-hop cache
associations, all five PEP 427 mappings, complete extracted and installed
ownership, exact bootstrap/coverage/editable metadata, total executable census,
three-alias interpreter/libpython/loader/stdlib closure, closed environments,
source-complete stable PYC ownership, independent launcher content preflight and
child path/lstat census with zero child PYC content reads. Cache-directory rows
bind complete no-follow device/inode/mode/link/size/mtime/ctime state operationally
at every pre/post equality boundary and remain excluded from stable identity.

## Residual risk

The accepted same-trust-domain transient replace-and-restore residual remains as
documented by R20. It is not broadened by R5. Persistent or observed byte, path,
identity, mode, link, size, inventory or clock drift fails closed. Runtime bytes
are deliberately frozen to the accepted local macOS arm64 Python 3.12.12 and uv
0.9.21 authority; host drift fails closed.

Disposition: runtime-control prerequisites are accepted and the guarded vertical-
slice product packet may dispatch. Real-root publication remains master-only after
fresh product review and the complete repository gate.
