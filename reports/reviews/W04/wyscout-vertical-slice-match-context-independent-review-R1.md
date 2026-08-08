# W04 selected-match context adapter independent review R1

- task: `W04-VERTICAL-SLICE-MATCH-CONTEXT-ADAPTER-REVIEW-01-R1`
- reviewed at: `2026-08-02T10:05:37Z`
- role: fresh independent W04 selected-match context reviewer
- recommendation: `PASS`
- findings: `P0=0`, `P1=0`, `P2=0`

## Scope and fixed bindings

The review read the packet, every `read_first` path, the candidate, its tests and
the accepted source-completion and identity runtimes. It did not edit producer
bytes. Every fixed binding was reproduced immediately before the final verdict:

| Binding | Required SHA-256 | Reproduced | Result |
| --- | --- | --- | --- |
| selected-match adapter | `2479f0db6eb949cb8856aa4efee5005f5531619726751230486039251e5fe4a3` | exact | PASS |
| producer tests | `a3a4d26edb34d53a66dc6e36a6b9c75f102942731846dc08d301feba064d165e` | exact | PASS |
| producer return | `a4f9fca7125ec41b26fc0b52af62a2d48225fe677f11b12f649dd563758b3591` | exact | PASS |
| completion adapter | `b1cdb309c3d81e7a3b0606987fdf6c456d61a66c393ca681d93e212e805ac43c` | exact | PASS |
| identity runtime | `a9bc386ec759252464e5d6b4b14b95082a3a4218a9a48cbea97ffbcbd11b95cd` | exact | PASS |
| match member | `620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29` | exact | PASS |

## Independent real-source reconstruction

The source facts below were derived directly from the accepted local files with
a fresh strict duplicate-key JSON decoder and an independently written canonical
JSON/framing implementation. Candidate constants and test fixtures were not used
as fact authority.

### Exact match member

- `archive-members/matches_England.json` is a regular `0600` file with link count
  one, size `1,694,720`, physical SHA-256 `620725c2...da3fe29`, and exactly `380`
  object rows.
- Source match `2499719` occurs once and only at ordinal `379`.
- Independently canonicalizing that row produced `3,960` bytes and raw-record
  SHA-256 `1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.
- Its strict values are competition `364`, season integer `181150`, source UTC
  clock `2017-08-11 18:45:00`, and exact team key/team-ID pairs
  `(1609,1609)` and `(1631,1631)`.
- Player `285508` occurs once on team `1631`'s bench, zero times in that lineup,
  and its sole substitution involvement is strict row
  `(playerIn=285508, playerOut=192748, minute=82)`.

### Identity and season bindings

The accepted identity bundle is `91,420,676` bytes with physical SHA-256
`4127705a...1fd1e80`; it has exactly `5,594` current rows. Direct row selection
found one `RESOLVED` row for each required source identity. Fresh UUIDv5
derivation from source namespace
`urn:scouting-intelligence:source:wyscout-soccer-match-events-figshare-v5`
reproduced:

- competition `364` -> `cb5c5317-fa4a-571e-93dc-ef6ce482eab7`;
- teams `1609` / `1631` -> `b5f2dd3c-0166-5384-99fa-0ed47cc7e44c` /
  `5b353635-819b-5bd1-8ca2-5a7364042a96`;
- player `285508` -> `be8da881-2b15-513f-978f-6bb3865bc8e2`;
- match `2499719` -> `bad97950-6fac-5cf0-a93c-094f91abbb9b`; and
- bounded season name `figshare-v5:181150` ->
  `4696aa1f-b512-5d18-af79-33cf031455cf`.

The five bundle rows also bind the expected master/member paths, ordinals and raw
digests; the match row independently binds ordinal `379` and raw digest
`1cc084...f74d86`.

### Exact checked event population

The independent event probe opened and hashed all of
`archive-members/events_England.json`: `188,888,614` bytes, physical SHA-256
`301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad`,
and exactly `643,150` rows. A fresh strict projection selected `1,768` unique
`(source ordinal, event ID)` pairs for match `2499719`. Sorting by the accepted
period/elapsed/ordinal/event tuple and independently reproducing the framed
membership formula yielded exactly:

| Period | Rows | Membership SHA-256 |
| --- | ---: | --- |
| `1H` | 901 | `473174accd75001471b64844afb2e49a88fee1c880c7e4818d26f02f1887b91b` |
| `2H` | 867 | `b9b2ef109ffc68aca6c5f218e4c74269378c62ed44b2d9dcacc58eca04be8c16` |

The unmocked public adapter was then executed against the exact real roots. It
recomputed/reopened the accepted identity bundle and source-completion evidence
and returned the same match ordinal/digest, five identity bindings, season UUID,
minute `82`, `1,768` actions and both period counts/digests.

## Candidate and adversarial audit

The candidate admits only the three exact absolute repository roots and all three
accepted caller digests. Match bytes are read through descriptor-relative,
no-follow traversal; the selected file must be regular, `0600`, single-link,
metadata-stable, exact-size and exact-digest before decode. Exact row cardinality,
selection, canonical raw digest, strict integer/type checks, team/lineup bindings
and the minute-82 substitution are all fail-closed.

The identity join calls the accepted source-complete read/recompute boundary and
requires exact bundle identity plus one exact resolved row per required binding.
The event join calls the accepted whole-member loader, revalidates index address,
scope, canonical order, unique identities, raw digests, exact indexed population,
period memberships and the opaque checked capability. Returned match JSON is
recursively frozen; the enclosing dataclasses, action tuples, raw action mappings
and canonical bytes are immutable.

A fresh 30-case mutation matrix, separate from the producer tests, rejected all
of the following:

- row truncation/addition, wrong ordinal and duplicate selected match;
- string/Boolean source IDs, competition/season/clock/team drift;
- bench omission, lineup addition, cross-team player injection, substitution
  omission/duplication and string minute;
- missing, added, duplicated, reordered, cross-match and cross-member events;
- event raw-digest, index-address and completion-capability substitution; and
- missing, duplicate, unresolved and wrong-canonical identity rows.

The producer suite additionally covers selected-row raw additions, unsafe mode,
symlink/directory/hard-link members, alternate/relative roots, caller-digest
drift, substitution-out/extra-key cases and nested mutation attempts. Static call
inspection found no file/product/manifest/receipt/run/staging writer, provider or
network surface in the candidate. After the unmocked proof, the real Wyscout
inventory still contained only the accepted identity queue/bundle and source /
source-completion manifests; no `runs/w04` tree or product byte existed.

## Reproduced gates

| Command | Exit | Result |
| --- | ---: | --- |
| `uv run ruff format --check src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py` | 0 | 2 files already formatted |
| `uv run ruff check src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py` | 0 | all checks passed |
| `uv run mypy src/scouting/sources/wyscout_vertical_slice.py tests/unit/test_w04_wyscout_vertical_slice_context.py` | 0 | no issues in 2 files |
| `uv run pytest -q tests/unit/test_w04_wyscout_vertical_slice_context.py tests/unit/test_wyscout_source_completion_index.py tests/unit/test_wyscout_identity.py` | 0 | 129 passed in 12.50s |
| `uv run bandit -q -r src/scouting/sources/wyscout_vertical_slice.py` | 0 | no findings |
| `uv run lint-imports` | 0 | 3 kept, 0 broken |
| `uv run python scripts/verify_local_only.py` | 0 | PASS; zero remotes, main, guard active, one root uv project, no external/deployment surface |
| fresh strict match/UUID probe | 0 | all physical, row, lineup and UUID facts reproduced |
| fresh strict 643,150-row event/framing probe | 0 | exact 901/867 counts and both digests reproduced |
| unmocked exact-root public adapter proof | 0 | exact context and 1,768 checked actions reproduced |
| fresh 30-case mutation matrix | 0 | 30/30 rejected |

## Findings and recommendation

- P0: none.
- P1: none.
- P2: none.

`PASS` with `P0/P1/P2=0/0/0`. The adapter is a bounded read-only verifier, not a
product materializer. Its deliberate full source-complete identity recomputation
and whole England-event read have bounded local runtime/memory cost, but preserve
the accepted completeness and no-invention guarantees. No residual correctness,
security, leakage, scope or local-only finding blocks master acceptance.
