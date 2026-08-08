# Subagent return

## Task

- task_id: `W09-DATA-INVENTORY-01`
- objective: Independently inventory and reconcile every retained Wyscout v5 source,
  identity, Bronze, Silver and Gold artifact while distinguishing the full source
  universe from the accepted W04 proof slice.

## Files changed

- `reports/verification/W09/data-inventory-and-coverage.md`
- `reports/reviews/W09/returns/W09-DATA-INVENTORY-01-R1.md`

## Summary

- Produced a retained-evidence report with byte sizes, checksums, schemas, clocks,
  rights, admitted/excluded scope, source and identity populations, all seven canonical
  products, layer lineage and concrete missing W09 products.
- Reconciled the five admitted partitions to 1,826 matches and 3,071,395 actions and the
  retained catalogues to 142 teams and 3,603 players.
- Streamed the full admitted JSON to distinguish 2,568 event-referenced non-zero players,
  3,011 lineup-referenced non-zero IDs (2,996 catalogued plus 15 absent-master), 3,603
  identity-resolved catalogue players and an explicitly unset future eligible count.
- Verified the population-capable identity bundle has 5,594 current rows: 5,578
  deterministic resolutions, 15 review-required absent-master players and one rejected
  zero actor, with zero duplicate source identities or resolved canonical IDs.
- Verified that retained W04 canonical products are a one-match/one-player-window proof,
  not the full historical population, and recorded the exact reconciliation questions
  for the full feature-matrix builder.

## Tests run

- command: `uv run python -c "import json; from pathlib import Path; p=Path('data/source/wyscout/v5/completion-manifest.json'); d=json.loads(p.read_text()); assert sum(x['row_count'] for x in json.loads(Path('data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json').read_text())['files'] if x['object_path'].startswith('archive-members/matches_')) == 1826; assert sum(x['row_count'] for x in json.loads(Path('data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json').read_text())['files'] if x['object_path'].startswith('archive-members/events_')) == 3071395; assert d['state'] == 'complete'"`
  - exit status: 0
  - result: PASS; retained source manifest sums and completion state reconcile exactly.
- command: `test -s reports/verification/W09/data-inventory-and-coverage.md`
  - exit status: 0
  - result: PASS; retained evidence report exists and is non-empty.
- command: `test -s reports/reviews/W09/returns/W09-DATA-INVENTORY-01-R1.md`
  - exit status: 0
  - result: PASS; mandatory return exists and is non-empty.

## Artifacts/evidence

- `reports/verification/W09/data-inventory-and-coverage.md`
- source snapshot manifest ID `4e16bdb5-afe7-5601-88ad-adc124cfce3b`, SHA-256
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
- source completion index SHA-256
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- identity bundle SHA-256
  `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`
- identity review queue SHA-256
  `e868d4376f18e7e191c8735ab17814c277f2d0ef1b29dd735c01eb84319e0b51`
- canonical build ID
  `b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`

## Risks

- The future eligible count is intentionally unset: 3,603 catalogue identities cannot
  be equated with players having defensible minutes, coverage and feature availability.
- Fifteen non-zero absent-master player IDs remain open and `player:0` remains rejected;
  they must fail closed in population building and retrieval.
- Exact minutes and per-90 are unsupported by W04 because terminal evidence can be
  censored; W09 must adopt and evidence explicit exposure/minimum-minutes semantics.
- The retained canonical chain covers one English match and one Gold player window only.
  It cannot support a population or retrieval-quality claim.
- Source data is historical 2017/18 male senior top-five-league evidence and does not
  support current-market, expert-relevance or recruitment-usefulness claims.

## Follow-up items

- `W09-FULL-FEATURE-MATRIX-02` must build the missing full canonical population and close
  each reconciliation question in
  `reports/verification/W09/data-inventory-and-coverage.md` before G-RW1 can pass.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; neither `pyproject.toml` nor
  `uv.lock` was changed and no dependency was installed.
- no edits outside `allowed_paths`: confirmed; only the two listed deliverable files were
  created (their required parent directories were created to hold them).
