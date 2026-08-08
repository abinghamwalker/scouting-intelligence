# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R21-R2`
- objective: Correct only the six bounded R21 R1 master-review defects,
  preserve every accepted R1 closure and the original R1 return, and return the
  revised design for fresh independent R14 review and master acceptance.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R21.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21-R2.md`

## Summary

- Replaced the incorrect lexical field-row ordering with the exact immutable
  R20 source-profile roster sequence: `competition`, `team`, `player`, `match`,
  `action`, `event-taxonomy`, and `tag-taxonomy`, with each kind retaining its
  declared profile order.
- Put all seventeen closed `prior_authority` keys, including both embedded v1
  examples, in exact Unicode lexical order:
  `review_recommendation` precedes `review_record_sha256`. Added the required
  wrong-order negative case.
- Replaced the ambiguous preimage chain with the explicit acyclic branch
  `R20 -> R21 -> {product preimage, schema preimage}`. Both siblings converge
  on field v2, have no sibling dependency, and precede possession v2 and
  feature authority.
- Defined `r21_design_sha256` only as SHA-256 of the complete frozen physical
  R21 Markdown bytes. Canonical terminology remains confined to canonical
  JSON preimages and JSON/YAML candidates.
- Split the final combined scope into three serial, disjoint packets:
  `W04-R21-CROSS-AUTHORITY-TEST-01-R1`,
  `W04-R21-CROSS-AUTHORITY-REVIEW-01-R1`, and
  `W04-R21-CROSS-AUTHORITY-GATE-01-R1`. Fixed the independent review ID/path,
  actor separation, digest bindings, dependencies, positive/negative
  validation, and master-only gate ownership. The review is control evidence
  and the runtime resource roster remains exactly 30.
- Enumerated all twelve exact `AGENTS.md` repository-gate commands in their
  required order, including Bandit, local guard check, phase verification,
  `git status --short`, and empty `git remote`, while retaining all additive
  R21 checks.
- Preserved the R20 binding, all v1 evidence, v2 supersession, strict
  integer-only/no-coercion action subevent mapping, rejected-string evidence,
  descriptor-only preimages, exact 15-feature roster, exact 30-resource roster,
  exact five dependencies, all unaffected packet paths, and the no-product
  boundary.
- This is bounded R2 rework of the original R1 producer candidate. It does not
  replace, modify, or self-approve the R1 return.

## Tests run

- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c "<exact packet acceptance assertions>"`
  - exit status: `0`
  - result: `PASS`; the forbidden lexical field-sort sentence and forbidden
    Markdown digest phrase are absent; all three cross-authority packet IDs and
    required repository-gate commands are present; and
    `review_recommendation` precedes `review_record_sha256`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; all 25 local-only and one-root-uv checks passed, including
    zero Git remotes, active push guard, Python 3.12.12, no hosted CI,
    deployment, container definition, or external service dependency.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c "<six-defect mechanical closure assertions>"`
  - exit status: `0`
  - result: `PASS`; prior-authority keys `17`, embedded examples `2`, final
    packets `3`, exact repository-gate commands `12`, and resource roster `30`.
- command:
  initial packet assertion invocation before the authoritative shell-safe rerun
  - exit status: `1`
  - result: not evidence; zsh interpreted Markdown backticks in a double-quoted
    `-c` argument before Python. It changed no repository file. The identical
    assertions were immediately rerun with a single-quoted shell argument and
    passed as recorded above.
- command:
  shell-only terminal full repository/site pyc inventory reconstruction and
  byte comparison with the preflight inventories
  - exit status: `0`
  - result: `PASS`; repository inventory remained byte-identical at 59 rows and
    SHA-256
    `a339bef860b00a51a9df5bcfa84540cd0ca91c19fd77ab63a80c38f77866745e`;
    site-packages inventory remained byte-identical at 1,086 rows and SHA-256
    `88bf87afd7c14b89ed6cb3fc29c535511beaa771167345efec3d8a13ea512fd3`.

## Artifacts/evidence

- corrected candidate:
  `reports/reviews/W04/wyscout-schema-design-R21.md`
  - bytes: `58986`
  - lines: `1242`
  - physical SHA-256:
    `08f64de257d32dafc0e47030025a22644acb1ab793e34a443bca34d18d154969`
- preserved immutable predecessor:
  `reports/reviews/W04/wyscout-schema-design-R20.md`
  - physical SHA-256:
    `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- preserved original R1 return:
  `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21.md`
  - bytes: `6692`
  - lines: `132`
  - physical SHA-256:
    `3d53c23e3028c635f75b303f67a9fc027a96b76ed030909cbfd7b5a7567bc545`
- preflight full-inventory evidence:
  `/tmp/w04_r21_design_producer_repo_pyc.preflight`
  - rows: `59`
  - inventory SHA-256:
    `a339bef860b00a51a9df5bcfa84540cd0ca91c19fd77ab63a80c38f77866745e`
- preflight full-inventory evidence:
  `/tmp/w04_r21_design_producer_site_pyc.preflight`
  - rows: `1086`
  - inventory SHA-256:
    `88bf87afd7c14b89ed6cb3fc29c535511beaa771167345efec3d8a13ea512fd3`

## Risks

- This R2 return is producer rework evidence, not independent review or master
  acceptance. Fresh independent R14 review and master readback remain mandatory.
- No Bronze, Silver, Gold, feature materialization, manifest, receipt, runtime,
  build, model, or product implementation is authorized by this correction.
- No broader architecture, root, dependency, rights, storage, local-only, or
  product change was required. No scoped stop condition was encountered.

## Follow-up items

- Dispatch fresh fixed independent review
  `W04-SCHEMA-DESIGN-REVIEW-01-R14` against the corrected physical R21 bytes.
- After a passing independent review, require independent master readback and
  acceptance before any R21 implementation packet starts.

## Scope confirmation

- no Git operations: confirmed; no Git command or Git state mutation was
  performed. The packet-required local-only verifier inspected Git safety
  read-only.
- no unauthorised dependency or lockfile changes: confirmed; all Python commands
  used only `uv run --locked --no-sync`.
- no edits outside `allowed_paths`: confirmed; only the R21 design and this new
  R2 return were modified. The original R1 return was preserved byte-identically.
