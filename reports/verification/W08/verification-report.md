# W08 final unattended verification report

Status: **AUTOMATED PASS / G-W08A PENDING / G-W08B BLOCKED**

Lifecycle: `MASTER_REVIEW`. Reviewed pilots: `0/1`. Genuine representative users:
`0/5`.

## Complete repository verification

- `uv sync --locked --all-groups`: PASS; 83 packages resolved and 82 audited.
- `uv run ruff format --check .`: PASS; 983 files already formatted.
- `uv run ruff check .`: PASS.
- `uv run mypy src/scouting scripts`: PASS; 91 source files.
- `uv run lint-imports`: PASS; 63 files, 144 dependencies, all 3 contracts kept and
  0 broken.
- `uv run bandit -q -r scripts src`: PASS; zero findings.
- `uv run python scripts/install_local_git_guards.py --check`: PASS; executable local
  pre-push guard, simulated push exit 1.
- `uv run python scripts/verify_local_only.py`: PASS; 25/25 checks.

The single definitive `uv run pytest -q` invocation collected 2,804 tests. It
completed with 2,800 passes and four W04 runtime-admission failures caused by the
repository's known in-place PYC census host state, before those witnesses' logical
assertions. No W08 product assertion failed.

The master recoverably moved 48 later-wave PYC files to
`/private/tmp/w08-pyc-quarantine.zNsmTZ`, restored the required frozen W04
foreign-cache sentinel at its exact 190,312-byte, mode-0644, single-link identity,
disabled bytecode writing and reran exactly the four failed node IDs. They passed
4/4 in 84.71 seconds. A bounded `--last-failed` confirmation selected those same four
current failures and passed 4/4 with 1,734 tests in the implicated files deselected in
85.62 seconds. One existing third-party Starlette TestClient deprecation warning was
retained. Thus the evidence set covers all 2,804 collected tests with zero logical
failure, without rerunning the complete suite or changing W04 source authority.

## Focused acceptance evidence

- Final independent security/confidentiality surface: 72/72 PASS; P0/P1/P2/P3 all
  zero.
- Fresh exporter/import-boundary surface: 72/72 PASS; exact exporter blob identity,
  3/3 import contracts and zero findings.
- Master exporter/security/web/browser reproduction after relocation: 37/37 PASS.
- Authentication/policy/database producer surface: 26/26 PASS; study-harness/auth
  reproduction: 18/18 PASS.
- Master scout brief and replay correction: 31/31 PASS; master multi-role correction:
  33/33 PASS.
- Browser/accessibility automation: 5/5 real-Chromium tests; 13/13 combined master
  browser/integration/security tests before the narrow-layout correction; 5/5 fresh
  browser tests after the correction.
- Browser mechanical receipt after runtime shutdown: database SHA-256
  `a208b51b...6251`, export-manifest SHA-256 `544689...140e` (abbreviated here; the
  full values remain in the browser/accessibility evidence).

## Outcomes

Authentication/session mechanics, positive and negative authorisation, IDOR denial,
private/team visibility, export privilege and revocation, persisted-byte tamper
denial, audit-chain integrity, concurrency conflicts, atomic failure recovery and
clean retry all pass. Browser and accessibility mechanics pass at desktop, mobile and
320-pixel width, including keyboard navigation, visible focus, semantic landmarks,
labels and internal table scrolling without body overflow.

The evidence proves local workflow mechanics only. It does not validate retrieval,
expert relevance, recruitment outcomes, transfer, price/value or production
readiness. W06 remains `NO_GO / MISSING_EXPERT_RELEVANCE_EVIDENCE /
resemblance_only / synthetic_development_only / LIMITED /
no_recommendation_evidence`. Protected W06 expected outputs were not accessed.

## Remaining staged gates

G-W08A is available but pending: one genuine operator must complete a pilot with T1–T7
all PASS; the receipts, identifiers and claim-boundary interpretation must reproduce;
no P0/P1 may remain; and an independent review must pass. A retained
`PASS / DEVELOPMENT_PROGRESSION_AUTHORIZED` report permits bounded local W09
challenger experimentation while W08 stays `MASTER_REVIEW`.

G-W08B (legacy G-W08) remains blocked at 0/5. Five qualifying representative users
must each complete T1–T7 unaided, all core tasks must pass, and checksums/receipts and
the summary must be reproduced and independently reviewed. Only G-W08B can support
W08 verification, the accepted checkpoint, closure, representative-user acceptance
or the W10 shadow-pilot path. The current phase-verifier failure of
`PHASE_GATE_READY` remains truthful and must not be converted into W08 acceptance by
a G-W08A result.
