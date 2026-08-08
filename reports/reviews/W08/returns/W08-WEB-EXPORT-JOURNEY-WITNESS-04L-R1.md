# W08-WEB-EXPORT-JOURNEY-WITNESS-04L-R1 return — rework required

Preflight succeeded: the live `read_export` route passes `pack_id=pack_id` at
`src/scouting/web/w08.py:994`; the prior stale blocker is not reproduced.

No test implementation was completed in this bounded return. The existing integration
module contains the necessary authenticated role/brief/shortlist helpers, but a fresh
dedicated witness still needs to compose the full approved exemplar replay → TEAM
shortlist → export → second analyst/scout/admin → revocation sequence. This is not a
new product defect or a shared-path blocker; it is unfinished packet work and must not
be reported as a passing journey.

No Git, dependency/lock, protected-output, external destination, or out-of-scope edit
occurred.
