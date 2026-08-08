# W04 vertical-slice source adapter independent review R1

Date: 2026-07-31

Verdict: `REWORK`

Open findings: `P0=0`, `P1=1`, `P2=0`.

The exact frozen candidate passes its focused acceptance checks and correctly performs
the whole-member, row-count, index and match-population comparisons before returning.
It is not acceptable yet because one authority-bearing part of every returned action
is still caller-mutable, contrary to the packet's explicit immutable-result contract.

## Fixed-binding verification

All candidate bindings were verified before analysis.

| Binding | Expected | Observed | Result |
| --- | --- | --- | --- |
| implementation SHA-256 | `3050b7a3c0ff47442db973fb18fee70c8bf3256827936739e63f87947cd07bed` | same | PASS |
| source-adapter test SHA-256 | `d01a630f1ce2c345597dde7fef81589ca14e8690515e67d8ff476d1f4063423d` | same | PASS |
| producer-return SHA-256 | `c14691f01e8575d91e06882bcd2e1c78ee628d6993d1c89391590b93e957a0b1` | same | PASS |
| completion-index SHA-256 | `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df` | same | PASS |
| England member SHA-256 | `301599543aa1a7fa457bb8ef33c9fe860bf81dca65d418d618d68abcda3defad` | same | PASS |
| England member size | `188888614` | `188888614` | PASS |

The accepted index remains at
`data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`.

## Confirmed behavior

- Caller pins for index address, exact member path and strict positive match ID are
  rejected before `_read_verified_member` is reached.
- Valid execution verifies stable source-manifest bytes, loads and validates the
  content-addressed index, nofollow-reads and hashes the complete admitted member,
  requires all `643150` decoded rows, and withholds output until those checks pass.
- Physical ordinals are assigned by enumeration before strict-integer match filtering.
  Selected actions are projected without coercion, canonically ordered, reconciled to
  the exact `901 + 867 = 1768` population and raw-record digest checked.
- The nested `raw_record` mappings and sequences are immutable, and the returned
  completion object is the authentic checked capability issued by the accepted reader.
- Existing adversarial coverage rejects omission, addition, duplication, reordering,
  non-strict match identity, decoded-row drift and source-byte mutation.
- No product bytes, dependency changes, provider/network access, Git operations,
  cloud, containers, hosted CI, endpoint, remote or deployment actions occurred.

## Finding

### P1 — Returned completion evidence is not deeply immutable

`_raw_tags_and_projection` creates a tuple around the source tag list but retains each
ordinary mutable tag dictionary (`src/scouting/sources/wyscout_completion_index.py:475-488`).
`completion_action_evidence` stores that tuple directly in
`CompletionActionEvidence.raw_tags` (`:546`). The adapter then places the same evidence
objects both in the public `VerifiedMatchAction` rows and in the authentic completion
capability issued at `:1048-1055`.

Consequently, a normal caller can mutate a returned evidence row even though the outer
dataclasses are frozen. The mutation also changes the membership preimage retained by
the checked capability, causing its next independent verification to fail. This is an
authority-state mutation/denial path and directly violates the packet requirement for
a deeply immutable returned raw/evidence population.

Executable reproduction, exit `0`:

```text
uv run python -c '<load accepted match; mutate first non-empty evidence.raw_tags[0]["id"]>'

before_periods 2
mutated_evidence {'id': 999999}
after_error population membership differs from completion index
```

A separate direct probe reported the retained value type as `dict` and accepted the
assignment:

```text
dict {'id': 1801}
mutated {'id': 999999}
```

The current positive immutability test at
`tests/unit/test_wyscout_source_completion_index.py:572` checks nested
`raw_record["positions"]` only; it does not attempt mutation through
`action.evidence.raw_tags`.

## Bounded rework required

1. Make the `raw_tags` values retained by every adapter-returned
   `CompletionActionEvidence` deeply immutable while preserving the exact canonical
   object representation used by `action_frame`.
2. Preserve all accepted index, R20/R21 and source bytes. The correction must not
   alter the action-frame preimage, membership hashes, accepted index address or public
   completion behavior.
3. Add a regression that proves mutation through
   `VerifiedMatchAction.evidence.raw_tags` raises `TypeError`, then proves the authentic
   completion capability still revalidates to the exact two periods.
4. Rerun the producer packet's focused suite and return a newly hashed candidate for
   fresh independent review.

No architecture, dependency, provider, product or deployment change is required for
this correction.

## Commands and results

- `shasum -a 256 src/scouting/sources/wyscout_completion_index.py tests/unit/test_wyscout_source_completion_index.py reports/reviews/W04/returns/W04-VERTICAL-SLICE-SOURCE-ADAPTER-01-R1.md`
  - exit `0`; all three expected hashes matched.
- `shasum -a 256 data/manifests/wyscout/v5/source-completion/46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df.source-completion-index.json`
  - exit `0`; exact accepted address matched.
- `wc -c data/source/wyscout/v5/archive-members/events_England.json`
  - exit `0`; `188888614` bytes.
- `shasum -a 256 data/source/wyscout/v5/archive-members/events_England.json`
  - exit `0`; exact accepted member digest matched.
- `uv run pytest -q tests/unit/test_wyscout_source_completion_index.py -k 'verified_match_adapter or verified_member_reader'`
  - exit `0`; `16 passed, 37 deselected in 3.16s`.
- `uv run python scripts/verify_local_only.py`
  - exit `0`; `PASS`, 25 checks and zero failures.
- two read-only `uv run python -c` immutability probes
  - exit `0`; reproduced mutable tag evidence and post-mutation membership failure.

## Review conclusion

The guarded read and exact-population comparison are sound for the bounded source
scope. Acceptance is withheld solely for the reproducible P1 immutability defect above.
Return this exact candidate for bounded correction; do not dispatch downstream product
use until the corrected candidate receives fresh independent review and master
acceptance.
