# W09 independent review

Review date: 2026-08-05
Reviewer packet: `W09-INDEPENDENT-REVIEW-07A-R1`
Scope: retained-data W09 research workbench, G-RW1 through G-RW3, and the G-RW4 claim boundary
Decision: **ACCEPT**

## Decision and finding register

| Severity | Open findings |
|---|---:|
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 0 |

No open implementation finding remained after the final authority rebuild and bounded re-review. This is an engineering acceptance of W09, not a football-relevance, recruitment-usefulness, recommendation, value, availability, fit, or outcome validation.

### Resolved review item (not included in the open counts)

`IR-P2-001` — feature construction imported the downstream modeling layer.

- Original impact: the provider-to-presentation dependency direction was inverted, and the feature builder depended on runtime/index implementation details.
- Bounded remediation inspected: `MatrixCatalogueEntry`, `rows_semantic_digest`, and `population_referred_grain_digest` now live in `src/scouting/contracts/research.py:71`, `src/scouting/contracts/research.py:99`, and `src/scouting/contracts/research.py:186`; `src/scouting/features/historical.py:26` imports them only from contracts; modeling re-exports the public seam. The matrix version now binds `code_version` and `code_digest` at `src/scouting/features/historical.py:1200`.
- Regression control: the forbidden feature-to-runtime rule and full W09 layer rule are declared at `.importlinter:35` and `.importlinter:46`. Keeping the rules in the root import-linter configuration preserves W04's byte-pinned `pyproject.toml` authority.
- Reproduction: `.venv/bin/lint-imports --no-cache` analyzed 90 modules/270 dependencies and kept 5 contracts with 0 broken.
- Resolution: closed; no residual P2.

## Gate status

| Gate | Status | Independent basis |
|---|---|---|
| G-RW1 | PASS | Reconciled canonical authority; unique 1,975-row feature matrix over 1,965 players; 3,059 eligibility grains; fixed closed window/cutoff; no synthetic product rows. |
| G-RW2 | PASS | Exact 1,975-candidate index; both transparent methods; full admitted-population scoring before limit; deterministic order, explanations, missingness, stale-pin and artifact-drift controls. |
| G-RW3 | PASS | One local browser journey covers dataset, exemplar/profile, ranked results, explanations, exact comparison, save/report, and replay without role switching, terminal use, or W08 administration. |
| G-RW4 | NOT PERFORMED | No expert relevance labels or football validation exist. This does not block honest W09 engineering, but it blocks every positive football-relevance or recruitment-usefulness claim. |

## 1. Data reconciliation, identity, rights, and physical authority

The accepted canonical manifest is `data/manifests/wyscout/v5/research/0837c2c3398362847da5ce1ace85a97ce9dd3299f6ba6a67c8a628ae8494ddc1.canonical-manifest.json`. Its physical SHA-256 independently reproduced as `a0cb68d5255d4a52dfe838eed632fca7793ec0b4999d9b0a80086179a40be031`.

| Boundary | Source | Canonical/accepted | Independent result |
|---|---:|---:|---|
| competitions | 7 | 7 | reconciled |
| teams | 142 | 142 | reconciled |
| players | 3,603 | 3,603 catalogue rows | reconciled; this is not the eligible count |
| matches | 1,826 | 1,826 | reconciled |
| actions | 3,071,395 | 3,071,395 | reconciled |
| appearances | n/a | 68,864 | unique `(match, team, player)` grains |
| identity exclusions | n/a | 16 | 15 review-required, 1 rejected; none admitted as a candidate |

Direct DuckDB/Parquet readback found 3,071,395 distinct canonical action IDs and 3,071,395 distinct source action IDs across 1,826 matches. Of those actions, 2,845,357 bind a resolved player and 226,038 retain a rejected/null actor; three actions have invalid coordinate evidence. The 68,864 appearance rows reconcile as 10,749 exact, 39,838 conservative-lower-bound, and 18,277 unusable. The 16 identity exclusions refer to 23 review-required and 226,041 rejected source rows/actions and expose no candidate canonical ID.

Every canonical artifact descriptor's recorded row count, size, SHA-256, schema version, and safe relative path reproduced through the production loaders. The authority explicitly records `wyscout_figshare_v5_cc_by_4`, the required attribution, `local_only: true`, and `raw_export_allowed: false`; the browser repeats the attribution and local-only/network-publication limitation.

The final feature authority is:

- matrix version `w09-historical-player-window-v1-22c725d54e41a916`;
- manifest semantic digest `9203c12dc100cbe4b2a2e089efa599d3de5bb374ab7ed35e34890ea957605e7c` (physical manifest SHA-256 `15f9021a41dacfd71f713fe1eca08ebf4d9a9deab728efcb87ebc073252ba7f0`);
- matrix digest `9a75b9842f60c048c5884953ce3391ae8d30b234180e443af654bd2d2f348441`;
- 3,603 catalogue decisions, 3,603 population decisions, 3,059 unique eligibility grains, 1,975 unique matrix grains, and 1,965 unique matrix players;
- eligibility reasons: 1,975 eligible, 439 unusable minutes, 645 below 450 minutes, and zero identity-membership, feature-missing, or temporal-cutoff failures after the earlier governed exclusions;
- 0 synthetic rows and 1,975 conservative-lower-bound minute rows.

The final index authority is index ID `5ca3b4d2-b4c4-5159-b96b-715ef4869495`, manifest digest `97d88a9fd1f4e46c42dc21da13992686991e03a6d86038a4fd9c0638ec32c14d`, catalogue digest `ff9894145f059fb9a91df87c4c497d19eadf8cf8f66e5664d66b64bee642e2af`, 1,975 candidates, 16 features, and 0 synthetic candidates. Production loading reproduced vector shape `(1975, 16)` and rejected both a stale pin set and a temporary tampered candidate catalogue. The relevant loader checks include matrix/catalogue uniqueness and lineage at `src/scouting/modeling/research.py:469`, `src/scouting/modeling/research.py:508`, `src/scouting/modeling/research.py:519`, and physical/semantic index verification at `src/scouting/modeling/research.py:984` through `src/scouting/modeling/research.py:1031`.

## 2. Temporal leakage, membership, and minutes

The source authority (`2020-01-28T14:24:27Z`) and identity authority (`2026-07-31T14:15:26Z`) are strictly before the feature cutoff (`2026-08-05T00:00:00Z`). The fixed feature window is `[2017-07-01T00:00:00Z, 2018-07-01T00:00:00Z)`, also strictly before the cutoff. These relations are contract-enforced at `src/scouting/contracts/research.py:138` through `src/scouting/contracts/research.py:145` and rechecked against the canonical and registry authorities at `src/scouting/features/historical.py:543` through `src/scouting/features/historical.py:551`.

Player/competition membership is built from match formation lineup/bench/substitution evidence at `src/scouting/data_products/wyscout/historical.py:1010` through `src/scouting/data_products/wyscout/historical.py:1174`. The manifests explicitly declare `current_team_id_used_for_membership: false` (`src/scouting/data_products/wyscout/historical.py:1635`, `src/scouting/features/historical.py:382`). Resolved actions that lack appearance-established membership fail closed at `src/scouting/features/historical.py:805`; action evidence is not used to invent membership or minutes.

Exact exits remain exact; terminal/no-exit intervals and six formation records without substitution evidence remain visibly conservative lower bounds or unusable. Feature aggregation admits only exact/lower-bound appearance states (`src/scouting/features/historical.py:78`, `src/scouting/features/historical.py:976`), propagates `minute_state`, and performs no silent imputation. The accepted population happens to contain only lower-bound eligible rows; that is a material evidence limitation, not a hidden exactness claim.

## 3. Retrieval, explanations, and stale-version behavior

Both `weighted_euclidean` and `weighted_cosine` use the exact robust scaler (median and linear-method IQR; constant dimensions use unit scale). The service validates exact pins before query execution (`src/scouting/serving/research.py:544`, `src/scouting/serving/research.py:587`), requires registry-ordered active features, accounts for every exclusion, scores all admitted rows, and applies the result limit only after scoring. Population arithmetic and deterministic result ordering are contract-enforced at `src/scouting/contracts/research.py:747` through `src/scouting/contracts/research.py:824`; full scoring and contribution construction are visible at `src/scouting/serving/research.py:809` through `src/scouting/serving/research.py:907`.

Independent production queries covered exemplar/profile × Euclidean/cosine and repeated exactly. The Italian S. Sirigu exemplar had 409 competition rows, one self-exclusion, 408 admitted/scored rows, and ten returned rows. M. Perin ranked first at `0.5526646247372221`; each candidate exposed all 16 raw/scaled contrasts and contributions with no hidden missing active feature. The weighted-profile browser query admitted/scored all 409 Italian rows. A stale pin set failed with `ResearchServingError: query pins are stale or incompatible`; a candidate-catalogue byte change in `/private/tmp/w09-independent-review-07a-index-tamper` failed with `ResearchIndexBuildError: candidate catalogue physical artifact drift`.

The frozen evaluation independently recomputes scaler operands, every returned contribution, Euclidean/cosine score, zero-weight behavior, and deterministic tie order at `src/scouting/evaluation/research.py:701` through `src/scouting/evaluation/research.py:857`. It does not treat sensitivity as ranking quality.

## 4. API, storage, report, and replay

The API exposes strict dataset, player-search, query, comparison, experiment, report, and replay contracts. It rejects a dataset/serving authority mismatch and any synthetic search population at `src/scouting/api/research.py:220` through `src/scouting/api/research.py:228`; result/comparison/save digests are bound before persistence at `src/scouting/api/research.py:316` through `src/scouting/api/research.py:404`. Replay executes the exact saved request and checks both deterministic result identity and digest at `src/scouting/api/research.py:435` through `src/scouting/api/research.py:496`.

The production acceptance experiment independently read from SQLite is `66372ff5-d444-4813-a260-76d4df2dda63`, bound to the final matrix/index versions above. Its canonical JSON report is content-addressed at `sha256/22/2220c20c7c3c84632fcca60af3e85db4025a5e3137aa6ba25dc6248789caccc2.json`; the file SHA-256 is exactly `2220c20c7c3c84632fcca60af3e85db4025a5e3137aa6ba25dc6248789caccc2`. It contains the exact query pins, ten ranked historical players, 408 scored rows, 16 contributions for the top candidate, two comparison rows, rights, warnings, and the historical-only claim.

Replay receipt `6c468c82-f5c3-5b29-ae7f-b14ab3f44817` records `status: reproduced` and equal original/replay result digest `f3c64b0a1d50fff9b9ba3a2bf611717191aa225e3743f18102002a16905e903d`. Experiment/report and replay tables are append-only; report bytes, canonical form, digest-derived path, and lineage are reverified on reads (`src/scouting/storage/research.py:389` through `src/scouting/storage/research.py:419`, `src/scouting/storage/research.py:534` through `src/scouting/storage/research.py:549`).

## 5. Browser journey and claim inspection

The real retained app was exercised at a loopback-only origin. It rendered one dataset authority with 1,826 matches, 3,071,395 actions, 142 teams, 3,603 source players, 1,975 matrix rows, and 1,965 eligible players. Direct browser actions covered:

1. search and select real S. Sirigu;
2. run the full-population exemplar query (408 scored, ten returned);
3. inspect visible limitations, missingness, 16 contribution terms, and scores;
4. compare exact M. Perin and T. Strakosha matrix rows, both visibly marked `conservative_lower_bound`;
5. switch to weighted profile and run a second full-population query (409 scored, ten returned);
6. inspect the retained saved report link and production replay evidence;
7. render at 320×800: `documentElement.scrollWidth == innerWidth == 320`, all main panels were 288px wide, and navigation overflow stayed inside its scrollable nav rather than the page.

The real journey made only same-origin loopback requests. The local middleware rejects non-loopback host headers and applies no-store, same-origin CSP/connect restrictions, frame denial, referrer, MIME, and permissions headers (`src/scouting/web/w09.py:63` through `src/scouting/web/w09.py:142`). The page contains semantic landmarks, labels, live status/error states, and a skip link. The real-browser automated acceptance independently passed exemplar/profile, both methods, explanation expansion, comparison, JSON/HTML save/report, replay, mismatch/incompatible replay states, keyboard navigation, a 320px viewport, same-origin containment, and distinct empty/422/409/503 states.

No W08 role, authentication, brief-revision, manual-audit, or pilot path appears in the W09 template, script, browser route, or production composition. W08 remains dormant rather than becoming the core journey. All rendered ranking language is historical resemblance/distance language and repeatedly disclaims football relevance and recruitment usefulness.

## 6. Frozen evaluation

The frozen suite digest is `be3d4f5a69ab57f3a53fa90b84f4fbfda94c7269f362afee9a8d5af9491872ba`. The retained result digest is `34a35882d1b9609cbf379783f6461b283f73bc37248c7b89b30eab0985c442c7`.

- 9 real-grain cases cover all four positions, all five eligible competitions, both query modes, and both retrieval methods.
- Every case ran twice at distinct fixed timestamps and reproduced exact result identity/digest, population, candidate order, scores, warnings, and explanations.
- 9 explanation witnesses checked 40 returned candidates and 200 active contribution terms (the empty-admission case checked zero); 15 filter witnesses cover self-exclusion, position, policy-floor/raised minutes, explicit exclusion, full-score-before-limit, and empty admission.
- The suite scored 2,841 admitted-row evaluations and returned 30 unique candidate grains. Returned-candidate coverage is only `30 / 1,975 = 0.0151898734`; this is correctly reported as coverage, not retrieval-quality evidence.
- Two ±0.1 weight sensitivity pairs retained all top five results; mean absolute displacement was 0.4 for Euclidean and 0.0 for cosine. Both witnesses explicitly set `sensitivity_only: true` and `validates_ranking_quality: false`.

`scripts/evaluate_w09_retrieval.py` was rerun against the final production authorities into `/private/tmp/w09-independent-review-07a-final-20260805-1`. It reproduced result digest `34a35882…42c7`, and `cmp -s` confirmed the new output was byte-for-byte identical to the retained evaluation file.

## Evidence limitations (not implementation defects)

`EL-01` — all 1,975 eligible rows use conservative-lower-bound minutes. Per-90 rates can therefore be overstated; the interface, manifests, evaluation, and report say so.

`EL-02` — the retained source is historical 2017/18 and only five domestic competitions pass the present closed-window/eligibility policy. It is neither a current market nor provider-parity result.

`EL-03` — the nine-case frozen suite is strong deterministic engineering evidence but covers only 30 unique returned grains (1.52% of the matrix) and has no relevance labels. The perturbations are sensitivity checks, not quality metrics.

`EL-04` — G-RW4 is absent. No expert has validated football relevance, recruitment usefulness, recommendation quality, value, availability, fit, or outcomes. Those positive claims remain blocked even though G-RW1 through G-RW3 pass.

## Reproductions run

- Packet pytest selection: **91 passed**, with one upstream Starlette/httpx deprecation warning.
- Ruff over the 12 scoped W09 source files: **passed**.
- mypy over the 12 scoped W09 source files: **passed**.
- Bandit over API/serving/web/evaluation/composition: **passed**.
- import-linter: **5 kept, 0 broken**.
- Final production matrix/index load: 3,603 catalogue, 3,603 population, 3,059 eligibility, 1,975 unique rows, 1,965 players, 0 synthetic, `(1975, 16)` index.
- Frozen evaluation regeneration: semantic digest and bytes reproduced exactly.
- Browser: real retained exemplar/profile and comparison path passed; the packet's temporary real-browser save/report/replay, responsive, keyboard, containment, and failure-state tests passed.

## Governance packet/return pairing

The final orchestration audit includes the durable bounded-rework packets `W09-FULL-CANONICAL-BUILD-02B-R2`, `W09-FULL-CANONICAL-BUILD-02B-R5`, and `W09-RESEARCH-STATE-04A-R2`. Their objectives, read-first sets, allowed paths, checks, stop conditions, and constraints match the already-retained R2/R5/R2 return reports. They document, respectively, strict rights/temporal/TOCTOU remediation, the six substitution-sentinel and conservative-minute reconciliation, and storage evidence for tightened explanation/replay contracts. These pairing records alter no implementation or accepted evidence and introduce no review finding.

## Final decision

**ACCEPT** — P0: 0, P1: 0, P2: 0, P3: 0. G-RW1, G-RW2, and G-RW3 are satisfied for the provider-neutral historical-player research workbench. G-RW4 remains deliberately unresolved and continues to block positive football-relevance and recruitment-usefulness claims.
