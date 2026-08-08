# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-REVIEW-01-R1`
- objective: Independently review the frozen R1 Wyscout possession-semantic
  decision, taxonomy, and progression-safe contract against accepted R20 and
  frozen local evidence.
- outcome: `PASS`
- findings: zero (`P0=0`, `P1=0`, `P2=0`)

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-REVIEW-01-R1.md`

## Summary

- Read every `read_first` resource completely, including all 4,516 R20 lines,
  all 1,176 R13 review lines, all 1,270 contract lines, both frozen CSVs, the
  complete decision/taxonomy, accepted field authority, orchestration evidence,
  and return template.
- Independently reproduced all candidate, contract, frozen-input, and field-route
  digest edges. The decision is strict canonical JSON; the taxonomy is the exact
  safe canonical-YAML restatement and its parsed canonical JSON equals the
  decision values.
- Audited every one of the 36 exact integer semantic rows against only accepted
  R20 and the frozen local taxonomy labels. The distribution is
  `CONTROL=11`, `RESTART=7`, `DEAD_BALL=8`, `CONTESTED=4`,
  `NON_CONTROL_ADMIN=2`, and `UNMAPPED=4`. All tag selectors are empty.
- Confirmed all four Duel rows use the bounded following-resolved-possession
  buffer; the out-of-game foul and whistle are explicitly unassigned; the other
  six dead-ball rows attach to the preceding resolved possession. All choices
  are conservative project-owned classifications and make no provider-native
  possession claim.
- Audited the complete 112-case contract and R20 rejection/progression boundary:
  strict schemas/types, exact keys, selector sorting/coverage/overlap, tag
  partition rules, actors, rationales, complete combination union, policies,
  canonical JSON/YAML, taxonomy equality, digests, reviews, findings,
  acceptances, clocks, and downstream blocking all close as required.
- Corrected one reviewer-helper assumption: the contract contains 24 test
  functions, not 22; parameterization expands them to exactly 112 cases. This
  was a reviewer-helper assertion only and revealed no candidate defect.
- Wrote one canonical `PASS`/zero-findings review record using the fixed
  independent reviewer ActorId and a truthful post-audit clock. Formal
  acceptance and every checked downstream path remain absent.

## Complete semantic row audit

| Pair | Frozen local label | Decision | Attachment |
| --- | --- | --- | --- |
| `(1,10)` | Duel / Air duel | `CONTESTED` | following resolved same-period possession |
| `(1,11)` | Duel / Ground attacking duel | `CONTESTED` | following resolved same-period possession |
| `(1,12)` | Duel / Ground defending duel | `CONTESTED` | following resolved same-period possession |
| `(1,13)` | Duel / Ground loose ball duel | `CONTESTED` | following resolved same-period possession |
| `(2,20)` | Foul / Foul | `DEAD_BALL` | preceding resolved possession |
| `(2,21)` | Foul / Hand foul | `DEAD_BALL` | preceding resolved possession |
| `(2,22)` | Foul / Late card foul | `DEAD_BALL` | preceding resolved possession |
| `(2,23)` | Foul / Out of game foul | `DEAD_BALL` | unassigned |
| `(2,24)` | Foul / Protest | `NON_CONTROL_ADMIN` | none |
| `(2,25)` | Foul / Simulation | `UNMAPPED` | none |
| `(2,26)` | Foul / Time lost foul | `NON_CONTROL_ADMIN` | none |
| `(2,27)` | Foul / Violent Foul | `DEAD_BALL` | preceding resolved possession |
| `(3,30)` | Free Kick / Corner | `RESTART` | action-team restart |
| `(3,31)` | Free Kick / Free Kick | `RESTART` | action-team restart |
| `(3,32)` | Free Kick / Free kick cross | `RESTART` | action-team restart |
| `(3,33)` | Free Kick / Free kick shot | `RESTART` | action-team restart |
| `(3,34)` | Free Kick / Goal kick | `RESTART` | action-team restart |
| `(3,35)` | Free Kick / Penalty | `RESTART` | action-team restart |
| `(3,36)` | Free Kick / Throw in | `RESTART` | action-team restart |
| `(4,40)` | Goalkeeper leaving line / Goalkeeper leaving line | `UNMAPPED` | none |
| `(5,50)` | Interruption / Ball out of the field | `DEAD_BALL` | preceding resolved possession |
| `(5,51)` | Interruption / Whistle | `DEAD_BALL` | unassigned |
| `(6,60)` | Offside / Offside | `DEAD_BALL` | preceding resolved possession |
| `(7,70)` | Others on the ball / Acceleration | `CONTROL` | action team |
| `(7,71)` | Others on the ball / Clearance | `CONTROL` | action team |
| `(7,72)` | Others on the ball / Touch | `CONTROL` | action team |
| `(8,80)` | Pass / Cross | `CONTROL` | action team |
| `(8,81)` | Pass / Hand pass | `CONTROL` | action team |
| `(8,82)` | Pass / Head pass | `CONTROL` | action team |
| `(8,83)` | Pass / High pass | `CONTROL` | action team |
| `(8,84)` | Pass / Launch | `CONTROL` | action team |
| `(8,85)` | Pass / Simple pass | `CONTROL` | action team |
| `(8,86)` | Pass / Smart pass | `CONTROL` | action team |
| `(9,90)` | Save attempt / Reflexes | `UNMAPPED` | none |
| `(9,91)` | Save attempt / Save attempt | `UNMAPPED` | none |
| `(10,100)` | Shot / Shot | `CONTROL` | action team |

Every row has all 12 mandatory fields, the exact top-level decision actor, a
nonempty NFC project-owned rationale, empty sorted/disjoint tag arrays, and one
permitted R20 combination. The 36 selectors are sorted, unique, complete, and
non-overlapping.

## Contract and progression audit

- Candidate boundary: exact top-level and row keys; strict booleans/integers/nulls;
  nonnegative IDs; sorted unique known tag IDs; required/forbidden disjointness;
  exact actor equality; NFC rationales; complete 9-concrete-variant realization
  of the six R20 decision rows; exact 36-pair coverage; deterministic selector
  order; no overlap.
- Canonical boundary: duplicate JSON keys, BOM, noncanonical JSON, YAML anchors,
  aliases, tags, directives, duplicate/non-string keys, floats, timestamps,
  multiple documents, and noncanonical YAML are rejected.
- Review boundary: exactly one `w04-authority-review-v1` fence; canonical record;
  all four candidate digests; fixed IDs/schema; independent strict UUID actor;
  ordered truthful clock; closed finding rows; `PASS` iff findings are empty and
  `REWORK` iff at least one exact finding exists.
- Acceptance boundary: exact canonical 15-key object; all candidate and review
  digests; `PASS` review only; master actor equality; reviewer separation;
  truthful ordered clock; null v1 supersession.
- Progression boundary independently exercised:
  `DECISION_ONLY`, `REVIEW_PASS`, `REVIEW_REWORK`, and later `ACCEPTED` are valid
  when their exact evidence is present. Any downstream marker is rejected for
  absent, PASS-review-only, REWORK-review-only, or malformed authority state and
  is admitted only after exact acceptance.
- Static collection model: 24 test functions expand to exactly 112 cases with
  parameterized counts
  `1,1,1,1,7,5,13,12,10,1,1,8,1,1,1,1,2,1,12,7,4,16,1,4`.

## Tests run

- command: complete shell-only pyc preflight over the repository, pruning
  `.git`/`.venv`, and the exact site-packages root
  - exit status: `0`
  - result: repository `59` pycs / `19` cache directories; site-packages
    `1,086` pycs / `131` cache directories. Every row binds relative path,
    kind/mode/size/link/device/inode/clocks, first 16 bytes, and complete SHA-256.
- command: first shell-only preflight classifier attempt
  - exit status: `1`
  - result: reviewer-helper mode-pattern assumption used `100644` instead of the
    macOS `stat` output `644`, so it classified zero rows. It did not modify a
    file or invalidate the preserved preflight snapshot.
- command: corrected shell-only complete classifier
  - exit status: `0`
  - result: repository `35` mapped normal + `21` mapped pytest + `3` exact inert
    orphans; site `972` mapped normal + `112` mapped pytest + `1` uv bootstrap +
    `1` exact six orphan; zero unsafe or unclassified rows.
- command: shell `shasum -a 256` frozen physical-digest reconstruction
  - exit status: `0`
  - result: all decision, taxonomy, contract, event/tag CSV, field acceptance,
    R20, and mandatory review-context hashes reproduced.
- command: first locked/no-sync independent Python audit attempt
  - exit status: `2`
  - result: sandbox denied read-only uv cache metadata before Python launched.
    The same exact bounded command was rerun with read authority; no sync,
    download, install, or mutation was requested.
- command: first executed independent canonical/semantic Python helper
  - exit status: `1`
  - result: every prior candidate/digest/36-row assertion passed, then the
    reviewer-helper incorrectly asserted 22 static test functions. The source
    has 24 functions; no candidate byte changed.
- command: corrected locked/no-sync contract/progression helper
  - exit status: `0`
  - result: 24 functions, exactly 112 modeled cases; decision-only, PASS review,
    REWORK review, later acceptance, and downstream blocking all passed.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `112 passed in 4.63s` with the actual review present.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `All checks passed!`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, all 25 checks, zero failures.
- command: post-check shell physical-hash and authority/downstream absence gate
  - exit status: `0`
  - result: all frozen candidate/input/test bytes unchanged; formal possession
    acceptance and all 15 checked downstream paths absent.
- command: terminal shell-only inventory reproduction after this return was
  written, followed by four byte-for-byte `cmp` comparisons
  - exit status: `0`
  - result: repository/site complete pyc and cache-directory inventories exactly
    equal the fresh preflight.

Every executed Python process used
`PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B`; no bare Python,
sync-capable uv, or alternate environment was used.

## Artifacts/evidence

- independent review:
  `reports/reviews/W04/authorities/wyscout-possession-semantic-independent-review-R1.md`
  - reviewed at: `2026-07-30T16:44:10Z`
  - bytes/lines: `1,729` / `19`
  - physical SHA-256:
    `1f70cc4b1a9d988d85daf573219c6316791709f7341f9abd802b7ceb1d28ccd4`
  - canonical review-record SHA-256:
    `40aa258984714f33d91c502df1d50eefd4e076a7617c0ac6659c9679937d0962`
- frozen candidate:
  - decision physical/canonical:
    `4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71`
  - taxonomy physical:
    `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`
  - taxonomy canonical:
    `6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa`
  - contract physical:
    `a5539c6c2e19d15579a033bc276358479a737d12dffefe4fe211b3f6cb7877f5`
- frozen inputs:
  - event taxonomy:
    `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`
  - tag taxonomy:
    `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`
  - field registry canonical:
    `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`
  - field acceptance physical:
    `fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365`
- shell inventory evidence root:
  `/tmp/w04-possession-semantic-review-r1.CqA1Ff`
- repository preflight and terminal:
  - pycs/cache directories: `59` / `19`
  - complete inventory SHA-256:
    `a769b9da05175d1fc30be50bed006cfe2186821e20c75d80e492974582064948`
  - cache-directory inventory SHA-256:
    `b6123a4a6367ab0f4a12373f7e9753e66eddd14c260505a1f202b27a1482024a`
- site-packages preflight and terminal:
  - pycs/cache directories: `1,086` / `131`
  - complete inventory SHA-256:
    `b245f364edd9da04791df1b959adf1d56a79503a586feeec0b5eb55356401c4d`
  - cache-directory inventory SHA-256:
    `4500d5ef41a918adcfd16bd7fc4b8d29565945ebaf4dc360fdf8933245628671`

## Risks

- No P0/P1/P2 semantic, schema, contract, or progression defect remains.
- The taxonomy is deliberately conservative project classification derived only
  from frozen local integer taxonomy evidence. It is not provider-native
  possession truth.
- This review PASS is not formal possession acceptance and grants no downstream
  authority.

## Follow-up items

- Master must independently reproduce this review evidence and decide formal
  acceptance under the separately owned packet. No downstream work is authorized
  by this return.

## Scope confirmation

- no Git operations: confirmed; no direct Git command or Git mutation was run.
  The mandated local-only verifier performed only its documented read-only Git
  checks.
- no unauthorised dependency or lockfile changes: confirmed; no sync/install
  occurred and `pyproject.toml`, `uv.lock`, and `.venv` were not edited.
- no edits outside `allowed_paths`: confirmed; exactly the review and this return
  were created.
- no candidate/test/field-authority/orchestration edit: confirmed.
- no delegation or self-approval: confirmed.
- no provider/network/external-football-knowledge access: confirmed.
- no acceptance, possession construction, dependency, Bronze, product, runtime,
  cloud, container, endpoint, CI, or deployment work: confirmed.
- no pyc cleanup, repair, deletion, baseline coercion, or environment recreation:
  confirmed.
