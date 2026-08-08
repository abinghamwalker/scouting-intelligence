# W08 morning handoff — pilot progression and representative acceptance

Status: **READY TO RUN; NO PILOT OR PARTICIPANT RESULT EXISTS**

The smallest next action is one end-to-end pilot in `W08-P01`. If it passes T1–T7 and
its receipts and boundary interpretation are reproduced and independently reviewed,
the master may record G-W08A PASS and begin bounded local W09 experimentation. The
five representative users remain a later, separate requirement for W08 acceptance.

## Browser-first study console

On macOS, open `scripts/start_w08_study_console.command` from Finder. Keep its small
launcher window open while moderating. The browser console then handles qualification
and consent, fresh participant runtime creation, synthetic credentials, T1–T7 capture,
exact-actor session expiry, safe runtime stop and the database/export receipts.

The console remains a local operator aid. It cannot provide consent, turn an automated
persona into a participant, change a captured outcome, perform independent review or
accept either gate. Existing capture files are opened in place and are changed only
when the moderator explicitly saves the corresponding browser form.

The console also provides three clearly marked pilot slots (`W08-P01`–`W08-P03`). Use
one first to smoke-test setup, navigation, role switching, T1–T7, failure recovery and
receipt generation. Pilot captures remain under the local temporary study parent and
use the distinct `w08_pilot_progression_capture` record type. A complete capture is
candidate G-W08A evidence, not an automatic pass; the master must reproduce it and
obtain independent review. It never increments, replaces or qualifies one of the five
G-W08B representative-user records. After any pilot-driven correction, freeze the
reviewed build and rerun the pilot before seeking progression review.

New pilot runtimes open a guided journey with persistent role and next-action
navigation. Synthetic roles switch with one click inside the pilot application; actor
IDs and passwords are a manual fallback only. The concise operator guide is
`reports/verification/W08/pilot-user-guide.md`. Representative-user runtimes retain
the explicit credential workflow because their authentication hand-off remains part
of the formal study.

The commands below remain the audited fallback and mechanical implementation reference.

## Before the pilot or first participant

From the repository root:

```bash
test "$(git branch --show-current)" = main
test -z "$(git remote)"
uv sync --locked --all-groups
uv run python scripts/install_local_git_guards.py --check
```

Read the complete `reports/verification/W08/moderated-study-protocol.md`. Create no
real-player or employer-confidential input. Use `W08-P01` for the first pilot; reserve
de-identified codes `W08-U01` through `W08-U05` for the representative cohort.

## One fresh runtime per participant

Choose an unused, non-existent local path and a free unprivileged port. For U01, for
example, start terminal A with:

```bash
uv run python scripts/run_w08_study.py serve \
  --study-root /private/tmp/w08-study-W08-U01 \
  --port 18768
```

The command refuses a reused/symlink/broad root, binds only `127.0.0.1`, disables the
access log and prints ephemeral synthetic credentials. Never copy a password into a
capture file.

Copy the capture template to a new participant path only after consent:

```bash
mkdir -p reports/verification/W08/participants
cp reports/verification/W08/moderated-study-capture-template.yaml \
  reports/verification/W08/participants/W08-U01.yaml
```

Moderate T1–T7 exactly. For T6, terminal B expires only the current exact actor:

```bash
uv run python scripts/run_w08_study.py expire-session \
  --study-root /private/tmp/w08-study-W08-U01 \
  --actor-id ACTOR_UUID_SHOWN_BY_TERMINAL_A
```

After T7, let the participant review the de-identified capture, stop terminal A, then
produce the mechanical receipt:

```bash
uv run python scripts/run_w08_study.py receipt \
  --study-root /private/tmp/w08-study-W08-U01
```

Record the database and export-manifest SHA-256 values plus the checked-out commit in
the capture. Repeat with a new root and port for U02–U05.

## Complete G-W08A and continue development

After one pilot is complete, stop its runtime and retain the generated receipt. The
master reproduces T1–T7, the database/export hashes and the claim-boundary answer,
checks for unresolved P0/P1 findings, and obtains an independent review. Only then may
`reports/phase-gates/W08/pilot-gate-report.json` change to:

```text
status: PASS
decision: DEVELOPMENT_PROGRESSION_AUTHORIZED
authorized_scope: bounded_local_w09_challenger_experimentation
```

That exact record permits W09 to move from `PLANNED` into bounded local challenger
work. W08 stays `MASTER_REVIEW`; do not create the W08 accepted tag or make a
representative-user claim.

## Complete G-W08B and accept W08

Populate a copy of `moderated-study-summary-template.yaml` only from the five real
captures. The master must reproduce their identifiers/receipts, validate distinct
authorised roles and consent, and commission a fresh independent review of
representativeness, protocol adherence, de-identification, outcomes and checksums.

Only if all five complete T1–T7 unaided with no unsupported claim inference or P0/P1
finding may W08 be verified, accepted, tagged `checkpoint/w08-accepted`, checkpointed
and closed. Otherwise retain the truthful finding and perform bounded correction plus
fresh review. Without G-W08A PASS, do not begin W09; with G-W08A PASS, restrict W09 to
the exact bounded local experimentation scope while G-W08B remains pending.
