# W09 retained full-feature-matrix verification

Verified locally on 2026-08-05 against the one accepted W09 canonical manifest. This is
engineering evidence for historical resemblance research only; it is not football-relevance,
recruitment-usefulness, current-market, outcome, value, availability, or expert-validation
evidence.

## Accepted authorities

- Canonical build ID: `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`
- Canonical manifest SHA-256: `587f696996304c3aea888f12a486afa89e458c7cc68a2fafd5e85d38e004be59`
- Feature matrix version: `w09-historical-player-window-v1-a31511705ac15a5d`
- Feature matrix manifest SHA-256: `d1eeb2948a64d277f14043d3d8d5a3468596e7e4c04aa8bf2096ee55d37a91ef`
- Feature matrix manifest semantic digest: `dda2588f7ad81443aac614a359fbda1fcb60e533ca0d56db5d59e4669a754692`
- Matrix semantic digest: `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1`
- Identity bundle digest: `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80`
- Feature registry digest: `bafccabfb64c347b72f5c9766b129baeac20784c0a577143552cf7259925623b`
- Eligibility policy digest: `e00fe7b2b9285980b52e10438064ce84c6810a613a50acb0809194e46f1199dd`
- Feature code digest: `e7798c77d461ea1ca79a502f2eb43eecc110c1f23f1ac7333b3a01a1e0a19373`
- Rights classification: `wyscout_figshare_v5_cc_by_4`; retained local-only, attribution
  required, raw export not authorised.
- Window: `[2017-07-01T00:00:00Z, 2018-07-01T00:00:00Z)`; feature cutoff:
  `2026-08-05T00:00:00Z`. Source and identity authorities are strictly earlier.

The producer rediscovered exactly one accepted canonical manifest, verified the physical
SHA-256, size, row count, schema/build version and temporal authorities of every declared
canonical file, and streamed all 3,071,395 action rows. The index loader then independently
re-read and revalidated every feature artifact physically and semantically.

## Population reconciliation

| Population boundary | Count |
|---|---:|
| Recorded source/catalogue players | 3,603 |
| Population decisions | 3,603 |
| Players referred by governed lineup evidence | 2,996 |
| Catalogue players with no lineup evidence | 607 |
| Player/competition/season eligibility grains | 3,059 |
| Eligible rows at the 450-minute policy | 1,975 |
| Unique eligible players | 1,965 |
| Below 450 governed minutes | 645 |
| Unusable-minute grains | 439 |
| Invalid-membership exclusions | 0 |
| Required-feature-missing exclusions | 0 |
| Temporal-cutoff exclusions | 0 |
| Resolved actor actions assigned to eligibility grains | 2,845,357 |
| Rejected zero-actor/player-0 actions | 226,038 |
| Total source actions reconciled | 3,071,395 |

The 3,603 source-player figure is therefore not an eligible-candidate count. Ten eligible
rows are additional competition/season grains for players who also have another eligible
grain. The retained eligible rows cover the five domestic competitions: England 389,
France 402, Germany 352, Italy 409, and Spain 423. The two other source competitions have no
row passing this fixed eligibility/window policy.

All 29 exact-minute eligibility grains fall below 450 minutes. All 1,975 eligible rows use
conservative-lower-bound exposure; their governed-minute total is 3,639,135.980197216, with
row range 450.6480585333333 to 3,611.7359195833333. This is a material limitation: a lower
bound denominator can overstate the corresponding per-90 rate.

Eligible rows contain 2,767,825 resolved actions. Valid-coordinate coverage is
2,767,823/2,767,825 and action-match coverage is 47,731/47,815. The feature predicates are
coordinate-independent, so the two retained invalid-coordinate actions remain in applicable
event counts while coverage records their coordinate limitation.

## Grain, eligibility, and features

The explainable grain is canonical player UUID by competition by season inside the fixed
2017/18 window. Membership comes only from canonical appearance evidence; neither catalogue
`currentTeamId` nor action presence supplies membership or minutes. A player is eligible at
450 governed usable minutes. Exact exposure is retained only if every played stint is exact;
otherwise the sum is a conservative lower bound. All-unusable/unused-bench grains remain
in the eligibility ledger but are not matrix rows.

The fixed ordered feature set is: passes, accurate passes, crosses, smart passes, shots,
shots on target, goals excluding own goals, key passes, assists, duels, duels won,
interceptions, clearances, accelerations, fouls, and touches. Every value is the exact
retained event count multiplied by 90 and divided by governed minutes. A zero count is an
observed zero, never silently imputed missingness.

## Physical artifacts

| Role | Rows | Format | Bytes | SHA-256 | Semantic digest |
|---|---:|---|---:|---|---|
| `player_catalogue` | 3,603 | canonical JSONL | 650,373 | `818e1d583c82e7defd86d43599c175f90b658d11928b8bb5810f56d585d2f18b` | `870b35da51ceca48ffbc6d350e2b4bcd7b35a6bd692495a6d56c0c2e0b6079d6` |
| `population_decisions` | 3,603 | canonical JSONL | 998,397 | `2999bf0130e1f7dec5ebad4fc9bc3ea061977dff19e5a8d51d759fb52445b986` | `c1b2a47ef6838737a08cb962319fcd140a8cec71cf19b8466b4fc76a41b1849a` |
| `eligibility_decisions` | 3,059 | canonical JSONL | 2,278,896 | `1d61e2bab2257efd720fc42584c9fb1762a5ea9f5ed907ee50f91e01cd74142f` | `fe450c4e74c896be3b47975011ff7f80cd08314b38a8c1e10333d9d032eb3e9e` |
| `feature_matrix_rows` | 1,975 | fixed-schema Parquet | 621,748 | `ca361a02401c898bc69bd52737edaf84ec237927b21b6ce7aa3193bbeeac623a` | `428d25ed4f1fd5dec7df74f30905db875cd548270fc2824b431e1bc8a6447cc1` |

The three governance ledgers are canonical and newline-terminated. The analytical matrix
uses a fixed Arrow schema, fixed column order, Parquet 2.6, Zstandard level 9, fixed row-group
size, no dictionary/byte-stream split, and stable writer settings. Test builds proved
byte-identical JSONL, Parquet, manifests and semantic digests across distinct roots and action
batch sizes. After independent review found a feature-to-modeling layer inversion, the shared
catalogue/digest seam moved to `scouting.contracts`; the final matrix version suffix now binds
the feature code version and digest as well as canonical, registry and policy authorities.
The pre-remediation output remains recoverable at `/tmp/w09-pre-layer-rebuild.uizmUE` and is
not an accepted discovery root.

## Accepted transparent index

- Index ID: `d362d87e-4d02-56a1-a5c8-446f5eaa72a3`
- Index version: `w09-historical-player-index-v1`
- Index manifest digest: `30c2b6c1e0d65c8214860131f690b8b6cac05fe317ffa208a2785e11160eb0bc`
- Candidate catalogue digest: `c96665b98221bb5f45f963a15192f754cebc5d748dd2ef8a2b98e22f854d31b7`
- Candidate count: 1,975, exactly equal to matrix rows.
- Methods: full-population weighted Euclidean and weighted cosine after median/IQR robust
  scaling. Constant features retain unit scale. No ANN, approximation, or pre-limit exists.

The production loader reproduced the scaled vectors from the raw candidate catalogue and
scaler, verified every byte/semantic digest and matrix pin, and constructed the immutable
serving authority. A retained exemplar smoke query scored all 408 admitted rows in its
competition before limiting and returned five candidates with all 16 feature contributions.
The scoring vectors and both scaler arrays are byte-identical to the superseded build; only
text labels and their bound authority digests changed.

## Unsupported claims

G-RW4 expert validation is absent. These artifacts support deterministic, inspectable,
replayable historical-player resemblance research. They do not support a claim that the
features are football-relevant, that the rankings improve recruitment decisions, that a
player is suitable/valuable/available, or that the retained 2017/18 population represents a
current provider or current market.
