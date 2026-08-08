# W04 transformed Wyscout dataset card — local governed proof v1

Status: **accepted local research-only proof; not deployable or publishable**

## Exact lineage

This transformed dataset is derived from Wyscout's *Soccer match event dataset*,
figshare collection v5, under CC BY 4.0. The complete admitted five-league source
snapshot is bound by manifest
`8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`
and completion index
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.

The retained product build is
`b1f1a9135e307b115fd1d00f19dae7951993765ee5ac1fb5d5afeb245fdc7b79`,
with code manifest
`c94e650146a982174820ba694a2dcd1b20dc6648426527213bf2e6de09861c2c`.
Its layer manifests are:

- Bronze: `abdc5d89fdac08638f4877f9a44dceb9356d789741bd93981cce4a9b6825d9c1`;
- Silver: `089673ff01edd7de7b6e5777958d19cbaffaa9f429b042ab4986746d80a7c36a`; and
- Gold: `08de1349a532c3f455d792ee56aafc3d8c587828bc9934dc7f77a58a71c90068`.

The controlling health evidence is
`reports/phase-gates/W04/data-health.json`, SHA-256
`ecbf0e52ec702a42b06a2b0a0528bd1716ee7c2922ab4924e468cca83fd9cfd5`.

## Intended use

The dataset supports a local engineering proof of governed Bronze/Silver/Gold
construction and a narrow research demonstration of four neutral count features.
It may be used for local contract, reconstruction, provenance, temporal-safety,
and future feature-pipeline work within the approved project boundary. It supplies
evidence to authorised people; it does not make recruitment decisions.

It is not suitable for live recruitment, present-day player valuation, automated
selection, deployment, external sharing, public display, commercial redistribution,
cross-provider identity claims, competition-strength adjustment, minutes/per-90
analysis, or claims about women, youth, non-top-five-league, or current populations.

## Population and coverage

The complete governed source population contains 1,826 matches and 3,071,395
actions across five 2017/18 domestic top-flight partitions. All six source coverage
dimensions are exact and complete: `7/7`, `10/10`, `5/5`, `5/5`, `5/5`, and
`4/4`, with overall coverage `1`.

The materialised W04 product is intentionally much smaller. It contains one
authorised English match window and one Gold player-window row. The exact product
population is:

| Product | Rows |
| --- | ---: |
| Bronze known record | 1,768 |
| Bronze rejected field | 3,544 |
| Silver action | 13 |
| Silver lineup stint | 1 |
| Silver possession | 2 |
| Silver player-match fact | 1 |
| Gold player window | 1 |

The Gold row carries 868 source-row references and one contributing player-match
fact. Its six distinct coverage equations are identity `3/3`, lineup `1/1`,
action `2/2`, coordinate `2/2`, possession `2/2`, and temporal `8/8`. Overall
Gold coverage is `1`, but applicability remains `research_only` because the
lineup/minute evidence is right-censored or uncertain. Complete Gold coverage
does not mean complete source population or production fitness.

## Transformations and corrections

The pipeline validates source membership and rights; records known and rejected
field projections in Bronze; applies accepted stable identities; derives strict
Silver action, lineup-stint, possession, and player-match evidence; then produces
a neutral-role Gold window under a closed five-dependency temporal lineage.

The project reconstructs possessions and lineup evidence; these are not native
provider truth and must remain labelled as derived. Unknown, malformed, unresolved,
zero-actor, out-of-range, and unsupported states remain explicit evidence or enter
the accepted quarantine paths. They are not silently repaired, coerced, dropped,
or used to broaden feature eligibility. The health report retains the exact source
anomaly and quarantine counts.

Thirty non-coverage Decimal paths use the lossless ordered
`decimal128(22,18)` value, `int8` exponent, and `bool` signed-zero structure.
Strict inverse reconstruction preserves the original exponent and signed zero.
Six coverage Decimal paths remain canonical UTF-8. Real product readback exactly
reproduced all logical JSON-byte digests.

## Supported and suppressed outputs

The only supported Gold features are four result-independent counts:

- `action_count = 2`;
- `coordinate_known_action_count = 2`;
- `match_count = 1`; and
- `resolved_possession_action_count = 2`.

Rates, per-90 values, exact elapsed minutes, fifth or inferred features, current
form, availability, injury, contract, valuation, role-fit scores, result-aware
features, and competition-strength adjustments are unavailable or suppressed.
The source does not establish an exact period terminal or a safe per-90 denominator.

## Temporal safety

No source record is treated as knowable before the collection release at
`2020-01-28T14:24:27Z`. The accepted product window is
`2017-08-11T00:00:00Z` to `2017-08-12T00:00:00Z`, with feature cutoff
`2026-08-01T00:00:00Z`. Every dependency clock and selected match start must be
strictly before that cutoff. The retained boundary receipts passed
`STRICT_BEFORE_CUTOFF_PASS`.

Unversioned player-master attributes are not admitted as historical match facts.
Acquisition time is operational metadata and is not backdated into historical
availability.

## Runtime and local reproduction evidence

The accepted operational baseline is the pair directed by the terminal closure
steer: accepted runtime R11 plus retained real-root R3. R3 contains two distinct
offline local runs that returned exact `COMPLETE`, exit `0`, and reproduced the
same build, seven products, three layer manifests, semantic digests, and logical
JSON bytes. R11/R12 add the final 30-resource, loaded-subset, executable-admission,
and truthful-completion controls verified by independent review and the 2,618-test
complete repository gate. R3 is not relabelled as an execution of later code.

The governed launch shape is:

```text
UV_OFFLINE=1 uv run --locked --no-sync python -S -B scripts/launch_wyscout_v5.py
```

It is valid only through the accepted closed environment, inherited source
descriptor, empty role prefixes, exact argv, and framed child-result protocol;
calling the text command outside that governed wrapper is expected to fail closed.
The retained successful commands, run IDs, receipts, and byte-level readback are
documented in
`reports/verification/W04/wyscout-real-root-invocation-R3-master-acceptance.md`.
No provider or network access is part of reproduction.

## Bias, limitations, and applicability

The source is historical male senior football from one season and five domestic
top flights. It inherits provider taxonomy, event-observation, operator, coordinate,
and missingness biases. Three coordinate values are outside the declared `0..100`
domain. Possession and lineup reconstruction add project-specific semantic risk.
One match cannot establish general model performance, longitudinal value, fairness,
transferability, or scouting effectiveness.

The Gold proof is right-censored or uncertain and research-only even though its
six coverage ratios equal one. It must not be presented as a representative player
sample or a complete transformation of the 3.07-million-action source.

## Rights and attribution

Attribution:

> Data source: Pappalardo et al., Soccer match event dataset, supplied by Wyscout,
> figshare collection v5, licensed CC BY 4.0.

Change notice: the project validates and normalises source JSON, retains explicit
quarantine evidence, reconstructs lineup stints and possessions, and derives
player-window count aggregates.

CC BY 4.0 permits transformation subject to its terms, but this repository's
stricter authority prohibits export, remote hosting, deployment, public endpoints,
hosted CI, external services, and publication. This card is an implementation
record, not legal advice.

## Deferred hardening

Host-specific `.pyc` presence, cache tags, inode/link counts, empty-directory
metadata, temporary paths, timestamps, and equivalent filesystem assurance are
preserved under `W10-RUNTIME-HOST-STATE-HARDENING-01`. They are not hidden or
waived; under the terminal closure steer they are not W04 blockers absent a
reproducible P0/P1 path affecting executable admission, product correctness,
rights, temporal safety, or truthful completion evidence.
