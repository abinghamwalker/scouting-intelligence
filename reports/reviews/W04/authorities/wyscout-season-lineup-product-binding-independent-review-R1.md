# W04 season/lineup product-binding independent review R1

Fresh adjudication: `W04-SEASON-LINEUP-PRODUCT-BINDING-REVIEW-01-R2`  
Date: 2026-08-01  
Reviewer: fresh independent W04 season/lineup R2 reviewer

## Verdict

`PASS — AUTHORITY EXACT; PROGRESSION CORRECTION SIDE-EFFECT-FREE`

- Recommendation: `PASS`
- P0: `0`
- P1: `0`
- P2: `0`
- Product implementation permission created by this review: `NO`

The unchanged additive authority correctly closes the bounded season UUID and
one-row lineup population. The three corrected permanent test modules now
validate authority/preimage bytes without requiring intended product roots to
remain absent forever. Each reader is side-effect-free when simulated
destinations are absent, files, directories, or mixed, while the authority and
preimages remain control-plane-only and grant no product permission.

## 1. Frozen evidence admission

Every R2 packet binding was verified before analysis:

| Artifact | Reproduced SHA-256 | Result |
|---|---|---|
| unchanged decision | `3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e` | exact |
| corrected season/lineup test | `3a4ed66082d16cf55a87921a742aea30f5600ad538f2664d0a65fe5be2b9e21f` | exact |
| corrected build-authority test | `12d7379b7594caaea2aed508fd1444cfa307d1911d8d12fb52222d050c0fc73b` | exact |
| corrected R21-preimages test | `6ae725e379a33cd0785b346fe4ddcdca3fdc296ff24a1f78697202834e7d0df6` | exact |
| R2 producer return | `98cc732eeb79341fc7d58885825c808bae9fa3a1ac1beeedcafdb7e3cb885e74` | exact |
| R2 master verification | `e573d849afcac3734c894d5f073871fd0eaf14ce7b3d7916e8c4b177053f6a2a` | exact |
| archived failed review | `431e0cfb98c6bbd94b6baf3cb6878c551028e894770fb02ada771be989fc31ba` | exact |
| archived failed review record | `b1708640631732f304f6c07455ee1530ae0ef800a70276d29fd34b46fc484e3d` | exact |
| retained failed-review return | `8218de5bb7e38114204d8c5a82586ff0718887c3ec3a2a682b216f367d91b547` | exact |
| progression audit | `4fe4b72dc17b50e360453836eb291d02cd0ab3574c59a2ca5e6a19e9bad27cdc` | exact |

The archived failed review is byte-identical, has exactly one canonical machine
record, still recommends `REWORK`, and retains its single P1 finding. It remains
immutable at
`reports/reviews/W04/archive/wyscout-season-lineup-product-binding-independent-review-R1-rework-431e0cfb.md`.
This fresh verdict occupies the exact lifecycle path, review ID, and schema frozen
by the unchanged decision; it does not overwrite or reinterpret the archive or
the retained R1 return.

## 2. Fresh authority reconstruction

The decision is canonical JSON with one terminal LF and all ten ordered bound
inputs reproduce physically. The source manifest and exact
`archive-members/matches_England.json` member reproduce SHA-256
`620725c2e6a58b4db3e574ed6c559136477451d81af543f8a06bd85c3da3fe29`,
1,694,720 bytes and 380 rows. Ordinal `379` is provider match `2499719`, carries
strict integer `seasonId=181150`, and has canonical raw-record SHA-256
`1cc084d5527c8fea222039b9362ddafcf5a69efe9dc3456b541f5f3eebf74d86`.

Independent UUIDv5 reconstruction from the authorized names reproduced source
namespace `89161938-1e8c-53ab-ab52-eba969681833`, season namespace
`afb775b9-a955-5bfc-80cd-3e941ca2f098`, season
`4696aa1f-b512-5d18-af79-33cf031455cf`, match namespace
`20b5206f-dfa5-55b4-84ab-8a336a75073e`, match
`bad97950-6fac-5cf0-a93c-094f91abbb9b`, team
`5b353635-819b-5bd1-8ca2-5a7364042a96`, player
`be8da881-2b15-513f-978f-6bb3865bc8e2`, and lineup stint
`591cdf5b-2281-53c4-8225-150313ca2c01`.

The physical match has target player `285508` exactly once on team `1631`'s
bench, zero times in its starting lineup, and exactly once as `playerIn`, at
minute 82. The exact population is one ordinal-zero right-censored stint beginning
at `[82,83)`, with no terminal interval, elapsed/lower/upper minutes, or per-90
eligibility. String, Boolean, zero, negative, alternate-name/namespace, and
alternate-ordinal attacks fail.

The projection remains the predecessor's exact 25 unique keys. The only
integration member is `authority_rows`; post-hash invocation remains 25 keys,
the one R20 SHA-256 rule is unchanged, and a second hash is forbidden. No identity
kind/root, schema root, feature, Gold row, or population expansion was introduced.

## 3. Progression-correction review

All three corrected modules use the same reviewable pattern:

1. snapshot complete destination state, including absence, kind, mode, size, and
   modification time;
2. install writer tripwires over write-capable `Path.open` modes and path
   creation, link, rename, replacement, deletion, touch, and write methods;
3. load and strictly validate the frozen authority or both canonical preimages;
4. repeat the destination snapshot and require exact equality; and
5. require zero writer calls while retaining the authority/preimage's explicit
   control-plane-only and no-product-permission claims.

The repository-root checks do not create a destination. The isolated tests use
only `tmp_path`, cover all-absent and pre-existing simulated content, preserve
sentinel bytes, and do not make immutable lifecycle semantics depend on filesystem
existence. A later separately gated product therefore cannot disable canonical,
digest, population, lifecycle, or preimage validation.

Independent review extended the producer matrix beyond its parameterization. For
each of the three modules, four isolated states were constructed: all destinations
absent; a destination root that is an existing file; a destination root that is
an existing directory containing a sentinel; and a mixed file/directory/absent
population. All `12/12` before/after snapshots were exact. A direct write attempt
was then made under each module's tripwire; all three raised before the file could
exist and recorded the attempted writer call.

Static and collected-suite inspection found no skip, xfail, environment bypass,
placeholder future gate, future task marker, broad existence waiver, or remaining
unconditional product-root absence gate in the corrected modules. The only other
W04 contract-suite root-absence assertion found is explicitly conditional on its
validated lifecycle not being accepted. No actual product destination was used by
the isolated simulations.

## 4. Executable checks

The exact packet suite passed before this active lifecycle review was written:

- Ruff format: three files already formatted;
- Ruff lint: all checks passed;
- mypy: no issues in three source files;
- focused authority/preimage/R21 suite: `169 passed in 3.81s`; and
- local-only verifier: `PASS`, all 25 checks, zero remotes, active `main`, active
  push guard, Python 3.12.12 root uv environment, and no hosted CI, deployment,
  container, or external-service definition.

The suite is rerun after materialization so the live lifecycle parser must consume
this exact canonical `PASS` record. Passing this review allows only master
acceptance and the downstream gates already required by the frozen authorities;
it does not authorize product construction or publication.

## 5. Final decision

`PASS` with zero findings. The R1 P1 is closed by progression-safe test behavior,
the failed evidence is preserved byte-identically, and no immutable authority or
architectural boundary changed.

```w04-season-lineup-product-binding-review-v1
{"decision_id":"w04-wyscout-season-lineup-product-binding-decisions-v1","decision_physical_sha256":"3afdb2817f0c275e66c4c261310c936e4ad896cd3ef967b136e9686822c5bf9e","findings":[],"recommendation":"PASS","review_id":"w04-wyscout-season-lineup-product-binding-independent-review-R1","review_schema_version":"w04-season-lineup-product-binding-independent-review-v1","reviewed_at":"2026-08-01T12:52:30Z","reviewed_by":"544d24d7-2c34-5111-8de0-ac767a692ab7"}
```
