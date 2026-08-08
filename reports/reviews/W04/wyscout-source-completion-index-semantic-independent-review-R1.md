# W04 source-completion-index R3 semantic independent review R1

Date: 2026-07-31

Disposition: `PASS`

Findings: `P0=0`, `P1=0`, `P2=0`

This is an independent data-semantics, provenance, lineage, and bounded-manifest
review of the exact R3 candidate. It is not producer self-approval and does not
authorize product materialization.

## Fixed candidate gate

All fixed bindings matched before semantic review:

| Binding | Reproduced value |
| --- | --- |
| completion implementation | `22d825631af0d27d1583a79ce4bb8adb10643bb32fe139630871727f814f1415` |
| Wyscout contract implementation | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` |
| completion-index unit test | `5beb37ee5fffadcab1d7355b879fcb65b76816b969c5581a943b1096afd98580` |
| Wyscout contract test | `7ef542d5ed65437683063e2980e08a94b260771405147a860ca5d4541f1c004b` |
| accepted index bytes | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` |
| accepted index size | `644037` bytes |
| R20 authority | `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047` |
| R21 authority | `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020` |

The accepted index parsed as canonical content-addressed JSON, retained the exact
five ordered event members, reconciled each member's indexed count to its frozen
row count, and reconciled `3,652` non-empty match-period rows to `3,071,395`
actions. The member totals were exactly `643150`, `632807`, `519407`, `647372`,
and `628659`.

## Semantic and provenance result

The strict source projection remains closed. Provider event identity is accepted
only as a strict integer. Numeric-string and Boolean event identities fail rather
than coerce. A raw subevent string such as `"10"` emits no canonical subevent and
is retained with reason
`ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`; admitted canonical subevents still
require an exact strict-integer event/subevent pair. Raw tags remain ordered raw
evidence while the possession projection is sorted, unique, and strict-integer.

Equal-clock behavior remains group-first. Opposing CONTROL actions at the same
clock produced no possession regardless of physical order; a possession completed
strictly before an ambiguous clock remained intact; the dependent contested buffer
was not assigned through an ambiguous clock. Possession source rows cover the
complete causal period sequence, and the dedicated other-player regression proved
that causal rows used for resolution remain in Possession, Fact, and Gold
provenance.

The real accepted match path used match `2499719`. Exact comparison covered all
`1,768` source actions in its two indexed periods (`901` and `867`) before a checked
Action, Possession, Fact, or Gold handle could be issued. The resulting selected
Fact and Gold values reconciled exactly:

```text
action_count = 2
coordinate_known_action_count = 0
match_count = 1
resolved_possession_action_count = 2
```

Those are the complete four-field Gold vector. Gold bound completion-index digest
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`,
five canonically ordered dependencies, and recomputed lineage hash
`78e7b59e1b78f619bb6a247efae27f31c7bd0f71f0aa05cd8596e7202e859537`.
Every dependency clock was strictly before cutoff, the temporal proof and row
lineage agreed, Gold fact keys were derived exactly, and Gold source rows equalled
the exact union of selected Fact rows.

The selected player had actions only in the `867`-action causal period, so Gold
correctly carried those `867` action source rows rather than falsely claiming all
`1,768` actions contributed to the feature vector. The opaque checked Gold handle
nevertheless remained bound to the exact two-period, `1,768`-action match
comparison. This is the required distinction between full-population construction
authority and exact causal feature provenance.

All six Gold coverage authorities reconciled in fixed order:

| Dimension | N/D | State |
| --- | ---: | --- |
| identity | `2/2` | `complete` |
| lineup | `1/1` | `complete` |
| action | `2/2` | `complete` |
| coordinate | `0/0` | `not_applicable_zero_denominator` with accepted FIELD authority |
| possession | `2/2` | `complete` |
| temporal | `8/8` | `complete` |

## Exact bounded manifest scope

One checked Gold manifest succeeded with exactly the real match's two completion
periods even though the accepted index contains `3,652` periods. The boundary did
not require or claim global-index materialization. Independent mutations failed as
follows:

| Case | Exact failure |
| --- | --- |
| omitted scope | `checked layer manifests require completion scopes` |
| duplicate capability identity | `layer completion scopes must be unique` |
| overlapping full-match and period scopes | `layer completion scopes cannot overlap one indexed period population` |
| separately issued equal-population substitution | `checked manifest completion scopes must exactly equal product scopes` |
| additional different-match scope | `checked manifest completion scopes must exactly equal product scopes` |
| different-match substitution | `checked manifest completion scopes must exactly equal product scopes` |
| unissued capability | `completion capability was not issued by the accepted reader` |
| raw/unregistered product | `checked product type is not authentic` |
| direct raw manifest model | `checked LayerManifest requires fields, not a direct model value` |

Thus manifest scope is the exact identity union of contributing checked-product
scopes: no omission, extra, duplicate, overlap, stale/reissued substitution, or
cross-match substitution crossed the boundary.

## Executable evidence

- `shasum -a 256 src/scouting/sources/wyscout_completion_index.py src/scouting/contracts/wyscout_data.py tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json reports/reviews/W04/wyscout-schema-design-R20.md reports/reviews/W04/wyscout-schema-design-R21.md`
  - exit `0`; every fixed digest matched.
- `wc -c data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit `0`; `644037` bytes.
- `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py tests/contracts/test_wyscout_data_contracts.py tests/contracts/test_foundation_contracts.py tests/contracts/test_w04_identity_ruleset_authority.py tests/contracts/test_w04_r21_cross_authority_composability.py tests/unit/test_wyscout_source_manifest.py`
  - exit `0`; `495 passed in 81.04s`.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, all `25` controls passed.
- `uv run python -` with the independent no-write semantic/manifest harness
  - exit `0`; reproduced the index/member/period/action reconciliation, real-match
    checked path and values above, strict no-coercion and equal-clock assertions,
    and all six independently enumerated manifest-scope rejection cases.

No provider or network access was used. No dependency, product byte, data byte,
implementation, test, orchestration, verification, cloud, container, hosted CI,
endpoint, remote, deployment, or Git operation was created or changed by this
review.

## Recommendation

`PASS` with `P0=0`, `P1=0`, `P2=0`. The candidate satisfies the packet's semantic,
provenance, lineage, exact-four-feature, and bounded-manifest requirements. Final
acceptance and the complete repository gate remain master-only.
