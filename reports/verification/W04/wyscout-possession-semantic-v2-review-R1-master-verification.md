# W04 possession semantic v2 independent review R1 — master verification

## Decision

`REWORK`. The master accepts the independent review's sole P1 finding,
`SEQUENCE_RESOLUTION_OVERCLAIM`, and returns the decision, candidate, and
focused contract for bounded R2 correction.

No architecture revision is required. The defect is within the v2 declarative
sequence policy and its focused executable evidence.

## Reproduced finding

The fixed review is canonical and recommends `REWORK` with one P1 finding:

```text
review physical SHA-256:
71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a
canonical review-record SHA-256:
9d42535376164183079ab642f51a43b35bda33e660627ebcce98e166787bd111
return physical SHA-256:
fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90
```

The master invoked the focused helper on isolated accepted `CONTESTED`,
`DEAD_BALL`, `NON_CONTROL_ADMIN`, and `CONTROL` predicates. Every one returned
`possession_eligibility_state=ELIGIBLE_RESOLVED` immediately after exact
predicate lookup.

That contradicts the R21 meaning of `ELIGIBLE_RESOLVED`: an exact accepted
predicate must participate in a deterministically resolved same-period
possession under R20's ordered sequence rules. Contested buffering, dead-ball
attachment, administration, equal-clock uncertainty, missing teams, and
period closure cannot be resolved from a single predicate lookup.

The green 321-test result therefore demonstrates progression-safe validation of
the current bytes but not semantic completeness.

## Preserved evidence

Before future correction of the fixed review path, the master retained the
exact R1 review and return bytes at:

```text
/private/tmp/W04-POSSESSION-SEMANTIC-V2-REVIEW-01-R1-failed/
```

The retained files reproduce the three digests above. The tracked R1 review,
return, master decision, and this report remain the durable audit narrative.

## Bounded correction

R2 must preserve the exact five inputs, 17-key predecessor, and all 36 v1
predicate rows. It must separate strict four-field predicate selection from
same-period sequence resolution and make the final eligibility state depend on
deterministic assignment.

The corrected authority and tests must cover the exact R20 action order;
control/restart open and transition behavior; dead-ball attachment; contested
buffering and period-boundary unassignment; non-control administration;
cross-team equal-clock uncertainty; missing team; period closure; and no
cross-period state.

Only actions assigned to exactly one deterministic resolved possession may emit
`ELIGIBLE_RESOLVED`. Every other action emits
`INELIGIBLE_UNMAPPED`. Predicate lookup by itself emits no final eligibility
claim.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R2` may start. Possession
acceptance and every later authority/product path remain blocked.
