# W08 browser and accessibility report

Status: **AUTOMATED AND MASTER BROWSER REVIEW PASS; HUMAN STUDY PENDING**

## Automated Chromium evidence

The retained Python Playwright suite uses the installed local Chrome binary and a
fresh `127.0.0.1` W08 runtime. Five tests cover:

- brief create/submit/approve and exact replayable retrieval linkage;
- shortlist entry, scout assignment, structured disagreement and amendment;
- stale optimistic-concurrency denial and reload/retry;
- hold, controlled rejection, owned next action and reconsideration;
- invalid export denial, successful retry, read, revoke and audit receipt;
- expiry/re-authentication and logout denial;
- captured requests restricted to `127.0.0.1`;
- skip link, visible focus, labels, landmarks, headings and scoped table headers;
- 1440x900, 390x844 and 320x700 responsive layouts.

The original browser producer's R1 evidence is retained but was not accepted because
it ran one prohibited read-only Git query. Fresh R2 directly inspected and adopted the
implementation with no Git command; master reproduction passed 13 combined browser,
integration and web-security tests. A subsequent master in-app-browser inspection
found a 5-pixel 320px brief-history overflow caused by an unwrapped limitation
paragraph. The bounded 04M correction added text wrapping without root clipping and
retained the wide history table as an internal scroll container; master reproduction
passed all 5 browser tests.

## Master in-app browser measurements

On the corrected 320x700 brief-history page:

- `window.innerWidth`: 320
- `document.body.scrollWidth`: 320
- both main paragraphs: `clientWidth=299`, `scrollWidth=299`,
  `overflow-wrap:anywhere`
- immutable-history table: `clientWidth=299`, `scrollWidth=1432`,
  `overflow-x:auto`
- one each of header, primary navigation, main, footer and H1
- W06 `NO_GO` and `MISSING_EXPERT_RELEVANCE_EVIDENCE` were prominent and unchanged

The post-stop temporary-browser mechanical receipt was:

- database SHA-256:
  `a208b51b07ae7a1768bbd402368806255455c92c6d428a2350f0b6e246637251`
- empty export-manifest SHA-256:
  `5446897477634347b30b8a2357fe5306f398dbd42bca89ce4971d2a90164140e`
- status: `mechanical_receipt_only`

Fresh independent R4 review reran all five Chromium journeys within its 72-test
focused surface and returned PASS with no accessibility finding. No presentation or
CSS path changed after the master 320-pixel correction and recheck.

No screenshot, automated persona or browser result is participant evidence.
