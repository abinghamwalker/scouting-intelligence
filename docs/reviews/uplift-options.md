# W09 historical-player workbench uplift options

**Date:** 2026-08-07

**Phase:** read-only options and evidence

**Decision status:** implementation not authorised

**Recommended non-acceptance checkpoint:** `checkpoint/w10-prestudy-uplift-reviewed`

## Executive recommendation

Approve **Package A — source-semantic repair plus the complete delivery bundle**. It is the
smallest package that fixes the strongest observed methodological problem at every call site,
preserves the transparent scorer, and closes the principal operator/documentation gaps. Estimated
elapsed engineering effort is **12.0 hours**, including the reserved **2.0-hour final gate**.

The proposed method change is deliberately narrow: `goals_per90` would continue to count retained
goal-tagged actions except that event 9 save-attempt rows would be excluded. The retained source
shows that the present predicate mixes 4,741 save-attempt events into a feature labelled goals.
Those events make the feature dominate the recorded goalkeeper example. Excluding them is a
source-semantic correction, not evidence that the resulting rankings are more football-relevant.

No Phase 2 work, build, re-pin, experiment mutation, W10 evidence collection, acceptance action,
commit, or tag has begun. The decision required is stated at the end of this paper.

## Current-state evidence

### Repository and programme state

The master independently verified:

- branch `main` at `5e002f18cedbdd524ed144e3cf24c83dd2d74db7`;
- `checkpoint/w10-cross-phase-remediation` resolves to that commit;
- clean working tree before this paper and no Git remotes;
- `checkpoint/w10-accepted` is absent;
- W09 is `CLOSED`; W10 is `REWORK`;
- 08D remains engineering-ready with human evidence required; 08E and 08F are unstarted;
- G-RW4 remains `INSUFFICIENT_EVIDENCE`; and
- formal W10 evidence collection remains disabled and unauthorised.

The recorded full gate is `3111 passed, 1 warning`. It was not repeated in this read-only phase,
because the verified starting state matches the accepted checkpoint. A clean temporary-root replay
of the current W09 frozen evaluation completed in 4.8 seconds and reproduced its recorded result
digest exactly.

### Live authority

| Authority | Verified identity |
|---|---|
| Canonical dataset/build ID | `2d018b617d870579be1acfa76a22ae1d6d184071feaa658f353b162e421bee6e` |
| Canonical manifest SHA-256 | `0105267ae0f107a63fad33b24adecdb3c4bb2e900bdf79a505e9ad4af6264b43` |
| Feature matrix | `w09-historical-player-window-v1-ad74298cf718d6f6` |
| Matrix digest | `49bf6f72d2e564fa5c421c2eb36f70ceb57810a44c1442da9e14a3db6b799bb9` |
| Research index | `97ed622c-3806-5095-9a3a-e32e457f6ba7` |
| Index manifest digest | `f4a9e692336d152938319193a5f5c7cf28cb406da4aa71ca881eae5e0c8fe7c0` |
| Scorer digest | `535e244720b7abd46ac25e7de6f3ac387247d4213a00b4857e08acc19e19fc1c` |
| Frozen evaluation result | `2c58d59abc0f1f0ac4b3495a5aa682bea637cfaf4e400300f0b5c5d43b3c3e47` |
| Frozen suite | `786ac9e7b1161965d8c5f0680f5096e4ff0c08453cdda19806e10e406d0432a2` |

The matrix contains 1,975 rows for 1,965 players: GK 136, DF 713, MD 711 and FW 415.
It contains no synthetic rows. The current model fits one median/IQR scaler over all 1,975 rows,
then scores every row admitted by one selected target competition/season and the other explicit
filters before limiting results.

Cross-league targeting is already implemented: the exemplar may come from another competition,
while candidates come from the one selected target competition. A combined all-leagues candidate
pool is a different product option.

### Saved-experiment evidence

The retained pre-uplift experiment is present and currently reproduces exactly:

| Item | Identity |
|---|---|
| Experiment | `e6a8a280-423c-8248-ac40-037a34b99cf7` |
| Experiment digest | `16b2491915431a1425dfc028e90a9b4d474cb65480bb3d65ae48477f208c4495` |
| Report digest | `4498abb7b4e70901deb51cd186b06204e009ccee9244099f984977a6acaba24a` |
| Result digest | `37ab6fa2033c8a9763c674d4c0115f72bf8c83b9c654a5df4f865d38aa8798d1` |

Its report bytes match their digest and retain the historical-resemblance claim boundary. Three
older experiments retain honest `INCOMPATIBLE_PINS` replay outcomes. No experiment was replayed,
mutated, migrated, deleted, or re-pinned during this phase.

## Methodological problems actually observed

### 1. The goals feature mixes incompatible event semantics

The feature registry currently defines `goals_per90` as tag 101 and not tag 102, with no event
restriction. Reconciliation against the accepted canonical action rows and eligible matrix shows:

| Retained goal numerator evidence | Count |
|---|---:|
| All current goal-tagged, non-own-goal actions | 9,436 |
| Event 9 save-attempt rows within that total | 4,741 |
| Non-event-9 rows within that total | 4,695 |
| Current GK numerator | 4,738 |
| GK event 9/90 `Reflexes` | 4,165 |
| GK event 9/91 `Save attempt` | 572 |
| GK event 10/100 `Shot` | 1 |

The retained authority does not establish that event 9 rows are goals scored, goals conceded,
shots faced, or save effectiveness. They cannot honestly be used as a generic player-goals rate.
The problem also affects four non-GK save-attempt rows.

For the recorded Sirigu-to-Italian-GK Euclidean scenario, 23 candidates are scored. The current
goal term is the largest squared-distance contribution for 22 of 23 candidates and has a 92.7%
median contribution share. Removing the invalid save-attempt term changes five of the top ten.
This establishes semantic dominance and material ranking sensitivity; it does **not** establish
that either top ten is more football-relevant.

A read-only equal-weight simulation of the narrow source correction retained 10/10 top-ten names
for Van Dijk and Kanté, 9/10 for Salah, and 9/10 for Messi-to-France under Euclidean at the recorded
population settings. Cosine retained 10/10, 10/10, 9/10 and 10/10 respectively. These are planning
estimates, not reproductions of every recorded custom weighting and not promoted evidence; Phase 2
would first freeze and reproduce the exact baseline requests.

### 2. Correlated nested rates duplicate closely related volume

The current feature set includes three numerator/parent pairs:

| Pair | Overall Pearson correlation | Within-position range |
|---|---:|---:|
| passes / accurate passes | 0.9905 | 0.982–0.992 |
| shots / shots on target | 0.9302 | 0.720–0.857 |
| duels / duels won | 0.9147 | 0.803–0.893 |

Equal weights therefore give closely related activity volume more than one coordinate. Explicit
efficiency ratios could reduce that duplication only by replacing a child rate, not by adding more
features. The retained fields support pass accuracy for every row, but shot opportunity is zero for
156 rows, including 129 of 136 GKs; 759 rows have fewer than ten shots. Ratio introduction therefore
requires real missingness, opportunity and uncertainty semantics. It is not a safe small edit.

### 3. Global scaling is position-sensitive, but a replacement is not validated

Global IQR scaling puts the GK median `goals_per90` 5.91 global IQRs above the population median.
Within GK, the goals IQR is about 2.07 times the global IQR, while the global pass IQR is about
3.02 times the GK pass IQR. Seven GK features have zero within-position IQR. Position-conditioned
scaling changes the Sirigu top ten by four names and changes all-exemplar top tens most heavily for
GKs. It can also amplify sparse defender goals by about 3.77 times.

Position-conditioned scaling is therefore a legitimate challenger, not a demonstrated
improvement. Position-by-competition scaling is rejected because the GK cohorts contain only
22–33 rows. W10's within-position percentiles are presentation context and do not validate a
position-conditioned retrieval geometry.

### 4. Covariance methods are numerically and explanatorily costly

The current globally scaled covariance condition numbers are 2,676 overall, 824 for DF, 2,528 for
FW, 2,044,233 for GK and 1,772 for MD. Empirical Mahalanobis is therefore rejected. Positive
identity shrinkage can bring every cohort below about 52, but the selection rule, fit population,
active-feature-subset semantics, and original-weight ordering would all need to be frozen.

Mahalanobis and whitening also introduce cross-feature terms. They cannot preserve the current
honest one-feature/one-non-negative-term Euclidean explanation. PCA/ZCA axes mix football features,
and variance preservation is not relevance preservation. A live covariance promotion does not fit
the budget or current explanation contract.

### 5. Per-90 rates have no small-sample adjustment

All rows use direct count-per-governed-minute rates, and every denominator is a conservative lower
bound. Lower-exposure rows show greater robust-scaled extremity, especially for GKs, but that
pattern can also reflect genuine role and selection differences. A shrinkage prior fitted and
judged on the same population would not demonstrate generalisation. Shrinkage remains a future,
split-window evidence question.

### 6. Delivery and explanation are incomplete

- The 23-line W09 card is titled as a combined dataset/model card but lacks population
  reconciliation, source/rights, eligibility, coverage/bias, detailed denominator semantics,
  lineage/pins and update policy.
- `docs/model-cards/` and `docs/runbooks/` contain only `.gitkeep`.
- The only `.command` launcher starts the W08 console; W09 has none.
- The README has no W09 quick start, URL, walkthrough or troubleshooting path.
- The interface does not define global median/IQR scaling, numerator-rate semantics, method-specific
  contribution arithmetic, or the fact that distances and weights are not percentages.
- “Full-population query” is ambiguous: it means every filter-admitted row in one selected target
  competition/season, not one combined all-leagues pool.

## Ranked package options

The ranking is by credible delivery value per engineering hour, including verification and the
two-hour final-gate reserve.

| Rank | Package | Live authority impact | Exact estimate | Recommendation |
|---:|---|---|---:|---|
| 1 | **A. Source-semantic repair + complete delivery bundle** | Tier 2 matrix cascade | **12.0 h** | **Approve** |
| 2 | B. GK-safe interactive default + complete delivery bundle | Tier 0; no artifact re-pin | **10.0 h** | Lower-risk fallback |
| 3 | C. Delivery-only hardening | Tier 0; no artifact re-pin | **6.5 h** | Safe, but leaves known default defect |
| 4 | D. Offline regularised-geometry benchmark + documentary readiness | Tier 0 unless later promoted | **11.0 h** | Useful future evidence, not the immediate fix |

### Package A — source-semantic repair plus complete delivery bundle

**Method scope**

- Extend the governed feature predicate with an explicit excluded event ID and set
  `goals_per90` to tag 101, excluding tag 102 and event 9.
- Preserve all 4,695 retained non-save goal actions, including retained shot and set-piece goal
  forms; do not replace the predicate with event 10 only.
- Keep the 16-feature shape, global median/IQR scaler, Euclidean/cosine methods, deterministic
  full-population scoring, user-visible raw values and per-feature explanations.
- Add a full-default evaluation witness because the current frozen suite's selected feature sets
  give `goals_per90` weight zero and cannot expose this defect on their own.

**Delivery scope**

- Expand `docs/dataset-cards/w09-historical-player-window-v1.md` as a dataset-only card.
- Add `docs/model-cards/w09-historical-retrieval-v1.md`.
- Add `docs/runbooks/w09-research-workbench.md` and a W09 quick start in `README.md`.
- Add executable `scripts/start_w09_research_workbench.command`, fixed to `127.0.0.1`, with a
  validated unprivileged port, no reload, remote bind, browser automation or detached process.
- Add visible, method-specific explanation copy and focused unit/real-browser coverage.
- Add methodological evaluation, representative-search comparison, and exact pin-transition
  reports.

**Time budget**

| Work | Hours |
|---|---:|
| Freeze exact baseline and acceptance record | 0.5 |
| Predicate/parser implementation and focused tests | 1.5 |
| Clean-root comparative evaluation and negative controls | 1.0 |
| Single matrix/index/evaluation/W10 authority cascade and pin audit | 2.0 |
| Cards, runbook, launcher, README, UI explanations and focused browser tests | 4.5 |
| Integration/contingency | 0.5 |
| Final gate and clean-root reproduction | 2.0 |
| **Total** | **12.0** |

This package fixes an evidenced semantic defect everywhere. Its cost is the full tier-2 authority
cascade and the honest loss of compatibility for every currently saved experiment.

### Package B — GK-safe interactive default plus complete delivery bundle

Set `goals_per90` to weight zero automatically when a GK exemplar is selected in the interactive
workbench, visibly explain why, retain the raw generic goal-tag value and permit an explicit user
override. Add a matching full-default witness and the entire delivery bundle above.

This is tier 0 and preserves matrix, index, evaluation pins and exact saved-experiment replay.
Estimated effort is **10.0 hours** including the final gate. It removes unsupported semantic
dominance from the main interactive default, but it does not correct the underlying feature for
custom API callers and can be overridden. It must be described as a safer interface preset, not a
validated goalkeeper method.

### Package C — delivery-only hardening

Ship the cards, runbook, loopback launcher, README quick start, UI method explanation and focused
tests without changing any weights or method. This is tier 0, has no rebuild/re-pin cascade, and
takes **6.5 hours** including the final gate.

It is the safest operator-readiness package and preserves the retained experiment exactly, but it
would knowingly leave the current all-one default in place for GKs. Documentation could disclose
the issue but would not mitigate it.

### Package D — offline regularised-geometry benchmark plus documentary readiness

Implement a preregistered, leave-one-competition-out evaluation-only challenger using
positive-identity regularised Mahalanobis, negative controls and held-out-feature coherence. Add the
dataset/model cards and runbook, but defer the launcher and interactive explanation work to fit the
budget. Do not expose or promote the challenger live.

This is tier 0 while it remains an offline report and takes **11.0 hours** including the final gate.
It can produce useful negative evidence about covariance-aware geometry, but it does not correct
the known goal-tag problem or improve the live workbench. A later live promotion would require a
tier-1 index/evaluation/W10 cascade and a separate explanation design.

## Package A preregistered evaluation plan

If Package A is approved, the following record is frozen before any methodology edit.

### Baseline

- Exact current pins and all 9,436 goal numerators, with event/position decomposition.
- Current matrix population, eligibility decisions, all non-goal feature structs and canonical
  source lineage.
- Exact Euclidean and cosine results, score distributions, explanation contributions, ties and
  top-ten membership for the five recorded representative scenarios using their exact settings.
- Full admitted-population GK contribution concentration for the Sirigu scenario.
- Current frozen evaluation output, retained report bytes and all experiment replay states.

### Success criteria

1. The rebuilt goal numerator contains **zero event 9 rows** and reconciles exactly to the retained
   source's **4,695 non-event-9, tag-101, non-tag-102 actions**.
2. The event-10-only negative control is rejected because it drops the retained set-piece goal
   evidence; no goal count is selected by visual inspection of rankings.
3. Matrix row count, player count, eligibility decisions, minutes, catalogues, non-goal feature
   values and canonical pins are unchanged. Only the intended goal values plus their necessary
   feature, lineage, artifact and downstream authority digests may change.
4. Two clean temporary-root builds are byte/digest deterministic. Manifest verification, report
   byte checks and replay state checks all pass.
5. The five representative candidate admission counts remain unchanged. For the four non-GK
   scenarios, top-ten overlap versus baseline is at least **8/10 for each method and scenario**.
   This is a churn rejection guard, not a relevance threshold. GK churn is fully reported without
   a quality claim.
6. Invalid save-attempt-derived GK goal contribution becomes zero. Euclidean and cosine explanation
   arithmetic still reconstruct exactly for every returned result.
7. The unchanged nine frozen cases and perturbation definitions still pass after exact re-pinning;
   a supplementary all-feature/default witness exposes the repaired behavior. Euclidean and cosine
   sensitivity are reported separately and only as sensitivity.
8. No W10 threshold, participant response, protected label or future formal evidence is used or
   changed. W10 remains `REWORK`, 08E/08F remain unstarted, and G-RW4 remains
   `INSUFFICIENT_EVIDENCE`.

Passing these criteria permits the claim “the goals feature no longer includes retained
save-attempt events.” It does not permit “retrieval relevance improved.”

### Rejection and stop criteria

Reject the live method change, retain the negative evidence, and ship only still-valid tier-0
delivery work if any of these occurs:

- any event 9 row remains in the goal numerator, or any of the 4,695 intended retained goal rows is
  lost;
- an unintended population, eligibility, minute, canonical or non-goal feature change occurs;
- any non-GK representative method/scenario falls below the 8/10 overlap guard;
- deterministic artifacts, exact explanations, report bytes, compatibility checks or replay fail;
- implementing the correction requires changing a preregistered W10 threshold, inspecting human
  responses, tuning from protected labels, or reselecting a result because names “look better”; or
- the cascade cannot distinguish current derived authorities from immutable historical W10
  evidence.

The rejected method edits would be reversed with targeted patches, not destructive Git commands.
The baseline, attempted-method report and negative result would be retained.

## Exact component and artifact consequences for Package A

The controlling tier rule is: touch the deepest tier once, then rebuild each downstream live
authority once.

| Component | Tier/status | Consequence |
|---|---|---|
| Canonical source and manifest | Tier 3, untouched | Build ID and canonical digest remain exact |
| `configs/features/w09-historical-player-window-v1.json` | Tier 2 | Versioned predicate and registry digest change |
| `src/scouting/features/historical.py` | Tier 2 | Predicate contract/code digest changes; focused tests required |
| Feature matrix and manifest | Tier 2 rebuild | New matrix version/digests; same population and non-goal logical values |
| Model configuration and `src/scouting/m0/scoring.py` | Unchanged | Same global scaling policy, scorer version and scorer digest |
| Research index | Tier 1 rebuild | New index ID/manifest and goal scaler/vector bytes |
| W09 evaluation authority/result | Downstream re-pin | Same nine cases, weights and thresholds; new exact pins/result identity |
| Saved experiments | Exact-pin boundary | All existing experiments, including the retained pre-uplift one, become `INCOMPATIBLE_PINS`; none are migrated or re-pinned |
| W10 v2 presentation config/contracts/current derived validation | Downstream re-pin | Update exact matrix predicate/pins and regenerate only live derived technical evidence; no threshold change or human activity |
| Superseded W10 v1 and retained pilot evidence | Historical, immutable | Do not re-issue, overwrite or count as current formal evidence |
| Cards/runbook/launcher/README/UI/reporting | Tier 0 | Finalised only after new live identities are verified |

Cascade order:

1. Build the feature matrix twice in clean temporary roots and compare.
2. Perform the single production matrix rebuild.
3. Rebuild the research index.
4. Reproduce/re-pin the W09 evaluation without changing its cases or thresholds.
5. Re-pin and regenerate only current W10 v2 derived technical evidence that contractually follows
   the live matrix; preserve historical authorities.
6. Verify every saved experiment against exact pins; create and replay one clearly labelled
   post-uplift experiment only after the new authority is final.
7. Finalise documentation/report identities, then run the complete final gate.

No canonical rebuild is expected. If the canonical tier becomes necessary, stop and return for a
new decision because Package A's scope and estimate would no longer hold.

## Explanation and reporting consequences

The workbench and cards must explain:

- raw values are retained event numerator counts per 90 governed minutes, not percentages;
- accurate passes, shots on target and duels won are numerator rates, not efficiency percentages;
- all governed-minute denominators are conservative lower bounds and rates may be overstated;
- scaling is frozen globally over all 1,975 eligible rows:
  `scaled = (raw - global median) / global IQR`, with unit scale for zero IQR;
- position and target-competition filters do not refit the scaler;
- Euclidean uses `weight * scaled_contrast^2` terms and the distance is their square-root sum;
- cosine uses weighted normalised vectors, has signed contributions, and is reported separately;
- distances, contributions and feature weights are not probabilities, calibrated match scores or
  percentages;
- lower distance is comparable only under the same method, features, weights and authority pins;
- full-population scoring means every filter-admitted row in one selected target
  competition/season; and
- the exemplar may come from a different competition. Combined all-leagues ranking is not present.

Package A must also define the corrected goal predicate exactly and state that it excludes recorded
save-attempt actions. It must not relabel those excluded events as goals conceded or save quality.

## Residual risks and non-claims

- The broad GK/DF/MD/FW classes are not a complete football role taxonomy.
- Generic count features remain poorly tailored to goalkeeper effectiveness even after the invalid
  goal term is removed. The retained source cannot support shot-stopping or goals-conceded claims.
- Correlated numerator pairs remain. Package A documents them but does not claim to solve them.
- Global scaling remains transductive over the declared historical population and position
  sensitive. Package A does not claim it is optimal.
- Conservative-lower-bound minutes can overstate every per-90 rate.
- The frozen W09 suite verifies execution, invariants, explanations and sensitivity; it contains no
  football-relevance labels.
- A semantic correction can create large GK rank changes without establishing that the new order is
  better.
- No package supports recruitment advice, football relevance, future performance, transfer value,
  availability, squad fit, outcomes or current-market coverage.
- W06 remains `NO_GO`; W10 remains `REWORK`; formal collection remains unstarted.

## Explicitly not doing

- no cloud, remote service, deployment, hosted CI, public endpoint, container or new dependency;
- no performance optimisation;
- no live Mahalanobis, PCA, ZCA or covariance-whitened method;
- no position-conditioned scaler promotion;
- no ratio feature, family-weight redesign or small-sample shrinkage;
- no new GK effectiveness feature and no reuse of W10 independent evidence as a retrieval input;
- no combined all-leagues candidate pool;
- no synthetic production population;
- no experiment migration, deletion or re-pin;
- no W10 participant recruitment, collection, 08E, 08F, acceptance, freeze or acceptance tag;
- no threshold movement or re-derivation; and
- no methodological-improvement claim based on ranking churn, stability, speed or attractive names.

## Decision required

Choose one package explicitly:

- **Approve Package A** — 12.0 hours; universal source-semantic correction, complete delivery
  bundle, one tier-2 cascade, and honest experiment incompatibility. **Recommended.**
- **Approve Package B** — 10.0 hours; safer GK interactive default and complete delivery bundle,
  with no artifact re-pin.
- **Approve Package C** — 6.5 hours; delivery hardening only, with no method mitigation.
- **Approve Package D** — 11.0 hours; offline geometry evidence plus documentary readiness, with no
  live method change.
- Request a revised package; Phase 2 remains stopped meanwhile.

Approval of a package authorises only its stated Phase 2 scope. The proposed checkpoint after a
successful implementation and full verification is
`checkpoint/w10-prestudy-uplift-reviewed`; it is explicitly not W10 acceptance.
