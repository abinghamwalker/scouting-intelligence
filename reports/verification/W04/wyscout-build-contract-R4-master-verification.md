# W04 Wyscout build contract R4 master verification

Date: 2026-08-01

Verdict: **PASS — bounded Packet-1 contract and fail-closed composition only**

The master inspected the complete R4 implementation and test changes, reproduced
every frozen hash, reviewed the retained failed evidence, and independently reran
the producer and fresh-review checks. R4 does not provide executable receipt
completion. It preserves the build/window/projection/invocation/receipt/result
contracts while making completion unavailable until the planned accepted 23-root
schema and aggregate authorities exist.

## Accepted frozen bytes

- R4 packet: `d55ed40ea24d8fff680a2fa4eadefbb5bfa32394b8fc562b2ca1bb7b45fc01ee`
- `src/scouting/contracts/wyscout_build.py`:
  `f4433ebeaadee2f1d17f7f5f286f6eee21656c7408338e972270b9237ee8bce6`
- `tests/contracts/test_w04_wyscout_build_contract.py`:
  `c6a50ffc7963c15ace11d68d78a9a5abd0e80953e52696a765ac2a4e259da229`
- producer return:
  `4e4bf858fec11d3cff40052f579164ddeae426f9ad70cc69852f1eb73f9b5db1`
- fresh independent review:
  `f1d0c36d1414dab72ff3ab3e213f8086d9a0700b030e76946622b45a0cdccc86`
- fresh reviewer return:
  `f4c6b9fd136ecad505930513f7dde9c01f95e9571f97c34fa32103e84de25435`

The retained R3 conformance review remains failed evidence at
`82cc1b09111b9236d51578a25ab525f81c2dd79cdd9014ff042b222b06d26592`.

## Independent verification

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- Ruff format and lint on the bounded files: PASS.
- mypy on the bounded files: PASS.
- focused five-path matrix: PASS, `268 passed`.
- complete Wyscout data-contract suite: PASS, `233 passed in 107.26s`.
- post-review focused replay: PASS, `268 passed in 6.60s`.
- local-only verifier before and after review: PASS, `25/25`.
- `git remote`: empty.

The master confirmed by inspection that `validate_receipt_closure` has no return
node and unconditionally raises `GoldSchemaAuthorityUnavailableError` after all
retained validations. Baseline, nullability, top-level order and nested integer-
width compositions cannot complete. Malformed manifest, Gold, boundary, parent,
population and clock inputs still fail earlier. No caller schema authority,
callback, Boolean, descriptor, digest, new root, projection field, dependency or
product write was added.

Receipt completion and product publication remain blocked pending the exact
23-root implemented-schema review, master v2 aggregate materialization/review, and
the later bounded content-bound composition.
