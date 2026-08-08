# W10 v2 bounded-rework independent PRE-PILOT re-review

- Review class: **fresh bounded PRE-PILOT engineering/security re-review**
- Date: 2026-08-06
- Scope: exact-current-response/history correction for `W10-V2-REWORK-PRE-01`, plus the
  requested stale-schema and v1/formal-isolation challenges
- Candidate status: **PASS for this bounded PRE-PILOT correction — no open P0-P3**
- Previous disposition: this report previously recorded one open P1 against SQLite contract v2;
  the fresh contract-v3 candidate independently closes that finding
- Explicit exclusion: **this is not `W10-V2-INDEPENDENT-REVIEW-08F`, A4/phase acceptance,
  product-owner approval, pilot evidence, pilot or formal-study authority, G-RW4, W10 closure or
  W11 authority.** This report does not self-approve or authorise participant approach.

## Decision

`W10-V2-REWORK-PRE-01` is closed in the bounded pre-pilot candidate. SQLite contract v3 binds every
successful record command to one exact append-only revision, preserves the command's per-session
ordinal in that revision, reconstructs command and per-presentation revision order on every load,
requires the current response to equal the latest exact revision, and keeps completion bound to the
ordered current-response digest set. The formerly accepted active current-row substitution now
fails before load, review or completion.

No P0, P1, P2 or P3 was found in the correction. The other four findings closed by the previous
bounded re-review remain closed; this narrowly scoped rerun found no regression in v1/formal
isolation. Progression remains a master decision under the addendum and cannot be inferred from
this technical finding closure.

## Findings

**No open P0-P3.**

## Exact-current-response/history closure

### Contract and write-side invariants

- `_V2_SCHEMA_CONTRACT` is now `w10-v2-mechanics-pilot-sqlite-contract-v3`
  (`src/scouting/storage/expert_study.py:1862`). Old contract rows are rejected before any schema
  object is added (`:2028-2057`).
- `v2_commands` has an exact positive ordinal unique within its session. Each
  `v2_judgement_revisions` row binds a unique `command_id` and unique per-session
  `command_ordinal`; the revision-command trigger requires the same session, record kind, response
  bytes and next session ordinal (`:2061-2072`). Commands and revisions remain append-only, and all
  post-completion mutation paths remain blocked (`:2074-2087`).
- The governed record transaction writes the same canonical response bytes to command, revision
  and current-response rows, with the command ordinal equal to `expected_revision + 1`, before
  incrementing the session revision (`:2631-2674`). Completion similarly writes the receipt as the
  final command at the next exact ordinal (`:2759-2790`).

### Read-side reconstruction

Every `load_session` now reads complete command identity/session/ordinal/kind/request/response
fields and all linked revision fields (`expert_study.py:2235-2279`). Reconstruction then proves:

- session revision equals command count and command ordinals are exactly contiguous;
- every command ID is canonical, belongs to this session and has a SHA-256 request digest;
- a completion command can occur only once and only as the final command;
- every record-command response is canonical, binds the exact participant/session/presentation and
  accepted comparison, and has one exact linked revision;
- revision ordinals are contiguous per presentation, command linkage is one-to-one, retained
  command ordinal and response bytes match, and cross-presentation linkage is rejected;
- current-response and revision rosters match exactly, and every current response equals the
  latest revision for that presentation (`:2324-2404`);
- completion state, one final completion command, canonical receipt digest/identity/authority/time,
  ordered current response digests and exact command response all agree (`:2410-2442`).

### Independent reproduction of the original P1

A fresh temporary v3 store recorded a rated response with confidence 4. I then changed only the
active `v2_judgements` row to a different canonical, contract-valid response with confidence 3 and
a recomputed judgement digest. The retained revision and record command remained unchanged. The
three public paths produced:

```text
{
  'load': 'REJECTED:v2 current judgement diverged from append-only history',
  'review': 'REJECTED:v2 current judgement diverged from append-only history',
  'complete': 'REJECTED:v2 current judgement diverged from append-only history'
}
```

This directly reverses the previous reproduction, where the same mutation loaded and normal
completion sealed it.

## Additional adversarial challenges

| Challenge | Independent result |
|---|---|
| Delete the only revision after removing only its delete trigger | `load_session` rejected the record command without an exact revision. |
| Insert an orphan revision with a nonexistent command after removing only the insert guard | `load_session` rejected the divergent revision/command history. |
| Link a second revision to the already-used record command | Physical schema uniqueness rejected the duplicate `command_id`/`command_ordinal` link. |
| Gap/reorder a retained command ordinal after removing its update trigger | `load_session` rejected the non-contiguous command history. |
| Move a revision from the first presentation to a second valid scheduled presentation | `load_session` rejected the cross-presentation revision/command binding. |
| After completion, coherently change current, revision and record-command response bytes while leaving the receipt | `load_session` rejected with `v2 completion receipt failed exact reconstruction`. |
| Open a database carrying schema contract v1 or v2 | Both were rejected as incompatible; subsequent inspection showed only the original `v2_schema_contract` table, proving no partial repair. |

The focused integration regression also retains direct-SQL checks for `complete` values outside
`0/1`, receipt-free completion, active schedule insertion, all completed session/current-response/
revision/schedule/command mutations, append-only command/completion rows, exact replay,
cross-session/cross-kind command reuse and concurrent record/completion handling.

## V1/formal isolation

- The v2 application still exposes only the v2 mechanics-pilot lane and has no approval or formal
  store/fallback. Independent TestClient probes returned 404 for `/w10/approval`, `/w10/sessions`,
  `/w10/submit`, `/w10/formal`, `/w10/v2/approval` and `/w10/v2/formal`.
- Read-only retained v1 aggregate inspection returned formal
  `1 approval / 0 sessions / 0 judgements / 0 completions` and pilot
  `0 approvals / 1 session / 2 judgements / 0 completions`. Those retained v1 rows were not opened,
  migrated or accepted by the v3 store.
- Production composition remains restricted to the v2 participant-safe mechanics-pilot authority
  and `mechanics-pilot-v2.sqlite3`; no v1 approval, formal route or evaluator was introduced.

## Commands and results

No Git command was run. No implementation, return, authority, data or orchestration file was
edited. Test-created stores were temporary and discarded; this report is the only retained write.

| Command/check | Result |
|---|---|
| `UV_NO_CACHE=1 uv run --no-sync pytest -q tests/unit/test_w10_expert_study_web.py tests/integration/test_w10_expert_study_console.py` | exit 0; **15 passed**, one upstream TestClient deprecation warning |
| Focused `ruff format --check` and `ruff check` over the storage implementation and integration test | exit 0; two files formatted and lint-clean |
| Focused `mypy src/scouting/storage/expert_study.py` | exit 0; no issues |
| Focused `bandit -q src/scouting/storage/expert_study.py` | exit 0; no findings/output |
| Independent active canonical current-row substitution probe | exit 0; load, review and completion all rejected with append-only-history divergence |
| Independent missing/orphan/duplicate/reordered history probes | exit 0; all four corruptions rejected, with duplicate linkage blocked by schema uniqueness |
| Independent two-presentation cross-link probe | exit 0; rejected with revision/command-history divergence |
| Independent post-completion coherent-history/unchanged-receipt probe | exit 0; rejected by exact receipt reconstruction |
| Independent schema-contract v1/v2 probe | exit 0; both rejected and neither database gained a partial v3 schema |
| Read-only retained v1 SQLite aggregate inspection | exit 0; formal `1/0/0/0`, pilot `0/1/2/0` for approval/session/judgement/completion |
| V2 mutation-route isolation probe | exit 0; all tested v1/formal/approval paths returned 404 |

## Disposition

The bounded contract-v3 candidate has **no open P0-P3 for `W10-V2-REWORK-PRE-01`**. The master may
use this evidence when deciding the next pre-pilot/A4 action, but this report itself grants no gate,
pilot, human-collection, freeze, approval, formal-study or phase authority. A future
`W10-V2-INDEPENDENT-REVIEW-08F` must still be a separate post-pilot, post-freeze review under the
addendum.
