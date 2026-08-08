# W04 Wyscout runtime-control R11 master acceptance

- Date: `2026-08-03`
- Task: `W04-WYSCOUT-RUNTIME-CONTROL-01-R11`
- Review: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R11`
- Decision: **MASTER_ACCEPTED**
- Findings: `P0/P1/P2 = 0/0/0`

## Accepted bounded correction

R11 closes the physical runtime-resource mismatch found during the pre-health
hierarchy audit. Effective R21 authority requires exactly thirty ordered local
resources, while the R10 runtime still bound the earlier R20 seventeen-resource
subset. Under the standing bounded-correction authority dated `2026-08-02`, R11
changes only the duplicated admission/launcher roster, its versioned algorithm
token, and focused tests.

The accepted roster is position-by-position identical to R21 Section 10:

- members 1 through 17 are unchanged from R20;
- members 18 through 30 are the exact R21 additions;
- cardinality and uniqueness are exactly 30;
- admission and launcher expose byte-identical ordered tuples;
- the algorithm is exactly `w04-local-resource-exact-30-v1`; and
- no glob, scan, sort, shorthand, optional path, substitution or normalization
  can select a resource.

The existing stable resource-row meaning is preserved. Each row remains the
exact closed `mode`, `path`, `sha256`, `size_bytes` observation over a singular
contained regular file. Position 17, the source-schema profile, is mode `0600`;
the other 29 resources are mode `0644`. The accepted canonical resource-detail
SHA-256 is
`29d8a7cf4c4acab8a52d6008fc5f8975509cc445f5680e45e5974687e65c7bfb`.

No logical field, root roster, serialization, inverse, source or rights
authority, product population, manifest/build formula, digest meaning,
dependency, lock byte or intended output changes in R11. A later code manifest,
build and product/receipt byte may change only as a mechanical consequence of
the accepted governed source bytes.

## Fixed accepted bindings

| Artifact | SHA-256 |
| --- | --- |
| producer packet | `dd047fbbe8ad9199dddcc23a6970ee351b9f0c6b62c3776cab2f0879a54d7804` |
| admission child | `68cb2e96a8006ab7e529d614d037a18e4b0dbd982c0c3e119ef23319f66b78cc` |
| launcher | `db77870605410ca16554b5ed869a6304c2b24b60122b21f1646b2d09c3dc2779` |
| runtime unit tests | `bd65a02b5dfa73e1f6bbf7d5e3bf32937c62233c9f12f07eeca4a9de65313332` |
| unchanged security tests | `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d` |
| producer return | `01f5f2f076f3e096f937a00d46be3b83968eae63586f150883321affa76d20b3` |
| independent review packet | `b3401e8afd95a7304eaff56c41e37dd035d80d4fcb93f6e2d8adcbb3c565a33a` |
| independent review | `d2fa07e7df97ca528ce6c7e0c08c8f84278f49f2541f60e22a48558c50325fcc` |
| independent review return | `17451dd5c5ef9c92032a6a50df3ef532095381a13bc309cd4e1687178bf372a7` |

## Producer and independent review

The producer's final exact seven-file population passed `403 passed in
1501.91s (0:25:01)`. Ruff format/lint, mypy, Bandit, import-linter and all 25
local-only checks passed. Its initial full gate correctly exposed one retained
`counts[8] == 17` assertion; the producer stopped only that exact gate process,
corrected the stale bounded constant to 30, reran focused proof, and then ran the
complete gate fresh. This was documented rework, not an accepted partial run.

The fresh independent reviewer reconstructed all thirty physical rows, strict
20-component authority and the fixed detail digest. It rejected 17 independent
read-only attacks covering omission, insertion, duplicate, reorder, v1/v2
substitution, obsolete/drifted algorithm, path/mode/hash/size mutation,
nonregular/symlink leaf, coherent attacked detail and component-proof mutation.
The reviewer returned `PASS`, `P0/P1/P2 = 0/0/0`, with `403 passed in
1680.93s (0:28:00)` and all static, security, import, guard and local-only checks
green.

## Independent master reproduction

The master began with locked all-group offline sync: 83 packages resolved and
82 audited. It independently extracted the R21 numbered roster and compared it
to both runtime tuples, obtaining `MASTER R11 ROSTER PASS: 30 exact ordered
unique paths`; focused resource tests passed `10 passed, 113 deselected`.

The complete master gate ran in retained exec session `75472`, shell PID `91714`
and pytest uv PID `1420`, using helper
`/tmp/w04-r11-master-gate.zsh` at SHA-256
`6826825f6db969e14742ac86c85c1cb4a411d1f038096e227000887eba997a0a`.
All caches, bytecode and inventory snapshots were isolated under `/tmp`.

- Ruff format/check: PASS
- mypy: PASS
- exact seven-file pytest population: `403 passed in 1683.55s (0:28:03)`
- Bandit: PASS
- import-linter: 3 kept, 0 broken
- local Git guard: PASS, simulated push rejected with exit 1
- local-only: PASS, 25/25 on `main` with zero remotes
- direct master `git diff --check`: PASS
- direct master remote check: empty

The master's first helper invocation, session `92890` / shell PID `82786`,
stopped before static or test execution because the retained temporary census
helper lacked execute mode. The helper content hash remained exact; the master
changed only that `/tmp` mode and ran the entire gate fresh. This procedural
harness correction changed no repository or retained-root byte and contributes
no acceptance result.

## Preservation proof and disposition

Producer, reviewer and master final pre/post inventories agree exactly:

| Scope | Rows | SHA-256 |
| --- | ---: | --- |
| selected site PYC/cache | 1218 | `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e` |
| repository PYC/cache | 132 | `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2` |
| retained `data/**` and `runs/**` | 272 | `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c` |

R11 is accepted. It does not release a new real-root execution by itself: the
separately documented R12 loaded-runtime subset/completion-evidence correction
must complete producer, fresh independent review and master acceptance first.
Existing R2/R3 runtime outputs remain immutable retained superseded evidence.
No Git, real-root, cleanup, deployment, publication or external operation was
performed by the R11 producer or reviewer.
