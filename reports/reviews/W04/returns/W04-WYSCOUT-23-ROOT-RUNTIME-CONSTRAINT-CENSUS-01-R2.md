# Subagent return

## Task

- task_id: `W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R2`
- objective: Reissue the complete runtime-constraint census while correcting only the R1 `CanonicalJsonValue` projection-path error and preserving R1 bytes as superseded evidence.

## Files changed

- `reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R2.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R2.md`

## Summary

- Reproduced all six R2 packet-fixed bindings before analysis.
- Preserved the R1 report and return bytes unchanged and explicitly marked R2 as superseding R1 only for `CanonicalJsonValue` projection paths.
- Reissued the complete census with every present field declared as `CanonicalJsonValue` or a concrete arm represented as one complete non-null `CANONICAL_JSON_VALUE_UTF8` scalar.
- Corrected the complete Parquet-root occurrence roster to the four direct paths: `BronzeKnownRecord.raw_record`, `BronzeRejectedRecord.raw_record`, `BronzeRejectedRecord.raw_kind.value`, and `BronzeRejectedField.original_value`.
- Removed the erroneous recursive Arrow paths and list claims beneath both `raw_record` fields. Their discriminators, member tuples, nested variants and arrays/objects remain inside the tagged logical JSON text; the seven-arm closure remains only the strict inverse-validation authority.
- Retained separate outer optionality and the rule that present tagged canonical null is non-null UTF-8 text.
- Did not inspect the schema producer candidate or change any logical model, accepted projection, root, dependency, semantic rule, physical rule, product or aggregate.

## Tests run

- command: `shasum -a 256 orchestration/task_packets/W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R1.yaml reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R1.md reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R1.md reports/reviews/W04/authorities/wyscout-logical-arrow-projection-decisions-v1.json src/scouting/storage/formats.py tests/unit/test_w04_wyscout_product_formats.py reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R2.md`
  - exit status: `0`
  - result: all six frozen inputs reproduced their packet bindings; the pre-return R2 census SHA-256 was `3ac167f4a63f26d930abe039ec7417637d204f984db6f0cc578dd322526c2120`.
- command: `uv run python scripts/verify_local_only.py` in the default sandbox
  - exit status: `2`
  - result: uv could not read its existing external cache path, reporting `Operation not permitted`; no repository check ran and no file was changed by this attempt.
- command: `uv run python scripts/verify_local_only.py` with approved read access to the existing uv cache
  - exit status: `0`
  - result: `PASS`, 25 checks and zero failures; zero configured remotes and the container-free/local-only boundary retained.
- command: final `shasum -a 256` over all six fixed inputs and both R2 outputs
  - exit status: recorded in the handback after this return was materialized
  - result: recorded in the handback; the return cannot contain its own content digest without self-reference.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R2.md`
- `reports/reviews/W04/returns/W04-WYSCOUT-23-ROOT-RUNTIME-CONSTRAINT-CENSUS-01-R2.md`
- Preserved superseded evidence: `reports/reviews/W04/wyscout-23-root-runtime-constraint-census-R1.md`

## Risks

- The correction is an implementation-independent oracle only. It does not review or approve the separately produced schema candidate.
- Tagged text intentionally leaves nested canonical JSON opaque to Parquet predicates; this is the already accepted deterministic and reversible representation.
- Master must independently verify that no producer descriptor recursively decomposes the four corrected direct scalar paths.

## Follow-up items

- Master should independently reproduce the hashes and local-only check, compare the producer against this corrected R2 oracle, and return any remaining recursive projection path for bounded rework.

## Scope confirmation

- no Git operations: confirmed; no Git command was directly invoked. The required local-only verifier performed its own read-only remote/branch checks and guard simulation.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and `uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed; only the two R2 report paths were created.
