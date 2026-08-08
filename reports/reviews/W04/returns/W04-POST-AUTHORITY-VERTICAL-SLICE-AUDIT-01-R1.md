# Subagent return

## Task

- task_id: `W04-POST-AUTHORITY-VERTICAL-SLICE-AUDIT-01`
- objective: Audit the current guarded source-to-product path and return the
  smallest exact producer/reviewer packets for the one-match four-feature
  raw-to-Gold slice after the authority, build-contract, schema and aggregate
  gates pass.

## Files changed

- `reports/reviews/W04/returns/W04-POST-AUTHORITY-VERTICAL-SLICE-AUDIT-01-R1.md`

## Summary

### Verdict

`BLOCKED` for product-producer dispatch. The existing components are sufficient
for the exact event population, checked Action-to-Gold graph, deterministic
Parquet bytes and semantic digests. They are not yet sufficient to make the real
slice semantically exact without inventing two product bindings:

1. the real source supplies strict `seasonId=181150`, but the accepted identity
   runtime has no `SEASON` entity and no accepted canonical `season_id` UUID
   derivation; `SilverPlayerMatchFact` and `GoldPlayerWindow` both require a
   non-null UUID; and
2. accepted source-complete identity evidence proves player `285508` is on the
   team `1631` bench and is substituted in at nominal minute `82`, while the
   packet-read contract audit prescribes only Action/Possession/Fact Silver
   products and explicitly omits lineup Parquet. Emitting the evidenced
   right-censored stint may expand the frozen product population; omitting it
   discards known lineup evidence and risks a false event-only/no-lineup claim.

Neither choice may be made in product code. The fresh build authority and
implemented-schema gates must reconcile both points explicitly, within the
already-authorized one-match/four-feature scope, before the packets below are
dispatched. If that requires a new identity kind, a new feature, a different
product population, or a change to R20/R21/R4, the master must stop for user
authorization.

No architecture, dependency, provider, cloud, container, hosted-CI, endpoint,
remote or deployment change is otherwise necessary. This audit wrote no product,
manifest, receipt, build, aggregate, data or control bytes.

### Fixed-binding verification

| Binding | Exact SHA-256 | Result |
| --- | --- | --- |
| R4 audit | `a6f8f3321dcfdb0c04d231d3e07d06497441ce703716d6e509f3f45b8829c222` | PASS |
| accepted source adapter | `ef16a489a13dffab7cf2b609f81d2a229a012ec5b92ba4debee0f628b35e721c` | PASS |
| completion runtime | `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c` | PASS |
| Wyscout data contract | `154f1ae9934615a2ce9a24a4f8e373cd640a4c3246df93f0e35e6bed28517932` | PASS |
| exact Parquet encoder | `bd849dda61b570378697ce703719c2058fc9c450e298a88a9f1e5f95ad0a7ff4` | PASS |
| accepted completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | PASS |

The index was reproduced at
`data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
with exact size `644037` bytes.

### Exact retained source/product oracle

- source manifest ID/digest:
  `4e16bdb5-afe7-5601-88ad-adc124cfce3b` /
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`;
- England event member:
  `archive-members/events_England.json`, digest
  `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`,
  `188888614` bytes, `643150` rows;
- match source ID / UUID: `2499719` /
  `bad97950-6fac-5cf0-a93c-094f91abbb9b`;
- exact match population: `1H=901` with digest
  `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b`,
  `2H=867` with digest
  `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16`,
  total `1768`;
- exact match member row: `matches_England.json#379`, raw digest
  `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`,
  competition `364`, season source ID `181150`, teams `{1609,1631}`, start
  `2017-08-11T18:45:00Z`;
- target player source ID / UUID: `285508` /
  `be8da881-2b15-513f-978f-6bb3865bc8e2`; target team source ID / UUID:
  `1631` / `5b353635-819b-5bd1-8ca2-5a7364042a96`;
- target action source IDs: `177960876`, `177961018`; both have two accepted
  in-bounds positions and intersect complete resolved groups of `7` and `6`
  actions;
- required checked graph, excluding the unresolved lineup choice: `13` Silver
  Actions, `2` Silver Possessions, `1` Silver PlayerMatchFact, and `1` Gold
  PlayerWindow;
- exact Gold vector: `(action_count=2,
  coordinate_known_action_count=2, match_count=1,
  resolved_possession_action_count=2)`;
- exact half-open window/cutoff:
  `[2017-08-11T00:00:00Z,2017-08-12T00:00:00Z)`, cutoff
  `2026-08-01T00:00:00Z`, snapshot `2017-08-11T18:45:00Z`;
- independently reproduced window identity SHA-256
  `3582348bc62d5624162078802a0495edd2a3206856cdf532322d1233bc33b327`
  and UUID `a0af8d56-e41d-5467-b46e-82887c4861e0`.

### Reusable accepted graph

| Surface | Exact reusable boundary | State |
| --- | --- | --- |
| source/index | `load_verified_match_population` | Accepted full-member verification, immutable `1768`-action population and authentic full-match capability |
| identity | `load_initial_identity_bundle` | Accepted source-complete bundle/readback, including exact competition/team/player/match identities |
| checked products | `build_checked_silver_action`, `build_checked_silver_possession`, `build_checked_silver_player_match_fact`, `build_checked_gold_player_window`, `build_checked_layer_manifest`, `require_checked_product` | Accepted acyclic re-deriving capability graph |
| row/path/manifest contracts | `src/scouting/contracts/wyscout_data.py` | Accepted strict semantic contracts and exact W04 path templates |
| product bytes | `encode_w04_wyscout_product_parquet` | Accepted R20 Parquet controls, explicit schema equality, ordered unique keys, semantic framing and deterministic vectors |
| generic storage | `GuardedStorage` | Reusable reader/primitives only; `write_bytes` is not a W04 product publisher because it creates a forbidden sidecar |

The repository currently contains only the accepted identity queue/bundle and
source/source-completion manifests beneath Wyscout working/manifest roots. There
are no Bronze, Silver, Gold, layer-manifest, receipt, rebuild-run or staging files.

### Remaining implementation gaps

The following are absent and must be supplied only by their independently accepted
upstream packets:

- exact 25-key projection/invocation implementation and one-hash rebuild check;
- complete 23-root closed schema exporters and accepted v2 schema/product
  aggregate instances;
- closed nine-key invocation and 15-key boundary receipt models/readers;
- sole two-key complete-`LayerManifest` semantic function and all-three-summary
  reconciliation;
- exact no-sidecar staged/no-replace W04 publisher;
- verified match-context adapter for source match member metadata; and
- actual Bronze/Silver/Gold serializers and rebuild composition.

The 23-root schema gate must also freeze, rather than leave to the product
producer, exact Bronze rejected-field traversal/cardinality and every artifact's
complete Arrow schema and primary-key roster. Repeated array paths cannot be
assigned an ad hoc ordinal or collapsed in product code.

## Shortest post-resolution packet sequence

The following is the shortest safe sequence after fresh authority acceptance and
the build-contract/schema/v2-aggregate gates close every prerequisite above.
Packets A and B are path-disjoint and may run in parallel; C is serial after both.

### Packet A: verified match-context adapter

`W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-01-R1`

- allowed implementation:
  `src/scouting/sources/wyscout_vertical_slice.py`
- allowed tests:
  `tests/unit/test_w04_wyscout_vertical_slice_context.py`
- allowed return: one new producer return only.
- behavior: no-follow whole-file verification of exact
  `archive-members/matches_England.json`, `1694720` bytes, `380` rows and accepted
  digest; strict selection of ordinal `379`; exact raw-record digest and match,
  competition, season-source, teams, start, bench/substitution reconciliation;
  join to the accepted identity-bundle target rows and existing verified event
  population; immutable return only after every equality passes. It returns the
  strict season source integer but must consume, never invent, the independently
  accepted canonical season UUID binding.
- reviewer packet: read-only candidate/tests; owns only
  `reports/reviews/W04/wyscout-vertical-slice-match-context-independent-review-R1.md`
  and its return. Challenge truncation, addition, duplicate match, wrong ordinal,
  source/member/digest drift, strings/Booleans, cross-match/team/competition/season,
  lineup mutation and mutable nested raw values.

### Packet B: exact sidecar-free publisher

`W04-STAGED-IMMUTABLE-PUBLISHER-01-R1`

- allowed implementation:
  `src/scouting/storage/wyscout_publication.py`
- allowed tests:
  `tests/unit/test_w04_staged_product_publisher.py`
- allowed return: one new producer return only.
- behavior: exact named roots, bounded POSIX tails, descriptor-relative
  `O_NOFOLLOW`, `0700` directories and `0600` files; exact serializer-owned
  `.partial` staging; fsync/reopen/validator/final code-environment-resource
  recheck; same-filesystem atomic no-replace hard-link promotion; equal-byte
  idempotency; unequal/race/symlink/cross-device failure; no sidecar; leave failed
  staged evidence; successful final link count one after staged-name unlink.
- reviewer packet: read-only candidate/tests; owns only
  `reports/reviews/W04/wyscout-staged-product-publisher-independent-review-R1.md`
  and its return. Independently reproduce physical/security vectors and every
  adversarial race/path/mode case.

Do not modify existing `GuardedStorage.write_bytes` or the accepted generic
Parquet encoder. Additive modules preserve their existing callers and bytes.

### Packet C: one exact vertical-slice rebuild

`W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1`

- allowed implementation, all new beneath
  `src/scouting/data_products/wyscout/`:
  `__init__.py`, `bronze.py`, `actions.py`, `possessions.py`,
  `player_match.py`, `silver_manifest.py`, `gold.py`,
  `temporal_boundary.py`, `rebuild.py`, plus `lineups.py` only if the upstream
  authority explicitly resolves the lineup population to one evidenced
  right-censored row;
- allowed tests:
  `tests/e2e/test_w04_wyscout_vertical_slice.py` and
  `tests/security/test_w04_wyscout_vertical_slice_publication.py`;
- allowed return: one new producer return only;
- dependencies: accepted authority, build contract, all 23 schema roots, both v2
  aggregate digests, accepted Packet A and B, identity runtime and Parquet encoder;
- behavior in exact order:
  1. admit the exact code/environment/resource, identity, source/index, window,
     season and lineage inputs and compute the sole 25-key build hash;
  2. load the exact immutable `1768`-action match population and verified match
     context;
  3. build all `1768` Bronze known Action records plus the schema-authorized exact
     rejected-field population; no rejected-record partition and no zero-row
     Parquet;
  4. construct exactly the required `13` checked Actions, `2` complete checked
     Possessions and `1` checked PlayerMatchFact, with the lineup population
     exactly as resolved upstream;
  5. construct exactly one checked Gold row with vector `(2,2,1,2)` and no fifth
     feature, rate, per-90, outcome, value, inferred role or provider-possession
     claim;
  6. call `require_checked_product` immediately at every Silver/Gold row and
     checked-manifest serialization boundary;
  7. encode products with exact accepted explicit schemas/primary keys and publish
     product Parquet before each layer's checked canonical manifest;
  8. derive each Bronze/Silver/Gold layer summary's semantic digest only from the
     R4 two-key complete-manifest wrapper, then reconcile Gold-to-Silver-to-Bronze
     summary/parent identities;
  9. derive the exact one-Gold population from the guard-read Gold manifest, reopen
     its complete parent chain and product, publish exactly one 15-key boundary
     receipt, reopen it, then publish exactly one nine-key invocation receipt only
     after `started_at <= checked_at <= completed_at`; and
  10. emit the already-accepted child-result summary only after complete readback.

Packet C tests may publish only below isolated temporary exact-root mirrors. The
real repository product roots remain untouched until independent review and the
master gate pass.

### Packet D: independent slice/publication review

`W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-REVIEW-01-R1`

- read-only access to all accepted inputs and Packet C code/tests;
- allowed writes: one independent review and one reviewer return only;
- independently reconstruct the real source values rather than importing test
  fixtures; run the complete focused matrix below in two isolated roots; confirm
  no product/control byte exists under the real roots; return `PASS` or bounded
  `REWORK`, never self-approval.

After Packet D passes, the master alone reruns the full repository gate, executes
the accepted launcher into the real local roots, performs a second isolated rebuild
for determinism, inspects every byte/readback, and accepts or returns bounded
rework. Real local publication is not delegated.

## Exact roots and output ownership

No writer receives the repository root or broad `data` root. The publisher maps
only these exact absolute named roots:

| Named root | Exact repository location | Owned logical outputs |
| --- | --- | --- |
| `wyscout-working` | `data/working/wyscout/v5` | `.staging/<build>/<run>/...`, final Bronze/Silver/Gold Parquet |
| `wyscout-manifests` | `data/manifests/wyscout/v5` | final Bronze/Silver/Gold layer manifests only |
| `w04-rebuild-runs` | `runs/w04/wyscout-rebuild` | one boundary receipt and one invocation receipt per accepted run |

Read-only roots are exact `data/source/wyscout/v5`, `data/manifests`, and
`data/working/wyscout/v5/identity`.

The bounded product paths are exactly:

- Bronze known Action:
  `data/working/wyscout/v5/bronze/build_id=<build>/records/record_kind=action/source_sha256=301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad/part-00000.parquet`;
- Bronze rejected field, only when the accepted traversal yields non-zero rows:
  `data/working/wyscout/v5/bronze/build_id=<build>/quarantine/rejected-field/record_kind=action/source_sha256=301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad/part-00000.parquet`;
- Silver Action, Possession and PlayerMatchFact:
  `data/working/wyscout/v5/silver/build_id=<build>/<action|possession|player-match-fact>/source_partition=england/part-00000.parquet`;
- Silver LineupStint only if explicitly authorized:
  `data/working/wyscout/v5/silver/build_id=<build>/lineup-stint/source_partition=england/part-00000.parquet`;
- Gold PlayerWindow:
  `data/working/wyscout/v5/gold/build_id=<build>/player-window/competition_id=cb5c5317-fa4a-571e-93dc-ef6ce482eab7/window_definition_id=a0af8d56-e41d-5467-b46e-82887c4861e0/window_start_utc=20170811T000000000000Z/window_end_utc=20170812T000000000000Z/feature_cutoff_ts=20260801T000000000000Z/part-00000.parquet`;
- manifests:
  `data/manifests/wyscout/v5/<bronze|silver|gold>/<build>.manifest.json`;
- boundary:
  `runs/w04/wyscout-rebuild/<build>/<run>/boundary/<sha256-of-exact-Gold-path>.temporal-boundary-receipt.json`;
- invocation:
  `runs/w04/wyscout-rebuild/<build>/<run>.receipt.json`.

No entity, Match, Competition, Team, Player, rejected-record, empty quarantine or
other product Parquet is emitted by this bounded slice.

## Focused acceptance matrix

| Priority | Case | Exact positive proof | Required failure |
| --- | --- | --- | --- |
| P0 | source/context admission | exact manifest/index/member/match bytes, `643150` event rows, `380` match rows, `901+867=1768`, ordinal `379` | any missing/additional/duplicate/reordered/stale/cross-source/member/match/period row fails before staging |
| P0 | identity/season/lineup | exact target identity rows, competition `364`, season source `181150`, teams, bench/substitution and accepted season UUID/population decision | absent or invented season UUID, ignored known lineup evidence, unauthorized lineup expansion or string/Boolean coercion fails |
| P0 | Bronze equality | exactly `1768` canonical raw Action rows and exact schema-authorized rejected fields | two-row shortcut, incomplete population, raw digest/ordinal drift, unsupported rejected-field ordinal/collapse or unknown record fails |
| P0 | checked graph | authentic capability, exact `13` Actions, `2` Possessions, `1` Fact, one Gold `(2,2,1,2)` | direct/copied/rehydrated models, missing contributor, coordinate zero, fifth feature, detached/cyclic/forged capability fails |
| P0 | temporal | exact half-open window, selected-match snapshot, strict cutoff, five dependencies, watermark and valid-from maximum | any bound clock at/after cutoff, wrong window edge/watermark/valid-from or post-cutoff read fails |
| P0 | schema/serialization | every artifact uses its accepted complete schema, canonical primary-key order, exact R20 Parquet and semantic formula | inference, extra/missing/nullability/type/metadata/order/key/parent mutation fails before publication |
| P0 | manifest semantics | complete manifest physical identity plus sole R4 two-key semantic derivation for all three summaries and exact parent chain | any copied entry/physical/other-layer digest, swapped summary or downstream rehash substitution fails |
| P0 | receipt population | guard-read Gold manifest yields exactly one Gold product and exactly one boundary; exact 15/9 keys and clock interval | empty/extra/duplicate/reordered/cross-build/run/path/hash/size/semantic/count/clock receipt fails before `COMPLETE` |
| P1 | immutable publisher | sidecar-free `0600` files below `0700` exact roots; no-replace promotion; exact replay idempotent | traversal, symlink, non-regular/unsafe mode, partial, validation/recheck, race, unequal final or cross-device leaves evidence and preserves final |
| P1 | deterministic rebuild | same accepted input/build/run in two isolated roots gives byte-identical products, manifests and receipts; a different run keeps products/manifests identical | wall clock, host, absolute path, random order, run ID or ambient state entering stable bytes blocks acceptance |
| P1 | rights/local only | exact restricted attribution, internal-only, export false; real roots absent before final master execution | rights drift, provider/network call, remote, cloud/container/CI/endpoint/deployment or escaped output fails |

Focused producer/reviewer commands, with the final filenames substituted by the
master packet, must include:

```text
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff format --check <owned paths>
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync ruff check <owned paths>
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync mypy <owned src paths>
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider \
  tests/unit/test_w04_wyscout_vertical_slice_context.py \
  tests/unit/test_w04_staged_product_publisher.py \
  tests/unit/test_w04_wyscout_product_formats.py \
  tests/unit/test_wyscout_source_completion_index.py \
  tests/contracts/test_wyscout_data_contracts.py \
  tests/e2e/test_w04_wyscout_vertical_slice.py \
  tests/security/test_w04_wyscout_vertical_slice_publication.py
PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync bandit -q -r \
  src/scouting/sources/wyscout_vertical_slice.py \
  src/scouting/storage/wyscout_publication.py \
  src/scouting/data_products/wyscout
uv run python scripts/verify_local_only.py
```

The master then runs the complete repository suite from `AGENTS.md`, including
`uv sync --locked --all-groups`, full Ruff, mypy, import-linter, full pytest,
Bandit, Git-guard check, local-only verifier, W04 phase verifier,
`git diff --check`, explained `git status --short`, and empty `git remote`.

## Tests run

- command: complete read of `AGENTS.md`, the packet, every `read_first` file,
  incorporated R2/R3 authority rules, and bounded current-surface inventory
  - exit status: `0`
  - result: exact reusable and absent surfaces identified; no implementation or
    output file was changed.
- command: fixed SHA-256 reproduction for R4, source adapter, completion runtime,
  data contract, Parquet encoder and accepted completion index
  - exit status: `0`
  - result: all six packet bindings matched; index size `644037`.
- command: read-only strict match-member probe through `uv run python -B`
  - exit status: `0`
  - result: exact `380` rows; sole match `2499719` at ordinal `379`; competition
    `364`, season source `181150`, teams `1609/1631`, target bench/substitution at
    minute `82`, start `2017-08-11T18:45:00Z`.
- command: read-only independent window SHA-256/UUIDv5 reproduction through
  `uv run python -B`
  - exit status: `0`
  - result: exact digest `3582348b...33b327` and UUID
    `a0af8d56-e41d-5467-b46e-82887c4861e0`.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run pytest -q -p no:cacheprovider tests/unit/test_wyscout_source_completion_index.py::test_verified_match_adapter_returns_exact_immutable_raw_evidence_pairs tests/unit/test_w04_wyscout_product_formats.py::test_fixed_physical_and_semantic_vectors_are_repeatable tests/unit/test_w04_wyscout_product_formats.py::test_exact_r20_parquet_controls_and_round_trip`
  - exit status: `0`
  - result: `3 passed in 2.82s`.
- command: exact file inventory under `data/working/wyscout/v5`,
  `data/manifests/wyscout/v5`, and `runs/w04`
  - exit status: `0`
  - result: only accepted identity queue/bundle and source/index manifests exist;
    no product, receipt, run or staging byte exists.
- command: first post-write hash/keyword verification shell line
  - exit status: `127` after all requested `shasum` and `wc` operations succeeded
  - result: an unquoted Markdown backtick in the final `rg` pattern caused zsh to
    attempt the harmless command name `BLOCKED`; no Python, product, control or
    repository mutation ran. The safe quoted verification was rerun separately.

## Artifacts/evidence

- this audit:
  `reports/reviews/W04/returns/W04-POST-AUTHORITY-VERTICAL-SLICE-AUDIT-01-R1.md`
- accepted completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
- accepted identity bundle:
  `data/working/wyscout/v5/identity/bundles/4127705ab1a66145576439e520351587d817c48a71a572bb2c0cefc291fd1e80.identity-bundle.json`

## Risks

- P0: inventing a season UUID would make a formally valid but semantically
  unauthorized Gold key and product path.
- P0: choosing either zero or one lineup row without authority reconciliation can
  respectively discard known evidence or expand the frozen population.
- P0: an ad hoc Bronze nested-field walker can collapse or duplicate rejected
  evidence because the schema/primary key must own repeated-path identity.
- P1: using generic `GuardedStorage.write_bytes` creates an unauthorized sidecar;
  replacing a destination after preflight is race-unsafe.
- P1: the existing real-source adapter is intentionally memory-resident for this
  bounded POC. General streaming is not required and must not become a dependency
  or architecture change here.

## Follow-up items

- The master must require the authority/build-schema reviewers to resolve the
  canonical season UUID and exact lineup population without altering frozen
  R20/R21/R4 bytes. If they cannot, stop for the user's bounded decision.
- Once resolved, issue Packets A and B in parallel, obtain their independent
  reviews, then issue C and D serially and perform the complete master gate before
  any real local product publication.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no product, manifest, receipt, build, aggregate, data, authority or control
  writes: confirmed
- no provider/network, cloud, container, hosted-CI, endpoint, remote or deployment
  action: confirmed
