# W08-BROWSER-OVERFLOW-04M-R1 return

## Task

- task/revision: `W08-BROWSER-OVERFLOW-04M-R1`
- invariant: the evidence boundary and immutable history wrap or scroll without hiding
  content; wide tables remain internally scrollable and controls remain keyboard
  operable.

## Inspection, root cause and bounded correction

I directly inspected the R2 browser packet/return, `base.html`, `brief.html`, the W08
stylesheet and the complete W08 Playwright witness. Master inspection correctly found
that the role-brief page's ordinary boundary/history paragraphs were not included in
the prior wrapping rule: only `.boundary`, `code`, and table cells used
`overflow-wrap:anywhere`. At 320px, a long fixed W06 limitation string in the role
brief body could therefore widen the document.

The bounded correction adds `p` and `dd` to the existing wrapping rule. It does not
set `overflow:hidden` on `body` or root, does not alter templates/content, and leaves
the table as `display:block; overflow:auto`, so immutable history remains reachable by
internal horizontal scrolling rather than being clipped or removed.

The first candidate also applied wrapping to `td`/`th`; the new regression showed that
this unnecessarily eliminated the history table's internal scroll range. I narrowed
the final rule to `code,dd,p`, preserving paragraph wrapping and table scrollability.

## Changed files

- `apps/web/static/w08/app.css`
- `tests/e2e/test_w08_local_workflow_playwright.py`
- `reports/reviews/W08/returns/W08-BROWSER-OVERFLOW-04M-R1.md`

## Regression evidence and checks

Added a real Chromium `320x700` witness that signs in with a fresh synthetic analyst,
creates/submits a brief, verifies the fixed `NO_GO: MISSING_EXPERT_RELEVANCE_EVIDENCE`
paragraph remains visible with `resemblance_only`, and measures:

- `document.body.scrollWidth <= window.innerWidth` at the 320px viewport (no body
  horizontal overflow);
- computed history-table `overflow-x: auto`;
- a positive internal `table.scrollLeft` after scrolling to `table.scrollWidth`, which
  proves the immutable history table's wide content is reachable inside the table
  rather than clipped or forcing body overflow.

Final focused commands all exited `0`:

```text
uv run ruff format --check tests/e2e/test_w08_local_workflow_playwright.py
# 1 file already formatted

uv run ruff check tests/e2e/test_w08_local_workflow_playwright.py
# All checks passed

uv run pytest -q tests/e2e/test_w08_local_workflow_playwright.py
# 5 passed in 21.16s
```

An initial focused pytest after the broader `td`/`th` wrapping attempt had one expected
new-regression failure because `scrollLeft` stayed zero; no accessibility assertion was
weakened. The narrowed CSS above corrected that exact condition before the final clean
run.

The existing parametrised witness still covers 1440x900, 390x844, and 320x700 keyboard
skip link/focus, landmarks, labels, table headings and body-width assertions. All
records/personas remain labelled as synthetic automation; this work supplies no
participant evidence and preserves the W06 `NO_GO` / `resemblance_only` /
`synthetic_development_only` / `LIMITED` / `no_recommendation_evidence` boundary.

## Residual risks and follow-up

The responsive regression establishes local presentation mechanics only. The prepared
moderated five-representative-user study remains required; no human result has been
created or inferred.

## Scope confirmation

- No Git command of any kind was run.
- No dependency or lockfile changed.
- No protected W06 output was accessed.
- No participant evidence was created or implied.
- No path outside this packet's allowed CSS, browser-test and return paths was edited.
