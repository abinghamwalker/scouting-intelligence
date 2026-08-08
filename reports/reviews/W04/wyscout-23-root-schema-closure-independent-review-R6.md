# W04 23-root schema closure independent review R6

- Date: 2026-08-02
- Task: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R6`
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R6`
- Verdict: **REWORK**
- Findings: **P0 0 / P1 1 / P2 0**

## Fixed bindings

All seven packet-fixed artifacts reproduced before review and immediately before
rendering.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| candidate schema | `bbef5823bf1635d08362a3ee0a0876e2ac1ec04c2c502d4e67c61a4350ee7a71` |
| candidate schema test | `dd8d66a1831ff7dfbd4a90c745607572a8c00358af4770d85e3e7ca115f3e500` |
| producer return | `e62b644ded21677e22fda2d389f12256e95a84fb9ad04dd3a456f51493efa796` |
| accepted formats implementation | `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9` |
| accepted formats test | `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89` |
| frozen R5 acceptance oracle | `a3f15f92a14ff342efd0f5b2848b60eab4898ea79eb69c7fd6f09e6946077efa` |
| frozen R5 oracle return | `b09297fb45eb7a16f431959f7e7840b8ae930902928094079fd7e26b1ba79116` |

## P1-01 — candidate and test ledger drift from the frozen oracle

I independently extracted the UTF-8 JSONL bytes between the frozen oracle markers,
including one LF after each row. The extraction contains 56 rows, 56 unique
`(owner, validator)` keys, and reproduces the frozen ledger SHA-256
`c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.

I then collected the unique runtime predicates from all 23 candidate exports and
loaded the test-owned `EXPECTED_RUNTIME_BINDING_LEDGER`. The complete comparison is:

| Comparison | Exact | Drift |
| --- | ---: | ---: |
| owner/validator binding roster | 56/56 | 0/56 |
| oracle `operation` | 0/56 | 56/56 |
| oracle ordered `operands` | 10/56 | 46/56 |
| oracle material-constant ledger | 0/56 | 56/56 |
| candidate export versus test-owned expectation | 56/56 | 0/56 |
| complete oracle rows | 0/56 | 56/56 |

The ten operand-exact rows are P02, P03, P06, P08, P10, P11, P15, P27, P46 and
P51. Every other oracle row has a different ordered operand sequence. Every
candidate operation uses a candidate-specific semantic label rather than its
frozen P01-P56 oracle operation ID. Every candidate constants value is a
candidate-specific dictionary, frozen by the test through its ordered key roster
and candidate-derived content hash, rather than the oracle row's ordered C1-C11 and
literal-constant ledger.

This is not a missing-binding defect: all 56 owners and validators are present. It
is an oracle-adoption defect. The candidate and test are exactly self-consistent,
but the test-owned expectations reproduce the candidate's alternate ledger instead
of the independently frozen oracle. A green test therefore cannot establish the
packet-required exact oracle operation, operand and material-constant ledger.

Bounded correction: mechanically reconcile all 56 `_VALIDATOR_SEMANTICS` records
and all 56 test-owned expectations to the frozen P01-P56 JSONL ledger, preserving
the exact owner/validator roster. Require a comparison whose expected values are
independent of candidate exports and whose canonical normalized ledger reproduces
`c36ad1932...`. Regenerate the derived 23 root bytes/digests after this correction;
do not alter validators, logical models, roots, features, populations, digest
meaning, projection semantics or external E1-E8 authority.

## Focused retained evidence

`uv run pytest -q tests/contracts/test_w04_wyscout_schema_closure.py` passed with
`36 passed in 10.98s`. Within the requested focused boundary, this retained the
R6 reversible Decimal projection vectors and census, the exact 29-row matrix and
its Bronze/SilverAction properties, and the 23 root-content/digest checks. No
separate obvious Decimal, 29-row or root-digest blocker was observed. These passes
do not override P1-01 because the ledger test asserts the same drifted candidate
expectations.

No 591-test suite rerun, implementation edit, Git operation, dependency/lock
change, provider/network action, product write, cloud/container/CI action,
publication or deployment occurred.

Verdict: **REWORK — P0 0 / P1 1 / P2 0**.
