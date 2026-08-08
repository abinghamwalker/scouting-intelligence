# Subagent return

## Task

- task_id: `W09-FULL-CANONICAL-BUILD-02B`
- objective: Build a deterministic local-only adapter and full canonical Parquet
  projection for all five retained Wyscout 2017/18 partitions without changing the
  accepted W04 proof paths.

## Files changed

- `src/scouting/sources/wyscout_historical.py`
- `src/scouting/data_products/wyscout/historical.py`
- `scripts/build_w09_historical_canonical.py`
- `tests/unit/test_w09_wyscout_historical_adapter.py`
- `tests/integration/test_w09_full_canonical_build.py`
- `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R1.md`

## Summary

- Added an exact production adapter that accepts only the retained source, manifest and
  identity roots; revalidates the frozen source manifest and its 18 payloads; validates
  the accepted completion index and exact five payload paths; validates the accepted
  91 MB identity bundle; and refuses to yield rows until those authorities agree.
- The adapter never globs event paths and never includes `.manifest.json` sidecars. Its
  population audit uses DuckDB over the explicit five-path list and reconciles
  3,071,395 unique actions, 226,038 zero-actor rows and partition match sets of
  380/380/306/380/380.
- Added a deterministic canonical producer for competitions, teams, players, matches,
  partitioned actions, appearances/minute evidence and identity exclusions. All
  provider identities used by candidates are accepted canonical UUIDs; the 15 open
  absent-master player IDs and `player:0` are retained only as non-candidate audit rows.
- Historical team membership comes only from match `teamsData`/formation evidence.
  `currentTeamId` is deliberately absent from the player projection and never used as a
  join.
- Minute evidence has three visible states: `exact` for observed entry/exit boundaries,
  `conservative_lower_bound` for observed entry through the greater of the explicit
  regular-duration floor and final event clock, and `unusable` for bench evidence
  without entry. No action/appearance proxy, imputation or exact-90 assertion is made.
- Artifacts are written immutably through guarded storage beneath
  `build_id=<authority-and-code-digest>/canonical/`. The canonical manifest binds
  rights/attribution, source/completion/identity authority and clocks, source and
  canonical counts, identity and minute audits, exact partition paths/hashes/counts,
  every artifact path/row count/schema/physical SHA-256, code digest and limitations.
- The fixture-only construction boundary is explicit (`from_test_fixture`) and is never
  selected by production construction. The build manifest marks that path, while the
  production adapter has no synthetic fallback.
- Action projection is bounded by 65,536-row Arrow batches rather than retaining all
  3,071,395 projected action dictionaries in memory at once.

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
  - result: PASS; 8 tests passed. Coverage includes exact recorded constants, exact
    admitted paths, authority-before-read, identity exclusions, duplicate actions,
    event/match alignment, deterministic two-root builds, temporal cutoff rejection,
    three minute states, guarded root rejection and W04 sentinel preservation.
- command: `uv run bandit -q -r src/scouting/sources/wyscout_historical.py src/scouting/data_products/wyscout/historical.py scripts/build_w09_historical_canonical.py`
  - exit status: `0`
  - result: PASS; no security findings. The initial inherited-suite B101 observation was
    resolved by replacing the fixture assertion with an explicit fail-closed runtime
    check.
- command: `uv run python -c 'from scouting.sources.wyscout_historical import WyscoutHistoricalAdapter; a=WyscoutHistoricalAdapter.retained().verify().audit_action_population(); print(a.action_count,a.unique_action_count,a.zero_actor_action_count,{k:len(v) for k,v in a.match_ids_by_partition.items()},flush=True)'`
  - exit status: `0`
  - result: READ-ONLY PASS; output was `3071395 3071395 226038 {'England': 380,
    'France': 380, 'Germany': 306, 'Italy': 380, 'Spain': 380}`. No canonical artifact
    was generated by this smoke check.

The first combined post-edit verification attempt exited `2` before executing any check
because sandboxed `uv` could not read the existing external cache path
`/Users/adrian/.cache/uv/sdists-v9/.git`. The same commands were rerun with read access to
the existing cache and passed as recorded above.

## Artifacts/evidence

- Adapter authority: source manifest
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b` /
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`.
- Completion authority:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
- Identity authority:
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`.
- Implementation evidence: the five code/test paths listed above.
- Handback evidence:
  `reports/reviews/W09/returns/W09-FULL-CANONICAL-BUILD-02B-R1.md`.
- No final full canonical artifact was generated in this packet, as required. The master
  must execute the accepted builder and reconcile the emitted manifest before G-RW1.

## Risks

- The exact retained identity bundle validation is intentionally strict and took roughly
  50 seconds in the read-only production smoke. This is build-time validation, not a web
  or serving dependency.
- Regular-match terminal exposure without an observed exit remains a conservative lower
  bound. The downstream eligibility policy must decide whether and how that state can
  qualify; this packet does not silently promote it to exact minutes.
- The full canonical materialization has not been run here by packet constraint. Physical
  artifact size/performance and final population/minute histograms therefore remain for
  master execution and reconciliation.
- The canonical layer establishes governed engineering evidence only. It supplies no
  football-relevance, recruitment-usefulness or current-market claim.

## Follow-up items

- Master: independently inspect the six changed files, rerun every named check, execute
  `scripts/build_w09_historical_canonical.py` over the retained roots, and reconcile all
  emitted counts/checksums before accepting this packet or dispatching the feature-matrix
  consumer.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor
  `uv.lock` was edited.
- no edits outside `allowed_paths`: confirmed; the exact changed-file list contains only
  the six packet-authorised paths above.
