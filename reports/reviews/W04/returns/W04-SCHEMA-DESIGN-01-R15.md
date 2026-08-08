# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R15`
- objective: Retain every passing R14 closure while making build identity
  acyclic, aligning rebuild dependency rows exactly to `EvidenceDependency`, and
  correcting the R13/R14 acceptance lineage.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R15.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R15.md`

## Summary

- Carried the complete R14 standalone design forward without compressing its
  exact acyclic outer/child environment algorithms, reproduced uv
  input-to-Python transformation, 16/8/10 envelopes, 25-key rebuild invocation,
  immutable-manifest/build-ID/rebuild-prefix chronology, R13
  encoding-source/descriptor/race/result-v2 closures, three unchanged child/outer
  argv, 58/19 census and four optional orphan predicates, 35 executables, three
  aliases, three denied `.pth` classes, 17 resources, and all earlier source,
  rights, temporal, identity, product, path, gate, ownership, two-root, and ledger
  contracts.
- Replaced the recursive completed-invocation build preimage with the one exact
  `w04-wyscout-pre-build-projection-v1` algorithm. The closed projection has
  exactly 25 keys: one schema version plus the 24 stable invocation values. It is
  formed only after immutable code-manifest readback and excludes `build_id`,
  run IDs, actual prefix/receipt/layer paths, descriptor numbers, nonces, actual
  transport hashes, output evidence, and every other operational field.
- Defined one build-ID calculation:
  `SHA256(canonical_json(exact_pre_build_projection))`. Only after that hash
  exists may the launcher construct `w04-rebuild-invocation-v1` by replacing the
  projection schema key with the computed `build_id`, then render the operational
  run-bound envelope paths.
- Defined exact child recomputation: validate accepted immutable authorities,
  remove only invocation `build_id`, insert only the fixed projection schema
  version, retain the other 24 values, canonical-encode the same 25-key object,
  perform the same one SHA-256, and require equality with every invocation,
  enclosing, result, receipt, layer, product-path, and final-recheck build ID.
  Placeholders, recursion, fixed-point search, a second preimage, a second build
  algorithm, and a second build-ID hash are forbidden.
- Replaced the dependency aliases with the exact closed accepted
  `EvidenceDependency` wire object: only `kind`, `dependency_id`, `digest`,
  `observed_at`, and `available_at`, with the existing enum, strict UUID,
  lowercase SHA-256, and UTC types. The design retains exactly five rows, the
  Section 5 kinds/cardinality/sort, strict-before clocks, watermark, and lineage
  hash, and explicitly forbids `dependency_kind`, `manifest_id`, and
  `manifest_sha256`.
- Corrected lineage throughout: R13 and R14 both received master `REWORK`
  decisions. R15 retains their passing/master-reproduced closures and the
  returned independent R8 findings without calling either revision accepted.
- Advanced the admitted code/environment manifest schema to
  `w04-code-environment-admission-v12` so stable authority binds the projection
  and post-hash invocation schemas while excluding every completed projection or
  invocation instance.

## Tests run

- command:
  `uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-R15.md'); assert p.is_file() and p.stat().st_size > 26000"`
  - exit status: `0`
  - result: PASS; the R15 design exists and is 179,095 bytes.
- command: `uv run --locked --no-sync python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; validator status `PASS`, all 25 checks passed, and
    `failures: []`. Its Git checks were read-only.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R15.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R15.md`
- sole build algorithm: `w04-wyscout-pre-build-projection-v1`
- post-hash runtime invocation schema: `w04-rebuild-invocation-v1`
- accepted dependency schema: `EvidenceDependency`
- admitted code/environment schema: `w04-code-environment-admission-v12`

## Risks

- This is design evidence only. The three future scripts and their tests remain
  absent; feasibility and exact runtime observations still require the named
  implementation packets plus master and independent review.
- Stable aggregate digests content-address the closed nested authorities described
  by the design. Implementers must prove those readbacks and equality checks
  before projection construction; a digest string alone is not permission to skip
  the component verification.
- The same-trust-domain transient replacement residual retained from R13/R14
  remains explicit and unchanged; R15 does not claim an unavailable stronger
  observation.

## Follow-up items

- Master and independent reviewer should verify the exact projection key set,
  one-hash reconstruction, post-hash invocation insertion, literal
  `EvidenceDependency` rows, lineage wording, and retained R14 closures before
  accepting or dispatching implementation.

## Scope confirmation

- no Git operations: confirmed; no Git command or `.git/**` mutation was
  performed. The mandated local-only verifier performed only its documented
  read-only Git checks.
- no unauthorised dependency or lockfile changes: confirmed; neither
  `pyproject.toml` nor `uv.lock` was modified, and checks used
  `--locked --no-sync`.
- no edits outside `allowed_paths`: confirmed; exactly the two R15 report paths
  listed above were created/modified. No parent-workspace path, directory,
  implementation file, dependency, environment, provider/network resource, or
  cleanup obligation was created.
