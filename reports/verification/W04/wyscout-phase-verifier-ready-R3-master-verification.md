# W04 phase verifier READY correction R3 — master verification

## Decision

`ACCEPTED`.

The master inspected the complete R3 verifier and test changes, both retained
producer rework histories, the independent R1 `REWORK`, the master packet-schema
correction, and the fresh independent R2 `PASS`. The correction is bounded to a
repository-control cycle exposed by the complete R21 gate; it changes no R21
semantic authority or product behavior.

Physical bindings:

```text
scripts/verify_phase.py
ad2c668c22ed2bc21b840c1fa2a8b842091a2cc9cc1bd731e7a62d2d7e276da5

tests/unit/test_orchestration_controls.py
825097186cea1ce65403f01b995895ce8856aa480675354259a1c0881ebb1253

R3 producer return
b3f523342b93ef0af3aa4e8d12f6100da98c2e0d6546fb1163b63e400a303ad6

fresh independent R2 review
cda97099eb889d015391ac81265e8ab8db2753f377747d1a45261a1e8fc14d41

fresh independent R2 review return
add1b838a4ef1957cdb04427f7651831919ef09ce432851fd2e8f4f45059d4ea

preserved independent R1 REWORK review
d5f9ed587f9045de2234ba1295cee73a22e1b6349179005262c6fdb940dd0965
```

Master reproduction:

```text
uv run ruff format --check scripts/verify_phase.py tests/unit/test_orchestration_controls.py
PASS — 2 files already formatted

uv run ruff check scripts/verify_phase.py tests/unit/test_orchestration_controls.py
PASS

uv run mypy scripts/verify_phase.py
PASS — no issues in 1 source file

uv run pytest -q tests/unit/test_orchestration_controls.py
PASS — 34 passed

uv run pytest -q tests/unit/test_orchestration_controls.py \
  -k 'empty_task_returns or master_return_exemption'
PASS — 25 passed, 9 deselected
```

The final behavior is:

1. `READY` is eligible for repository verification but does not bypass allowed
   state, closed dependency, accepted/evidenced task, required evidence,
   declared check, zero-remote, start-checkpoint, accepted-checkpoint, or
   closed-tree enforcement.
2. A task with retained returns is unchanged.
3. A task with no delegated return is accepted only if every referenced packet
   exists, parses, contains every field in the shared
   `REQUIRED_PACKET_FIELDS` authority, has exact `assigned_role: master`, and
   has the exact registry task ID.
4. Missing, skeletal, malformed, incomplete, delegated, mixed, borrowed, or
   task-mismatched packet evidence fails closed.

The master corrected the only two missing mandatory fields among packets
supporting current empty-return tasks:

```text
W04-SOURCE-AUTHORITY-01-R2
2c58e8e8de33b625233048a2e33b9cbfd133548ba923cfa17d4d79b5b0f6a0c9

W04-SOURCE-ACQUIRE-01-R1
6059d8465f3cee5232701adc30e067372086b8fc86658b35ca94f779d3784d1b
```

Both now have zero missing canonical fields. The complete repository and R21
gates remain mandatory before downstream implementation.
