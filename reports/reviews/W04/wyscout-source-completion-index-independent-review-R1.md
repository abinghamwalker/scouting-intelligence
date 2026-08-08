# W04 Wyscout source-completion-index independent review R1

## Disposition

- Packet: `W04-SOURCE-COMPLETION-INDEX-REVIEW-01-R1`
- Role: fresh independent reviewer
- Disposition: **REWORK**
- Open findings: P0 `0`, P1 `1`, P2 `0`
- Acceptance rule: PASS requires zero open P0-P2 findings.

The immutable index, accepted-address pin, population comparisons, strict action
preimage, equal-clock correction, and digest propagation pass their focused checks.
The candidate does not, however, make the completion reader the executable product
construction boundary. Public low-level contracts still produce an accepted
`GoldPlayerWindow` from a caller-selected singleton period carrying an arbitrary
membership digest without invoking any completion-index load, validation, population
comparison, or factory. Calling that route test-only is a convention, not an
enforced restriction, and is expressly insufficient under the review packet.

Product implementation must remain blocked.

## Fixed candidate identity

Every packet binding was recomputed before analysis and matched:

| Material | Expected and observed SHA-256 | Result |
|---|---|---|
| `src/scouting/sources/wyscout_completion_index.py` | `d81acf16302ce47bffe6461181163e1607b8744ca68f75e5719a2e50c7e43285` | match |
| `src/scouting/contracts/wyscout_data.py` | `acf5555d31c931dda6c3575e5b088401847e0b8efc50c50f349ca188ee019aa0` | match |
| `tests/unit/test_wyscout_source_completion_index.py` | `8b4194574e0d362c7ddcf43b3d6787de5672a9a71d1c938b20a5eb70781f2cef` | match |
| `tests/contracts/test_wyscout_data_contracts.py` | `ba01261521923bf2b62ea4a63930f43bc20e2df18fb3028accdf53b90d8e77c1` | match |
| immutable completion index | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | match |
| R2 producer return | `35b65b440ce6da7dd61f93b35e38a52d796f2749c8448f9980d59caccc50447d` | match |

The index is exactly `644037` bytes and records aggregate action count `3071395`.
Frozen R20 and R21 remain respectively:

- `8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047`
- `faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020`

The frozen completion manifest remains
`69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`,
and the accepted source snapshot manifest remains
`8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`.

## Independent source and index reconstruction evidence

The five authorized event members were independently read and recomputed from the
frozen local source. Their digest, size, and top-level JSON row counts were:

| Member | SHA-256 | Bytes | Rows |
|---|---|---:|---:|
| `events_England.json` | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` | 188888614 | 643150 |
| `events_France.json` | `18e6316ab3efd357e99f90847791780e279765ba06b4bd60cf483adba5b9a317` | 186374196 | 632807 |
| `events_Germany.json` | `2612a6f8cbd8209acf39d5e3c7d2a43689138b1134d09b36e23a4b0422a781f3` | 152916631 | 519407 |
| `events_Italy.json` | `b41f2d545b5cf80aeab0f9619e3091dbce159ca8e0a6e2d87ae2daee4d040a84` | 190544685 | 647372 |
| `events_Spain.json` | `b55fabec6624e469b9396100de915eaca334d4457de2c61a887a7a67de79a154` | 184164406 | 628659 |

The independent totals are `902888532` bytes and `3071395` rows. They equal the
five index member reconciliations and aggregate. The index contains exactly those
five members, in fixed order, with period counts `760`, `760`, `612`, `760`, `760`.

The bridge implementation was inspected: `derive_source_completion_index` calls
`build_source_snapshot_manifest` before opening an index member; that bridge measures
the frozen source evidence, verifies the completion-manifest digest and exact closed
document, and the index reader then opens only `_EVENT_MEMBERS` through guarded
descriptor reads.

A real England match-period was independently reprojected from its physical rows:

```text
PERIOD_REDERIVED 2499719 1H 901 901
473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b
473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b
```

The physical population count and recomputed ordered-membership digest exactly equal
the accepted index row.

## Accepted-address and population failure reproduction

An independently constructed self-consistent index with one changed period digest
had content address
`8c5d76e515abc90a9d8a7884af4cb3130d201689d5a56f2caa936446b6f3fade`.
The public validator rejected it as unaccepted. Replacing only its declared address
with the accepted address was also rejected by independent canonical-byte
recomputation:

```text
LOOKALIKE REJECTED completion index address is not accepted
ADDRESS_SPOOF REJECTED completion index canonical address drifted
```

Against the rederived 901-action period, the independent mutation matrix produced:

```text
missing                         REJECTED population count differs from completion index
additional                      REJECTED population count differs from completion index
duplicate                       REJECTED population contains duplicate action evidence
reordered                       REJECTED population is not in canonical action order
stale                           REJECTED population membership differs from completion index
cross_member                    REJECTED supplied population has no indexed match-period
cross_match                     REJECTED population crosses member, match, or period
cross_period                    REJECTED population crosses member, match, or period
whole_period                    REJECTED whole-period omission is forbidden
whole_indexed_period_omission   REJECTED match population omits or adds an indexed period
whole_match                     REJECTED whole-match omission is forbidden
```

The unit suite additionally exercises member/aggregate count drift, member and period
order drift, duplicate period identity, immutable materialization, wrong load
argument before file open, and all four public validation/factory entry points.

## Action preimage and strict semantic reproduction

The action and period frames bind the authorized source member path and digest,
physical ordinal, provider event and match IDs, period/rank/clock token, player/team,
event/subevent, ordered raw tags, projected strict-integer possession tags, and the
Bronze-compatible canonical raw-record digest. The period digest frames every action
in canonical `(period_rank, elapsed_seconds, physical_ordinal, provider_event_id)`
order.

Independent probes rejected string, Boolean, or float coercion for event identity,
match identity, event clock, player/team identity, and tag identity. Missing, null,
string, Boolean, and non-integer-number subevents all remained canonically unmapped,
but produced five distinct action-frame digests because exact raw evidence and the
raw-record digest remain bound. No variant was coerced to integer `10`.

## Equal-clock and provenance reproduction

The exact independent focused regressions passed:

- opposing-team CONTROL at the same clock resolves no group;
- an earlier strictly deterministic group remains when the later clock is ambiguous;
- a contested buffer dependent on the ambiguous cross-team clock remains unassigned;
- source ordinal and provider event ID are not used to choose a simultaneous team.

The completion-index constant is present in row lineage, possession sequence,
Silver possession, Silver player-match fact, Gold, temporal proof and layer manifest.
`dependency_lineage_hash` includes it as a framed named value, and digest drift at
those boundaries is rejected. Causal other-player sequence rows are retained through
possession, Fact and Gold. These are valid closures, but they bind the accepted
digest value; they do not prove that the reader validated the population used to
construct the row.

The Gold model still contains exactly four fields:

1. `action_count`
2. `coordinate_known_action_count`
3. `match_count`
4. `resolved_possession_action_count`

No product/runtime artifact was written by this review.

## Open finding

### W04SCIIDXR1-P1-001 — public Gold construction bypasses the completion reader

`build_possession_period_sequence` and `build_match_period_sequences` correctly
validate a supplied population against the accepted index. Nothing makes those
factories the required executable entry point for the public product contracts.

`PossessionPeriodSequence` remains publicly constructible and exported. Its validator
requires the accepted index digest, but accepts any syntactically valid
`source_completion_membership_sha256` and only reconciles `period_action_count` to the
caller's own `actions` tuple. `SilverAction`, `SilverPossession`,
`SilverPlayerMatchFact`, and `GoldPlayerWindow` are also publicly constructible and
derive their locally consistent counts from that caller-selected sequence and its
selected descendants. Their accepted index constant and dependency-lineage binding
therefore attest to a value, not to execution of the completion reader.

The independent probe loaded the real index, proved that `"9" * 64` is not any
indexed period membership, then replaced every completion load/validate/population/
factory function with a fail-fast function. Ordinary checked constructors still
returned accepted Gold:

```text
BYPASS_ACCEPTED
features={'action_count': 1,
          'coordinate_known_action_count': 1,
          'match_count': 1,
          'resolved_possession_action_count': 1}
membership=9999999999999999999999999999999999999999999999999999999999999999
period_action_count=1
sequence_actions=1
completion_reader_calls=0
```

The probe used no `model_construct`, unchecked copy/update, serializer, filesystem
write, or product artifact. The repository's own standard positive fixture exercises
this exact direct-construction route. The producer return describes low-level models
as test constructs and instructs the future product implementation to consume the
reader factories, but no executable control enforces that instruction.

Required bounded correction:

1. Make every authorized downstream raw-to-Bronze-to-Silver-to-Gold construction or
   materialization entry point execute the accepted completion-reader population
   validation before it can return or write an accepted product.
2. Do not accept a low-level model, fixed digest, arbitrary membership digest,
   Boolean, count, witness, or subset-derived digest as evidence that this happened.
3. Make direct low-level construction explicitly incapable of being consumed by the
   authorized product path, rather than relying on naming, documentation or packet
   instructions.
4. Add a regression equivalent to the probe above: when completion-reader entry
   points fail, downstream accepted product construction/materialization must fail;
   an arbitrary or real-index-copied membership digest without exact reader
   population comparison must also fail.

This is a bounded enforcement correction to the already-authorized completion-reader
boundary. It does not require a feature, provider, dependency, cloud, container,
deployment, storage, rights, R20 or R21 architecture revision.

## Prescribed-check results

| Command | Result |
|---|---|
| Ruff format check on the four packet files | exit `0`; four files formatted |
| Ruff check on the four packet files | exit `0`; all checks passed |
| Mypy on the four packet files | exit `0`; no issues |
| `uv run lint-imports` | exit `0`; 31 files, 49 dependencies, three contracts kept |
| Exact six-module pytest command | exit `0`; all `488` collected tests passed |
| Bandit on the two implementation files | exit `0`; no findings |
| `uv run python scripts/verify_local_only.py` | exit `0`; PASS, 25 checks and zero failures |
| Four focused equal-clock/digest tests | exit `0`; `4 passed in 0.18s` |

The first combined prescribed-check invocation was denied before execution because
the sandbox could not read shared uv-cache metadata. The unchanged exact checks were
rerun with read access and passed. No dependency or environment mutation occurred.

## Scope and recommendation

Recommendation: **REWORK**. Return only W04SCIIDXR1-P1-001 for one bounded correction,
then obtain a fresh independent review before running the complete repository master
gate or resuming product implementation.

- No implementation, test, data, source, manifest, index, frozen authority, R20/R21,
  orchestration, dependency, lock, product or verification byte was edited.
- No provider or network access, external service, cloud, container, hosted CI,
  public endpoint, remote, deployment, product write, Git operation, delegation or
  self-approval occurred.
- Only this review and its mandatory return are reviewer-owned outputs.
