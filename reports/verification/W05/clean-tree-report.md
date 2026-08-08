# W05 checkpoint clean-tree predicate certificate

Date: 2026-08-03
Status: PASS

## Accepted integration checkpoint

- Accepted tag: `checkpoint/w05-accepted`
- Accepted annotated tag object: `ddd7607d202bc3b98a3977c4c8f5d95a2a96950d`
- Accepted integration commit: `1dd3f6e3296100b3d1615bd57e18cf256e312043`
- Accepted commit subject: `phase(w05): accept transparent retrieval baseline`
- `git rev-parse checkpoint/w05-accepted^{}` resolved exactly to the accepted
  integration commit: PASS.
- `git cat-file -t checkpoint/w05-accepted` returned `tag`: PASS.

## Exact ledger paths

Only these two paths belong to the checkpoint-ledger mutation:

1. `orchestration/phase_registry.yaml`
2. `reports/verification/W05/clean-tree-report.md`

No ledger commit SHA, repository tree hash, or digest of this report is embedded in
the ledger.

## Predicate certificate

The master ran and confirmed the following immediately before the ledger commit:

| Predicate | Command | Result |
|---|---|---|
| no unstaged path | `git diff --quiet` | PASS, exit 0 |
| no untracked path | `test -z "$(git ls-files --others --exclude-standard)"` | PASS, exit 0 |
| exact staged roster | `git diff --cached --name-only` | PASS, exactly the two ledger paths above |
| staged whitespace | `git diff --cached --check` | PASS, empty output |
| index/worktree equality | `git diff --quiet -- orchestration/phase_registry.yaml reports/verification/W05/clean-tree-report.md` | PASS, exit 0 |
| empty remote list | `test -z "$(git remote)"` | PASS, exit 0 |
| active local-only guard | `uv run python scripts/install_local_git_guards.py --check` | PASS, executable guard and simulated rejection |
| accepted tag immutability | `git rev-parse checkpoint/w05-accepted^{}` | PASS, accepted integration commit unchanged |
| registry closure candidate | `uv run python scripts/verify_phase.py --phase W05 --allow-pending-checkpoint` | PASS |
| local-only boundary | `uv run python scripts/verify_local_only.py` | PASS, 25/25 |

The final post-ledger verification is read-only. It requires an empty worktree and
index, zero remotes, the same accepted tag target, the exact ledger commit subject,
an active guard, a CLOSED W05 registry and a passing local-only verifier.
