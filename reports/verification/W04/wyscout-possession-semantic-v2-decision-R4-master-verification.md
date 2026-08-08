# W04 possession semantic v2 decision R4 — master verification

## Decision

`ACCEPT_FOR_INDEPENDENT_REVIEW`. R4 restores the sole R21-fixed current review
ID/path, preserves both failed review generations as exact historical
non-authority, and fails closed for all other invalid review bytes.

The producer changed exactly its focused executable contract and R4 return.
This decision releases only a fresh independent review; it is not possession
acceptance.

## Readback and integrity

Frozen decision/candidate bytes remain:

```text
decision physical/canonical SHA-256:
8d59c06f0bc555572fbb07d67eecbda9a7d4d5615aaf716d6c3cd9e72e0b7425
candidate physical SHA-256:
24223b25b5faa1521691f55a3258f28e186a3ed7cb6ebd0d5d8ed421286b0187
candidate canonical SHA-256:
3a3c7cdb0e6ce441d3514e4f415bb5117ebc53f2d18b753206a6ca8d7fcdd881
R4 focused contract SHA-256:
dd4167747b71203390ba04d7c0899dc98099e203368ba5b3c3942b1b9a6e3116
R4 return SHA-256:
d666af0b960b3371fb26d879adee6c3ddbedbd100170dbec531e4a075ff2fc40
```

The exact historical physical review hashes are:

```text
failed R1:
71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a
failed R2:
609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a
```

Only these two hashes become transitional `None` in the actual progression
reader. They cannot satisfy review or acceptance. Every other present
fixed-path byte string enters the complete strict review validator.

The sole current route is:

```text
review ID:
w04-wyscout-possession-semantic-independent-review-v2-R1
review path:
reports/reviews/W04/authorities/
  wyscout-possession-semantic-independent-review-v2-R1.md
```

No invented `v2-R2` current route remains.

## Independent master reproduction

The master began with a fresh locked synchronization:

```text
83 packages resolved
82 packages audited
```

The complete focused suite passed:

```text
332 passed in 28.24s
```

An independent direct challenge proved:

- the actual fixed-path `609a4e0b...` failed review becomes no current review;
- the actual authority state is exactly `DECISION_ONLY`;
- unknown malformed review bytes are not suppressed and raise `ValueError`;
- acceptance and later authority remain impossible without a valid review.

Additional checks:

```text
focused Ruff format/check: PASS
local-only verifier: 25/25 PASS
retained pyc files: 1,145
retained __pycache__ directories: 150
git diff --check: PASS
git remote: empty
```

The producer's preflight and terminal inventory matched exactly: 1,295 rows,
222,755 bytes, SHA-256
`13fcf204919e60067fa57a0d4c5032b039875872a442f165593484cf6e3a8f52`.

The master-corrected historical R2 packet parses, contains no outside-root
path, and has physical SHA-256
`214cf68e582025ed8f737bea3be751e7beb857cc5e2e4ffb2222dd7ae85afd19`.

## Fresh review requirements

The next reviewer must:

- verify both failed review generations before overwriting the fixed path;
- use canonical UUIDv5 actor
  `b4b3e91b-d13b-53c4-95d4-a6019f6faa98`;
- independently reconstruct all authority and semantic bytes;
- rerun selector, sequence, multi-scope, progression, and product-absence
  challenges;
- issue `PASS` only with zero P0-P2 findings.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R3` may start. Possession
acceptance and all later authority/product work remain blocked.
