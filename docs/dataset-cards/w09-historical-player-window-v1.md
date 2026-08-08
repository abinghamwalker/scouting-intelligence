# W09 historical player-window dataset card

## Status and authority

This card describes the retained Wyscout 2017/18 player–competition–season feature population
used by the local W09 historical-player research workbench after the approved Package A semantic
uplift. It is a dataset card, not a model card and not evidence of football relevance.

- Canonical dataset: `2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e`
- Canonical-build digest: `0105267ae0f107a63fad33b24adecdb3c4bb2e900bdf79a505e9ad4af6264b43`
- Feature matrix version: `w09-historical-player-window-v1-a9f7cc2d5fc12ea0`
- Feature matrix manifest digest: `41e5c6d767d64f510718df912e71c26e55509ad8f9f1799ba0270837ee637f6a`
- Feature matrix digest: `20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42`
- Semantic evaluation: `w09-goal-event-semantic-uplift-v1`
- Semantic evaluation digest: `4bf40416d1474188c801b9d122a3c8a7000da19ba40aa00f4c886b67c4d0d880`

Independent clean-root reconstruction confirmed that Package A left canonical source authority,
population, eligibility and every non-goal feature value unchanged.

## Intended use and claim boundary

The dataset supports deterministic, inspectable resemblance research within one governed
historical population. It may be used to:

- choose a real historical exemplar or declare a weighted 16-feature profile;
- filter eligible candidates by one selected target competition, season, broad position and
  evidenced minutes;
- inspect exact per-90 inputs, coverage, lineage and version pins; and
- reproduce a saved local experiment against the exact compatible authority.

It does not establish football relevance, recruitment usefulness, future performance, transfer
success, price, value, availability, squad fit, outcomes or current-market coverage. W06 remains
`NO_GO` for positive relevance or recruitment claims. W10 remains `REWORK`; no formal W10
evidence has been collected and G-RW4 remains `INSUFFICIENT_EVIDENCE`.

## Source, rights and temporal scope

- Source: Pappalardo et al., *Soccer match event dataset*, supplied by Wyscout, figshare
  collection v5, licensed CC BY 4.0.
- Retained source universe: 1,826 matches, 3,071,395 actions, 142 teams and 3,603 players.
- Provider boundary: retained Wyscout concepts are mapped into provider-neutral canonical
  identities, appearances and actions before feature construction.
- Historical window: `[2017-07-01T00:00:00Z, 2018-07-01T00:00:00Z)`.
- Feature cutoff: `2026-08-05T00:00:00Z`; admitted source and identity authorities must be
  strictly earlier.
- Operational restriction: this authority remains inside the local workbench. Provider/network
  access, external transfer, deployment and publication are not authorised by this project.

The source licence does not override the repository's stricter local-only operating boundary.
Attribution must remain attached to reports and other retained representations.

## Population and grain

The explainable grain is one canonical player UUID by competition by season within the fixed
2017/18 window. The retained population contains:

| Boundary | Retained count |
|---|---:|
| Source/catalogue players | 3,603 |
| Eligible matrix rows | 1,975 |
| Unique eligible players | 1,965 |
| Goalkeepers | 136 |
| Defenders | 713 |
| Midfielders | 711 |
| Forwards | 415 |

The eligible rows cover five domestic competitions: England 389, France 402, Germany 352, Italy
409 and Spain 423. A player can contribute more than one eligible competition-season grain, so
matrix rows and unique players are intentionally different counts. The other retained source
competitions have no row that satisfies the fixed window and eligibility policy.

This is not a combined all-leagues retrieval promise. The index contains every eligible row, but
each live query scores every filter-admitted row in one selected target competition and season
before applying its result limit. An exemplar may come from a different competition.

## Eligibility and governed minutes

A grain is eligible at a minimum of 450 governed usable minutes. Membership and minutes come only
from canonical played appearances:

- action presence does not establish membership or minutes;
- catalogue `currentTeamId` does not establish historical membership;
- exact total minutes require every played stint to be exact;
- otherwise usable exposure is retained as a conservative lower bound; and
- all-unusable or unused-bench grains remain in the eligibility ledger but are not matrix rows.

Every one of the 1,975 eligible rows currently has a conservative lower bound rather than an exact
minute total. The true denominator can therefore be larger, so every derived per-90 rate may be
overstated. A higher minute filter narrows exposure uncertainty but does not turn lower-bound
minutes into exact minutes.

## Features and denominator semantics

Every active value is a retained coordinate-independent canonical-action count divided by
governed usable minutes:

`feature_per90 = admitted_numerator_count × 90 / governed_minutes`

The fixed ordered features are passes, accurate passes, crosses, smart passes, shots, shots on
target, goals, key passes, assists, duels, duels won, interceptions, clearances, accelerations,
fouls and touches. Their stored unit is `count_per_90_governed_minutes`.

These are count rates, not efficiency percentages. In particular, `accurate_passes_per90`,
`shots_on_target_per90` and `duels_won_per90` are numerator rates; they are not pass accuracy,
shot conversion or duel-win percentage. Parent/numerator pairs are strongly correlated and can
duplicate activity volume when weighted together.

### Corrected goals predicate

After Package A, `goals_per90` counts retained actions carrying goal tag 101, excludes own-goal
tag 102 and excludes event 9. Event 9 represents retained save-attempt forms in this source and
must not enter a generic player-goals numerator. The predicate deliberately does not use an
event-10-only shortcut because that would discard retained non-event-10 set-piece goal evidence.

The correction does not relabel excluded event 9 rows as goals conceded, shots faced, saves or
save quality. The retained source does not support those goalkeeper-effectiveness claims. The
post-uplift reconciliation requirement is 4,695 admitted non-event-9 goal rows and zero event 9
goal rows; the master-owned semantic evaluation identity above must prove that result.

## Completeness, coverage and missingness

The registry is count-based. A valid zero numerator is the observed state `ZERO`, not missing
evidence. Every eligible row therefore contains every active feature, and matrix/index loading
rejects a row with a missing active value.

Coordinate-independent predicates retain applicable actions even when coordinates are absent or
invalid. Coordinate coverage remains separate evidence; it is not silently converted into feature
missingness. Match/action coverage and minute state travel with each row and must remain visible
in exact comparisons.

Legacy saved contracts retain empty missing-feature fields for compatibility. Those fields are
internal compatibility data, not a claim that future registries can never be missing. A future
ratio feature with a zero or unavailable denominator would require new eligibility, missingness,
serving, reporting, evaluation and UI semantics before acceptance.

## Known biases and limitations

- The data describes selected 2017/18 domestic competitions, not contemporary football or a
  complete market.
- Provider event definitions, collection practices and lineup evidence constrain what can be
  measured.
- All eligible minute denominators are lower bounds; direct rate comparisons inherit that
  uncertainty.
- The four broad position codes are not a role taxonomy. Within-position styles and tactical
  responsibilities remain heterogeneous.
- The 16 inputs are generic action-volume features. They remain poorly suited to goalkeeper
  effectiveness even after removing save-attempt events from `goals_per90`.
- No small-sample shrinkage is applied. A rate near the eligibility floor is treated as a direct
  observation, not pulled toward a cohort estimate.
- Related numerator/parent features are highly correlated. This card does not claim the feature
  set is decorrelated or optimally weighted.
- The population contains no expert relevance labels, recruitment outcomes or protected W10
  responses.

## Synthetic-data prohibition

Synthetic player rows are restricted to automated tests and failure-path fixtures. They must not
enter this matrix, the live candidate catalogue, an operator walkthrough, a saved product
experiment or evidence offered as retrieval quality. A loader that cannot establish the exact
governed matrix and compatible index must fail closed rather than substitute synthetic, stale,
legacy or newest-found data.

## Lineage and update policy

Every row binds immutable source, identity, canonical-build, feature-registry, eligibility-policy
and cutoff authorities. Matrix and index loaders verify physical bytes, semantic digests, feature
order, scaler reconstruction, catalogue identity and exact pins before serving.

The Package A event-9 exclusion changes the feature registry and therefore requires one governed
matrix → index → evaluation → live W10-derived-evidence cascade. It does not authorise a canonical
rebuild or a W10 threshold change. Historical authorities remain historical and are not rewritten.

Any later change to source, identity, population, eligibility, feature semantics or ordering must:

1. create a new immutable version;
2. rebuild only the affected tier and its downstream authorities;
3. reproduce deterministic bytes and manifests in clean temporary roots;
4. update this card from verified live manifests; and
5. test every saved experiment through exact pin compatibility.

Saved experiments are never migrated or re-pinned. A pre-change experiment must report
`INCOMPATIBLE_PINS` against a new authority rather than being made to appear reproduced.
