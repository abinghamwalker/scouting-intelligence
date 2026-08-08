# Subagent return

## Task

- task_id: `W04-FIELD-SEMANTIC-DECISION-01-R1`
- objective: Make and contract-test the complete conservative 119-row Wyscout
  field-semantic decision and registry candidate.

## Files changed

- `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`
- `configs/schema/wyscout-v5-field-registry-v1.yaml`
- `tests/contracts/test_wyscout_field_registry_authority.py`
- `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-DECISION-01-R1.md`

## Summary

- Independently parsed the exact R20 normative roster and the fixed source profile.
  Reproduced all 119 unique `(record_kind,json_path)` pairs in exact roster order,
  with exact per-kind counts `10/11/26/47/18/4/3` and mechanically derived
  source-shape digest
  `991e95a991b03c28c5e49c7a29762decca2810c55a47f114f59dc9b1e059bbfe`.
- Froze 119 explicit conservative decisions:
  - `TRANSFORM`: 27
  - `PRESERVE_UNMAPPED`: 53
  - `FORBIDDEN`: 39
- The 27 closed transforms are:
  - `CANONICAL_SOURCE_ID`: 14
  - `STRICT_INTEGER`: 4
  - `EVENT_TAXONOMY_ID`: 3
  - `COPY_EXACT`: 1
  - `PARSE_UTC`: 1
  - `PERIOD_RELATIVE_SECONDS`: 1
  - `POSITION_ARRAY`: 1
  - `SORTED_TAG_IDS`: 1
  - `TAG_TAXONOMY_ID`: 1
- Kept mixed and unsupported semantics conservative. In particular, the measured
  7,821 string `action.$.subEventId` values, mixed substitution container,
  mixed geographic IDs, raw date/duration/status/side/formation indicators, and
  unsupported referee/coach fields remain `PRESERVE_UNMAPPED`. Current-team,
  provider-role, name/display-label, venue, winner, score, goal, and card
  projections are `FORBIDDEN`.
- Sampled the actual local UTC clock only after the choices were frozen:
  `2026-07-30T14:10:46Z`. The exact master actor is
  `4efe5691-8903-5148-8275-30d2e7e8aed0`.
- Rendered the decision as canonical UTF-8 JSON with exactly one terminal LF.
  Rendered the registry as one deterministic, safe UTF-8 YAML document with no
  aliases, anchors, tags, merge keys, duplicate/non-string keys, timestamps, or
  floats. Its parsed `fields`, `bound_inputs`, and `policies` equal the decision,
  and its `decision_sha256` binds the canonical/physical decision bytes.
- Added an exhaustive contract route covering independent input/shape
  reproduction; schemas, ordering, counts, source support, transforms and
  collisions; canonical JSON/YAML; strict actor/clock/digests; YAML unsafe
  classes; and every premature review/acceptance/dependency/Bronze claim named by
  the packet.
- The exact future field review and acceptance artifacts remain absent. No
  dependency, Bronze, product, runtime-entrypoint, or provider output was created.

## Tests run

- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c
  '<independent R20/profile 119-row and source-shape reproduction helper>'`
  - exit status: 0
  - result: `PASS_PROFILE_ROSTER_119`; 119 rows; counts
    `10/11/26/47/18/4/3`; source-shape digest
    `991e95a991b03c28c5e49c7a29762decca2810c55a47f114f59dc9b1e059bbfe`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: 0
  - result: `46 passed in 2.96s`.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: 0
  - result: `1 file already formatted`.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py`
  - exit status: 0
  - result: `All checks passed!`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: 0
  - result: overall `PASS`; all 25 reported local-only checks passed.
- shell-only complete pyc preflight:
  - exit status: 0
  - result: repository 58 and site 1,086; complete metadata/content inventory
    digests recorded below. A preliminary shell attempt was invalid because a
    zsh-special `path` loop name removed command lookup inside its subshell. It
    ran before Python or artifact writes, produced empty digest rows, mutated
    nothing, and was discarded rather than substituted or cleaned. The corrected
    complete preflight below is the sole baseline.
- identical shell-only complete pyc postflight:
  - exit status: 0
  - result: `PASS_IDENTICAL`; all counts and every complete metadata/content
    inventory digest equal the corrected preflight baseline.

## Artifacts/evidence

- Decision:
  `reports/reviews/W04/authorities/wyscout-field-semantic-decisions-v1.json`
  - bytes: 64,375
  - SHA-256:
    `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999`
- Registry:
  `configs/schema/wyscout-v5-field-registry-v1.yaml`
  - bytes: 63,963
  - physical SHA-256:
    `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2`
  - `decision_sha256`:
    `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999`
- Contract test:
  `tests/contracts/test_wyscout_field_registry_authority.py`
  - SHA-256:
    `f561e9e0fed14a44fe075df92fa31efdbf8bc84603bf5a535f8c9b1e247bb9bc`
- Corrected preflight and identical postflight:
  - repository pyc count: 58
  - repository metadata inventory SHA-256:
    `222dee4c0ccc1006062785ca7578671c37d5617a28d78e5967c3ee6c3bfe70f6`
  - repository content inventory SHA-256:
    `a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9`
  - site pyc count: 1,086
  - site metadata inventory SHA-256:
    `3d5c4aab8f3e7d9241ec18dee42bed4dc5386d118b69cd6725defe68991ca874`
  - site content inventory SHA-256:
    `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18`

## Risks

- These are decision and registry candidates, not an independent review or
  acceptance. Bronze and every downstream dependency remain blocked until the
  separately owned exact review and acceptance artifacts pass.
- `PRESERVE_UNMAPPED` intentionally retains measured evidence without granting a
  semantic claim. A later consumer must not reinterpret those rows without a new
  accepted authority.
- `SORTED_TAG_IDS` is deliberately bound to the repeated integer leaf
  `action.$.tags[].id`; the parent array/object rows remain unmapped and no label
  matching or unknown-tag semantic is inferred.

## Follow-up items

- Dispatch the separately owned
  `W04-FIELD-SEMANTIC-REVIEW-01-R1` packet for independent review.
- Only after a passing review, dispatch the separately owned
  `W04-FIELD-SEMANTIC-ACCEPT-01-R1` packet. Do not begin Bronze before acceptance.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no `.venv` or pyc cleanup, repair, sync, purge, recreation, or mutation:
  confirmed
- no provider, network, cloud, container, endpoint, or deployment action:
  confirmed
- no delegation or self-approval: confirmed
- no review, acceptance, dependency, Bronze, Silver, Gold, possession, identity,
  feature, quality, or runtime-entrypoint artifact created: confirmed
