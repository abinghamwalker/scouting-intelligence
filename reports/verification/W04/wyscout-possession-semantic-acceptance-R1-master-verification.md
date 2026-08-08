# W04 possession-semantic acceptance R1 — master verification

## Decision

`REWORK`. The R1 acceptance is not a valid authority and grants no possession,
dependency, Bronze, or downstream permission.

## Defect

The 1,000-byte R1 JSON contains the correct values and digest edges but is not
canonical. Its final review keys are ordered:

```text
review_id
review_physical_sha256
review_record_sha256
review_recommendation
supersedes_acceptance_id
```

Canonical lexical order requires:

```text
review_id
review_physical_sha256
review_recommendation
review_record_sha256
supersedes_acceptance_id
```

The independent canonical reconstruction failed, and the actual progression
test rejected the file as `noncanonical JSON`: 111 tests passed and one failed.
Both Ruff checks and all 25 local-only checks still passed.

The shell-only pyc inventory remained exactly equal to its preflight:

```text
repository pycs/cache dirs: 59 / 19
repository complete-row digest:
f6eab1210fc649c463d493d15cca8c4f2413f7df02859911793acc37d156be73
repository ordered-content digest:
c1fff9e70887c54142170192f9c293b23cc7bf198307f55b7aa5b2f86fb2fff1

site pycs/cache dirs: 1,086 / 131
site complete-row digest:
102512a54a1a5df30d566c0a7a3d5e2896328b796a9da32a9a989f1635df980b
site ordered-content digest:
b24485398b491149553e3cec4fafb870d4ee4c6ab8f7b2bd5724aa56d011eb1a
```

R2 is bounded to canonical rerendering of the same authority edges under a new
truthful acceptance clock, plus the R2 return and full accepted-state
verification. Candidate and review bytes remain frozen.
