# Scouting Intelligence

A local-first ML research workbench for exploring player resemblance in football data —
built to answer one question rigorously: *given a player I'm interested in, who in this
dataset plays a similar role or style, and how confident should I be in that comparison?*

The project is also a deliberate exercise in **not overclaiming**. Every result ships
with the feature-level evidence behind it, every experiment is automatically
reproducible, and no similarity score is presented as a recruitment recommendation
until it has survived independent domain-expert review.

## What it does

1. **Select a dataset and population** — choose a governed historical season/window and
   the eligible player pool within it.
2. **Query** — pick a real player as an exemplar, or hand-declare a weighted playing
   profile of your own.
3. **Retrieve** — rank every eligible candidate by transparent, explainable distance
   from the query, not a black-box score.
4. **Inspect the evidence** — see exactly which features drove each ranking, how
   candidates contrast with the exemplar, and where the data is thin or missing.
5. **Compare and save** — line candidates up side by side and save the run as a
   reproducible, replayable experiment.

## What's implemented

- **A governed historical dataset spine.** Built from a real Wyscout 2017/18 dataset
  (1,826 matches, 3M+ raw match actions, 142 teams, 3,603 players), reconciled down to a
  clean, versioned feature matrix of ~1,965 eligible players.
- **A transparent retrieval engine.** Sixteen per-90 features (passing, chance creation,
  defensive actions, duels, discipline, and more) feed a weighted Euclidean/cosine
  similarity search over the full eligible population — every contribution is
  inspectable, nothing is hidden behind a single similarity number.
- **A working end-to-end research UI.** Dataset selection, query, ranked results,
  per-feature evidence, candidate comparison and saved experiments all live in one
  browser workspace — no logins or manual audit steps required to explore the data.
- **Full experiment provenance.** Every query automatically records the data snapshot,
  feature/model version, filters, random seed, results and warnings, so any experiment
  can be exactly reproduced later.
- **A dormant collaboration module.** An earlier product direction built out
  authentication, role-based review, shortlists, an audit trail and export tooling.
  It's fully implemented and tested but currently unused — kept in reserve for if/when
  a team review workflow is needed.
- **A fully local runtime.** SQLite for operational/audit data, Parquet with DuckDB and
  Polars for analytics, and in-process vector search. No Docker, no Postgres, no Redis,
  no external services — the whole system runs from a single checked-out folder.

## Where it's headed

The retrieval workbench works end to end, but a real similarity score is only useful if
domain experts agree the comparisons actually make football sense — not just that the
underlying stats look similar. The project is currently working through exactly that
problem:

- **Redesigning what evidence reviewers see.** An early pilot showed that names, teams
  and minutes played weren't enough for an expert to judge a comparison — reviewers need
  real playing evidence (passing patterns, territory, shooting and defensive output),
  not just the raw inputs the model itself used. That richer, position-aware evidence
  presentation is in active development.
- **Running an independent expert evaluation.** Once the new evidence presentation is
  built and piloted, a panel of football-domain reviewers will formally assess a frozen
  set of comparisons, producing a clear pass/fail/insufficient-evidence result before any
  claim of real-world relevance is made.
- **Expanding beyond the historical demonstration dataset.** The data layer is built
  provider-neutral by design, so a licensed current-season data source can be plugged in
  through an adapter without touching the retrieval, evaluation or UI layers — once the
  expert-relevance work above justifies making that investment.

## What this project doesn't claim (yet)

This is intentionally conservative: the system does not predict transfer or performance
outcomes, does not automate or approve recruitment decisions, and does not yet claim
expert-validated football relevance — that claim is gated behind the independent
evaluation described above. It's an evidence-generating research tool, not a scouting
oracle.

## Tech stack

- **Python 3.12**, dependency-managed end to end with [`uv`](https://docs.astral.sh/uv/)
- **FastAPI** + **Jinja2** for the web workbench
- **DuckDB**, **Polars** and **PyArrow** for the analytical data layer
- **scikit-learn** for the retrieval baseline
- **SQLAlchemy** + **SQLite** for local operational/audit storage
- **pytest**, **mypy**, **ruff** and **bandit** for testing, type-checking, linting and
  security scanning (100+ test modules)

## Getting started

```bash
uv sync --locked --all-groups
uv run python scripts/apply_migrations.py
./scripts/start_w09_research_workbench.command
```

Then open `http://127.0.0.1:8769/` and keep the launcher terminal running (`Ctrl-C` to
stop it).

Before interpreting results, it's worth reading:

- `docs/runbooks/w09-research-workbench.md` — setup, walkthrough and how to read the
  numbers correctly;
- `docs/dataset-cards/w09-historical-player-window-v1.md` — data source, population,
  eligibility and known limitations; and
- `docs/model-cards/w09-historical-retrieval-v1.md` — how the retrieval and scaling
  actually work, and what it's evaluated for.

## Local verification

```bash
uv sync --locked --all-groups
uv run python scripts/apply_migrations.py
uv run python -c "import scouting"
uv run ruff format --check .
uv run ruff check .
uv run mypy src/scouting
uv run pytest -q
```

## Documentation

The `docs/` directory has the full detail behind the summary above: architecture
decisions in `docs/adr/`, dataset and model cards in `docs/dataset-cards/` and
`docs/model-cards/`, and operational runbooks in `docs/runbooks/`.
