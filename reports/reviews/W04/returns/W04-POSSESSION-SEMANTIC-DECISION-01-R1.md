# Subagent return

## Task

- task_id: `W04-POSSESSION-SEMANTIC-DECISION-01-R1`
- objective: Freeze the complete conservative 36-pair Wyscout possession-semantic decision, its exact canonical taxonomy restatement, and a progression-safe authority contract without constructing possessions or beginning Bronze.

## Files changed

- `reports/reviews/W04/authorities/wyscout-possession-semantic-decisions-v1.json`
- `configs/taxonomies/wyscout-v5-possession-taxonomy-v1.yaml`
- `tests/contracts/test_w04_possession_semantic_authority.py`
- `reports/reviews/W04/returns/W04-POSSESSION-SEMANTIC-DECISION-01-R1.md`

## Summary

- Frozen exactly 36 non-overlapping predicates, one for every exact integer `(event_id, subevent_id)` pair reproduced from the fixed event-taxonomy CSV. No tag partition is used.
- Decision distribution is `CONTROL=11`, `RESTART=7`, `DEAD_BALL=8`, `CONTESTED=4`, `NON_CONTROL_ADMIN=2`, and `UNMAPPED=4`.
- All four Duel pairs buffer until the following resolved same-period possession. Dead-ball rows explicitly select either preceding-resolved-possession attachment or unassigned attachment. Unknown or unmatched combinations remain `UNMAPPED`.
- Every rationale identifies the classification as a conservative project-owned inference from the frozen local taxonomy and expressly denies provider-native possession truth. Runtime matching is limited to integer selectors and frozen digests.
- The decision is strict canonical JSON with one terminal LF. The taxonomy is the deterministic safe canonical-YAML restatement and binds the decision SHA-256.
- The 112-case contract derives the expected 36-pair universe and 59-tag universe from the frozen CSV bytes. It enforces strict schemas and types, canonical JSON/YAML, frozen digests, pair coverage, sorting, non-overlap, tag rules, actor equality, the complete combination union, rationale requirements, taxonomy equality, and candidate digest edges.
- The contract is progression-safe: absent review/acceptance is valid at this packet boundary, and any later exact review/acceptance is fully validated when present. Downstream possession, dependency, Bronze, product, and runtime outputs remain blocked without a valid PASS review and formal acceptance.

## Tests run

- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `112 passed in 4.49s` after final formatting; a confirmatory earlier post-correction run also passed all 112 in 4.75s.
- command: `uv run --locked --no-sync ruff format --check tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `1 file already formatted`.
- command: `uv run --locked --no-sync ruff check tests/contracts/test_w04_possession_semantic_authority.py`
  - exit status: `0`
  - result: `All checks passed!`
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, 25 checks and zero failures; zero configured remotes, local `main`, active push guard, one root uv project, Python 3.12.12, and no hosted CI, deployment, container, or external-service artifact.
- developmental correction evidence:
  - The first focused run exited `1` with `15 passed, 97 failed`; every failure shared the noncanonical taxonomy surface cause. The owned taxonomy was mechanically rendered with the accepted no-alias canonical dumper without changing parsed values.
  - The next run exited `1` with `111 passed, 1 failed`; the remaining failure was the test's expected error wording for a deliberately appended duplicate. The duplicate fixture was inserted in sorted position so the intended overlap rejection is tested, after which all 112 passed.
  - The first Ruff format check exited `1` because the new contract required mechanical formatting. `uv run --locked --no-sync ruff format tests/contracts/test_w04_possession_semantic_authority.py` reformatted the owned test, and both final Ruff checks passed.
  - A read-only canonical-digest helper attempted with `python -S -B` exited `1` because `-S` intentionally hides the installed `yaml` package. The exact helper was rerun with `python -B` under the same locked/no-sync uv environment and exited `0`.

## Artifacts/evidence

- decision:
  - ID: `w04-wyscout-possession-semantic-decisions-v1`
  - bytes: `22148`
  - physical/canonical SHA-256: `4161e0c062a1ad7a819a2c28c49473d54ae0494184e907a81eccbb88975c8d71`
  - decided at: `2026-07-30T16:12:58Z`
  - decided by: `4efe5691-8903-5148-8275-30d2e7e8aed0`
- taxonomy:
  - ID: `w04-wyscout-possession-taxonomy-v1`
  - bytes/lines: `22189` / `451`
  - physical SHA-256: `e456377183d6e7f3742a64dcbbd2972eeb6cc70ef55184d40c2dbb822e15a78d`
  - canonical SHA-256: `6a598da111bdf4be71b59d5646d56560c0024ffd7532d95e1553aa6fcaf4fdfa`
  - canonical JSON bytes: `22102`
- contract:
  - lines: `1270`
  - SHA-256: `a5539c6c2e19d15579a033bc276358479a737d12dffefe4fe211b3f6cb7877f5`
  - cases: `112`
- frozen input digests independently reproduced by the contract:
  - event taxonomy: `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`
  - tag taxonomy: `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`
  - field registry canonical: `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`
  - field acceptance: `fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365`
- actual shell-only pyc preflight:
  - repository: `59` pycs in `19` `__pycache__` directories; complete metadata/header/content row digest `8d75a0f8dc3ffe214bcf28fd8f5c5584ec12f3dbef0499968c49f7c73c5f051c`; ordered content digest `c53ff5132b4d4a644aca5b9cf6dfddf3e65cd6eb8e4dee30a90115e38fa80b00`.
  - site-packages: `1086` pycs in `131` `__pycache__` directories; complete metadata/header/content row digest `c518da93727357ac3097ca6f62cc92f116e33da3bf2ad4e6c05df85c0a579923`; ordered content digest `ea4e63c8e850193c8e7bd235575fe88d7389d902350dd38469737e8f41176bd8`.
- execution-time absence evidence:
  - the separately owned review and acceptance paths are absent;
  - all checked Wyscout possession, dependency, staging, identity, Bronze, Silver, Gold, manifest, admission/rebuild/launch, and runtime construction paths are absent.

## Risks

- Possession semantics are deliberately conservative project classifications derived only from frozen local integer taxonomy evidence. They are not provider-native possession truth and remain subject to independent semantic review before acceptance or construction.
- Save attempts, goalkeeper-leaving-line, and simulation remain explicitly `UNMAPPED`; this preserves uncertainty rather than inventing possession behavior.

## Follow-up items

- Dispatch the separately owned independent possession-semantic review packet. Do not construct possessions or begin Bronze until a valid PASS review is formally accepted by the master.

## Scope confirmation

- no Git operations: confirmed; no direct or mutating Git command was run. The packet-required local-only verifier performed its own read-only branch, remote, ignore, and guard checks.
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml`, `uv.lock`, and `.venv` were not edited and no sync occurred.
- no edits outside `allowed_paths`: confirmed; exactly the four packet-owned paths were created or modified.
- no delegation or self-approval: confirmed.
- no provider/network access, external service, cloud, hosted CI, public endpoint, container, or deployment activity: confirmed.
