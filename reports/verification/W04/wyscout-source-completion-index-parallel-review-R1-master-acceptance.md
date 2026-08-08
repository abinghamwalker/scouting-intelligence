# W04 source-completion-index parallel review R1 master acceptance

Date: 2026-07-31

Disposition: `REWORK_EVIDENCE_ACCEPTED_AND_R4_DISPATCHED`

The master inspected both independent reviews and recomputed all four report hashes.
The semantic/provenance lane passed with `P0=0, P1=0, P2=0`; its evidence confirms
the accepted five-member index, 3,652 periods, 3,071,395 actions, strict R21 mapping,
equal-clock behavior, exact four-feature Gold derivation and bounded one-match
manifest scope. That PASS applies to the exact R3 candidate and must remain regression
evidence after the bounded correction.

The capability/security lane returned `REWORK` with `P0=0, P1=1, P2=0`. The master
accepts `W04SCIIDXR3CAPR1-P1-001`: standard Python callable introspection retains the
issuer functions and weak registries, while `require_checked_product` trusts registry
membership without independently re-verifying the exact source population and exact
product derivation. Deleting issuer names and marking helpers private does not close
that route. Product work and the complete repository gate remain blocked.

Exact evidence:

- capability review: `5fb92056c3c23cee2f052fcd2d568520e28eaead5857a6b172944c6a6f39fb87`
- capability return: `fd4c4ba4c8ea2256a31d6b04333fa251f3b9c971b57567bcc583b1657fd16bb4`
- semantic review: `9d270746900394f2ae1abd3c145e278d61cf3cdef8c7e12165cde138d089c3fa`
- semantic return: `1f4ae67a0bcfff090f1efdc3371f820ab1e950c20fce50ef036c5def63be9ebf`

R4 is bounded to making authority independently verifiable at consumption. It may
retain an in-process registry as a cache, but registry identity, issuer secrecy or
private naming cannot be the authority. Every accepted completion/product handle must
be revalidated from exact retained evidence and exact dependency scope so an exposed
issuer or mutable registry entry cannot make a raw semantic value accepted.

No architecture, source, index, R20/R21, dependency, feature, provider, local-only or
product decision changes. `git diff --check` passed and `git remote` printed nothing.
