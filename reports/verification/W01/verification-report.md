# W01 verification report

Status: **PASS**

Verification point: accepted candidate tree, independently rerun by the master
after bounded corrections and before checkpoint creation.

## Reproducible command suite

| Command | Exit | Result |
| --- | ---: | --- |
| `uv lock --check` | 0 | Lock is current; 135 package records. |
| `uv sync --locked --all-groups` | 0 | 135 packages resolved; 132 installed packages audited by uv; one root `.venv`. |
| `uv run python -c "import platform, scouting, sys; ..."` | 0 | Package `0.1.0`; CPython `3.12.12`; root `.venv`; macOS arm64. |
| `uv run ruff format --check .` | 0 | Ten supported files already formatted. |
| `uv run ruff check .` | 0 | All checks passed. |
| `uv run mypy src/scouting` | 0 | No issues in one source file. |
| `uv run pytest -q` | 0 | Two tests passed. |
| `uv run bandit -q -r scripts src` | 0 | No retained static-security findings. |
| `uv run python scripts/install_local_git_guards.py --check` | 0 | Exact active hook is executable and its simulated exit is `1`. |
| `uv run python scripts/verify_local_only.py` | 0 | All 18 W01 local-only checks passed. |
| `git diff --check` | 0 | No whitespace errors. |
| `git remote` | 0 | Standard output is empty. |

## Local-only checks

The machine-readable verifier confirms:

- one root `pyproject.toml`, `uv.lock`, and `.venv`;
- Python 3.12 at both declared and running boundaries;
- exactly the eight approved dependency groups;
- no Git or direct URL dependency declarations;
- no nested environments or alternate Python/Node package-manager manifests;
- no Node manifests, hosted CI, infrastructure-as-code, or deployment control files;
- no outside-root symlinks;
- `main`, zero remotes, ignored `.venv`, and an active rejecting pre-push hook;
- every approved W01 scaffold directory exists.

The lockfile contains normal approved Python-index artifact URLs. It contains no Git
source. No external vulnerability-service query was performed; that egress is not a
G-W01 requirement and would exceed the local-only evidence boundary. The installed
security group and local Bandit check establish the W01 baseline without that egress.

## Preservation evidence

The SHA-256 fingerprints of both controlling HTML documents and the unrelated original
scouting plan match their pre-W01 values. They remain in the parent planning directory
and are not part of the new Git repository.
