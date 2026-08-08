# W04 content-addressed evidence byte preservation R1

Date: 2026-08-03
Status: PASS

## Purpose

The terminal checkpoint stages historical W04 review evidence that is already bound
by physical SHA-256 values in accepted authorities. Six Markdown documents use two
trailing spaces as intentional hard-break bytes, and five documents retain one
accepted terminal blank line. Rewriting those bytes would invalidate accepted
authority bindings and require an unnecessary product-authority cascade.

The repository `.gitattributes` file therefore changes only Git's whitespace-error
classification for the exact eleven paths below. It does not rewrite a byte, affect
runtime behavior, change product inputs or outputs, weaken a validation, or exempt
any other path from the staged whitespace check.

## Preserved accepted bytes

| Path | Accepted SHA-256 | Git classification |
|---|---|---|
| `reports/reviews/W04/archive/wyscout-season-lineup-product-binding-independent-review-R1-rework-431e0cfb.md` | `431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba` | intentional Markdown hard breaks |
| `reports/reviews/W04/authorities/wyscout-build-product-independent-review-R1.md` | `f780a1e4e6043562e9aa342559350eabbaeef3915c64280b096a08d160e522e9` | intentional Markdown hard breaks |
| `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-independent-review-R1.md` | `3f88335db70609e90f0d02cbbc206752479f5300e196329fc48f07154899cf0f` | intentional Markdown hard breaks |
| `reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R2.md` | `b67e4f95e97567b60d93bab58e94bad877931b2259f219709b199d7325634658` | intentional Markdown hard breaks |
| `reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R3.md` | `658cfeb2d504b4124467861391acfdc25643d0c5a1faf2afbf538eeb7c652074` | intentional Markdown hard breaks |
| `reports/reviews/W04/wyscout-build-receipt-closure-audit-independent-review-R4.md` | `288c58c29bbd572b8fe9bf5df9875d5a6b9c24cfca44923b8780e2dcb7bd7827` | intentional Markdown hard breaks |
| `reports/reviews/W04/returns/W04-WYSCOUT-SCHEMA-CLOSURE-R5-ACCEPTANCE-ORACLE-01-R1.md` | `b09297fb45eb7a16f431959f7e7840b8ae930902928094079fd7e26b1ba79116` | accepted terminal blank line |
| `reports/reviews/W04/returns/W04-WYSCOUT-SCHEMA-COMPOSITION-BOUNDARY-AUDIT-01-R1.md` | `df20a183a608b0b9ac84d5791298f473de4e7d15405fb98401a9a7ffd5662623` | accepted terminal blank line |
| `reports/reviews/W04/wyscout-schema-composition-boundary-audit-R1.md` | `e1d3597b5331705d030a25be7ffc7fd390a5c0fe4b7c84000a25ec744b30517b` | accepted terminal blank line |
| `reports/verification/W04/wyscout-data-contracts-R3-master-verification.md` | `8fe10146e921c27deb54edfadcc55920f94e6550dde148bb5e9a73e8728dd161` | accepted terminal blank line |
| `reports/verification/W04/wyscout-data-contracts-R4-master-verification.md` | `cd6243bc96081281230a4c8b60161ad5d191904a6b19f57ffc84b24ee524a95f` | accepted terminal blank line |

## Verification

- Every worktree hash above equals its accepted physical binding: PASS.
- The attributes are exact-path rules and do not use a wildcard: PASS.
- Global `git diff --cached --check` after staging the complete integration tree:
  PASS.
- Runtime, schema, product, source, rights, temporal, and local-only behavior is
  unchanged: PASS.

This is checkpoint evidence-byte preservation, not a new runtime-control revision or
product authority.
