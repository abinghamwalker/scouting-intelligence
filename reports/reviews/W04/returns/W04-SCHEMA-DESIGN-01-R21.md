# Subagent return

## Task

- task_id: `W04-SCHEMA-DESIGN-01-R21`
- objective: Produce the bounded additive R21 correction that preserves R20/v1
  evidence, closes the acyclic digest/preimage graph, defines strict integer-only
  action subevent semantics, fixes the conservative 15-feature roster, and
  requires cross-authority review and gating without implementing a product.

## Files changed

- `reports/reviews/W04/wyscout-schema-design-R21.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21.md`

## Summary

- Bound the immutable R20 physical SHA-256 and defined an exact six-clause-family
  merge rule that leaves all unrelated R20 architecture authoritative.
- Preserved complete field-v1 and possession-v1 authority records, fixed the
  field-v2 and possession-v2 decision/candidate/review/acceptance IDs and paths,
  and required each v2 acceptance to supersede the exact v1 acceptance.
- Closed `EVENT_SUBEVENT_TAXONOMY_ID_V2`: only strict JSON integers admitted by
  the frozen event/subevent pair taxonomy emit
  `action_subevent_taxonomy_id`; boolean, strings, null, decimals, arrays,
  objects, and unknown integers remain unmapped without coercion. The measured
  7,821 strings retain exact raw rejected-field evidence and reason
  `ACTION_SUBEVENT_STRING_PRESERVED_UNMAPPED`.
- Defined possession-v2 composition using only the four accepted field-v2
  canonical outputs and an exact fail-closed selector; raw/name matching is
  forbidden and missing canonical subevent is ineligible/unmapped.
- Defined both canonical JSON control-preimage IDs, paths, closed top-level/row
  schemas, ordering, canonical rendering, terminal-LF digest rule, and
  no-self-hash/no-feature-hash/no-output constraints.
- Marked all sixteen schema-bundle rows
  `CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA`; they are versioned
  R20 contract-surface descriptors, not implemented product schemas. The typed
  `feature_schema_hash` placeholder remains null until accepted feature
  authority exists.
- Fixed the exact sorted 15-feature roster: four supported, four
  `SUPPRESSED_UNSUPPORTED_DENOMINATOR`, and seven `UNAVAILABLE`, with all eight
  row fields and values closed.
- Mechanically derived and enumerated the exact resource cardinality as
  `17 + 1 + 1 + 2 + 4 + 4 + 1 = 30`. Existing supported-feature artifacts
  remain at retained positions 4 and 14–16 and therefore do not get
  double-counted.
- Defined the corrected five-dependency bindings, fourteen serial packet IDs,
  exhaustive sole path ownership, independent review separation, positive and
  negative `CROSS_AUTHORITY` tests, and the complete repository gate.
- Explicitly ended R21 before any Bronze, Silver, Gold, manifest, receipt,
  serializer, build, runtime, feature materialization, model, product, provider
  acquisition, network, cloud, container, endpoint, hosted CI, or deployment
  implementation.

## Tests run

- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -S -B -c "<packet R21 size and required-token assertions>"`, bracketed by site/repository pyc counts.
  - exit status: `0`
  - result: `PASS`; report size exceeded 20,000 bytes; all required tokens were
    present; site pyc count remained `1086`; repository pyc count remained `59`.
    The first sandboxed attempt was denied read access to the existing uv cache
    and therefore was not treated as a pass; the authoritative rerun used the
    approved existing locked/no-sync environment and explicit failure
    propagation.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`; 25 local-only/one-root-uv checks passed with zero failures,
    including zero Git remotes, active local push guard, one root project/lock/
    venv, Python 3.12.12, no alternate package manager, no hosted CI/deployment,
    no container definition, and no external service dependency.
- command:
  shell-only mechanical count and frozen-digest assertions over the R21 report
  and immutable predecessor/acceptances.
  - exit status: `0`
  - result: `PASS`; exact feature distribution was `15/4/4/7`, resource
    cardinality was `30`, R20 SHA-256 was
    `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`,
    field-v1 acceptance SHA-256 was
    `fd6b9f813c8e810e972ba5d943b2fb4c5fe2fcd7716b4ec9a38ddca3b0439365`,
    and possession-v1 acceptance SHA-256 was
    `f6b2efcb746907886ab97876bf253115a804786e31cae34b25a1eb3771346112`.
- command:
  shell-only terminal full repository/site pyc inventory reconstruction and
  byte comparison with the preflight inventories.
  - exit status: `0`
  - result: `PASS`; repository inventory remained 59 rows with inventory
    SHA-256
    `a339bef860b00a51a9df5bcfa84540cd0ca91c19fd77ab63a80c38f77866745e`;
    site-packages inventory remained 1,086 rows with inventory SHA-256
    `88bf87afd7c14b89ed6cb3fc29c535511beaa771167345efec3d8a13ea512fd3`.

## Artifacts/evidence

- `reports/reviews/W04/wyscout-schema-design-R21.md`
- `reports/reviews/W04/returns/W04-SCHEMA-DESIGN-01-R21.md`
- preflight full-inventory evidence:
  `/tmp/w04_r21_design_producer_repo_pyc.preflight`
- preflight full-inventory evidence:
  `/tmp/w04_r21_design_producer_site_pyc.preflight`

## Risks

- R21 is a producer candidate, not an acceptance. Its fixed R14 independent
  review and master verification are mandatory before any preimage or v2
  authority packet begins.
- Descriptor versions deliberately identify only R20 contract surfaces. A later
  packet must fail if it tries to treat them as implemented Parquet/row schemas
  or uses the null feature-hash placeholder as a concrete hash.
- The accepted 36 possession predicates remain a project-owned conservative
  taxonomy and never become provider-native truth.
- No broader architecture or product blocker was found within this design
  packet. Any later need to invent fields beyond the descriptor-only surface is
  a stop condition, not implied authority.

## Follow-up items

- Dispatch fixed independent review
  `W04-SCHEMA-DESIGN-REVIEW-01-R14`.
- After a passing independent review, the master must independently read back,
  verify, and accept R21 before materializing either control preimage.

## Scope confirmation

- no Git operations: confirmed; the producer performed no Git command or Git
  state mutation. The packet-required local-only verifier internally checked
  local Git safety read-only.
- no unauthorised dependency or lockfile changes: confirmed; used only
  `uv run --locked --no-sync`.
- no edits outside `allowed_paths`: confirmed; only the two packet-owned report
  paths were created or modified.
