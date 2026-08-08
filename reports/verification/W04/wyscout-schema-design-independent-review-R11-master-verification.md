# W04 Wyscout schema design independent review R11 — master verification

## Decision

`REWORK`. R11 is an invalid independent review run and issues no R18 merits
verdict. The reviewer imported installed `packaging` modules without Python
bytecode denial and created eleven `.pyc` files outside its two-report ownership
before completing the required site census. The master independently reproduced
the incident and performed no cleanup or repair.

This is a review-process P1, not evidence that the R18 stable source-derived
bytecode authority is wrong. The new files are mapped normal caches for admitted
Packaging sources. The bounded correction is to refresh the truthful operational
snapshot and require a no-write preflight/postflight review harness.

## Artifact integrity and readback

- Independent R11 review: 819 lines, `38,008` bytes; SHA-256
  `8a7e0a65906aeb24f76d6676ad1daadb5311202b78a5fb6af0be5251082df6f8`.
- R11 return: 118 lines, `4,350` bytes; SHA-256
  `bbe396e87fbb2a7f595a62b9ad946e122f5faad10038896621cf7535866999a1`.
- Candidate R18 remains SHA-256
  `d6f81a663a6e7db46e1059f2fee11521f0afde81a79cca3ec9d003d5954f8396`.
- The master read both R11 artifacts completely.
- R11 intentionally authored only its two assigned reports, but CPython's eleven
  implicit `.venv` writes still violate the packet's path-ownership boundary.

## Reproduced incident

The master found exactly these new current-tag files:

```text
.venv/lib/python3.12/site-packages/packaging/__pycache__/__init__.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/_elffile.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/_manylinux.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/_musllinux.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/_parser.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/_tokenizer.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/markers.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/specifiers.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/tags.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/utils.cpython-312.pyc
.venv/lib/python3.12/site-packages/packaging/__pycache__/version.cpython-312.pyc
```

Every file is regular, single-link, mode `0644`, has CPython 3.12 magic
`cb0d0d0a`, and has its exact installed Packaging source sibling. All eleven
share modification epoch `1785412176`, rendered
`2026-07-30T12:49:36+0100`. The master reproduced every size and SHA-256 in the
R11 table.

The observed census is now:

```text
site pycs:                    1,086
site normal lexical names:     973
site distribution mappings:    972
site uv-bootstrap mappings:       1
site pytest rewrites:           112
site optional-six orphan:         1

repository pycs:                 58
repository cache directories:    19
repository mapped normal:         35
repository pytest rewrites:       20
repository exact inert orphans:    3
```

A fresh `uv sync --locked --all-groups` resolved 83 and audited 82 without
changing either the 1,086 site or 58 repository counts. The master then ran all
Python checks with `-B`; site and repository counts remained unchanged.

## Governance disposition

No file was deleted, truncated, rewritten, moved, touched, or accepted through
cleanup. The `.venv` remains ignored and the local-only guard still passes all 25
checks. Git remote output remains empty.

R18's stable pyc authority is source-complete and intentionally independent of
mapped-cache presence, so no schema, dependency, architecture, project root,
rights, storage, Git, or local-only change is required. However, R18 also records
the former exact current-root count in operational evidence and a required test.
A standalone replacement must now:

1. preserve the exact incident evidence;
2. record the truthful 1,086 decomposition;
3. state that later mapped-cache cardinality is an operational preflight result,
   not stable identity or a fixed admission count;
4. require every present pyc to classify and the full preflight inventory to
   remain byte-identical through review/runtime postflight;
5. fail on any unclassified file or any mutation during the bounded run;
6. make health/tests report the actual preflight census rather than a stale
   hardcoded count; and
7. require every review Python helper to start with both `-B` and
   `PYTHONDONTWRITEBYTECODE=1`, with read-only pre/post shell inventories and no
   cleanup.

The next independent review must be performed by an agent other than the R18
producer and invalid R11 reviewer.

## Checks

- Complete R11 review/return readback: PASS; 819/118 lines.
- Artifact sizes/digests: PASS.
- R11 path ownership: FAIL; eleven implicit `.venv` writes.
- Exact eleven-file master inventory: PASS; path/size/mode/link/mtime/magic/source
  sibling/digest reproduced.
- Census: PASS; 1,086 site and 58 repository files.
- Fresh locked sync: PASS; 83 resolved, 82 audited, zero census change.
- R11 report acceptance predicate rerun with `python -B`: PASS.
- Local-only verification rerun with `python -B`: PASS; 25/25.
- `git diff --check`: PASS.
- `git remote`: PASS; empty.

No provider acquisition or network access occurred. No product implementation,
cloud resource, hosted CI, public endpoint, Git remote, container, or deployment
was created.
