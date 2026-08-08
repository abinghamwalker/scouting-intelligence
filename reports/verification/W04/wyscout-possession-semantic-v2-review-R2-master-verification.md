# W04 possession semantic v2 independent review R2 — master verification

## Decision

`REWORK`. The master independently reproduces both reviewer findings and adds
one further P1 control defect in the R2 review authority:

```text
REVIEW_ID_PATH_DRIFT
OUTSIDE_ROOT_PACKET_CONFIG
REVIEW_ACTOR_NOT_UUIDV5
```

The selector and same-period resolution semantics themselves passed independent
review. These three findings are bounded to the executable progression test,
master-owned packet configuration, and reviewer actor. They require no
architecture or product revision.

## Preserved R2 review evidence

Before any later fixed-path review, the master retained the exact R2 review and
return bytes in the operational failed-review archive. Their durable hashes
are:

```text
R2 review physical SHA-256:
609a4e0bc42fd611cb63d9483ae4ef262e2633472c3a8c32f4f99a4caf88b37a
R2 canonical review-record SHA-256:
de5227391e050a87c731491528627f14e654ba4a64ca4f6b4087c21895ad9d4f
R2 return physical SHA-256:
974d8418a7408eca3be338b0f8ae9211fb5df37eb9827c70251843051d404a23
pre-correction R2 packet physical SHA-256:
f4546c47bd1a8a3971ff97f687136b25dea6c376d30388c91f1529c0b2fc3057
```

The older failed R1 review and return also remain exact:

```text
R1 review:
71f4bdb25b0e2b3903abbede25afa5b2f62fd1763b54276899dd8ad4364feb8a
R1 return:
fc167434bf5da53e39b702d7fcc634222c53c84330cd05767eca1a3b52f98b90
```

The R2 reviewer changed exactly its fixed review and R2 return paths and
performed no Git, dependency, authority-input, acceptance, or product work.

## Reproduced findings

### P1 — review identity/path drift

Frozen R21 fixes the sole current review route at:

```text
w04-wyscout-possession-semantic-independent-review-v2-R1
reports/reviews/W04/authorities/
  wyscout-possession-semantic-independent-review-v2-R1.md
```

The executable contract instead declares an invented `v2-R2` current ID/path
and asserts that the R21-fixed `v2-R1` path must retain the old failed R1 hash.
After the reviewer correctly replaced the fixed path, the master suite
reproduced:

```text
327 passed, 1 failed
```

The sole failure is the stale assertion at focused-test line 1400, where current
review hash `609a4e0b...` is incorrectly compared with failed R1 hash
`71f4bdb2...`.

### P1 — outside-root packet configuration

The pre-correction R2 packet embedded an absolute operational archive path.
The master reproduced `verify_local_only.py` status `FAIL`: 24 checks passed
and `no_outside_root_config` alone failed.

The master has removed only that external path literal from the packet and
retained the verified archive flag and exact failed hashes. The operational
archive remains intact; its location is not repository configuration.

### P1 — reviewer actor is not UUIDv5

The R2 packet and review use:

```text
db5e4511-e465-4f24-8b50-fa017eebe8fa
```

Independent parsing proves `UUID(...).version == 4`. The possession authority
validator requires canonical RFC 4122 UUIDv5 actors. The review narrative
incorrectly calls this actor version 5, and the machine record cannot become
acceptance authority even after correcting the path constant.

A fresh review must use a distinct canonical UUIDv5 actor. The next fixed actor
is:

```text
b4b3e91b-d13b-53c4-95d4-a6019f6faa98
```

## Bounded correction

R4 must:

- restore `REVIEW_PATH` and `REVIEW_ID` to the sole R21-fixed `v2-R1` route;
- remove the invented current `v2-R2` route;
- recognize only the two exact failed-review physical hashes as historical
  transitional evidence, never as current accepted review authority;
- validate any other present fixed-path review normally and fail closed;
- preserve all decision/candidate/selector/sequence/v1 bytes and tests.

After R4 passes, a fresh R3 review packet must use the valid UUIDv5 actor above,
contain no outside-root config, and overwrite the fixed path only after
verifying the retained R1 and R2 failed bytes.

## Gate

Only `W04-POSSESSION-SEMANTIC-V2-DECISION-01-R4` may start. Possession
acceptance, feature authority, cross-authority work, and all product
implementation remain blocked.
