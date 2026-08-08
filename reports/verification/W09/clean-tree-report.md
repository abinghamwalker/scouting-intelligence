# W09 checkpoint clean-tree predicate certificate

Date: 2026-08-05
Status: **PASS**

## Accepted integration checkpoint

- Start tag: `checkpoint/w09-start`
- Accepted tag: `checkpoint/w09-research-workbench-accepted`
- Accepted annotated tag object: `3b820a0ef12d065aa5e7b11c6d0ae56386160b35`
- Accepted integration commit: `f57ce70e84b74c5c43b9691d2df93fd977042954`
- Accepted integration commit subject: `phase(w09): accept historical research workbench`
- `git rev-parse checkpoint/w09-research-workbench-accepted^{}` resolved exactly to
  the integration commit: PASS.
- `git cat-file -t checkpoint/w09-research-workbench-accepted` returned `tag`: PASS.

## Exact ledger paths

Only these four paths belong to the post-tag checkpoint-ledger mutation:

1. `orchestration/master_plan.yaml`
2. `orchestration/phase_registry.yaml`
3. `reports/verification/W09/clean-tree-report.md`
4. `tests/unit/test_orchestration_controls.py`

No ledger commit identity or tree hash is embedded in the ledger.

## Pre-checkpoint predicates

| Predicate | Result |
|---|---|
| existing user and W08 changes preserved by the W09 start checkpoint | PASS |
| no configured Git remotes | PASS |
| active executable local-only push guard | PASS |
| dependency lock unchanged | PASS |
| complete repository evidence | PASS, 2,972 complete-run passes plus exact recovered 5/5 |
| G-RW1, G-RW2 and G-RW3 | PASS |
| independent review | PASS, zero open P0/P1/P2/P3 |
| G-RW4 claim boundary | PASS, absence recorded and positive claims blocked |
| W08 disposition | PASS, preserved dormant optional module |
| next-phase boundary | PASS, W10 remains PLANNED and unstarted |

Immediately before staging the ledger mutation, the worktree and index were empty. Immediately
before its commit, there was no unstaged or untracked path and the index contained exactly the
four ledger paths above. The remote list was empty, the accepted tag peeled to the exact
integration commit, and the W09 phase candidate passed. Final post-ledger checks are read-only:
normal W09 phase verification, an empty worktree/index, zero remotes, the same tag target,
CLOSED W09, PLANNED W10 and the active local push guard.

## Provider Unicode corrective checkpoint

- Corrective tag: `checkpoint/w09-unicode-correction-accepted`
- Corrective annotated tag object: `b7ceb23fc1559b53138885da44c90fb1c84b049f`
- Corrective commit: `04c95ee08a79d3515ba20b20f5085929f16c3fd6`
- Corrective commit subject: `fix(w09): normalize retained provider Unicode text`
- `git rev-parse checkpoint/w09-unicode-correction-accepted^{}` resolved exactly to the
  corrective commit: PASS.
- `git cat-file -t checkpoint/w09-unicode-correction-accepted` returned `tag`: PASS.
- Complete correction evidence: 2,980 complete-run passes plus the exact recovered 4/4 W04
  witnesses, covering all 2,984 collected tests with zero logical failures.
- Later-wave ignored PYC files were moved recoverably to
  `/private/tmp/w09-unicode-pyc-quarantine.zkISGn`; no source, retained data or W04 control was
  changed by that cleanup.
- Independent Unicode correction review: PASS, zero open P0/P1/P2/P3.
- Corrected live workbench: readable Unicode names and zero visible literal escape sequences.
- Ranking boundary: feature arrays, scaled index vectors, candidate ordering, ranks and scores are
  unchanged.

The corrective checkpoint records the text-fidelity repair only. W09 remains CLOSED, W10 remains
PLANNED and G-RW4 remains not performed.
