# W10 presentation-v2 independent PRE-PILOT review

- Review class: **PRE-PILOT engineering/scientific/security review**
- Explicit exclusion: **this is not `W10-V2-INDEPENDENT-REVIEW-08F`**. That post-pilot,
  post-freeze review remains prohibited until A5 has real eligible reviewer evidence, A6 has exact
  frozen v2 authorities, and the product owner has not yet approved those exact digests.
- Scope reviewed: accepted 08A/08B work and the 08C implementation return, including the relevant
  retained v1 boundaries.
- Date: 2026-08-06
- Status: **REWORK — five open P1/P2/P3 findings; not pilot-ready**
- Gate effect: none. This review does not approve A4, start A5, freeze A6, authorise formal
  collection, pass G-RW4, close W10, or imply human/pilot evidence.

## Executive decision

The implementation has strong purpose separation, missingness semantics, position-specific
eligibility, participant-payload blinding, and v1 isolation. It is not ready to approach mechanics-
pilot reviewers. The production evidence loader does not bind the canonical manifest bytes that
the accepted matrix names, the SQLite state machine can be put into a receipt-free completed state
by direct SQL, pseudonym-only recovery can rotate another participant's capability, and the A3
browser surface omits the required accessible profile visualisation while carrying broken v2
navigation.

No P0 was found. Open findings are two P1, two P2 and one P3. Under the requested rule, any open
P0-P3 precludes PASS.

## Findings

### W10-V2-PRE-01 — P1 — independent evidence can be rebuilt from a substituted canonical manifest

**Evidence.** The matrix boundary correctly requires the accepted matrix's hard-coded canonical
build digest at `src/scouting/data_products/wyscout/expert_evidence.py:1093-1100`. The production
loader later reads the canonical manifest, checks canonical JSON and only the public build ID, then
trusts each manifest-declared action path/hash/size at
`src/scouting/data_products/wyscout/expert_evidence.py:1326-1354`. It never hashes the canonical
manifest bytes and compares them with `matrix.manifest.canonical_build_digest` (the retained exact
value is `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`). The bundle then labels
descriptor rows with the unchanged matrix-row lineage digest at
`src/scouting/data_products/wyscout/expert_evidence.py:898-905`.

The retained manifest currently has the expected SHA-256, so this is a substitution acceptance
path, not evidence that current bytes are corrupt. A changed canonical manifest can keep the same
build ID, name changed action files with matching self-declared hashes and preserve player action
counts. The builder would then derive changed independent descriptors while presenting unchanged
W09 matrix lineage, scorer inputs and rankings. That defeats A2's exact lineage/substitution
boundary and could manufacture the supposedly independent assessment evidence.

**Bounded fix.** Before parsing artifacts, require the canonical manifest's exact SHA-256 to equal
the matrix manifest's `canonical_build_digest` and the accepted pinned value. Reuse the repository's
guarded manifest/artifact loader if possible; otherwise also reject symlinked path components and
unsafe physical aliases. Bind the accepted canonical manifest digest explicitly into the evidence
policy/bundle lineage. Add a production-loader mutation test that supplies a canonical manifest
with the same build ID and internally consistent changed artifact descriptors and proves rejection
before any Parquet scan.

### W10-V2-PRE-02 — P1 — direct SQL can forge completion and change the frozen schedule without a receipt

**Evidence.** The v2 schema stores independent mutable `revision` and `complete` columns and a
separate completion table at `src/scouting/storage/expert_study.py:1994-2003`. Its session trigger
only prevents `complete=1` changing back to zero, and its presentation insert trigger only applies
after completion; update/delete protections do not seal insertion while a session is active
(`src/scouting/storage/expert_study.py:2004-2015`). `load_session` trusts the session boolean without
requiring or validating a completion receipt at `src/scouting/storage/expert_study.py:2143-2174`.
The governed completion path does create a receipt and response-digest list at
`src/scouting/storage/expert_study.py:2465-2489`, but that path is not the read-side authority.

A focused temporary-store probe executed direct SQL
`UPDATE v2_sessions SET complete=1 ...` before any response. `load_session` then returned
`complete=True` with `judgements=0` and `SELECT count(*) FROM v2_completions` returned `0`. The
existing direct-SQL test checks only reopening an already completed session and schedule insertion
after completion at `tests/integration/test_w10_expert_study_console.py:760-784`; it does not cover
the reproduced pre-completion transition or insertion into an active schedule.

**Impact.** A corrupted or locally modified SQLite file can be presented as an immutable completed
pilot record without a receipt or complete response set. While active, an extra presentation can
also be inserted outside the exact authority schedule. This breaks the claimed receipt, schedule,
denominator and replay integrity and makes A5 evidence unauditable.

**Bounded fix.** Make completion a validated immutable event rather than a trusted mutable session
flag. On every load, require one canonical receipt whose digest reconstructs, whose session and
authority digest match, and whose ordered response digests equal the exact current judgement set;
derive `complete` from that event. Reconstruct the exact presentation schedule from the in-memory
authority on load (count, ordinal, comparison bytes/digest and no extras). Add fail-closed checks or
triggers for authority/session identity, consent, revision, active-schedule insertion and completion
creation. Extend direct-SQL tests to the reproduced zero-response completion, active-schedule
insertion, authority drift and receipt/response mismatch cases.

### W10-V2-PRE-03 — P2 — pseudonym re-entry is an unauthenticated capability takeover path

**Evidence.** Participant and session identity are deterministic from the digest of the participant
code at `src/scouting/storage/expert_study.py:2073-2079`. If a row exists, supplying the same code
and the same low-entropy eligibility/consent declarations rotates the opaque browser capability at
`src/scouting/storage/expert_study.py:2083-2114`. The UI describes that value only as a “Participant
pseudonym” at `apps/web/templates/w10_expert_study/v2_dashboard.html:8`; it does not identify it as
a recovery secret or enforce high entropy. The intended rotation is positively demonstrated by
`tests/integration/test_w10_expert_study_console.py:677-689`.

**Impact.** Anyone with local browser access who knows or guesses a reviewer pseudonym and ordinary
declarations can invalidate the reviewer's current cookie, resume the session and replace
pre-submission responses. That compromises reviewer identity, recovery and pilot evidence even
though the store remains local.

**Bounded fix.** Keep the pseudonym non-secret, but issue a separate high-entropy recovery secret
once and retain only its digest, or make recovery an operator-mediated local action that issues a
new capability after an explicit identity check. Rotate a capability only with that recovery
authority. Add tests proving that the same pseudonym and declarations without the recovery secret
cannot load or rotate an existing session and that a legitimate recovery invalidates only the old
capability.

### W10-V2-PRE-04 — P2 — A3 is table-only and its v2 navigation has dead targets

**Evidence.** A3 requires a side-by-side accessible profile visualisation and A4 requires raw/
percentile/visual reconstruction parity (`docs/architecture/w10-expert-evidence-presentation-v2-addendum.md:81-83,108-110`).
The participant template renders the 16 W09 metrics and every metric in all six independent
families as tables at `apps/web/templates/w10_expert_study/v2_participant.html:7-11`; it contains no
profile visualisation or equivalent compact comparison. The fixed contract roster contains 16 W09
rows and 57 descriptor rows per player at
`src/scouting/contracts/expert_relevance.py:529-575`, so the default pair exposes 146 scalar rows,
including supplementary and not-applicable family tables. Values are emitted without participant-
readable rounding at `apps/web/templates/w10_expert_study/v2_participant.html:3-5`.

The real-browser check establishes string presence, leakage absence, a raw/percentile toggle and no
horizontal overflow, but no chart parity, screen-reader reading order/verbosity or comprehension
property at `tests/e2e/test_w10_expert_study_playwright.py:325-352`. In addition, the shared base
links “Study home” to `/w10` and “Current step” to `#study-content` at
`apps/web/templates/w10_expert_study/base.html:21`, while the v2 app registers only `/` and
`/w10/v2` at `src/scouting/web/w10_expert_study.py:713-719` and no v2 template defines
`id="study-content"`. A focused TestClient probe reproduced `/w10 -> 404` and the missing fragment
target.

**Impact.** The surface technically contains the evidence but does not satisfy the authorised A3
presentation. Its volume makes position-specific comparison and screen-reader use unnecessarily
costly and risks turning A5 into a test of table endurance rather than football evidence
sufficiency. Keyboard/navigation users can also leave the v2 journey through a dead home link or
activate a no-op current-step link.

**Bounded fix.** Add a genuinely accessible, symmetric compact profile visualisation derived from
the same raw rows, with a structured text/table fallback and exact raw/percentile/visual parity
tests. Default the comparison to the position/MD-branch mandatory families, keep supplementary and
unsupported detail available in clearly labelled disclosure regions, and apply deterministic
participant-readable number formatting without changing contract bytes. Make base navigation
route-aware (v2 home must be `/w10/v2`), provide the declared current-step target, and add real-
browser keyboard plus semantic reading-order assertions. This is presentation work only; it must
not add ranking cues or change evidence/ranking authority.

### W10-V2-PRE-05 — P3 — the accepted A1 report misstates the action-partition count

**Evidence.** `reports/verification/W10/v2-evidence-capability-and-construct.md:54-59` says the
canonical manifest has seven action partitions. The manifest has five `canonical_actions`
artifacts (England, France, Germany, Italy and Spain), totalling the correctly stated 3,071,395
rows; the production loader independently requires five at
`src/scouting/data_products/wyscout/expert_evidence.py:1339-1353`.

**Impact.** The row count and implemented roster agree, so derivation is not affected, but the
accepted construct/capability evidence is factually inconsistent with its cited authority and can
misdirect later reconstruction or independent review.

**Bounded fix.** Correct “seven action partitions” to “five action partitions” and update the 08A
return if it repeats the statement. Do not change the manifest, action data or accepted row count.

## Explicit no-finding areas

- **W09-input circularity and ranking path:** no independent family identifier occurs in the W09
  feature, index, serving or shared scorer execution paths. Independent descriptors are aggregated
  separately from canonical actions; protected v2 responses have no call path into W09 features,
  weights, scaler, index, scores or ranking. PRE-01 is a lineage-substitution issue, not a detected
  ranking mutation.
- **Purpose and missingness:** contracts distinguish `W09_INPUT` from
  `INDEPENDENT_DESCRIPTOR`; observed zero, observed value, insufficient opportunity, not
  applicable, not captured and invalid missing remain structurally distinct. Numeric fields are
  forbidden for unsupported inference, and mandatory-family failure makes a selected row
  ineligible.
- **Position and MD appropriateness:** GK/DF/FW mandatory rosters are fixed; MD requires one branch
  shared by exemplar and candidate. The narrow GK family does not claim shots faced, save
  percentage, shot-stopping quality, goals prevented, sweeping effectiveness or recruitment value.
- **Asymmetric/protected rendering:** exemplar and candidate use the same panel macro and evidence
  schema. Retrieved/control origin, retrieval/control rank, distance/score, control rule, evidence
  band, difficulty, repeat linkage, expected answer and prior/aggregate participant outcomes were
  absent from the participant-safe contract/browser test. No aggregate closer/better/recommended
  cue was found.
- **Internal identity/digest leakage:** player, grain, candidate and query identities are absent
  from evidence bundles. Bundle/comparison and source-lineage digests remain server-side contract
  authority and were not rendered in HTML. Opaque task tokens are resolved server-side.
- **V1 preservation and substitution:** retained v1 presentation bytes still validate under digest
  `4ca84a2b9873cbc9c402dc85a740753c8a876ac9e72f4e37481b4973b0f5da96`.
  Read-only aggregate inspection reproduced formal approval/session/judgement/completion counts
  `1/0/0/0` and pilot session/judgement/completion counts `1/2/0`. The production v2 composition
  opens only v2 pilot paths and has no v1 approval, formal route, evaluator or fallback.
- **Pilot/formal phase separation:** the current v2 store accepts only `MECHANICS_PILOT`; no formal
  v2 collection route exists. No A5 pilot authority is present in the production working path, so
  the production service is unavailable rather than substituting v1. A5 disjoint pilot evidence,
  A6 frozen protocol/query/presentation/approval digests, 08F and A7 formal evidence remain future
  prerequisites, not accomplishments of this review.
- **Normal API correction/replay/concurrency:** focused tests passed for append-only judgement
  revisions, exact command replay, cross-session/cross-kind command rejection, concurrent record/
  completion handling, correction of rating zero and normal receipt creation. PRE-02 is the
  uncovered direct-SQL/read-side integrity gap.
- **Eligibility and consent:** the pilot path enforces at least two years, a declared eligible
  football experience kind, recent assessment, no declared conflict and all consent items. PRE-03
  concerns recovery authentication after that initial check.
- **Local-only/external requests:** host header and peer address must both be loopback, security
  headers and strict same-site HttpOnly cookies are present, and the real-browser journey observed
  only loopback requests. No provider, network, credential, cloud or external-service request was
  found.
- **Basic keyboard/mobile/recovery behavior:** the skip link, focus styling, form labels, native
  controls, 320-pixel no-overflow layout, cookie-loss recovery mechanics, correction review,
  immutable-submit UX and detach flow execute. PRE-03 and PRE-04 remain the bounded recovery and
  accessibility exceptions.

## Reproduced verification

| Check | Result |
|---|---|
| Focused contract/unit/integration suite for v1/v2 evidence, evaluator boundaries, web and store | 78 passed; the three e2e cases could not bind a loopback socket inside the initial sandbox |
| `tests/e2e/test_w10_expert_study_playwright.py` with temporary loopback bind | 3 passed in 10.24s |
| Focused Ruff format/check | pass; 11 files formatted and lint-clean |
| Focused mypy over six v2 source/composition files | pass; no issues |
| Focused Bandit over six v2 source/composition files | pass; no findings |
| Retained v1 SQLite aggregate counts (read-only) | formal `1 approval/0 sessions/0 judgements/0 completions`; pilot `1/2/0` |
| Canonical manifest SHA-256 | current bytes equal `587f6969...004be59`; PRE-01 is the missing enforcement path |
| Direct-SQL pre-completion probe | reproduced `complete=True`, zero judgements, zero completion receipts |
| V2 navigation probe | reproduced `/w10` status 404 and absent `study-content` target |
| W09 execution-path token scan | no `ID-LOC/PASS/DUEL/DEFLOC/SHOTLOC/GK` identifier in feature/model/serving/scorer/config execution files |

## Required disposition

Return 08B/08C for bounded correction of PRE-01 through PRE-04 and correct the 08A evidence typo in
PRE-05. Independently rerun the focused suite plus the new adversarial cases. Only after a fresh
pre-pilot review has no open P0-P3 may the master decide whether A4 is satisfied and whether the
separate 08D mechanics-pilot packet can begin.

This report must not be renamed, cited or treated as `W10-V2-INDEPENDENT-REVIEW-08F`; 08F remains a
new independent review after a real eligible A5 pilot, exact A6 freeze material and the applicable
human approval boundary.
