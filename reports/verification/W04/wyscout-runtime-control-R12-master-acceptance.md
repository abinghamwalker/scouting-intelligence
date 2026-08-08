# W04 Wyscout runtime-control R12 master acceptance

- Date: `2026-08-03`
- Producer: `W04-WYSCOUT-RUNTIME-CONTROL-01-R12`
- Review: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R12`
- Decision: **MASTER_ACCEPTED_TERMINAL_RUNTIME_CYCLE**
- Findings: `P0/P1/P2 = 0/0/0`

## Decision and controlling boundary

The master accepts the frozen R12 correction after reading the complete producer
return, both complete independent-review artifacts, the changed implementation
and tests, both mechanically regenerated aggregate preimages, the two correction
authorities, and the controlling closure steer. R12 is the terminal W04 runtime-
hardening cycle. No R13 or other W04 runtime-control authority is opened.

Accepted runtime R11 and retained real-root R3 remain the minimum operational
baseline as directed by the user. Cross-host PYC/cache-tag/inode/link-count/empty-
directory/timestamp/temp-path assurance that does not reproduce a controlling
P0/P1 is preserved as explicit non-blocking W10 backlog.

## Accepted correction

R12 closes the six failures from the retained complete gate (`507 passed, 6
failed`) without changing a logical contract, root roster, feature/product
population, source or rights authority, intended output, or digest meaning:

1. Both independently implemented PYC collectors classify exactly
   `scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc` by contained
   no-follow metadata under class `REPOSITORY_FOREIGN_CACHE_TAG_DENIED` and
   policy `FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ`. The row has no owner,
   digest, source authority, component, environment, build, product, roster,
   import, or execution authority. The retained PYC is never opened, read,
   hashed, imported, executed or mutated.
2. The exact separate repository-code source prerequisite and foreign predicate
   are closed and adversarially reject missing/substituted/duplicate rows,
   unsafe/wrong path or tag, mode/size drift, link/symlink substitution and any
   attempted PYC read/use in both collectors.
3. The descriptor-only schema/product v2 preimages are mechanically regenerated
   from unchanged v1 inputs and accepted builders. The launcher and tests bind
   their new body digests. The exact 23-root order, earlier-only DAG, algorithms,
   logical population and digest formulas are unchanged.
4. The process-evidence validator binds the demonstrated real Darwin empty mode-
   `0700` prefix-directory link count `2` instead of file-style `1`, while
   retaining exact pre/post identity, emptiness, transport, descriptor, frame,
   timeout, exit and cross-field evidence. Coherent false evidence with `1` is
   rejected.

## Frozen identities

| Artifact | SHA-256 |
| --- | --- |
| producer packet | `35281e769533fed6b042c66c7d6d0c8a87a4916a459c1ffd2d4847b2d8a26e9a` |
| producer return | `7d71f33382f1ae5433def1741c446da59524448d82344bfbdc9ce70d6b109774` |
| terminal review packet | `92b7e265793bbfe72c04ea5daa911f447e4d83e9cde267db27404974abd6fcaf` |
| independent review | `7c37979f3e57701907363513376d269e6f0e9edca37b0e8d991324549b132597` |
| independent review return | `acb5b91ce87b2c7f0545da2040639c214f909038780ef2e984da700f39711fb2` |
| admission child | `db6ffbada5e271310b2b2495b264475d0ace27dfe0e4a0b35077a471fbde5be0` |
| launcher | `827714c8baefbf37fe2f216972d00027d8931df45ba95e48002fee5a168a1353` |
| rebuild child | `5bc93975adff9cd78e5ac215ff13dba7726e925a6fe3e21a92670817062a58ed` |
| build contract | `fca15a585d928c17999fb606df06f5de370f20ea273f164485ed26dc8a57cdd6` |
| build-contract tests | `d5269ca57e9a5b4e386c9891aa6aa472850363fa72ab61ecc9744de13a47bc9d` |
| runtime-control tests | `8083ea75b0ddfe3939b9fad306bbb612ce0e95da7be40a9dc8ee10fe3a1d4392` |
| publication-security tests | `a854ada3588af9540a7e00a35d545d7092b3e66b6504676d317c5b6886668c64` |
| end-to-end tests | `5ce8de532124869eb7e88c55a5504db4d153222525cfa46eb897dc9232a4b83c` |
| schema v2 physical | `c760710eacbb6575b4af46b31ae5f69c1b16ef702d14630c84597a118a40911e` |
| product v2 physical | `465a2abf9e72eb25cc6717cfc656304ae9bb208e4ed0e08d54a46420e3db23ce` |

The corresponding no-LF schema/product body digests are
`a0daa1a22619bf2719ff67d1a22f4495a8de0ea8884f53bb5f05276c9b71ddc0`
and `a50dd67b5ab989c783d67cda3cc0fe15229b6991de342d74bbdc3c40a465c832`.

## Producer and independent proof

The frozen producer evidence passes the complete runtime-control unit population
(`287`), companion contract/security/end-to-end population (`95`), all four
previously failing real-admission regressions, post-format affected population
(`85`), Ruff format/lint and mypy. The retained failed attempts and the interim
two-pass/two-fail directory discovery remain visible.

The terminal independent review reconstructed every fixed binding, both denial
paths and the aggregate graph, then passed eight-file format/lint/mypy, the
67-case terminal foreign-cache/process selection, the complete 17-case aggregate
contract file, diff-check and zero-remotes check. It returned `PASS`,
`P0/P1/P2 = 0/0/0` and reproduced none of the controlling blocker classes.

## Preservation and disposition

The failed-gate pre/post preservation evidence remains exact: selected-site PYC
`1218` rows / `bd0b8036ffff7542a4216db800622c9379e953d7cbd38b45ab464636ca4001dd`,
repository PYC `133` rows /
`d3f27229f8b43fd3fc1aba948462b6fb8a872790f4def522e494090ff444ff8d`,
and retained `data/**` plus `runs/**` `272` rows /
`c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`.

No dependency/lock, provider/network, credential, container/cloud, deployment,
publication, destructive filesystem, retained product/manifest/receipt/data/run,
or Git mutation occurred in producer or independent review. R12 is accepted and
releases only the single master-owned complete-repository/W04 phase gate,
followed by required health readback, registry reconciliation and checkpoint.
