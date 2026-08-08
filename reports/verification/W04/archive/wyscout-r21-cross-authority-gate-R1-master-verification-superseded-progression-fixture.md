# W04 R21 cross-authority gate R1 — master verification

## Decision

`PASS`.

The master inspected and independently reproduced the frozen R21 correction,
all producer and review returns, the superseded failure evidence, the final
cross-authority test, the fresh independent review, and the bounded
phase-verifier correction required by the complete repository gate.

This report, its canonical machine record, and the fixed gate return were
materialized as one master-owned step only after the following preconditions
passed:

```text
fresh independent cross-authority review recommendation
PASS

fresh independent cross-authority review physical SHA-256
f266477e21be381f9acb014e9caa3669e9295dcc57422a8dbb5602fa413d28bb

final cross-authority test physical SHA-256
fffb71d4d382816f3572b575cbcd9e951309f92239ca540327cdb02304c4f9b0

final cross-authority test return physical SHA-256
9f45ccd44c9f27c53b72331609dd040fc1ca9211c630181117ad34f17ca5efb5

exact focused R21 suite
478 passed in 35.04s

governed product path scan
9/9 absent

git remote
no output
```

## Complete repository history

The R1 complete gate retained `REWORK` after 1,145 unaffected tests passed and
74 cases exposed an invalid environment assertion in the new contract test.
The R2 complete gate then passed 1,219 tests, including the corrected
`credential_separator_encoding` security authority fixture, but retained
`REWORK` when the generic phase verifier could not evaluate an in-progress
`READY` phase.

The bounded R3 verifier correction and fresh independent R2 review are
master-accepted:

```text
verifier
ad2c668c22ed2bc21b840c1fa2a8b842091a2cc9cc1bd731e7a62d2d7e276da5

verifier tests
825097186cea1ce65403f01b995895ce8856aa480675354259a1c0881ebb1253

independent verifier review R2
cda97099eb889d015391ac81265e8ab8db2753f377747d1a45261a1e8fc14d41

master verifier acceptance
reports/verification/W04/wyscout-phase-verifier-ready-R3-master-verification.md
```

That correction admits `READY` only as a verification-eligible state and keeps
every dependency, task, evidence, declared-check, checkpoint, clean-tree, and
zero-remote control. Empty delegated returns are exempt only for complete,
exact-task-ID-matched, master-assigned packets.

## R21-specific gate

The master confirms:

1. R21 physical bytes retain their immutable R20 binding.
2. The fresh R15 design review passes.
3. Both acyclic preimages and their independent review pass.
4. No self-hash, cycle, or concrete feature hash enters either preimage.
5. Field v2 decision, candidate, review, acceptance, and master verification
   pass.
6. Canonical action subevents accept strict integers only; string values remain
   unmapped or quarantined without coercion.
7. Possession v2 decision, candidate, review, acceptance, and master
   verification pass.
8. All 36 possession predicates and the canonical selector pass.
9. The exact 15-row feature authority contains only the four supported rows:
   `action_count`, `coordinate_known_action_count`, `match_count`, and
   `resolved_possession_action_count`.
10. v1 physical immutability and v2 semantic supersession pass.
11. The exact five-dependency lineage and v1/v2 anti-mixing rules pass.
12. The exact 30-resource order, cardinality, and digest pass.
13. The returned test, fixed independent review, and master gate remain serial
    and path-disjoint.
14. The complete CROSS_AUTHORITY positive and negative suite passes.
15. All nine governed product paths were absent before this materialization.
16. The retained bytecode path baseline is 1,152 files with sorted-path SHA-256
    `4531c4a0b91b83eef7ad2be164a5183d7448ee830a825376c8f2fdd430cf91c6`;
    150 cache directories retain sorted-path SHA-256
    `79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.
17. Prior master acceptance reports and retained evidence were read back; no
    unresolved R21 finding remains.
18. The machine record is closed canonical JSON, binds the complete fresh
    review bytes, and has exact decision `PASS`.

## Post-materialization complete repository gate

The master immediately reran the exact focused suite and complete `AGENTS.md`
repository suite after all three fixed gate paths and the truthful registry
records existed:

```text
focused R21 suite
PASS — 478 passed in 35.32s

uv sync --locked --all-groups
PASS — resolved 83 packages; audited 82 packages

uv run ruff format --check .
PASS — 367 files already formatted

uv run ruff check .
PASS

uv run mypy src/scouting scripts
PASS — no issues in 40 source files

uv run lint-imports
PASS — 28 files, 41 dependencies, 3 contracts kept, 0 broken

uv run pytest -q
PASS — 1245 passed, 1 known Starlette deprecation warning in 162.02s

uv run bandit -q -r scripts src
PASS

uv run python scripts/install_local_git_guards.py --check
PASS — executable guard; simulated exit 1

uv run python scripts/verify_local_only.py
PASS — 25 checks, zero failures

uv run python scripts/verify_phase.py --phase W04
PASS — READY; all tasks/evidence/checks accepted; zero remotes

git status --short
expected accepted W03/W04 checkpoint candidates only

git remote
PASS — no output
```

The retained bytecode inventory was byte-for-byte path-stable across the gate:
1,152 files at sorted-path SHA-256
`4531c4a0b91b83eef7ad2be164a5183d7448ee830a825376c8f2fdd430cf91c6`
and 150 cache directories at
`79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6`.

The stale `credential_separator_encoding` authority fixture passes inside the
1,245-test repository run. No cloud resource, hosted CI, public endpoint,
external deployment, container definition, Git remote, or product path was
created.

The R21 correction is accepted. Downstream implementation remains gated on the
immediate clean local checkpoint and its final empty-status/no-remote proof.
