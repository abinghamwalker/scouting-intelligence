# Subagent return

## Task

- task_id: `W09-FULL-CANONICAL-BUILD-02B-R2`
- objective: Resolve the master review findings on rights authority, strict-before
  temporal semantics, retained output roots, action-file TOCTOU protection and evidence
  wording without expanding the accepted R1 packet scope.

## Files changed

- `src/scouting/sources/wyscout_historical.py`
- `src/scouting/data_products/wyscout/historical.py`
- `scripts/build_w09_historical_canonical.py`
- `tests/unit/test_w09_wyscout_historical_adapter.py`
- `tests/integration/test_w09_full_canonical_build.py`
- `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R2.md`

## Summary

- Corrected `RIGHTS_CLASSIFICATION` to the exact accepted authority ID
  `wyscout_figshare_v5_cc_by_4`. Project restrictions remain separate manifest and
  guarded-storage retention fields: `local_only=true` and
  `raw_export_allowed=false`.
- Changed temporal admission to strict-before semantics. Source availability, identity
  availability and every selected match time must be strictly less than the feature
  cutoff; equality now fails closed. Added distinct equality-at-cutoff adversarial tests
  for source authority, identity authority and match time.
- Added canonical production output roots:
  `data/working/wyscout/v5/research` and
  `data/manifests/wyscout/v5/research`. A retained/non-fixture adapter rejects any other
  output root before adapter verification, directory creation or artifact write.
  Temporary roots remain available only through the explicit automated-test fixture
  adapter.
- Closed the action-file TOCTOU gap by binding no-follow regular-file fingerprints
  (`device`, `inode`, `mode`, link count, size and nanosecond mtime) for every exact
  admitted action payload immediately after source/completion authority verification.
  The adapter rechecks each fingerprint before and after partition iteration and rechecks
  all five before and after the retained population audit. Missing, linked, replaced or
  changed action payloads fail closed. An adversarial unit test mutates a bound file and
  proves rejection.
- Retained the exact-path rule: DuckDB receives only the five admitted action payload
  paths, with no glob and no manifest sidecars. The read-only production smoke still
  reconciles 3,071,395 unique actions, 226,038 zero actors and match partitions
  380/380/306/380/380 under the new fingerprint boundary.
- Corrected the R1 performance wording. Projection dictionaries are bounded to one
  65,536-row input batch, but the resulting Arrow RecordBatches are accumulated for one
  league partition before that partition is serialized. The builder does not accumulate
  dictionaries or RecordBatches across all five partitions simultaneously.

## Tests run

- command: `uv run ruff format --check src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`
  - result: PASS; all five implementation/test files are formatted.
- command: `uv run ruff check src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`
  - result: PASS; no lint findings.
- command: `uv run mypy src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py`
  - exit status: `0`
  - result: PASS; no issues in three source files.
- command: `uv run pytest -q tests/unit/test_w09_wyscout_historical_adapter.py tests/integration/test_w09_full_canonical_build.py`
  - exit status: `0`
  - result: PASS; 12 tests passed. R2 additions cover the exact rights ID; source,
    identity and match equality at cutoff; alternate retained output roots before
    verification/write; and post-verification action-file mutation.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py`
  - exit status: `0`
  - result: PASS; no security findings.
- command: `uv run python -c 'from scouting.sources.wyscout_historical import WyscoutHistoricalAdapter; a=WyscoutHistoricalAdapter.retained().verify().audit_action_population(); print(a.action_count,a.unique_action_count,a.zero_actor_action_count,{k:len(v) for k,v in a.match_ids_by_partition.items()},flush=True)'`
  - exit status: `0`
  - result: READ-ONLY PASS; output was `3071395 3071395 226038 {'England': 380,
    'France': 380, 'Germany': 306, 'Italy': 380, 'Spain': 380}`. Fingerprints were
    checked before and after the audit; no canonical artifact was generated.

## Artifacts/evidence

- Accepted rights authority: `wyscout_figshare_v5_cc_by_4`.
- Source manifest authority:
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b` /
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`.
- Completion authority:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- Identity authority:
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`.
- R2 handback:
  `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R2.md`.
- No final full canonical artifact was generated during this rework.

## Risks

- Fingerprints detect normal file replacement, mutation, permission/link-count change and
  path substitution around DuckDB reads. They are a local immutable-snapshot control,
  not a defence against a privileged actor deliberately restoring every inode metadata
  field after byte tampering. The exact manifest SHA is still independently reverified at
  adapter construction.
- One league partition's Arrow RecordBatches are accumulated before Parquet serialization;
  peak build memory therefore depends on the largest admitted league, not a single batch.
  It does not depend on all 3,071,395 projected dictionaries at once.
- Terminal exposure without an observed player exit remains a conservative lower bound;
  downstream eligibility must retain that state rather than promote it to exact minutes.
- The full canonical materialization remains intentionally unexecuted under this packet's
  stop condition. Master execution must reconcile its physical artifacts before G-RW1.

## Follow-up items

- Master: independently inspect R2, rerun the exact static/test/Bandit checks and retained
  read-only smoke, then execute the accepted builder only at the two canonical production
  roots and reconcile the generated manifest.

## Scope confirmation

- stop conditions: none triggered; retained rights/source/completion/identity authorities
  remained coherent and no external access or product decision was required.
- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor
  `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; R2 touched only the five original code/test
  paths and this newly authorised R2 return report.
