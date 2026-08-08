# W04 R21 complete repository gate R1 — failure evidence

## Decision

`REWORK`.

The master ran the complete repository suite in the exact `AGENTS.md` order.
Environment sync, formatting, lint, strict typing, and import architecture
passed. The complete pytest command then failed:

```text
uv run pytest -q
1145 passed, 1 warning, 74 errors in 156.51s
```

Every error had the same root cause:

```text
tests/contracts/test_w04_r21_cross_authority_composability.py:158
assert sys.dont_write_bytecode
E assert False
```

The focused producer/reviewer commands set `PYTHONDONTWRITEBYTECODE=1`, but the
frozen complete repository command is exactly `uv run pytest -q`. A contract
test cannot require an environment option absent from the mandatory master
gate. The 1,145 unaffected tests passed, including the corrected
`credential_separator_encoding` security authority fixture.

The exact repository run naturally materialized the new test's normal pytest
bytecode cache. No bytecode was deleted or rewritten:

```text
*.pyc: 1151
sorted-path SHA-256:
d9c0a14033a78398072b597944de104470cb69aa3df97ee47ecdde3f182d9a48

__pycache__: 150
sorted-path SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6

new retained path:
tests/contracts/__pycache__/
  test_w04_r21_cross_authority_composability.cpython-312-pytest-9.1.1.pyc
```

The independent PASS review at physical SHA-256
`30cd68f120088f4673736976d54a896cf32aa954934dd62177d354c15113add4`
is preserved byte-for-byte at:

```text
reports/reviews/W04/archive/
  wyscout-r21-cross-authority-composability-independent-review-R1-
  superseded-full-gate-30cd68f1.md
```

It is superseded because it did not reproduce the mandatory unsuppressed
repository command. The fixed review path is vacant for a fresh review after
bounded correction. No master PASS gate or product path was created.
