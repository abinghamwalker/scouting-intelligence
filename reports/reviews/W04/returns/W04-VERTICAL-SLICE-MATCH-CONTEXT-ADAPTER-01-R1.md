# Subagent return

## Task

- task_id: `W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-01`
- objective: Implement the bounded read-only adapter that joins the exact selected
  Wyscout match member, accepted season/lineup binding, identity bundle, and
  complete checked 1,768-action population without inventing a product value.

## Files changed

- `src/scouting/sources/wyscout_vertical_slice.py`
- `tests/unit/test_w04_wyscout_vertical_slice_context.py`
- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-01-R1.md`

## Summary

- Added `load_verified_match_context`, which accepts only the exact absolute
  repository source, manifest, and identity roots and the three accepted caller
  digests.
- The adapter descriptor-relatively opens only
  `archive-members/matches_England.json` beneath the exact source root with
  no-follow traversal. It requires a unique regular `0600` inode, stable metadata,
  exactly `1,694,720` bytes, physical SHA-256 `620725...`, strict JSON array
  cardinality `380`, and one selected match only at ordinal `379`.
- The selected raw record must reproduce canonical raw SHA-256 `1cc084...` and
  strict source values match `2499719`, competition `364`, season integer `181150`,
  UTC source clock `2017-08-11 18:45:00`, and teams exactly `1609` and `1631`.
- The target player must occur exactly once on team `1631`'s bench, never in its
  lineup or as a substitution-out, never cross team `1609`, and have exactly one
  strict-integer substitution-in at minute `82`. The adapter never derives an end,
  elapsed minutes, denominator, or per-90 eligibility.
- The accepted `bounded_season_uuid(181150)` is consumed and must equal
  `4696aa1f-b512-5d18-af79-33cf031455cf`; there is no second season derivation.
- The existing source-complete identity loader is called, forcing recomputation and
  readback of bundle `412770...` / ID `31638732...`. Exact resolved bindings are
  then required for competition, both teams, the target player, and match.
- The existing verified event loader is called and its opaque completion capability
  is revalidated. The adapter requires exactly `1,768` uniquely ordered actions,
  `1H=901` / `2H=867`, and accepted membership digests `473174...` / `b9b2ef...`.
- The returned frozen context recursively freezes the raw match mapping, arrays, and
  nested objects. The implementation contains no write, materialization, network,
  provider, product, receipt, run, staging, or publication path.
- Tests independently create exact temporary root mirrors and cover truncation,
  addition, wrong cardinality/ordinal/digest, duplicate selected match, symlink,
  directory, hard link, unsafe mode, nonabsolute/alternate roots, digest argument
  drift, strings/Booleans, competition/season/team/clock drift, bench/substitution
  omission/addition/duplication/cross-team drift, identity drift, nested mutation,
  and incomplete/additional/duplicate/reordered/cross-scope event populations.

## Exact fixed-binding and positive proof

All packet bindings were verified before editing:

| Binding | SHA-256 / physical proof | Result |
| --- | --- | --- |
| completion adapter | `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c` | PASS |
| build contract | `c71f2746b285d6ecadd5a2a2eef8333f5f66df491b23f966640cbc4994a76b16` | PASS |
| identity runtime | `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd` | PASS |
| identity bundle | `4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80` | PASS |
| season/lineup decision | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` | PASS |
| season/lineup acceptance | `6cbf2cd2aea87489854eee208ee4cbb3f7d3dc2c603d32aa306515418863c27e` | PASS |
| source manifest | `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd` | PASS |
| match member | regular `0600`, `1,694,720` bytes, `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` | PASS |

The producer also invoked `load_verified_match_context` against the unmocked real
accepted roots. It independently recomputed and reopened the exact identity bundle
and exact event population and returned:

- match source row: ordinal `379`, raw SHA-256
  `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`;
- match canonical ID: `bad97950-6fac-5cf0-a93c-094f91abbb9b`;
- competition canonical ID: `cb5c5317-fa4a-571e-93dc-ef6ce482eab7`;
- season source/canonical IDs: `181150` /
  `4696aa1f-b512-5d18-af79-33cf031455cf`;
- team canonical IDs in accepted source order:
  `b5f2dd3c-0166-5384-99fa-0ed47cc7e44c` and
  `5b353635-819b-5bd1-8ca2-5a7364042a96`;
- target player canonical ID: `be8da881-2b15-513f-978f-6bb3865bc8e2`;
- event population: `1H=901`, `2H=867`, total `1768`, with membership SHA-256
  `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`
  and `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`.

Final deliverable hashes before this return was written:

- `src/scouting/sources/wyscout_vertical_slice.py`:
  `2479f0db6eb949cb8856aa4efee5005f5531619726751230486039251e5fe4a3`
- `tests/unit/test_w04_wyscout_vertical_slice_context.py`:
  `a3a4d26edb34d53a66dc6e36a6b9c75f102942731846dc08d301feba064d165e`

## Tests run

- command: `uv run ruff format --check src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py`
  - exit status: `0`
  - result: `2 files already formatted`
- command: `uv run ruff check src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py`
  - exit status: `0`
  - result: all checks passed
- command: `uv run mypy src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py`
  - exit status: `0`
  - result: success, no issues in two source files
- command: `uv run pytest -q tests/unit/test_w04_wyscout_vertical_slice_context.py tests/unit/test_wyscout_source_completion_index.py tests/unit/test_wyscout_identity.py`
  - exit status: `0`
  - result: `129 passed in 12.15s`
- command: `uv run bandit -q -r src/scouting/sources/wyscout_vertical_slice.py`
  - initial sandbox exit status: `2`
  - initial result: existing uv cache path outside the workspace was unreadable;
    no candidate finding was produced
  - approved rerun exit status: `0`
  - approved rerun result: no findings
- command: `uv run lint-imports`
  - initial sandbox exit status: `2`
  - initial result: existing uv cache path outside the workspace was unreadable;
    no architecture result was produced
  - approved rerun exit status: `0`
  - approved rerun result: `3 kept, 0 broken`
- command: `uv run python scripts/verify_local_only.py`
  - exit status: `0`
  - result: `PASS`, zero remotes, branch `main`, local guard active, one root uv
    project, no hosted CI/container/external-service/deployment surface
- command: real-root `uv run python -c '<load_verified_match_context proof>'`
  - exit status: `0`
  - result: exact source row, five canonical identity bindings, season binding,
    period counts/digests, and `1768` actions reproduced as listed above

## Artifacts/evidence

- `src/scouting/sources/wyscout_vertical_slice.py`
- `tests/unit/test_w04_wyscout_vertical_slice_context.py`
- `reports/reviews/W04/returns/W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-01-R1.md`
- accepted source manifest:
  `data/manifests/wyscout/v5/source/4e16bdb5-afe7-5601-88ad-adc124cfce3b.source-snapshot-manifest.json`
- accepted identity bundle:
  `data/working/wyscout/v5/identity/bundles/4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80.identity-bundle.json`
- accepted completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`

## Risks

- The intentionally fail-closed public load recomputes the source-complete identity
  population and rereads the complete England event member. This has bounded local
  runtime and memory cost, but avoids trusting caller-supplied identities or a
  partial event population.
- No unresolved leakage, schema, security, scope, or correctness risk identified.

## Follow-up items

- Fresh independent review and master reproduction of the packet evidence.

## Scope confirmation

- no Git operations: confirmed; no Git command was run
- no unauthorised dependency or lockfile changes: confirmed; `pyproject.toml` and
  `uv.lock` were not edited
- no edits outside `allowed_paths`: confirmed
