# W10 historical-player-comparison mechanics-pilot handoff

- Status: **PILOT_READY — AUTHENTIC HUMAN EXECUTION REQUIRED**
- Human evidence collected under the new authority: **none**
- New pilot sessions, judgements, feedback rows and completions: **0 / 0 / 0 / 0**
- W10: **REWORK**
- G-RW4: **INSUFFICIENT_EVIDENCE**
- 08E, 08F and formal collection: **unstarted and prohibited**
- Counts toward G-RW4: **no**

This is the active operator handoff for the reworked five-comparison mechanics pilot. It is not a
pilot result, formal-study authority, successful human evidence or W10 acceptance.

## Preserved stopped attempt

The first v2 mechanics-pilot attempt was stopped for participant comprehension rework. These
three files are immutable historical evidence and must not be overwritten, migrated, repaired,
reused or reclassified:

| Preserved file | SHA-256 |
|---|---|
| `data/working/w10/study/v2/pilot/mechanics-pilot-v2.sqlite3` | `b5e5f35bdbd8acf6ef1827cb2480f65440ce74b44b924418cac6d7553ad393a2` |
| `data/working/w10/study/v2/pilot/mechanics-pilot-authority-v1.json` | `33684b88c683b8e565757972ab78e558a0e29dfad7ddcb94fd659dfb631a4791` |
| `data/working/w10/study/v2/pilot/pilot-pack-separation-v1.json` | `559a40c5adc7f803dfb017e26ec35d3cfdcd7f3c3de4ba4dd3e4b04c5f31c1e4` |

The stopped database reconstructs exactly with SQLite integrity `ok`: one session, zero completed
sessions, two current judgements, two revision rows and zero completion receipts. It remains an
incomplete `REWORK` finding and cannot produce 08D GO. The usability findings came from the
product owner/operator and are not eligible-reviewer evidence.

## New isolated authority

| Item | Identity |
|---|---|
| Participant authority | `data/working/w10/study/v2/pilot/historical-player-comparison-pilot-authority-v1.json` |
| Authority SHA-256 | `676de717e5790d2c0f1139eeaa77a90e72a7b64de8d2f1a5c7a1fad8fe572768` |
| Operator separation authority | `data/working/w10/study/v2/pilot/pilot-pack-separation-v2.json` |
| Separation SHA-256 | `04413d9808c0b2d6dc067a9c711a443bb2c4d8a5453e1150a35eedc7172d0a7e` |
| New database path | `data/working/w10/study/v2/pilot/historical-player-comparison-pilot-v1.sqlite3` |
| Required database state at handoff | **ABSENT** |
| Task count | **5** |
| Position coverage | GK, DF, defensive MD, attacking/shooting MD, FW |

The authority uses `historical-player-comparison-pilot-authority-v1`, participant contract
`historical-player-comparison-participant-v1`, response contract
`historical-player-comparison-response-v1` and the separate feedback contract
`historical-player-comparison-debrief-v1`. Participant-keyed ordering is deterministic and does
not use answers. The response database contract is physically separate from the stopped store;
its verified SQLite schema digest is
`38d2afbe4d4877d107bc236e47d2a5c910bf02fd5c67586cc6e9712910017e0f`.

The five comparison digests are:

- `f754a8f74aacc88dff3abfe7cba9d79cfa90dc90ce63e60f16353b674077a340`
- `937902534a3b36cd916038f9d92854e0e4d12de6135b7690858efdc382a3f28e`
- `27a963f4a29f631001e2e74c11cb727e7e42b2b466d1bd98b1041e226a7d570a`
- `c61dd51b3214caa702f4c113b4208c62cb87562c1f187fee4b237e2f04f89890`
- `affa8a7f2ff78215ea5576408b99cf0d5c159a212b4bfd9a2f2cfa2ea4d5c9de`

The new pack has empty grain and player intersections with the stopped pack and withdrawn v1
pack. The formal exclusion roster now contains exactly 20 grains and 20 canonical players: all
ten exposed by the stopped pilot plus all ten exposed by the new pilot. A future formal builder
must also prove disjointness; changing competition or season does not make a reserved player
eligible. No formal pack exists.

## Eligible reviewers

Use at least **two distinct, genuinely eligible football-domain reviewers**. Each reviewer must:

1. have at least two years of experience in professional scouting, recruitment analysis,
   performance analysis, professional coaching or professional playing;
2. have assessed players professionally within the last five years;
3. declare no current or recent conflict involving a displayed player or club;
4. personally accept every local consent item;
5. use a unique 6–32 character uppercase alphanumeric/hyphen participant code; and
6. personally complete all five comparisons, the four form-feedback questions, review and final
   immutable submission.

An AI agent, automated test, test fixture, product owner, operator-entered answer, inferred answer
or synthetic response is not an eligible reviewer. If two eligible humans are unavailable, stop
in `PILOT_READY` and do not start 08E.

## Exact local procedure

1. Re-run `scripts/verify_w10_participant_interface_rework.py` under command-scoped `caffeinate`.
   It must reproduce the three stopped identities and state, both new authority identities, the
   20/20 exclusion roster, closed ports and an absent new database.
2. Start the service from the repository root with:

   ```text
   caffeinate -dimsu uv run python services/api/w10_study_main.py
   ```

3. Direct the reviewer to exactly
   `http://127.0.0.1:8771/historical-player-comparison`. Do not use the stopped internal URL. Do
   not bind outside loopback or expose the service through a tunnel, proxy or network service.
4. The reviewer enters their own eligibility, conflict, consent and participant-code values. The
   operator must not translate the interface, suggest ratings, reveal ordering provenance or
   enter answers for them.
5. The reviewer completes each plain-language Player A/Player B comparison. “Statistics used to
   find similar players” are the unchanged accepted W09 inputs. “Additional playing evidence” is
   independently derived context not used to select the comparison; a form-based rating must cite
   at least one applicable additional section.
6. The reviewer answers the four in-form usability questions. These remain separate from football
   relevance, sufficiency, confidence and any future outcome.
7. The reviewer reviews corrections and submits once. Submission locks responses and feedback.
   Detach only after the local receipt is visible; then the next reviewer may start.
8. After at least two eligible completions, stop the service and reconstruct the database exactly
   before any 08D decision. Do not tune W09, evidence semantics, thresholds or future selection
   from pilot relevance answers.

## Exact GO/REWORK rule

For `N` eligible completed reviewers, the expected task denominator remains `5 × N`. A task is
assessable only when it is a rated response with sufficient evidence, confidence 1–5, assessment
basis supplied evidence or both, and at least one applicable additional-evidence citation.
Prior-knowledge-only, unable, incomplete and missing responses do not enter the numerator.

08D is GO only if every existing preregistered condition holds:

- at least two eligible humans have immutable five-task completions;
- assessable tasks / expected tasks is at least 0.80;
- median confidence across assessable tasks is at least 3/5;
- no reviewer reports that names or minutes were the only usable basis;
- no position-specific evidence or comprehension issue remains;
- no reviewer reports that the form revealed the preferred comparison; and
- every session, action, revision, response, feedback record and receipt reconstructs exactly.

Any failed condition is `REWORK`, not an exclusion, imputation or threshold change.

## Human result fields

- Eligible completed reviewers: **PENDING HUMAN EVIDENCE**
- Expected task denominator: **PENDING**
- Assessable numerator/rate: **PENDING**
- Median assessable-task confidence: **PENDING**
- Names/minutes-only reports: **PENDING**
- Open position/evidence/comprehension issues: **PENDING**
- Apparent system-preference leaks: **PENDING**
- Receipt/integrity result: **PENDING**
- 08D decision: **NOT YET MADE**

No 08E protocol freeze, 08F review, formal collection or W10 acceptance may begin until authentic
human pilot evidence satisfies every condition above.
