# W04 Wyscout schema design R9 — master verification

## Decision

`REWORK`. The master read all 1,852 R9 design lines and the complete 53-line
producer return, began review with a fresh locked all-groups uv sync, and reproduced
the packet checks and environment census. R9 closes R8's executable, `.pth`,
interpreter-alias, Packaging-bootstrap, and site-bytecode findings, but three P1
construction defects remain. Independent acceptance and implementation remain
blocked.

## Integrity

- R9 design: `96,263` bytes; SHA-256
  `adfb6d79c6c3650f452a86089b3aa3ed4c929ec688f11641c2329dcf4a14decf`.
- R9 producer return: `4,680` bytes; SHA-256
  `d4c28ada32cec9c2abb81afc934f5d53c52c6fb9fe196d9f562f97972246da12`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.

## Retained closures

R9 constructively closes the actual 35-row executable census, the direct-wrapper/
pip-alias/Ruff-wheel-script partition, canonical `python`/`python3` alias topology,
no-site Packaging bootstrap, exact three `.pth` classes, editable-root
normalization, and the site pyc normal/pytest/bootstrap/orphan observations. It
also retains R8's accepted source, rights, temporal, identity, key, coverage,
resource, path, serializer, build, gate, ownership, and ledger boundaries. R10 must
preserve these corrections.

## P1 findings

### Stage-0/build-ID cycle

R9 requires stage-0 to start with an already-empty
`data/working/wyscout/v5/.staging/<build_id>/<run_id>/runtime-pycache/`. The stable
code/environment manifest is produced by stage-0 and is itself a build-ID input;
`build_id` is therefore unavailable when that path must be selected. The sequence
cannot be executed as written.

R10 must use two explicit operational prefixes: a pre-build admission prefix whose
identity is available before stage-0, and, only after code-manifest and build-ID
formation, the existing build/run staging prefix for the rebuild process. Both must
be created empty before their respective interpreter starts, remain empty under
`-S -B`/`PYTHONDONTWRITEBYTECODE`, be rechecked, and stay outside stable identity.

### Unclassified repository orphan

The current repository inventory is 56 pyc files, but only 35 normal and 20 pytest
rewrite files map to an existing source. The remaining normal-shaped file is
`src/scouting/storage/__pycache__/postgres.cpython-312.pyc`; its source was removed
by the accepted container-free storage work. R9 says all 36 normal repository pycs
must map to repo-manifest-owned source, so its own positive census fails.

R10 must classify this exact known repository orphan as optional, inert operational
debris under the same no-read/no-change guard, analogous to the site `six` orphan.
It must not become code, ownership, import, or build authority. A different or
second repository orphan fails pending review.

### Stable-map/count contradiction

R9 simultaneously requires exact current pyc counts/source mappings and says actual
inventories may differ across roots while stable pyc evidence remains equal. A
stable map derived only from sources having a current pyc cannot remain equal when
one root lacks or gains that pyc. It also freezes the current 56-row repository
mapping even though accepted W04 implementation will add repository source files.

R10 must bind a stable, inventory-independent source-authority map over every
admitted installed/repository/bootstrap `.py`, whether or not a pyc currently
exists. Actual pyc files and counts are operational snapshots classified against
that complete map. The current 1,075-site/56-repository counts are first-root
evidence, not two-root or future-code invariants; only the locked 35-executable
census is fixed by the reviewed environment. Optional exact known orphan presence
may differ, but its allowlisted path/predicate is stable.

### Omitted `python3.12` interpreter alias

R9 says the exact venv scripts directory has only two permitted interpreter aliases
and that another alias fails. The locked uv environment actually has three:
`python` points to the admitted physical interpreter, while both `python3` and
`python3.12` point exactly to `python`. All are mode `0755` symlinks with distinct
inodes and the two relative aliases resolve through the same canonical `python`
link. R9 therefore rejects its actual environment.

R10 must admit exactly these three aliases and no fourth, bind both relative chain
rows in stable topology, retain `python` as the only generated-wrapper shebang, and
keep `uv run python`'s `python3` spelling operational.

## Scope provenance

The producer disclosed creating and deleting a duplicate R9 file at the parent
`../reports/...` path. Master verification found no file but did find the three
agent-created empty directories. After confirming that they contained no file or
user work, the master removed exactly those empty directories with `rmdir`; the
parent path is now absent. This process violation is recorded as P2 and no product
content from it is accepted or retained.

## Checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R9 size assertion: PASS; `96,263` bytes.
- Local-only verification: PASS; 25 checks, zero failures.
- Site executable/`.pth` evidence: PASS for the R9 candidate corrections.
- Interpreter-alias census: FAIL; R9 specifies two but the exact uv environment has
  `python`, `python3`, and `python3.12`.
- Repository pyc classification: FAIL; 35 normal mapped, 20 pytest mapped, one
  source-absent `postgres` orphan.
- Orchestration YAML parsing and registry task-ID uniqueness: pending R10 dispatch
  update, then required.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.
- Parent transient path: PASS after precise empty-directory remediation; absent.

No dependency, lock, architecture, provider, network, storage, Git history,
environment cleanup, or local-only change is authorised.
