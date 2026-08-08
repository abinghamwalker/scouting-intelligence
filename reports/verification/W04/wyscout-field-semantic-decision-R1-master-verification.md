# W04 field-semantic decision R1 — master verification

## Decision

`REWORK` for one P1 progression defect in the permanent contract test. The
119-row semantic decision and registry are otherwise accepted as the frozen
candidate basis for bounded R2 correction.

The defect does not change the approved architecture, project root, dependency
policy, provider/rights decision, storage boundary, or local-only operation.
Review, acceptance, and Bronze remain blocked until R2 passes master and
independent review.

## Complete readback and artifact integrity

The master read the complete producer return, all 1,223 lines of the contract
test, all 1,330 lines of the registry, and independently enumerated every parsed
decision row with its canonical field and complete transform object.

```text
decision JSON:       1 line / 64,375 bytes
decision SHA-256:
e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999

registry YAML:       1,330 lines / 63,963 bytes
registry physical SHA-256:
805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2
registry canonical SHA-256:
fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034

contract test:       1,223 lines / 44,987 bytes
contract-test SHA-256:
f561e9e0fed14a44fe075df92fa31efdbf8bc84603bf5a535f8c9b1e247bb9bc

producer return:     157 lines / 7,053 bytes
producer-return SHA-256:
ce23a3fefddba7da0cf8d1fe32b805cafb84f29529b71ce781eee73430c71932
```

The registry parses to the exact decision rows, policies, and bound inputs. Its
`decision_sha256` equals the canonical/physical decision digest.

## Semantic audit

The candidate contains exactly 119 unique roster rows in normative order with
exact per-kind counts `10/11/26/47/18/4/3`:

```text
TRANSFORM:             27
PRESERVE_UNMAPPED:     53
FORBIDDEN:             39
```

The transform distribution is:

```text
CANONICAL_SOURCE_ID:   14
STRICT_INTEGER:         4
EVENT_TAXONOMY_ID:      3
COPY_EXACT:             1
PARSE_UTC:              1
PERIOD_RELATIVE_SECONDS:1
POSITION_ARRAY:         1
SORTED_TAG_IDS:         1
TAG_TAXONOMY_ID:        1
```

The master checked every mapping against its measured source shape and the R20
claim boundary. Names, display labels, provider roles, current teams, venue,
winner, score, goal, and card fields do not project. Mixed or unsupported
geographic IDs, dates, durations, status, referee/coach data, formation
indicators, and mixed `subEventId` evidence remain unmapped.

The `action.$.playerId` transform correctly uses `zero_policy: REJECT`. R20 makes
zero an invalid player identity and later classifies it as
`PROVIDER_ZERO_ACTOR_REJECTION`; the 226,038 zero actors remain a separate source
reconciliation population rather than disappeared or resolved identities.

## P1 progression defect

`test_future_review_acceptance_and_bronze_outputs_remain_absent` permanently
requires the future review, acceptance, and Bronze paths not to exist.

That is not progression-safe:

1. the exact next review packet must create the review path;
2. that packet cannot edit this test;
3. the test would fail after a correct review;
4. the same contradiction recurs after correct acceptance and authorized Bronze;
5. therefore the focused suite and eventual W04 full suite cannot remain green.

R2 is bounded to the test and its return. It must leave the frozen decision and
registry unchanged and implement a closed authority-state validator: a present
review must be strictly valid; a present acceptance must be backed by a valid
PASS review and unchanged candidate; Bronze/runtime outputs must remain absent
until such an acceptance is valid. This preserves the fail-closed intent while
allowing the mandated sequence to advance.

## Independent checks

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The master then reproduced:

- focused contract tests: `46 passed`;
- Ruff formatting: pass;
- Ruff lint: pass;
- local-only verifier: all 25 checks pass;
- branch: `main`;
- Git remotes: empty;
- future review and acceptance: absent;
- future Bronze/runtime launch/admit/rebuild paths: absent.

The required fresh sync caused metadata-only drift relative to the initial
pre-sync pyc snapshot; all complete pyc content inventories remained unchanged.
The master established a clean post-sync baseline, reran the complete focused
suite, and reproduced this exact terminal inventory:

```text
repository count: 58
repository metadata SHA-256:
37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733
repository content SHA-256:
a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9

site count: 1,086
site metadata SHA-256:
a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8
site content SHA-256:
b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18
```

No provider access, external network activity, cloud resource, hosted CI, public
endpoint, container, deployment, Git remote, or Git mutation was created.
