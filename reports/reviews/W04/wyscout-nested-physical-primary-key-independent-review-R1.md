# W04 nested physical primary-key independent review R1

- Date: 2026-08-02
- Task: `W04-NESTED-PHYSICAL-PRIMARY-KEY-REVIEW-01-R1`
- Candidate: `W04-NESTED-PHYSICAL-PRIMARY-KEY-01-R1`
- Verdict: **PASS**
- Findings: **P0 0 / P1 0 / P2 0**

## Fixed bindings

All seven packet-fixed artifacts matched before review and again after the
candidate-facing probes and acceptance suite.

| Artifact | Required and observed SHA-256 |
| --- | --- |
| schema runtime | `b76ff6d55f841594a337929c382137d27d841b37e49f0f40c1961b9af743bb54` |
| storage formats | `d5e6690f4b2467baeb364e2f8339b2b091f18bc01f8e18a96e8d770da66af9b6` |
| schema tests | `e6d14e9fb8787990716796b1e9031013a7386fae4d7637ccc77b28d746bb9817` |
| formats tests | `8fe2d3b587541ee4fd80c6e5604e788b48ef78ba4bdc608a9245b64b30afd345` |
| producer return | `287faf0eec55582e16d5e3354304e82f62e1ec3d337c41a6b0af2eefc23a7c91` |
| product-contract v2 physical bytes | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |
| schema-bundle v2 physical bytes | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |

No producer implementation, test, aggregate, dependency or lock bytes were
changed by this review.

## Independently re-derived physical-key roster

The logical model keys, accepted descriptors and exported physical-path roster
reconcile exactly and in the same order:

| Serialized role | Exact physical primary-key paths |
| --- | --- |
| `BRONZE_KNOWN_RECORD` | `source_row.source_manifest_id`, `source_row.completion_relative_path`, `source_row.source_record_ordinal` |
| `BRONZE_REJECTED_RECORD` | `source_row.source_manifest_id`, `source_row.completion_relative_path`, `source_row.source_record_ordinal` |
| `BRONZE_REJECTED_FIELD` | `source_row.source_manifest_id`, `source_row.completion_relative_path`, `source_row.source_record_ordinal`, `json_path` |
| `SILVER_COMPETITION` | `competition_id` |
| `SILVER_TEAM` | `team_id` |
| `SILVER_PLAYER` | `player_id` |
| `SILVER_MATCH` | `match_id` |
| `SILVER_ACTION` | `action_id` |
| `SILVER_LINEUP_STINT` | `lineup_stint_id` |
| `SILVER_POSSESSION` | `possession_id` |
| `SILVER_PLAYER_MATCH_FACT` | `tenant_context.tenant_id`, `source_manifest_id`, `match_id`, `player_id`, `player_match_fact_schema_version` |
| `GOLD_PLAYER_WINDOW` | `tenant_context.tenant_id`, `player_id`, `competition_id`, `season_id`, `role_context_id`, `role_context_version`, `window_definition_id`, `window_start_utc`, `window_end_utc`, `feature_cutoff_ts`, `dependency_lineage_hash` |

The roster owns exactly the first twelve W04 roots. Unsupported or non-serialized
roles fail closed. Import-time validation requires nonempty unique canonical path
segments, non-null fields at every hop, descent only through fixed named
`OBJECT_STRUCT` children, and a terminal `IDENTITY` scalar in the accepted
integer/UTF-8/timestamp projection roster.

The complete Bronze source-row identity is retained. In particular, two rejected
field rows for the same source row cannot be uniquely ordered without the terminal
`json_path`; the focused population proof accepts the complete four-field key and
rejects the truncated duplicate key.

## Encoder and adversarial review

The encoder parses only an exact nonempty tuple of canonical dotted strings and
rejects empty segments and duplicate paths. Each path is independently resolved
against both the descriptor and its generated Arrow schema. The same path is then
resolved in the inverse-projected canonical logical row. Equality with the
supplied key requires both exact runtime type identity and exact value equality;
no top-level alias, callback, fallback, inference or coercion path exists.

The existing key boundary remains intact: per-row arity, per-position type
homogeneity, uniqueness, canonical tuple ordering and exact row/key alignment are
checked before semantic hashing or Parquet writing.

A fresh synthetic reviewer probe produced two valid nested/timestamp encodes and
26 fail-closed cases covering:

- empty/non-tuple input, leading/trailing/double dots, malformed names, index and
  wildcard syntax, non-string input and duplicate paths;
- missing fields, nested-to-top-level alias fallback, nullable containers and
  leaves, list descent, positional-struct descent and non-scalar terminals;
- Boolean and null terminals, projected key value and type drift, duplicate keys,
  and row/key reordering;
- raw timestamp keys, drifted canonical timestamp strings and Arrow timestamp
  type drift.

The full frozen test suite independently retains the repeated rejected-field
ordering proof and direct Fact/Gold nested-tenant encodes. A fresh call through
the public product encoder round-tripped one strict `SILVER_PLAYER_MATCH_FACT`
fixture and one strict `GOLD_PLAYER_WINDOW` fixture. Their observed review vectors
were:

| Role | Physical SHA-256 | Semantic SHA-256 |
| --- | --- | --- |
| `SILVER_PLAYER_MATCH_FACT` | `a3c43a3dcf2ec41b6748016e21eebca5d6bdd1fbfc3314b11843c598819e77fa` | `fa80563c71368309b248d706096e9d2b2fe5751e88f399a863d8db042f544848` |
| `GOLD_PLAYER_WINDOW` | `67f34a15bfa58c6269dd094c97b4ffe0b2e8c3005f5cfab67aa10507cd388cbe` | `f44d30dd24bafe2954e490e1141d8652650e963ed421cb71339dcc94d6be7759` |

Both reopened as exactly one row.

## Gold timestamp reconciliation

`window_start_utc`, `window_end_utc` and `feature_cutoff_ts` remain physical
`timestamp[us, tz=UTC]` fields in the accepted Gold Arrow schema. The unchanged
inverse identity projection returns canonical UTC text, including exact
microseconds when present, before primary-key comparison. A canonical string key
passes; a raw `datetime`, a drifted string or an Arrow UTF-8 substitution fails.
This preserves the accepted logical labels, physical fields and digest meanings.

## Aggregate reproduction

Freshly built aggregate objects were physically byte-identical to both checked-in
preimages:

| Aggregate | Logical digest | Physical bytes | Physical SHA-256 |
| --- | --- | ---: | --- |
| schema bundle v2 | `ba5db90f2b130af450fba609520984f6e07c255be4fbddc3f933f94149ef63be` | 12295 | `8426726dd9a21da81b37e34860d9b38949b7c15243eecbee5d7df85a788b0d45` |
| product contract v2 | `fe68e8f31b7dd6f6fb9e8eb3a025de3e78d8825eabeeeea72327481101489fc0` | 6386 | `7034fa9d88b11eccc84ee37dfaa722b1a130a97a1a34cecafbe549bd6974e1af` |

`scripts/materialize_wyscout_v5_contracts.py --check` also reproduced both
logical digests and returned PASS. No aggregate was written.

## Executed checks and boundary

All commands used `PYTHONDONTWRITEBYTECODE=1`, isolated
`UV_CACHE_DIR=/tmp/w04-nested-pk-review.TyzpyT`, `UV_LOCKED=1`,
`UV_NO_SYNC=1`, and `uv run --locked --no-sync`.

- Ruff format check: PASS, four files already formatted.
- Ruff lint: PASS, all checks passed.
- Mypy: PASS, no issues in four source files.
- Pytest with `-p no:cacheprovider`: PASS, `360 passed in 57.45s`.
- Bandit: PASS, no findings.
- Import-linter: PASS, 39 files and 74 dependencies; `3 kept, 0 broken`.
- Local-only verifier: PASS, all 25 checks and zero failures.
- Independent roster, public Fact/Gold encode/readback, Gold timestamp and
  aggregate-byte probe: PASS.
- Independent 26-case adversarial path/key probe: PASS.

No Git operation, provider/network action, credential access, dependency change,
product publication, deployment, container/cloud action or producer-owned write
occurred.

Verdict: **PASS — P0 0 / P1 0 / P2 0**.
