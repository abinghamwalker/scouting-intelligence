# Subagent return

## Task

- task_id: `W10-V2-DATA-CONTRACTS-08B-R1`
- objective: Implement deterministic participant-safe v2 evidence contracts, derivation,
  glossary, coverage and response semantics from the accepted A1 construct without changing W09
  retrieval or v1 authority bytes.

## Files changed

- `src/scouting/contracts/expert_relevance.py`
- `src/scouting/data_products/wyscout/expert_evidence.py`
- `configs/evaluation/w10-expert-evidence-presentation-v2.json`
- `scripts/build_w10_expert_evidence_v2.py`
- `tests/contracts/test_w10_expert_evidence_v2_contracts.py`
- `tests/unit/test_w10_expert_evidence_v2.py`
- `reports/reviews/W10/returns/W10-V2-DATA-CONTRACTS-08B-R1.md`

## Summary

- Added a wholly separate v2 contract family. Existing v1 classes, validators, digest
  projections and stored bytes remain unchanged and parse/serialize byte-for-byte.
- Added `ParticipantEvidenceComparisonV2`, which binds exactly one exemplar panel and one distinct
  candidate panel under the same policy, evidence version, position and MD branch. Its semantic
  digest is now the sole evidence authority carried by a v2 response. A boundary validator checks
  response digest/position/branch and requires every cited family to be mandatory and observed in
  both exact panels.
- Added participant-safe player context with the historical window, competition, teams, declared
  position, governed minutes/minute state, match count, retained action count, and exact lineup,
  action-match and coordinate coverage.
- Added exactly 16 ordered `W09_INPUT` metric rows with football labels, definitions, exact
  predicates, raw event counts, governed-minute denominators, exact matrix values, comparable
  within-position midrank percentiles, reference counts, coverage, lineage and the fixed
  `used_by_w09_ranking=true` flag.
- Added the accepted independent roster `ID-LOC-01`, `ID-PASS-01`, `ID-DUEL-01`,
  `ID-DEFLOC-01`, `ID-SHOTLOC-01` and narrow `ID-GK-01`. Every scalar has an exact unit,
  predicate, raw numerator/opportunity denominator, coverage, availability, comparable-reference
  count, percentile when observed, derivation version, lineage and fixed
  `used_by_w09_ranking=false` flag. DEFLOC retains separate defending-duel, interception and
  clearance predicates, denominators and floors. Every descriptor scalar carries its own exact
  predicate-specific coverage; clearance rows no longer inherit another defensive component and
  GK goal-kick/leaving-line rows no longer inherit save-attempt coverage.
- Made metric units a closed `share` / `count_per_90_governed_minutes` enum and validate exact
  numerator/denominator reconstruction, positive observed reference counts, W09 metric order,
  every independent family/metric shape and every opportunity-component roster. DEFLOC and GK
  expose no top-level composite denominator or floor; only their separate component rules remain.
- Frozen neutral 3x3 recorded-coordinate bins with no direction, progressive, final-third,
  pitch-side or toward-goal meaning. GK evidence is limited to distribution, save-attempt/reflex
  mix, leaving-line and goal-kick involvement; it makes no shots-faced, save-percentage, outcome,
  quality or effectiveness claim. Unsupported dimensions are now explicit typed
  `UNSUPPORTED_INFERENCE` / `not_captured` rows with no numeric field; the GK roster includes every
  unsupported A1 dimension.
- Preregistered explicit pre-pilot measurement rules under policy digest
  `7bfb2615b6029d2404add8dd3dd1350c0521d5f6330c233498f3c3d7f788673f`: 100 valid starts,
  25 passes, 20 duels, DEFLOC valid-start floors 5/5/3, 10 valid shot starts, GK floors 10 save
  attempts/3 leaving-line/20 goal kicks, and 95% coordinate coverage. The policy explicitly says
  these are not scientifically validated reliability cutoffs and requires stability validation
  before formal freeze.
- Frozen MD comparability as one explicit `DEFENSIVE` or `SHOOTING` branch shared by exemplar and
  every candidate in a task. The builder requires the branch for each selected MD, rejects extra
  branch keys, and never performs per-player fallback.
- Missingness is non-collapsible: captured zero with adequate opportunity is `observed_zero`;
  sparse or zero opportunity is `insufficient_opportunities`; rubric exclusion is
  `not_applicable`; source absence is `not_captured`; lineage/coverage corruption is
  `invalid_missing`. Missing, sparse and invalid values never become zero, estimates,
  percentiles or prose substitutes. Observed families now require every predicate-specific
  opportunity component to meet its floor, while `insufficient_opportunities` requires at least
  one component below its floor; `not_applicable` remains exempt and `invalid_missing` remains the
  coverage-corruption lane. Mandatory-family failure raises query-ineligibility.
- Bound every glossary row to the exact displayed metric label, definition, coverage definition,
  purpose and W09-use flag as well as its metric id and display order. Recomputed outer bundle
  digests cannot conceal drift in any of those semantic fields.
- Added separate v2 response contracts without modifying v1 `CandidateJudgement`. Relevance,
  confidence, sufficiency, assessment basis, evidence gap and cited independent families are
  distinct. Responses bind the exact comparison digest plus position/MD branch. Supplied-evidence/
  both citations are limited to the position/branch mandatory roster; prior professional knowledge
  remains a sensitivity lane. Insufficient evidence requires both a gap category and qualitative
  explanation. Rated/abstain/unable coherence is enforced under a semantic digest.
- Changed the CLI to require one exemplar grain and one candidate grain and emit only their exact
  comparison. It can no longer emit an ambiguous panel list that resembles an authorised task
  pack; one optional MD branch is applied identically to both panels.
- Participant serialization rejects protected provenance keys/values and omits player/grain,
  candidate/query, origin, rank, distance/score, control rule, evidence band/difficulty, repeat,
  expected result and previous/aggregate response identity. Independent descriptor identifiers
  remain absent from the feature matrix, scaler, index, query-weight and scorer execution files.

## Tests run

- command: `UV_NO_CACHE=1 uv run --no-sync ruff format --check` over all five implementation/test
  Python files
  - exit status: `0`
  - result: `5 files already formatted`.
- command: `UV_NO_CACHE=1 uv run --no-sync ruff check` over all five implementation/test Python
  files
  - exit status: `0`
  - result: all checks passed.
- command: `UV_NO_CACHE=1 uv run --no-sync mypy src/scouting/contracts/expert_relevance.py
  src/scouting/data_products/wyscout/expert_evidence.py scripts/build_w10_expert_evidence_v2.py`
  - exit status: `0`
  - result: no issues in three source files.
- command: `UV_NO_CACHE=1 uv run --no-sync bandit -q
  src/scouting/contracts/expert_relevance.py
  src/scouting/data_products/wyscout/expert_evidence.py
  scripts/build_w10_expert_evidence_v2.py`
  - exit status: `0`
  - result: no findings in the packet's implementation files.
- command: `UV_NO_CACHE=1 uv run --no-sync pytest -q
  tests/contracts/test_w10_expert_evidence_v2_contracts.py
  tests/unit/test_w10_expert_evidence_v2.py`
  - exit status: `0`
  - result: `30 passed in 1.40s`; final bounded hardening cases recompute the outer bundle digest
    after creating an observed family below one component floor, an insufficient family whose
    components all meet their floors, and glossary drift in label, definition, coverage definition
    or the internally coherent purpose/W09-use pair. Nested semantic validation rejects every
    mutation.
- command: `UV_NO_CACHE=1 uv run --no-sync pytest -q
  tests/contracts/test_w10_expert_evidence_v2_contracts.py
  tests/unit/test_w10_expert_evidence_v2.py
  tests/contracts/test_w10_expert_relevance_contracts.py
  tests/unit/test_w10_expert_relevance_evaluation.py`
  - exit status: `0`
  - result: `64 passed in 6.75s`; covers reconstruction, exact 16/order, purpose flags,
    mandatory position rules, MD branch rules, lineage/temporal/identity fields, coverage,
    missing-vs-zero, deterministic percentiles, forbidden bytes, response coherence, W09 path
    noninterference and v1 byte/digest compatibility. Adversarial cases recompute outer digests
    after corrupting share formulas, per-90 denominators, W09/family order and opportunity
    components; nested validation still rejects each mutation.
- command: `UV_NO_CACHE=1 uv run --no-sync python
  scripts/build_w10_expert_evidence_v2.py --help`
  - exit status: `0`
  - result: the CLI exposes required `--exemplar-grain-id` and `--candidate-grain-id`, optional
    single `--md-subrubric {DEFENSIVE,SHOOTING}`, and no bulk panel-list mode.
- command: `UV_NO_CACHE=1 uv run --no-sync python -c '<DuckDB retained-population and legacy
  query-pack threshold audit>'`
  - exit status: `0`
  - result: exact eligible/final counts were GK `136/136`, DF `713/713`, MD `692/711`, FW
    `385/415`. Both legacy MD tasks lack a single common branch across all 11 displayed players;
    legacy FW query Q04 has `10/11` eligible while Q08 has `11/11`. Legacy GK and DF queries have
    `11/11`. This is a deterministic redesign signal, not a reason to relax the frozen rules.
- command: initial full pure-Python production builder witness for one accepted GK grain
  - exit status: `130` (manually interrupted after exceeding the bounded interactive check time)
  - result: no output authority was retained. The exact source joins and threshold coverage were
    instead exercised read-only by the successful DuckDB authority audit; fixture reconstruction
    exercises the serialization path. This packet does not claim production-byte reconstruction;
    the master must run that bounded witness under `caffeinate`.
- command: master-owned pre-rework production witness under `caffeinate`
  - exit status: `0`
  - result: completed in approximately 159 seconds and produced 151,711 participant bytes with
    pre-rework bundle digest prefix `dca2299e`. Because this rework changes bundle/comparison
    semantics, that is retained performance/reconstruction evidence only and is not the final
    comparison-byte authority.

## Artifacts/evidence

- `configs/evaluation/w10-expert-evidence-presentation-v2.json`
- policy digest: `7bfb2615b6029d2404add8dd3dd1350c0521d5f6330c233498f3c3d7f788673f`
- canonical build: `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`
- matrix: `w09-historical-player-window-v1-a31511705ac15a5d`
- v1 presentation compatibility digest:
  `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`
- retained coverage witness: `tests/unit/test_w10_expert_evidence_v2.py`

## Risks

- The opportunity floors are preregistered pre-pilot measurement rules, not scientifically
  established reliability thresholds. A deterministic match-level split-half or bootstrap
  stability study remains required before formal v2 freeze; the policy makes that requirement
  machine-readable.
- The legacy v1 query pack is not v2-eligible as-is: neither MD task has one comparable branch for
  all players, and Q04 contains one ineligible FW. The mechanics/formal v2 query authorities must
  be redesigned from eligible rows without relaxing thresholds or selecting branches after
  responses.
- Production derivation streams 3.07M actions in Python. The master pre-rework witness completed in
  about 159 seconds, but the final reworked comparison bytes still require a master reconstruction
  run; this packet intentionally did not repeat the full scan.
- All retained eligible minutes are conservative lower bounds; every per-90 metric preserves that
  limitation, but unknown true exposure remains an inherent source limitation.
- This packet does not self-approve the policy, establish construct reliability, authorise a v2
  pilot/formal study, or freeze a new query pack.

## Follow-up items

- Run and independently review a retained match-level split-half or preregistered bootstrap
  stability analysis before formal v2 freeze.
- Build disjoint pilot/formal v2 query packs only from rows satisfying one task-wide comparable MD
  branch and every mandatory family; replace the ineligible legacy rows rather than weakening the
  rules.
- Master-rerun one exact final exemplar/candidate comparison under `caffeinate`, then retain its
  final bytes and digest as reconstruction evidence. Optimize runtime only if needed while
  preserving exact participant bytes and W09 noninterference.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

## Bounded rework candidate — 2026-08-06

This section supersedes the pre-rework production-witness limitation above. It does not change the
packet's scientific risks or authorise a pilot or formal collection.

- The exact ordered neutral location-bin roster and exact forbidden-direction-semantics roster are
  now validated against immutable code authority. The accepted canonical policy digest
  `7bfb2615b6029d2404add8dd3dd1350c0521d5f6330c233498f3c3d7f788673f` is pinned independently
  of the policy's embedded self-digest. Recomputed self-digests cannot conceal label, order,
  definition or forbidden-roster changes; explicit `left_flank_0` … `left_flank_8`, reordered-bin,
  modified-forbidden-roster and threshold-definition adversarial cases fail.
- Production evidence loading now requires the guarded physical canonical manifest bytes to hash
  to the independently pinned digest
  `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59` before reading the five
  retained action partitions. Symlink, hard-link, path-escape, substituted-manifest and same-build-
  ID substitution cases fail closed.
- Cross-panel reconstruction now requires identical season/window semantics, ordered
  family/metric meanings, glossary and unsupported-inference roster. An internally re-digested
  asymmetric label or definition cannot produce an accepted participant comparison.
- Final production comparison reconstruction completed under `caffeinate` with 318,525 canonical
  participant-safe bytes, file SHA-256
  `ebecc523f790264df4b1500ce5f9a2889c085607aa7858dfc776159eee4b3554`, and comparison digest
  `e06544feff1fa7733dbcced337617f1b87502256702edf75b63800cc2bdde69b`. The independent
  protected-field/value scan returned empty key and value findings. These bytes are a witness only,
  not a pilot/query-pack authority.
- The combined W10 v1/v2 contract, unit and integration boundary passed **93 tests** after the
  bounded correction. Repository-wide Ruff checking, mypy, import-contracts and Bandit passed;
  the final full-suite result is recorded in the master handoff and the A3 return.

Remaining risks are unchanged: the pre-pilot measurement floors still require the preregistered
stability study before any v2 freeze, and pilot/formal query populations still require disjoint
construction from eligible rows. No W09 feature, scaler, weight, index, score or ranking path was
changed; independent descriptors still have no executable ranking path. Formal v2 collection
remains disabled.

### Runtime-gate integration correction — 2026-08-06

The independently duplicated W04 post-W04 bytecode audit-only rosters now include exactly the four
new W10 Python paths: `scripts/build_w10_expert_evidence_v2.py`,
`src/scouting/data_products/wyscout/expert_evidence.py`,
`tests/contracts/test_w10_expert_evidence_v2_contracts.py` and
`tests/unit/test_w10_expert_evidence_v2.py`. The retained classification remains
`REPOSITORY_POST_W04_CACHE_AUDIT_ONLY` with `AUDIT_ONLY_ZERO_READ_USE`; it adds no stable source,
execution, retrieval or model authority. Both independent collectors are exercised by the expanded
adversarial test. The four reproduced W04 admission failures pass after this bounded correction,
and the complete retained runtime-control suite passes **298 tests** in 114.47 seconds.

The production witness was rebuilt again after this integration correction from the exact accepted
W09 grains for T. Strakosha and W. Hennessey. It reproduced the same 318,525 bytes, SHA-256,
comparison digest, canonical participant serialization and empty protected-key/value findings
recorded above. W09 semantics and artifacts are unchanged.
