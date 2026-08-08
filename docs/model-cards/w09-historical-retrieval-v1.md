# W09 historical retrieval model card

## Status and live authority

This card describes the transparent W09 retrieval baseline after the approved Package A source-
semantic uplift. It documents a deterministic historical-resemblance method; it does not promote
a football-relevance or recruitment model.

- Model configuration: `w09-historical-retrieval-v1`
- Model version: `w09-robust-scaled-transparent-baselines-v1`
- Feature matrix version: `w09-historical-player-window-v1-a9f7cc2d5fc12ea0`
- Feature matrix digest: `20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42`
- Research index ID: `ff55b286-935c-55c4-bb8e-814a95962b41`
- Research index manifest digest: `b805bd66db988d2db79128c1700ef1134191a717980a4a87af8ea3a779e6e580`
- Semantic evaluation: `w09-goal-event-semantic-uplift-v1`
- Semantic evaluation digest: `4bf40416d1474188c801b9d122a3c8a7000da19ba40aa00f4c886b67c4d0d880`
- Frozen suite digest: `6a2630c3766d4762c12fc5ebf74e1fbfd43b4c2aa11b55847615c3c34e896a84`
- Frozen evaluation result: `5dd3cf9bd0cf20ae689c121fdf05471b930836c09b2a4bea4b8bb43729ae7e90`
- Reviewed non-acceptance checkpoint: `checkpoint/w10-prestudy-uplift-reviewed`

The scorer digest remains
`535e244720b7abd46ac25e7de6f3ac387247d4213a00b4857e08acc19e19fc1c` and the model
configuration is unchanged. The corrected goal values create new matrix, scaler/vector, index and
evaluation identities.

## Intended use

The model helps a local researcher ask: “Within this governed historical population and declared
feature weighting, which candidates have the smallest transparent vector distance from this
exemplar or target profile, and why?”

Supported uses are:

- an exemplar query using one exact retained player grain;
- a weighted profile containing the same ordered feature set;
- weighted Euclidean or weighted cosine retrieval;
- an explicit selected target competition, season, broad-position filter, minimum-minutes filter
  and exclusions;
- exact per-feature contrasts and contributions; and
- deterministic local save, report and replay under exact version pins.

The exemplar can come from a different competition from the candidates. Cross-league targeting
therefore works for one selected target competition. The product does not provide one combined
all-leagues candidate pool.

## Inputs and corrected feature semantics

The input is the 1,975-row, 1,965-player dataset described in
`docs/dataset-cards/w09-historical-player-window-v1.md`. It has 16 direct count-per-90 features in
a fixed order. All denominators are governed played minutes and currently carry a conservative
lower bound state.

Raw values are rates, not percentages. Accurate passes, shots on target and duels won are child
numerator rates rather than accuracy, conversion or win ratios.

Package A corrects `goals_per90` to include goal tag 101, exclude own-goal tag 102 and exclude
event 9 save-attempt rows. It retains non-event-9 set-piece goal evidence. This is a semantic
repair to what the feature counts, not evidence that candidate rankings became more relevant.

## Scaling

One scaler is fitted globally across all 1,975 eligible rows. For feature `i`:

`z_i = (raw_i - global_median_i) / global_IQR_i`

The IQR is the linearly interpolated 75th percentile minus the 25th percentile. If it is zero, the
model retains the feature with unit scale. No row is sampled or imputed.

The position and selected target competition filters do not refit this scaler. It is therefore a
transductive description of the declared historical population, not a learned claim that global
scaling is optimal for every role or competition.

## Retrieval geometry

Weights are finite, non-negative relative influence settings. Zero disables a feature; at least
one weight must be positive. Weights are not probabilities or percentages.

For weighted Euclidean retrieval, with scaled contrast `d_i = candidate_z_i - query_z_i`:

`contribution_i = weight_i × d_i²`

`distance = sqrt(sum(contribution_i))`

Each Euclidean contribution is non-negative and the contributions sum to squared distance. A
contribution is not a percentage share unless someone separately computes and clearly labels such
a diagnostic; the live contract does not do so.

For weighted cosine retrieval:

`distance = 1 - weighted_cosine_similarity`

The query and candidate are normalised using the active weights. The displayed per-feature term is
the signed negative product of their normalised components, and distance is `1 +` the sum of those
terms. A cosine term can increase or reduce distance. Euclidean and cosine contributions must not
be compared as if they had the same meaning.

For both methods, a smaller value means closer only under the exact same method, feature subset,
weights, filters and authority pins. Distance is not a calibrated match score, probability,
football grade or percentage. Euclidean distance is unbounded; cosine distance is bounded from
zero to two.

## Candidate population and deterministic execution

The index contains every eligible matrix row and uses no approximate-nearest-neighbour search or
pre-limit. Each request first applies its explicit selected target competition/season, position,
minimum-minutes and player exclusions. The scorer evaluates every admitted row and only then
applies the result limit.

“Full-population scoring” therefore means the full filter-admitted population of one selected
target competition and season, not all five competitions combined. Candidate order is determined
by distance followed by stable player/grain identity tie keys.

## Explanations

Every returned candidate carries, in the active feature order:

- query and candidate raw count-per-90 values;
- their globally scaled values and scaled contrast;
- the exact submitted weight;
- the method-specific contribution term; and
- row-level minutes, coverage and limitations.

The service verifies that Euclidean terms reconstruct squared distance and that signed cosine
terms reconstruct cosine distance. Exact comparison returns retained matrix evidence rather than
recomputing or inferring new football metrics.

## Evaluation evidence and limits

The retained frozen suite verifies deterministic execution, identity and filter accounting,
full scoring before limit, exact explanation arithmetic, reproducibility and bounded weight
sensitivity. It contains no expert relevance labels.

The Package A semantic evaluation is separately preregistered. Its required checks include:

- zero event 9 rows and exactly 4,695 intended rows in the corrected goal numerator;
- rejection of an event-10-only negative control that drops set-piece goal evidence;
- unchanged canonical authority, population, eligibility, minutes and non-goal features;
- unchanged candidate admission counts in five representative scenarios;
- exact Euclidean/cosine explanation reconstruction;
- at least 8/10 before/after top-ten overlap for every non-goalkeeper method/scenario as a churn
  rejection guard; and
- no W10 threshold movement or use of protected human evidence.

The live evaluation above passed these preregistered checks. Ranking overlap and sensitivity are
engineering diagnostics, not a football-quality threshold. The corrected output may be described
as excluding save-attempt events from `goals_per90`; it may not be described as proven more
football-relevant.

## Limitations

- The 16 inputs are generic event-count rates and remain poorly tailored to goalkeeper
  effectiveness. The source does not support shot-stopping, goals-conceded or save-quality claims.
- The broad GK/DF/MD/FW filter is not a complete role taxonomy.
- Accurate-pass/pass, shot-on-target/shot and duel-won/duel pairs are correlated and can duplicate
  activity volume under equal weights.
- No covariance correction, position-conditioned scaler, ratio redesign or small-sample shrinkage
  is applied.
- All eligible minute denominators are conservative lower bounds, so raw per-90 rates may be
  overstated.
- The global scaler is position-sensitive and fitted on the same complete historical population
  that is searched.
- The population is retained 2017/18 evidence from five domestic competitions, not current-market
  coverage.
- Determinism and transparent explanations do not establish relevance.

## Prohibited claims and governance state

This model must not be presented as a recommendation, ranking of player quality, prediction of
future performance, transfer-success model, valuation, availability assessment, squad-fit tool or
outcome model. It must not be used to expose protected W10 labels or tune from future formal W10
responses.

W06 remains `NO_GO` for positive football-relevance and recruitment claims. W10 remains `REWORK`;
08E and 08F are unstarted, formal collection is unauthorised, and G-RW4 remains
`INSUFFICIENT_EVIDENCE`.

The runtime is local, container-free and provider-neutral. No provider/network access, credential,
cloud service, public endpoint or deployment is part of the model.

## Experiment compatibility

Every experiment binds the source, canonical data, matrix, feature registry, model configuration,
scorer, index, query, filters, result and report digests. Package A changes live matrix and index
authority. Pre-uplift experiments must therefore replay as `INCOMPATIBLE_PINS`; they are not
migrated, deleted or re-pinned.

A post-uplift experiment may report `REPRODUCED` only when the exact saved request, authority pins,
result identity and result digest reproduce. `RESULT_MISMATCH` is a retained failure requiring
investigation, never an invitation to overwrite history.
