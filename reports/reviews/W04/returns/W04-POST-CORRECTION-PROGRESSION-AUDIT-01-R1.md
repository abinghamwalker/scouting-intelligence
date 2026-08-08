# Subagent return

## Task

- task_id: `W04-POST-CORRECTION-PROGRESSION-AUDIT-01-R1`
- objective: Determine whether the additive season/lineup authority closes the two
  prior product blockers and return the shortest exact downstream packet graph,
  including the required stale progression-test correction.

## Files changed

- `reports/reviews/W04/returns/W04-POST-CORRECTION-PROGRESSION-AUDIT-01-R1.md`

## Summary

### Verdict

`REWORK_REQUIRED` — bounded test-only R2; authority semantics pass.

The candidate closes both prior blockers without changing an R20/R21/R4 byte,
adding an identity-bundle kind, adding a schema root, changing the 25-key build
projection, adding a feature or Gold row, or widening the selected source/product
population. The fresh independent R1 review has now returned `REWORK` with one P1
progression-test finding and no authority-byte finding. Its currently live failed
review/return bytes, which must become immutable archive evidence before reuse of
the decision-fixed review location, are:

```text
reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-independent-review-R1.md
sha256 = 431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba

reports/reviews/W04/returns/W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R1.md
sha256 = 8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547
```

Product implementation therefore remains blocked by one combined, test-only R2,
a fresh R2 independent `PASS`, master acceptance, and the already-required
build/schema/aggregate/runtime/publication gates. The decision JSON must not be
revised.

### Fixed bindings

Every packet-fixed SHA-256 was reproduced before analysis and again after the
read-only probes:

| Artifact | Expected and observed SHA-256 | Result |
|---|---|---|
| season/lineup decision | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` | PASS |
| season/lineup closed test | `0b5b933575f22451b5474323188619acec659c7291262c2e457086319fe93e29` | PASS |
| decision master verification | `d635d3836bf98e46c09d640c89ec1433992836d7951545b81ddd484ef632ffd6` | PASS |
| build/product decision | `3da3baa03190dfc711d81e7b65f7fdb22ca4f9b5b6f14784b03f94be2be9dd6d` | PASS |
| build/product acceptance | `9bcd9ef6f61b06f443a4d8f0d590db74559ee739976f285c41127da5ff1f5921` | PASS |
| prior build/schema audit | `402106160add4af2d12b46022220b6d7d71b3f0243e85162b56fd1674c28fc24` | PASS |
| prior vertical-slice audit | `ccc7a7c803cf2acfb5a787f0f8594c7f2c1c446ba3365ced84bcde2e35b3cad7` | PASS |

### Blocker closure

The season blocker is closed by one deterministic value only:

```text
source namespace =
  UUIDv5(NAMESPACE_URL,
    "urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5")
season namespace = UUIDv5(source namespace, "season")
season_id = UUIDv5(season namespace, "figshare-v5:181150")
          = 4696aa1f-b512-5d18-af79-33cf031455cf
```

The physical source independently reproduced strict integer `seasonId=181150` at
`archive-members/matches_England.json` ordinal `379`. This is a bounded product
binding, not an identity-bundle entity: `identity_bundle_kind_added=false`, the
second derivation is forbidden, and the existing bundle's four entity kinds stay
unchanged.

The lineup blocker is closed by exactly one ordered row for match `2499719`, team
`1631`, player `285508`, stint ordinal `0`. Independent source readback reproduced
one bench membership and the sole substitution-in
`{"minute":82,"playerIn":285508,"playerOut":192748}`. The exact UUID is
`591cdf5b-2281-53c4-8225-150313ca2c01`; start is `[82,83)`, end and every minute
bound are null, `right_censored=true`, `per90_eligible=false`, and the suppression
reason remains `suppressed_unsupported_denominator`. Omission, addition,
duplication, reordering, inferred terminal/minutes/per-90, or another
match/team/player/stint is explicitly rejected.

The source row/member evidence also reproduced exactly: source-manifest digest
`8fb6eb54...fd89bd`, match-member digest `620725c2...fe29`, size `1694720`, row
count `380`, ordinal `379`, and raw-row digest `1cc084d5...74d86`. The accepted
completion-index digest remains `46a22423...f87df`; the event population remains
`901+867=1768`. The exact product remains one Gold row with four values
`(2,2,1,2)`. The one lineup row is supporting Silver evidence and does not create a
fifth feature or Gold row.

The only build integration is one accepted authority reference appended within the
existing `authority_rows` member. The projection still has the exact same 25
top-level keys and one R20 canonical SHA-256; no 26th key or second hash is
permitted.

### Real stale progression-test risk

Three tests contain unconditional assertions that the real Bronze/Silver/Gold,
manifest and rebuild roots do not exist:

- `tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py`,
  `test_no_downstream_product_manifest_receipt_or_build_bytes_exist`;
- `tests/contracts/test_w04_wyscout_build_product_authority.py`, the same test
  name; and
- `tests/contracts/test_w04_r21_control_preimages.py`,
  `test_descriptor_strings_create_no_product_destination`.

They correctly describe their producer-time state, and all seven roots are absent
now, but they would fail after a legitimately accepted local publication. They are
tests, not frozen authority bytes. The authority JSON, acceptance JSON, R20, R21,
R4, v1/v2 preimages, completion index, source, and prior reports must remain
byte-identical. The failed R1 review has completed, so the three test bytes may now
be superseded only by the bounded R2 below. Before the decision-fixed review
location is reused, the failed R1 review and return must be copied byte-identically
into immutable archive paths and their original hashes reverified.

One combined R2 must supersede only those three stage-scoped live-filesystem
assertions. It must retain pre-acceptance absence, permit an independently accepted
later lifecycle, and prove authority/preimage validation itself is side-effect
free. It must not skip when a real product exists, weaken any canonical/digest
check, or claim that acceptance alone publishes a product. Existing lifecycle-aware
checks in the R21 cross-authority, field-v2, possession-v2 and supported-feature
tests already admit only their declared later states and must not be rewritten.

The smallest exact test-only correction contract is:

```text
packet = W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R2

allowed paths =
  tests/contracts/test_w04_wyscout_season_lineup_product_binding_authority.py
  tests/contracts/test_w04_wyscout_build_product_authority.py
  tests/contracts/test_w04_r21_control_preimages.py
  reports/reviews/W04/returns/
    W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R2.md

all authority, review, acceptance, source, index, R20/R21/R4, runtime,
product, data, config, orchestration, dependency and Git paths = read-only
```

Exact behavior:

1. In the season/lineup test, preserve every decision/digest/source/UUID/population
   and malformed-lifecycle assertion. The seven real roots remain required absent
   in `AUTHORITY_ONLY_NO_PRODUCT_BYTES`, `REVIEW_PASS`, and `REVIEW_REWORK`. In a
   strictly validated accepted state, replace permanent absence with exact
   before/after root-state equality around authority validation, proving that the
   authority reader creates, removes and promotes nothing while not outlawing a
   separately gated later product.
2. Apply the identical rule to the build-product test using its existing strict
   review/acceptance lifecycle parser. Preserve the accepted decision's
   `product_bytes_permitted=false` as its historical decision-time value; do not
   mutate or reinterpret that byte as a live publication switch.
3. In the R21 control-preimage test, preserve the exact seven descriptor
   destinations, all descriptor/digest/acyclic tests, and replace only
   `assert all(not destination.exists() ...)` with before/after destination-state
   equality around strict loading/validation of both inert preimages. The R21
   cross-authority test remains the lifecycle gate; the descriptor test proves
   that parsing descriptor strings does not create destinations.
4. Add synthetic regression coverage in the same three files proving:
   pre-review/pre-acceptance product presence fails; accepted-state validation
   succeeds with a simulated already-existing product root; and every authority or
   preimage validation call leaves the supplied root-state snapshot identical.
   No `pytest.skip`, `xfail`, environment flag, mutable global override, broad
   `exists()` waiver, or network/provider path is permitted.

R2 must bind the original three test hashes and the failed R1 review/return hashes
above in its return. A fresh independent review must fix the three new test hashes,
reproduce both synthetic lifecycle branches, search the whole collected W04
contract suite for any remaining unconditional real-root absence assertion, and
return `PASS` with zero findings before master acceptance.

The frozen decision does **not** name an R2 lifecycle review. It fixes both:

```text
path = reports/reviews/W04/authorities/
  wyscout-season-lineup-product-binding-independent-review-R1.md
review_id = w04-wyscout-season-lineup-product-binding-independent-review-R1
```

The acceptance validator requires that exact path, ID and schema. Consequently, a
new review stored only under an R2 path/ID cannot unlock acceptance. The smallest
non-architectural evidence-preserving route is:

```text
archive failed review bytes at:
  reports/reviews/W04/archive/
    wyscout-season-lineup-product-binding-independent-review-R1-rework-431e0cfb.md
  expected sha256 = 431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba

archive failed return bytes at:
  reports/reviews/W04/archive/
    W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R1-rework-8218de5b.md
  expected sha256 = 8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547

fresh PASS lifecycle review:
  reports/reviews/W04/authorities/
    wyscout-season-lineup-product-binding-independent-review-R1.md
  review_id = w04-wyscout-season-lineup-product-binding-independent-review-R1

fresh additive reviewer return:
  reports/reviews/W04/returns/
    W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R2.md
```

The master must create and hash-check the two archives before allowing replacement
of the fixed lifecycle review. No archive collision, byte mismatch, or loss of the
failed evidence is permitted. If replacement of that fixed location after exact
archival is not authorized, stop: changing the frozen decision or acceptance
lifecycle would exceed this test-only correction.

### Exact remaining surfaces and authority

| Missing surface | Exact authority already present | Wider decision needed |
|---|---|---|
| season UUID constructor and accepted authority-row integration | additive season/lineup decision | no |
| exact five-key window, 25-to-25 build/inverse, two receipts and eight result models | R20 plus accepted R4/build-product authority | no |
| complete canonical closure for exactly 23 roots | accepted build-product authority | no |
| real v2 schema-bundle then product-contract aggregates | accepted acyclic aggregate authority | no |
| verified selected-match context reader | R20 source seam plus additive season/lineup decision | no |
| sidecar-free staged immutable publisher | R20 publication rules | no |
| admission, local-control launcher and post-build rebuild child | R20 runtime/build rules | no |
| Bronze/action/lineup/possession/fact/Gold serializers, manifests and receipts | R20/R21/R4/build authority plus additive lineup population | no |
| exact rejected-field traversal, complete Arrow schemas and product key rosters | R20/R21 plus the independently reviewed 23-root closure | no |

The currently absent implementation paths were reproduced exactly:
`wyscout_build.py`, `wyscout_schema.py`, `wyscout_aggregates.py`, both v2 aggregate
JSON files, the match-context adapter, the publisher, the Wyscout data-product
package, and all three runtime scripts. This is missing implementation, not a
missing product or architecture decision.

### Shortest safe downstream packet graph

All reviews are fresh actors, own reports only, and cannot edit producer bytes.
All producer packets prohibit Git, dependencies, provider/network access and real
product-root writes. Every packet stops on fixed-byte drift, a new schema root,
feature, Gold row, source population, dependency, architecture or local-only
change.

#### Gate 0 — bounded R2, fresh review, then acceptance

1. Master first preserves the failed R1 review and return byte-identically at the
   two exact archive paths above, verifies their original hashes, and records the
   copy operation. This is evidence preservation, not an authority revision.
2. Dispatch `W04-SEASON-LINEUP-PRODUCT-BINDING-DECISION-01-R2` with exactly the four
   allowed paths and behavior listed in the test-only correction contract. It
   creates no R2 decision JSON: the accepted candidate remains the unchanged R1
   decision.
3. `W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R2` owns only the decision-fixed R1
   lifecycle review path and a new R2 return. It must first verify both archived
   failed artifacts, then replace the live review with a fresh `PASS` using the
   unchanged R1 review ID/schema. It binds the unchanged decision, failed R1
   evidence and all three corrected test hashes; runs the exact R2 regression
   matrix plus the R21 cross-authority suite; and returns `PASS` only with zero
   findings.
4. Master-only `W04-SEASON-LINEUP-PRODUCT-BINDING-ACCEPT-01-R1` owns only the
   canonical acceptance JSON, its master-acceptance verification, and return.
   Reproduce the unchanged decision hash, fresh fixed-path PASS review hash,
   archived failed-evidence hashes, actors, clocks, source evidence and the focused
   `season-lineup + build-authority + R21-cross-authority` suite.

#### Gate 1 — complete master gate

5. The R2 producer and reviewer checks are exactly:

   ```text
   uv run ruff format --check <three tests>
   uv run ruff check <three tests>
   uv run mypy <three tests>
   uv run pytest -q <three tests> tests/contracts/test_w04_r21_cross_authority_composability.py
   uv run python scripts/verify_local_only.py
   ```

6. The master runs the complete `AGENTS.md` repository gate before any product or
   build implementation resumes and records a new W04 verification report.

#### Lane A — serial build/schema/aggregate closure

7. `W04-WYSCOUT-BUILD-CONTRACT-01-R1` owns exactly
   `src/scouting/contracts/wyscout_build.py`,
   `tests/contracts/test_w04_wyscout_build_contract.py`, and its return. Implement
   the five-key window, sole season UUID helper, accepted fifth authority reference
   inside `authority_rows`, unchanged 25-key projection/invocation and inverse,
   nine-key invocation receipt, 15-key boundary receipt, and eight result models.
   Checks are Ruff format/lint, mypy, the new test plus build-authority,
   season/lineup and R21 composability suites, and local-only verification.
8. `W04-WYSCOUT-BUILD-CONTRACT-REVIEW-01-R1` owns only its review and return;
   independently reconstruct every UUID/preimage/hash/key/order and attack a sixth
   authority, 26th projection key, alternate season derivation, second hash,
   inferred lineup/minutes, clock equality and receipt/result substitution.
9. `W04-WYSCOUT-23-ROOT-SCHEMA-CLOSURE-01-R1` owns exactly
   `src/scouting/contracts/wyscout_schema.py`,
   `tests/contracts/test_w04_wyscout_schema_closure.py`, and its return. Export the
   exact 23 complete transitive closed schemas in the accepted order, including the
   one-lineup-row semantics, exact rejected-field traversal and each emitted
   artifact's Arrow schema/key roster. It writes no aggregate or product byte.
10. Its independent review owns only the fixed review and return, regenerates all 23
   schema byte streams/digests and attacks omissions, aliases, forward edges,
   cycles, placeholders and a 24th root.
11. Master-only `W04-WYSCOUT-V2-AGGREGATE-MATERIALIZATION-01-R1` owns exactly
    `src/scouting/contracts/wyscout_aggregates.py`,
    `scripts/materialize_wyscout_v5_contracts.py`, its test, the exact two v2
    preimage JSON files, and verification report. Materialize the eight-key schema
    bundle first, hash it once, insert its real digest into the ten-key product
    contract, and hash once. No product/run path is written.
12. Its independent review owns reports only and reproduces the 23 content digests,
    both aggregates, 23/8/10/25/9/15 rosters, sole two-key complete-manifest
    semantic formula and all substitution attacks. The master then reruns the
    complete repository gate.

#### Lane B — bounded readers and publisher

After Gate 1, publisher work may run in parallel with Lane A. The context adapter
starts after Packet 6 review because it consumes the accepted season helper. These
write sets are path-disjoint from Lane A.

13. `W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-01-R1` owns only
    `src/scouting/sources/wyscout_vertical_slice.py`, its focused unit test, and
    return. It no-follow verifies the exact match member and ordinal, reproduces
    source/raw/season/bench/substitution bindings, consumes the sole season helper,
    joins the accepted identity bundle and verified `1768`-action population, and
    returns immutable context. Its reviewer owns reports only and attacks every
    omission/addition/type/ordinal/cross-match/team/player/season/lineup mutation.
14. `W04-STAGED-IMMUTABLE-PUBLISHER-01-R1` owns only
    `src/scouting/storage/wyscout_publication.py`,
    `tests/unit/test_w04_staged_product_publisher.py`, and its return. Implement the
    exact named-root, descriptor-relative, `O_NOFOLLOW`, `0700`/`0600`, sidecar-free,
    same-filesystem no-replace promotion with exact replay idempotency and retained
    failure evidence. Its reviewer owns reports only and reproduces all path,
    symlink, mode, link-race, unequal-final, partial, recheck and cross-device
    attacks. It must not modify `GuardedStorage` or the accepted Parquet encoder.

#### Lane C — runtime and one exact temporary-root vertical slice

15. After Lane A, Packet 13 and Packet 14 are accepted,
    `W04-WYSCOUT-RUNTIME-ADMISSION-CONTROL-01-R1` owns only
    `scripts/admit_wyscout_v5_runtime.py`, `scripts/launch_wyscout_v5.py`, focused
    security/e2e tests and its return. It implements the already-authorized R20
    v15 admission, exact 30-resource digest, child/result framing, immutable code
    manifest readback, one build hash and post-hash rebuild invocation. It cannot
    invoke a real product writer in this packet. Its independent reviewer owns
    reports only and must reproduce R20's environment, executable, bytecode,
    descriptor, path, one-hash and two-root attacks.
16. `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-01-R1` owns only new files beneath
    `src/scouting/data_products/wyscout/` (`bronze.py`, `actions.py`, `lineups.py`,
    `possessions.py`, `player_match.py`, `silver_manifest.py`, `gold.py`,
    `temporal_boundary.py`, `rebuild.py`, `__init__.py`),
    `scripts/rebuild_wyscout_v5.py`, its e2e/security tests and return. In isolated
    exact-root mirrors only, it emits `1768` Bronze Action rows plus the
    schema-derived rejected-field population; exactly `13` checked Actions, `2`
    checked Possessions, `1` exact right-censored LineupStint, `1` checked Fact;
    and one Gold row `(2,2,1,2)`. It guard-checks every capability before
    serialization, publishes product before manifest, derives all three layer
    semantics only from R4's two-key complete-manifest wrapper, reconciles parents,
    derives one Gold/one boundary population, and writes the 15-key then nine-key
    receipts in accepted order.
17. `W04-WYSCOUT-FOUR-FEATURE-VERTICAL-SLICE-REVIEW-01-R1` owns only one review and
    return. It reconstructs source facts independently, runs two isolated rebuilds,
    executes the full adversarial matrix from the prior acceptance audit, and
    confirms the real repository product roots remain absent. `PASS` with zero
    findings is mandatory.
18. The master inspects every byte, reruns the complete repository gate, executes
    the accepted launcher once into the real local roots, executes a second
    isolated deterministic rebuild, guard-reads/reconciles every product,
    manifest and receipt, and records final W04 evidence. Any mismatch is bounded
    rework; no product is published before this point.

The serial critical path is therefore:

```text
failed R1 review archived byte-identically -> combined test-only R2
  -> fresh PASS at decision-fixed R1 review path plus additive R2 return
  -> master acceptance -> complete repository gate
  -> build contract -> review -> 23-root schema -> review
  -> v2 aggregates -> review -> complete repository gate
  -> runtime admission/control -> review -> temporary-root vertical slice
  -> independent slice review -> complete master gate -> real local publication
```

The publisher can proceed beside the build/schema lane after Gate 1; the context
adapter can proceed beside schema/aggregate work after the build-contract review.
No other parallelization is safe because the remaining digests and runtime inputs
are serial dependencies.

## Tests run

- command: fixed SHA-256 reproduction with `shasum -a 256`
  - exit status: `0`
  - result: all seven packet values matched twice.
- command: complete read of `AGENTS.md`, the packet and every `read_first` input;
  bounded symbol/path and progression-assertion inventory
  - exit status: `0`
  - result: exact existing/missing surfaces and the three unconditional stale
    assertions identified.
- command: independent locked/no-sync source/member/UUID/lineup probe through
  `uv run ... python -B`
  - exit status: `0`
  - result: exact manifest/member/row digests, `380` rows, ordinal `379`, strict
    season `181150`, all five UUIDv5 outputs, one bench row and sole minute-82
    substitution reproduced.
- command: locked/no-sync Ruff format, Ruff lint and mypy over the three tests
  requiring progression correction
  - exit status: `0`
  - result: three files formatted; lint and typing passed.
- command: `PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q -p no:cacheprovider` over season/lineup, build-product, R21 cross-authority and R21 control-preimage tests
  - first exit status: `2`
  - result: sandbox denied read access to the existing external uv cache; no test or
    repository code ran and no file changed.
  - approved read-only rerun exit status: `0`
  - result: `163 passed in 3.62s`.
- command: exact real product-root and missing-surface inventory
  - exit status: `0`
  - result: all seven real product/manifest/run roots and every listed future
    build/schema/aggregate/adapter/publisher/runtime/product path are absent.

## Artifacts/evidence

- this audit:
  `reports/reviews/W04/returns/W04-POST-CORRECTION-PROGRESSION-AUDIT-01-R1.md`
- additive decision:
  `reports/reviews/W04/authorities/wyscout-season-lineup-product-binding-decisions-v1.json`
- accepted prior build authority:
  `reports/reviews/W04/authorities/wyscout-build-product-authority-acceptance-v1.json`
- exact source-completion index:
  `data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`

## Risks

- P0: the failed R1 review and return must first be preserved byte-identically at
  the exact archive paths and hashes specified above. Only then may the fresh
  reviewer replace the decision-fixed live review path; neither archive nor
  decision may be overwritten.
- P0: allowing real product roots merely because an authority acceptance exists
  would bypass build/schema/aggregate/runtime/publication gates. The three test
  changes must prove isolated no-side-effects, not grant publication.
- P0: the build contract must integrate the accepted season/lineup reference only
  within `authority_rows`; a new projection key or second build hash is forbidden.
- P0: the exact one lineup row is required Silver evidence. Zero, two, inferred
  terminal/minute/per-90 values, or a lineup-count feature fail closed.
- P1: complete 23-root schema closure must freeze rejected-field traversal and all
  emitted Arrow/key rosters before the product producer can serialize them.
- P1: the runtime R20 v15 admission/control surface is substantial but already
  authorized. Difficulty or duration is not permission to omit or weaken it.

## Follow-up items

- Issue one combined test-only R2 for the exact three test paths above, obtain a
  fresh independent R2 `PASS`, then create master acceptance and run the complete
  repository gate before the build-contract packet.

## Scope confirmation

- no Git operations: confirmed
- no unauthorised dependency or lockfile changes: confirmed
- no edits outside `allowed_paths`: confirmed
- no authority, test, source, runtime, config, data, product, manifest, receipt,
  build, verification, phase-gate or orchestration file changed: confirmed
- no provider/network, cloud, container, hosted CI, endpoint, remote, deployment or
  publication action: confirmed
