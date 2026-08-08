# W04 supported feature registry review R3 — master verification

## Decision

`REWORK`.

The R3 reviewer correctly distinguished accepted predicate membership from
actual sequence-resolution capability. The focused helper presently admits all
32 non-`UNMAPPED` pairs, but the accepted same-period resolver can assign only
28 of them under some valid context.

Four additional accepted pairs are structurally ineligible:

```text
(2,23) DEAD_BALL / UNASSIGNED
(2,24) NON_CONTROL_ADMIN
(2,26) NON_CONTROL_ADMIN
(5,51) DEAD_BALL / UNASSIGNED
```

Together with the four exact `UNMAPPED` pairs, the correct accepted-candidate
partition is:

```text
potentially resolution-capable: 28
structurally ineligible: 8
```

This is a focused executable-proof correction. No authority or architecture
revision is required.

## Evidence

```text
review recommendation: REWORK
P0 findings: 0
P1 findings: 0
P2 findings: 1
review physical SHA-256:
acb43cec3597debd8feda0387a8c0720a8353bed7420b6b4083c3b3a6df51677
review record SHA-256:
6aae590291c7a30ca4d6d3d7f3c67bd7d2d2e6ed509c1b3be9cf5fa9f552e50a
review return SHA-256:
4f76f05eded8665cab54aa0932204847343cf1ac67cc0ed5888bef890b006e32
R3 focused contract SHA-256:
b1dea886128861eff5d2873c4d1edad8a5b5d5d89ddd6eb2348ac0bb3b95740e
```

The exact review is preserved before fixed-route reuse at:

```text
reports/reviews/W04/archive/
  wyscout-supported-feature-registry-independent-review-R3-rework-acb43cec.md
```

## Bounded R4

R4 must derive structural capability from the accepted predicate's exact
opening/attachment semantics:

- `CONTROL` and `RESTART` can open/continue a deterministic possession;
- `CONTESTED` can attach only through an accepted non-`UNASSIGNED`
  contested-attachment rule;
- `DEAD_BALL` can attach only through
  `PRECEDING_RESOLVED_POSSESSION`;
- `NON_CONTROL_ADMIN`, `UNMAPPED`, and any `UNASSIGNED` attachment are
  structurally ineligible.

The proof must derive the exact 28/8 split from the accepted possession-v2
candidate and directly compose representative sequences with the accepted
same-period resolver. It must not add sequence state, tags, attachments, or any
other hidden feature input.

The retained inventory remains:

```text
pyc files: 1,150
pyc path-list SHA-256:
7953ff36ecd0721d414d637085d0f2331dac35cafc160745e9bf35280f8a4f44
__pycache__ directories: 150
cache path-list SHA-256:
79250878e3cfb60a3b0131857ca7b0dc79878c5165725132223d95e32f7f9fd6
```

## Gate

Only `W04-FEATURE-REGISTRY-DECISION-01-R4` may start. Feature acceptance,
cross-authority composition, and all product work remain blocked.
