# W03 modular-monolith synthetic spine

- Status: Accepted W03 architecture boundary
- Runtime boundary: Local, single-tenant and loopback-only
- Data boundary: Deterministic generated synthetic fixtures
- Model boundary: Contract seam only; no retrieval-quality or promotion claim

## Architecture

W03 uses a modular monolith in one uv-managed Python project:

- one FastAPI process composes local HTML and JSON endpoints;
- one worker process owns scheduled materialisation and asynchronous work;
- embedded SQLite is the authoritative operational/workflow store;
- in-process or guarded-file mechanisms provide bounded jobs, cache and run locks;
- guarded local files hold immutable manifested products and evidence;
- no browser template or static module calculates a model score;
- no request handler reads provider files at request time;
- every cross-module payload uses a strict versioned contract.

FastAPI, the worker and embedded SQLite run from the root environment. The database
opens no listener and needs no credentials. There is no container, external service,
cloud resource, public endpoint, external identity, hosted telemetry, external model
call or remote deployment.

## One synthetic role-brief-to-audit journey

1. **Authenticate and authorise.** A local synthetic analyst enters with actor, role
   and tenant context. Unknown or mismatched context is denied before object access.
2. **Create a role brief.** `workflow` accepts a versioned `RoleBrief` contract with
   hard constraints and visible preference weights. `audit` records the material
   creation through an `AuditEvent` contract.
3. **Resolve eligible synthetic evidence.** `policy` checks tenant, synthetic-only
   rights and brief constraints. A fixture fact lacking valid as-of evidence is
   excluded; an ambiguous identity is not guessed.
4. **Retrieve through one interface.** `serving` receives the authorised, policy-safe
   request and returns a deterministic synthetic `RetrievalResult` with reason codes,
   contrasts, confidence/applicability and pinned versions. In W03 this proves the
   serving contract, not a trained or validated scouting model.
5. **Explain and inspect.** `web` renders the contract fields. It does not recompute
   retrieval maths and does not describe resemblance as outcome prediction.
6. **Create a shortlist entry.** `workflow` records an analyst-owned synthetic entry
   with provenance, rationale, result version and optimistic version. Product policy
   and the analyst action remain separate from model evidence.
7. **Record the material trail.** The composition layer sends strict `AuditEvent`
   contracts for the brief, retrieval and shortlist actions. Audit records identify
   actor, tenant, action, target, request, time, versions and digests. Audit failure
   blocks the corresponding privileged/material action.

The replay is complete only when the brief, admitted evidence, result, shortlist entry
and audit chain resolve to the same declared manifest/cutoff/version set.

## Module and import boundaries

| Module | May depend on | Must not import |
| --- | --- | --- |
| `contracts` | Standard library and validation primitives | Any other project module |
| `sources`, `identity` | `contracts`, `storage` | `features`, `modeling`, `serving` |
| `data_products` | `contracts`, `sources`, `identity`, `storage` | `serving`, `workflow`, web modules |
| `features` | `contracts`, Gold readers in `data_products` | `modeling` internals, `serving` |
| `modeling`, `evaluation` | `contracts`, `features`, `storage` | serving handlers, `workflow`, web modules |
| `serving` | `contracts`, `storage`, registered artifacts read-only | training code, provider adapters |
| `policy`, `workflow`, `observations` | `contracts`, serving read interfaces | `modeling`, `features`, `sources` |
| `audit` | `contracts` only | Everything it records |
| `web`, API and worker composition | Versioned interfaces from the modules above | Model maths, provider parsing or unguarded persistence |

`audit` does not import callers. Callers or the composition layer submit an
`AuditEvent` contract to its write interface.

## Three deliberately separate decisions

```text
model/serving evidence
  -> product policy (eligibility, rights, risk and brief constraints)
  -> authorised human workflow action
  -> append-only audit event
```

- A model/serving result is immutable evidence with uncertainty and applicability.
- Product policy may filter or suppress it but may not rewrite the model evidence.
- A shortlist state is an attributable human/workflow decision, never a model output.
- Audit records the material action and its evidence references without controlling the
  underlying decision.

This separation allows future models to be evaluated against the same evidence
contract while different briefs apply explicit policy. It also prevents the presence
or rank of a candidate from being mislabelled as a human outcome.

## Failure behaviour

- Future or unprovable evidence: exclude and suppress the recommendation.
- Ambiguous identity: quarantine/review; never guess.
- Unknown role/action, tenant mismatch or object mismatch: deny.
- Rights classification other than W03 synthetic: reject.
- Path outside a guarded root: reject before I/O.
- Model/index unavailable: labelled unavailable state; no silent substitution.
- Audit unavailable for a privileged/material write: fail the write.
- Optional cache or background work unavailable: do not lose authoritative state or
  relax controls; execute synchronously or report a labelled unavailable state.

## Deferred work

W03 does not establish a provider adapter, real identity quality, feature/model quality,
expert evaluation set, R0 claim, R1 users, pilot, security test, external identity,
multi-club runtime or deployment. Those remain behind their named later gates.

## Authority trace

- `../scouting-ml-production-blueprint.html`: sections 03–04, 06, 08 (P1.1–P1.8),
  11 decisions D4–D7, D9–D10, and section 12.
- `../scouting-ml-agent-implementation-workflow.html`: sections 01, 03, 05, 07 and
  wave W03.
