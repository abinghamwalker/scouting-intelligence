# W03 local security, dependency, and container report

Status: **PASS with disclosed metadata limitations**

The master ran these checks locally against the W03 candidate. No external
vulnerability service, cloud scanner, public registry, or hosted service was queried.

## Secret inspection

`uv run detect-secrets scan --all-files ...` ran with detect-secrets 1.5.0.

The first scan reported only:

- the accepted W01 commit SHA in `orchestration/phase_registry.yaml`;
- frozen SHA-256 content, source, feature-lineage, development-fixture, and
  protected-fixture digests;
- test assertions for those same frozen digests.

The master read every reported line and confirmed that each value is an immutable
commit or content digest, not a credential. A second scan excluded only caches,
`uv.lock`, generated evidence/returns, the protected partition, and those manually
reviewed digest-bearing files. It returned an empty `results` mapping. A separate
literal search confirmed that the ephemeral local database review password was not
written anywhere in the project tree.

## Python dependency and licence inspection

`uv run pip-licenses --summary` completed successfully against the locked root
environment. It enumerated 135 installed distributions and reported declared licence
metadata across MIT, BSD, Apache, MPL, PSF, LGPL and compatible compound expressions.

Three existing distributions report `UNKNOWN` metadata:

- `huey==3.3.0`;
- `skops==0.14.0`;
- the local `scouting-intelligence==0.1.0` project, for which the user has not selected
  a project licence.

Huey and skops predate the W03 dependency packet in the accepted W01 lock. The new W03
direct dependencies expose declared licence metadata in the local inventory. The
unknown metadata is disclosed and does not represent an unreviewed licence grant,
provider-data right, or new W03 package.

No `pip-audit` network query was run. The accepted W01 boundary explicitly records that
external vulnerability-service egress exceeds the local evidence boundary. W03 instead
uses the locked inventory, local licence inspection, Bandit, contract/security tests,
and container/runtime inspection.

## Local container inspection

`docker compose ps --format json` reported both required services running and healthy:

| Service | Cached image identity | Published binding | Health |
| --- | --- | --- | --- |
| PostgreSQL/pgvector | `sha256:0a07c4114ba6d1d04effcce3385e9f5ce305eb02e56a3d35948a415a52f193ec` | `127.0.0.1:55432` → `5432/tcp` | healthy |
| Redis | `sha256:ee64a64eaab618d88051c3ade8f6352d11531fcf79d9a4818b9b183d8c1d18ba` | `127.0.0.1:56379` → `6379/tcp` | healthy |

Local image inspection resolved the corresponding immutable cached RepoDigests:

- `pgvector/pgvector@sha256:0a07c4114ba6d1d04effcce3385e9f5ce305eb02e56a3d35948a415a52f193ec`;
- `redis@sha256:ee64a64eaab618d88051c3ade8f6352d11531fcf79d9a4818b9b183d8c1d18ba`.

No image was pushed, published, deployed, or scanned through an external service.
Neither service has a non-loopback published port.
