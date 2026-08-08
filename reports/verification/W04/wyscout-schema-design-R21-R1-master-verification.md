# W04 bounded R21 design R1 — master verification

## Decision

`REWORK`. The candidate remains within the authorized bounded correction, but
it is not exact enough for independent R14 review.

## Preserved passing surface

The master read all 1,185 design lines and all 132 return lines. The candidate:

- binds immutable R20 SHA-256
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`;
- preserves the accepted v1 authorities;
- defines field and possession v2 IDs and paths;
- closes strict integer-only action subevent behavior without coercion;
- defines two descriptor-only canonical preimages;
- fixes the exact 15-feature distribution as four supported, four suppressed,
  and seven unavailable; and
- derives the evidence-preserving resource count as 30.

The producer's content check and all 25 local-only checks pass.

## Bounded defects

Six corrections are required before review:

1. Field v2 must preserve the fixed R20 profile roster order. It must not sort
   the 119 rows lexically by `(record_kind,json_path)`.
2. The canonical 17-key prior-authority order must place
   `review_recommendation` before `review_record_sha256`, including both exact
   JSON examples.
3. The dependency graph must draw the product and schema preimages as siblings
   after R21, converging at field v2. It cannot show an edge between siblings.
4. Cross-authority test production, fresh independent review, and final master
   gate need three separately owned serial packets and evidence paths.
5. The final gate must enumerate every exact AGENTS.md command, including
   Bandit, Git-guard verification, W04 phase verification, `git status --short`,
   and `git remote`.
6. `r21_design_sha256` is the physical SHA-256 of the complete Markdown report.
   It is not a canonical-JSON digest.

## Master environment evidence

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master reproduced the passing content/local-only checks and the six defects.
The terminal pyc inventory exactly equals the post-sync baseline:

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

`git remote` is empty. No product, dependency, network, cloud, container,
endpoint, CI, deployment, or Git mutation occurred.
