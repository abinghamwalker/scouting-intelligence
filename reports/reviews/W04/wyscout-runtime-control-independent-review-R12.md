# W04 Wyscout runtime-control terminal independent review R12

- Date: `2026-08-03`
- Producer task: `W04-WYSCOUT-RUNTIME-CONTROL-01-R12`
- Review task: `W04-WYSCOUT-RUNTIME-CONTROL-REVIEW-01-R12`
- Decision: **PASS**
- Findings: `P0/P1/P2 = 0/0/0`
- Disposition: `TERMINAL_R12_REVIEW_PASS_FOR_MASTER_ACCEPTANCE`

## Review boundary

This is the one terminal independent R12 review required by the controlling
W04 closure steer. I applied the five blocker tests in
`reports/verification/W04/w04-closure-steer-2026-08-03.md` and did not open or
request R13 or another W04 runtime authority. Accepted runtime R11 and retained
real-root R3 are the minimum operational baseline. The master, not this review,
owns the one remaining complete-repository/W04 phase gate, health readback,
registry reconciliation and checkpoint sequence.

The frozen review packet SHA-256 is
`92b7e265793bbfe72c04ea5daa911f447e4d83e9cde267db27404974abd6fcaf`.
The frozen producer packet and return SHA-256 values reproduce as
`35281e769533fed6b042c66c7d6d0c8a87a4916a459c1ffd2d4847b2d8a26e9a`
and
`7d71f33382f1ae5433def1741c446da59524448d82344bfbdc9ce70d6b109774`.
Every other fixed review binding reproduced exactly, including the closure steer,
W10 backlog, R11 acceptance, real-root R3 acceptance, both bounded-correction
authorities and the master-derived aggregate verification.

## Frozen candidate identities

| Artifact | SHA-256 |
| --- | --- |
| `scripts/admit_wyscout_v5_runtime.py` | `db6ffbada5e271310b2b2495b264475d0ace27dfe0e4a0b35077a471fbde5be0` |
| `scripts/launch_wyscout_v5.py` | `827714c8baefbf37fe2f216972d00027d8931df45ba95e48002fee5a168a1353` |
| `scripts/rebuild_wyscout_v5.py` | `5bc93975adff9cd78e5ac215ff13dba7726e925a6fe3e21a92670817062a58ed` |
| `src/scouting/contracts/wyscout_build.py` | `fca15a585d928c17999fb606df06f5de370f20ea273f164485ed26dc8a57cdd6` |
| `tests/contracts/test_w04_wyscout_build_contract.py` | `d5269ca57e9a5b4e386c9891aa6aa472850363fa72ab61ecc9744de13a47bc9d` |
| `tests/unit/test_w04_wyscout_runtime_control.py` | `8083ea75b0ddfe3939b9fad306bbb612ce0e95da7be40a9dc8ee10fe3a1d4392` |
| `tests/security/test_w04_wyscout_vertical_slice_publication.py` | `a854ada3588af9540a7e00a35d545d7092b3e66b6504676d317c5b6886668c64` |
| `tests/e2e/test_w04_wyscout_vertical_slice.py` | `5ce8de532124869eb7e88c55a5504db4d153222525cfa46eb897dc9232a4b83c` |

## Exact foreign-cache denial

Both independently implemented collectors bind one and only one foreign-cache
predicate:

- path
  `scripts/__pycache__/admit_wyscout_v5_runtime.cpython-314.pyc`;
- `WHOLE_REPOSITORY` traversal role, `cpython-314` tag, mode `0644`, link
  count `1` and size `190312`;
- class `REPOSITORY_FOREIGN_CACHE_TAG_DENIED`; and
- policy `FOREIGN_INTERPRETER_TAG_DENIED_ZERO_READ`.

The admission collector constructs its own exact predicate; the launcher
reconstructs the same predicate independently. Each collector accepts the
retained file only after contained no-follow `lstat` classification. Neither
collector opens, reads, hashes, parses a header or magic value, imports, executes,
repairs, renames, deletes or otherwise mutates the PYC. The incident digest does
not occur in either implementation or emitted row.

The required source is a separate prerequisite: one exact seven-field
`REPOSITORY_CODE_MANIFEST` row for
`scripts/admit_wyscout_v5_runtime.py`, with exact owner/path, normal and pytest
cache-name forms, SHA-256 shape and size, plus singular regular no-follow mode
`0644` metadata. The denied PYC row has `source_authority=None`, no owner and no
digest. Its `source_authority_required` value describes the prerequisite and
does not grant the PYC source, owner, component, environment, build, schema,
product, roster, import or execution authority.

The dual-collector matrix rejects substituted or missing predicate fields,
duplicate predicate, path escape, wrong path/tag/role/class/policy/mode/size,
missing or malformed source authority, wrong source owner/class/path/digest
shape/size/mode, duplicate source, source symlink/hardlink, missing denied file,
additional foreign tag, denied-file symlink/hardlink and attempted open/read/use.
The exact terminal review selection passed `67 passed, 220 deselected in 0.27s`.
Static inspection also confirms both collector bodies contain no PYC read/hash or
magic/header path.

I inspected the retained incident file by `lstat` only. It remains the same
regular mode-`0644`, link-count-`1`, size-`190312` object with the same retained
device, inode and timestamps observed before review. I did not open, read or hash
it.

## Mechanical v2 aggregate correction

The unchanged accepted v1 inputs reproduce as:

- schema v1: `a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`;
- product v1: `0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`.

The accepted builders reconstruct the serial schema-then-product v2 graph with
the exact existing key order, 23 ordered roots, earlier-only dependency DAG,
constant corpus, completion binding, publication order and receipt composition.
The regenerated identities reproduce as:

| Preimage | Canonical body SHA-256 | Physical SHA-256 |
| --- | --- | --- |
| schema v2 | `a0daa1a22619bf2719ff67d1a22f4495a8de0ea8884f53bb5f05276c9b71ddc0` | `c760710eacbb6575b4af46b31ae5f69c1b16ef702d14630c84597a118a40911e` |
| product v2 | `a50dd67b5ab989c783d67cda3cc0fe15229b6991de342d74bbdc3c40a465c832` | `465a2abf9e72eb25cc6717cfc656304ae9bb208e4ed0e08d54a46420e3db23ce` |

The product binds the exact schema body digest. The same two body values are
frozen in the launcher and runtime tests. Exactly the four R12 physical result
descriptor content hashes changed from the earlier descriptor bytes;
the other 19 root hashes, roster and edges remain unchanged. The 17-case
aggregate contract population was collected and the complete file exited `0`,
including exact physical-byte reconstruction, all root-content/edge checks and
adversarial missing/reordered/substituted/self-digest cases.

No logical schema, root roster, source or rights authority, feature/product
population, intended output, aggregate algorithm, key order, DAG or digest
meaning/formula changed.

## Darwin prefix-directory physical correction

The real preparation regressions advanced beyond the original foreign-PYC
failure and demonstrated that the empty mode-`0700` Darwin runtime prefix is a
directory with exact `st_nlink=2`. R12 corrects only the stale file-style
validator constant.

The launcher still captures exact device, inode, full mode and link count before
the child, requires the prefix empty before execution, and requires byte-identical
identity and emptiness after execution. Process evidence validation retains the
exact argv/environment, entrypoint descriptor, result descriptor, frame, nonce,
payload, exit `0`, timeout, diagnostic-empty and cross-field bindings. It now
requires directory link count `2`; a coherent observation and retained-fact
substitution to `1` is rejected. The terminal focused selection includes and
passes that adversarial case.

This is a bounded correction of an observed physical fact. It neither weakens
process evidence nor changes execution or product behaviour.

## Controlling blocker adjudication

1. **Executable or authority substitution:** not reproduced. Executable,
   source, owner, installed-record, loaded-runtime subset and predicate identities
   remain exact and fail closed; the foreign PYC receives denial only.
2. **Incorrect product, manifest, receipt or digest bytes:** not reproduced.
   Both aggregates reproduce exactly, product-to-schema binding is exact, and the
   accepted R11/R3 product/manifest/receipt baseline is unchanged.
3. **Completeness, rights, temporal or local-only bypass:** not reproduced. R12
   changes no such authority or algorithm, and `git remote` remains empty.
4. **False success after failed execution:** not reproduced. Exit, timeout,
   frame, descriptors, diagnostics, prefix identity and cross-field evidence all
   remain mandatory and adversarially checked.
5. **Reproducible P0/P1 exploit:** none found in code inspection or the complete
   focused adversarial matrix.

The six demonstrated complete-gate failures are closed by the exact bounded
corrections above. The previously failed gate remains visible as `507 passed,
6 failed in 1561.85s`; its pre/post inventories remain fixed at selected-site
PYC `1218` / `bd0b8036ffff7542a4216db800622c9379e953d7cbd38b45ab464636ca4001dd`,
repository PYC `133` /
`d3f27229f8b43fd3fc1aba948462b6fb8a872790f4def522e494090ff444ff8d`,
and retained `data/**` plus `runs/**` `272` /
`c7edcc0341628b7224069cf4fc3cf3f1ef3bce4994f5bcf2ece904c313b1627c`.

## Independent checks

- Ruff format check: `8 files already formatted`, exit `0`.
- Ruff lint: `All checks passed!`, exit `0`.
- mypy with review cache under `/private/tmp`: `Success: no issues found in 8
  source files`, exit `0`.
- terminal foreign-cache/prefix-evidence selection: `67 passed, 220 deselected
  in 0.27s`, exit `0`.
- complete 17-case aggregate contract file: exit `0`.
- `git diff --check`: exit `0`.
- `git remote`: empty.

The producer additionally passed the complete runtime unit population (`287
passed`), the companion build/security/e2e population (`95 passed`), all four
real-admission regressions after bounded rework, and the smallest affected
post-format population (`85 passed`). Mechanical formatting was followed by
fresh static and affected dynamic checks on the frozen hashes.

## Residual risk and W10 backlog

No W04-blocking risk remains. Portable treatment of unrelated host PYC state and
cross-filesystem directory link-count/inode/timestamp variation is explicitly
retained as non-blocking W10 work in
`reports/verification/W04/w10-deferred-runtime-host-state-hardening-backlog-R1.md`.
It grants no authority and is not an R12/W04 acceptance dependency.

## Verdict

**PASS.** `P0/P1/P2 = 0/0/0`. The frozen R12 candidate closes the six
demonstrated failures without crossing a logical, product, rights, temporal,
digest-meaning, local-only or evidence boundary. It is ready for master R12
acceptance and the single master-owned complete-repository/W04 closure gate. No
R13 or additional W04 runtime-control revision is requested.
