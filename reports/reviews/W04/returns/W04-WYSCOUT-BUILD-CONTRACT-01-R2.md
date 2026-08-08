# Subagent return

## Task

- task_id: `W04-WYSCOUT-BUILD-CONTRACT-01-R2`
- objective: Correct only the R1 v15 admission component/proof binding, exact Gold
  competition path, and composed all-three-manifest/parent/Gold receipt closure.

## Files changed

- `src/scouting/contracts/wyscout_build.py`
- `tests/contracts/test_w04_wyscout_build_contract.py`
- `reports/reviews/W04/returns/W04-WYSCOUT-BUILD-CONTRACT-01-R2.md`

## Summary

- Preserved the R1 evidence return byte-identically at SHA-256
  `3d6b6f017d1974620024bd32507b600340b65ef16f3c6a75aab738acbe3cd5c8`.
- Bound the independent frozen-authority interpretation at
  `reports/reviews/W04/returns/W04-BUILD-CONTRACT-R2-AUTHORITY-AUDIT-01-R1.md`,
  SHA-256 `393113a0f7c06e876c20518a4dc8f7a0a3a016a33127e045a1f48fcf3925ea91`,
  verdict `PASS_TO_IMPLEMENT`. The audit is read-only authority interpretation,
  not candidate approval.
- Closed decoded `w04-code-environment-admission-v15` bytes to the exact 23 lexical
  top-level fields: the fixed twenty component values plus `environment_digest`,
  `repository_code_sha256`, and `schema_version`, with no wrapper or operational
  field.
- Recomputes `environment_digest` from the exact 20-key canonical component object;
  requires exact accepted `uv 0.9.21 (Homebrew 2025-12-30)`, a nonempty canonical
  selector object, and lowercase SHA-256 for the other eighteen component values.
- Recomputes each of the twenty proof value digests from the corresponding decoded
  manifest component and recomputes the exact proof-array digest. The separate pure
  `validate_admission_component_authority` seam compares the decoded components to
  independently retained exact component authority and compares every proof count
  to an independently recounted ordered 20-key count roster. Counts are strict
  non-Boolean integers in `1..10_000_000`; they are not inferred from components or
  copied from proof claims.
- Replaced the generic competition UUIDv5 Gold-path segment with only
  `cb5c5317-fa4a-571e-93dc-ef6ce482eab7`. The former R1 fixture and every other
  competition UUID fail.
- Extended pure receipt closure to consume exactly three complete physical manifest
  byte streams and their corresponding already closed-schema-validated complete
  parsed objects in Bronze/Silver/Gold order. It reproduces canonical JSON plus one
  terminal LF, exact parsed-object equality, physical digest/size, layer/build/path/
  completion, all frozen source/index/tenant/rights/clock/authority/feature/lineage
  bindings, and the same sole R4 two-key whole-manifest semantic digest.
- Reconciles exact Bronze empty parents, Silver-to-Bronze physical parent, and
  Gold-to-Silver physical parent only after all three manifests pass. It then derives
  the one-entry `GOLD_PLAYER_WINDOW` population in manifest order and requires exact
  equality with the boundary summary and receipt, including exact path, manifest,
  product physical/semantic, row-count, lineage, proof, build/run, and interval
  bindings. There is no sort, filter, deduplication, witness, fallback, or recovery.
- Preserved the exact five-window, bounded season, five-authority, five-dependency,
  25/25 one-hash inverse, 15/9 receipt, and eight result-root field rosters. No ninth
  result role, schema root, aggregate, materializer, writer, dependency, or public
  export was added.

## Tests run

- command: `uv run ruff format --check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/contracts/wyscout_build.py tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py`
  - exit status: `0`
  - result: `38 passed in 0.32s`
- command: `uv run pytest -q tests/contracts/test_w04_wyscout_build_contract.py tests/contracts/test_w04_wyscout_build_product_authority.py tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py`
  - exit status: `0`
  - result: `199 passed in 3.99s`
- command: standalone/data-contract dependency-lineage cross-reproduction through
  `uv run python -c`
  - exit status: `0`
  - result: both implementations reproduced
    `ded9ae0a3bece552eb047e005809837871a0ccd2cf76ead47e33abcb9288ea9d`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 checks, zero failures, zero Git remotes, local `main`, one
    root uv project/lock/venv, Python 3.12.12, and no cloud, hosted CI, deployment,
    container, endpoint, or external-service boundary.

## Artifacts/evidence

- `src/scouting/contracts/wyscout_build.py`
  - R2 producer-observed SHA-256:
    `ed7345a8bddbfcb0b26deef57fba09726ce05691e553e1fc1166308e449b06dd`
- `tests/contracts/test_w04_wyscout_build_contract.py`
  - R2 producer-observed SHA-256:
    `9a6446a441ebc8a625395418c0c914a76f980c43fe7e17bd2b40294db95fd1ec`
- `reports/reviews/W04/returns/W04-BUILD-CONTRACT-R2-AUTHORITY-AUDIT-01-R1.md`
  - bound read-only SHA-256:
    `393113a0f7c06e876c20518a4dc8f7a0a3a016a33127e045a1f48fcf3925ea91`
- Adversarial coverage includes every one of the twenty component values, every
  proof digest and count position, proof order, exact 23-field omission/addition/
  stale/operational inputs, all three physical/semantic summaries and readbacks,
  each manifest binding, each parent field/cardinality, Gold role/path/cardinality/
  product value, former competition UUID, and downstream receipt/child rehash.

## Risks

- Receipt composition deliberately consumes parsed manifest objects only after the
  accepted complete closed v2 `LAYER_MANIFEST` schema has validated them. It repeats
  all build/authority/physical/semantic/parent/population equalities but does not
  define a second LayerManifest schema. Downstream callers must preserve that
  validation order.
- The selector's internal runtime value and component evidence counts are not frozen
  fixture guesses. They are compared through the explicit independent authority/
  recount seam; the result cannot authorize its own submitted values or counts.
- This producer return is evidence only, not independent review or self-acceptance.

## Follow-up items

- Master must independently inspect the R2 candidate and tests, rerun the complete
  acceptance suite, and dispatch a fresh candidate reviewer. Only a zero-finding
  independent `PASS` plus master acceptance may release the next packet.

## Scope confirmation

- no Git operations: confirmed; none performed
- no unauthorised dependency or lockfile changes: confirmed; none performed
- no edits outside `allowed_paths`: confirmed; only the two R2 candidate paths and
  this new R2 return were changed
- no product/control/data/run writes or provider/network/external action: confirmed
