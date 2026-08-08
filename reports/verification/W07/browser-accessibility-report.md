# W07 master browser and accessibility review

Date: 2026-08-04
Status: **PASS**

## Runtime and scope

The master ran the real FastAPI application on `127.0.0.1:8765` and inspected the
server-rendered W07 overview, search, player, retrieval, comparison, evidence-centre
and explicit-state pages. The application server was stopped after review. Browser
traffic contained only loopback document and local stylesheet requests; no external
request, webfont, script, image, provider or public endpoint was used.

## Journey and responsive evidence

- Overview → candidate search → Synthetic candidate 01 → role-aware retrieval took
  exactly three activations.
- The evidence centre and explicit NO_GO state were directly reachable from primary
  navigation.
- Desktop `1440×900` and mobile `390×844` master inspections had one `h1`, header,
  labelled primary navigation, main and footer landmarks and no body horizontal
  overflow.
- Genuine Python Playwright coverage also passed at `320×700`, with scroll-contained
  evidence tables rather than body overflow.
- Search exposed exactly 18 stable synthetic candidate labels, a labelled searchbox,
  a closed position selector and an accessible captioned evidence table.
- Retrieval and comparison exposed returned rows, reasons, limitations, confidence,
  applicability, feature contributions, dimension evidence and the exact W04 bridge
  with minutes/rates/per-90 marked `SUPPRESSED`.

## Keyboard, focus and semantics

The Python Playwright journey proved the first Tab exposes the skip link, Enter moves
focus to `main`, keyboard-only navigation reaches retrieval, and focused controls have
a visible non-zero outline. It also asserted a single `h1`, semantic landmarks,
labels, headings, captions, scoped table headers and labelled digest disclosures.
The master inspected the corresponding DOM and presentation surfaces. Loading, empty,
unavailable, error and NO-GO use distinct headings, messages, state classes and border
signals; unknown state names return 404.

## Visual hierarchy, contrast and console

The prominent red NO_GO banner precedes every page's primary content and cannot read
as a positive validation. The desktop and mobile layouts preserve readable hierarchy,
wrapping and spacing. Sampled browser-computed contrast ratios were:

| Surface | Contrast ratio |
|---|---:|
| Body text | 16.27:1 |
| Primary navigation | 14.42:1 |
| NO_GO banner | 14.90:1 |
| Primary action | 11.17:1 |

No browser console warning or error was present. The only observed 404 was the
browser's optional favicon request; it had no content, navigation, security or
accessibility effect.

## Executable evidence

- `tests/e2e/test_w07_local_evidence_playwright.py`
- `tests/integration/test_w07_local_evidence_app.py`
- Master/independent focused parity set: 17 passed.
- Final post-authority-restoration W03/W07 regression set: 73 passed with one existing
  Starlette TestClient deprecation warning.
