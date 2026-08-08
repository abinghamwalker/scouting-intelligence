# W04 Wyscout source-profile master verification — R2

Verified at: `2026-07-29T17:20:34Z`

## Decision

`W04-SOURCE-PROFILE-01` and `W04-SOURCE-PROFILE-REVIEW-01` are accepted at R2.
This is task-level acceptance only; W04 remains open.

The R1 reviewer exposed six material completeness defects. The master reproduced the
failed gate, disqualified that review from acceptance because it ran a forbidden
read-only Git command, issued a bounded R2 correction, read all four producer artifacts,
and reran the complete candidate suite. A different independent reviewer then retained
the R1 recomputation, added five full-snapshot challenges, and recommended ACCEPT. The
master read all three reviewer artifacts and independently reproduced the expanded
suite before accepting either task.

## Accepted evidence

- Completion SHA-256:
  `69b8f9c1bde77545983ddffac5d2e1ba40b823f5081b464177b28b0f1d4a3cb1`.
- Profile SHA-256:
  `569b9a19d7ace084b833171574533d9fcbde96b01053c0991c6bfc0095dab649`;
  exact size `18,574` bytes.
- Exact inventory bridge: seven completion source objects and ten separately durable
  admitted members, each with logical path, size, digest, and access state.
- Admitted scope: five match members, five event members, five referenced
  competitions, 98 referenced teams, and exact event/match partition equality.
- Identity and relationships: 1,826 matches; 3,071,395 events; 3,071,395 distinct
  event-record IDs; zero duplicate event IDs; zero match, partition, or event-team
  boundary exceptions; 50,522 non-zero player/match presence pairs.
- Temporal evidence uses lossless `Decimal`; maximum source scale is 18. Exact period
  terminals, player minutes, possession semantics, and per-90 denominators remain
  explicitly unsupported.
- Coordinate evidence retains three anomalies without clamping or repair.
- Production source, output, and completion-digest overrides reject unless they resolve
  exactly to the approved repository values.

## Master rerun

- `uv sync --locked --all-groups`: PASS; 83 packages resolved, 82 audited.
- Producer plus retained R1 suite: PASS; `10 passed in 88.69s`.
- Expanded producer plus independent R2 suite: PASS; `15 passed in 93.03s`.
- Two separate full-source `scripts/profile_wyscout_v5.py --check` reruns: PASS; exact
  tracked bytes matched.
- Ruff format and lint across producer and reviewer paths: PASS.
- Mypy across producer and reviewer paths: PASS.
- Bandit across the profiler: PASS; no findings.
- `scripts/verify_local_only.py`: PASS; 25 checks, no failures.
- `git diff --check`: PASS.
- `git remote`: PASS; empty output.

## Boundary

No provider request, network access, raw-data mutation, cloud resource, hosted CI,
public endpoint, container, deployment, Git remote, dependency change, or alternate
output was created in this profile correction/review cycle. The immutable acquisition
snapshot and unrelated user-owned work were preserved.

