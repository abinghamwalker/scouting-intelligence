# W04 bounded R21 design R2 — master verification

## Decision

`ACCEPT FOR FRESH INDEPENDENT R14 REVIEW`. This is not final R21 acceptance and
does not authorize any downstream materialization or product implementation.

## Complete readback

The master read all 1,242 lines of the corrected R21 design and all 132 lines of
the R2 producer return. The corrected design is 58,986 bytes with physical
SHA-256:

```text
08f64de257d32dafc0e47030025a22644acb1ab793e34a443bca34d18d154969
```

The master independently confirmed:

- the field-v2 roster preserves the immutable R20 profile sequence and changes
  only the action `$.subEventId` decision;
- `review_recommendation` precedes `review_record_sha256` in the closed
  seventeen-key prior-authority object and both exact examples;
- the digest graph is
  `R20 -> R21 -> {product preimage, schema preimage} -> field v2`, with no
  sibling edge and no self, downstream, feature, build, or runtime digest in
  either preimage;
- `r21_design_sha256` means the SHA-256 of the complete frozen R21 Markdown
  physical bytes only;
- the action subevent transform admits strict JSON integers only, excludes
  booleans, requires exact event/subevent pair membership, and preserves every
  string, other type, and unknown integer as unmapped typed evidence without
  coercion;
- possession v2 consumes canonical field-v2 selectors only and preserves all
  36 accepted v1 predicates;
- the exact feature roster has 15 rows: four supported, four suppressed for
  unavailable minutes denominators, and seven unavailable;
- the resource roster has exactly 30 paths and the temporal dependency set
  remains exactly five;
- the final cross-authority flow has separate serial producer-test,
  independent-review, and master-gate packets; and
- all twelve exact repository-gate commands plus additive R21 checks are
  enumerated.

## Preserved evidence

The immutable predecessor and producer evidence retain these physical hashes:

```text
R20:
8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047

original R21 R1 return:
3d53c23e3028c635f75b303f67a9fc027a96b76ed030909cbfd7b5a7567bc545

R21 R2 return:
82b4fa67311c30dc66693e9465f1a466c22d0a726437bbe345e852b1cff6ac10
```

The six R1 defects remain preserved in
`orchestration/reviews/REVIEW-W04-SCHEMA-DESIGN-01-R21-R1.yaml`; the R2
candidate supersedes their affected wording for review without rewriting that
evidence.

## Independent master checks

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master reran a shell-safe structural reconstruction of the design,
reproduced its hashes and cardinalities, and ran the local-only verifier. All
25 checks passed, including Python 3.12.12, one root uv project, active push
guard, zero Git remotes, and no hosted CI, deployment, container definition, or
external service dependency.

The producer's complete shell inventory was independently regenerated after
the master sync and checks and compared byte-for-byte:

```text
repository pycs / cache dirs: 59 / 19
repository inventory SHA-256:
a339bef860b00a51a9df5bcfa84540cd0ca91c19fd77ab63a80c38f77866745e

site pycs / cache dirs: 1,086 / 131
site inventory SHA-256:
88bf87afd7c14b89ed6cb3fc29c535511beaa771167345efec3d8a13ea512fd3
```

The comparisons are identical. `git remote` prints nothing. No Git mutation,
dependency or lock change, provider/network action, cloud/container action,
endpoint, hosted CI, deployment, Bronze, Silver, Gold, feature
materialization, or product implementation occurred.

## Gate

The bounded producer correction passes master review and is eligible for a
fresh independent R14 merits review. R21 remains unaccepted until that review
passes and the master independently verifies it.
