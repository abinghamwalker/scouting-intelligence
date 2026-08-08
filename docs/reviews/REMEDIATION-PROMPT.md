# Handoff prompt — post-W10 remediation pass

Revised 2026-08-06 after the W10 v2 engineering work landed and the review was revalidated.
Paste the block below into a fresh Claude Code session started in
`/Users/adrian/Documents/personal_repos/investigation_v2/scouting-intelligence`.

**Timing note:** W10 is still `REWORK`. `W10-V2-PROTOCOL-FREEZE-08E` and
`W10-V2-INDEPENDENT-REVIEW-08F` are unstarted, and the formal study `W10-FORMAL-EXPERT-STUDY-02B`
is `PLANNED` and blocked by both. The pre-freeze window is therefore **still open** — see the
blocking decision below, which changed identity in the revalidation.

---

```
Read `docs/reviews/cross-phase-code-review-2026-08-06.md` in full before touching any code. It is a
cross-phase code review of this repository, plus two appended sections you must also read:
"Remediation plan — single-pass, post-W10" and "Revalidation after W10 v2 landed". The revalidation
changes the status of several findings — trust it over the original body where they disagree.

Every finding has a stable ID (C1-C12 complexity, P-1..P-15 performance, L-1..L-16 logic,
M-1..M-7 missing/incomplete, W10-1..W10-4 W10-specific). Use those IDs in your plan and reports.

Also read `AGENTS.md` first. It is binding. The master owns every Git operation, phase gate,
checkpoint and tag. Do not run any Git command that mutates state — no add, commit, tag, branch,
stash, reset, checkout or rebase. Do not edit `.git`. Leave changes in the working tree and report.

## Where you are in the workflow

This pass is running BEFORE `W10-V2-PROTOCOL-FREEZE-08E`. W10 is `REWORK`; 08E and
`W10-V2-INDEPENDENT-REVIEW-08F` are unstarted; `W10-FORMAL-EXPERT-STUDY-02B` is `PLANNED` and
blocked by both. Nothing is frozen yet.

That is the favourable case and it changes one thing: W10-2 can be *fixed properly* now rather than
recorded as a permanent limitation in a frozen protocol. Treat it as remediable, not as something
to document around.

## Task

Apply the review's corrections in one deliberate pass, in the batch order the remediation plan
specifies (A -> B -> C -> D -> E, plus the standalone items), with the W10 additions below.

## The thing that will go wrong if you ignore it

Three source files are SHA-256'd into the artifacts they produce and re-checked on load:
`m0/scoring.py` (tier 1, research index), `features/historical.py` (tier 2, feature matrix),
`data_products/wyscout/historical.py` + `sources/wyscout_historical.py` (tier 3, canonical build).
A one-byte edit to any of them invalidates that artifact and everything downstream:
canonical -> matrix -> index -> saved experiments -> W10 v2 evidence.

The remediation plan has the verified call sites and rebuild entry points. Read that table before
you plan. Getting it wrong produces silent INCOMPATIBLE_PINS on saved experiments, or a "stale
scorer pin" failure that looks like a code bug and is not.

Batch each tier so you rebuild it exactly once. Never interleave refactors (Batch E) with rebuilds.

## Decision required BEFORE W10-V2-PROTOCOL-FREEZE-08E — do not decide this implicitly

This is finding W10-2, and it replaces L-5 as the pre-freeze blocker.

`storage/expert_study.py:2277` orders v2 presentations as `enumerate(self.comparisons, 1)` — the
authority file's array order, identical for every participant. The v1 formal path is stronger:
`contracts/expert_relevance.py:1386-1492` applies a participant-digest-keyed SHA-256 permutation,
places repeat anchors in keyed delayed slots, and enforces nonterminal/nonadjacent repeats.

The query pack builds `candidates=(*retrieved, *frozen_controls)`
(`scripts/build_w10_expert_protocol.py:490`) — retrieved first. In v1 the keyed permutation
destroys that correlation. In v2 nothing does.

Acceptable for a mechanics pilot. Not acceptable for formal collection: order effects would be
confounded with specific candidates and retrieved/control position may be inferable.

Stop and ask the user before 08E:
  (a) the v2 formal path inherits `build_formal_candidate_presentations` (participant-keyed); or
  (b) v2 keeps fixed ordering and the limitation is recorded explicitly in the frozen protocol.
Do not pick one yourself. If (a), also add a contract test asserting provenance does not correlate
with presentation ordinal.

## Status corrections since the original review

- M-7 is FIXED (roster entries added). The underlying design flaw is not: the same four entries had
  to be hand-added to three files, and it will recur on the next new module. Fix the derivation.
- L-5 is NO LONGER a pre-freeze blocker. Verified: `lineup_match_coverage` is not rendered to
  participants (`v2_participant.html:18` renders only governed minutes and minute state). It is
  still a constant-1.0 field inside the retained, digested evidence bytes. Treat as normal tier-2
  work in Batch C. Do not re-escalate it.

## Scope

In scope: everything in the review, including W10-1..W10-4. W10 code is now in scope — the original
review excluded it, the revalidation section does not.

If Batch C rebuilds the matrix, `configs/evaluation/w10-expert-evidence-presentation-v2.json` pins
`canonical_build_id`, `matrix_version` and `matrix_digest` as literals and declares
`"stability_validation_required_before_formal_freeze": true`. Re-pinning it and re-running threshold
validation is then part of the work, not an afterthought. Confirm with the user before doing it.

Out of scope: new features, dependency changes, `pyproject.toml`, `uv.lock`, migrations, and
anything the review does not name. If you find a new defect, add it to the review file with a new ID
and priority; do not silently fix it.

## Verification

Baseline: `ruff` clean, `mypy src/scouting` clean. The master's recorded full-gate result for the
landed W10 work is 3,091 passed in ~34m48s (`reports/verification/W10/v2-scientific-adversarial-verification.md`).
Reproduce that yourself before starting — do not take it on trust — and treat anything failing
beyond your own reproduced baseline as a regression you introduced.

Run after each batch (the suite takes ~35 minutes — run it in the background and keep working):
  uv run ruff format --check . && uv run ruff check .
  uv run mypy src/scouting
  uv run pytest -q
  uv run python scripts/verify_local_only.py

After any rebuild, also confirm `scripts/evaluate_w09_retrieval.py` passes and that saved
experiments either replay REPRODUCED or are explicitly accepted as INCOMPATIBLE_PINS.

## Working style

Plan before editing: list the batches, which findings are in each, which tier each touches, and
which rebuilds each triggers. Show me that plan before starting Batch A.

Work batch by batch and report after each: findings applied, files changed, rebuilds run,
verification results, and anything skipped and why. Do not report a batch complete until its
verification has actually passed — quote the output.

If a fix turns out to be wrong, or the review mischaracterised something, say so plainly and update
the review file rather than working around it. The review has already been wrong once (L-5) and was
corrected; that is the expected behaviour, not a failure.
```

---

## Notes for the human

- The blocking decision **changed identity**: it was L-5, it is now W10-2. L-5 turned out not to
  reach participants; W10-2 is a real v1 capability that did not carry into v2, and 08E is where it
  becomes permanent.
- W10-2 is the one item genuinely worth acting on before the freeze. Everything else can wait for
  the single post-W10 pass.
- `docs/reviews/` was chosen over `reports/reviews/` because `reports/` is phase-scoped,
  master-owned acceptance evidence and this review is neither. Update the path in the prompt if you
  move it.
- Both files remain untracked. Committing them is a master-owned Git operation.
