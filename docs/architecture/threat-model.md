# Initial local threat model

- Status: Design-stage threat model for W03
- Scope: Single-tenant, loopback-only synthetic vertical slice
- Assurance status: Controls are required but not claimed as security-tested
- Out of scope: Remote deployment, external identity, real provider data and a real
  pilot

## Assets and trust boundaries

Protected assets are canonical identities, temporal evidence, role briefs, retrieval
results, confidential observations and shortlists, audit events, local credentials,
configuration, manifests, model/index identifiers and guarded local artifacts.

The W03 boundaries are:

1. local browser to the FastAPI web/API process;
2. request handling to authorisation, policy and serving interfaces;
3. the web/API process and worker to the guarded embedded SQLite file;
4. application modules to guarded project-local files;
5. model evidence to product policy and then to explicit human workflow;
6. material actions to the append-only audit interface.

All services remain on the approved local machine and loopback interfaces. Local-only
reduces network exposure; it does not establish that the application is secure.

## Threats, required controls and residual risk

| ID | Threat and impact | Required fail-closed control | Residual risk / later evidence |
| --- | --- | --- | --- |
| T01 | **Identity mismatch:** two source identities are merged incorrectly or an ambiguous identity is guessed, attaching evidence to the wrong player. | Versioned crosswalk evidence and confidence; never join on display name alone; ambiguous identity is quarantined/reviewable and excluded from retrieval. Corrections supersede rather than rewrite. | Synthetic ambiguity proves only control flow. Real provider reconciliation thresholds and human review quality remain untested. |
| T02 | **Future leakage:** a late or post-cutoff fact enters a historical snapshot, creating impossible performance and misleading lineage. | Require observed, available and cutoff times; admit only strictly before cutoff; generated time is not availability; missing proof is research-only; corrections create new versions. | Timezone, DST, provider revision and real late-delivery behaviour require later leakage review. |
| T03 | **Storage path escape:** untrusted names, traversal or escaped symlinks write/read outside guarded artifact roots. | Resolve against explicit roots, reject traversal/absolute/outside-root targets and escaped symlinks before I/O, use atomic writes and content manifests. | W03 tests cannot establish safety for all filesystems, race conditions or later archive parsers. |
| T04 | **Tenant, object or action authorisation failure:** an actor reads or changes another tenant's/object owner's work, or an unknown action is implicitly allowed. | Tenant context on every contract/row; same-tenant and object checks; explicit role/action allowlists; unknown actor, role, action or context defaults to deny; negative access tests. | Runtime is single-tenant. A second club or external identity requires a new isolation and identity review. |
| T05 | **Confidential evidence disclosure:** observations, shortlists or exports leak through responses, logs, files or permissive export. | Minimise returned fields; enforce visibility and data-rights checks after authZ; W03 export is denied; audit material reads/attempts; keep artifacts local and classify outputs. | No real confidential data, export workflow or privacy test exists in W03. Later R1 needs IDOR, log-redaction and export testing. |
| T06 | **Audit tampering or omission:** a material action is changed, deleted or performed without a durable audit record. | Audit depends only on strict contracts; append-only writes; before/after digests, actor, tenant, action, target, request ID, reason and time; privileged actions fail closed if audit cannot be written; correction is a new event. | Local administrator and database compromise can still affect the same trust domain. Tamper-evidence, restore and clock controls require later verification. |
| T07 | **Secret exposure:** credentials appear in tracked YAML, logs, fixtures, returns or browser content. | Commit no secret values; use ignored local environment configuration; redact structured logs; synthetic fixtures contain no credentials; fail checks on discovered secrets. | W03 does not prove credential rotation, compromise response or a production secrets manager. External identity is deferred. |
| T08 | **Model/product misuse:** resemblance is presented or acted on as success, value, availability or automatic selection; a fallback silently changes the model. | Enforce the published claim/non-claims; keep model evidence separate from policy and decision events; expose versions, uncertainty and applicability; suppress incomplete evidence; never silently substitute; authorised humans decide. | Organisational pressure and user misunderstanding require later moderated and prospective evidence; none is claimed now. |
| T09 | **Rights or source misuse:** real, open, licensed or personal data is admitted under the synthetic classification or exported. | W03 admits only generated, local, non-personal synthetic fixtures; deny absent/unknown classification; no export/external sharing; strictest upstream rights would propagate in later phases. | No provider licence has been reviewed. Real/open data is blocked until a separately governed rights packet exists. |
| T10 | **Cache/job confusion:** stale in-process or file-backed state, or retries, duplicate a material action. | Treat SQLite/manifests as authoritative; namespace by tenant/version; bounded expiry; idempotency keys; cache loss must be safe; audit the authoritative action. | Concurrency and retry-storm drills occur in later hardening, not W03. |
| T11 | **Local exposure or path escape:** the application binds beyond loopback, or the embedded database escapes its guarded root. | Bind FastAPI to loopback; give SQLite no listener; reject database paths outside the guarded root; create no public endpoint, external service, hosted telemetry or deployment. | Host compromise and local multi-user access remain outside application isolation and need operational controls. |

## Abuse and misuse rules

- No actor may use model evidence to perform autonomous recruitment selection.
- No protected or sensitive trait may be inferred, ranked or optimised.
- No restricted datum may be sent to an external model or service.
- No unknown action or missing context may degrade into an allow.
- Search/profile fallback may remain available when model evidence is unavailable, but
  it must be clearly labelled and cannot impersonate a recommendation.
- Security, pilot and licence statements require retained evidence; configuration or
  the existence of this document is not such evidence.

## W03 security acceptance boundary

W03 must demonstrate only the deterministic negative cases in
`evaluation-contract.md`: ambiguous identity, future leakage, path escape, authZ/tenant
denial, confidential evidence denial, audit mutation denial, absent rights denial and
no silent model substitution. Passing those cases does not constitute a penetration
test, ASVS assessment, privacy assessment or production security approval.

Security verification, dependency and local-runtime scanning, recovery, penetration testing
and remediation evidence are later gates. Any unresolved high-severity issue blocks
promotion.

## Authority trace

- `../scouting-ml-production-blueprint.html`: sections 00, 03, 04, 06, 08
  (P0.5, P1.4–P1.8, P4.5, P6.3), 09, 10 and decisions D4, D6, D9 and D10.
- `../scouting-ml-agent-implementation-workflow.html`: sections 01, 03, 05, waves W03,
  W08 and W10, and sections 09–11.
