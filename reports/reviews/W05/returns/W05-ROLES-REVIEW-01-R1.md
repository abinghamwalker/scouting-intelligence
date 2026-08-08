# Subagent return

## Task

- task_id: W05-ROLES-REVIEW-01
- objective: Independently verify responsibility-language taxonomy identity, contextual
  membership, fail-closed behaviour, claim boundaries, fixture alignment, and safe M0
  taxonomy binding.

## Files changed

- reports/reviews/W05/w05-role-taxonomy-independent-review-R1.md
- reports/reviews/W05/returns/W05-ROLES-REVIEW-01-R1.md

## Summary

- Verdict: **REWORK — P0: 0; P1: 1; P2: 0**.
- Reproduced the accepted full-config digest, re-signed substitution/order/dangling/claim
  rejection, deterministic exact-sum contextual probabilities, all required fail-closed
  inputs, contextual variation, synthetic-only/no-permanent-label boundaries, and exact
  alignment to all 18 complete feature rows.
- P1 `W05-ROLES-R1-P1-01`: the loader returns a
  `FootballResponsibilityTaxonomy` admitted only through `model_construct`. Its exposed
  digest is `596886...`, while the shared strict contract computes `26e90f...` and rejects
  the projection. Normal re-signed M0 manifest/result construction accepts that invalid
  digest and also an arbitrary digest; downstream equality is exact but does not
  authenticate valid taxonomy semantics or claim fields.
- Smallest correction: make the shared strict taxonomy cover the accepted full semantic
  digest, remove `model_construct`, prove public revalidation/digest equality, and source
  downstream taxonomy pins from that authenticated object.

## Tests run

- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python -c 'from pydantic import ValidationError; from scouting.contracts.m0 import FootballResponsibilityTaxonomy; from scouting.roles.taxonomy import load_role_taxonomy; t=load_role_taxonomy("configs/roles/w05-football-responsibility-taxonomy-v1.json"); p=t.contract.model_dump(mode="python"); print(type(p["responsibilities"]).__name__, type(p["roles"][0]["responsibility_codes"]).__name__); print("computed",FootballResponsibilityTaxonomy.digest_for_payload(p));\ntry:\n x=FootballResponsibilityTaxonomy.model_validate(p); print("UNEXPECTED_VALID",x)\nexcept ValidationError as e:\n print("REJECTED",[(z["loc"],z["type"],z["msg"]) for z in e.errors()])'`
  - exit status: 0
  - result: strict computed digest `26e90f...`; public strict validation rejected the
    actual projection because its digest is not the canonical taxonomy digest.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python -c 'import copy,json; from unittest.mock import patch; from scouting.contracts.m0 import FootballResponsibilityTaxonomy; import scouting.roles.taxonomy as m; raw=json.load(open("configs/roles/w05-football-responsibility-taxonomy-v1.json"));\ndef resigned(mut):\n x=copy.deepcopy(raw); mut(x); x["taxonomy_digest"]=m.canonical_digest(x,"taxonomy_digest"); return x\ndef probe(name,x,patch_identity=False):\n ident=(x["taxonomy_id"],x["taxonomy_version"],x["taxonomy_digest"])\n with patch.object(m,"_load_exact_json",return_value=x):\n  ctx=patch.object(m,"_ACCEPTED_TAXONOMY_IDENTITY",ident) if patch_identity else patch.object(m,"_ACCEPTED_TAXONOMY_IDENTITY",m._ACCEPTED_TAXONOMY_IDENTITY)\n  with ctx:\n   try: m.load_role_taxonomy("unused"); print(name,"UNEXPECTED_ACCEPT")\n   except Exception as e: print(name,type(e).__name__,str(e).splitlines()[0])\nprobe("RESIGNED_SAME_ID_CONTENT",resigned(lambda x:x["roles"][0].update(label="changed")))\nprobe("RESIGNED_REORDER_AFTER_REPIN",resigned(lambda x:x["roles"].reverse()),True)\nprobe("RESIGNED_DANGLING_AFTER_REPIN",resigned(lambda x:x["deterministic_mappings"][0].update(role_code="missing_role")),True)\nprobe("RESIGNED_CLAIM_AFTER_REPIN",resigned(lambda x:x.update(claim="expert_validated")),True)\nt=m.load_role_taxonomy("configs/roles/w05-football-responsibility-taxonomy-v1.json"); p=t.contract.model_dump(mode="python"); p["taxonomy_digest"]=FootballResponsibilityTaxonomy.digest_for_payload(p); valid=FootballResponsibilityTaxonomy.model_validate(p); print("CORE_WITH_CONTRACT_DIGEST_VALID",valid.taxonomy_digest)'`
  - exit status: 0
  - result: same-ID changed content rejected by accepted identity; reordered roles,
    dangling mapping, and changed claim rejected by their structural/claim checks after
    in-memory identity repinning; the core payload validated after using `26e90f...`.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python -c 'import json,math; from decimal import Decimal; from uuid import UUID; from scouting.roles.taxonomy import *; p=UUID("10000000-0000-4000-8000-000000000001"); t=load_role_taxonomy("configs/roles/w05-football-responsibility-taxonomy-v1.json");\ndef infer(ctx,evidence,prior=None): return contextual_role_membership(player_id=p,context_id=ctx,taxonomy=t,responsibility_evidence=evidence,source_label_prior=prior)\na=infer("window-a",{"progress_through_pressure":6,"retain_recycle_possession":2},"CENTRAL_MIDFIELD"); b=infer("window-b",{"threaten_penalty_area":8,"secure_first_contact":4}); a2=infer("window-a",{"retain_recycle_possession":2,"progress_through_pressure":6},"CENTRAL_MIDFIELD"); print("ORDER_SUM_REPEAT_CONTEXT",[x.role_code for x in a.memberships],sum((Decimal(str(x.probability)) for x in a.memberships),Decimal()),a==a2,a.memberships!=b.memberships); prior=infer("prior-only",{"retain_recycle_possession":0},"CENTRE_FORWARD"); print("ZERO_WITH_PRIOR",[(x.role_code,x.probability) for x in prior.memberships]); cases=[("unknown",{"unknown":1},None),("negative",{"create_chances":-1},None),("nan",{"create_chances":float("nan")},None),("inf",{"create_chances":float("inf")},None),("all_zero",{"create_chances":0},None),("empty",{},None),("bool",{"create_chances":True},None),("unknown_prior",{"create_chances":1},"NOPE")];\nfor name,e,pr in cases:\n try: infer(name,e,pr); print("FAIL_CLOSED",name,"UNEXPECTED_ACCEPT")\n except Exception as ex: print("FAIL_CLOSED",name,type(ex).__name__,str(ex))\nrf=json.load(open("tests/fixtures/w05/synthetic-development-roles-v1.json")); ff=json.load(open("tests/fixtures/w05/synthetic-development-features-v1.json")); rows=load_synthetic_role_fixture("tests/fixtures/w05/synthetic-development-roles-v1.json",t); rk={(x["player_id"],x["feature_cutoff_ts"]) for x in rows}; fk={(x["player_id"],x["feature_cutoff_ts"]) for x in ff["complete_rows"]}; ek={(x["player_id"],x["feature_cutoff_ts"]) for x in ff["edge_rows"]}; print("FIXTURE",len(rows),len(rk),len(fk),rk==fk,rk.isdisjoint(ek),rf["feature_fixture_id"]==ff["fixture_id"],rf["feature_fixture_digest"]==ff["fixture_digest"],canonical_digest(ff,"fixture_digest")==ff["fixture_digest"])'`
  - exit status: 0
  - result: exact decimal sum, deterministic/order-invariant output, context variation,
    admitted-prior non-uniform result, all required invalid inputs rejected, and 18/18
    fixture alignment with exact feature-fixture digest.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python -c 'import runpy; from scouting.roles.taxonomy import load_role_taxonomy; ns=runpy.run_path("tests/contracts/test_w05_m0_contracts.py"); make_artifact=ns["make_artifact"]; make_result=ns["make_result"]; t=load_role_taxonomy("configs/roles/w05-football-responsibility-taxonomy-v1.json"); a=make_artifact(taxonomy_id=t.taxonomy_id,taxonomy_version=t.taxonomy_version,taxonomy_digest=t.taxonomy_digest); r=make_result(a); print("CONFIG_DIGEST_MANIFEST_RESULT_ACCEPTED",a.taxonomy_digest,r.artifact_manifest.taxonomy_digest,r.pinned_serving_request.expected_taxonomy_digest); arbitrary="f"*64; a2=make_artifact(taxonomy_id=t.taxonomy_id,taxonomy_version=t.taxonomy_version,taxonomy_digest=arbitrary); r2=make_result(a2); print("ARBITRARY_DIGEST_MANIFEST_RESULT_ACCEPTED",a2.taxonomy_digest,r2.result_digest); print("EXACT_PIN_EQUALITY",r2.pinned_serving_request.expected_taxonomy_digest==r2.artifact_manifest.taxonomy_digest)'`
  - exit status: 0
  - result: normal fully re-signed manifests/results accepted both the invalid config
    digest and an arbitrary `f...f` digest while preserving exact pin equality.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync pytest -q tests/unit/test_w05_roles.py tests/unit/test_w05_features.py tests/contracts/test_w05_m0_contracts.py`
  - exit status: 0
  - result: 56 passed in 0.24s.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync ruff check src/scouting/roles tests/unit/test_w05_roles.py`
  - exit status: 0
  - result: all checks passed.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync mypy src/scouting/roles`
  - exit status: 0
  - result: success; no issues in 2 source files.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync lint-imports`
  - exit status: 0
  - result: 3 contracts kept, 0 broken; 44 files and 83 dependencies analyzed.
- command: `UV_CACHE_DIR=/tmp/w05-roles-review-01-r1-uv-cache uv run --no-sync python scripts/verify_local_only.py`
  - exit status: 0
  - result: PASS; all 25 checks passed.

## Artifacts/evidence

- reports/reviews/W05/w05-role-taxonomy-independent-review-R1.md
- taxonomy full-config digest:
  `59688694131370f42b24a0dd00b609d08254ec945df2ba4352055c8391983097`
- strict core-contract digest:
  `26e90f5780f6be45d1e94c13089e3f15d6c10667d5d15f64f0678450d127794c`
- role fixture digest:
  `d087269c83342051fe0274641d91ac1598963af88fda81bf7d5e95916f389b67`
- feature fixture digest:
  `7abd569366caa439cc28563a53c51a0c7ecdd1dfb622bee49d69957f444b9545`

## Risks

- Until P1-01 is corrected, downstream M0 taxonomy pins can be byte-equal yet cannot be
  validated as the canonical identity of the public strict taxonomy contract. Claim-field
  binding is consequently ambiguous across the private full-config and public core views.
- No separate football-content, probability, fail-closed, fixture, provider/expert,
  production-validity, W06-evidence, or permanent-label blocker reproduced.

## Follow-up items

- Issue bounded shared-contract/role-loader/M0-binding rework for
  `W05-ROLES-R1-P1-01`, then obtain a fresh independent review with the same strict
  revalidation and arbitrary re-signed digest probes.

## Scope confirmation

- no Git operations: confirmed.
- no unauthorised dependency or lockfile changes: confirmed.
- no edits outside `allowed_paths`: confirmed.
