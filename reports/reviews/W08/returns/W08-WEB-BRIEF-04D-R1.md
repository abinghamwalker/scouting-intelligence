# W08-WEB-BRIEF-04D-R1 return — blocked

## Task and invariant

`W08-WEB-BRIEF-04D-R1`: a role-brief status change must not rewrite requirements,
and a retrieval link may be persisted only from a fully pinned, successful local W05/W07
public-serving replay. Random, invented, or substituted result evidence is forbidden.

## Exact user-boundary-safe blocker

The local M0 public serving path supports exemplar-mode replay with
`resolved_query.query_player_id = None`.  The accepted shared
`ReplayableRetrievalLink` contract instead requires a non-null `query_player_id` and
does not retain `exemplar_player_ids`. Persisting `None`, or silently replacing it with
one exemplar, would be false replay evidence. This packet forbids the required shared
contract/migration/workflow change, so the exact exemplar deliverable cannot be completed
without violating its invariant. No workaround was attempted.

## Partial bounded work retained

- `src/scouting/web/w08.py` now has a deterministic W08-to-W07 public-serving replay
  builder for query-player compatible briefs. It rebuilds a fully pinned request using
  the actual tenant, brief ID/version, resolved-query digest, registered W05 artifact
  and W07 core; it uses the result's real request/result/run IDs, result digest and
  dependency-lineage hash instead of random placeholders.
- Status-version construction preserves persisted responsibilities, constraints,
  preferences, exemplars and original submission timestamp.
- The brief form parser accepts multiple responsibility codes, one bounded constraint,
  transparent preference weight and optional exemplar IDs, but this packet stops before
  presenting it as a completed exemplar workflow.
- No model fitting, protected W06 output access, protected W06 rerun, external call or
  provider/model call occurred.

## Evidence performed before stop

```text
uv run mypy src/scouting/web/w08.py
# exit 0 before the final form-parser partial edit
uv run pytest -q tests/integration/test_w08_local_workflow_app.py::test_synthetic_automated_shortlist_assignment_observation_and_conflict
# exit 0; 1 passed, one existing Starlette TestClient deprecation warning
```

The focused journey initially exposed the forbidden placeholder replay because its
responsibility was not a W05 code. Replacing that synthetic test input with the accepted
`progress_through_pressure` code yielded the deterministic local replay witness. This
does not resolve exemplar mode or constitute acceptance.

## Required follow-up

Master must issue a serial shared-contract correction that can represent the exact
mutually exclusive query-player versus exemplar replay inputs (and retain the selected
mode) without fabricating a query player. After that correction, issue a fresh web
packet and re-run the full packet checks.

No Git operations, dependency/lock changes, protected-output access, network/external
service/model call, delegation, or edits outside the packet's allowed paths were made.
