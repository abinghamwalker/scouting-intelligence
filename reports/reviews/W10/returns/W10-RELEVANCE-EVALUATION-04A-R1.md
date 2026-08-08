# W10 expert-relevance evaluation implementation return

## Task

- task_id: `W10-RELEVANCE-EVALUATION-04A`
- objective: Implement deterministic, protocol-driven W10 expert-relevance metrics, exact authority and denominator validation, tri-state gating, immutable negative-result retention, deterministic reports, and an exclusive one-use formal evaluation runner.

## Files changed

- `src/scouting/evaluation/expert_relevance.py`
- `scripts/evaluate_w10_expert_relevance.py`
- `tests/unit/test_w10_expert_relevance_evaluation.py`
- `tests/integration/test_w10_expert_relevance_evaluation_integration.py`
- `reports/reviews/W10/returns/W10-RELEVANCE-EVALUATION-04A-R1.md`

## Summary

- Added exact loading and cross-validation for the frozen protocol, query pack, participant-safe presentation, approval, W09 pins, presentation projection, and opaque repeat-anchor roster. The final accepted identities are protocol `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`, query pack `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`, and presentation `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`.
- Added strict eligibility, consent, chronology, formal-session, presentation-roster, judgement, repeat, authority, duplicate-exclusion, coverage, and denominator validation. The 80 primaries enter relevance metrics; the two repeats enter only repeat MAD and within-one consistency.
- Implemented candidate mean 0-4 gains; macro query retrieved/control NDCG@5 against the pooled top-five ideal; macro retrieved precision@5; overall retrieved-control relevant-rate lift; paired deterministic query bootstrap; pairwise ordinal agreement; repeat consistency; coverage/missingness; position and competition subgroups; confidence distribution; and preregistered qualitative failure-category counts.
- Implemented the clarified all-zero rule: a fully rated all-zero pooled query produces supported retrieved and control NDCG values of `0.0`, yielding complete negative evidence rather than an invented denominator deficit.
- Implemented terminal `PASS`, `FAIL`, and `INSUFFICIENT_EVIDENCE` ordering with all threshold misses retained. Exact duplicate records are deterministically excluded and counted; stale/substituted or incompatible evidence fails closed.
- Added deterministic aggregate-only result and report rendering with the repository canonical JSON serializer: UTF-8, NFC-safe Unicode, lexical keys, compact separators, and one terminal LF. Reports contain no row-level rating or explanation fields.
- Added a one-use runner that validates public authority first, opens an exclusive claim before protected input, rejects replay or any partial output collision, uses directory-fd exclusive/no-follow writes at mode `0600`, retains integrity and below-threshold failures, and binds exact artifact bytes in a final receipt.
- Added a pure status route with no protected-input argument. With absent approval it returns `INSUFFICIENT_EVIDENCE / FORMAL_APPROVAL_ABSENT`; with approval but absent evidence it returns `INSUFFICIENT_EVIDENCE / FORMAL_EVIDENCE_ABSENT`; neither path writes run/result artifacts.
- Added a CLI with explicit `status` and `run` commands. Formal execution requires an exact approval, protected-input path, output directory, invocation UUID, and UTC evaluation timestamp.
- Test labels and participant objects are synthetic implementation fixtures only. No authentic participant evidence was requested, opened, fabricated, or retained, and no synthetic outcome was presented as formal study evidence.

## Tests run

- command: `uv run pytest -q tests/unit/test_w10_expert_relevance_evaluation.py`
  - exit status: `0`
  - result: `11 passed in 0.92s`
- command: `uv run pytest -q tests/integration/test_w10_expert_relevance_evaluation_integration.py`
  - exit status: `0`
  - result: `6 passed in 0.41s`
- command: `uv run ruff format --check src/scouting/evaluation/expert_relevance.py scripts/evaluate_w10_expert_relevance.py tests/unit/test_w10_expert_relevance_evaluation.py tests/integration/test_w10_expert_relevance_evaluation_integration.py`
  - exit status: `0`
  - result: all four files formatted
- command: `uv run ruff check src/scouting/evaluation/expert_relevance.py scripts/evaluate_w10_expert_relevance.py tests/unit/test_w10_expert_relevance_evaluation.py tests/integration/test_w10_expert_relevance_evaluation_integration.py`
  - exit status: `0`
  - result: all checks passed
- command: `uv run mypy src/scouting/evaluation/expert_relevance.py scripts/evaluate_w10_expert_relevance.py`
  - exit status: `0`
  - result: success, no issues in two source files
- command: `uv run python scripts/evaluate_w10_expert_relevance.py status`
  - exit status: `0`
  - result: canonical `INSUFFICIENT_EVIDENCE` with `FORMAL_APPROVAL_ABSENT`, exact final frozen digests, and both run/result creation flags false

## Artifacts/evidence

- Evaluator: `src/scouting/evaluation/expert_relevance.py`
- Formal/status CLI: `scripts/evaluate_w10_expert_relevance.py`
- Synthetic metric and authority witnesses: `tests/unit/test_w10_expert_relevance_evaluation.py`
- Replay, concurrency, collision, canonical artifact, receipt, and symlink witnesses: `tests/integration/test_w10_expert_relevance_evaluation_integration.py`
- This return: `reports/reviews/W10/returns/W10-RELEVANCE-EVALUATION-04A-R1.md`
- No `runs/`, protected-label, or formal participant-evidence artifact was created by this task.

## Risks

- The positive gate remains unavailable until a separately authorised exact approval and authentic protected expert submissions exist. The evidence-honest current status is `INSUFFICIENT_EVIDENCE`.
- The formal runner intentionally consumes an invocation even when protected input is inaccessible or malformed. A partial claim is negative immutable evidence and must not be deleted or replayed.
- The one-use writer relies on POSIX-style directory file descriptors, exclusive creation, `O_NOFOLLOW` where available, and local-filesystem semantics. Deployments on a filesystem with weaker exclusivity or durability guarantees require an environment-specific review before protected use.
- Aggregate submission digests are retained for lineage. They do not expose row labels, but access to formal output artifacts should still remain restricted because they describe a protected study population.
- The packet mandates identically named unit and integration test files in non-package directories. The two specified acceptance commands pass separately, but a single default pytest invocation containing both paths reports an import-name collision. Fixing combined collection requires an out-of-scope package or pytest import-mode change.

## Follow-up items

- Obtain separate human approval for the exact final protocol/query-pack authority before any formal participant workflow.
- Run the formal command exactly once only after authentic protected submissions are available and operational ownership of the retained claim/run/result/report/receipt directory is confirmed.
- If one-command combined W10 test collection is required, authorise a repository-level pytest import-mode or test-package change outside this packet's `allowed_paths`.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed

## Master remediation after independent review

Before approval or formal evidence existed, the master froze a minimum 80% rated-repeat-pair
denominator, added evaluation chronology rejection, made macro precision expose its exact rational
numerator/denominator under variable abstention, and moved the one-use claim into a fixed
authority-owned registry keyed by protocol/query/presentation/approval. Replaying the same
authority through a second output directory now fails before protected input is opened. The
evaluator reconstructs the exact participant-keyed schedule and rejects seven schedule
substitutions. Lift evidence retains both arms and its exact signed reduced fraction. The
integration test was renamed so the complete repository suite collects both unit and integration
modules without collision, superseding the earlier packet-local collision risk. Focused synthetic
witnesses for all corrections are included in the final 54/54 W10 suite; they are not formal
G-RW4 evidence.
