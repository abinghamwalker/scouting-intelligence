# Subagent return

## Task

- task_id: `W04-BUILD-RECEIPT-CLOSURE-AUDIT-01`
- objective: Bind every R20 layer-summary semantic digest to one exact acyclic
  derivation from its complete guard-read `LayerManifest` value.

## Files changed

- `reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md`
- `reports/reviews/W04/returns/W04-BUILD-RECEIPT-CLOSURE-AUDIT-01-R4.md`

## Summary

- Preserved R3 by exact digest and corrected only its unbound layer-summary
  `semantic_sha256` plus the candidate user question.
- Defined the sole two-key, code-point-ordered preimage containing the complete
  parsed closed-schema `layer_manifest` object and exact semantic schema version;
  SHA-256 uses R20 canonical UTF-8 NFC JSON with no BOM or terminal LF.
- Required independent Bronze, Silver and Gold manifest guard-read, physical
  path/hash/size/canonical/schema/build checks and direct reproduction of each R20
  summary semantic value before any Gold population work.
- Reconciled Gold's Silver parent and Silver's Bronze parent path/physical identities
  exactly to the corresponding R20 summary rows; Bronze has no parent and no parent
  semantic field was invented.
- Required isolated, entry-copy, other-layer-copy, swap and downstream-wrapper-
  rehash substitutions to fail at the direct complete-manifest equality.
- Updated the exact candidate question while retaining every R2/R3 window, schema,
  aggregate, receipt, population, readback and 25-key rule.

## Tests run

- command: `shasum -a 256` over all six R4 fixed bindings
  - exit status: `0`
  - result: every R3/R20/R21/index byte reproduced exactly.
- command: complete `sed` reads of every packet `read_first` path
  - exit status: `0`
  - result: R3/review/return, R20/R21, all implemented contract lines and return
    template inspected; no Python, uv, Git or executable action used.
- command: bounded static audit of R20 summaries and implemented manifest/parent
  fields
  - exit status: `0`
  - result: exact five-key summaries, complete manifest fields, absent self-semantic
    field, and four-key parent identities reconciled to the R4 formula.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-build-receipt-closure-audit-R4.md`
- preserved R3 SHA-256:
  `0cf86df75af1276b3703083d3137de9ef345e2125a08a4e819617bbfd6100435`
- fixed R20 SHA-256:
  `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`

## Risks

- Fresh independent R4 review remains mandatory; this report neither materializes
  a digest nor authorizes implementation.
- The future complete accepted `LAYER_MANIFEST` schema must be used without field
  omission; a partial projection is forbidden.

## Follow-up items

- Dispatch a different fresh reviewer. Present the Section 7 question or dispatch
  authority implementation only after an independent `PASS`.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no delegation or self-approval: confirmed
- no implementation/test/data/authority/product/receipt/provider/network/cloud/
  container/CI/remote/endpoint/deployment action: confirmed
