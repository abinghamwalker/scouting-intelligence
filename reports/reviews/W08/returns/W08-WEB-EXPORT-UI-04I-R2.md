# Subagent return — partial implementation

## Task

- task_id: `W08-WEB-EXPORT-UI-04I`, revision `R2`
- invariant: only verified policy-authorised export controls and safe metadata are
  reachable; revoked or unauthorised records never render a readable pack.

## Files changed

- `src/scouting/web/w08.py`
- `apps/web/templates/w08/base.html`
- `reports/reviews/W08/returns/W08-WEB-EXPORT-UI-04I-R2.md`

## Completed work

- Base navigation now shows `Local evidence packs` only to a present analyst/approver
  principal and `Audit` only to admin; landing remains safe without a principal.
- Verified read passes `pack_id` to the export template, enabling the authorised
  revoke UI to be completed without deriving or exposing an object identity from
  pack content.

## Checks

- No new check was run after these two minimal UI edits. The immediately preceding
  R2 export-route focused suite had passed: mypy exit 0 and 21 focused tests passed.

## Unfinished mandatory gaps

- Inventory template still needs active-link versus revoked non-link rendering and
  exact safe metadata treatment.
- Export template still needs the complete safe projection and authorised CSRF revoke
  form; audit template needs the requested UI review.
- The dedicated analyst/approver/second-analyst/scout/admin TestClient reachability,
  revocation and control-absence witness was not implemented.

## Scope confirmation

- no Git operations, dependency/lock changes, protected-output access, delegation or
  edits outside allowed paths.
