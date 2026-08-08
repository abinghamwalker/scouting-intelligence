# Handoff prompt — SOTA / delivery-grade uplift pass

Run this **after** the remedial pass has landed and **before** W10 resumes.
Budget: **12 hours of implementation time.** Study execution is out of scope and not counted.

---

```
You are doing a methodological and delivery-readiness uplift on this repository. This is NOT a
defect-fixing pass — that already happened. Read these first, in order:

  1. `AGENTS.md` — binding. The master owns every Git operation, phase gate, checkpoint and tag.
     Do not run any Git command that mutates state. Leave changes in the working tree and report.
  2. `docs/reviews/cross-phase-code-review-2026-08-06.md` — the prior defect review and its two
     appendices, including the artifact digest/rebuild cascade table. You must not contradict or
     re-litigate it.
  3. `docs/architecture/` — ADR 0004, the research-workbench pivot, and the W10 v2 addendum.

## Goal

Make this system measurably better at its actual job — helping a researcher find and justify
historical player comparisons — and make it defensible as a client deliverable. Prioritise
methodological quality of the retrieval itself over code aesthetics.

## Hard constraints — a proposal that violates any of these is out of scope

- **12 hours total implementation.** The full test suite is ~36 minutes per run; an artifact
  rebuild cascade costs more. Budget verification time explicitly, not as an afterthought.
- **No rewrite.** No new frameworks, no restructuring of the phase/packet model, no new services.
- **Local-only, provider-neutral, container-free (ADR 0004).** No cloud, no external API or model
  call, no hosted vector DB, no new required service, no network at runtime. Do not propose
  foundation-model embeddings, hosted inference, or anything requiring credentials.
- **No dependency additions** unless you can justify one specifically and it is already a
  transitive dependency. `pyproject.toml` and `uv.lock` are master-owned.
- **W06 remains NO_GO.** No change may enable, imply, or make easier a positive claim about
  football relevance, recruitment usefulness, player value, or future performance. Retrieval
  quality improvements are in scope; claims about them are not. If a change would strengthen a
  claim, it must also strengthen the evidence for that claim or it does not ship.
- **Respect the digest cascade.** Touching `m0/scoring.py` (index rebuild),
  `features/historical.py` (matrix + index), or `data_products/wyscout/historical.py` /
  `sources/wyscout_historical.py` (canonical + everything) forces rebuilds. A matrix rebuild also
  invalidates the literal pins in `configs/evaluation/w10-expert-evidence-presentation-v2.json`
  and forces a W10 threshold/stability revalidation. Cost that honestly in every estimate.
- **W10 is next.** Anything that forces a W10 re-pin must be flagged loudly and sequenced with the
  user, not absorbed silently.

## Measured baseline — use this, do not re-derive it

Taken on the built production artifacts. A prior review assigned performance priorities by
inferring population scale and was wrong; do not repeat that.

  Population        1,975 rows / 1,965 players / 5 leagues / 16 features / 2017-18
  Positions         GK 136, DF 713, MD 711, FW 415
  Cold boot         1.63s (load + full verification)
  search_players    0.1ms
  execute_query     6.0ms weighted_euclidean, 9.5ms weighted_cosine
  Rows scored/query 408 (retrieval is single-competition by design)
  Test suite        3,091 passed in ~36 minutes

**Performance is not a problem at this scale.** Do not propose ANN indexes, caching layers,
vectorisation, or async. Those are solved-by-smallness. Spend the budget on method and evidence.

## Leads worth costing — verify each yourself, do not take them as conclusions

These came out of the prior review and the measurement above. Confirm or refute each against the
code before proposing anything based on them. Finding one of them wrong is a useful result.

- The robust scaler is fit **globally** across all positions, not within position, while W10's
  evidence layer computes percentiles **within** position. Retrieval and evidence may therefore
  disagree about what "typical" means.
- All 16 features are **volume counts per 90**. Numerator pairs exist (`accurate_passes`/`passes`,
  `shots_on_target`/`shots`, `duels_won`/`duels`) but no efficiency ratio is exposed — arguably the
  first thing a scout looks at.
- There is **no small-sample treatment**. A per-90 rate from ~500 governed minutes is treated
  identically to one from ~3,000. Empirical-Bayes / James-Stein shrinkage toward a position mean is
  standard practice for rate statistics.
- The 16 features are **strongly correlated** (`passes`, `accurate_passes`, `touches` move
  together). Weighted Euclidean over an uncorrelated-assumption basis implicitly over-weights
  correlated clusters. Mahalanobis distance or PCA/ZCA whitening is the textbook correction and is
  trivially cheap on a 1,975 x 16 matrix.
- **Goalkeepers are scored on outfield-action features.** 136 GKs across five leagues, on a feature
  set built from passes, shots, duels, interceptions and clearances.
- Retrieval is **single-competition** (`filters.competition_id` is required). Cross-league
  comparison — plausibly the single most useful scouting capability — is not reachable.

You are not limited to this list. Blue-sky proposals are welcome if they survive the constraints.

## Deliverable — two phases, and you stop between them

### Phase 1 (target ~1 hour): a ranked, costed options paper. No code.

Write `docs/reviews/uplift-options.md` containing, for each candidate change:

  - what it changes, in one paragraph, at file level
  - the methodological justification, with a citation or a standard-practice reference where the
    technique is established, and an honest statement of what it does NOT fix
  - **estimated implementation hours**, including verification and any rebuild cascade
  - which digest tier it touches and whether it forces a W10 re-pin
  - how you would *demonstrate* the improvement — what measurement, on what data, showing what.
    A proposal with no proposed evidence is not a proposal.
  - risk of regression, and what could go wrong

Then give a recommended **12-hour package** and an explicit **not-doing list** with reasons. The
not-doing list matters as much as the package; I want to know what you rejected and why.

Rank by (delivery value / hour), not by intellectual interest.

**Stop and present the paper. Do not start implementing.** I will choose the package.

### Phase 2: implement only the approved package.

Work item by item. After each: run the bounded checks, report what changed, what you measured, and
whether the demonstration you promised in Phase 1 actually holds. If it does not, say so — a
technique that did not help is a real finding and I would rather have it than a silent success
claim.

Reserve the final ~2 hours for full verification and for writing up what shipped.

## Delivery artifacts — treat as first-class, not documentation chores

`docs/model-cards/` and `docs/runbooks/` are both **empty**, and there is no launcher for the W09
workbench (only `start_w08_study_console.command`, which serves the dormant W08 module). A
researcher currently cannot start the product without reading source.

Include in your Phase 1 costing:
  - a W09 model card (intended use, population, method, evaluation, limitations, out-of-scope
    claims, the W06 NO_GO, and the single-competition retrieval scope of 408/1,975 rows)
  - a W09 dataset card for the delivered population
  - a runbook and a launcher for the workbench

These are tier 0, force no rebuild, and are the difference between a repository and a deliverable.
Rank them honestly against the methodological work rather than assuming either wins.

## Verification

  uv run ruff format --check . && uv run ruff check .
  uv run mypy src/scouting
  uv run pytest -q                      # ~36 min; run in background, do not block serially
  uv run python scripts/verify_local_only.py

Establish your own green baseline before changing anything. Anything failing beyond that baseline
is a regression you introduced. After any rebuild, confirm `scripts/evaluate_w09_retrieval.py`
passes and report saved-experiment replay status explicitly.

## Working style

Be honest about uncertainty. If a technique is standard but you cannot demonstrate it helps on
1,975 rows, say that. If a lead above is wrong, say that. Do not pad the options paper to look
thorough — a short paper with three well-justified options beats twelve speculative ones.
```

---

## Notes for the human

- Phase 1 is deliberately capped at ~1 hour and gated on your approval. With a fixed 12-hour
  budget the dominant risk is an agent spending it all on the first idea it has.
- The prompt explicitly forbids performance work. At 6ms/query that would be pure waste, and
  "optimise the hot path" is the default reflex.
- The measured baseline is handed over precisely so the agent does not repeat the earlier mistake
  of inferring scale and mis-prioritising from it.
- Every lead is framed as "verify or refute", not as an instruction. Several may be wrong.
