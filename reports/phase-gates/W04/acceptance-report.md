# W04 acceptance report

- Date: `2026-08-03`
- Phase: `W04 — Source data, identities and Bronze/Silver/Gold`
- Decision: **VERIFIED_AND_READY_FOR_CHECKPOINT**
- P0/P1 blockers: **none**

W04 has completed its governed source, identity, Bronze/Silver/Gold, schema,
aggregate, vertical-slice, product, runtime, complete-repository, health, and
dataset-card work. The terminal R12 independent review passed with no findings;
the master accepted R12 and the smallest two-blocker correction exposed by the
first complete gate. The restarted complete gate passed all 2,618 tests and every
static, security, local-only, phase, and repository-integrity check.

Accepted runtime R11 and retained real-root R3 are the controlling minimum
operational baseline. The two R3 runs produced the same build, products, manifests,
receipts, semantic hashes, and reconstructed logical JSON bytes. Later R11/R12
hardening is not falsely attributed to those runs; it is independently review- and
test-verified under the terminal closure steer.

The complete source population and the one-match Gold proof remain explicitly
separate. Rights and temporal controls pass, exact minutes/per-90 remain suppressed,
Gold remains research-only, and no external deployment or publication is claimed.

Host-specific PYC/cache tags, inode/link counts, empty-directory metadata,
temporary paths, timestamps, and equivalent filesystem assurance remain visible
under `W10-RUNTIME-HOST-STATE-HARDENING-01`. They are not W04 blockers absent a
reproducible controlling P0/P1 path.

The master authorises the prescribed local integration commit and annotated
`checkpoint/w04-accepted` tag, followed by the checkpoint-ledger commit. No W05
work is started by this acceptance.
