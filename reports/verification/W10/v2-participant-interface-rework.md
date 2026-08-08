# W10 v2 participant-interface rework verification

- Date: 2026-08-07
- Engineering disposition: **PILOT_READY**
- Human pilot result: **not started**
- W10 state: **REWORK**
- G-RW4: **INSUFFICIENT_EVIDENCE**
- 08E, 08F and formal collection: **unstarted and prohibited**
- `checkpoint/w10-accepted`: **must remain absent**

This evidence covers the governed participant-surface and comprehension rework only. It does not
alter the accepted W09 scorer, feature meanings, matrix, index, rankings, Package A
`goals_per90` correction, evidence thresholds or protected outcomes.

## Trigger and evidence classification

The first v2 mechanics-pilot attempt was stopped cleanly after the product owner found that the
interface read like an engineering console and required operator translation. Phase codes,
“observed value,” predicates, independent-family language, raw coordinate names, duplicated
descriptor panels and technical accordions were not understandable to an external football
professional.

This is a genuine presentation/comprehension failure. It is recorded as product-owner/operator
usability evidence, not eligible-reviewer evidence. There is no inference that the product owner
met reviewer eligibility.

## Preserved stopped evidence

| Item | Verified identity/state |
|---|---|
| Stopped database | SHA-256 `b5e5f35bdbd8acf6ef1827cb2480f65440ce74b44b924418cac6d7553ad393a2` |
| Stopped authority | SHA-256 `33684b88c683b8e565757972ab78e558a0e29dfad7ddcb94fd659dfb631a4791` |
| Stopped separation authority | SHA-256 `559a40c5adc7f803dfb017e26ec35d3cfdcd7f3c3de4ba4dd3e4b04c5f31c1e4` |
| SQLite state | integrity `ok`; sessions 1; completed 0; current judgements 2; revisions 2; receipts 0 |
| Disposition | incomplete preserved `REWORK`; prohibited from formal evidence and G-RW4 |

No stopped file was deleted, overwritten, migrated, repaired, reused or silently reclassified.

## Participant-visible text audit

The full accepted content specification and forbidden inventory are in
`docs/reviews/w10-participant-language-and-ux-spec.md`.

| Superseded participant text/concept | Current participant presentation |
|---|---|
| Internal W03–W10, gate and packet language | No participant equivalent; removed |
| Mechanics-pilot console framing | “A trial of a historical player-comparison research form” |
| Exemplar / candidate | Player A / Player B |
| Frozen W09 model inputs | Statistics used to find similar players |
| Independent descriptors / family IDs | Additional playing evidence with football-readable section names |
| Neutral recorded start locations | Where recorded actions began |
| Passing subtype distribution | Types of passes attempted |
| Duel subtype distribution | Types of duels contested |
| Neutral shot start locations | Where shots were taken |
| Neutral defensive-action locations | Where defensive actions occurred |
| Narrow goalkeeper involvement mix | Goalkeeper action mix — not save quality |
| Raw / observed value | Recorded value |
| Within-position percentile | Compared with players in the same position |
| Unsupported inference | What this information cannot tell you |
| Evidence sufficiency | Can you make a fair comparison from the information provided? |
| Assessment basis | What did you base your answer on? |
| Independent families cited | What information helped you most? |

Participant bytes and assets are now served only through
`/historical-player-comparison` and `/static/historical-player-comparison/...`. The legacy GET
redirects immediately to the friendly address. Participant pages, form actions, validation,
review, receipt and asset payloads contain no phase code, rank, score, distance, origin, repeat,
expected answer, raw coordinate identifier, authority/digest language or stable evidence-family
ID.

## Journey delivered

The form now provides:

- a self-contained purpose, local pseudonymous storage, withdrawal, immutable-submission,
  eligibility, conflict and non-recruitment boundary;
- a consistent Player A/Player B comparison with readable positions and one shared historical
  evidence limitation;
- aligned recorded statistics and optional same-position comparison text;
- applicable-only additional playing evidence, useful sections first, counts plus percentages or
  rates, neutral map labels and explicit pitch-direction limitations;
- one progressive shared limitations disclosure rather than duplicated player-column warnings;
- direct fair-comparison, credibility, confidence, basis, helpful-information, missing-information
  and explanation questions;
- visible progress, resume, review, append-only correction and immutable final submission;
- a local plain-language completion receipt with no governed identifier; and
- four separately stored in-form feedback questions, so no operator-led debrief translation is
  required.

## Scientific and storage invariants

The accepted W09 input family remains visible as selection statistics. Additional playing
evidence remains independently derived and was not used to select the comparison. A response
based on the form must still cite at least one applicable additional-evidence section; the
selection statistics cannot substitute for that requirement.

Both players reconstruct from the same evidence schema and are rendered through the same table
structure. Non-applicable or insufficient sections are hidden, never converted to zero. Blinding,
protected-label separation and participant-keyed deterministic ordering remain intact. Pilot
answers have no path into W09, thresholds, selection, formal evidence or G-RW4.

The stopped store remains readable by its retained store and legacy templates/assets. The new
store is physically separate, append-only, exact-reconstructing and digest-bound. Response,
feedback and receipt histories reject semantic tampering and become immutable after final
submission.

## Contract transition

| Surface | Stopped issue | Current issue |
|---|---|---|
| Authority | `w10-v2-mechanics-pilot-authority-v1` | `historical-player-comparison-pilot-authority-v1` |
| Participant | presentation-v2 evidence bytes | `historical-player-comparison-participant-v1` |
| Response | `w10-v2-candidate-evidence-response-v2` | `historical-player-comparison-response-v1` |
| Form feedback | external operator debrief | `historical-player-comparison-debrief-v1` |
| Receipt | stopped store receipt contract | `historical-player-comparison-completion-receipt-v1` |
| SQLite schema | stopped `v2_*` tables | isolated `hpc_*` tables; digest `38d2afbe4d4877d107bc236e47d2a5c910bf02fd5c67586cc6e9712910017e0f` |

Internal query, candidate, comparison, family and digest identities remain available for exact
audit reconstruction but are not participant content.

## Fresh authority and formal exclusion proof

| Item | Verified identity |
|---|---|
| New participant authority | SHA-256 `676de717e5790d2c0f1139eeaa77a90e72a7b64de8d2f1a5c7a1fad8fe572768`; 1,605,207 bytes |
| New separation authority | SHA-256 `04413d9808c0b2d6dc067a9c711a443bb2c4d8a5453e1150a35eedc7172d0a7e`; 8,004 bytes |
| New database | `historical-player-comparison-pilot-v1.sqlite3`; **absent at handoff** |
| Coverage | five comparisons: GK, DF, defensive MD, attacking/shooting MD, FW |
| New exposure | 10 grains and 10 canonical players |
| Extended formal exclusion | exactly 20 grains and 20 canonical players across both pilots |

The fresh pack has empty player and grain intersections with the stopped pack and withdrawn v1
pack. The future formal pack is absent and unstarted. The separation authority prohibits every
player/grain exposed by either pilot from future formal exemplars or candidates.

## Master/subagent packets

| Packet | Owned scope | Acceptance |
|---|---|---|
| `W10-PARTICIPANT-LANGUAGE-UX-01` | `docs/reviews/w10-participant-language-and-ux-spec.md` | Accepted: 790-line audit/spec, forbidden inventory and translation hierarchy; no Git operations |
| `W10-PARTICIPANT-UI-02` | six participant template/CSS/JS paths | Accepted: 25 participant/web/browser checks passed in 17.46 s; no out-of-scope edits or Git operations |
| `W10-PARTICIPANT-BOUNDARY-TESTS-03` | three new contract/unit/e2e test paths | Independently accepted: 18 passed in 16.86 s, including two real-Chrome tests in 10.47 s; no out-of-scope edits or Git operations |

The independent boundary reviewer found and verified fixes for the shared-limitations heading,
server validation, Chromium pattern grammar, favicon/CSP behavior, feedback digest construction
and MD position projection. Its final witness reported zero external requests, HTTP errors,
console errors or page errors and used temporary fixture databases only.

## Focused verification

- Master focused Ruff/mypy plus contract/boundary/composition run: **23 passed** in 6.66 s; one
  pre-existing Starlette TestClient/httpx deprecation warning.
- Participant/UI combined gate: **25 passed** in 17.46 s.
- Final participant contract/unit/browser gate after unable-to-assess and review-summary fixes:
  **26 passed** in 15.86 s; one pre-existing Starlette TestClient/httpx deprecation warning.
- Complete W10 compatibility/evidence/storage/browser run: initial **116 passed / 3 failed** in
  55.29 s; the three failures identified shared legacy template/asset paths after the participant
  files were versioned. The stopped interface was bound to byte-preserved legacy templates/assets;
  the exact three-test rerun then passed in **8.46 s**.
- Final complete W10 compatibility/evidence/storage/browser run: **120 passed** in 33.06 s
  (33.78 s command wall time); one pre-existing Starlette TestClient/httpx deprecation warning.
- Authority build: five comparisons; database absent; canonical authority and separation hashes
  above.
- Authority verification: stopped identities/state, exact safe reconstruction, symmetric evidence
  schemas, new/old/withdrawn disjointness, 20/20 exclusion roster, closed ports and absent new
  database all passed.
- Production-style in-app browser witness: HTTP 200 on the friendly page; legacy GET redirected to
  the friendly address; one H1 and one form; viewport fit; neutral local actions/assets only; no
  forbidden HTML or visible text; empty warning/error console log. Only GETs were issued. The
  service stopped cleanly and the post-browser authority verification reconfirmed no new database.

## Complete repository gate

All long-running commands were protected only by command-scoped `caffeinate`.

| Gate | Final result | Wall time |
|---|---|---:|
| Locked dependency sync, all groups | resolved 83 packages; audited 82 packages | 0.03 s |
| Ruff format check | 1,137 files already formatted | 0.03 s |
| Ruff lint | pass | 0.03 s |
| mypy | no issues in 125 source files | 0.36 s |
| Import contracts | 5 kept, 0 broken across 97 files / 294 dependencies | 0.10 s |
| Full pytest (final exact pre-commit tree) | 3,143 passed; one pre-existing Starlette deprecation warning | 2,145.23 s |
| Bandit | pass; no medium/high findings | 1.96 s |
| Git guard | pass; executable pre-push guard blocks pushes | 0.06 s |
| Local-only verifier | pass; zero remotes and all 25 checks pass | 1.40 s |
| Participant authority/stopped-state verifier (final pre-commit run) | pass | 1.47 s |

Bandit initially rejected use of Python `assert` in the new governance verifier. Those checks were
replaced with explicit `RuntimeError` guards that remain active under optimized Python; Ruff,
mypy, the authority verifier and the complete Bandit scan then passed without a suppression.

`verify_phase.py --phase W10` returned its expected policy-aligned nonzero result in 0.12 s:
W10 is `REWORK`, 08E/08F are unstarted, the human study is insufficient and the declared result
cannot pass an acceptance gate. This is required evidence that the engineering checkpoint did not
silently accept W10.

## Remaining limitations and disposition

This engineering work does not show that eligible football professionals understand or can use
the form. No current pilot data may enter formal evidence or G-RW4. W10 remains `REWORK`, G-RW4
remains `INSUFFICIENT_EVIDENCE`, and 08E, 08F, formal collection and W10 acceptance remain
prohibited.

The exact remaining human action is:

> Run the new isolated mechanics pilot with at least two fresh eligible football-domain reviewers.

Do not start it automatically.

## Checkpoint

- Commit: the single bounded rework commit carrying this report; its exact object identity is
  verified after creation and reported in the master handoff.
- Annotated checkpoint: `checkpoint/w10-v2-participant-interface-rework-reviewed` — reviewed
  engineering checkpoint only, created from the bounded commit after all success gates pass.
- `checkpoint/w10-accepted`: **absent and prohibited**
