# W09 browser research-workbench journey

## Decision

`W09-RESEARCH-UI-05` is accepted. The local browser provides one coherent journey from governed
dataset authority through a real-player query, ranked explanations, exact comparison and a saved,
replayable report. It does not expose W08 as the core journey and does not require role switching,
terminal commands, manual workflow administration or manual audit entry.

## Production authority shown

- Source universe: 1,826 matches, 3,071,395 actions, 142 teams and 3,603 players.
- Eligible matrix: 1,975 player-window rows and 1,965 unique players.
- Matrix version: `w09-historical-player-window-v1-a31511705ac15a5d`.
- Index version: `w09-historical-player-index-v1`.
- Window: 2017-07-01 through 2018-07-01; cutoff 2026-08-05T00:00:00Z.
- Browser and API displayed the same exact dataset and version pins.

## Corrective Unicode browser witness

After rebuilding the text-bearing authorities, the master loaded the production composition at
`http://127.0.0.1:8769/`, searched for `Gündoğan`, and received exactly one eligible row named
`İ. Gündoğan`. The visible DOM contained zero literal `\\uXXXX` sequences. Initial catalogue
cards also rendered names such as `A. Aréola`, `A. Balić`, `A. Barák` and `A. Begović` as Unicode
characters. The screenshot and DOM check were taken from the corrected production authority.

The retained save/replay witness below records the original accepted W09 checkpoint. Its old
content-addressed pins remain historical provenance; the corrected runtime intentionally treats
them as superseded rather than silently replaying them against a different authority.

## Retained-data browser witness

The master started the production composition root on loopback and used the in-app browser against
`http://127.0.0.1:8769/`:

1. The dataset section loaded one verified local authority and reconciled source and eligible
   counts without equating them.
2. Player search for `S. Sirigu` returned exactly one eligible retained row: goalkeeper, Italian
   first division, 3,477.7 conservative-lower-bound minutes.
3. The real row was selected as an exemplar and a robust-scaled weighted Euclidean query was run
   with all 16 transparent features.
4. The service reconciled 1,975 matrix rows, 409 Italian rows, one exemplar self-exclusion, 408
   admitted/scored rows, zero missing-feature exclusions and ten returned rows.
5. The top result was M. Perin at distance `0.5526646247372221`; every returned player exposed 16
   feature contributions, raw values, scaled contrasts, missingness and limitations.
6. M. Perin and T. Strakosha were selected and compared from exact matrix evidence, including
   minutes, evidence state, coverage, matches, actions and all feature values.
7. The browser saved `W09 retained-data acceptance journey` as experiment
   `66372ff5-d444-4813-a260-76d4df2dda63` with experiment digest
   `d45f9d77487ff22367ad878d6acd8994f7b315226228ad2d90d3b89ae5c673f0`.
8. The content-addressed canonical JSON report has digest
   `2220c20c7c3c84632fcca60af3e85db4025a5e3137aa6ba25dc6248789caccc2`, result digest
   `f3c64b0a1d50fff9b9ba3a2bf611717191aa225e3743f18102002a16905e903d` and comparison digest
   `a3af1fb10b1cb1f65718e9c099750901c98c7437c991d4a07beed3f8ee09f8d9`.
9. Replay reproduced the exact saved query, pins, result identity and digest. Receipt
   `6c468c82-f5c3-5b29-ae7f-b14ab3f44817` has digest
   `495165366a4c9e76e7a293e607d7f1ea99c6f23d5da03bbcf3fa26705a9f771a`.

The report bytes were independently read back through the same loopback API. They contain ten
ranked real-player rows, the two comparison rows, exact version pins, CC BY 4.0 attribution,
rights limitations and the `historical_resemblance_research_only` boundary.

## Browser and implementation checks

- The production browser showed a responsive, keyboard-oriented page with sticky section
  navigation, readable authority metrics, explicit warning cards and a clear successful replay
  state.
- Browser traffic remained same-origin and loopback-only. Production server logs recorded only
  the page/static loads and W09 dataset, player, query, comparison, experiment, replay and report
  endpoints. No external provider or network service was used.
- Browser fixture tests additionally cover both query modes, both methods, JSON and HTML reports,
  scientific-notation canonical digests, narrow-screen layout, keyboard landmarks and distinct
  empty, validation, stale/conflict and unavailable states.
- The master reran Ruff format/lint, mypy, Bandit and the UI unit/e2e set: `9 passed`, with only the
  existing Starlette TestClient/httpx deprecation warning.
- Missing, ambiguous or incompatible feature/index authorities render an honest unavailable page;
  no synthetic, stale, newest-found, W07 or W08 population is substituted.

## Claim boundary

The page and report say that results are historical resemblance within this governed population.
They do not claim future performance, football relevance, recruitment usefulness, value,
availability, fit or outcomes. `G-RW4` expert validation remains absent.
