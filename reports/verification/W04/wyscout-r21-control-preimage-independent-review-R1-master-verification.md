# W04 R21 control-preimage independent review R1 — master verification

## Decision

`ACCEPT`. The fresh independent review passes with no P0, P1, or P2 finding,
and the master independently reproduces its evidence.

## Complete readback

The master read all 618 review lines and all 123 return lines. Exact evidence:

```text
independent review
bytes: 21535
lines: 618
SHA-256:
4d640b25a47ed9098b5311aad35aeae6098126cb4cfe5cd074ccd13085221ac6

return
bytes: 5889
lines: 123
SHA-256:
26888a2ed76128fc4fa30f97f20072a996e5426980b5d7253390512f9bbacaff
```

The review recommends `PASS`, reports `P0=0`, `P1=0`, `P2=0`, and binds:

```text
product preimage physical/canonical SHA-256:
0003daf8ea7b4a40841fc4a29c6e2191f8b0850287fa38dcbdf4a68ab3dc6293

schema preimage physical/canonical SHA-256:
a37b426ee20dc3f63f5186ab97495511433eca7c7649098b439d01eddd8b916f

focused-test physical SHA-256:
b2bccb03e59c60a8d61439ea938e2da0fbb8a2bba2dcf77ff3549f2aabb54e53
```

## Independent master reconstruction

After a fresh locked sync, the master reproduced:

- canonical compact UTF-8 JSON bytes with one terminal LF;
- exact product cardinalities `17/10/2/5`;
- 16 unique schema descriptors with identical order and earlier-only edges;
- the typed-null unresolved feature placeholder;
- byte-equal R20/R21 authority links and the sibling-only acyclic graph;
- no own, sibling, field, possession, feature, build, run, product, clock,
  host, root, absolute-path, environment, or mutable-runtime digest/value;
- six passing focused tests and focused Ruff format/lint;
- all 25 local-only checks;
- absence of all seven product roots and every named next-stage path; and
- an empty `git remote`.

No field, possession, feature, Bronze, Silver, Gold, serializer, manifest,
receipt, build, model, runtime, cloud, container, endpoint, hosted CI,
deployment, provider acquisition, dependency/lock, or Git mutation occurred.

## Inventory evidence

The reviewer's required preflight and postflight inventories are byte-identical:

```text
pycs: 1,145
__pycache__ directories: 150
records plus header: 1,296
SHA-256:
b32b4bb8a740a2030ca0337ec8d00d865b7ebe8fc96fbc360ab034c4dfb8c777
```

The master regenerated the same complete inventory after its checks and matched
the retained preflight exactly. The reviewer also preserved a broader
diagnostic showing pytest changed only `.pytest_cache`; that path is outside
the packet-defined pyc/`__pycache__` inventory. Nothing was cleaned or repaired.

## Gate

The control-preimage review is accepted. Only
`W04-FIELD-SEMANTIC-V2-DECISION-01-R1` may start. Every later authority and
all product implementation remain serially blocked.
