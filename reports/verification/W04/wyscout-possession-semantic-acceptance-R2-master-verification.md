# W04 possession-semantic acceptance R2 — master verification

## Decision

`ACCEPT`. The Wyscout possession-semantic authority is formally accepted under
R20.

This lifts only the possession-authority prerequisite. It does not by itself
authorize possession construction, a dependency row, Bronze, Silver, Gold,
product, or runtime work; the remaining supported-feature and identity
authorities and pre-Bronze gates still apply.

## Accepted authority

```text
decision physical/canonical:
4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71

taxonomy physical:
e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d

taxonomy canonical:
6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa

review physical:
1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4

review record:
40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962

acceptance physical/canonical:
f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112
```

Authority clocks and actors are valid:

```text
decided_at  = 2026-07-30T16:12:58Z
reviewed_at = 2026-07-30T16:44:10Z
accepted_at = 2026-07-30T16:55:47Z

decided_by/accepted_by =
4efe5691-8903-5148-8275-30d2e7e8aed0

reviewed_by =
03a65770-02f6-5eb0-9bd2-e2ebb44b62bd
```

## R1 correction

R1 placed `review_record_sha256` before `review_recommendation`. The strict
accepted-state contract rejected those otherwise correct values as
noncanonical JSON: 111 passed, one failed. The master recorded R1 as `REWORK`;
it granted no authority.

R2 preserves every frozen value, samples a new truthful acceptance clock, and
uses exact lexical key order. Its 1,000 physical bytes equal its canonical JSON
bytes.

## Master verification

The master independently reconstructed the 15-key acceptance, all candidate and
review hashes, actor separation, PASS/zero-findings condition, null v1
supersession, and ordered clocks. The accepted-state suite then passed:

- focused contract: 112 passed in 4.82 seconds;
- Ruff formatting: pass;
- Ruff lint: pass;
- local-only verifier: 25/25;
- `git remote`: empty.

The R2 terminal shell-only inventory exactly equals its fresh preflight:

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

No provider acquisition, network data access, Git mutation, dependency change,
cloud resource, hosted CI, public endpoint, container, deployment, possession
construction, dependency row, or Bronze output was created.
