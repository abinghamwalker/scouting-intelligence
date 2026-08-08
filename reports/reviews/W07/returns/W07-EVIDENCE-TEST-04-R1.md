# Subagent return

## Task

- task_id: W07-EVIDENCE-TEST-04-R1
- objective: Encode executable integration and genuine real-browser acceptance evidence for every W07 semantic, parity, state, local-only, and accessibility predicate without changing production code.

## Files changed

- tests/integration/test_w07_local_evidence_app.py
- tests/e2e/test_w07_local_evidence_playwright.py
- reports/reviews/W07/returns/W07-EVIDENCE-TEST-04-R1.md

## Summary

- Added integration witnesses for the exact 18-record catalogue and filter states; known-record evidence; malformed/unknown identity fail-closed behaviour; public single/batch serving and `LoadedM0Artifact.score` spies; direct/batch byte and result-digest identity; the four exact W05 artifact SHA-256 values; result authority, explanation, reason, confidence, limitation and W04 evidence; closed states; response policy headers; local stylesheet; local URL boundary; and prohibited claim labels.
- Added genuine `playwright.sync_api` tests which run the real local Chrome binary against loopback uvicorn. They cover 1440x900, 390x844, and 320x700 layouts; zero external hosts; the specified activation journeys; skip-link and keyboard focus; landmarks, headings, controls, captions, scoped headers and details; and distinct honest state pages. Browser locator waits are bounded to three seconds so a missing required control returns a concrete failing node promptly.
- Retained all failing assertions. No production/template change was made.

## Tests run

- command: `uv run ruff format --check tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  - exit status: 0
  - result: both files already formatted.
- command: `uv run ruff check tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  - exit status: 0
  - result: all checks passed.
- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py tests/e2e/test_w07_local_evidence_playwright.py`
  - exit status: 1
  - result: 8 failed, 3 passed, one pre-existing TestClient deprecation warning. The retained failing nodes are:
    - `tests/integration/test_w07_local_evidence_app.py::test_catalogue_has_exactly_18_stable_labels_and_all_filter_modes` — labels are renumbered by a filtered result, so `Synthetic candidate 04` cannot resolve the accepted UUID.
    - `tests/integration/test_w07_local_evidence_app.py::test_known_player_displays_exact_feature_role_cutoff_and_lineage` — `player.html` has a Jinja syntax error at its `.items()` loop and the known-player page cannot render.
    - `tests/integration/test_w07_local_evidence_app.py::test_result_displays_pinned_result_context_exact_digests_and_explanation_values` — result output omits the accepted lineage identity (and the test retains assertions for all required result authority/explanation context).
    - `tests/integration/test_w07_local_evidence_app.py::test_closed_states_headers_stylesheet_local_only_and_claim_boundary` — prohibited claim label text remains in served page content.
    - `tests/e2e/test_w07_local_evidence_playwright.py::test_real_browser_has_no_body_horizontal_overflow[viewport1]` — body overflow at 390x844.
    - `tests/e2e/test_w07_local_evidence_playwright.py::test_real_browser_has_no_body_horizontal_overflow[viewport2]` — body overflow at 320x700.
    - `tests/e2e/test_w07_local_evidence_playwright.py::test_real_browser_exact_activation_journeys_and_local_requests` — required `Search synthetic-development evidence` control is absent at the first activation.
    - `tests/e2e/test_w07_local_evidence_playwright.py::test_real_browser_keyboard_landmarks_controls_and_distinct_states` — activating the skip link does not move focus to `#main-content`.
- command: `uv run pytest -q tests/integration/test_w07_local_evidence_app.py::test_malformed_or_unknown_identity_is_unavailable_without_serving_or_scoring tests/integration/test_w07_local_evidence_app.py::test_retrieval_and_comparison_use_only_public_serving_paths_and_shared_scorer -x`
  - exit status: 0
  - result: 2 passed. Invalid identities do not invoke either public serving path or scorer; retrieval invokes only the direct public API, comparison only the batch public API, shared scorer calls are observed, exact artifact files remain unchanged, and direct/batch results are byte/digest identical.

## Artifacts/evidence

- `tests/integration/test_w07_local_evidence_app.py`
- `tests/e2e/test_w07_local_evidence_playwright.py`
- Exact W05 artifact SHA-256 authority asserted by the tests: `arrays.npz=73374ba529e2628112b7886e549e2b570883781544cd65478ea96a838975dfc6`, `candidate-universe.json=2a8bd89b9715e2a0349e2aaba22f890333139a5142b931ae4e844aaa9bc5807e`, `configuration.json=d4d6839382267f3eb1cb8d767e01f833e106332e314ead886e9f08997681c006`, `manifest.json=c88f101211d8e26c06622021a4d9333ce1c0e9217999a100aee71812446f443a`.

## Risks

- Production does not currently meet the retained W07 acceptance contract; this is intentionally a failing evidence suite pending a production-owned correction.
- The genuine browser witnesses depend on the existing local Chrome path required by the packet; no browser download, Node command, external request, or external endpoint was used.

## Follow-up items

- Production owner: correct the `player.html` Jinja loop, preserve catalogue labels across all filter/search paths, render the complete pinned authority/result/explanation context, remove forbidden claim labels, eliminate mobile/narrow overflow, provide the exact required journey control, and make the skip target programmatically focusable.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
