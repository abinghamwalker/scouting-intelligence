# W03 verification report

Status: **PASS**

Verification point: final accepted W03 candidate after R6 implementation, independent
R2 review, and the master-owned continuous-authority test correction.

## Complete master command suite

| Command | Exit | Result |
| --- | ---: | --- |
| `uv sync --locked --all-groups` | 0 | 142 packages resolved; 139 installed packages audited in the one root environment. |
| `uv lock --check` | 0 | 142 packages resolved with no lock drift. |
| `uv run ruff format --check .` | 0 | 101 files already formatted. |
| `uv run ruff check .` | 0 | All checks passed. |
| `uv run mypy src/scouting scripts` | 0 | No issues in 37 source files. |
| `uv run lint-imports --no-cache` | 0 | 27 files/37 dependencies; 3 contracts kept, 0 broken. |
| `uv run pytest -q` | 0 | 185 passed; one disclosed upstream TestClient deprecation warning. |
| `uv run bandit -q -r scripts src` | 0 | No retained static-security finding. |
| `uv run python scripts/validate_w03_governance.py` | 0 | Frozen authorization, data-rights, and local-review controls passed. |
| `uv run python scripts/run_w03_protected_gate.py` | 0 | Ten protected checks passed; exact and repeat digest `dcab08…53e`. |
| `uv run python scripts/install_local_git_guards.py --check` | 0 | Executable pre-push guard reproduced exit `1`. |
| `uv run python scripts/verify_local_only.py` | 0 | All 21 local-only and one-root-uv checks passed. |
| `docker compose config --quiet` | 0 | Local service configuration is valid. |
| `docker compose ps --format json` | 0 | PostgreSQL/pgvector and Redis are healthy and published only on `127.0.0.1`. |
| `git diff --check` | 0 | No whitespace errors. |
| `git remote` | 0 | Standard output is empty. |

Database-backed commands used only the approved loopback PostgreSQL URL supplied at
runtime. The ephemeral review password is absent from the project tree.

## Independent and protected evidence

- R1 boundary review deliberately remains a failing historical artifact and records
  the P1 collision. It is not part of the final green suite.
- The unchanged R1 reproduction and additive R2 tests pass on R6: 17 independent
  boundary checks.
- The master-only protected gate selects only `PROTECTED_TEST`, performs exact
  contract/result/explanation and admitted/rejected-fact comparisons, proves no
  post-cutoff admission, and reproduces the same result digest twice.
- Implementers and independent reviewers did not access the protected partition or its
  expected output.

## Local security and supply-chain evidence

The local secret scan returned only manually reviewed commit/content SHA false
positives; the narrowed rerun returned no findings. The locked Python licence inventory
and its three pre-existing `UNKNOWN` metadata cases are disclosed in
`security-dependency-container-report.md`. Cached image identities and loopback
bindings are recorded there as well.

No external vulnerability-service query was performed because the accepted W01
boundary records that egress as outside the local evidence contract. No cloud scanner,
hosted CI, public registry, remote repository, or deployment was used.

