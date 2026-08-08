# W04 Wyscout schema design R8 — master verification

## Decision

`REWORK`. The master read all 1,498 R8 design lines and the complete producer
return, reproduced the packet checks, and compared the proposed installed-file
admission against the freshly synchronised all-groups uv environment. R8 closes
the ten returned R7 defects, but its executable classification is not complete for
the actual locked environment. No independent review or implementation packet is
authorised from R8.

## Integrity

- R8 design: `73,683` bytes; SHA-256
  `26a887bef1872ed18d22fb23e3a16c80469ca703b453497de4053a6c02fae50c`.
- R8 producer return: SHA-256
  `002dac1ebaba6edecbe424a485b511b56db2179d16ccc0d35f078146a3ed8a50`.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.

## Retained closures

R8 restores the exact strict-before temporal rule, completion-path record-family
authority, known Bronze path, player-match and Gold keys, separate source and Gold
coverage contracts, pre-existing-pyc enumerate-and-deny policy, operational-only
absolute uv path, exact 17 resources, ownership graph, and two-local-commit ledger.
Those corrections are retained for R9.

## Reproduced executable evidence

- Fresh `uv sync --locked --all-groups` produces 35 installed
  `../../../bin/*` RECORD rows across 21 owners.
- Thirty-three rows correspond directly to verified console/gui entry-point names.
- Ruff 0.16.0 owns `../../../bin/ruff`, but has no console/gui entry point. Its
  extracted RECORD instead owns `ruff-0.16.0.data/scripts/ruff`; the installed
  Mach-O file is byte-identical, mode `0755`, size `23,669,488`, and SHA-256
  `1ac190f23d9a690d75b3e74eb88a07e02f6414227a41ba1920609af989ecec52`.
  R8's entry-point-only controlled path rule therefore rejects one member of `I`.
- Pip 26.1.2 declares `pip` and `pip3`, but uv also owns the deterministic
  interpreter-version alias `../../../bin/pip3.12`. All three wrappers are
  byte-identical. R8 has no constructive authority for the extra alias.
- uv-generated Python wrappers use the exact shebang
  `<project>/.venv/bin/python`, while `uv run python` reports
  `<project>/.venv/bin/python3`. Both safe venv aliases resolve to the same physical
  Python 3.12.12 interpreter, but R8 incorrectly requires the wrapper spelling to
  equal the launch-time `sys.executable` spelling.
- The site root contains three `.pth` files. `_virtualenv.pth` is unowned,
  executable content that imports the unowned `_virtualenv.py`;
  `a1_coverage.pth` is a RECORD-owned executable coverage hook; and the editable
  root `scouting_intelligence.pth` contains the absolute project `src` path. R8
  rejects executable `.pth` files and has no authority/normalization for the uv
  bootstrap or root-bearing editable metadata. A clean `uv run python -S` proves a
  constructive no-site launch is available: `_virtualenv` is absent and no
  site-packages path has been added.
- Of 1,075 current site-root pyc files, 962 use the normal cache grammar, 112 use
  pytest assertion-rewrite names such as
  `module.cpython-312-pytest-9.1.1.pyc`, and one is an orphaned
  `six.cpython-312.pyc` whose source is absent. R8's normal-only,
  source-owned grammar rejects 113 existing files despite its no-cleanup rule.
  The uv bootstrap pyc also needs explicit bootstrap ownership.
- The repository itself contains 56 pyc files in 17 `__pycache__` directories.
  They can be made inert by the same early alternate-prefix/no-read guard but are
  outside R8's site-root-only operational inventory.
- R8 says pre-execution admission imports no third-party code while selecting tags
  through `packaging.tags.sys_tags()`. R9 must make this ordering constructive,
  either with a stdlib/repository-owned selector or a narrowly bootstrapped,
  byte-admitted `packaging` stage before any other third-party execution.

## Checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- R8 size assertion: PASS; `73,683` bytes.
- Local-only verification: PASS; 25 checks, zero failures.
- Installed script classification: FAIL as candidate acceptance evidence; 35 total,
  33 direct entry-point wrappers, one pip version alias, one wheel-provided script.
- Ruff extracted-to-installed byte comparison: PASS as defect evidence.
- Python wrapper/interpreter alias comparison: PASS as defect evidence.
- Existing pyc inventory: 1,075 files; R8 enumerate-and-deny policy retained.
- Site-root pyc classification: FAIL as candidate acceptance evidence; 962 normal,
  112 pytest assertion-rewrite, one orphan.
- Repository pyc inventory: FAIL as candidate acceptance evidence; 56 files in 17
  cache directories are not covered by R8's inventory.
- Site bootstrap inventory: FAIL as candidate acceptance evidence; two executable
  `.pth` files plus root-bearing editable metadata lack a constructive no-execution
  authority.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

## Bounded R9 correction

R9 remains report-only. It must partition every installed `../../../bin/*` RECORD
row into a total, mutually exclusive, verified class: generated entry-point wrapper,
the exact reviewed pip interpreter-version alias, or wheel-provided `.data/scripts`
payload. It must bind safe path resolution, ownership, actual bytes/hash/size/mode,
stable two-root treatment, collision rejection, and rebuild read/execute denial for
all classes. It must also define the canonical safe venv wrapper-interpreter alias
and prove all accepted aliases resolve to the admitted physical interpreter rather
than comparing an incidental `sys.executable` spelling. It must additionally use an
exact no-site/stdlib-first launch or equivalently strict mechanism so executable
`.pth` files never run, classify uv bootstrap and editable-root metadata, cover
normal, pytest-rewrite, orphaned-inert, bootstrap, and repository pyc without
cleanup, and remove the pre-execution `packaging` import cycle.

No dependency, lock, architecture, provider, network, storage, Git, environment
cleanup, or local-only change is permitted.
