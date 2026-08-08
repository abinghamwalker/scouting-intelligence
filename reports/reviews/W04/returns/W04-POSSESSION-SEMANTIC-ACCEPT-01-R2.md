# Master return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-ACCEPT-01-R2`
- objective: Correct only the R1 noncanonical acceptance key order, resample a
  truthful acceptance clock, and prove the actual accepted authority state.
- outcome: `PASS`

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-acceptance-v1.json`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-ACCEPT-01-R2.md`

## R1 bounded rework

R1 used correct authority values but placed `review_record_sha256` before
`review_recommendation`. Strict canonical JSON requires
`review_recommendation` first. The R1 accepted-state run therefore failed closed
with 111 passing tests and one `noncanonical JSON` failure. R1 was recorded as
`REWORK` and granted no downstream authority.

R2 preserves every frozen ID, actor, digest, recommendation, and null
supersession value. It moves only that key into canonical order and samples a
new truthful acceptance clock after the review.

## Accepted authority

```text
acceptance_id:
w04-wyscout-possession-semantic-acceptance-v1

accepted_at:
2026-07-30T16:55:47Z

accepted_by:
4efe5691-8903-5148-8275-30d2e7e8aed0

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

The 1,000-byte acceptance is strict canonical JSON with one terminal LF and the
exact 15-key R20 schema. `accepted_by` equals the decision actor and differs
from the independent reviewer. The ordered authority clocks are:

```text
decided_at  = 2026-07-30T16:12:58Z
reviewed_at = 2026-07-30T16:44:10Z
accepted_at = 2026-07-30T16:55:47Z
```

## Verification

- independent canonical byte and digest reconstruction: pass;
- actual accepted-state focused contract: 112 passed in 4.82 seconds;
- Ruff format check: pass;
- Ruff lint: pass;
- local-only verifier: 25/25;
- candidate and review hashes: unchanged;
- `git remote`: empty;
- dependency, possession, Bronze, product, and runtime construction: not begun.

## pyc evidence

The fresh R2 preflight before Python was:

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

The terminal shell-only inventory after this return was written reproduced all
eight values exactly. No pyc was created, removed, repaired, or coerced.

## Scope confirmation

- no Git mutation;
- no dependency or lockfile change;
- no candidate, review, contract, orchestration-after-dispatch, or downstream
  implementation edit;
- no provider/network access;
- no cloud, hosted CI, endpoint, container, or deployment state;
- no delegation or self-approval of an independent review.
