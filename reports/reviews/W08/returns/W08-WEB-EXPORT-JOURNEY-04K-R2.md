# Subagent return — blocked at test-only boundary

## Task

- task_id: `W08-WEB-EXPORT-JOURNEY-04K`, revision `R2`
- invariant: analyst-owner/approver success, other-analyst/scout/admin denial and
  revoked non-readability must be executable.

## Exact blocker

The existing verified-pack template submits revocation to
`/w08/export/{{ pack_id }}/revoke`, but `read_export` in
`src/scouting/web/w08.py` renders `export.html` with `payload` only and does not pass
`pack_id`. Jinja therefore renders an empty identifier in the action URL. The required
analyst create → verified read → revoke journey cannot be truthfully witnessed.

The repair belongs in the forbidden production path `src/scouting/web/w08.py`; this
test-only packet must not alter it. No test was added because it would correctly fail
until that bounded production correction is issued.

## Scope confirmation

- changed files: this return only
- no Git operations, dependency/lock changes, protected-output access or out-of-scope
  edits.
