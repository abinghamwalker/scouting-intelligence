# Role-brief and shortlist state-machine boundary

- Status: Normative W03 control boundary
- Scope: Ownership, versions, states, approvals, reasons, visibility, retention and
  audit semantics
- Runtime status: Full collaborative implementation is deferred to W08

This document defines the workflow rules that later contracts and implementations must
preserve. W03 may exercise a minimal synthetic path through these rules, but it does not
claim that the collaborative workflow, its users or its operating evidence exists.

## Shared invariants

- Every object carries `tenant_id`, a stable object ID, an explicit owner, visibility,
  an immutable version/revision ID and an optimistic lock version.
- Missing actor, role, tenant, owner, visibility, version or action context denies the
  operation.
- Cross-tenant access is always denied. Visibility never overrides the tenant boundary.
- Approved evidence and prior versions are immutable. A correction creates a linked new
  version; it never rewrites the historical version used by a retrieval or decision.
- A model result supplies evidence only. Product policy filters that evidence, and an
  authorised human performs every workflow transition.
- Every state change, ownership or visibility change, approval, rejection and export
  attempt is a material action. It requires an append-only audit event; if the audit
  write fails, the material action fails.
- Retirement or rejection removes an item from new active work. It does not delete its
  versions, evidence references, reasons or audit history.

## Role brief

### Ownership and versioning

The creating analyst is the `owner_actor_id`. Ownership may be reassigned only by an
authorised administrative action with a reason and audit event; admin status alone does
not grant approval authority.

A role brief is a stable container with immutable numbered versions. Editing a draft
increments its optimistic lock and creates a new immutable version at submission.
Changing an approved or rejected brief starts a linked `DRAFT` version; the prior
version and every retrieval that pins it remain unchanged.

Each submitted version contains the responsibilities, hard constraints, visible
preference weights, exemplars if used, tenant, owner, visibility, taxonomy version and
creation/submission timestamps needed to replay it.

### States and legal transitions

| From | To | Actor and preconditions | Required reason / audit |
| --- | --- | --- | --- |
| none | `DRAFT` | Analyst creates a brief in their tenant and becomes owner. | Audit creation and initial version digest. |
| `DRAFT` | `SUBMITTED` | Owning analyst; required fields and policy context are complete. | Submission note; audit submitted version digest. |
| `SUBMITTED` | `APPROVED` | Approver in the same tenant; approver is not acting solely under the admin role. | Explicit approval reason; approver, timestamp and approved version audited. |
| `SUBMITTED` | `REJECTED` | Approver in the same tenant. | Controlled rejection reason and optional bounded note; audit before/after digests. |
| `SUBMITTED` | `DRAFT` | Owning analyst after an approver requests changes. | Change-request reason; new linked draft version and audit event. |
| `DRAFT` | `RETIRED` | Owner, before submission. | Retirement reason and audit event. |
| `APPROVED` | `RETIRED` | Owner or approver; no in-place change to the approved version. | Retirement reason and audit event. |
| `REJECTED` | `DRAFT` | Owner creates a new linked version. | Reference the rejection and audit the new version. |

All other transitions are denied. `REJECTED` and `RETIRED` versions cannot be used for a
new retrieval. Only an `APPROVED` version may be used as the approved input to a shared
workflow. W03's synthetic contract path may exercise a specifically identified test
approval; it is not evidence of real approval practice.

### Role-brief rejection reasons

The reason is one of:

- `requirements_unclear`
- `constraints_unapproved`
- `rights_or_policy_conflict`
- `evidence_definition_incomplete`
- `other`

`other` requires a bounded explanatory note. A rejection is not deletion and cannot
silently alter retrievals already pinned to the rejected version.

### Visibility

- `OWNER_ONLY`: owner plus explicitly assigned approvers may read the draft.
- `TEAM`: authorised same-tenant analysts, assigned scouts and approvers may read
  according to their action policy.

Submission identifies the intended visibility. Approval for shared work requires
`TEAM`; a visibility change creates a new version and audit event. Visibility does not
grant export rights.

## Shortlist and shortlist entries

### Ownership and versioning

The analyst who creates a shortlist is its owner. The shortlist container has an
optimistic lock version. Each candidate entry has an immutable revision sequence that
pins the role-brief version, retrieval result/model/index/data versions, rank at
addition, owner, rationale, state and evidence references.

Comments, scout observations and recommendations remain separately attributable
evidence. They do not overwrite the entry or become a model label automatically.
Concurrent writes with a stale optimistic version are rejected rather than merged.

### Entry states and legal transitions

| From | To | Actor and preconditions | Required reason / audit |
| --- | --- | --- | --- |
| none | `LONGLIST` | Analyst adds an eligible candidate from traceable evidence. | Addition rationale, pinned evidence versions and audit event. |
| `LONGLIST` | `MONITOR` | Owning analyst. | Next action and transition reason audited. |
| `LONGLIST` or `MONITOR` | `SCOUT` | Owning analyst assigns a scout/review. | Assignment, evidence scope and reason audited. |
| `MONITOR` | `LONGLIST` | Owning analyst returns the entry for broader triage. | Reason and new entry revision audited. |
| `SCOUT` | `MONITOR` | Owning analyst after recording the scout recommendation. | Recommendation reference and reason audited. |
| `SCOUT` | `SHORTLIST` | Approver in the same tenant after reviewing evidence completeness and disagreement. | Explicit approval reason, approver and evidence-version set audited. |
| Any active state | `HOLD` | Approver in the same tenant. | Hold reason, review owner and next review condition audited. |
| `HOLD` | prior active state | Approver; the prior state and new evidence are explicit. | Release reason and new entry revision audited. |
| Any active state or `HOLD` | `REJECTED` | Owning analyst or approver, as permitted by the action policy. | Controlled rejection reason and audit event. |

`LONGLIST`, `MONITOR`, `SCOUT` and `SHORTLIST` are active states. A scout may record an
observation, disagreement and recommended next action but cannot perform an approval
transition. `REJECTED` is terminal for that entry revision. Reconsideration creates a
new linked entry with a new rationale; it never erases the rejection.

### Shortlist rejection and hold reasons

Rejection uses one of:

- `outside_brief`
- `insufficient_evidence`
- `identity_unresolved`
- `rights_or_eligibility`
- `scout_not_recommended`
- `duplicate_candidate`
- `other`

Hold uses one of:

- `awaiting_evidence`
- `identity_review`
- `rights_review`
- `availability_review`
- `other`

`other` requires a bounded note. Reasons are retained with the entry revision and
available to authorised reviewers.

### Visibility

- `OWNER_ONLY`: owner and explicitly assigned reviewers/approvers.
- `TEAM`: authorised same-tenant workflow participants.

Entries inherit shortlist visibility, but a more restrictive observation remains
restricted. Moving or copying evidence must not widen its visibility. Every visibility
or ownership change is permissioned, versioned and audited. Export additionally needs
authorisation, data-rights and environment permission; the W03 synthetic policy denies
export.

## Retention

W03 sets no fabricated calendar duration. All versions, transition reasons, evidence
references and audit events remain in guarded local storage for the local project's
retention lifetime until an approved retention policy supplies a duration and disposal
procedure. No W03 hard-delete transition exists.

A future retention change must preserve the evidence needed to reconstruct historical
recommendations and decisions, honour the strictest source-rights class and record an
auditable disposition. It must not silently delete rejected or negative evidence.

## Material audit event

Each material action records at least actor, tenant, action, target, request ID, UTC
timestamp, prior and resulting state/version, before/after digests, reason, visibility,
and pinned evidence identifiers. Export attempts also record export scope.

The audit store is append-only. Correction or reversal is a new event linked to the
earlier event. Update or delete requests are denied.

## Deferred W08 implementation

W08 owns the full local collaborative runtime: persisted state machines, local users
and sessions, assignments, comments, scout observation UI, notifications, object-level
permission enforcement, optimistic-concurrency UX, authorised evidence packs and
end-to-end workflow/security tests. W03 owns only this normative boundary and a minimal
synthetic role-brief-to-shortlist-to-audit seam. W03 must not claim representative
users, moderated task evidence or a shadow pilot.

## Authority trace

- `../scouting-ml-production-blueprint.html`: sections 02–04, 06, and P0.3/P4.1–P4.5.
- `../scouting-ml-agent-implementation-workflow.html`: waves W03 and W08.

