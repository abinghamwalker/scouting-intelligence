# Subagent return — W04-SCHEMA-DESIGN-REVIEW-01-R11

## Status

`REWORK — INVALID INDEPENDENT REVIEW RUN`

No `PASS` or merits-based `REWORK` verdict is issued for the R18 candidate. The
review run was invalidated when a reviewer `uv run --locked --no-sync python -c`
dependency-closure probe imported `packaging` without `-B` or
`PYTHONDONTWRITEBYTECODE=1` and created eleven site pycs outside assigned path
ownership.

## Summary

- Read the complete 4,260-line R18 candidate and the packet's read-first set.
- Reproduced the exact ordered 119-pair profile roster and
  `10/11/26/47/18/4/3` category counts.
- Reproduced strict UUID `ActorId` behavior and canonical-lowercase
  reserialization requirement.
- Parsed exactly twelve required possession predicate fields and the six closed
  decisions including explicit `UNMAPPED`.
- Confirmed the approved field contract-test path and disjoint semantic packet
  ownership.
- Reproduced current logical/physical uv admission, outer 29-name environment,
  both 32-name child environments, version sequence, schema cardinalities,
  24-key invocation/projection intersection, and synthetic H1/H2 equality through
  build ID.
- Reproduced exact EvidenceDependency fields, alias rejection, strict temporal
  cutoff behavior, `L==I==82`, three `.pth` files, 35/21 executable census,
  33/1/1 classes, and interpreter aliases.
- Detected the reviewer-caused bytecode mutation before completing the pyc
  closure.
- Disclosed it immediately and performed no cleanup.
- Stopped all uv/Python and candidate probes when directed by the master.

## Invalidation evidence

The accepted R18 current-root baseline is 1,075 site pycs. The post-import
observation was 1,086. Exactly eleven recent files appeared under:

```text
.venv/lib/python3.12/site-packages/packaging/__pycache__/
```

They are:

```text
__init__.cpython-312.pyc
_elffile.cpython-312.pyc
_manylinux.cpython-312.pyc
_musllinux.cpython-312.pyc
_parser.cpython-312.pyc
_tokenizer.cpython-312.pyc
markers.cpython-312.pyc
specifiers.cpython-312.pyc
tags.cpython-312.pyc
utils.cpython-312.pyc
version.cpython-312.pyc
```

Every file is regular, mode `0644`, link count one, with modification epoch
`1785412176` / `2026-07-30T12:49:36+0100`. Exact sizes and SHA-256 values are in
the independent report. Repository pyc evidence remained 58 files in 19 cache
directories, including 20 pytest-rewrite files.

No pre-probe R11 site census was taken. The “before” value is the accepted R18
and preceding independent baseline, not a contemporaneous R11 snapshot. That
missing preflight and the out-of-scope write make a candidate verdict invalid.

## Finding

`P1-R11-PROCEDURE-01`: the reviewer mutated the operational evidence population
outside the two assigned report paths. This is a review-validity finding, not an
adjudicated R18 candidate defect.

## Changed paths

Only these assigned report paths were intentionally authored:

```text
reports/reviews/W04/wyscout-schema-design-independent-review-R11.md
reports/reviews/W04/returns/W04-SCHEMA-DESIGN-REVIEW-01-R11.md
```

The eleven implicit `.venv` pyc creations are separately disclosed as the
invalidating out-of-scope side effect. They were not deleted, modified, repaired,
or accepted.

## Verification

Not run after invalidation:

```text
uv run --locked --no-sync python -c "from pathlib import Path; p=Path('reports/reviews/W04/wyscout-schema-design-independent-review-R11.md'); s=p.read_text(); assert p.is_file() and p.stat().st_size > 30000; assert 'recommendation' in s.lower()"
uv run --locked --no-sync python scripts/verify_local_only.py
```

The master ordered no more uv/Python commands. These checks must be performed by
the fresh bounded independent review after the baseline is established.

## Prohibitions observed

- No candidate edit.
- No configuration, source, script, test, data, migration, or orchestration edit.
- No provider or network access.
- No implementation or product build.
- No Git operation.
- No delegation.
- No self-approval.
- No pyc cleanup or environment repair.

## Required next action

Close R11 as invalid. The master must decide how to establish a truthful
environment baseline, then dispatch a fresh independent review with a preflight
inventory and process-start bytecode denial for every Python helper. R18 remains
unaccepted by R11.

