# Subagent return

## Task

- task_id: W07-PRESENTATION-03-R1
- objective: Render each master-frozen W07 context as accessible, responsive, local-only and evidence-honest presentation surfaces.

## Files changed

- apps/web/templates/w07/_authority.html
- apps/web/templates/w07/base.html
- apps/web/templates/w07/landing.html
- apps/web/templates/w07/search.html
- apps/web/templates/w07/player.html
- apps/web/templates/w07/result.html
- apps/web/templates/w07/evidence.html
- apps/web/templates/w07/state.html
- apps/web/static/w07/app.css
- reports/reviews/W07/returns/W07-PRESENTATION-03-R1.md

## Summary

- Added a reusable Jinja document shell and evidence-authority primitives, including a high-priority NO_GO / MISSING_EXPERT_RELEVANCE_EVIDENCE banner and accessible digest disclosure.
- Rebuilt all assigned W07 surfaces with landmark structure, current navigation signal, skip link, explicit governed states, GET search controls, responsive evidence tables, genuine compare links, W04/W05/W06 evidence boundaries, local design tokens and print/reduced-motion support.
- Presentation uses no external assets, scripts, webfonts, network sources or client-side filtering/scoring. It does not display a match percentage or blended score and makes no recommendation, transfer, outcome, price, value, approval, validation or production-fitness claim.

## Tests run

- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py`
  - exit status: 0
  - result: 8 passed (one upstream Starlette deprecation warning).
- command: `uv run ruff format --check .`
  - exit status: 0
  - result: 897 files already formatted.

## Artifacts/evidence

- apps/web/templates/w07/base.html
- apps/web/templates/w07/_authority.html
- apps/web/static/w07/app.css

## Risks

- The interface deliberately preserves the W05/W06 evidence ceiling: generated synthetic-development evidence remains resemblance-only and LIMITED, while expert relevance evidence is absent.

## Follow-up items

- none.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
