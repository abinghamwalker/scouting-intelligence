# W08 workflow, audit, export and recovery report

Status: **AUTOMATED MECHANICS AND INDEPENDENT REVIEW PASS; HUMAN STUDY PENDING**

## Versioned workflow

Role briefs retain immutable draft, submit, reject/correct, resubmit and approval
versions; the browser witness retains six exact versions for that lifecycle. Replay
links pin the exact approved brief version and exactly one truthful query mode: either
one public query player or a non-empty unique public exemplar set. The link retains
request/result/run IDs, resolved digest, trace, wrapper digest, lineage, model, index,
taxonomy, data version and ordered synthetic resemblance candidates.

Shortlists retain owner, retrieval link, entries, assignments, controlled state
transitions/reasons, comments, next-action ownership and optimistic lock versions.
Stale writes fail without overwriting the winning revision and expose a reload/retry
path. Rejection, hold and reconsideration append attributed revisions rather than
rewriting history.

Scout observations retain five structured rubric dimensions, per-dimension and
overall confidence, local note/clip references, TEAM/OWNER_ONLY visibility,
disagreement/reason, next action, amendments and version history. Disabled, wrong-
tenant, unassigned and wrong-role actors are denied before mutation. Every fixture is
`synthetic_automated_test`, not real scout evidence.

## Export and audit

The local evidence pack is deterministic for the exact tenant/actor/brief-version/
replay-link/shortlist tuple. It carries classification, included underlying values,
model/data/taxonomy/lineage versions, fixed W06 limitations, SHA-256 checksums and an
append-only audit receipt. Authorised owner and approver access is role/object scoped;
other analyst, scout, admin and foreign-tenant IDOR paths deny generically.

Repeat create is idempotent; repeat revoke and read-after-revoke deny without a second
receipt or revocation. Current assignment, authorship and visibility are evaluated per
record, so former assignment does not leak OWNER_ONLY content or the presence of a
`human_entered_local` origin. No external destination or publication path exists.

The audit chain binds predecessor digest, sequence, event digest and event ID. SQLite
triggers reject receipt mutation, and application verification rejects orphan or
digest-corrupted ledgers before audit view, export create, inventory, read or revoke.
The local host administrator remains in the same trust domain: receipts are
tamper-evident application evidence, not external notarisation.

## Adversarial and recovery evidence

Route-level witnesses retain exact database/audit/file baselines across role, IDOR,
CSRF, wrong-object, media-type, content-length, invalid UTF-8 and actual streamed
body-over-limit denials. The parser checks a chunk against remaining 64 KiB capacity
before retaining it and admits no multipart/file path. Private marker values and
submitted secret markers are absent from packs and denial responses.

Byte tamper, audit corruption, storage read/write faults, audit-append faults and a
real SQL export-insert failure all fail closed; after removal of injection, one retry
succeeds without duplicate or partial state. Focused retained results include 31
audit/export/workflow tamper tests, 42 export/privacy/storage tests, 27 replay-contract
tests and 23 route adversarial tests, all passing.

These results establish mechanics only and preserve W06 `NO_GO` and the pending
five-representative-user gate.

The final independent security/confidentiality review passed with zero findings at
every severity. Its complete focused workflow/security/browser surface passed 72
tests and independently re-proved export byte verification, receipt binding,
optimistic concurrency, failure atomicity and multi-role read/transition composition.
