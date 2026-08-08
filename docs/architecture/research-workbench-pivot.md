# Research workbench pivot

- Decision: accepted
- Date: 2026-08-05
- Scope: product direction, active phase ordering and claim boundary
- Supersedes: W08 staged-progression authority and workflow-first product ordering

## Context

The repository was intended to demonstrate an ML-assisted football player research system
that could later be connected to a licensed current-data provider. W04 established a
governed historical Wyscout data spine, W05 established feature/retrieval contracts and W07
established a local evidence application. The interactive demonstrations, however, used a
small synthetic candidate catalogue.

W08 then made authentication, role switching, brief revisions, shortlist state changes,
manual audit evidence and a multi-participant study the visible product journey. Direct use
of that pilot showed a product mismatch: the user was performing administrative mechanics
without receiving useful real-player ML research.

## Decision

The primary product is a provider-neutral ML research workbench:

`governed dataset → exemplar/profile query → ranked players → evidence and comparison → evaluation → reproducible report`

W08 is stopped as an active product path. Its code, tests and evidence remain intact as a
dormant optional collaboration module. No further W08 participant recruitment or T7/G-W08
completion is required to build the research workbench.

W09 is redesigned as `Historical-player ML research workbench` and depends on accepted W07
plus this explicit product authority. It does not depend on W08 acceptance.

## Architectural consequences

### Data

- Use the retained historical Wyscout 2017/18 governed source now.
- Materialise one versioned row per eligible player-season/window from canonical actions,
  with minutes, coverage, lineage and temporal cutoffs.
- Reconcile the eligible matrix with the known source universe and document every filter.
- Do not treat the accepted one-player W04 Gold proof as population coverage.
- Do not serve synthetic candidates outside automated test mode.

### Provider abstraction

Each source adapter must ingest an authorised snapshot, map provider identities and events
to canonical tables, declare available concepts and retain rights/version/checksum lineage.
Features, models and the research UI consume only canonical contracts.

A future licensed current source requires new explicit data-rights, credential and network
authority; an adapter; mapping/capability/identity tests; a full derived-artifact rebuild;
and a coverage/parity review. Provider interchangeability is an architectural boundary,
not an assertion that providers expose equivalent concepts.

### ML and evaluation

- Establish a transparent scaled-distance/cosine baseline over the full eligible population.
- Display feature contributions, contrasts, missingness, cohort and applicability.
- Freeze query/evaluation sets before comparing PCA, learned-metric or embedding challengers.
- Promote a challenger only for measured gain without loss of reproducibility, coverage,
  temporal safety or explanation quality.
- Missing expert relevance evidence blocks a positive relevance claim, not development of
  an honestly labelled historical research system.

### Product experience

The default browser experience contains dataset, query, results, compare and experiment
areas in one coherent workspace. A first-time user can run an exemplar query over real
historical players without fictional sign-ins, role switching, manual revision management
or audit-form entry.

### Provenance

Experiment provenance is automatic. Every run binds source, canonical data, features,
model/index, code, query, filters, population, seed, outputs, metrics, warnings and artifact
checksums. User annotations supplement this record; they do not create it.

## Existing work disposition

| Foundation | Disposition |
| --- | --- |
| W04 ingestion, identities, lineage, temporal controls | Reuse and extend to the full eligible player population. |
| W05 contracts, feature/model registry and serving path | Reuse with governed historical artifacts. |
| W07 search/profile/compare UI foundations | Recompose as the core research workspace. |
| W08 auth, workflow, audit, concurrency and exports | Preserve, test and keep dormant. |
| W08 synthetic pilot | Stop; retain as a product-direction finding, not acceptance evidence. |
| Synthetic datasets | Automated tests and failure-path fixtures only. |

## Acceptance gates

1. **G-RW1 Population:** reconciled, unique, versioned and temporally valid historical
   player feature matrix; explicit coverage and no synthetic product rows.
2. **G-RW2 Retrieval:** deterministic full-population ranking, inspectable contributions,
   correct eligibility, and identity/leakage/stale-version protection.
3. **G-RW3 Workbench:** understandable end-to-end browser journey ending in a replayable
   experiment/report, without required role switching or terminal use.
4. **G-RW4 Relevance (active W10 gate):** real eligible football-domain experts assess a
   frozen query set under the user-approved digest-bound protocol. The retained formal result is
   PASS, FAIL or INSUFFICIENT_EVIDENCE. Mechanics pilots and synthetic responses cannot count.
   This gate is required before positive expert relevance or recruitment-usefulness claims.

The 2026-08-06 W10 mechanics pilot found that presentation v1 showed evidence quantity but not
playing evidence, so it could not support the intended expert role/style judgement. No formal v1
response was collected. V1 is retained but withdrawn for formal use, and W10 has returned to
rework under `docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`. G-RW4 now
requires a freshly approved v2 evidence presentation after its separate sufficiency pilot.

W10 implementation, human-boundary and checkpoint semantics are controlled by
`docs/architecture/w10-expert-relevance-validation.md` and its active v2 addendum.

## Non-authority

This decision does not authorise provider access, credentials, scraping, remote services,
cloud infrastructure, deployment, publication, a recruitment recommendation, a current-
market claim or a shadow recruitment pilot.
