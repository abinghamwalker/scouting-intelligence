# Subagent return

## Task

- task_id: W04-VERTICAL-SLICE-ACCEPTANCE-AUDIT-01
- objective: Define the adversarial acceptance matrix for the smallest real W04 raw-to-Bronze-to-Silver-to-Gold slice without changing implementation or product bytes.

## Files changed

- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-ACCEPTANCE-AUDIT-01-R1.md`

## Summary

- Verdict: **PASS_TO_PRODUCER_DISPATCH**. The frozen contracts and accepted completion index are sufficient for this bounded slice; no architecture, dependency, provider, cloud, container, deployment, or feature expansion is required. This is an acceptance-plan verdict, not product acceptance; the master must mark the implementation `BLOCKED` if any mandatory row below fails.
- Exact slice: England source member `archive-members/events_England.json` (`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`), match source ID `2499719` / UUID `bad97950-6fac-5cf0-a93c-094f91abbb9b`, player source ID `285508` / UUID `be8da881-2b15-513f-978f-6bb3865bc8e2`, and action source IDs `177960876` and `177961018`.
- Exact completion/output oracle: `1H=901`, `2H=867`, whole match `1768`; both selected-player actions are `2H`, exact causal period provenance is `867` source rows, and Gold is exactly `action_count=2`, `coordinate_known_action_count=2`, `match_count=1`, `resolved_possession_action_count=2`. Their two intersecting resolved possession groups contain `7` and `6` actions, so the faithful bounded Silver graph has `13` checked actions and `2` checked possessions while the player-match fact contributes only the target player's `2` actions. The accepted index is `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.

### Mandatory acceptance matrix

| Priority | Acceptance case | Required proof | Expected negative behavior |
| --- | --- | --- | --- |
| P0 | Frozen source admission | Before selection, verify exact source-manifest bytes/ID/digest, England member digest/size/`643150` rows, then extract the exact `2499719` population. Bronze must preserve all `1768` match action records with physical ordinal and canonical raw-record digest. | Wrong/stale/cross-source manifest or member, size/count drift, or source mutation fails before any product write. |
| P0 | Exact completion equality | `validate_checked_match_population` must accept only the canonically ordered `901+867` population and bind every downstream checked graph to the accepted index digest. | Truncation, single-row omission, additional row, duplicate, reorder, stale row digest, stale index, cross-period, cross-match, or cross-member evidence raises `WyscoutCompletionIndexError`; no layer manifest or receipt may claim completion. |
| P0 | Checked write boundary | Immediately before every Silver/Gold serialization and checked Silver/Gold manifest serialization, call `require_checked_product` for the exact expected type; re-derivation must traverse the authentic acyclic capability graph. | Direct models, dump/revalidated copies, detached values, substituted capabilities, registry/closure forgeries, malformed records, cycles, or altered dependency payloads fail closed before bytes are promoted. |
| P0 | Silver/Gold reconciliation | Materialized Silver must contain the exact `13` checked actions and `2` checked possessions needed by the two resolved groups, with the fact selecting the player's exact `2` actions; all values preserve the `867` causal rows and reconcile to Gold `(2,2,1,2)`. Both target actions have two accepted in-bounds positions. No rate, per-90, outcome, value, role, continuous-time, provider-possession, or lineup-count feature is emitted. | Missing/extra contributor, dropped accepted positions, coordinate count `0`, wrong player/team/match, double possession membership, arbitrary count, fifth feature, or unsupported-feature substitution is rejected and produces no complete Gold manifest. |
| P0 | Temporal leakage | Every dependency `observed_at` and `available_at`, source acquisition, all authority clocks, snapshot, contributing match start, and window fact must be strictly before `feature_cutoff_ts`; watermark is the exact maximum and `valid_from_ts=max(snapshot, watermark)`. Window membership is start-inclusive/end-exclusive. | A clock equal to or after cutoff, forged/omitted dependency, wrong watermark/valid-from, fact at/after cutoff, or fact outside the window fails validation; prove zero post-cutoff facts were read into Gold. |
| P1 | Deterministic rebuild | Two isolated guarded roots with the same frozen inputs, build ID and run ID produce byte-identical Parquet, manifests and receipts; semantic and physical digests, row order/counts, paths, and Gold value match. With a different run ID, product and layer-manifest bytes remain identical. | Any wall-clock, host, absolute-path, random-order, or serializer drift makes acceptance `BLOCKED`. |
| P1 | Idempotent immutable writes | First run creates artifacts; exact replay changes no bytes and reports idempotent confirmation. Same path with different bytes, symlink/traversal, or an injected late conflict is rejected; no partial run gains a complete manifest. | Guarded conflict/path errors; existing accepted bytes remain unchanged and no success/completion receipt is issued. |
| P1 | Manifest and lineage closure | Every entry has the exact path role/serializer owner/schema role, sorted partitions/parents, positive row count/size, correct semantic and physical hashes, restricted classification, and `complete=true`. Bronze has no parent; Silver has exact same-build Bronze; Gold has exact same-build Silver. All layer and Gold lineage binds source manifest, completion index and five ordered dependencies. | Missing/extra/duplicate/unsorted entry, count/hash/size drift, wrong parent/build/serializer/path/classification, copied digest, or completion-scope mismatch fails manifest construction/readback. |
| P1 | Receipt closure | Rebuild and temporal-boundary receipts use only the frozen templates, bind exact build/run, layer-manifest and Gold-path hashes, row counts and zero-leakage result, and never broaden the one-match/player claim. | Stale/cross-build/cross-run/cross-Gold receipt or Boolean/count-only completeness witness is rejected; no successful status is retained. |
| P1 | Rights and local-only boundary | Restricted/internal-only classification and attribution propagate; export remains false. Verification shows no provider/network call, remote, cloud, hosted CI, public endpoint, container, external service, or deployment, and all outputs remain under guarded local roots. | Any rights drift, external access/configuration, escaped path, Git remote, or missing push guard blocks acceptance. |

The complete repository master gate is mandatory after the focused slice tests:

```text
uv sync --locked --all-groups
uv run ruff format --check .
uv run ruff check .
uv run mypy src/scouting scripts
uv run lint-imports
uv run pytest -q
uv run bandit -q -r scripts src
uv run python scripts/install_local_git_guards.py --check
uv run python scripts/verify_local_only.py
uv run python scripts/verify_phase.py --phase W04
git diff --check
git status --short
git remote
```

Acceptance requires every command to exit `0`, expected worktree changes to be fully explained, and `git remote` to print nothing.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -q -p no:cacheprovider tests/contracts/test_wyscout_data_contracts.py::test_real_match_checked_path_reaches_gold_and_exact_scoped_manifest`
  - exit status: 0
  - result: `1 passed in 108.14s`; the existing authentic checked path reached an exact one-match scoped manifest. This is a capability-composition baseline only: its test helper deliberately replaces real positions with `()`, so production acceptance uses the raw-field oracle `(2,2,1,2)`, not that fixture's `(2,0,1,2)`.

## Artifacts/evidence

- This acceptance matrix: `reports/reviews/W04/returns/W04-VERTICAL-SLICE-ACCEPTANCE-AUDIT-01-R1.md`
- Accepted complete repository gate authority: `reports/verification/W04/wyscout-source-completion-index-R4-complete-repository-gate.md`
- Accepted completion index: `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- Independent real-source audit: `reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-AUDIT-01-R1.md`

## Risks

- Product bytes, receipt models, and the new end-to-end rebuild tests are intentionally not implemented by this audit; final acceptance remains blocked until the producer implements them and independent reviewers plus the master reproduce every mandatory case.
- The real-source focused baseline takes about two minutes locally; this is a verification-cost risk, not a scope contradiction.

## Follow-up items

- Producer implements only the exact bounded slice and matrix; independent reviewers exercise positive determinism plus adversarial authority/temporal/immutability cases; master reruns the complete repository gate.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
