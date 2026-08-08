# W09 final verification report

Status: **VERIFIED_AND_READY_FOR_CHECKPOINT**

## Corrective Unicode verification

The current W09 authority is the Unicode-corrected rebuild documented in
`reports/verification/W09/unicode-correction.md`. It supersedes the original text-bearing
canonical, matrix, index and evaluation IDs without changing any feature value, scoring vector,
rank or score. The earlier complete-gate narrative below remains the original checkpoint record;
the correction gate adds focused fail-closed Unicode tests, downstream feature propagation, a
live production browser witness and a fresh independent review.

The final focused correction suite passed 60/60 and the complete W09 contracts-to-browser gate
passed 126/126. The final live production browser returned exactly one `İ. Gündoğan` row for a
`Gündoğan` search, contained zero literal escape sequences and successfully ran the corrected
exemplar query. The fresh independent correction review closed with zero findings at all
severities.

The correction's complete `uv run pytest -q` invocation collected 2,984 tests and produced 2,980
passes plus four W04 frozen-runtime witness failures. All four failures were caused solely by
later-wave ignored PYC files encountered by the frozen W04 repository census. The generated cache
files were moved recoverably to `/private/tmp/w09-unicode-pyc-quarantine.zkISGn`; the exact four
witnesses then passed 4/4 in 85.80 seconds with bytecode writes disabled. The correction evidence
therefore covers all 2,984 collected tests with zero logical failures. No source, retained data or
W04 control was changed to obtain that result.

## Terminal verification

- `uv sync --locked --all-groups`: PASS; 83 packages resolved and 82 audited, with no
  lock or dependency change.
- `.venv/bin/ruff format --check .`: PASS; 1,061 files already formatted.
- `.venv/bin/ruff check .`: PASS.
- `.venv/bin/mypy src/scouting scripts`: PASS; 112 source files.
- `.venv/bin/lint-imports --no-cache`: PASS; 90 modules, 270 dependencies, 5 contracts
  kept and 0 broken.
- `.venv/bin/bandit -q -r scripts src`: PASS; zero findings.
- `.venv/bin/python scripts/install_local_git_guards.py --check`: PASS; executable
  guard and simulated push exit 1.
- `.venv/bin/python scripts/verify_local_only.py`: PASS; 25/25 local-only checks.
- W09 UI packet: PASS; 9 tests.
- W09 evaluation packet: PASS; 17 tests.
- Independent retained-data review packet: PASS; 91 tests, byte-identical evaluation
  regeneration and real browser verification.

## Complete repository suite

The complete `uv run pytest -q` invocation collected 2,977 tests and produced 2,972
passes plus five W04 frozen-runtime failures. Four failures came from a temporary W09
import-boundary declaration in byte-pinned `pyproject.toml`; the fifth came from the
master's over-broad recoverable PYC quarantine moving the retained launcher witness.

The master moved the two W09 import contracts to root `.importlinter`, restored the exact
accepted `pyproject.toml` SHA-256
`963db0004a52d36097bb66d7b5893044e7ac706580b14bae9e7e70e12ce5a89b`, and restored
the retained launcher/foreign-tag PYC witnesses. Because `uv sync` had refreshed editable
package metadata from the later W09 README, the master also restored the ignored W04
editable `METADATA` and RECORD bytes to their accepted digest, without changing source,
the lock, or any dependency. Later-wave PYC files were moved recoverably to
`/tmp/w09-final-pyc-quarantine.ChRndv`; the two W04-required witnesses remain in place.

The exact four admission witnesses then passed 4/4 in 85.54 seconds and the exact outer
PYC-census witness passed 1/1 in 0.64 seconds with bytecode writes disabled. The evidence
set therefore covers all 2,977 collected tests with zero logical failures. No W04 control
was weakened and no W08 implementation was changed.

## Production authority verification

- Source reconciliation: 7 competitions, 142 teams, 3,603 source players, 1,826
  matches, 3,071,395 actions, 68,864 canonical appearances and 16 visible identity
  exclusions.
- Feature authority: 3,603 decisions, 3,059 eligibility grains, 1,975 unique rows,
  1,965 unique eligible players, 16 explainable features and zero synthetic rows.
- Index authority: 1,975 candidates; deterministic robust-scaled weighted Euclidean and
  cosine methods; full admitted-population scoring before limit.
- Frozen evaluation: 9 retained real-player queries, 2,841 score evaluations, exact
  repeatability, explanation/filter witnesses and bounded sensitivity observations.
- Browser: real S. Sirigu exemplar, ranked historical results, 16-term explanations,
  M. Perin/T. Strakosha comparison, canonical report save and exact replay all passed on
  the loopback production composition.

## Claim boundary

G-RW1, G-RW2 and G-RW3 pass. G-RW4 was not performed. The accepted result is a local
historical-resemblance research workbench and reproducible engineering artifact; it is
not evidence of football relevance, recruitment usefulness, recommendation quality,
value, availability, fit or outcomes.
