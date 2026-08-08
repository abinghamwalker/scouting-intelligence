# W04 independent source-authority boundary audit — R3

- Task: `W04-AUTHORITY-REVIEW-01-R3`
- Reviewer role: independent verifier
- Review date: 2026-07-29
- Recommendation: **ACCEPT**
- Defects: no reproduced `P0`, `P1`, or `P2`
- Data-access status: no protected fixture, archive payload, real provider data,
  external service, or network resource was accessed

## Executive result

The master’s archive-scope correction accurately records the published Wyscout v5 ZIP
directory shape without widening first-pass extraction or admission authority. Each
archive has exactly five admitted domestic members and exactly two known
scope-excluded tournament members:

- Matches exclusions:
  `matches_European_Championship.json` and `matches_World_Cup.json`.
- Events exclusions:
  `events_European_Championship.json` and `events_World_Cup.json`.

The admitted and excluded sets are disjoint. The configured handling is exactly
`verify_directory_entry_but_do_not_extract_or_admit_payload`, and the dataset card,
authority decision, and directory-preflight record all preserve that non-extraction
and non-admission boundary. Any other member remains unknown and denied.

The retained R1/R2 URL, path-alias, rights, archive-safety, temporal, claim, and
cross-artifact challenges remain green. Additive R3 mutations prove tournament
reclassification, duplicate admitted/excluded members, and six representative eighth
or otherwise unknown members fail the frozen scope. The complete
producer-plus-independent suite reports **43 passed**; Ruff and mypy also pass.

The reviewer recommends **ACCEPT**. This is an independent recommendation only; the
master retains task, phase, acquisition, and checkpoint authority.

## Controlling and reviewed artifacts

The reviewer read every R3 packet-required artifact completely:

- `AGENTS.md`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R3.yaml`
- `orchestration/task_packets/W04-AUTHORITY-REVIEW-01-R2.yaml`
- `orchestration/reviews/REVIEW-W04-AUTHORITY-REVIEW-01-R2.yaml`
- `configs/sources/w04-provider.yaml`
- `docs/dataset-cards/w04-source.md`
- `reports/phase-gates/W04/provider-rights-decision-required.md`
- `reports/phase-gates/W04/archive-directory-preflight.md`
- `tests/governance/test_w04_source_authority.py`
- `tests/security/test_w04_source_authority_boundary.py`
- `orchestration/templates/subagent_return.md`

The source authority, dataset card, decision, preflight, and producer test were read
only. No archive was opened and no member was extracted or parsed. The reviewer wrote
only the allowed independent test additions, this R3 report, and the mandatory return.

## Archive-scope correction readback

The recorded directory preflight establishes these exact observed entries:

| Archive | Five admitted members | Two directory-only exclusions |
| --- | --- | --- |
| `matches.zip` | England, France, Germany, Italy, Spain match JSON | European Championship and World Cup match JSON |
| `events.zip` | England, France, Germany, Italy, Spain event JSON | European Championship and World Cup event JSON |

The corrected authority has three distinct outcomes:

1. Exact domestic member: admitted for the first-pass extraction/data product.
2. Exact named tournament member: directory entry may be verified, but its compressed
   payload has no extraction or admission authority.
3. Any other member: unknown-member failure.

This change describes two already-published entries per ZIP. It does not add a
competition, enlarge the admitted population, or grant licence, product, model,
export, hosting, or network authority.

## Independent executable evidence

| Boundary challenge | R3 result | Evidence |
| --- | --- | --- |
| Exact archive directory shape | PASS | Each preflight section contains seven unique entries equal to the declared five admitted plus two excluded names |
| Exact admitted membership | PASS | Each match/event admitted list remains the five 2017/18 domestic top-flight members |
| Exact excluded membership | PASS | Each match/event exclusion list contains only European Championship and World Cup |
| Admitted/excluded disjointness | PASS | Both archives have disjoint five-member and two-member sets |
| Non-extraction/non-admission authority | PASS | Exact handling value plus consistent card, decision, and preflight language |
| Tournament reclassification | PASS | Each of the four excluded names fails if appended to its admitted list |
| Unknown/eighth member denial | PASS | Portugal, generic Europe, README, and metadata mutations remain undeclared and fail while `reject_unknown_members` is mandatory |
| Duplicate denial | PASS | Duplicating an admitted or excluded member in either archive fails the frozen scope |
| Link, absolute, and parent-path safety | PASS | All three safety switches remain mandatory; parent-path mutation remains rejected |
| URL and config-path exactness | PASS | Equivalent URL spellings, unrelated paths, parent aliases, and symlink aliases deny |
| Rights inheritance | PASS | Permissive CC BY rights cannot enable raw export, network transfer, external sharing, hosting, remote storage, public demo, or external-model use |
| Temporal availability | PASS | Collection release remains the earliest availability; acquisition time and pre-release replay mutations reject |
| Frozen claim boundary | PASS | Current/live/women-youth/prospective/provider-equivalence claims cannot become allowed |
| Producer governance suite | PASS | Producer independently checks exact excluded lists, handling, and disjointness |

## Authority-to-evidence mapping

| Authority boundary | Independent R3 evidence | Assessment |
| --- | --- | --- |
| Exact Wyscout Figshare v5 identity | DOI, version, release, licence, URLs, file identities, dataset card, and recorded decision remain consistent. | PASS |
| Local-only URL exception | Only exact reviewed URL strings at the literal normative source-config path receive the exception. | PASS |
| Rights inheritance | The stricter project boundary continues to deny external/export paths despite upstream CC BY permissions. | PASS |
| Five-competition admission | Both archives retain exactly five domestic members; no tournament member enters an admitted list. | PASS |
| Known archive exclusions | Both archives declare exactly two observed tournament entries, disjoint from admitted members and without payload authority. | PASS |
| Unknown/safe archive handling | Any undeclared or duplicate member fails; unknown, link, absolute, and parent-path denial flags remain mandatory. | PASS |
| Temporal and claim restrictions | Collection release remains the availability floor and only frozen historical claims remain allowed. | PASS |

## Command results

- Baseline before R3 additions:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `26 passed`
- Initial expanded run:
  - `40 passed, 3 failed`
  - all three failures were reviewer-harness parsing assumptions: indented Markdown
    bullets and equivalent non-extraction wording in the preflight report
  - no authority defect was indicated; the parsing helpers were corrected without
    weakening an invariant
- Final combined authority suite:
  `uv run pytest -q tests/governance/test_w04_source_authority.py tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - `43 passed`
- `uv run ruff format --check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - one file already formatted
- `uv run ruff check tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - all checks passed
- `uv run mypy tests/security/test_w04_source_authority_boundary.py`
  - exit `0`
  - no issues found in one source file

## Residual boundary

- This is an authority/configuration review. It does not implement or claim safe ZIP
  extraction, acquired-file digests, archive-bomb resistance, record counts, data
  quality, ingestion idempotency, modeling, or serving evidence.
- The preflight report was read as master-supplied evidence; the reviewer did not
  download, open, extract, or parse either provider archive or any JSON payload.
- Any future archive member, authority relocation, scope change, or URL revision needs
  an explicit reviewed update and must remain fail-closed until then.
- The master retains acquisition, implementation allocation, full integration,
  phase-gate, and every Git/checkpoint action.

## Recommendation

**ACCEPT.** The archive authority now truthfully represents five admitted plus two
known scope-excluded entries per ZIP while keeping their payloads out of the first pass
and preserving unknown, duplicate, link, absolute, and parent-path denial. All retained
R1/R2 controls and the complete expanded suite pass. This is a recommendation to the
master, not self-approval or a phase-gate decision.
