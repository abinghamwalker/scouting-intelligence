# W04 Wyscout runtime-control independent review R11

- Date: `2026-08-03`
- Task: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R11`
- Producer task: `W04-WYSCOUT-RUNTIME-CONTROL-01-R11`
- Recommendation: **PASS**
- Severity counts: **P0/P1/P2 = 0/0/0**

## Binding and scope verification

I read `AGENTS.md` and every packet `read_first` path completely before review
work. The review packet itself is exact at
`b3401e8afd95a7304eaff56c41e37dd035d80d4fcb93f6e2d8adcbb3c565a33a`.
Every fixed binding reproduced before any Python-backed command:

| Artifact | SHA-256 |
| --- | --- |
| R11 producer packet | `dd047fbbe8ad9199dddcc23a6970ee351b9f0c6b62c3776cab2f0879a54d7804` |
| R11 producer return | `01f5f2f076f3e096f937a00d46be3b83968eae63586f150883321affa76d20b3` |
| R21 design | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |
| R21 independent review R15 | `262fbf6f4cc3f239daebb8db69059d46125415647d58ffb432b630c44353c3aa` |
| R21 master acceptance | `5a50b633e7ea4384fb65dd4008f8fb25da0cbf40d42b4408687315adde07b85f` |
| Runtime R10 master acceptance | `1f7c09f15ea7ae8f3fbac9f517ad2e9b444b177da719751013eae5c2b867562a` |
| Candidate admission child | `68cb2e96a8006ab7e529d614d037a18e4b0dbd982c0c3e119ef23319f66b78cc` |
| Candidate launcher | `db77870605410ca16554b5ed869a6304c2b24b60122b21f1646b2d09c3dc2779` |
| Candidate runtime tests | `bd65a02b5dfa73e1f6bbf7d5e3bf32937c62233c9f12f07eeca4a9de65313332` |
| Unchanged security tests | `5907b945fa61855ff1104a2e03dd13057a76863251258b8a53088e322b44d18d` |

I kept producer code, tests, orchestration, PYC, products, manifests, staging,
data, runs, and retained failures read-only. Python bytecode and tool caches
were redirected to `/private/tmp`. I performed no real-root execution, cleanup,
publication, dependency operation, or Git operation.

## Exact R21 resource roster

I mechanically extracted the numbered paths from R21 Section 10 and the
producer packet's fixed ordered list, then compared them position-by-position.
The sequences are identical, cardinality and uniqueness are both exactly 30,
and neither contains a glob, discovery expression, directory shorthand,
optional path, absolute path, traversal component, or normalization choice.

The immutable R20 members occupy positions 1 through 17 unchanged. The exact
R21 additions occupy positions 18 through 30. Independent canonical roster
digests are:

- first 17 path sequence:
  `7068f5bbdcc6651c330d21da9ef1e2db2934fd245e90af9f2342558d341cd4ec`
- appended 13 path sequence:
  `f0fdf14df49111235a2785dc8a6052f6f59361c9d98d27f381ab2ac004f3ad70`

Both `scripts/admit_wyscout_v5_runtime.py` and
`scripts/launch_wyscout_v5.py` expose the identical exact tuple and the exact
algorithm token `w04-local-resource-exact-30-v1`. The admission and launcher
retain separate row constructors; no implementation delegates roster choice to
a glob, scan, sort, optional lookup, or the other implementation.

## Physical rows, digest meaning, and component proof

The independent proof opened all thirty paths using contained no-follow
descriptor traversal and required a singular regular file at each leaf. It
read the complete current bytes under stable device/inode/mode/link/size/clock
metadata and independently reconstructed every row as the unchanged closed
surface:

```text
mode
path
sha256
size_bytes
```

Position 17, `reports/phase-gates/W04/source-schema-profile.md`, is exactly
mode `0600`; all other resources are mode `0644`. Admission and launcher
reconstructed byte-identical rows in the same order. Canonical detail

```text
{"algorithm":"w04-local-resource-exact-30-v1","rows":<ordered 30 rows>}
```

reproduced the fixed SHA-256
`29d8a7cf4c4acab8a52d6008fc5f8975509cc445f5680e45e5974687e65c7bfb`.
This preserves the accepted resource-digest meaning: it is still the stable
digest of the same exact ordered physical-row fields; only the governing R21
roster cardinality and algorithm version token changed.

I also constructed a strict 20-component admission result around this exact
resource detail, including canonical manifest bytes, environment binding,
ordered component proofs, and evidence row count 30. The independent retained
authority validator accepted it. A coherently rehashed resource component and
an independently mutated proof count were both rejected against the frozen
authority.

## Independent adversarial proof

The read-only proof helper `/private/tmp/w04-r11-independent-proof.py`, SHA-256
`c684e6754dfa8672cfda42655913ca1773edd79242c5618f358075a9dad8b2d2`,
returned `PASS`. It rejected all 17 distinct attacks:

1. omission;
2. insertion;
3. duplicate;
4. reorder;
5. v1-for-v2 substitution;
6. v2-for-v1 substitution;
7. obsolete 17-resource algorithm;
8. drifted 30-resource algorithm;
9. mode mutation;
10. physical-hash mutation;
11. size mutation;
12. path mutation;
13. coherent attacked row/detail reconstruction;
14. nonregular directory leaf;
15. symlink leaf;
16. coherently rehashed component-value substitution;
17. component-proof count mutation.

Every detail attack produced a digest different from the frozen value, and
every attack was rejected by the independently frozen roster, physical-row,
detail-digest, or strict component-proof predicate. Test-only filesystem probes
were created under `/private/tmp`; no repository or retained byte was written.

## Retained-root and PYC preservation

Fresh complete shell-only preflight inventories, captured before any
Python-backed review command, reproduced the fixed evidence:

| Scope | Rows | SHA-256 |
| --- | ---: | --- |
| `data/**` and `runs/**` | 272 | `c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c` |
| selected site-packages PYC/cache directories | 1218 | `ad6397ba9131fc7684bf9dbfdef4e3ae69ef9a7d9662f561948bef16868f835e` |
| repository PYC/cache directories | 132 | `9b1407d4f9d5adae170014b9a4852bc1e62331efd57c99d04e69df14ac8719a2` |

Fresh complete shell-only postflight inventories after the entire verification
gate reproduced the same row counts and SHA-256 values byte-for-byte. The gate
therefore created, removed, or mutated no retained-root or governed PYC/cache
entry.

## Complete verification gate

- Ruff format over the four packet paths: PASS, `4 files already formatted`
- Ruff check over the four packet paths: PASS, `All checks passed!`
- mypy over the four packet paths: PASS,
  `Success: no issues found in 4 source files`
- exact seven-file pytest population: PASS,
  `403 passed in 1680.93s (0:28:00)`
- Bandit over admission/launcher/rebuild: PASS, no findings
- import-linter: PASS, 3 contracts kept and 0 broken
- local Git guard: PASS; executable guard present and simulated pre-push
  rejected with exit status 1
- local-only verifier: PASS, all 25 checks, branch `main`, zero remotes
- final retained/PYC shell inventories: PASS, all three postflight streams are
  byte-identical to preflight and the fixed evidence

The complete locked/offline gate ran sequentially in retained exec session
`16410` with Python bytecode disabled and every tool cache redirected under
`/private/tmp`. Its helper SHA-256 is
`8d862a40cc5b9f6e50ce11b069cad24ae8f113c98e2a56750ddf6b72e660d1f5`.
Every fixed candidate and governing binding was rehashed after the gate and
remained exact.

The packet forbids every Git operation, so the reviewer does not invoke the
listed `git diff --check` or `git remote` commands. The permitted local-only
validator supplies the independent branch and zero-remotes predicates; the
master retains ownership of direct Git checks.

## Findings and disposition

- P0: 0
- P1: 0
- P2: 0

The exact-30 roster correction is complete, correctly bound to R21, physically
and logically fail-closed, independently adversarially proved, and fully green
under the required 403-test gate. I return **PASS** for master adjudication. This
review is not self-approval and performs no acceptance or checkpoint operation.
