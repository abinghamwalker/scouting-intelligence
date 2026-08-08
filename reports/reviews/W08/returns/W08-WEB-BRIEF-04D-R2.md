# W08-WEB-BRIEF-04D-R2 return

`W08-WEB-BRIEF-04D-R2` preserves the invariant that every persisted link derives from
the exact local W05/W07 replay, with neither random nor substituted identity.

Changed: `src/scouting/web/w08.py`, `tests/integration/test_w08_local_workflow_app.py`,
and this return. The web builder preserves all brief fields through status revisions,
parses typed constraints/preferences/exemplars, builds a deterministic W08 pinned
request with the real tenant/brief/version/trace, invokes the registered W07 core, and
persists replay request/result/run identities, wrapper digest, lineage digest, exact
query mode and candidate-universe version. It uses
`retrieval_result.retrieval_result_id`, not wrapper ID.

Focused checks passed: Ruff format/check, mypy, and
`uv run pytest -q tests/integration/test_w08_local_workflow_app.py tests/security/test_w08_web_security.py tests/e2e/test_w05_m0_retrieval.py`:
6 passed (one existing TestClient deprecation warning).

Residual: template expansion and explicit double-replay/candidate-allowlist HTTP
witnesses still require follow-up; do not accept this as representative-user evidence.
Weights are replay context only, not applied by W05 scoring. W06 remains
NO_GO/resemblance_only/synthetic_development_only/LIMITED/no_recommendation_evidence.

No Git, dependency/lock, protected-output, network/provider, fitting, or out-of-scope
edits occurred.
