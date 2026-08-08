# W03 synthetic evaluation contract

- Contract ID: `w03-synthetic-evaluation-v1`
- Status: Frozen for W03
- Evidence class: Deterministic synthetic foundation evidence only
- Claim permitted by this contract: contract, temporal, storage, authorisation and
  audit seam behaviour
- Claims not permitted: expert relevance, real-data quality, usability, security
  assurance, pilot benefit or model performance

## Purpose

W03 must prove that one local synthetic role-brief-to-audit journey can be reconstructed
through strict boundaries and that unsafe variants fail closed. It does not train,
select or promote a scouting model. No result from this contract may be presented as
evidence that real candidates are relevant or that real users benefit.

## Frozen input classes

The fixture implementation must be deterministic and contain:

- two synthetic competitions with synthetic teams, players and matches;
- a versioned synthetic role brief and expected eligible universe;
- one ambiguous synthetic identity;
- one late-arriving fact;
- one prohibited future fact;
- an attempted storage path escape;
- same-tenant authorised actors and cross-tenant or unauthorised actors;
- confidential synthetic evidence and an unauthorised read/export attempt;
- an expected append-only audit sequence for the successful journey.

All names, identifiers and facts must be generated fixtures. They must not represent,
copy or claim facts about real people, clubs, providers, users or pilots.

## Replay and temporal cutoff

The fixture manifest must declare one fixed UTC `decision_cutoff_ts`. The concrete
timestamp belongs to the fixture packet and must be stable once reviewed; this
governance document does not fabricate one.

For every admitted fact:

1. `observed_at` describes when the event purports to occur.
2. `available_at` describes when the fact could have been known.
3. `feature_cutoff_ts` is the strict upper bound.
4. Admission requires `available_at < decision_cutoff_ts`.
5. A fact observed before the cutoff but available at or after it is ineligible.
6. `generated_at` is execution metadata and never evidence of availability.
7. A missing or unprovable availability time makes the snapshot research-only and
   unavailable to the replay.

Corrections create new versions. They never mutate the replay's prior evidence.
Replaying the same fixture manifest, brief version, policy version and cutoff must
resolve the same eligible evidence and result/audit digests.

## Partitions and protected-fixture rule

Synthetic development fixtures may be reused for contract and implementation work. A
separate protected synthetic fixture must be physically or logically separated from
development inputs and identified by an immutable manifest digest.

- Implementers must not read protected expected outputs while tuning behaviour.
- The master brokers protected-fixture execution against a preregistered candidate
  implementation.
- The protected result and gate decision are retained whether positive or negative.
- Any access before the brokered run invalidates the protected comparison; the fixture
  must be replaced and the event recorded.
- Protected synthetic success proves only the W03 foundation properties listed here.

`FIT`, `TUNE`, `CALIBRATION`, `PROTECTED_TEST` and `PROSPECTIVE` remain distinct
evaluation meanings. W03 uses no real expert labels, calibration partition or
prospective outcome. No W03 fixture may be relabelled as one.

## Required negative cases

| Case | Required response |
| --- | --- |
| Ambiguous identity | Do not merge or score under a guessed canonical identity; quarantine or route to a synthetic review state. |
| Post-cutoff availability | Reject the fact from the historical replay even when its event time is earlier. |
| Missing temporal evidence | Mark research-only and suppress the recommendation. |
| Storage path escape or escaped symlink | Reject before writing; create no outside-root artifact. |
| Unknown role or action | Deny by default. |
| Cross-tenant or object-ownership mismatch | Deny without returning confidential object content. |
| Unauthorised confidential evidence read/export | Deny and emit the required material-action audit attempt without exporting data. |
| Rights classification absent or not `w03_synthetic_generated` | Reject admission. |
| Attempted audit mutation/deletion | Reject; append a new corrective/security event rather than changing history. |
| Missing model/index evidence | Do not silently substitute a model; return a labelled unavailable/fallback state. |

## Acceptance metrics and exact W03 minimum gate

Metrics are computed over the frozen fixture manifest. Counts are requirements, not
reported test results.

| Metric | Minimum |
| --- | --- |
| Post-cutoff facts admitted | exactly `0` |
| Outside-root writes | exactly `0` |
| Unauthorised or cross-tenant actions allowed | exactly `0` |
| Unknown actions allowed | exactly `0` |
| Required negative cases with the specified fail-closed outcome | `100%` |
| Successful material journey actions linked to append-only audit events | `100%` |
| Result fields carrying required brief/data/policy/lineage/cutoff identifiers | `100%` |
| Repeat replays with identical result and audit digests | `100%` of repeated runs |
| Silent model/index substitutions | exactly `0` |

The W03 minimum gate passes only if every row above passes, all strict contracts reject
unknown fields as specified by their contracts, the role-brief-to-audit journey
completes locally, and the master and independent reviewer agree on the boundary
evidence. There is no weighted average, waiver by aggregate score or partial pass.

## Future retrieval metrics, not available in W03

When expert-labelled and governed data later exist, the evaluation protocol must
preregister Precision@5/10/25, Recall@k, NDCG@k, pair preference, coverage,
inter-rater agreement, rank correlation, top-k overlap/churn, split-half reliability,
bootstrap intervals, null controls and time/league/source transfer tests. A challenger
must beat a simple baseline with an interval excluding the preregistered minimum useful
effect or receive `NO-GO`.

No threshold or result for those metrics is asserted here because no expert evaluation
set, provider data, reviewer evidence or protected model run is available in W03.

## Authority trace

- `../scouting-ml-production-blueprint.html`: sections 03–05, 07, 08 (P0.6, P1.8,
  P3.4–P3.7), 09 and decision D1.
- `../scouting-ml-agent-implementation-workflow.html`: sections 02–05, wave W03,
  wave W06 and section 09.

