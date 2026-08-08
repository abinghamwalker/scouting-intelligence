# W04 Wyscout schema design R5 — master verification

## Decision

`REWORK`. The master read the full 1,220-line producer design and return, read the
full independent R4 review and return, reran both packet suites, and independently
reproduced all seven P1 findings. No R5 implementation packet is authorised.

## Scope and integrity

- Producer design:
  `reports/reviews/W04/wyscout-schema-design-R5.md`
  (`69,415` bytes; SHA-256
  `6a22b742e6e84124a4cef3dd0c3b8c2c2e2bef16cfc5759d34cc4905ad5bb37f`).
- Independent review:
  `reports/reviews/W04/wyscout-schema-design-independent-review-R4.md`
  (`26,393` bytes; final SHA-256
  `a96c945b416c486f3635c9fa6d9742a9c1ff7f06303a4668e0594b873c3bcede`).
- Both producer and reviewer changed only their two assigned report paths and
  confirmed no Git, dependency, network, provider or delegated action.
- Master base: `8eab3d5488735379817800be4b463f046f5d6e69`.

## Independently reproduced defects

1. R5 writes identity runtime state under undeclared and unignored
   `data/identity/...`; the approved roots are only `data/source`,
   `data/reference`, `data/working`, `data/manifests`, `reports`, and `runs`.
2. R5 requires original selected wheel ZIP bytes in the uv cache, but read-only
   searches found no named Pydantic, PyArrow, Polars, Packaging, or PyYAML wheel
   archives. The cache contains symlinks to extracted `archive-v0` trees plus small
   metadata sidecars, so the original archive-byte hash cannot truthfully be
   reproduced.
3. The supported-feature registry controls Gold behavior and build identity but has
   no independent semantic review/master acceptance lifecycle or strict-before
   `feature_schema` dependency.
4. The required crosswalk row uses the existing match-method enum for all states,
   but the enum has only `exact`, `deterministic`, and `reviewed`; R5 leaves
   review-required, provider-rejected, and reviewed-reject methods undefined.
5. R5 gives no exact physical paths for the Bronze payload, Silver products, Gold
   partitions, quarantine/rejected fields, or temporal receipts, while granting the
   rebuild a broad shared working subtree.
6. R5 updates the registry before its checkpoint, while the controlling workflow
   requires the full gate, acceptance commit/tag, then registry and clean-tree
   proof.
7. R5 requires every normalized correction to bind a queue item, but a previously
   resolved mapping has no queue item and therefore cannot use the claimed direct
   correction/supersession lifecycle.

## Master checks

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- Producer size assertion: PASS; `69,415` bytes.
- Independent-review size assertion: PASS; at least `26,393` bytes.
- `uv run python scripts/verify_local_only.py`: PASS; 25 checks, zero failures.
- Orchestration YAML parse and phase-registry task-ID uniqueness: PASS.
- Read-only uv-cache wheel search: PASS as evidence; required archives absent.
- `git diff --check`: PASS.
- `git remote`: PASS; no output.

## Rework boundary

`W04-SCHEMA-DESIGN-01-R6` owns only a replacement standalone design and mandatory
return. It may not edit code, tests, configuration, dependencies, data, Git state,
or the approved local-only boundary. A fresh independent review remains mandatory
before any W04 implementation packet is dispatched.
