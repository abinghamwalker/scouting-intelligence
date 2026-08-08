# Subagent return

## Task

- task_id: `W09-REPRODUCIBLE-REPORT-04B-R1`
- objective: Implement deterministic, content-addressed local JSON/HTML W09 research reports that preserve the exact query, result, comparison, population, explanation, version, rights, limitation, and claim-boundary evidence required for save/replay.

## Files changed

- `src/scouting/reporting/__init__.py`
- `src/scouting/reporting/research.py`
- `tests/unit/test_w09_research_reporting.py`
- `tests/integration/test_w09_research_report_persistence.py`
- `reports/reviews/W09/returns/W09-REPRODUCIBLE-REPORT-04B-R1.md`

## Summary

- Added one strict `render_research_report` boundary that freshly validates an exact `ResearchQueryResult`, optionally freshly validates and binds an exact `ResearchComparison`, requires an explicit UTC report clock, and requires explicit retained-source rights classification, attribution, and limitations.
- Added immutable `RenderedResearchReport` output containing exact `bytes` plus a valid `ResearchReportDescriptor`. The descriptor SHA-256 and `sha256/<prefix>/<digest>.<format>` path are computed from the final report bytes.
- Added canonical JSON output using the repository canonical JSON encoder. It exposes the full request, exemplar/profile mode, method, weights, filters, all version pins and evidence digests, full-population accounting, deterministic ranked candidate contracts, raw/scaled/normalised contribution operands, warnings, candidate and report limitations, optional exact comparison rows, attribution, and the closed historical-only claim boundary.
- Added deterministic self-contained UTF-8 HTML with readable authority, query, pins, population, ranked explanations, comparison, warning, and limitation sections. Every data value is HTML escaped; a restrictive local-only CSP is present; there are no scripts, links, images, or remote resources. The canonical semantic report JSON is embedded as escaped text for complete inspection.
- Reused the accepted storage content-address helper so the renderer and `ResearchExperimentStore` enforce the same report path invariant.
- Added fail-closed checks for stale/mismatched comparison result IDs/digests/query digests/pins, non-candidate comparison grains, row/candidate identity drift, mutated contracts, invalid clocks, formats, and rights classifications.
- Added fixture-only contract tests for stable JSON/HTML bytes, canonical JSON, escaping, complete evidence surfaces, exact descriptor bindings, claim limits, and strict comparison binding.
- Added JSON and HTML integration tests proving generated descriptors and exact bytes save, load, list, and round-trip through SQLite plus guarded local artifact storage.

## Tests run

- command: `uv run ruff format --check src/scouting/reporting tests/unit/test_w09_research_reporting.py tests/integration/test_w09_research_report_persistence.py`
  - exit status: `0`
  - result: `4 files already formatted`
- command: `uv run ruff check src/scouting/reporting tests/unit/test_w09_research_reporting.py tests/integration/test_w09_research_report_persistence.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `uv run mypy src/scouting/reporting`
  - exit status: `0`
  - result: `Success: no issues found in 2 source files`
- command: `uv run pytest -q tests/unit/test_w09_research_reporting.py tests/integration/test_w09_research_report_persistence.py tests/integration/test_w09_research_storage.py`
  - exit status: `0`
  - result: `21 passed in 0.46s`
- command: `uv run bandit -q -r src/scouting/reporting`
  - exit status: `0`
  - result: no findings

## Artifacts/evidence

- `reports/reviews/W09/returns/W09-REPRODUCIBLE-REPORT-04B-R1.md`
- Unit evidence: `tests/unit/test_w09_research_reporting.py`
- Persistence evidence: `tests/integration/test_w09_research_report_persistence.py`

## Risks

- Report generation intentionally does not infer current artifact availability; stale-version enforcement remains the responsibility of the accepted query/retrieval boundary before it produces the exact result supplied here, while the report preserves every supplied pin and digest without substitution.
- The HTML is designed for local inspection and uses inline CSS under a restrictive CSP. It contains no active code or remote resource dependency.
- No production report was emitted. All report payloads exercised here are ephemeral test-fixture artifacts.
- G-RW4 remains absent, so the report explicitly avoids football-relevance, future-performance, or decision-suitability claims.

## Follow-up items

- none

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
