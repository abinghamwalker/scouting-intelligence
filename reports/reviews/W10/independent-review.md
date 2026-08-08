# W10 independent review — 07A-R1

**Initial candidate reviewed:** `4086756` (the candidate identifier supplied in the task packet)  
**Remediation candidate re-reviewed:** `fcbd4f9` (the supplied follow-up identifier; includes `424dd07`)  
**Final master candidate re-reviewed:** `f07224c` (the supplied master candidate identifier)
**Review date:** 2026-08-05
**Current recommendation:** **ACCEPT**
**Initial finding count:** P0: none; P1: 5; P2: 3; P3: none  
**Open after `fcbd4f9`:** P0: none; P1: 1; P2: 1; P3: none
**Final open after `f07224c`:** P0: none; P1: none; P2: none; P3: none

This was a fresh read-only review of the W10 protocol, blinded query pack, participant presentation, collection boundary, persistence, evaluator, retained W09 runtime controls, tests, and claim boundaries. Line references below identify the candidate snapshot as it stood during review; remediation performed after the candidate was handed over may move those lines. I made no Git operation, dependency change, formal-study action, or implementation edit. This report is the only file created by the review.

## Initial recommendation basis

The initial candidate has strong foundations: it reconstructs the frozen W09 authority, provides five retrieved candidates and five matched controls for each of eight queries, excludes origin/rank/score/evidence-band and W09 identifiers from the participant projection, separates pilot/formal/test-only storage, retains immutable evidence, and keeps W10 labels out of modeling, ranking, and serving. Independent arithmetic also reproduced its intended metric values.

The initial candidate is not engineering-ready, however. Five P1 defects affect retained runtime integrity, experimental blinding, preregistered denominator policy, local-only enforcement, and the one-use protected-label claim. Three P2 defects affect chronology, metric evidence, and pre-submission review. A formal study must not start on that candidate.

## Findings

### W10-IR-01 — P1 — retained W04 runtime control rejects ordinary post-W04 test activity

**Evidence.** After the focused W10 tests created normal Python bytecode caches, the retained runtime-control suite finished with **4 failed, 292 passed**. Each failure reached `scripts/launch_wyscout_v5.py:3615-3628` and raised `RuntimeControlError` for an existing source-backed cache that was absent from the exact post-W04 audit-only roster; the first reported example was:

```text
WHOLE_REPOSITORY:scripts/__pycache__/evaluate_w09_retrieval.cpython-312.pyc
-> scripts/evaluate_w09_retrieval.py
```

The same exact roster is duplicated at `scripts/admit_wyscout_v5_runtime.py:303` and `scripts/launch_wyscout_v5.py:1521`; parity checks occur at `scripts/launch_wyscout_v5.py:3354-3387`. Comparing live source-backed caches with both retained rosters found these 42 unclassified source siblings:

```text
scripts/evaluate_w09_retrieval.py
src/scouting/data_products/wyscout/historical.py
src/scouting/evaluation/research.py
src/scouting/features/historical.py
src/scouting/sources/wyscout_historical.py
tests/contracts/test_w05_m0_contracts.py
tests/contracts/test_w08_workflow_contracts.py
tests/contracts/test_w09_research_contracts.py
tests/e2e/test_w05_m0_retrieval.py
tests/e2e/test_w07_local_evidence_playwright.py
tests/e2e/test_w08_local_workflow_playwright.py
tests/e2e/test_w09_research_workbench_playwright.py
tests/integration/test_w05_m0_serving.py
tests/integration/test_w07_local_evidence_app.py
tests/integration/test_w08_evidence_export.py
tests/integration/test_w08_local_workflow_app.py
tests/integration/test_w08_study_harness.py
tests/integration/test_w08_workflow.py
tests/integration/test_w09_feature_matrix.py
tests/integration/test_w09_full_canonical_build.py
tests/integration/test_w09_research_api_integration.py
tests/integration/test_w09_research_evaluation_integration.py
tests/integration/test_w09_research_index_build.py
tests/integration/test_w09_research_report_persistence.py
tests/integration/test_w09_research_serving_integration.py
tests/integration/test_w09_research_storage.py
tests/security/test_w08_auth_audit.py
tests/security/test_w08_export_boundaries.py
tests/security/test_w08_web_security.py
tests/security/test_w08_workflow_access.py
tests/unit/test_w05_features.py
tests/unit/test_w05_m0_models.py
tests/unit/test_w05_roles.py
tests/unit/test_w06_missing_population_gate.py
tests/unit/test_w09_historical_features.py
tests/unit/test_w09_research_api.py
tests/unit/test_w09_research_evaluation.py
tests/unit/test_w09_research_index.py
tests/unit/test_w09_research_reporting.py
tests/unit/test_w09_research_serving.py
tests/unit/test_w09_scoring_kernel.py
tests/unit/test_w09_wyscout_historical_adapter.py
```

**Impact.** The candidate's claimed retained runtime-hardening gate does not survive the repository's own normal test activity. This makes the W04 gate non-reproducible and prevents W10 engineering readiness.

**Bounded correction.** Reconcile the admission and launcher audit-only rosters for every intended post-W04 source while preserving zero-read/deny authority, add a regression that creates representative source-backed caches across the retained W05–W09 surface, and run the W10 suite before the complete W04 runtime suite in a fresh checkout/worktree-equivalent state.

### W10-IR-02 — P1 — the two repeat assessments are predictably exposed as tasks 81 and 82

**Evidence.** `src/scouting/storage/expert_study.py:687-768` creates all primary presentations first and appends both repeats afterward, assigning them the final ordinals. The participant-facing dashboard discloses “80 blinded primary candidates plus 2 delayed, blinded repeat assessments” and 82 total responses at `apps/web/templates/w10_expert_study/dashboard.html:21-31`; the task view exposes the current ordinal and total at `apps/web/templates/w10_expert_study/participant.html:5-10`.

**Impact.** A participant knows that the final two tasks are repeats and can consciously reproduce earlier answers. The repeat metrics therefore do not provide an adequately blinded estimate of response consistency and can be inflated without any evaluator-detectable integrity failure.

**Bounded correction.** Freeze a participant-keyed deterministic interleaving rule that places the repeats after a suitable delay at nonterminal, nonadjacent positions; update the protocol/presentation digests before approval; and have the evaluator independently reconstruct and verify the exact schedule rather than trusting submitted presentation metadata. Add tests proving repeats are delayed, nonterminal, nonadjacent, deterministic, and rejected when substituted or reordered.

### W10-IR-03 — P1 — evaluator silently requires every repeat pair to be rated

**Evidence.** In the candidate, `src/scouting/evaluation/expert_relevance.py:839-844` required the count of valid repeat differences to equal `participant_count × 2`. Yet the frozen protocol describes consistency among repeat pairs with two rated answers and declares insufficient evidence when a required metric has no valid denominator; it does not preregister a 100% rated-repeat threshold. In a synthetic otherwise-PASS five-participant study, changing only one of ten repeat responses to an explicit abstention left nine valid repeat pairs but caused `INSUFFICIENT_RATED_REPEAT_PAIRS` and suppressed both repeat metrics.

**Impact.** A hidden post-freeze denominator rule changes the formal decision policy. It can turn a study with a valid repeat denominator into insufficient evidence without participant-visible or authority-bound preregistration.

**Bounded correction.** Before any approval or formal response, freeze an explicit minimum valid-repeat-pair rate/count in the protocol and participant-facing decision explanation, or use the already declared nonzero valid denominator rule. Bind the chosen policy into a new protocol digest and test zero, partial, boundary, and complete valid-repeat coverage.

### W10-IR-04 — P1 — “local-only” policy trusts a spoofable HTTP Host header

**Evidence.** `src/scouting/web/w10_expert_study.py:240-251` validates only `request.headers["host"]`; it does not validate the transport peer in `request.client.host`. An ASGI request whose remote client was `198.51.100.23` and whose header was `Host: localhost` passed this middleware and reached the application, returning the application's 503 availability response rather than the middleware's 400 denial.

**Impact.** If the service is accidentally bound to a non-loopback interface, a remote caller can supply `Host: localhost` and reach approval, session, judgement, and submission mutation routes. Host validation alone is not a local-transport boundary.

**Bounded correction.** Require both an allowed Host value and a loopback transport peer for every route, with a narrowly explicit test-client exception that cannot be enabled in production. Add remote-peer/localhost-Host and loopback-peer/foreign-Host tests for read and mutation routes.

### W10-IR-05 — P1 — one-use protected-label claim is scoped only to a caller-selected output directory

**Evidence.** `src/scouting/evaluation/expert_relevance.py:1219-1259` derives the claim/run/result/report/receipt paths solely from the supplied `output_directory` and rejects replay only when one of those filenames already exists in that directory. The same approval and protected-input envelope can therefore be evaluated again by selecting a second empty directory.

**Impact.** The one-use label-opening policy is not globally enforced for the approved protocol/query/presentation authority. A caller can inspect protected labels repeatedly, defeating the preregistered single-use boundary even though each directory locally says `one_use: true`.

**Bounded correction.** Claim the authority tuple (at minimum protocol, query-pack, presentation, and approval digests) atomically in one fixed, authority-owned namespace before opening protected input. Treat any second claim—regardless of output directory—as replay, and add a concurrency test using two distinct directories plus recovery tests for a partial first invocation.

### W10-IR-06 — P2 — candidate accepted an evaluation timestamp preceding approval or submissions

**Evidence.** At candidate `src/scouting/evaluation/expert_relevance.py:718-745`, the evaluator checked only that `evaluated_at` was an exact UTC datetime and did not compare it with `approval.approved_at` or the included `submitted_at` values. A synthetic study retained PASS with `evaluated_at=2026-08-04T12:01:00Z` even though its latest formal submission was `2026-08-05T16:21:00Z`.

**Impact.** The retained result/run chronology can be impossible, weakening provenance, auditability, and claim-before-open evidence.

**Bounded correction.** Before metric computation and artifact retention, require `evaluated_at >= approved_at` and `evaluated_at >= max(submitted_at)`; return a deterministic integrity failure for violations and test both boundaries and timezone handling.

### W10-IR-07 — P2 — precision evidence fields do not describe the macro metric

**Evidence.** The candidate computes retrieved precision as an unweighted macro average of candidate-level relevant rates at `src/scouting/evaluation/expert_relevance.py:907-922`, but its metric evidence fields used pooled relevant/rated counts at the corresponding precision metric row (candidate `src/scouting/evaluation/expert_relevance.py:946-952`). With synthetically variable abstention, the emitted precision value was `0.975`, while the supplied numerator and denominator were `195/198 = 0.984848…`. The lift row similarly supplied only retrieved pooled counts even though the value is a difference between retrieved and control rates.

**Impact.** A reviewer cannot reproduce the reported metric from its declared numerator and denominator. Exact-looking but semantically unrelated evidence is misleading in a formal gate artifact.

**Bounded correction.** Encode the exact reduced fraction (or explicit macro component count) for macro precision, and represent lift with both retrieved and control component counts/rates rather than a single numerator/denominator pair. Add variable-abstention fixtures that assert every retained metric is reproducible from its evidence fields.

### W10-IR-08 — P2 — “review” cannot inspect or correct responses before immutable submission

**Evidence.** `src/scouting/storage/expert_study.py:859-997` permits writing only the current unanswered task and stores one immutable judgement per presentation. Once all tasks are answered, `apps/web/templates/w10_expert_study/participant.html:32-35` shows only aggregate rated/abstained counts and a submit button; it does not show response-level answers or provide correction controls.

**Impact.** The UI calls this a review but does not provide meaningful review. An accidental rating or abstention cannot be corrected before the session is sealed, adding avoidable response error to a small formal expert study.

**Bounded correction.** Add participant-safe response review and pre-submit correction with append-only revisions, preserving the original and revised entries and making the submitted snapshot immutable. Do not expose origin, rank, scores, controls, repeat linkage, or expected answers during review. Test replay/idempotency, concurrent edits, revision history, and immutability after submission.

## P0 and P3 disposition

- **P0:** none found. I found no current path that imports formal W10 labels into feature construction, retrieval/ranking, serving, or W09 runtime authority; no formal artifacts exist to leak.
- **P3:** none found. The remaining observations were either covered by the findings above or were non-actionable preferences rather than correctness, scientific, privacy, security, browser, persistence, or claim-boundary defects.

## Independent scientific and contract checks

The following checks passed and should be preserved through rework:

- The frozen authority files were internally pinned as protocol `42c15dc389291d7b556156c8341b1ff7106a81c4f8f9c537b9d0615a64aa0c7b`, query pack `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`, and participant presentation `79be7a4870689c751b2b0cced962157c2031630236f2202a941d4bf7bf281590`.
- Each of eight queries has five retrieved candidates and five controls. Controls match competition and position and are assigned within the declared evidence band. Across five participants this yields 100 rated primary judgements per position subgroup; competition query counts are England 1, France 2, Germany 1, Italy 2, and Spain 2.
- The participant projection contains opaque presentation/candidate identifiers and football-display evidence but excludes origin, rank, retrieval score, candidate grain, W09 row identifiers, difficulty, and evidence-band labels. Browser code does not import the query pack, evaluator, or W09 research runtime.
- Equal eight-feature weights per side were preserved. With representative gains `[4,3,4,3,4]` for retrieved candidates and `[2,1,0,2,1]` for controls, independent standard-library calculations produced: retrieved NDCG@5 `0.9777632910699184`; control NDCG@5 `0.3534099071758478`; paired delta and deterministic bootstrap lower/upper `0.6243533838940707`; precision@5 `1.0`; retrieved-control relevant-rate lift `1.0`; ordinal agreement `1.0`; repeat MAD `0.0`; repeat-within-one `1.0`. An all-zero-gain query correctly yields NDCG `0.0` for both arms.
- Pilot, formal, and test-only stores/evidence classes are separated. Formal export rejects pilot/test-only, stale, and mixed evidence. Canonical immutable capture, idempotency, concurrency, and symlink protections have focused tests.
- Searches over modeling, ranking, serving, feature, and workflow code found no W10 label consumption or model/ranker mutation path. Claim searches found prohibitions rather than unsupported positive recruitment, current-outcome, or future-outcome claims.
- The participant page includes a skip target, live status, semantic fieldsets/labels, explicit progress, responsive 320 px rules, and abstain/unable paths. The focused Playwright test passed. These browser positives do not cure the repeat-disclosure and review defects above.

## Commands and observed results

All Python commands used `UV_CACHE_DIR=/private/tmp/w10-review-uv-cache` and `uv run --no-sync` because the sandbox denied the default repository-adjacent uv cache. No dependency resolution or installation was performed.

- Focused W10 contracts, web unit/integration/e2e, and evaluator unit/integration tests: **38 passed**, one Starlette/httpx deprecation warning, 12.57 s.
- Retained `tests/unit/test_w04_wyscout_runtime_control.py`: **4 failed, 292 passed**, 45.38 s; all four failures were the unclassified source-backed-cache defect W10-IR-01.
- Focused Ruff on W10 source/build/test files: passed.
- Producer-equivalent focused mypy groupings (web/storage/contracts; evaluator/CLI; builder): passed. A later over-combined invocation produced a duplicate-module-name collision caused by the invocation grouping, not a candidate code finding.
- Synthetic evaluator probes: one-of-ten repeat abstention reproduced W10-IR-03; variable abstention reproduced W10-IR-07; a pre-submission timestamp reproduced W10-IR-06.
- ASGI remote-peer probe with `Host: localhost`: reached the application and reproduced W10-IR-04.
- Independent metric calculation did not import or call the W10 evaluator and reproduced the values listed above.
- Formal status CLI and `reports/verification/W10/no-formal-evidence-status.json`: `INSUFFICIENT_EVIDENCE`, reason `FORMAL_APPROVAL_ABSENT`, no run artifact, no result artifact.

## Human-study truth and gate state

No formal study was conducted. There is no exact human protocol approval, no formal participant submission set, no accepted protected-input envelope, and no formal result. The current truthful state is therefore:

- **G-RW4-PROTOCOL:** awaiting exact human approval; not passed.
- **G-RW4-STUDY:** `INSUFFICIENT_EVIDENCE`; formal evidence absent.
- **G-RW4-RESULT:** `INSUFFICIENT_EVIDENCE`; no run/result artifact exists.
- **Overall G-RW4:** not passed.

Per `docs/architecture/w10-expert-relevance-validation.md:92-94`, engineering readiness alone cannot close W10, and W11 must not begin before formal tri-state evidence, retained runtime hardening, complete verification, and independent review are all closed. Because this candidate also has the P1/P2 defects above, the immediate disposition is **REWORK**, followed by a fresh independent rerun on a new candidate. Formal approval and recruitment remain separate later human actions and must not be inferred from engineering completion.

## Remediation re-review — 2026-08-05 — `fcbd4f9`

This section re-reviews the supplied remediation identifier `fcbd4f9`, which includes the earlier remediation identifier `424dd07`, against all eight original findings. As before, I used no Git operation and made no implementation, dependency, approval, study, or evidence change. The candidate identifier is supplied authority; this review inspects the workspace content directly.

**Final recommendation:** **REWORK**  
**Final open counts:** P0: none; P1: 1; P2: 1; P3: none

Six findings are closed. W10-IR-02 remains open at P1 because protected submissions with terminal or substituted repeat schedules still pass evaluator integrity. W10-IR-07 remains open at P2 because macro precision evidence is fixed but the lift metric still publishes a fraction for the retrieved rate rather than for the reported retrieved-minus-control value. A formal study must not start until both are corrected and independently re-reviewed.

### Closure matrix

| Finding | Re-review status | Evidence and disposition |
|---|---|---|
| W10-IR-01 (P1 runtime cache roster) | **CLOSED** | The exact audit-only rosters in `scripts/admit_wyscout_v5_runtime.py:300-406` and `scripts/launch_wyscout_v5.py:1519-1624` now include the previously unclassified live source siblings while preserving `AUDIT_ONLY_ZERO_READ_USE`. `tests/unit/test_w04_wyscout_runtime_control.py:2704-2750` checks representative normal and pytest-rewrite caches through both independent collectors and exact child/launcher roster parity. The actual admission witness plus the two parametrized multi-cache witnesses passed 3/3 independently. |
| W10-IR-02 (P1 repeat blinding/schedule integrity) | **OPEN — P1** | Collection now interleaves delayed, nonterminal repeats, but the exact repeat-slot algorithm is not frozen in the presentation contract and the evaluator does not verify it. A direct terminal-repeat fixture at ordinals 81/82 still produces PASS. Detailed evidence follows. |
| W10-IR-03 (P1 hidden repeat denominator) | **CLOSED** | `StudyCompletionRules.minimum_rated_repeat_pair_rate` is authority-bound at `src/scouting/contracts/expert_relevance.py:121-142`; the frozen value is 0.80 and is disclosed in the protocol and dashboard. `src/scouting/evaluation/expert_relevance.py:864-872` enforces it. Nine of ten valid pairs remain evaluable, while seven of ten are insufficient, in `tests/unit/test_w10_expert_relevance_evaluation.py:362-415`. The protocol/presentation digests were regenerated before approval. |
| W10-IR-04 (P1 Host-only local boundary) | **CLOSED** | `src/scouting/web/w10_expert_study.py:241-254` now requires both an allowed Host and a loopback transport peer. `tests/unit/test_w10_expert_study_web.py:79-107` proves a remote `203.0.113.19` peer with `Host: localhost` is denied. My focused rerun passed. |
| W10-IR-05 (P1 directory-local one-use claim) | **CLOSED** | `src/scouting/evaluation/expert_relevance.py:1237-1279` atomically claims the protocol/query/presentation/approval tuple under fixed `FORMAL_EVALUATION_AUTHORITY_ROOT` before opening labels. `tests/integration/test_w10_expert_relevance_evaluation_integration.py:159-172` proves a second empty output directory cannot reset consumption; the concurrent exclusive-claim test also passed independently. |
| W10-IR-06 (P2 impossible chronology) | **CLOSED** | `src/scouting/evaluation/expert_relevance.py:737-776` fails closed when evaluation precedes approval or any submission. The retained submission-boundary test passed, and an independent approval-boundary probe returned `FAIL / INTEGRITY_FAILURE:EVALUATION_PRECEDES_PROTOCOL_APPROVAL`. |
| W10-IR-07 (P2 metric evidence mismatch) | **OPEN — P2** | The macro-precision fraction is corrected and its variable-abstention test passes. The lift evidence remains semantically wrong: its value is a difference, while its numerator/denominator still encode only the retrieved rate. Detailed evidence follows. |
| W10-IR-08 (P2 no pre-submit correction) | **CLOSED** | `src/scouting/storage/expert_study.py:397-415,982-1262` retains an append-only revision chain, verifies it against the current projection, supports idempotent pre-seal correction, and rejects post-seal mutation. `apps/web/templates/w10_expert_study/participant.html:32-54` provides participant-safe response-level review and correction without origin, presentation kind, expected result, or repeat linkage. Focused storage/browser witnesses passed. |

### Remaining W10-IR-02 — P1 — evaluator still accepts a non-frozen terminal repeat schedule

**What improved.** `src/scouting/storage/expert_study.py:706-829` now generates participant-keyed repeat slots with at least ten intervening primary assessments and leaves a primary as the terminal task. The formal console test proves deterministic, delayed, nonterminal collection for the same participant at `tests/integration/test_w10_expert_study_console.py:359-410`. This closes the participant-facing disclosure mechanism for sessions produced by that store.

**Residual evidence.** The formal authority does not bind or independently adjudicate that schedule:

- `ExpertStudyPresentationBundle` has query- and candidate-order prose but no exact repeat-slot/delay rule at `src/scouting/contracts/expert_relevance.py:439-472`. The implementation-only constant `minimum_primary_delay = 10` and keyed slot formula at `src/scouting/storage/expert_study.py:786-808` are therefore not an exact presentation-digest field.
- `src/scouting/evaluation/expert_relevance.py:382-405` verifies the primary set and repeat-anchor candidate set only. It does not reconstruct participant-keyed order, delay, nonterminal placement, adjacency, repeat-to-primary identity, or presentation IDs from the submitted participant/session authority.
- The evaluator's own synthetic formal fixture appends all 80 primaries and then repeats at ordinals 81 and 82 (`tests/unit/test_w10_expert_relevance_evaluation.py:120-151`). That fixture still receives PASS in `tests/unit/test_w10_expert_relevance_evaluation.py:290-305`.
- An independent direct probe printed `terminal_repeat_ordinals=[81, 82]` and `terminal_schedule_decision='PASS'` under the remediated frozen protocol and presentation.

**Impact.** A protected envelope can substitute a knowingly exposed repeat schedule even though the frozen protocol now promises interleaved, nonterminal repeats. The formal evaluator will treat the resulting consistency values as authoritative. Store correctness alone does not protect evaluator inputs or retained evidence.

**Required bounded correction.** Bind the exact participant-keyed query, candidate, and repeat-slot algorithm—including minimum delay and nonterminal/nonadjacent constraints—into frozen authority. Extract or independently reproduce the pure schedule derivation in the evaluator using the submission's participant-code digest and session ID. Reject any mismatch before metric access. Replace terminal evaluator fixtures with exact generated schedules and add negative tests for terminal, reordered, adjacent, under-delayed, wrong-reference, wrong-ID, and participant-substituted schedules. Regenerate authority digests before any approval.

### Remaining W10-IR-07 — P2 — lift evidence still describes the retrieved rate, not the lift

**What improved.** Macro precision is now computed as an exact `Fraction` and the metric row retains that reduced fraction at `src/scouting/evaluation/expert_relevance.py:915-919,943-949`. The variable-abstention witness in `tests/unit/test_w10_expert_relevance_evaluation.py:417-449` passed and proves `value == numerator / denominator` for precision.

**Residual evidence.** The lift is computed as `retrieved_rate - control_rate` at `src/scouting/evaluation/expert_relevance.py:926-932`, but the lift metric row at `src/scouting/evaluation/expert_relevance.py:974-979` still stores `retrieved_relevant / retrieved_rated`. A direct fully rated probe with retrieved rate 0.60 and control rate 0.20 emitted:

```text
lift value:       0.39999999999999997
evidence fields:  120 / 200
evidence value:   0.6
```

**Impact.** The formal result still contains an exact-looking numerator/denominator pair that cannot reproduce the metric it purports to support. This is especially problematic for a decision-bearing threshold and for negative lift, which the current nonnegative numerator contract cannot represent as one fraction.

**Required bounded correction.** Extend the metric evidence schema or introduce a lift-specific component contract that retains both retrieved and control relevant/rated counts and the resulting rates. Make the retained value reproducible from those declared components, and add positive, zero, negative, and unequal-denominator tests. Do not overload the generic numerator/denominator fields with one arm of a two-arm contrast.

### Re-review verification

Independent reruns on the remediation workspace produced:

- Focused W10 contracts, web, console, Playwright, evaluator unit, and evaluator integration suite: **43 passed**. The sandbox run produced 41 passes plus two loopback-bind errors; the same two Playwright tests passed 2/2 when rerun with the required loopback permission. Thus the combined code result is 43 passed, with one Starlette/httpx deprecation warning outside the browser-only rerun.
- Ten selected remediation witnesses covering loopback enforcement, delayed collection, append-only correction, partial repeat coverage, macro precision, chronology, global one-use replay, and concurrency: **10 passed**.
- Retained actual-admission witness plus both new multi-cache collector witnesses: **3 passed** with the existing uv cache and locked child process available. Two earlier sandboxed attempts failed only because the isolated cache lacked `archive-v0` and the default cache's `.git` path was denied; neither reached a candidate assertion. The permitted rerun passed.
- Direct evaluator probes: terminal repeats at 81/82 were accepted as PASS (open W10-IR-02); a 0.60 retrieved rate minus 0.20 control rate emitted lift `0.40` with evidence `120/200 = 0.60` (open W10-IR-07); evaluation one second before approval failed with the correct integrity reason (closed W10-IR-06).

The producer-provided broader evidence—43 focused W10 passes, six exact runtime-cache regressions, 49 passes with 292 deselected in the combined selection, and passing relevant Ruff, mypy, and Bandit—is consistent with the independently rerun passing surfaces. Those pass counts do not exercise the two direct residual witnesses above.

### Current formal truth after remediation

The remediation legitimately refroze the protocol before any approval: protocol digest `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f`, unchanged query-pack digest `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5`, and presentation digest `5ab669367e6c7a98ea9b4f920bd53aa9f15381ae0cd20cf7ebebcdc855bb059a`. `reports/verification/W10/no-formal-evidence-status.json` remains truthful: `INSUFFICIENT_EVIDENCE / FORMAL_APPROVAL_ABSENT`, with no run or result artifact.

No formal study was conducted. G-RW4-PROTOCOL still awaits exact human approval; G-RW4-STUDY and G-RW4-RESULT remain `INSUFFICIENT_EVIDENCE`; overall G-RW4 is not passed. Because one P1 and one P2 remain open, the remediation candidate is **REWORK**, not ACCEPT. W11 must not start.

## Final master re-review — 2026-08-05 — `f07224c`

This final addendum independently re-reviews the supplied master candidate `f07224c`, concentrating on the two findings left open after `fcbd4f9` and scanning the touched contracts, collection, evaluator, safe evidence, browser, persistence, runtime-cache, and claim boundaries for regression or new P0–P3 issues. I used no Git operation and made no implementation, dependency, approval, formal-study, or evidence change. This review report is the only file I edited.

**Final recommendation:** **ACCEPT**
**Final open counts:** P0: none; P1: none; P2: none; P3: none

This is acceptance of the engineering candidate only. It is not protocol approval, recruitment, formal evidence, a G-RW4 result, W10 closure, or permission to start W11.

### W10-IR-02 — CLOSED — exact formal schedule is frozen and independently enforced

The complete formal schedule policy is now part of the participant-safe authority projection at `src/scouting/contracts/expert_relevance.py:442-479`:

- `schedule_rule = w10-participant-keyed-interleaved-v1`;
- `minimum_repeat_primary_delay = 10`;
- `repeat_must_be_nonterminal = true`;
- `repeats_must_be_nonadjacent = true`;
- the participant-digest-keyed query and candidate ordering rules.

Those fields are included in `ExpertStudyPresentationBundle.digest_projection`. A separate standard-library recomputation over the exact projection produced the declared presentation digest `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`; independently changing the minimum delay, nonterminal flag, or nonadjacent flag changed the digest. The canonical artifact and all frozen constants/status references use the new digest. The protocol and query-pack digests remain `7420c3ec94e10b72276854d25aca37fffa64b4fbc26890e898b9f20ccdf0927f` and `cf6796d5fd6905129548d194404f4de0577df1c2b0c5183cf2da7848a309ffd5` respectively.

`build_formal_candidate_presentations` at `src/scouting/contracts/expert_relevance.py:567-679` is now the pure, versioned schedule constructor. It derives exact query/candidate order, primary/repeat UUIDs, anchor order, delayed repeat slots, ordinals, nonterminal placement, and nonadjacency from the frozen presentation, session UUID, and participant-code digest. Formal collection delegates to that constructor at `src/scouting/storage/expert_study.py:707-722`.

The evaluator no longer trusts the protected envelope's ordering metadata. At `src/scouting/evaluation/expert_relevance.py:337-423` it revalidates participant/session/authority chronology, independently rebuilds the expected tuple from the frozen presentation plus the submitted session UUID and eligibility-bound participant digest, and requires exact tuple equality before metric access.

Independent direct evidence for participant fixture zero was:

```text
repeat ordinals:       [31, 77]
intervening primaries: [27, 60]
terminal kind:         primary
adjacent repeats:      false
```

Terminal, reordered, adjacent, under-delayed, wrong-ID, and participant-substituted schedules each returned `FAIL / INTEGRITY_FAILURE:formal participant-keyed presentation schedule mismatch`. A wrong repeat reference was rejected earlier by the formal submission contract because it did not preserve primary query/candidate identity. The retained negative fixtures at `tests/unit/test_w10_expert_relevance_evaluation.py:354-401` cover every required substitution class, and the real store/evaluator fixtures now use the exact constructor rather than terminal repeats.

No participant-facing repeat identity is introduced: the constructor uses only the participant-safe presentation bundle, and the browser projection remains free of origin, rank, score, protected query-pack fields, presentation kind, and repeat linkage.

### W10-IR-07 — CLOSED — lift has signed exact two-arm evidence

`RateContrastEvidence` at `src/scouting/contracts/expert_relevance.py:864-882` retains retrieved and control relevant/rated counts plus rates and verifies each arm against its declared counts. `MetricValue` at `src/scouting/contracts/expert_relevance.py:885-921` now permits a signed numerator, requires the two-arm evidence exactly for a supported lift, reconstructs the exact `Fraction(retrieved) - Fraction(control)`, and requires the reported float and reduced signed numerator/denominator to match that fraction.

The evaluator constructs retrieved/control fractions and the signed contrast at `src/scouting/evaluation/expert_relevance.py:953-962`, then retains the exact signed fraction and both arms at `src/scouting/evaluation/expert_relevance.py:1004-1017`. Independent direct probes reproduced:

| Case | Lift fraction | Retrieved evidence | Control evidence |
|---|---:|---:|---:|
| Positive | `1/1` | `200/200` | `0/200` |
| Zero | `0/1` | `200/200` | `200/200` |
| Negative | `-1/1` | `0/200` | `200/200` |
| Unequal denominators | `1/1` | `199/199` | `0/200` |

The positive/zero/negative parameterization and unequal-denominator case at `tests/unit/test_w10_expert_relevance_evaluation.py:548-622` independently reconstruct the contrast from the retained components and require the signed reduced fraction. Aggregate two-arm evidence is safe to retain; it exposes no participant row, candidate rating, free text, or protected-label path into modeling, ranking, features, or serving.

### Regression and new-finding disposition

- **P0:** none open and none newly found. No formal labels or new consumer path enter model, feature, ranker, serving, or W09 authority.
- **P1:** none open and none newly found. Exact schedule substitution now fails before metric access; the retained runtime, local-only, repeat-denominator, and global one-use boundaries remain intact.
- **P2:** none open and none newly found. Signed lift evidence is exactly reconstructible; chronology and append-only pre-submit correction remain intact.
- **P3:** none open and none newly found. No actionable low-severity regression was identified in the touched surfaces.

The six findings already closed at `fcbd4f9` remain closed. The current presentation digest is consistently pinned in storage, evaluator, service startup, verification reports, browser authority, and the no-formal-evidence status. The old remediation digest remains only in this review's historical narrative. No W10 working or run evidence artifact exists.

### Commands and results

All uv-based checks used `UV_CACHE_DIR=/private/tmp/w10-final-review-uv-cache` with `uv run --no-sync`; no resolution or installation occurred.

- Frozen-authority contracts, full evaluator unit suite, full evaluator integration suite, exact formal store journey, and both retained post-W04 multi-cache collectors: **44 passed**, one Starlette/httpx deprecation warning, 7.61 s.
- Full local study-console integration suite, including append-only correction and formal/pilot separation: **5 passed**, one identical deprecation warning, 1.45 s.
- W10 web unit suite, including remote-peer/localhost-Host denial and frozen digest loading: **6 passed**, one identical deprecation warning, 0.47 s.
- W10 Playwright narrow-screen pilot/resume/submit/detach and exact-approval/formal-entry journeys: **2 passed**, 6.75 s. These required the normal loopback-bind permission.
- Focused Ruff over the touched W10 contracts, storage, evaluator, builder, and tests: passed.
- Focused mypy: three core source files passed; the builder passed separately.
- Focused Bandit over the four touched implementation/build files: passed.
- Standard-library frozen-digest probe: declared and computed presentation projection digests matched; all three schedule-policy mutations changed the digest.
- Direct schedule/lift probe: six evaluator schedule substitutions failed with the exact integrity reason; wrong-reference construction failed contract validation; all four signed lift cases reconstructed exactly.
- Pure CLI status: `INSUFFICIENT_EVIDENCE / FORMAL_APPROVAL_ABSENT`, presentation digest `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`, no run artifact, no result artifact.

### Formal-study truth and W11 boundary

No formal study was conducted. No human product owner approval, formal recruitment record, formal participant submission, accepted protected input, or formal run/result exists.

- **G-RW4-PROTOCOL:** awaiting separate exact human approval; not passed.
- **G-RW4-STUDY:** `INSUFFICIENT_EVIDENCE`; formal evidence absent.
- **G-RW4-RESULT:** `INSUFFICIENT_EVIDENCE`; no formal run/result artifact.
- **Overall G-RW4:** not passed.

Candidate `f07224c` is **ACCEPTED for W10 engineering readiness** with zero open P0–P3 findings. Under `docs/architecture/w10-expert-relevance-validation.md:92-94`, that does not close W10. W11 must not begin until the separate human protocol approval, formal study, retained tri-state result, and remaining W10 closure authority are complete.
