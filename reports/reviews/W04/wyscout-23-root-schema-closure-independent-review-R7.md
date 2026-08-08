# W04 23-root schema closure independent review R7

- Date: 2026-08-02
- Task: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-REVIEW-01-R7`
- Candidate: `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R7`
- Verdict: **REWORK**
- Findings: **P0 0 / P1 1 / P2 0**

## Fixed bindings

All seven packet-fixed artifacts reproduced before review and immediately before
rendering.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| candidate schema | `8ff15eb36e588806d3768e7a3769d7e5cad9a95ea994f676f5930bc63205d0f4` |
| candidate schema test | `af355c891aa6472e778c2ad104ccd5a593700c9433bedaf3f7e2cc6f82eb8636` |
| producer return | `e156f57547424dc194c3d20e7b7794a03abae7576f4b7fdcce0c0634ba9722f8` |
| frozen R5 acceptance oracle | `a3f15f92a14ff342efd0f5b2848b60eab4898ea79eb69c7fd6f09e6946077efa` |
| accepted formats implementation | `2dfdf3675a47f6c2b53478857de1af27aebecb85def8f0701e6ef86c65fafcc9` |
| accepted formats test | `ba38c5a66f41aee8ef2b998f4622c71ec30f3b8861d7ef07d8540d001b0bee89` |

## Retained exact reconstruction evidence

I independently extracted the UTF-8 JSONL bytes between the R5 markers without
using the candidate or its test as the expected source. The extraction contains 56
rows, 56 unique effective `(owner, validator)` bindings, operations P01-P56 and
SHA-256 `c36ad1932ff075c6a4f35f2ea0cbd69496f4914ae401a1560ed03eb938a1ad8d`.
The normalized candidate ledger is byte-identical for all 56 rows and reproduces
the same digest. Every declared owner agrees with the runtime MRO, including the
inherited bindings, and every direct validator field read is covered by the frozen
operand roster.

The closed C1-C11 resolver contains material values, not unresolved labels.
Independent normalization reproduced the R3 executable comparison values: C2
15-row source map `dbfe3ff7...`; C3 data rows/clocks/build rows
`d1201327...`/`e6149227...`/`af3b07e4...`; C4 119-row registry `f9d72b83...`;
C5 36 pairs `561669e7...`; C6 seven reasons `85241c55...`; C7
`1927b170...`; C8 five rows `27dc516c...` and lineage hash `ded9ae0a...`;
C9 season/lineup `bceaf3eb...`/`256a83de...`; C10 key, component and argv
digests `64498445...`, `affe4790...`, `e76f1e73...`, `ff4326bf...` and
`c5232e36...`; and C11 receipt contracts `ca4e3715...`. E1-E8 remain eight
distinct external predicates.

Independent export reconstruction also reproduced 23 canonical roots in frozen
order, 12 descriptor roots, 11 explicit JSON-only roots, exact earlier-only
dependencies and every producer-listed root-content digest. Descriptor inspection
retains 30 non-coverage `EXACT_DECIMAL128_WITH_EXPONENT` logical paths, each with
the exact ordered `value: decimal128(22,18)`, `exponent: int8`,
`negative_zero: bool` children, while the six reachable coverage paths remain
`CANONICAL_DECIMAL_UTF8`.

## P1-01 — the frozen SilverAction matrix variants are not implemented

The matrix has the required total cardinality 29 and root cardinality vector
`[2,5,7,1,1,1,1,3,2,2,2,2]`, but its three SilverAction rows do not implement
the exact R5 Section 5.6 variants. A fresh dynamic readback produced:

| Observed row | identity/source | nullable IDs | seconds / declared scale | positions | taxonomy |
| --- | --- | --- | --- | ---: | --- |
| first | action ID `f6298526-f978-58fb-890a-cedd787f338f`, source/action ID `5`, ordinal `0` | all competition/player/team/event/subevent non-null | `10` / `0` | 1 | CONTROL `(7,70)` |
| second | same action ID/source/ordinal | competition remains non-null; player/team/event/subevent null | `11` / `0` | 0 | null/unmapped |
| third | same action ID/source/ordinal | all identity/taxonomy fields non-null | `10.123456789012345678` / `18` | 2 | CONTROL `(7,70)` |

The frozen expected states require three distinct action/source identities;
SA-NULL-UNMAPPED with `competition_id`, `player_id`, `team_id`, event and subevent
all null plus `Decimal("0")`/scale 0; a one-position admitted CONTROL row retaining
scale 18; and a two-position admitted RESTART row. Across the admitted rows one
seconds value must exercise the exact capacity boundary
`9999.999999999999999999`. Observed unique action IDs and unique source identities
are both `1`, the boundary is absent, and no two-position RESTART row exists.

The current test asserts only position lengths `(1,0,2)`, scales `(0,0,18)` and
four of the null-state fields, so it passes while omitting these frozen conditions.
This defeats the R5 adversarial matrix evidence even though the candidate schema,
ledger and current test are self-consistent.

Bounded correction: replace only the three test-owned SilverAction matrix fixtures
with three independently strict-validated rows that reproduce every R5 Section 5.6
condition, and add exact assertions for distinct action/source identities, all five
null fields, zero seconds/scale 0, one-position scale 18, two-position RESTART and
the capacity-boundary value. Preserve the runtime contracts, 23 roots, ledger,
projection semantics, logical models, populations and digest formula. Regenerate
derived root bytes only if those test-only corrections mechanically require it.

## Executed checks and boundary

- Fixed-binding `shasum -a 256`: PASS before review and before rendering.
- Read-only independent oracle/candidate/root/resolver reconstruction: PASS for the
  retained evidence above.
- Read-only 29-row matrix probe: PASS cardinality, **FAIL exact SilverAction
  variants** as P1-01 above. The first sandboxed invocation was denied while uv
  inspected its existing cache `.git`; the same command was rerun with read-only
  cache approval and completed.
- Per master direction, the broad focused/adjacent acceptance commands were not
  rerun after the definitive bounded P1 was reproduced; they cannot convert this
  exact-oracle failure into PASS.

No candidate/test edit, Git operation, dependency or lock change, provider/network
action, product write, cloud/container/CI action, publication or deployment
occurred.

Verdict: **REWORK — P0 0 / P1 1 / P2 0**.
