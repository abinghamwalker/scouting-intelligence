# W04 R21 independent review R14 — master verification

## Decision

`REWORK`. The independent reviewer found no P0, P1, or P2 defect in the merged
R20 plus R21 design merits, but correctly found one P2 evidence-integrity defect
in the predecessor master evidence.

## Complete master readback

The master read all 740 lines of
`reports/reviews/W04/wyscout-schema-design-independent-review-R14.md` and all
108 lines of its return. Their physical SHA-256 values are:

```text
R14 review:
8c2c78276191b67ff074d1f405306ed811b92d36319a5c0e7b119807a3a611d3

R14 return:
716a21919eabb9bc1b5c6e8227c4b056a18f41da8f7cdbf0ef4def6c8a9274f9
```

The review recommendation is `REWORK` with exact finding counts `P0=0`,
`P1=0`, and `P2=1`.

## Independently reproduced defect

The master reread every line of the immutable R2 producer return and reproduced:

```text
path:
reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21-R2.md

bytes: 6675
lines: 141
physical SHA-256:
82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10
```

The predecessor
`orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R21-R2.yaml` and
`reports/verification/W04/wyscout-schema-design-R21-R2-master-verification.md`
both state 132 R2-return lines. That count belongs to the original R1 return,
not the immutable R2 return. Those erroneous predecessor artifacts remain
preserved; this successor evidence supersedes their affected readback claim.

The discrepancy arose because the master read a 132-line intermediate R2 return
before the producer appended final inventory evidence, then verified the final
return hash without rereading its appended lines. It is a P2 evidence-integrity
failure in the master loop, not a candidate design defect.

## Design-merits reproduction

The master independently reproduced the R14 conclusions that R21:

- binds immutable R20 and replaces only six declared clause families;
- defines an acyclic sibling-preimage graph;
- preserves exact seventeen-key v1 prior-authority records;
- changes one field row in an immutable 119-row order;
- admits only strict non-boolean integer event/subevent pairs and preserves
  strings and other rejected values without coercion;
- preserves 36 possession predicates and canonical selectors;
- defines exactly 15 features split 4 supported / 4 suppressed / 7 unavailable;
- defines 17 product path descriptors and 16 descriptor-only schema surfaces;
- retains exactly 30 resources and five temporal dependencies;
- separates 16 serial packet scopes, including test/review/master gate; and
- lists all twelve complete repository-gate commands and forbids all product
  implementation until the final pass.

No broader architecture, dependency, source/provider/right, root, storage,
local-only, network, cloud, container, endpoint, hosted CI, deployment, or
product change is required.

## Environment and inventory evidence

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master reran the review assertions and all 25 local-only checks.

The reviewer preflight and terminal postflight compare byte-identically:

```text
cache directories: 150
pycs: 1,145
inventory lines: 1,149
inventory SHA-256:
9c734eb70eab9a8c39798639b37ba4caf18307fd46d1ce4b14b72e1c36abc3fc
```

`git remote` prints nothing. No Git mutation, dependency/lock change,
provider/network access, external service, cloud/container action, endpoint,
hosted CI, deployment, preimage, v2 authority, feature, Bronze, Silver, Gold,
manifest, receipt, build, model, or product implementation occurred.

## Bounded next action

R14 remains immutable failed evidence. The design must receive one bounded R3
control update that designates a fresh R15 review as the active passing review
and the single review member of the 30-resource roster while preserving R14
outside that runtime resource roster. No other R21 contract may change.
