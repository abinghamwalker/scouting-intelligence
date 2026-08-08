# W02 verification report

Status: **PASS**

Verification point: accepted W02 candidate tree, independently rerun by the master after
the synthetic correction and before checkpoint creation.

## Reproducible command suite

| Command | Exit | Result |
| --- | ---: | --- |
| `uv sync --locked --all-groups` | 0 | 135 packages resolved; 132 installed packages audited; existing root `.venv`. |
| `uv run ruff format --check .` | 0 | 25 supported files already formatted. |
| `uv run ruff check .` | 0 | All checks passed. |
| `uv run mypy src/scouting scripts` | 0 | No issues in eight source files. |
| `uv run pytest -q` | 0 | Ten tests passed. |
| `uv run bandit -q -r scripts src` | 0 | No retained static-security findings. |
| `uv run python scripts/install_local_git_guards.py --check` | 0 | Exact active pre-push hook is executable and simulated exit is `1`. |
| `uv run python scripts/verify_local_only.py` | 0 | All 21 local-only/environment checks passed. |
| `uv run python scripts/verify_parallel_safety.py` | 0 | Five required allow/deny scenarios passed. |
| `uv run python scripts/verify_task_return.py ...R2...` | 0 | Corrected structured and Markdown returns passed with no failures. |
| `git diff --check` | 0 | No whitespace errors. |
| `git remote` | 0 | Standard output is empty. |

The master also reruns
`uv run python scripts/verify_phase.py --phase W02 --allow-pending-checkpoint`
against the complete evidence candidate, then reruns the normal command without that
flag after creating the accepted local tag.

## Machine-readable controls

- `verify_local_only.py` reports stable named checks for Git remotes/branch/guard,
  Python and root uv state, forbidden package managers, hosted/deployment files,
  structured-config parsing, outside-root values, prohibited URLs, skeleton paths,
  symlinks, and ignored `.venv`.
- `verify_task_return.py` reports stable failure codes for packet, scope, typed scope
  confirmation, uv-only check records, exact return paths, and mandatory headings.
- `verify_parallel_safety.py` allows only the path-disjoint fixture/readme case and
  denies `uv.lock`, contracts, migrations, and overlapping scopes.
- `verify_phase.py` checks allowed/gate-ready state, closed dependencies, accepted and
  evidenced tasks, required evidence, declared checks, zero remotes, checkpoint tags
  and subjects, and the final clean tree.

## Boundary confirmation

There is still one root `pyproject.toml`, `uv.lock`, and `.venv`, running Python
3.12.12. There is no Git remote, hosted CI, cloud resource, public endpoint, external
model call, or deployment. No product code or W03 work exists.
