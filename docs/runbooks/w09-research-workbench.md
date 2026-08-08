# W09 local research-workbench runbook

## Purpose and operating boundary

This runbook starts and operates the accepted historical-player research workbench on one local
machine. It does not start W10 evidence collection, the dormant W08 workflow, a provider adapter,
an external service or a deployment.

W10 remains `REWORK`. Formal W10 collection is unauthorised, 08E/08F are unstarted and G-RW4
remains `INSUFFICIENT_EVIDENCE`.

## Prerequisites

- Work from the repository root with Python 3.12 and the committed `uv.lock`.
- `uv` and the single root `.venv` are the only environment authority; do not use `pip`, a nested
  environment or a second lockfile.
- The approved matrix manifest and its one compatible index must already exist at the governed
  local paths. Routine startup must not rebuild, select a newest artifact or repair pins.
- Runtime traffic is loopback-only. Do not bind to another host or expose the port externally.
- If `uv` needs an unapproved network download rather than using the provisioned local
  environment/cache, stop and return to the master.

Prepare or verify the locked environment:

```text
uv sync --locked --all-groups
```

## Start and stop

From the repository root, run the one-command launcher:

```text
./scripts/start_w09_research_workbench.command
```

It defaults to `http://127.0.0.1:8769/`. An optional unprivileged port may be supplied:

```text
./scripts/start_w09_research_workbench.command 8879
```

The launcher must remain fixed to `127.0.0.1`; the argument changes only the bounded port. It does
not use reload, detach, open a browser, start an unbounded `caffeinate` process or contact a
provider. Leave the terminal open while using the workbench. Press `Control-C` once to stop it.

Use only the exact URL printed by the launcher. `localhost` is accepted by the application, but
the printed numeric loopback address makes the intended transport boundary unambiguous.

## First walkthrough

1. Open the dataset section. Confirm that it reports one verified local authority, 1,975 eligible
   rows, 1,965 players, the historical window and explicit limitations. If the post-cascade live
   IDs are needed, use the verified identities in the dataset and model cards; do not copy IDs
   from older verification reports.
2. Search for an eligible real historical player and select the exact player grain as the
   exemplar. Player search may span all retained competitions.
3. Choose the selected target competition and season for candidates. The exemplar may come from
   another competition; the query still returns candidates only from this one target. There is no
   combined all-leagues candidate pool.
4. Optionally narrow candidates by GK/DF/MD/FW and a higher evidenced-minute floor. Remember that
   every eligible minute total remains a conservative lower bound.
5. Choose weighted Euclidean or weighted cosine. Keep at least one non-zero weight. A zero weight
   disables its feature for that query.
6. Run the query. The service scores every filter-admitted row in the selected target competition
   and season before limiting returned results.
7. Open a candidate's contribution table. Inspect raw query/player rates, scaled contrast, weight,
   method-specific contribution, evidenced minutes and limitations.
8. Select two to five candidates for exact comparison. The comparison shows retained matrix rows;
   it does not calculate new relevance or goalkeeper-effectiveness metrics.
9. Save a clearly named experiment and choose canonical JSON or self-contained HTML. Open the
   report, then replay the experiment to verify exact compatibility.

Synthetic rows are test fixtures only. A live search or report must contain governed historical
players, never a synthetic fallback.

## Interpret the numbers exactly

### Raw values and minutes

Raw feature values are retained event numerator counts per 90 governed played minutes. They are
not percentages. Accurate passes, shots on target and duels won are numerator rates, not accuracy,
conversion or duel-win percentages.

Every eligible denominator is a conservative lower bound, so the true minutes can be larger and a
displayed per-90 rate can be overstated. The event-9 semantic uplift also means `goals_per90`
excludes retained event 9 save-attempt rows; those rows are not relabelled as goals conceded,
shots faced, saves or save quality.

### Global robust scaling

The frozen scaler is fitted once over all 1,975 eligible rows:

`scaled = (raw - global median) / global IQR`

IQR is the 75th percentile minus the 25th percentile. A zero IQR uses unit scale. Position and
target-competition filters do not refit these values.

### Euclidean

For each feature, the displayed Euclidean contribution is:

`weight × (candidate_scaled - query_scaled)²`

The distance is the square root of the contribution sum. Terms are non-negative, but neither a
term nor the distance is a percentage or calibrated match score.

### Cosine

Cosine distance is `1 - weighted cosine similarity`. Its feature contributions are signed terms
from the weighted normalised vectors and reconstruct the distance as `1 +` their sum. A negative
term can reduce distance; do not interpret it as negative football value.

For both methods, lower means closer only under the same method, active features, weights, filters
and authority pins. Never compare Euclidean and cosine numbers as if they share a scale, and never
describe either as a relevance probability.

## Local reads and writes

Startup reads the exact matrix manifest/artifacts and compatible immutable index. It also opens the
embedded database at `data/working/scouting.sqlite3` and applies append-only migrations
idempotently. SQLite may create or update its database, WAL and shared-memory sidecars.

Saving and replaying experiments writes governed operational records to that SQLite database.
Deterministic reports are written below `data/working/w09/research-reports/`. Normal Python/`uv`
execution may update the root environment metadata or ignored bytecode caches. No write is
authorised outside the repository's guarded local roots.

Do not edit matrix/index bytes, report bytes or database rows manually. Do not delete an old
experiment to make a compatibility warning disappear.

## Experiment compatibility

Replay has three meaningful closed outcomes:

- `REPRODUCED`: exact saved request, pins, result identity and digest reproduced.
- `INCOMPATIBLE_PINS`: the loaded live authority differs from the saved authority. Package A
  intentionally causes every pre-uplift experiment to reach this status.
- `RESULT_MISMATCH`: the exact pins were accepted but the deterministic result identity or digest
  differed; preserve the evidence and escalate to the master.

Never migrate or re-pin an experiment. A post-uplift experiment should be saved only against the
master-verified post-cascade authority and must reproduce exactly before delivery is declared
ready.

## Fail-closed troubleshooting

### Governed population unavailable (HTTP 503)

The application found no unique compatible matrix/index authority. Stop the server and report the
displayed reason. Check only that the approved local artifacts are present. Do not choose a newest
manifest, substitute W07/W08/synthetic data, rebuild artifacts or change pins as a startup fix.

### Address already in use or invalid port

Stop the existing process if it is the operator's own stale launcher, or restart with another
unprivileged port from 1024 through 65535. Do not change the host from `127.0.0.1`.

### Loopback-host rejection

Use the exact URL printed by the launcher. A foreign Host value is rejected deliberately. Do not
weaken the guard or bind the server to `0.0.0.0`.

### Empty or unexpected candidate count

Recheck selected target competition, season, broad position, minimum minutes and explicit
exclusions. “Full population” means all rows surviving those filters, not all 1,975 matrix rows.
Do not move the 450-minute eligibility policy or silently relax query filters.

### Query validation error

Confirm at least one weight is positive, all values are finite, the season is explicit and the
browser has loaded the same pins as the API. Do not alter a digest or request body by hand to bypass
validation.

### `INCOMPATIBLE_PINS`

This is the honest expected result for every pre-uplift experiment after Package A. Preserve the
experiment and receipt. Do not migrate, delete, clone as current or re-pin it.

### `RESULT_MISMATCH`

Stop using the result, preserve its report and receipt, and return the exact IDs to the master.
Do not overwrite the experiment or select a ranking because its names look more plausible.

### Database or report-path failure

Keep the failing files in place and record the exact error. Confirm the paths remain regular files
inside the guarded repository root and that the operator owns them. Do not change to a broad path,
follow a symlink, weaken permissions or delete retained evidence as a repair.

## References

- Dataset: `docs/dataset-cards/w09-historical-player-window-v1.md`
- Model: `docs/model-cards/w09-historical-retrieval-v1.md`
- Product boundary: `docs/architecture/research-workbench-pivot.md`
- Active W10 boundary: `docs/architecture/w10-expert-relevance-validation.md`
