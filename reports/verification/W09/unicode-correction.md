# W09 provider Unicode correction

- Date: `2026-08-05`
- Decision: **PASS — corrected text-bearing authority**
- Scope: retained provider player/team text only
- Claim boundary: unchanged historical-resemblance engineering; no G-RW4 evidence

## Defect and correction

The retained Wyscout catalogue stores some names with a literal JSON-style Unicode escape layer,
for example `\\u0130. G\\u00fcndo\\u011fan`. Standard JSON parsing correctly preserved those bytes
as text, but the canonical projection copied them without the additional provider-specific decode.
The browser therefore displayed the escape notation literally. This was an ingestion defect, not a
font, browser, CSS or ML defect.

The canonical text boundary now:

1. preserves already-correct Unicode;
2. decodes exactly one valid `\\uXXXX` layer, including valid surrogate pairs;
3. normalises the resulting text to Unicode NFC; and
4. fails before artifact writes on malformed or nested escapes and on escaped or already-decoded
   unpaired surrogate code points.

The retained source audit found escaped text in 722 player short names, 531 first names, 828 last
names and 45 team name/official-name/city fields. The corrected 3,603-player canonical catalogue
contains zero literal Unicode escapes. Examples include `İ. Gündoğan`, `Ł. Fabiański` and
`Ó. Duarte`.

## Corrected authority

- Canonical build: `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`
- Canonical manifest SHA-256: `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`
- Matrix: `w09-historical-player-window-v1-a31511705ac15a5d`
- Matrix digest: `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1`
- Matrix manifest digest: `dda2588f7ad81443aac614a359fbda1fcb60e533ca0d56db5d59e4669a754692`
- Index ID: `d362d87e-4d02-56a1-a5c8-446f5eaa72a3`
- Index manifest digest: `30c2b6c1e0d65c8214860131f690b8b6cac05fe317ffa208a2785e11160eb0bc`
- Evaluation suite digest: `1c922dafed2d7bdd773ad104ae2700330f0262da80a1e2e67327c5bcb6e8adc1`
- Evaluation result digest: `835e31f1eb2ba0e7dc0456c3dca9a5918fb82c278567f00247aa26bf8a5da9c0`

The superseded generated authority was moved intact to the recoverable local backup
`/private/tmp/w09-unicode-correction-backup.XJ5WtD`. The intermediate Unicode rebuild that
predated final surrogate hardening is preserved beneath its `surrogate-hardening-pre-rebuild`
directory. Neither backup is an accepted discovery root.

## No ranking change

The rebuilt matrix retains 1,975 rows for 1,965 players. An old/new Parquet comparison found all
23 stable fields identical. Exactly 398 eligible display names and 181 team-name lists changed;
only the bound matrix/canonical/lineage authority fields changed alongside them. Minutes,
eligibility, identities, competitions, positions, feature values, missingness and coverage did
not change.

The old and corrected `index-vectors.npy`, `scaler-center.npy` and `scaler-scale.npy` files are
byte-identical. Frozen evaluation player IDs, candidate ordering, ranks and scores are identical;
only text-bearing and content-addressed authority identities changed.

## Verification

- Focused canonical/feature/index/evaluation integration: 60 passed.
- Unicode fixtures cover preserved decoded text, one-layer decoding, NFC composition, valid
  surrogate pairs, malformed escapes, nested escapes, escaped unpaired surrogates and actual high
  and low surrogate code points.
- The feature fixture proves `İ. Gündoğan` survives canonical construction, feature catalogue
  loading and matrix loading.
- Live production browser search for `Gündoğan`: one result, `İ. Gündoğan`; visible literal escape
  count: zero.
- Complete W09 contracts, feature, index, serving, API, web, browser and evaluation gate:
  126 passed. Its browser fixture clock now remains safely after the browser-generated request
  instant instead of expiring at a fixed time on the verification date.
- Complete repository suite: 2,980 passed and four W04 frozen-runtime witnesses initially failed
  only because later-wave ignored PYC files existed in the repository census. Those generated
  cache files were moved recoverably to
  `/private/tmp/w09-unicode-pyc-quarantine.zkISGn`; the exact four witnesses then passed 4/4 in
  85.80 seconds with bytecode writes disabled. The evidence therefore covers all 2,984 collected
  tests with zero logical failures.
- Ruff format/lint, mypy, import boundaries, Bandit, Git guard and 25 local-only checks: PASS.
- Complete repository and phase-gate results are recorded in `verification-report.md`.

## Residual boundary

This correction improves text fidelity only. It does not add current licensed data, improve the
feature model, validate football relevance or make the rankings recruitment recommendations.
G-RW4 remains not performed.
