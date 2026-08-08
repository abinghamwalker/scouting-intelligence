# W04 R21 control preimages — fresh independent review R1

## Review identity and recommendation

- task ID: `W04-CONTROL-PREIMAGE-REVIEW-01-R1`
- role: fresh independent R21 control-preimage reviewer
- product-contract candidate:
  `configs/schema/wyscout-v5-product-contract-preimage-v1.json`
- schema-bundle candidate:
  `configs/schema/wyscout-v5-schema-bundle-preimage-v1.json`
- focused test:
  `tests/contracts/test_w04_r21_control_preimages.py`
- recommendation: `PASS`
- finding cardinality: `P0=0`, `P1=0`, `P2=0`

I recommend `PASS` for these exact candidate bytes. The two preimages are
canonical, inert sibling control artifacts that faithfully materialize the
accepted R21 clauses. The focused test checks the exact byte identities and
closed structures, and it rejected every independent negative mutation applied
during this review. I found no P0, P1, or P2 defect.

This recommendation is not self-acceptance. It does not accept or create field
v2, possession v2, the supported-feature route, the final cross-authority test,
any dependency set, any build identity, or any data product. Only the master may
accept this review and authorize the next serial packet.

## Scope and complete readback

I read the packet and every listed authority in full before reaching a merits
conclusion:

- repository `AGENTS.md`;
- `orchestration/task_packets/W04-CONTROL-PREIMAGE-REVIEW-01-R1.yaml`;
- all 4,516 lines and 245,957 bytes of immutable
  `reports/reviews/W04/wyscout-schema-design-R20.md`;
- all 1,254 lines and 59,565 bytes of accepted
  `reports/reviews/W04/wyscout-schema-design-R21.md`;
- all 783 lines of
  `reports/reviews/W04/wyscout-schema-design-independent-review-R15.md`;
- the complete R21 master-verification record;
- both complete one-line canonical preimages, not excerpts or pretty-printed
  substitutes;
- all 569 lines and 18,992 bytes of the focused test;
- all 98 lines of the producer return;
- the complete producer master review and master verification; and
- the complete subagent return template.

The readback was independent of the producer's conclusion. I reconstructed the
bytes and structures directly from the accepted R20/R21 authorities, inspected
the test assertions line by line, ran the mandated checks, and challenged the
test with separate in-memory corruptions.

The controlling immutable design hashes reproduced as:

```text
R20 physical SHA-256
8cb2f0d4d4015484453491f1846bd5bd0f41e8b8f11d8e52c0fab81b40078047

R21 physical SHA-256
faff34cc5f8c976809f58d7847038aafd39eac8ac68f6c418d717f74e6287020

R15 physical SHA-256
262fbf6f4cc3f239daebb8db69059d46125415647d58ffb432b630c44353c3aa
```

Those values equal the authority links and accepted verification evidence.

## P0, P1, and P2 findings

### P0

None.

### P1

None.

### P2

None.

No lower-severity observation has been omitted in a way that changes the
recommendation. The unresolved descendant-authority and product obligations are
intentional later-gate work, not defects in these two bounded preimages.

## Shell-only preflight and chain of custody

Before reading R20/R21 and before invoking Python, I created the required
shell-only repository/site inventory and retained it at:

```text
/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.pre.inventory
```

The inventory schema is:

```text
kind|path|size|mode|link|mtime_epoch|first32_hex|sha256
```

For every `.pyc` it records the complete file SHA-256 and first 32 bytes. For
every `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, or `.cache`
directory it records the path metadata and the first 32 bytes plus SHA-256 of a
complete read-only tar stream of that directory. Candidate paths were sorted
under `LC_ALL=C`. The retained inventory includes:

```text
repository pycs:       59
site pycs:           1,086
total pycs:          1,145
repository __pycache__ dirs: 19
site __pycache__ dirs:       131
total __pycache__ dirs:      150
required records plus header: 1,296
```

The shell capture also retained three deliberately broader diagnostic rows for
`.pytest_cache`, `.mypy_cache`, and `.ruff_cache`. Those rows are outside R20's
defined repository/site `.pyc` plus `__pycache__` inventory and outside the
producer/master 1,145/150 cardinality. They were retained so that the review
would not discard evidence, but they are not silently counted as Python cache
directories. The required 1,296-line preflight subset SHA-256 is:

```text
b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777
```

No inventory entry was cleaned, repaired, renamed, truncated, or deleted.
Every Python/test command used `PYTHONDONTWRITEBYTECODE=1`, locked/no-sync uv,
and `python -B` or pytest through the same locked environment. The standalone
mutation helper asserted both the environment value and
`sys.dont_write_bytecode` before importing further file-backed modules.

The terminal required postflight is recorded below after the final report
checks. It is byte-identical to the required preflight subset; no `.pyc` or
`__pycache__` chain-of-custody drift occurred.

## Exact canonical-byte reconstruction

The product-contract file is exactly 5,473 bytes and one LF-terminated physical
line. Its independently reproduced physical SHA-256 is:

```text
0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293
```

Strict UTF-8 parsing followed by compact JSON serialization with Unicode
code-point-sorted keys, retained array order, no insignificant whitespace,
`ensure_ascii=False`, `allow_nan=False`, and exactly one terminal LF reproduces
the physical bytes byte-for-byte. Therefore its canonical SHA-256 is also:

```text
0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293
```

The schema-bundle file is exactly 6,104 bytes and one LF-terminated physical
line. Its independently reproduced physical SHA-256 is:

```text
a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f
```

The same strict parse and canonical serialization reproduces its physical bytes
byte-for-byte, so its canonical SHA-256 is also:

```text
a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f
```

Both files decode as strict UTF-8; contain no carriage return; contain exactly
one LF, at EOF; and contain NFC strings throughout. Because physical bytes equal
the sole canonical rendering, duplicate keys, reordered object keys, alternate
escaping, extra whitespace, or a missing/extra terminal LF cannot pass the
pinned digest and canonical-byte checks.

## Product-contract structure

The product object has exactly these nine top-level keys in canonical order:

```text
authority_links
layer_order
manifest_receipt_templates
path_templates
policy
preimage_id
preimage_schema_version
primary_key_contracts
serializer_ownership
```

Identity is exact:

```text
preimage_id = w04-wyscout-product-contract-preimage-v1
preimage_schema_version = w04-product-contract-preimage-v1
layer_order = [BRONZE,SILVER,GOLD]
```

The closed policy is exactly:

```text
control_plane_only = true
no_product_before_gate = R21_COMPLETE_GATE_PASS
product_bytes_forbidden = true
```

The `authority_links` object has exactly four keys. It binds immutable R20 ID and
digest and accepted R21 ID and physical digest. It contains no explanatory angle
bracket placeholder.

### Path rows

There are exactly 17 `path_templates` rows, in the R21 order. Each row has only
`path_role` and `relative_template`. The roster covers:

1. three Bronze record/quarantine roles;
2. eight Silver roles: competition, team, player, match, action, lineup stint,
   possession, and player-match fact;
3. one Gold player-window role;
4. three layer manifests; and
5. two rebuild/temporal receipt roles.

All templates are the exact R21 descriptor strings. They are relative and
contain only declared placeholders. The known Bronze template uses the literal
`records`, the quarantine templates retain their exact fixed segments, the
Silver paths retain `source_partition`, and the Gold path retains its full
competition/window/cutoff partition sequence.

### Serializer ownership

There are exactly ten owner rows, sorted by owner:

```text
actions.py
bronze.py
entities.py
gold.py
lineups.py
player_match.py
possessions.py
rebuild.py
silver_manifest.py
temporal_boundary.py
```

Every row has only `owner` and `path_roles`. Flattening all `path_roles`
produces the exact 17-role path roster with cardinality 17 and uniqueness 17.
Every path role is owned once and only once. In particular, Bronze owns all
three Bronze rows plus its manifest; the Silver family owners remain disjoint;
Gold owns its player-window row and manifest; rebuild owns only its invocation
receipt; and temporal-boundary owns only its boundary receipt.

### Primary keys

There are exactly two primary-key rows, each with only `key_fields` and
`schema_role`.

`SILVER_PLAYER_MATCH_FACT` retains exactly:

```text
tenant_id
source_manifest_id
match_id
player_id
player_match_fact_schema_version
```

`GOLD_PLAYER_WINDOW` retains exactly:

```text
tenant_id
player_id
competition_id
season_id
role_context_id
role_context_version
window_definition_id
window_start_utc
window_end_utc
feature_cutoff_ts
dependency_lineage_hash
```

No key is invented for another descriptor, and `feature_schema_hash` does not
replace either accepted key member.

### Manifest and receipt rows

There are exactly five `manifest_receipt_templates` rows, each with only
`artifact_role`, `owner`, and `relative_template`. Their roles are path-template
rows 13 through 17 in the same order. Every template is byte-equal to the
corresponding path row and every owner is equal to the unique ownership mapping.
This prevents an alternate receipt or manifest vocabulary.

## Schema-bundle structure

The schema-bundle object has exactly these six top-level keys in canonical order:

```text
authority_links
dependency_order
descriptors
feature_schema_hash_placeholder
preimage_id
preimage_schema_version
```

Identity is exact:

```text
preimage_id = w04-wyscout-schema-bundle-preimage-v1
preimage_schema_version = w04-schema-bundle-preimage-v1
```

The authority-links object is byte-semantically equal to the product preimage's
four-key object.

### Descriptor roster and DAG

There are exactly 16 descriptor rows. Each has exactly:

```text
depends_on
descriptor_id
descriptor_version
role
surface_kind
```

The 16 descriptor IDs are unique. `dependency_order` is byte-semantically equal
to the ordered descriptor-ID projection of `descriptors`. Every `depends_on`
array is duplicate-free, every target exists, and every target is earlier than
its source row in `dependency_order`.

The roster begins with the source-record envelope, then the Bronze surfaces,
Silver surfaces, Gold surface, layer manifest, rebuild receipt, and temporal
boundary receipt. The layer-manifest row depends on the exact twelve earlier
Bronze/Silver/Gold surfaces. The rebuild receipt depends on the earlier layer
manifest. The temporal boundary receipt depends on the earlier Gold surface and
layer manifest. No self-edge, forward edge, unknown target, duplicate edge, or
cycle exists.

Every row's `surface_kind` is exactly:

```text
CONTRACT_SURFACE_DESCRIPTOR_ONLY_NOT_IMPLEMENTED_SCHEMA
```

No descriptor is represented as a Pydantic model, Parquet schema, serializer,
table, manifest, receipt, or implemented product.

### Typed unresolved feature placeholder

The feature placeholder has exactly five keys and values:

```text
concrete_value = null
json_type = string
pattern = ^[0-9a-f]{64}$
resolution_source =
  accepted:w04-wyscout-supported-count-features-v1:candidate_sha256
state = TYPED_UNRESOLVED_UNTIL_SUPPORTED_FEATURE_ACCEPTANCE
```

The JSON null is a typed unresolved sentinel, not a concrete feature hash. No
feature digest is present elsewhere in either preimage.

## Sibling graph and absence of prohibited edges

The two preimages contain byte-equal authority links and have the same sole
design parent, accepted R21:

```text
R21 -> product-contract preimage
R21 -> schema-bundle preimage
```

Neither preimage contains the other's ID or digest. The valid topological
presentations are both:

```text
R21, product-contract preimage, schema-bundle preimage
R21, schema-bundle preimage, product-contract preimage
```

The order of sibling materialization therefore creates no dependency. The
schema descriptor graph is internal to the schema-bundle value and has only
earlier descriptor edges; it does not create an authority edge to the product
preimage.

Across each complete parsed object, the only 64-lowercase-hex values are the
accepted R20 and R21 authority hashes. Consequently neither preimage contains:

- its own physical or canonical digest;
- the sibling's physical or canonical digest;
- a field-v2, possession-v2, supported-feature, dependency, or acceptance
  digest;
- a concrete feature schema hash;
- a build ID or run ID;
- a clock or canonical UTC instant;
- a UUID runtime value;
- a root, host, absolute path, environment observation, or mutable runtime
  value; or
- a generated product, manifest, or receipt byte or observed output identity.

The product path strings and schema descriptor IDs are the expressly authorized
inert contract descriptors. They are not filesystem observations, implemented
schemas, or output authority.

## Focused-test quality and mutation challenge

I read all 569 lines rather than relying on the six passing test names. The test
pins both complete physical/canonical file hashes and independently asserts the
closed semantic structures. Its coverage includes:

- exact canonical UTF-8 bytes, terminal LF, and NFC strings;
- exact top-level and nested key sets;
- all product cardinalities and full ordered expected constants;
- once-only serializer ownership;
- exact primary keys and receipt/manifest correspondence;
- all 16 descriptor identities, versions, roles, dependency arrays, and the
  descriptor-only literal;
- identical dependency order and earlier-only edges;
- the typed unresolved feature placeholder;
- equal authority links and the two sibling-first presentations;
- absence of own/sibling/future/runtime digest and value classes; and
- absence of all seven product destination roots.

I then loaded the test module under locked/no-sync/no-bytecode controls and
applied 14 independent in-memory mutations without modifying a repository file.
Every mutation raised the expected assertion:

```text
product-extra-top-key
product-missing-path-row
product-duplicate-owner
product-primary-key-drift
product-receipt-template-drift
schema-forward-edge
schema-dependency-order-drift
schema-surface-overclaim
schema-concrete-feature-hash
sibling-authority-link-drift
product-own-digest-edge
product-sibling-digest-edge
schema-build-id-edge
schema-absolute-host-value
```

The same harness first ran three unmodified positive semantic checks
successfully. This challenge demonstrates that the exact assertions, not merely
the pinned hashes, reject representative structural, ownership, DAG,
premature-feature, sibling/self-edge, downstream, and runtime contamination.
Conversely, the pinned complete-file hashes ensure that any otherwise overlooked
physical or semantic byte change also fails.

I found no test-quality defect at P2 or above.

## Destination and descendant absence

The following exact seven destination roots were absent both before report
creation and after the required checks:

```text
data/working/wyscout/v5/bronze
data/working/wyscout/v5/silver
data/working/wyscout/v5/gold
data/manifests/wyscout/v5/bronze
data/manifests/wyscout/v5/silver
data/manifests/wyscout/v5/gold
runs/w04/wyscout-rebuild
```

I also checked every named next-stage descendant path. All field-v2 decision,
candidate, review, and acceptance paths are absent. All possession-v2 decision,
candidate, review, and acceptance paths are absent. The supported-feature
decision, candidate, review, and acceptance paths are absent. The final
cross-authority test path is absent. A filename scan found no Wyscout
Bronze/Silver/Gold/rebuild/field/possession/feature implementation artifact
under `src`, `scripts`, `tests`, `configs`, `reports`, `data`, or `runs` beyond
the reviewed control evidence.

Therefore this packet has not created or acquired field, possession, feature,
data-product, serializer, manifest, receipt, build, model, or product
implementation.

## Local-only boundary

The required local-only verifier passed all 25 checks. It confirmed:

- zero configured Git remotes;
- the active local-only pre-push guard;
- one root `pyproject.toml`, one root `uv.lock`, and one root `.venv`;
- Python 3.12.12 and the exact project Python constraint;
- all eight expected dependency groups;
- no Git/direct-URL dependency;
- no alternate package manager or Node manifest;
- no hosted CI/deployment or container definition;
- no external service dependency;
- the accepted embedded/container-free authority;
- structured config parse success;
- no outside-root or prohibited-URL config;
- the approved directory skeleton;
- no outside-root symlink; and
- the root `.venv` remains ignored.

No sync, install, provider access, network acquisition, external model call,
cloud action, container action, endpoint, hosted CI, deployment, remote
repository operation, or Git command was performed by this reviewer.

## Commands and results

The following bounded commands form the review evidence:

```text
shell-only preflight inventory
exit 0
required subset: 1,296 lines; SHA-256
b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777
broad diagnostic capture: 1,299 lines; SHA-256
1db30090454bb2e5ce0841e383285bb214221a57a7aba00f0c084c27e1c04648

shasum -a 256 <R20 R21 R15 both-preimages focused-test>
exit 0
all expected physical hashes reproduced

wc -l -c <both-preimages focused-test>
exit 0
5473/1, 6104/1, and 18992/569 reproduced

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync pytest -q
tests/contracts/test_w04_r21_control_preimages.py
first restricted-sandbox attempt: exit 2 because the existing uv-cache
`.git` path was unreadable; no test ran and no repository file changed
approved existing-cache read rerun: exit 0; 6 passed in 0.09s

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -c
<independent positive and in-memory negative mutation harness>
exit 0
3 positive semantic checks passed; 14 negative mutations rejected

PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B
scripts/verify_local_only.py
exit 0
status PASS; 25 checks passed; failures empty

shell seven-destination and named-descendant absence checks
exit 0
all seven destination roots and all named downstream authority/test paths absent
```

The packet acceptance commands were rerun after the final report edit and are
recorded in the companion return. The terminal inventory command was then
repeated byte-for-byte and compared with `cmp`.

## Terminal inventory comparison

After the last report edit and required acceptance checks, I repeated the exact
preflight inventory construction into:

```text
/tmp/W04-CONTROL-PREIMAGE-REVIEW-01-R1.post.inventory
```

`cmp` reports byte identity for the packet-defined repository/site `.pyc` and
`__pycache__` inventory. Both required files contain 1,296 lines and both hash
to:

```text
b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777
```

There was no `.pyc` creation, deletion, rename, content/header mutation,
mode/link/mtime change, or cache-directory drift. No cleanup or repair was
attempted. The broader diagnostic capture recorded one expected pytest-tool
cache side effect: `.pytest_cache` retained the same path, size, mode, link, and
mtime, but its recursive tar digest changed while pytest ran. That tool cache is
not a repository/site `__pycache__` directory and is not part of the required
R20 inventory. The differing broad pre/post files and their one-line diff remain
preserved under `/tmp`; they were not cleaned or rewritten into equality.

## Residual risks and bounded obligations

The following are future obligations, not findings in this packet:

- field v2 still needs its distinct decision/candidate producer, independent
  review, and master acceptance;
- possession v2 remains blocked on accepted field v2 and needs its own serial
  route;
- the supported-feature candidate and concrete `feature_schema_hash` remain
  unavailable until their own review and acceptance;
- the cross-authority test, independent review, master gate, and full repository
  gate have not run;
- the preimage path strings and descriptors must never be interpreted as
  implemented products; and
- the seven-root absence result is a truthful bounded review-time observation,
  not permission to create those roots.

None of these obligations warrants a P2 finding because R21 fixes their exact
serial ownership, paths, dependencies, negative tests, and gate boundaries.

## Final recommendation

`PASS`.

The exact product-contract preimage at
`0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293`
and exact schema-bundle preimage at
`a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f`
faithfully materialize the accepted R21 descriptor-only contract. Their
structures, cardinalities, ownership, primary keys, descriptor DAG, typed
placeholder, sibling relationship, canonical bytes, test behavior, destination
absence, and local-only boundary all pass fresh independent review.

Finding count remains `P0=0`, `P1=0`, `P2=0`. This is a recommendation to the
master only; it is not self-acceptance and grants no downstream or product
authority.
