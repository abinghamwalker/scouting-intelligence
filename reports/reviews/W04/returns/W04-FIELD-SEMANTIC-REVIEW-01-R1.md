# Subagent return

## Task

- task_id: `W04-FIELD-SEMANTIC-REVIEW-01-R1`
- objective: Independently audit the frozen W04 field-semantic decision,
  registry, and progression-safe contract, then create only the exact R20
  independent review record and this return.
- outcome: `PASS`
- findings: none (`P0=0`, `P1=0`, `P2=0`)

## Files changed

- `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
- `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R1.md`

## Summary

- Independently parsed the R20 normative roster, frozen source profile, decision
  JSON, canonical registry YAML, four bound inputs, and progression validator
  rather than relying on the producer's conclusion.
- Proved exact ordered coverage of 119 field rows with record-kind counts
  `10/11/26/47/18/4/3` for
  `competition/team/player/match/action/event-taxonomy/tag-taxonomy`.
- Proved decision counts of `27 TRANSFORM`, `53 PRESERVE_UNMAPPED`, and
  `39 FORBIDDEN`.
- Proved transform coverage of `14 CANONICAL_SOURCE_ID`, `4 STRICT_INTEGER`,
  `3 EVENT_TAXONOMY_ID`, and one each of `COPY_EXACT`, `PARSE_UTC`,
  `PERIOD_RELATIVE_SECONDS`, `POSITION_ARRAY`, `SORTED_TAG_IDS`, and
  `TAG_TAXONOMY_ID`.
- Reproduced every source shape/support claim, exact registry restatement,
  canonical JSON/YAML constraints, bound-input digest, ActorId, clock, and
  physical/canonical candidate digest. There were zero canonical-field
  collisions and zero unsafe projections.
- Audited all forbidden claims: 14 name fields, 2 current-team fields, 4 role
  fields, 13 outcome/score fields, and 6 taxonomy-label fields. No forbidden
  inference is admitted.
- Confirmed the intentionally mixed `subEventId` remains unmapped, source ID zero
  is rejected rather than treated as missing, coordinate anomalies are preserved
  but made ineligible, and duplicate source tag evidence is preserved while the
  canonical ID list is sorted and deduplicated.
- Independently checked taxonomy evidence: event taxonomy has 36 rows, 10 event
  IDs, 36 unique `(eventId,subEventId)` pairs, and 36 subevent IDs; tag taxonomy
  has 59 rows and 59 distinct tag IDs.
- Independently exercised the progression validator. It accepted three valid
  states: decision-only, exact PASS review, and later exact acceptance with
  downstream state. It rejected all 15 invalid/mutated states: missing review
  with acceptance; non-PASS acceptance; malformed review; candidate digest
  drift; self-review; wrong reviewer actor; review clock before the decision;
  wrong/second review fence; downstream before acceptance; acceptance review
  digest drift; reviewer self-acceptance; acceptance clock inversion; candidate
  change after review; and a coherent candidate rewrite blocked by the frozen
  digest gate. It also rejected downstream state without fully valid acceptance.
- Sampled the actual UTC clock only after the independent audit was complete.
  The review uses `reviewed_at=2026-07-30T15:18:11Z`, exact reviewer ActorId
  `03a65770-02f6-5eb0-9bd2-e2ebb44b62bd`, an empty finding list, and
  recommendation `PASS`.
- The review contains explanatory prose outside exactly one
  `w04-authority-review-v1` fenced block. Its body is exactly one strict,
  canonical JSON record followed by one LF.

## Tests run

- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py`
  (initial sandboxed pre-write attempt)
  - exit status: `2`
  - result: the launcher could not read
    `/Users/adrian/.cache/uv/sdists-v9/.git`; Python and pytest did not launch.
    This was an execution-sandbox access failure, not a contract failure.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py`
  (initial sandboxed pre-write attempt)
  - exit status: `2`
  - result: the same uv-cache read denial occurred before Ruff launched.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py`
  (initial sandboxed pre-write attempt)
  - exit status: `2`
  - result: the same uv-cache read denial occurred before Ruff launched.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  (initial sandboxed pre-write attempt)
  - exit status: `2`
  - result: the same uv-cache read denial occurred before Python launched.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py`
  (read-only uv-cache access, pre-write)
  - exit status: `0`
  - result: `123 passed in 17.07s`.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py`
  (read-only uv-cache access, pre-write)
  - exit status: `0`
  - result: `1 file already formatted`.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py`
  (read-only uv-cache access, pre-write)
  - exit status: `0`
  - result: `All checks passed!`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  (read-only uv-cache access, pre-write)
  - exit status: `0`
  - result: `PASS (25/25 checks)`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent 119-row semantic audit>'`
  - exit status: `1` on the first reviewer-helper attempt.
  - result: the helper incorrectly assumed the profile presentation order was
    roster order; the profile presents CSV sections before JSON sections. This
    was a reviewer-helper defect, not a candidate finding.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<corrected independent 119-row semantic audit>'`
  - exit status: `0`
  - result: exact 119-row coverage/counts, transform/forbidden semantics,
    source support, registry equality, and all frozen digests passed.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<independent progression mutation audit>'`
  - exit status: `1` on the first reviewer-helper attempt.
  - result: assigning into the dictionary returned by `runpy` did not patch the
    validator function's globals. This was a reviewer-helper instrumentation
    defect, not a validator finding.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<corrected independent progression mutation audit>'`
  - exit status: `0`
  - result:
    `PROGRESSION_VALIDATOR_AUDIT_PASS mutations=15 valid_states=3 downstream_paths=13`.
- command: shell-only `awk` uniqueness/count audit over
  `data/source/wyscout/v5/objects/eventid2name.csv` and
  `data/source/wyscout/v5/objects/tags2name.csv`
  - exit status: `0`
  - result: event `rows=36,event_ids=10,pairs=36,subevent_ids=36`; tags
    `rows=59,distinct_tag_ids=59`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 python3 -S -B -c '<inventory classification audit over shell-generated TSVs>'`
  - exit status: `0`
  - result: all 1,086 site and 58 repository pycs were classified; zero unsafe
    or unclassified entries.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py`
  (post-review)
  - exit status: `0`
  - result: `123 passed in 17.52s`; the newly present review validated and
    absent acceptance/downstream state remained blocked.
- command:
  `uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py`
  (post-review)
  - exit status: `0`
  - result: `1 file already formatted`.
- command:
  `uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py`
  (post-review)
  - exit status: `0`
  - result: `All checks passed!`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py`
  (post-review)
  - exit status: `0`
  - result: `PASS (25/25 checks)`.
- command:
  `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c '<strict review and canonical digest verifier>'`
  - exit status: `0`
  - result: exact fence/key/canonical-body/reviewer/recommendation checks passed;
    decision and candidate canonical digests reproduced.
- command: terminal shell-only complete pyc inventory reproduction and
  `cmp` of pre/post complete, metadata, and content TSVs for both roots
  - exit status: `0`
  - result: all six comparisons were byte-for-byte identical.

## Artifacts/evidence

- review:
  `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
- return:
  `reports/reviews/W04/returns/W04-FIELD-SEMANTIC-REVIEW-01-R1.md`
- review record SHA-256:
  `8beb747f71f43586c4a57125fae405e90db8af2bd8b6b408346b38b64d7e7fa0`
- complete physical review SHA-256:
  `e2e983c99ed06eb2043c1f3f9a4eac8e4f4c6d69da97fe55bfc9a27745ade861`
- complete physical review size/count: `1299 bytes`, `14 lines`
- frozen decision before and after:
  - physical:
    `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999`
  - canonical:
    `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999`
- frozen registry candidate before and after:
  - physical:
    `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2`
  - canonical:
    `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034`
- frozen contract test before and after, physical:
  `d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3`
- bound input digests reproduced:
  - completion manifest:
    `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`
  - source profile:
    `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`
  - event taxonomy:
    `ce7bafb341b36ab4c6093bf1c09c967e9cea10d4223724a1fc679086e5d16842`
  - tag taxonomy:
    `e0bc1bd8ff6ea5339586fdfc3e8e9b285a4a18f1ae2f5868ccc9ec9cecc8a922`
- shell-only inventory evidence root:
  `/tmp/w04-field-semantic-review-r1.rCyRwI`
- inventory algorithm:
  - enumerated every `*.pyc` beneath the repository while pruning `.git` and
    `.venv`, and every `*.pyc` beneath the exact root
    `.venv/lib/python3.12/site-packages`;
  - emitted a C-locale sorted TSV with relative path, filesystem kind, byte
    size, permission mode, link count, integer mtime, first 16 bytes, first
    4-byte magic, and full SHA-256;
  - projected metadata columns 1-8 and content columns 1 and 9;
  - compared the complete, metadata, and content projections byte-for-byte.
- repository preflight and terminal inventory:
  - entries: `58`
  - metadata TSV SHA-256:
    `1f81d2110f3cee98c95b80263521691ff4a4c026fd9c2131ea89644c0f882eda`
  - content TSV SHA-256:
    `a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9`
  - complete TSV SHA-256:
    `7a71382218f592173d68eef34eef5c6f8e8554786e10bc141b8eabfb262ec4b4`
- site-packages preflight and terminal inventory:
  - entries: `1086`
  - metadata TSV SHA-256:
    `3679170a0920f5655765024826177f001c675d9fc48fdc3910d7d50fb9e3d9bf`
  - content TSV SHA-256:
    `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18`
  - complete TSV SHA-256:
    `e55ec57dc8e8913885e31dafa207b46845092af43418388dc5f5a729780777b5`
- inventory classification:
  - site-packages: `972 SITE_DISTRIBUTION_NORMAL`,
    `112 SITE_PYTEST_REWRITE`, `1 UV_BOOTSTRAP_NORMAL`, and
    `1 SITE_SIX_OPTIONAL_INERT_ORPHAN`;
  - repository: `35 REPOSITORY_NORMAL`, `20 REPOSITORY_PYTEST_REWRITE`, and the
    3 exact inert orphans
    `migrations/__pycache__/env.cpython-312.pyc`,
    `migrations/versions/__pycache__/0001_foundation.cpython-312.pyc`, and
    `src/scouting/storage/__pycache__/postgres.cpython-312.pyc`;
  - all 1,144 entries were regular files, mode `0644`, link count `1`, and
    magic `cb0d0d0a`; zero unsafe/unclassified entries;
  - 5,761 RECORD-owned site Python sources were present for provenance checks.
- preflight absence gate: the review, acceptance, and all 13 downstream paths
  were absent before review creation.
- post-review authority gate: the exact review is present; acceptance and all
  13 downstream paths remain absent.

## Risks

- No P0, P1, or P2 defect or residual technical uncertainty was found within
  this packet's field-semantic and progression-contract scope.
- This PASS review is not acceptance and grants no downstream authority.
  Acceptance remains a separate master-owned action.

## Follow-up items

- Master may independently verify this return and, only under separate
  authorization, create the exact acceptance artifact. No downstream work is
  authorized by this return.

## Scope confirmation

- no Git operations: confirmed; no Git command was run.
- no unauthorised dependency or lockfile changes: confirmed; no dependency
  install/sync occurred and `pyproject.toml`/`uv.lock` were not edited.
- no edits outside `allowed_paths`: confirmed; exactly the two owned review and
  return paths were created.
- no delegation: confirmed.
- no self-approval or acceptance artifact: confirmed.
- no provider/network access: confirmed.
- no Bronze, Silver, Gold, product, runtime, cloud, container, endpoint,
  deployment, or other downstream artifact: confirmed.
- no pyc cleanup or repair: confirmed; caches were inventory-only and reproduced
  byte-for-byte.
