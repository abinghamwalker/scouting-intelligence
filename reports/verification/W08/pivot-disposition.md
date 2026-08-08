# W08 pivot disposition

- Decision date: 2026-08-05
- Decision: stop the W08 pilot and freeze the workflow as a dormant optional module
- Authority: direct user product decision, recorded in
  `docs/architecture/research-workbench-pivot.md`

## What happened

The pilot operator progressed through the synthetic local workflow and repeatedly reported
that the purpose, screen sequence and role switching were unclear. The visible experience
required administrative state changes and manual evidence recording but did not expose the
intended real-player ML research value. The pilot was stopped before it could be represented
as G-W08A, G-W08B or representative-user acceptance evidence.

## Evidence interpretation

The partial journey is retained as a product-direction finding:

- the workflow mechanics are not accepted as the primary product experience;
- no usability, expert relevance, recommendation or representative-user claim is made;
- no additional participant, T7 completion or W08 gate is required for W09 research work;
- existing W08 security, audit, concurrency, recovery and export evidence remains valid only
  for the code/build boundaries it actually tested.

## Code disposition

W08 authentication, workflow, audit and export code is preserved and remains covered by its
automated tests. It is removed from the core research journey and must not be reactivated as
a user-facing collaboration product without a separate decision after the real-data research
workbench has demonstrated useful value.

## Next path

W09 depends on accepted W07 plus the explicit research-workbench pivot. It begins by
materialising the full eligible historical player feature matrix and then connects a
transparent retrieval baseline to one coherent browser research workspace.
