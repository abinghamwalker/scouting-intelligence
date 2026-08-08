# W10 presentation-v2 construct and retained-source capability

- Packet: `W10-V2-EVIDENCE-DESIGN-08A-R1`
- Date: 2026-08-06
- Decision: **A1 CAPABLE WITH A NARROW GK CONSTRUCT AND QUERY-LEVEL SUFFICIENCY FILTERS**
- Authority: accepted W09 canonical build
  `72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7`, feature matrix
  `w09-historical-player-window-v1-a31511705ac15a5d`

This report fixes what presentation v2 may measure. It does not authorise collection, freeze a
protocol, add a feature, change W09 ranking or establish football relevance.

## Construct and decision rule

The construct is **credible historical role/style comparison**: similarity in realised 2017/18
functional involvement and action-selection patterns within the same broad position, evidenced by
recurring recorded territory, action mix and execution distributions. It is not W09 distance,
rank, reputation, player quality, recruitment suitability, future performance, value, availability,
team fit or an outcome claim.

An expert answers: “Is this candidate a credible historical role/style comparison to the exemplar,
given the football evidence presented?” Relevance, confidence and evidence sufficiency are three
separate responses. A primary judgement is analysis-eligible only when the assessment-basis field
records use of the supplied independent descriptors (`supplied_profile` or `both`). Prior
professional knowledge is recorded separately; `prior_knowledge_only` remains useful sensitivity
evidence but is not primary construct evidence. `unable_to_assess` is an abstention, never a zero or
an irrelevant rating.

The evidence prerequisites for each displayed player are:

1. governed evidence quantity and coverage;
2. all 16 transparent W09 inputs and within-position percentiles;
3. the mandatory position-specific independent families below; and
4. sufficient raw opportunities under thresholds preregistered by A2 before participant exposure.

The 16 inputs alone never satisfy item 3: asking an expert to agree with the exact attributes used
to retrieve a player would provide circular face validation of the scorer, not an independent
football-relevance test.

## Five evidence classes

| Class | Meaning and treatment |
|---|---|
| `EVIDENCE_QUANTITY` | Governed minutes, minute state, matches, retained actions and coverage. It says how much evidence exists, not how a player played. |
| `W09_INPUT` | The exact 16 matrix fields read by the frozen scorer. Display for transparency, never relabel as independent evidence. |
| `INDEPENDENT_DESCRIPTOR` | A deterministic event distribution not present in the W09 vector and not read by its code path. This is the required primary assessment basis. |
| `PRIOR_PROFESSIONAL_KNOWLEDGE` | Participant knowledge outside the supplied bundle. Record separately because visible identity/name can invoke it; never backfill source fields from it. |
| `UNSUPPORTED_INFERENCE` | A dimension the retained source cannot establish. Do not calculate, imply, impute, render as zero or invite the participant to infer it. |

Identity, name, club and competition are context, not playing evidence. Name recognition is an
unavoidable measured basis while identity remains visible; it cannot silently substitute for an
independent descriptor.

## Exact retained authority

The canonical manifest is
`data/manifests/wyscout/v5/research/72969be11e9a13a3f2c87b92ccff0296e9ab026fdd531383ce67af074740fdb7.canonical-manifest.json`.
Its five action partitions contain 3,071,395 rows. The exact retained action schema is
`src/scouting/data_products/wyscout/historical.py::_ACTION_SCHEMA`; projection is performed by
`_action_batches_for_partition`, with coordinates classified by `_positions`. It retains source and
canonical action/match/competition/player/team identity, `event_id`, optional `sub_event_id`,
`tag_ids`, period and time, `start_x`, `start_y`, optional `end_x`, `end_y`,
`coordinate_evidence_state`, source/identity availability and cutoff clocks. The canonical manifest
records only three invalid-coordinate actions, preserves them without clamping, and admits only
`coordinate_evidence_state == "valid"` to coordinate coverage.

The accepted matrix manifest is
`data/manifests/wyscout/v5/research_features/w09-historical-player-window-v1-a31511705ac15a5d.feature-matrix.manifest.json`.
It contains 1,975 eligible grains: GK 136, DF 713, MD 711 and FW 415. Every eligible row has
`minute_state == "conservative_lower_bound"`; consequently every per-90 rate has a lower-bound
minutes denominator and can overstate the rate that would result from the unknown true minutes.
That limitation must appear beside values, not only in a global footnote.

### W09 scorer-input separation

`configs/features/w09-historical-player-window-v1.json` fixes, in order: passes, accurate passes,
crosses, smart passes, shots, shots on target, goals, key passes, assists, duels, duels won,
interceptions, clearances, accelerations, fouls and touches, all per 90 governed minutes.
`src/scouting/features/historical.py::load_historical_feature_registry` rejects any predicate/order
drift; `HistoricalFeatureDefinition.matches`, `feature_numerators` and
`_stream_action_aggregates` construct only those fields. `src/scouting/modeling/research.py::build_research_index`
requires matrix feature order, converts only `feature_values` into the index, and
`fit_robust_scaler` scales those columns. `src/scouting/serving/research.py::ResearchServingService.execute_query`
selects only names from `index_manifest.feature_names` and calls
`src/scouting/m0/scoring.py::score_vector_rows`. The frozen W10 v1 request builder supplied all
manifest names at equal weight.

Therefore every descriptor below is independent of the W09 ranking code path: it requires a new,
separate canonical-action aggregation and must never be appended to matrix `feature_names`, scaler
arrays, index vectors, query weights or scorer inputs. Protected W10 responses likewise must never
enter either path.

## Availability, denominator and coverage contract for A2

Every scalar, distribution and visual must carry its class, `used_by_w09_ranking`, exact predicate,
raw numerator(s), raw opportunity denominator, governed-minutes denominator where a per-90 value is
shown, coordinate-valid numerator/expected denominator where locations are used, position reference
population, derivation version and source lineage. A percentile is calculated only among comparable
within-position `observed_value`/`observed_zero` rows; it is not a replacement for a raw value or
coverage state.

A2 must represent these mutually exclusive states and must not collapse them:

| State | Required meaning |
|---|---|
| `observed_value` | Captured, valid, opportunity threshold met and numerator is non-zero. |
| `observed_zero` | Captured, valid, opportunity threshold met and exact numerator is zero. |
| `insufficient_opportunities` | Captured but the frozen family denominator is below its threshold; suppress the estimate/percentile. |
| `not_applicable` | The frozen position rubric excludes the family. |
| `not_captured` | The retained canonical source does not record the dimension. |
| `invalid_missing` | A required field, lineage pin or coverage requirement failed; fail the bundle visibly. |

Thresholds are measurement rules, not facts discovered from this audit. A2 must preregister them,
show the raw counts and exclude a formal query/player that lacks any mandatory family. It must not
choose thresholds after seeing expert responses. Recorded zero means a valid searched opportunity
space produced zero events; absent/invalid coordinates, optional-null sub-events and low opportunity
counts are not zero.

Recorded `x`/`y` values may be shown as raw coordinates or neutral fixed bins (for example,
`recorded_x_0_33`), with start/end denominators kept distinct. No accepted authority establishes
attacking direction, pitch side semantics or direction normalisation. Terms such as “progressive”,
“advanced”, “final third”, “left/right flank” or “toward goal” are forbidden until separately
governed orientation semantics exist.

## Accepted independent descriptor roster

All counts below are event-descriptive. Distribution shares use the stated raw opportunities;
per-90 versions, if displayed, additionally disclose governed minutes and their lower-bound state.

| Family ID and exact retained predicate | Descriptor and denominator | Position use | W09 relationship |
|---|---|---|---|
| `ID-LOC-01`: any action with valid start coordinates | Neutral fixed-bin start-location distribution; numerator per bin / all qualifying valid starts, plus valid-start / retained-action coverage. Optional end-location distribution uses its own end-present denominator. | Mandatory GK/DF/MD/FW. | Coordinates and coverage are not scorer columns. No direction semantics. |
| `ID-PASS-01`: event 8, sub-events 81 hand pass, 83 high pass, 84 launch, 85 simple pass | Raw subtype counts and shares / all event-8 passes; four named shares do not have to sum to one because other subtypes remain in the denominator. | Mandatory GK/DF/MD/FW. | Pass total is a W09 denominator; these non-W09 subtype numerators/distribution are independent. Exclude 80 crosses and 86 smart passes from this family because their counts are W09 inputs. |
| `ID-DUEL-01`: event 1, sub-events 10 air, 11 ground attacking, 12 ground defending, 13 ground loose-ball duel | Raw subtype counts and shares / all event-1 duels. | Mandatory DF/MD; mandatory FW action-mix evidence; supplementary GK. | Total duels is W09 input; subtype mix is not. Win rate/quality is not introduced. |
| `ID-DEFLOC-01`: valid starts for event 1/sub-event 12, tag 1401 interceptions, and sub-event 71 clearances, reported as separate components | Component raw counts plus neutral start-location distributions / valid starts for each component; never combine away component denominators. | Mandatory DF; mandatory MD when opportunity threshold met, otherwise query ineligible; supplementary FW; not applicable GK. | Interception/clearance counts and total duels are W09 inputs, but their spatial distributions and defending-duel subtype are not. |
| `ID-SHOTLOC-01`: event 10 with valid start coordinates | Neutral shot start-location distribution / valid-coordinate shots, with valid-coordinate shots / all shots coverage. | Mandatory FW; mandatory MD when opportunity threshold met; supplementary DF; not applicable GK. | Shot count is W09 input; its spatial distribution is not. Do not infer chance quality or direction. |
| `ID-GK-01`: event 3/sub-event 34; event 4/sub-event 40; event 9/sub-events 90 and 91 | Goal-kick and leaving-line event rates/counts; save-attempt mix (90 reflexes versus 91 generic) / all event-9 save attempts; pair with `ID-PASS-01` and neutral locations. | Mandatory GK only. | None of these predicates is a W09 feature. These describe recorded involvement/mix, not effectiveness. |

Do not manufacture a generic composite, “style score”, similarity label, better/worse colouring or
position rank from these descriptors. Exemplar and candidate receive identical rows and glossary.

## Position answerability

| Position | Decision | Minimum independent basis for a formal task | Boundary/fallback |
|---|---|---|---|
| GK | **YES — deliberately narrow** | `ID-LOC-01`, `ID-PASS-01`, and all of `ID-GK-01`. The full eligible audit found every one of 136 GK grains had recorded passes, save attempts, leaving-line actions, goal kicks and launches: minima 75, 16, 4, 34 and 12 respectively; minimum valid-coordinate coverage was 99.9285%. | Judge recorded distribution/involvement style only. If a protocol needs goalkeeper quality or an unavailable dimension below, remove/redesign GK queries before freeze. |
| DF | **YES** | `ID-LOC-01`, `ID-PASS-01`, `ID-DUEL-01`, `ID-DEFLOC-01`; shot location is supplementary when supported. | A row failing any mandatory family is query-ineligible; do not replace it with shooting or generic W09 counts. |
| MD | **YES** | `ID-LOC-01`, `ID-PASS-01`, `ID-DUEL-01`, plus supported defensive-action and/or shot-location evidence according to a frozen MD sub-rubric. | The sub-rubric and opportunity thresholds must be fixed before query selection, not selected per result. Mandatory-family failure makes the row query-ineligible. |
| FW | **YES** | `ID-LOC-01`, `ID-PASS-01`, `ID-DUEL-01`, `ID-SHOTLOC-01`. | A forward without sufficient shot opportunities is query-ineligible; do not call zero/low shots a stable style estimate. |

These are population-capability decisions, not claims that every possible player pair will be
assessable. A2 must derive query eligibility deterministically from the frozen thresholds. The v1
W10 pack observed stronger minima for its selected GK rows (at least 108 passes, 39 save attempts,
12 leaving-line actions, 92 goal kicks and 99.9% coordinate coverage), but those observations are
neither formal evidence nor appropriate threshold selection.

## Explicit unsupported dimensions

Across positions the source does not support causal tactics, off-ball movement, pressing intensity,
true possession responsibility, role instructions, formation-adjusted behaviour, opponent/context
adjustment, current ability, future performance, availability, fit, value, errors or recruitment
outcomes. Coordinates do not support directional semantics without a new authority.

For GK specifically, the retained events do **not** support shots faced, save percentage,
shot-stopping quality, goals conceded, xG/PSxG, goals prevented, claims/cross dominance, errors,
sweeping effectiveness or any performance/recruitment conclusion. Event 9 is a recorded
save-attempt/reflex mix, not proof of the shot population or outcome. Event 4 is recorded
leaving-line frequency, not sweeping success. These fields must be `not_captured`, not zero.

## A2 freeze instruction

A2 may proceed with all four broad positions only if it implements the exact class labels,
availability states, lineage/denominator/coverage fields, descriptor roster, position rules and
W09 code-path separation above. It must fail bundle construction for missing mandatory evidence and
freeze opportunity thresholds before participant exposure. Any request to add directional labels,
GK effectiveness, outcome inference, a composite descriptor or a new provider is a redesign, not a
bounded implementation detail.
