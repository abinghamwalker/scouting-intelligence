# W04 source-completion-index R1 master verification

Disposition: `REWORK`

## Candidate inspected

- index implementation SHA-256:
  `8dea0c12678667c80171dc19890d672a88403b9c5f77e06438f53a4cd5cb4565`
- Wyscout contract SHA-256:
  `acf5555d31c931dda6c3575e5b088401847e0b8efc50c50f349ca188ee019aa0`
- focused index test SHA-256:
  `ea569ca0c41348842893ae5f51d0b147cb309f0421c259141c47a4b7c737439b`
- focused contract test SHA-256:
  `ba01261521923bf2b62ea4a63930f43bc20e2df18fb3028accdf53b90d8e77c1`
- immutable index SHA-256:
  `46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`
- producer return SHA-256:
  `c8c1d8a36119c5926481552b5dc32ac5753a19df1968dbeac8109a594c0cfa93`

The master read the producer return, the complete new index module and focused index
tests, every completion-index/equal-clock/provenance modification in the Wyscout
contract and contract tests, and independently inspected the canonical index structure.
The index file is exactly 644,037 bytes, its filename equals its SHA-256, its five
member counts reconcile independently, and both member and period sums equal
3,071,395.

Frozen R20, R21, both accepted preimages, the accepted source manifest and the raw
completion manifest retained their required hashes. `git remote` printed nothing.

## Independently reproduced checks

- Ruff format: pass, four files formatted.
- Ruff check: pass.
- Mypy: pass, four files.
- Import-linter: pass, three contracts kept and zero broken.
- Focused unit/contract suite: pass, 250 tests.
- Pre-derivation full source bridge: pass, source manifest re-confirmed as
  `8fb6eb54ccca7656d66f53affb79e38abfef88d449d6903593ede4bf34fd89bd`.

## Finding W04SCIR1-P1-001 — accepted address is not pinned by the public validator

`validate_index` verifies that a candidate is internally content-addressed but does
not require its SHA-256 to equal the accepted index digest. `load_source_completion_index`
also accepts a caller-selected canonical digest. The master changed one period's
membership digest, recomputed a self-consistent index payload/address, and observed:

```text
forged b1ff0d29cbfeb3b3370e5f379da35032880e497d07164ee953ffc6d98e480923 True False
```

Here `True` means the public validator accepted the forged index; the final `False`
means its address did not equal the accepted
`46a22423d5a32122429e7bf15d79dc892fa8177b19d9672b61303bc6e1df87df`.
Although the later sequence factory has a second pin, the authorized completion-reader
boundary itself must load and validate only the accepted address. An internally
consistent caller-created replacement index is not source authority.

Required bounded correction:

1. reject any index object or requested load address other than the accepted digest at
   the earliest public validation/load/materialization boundary;
2. retain independent payload-address recomputation after the accepted-address check;
3. add an adversarial regression using a self-consistent recomputed lookalike index;
4. preserve the accepted artifact bytes and all existing R1 behavior.

No architecture change, product implementation, source re-acquisition, dependency, or
new artifact is required.
