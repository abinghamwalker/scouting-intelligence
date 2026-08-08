# W10 v2 participant-interface bounded return

- Date: 2026-08-07
- Bounded decision: **ACCEPTED FOR PILOT_READY ENGINEERING HANDOFF**
- Human evidence decision: **NOT MADE**
- W10: **REWORK**
- G-RW4: **INSUFFICIENT_EVIDENCE**

## Reviewed packets

### `W10-PARTICIPANT-LANGUAGE-UX-01`

The language/UX agent edited only
`docs/reviews/w10-participant-language-and-ux-spec.md`. It produced the 790-line content hierarchy,
translation table, dynamic-string audit, forbidden-language inventory and accessibility/mobile
acceptance checklist. It classified the initiating feedback as product-owner/operator usability
evidence, not eligible-reviewer evidence. It performed no Git operation.

### `W10-PARTICIPANT-UI-02`

The UI agent edited only the six assigned participant template, CSS and JavaScript paths. Its
final combined participant contract, boundary, web and real-browser run passed **25 tests in
17.46 seconds**. Jinja parsed all four current participant templates, Node accepted the
JavaScript, and the participant-source forbidden scan had no matches. It performed no Git
operation.

### `W10-PARTICIPANT-BOUNDARY-TESTS-03`

The independent test agent edited only the three assigned new test paths. Its **18-test** combined
run passed in **16.86 seconds**, including **two real-Chrome tests in 10.47 seconds**. Coverage
includes exact response/debrief digests, participant-keyed ordering, byte leakage, friendly and
legacy URLs, loopback-only behavior, plain validation, identical evidence structure,
applicable-only sections, desktop/mobile/keyboard use, five-task resume/review/correction/submit,
separate feedback, exact reconstruction, revisions, tamper detection and post-submit
immutability. It reported zero external requests, HTTP errors, console errors or page errors. All
database writes used pytest temporary paths. It performed no Git operation.

## Independent findings resolved

The independent packet identified the following before handoff, and the master/UI owner resolved
each without weakening a test:

1. missing shared “What this information cannot tell you” disclosure;
2. nonnumeric experience errors not naming the field or marking it invalid;
3. an invalid Chromium `/v` pattern character class;
4. favicon 404 followed by a blocked data-URI favicon;
5. feedback digest construction omitting its schema version;
6. a missing midfielder-subrubric import; and
7. stopped legacy templates/assets sharing the reworked participant files.

The final focused reruns are green. The stopped interface now uses separate retained legacy
templates/assets, while production uses only the friendly participant route and neutral assets.

## Acceptance boundary

This return accepts the bounded engineering rework and independent browser/storage verification
only. It does not accept a mechanics-pilot human result, 08D GO, 08E, 08F, formal collection,
G-RW4 or W10. No agent started a human session or wrote the new production database.

The only next action is to run the new isolated mechanics pilot with at least two fresh eligible
football-domain reviewers.
