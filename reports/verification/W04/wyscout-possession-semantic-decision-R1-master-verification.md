# W04 possession-semantic decision R1 — master verification

## Decision

`ACCEPT` as the frozen candidate for fresh independent review. This is the
master task decision only; it is not the formal
`w04-wyscout-possession-semantic-acceptance-v1` authority and does not authorize
possession construction, a dependency row, Bronze, or downstream product work.

## Candidate

The accepted candidate is:

```text
decision physical/canonical SHA-256:
4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71

taxonomy physical SHA-256:
e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d

taxonomy canonical SHA-256:
6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa

contract-test physical SHA-256:
a5539c6c2e19d15579a033bc276358479a737d12dffefe4fe211b3f6cb7877f5

producer-return physical SHA-256:
a3bad59e73ee7f5f202e80a9e46302a37fb4536a17b17b6cab5d9c18c786cc88
```

The decision contains exactly one predicate for each of the 36 fixed
`(event_id, subevent_id)` pairs and no tag partitions. The distribution is
`CONTROL=11`, `RESTART=7`, `DEAD_BALL=8`, `CONTESTED=4`,
`NON_CONTROL_ADMIN=2`, and `UNMAPPED=4`. All four Duel rows use the bounded
following-possession buffer. The two locally ambiguous dead-ball attachments are
explicitly unassigned; Simulation, Goalkeeper leaving line, and both Save
attempt rows remain explicitly unmapped.

Every predicate is a project-owned conservative classification bound to the
frozen integer taxonomies. The closed policy denies provider-native possession
truth and forbids runtime label/name matching.

## Master reproduction

The master read all four changed files, including all 1,270 contract lines, and
independently reconstructed the authority without calling the candidate
validator. The reconstruction reproduced:

- 36 unique fixed event/subevent pairs and 59 fixed tag IDs;
- all exact top-level and predicate key sets;
- strict UUID actor equality and the complete R20 combination union;
- the stated six-way decision distribution;
- empty, disjoint tag selectors for this conservative version;
- exact decision/taxonomy equality and all frozen input hashes; and
- the decision physical/canonical, taxonomy physical, and taxonomy canonical
  hashes shown above.

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master then reran:

- focused contract: 112 passed in 5.04 seconds;
- Ruff formatting: pass;
- Ruff lint: pass;
- local-only verifier: 25/25.

The post-sync shell-only pyc inventory was identical before and after all master
Python and verification commands:

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

`git remote` prints nothing. No provider acquisition, network data access,
cloud resource, hosted CI, public endpoint, container, deployment, dependency
change, or Git mutation was created.

The next authorized step is a fresh independent possession-semantic review with
read-only candidate ownership. Formal acceptance remains blocked until a PASS
review is independently verified by the master.
