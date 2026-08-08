# W08-WEB-BRIEF-HISTORY-04E-R1 return — rework required

The accepted R1 workflow service supports immutable status versions, but the current
HTTP seam has no rejected-to-draft correction route or form and does not expose the
controlled rejection reason/note required by this packet. This is an implementation
gap, not a shared-contract blocker; no unsafe workaround or history rewrite was made.

No allowed implementation was completed in this bounded return. The smallest follow-up
is a fresh producer pass adding service-backed correction parsing and the five-version
TestClient chain, with status decisions retaining existing field values and corrections
creating a new draft version only.

No Git, dependency/lock, protected-output, external call, or out-of-scope edit occurred.
