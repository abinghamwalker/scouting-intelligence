# W04-FIELD-SEMANTIC-DECISION-01-R3 return

## Outcome

`PASS`

This R3 run produced evidence only. It changed no implementation, candidate,
test, configuration, source, data, orchestration, review, acceptance, or
downstream artifact. The only R3 write was this return:

`reports/reviews/W04/returns/W04-FIELD-SEMANTIC-DECISION-01-R3.md`

## R2 lineage correction

R2 was rejected because its return reused stale R1 metadata inventory hashes
instead of reporting the actual R2-era metadata hashes. In particular, the
R2 return's repository metadata value `222dee...` and site-packages metadata
value `3d5c...` were stale; the master-observed R2-era values were
`37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733`
and `a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8`.
Two subsequent R2 metadata inventory attempts were interrupted/nonresponsive
and did not complete. This R3 return does not relabel either attempt as a
completed check or as evidence.

All inventory values below were freshly measured during this R3 run.

## Fresh R3 shell-only pyc preflight

The exact complete R2 repository/site inventory algorithm was run at the
actual start of R3, before any R3 Python process.

| Inventory field | Fresh R3 preflight |
|---|---:|
| repository pyc count | `58` |
| repository metadata inventory SHA-256 | `37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733` |
| repository content inventory SHA-256 | `a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9` |
| site-packages pyc count | `1086` |
| site-packages metadata inventory SHA-256 | `a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8` |
| site-packages content inventory SHA-256 | `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18` |

## Pre-Python frozen-artifact gate

The physical digests were measured with `shasum -a 256`. The canonical
registry digest was independently measured before Python by loading the
frozen YAML with the system Ruby safe YAML loader, recursively ordering
mapping keys, serializing compact JSON with one terminal newline, and hashing
those bytes.

| Frozen artifact | Required SHA-256 | Actual SHA-256 | Result |
|---|---|---|---|
| decision physical | `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999` | `e09d6c66249209752df2bea5fcf34496bb7cf697d1cf1085e4bded844b856999` | `PASS` |
| registry physical | `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2` | `805fccd142b1a2b379a18cfc5eb1755dd467c5363b0044f1c2cfe19a248481f2` | `PASS` |
| registry canonical | `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034` | `fb133df629ec8797c280ff3eb67f509221884bf7f4c379ab8c0a1205bbc31034` | `PASS` |
| contract test physical | `d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3` | `d8616b4afd9b9b83fccc0fbd52e387713c08b6d3904a956d271ef0bfe3a5f7b3` | `PASS` |

## Required absence gate

The exact review and acceptance artifacts and all downstream paths named by
the contract test were checked with shell path predicates before Python. All
were absent:

- `reports/reviews/W04/authorities/wyscout-field-semantic-independent-review-R1.md`
- `reports/reviews/W04/authorities/wyscout-field-semantic-acceptance-v1.json`
- `data/working/wyscout/v5/.staging`
- `data/working/wyscout/v5/identity`
- `data/working/wyscout/v5/bronze`
- `data/working/wyscout/v5/silver`
- `data/working/wyscout/v5/gold`
- `data/manifests/wyscout/v5/code`
- `data/manifests/wyscout/v5/bronze`
- `data/manifests/wyscout/v5/silver`
- `data/manifests/wyscout/v5/gold`
- `scripts/admit_wyscout_v5.py`
- `scripts/admit_wyscout_v5_runtime.py`
- `scripts/rebuild_wyscout_v5.py`
- `scripts/launch_wyscout_v5.py`

Result: `PASS` (`15/15` absent).

## Exact acceptance checks

1. Command:

   ```text
   PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B -m pytest -q tests/contracts/test_wyscout_field_registry_authority.py
   ```

   Result: `PASS`; exit `0`; `123 passed in 17.51s`.

   The first sandboxed invocation of this exact command exited `2` before
   test collection because the sandbox could not read the existing
   `/Users/adrian/.cache/uv/sdists-v9/.git` path. No sync was attempted. The
   exact command was reissued with read access to the existing uv cache; the
   acceptance execution above is that completed run.

2. Command:

   ```text
   uv run --locked --no-sync ruff format --check tests/contracts/test_wyscout_field_registry_authority.py
   ```

   Result: `PASS`; exit `0`; `1 file already formatted`.

3. Command:

   ```text
   uv run --locked --no-sync ruff check tests/contracts/test_wyscout_field_registry_authority.py
   ```

   Result: `PASS`; exit `0`; `All checks passed!`.

4. Command:

   ```text
   PYTHONDONTWRITEBYTECODE=1 uv run --locked --no-sync python -B scripts/verify_local_only.py
   ```

   Result: `PASS`; exit `0`; validator status `PASS`; `failures: []`.

Every Python execution used both process-start
`PYTHONDONTWRITEBYTECODE=1` and `python -B`. Every uv execution used
`--locked --no-sync`. No dependency sync occurred.

## Terminal shell-only pyc postflight

After this return was written, the exact same complete shell-only inventory
algorithm was run once.

| Inventory field | Fresh R3 preflight | Terminal R3 postflight | Result |
|---|---:|---:|---|
| repository pyc count | `58` | `58` | `PASS_IDENTICAL` |
| repository metadata inventory SHA-256 | `37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733` | `37051613e93742cac99eb53988852eb608b4fa9cb0c52b85e208845b82739733` | `PASS_IDENTICAL` |
| repository content inventory SHA-256 | `a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9` | `a5893b65852cd0d912cd950216d81b10dd704c821c0b4ffc408c9f2ea5dd57b9` | `PASS_IDENTICAL` |
| site-packages pyc count | `1086` | `1086` | `PASS_IDENTICAL` |
| site-packages metadata inventory SHA-256 | `a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8` | `a2b5cd4395cdf36f2b86838ae0aa465a5964af7d539a01cc79c1bb38b8ceeaa8` | `PASS_IDENTICAL` |
| site-packages content inventory SHA-256 | `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18` | `b6fe68b41a1da1ccd3589a700a60d3273338c303d7d650ecca1d12c03e5baa18` | `PASS_IDENTICAL` |

Result: `PASS_IDENTICAL` for all six inventory fields.

## Scope and authority

- No Git command was run.
- No delegation or self-approval occurred.
- No network or provider data was accessed.
- No implementation or frozen artifact was edited.
- No review, acceptance, dependency, Bronze, Silver, Gold, product, runtime,
  cloud, container, endpoint, or deployment artifact was created.
- This return is evidence only and does not perform independent review,
  acceptance, or downstream authorization.
