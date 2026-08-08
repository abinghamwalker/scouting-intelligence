# Subagent return

## Task

- task_id: `W04-SOURCE-COMPLETION-INDEX-01-R1`
- objective: Derive an immutable, independently addressable completion index for all
  3,071,395 admitted Wyscout event rows; require exact source-population equality at
  the public period/match factory; bind the accepted index through W04 provenance and
  dependency lineage; and correct equal-clock group resolution and causal source-row
  closure.

## Files changed

- `src/scouting/sources/wyscout_completion_index.py`
- `src/scouting/contracts/wyscout_data.py`
- `tests/unit/test_wyscout_source_completion_index.py`
- `tests/contracts/test_wyscout_data_contracts.py`
- `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- `reports/reviews/W04/returns/W04-SOURCE-COMPLETION-INDEX-01-R1.md`

## Summary

- Added a local-only completion-index derivation path that first rebuilds the frozen
  source-snapshot bridge, verifies the existing source-manifest address, and then
  reads only the exact five completion-declared event members through the guarded
  descriptor seam. Each member is checked for its fixed path, byte size, SHA-256,
  and row count before projection.
- Projected every action without coercion into its exact source member/path/digest,
  physical ordinal, provider event/match identifiers, strict period/rank and decimal
  clock token, nullable player/team identifiers, strict event taxonomy, integer-only
  subevent projection, preserved ordered raw tags, sorted unique possession tags,
  and canonical raw-record SHA-256.
- Framed those values with explicit action and period domain separators, sorted every
  match-period by the canonical action key, and materialized one immutable period
  count/membership digest per indexed period. Member and aggregate reconciliation is
  exact and duplicate/order drift fails closed.
- Materialized the canonical 644,037-byte index at its own content address. It binds
  source manifest ID `4e16bdb5-afe7-5601-88ad-adc124cfce3b`, source manifest SHA-256
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`,
  completion manifest SHA-256
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`,
  the exact five member authorities, and 3,071,395 indexed actions.
- Added public whole-period and whole-match validators. Missing, extra, duplicate,
  reordered, stale, cross-member, cross-match, cross-period, and whole-period omitted
  evidence is rejected against the independent index count and membership digest.
- Added public period and whole-match factories that construct
  `PossessionPeriodSequence` only after exact population equality. Factory-produced
  sequences bind both the immutable index digest and their exact indexed
  match-period membership digest, use canonical source UUIDs, and retain their exact
  physical action references.
- Bound the accepted completion-index digest into Wyscout row lineage, every Silver
  and Gold product row, semantic temporal proof, possession period sequences, and
  layer manifests. Dependency-lineage hashing now covers the completion-index digest,
  so Gold's lineage-hash key transitively changes if that authority changes.
- Bound every sequence action identity to
  `canonical_source_uuid(ACTION, source_event_record_id)`.
- Changed possession resolution to inspect all CONTROL/RESTART evidence at one
  `(period_rank, period_elapsed_seconds)` clock before applying transitions. Multiple
  controlling teams make the whole clock and dependent contested buffer unassigned,
  while genuinely resolved pre-clock possession members remain intact.
- Expanded possession source rows to all actions in the complete causal period
  sequence, and expanded Fact and Gold source-row closure transitively. An
  other-player action that decides a possession boundary is retained even when it is
  not a selected row-player action.
- Added regressions for exact immutable addressing and reconciliation, population
  truncation and every membership drift family, whole-period omission, strict/no-
  coercion projection, public factory output, noncanonical action identity,
  completion-digest drift at every boundary, equal-clock group-first behavior,
  pre-existing possession preservation, contested-buffer uncertainty, and
  other-player causal provenance through Gold.

## Tests run

- command:
  `uv run python -m scouting.sources.wyscout_completion_index derive --source-root data/source/wyscout/v5 --manifest-root data/manifests`
  - exit status: `0`
  - result: created the content-addressed index with SHA-256
    `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
    `rows=3071395`, and `size_bytes=644037`.
- command:
  `uv run pytest -q tests/contracts/test_wyscout_data_contracts.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: `250 passed in 7.44s`.
- command: `uv run pytest -q`
  - exit status: `0`
  - result: `1576 passed, 1 warning in 298.79s`; the only warning is the existing
    Starlette `TestClient`/httpx deprecation warning.
- command: `uv run ruff format --check <four changed Python files>`
  - exit status: `0`
  - result: `4 files already formatted`.
- command: `uv run ruff check .`
  - exit status: `0`
  - result: all checks passed.
- command:
  `uv run mypy src tests/contracts/test_wyscout_data_contracts.py tests/unit/test_wyscout_source_completion_index.py`
  - exit status: `0`
  - result: success; no issues in 33 source files.
- command: `uv run lint-imports`
  - exit status: `0`
  - result: 31 files and 49 dependencies analyzed; all three contracts kept, zero
    broken.
- command: `uv run --group security bandit -q -r src/scouting`
  - exit status: `0`
  - result: no findings.
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: PASS; all 25 local-only and one-root-uv checks passed with zero failures.

## Artifacts/evidence

- immutable source-completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - bytes: `644037`
  - SHA-256:
    `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
  - indexed members/actions: England `643150`, France `632807`, Germany `519407`,
    Italy `647372`, Spain `628659`; aggregate `3071395`.
- `src/scouting/sources/wyscout_completion_index.py`
  - SHA-256:
    `8dea0c12678667c80171dc19890d672a88403b9c5f77e06438f53a4cd5cb4565`
- `src/scouting/contracts/wyscout_data.py`
  - SHA-256:
    `acf5555d31c931dda6c3575e5b088401847e0b8efc50c50f349ca188ee019aa0`
- `tests/unit/test_wyscout_source_completion_index.py`
  - SHA-256:
    `ea569ca0c41348842893ae5f51d0b147cb309f0421c259141c47a4b7c737439b`
- `tests/contracts/test_wyscout_data_contracts.py`
  - SHA-256:
    `ba01261521923bf2b62ea4a63930f43bc20e2df18fb3028accdf53b90d8e77c1`

## Risks

- The producer return is implementation evidence, not independent review or master
  acceptance. Fresh independent adversarial reproduction is still required.
- The public factory is the source-population authority for production construction;
  low-level immutable Pydantic models remain directly constructible for bounded
  in-memory validation and tests and therefore do not independently read the index.
- No downstream Bronze, Silver, Gold, layer-manifest, receipt, runtime, or serializer
  artifact was materialized by this packet.

## Follow-up items

- Dispatch independent review against the exact code, test, and immutable-index
  hashes recorded above.
- Require the product implementation path to consume
  `build_match_period_sequences`/`build_possession_period_sequence` rather than
  treating direct model construction as source-completion authority.

## Scope confirmation

- no Git operations: confirmed; no Git command or Git state mutation was performed.
  The packet-required local-only verifier inspected Git safety read-only.
- no delegation or self-approval: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside allowed paths: confirmed.
- no provider, network, cloud, container, external service, endpoint, hosted CI, or
  deployment access: confirmed.
