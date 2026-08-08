# Product claim and release boundary

- Status: Accepted research-workbench pivot boundary
- Authorised: 2026-08-05
- Applies to: historical-data research implementation and future provider adapters
- Evidence status: architecture and product authority; no expert relevance, current-market
  coverage, recruitment outcome or representative-user acceptance is asserted

## Primary claim

The product is a provider-neutral ML research workbench for governed football data. It
lets a researcher:

1. select an available dataset, season/window and eligible player population;
2. choose a real exemplar player or declare a weighted football profile;
3. retrieve ranked players from that governed population;
4. inspect feature contributions, contrasts, coverage, uncertainty and limitations;
5. compare candidates and save a reproducible experiment and report.

The first model-assisted claim remains **resemblance within a declared evidence
boundary**. A high rank means that, for the recorded dataset, window, eligibility
population, feature set, weights and retrieval method, the candidate is closer to the
query on the displayed evidence dimensions than lower-ranked eligible candidates.

It does not mean that the candidate will succeed, transfer, remain available, be
affordable, provide value for money, fit a squad or be selected.

## Immediate data boundary

The retained historical Wyscout 2017/18 data is the current authorised demonstration
source. It proves the research system end to end using real historical records; it is not
current-market coverage. The source-universe report records 1,826 matches, 3,071,395
actions, 142 teams and 3,603 players. Research eligibility may produce a smaller player
population and must state the filters and reconciliation.

The accepted W04 one-row/four-feature Gold artifact proved lineage and temporal mechanics.
The accepted W05/W07 synthetic catalogues proved contracts and application seams. Neither
is the product research population. Interactive product results must come from the
governed historical feature/index artifacts; synthetic data is restricted to tests.

## Provider-neutral boundary

Downstream feature, retrieval and UI code consumes canonical football tables and
capability declarations, not provider payloads. A future licensed current-data source
requires separately authorised rights and access plus a provider adapter, schema and
concept mapping, identity reconciliation, capability tests, a complete feature/index
rebuild and coverage/parity review. It is not a URL or credential substitution.

No credential, provider network access, external service, cloud resource, deployment or
publication is authorised by this boundary.

## Evidence and reproducibility

Every experiment automatically records:

- source snapshot, canonical-data build, feature set, model/index and code versions;
- query exemplar or weights, filters, eligibility population and random seed;
- ranked results, explanations, coverage, metrics, warnings and artifact checksums;
- creation time plus any user-supplied name or research note.

The user does not need to switch fictional roles or manually record audit events. Saved
experiments may be named, annotated, cloned and exported locally.

## Users and decision authority

The primary near-term user is a football research analyst exploring and evaluating player
resemblance. Football-domain experts later assess a frozen query set under an approved
protocol before any positive relevance or recruitment-usefulness claim.

Scouts, approvers, observations, shortlists and permissioned workflow may later be offered
as an optional collaboration module. W08 code and evidence are retained for that possible
future use but are dormant and are not a prerequisite for the research workbench.

## Non-claims and prohibited uses

The product does not:

- predict or guarantee future performance, transfer or signing success, availability,
  price, value for money or squad fit;
- make, automate or approve a recruitment decision;
- claim expert relevance until the dedicated frozen-query expert gate passes;
- claim current-market coverage from historical data;
- infer, rank or optimise protected or sensitive personal characteristics;
- conceal missing evidence or uncertainty behind one authoritative percentage;
- silently substitute a synthetic catalogue, different model or stale index;
- learn outcome truth directly from clicks, saved results or uncurated workflow feedback;
- send restricted provider evidence to an external model or service.

## Release progression

The research path is evidence-gated:

- **G-RW1 Population:** full eligible historical player feature matrix, reconciled grain,
  coverage, lineage and temporal validation; no synthetic product rows.
- **G-RW2 Retrieval:** deterministic full-population retrieval with explanations, identity,
  leakage and stale-version controls.
- **G-RW3 Workbench:** coherent dataset → query → results → compare → saved experiment
  browser journey without required role switching or manual audit entry.
- **G-RW4 Relevance (active W10 gate):** independent eligible football-domain review of a
  frozen query set under the user-approved protocol. The formal result is PASS, FAIL or
  INSUFFICIENT_EVIDENCE; mechanics pilots and synthetic responses cannot count. This is required
  for a positive relevance claim, not for honest engineering work.

The W10 implementation sequence, formal human boundary and checkpoint meanings are defined in
`docs/architecture/w10-expert-relevance-validation.md`. The active 2026-08-06 construct-validity
rework is defined in `docs/architecture/w10-expert-evidence-presentation-v2-addendum.md`; no
positive G-RW4 claim may use presentation v1 or its incomplete mechanics pilot.

## Authority trace

This document materialises the 2026-08-05 user-authorised pivot and is governed by:

- `../scouting-ml-agent-implementation-workflow.html`, version 2.0;
- `../scouting-ml-production-blueprint.html`, version 2.0 pivot section;
- `docs/architecture/research-workbench-pivot.md`.
