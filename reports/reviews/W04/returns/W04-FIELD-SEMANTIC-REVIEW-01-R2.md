# Subagent return

## Task

- task_id: `W04-FIELD-SEMANTIC-REVIEW-01-R2`
- objective: Produce truthful evidence for the already complete zero-finding
  independent field-semantic review from a new actual post-incident pyc
  baseline, without changing the review, candidate, test, or implementation.
- outcome: `PASS`
- semantic review recommendation/findings: `PASS`, zero findings
  (`P0=0`, `P1=0`, `P2=0`)

## Files changed

- `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R2.md`

## Summary

- This is evidence-only rework. The valid R1 independent review, frozen
  decision, registry, contract test, implementation, configuration, source
  data, and inaccurate historical R1 return were all treated as read-only.
- The R1 terminal inventory did **not** pass. Its repository state changed from
  58 to 59 pycs: the focused contract pytest-rewrite pyc was created and the
  existing `verify_local_only` pyc changed. The R1 return incorrectly records
  terminal exit `0` and six identical comparisons; the actual exit was `1`.
  This R2 return corrects that evidence and makes no claim that R1 passed.
- R2 started from a new, actual, complete baseline containing the preserved
  post-incident state: 59 repository pycs and 1,086 site-packages pycs. No pyc
  was cleaned, deleted, repaired, regenerated for baseline purposes, or
  relabelled.
- Every preflight row was classified using shell-generated inventory evidence.
  All 1,145 pycs were regular files, mode `0644`, link count `1`, and CPython
  3.12 magic `cb0d0d0a`; no unsafe or unclassified row remained.
- Before any Python process, shell/Ruby verification reproduced all frozen
  physical/canonical hashes, the one exact canonical PASS/zero-findings review
  record, its independent ActorId, and absence of acceptance plus all 13
  downstream paths.
- All exact packet checks passed through the root uv environment with
  `--locked --no-sync`. Every Python launch used process-start
  `PYTHONDONTWRITEBYTECODE=1` and `python -B`; no bare `python` or `python3`
  helper was used.
- After this return was written, one exact shell-only postflight reproduced the
  same 59 repository and 1,086 site-packages rows. Repository/site complete,
  metadata, and content projections were all byte-for-byte identical to the
  actual R2 preflight.

## R1 evidence correction

- inaccurate R1 return:
  `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R1.md`
- current physical R1 return SHA-256:
  `a324e3e0972201d4cc32ba59d93f1cc7b6fe4b395aa985725ac4d90f57c1b284`
- actual R1 terminal result: exit `1`, repository `58 -> 59`;
  site-packages `1086 -> 1086` and identical.
- R1 repository changes preserved in the R2 baseline:
  - new
    `tests/contracts/__pycache__/test_wyscout_field_registry_authority.cpython-312-pytest-9.1.1.pyc`,
    size `95026`, SHA-256
    `cd5aaa7895728f9992008585841958377ad41cea0b78b8659c57b9677c06b217`;
  - changed
    `scripts/__pycache__/verify_local_only.cpython-312.pyc`, size `24014`,
    SHA-256
    `f2490301227b2a4ff82c4f0f606de53b146ded7f1eea14c3d34a8d169562125a`;
  - both have integer mtime `1785424745`.

## Tests run

- command: fresh shell-only complete pyc preflight over the repository (pruning
  `.git` and `.venv`) and exact
  `.venv/lib/python3.12/site-packages`
  - exit status: `0`
  - result: actual baseline `repository=59`, `site=1086`; all complete,
    metadata, and content projections recorded under
    `/tmp/w04-field-semantic-review-r2.YPMXut/pre`.
- command: first shell-only classification attempt over the preflight TSVs
  - exit status: `1`
  - result: reviewer evidence-helper glob incorrectly searched for an absolute
    `site-packages` segment after changing into site-packages, producing an
    empty RECORD-source list. No Python or repository write occurred; the
    preflight TSVs were unchanged.
- command: second shell-only classification attempt over the same preflight
  TSVs
  - exit status: `1`
  - result: repository classification completed, but a reviewer-helper
    assertion incorrectly expected `_virtualenv.py` to be absent. The source is
    present but is not distribution-RECORD-owned. No Python or repository write
    occurred; the preflight TSVs were unchanged.
- command: corrected shell-only row classification and RECORD provenance check
  - exit status: `0`
  - result: all 59 repository and 1,086 site rows classified; 5,761
    distribution-RECORD-owned Python sources reproduced; zero unsafe or
    unclassified rows.
- command: shell `shasum`/absence gate plus Ruby strict YAML/JSON canonical
  verifier, before Python
  - exit status: `0`
  - result: all frozen hashes exact; review canonical and PASS with zero
    findings; acceptance and all 13 downstream paths absent.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: `0`
  - result: `123 passed in 17.33s`.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25/25 local-only checks.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<strict review/canonical six-digest verifier>'`
  - exit status: `0`
  - result: exact review fence/body/keys/ActorId/recommendation, candidate
    canonical digest, and all six frozen digests passed.
- command: post-check shell frozen physical-hash and authority-absence gate
  - exit status: `0`
  - result: decision, registry, test, and review unchanged; acceptance and all
    13 downstream paths absent.
- command: one terminal shell-only complete inventory reproduction followed by
  six `cmp` comparisons against the actual R2 preflight
  - exit status: `0`
  - result: repository `59`, site `1086`; complete, metadata, and content TSVs
    all byte-for-byte identical.

## Artifacts/evidence

- sole owned return:
  `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R2.md`
- unchanged independent review:
  `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
- inventory evidence root:
  `/tmp/w04-field-semantic-review-r2.YPMXut`
- frozen decision physical SHA-256:
  `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999`
- frozen registry physical SHA-256:
  `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2`
- frozen registry canonical SHA-256:
  `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`
- frozen contract-test physical SHA-256:
  `d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3`
- unchanged review physical SHA-256:
  `e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861`
- unchanged canonical review-record SHA-256:
  `8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0`
- review size/count: `1299 bytes`, `14 lines`
- repository preflight and terminal:
  - rows: `59`
  - metadata SHA-256:
    `bcec75958666485026e6cc5f879e8d843903d498198bf8bb87f5a88a96b09c9c`
  - content SHA-256:
    `32ce178db2ecc3fcb044be1dee18777b1b8cb30400220bec0c128475a1d57680`
  - complete SHA-256:
    `35612b58fa05a5564c834755ca2e5a8e180af7bdeca8da5af90be4df7faab8a2`
- site-packages preflight and terminal:
  - rows: `1086`
  - metadata SHA-256:
    `3679170a0920f5655765024826177f001c675d9fc48fdc3910d7d50fb9e3d9bf`
  - content SHA-256:
    `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18`
  - complete SHA-256:
    `e55ec57dc8e8913885e31dafa207b46845092af43418388dc5f5a729780777b5`
- classification:
  - repository: `35 REPOSITORY_NORMAL`,
    `21 REPOSITORY_PYTEST_REWRITE`, `3 REPOSITORY_INERT_ORPHAN`;
  - site: `972 SITE_DISTRIBUTION_NORMAL`, `112 SITE_PYTEST_REWRITE`,
    `1 UV_BOOTSTRAP_NORMAL`, `1 SITE_SIX_OPTIONAL_INERT_ORPHAN`;
  - repository classification SHA-256:
    `8d6ab4d2a40cff696fa9bc68198ffbf96f5f67873346f5a97593d1cbb3759cba`;
  - site classification SHA-256:
    `145c8fff05f3719ec06170cc01d9867ea28868c59a38ab8719e84820e9fa3bf3`;
  - RECORD-owned Python-source list SHA-256:
    `3585e28a5842a8772326092f9bb61b5e702929850cd8587b07bd7875cb1baa2b`.
- authority state after checks: exact review present; acceptance and all 13
  downstream paths absent.

## Risks

- No semantic P0/P1/P2 finding exists in the independent review.
- R1 environment evidence remains historically failed and its return remains
  inaccurate; this R2 return corrects rather than rewrites that immutable
  history.
- This evidence PASS is not formal field acceptance and grants no downstream
  authority.

## Follow-up items

- Master must independently reproduce R2 evidence and decide acceptance under
  separate authority. No downstream work is authorized by this return.

## Scope confirmation

- no Git operations: confirmed; no direct Git command or Git mutation was run.
  The mandated local-only verifier performed only its documented read-only Git
  checks.
- no unauthorised dependency or lockfile changes: confirmed; no sync/install
  occurred and `pyproject.toml`/`uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed; the R2 return is the sole
  changed path for this packet.
- no review/candidate/test/prior-return edit: confirmed.
- no delegation or self-approval: confirmed.
- no bare Python helper: confirmed.
- no provider/network access or acceptance/downstream work: confirmed.
- no pyc cleanup, deletion, repair, or baseline coercion: confirmed.
