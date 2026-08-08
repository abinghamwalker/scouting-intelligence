# W04 checkpoint clean-tree predicate certificate

Date: 2026-08-03
Status: PASS

## Accepted integration checkpoint

- Accepted tag: `checkpoint/w04-accepted`
- Accepted integration commit: `330141315f67df64ba1b7ad63d5c1f6e95c2f978`
- Accepted commit subject: `phase(w04): accept governed data spine`
- `git rev-parse checkpoint/w04-accepted^{}` resolved exactly to the accepted
  integration commit: PASS.
- `git cat-file -t checkpoint/w04-accepted` returned `tag`: PASS.

## Exact ledger paths

Only these two paths belong to the checkpoint-ledger mutation:

1. `orchestration/phase_registry.yaml`
2. `reports/verification/W04/clean-tree-report.md`

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
| index/worktree equality | `git diff --quiet -- orchestration/phase_registry.yaml reports/verification/W04/clean-tree-report.md` | PASS, exit 0 |
| empty remote list | `test -z "$(git remote)"` | PASS, exit 0 |
| active local-only guard | `uv run python scripts/install_local_git_guards.py --check` | PASS, executable guard and simulated rejection |
| accepted tag immutability | `git rev-parse checkpoint/w04-accepted^{}` | PASS, accepted integration commit unchanged |
| registry closure candidate | `uv run python scripts/verify_phase.py --phase W04 --allow-pending-checkpoint` | PASS |
| local-only boundary | `uv run python scripts/verify_local_only.py` | PASS |

The final post-ledger verification is read-only. It requires an empty worktree and
index, zero remotes, the same accepted tag target, the exact ledger commit subject,
an active guard, a CLOSED W04 registry, and a passing local-only verifier.
