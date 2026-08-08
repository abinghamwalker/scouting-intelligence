# W09 Package A methodological evaluation

## Decision

Package A passed its preregistered semantic and delivery guardrails. The shipped change is a
source-semantic repair: `goals_per90` now admits tag-101, non-own-goal actions only when the event
is not event 9. This removes retained save-attempt forms from a generic goals numerator while
retaining all 4,695 legitimate goal actions supported by the existing source fields.

This is not evidence that the rankings are more football-relevant. It does not authorise a
recruitment, outcome, goalkeeper-quality or W10 acceptance claim.

## Frozen evaluation authority

- Preregistered configuration: `configs/evaluation/w09-semantic-uplift-evaluation-v1.json`
- Configuration digest: `6340ec28d24150b3fe16174fb01c07c383119331f622fe6b9fad3582eb602fb6`
- Immutable baseline: `reports/verification/W09/uplift-semantic-baseline-v1.json`
- Baseline evaluation digest: `8f9f7ebde22029912483a9ea54e5f9d127d713419a5fe5c9f46e08d78e755429`
- Baseline file SHA-256: `3dcf5b2df54e8400b2d6d42a504e0ff63b0850a30919cb1f191539ada4da4ce4`
- Immutable post-uplift result: `reports/verification/W09/uplift-semantic-post-v1.json`
- Post-uplift evaluation digest: `4bf40416d1474188c801b9d122a3c8a7000da19ba40aa00f4c886b67c4d0d880`
- Post-uplift file SHA-256: `856b6dc94af8ee0709919cfe9e8e200c846f124425d5c506dfe88dffb6f9771a`
- Cases: 12 exact query cases across five representative scenarios, both methods and two
  preregistered Kanté weight profiles.

The production post-uplift evaluation was repeated to
`/private/tmp/w09-semantic-post-production-repro.json`; the files were byte-identical.

## Source-semantic reconciliation

| Check | Before | After | Result |
|---|---:|---:|---|
| Generic goal numerator | 9,436 | 4,695 | Pass |
| Event-9 rows in goal numerator | 4,741 | 0 | Pass |
| Legitimate non-event-9 goal actions | — | 4,695 | Pass |
| Event-10-only negative control | — | 4,177 | Rejected |
| Non-event-10 set-piece goal evidence retained | — | 518 | Pass |

The event-10-only alternative was rejected because it would discard 518 supported set-piece goal
actions. The repaired 4,695 total is distributed as DF 532, FW 2,656, GK 1 and MD 1,506.

## Preregistered criteria

| Criterion | Evidence | Result |
|---|---|---|
| Canonical authority unchanged | Dataset `2d018…bee6e`; build `010526…264b43` before and after | Pass |
| Population and eligibility unchanged | 1,975 rows, 1,965 players; catalogue, population and eligibility ledgers byte-identical | Pass |
| Non-goal feature values unchanged | Zero logical differences across all 15 other features | Pass |
| Candidate populations unchanged | All 12 cases retained the exact filter/scoring accounting | Pass |
| Non-GK top-10 churn guard | Every non-GK case retained 9/10 or 10/10; required minimum 8/10 | Pass |
| Explanation reconstruction | Existing exact Euclidean and cosine checks pass under the new authority | Pass |
| Canonical/scorer code unchanged | Canonical build and scorer digest unchanged | Pass |
| W10 threshold movement prohibited | Threshold projection SHA-256 remained `b916567a…983c`; full threshold-policy projection remained `a4e2d6d…fb23` | Pass |
| Positive football-relevance claim prohibited | No protected response or future W10 label used | Pass |

The overall `preregistered_criteria_passed` field is `true`.

## Goalkeeper diagnosis

Before the repair, the median `goals_per90` squared-distance share among Sirigu's Euclidean top ten
was 68.84%. After repair it is 0% for all ten because the retained goal numerator for those
goalkeepers no longer contains event-9 save attempts. The goalkeeper top-ten overlap is 5/10 for
both methods. That larger change was expected and deliberately had no arbitrary overlap threshold:
the repaired feature no longer encodes the observed contaminant.

This does not make the generic 16-feature profile suitable for goalkeeper evaluation. The source
still does not support shot-stopping, goals-conceded, saves, save quality or goalkeeper
effectiveness claims.

## Clean-root reproducibility

Two independently built temporary matrices were byte-identical and produced matrix version
`w09-historical-player-window-v1-a9f7cc2d5fc12ea0` and semantic matrix digest
`20752d615978eb908a313dff346bff258a255602dff639c520e3dc45cb29bb42`. Two independently built
temporary indices were also byte-identical. Their scorer digest remained
`535e244720b7abd46ac25e7de6f3ac387247d4213a00b4857e08acc19e19fc1c`.

The preregistered post-uplift evaluation was reproduced against both clean temporary authorities;
the result bytes matched and the temporary evaluation digest was
`7e7c956e4a38b1ab421aba1920c20549f335a45295ec4562604a071d0b404f35`.
Temporary manifest identities differ from production where their guarded logical paths are part
of the manifest projection; semantic matrix content and the two same-root reproductions match.

## Weight and method reporting

Kanté's post-uplift defensive reweighting retains 8/10 Euclidean results, introducing N. Matić
and E. Dier, and 9/10 cosine results, introducing Ander Herrera. This is sensitivity evidence,
not a relevance judgment. Euclidean and cosine distances retain different arithmetic and scales;
neither is a percentage, probability or calibrated match score.

## Residual risks and non-claims

- Parent/numerator feature pairs remain correlated and can duplicate activity volume.
- Scaling remains global rather than position-conditioned.
- No covariance correction, ratio redesign or small-sample shrinkage was shipped.
- All governed minutes remain conservative lower bounds.
- The four broad positions are not tactical roles.
- No all-leagues combined candidate pool was added.
- W06 remains `NO_GO`; W10 remains `REWORK`; G-RW4 remains `INSUFFICIENT_EVIDENCE`.
- Formal W10 evidence collection, 08E, 08F, acceptance, freeze and acceptance tagging remain
  unstarted.
