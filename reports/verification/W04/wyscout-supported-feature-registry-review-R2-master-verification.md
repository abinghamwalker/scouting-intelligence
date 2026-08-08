# W04 supported feature registry review R2 — master verification

## Decision

`REWORK`.

The R2 reviewer preserved all producer and archived evidence, held the retained
inventory stable, and correctly found one remaining composability defect.

R2 verifies strict types but does not prove an event/subevent pair is one of the
accepted possession-v2 predicates capable of resolution. A claimed
`ELIGIBLE_RESOLVED` state therefore makes impossible, unknown, or explicitly
`UNMAPPED` pairs applicable. The reviewer reproduced this for `(0,0)`,
`(7,999)`, `(999999,999999)`, and `(9,90)`.

This is a bounded executable-proof defect. It does not contradict or change the
frozen R21 architecture, feature roster, or three declared selector inputs.

## Evidence

```text
review recommendation: REWORK
P0 findings: 0
P1 findings: 0
P2 findings: 1
review physical SHA-256:
31653ac8cc12333b91a82ea81e655a69ad71e7b8e20435e14d101c6b15ae62ac
review record SHA-256:
57439c69bf347b1b38cc49d735795b81e0ba1ae016e961ef2141e05f17095891
review return SHA-256:
cade60ba7f656c9e560f1b6961f3cfe611076776700ef68d4e87532ed06531db
focused contract SHA-256:
2331bf0bdbc25457e29b9e9a72c6667cc4852711ee55bbcc5d63711b005eca03
```

The exact R2 review is preserved before fixed-route reuse at:

```text
reports/reviews/W04/archive/
  wyscout-supported-feature-registry-independent-review-R2-rework-31653ac8.md
```

## Bounded R3

R3 must bind the existing three possession selector fields to the accepted
possession-v2 predicate set and admit only predicates whose exact `decision` is
not `UNMAPPED`. The exact possession taxonomy contains 36 predicates, of which
four are explicitly `UNMAPPED`; R3 must therefore derive and prove the exact 32
resolution-capable pairs from the accepted candidate rather than copy an
unbound list.

`possession_eligibility_state` remains a separate applicability condition and
must not become a fourth feature input. Tags remain possession-selector
evidence consumed when deriving the eligibility state and must not become a
feature input.

R3 must reject:

- strict-integer pairs absent from the accepted candidate;
- the four exact `UNMAPPED` pairs;
- zero and negative pairs;
- the already-covered wrong scalar types and invalid team/state values.

The inventory baseline remains:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

## Gate

Only `W04-FEATURE-REGISTRY-DECISION-01-R3` may start. Feature acceptance,
cross-authority composition, and all product work remain blocked.
