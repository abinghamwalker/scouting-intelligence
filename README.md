# Scouting Intelligence

Local-only, container-free, provider-neutral football ML research project.

## Current checkpoint scope

W09 is closed as the historical-player ML research workbench. The active phase is W10
presentation-v2 rework: its first mechanics pilot proved that names and minutes do not
supply enough football evidence for an expert role/style judgement. No formal response was
collected. The retained v1 approval and incomplete pilot cannot unlock v2.

W08's authentication, role workflow, audit and export implementation is preserved as a
dormant optional module after the 2026-08-05 product pivot. It is not the core journey and
its participant study no longer gates research implementation. Synthetic player data is
restricted to automated tests; interactive results must use governed historical artifacts.
See `docs/architecture/research-workbench-pivot.md` and
`docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`.

## W09 quick start

The W09 workbench remains available for local historical-resemblance research while W10 remains
`REWORK`. From the repository root, prepare the locked environment and start the fixed-loopback
launcher:

```text
uv sync --locked --all-groups
./scripts/start_w09_research_workbench.command
```

Open `http://127.0.0.1:8769/` and keep the launcher terminal open. Press `Control-C` to stop it.
The launcher accepts one optional unprivileged port but never a different host.

Each query scores all filter-admitted rows in one selected target competition and season before
limiting results. An exemplar may come from another competition; a combined all-leagues candidate
pool is not provided. Raw inputs use a conservative lower bound minute denominator and global
median/IQR scaling. Distances, weights and contributions are not a percentage or calibrated match
score. The corrected `goals_per90` semantics exclude event 9 save-attempt rows.

Before operating or interpreting results, read:

- `docs/runbooks/w09-research-workbench.md` — setup, walkthrough, local writes, exact number
  interpretation and fail-closed troubleshooting;
- `docs/dataset-cards/w09-historical-player-window-v1.md` — source, population, eligibility,
  features, rights and limitations; and
- `docs/model-cards/w09-historical-retrieval-v1.md` — scaling, retrieval geometry, evaluation,
  experiment compatibility and prohibited claims.

Package A changes live matrix/index pins. Pre-uplift experiments must report
`INCOMPATIBLE_PINS`; never migrate or re-pin them. The dataset and model cards record the
independently reproduced post-cascade identities.

## Local toolchain

- Python is pinned to 3.12 by `.python-version` and `pyproject.toml`.
- `uv` owns the single root environment at `.venv` and the committed `uv.lock`.
- Every Python command is run through `uv run`; direct `pip` use is not an
  authority for this project.
- SQLite under `data/working/` is the embedded operational/audit store and requires no
  port, service process, password or container.
- Parquet with DuckDB/Polars is the analytical store; vector retrieval uses versioned
  local artifacts and in-process Python.
- Redis, PostgreSQL, pgvector, Compose and required external services are prohibited by
  ADR 0004 unless the user explicitly approves a new architecture decision.
- Git is local-only on `main`, with zero remotes and an installed pre-push hook
  that always rejects pushes.

## Local verification

```text
uv sync --locked --all-groups
uv run python scripts/apply_migrations.py
uv run python -c "import scouting"
uv run ruff format --check .
uv run ruff check .
uv run mypy src/scouting
uv run pytest -q
uv run python scripts/install_local_git_guards.py --check
uv run python scripts/verify_local_only.py
git diff --check
git remote
```

Historical phase evidence remains under `reports/`; ADR 0004 is the current runtime
authority.
