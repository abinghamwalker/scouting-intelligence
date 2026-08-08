# W04 field semantic v2 decision R2 — master verification

## Decision

`ACCEPT FOR FRESH INDEPENDENT REVIEW`. This is not field-v2 acceptance and
does not release possession, feature, cross-authority, or product work.

## Complete readback

The master read the complete canonical decision, all 1,365 registry lines, all
2,149 focused-test lines, and all 66 return lines.

```text
decision
bytes: 66640
lines: 1
physical/canonical SHA-256:
cd4d51c0d7c365b73b0c23997716eb7755797889dca1fc545772263dc9924736

registry
bytes: 66221
lines: 1365
physical SHA-256:
15023556072f90b1e956277f255dc4a1df0bea78a5dcbb14b4863346ff9b5193
canonical parsed-value SHA-256:
93bc4592b9a5ee5eccdf7f4fbddec9e8bd3ac3dd9f597df278c108356cdc6959

focused test
bytes: 80297
lines: 2149
SHA-256:
12a93afb72019f36e2c775a8e2898029fac8a26466e57114430edcc39e575d2f

return
bytes: 4148
lines: 66
SHA-256:
3a7fda18111299e2b3b071efafb3921b50869296881820f65c62cdb55e445c83
```

## Independent master reconstruction

The master independently parsed and reconstructed:

- strict canonical decision JSON with exactly one terminal LF;
- strict deterministic YAML and its distinct physical/canonical hashes;
- ten exact bound inputs, including both sibling preimages and R20/R21;
- the immutable seventeen-key field-v1 prior-authority object;
- 119 unique rows in source-profile order and per-kind counts
  `10/11/26/47/18/4/3`;
- semantic equality with v1 at 118 rows and the sole difference at index 106,
  `(action, $.subEventId)`;
- exact `EVENT_SUBEVENT_TAXONOMY_ID_V2` transform and measured
  `integer:3063574, string:7821` evidence;
- 36 exact frozen integer taxonomy pairs;
- strict exclusion of bool, strings, null, noninteger numbers, arrays, objects,
  absent canonical events, and unknown integer pairs;
- raw typed evidence preservation and all seven exact reason codes;
- fail-closed future review/acceptance validation and exact v1 supersession;
  and
- absence of field review/acceptance and all later/product paths.

The five field-v1 artifacts remain byte-identical at their accepted hashes.

## Verification

A fresh `uv sync --locked --all-groups` resolved 83 packages and audited 82.
The combined v2/v1 suite passes `271 passed in 37.05s`; focused Ruff format and
lint pass; and all 25 local-only checks pass.

Producer preflight and terminal inventories are byte-identical:

```text
pycs: 1,145
__pycache__ directories: 150
records plus header: 1,296
SHA-256:
fa317c8a32e8ec7df9b0b4a76b73829fb5c8533fbc7141b09738c39fd617796f
```

The master independently regenerated the established complete inventory after
its checks and matched the retained baseline:

```text
records plus header: 1,296
SHA-256:
b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777
```

The differing inventory digests reflect different retained serialization
schemas; each covers the same 1,145 files and 150 directories and is internally
byte-stable.

R1's two known accidental drafts remain hash-preserved in temporary quarantine.
Their confirmed-empty parent-workspace directory chains remain absent. No
unrelated user work, Git remote, dependency/lock state, provider data, network,
cloud, container, endpoint, hosted CI, deployment, review, acceptance,
possession, feature, Bronze, Silver, Gold, manifest, receipt, build, runtime,
model, or product implementation changed.

## Gate

The producer result may proceed only to
`W04-FIELD-SEMANTIC-V2-REVIEW-01-R1`.
