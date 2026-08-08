# W08 moderated local-workflow study protocol

Status: **PILOT AND REPRESENTATIVE PATHS PREPARED — NO RESULTS RECORDED**

This protocol supplies two deliberately different evidence paths. `G-W08A` needs one
successful development pilot plus reproduction and review; it can authorize bounded
W09 technical experimentation. `G-W08B` (legacy `G-W08`) and blueprint `G4/G4B` still
need five representative users and are the only path to W08 acceptance. This document
does not itself satisfy either path. Automated fixtures must never be entered as pilot
or participant results.

## Staged gate paths

### G-W08A — development progression pilot

Use one `W08-P01`–`W08-P03` pilot slot with one genuine operator. The operator may be
an internal developer or a representative user; they are exercising the system, not
being counted in the representative cohort. A candidate G-W08A result requires:

1. all T1–T7 outcomes marked `PASS` on the same frozen local build;
2. a stopped runtime with reproducible database and export-manifest receipts;
3. correct interpretation of the retained W06/claim boundary;
4. no unresolved P0/P1 finding; and
5. master reproduction plus independent review recorded in
   `reports/phase-gates/W08/pilot-gate-report.json`.

Only an exact `PASS / DEVELOPMENT_PROGRESSION_AUTHORIZED` decision authorizes bounded
local W09 challenger experimentation. W08 remains `MASTER_REVIEW`; the pilot does not
create `checkpoint/w08-accepted`, count as any of U01–U05, authorize W10 or external
deployment, or establish representative-user, model-quality or production-readiness
claims. If the pilot exposes a defect and the build changes, rerun the pilot on the
corrected frozen build before seeking G-W08A review.

### G-W08B — representative acceptance

Use `W08-U01`–`W08-U05` exactly as specified below. This is the legacy `G-W08` and
blueprint `G4/G4B` path. It alone can support W08 verification, acceptance,
checkpointing and closure, representative-user acceptance, and later shadow-pilot
readiness.

## Fixed evidence boundary

- W06 remains `NO_GO` solely because `MISSING_EXPERT_RELEVANCE_EVIDENCE` is absent.
- Retrieval is `resemblance_only`, `synthetic_development_only`, `LIMITED` and carries
  `no_recommendation_evidence`.
- Participants assess local workflow, access-control, audit, reversibility and
  usability mechanics. They do not validate player relevance, recruitment outcomes,
  market value, transferability, model quality or production readiness.
- Protected W06 expected outputs must not be opened, shown or reconstructed.
- The study uses only the local synthetic-development records supplied by the W08
  study runtime. No real player assessment or invented scout judgement is requested.

## Required participant set

Recruit exactly five genuine representative users who work in, closely support, or
are accountable for football recruitment analysis/scouting decisions. The set must
collectively represent analyst, scout and approval/meeting responsibilities; record
the relevant responsibility for each participant without recording a name. A
developer, automated agent, browser persona or moderator is not a substitute.

Use participant codes `W08-U01` through `W08-U05`. Before the session, obtain explicit
authorisation from the study owner and the participant. If five qualifying,
authorised participants are not available, stop and retain the gate as blocked.

## Consent and data-handling boundary

Read this statement before starting:

> This is a moderated evaluation of a local synthetic scouting-workflow prototype,
> not of your job performance and not of any real player. Participation is voluntary.
> We record a participant code, relevant work role, task completion, elapsed time,
> observed interaction problems and your answers about the evidence boundary. We do
> not record your name, account password, real-player judgement, employer-confidential
> information, audio, video or screen capture. You may stop at any time. Study data
> stays in this local repository and is not sent externally.

Record `consent_obtained: true` only after an affirmative response. Do not start for a
participant who declines. Never put passwords, names, contact details, free-form real
player evaluations or other personal data in the capture record. Paraphrase only the
minimum usability observation needed, and let the participant review it before the
session ends.

## Moderator preparation

1. Confirm the repository is on `main`, W08 is `MASTER_REVIEW`, Git remotes are zero,
   the local push guard passes, and the retained study-runtime commit is checked out.
2. Run the study-runtime preparation command from the morning handoff once per
   participant. It creates a fresh database and export root under an explicitly chosen
   local study directory and prints synthetic account identifiers separately from the
   capture file.
3. Start only the loopback W08 application. Confirm the browser address begins with
   `http://127.0.0.1:` and developer tools show no non-loopback request.
4. Give the participant the participant instructions below. Do not demonstrate the
   solution path. Offer only the scripted neutral prompts.
5. Start the timer when the landing page is visible. Record observations in a copy of
   `moderated-study-capture-template.yaml`.
6. After the tasks, run the retained verification command from the morning handoff,
   let the participant review the de-identified record, then stop the local server.

## Participant instructions

You are evaluating workflow mechanics using synthetic records. Work as you normally
would and narrate what you expect to happen. The retrieval output is not a player
recommendation and has no expert relevance evidence. Do not enter any real player,
club, colleague or confidential information. Ask the moderator to pause or stop at
any time.

Complete the tasks in order. You may use mouse, keyboard or both. If an action fails,
recover using only what the interface tells you; do not ask the moderator for the
solution.

## Core task script

### T1 — Create and submit a role brief (analyst)

Sign in as the supplied synthetic analyst. Create a brief from the W08 template,
enter at least one responsibility, one hard constraint, one weighted preference and
one exemplar, then submit it. Explain what will remain historically visible after a
later edit.

Success evidence: submitted immutable version, attributable actor, visible version
number, no silent rewrite and correct explanation of historical preservation.

### T2 — Approve the brief and inspect retrieval linkage (approver and analyst)

Sign out, sign in as the supplied synthetic approver, review and approve the submitted
brief, then sign out. As the supplied analyst, create the deterministic local retrieval
link for that exact approved version, sign out, and return as approver to inspect it.
Identify the model version, data version, applicability and primary limitation. State
whether the result is a recruitment recommendation.

Success evidence: separate approval authority, approved version retained, replay link
pins the prior brief version, and the participant answers “no” while identifying
`LIMITED` and `MISSING_EXPERT_RELEVANCE_EVIDENCE` (wording may be paraphrased).

### T3 — Assign and perform scout review (analyst then scout)

As analyst, add one synthetic candidate to the longlist, assign it to the supplied
synthetic scout and request review. As scout, enter the structured rubric, confidence,
a local synthetic clip/note reference, a disagreement with a reason and a next action.
Amend the observation once and inspect both versions.

Success evidence: only the assigned scout can submit; rubric/confidence/reference,
disagreement and next action persist; both observation versions remain visible; no
entry is represented as real scout evidence.

### T4 — Conduct shortlist-meeting mechanics (approver)

Review the brief, retrieval linkage and scout history. Put the candidate on hold with
a controlled reason and owned next action, then create a new revision that rejects the
candidate with a controlled reason. Reconsider that rejection back to longlist using a
new reason, then find the complete decision history.

Success evidence: permitted transitions only, reason and next-action ownership are
retained, reconsideration appends a new revision to the same candidate entry without
changing the rejected revision, and every human action is identifiable and reversible
by a later allowed revision.

### T5 — Export and verify audit evidence (authorised role)

Create the local evidence pack, inspect its classification, values, versions,
limitations and checksum, then inspect the audit receipt. Attempt the supplied denied
export path while signed in as the synthetic admin.

Success evidence: authorised local pack succeeds, checksum verification passes,
owner-only content outside the actor’s visibility is absent, audit linkage is visible,
and the admin attempt is denied without leaking object details.

### T6 — Recover from expiry, conflict and failure

Ask the moderator to run the retained one-session expiry command for the currently
signed-in synthetic actor, then confirm re-authentication is required. Open the same
shortlist revision in two tabs; save one, then try the stale save and recover by
reviewing the newer version. Submit the moderator-supplied invalid or mismatched local
export input, confirm that it fails without an export or audit receipt, then correct the
input and retry.

Success evidence: expired session denied, stale write preserves the winning revision,
no partial workflow/audit/export record remains after failure, and retry succeeds
without duplicate or overwritten history.

### T7 — Keyboard, layout and final interpretation check

Repeat one create/review action using only the keyboard at the desktop size, then
inspect the queue and evidence pack at the mobile size supplied by the moderator.
Answer: “What can this workflow evidence establish, and what can it not establish?”

Success evidence: visible focus, skip link, labelled controls, semantic landmarks,
usable desktop/mobile layout, and an answer limited to workflow mechanics rather than
model quality or recruitment outcome.

## Neutral moderator prompts

Use only: “What are you looking for?”, “What did you expect?”, “Please continue using
what the page shows”, “What does that limitation mean to you?”, and “Would you like to
pause or stop?” Do not name the correct control, interpretation or recovery step.

## Observation rubric and success measures

For each task record `PASS`, `FAIL`, `ASSISTED` or `NOT_RUN`, elapsed whole seconds,
assistance count and a short de-identified observation. `ASSISTED` is not a completion
pass. Also record:

- evidence-boundary interpretation: `CORRECT`, `PARTIAL` or `UNSUPPORTED_INFERENCE`;
- whether access denial disclosed another object’s existence;
- whether material history was identifiable and reversible;
- whether a keyboard blocker, missing label/landmark/focus indicator, horizontal
  overflow or unrecoverable state occurred;
- participant confidence in completing the same synthetic workflow unaided, 1–5.

The G-W08B representative-user gate passes only when all five authorised representative
users provide consent and complete T1–T7 with every core task marked `PASS`; none makes
an unsupported model/recruitment inference after reading the retained limitations;
and there is no P0/P1 access, confidentiality, audit-integrity, reversibility,
accessibility or recovery finding. Any P0/P1 stops the study and returns W08 to bounded
correction plus fresh independent review. Lower-severity usability findings may be
retained only if they do not prevent a core task and are explicitly reviewed by the
master.

## Evidence completion and review

For G-W08B, after all five sessions, the master must:

1. validate five distinct authorised participant codes and consent records;
2. reproduce the captured workflow/audit/export identifiers against each participant
   database without opening protected W06 outputs;
3. verify each capture file checksum and the study-summary checksum;
4. have an independent reviewer check representativeness, protocol adherence,
   de-identification, task outcomes and claim-boundary interpretation;
5. record the reviewed result in the W08 gate report without inventing missing fields.

Until those steps are complete, W08 must not be `VERIFIED`, `CHECKPOINTED` or `CLOSED`,
even when G-W08A has separately authorized bounded W09 experimentation.
