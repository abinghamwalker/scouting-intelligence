# W04 football event-data provider, rights, and coverage research packet

Status: **RESEARCH COMPLETE — SUPERSEDED BY USER'S FROZEN POC SOURCE DECISION**

Decision addendum, 2026-07-29: the user selected the Wyscout Soccer match event
dataset, figshare collection v5, under CC BY 4.0 for a one-time, local-only, frozen
proof of concept. The earlier NO-GO applied to a continuing governed operational
source and current/commercial scouting claims. It does not override the user's narrower
POC authority. The binding implementation scope and controls are recorded in
[`provider-rights-decision-required.md`](provider-rights-decision-required.md) and
[`configs/sources/w04-provider.yaml`](../../../configs/sources/w04-provider.yaml).

Research and access date: **2026-07-29**  
System boundary assessed: embedded SQLite and guarded local Parquet/vector artifacts only; no
cloud deployment, hosted CI, public endpoint, redistribution service, or external model
call.

This packet is decision support, not legal advice or legal approval. No account was
created, no terms were accepted, no purchase was made, and no event-data payload was
downloaded or inspected. Public documentation and licence documents were reviewed
without authenticating. A public Wyscout OpenAPI documentation file—not football
data—was temporarily fetched for schema review.

## Finding labels

Every substantive finding uses one of these labels:

- `C:` **CONFIRMED BY PRIMARY SOURCE** — stated in a provider, licensor, repository,
  data-paper, schema, price page, or published contract controlled by the relevant
  organisation.
- `I:` **REASONABLE INFERENCE** — a bounded conclusion from confirmed facts, but not a
  right, warranty, or provider commitment.
- `U:` **UNKNOWN / REQUIRES WRITTEN CONFIRMATION** — absent, ambiguous, conflicting,
  product-specific but unpublished, or dependent on an Order Form/Work Order/direct-use
  licence.

“Allowed,” “restricted,” and “forbidden” below describe published text only. A public
product page or reachable repository is never treated as a grant of rights.

## Executive decision

**Current decision: NO-GO for acquisition or implementation.**

- `C:` The current Hudl Master Subscription Agreement permits customer content use for
  internal business purposes and defines those purposes to include scouting, but its
  default restrictions prohibit copying/downloading, modification and derivative works,
  model training, display/distribution, third-party availability, and continued use
  after the subscription. An Order Form may override the MSA for its subject matter.
  ([HUDL-MSA])
- `C:` Stats Perform's published Master License Agreement likewise makes the Work Order
  decisive and, by default, prohibits bulk download/archive, editing/manipulation,
  derivative works, downloadable outputs, redistribution, and use in ML, AI, or
  generative-AI development or training. It may also require a separate direct-use
  licence from a governing rights owner. ([OP-MLA])
- `I:` Those defaults conflict with immutable Bronze preservation, canonical Silver
  transformation, Gold derivation, retrieval/model evaluation, a local UI, generated
  explanations, and bounded exports. No commercial finalist is usable unless signed,
  product-specific terms expressly grant each required right.
- `C:` The Wyscout figshare dataset v5 and the DFL Integrated Data Set for Soccer
  Analytics are published under CC BY 4.0, which permits sharing and adaptation for any
  purpose, including commercially, subject to attribution and change notices and only
  for rights the licensor controls. ([WY-PAPER], [IDSSE], [CC-BY])
- `I:` Those two datasets are suitable for local schema prototyping, frozen evaluation,
  or tracking/event reconciliation only. One is a static 2016–2018 event collection
  without women's or youth coverage; the other contains only seven 2022/23 men's
  matches. Neither can govern a current scouting product.

### Shortlist

1. **Conditional primary — Hudl StatsBomb Data plus StatsBomb 360**

   - `C:` Rich event semantics, provider event UUIDs, millisecond match timestamps,
     possession context, lineups/substitutions, event coordinates, human quality
     assurance, and optional contextual 360 frames are publicly documented. The
     commercial product advertises more than 3,400 events per match and JSON, XML, and
     CSV delivery. ([SB-DATA], [SB-360], [SB-EVENTS], [SB-LINEUPS])
   - `I:` This is the best technical fit for transparent, possession-aware, spatial
     scouting features and explanations.
   - `U:` Current competition-by-season coverage, women/youth depth, historical
     entitlement, price, post-match delivery SLA, corrections API, immutable snapshot
     support, and every required local/model/display/export right need a signed Order
     Form.

2. **Conditional fallback — Hudl Wyscout Data v3, Database Pack plus Events Pack**

   - `C:` Wyscout advertises 600+ competitions, 500,000+ player profiles, up to five
     years of history, roughly 1,800 events per match, stable `wyId` identifiers,
     formations, substitutions, possession objects, event coordinates, and an updated
     objects endpoint covering match events. ([WY-API-PRODUCT], [WY-DOC],
     [WY-OPENAPI])
   - `I:` Broader advertised scouting coverage and explicit update polling make it the
     strongest fallback when coverage matters more than StatsBomb 360 context.
   - `U:` Exact licensed leagues/seasons, women/youth event depth, deletion/tombstone
     behaviour, past-version retrieval, price, and all project-specific rights remain
     subject to the same Hudl MSA and an Order Form.

3. **Conditional third finalist — Stats Perform Opta F24 XY Event Data Feed**

   - `C:` Opta advertises F24 x/y event data, more than 60 standardised on-field event
     types, pass origin/destination coordinates, long historical archives, and optional
     Opta Vision continuous x/y tracking for all 22 players in more than 80 leading
     competitions. ([OP-GRANULAR], [OP-DEFS], [OP-VISION])
   - `I:` Opta has the strongest public continuity and optional tracking proposition,
     but is less decision-ready because the current F24 schema, feed version, football
     coverage matrix, identity semantics, correction protocol, and pricing are not
     public.
   - `U:` A bespoke Work Order, possible direct-use licences, and written permission for
     every local/model/display/export use are mandatory.

### Recommended route

- `I:` Send the same bounded request-for-information and rights schedule to StatsBomb,
  Wyscout, and Stats Perform. Compare only written responses and draft contractual
  language.
- `I:` Select StatsBomb Data + 360 if it grants the required rights, covers the target
  competition-season matrix, exposes correction and availability semantics, supplies
  reproducible content versions or permits customer snapshots, and fits the budget.
- `I:` Select Wyscout Data v3 Database + Events as fallback if StatsBomb fails any of
  those gates and Wyscout passes them.
- `I:` Keep Opta F24 as the negotiating benchmark and third finalist; add Opta Vision
  only if continuous tracking is a funded requirement rather than a W04 ideal.
- `C:` Do not implement an adapter, acquire credentials, or ingest data until the W04.1
  packet is replaced with the signed product/right/coverage evidence described below.

## Comparison table

| Candidate and exact public version | Access / pricing | Coverage | Technical fit | Temporal and snapshot fit | Published-rights fit | Decision |
|---|---|---|---|---|---|---|
| Hudl **StatsBomb Data + StatsBomb 360**; commercial schema version `U` | `C:` Commercial; contact team/sales, no public price. ([SB-DATA]) | `C:` 140+ leagues advertised for 2024; commercial page also documents women's coverage historically. Current league-season matrix and youth depth `U`. ([SB-DATA], [SB-WOMEN]) | `C:` 3,400+ events/match, coordinates, outcomes, pressures, possession, IDs, lineups and optional contextual 360; JSON/XML/CSV. ([SB-DATA], [SB-360], [SB-EVENTS]) | `C:` Public schema exposes event time and match `last_updated`; open catalogue exposes availability/update fields. Commercial correction history, publication SLA, immutable revisions, and snapshot entitlement `U`. ([SB-MATCHES], [SB-COMP]) | `C:` Default Hudl MSA conflicts with retention, transformation, ML, display, and export; Order Form can override. ([HUDL-MSA]) | **Conditional primary; no acquisition yet.** |
| Hudl **Wyscout Data v3 Database Pack + Events Pack**; docs build 2026-06-26 | `C:` Commercial; contact sales. ([WY-PRICE]) | `C:` 600+ competitions, 500k+ players, up to 5 years advertised. Exact countries/seasons/women/youth/event tier `U`. ([WY-API-PRODUCT]) | `C:` ~1,800 events/match; `wyId`, event/period/minute/second, x/y, pass/shot/duel outcomes, possession, formations, substitutions; REST JSON/OpenAPI. ([WY-DOC], [WY-OPENAPI]) | `C:` `updatedobjects` supports `matchevents`, max seven-day lookback, recommended multiple polls/day; API version overlap is at least six months. No immutable content history or tombstone guarantee is published. ([WY-DOC], [WY-OPENAPI]) | `C:` Same default Hudl restrictions as StatsBomb. ([HUDL-MSA]) | **Conditional fallback; no acquisition yet.** |
| Stats Perform **Opta F24 XY Event Data Feed**; current feed schema/version `U`; optional **Opta Vision** | `C:` Commercial custom quote/contact sales. ([OP-PRICE]) | `C:` “hundreds of leagues” for granular football; broad women's offering; Opta archive up to 35 years; exact purchased matrix `U`. ([OP-GRANULAR], [OP-WOMEN]) | `C:` F24 x/y events and >60 action definitions; Vision adds continuous all-22 tracking and synchronisation. Public F24 schema/minutes/possession/freeze-frame details `U`. ([OP-GRANULAR], [OP-DEFS], [OP-VISION]) | `C:` Provider says feeds are captured, validated, and stored. Record availability/correction/version fields and reproducible snapshots `U`. ([OP-FEEDS]) | `C:` Default MLA bars archive, transforms, ML, downloadable outputs, and redistribution; Work Order and possibly direct-use licence control. ([OP-MLA]) | **Conditional third finalist.** |
| Sportradar **Soccer Extended API v4** | `C:` Commercial/contact sales; public 30-day trial is 1,000 calls/30 days at 1 QPS. ([SR-ACCOUNT]) | `C:` 1,000+ competitions, men and women, with per-match coverage tiers; youth depth `U`. ([SR-BASICS], [SR-TIERS]) | `C:` JSON/XML REST, push feeds, >100 statistics, extended timeline actions and x/y, lineups/formations/substitutions. No freeze-frame/tracking. ([SR-EXT], [SR-TIMELINE]) | `C:` created/updated/removed feeds, UTC `updated_at`, 24-hour update windows, removed IDs for two weeks; standard historical access is constrained. ([SR-CHANGES], [SR-HISTORY]) | `U:` No public product licence located that affirmatively grants the required local/model/display/export rights. | **Reject for W04 shortlist.** |
| Sportmonks **Football API v3** | `C:` €29/€99/€249 monthly public tiers; enterprise custom; historical and xG add-ons. Published rate pages conflict on Growth/Pro limits. ([SM-PRICE], [SM-RATE]) | `C:` up to 2,300+ leagues advertised; exact event depth, women/youth and historical entitlement by league `U`. ([SM-PRICE]) | `C:` lineups/minutes and significant events such as goals, cards and substitutions; separate ball coordinate/live trend includes. `I:` Not a full on-ball event stream. ([SM-EVENTS], [SM-INCLUDES]) | `U:` No immutable snapshot, content-version, availability-time, or record-level correction protocol found. | `C:` Terms say data may be stored/transferred/distributed and resale needs consent; transformations, ML, UI, explanations and derived exports are not expressly addressed. ([SM-TERMS]) | **Reject: insufficient action granularity and rights precision.** |
| API-Sports **API-Football v3.9.3** ([AF-DOC]) | `C:` free 100 calls/day; paid $19/$29/$39 monthly tiers. ([AF-PRICE]) | `C:` 1,235 leagues/cups and a public coverage matrix including women/youth competitions. ([AF-PRODUCT], [AF-COVERAGE]) | `C:` fixtures, lineups, statistics and event highlights (goals/cards/substitutions). `C:` No full action-coordinate feed is advertised. ([AF-PRODUCT]) | `U:` Content correction, availability, record-version and snapshot semantics are not published. | `C:` Terms state API-Football does not grant a licence for use/publication and users must obtain permissions from competent authorities; resale is prohibited. ([AF-TERMS]) | **Reject: rights chain not supplied and event data too sparse.** |
| Hudl **StatsBomb Open Data**, Events v4 / Matches v3 / Lineups v2 / Competitions v2 / 360 v1 | `C:` Free public-data agreement for research/analysis and genuine interest; not an OSI-style or CC open licence. ([SB-OPEN], [SB-PUBLIC-LIC]) | `C:` Mutable catalogue across selected men's, women's, and historic competitions/seasons; selected 360. No continuity commitment. ([SB-FREE], [SB-COMP]) | `C:` Excellent schema fit, including event UUIDs, x/y, possession, outcomes, lineups and selected 360. ([SB-EVENTS], [SB-360]) | `C:` Schema/catalogue include update and availability fields; repository commits can be pinned. No release-level content guarantees or correction history. ([SB-COMP], [SB-OPEN]) | `C:` Agreement forbids editing, distribution/reproduction, external provision, commercial exploitation of data, and commercial exploitation of derived analysis; attribution required for publication. ([SB-PUBLIC-LIC]) | **Reject as governed operational source.** |
| **Wyscout Soccer match event dataset**, figshare collection version 5 / DOI 10.6084/m9.figshare.c.4415000.v5 | `C:` Open data, CC BY 4.0. ([WY-PAPER], [WY-FIGSHARE]) | `C:` 1,941 matches: 2017/18 big-five leagues plus Euro 2016 and World Cup 2018; 4,299 players. No women/youth/continuing seasons. ([WY-PAPER]) | `C:` 3,251,294 JSON events, IDs, periods, elapsed seconds, origin/destination x/y, tags/outcomes, lineups/bench/substitutions. No native possession ID, freeze-frame, or tracking. ([WY-PAPER]) | `C:` Versioned DOI gives a frozen v5 snapshot. No event availability timestamp, ongoing updates, or correction ledger. | `C:` CC BY permits sharing/adaptation, including commercially, with attribution/change notice; ML is not named. ([CC-BY]) | **Best open event benchmark; reject as live governed source.** |
| DFL **Integrated Data Set for Soccer Analytics (IDSSE)**, Scientific Data 2025 publication | `C:` Open data, CC BY 4.0 with stated DFL authorisation. ([IDSSE]) | `C:` Seven men's matches from Bundesliga/Bundesliga 2, 2022/23; 207 players/10 teams. No women/youth/continuity. ([IDSSE]) | `C:` 11,137 events plus 1,002,644 synchronised tracking frames, x/y, ball state/possession, lineups, timestamps and event context in XML. ([IDSSE]) | `C:` Frozen publication snapshot; no continuing correction or release channel. | `C:` CC BY rights with attribution/change notice; ML is not named. ([IDSSE], [CC-BY]) | **Best open tracking/event QA set; reject as governed source.** |
| Metrica Sports **Sample Data**, GitHub `master`, three anonymised matches | `C:` Public samples; no formal licence file identified. README requests responsible use and acknowledgement. ([METRICA]) | `C:` Three anonymised matches only. | `C:` synchronised event/tracking samples in CSV/JSON/EPTS forms. ([METRICA]) | `U:` No versioned release, correction protocol, or availability semantics. | `U:` Public accessibility and an acknowledgement request are not a licence grant. | **Reject: no adequate licence and trivial scope.** |

## Published-rights comparison

The table evaluates the published baseline before any private Order Form, Work Order,
data-owner permission, or legal advice. “Restricted” means the text is narrower than the
project requirement; it is not permission to proceed.

| Required use | Hudl commercial MSA: StatsBomb/Wyscout | Stats Perform MLA | Sportradar Extended | Sportmonks v3 | API-Football | StatsBomb Public Data Agreement | CC BY 4.0 datasets | Metrica samples |
|---|---|---|---|---|---|---|---|---|
| Local raw-data retention | `C:` **Restricted** — default copy/download ban; delete/stop use after term; API delivery may be specified in Order Form. | `C:` **Forbidden by default** — no bulk download/archive; return/destroy at end, unless Work Order allows. | `U:` No affirmative grant located. | `C:` **Allowed in general** — terms say data may be stored; duration/snapshot scope `U`. | `U:` No supplied data licence; other rights permissions required. | `U:` GitHub access requires a local transfer but the agreement does not affirm archival retention and forbids reproduction. | `C:` **Allowed** within licensed copyright/database rights. | `U:` No licence. |
| Normalised/transformed datasets | `C:` **Restricted/forbidden by default** — no modification or derivative works. | `C:` **Forbidden by default** — no editing, manipulation, or derivative works. | `U:` | `U:` Storage is allowed; transformation is not addressed. | `U:` | `C:` **Restricted** — no editing/distortion; transformation right not granted. | `C:` **Allowed** as adaptation; indicate changes when shared. | `U:` |
| Derived statistics/features | `I:` Likely a derivative work; explicit grant required. | `C:` **Restricted by default**; only Work Order-permitted usage. | `U:` | `I:` Terms contemplate creating a product from data, but the exact derived-feature right is not stated. | `U:` | `C:` Analysis is contemplated only for noncommercial research/genuine interest; commercial exploitation of any analysis is forbidden. | `C:` **Allowed** as adaptation/use, subject to attribution on sharing. | `U:` |
| Model training/evaluation | `C:` **Expressly forbidden by default**, including ML/AI models or algorithms. | `C:` **Expressly forbidden by default**, including training, developing, testing, enhancing, populating, or supporting ML/AI/gen-AI. | `U:` | `U:` Not addressed. | `U:` | `U:` Research analysis is allowed, but model training/evaluation is not named. | `I:` Permitted by broad use/adaptation grant, but ML is not expressly named. | `U:` |
| Internal scouting/recruitment | `C:` **Allowed in principle** as an Internal Business Purpose, but only within all other product/content restrictions. | `U:` Must be stated as Permitted Usage in the Work Order and any direct-use licence. | `U:` | `I:` Likely within a customer's own product use; written confirmation needed. | `U:` API use does not supply the underlying competition permission. | `U:` Noncommercial research is allowed; professional recruitment may be commercial exploitation. | `C:` **Allowed** within licensed rights. | `U:` |
| Internal UI display | `C:` **Restricted by default** — display is prohibited except as expressly permitted by the Agreement/Product and limited to authorised users. | `C:` **Restricted by default** — platform, display, fields, territory and permitted usage must be in Work Order. | `U:` | `U:` Not expressly described. | `U:` Underlying publication/display permission must be obtained elsewhere. | `U:` Sharing analysis is contemplated, but a persistent internal product display is not stated. | `C:` **Allowed** within licensed rights; attribution obligations attach when material is shared. | `U:` |
| Generated explanations | `U:` Customer-generated explanation right is unstated; local model training is expressly barred by default. | `U:` Unstated; default ML/gen-AI prohibition blocks the intended route. | `U:` | `U:` | `U:` | `U:` Research analysis may be discussed, but generated-model explanations are not addressed. | `I:` Allowed as derived/adapted output, subject to attribution when shared and no endorsement. | `U:` |
| Raw-data export | `C:` **Forbidden by default**, including distribution, disclosure, publication, and third-party access. | `C:` **Forbidden by default**, including downloadable/copyable and retransmittable output. | `U:` | `C:` Transfer/distribution is stated generally, but resale requires consent; recipient and competition-right limits `U`. | `C:` Resale prohibited; underlying publication licence not supplied. | `C:` **Forbidden**, including distribution, reproduction, sale, and provision to external third parties. | `C:` **Allowed** with attribution, licence link, and applicable change notice. | `U:` |
| Derived-result export | `U:` Not separately granted; derivative and distribution restrictions make an explicit carve-out mandatory. | `U:` Must be expressly defined in the Work Order, including fields, recipients, and downloadability. | `U:` | `U:` Not expressly addressed. | `U:` Underlying permission still required. | `C:` Noncommercial publication of analysis is contemplated with required attribution/logo; commercial derived export is forbidden. | `C:` **Allowed** with attribution obligations when sharing licensed/adapted material. | `U:` |
| Redistribution/publication | `C:` **Forbidden by default**. | `C:` **Forbidden except Work Order-permitted service/platform/territory/use**. | `U:` | `C:` Data distribution is stated, but product resale is forbidden without consent; exact publication rights `U`. | `C:` Provider does not grant publication rights; user must obtain them. | `C:` Raw data redistribution forbidden; publication of analysis is noncommercial and attributed. | `C:` **Allowed** with CC BY conditions and no implied endorsement. | `U:` |
| Commercial use | `C:` Internal business use, including scouting, is allowed in principle; external commercial exploitation is forbidden and other restrictions still apply. | `U:` Only the Work Order's Permitted Usage; direct-use licences may also be required. | `U:` | `C:` Terms say creating something with data and earning from it is in principle acceptable; resale needs consent. Exact model/UI/export uses `U`. | `C:` API-Football disclaims a competition-data licence and says commercial rights belong to rights holders. | `C:` **Forbidden** for both data and derived analysis. | `C:` **Allowed** within licensed rights. | `U:` |
| Required attribution | `C:` Proprietary notices must not be removed; a project-output attribution form is `U`. | `C:` Stats Perform logo/copyright attribution is required for uses of statistical content unless the Work Order changes it. | `U:` | `U:` Terms do not define a complete attribution schedule for data outputs. | `U:` Third-party rights-holder requirements may apply. | `C:` Publication must credit StatsBomb and use the specified brand/logo approach. | `C:` Credit, licence link, and change indication are required when sharing; no endorsement. | `C:` README requests acknowledgement for public use, but this is not a complete licence. |

Evidence: [HUDL-MSA], [OP-MLA], [SM-TERMS], [AF-TERMS],
[SB-PUBLIC-LIC], [CC-BY], [METRICA].

## Candidate dossiers

### 1. Hudl StatsBomb Data plus StatsBomb 360

1. **Provider/product/version**
   - `C:` Provider: Hudl/StatsBomb; products: StatsBomb Data and optional StatsBomb
     360. ([SB-DATA], [SB-360])
   - `U:` The current commercial event-schema, taxonomy, and delivery release number
     are not publicly frozen. Open-data Events v4, Matches v3, Lineups v2,
     Competitions v2, and 360 v1 document public-data structures; they must not be
     assumed to be the contracted commercial schema. ([SB-DOCS])
2. **Access model**
   - `C:` Commercial subscription/API product. A separate public-data programme exists
     under different terms and is assessed in dossier 7.
3. **Price**
   - `C:` No public tariff was found; the product page directs prospects to contact the
     team. ([SB-DATA])
4. **Coverage**
   - `C:` The commercial page says 140+ leagues were covered in 2024. StatsBomb has
     publicly described coverage of leading women's competitions, but the cited
     women's list is historical rather than a current contract matrix. ([SB-DATA],
     [SB-WOMEN])
   - `U:` Exact countries, competitions, season start/end dates, backfill depth,
     promotion/relegation continuity, women/youth event parity, and 360 availability
     must be attached to the quote.
5. **Files/endpoints/formats/delivery**
   - `C:` JSON, XML, CSV, API documentation, and technical support are advertised.
     StatsBomb's public live guide documents GraphQL queries/subscriptions and
     competition-season, lineup, match, event, and squad schemas. ([SB-DATA],
     [SB-LIVE])
   - `U:` Whether W04 would receive batch files, a post-match REST API, live GraphQL, or
     multiple channels; re-download rules; and bulk backfill delivery are quote-specific.
6. **Fields**
   - `C:` Product materials describe 3,400+ events per match, pressure, pass foot/height,
     shot freeze frames, human QA, and 360 teammate/opponent positions around events.
     ([SB-DATA], [SB-360])
   - `C:` Public schema v4 documents event UUID, index, period, match timestamp to
     milliseconds, minute, second, type, possession and possession team, play pattern,
     team/player/position IDs, x/y, duration, pressure, pass/shot outcome, and
     substitution replacement. Lineups v2 covers player/team IDs, positions, cards and
     country. ([SB-EVENTS], [SB-LINEUPS])
   - `C:` 360 v1 documents an event UUID, visible-area polygon, and freeze-frame
     locations with teammate/actor/keeper flags. It is contextual freeze-frame, not
     continuous tracking; some events/players are outside the visible area. ([SB-360-SCHEMA])
   - `U:` Commercial field parity with those public schemas, explicit minutes/stints,
     player-biographical identity fields, and data-completeness flags require a sample
     schema under non-acceptance review terms or written specification.
7. **Time/correction/version/snapshot**
   - `C:` Public Matches v3 includes match date/kickoff/status, `last_updated`, and
     metadata data version. Public Competitions v2/catalogue includes match update and
     availability fields for event and 360 data. ([SB-MATCHES], [SB-COMP])
   - `C:` Event time is match-clock time; it is not evidence of when the provider first
     made the fact available.
   - `U:` Commercial first-published time, finalisation SLA, record-level revision ID,
     correction cause, deletion/tombstone handling, retained historical revisions,
     late lineup change semantics, and provider-signed snapshot hashes are not public.
8. **Limits/auth/dependencies**
   - `C:` The public live API uses client credentials to obtain a token valid for 24
     hours; GraphQL supports queries and subscriptions. ([SB-LIVE])
   - `U:` Post-match rate limits, concurrency, page/bulk limits, backfill windows,
     service availability, credentials, IP restrictions, and support SLA are
     contract-specific.
9. **Rights**
   - `C:` The Hudl commercial column in the rights table applies. The published default
     is incompatible with W04 unless the Order Form expressly overrides it.
10. **Risks**
    - `I:` **Quality:** rich semantics and human QA are strengths; subjective event
      labels, visible-area omissions, and provider methodology changes still need
      monitoring.
    - `I:` **Identity:** provider UUID/event IDs help lineage, but player merge/split,
      alias, transfer, academy-to-senior, and placeholder policies are unknown.
    - `I:` **Leakage:** match-clock timestamps alone cannot establish fact availability.
      Local `ingested_at` does not cure a missing provider `available_at`; Gold must use
      a contractual availability/finalisation rule.
    - `I:` **Continuity/lock-in:** proprietary taxonomy, 360 semantics, and a
      delete-at-termination default create high lock-in and reproducibility risk.
11. **Evidence**
    - Product/schema: [SB-DATA], [SB-360], [SB-DOCS], [SB-EVENTS], [SB-MATCHES],
      [SB-LINEUPS], [SB-360-SCHEMA], [SB-COMP], [SB-LIVE].
    - Rights: [HUDL-MSA].
12. **Provider questions**
    - Grant the complete project rights schedule under “Mandatory written terms.”
    - Supply an exact competition-season-gender-age-level matrix for event and 360 data.
    - Supply current schemas, event taxonomy, identity dictionary, sample change event,
      and version lifecycle without providing licensed match payload.
    - Define `occurred_at`, `first_available_at`, `corrected_at`, finalisation, revision,
      deletion, and backfill semantics and their timezones.
    - State whether all revisions may be retained after correction and after contract
      expiry solely for reproducibility/audit, and whether hashes may be recorded.

### 2. Hudl Wyscout Data v3, Database Pack plus Events Pack

1. **Provider/product/version**
   - `C:` Hudl Wyscout Data API, Database Pack plus Events Pack; public API v3
     documentation build dated 2026-06-26. ([WY-DATA], [WY-DOC])
2. **Access model**
   - `C:` Commercial API/data product; no account was created and no trial was used.
3. **Price**
   - `C:` Data/API packages are “contact sales.” Public platform subscription pricing
     is not evidence of API entitlement. ([WY-PRICE])
4. **Coverage**
   - `C:` Wyscout advertises 600+ competitions, 500,000+ player profiles, 2,000 tagged
     games per matchday, and up to five years of historical data. ([WY-API-PRODUCT])
   - `C:` The schema supports competition and player gender, and team structures can
     include academy age groups. This proves schema capability, not licensed event
     coverage. ([WY-DOC])
   - `U:` Exact countries, seasons, women's competitions, youth competitions, match
     completeness, event-tier parity, and years available per competition.
5. **Files/endpoints/formats/delivery**
   - `C:` REST JSON with downloadable OpenAPI 3 specification; endpoints cover areas,
     competitions, seasons, rounds, matches, teams, players, careers, lineups/formations,
     substitutions, events, possessions, and updated objects. ([WY-DOC], [WY-OPENAPI])
   - `U:` Bulk file delivery, initial backfill export, event video linkage entitlement,
     and offline re-download capability.
6. **Fields**
   - `C:` Events expose a unique integer ID, match/period, match timestamp,
     minute/second, attack-oriented percentage x/y, team/opponent/player IDs, and typed
     pass/shot/duel details and outcomes. Possessions expose ID, duration, start/end,
     event count, team, and type. Formations and substitutions include time spans and
     player IDs. ([WY-DOC], [WY-OPENAPI])
   - `C:` Product material advertises an average of 1,800 tagged events per match.
     ([WY-API-PRODUCT])
   - `U:` Full minutes-played field, freeze-frame/tracking, stable cross-provider
     identity links, and completeness/quality flags. No 360-like freeze-frame is
     documented in the selected packs.
7. **Time/correction/version/snapshot**
   - `C:` `/updatedobjects` accepts `matchevents` and other resource types, looks back
     at most 168 hours, caps payloads at 10 MB, recommends polling every 1–4 hours or
     several times daily, and says unspecified times are Europe/Rome. ([WY-OPENAPI])
   - `C:` API Current/Preview/Legacy lifecycle retains the prior Current until another
     Current is released, at least six months later. This is interface versioning, not
     a historical content ledger. ([WY-DOC])
   - `U:` First-publication timestamp, exact updated timestamp in each response,
     before/after revision IDs, deletion/tombstone channel, correction reasons,
     immutable historical response retrieval, and snapshot hashes.
8. **Limits/auth/dependencies**
   - `C:` HTTP Basic authentication and 12 requests/second/API key; list endpoints often
     cap a page at 100 records; `updatedobjects` has its separate 10 MB/one-week
     operational constraint. ([WY-DOC], [WY-OPENAPI])
   - `I:` Missing a week of update polling can silently lose correction notices unless
     full reconciliation is contractually and technically available.
9. **Rights**
   - `C:` The Hudl commercial column in the rights table applies. An Order Form must
     override the incompatible defaults.
10. **Risks**
    - `I:` **Quality:** lower advertised event density than StatsBomb and no documented
      360 context can limit pressure/off-ball explanations.
    - `I:` **Identity:** `wyId` is a strong source key, but current-team/profile fields
      can reflect knowledge later than a historical match. Canonical identity must be
      time-versioned.
    - `I:` **Leakage:** Europe/Rome defaults, live profile changes, and absent
      first-availability fields require explicit as-of policy.
    - `I:` **Continuity/lock-in:** broad Wyscout IDs and taxonomy are proprietary; the
      one-week update window and at-least-six-month interface overlap are operational
      dependencies, not archival guarantees.
11. **Evidence**
    - Product/schema/operations: [WY-DATA], [WY-API-PRODUCT], [WY-DOC],
      [WY-OPENAPI], [WY-PRICE].
    - Rights: [HUDL-MSA].
12. **Provider questions**
    - Answer the complete rights and coverage schedule.
    - Confirm whether `updatedobjects` includes every event correction and deletion,
      how a removed event is represented, and how to recover after more than seven days.
    - Define publication/finalisation times, source timezone, stable-ID
      merge/split/deprecation policy, and historical player-profile semantics.
    - Confirm customer-created immutable snapshots, revision retention after term,
      local hashes/manifests, and bounded internal export.

### 3. Stats Perform Opta F24 XY Event Data Feed

1. **Provider/product/version**
   - `C:` Stats Perform Opta; public product name F24 x/y football event data, with
     optional Opta Vision tracking. ([OP-GRANULAR], [OP-VISION])
   - `U:` Current feed schema/version identifier and whether a modern replacement name
     would appear in the Work Order.
2. **Access model**
   - `C:` Commercial data-feed licence; API/data-feed delivery is productised.
3. **Price**
   - `C:` Custom quote/contact sales; scope can be customised by competition, country,
     and data level. ([OP-PRICE])
4. **Coverage**
   - `C:` The granular-data page advertises hundreds of leagues and an archive reaching
     35 years; Stats Perform markets broad women's-sport coverage. Opta Vision is
     advertised in 80+ leading competitions. ([OP-GRANULAR], [OP-WOMEN],
     [OP-VISION])
   - `U:` Football-only current competition-season-country matrix, women/youth parity,
     historical event depth, and tracking availability by match.
5. **Files/endpoints/formats/delivery**
   - `C:` Opta Data Feeds are delivered through APIs/data feeds; the product page also
     describes widgets and other products. ([OP-FEEDS])
   - `U:` Exact F24 endpoint/file names, formats, authentication, backfill delivery,
     compression, pagination, and schema files are not public.
6. **Fields**
   - `C:` Public definitions cover more than 60 standardised actions and pass
     origin/destination x/y. F24 is explicitly x/y data. Vision adds synchronised,
     continuous x/y tracking for all 22 players and more than two million points per
     game, with generative estimation for players outside the broadcast frame.
     ([OP-DEFS], [OP-GRANULAR], [OP-VISION])
   - `U:` Lineup/minutes/substitution schema, possession identifiers, event UUID
     stability, outcomes/qualifiers, freeze-frame representation, ball coordinates,
     formation, and identity fields in the offered feed.
7. **Time/correction/version/snapshot**
   - `C:` Stats Perform says data is captured, validated, and stored and has a
     long-running archive. ([OP-FEEDS], [OP-GRANULAR])
   - `U:` Event occurrence precision, provider availability timestamp, publication
     delay, provisional/final states, correction feed, revision IDs, deletion
     semantics, schema lifecycle, and reproducible prior snapshots.
8. **Limits/auth/dependencies**
   - `C:` The published MLA baseline states two million API calls/month and 20
     calls/second, with a listed charge for additional call volume, unless varied by
     Work Order. ([OP-MLA])
   - `U:` Actual F24 delivery may use a different entitlement, authentication method,
     polling/push pattern, or SLA.
9. **Rights**
   - `C:` The Stats Perform column in the rights table applies. The Work Order controls
     permitted service, platform, territory and use; separate direct-use licences may
     be required. ([OP-MLA])
10. **Risks**
    - `I:` **Quality:** long-running standardisation is attractive; Vision's
      out-of-frame positions are model-generated, so observed versus estimated data
      must be separable.
    - `I:` **Identity:** stable source identities are likely necessary for the product,
      but the public materials do not prove player-ID persistence or merge history.
    - `I:` **Leakage:** “validated and stored” is not a record-level availability
      contract. Without one, temporally safe Gold cannot be proven.
    - `I:` **Continuity/lock-in:** proprietary qualifiers and broad historic dependence
      create high migration cost; direct-use rights can vary by competition and rights
      owner.
11. **Evidence**
    - Product: [OP-FEEDS], [OP-GRANULAR], [OP-DEFS], [OP-VISION], [OP-WOMEN],
      [OP-PRICE].
    - Rights/limits: [OP-MLA].
12. **Provider questions**
    - Supply the exact feed/version/schema/data dictionary and event/identity change
      policies.
    - Supply the licensed competition-season matrix and identify every required
      Football DataCo, league, federation, or other direct-use licence and cost.
    - Define availability/finalisation/correction/deletion/snapshot semantics.
    - Put every required retention, derivative, model, internal display, explanation,
      audit, and export right in the Work Order, including survival after termination.

### 4. Sportradar Soccer Extended API v4

1. **Provider/product/version**
   - `C:` Provider: Sportradar; product: Soccer Extended API v4 with optional push
     feeds. ([SR-BASICS], [SR-EXT])
2. **Access model**
   - `C:` Commercial B2B API. A public self-service trial exists, but no trial was
     started and trial access would not establish production rights. ([SR-ACCOUNT])
3. **Price**
   - `C:` Production pricing is contact sales; no public commercial tariff was found.
4. **Coverage**
   - `C:` 1,000+ competitions and more than 20 top leagues are advertised, for men's
     and women's soccer; per-match coverage tiers describe available detail. ([SR-BASICS],
     [SR-TIERS])
   - `U:` Youth and exact historical/event coverage by purchased competition.
5. **Files/endpoints/formats/delivery**
   - `C:` JSON/XML REST endpoints and optional real-time push-event and push-statistics
     feeds are documented. ([SR-EXT])
   - `U:` Bulk historical file delivery, full-backfill mechanism, and customer snapshot
     export are not public.
6. **Fields**
   - `C:` JSON/XML REST; push events/statistics. Extended timelines include passes,
     tackles, dribbles, interceptions, event IDs, UTC time, match clock, x/y,
     participant IDs and outcomes; lineups/formations/substitutions depend on coverage.
     ([SR-EXT], [SR-TIMELINE])
   - `C:` No continuous tracking or 360 freeze-frame is documented for this product.
7. **Time/correction/version/snapshot**
   - `C:` created, updated and removed sport-event feeds, UTC `updated_at`, a 24-hour
     updated-event window, and retained removed IDs for two weeks are documented.
     ([SR-CHANGES])
   - `C:` IDs are normally stable, with documented exceptions for postponed/duplicate
     events. Standard season endpoints usually cover current plus two prior seasons,
     while older/full match detail has archive constraints. ([SR-ID], [SR-HISTORY])
   - `U:` Event-level before/after revision history, first-availability time, immutable
     snapshots, and long-term extended-event backfill entitlement.
8. **Limits/auth/dependencies**
   - `C:` API key authentication; the public trial is 30 days, 1,000 calls per rolling
     30 days, and 1 request/second. Production limits are account-specific, so trial
     limits are not production commitments. ([SR-ACCOUNT])
9. **Rights**
   - `U:` No publicly accessible product agreement was located that expressly answers
     the project's twelve rights questions. Developer documentation is not a rights
     grant.
10. **Risks**
   - `I:` Strong correction discovery is offset by limited update windows and
     potentially shallow standard historical access.
   - `I:` Coverage tiers can vary match by match, creating missing-not-at-random
     features and league/player bias.
   - `I:` Postponed/duplicate ID exceptions require explicit lineage aliases.
11. **Evidence**
   - [SR-BASICS], [SR-EXT], [SR-TIMELINE], [SR-TIERS], [SR-CHANGES], [SR-ID],
     [SR-HISTORY], [SR-ACCOUNT].
12. **Provider questions**
   - All rights-schedule questions; exact price/coverage; full-history backfill and
     retention; version/snapshot SLA; tier changes; update-window recovery; deletion
     payloads; ID supersession; women/youth parity.

`I:` **Decision:** Reject from the top three because rights are wholly unresolved and
standard historic continuity is weaker, despite excellent public correction mechanics.

### 5. Sportmonks Football API v3

1. **Provider/product/version**
   - `C:` Provider: Sportmonks; product: Football API v3. ([SM-PRICE], [SM-EVENTS])
2. **Access model**
   - `C:` Commercial REST API with a 14-day trial. No account or trial was created.
     ([SM-PRICE])
3. **Price**
   - `C:` Public monthly tiers are Starter €29, Growth €99, Pro €249, and Enterprise
     custom; annual billing and add-ons change effective prices. ([SM-PRICE])
4. **Coverage**
   - `C:` Up to 2,300+ leagues are advertised. Historical data beyond three seasons and
     xG are add-ons on some plans. ([SM-PRICE])
   - `U:` Exact women/youth coverage and per-league lineup/event/coordinate depth.
5. **Files/endpoints/formats/delivery**
   - `C:` Token-authenticated JSON REST with nested `include` relationships.
     ([SM-INCLUDES])
   - `U:` Bulk files, initial full-backfill export, offline replay, and immutable
     provider snapshots.
6. **Fields**
   - `C:` JSON REST with nested `include` relationships. Events are described as
     significant moments—goals, cards, substitutions and similar—not a comprehensive
     pass/duel/carry stream. Lineups include players and statistics such as minutes;
     ball-coordinate and possession/trend data are separate includes. ([SM-EVENTS],
     [SM-INCLUDES], [SM-LINEUPS])
   - `I:` This cannot support the requested general event-action feature space without
     undocumented data.
7. **Time/correction/version/snapshot**
   - `U:` No record-level first-availability, correction version, deletion stream,
     immutable snapshot, or reproducible historical-response mechanism was found.
8. **Limits/auth/dependencies**
   - `C:` Token-authenticated API with entity/hour limits. The pricing page says
     Starter/Growth/Pro are 2,000/2,500/3,000 calls per entity per hour; the rate-limit
     documentation labels Growth and Pro differently. ([SM-PRICE], [SM-RATE])
9. **Rights**
   - `C:` Published terms say customers may store, transfer and distribute data and may
     in principle earn from something created with it, but may not resell the product
     without written consent. ([SM-TERMS])
   - `U:` Normalisation, persistent internal UI, derived datasets, ML/evaluation,
     generated explanations, recipient-bounded exports, attribution, and survival after
     termination are not expressly resolved.
10. **Risks**
   - `I:` Significant-event granularity is disqualifying for rich player similarity.
     Marketing breadth does not prove consistent action depth.
   - `I:` The public rate-limit inconsistency and absent correction/snapshot contract
     increase operational risk.
11. **Evidence**
   - [SM-PRICE], [SM-RATE], [SM-EVENTS], [SM-INCLUDES], [SM-LINEUPS], [SM-TERMS].
12. **Provider questions**
   - Complete rights schedule; event types and coordinates by league; women/youth
     matrix; correction/version protocol; rate-limit discrepancy; source-rights chain;
     termination retention and exports.

`I:` **Decision:** Reject for W04 because it does not publicly offer the required full
event stream and its otherwise permissive-sounding terms omit the key model,
transformation, display, and export rights.

### 6. API-Sports API-Football v3.9.3

1. **Provider/product/version**
   - `C:` Provider: API-Sports; product: API-Football v3.9.3. ([AF-DOC])
2. **Access model**
   - `C:` Free and commercial REST API subscriptions. No account was created.
3. **Price**
   - `C:` Public limits/prices are free 100 requests/day, Pro $19 for 7,500/day, Ultra
     $29 for 75,000/day, and Mega $39 for 150,000/day. ([AF-PRICE])
4. **Coverage**
   - `C:` 1,235 leagues and cups are advertised with a public coverage matrix containing
     women's and youth competitions. ([AF-PRODUCT], [AF-COVERAGE])
5. **Files/endpoints/formats/delivery**
   - `C:` API-key-authenticated JSON REST endpoints. ([AF-DOC])
   - `U:` Bulk file/backfill delivery, replay, and immutable snapshot mechanisms.
6. **Fields**
   - `C:` Fixtures, teams, players, lineups, statistics, and events are exposed over
     JSON REST; the event description is goals, cards, and substitutions. No full
     pass/duel/carry event stream, possession chain, freeze-frame, or event x/y is
     advertised. ([AF-PRODUCT])
7. **Time/correction/version/snapshot**
   - `U:` Record availability, publication delay, corrections, version history,
     tombstones, stable snapshot, and historical reproducibility.
8. **Limits/auth/dependencies**
   - `C:` API key subscription and daily request caps are tier-dependent.
     ([AF-PRICE])
9. **Rights**
   - `C:` Terms prohibit resale and expressly say API-Football does not provide a
     licence for use/publication; customers must obtain permissions from competent
     authorities, and commercial competition rights belong to rights holders.
     ([AF-TERMS])
10. **Risks**
   - `I:` The rights-chain disclaimer alone prevents governance approval; sparse event
     detail separately fails the technical requirement.
11. **Evidence**
   - [AF-DOC], [AF-PRODUCT], [AF-COVERAGE], [AF-PRICE], [AF-TERMS].
12. **Provider/data-owner questions**
   - Which rights owners and permissions cover every competition/use; all project
     rights; full action stream existence; identity/correction/snapshot guarantees.

`C:` **Decision:** Reject unless the project independently obtains and documents all
underlying rights. `I:` Even then, advertised event granularity is insufficient.

### 7. Hudl StatsBomb Open Data

1. **Provider/product/version**
   - `C:` Provider/licensor: Hudl/StatsBomb; dataset: StatsBomb Open Data. Public schemas
     are Competitions v2, Matches v3, Events v4, Lineups v2, and 360 v1. ([SB-OPEN],
     [SB-DOCS])
2. **Access model**
   - `C:` Free public dataset for research/analysis and genuine interest under the
     StatsBomb Public Data User Agreement, last updated 2023-09-08. It is not a CC or
     OSI-style open licence. ([SB-PUBLIC-LIC])
3. **Price**
   - `C:` No charge for the selected public files; no continuity or support entitlement.
     ([SB-OPEN], [SB-PUBLIC-LIC])
4. **Coverage**
   - `C:` Selected men's, women's and historic competitions/seasons are in a mutable
     catalogue; selected matches have 360. StatsBomb gives no continuity or completeness
     promise. ([SB-FREE], [SB-COMP])
5. **Files/endpoints/formats/delivery**
   - `C:` GitHub JSON files organised as competitions, matches, events, lineups and
     selected 360. No production API is promised. ([SB-OPEN])
6. **Fields**
   - `C:` JSON hierarchy for competitions, matches, events, lineups, and selected 360.
     Fields include stable provider match IDs/event UUIDs, match clock, x/y, possession,
     teams/players, outcomes, lineups, substitutions, and contextual frames.
     ([SB-OPEN], [SB-EVENTS], [SB-LINEUPS], [SB-360-SCHEMA])
7. **Time/correction/version/snapshot**
   - `C:` Catalogue fields include match update and availability dates for events and
     360; schema documents version changes. Repository commits can identify the fetched
     tree. ([SB-COMP], [SB-DOCS])
   - `I:` A Git commit can make a customer-created snapshot reproducible, but does not
     establish a contractual right to preserve it or supply a provider correction
     ledger.
8. **Limits/auth/dependencies**
   - `C:` Public GitHub files; no API authentication or rate-limit commitment. Service
     may be changed or withdrawn. ([SB-OPEN], [SB-PUBLIC-LIC])
9. **Rights**
   - `C:` Agreement purpose is research/analysis and sharing genuine-interest ideas. It
     prohibits editing/distortion, distribution/reproduction/sale, external provision,
     commercial exploitation of the data, and commercial exploitation of any derived
     analysis. Publication requires StatsBomb credit/branding. ([SB-PUBLIC-LIC])
   - `U:` Long-term raw archival, normalisation for an internal database, noncommercial
     model training, persistent UI display, and generated explanations are not
     explicitly granted.
10. **Risks**
   - `I:` High technical value but unacceptable operational rights, mutable coverage,
     no SLA, no guaranteed identity/correction continuity, and no commercial use.
11. **Evidence**
   - [SB-OPEN], [SB-FREE], [SB-PUBLIC-LIC], [SB-DOCS], [SB-COMP], [SB-EVENTS],
     [SB-MATCHES], [SB-LINEUPS], [SB-360-SCHEMA].
12. **Provider questions**
   - Would Hudl grant a separate written licence for local immutable retention,
     transformation, ML/evaluation, internal scouting/UI/explanations and bounded
     derived export? Which exact snapshots and attribution would it cover?

`C:` **Decision:** Reject as the governed operational source under the published
agreement.

### 8. Wyscout Soccer match event dataset, figshare version 5

1. **Provider/product/version**
   - `C:` Dataset authors/Pappalardo et al.; “A public data set of spatio-temporal match
     events in soccer competitions,” figshare collection version 5, DOI
     `10.6084/m9.figshare.c.4415000.v5`. Source events were supplied by Wyscout.
     ([WY-PAPER], [WY-FIGSHARE])
2. **Access model**
   - `C:` Open research dataset licensed CC BY 4.0. ([WY-PAPER], [CC-BY])
3. **Price**
   - `C:` Free file download; no API, support or continuity entitlement. No data was
     downloaded for this research.
4. **Coverage**
   - `C:` 1,941 matches, 4,299 players, and 3,251,294 events from the 2017/18 English,
     Spanish, Italian, German and French top flights, Euro 2016, and World Cup 2018.
     No women's or youth competitions. ([WY-PAPER])
5. **Files/endpoints/formats/delivery**
   - `C:` Versioned figshare JSON archives for competitions, matches, teams, players,
     events, referees and coaches; no production endpoint. ([WY-PAPER], [WY-FIGSHARE])
6. **Fields**
   - `C:` JSON files for competitions, matches, teams, players, events, referees and
     coaches. Match team data contains lineups, bench and substitutions. Events contain
     provider event/subevent IDs/names, tags/outcomes, match/player/team IDs, half,
     elapsed seconds, and attack-oriented origin/destination percentage coordinates.
     ([WY-PAPER])
   - `C:` No native possession ID or tracking/freeze-frame. The paper constructs
     possession sequences analytically. Minutes require lineup/substitution
     reconstruction rather than a stated authoritative minutes field.
7. **Time/correction/version/snapshot**
   - `C:` The versioned DOI identifies a frozen v5 collection.
   - `U:` No first-publication timestamps, per-record revisions, correction log, or
     continuing update channel.
8. **Limits/auth/dependencies**
   - `C:` Downloadable figshare archive with no production API/authentication
     dependency or provider rate-limit/SLA.
9. **Rights**
   - `C:` CC BY permits copy, redistribution, remixing, transformation and building upon
     for any purpose, including commercially, with credit, licence link and indication
     of changes. It covers only copyright and similar rights the licensor can license;
     personality, privacy, moral, trademark and other rights may remain. ([CC-BY])
   - `I:` Model training/evaluation and internal generated explanations fall within the
     broad adaptation/use permission, but ML is not named; preserve attribution and
     obtain legal confirmation for output handling.
10. **Risks**
   - `I:` Frozen, old, male-senior coverage cannot support current availability,
     continuity, transfer, women, or youth use.
   - `I:` Publication-time player master fields such as current team can leak future
     state into historical models. Only match-bound roster/team facts should be eligible
     as of the match.
   - `I:` Provider IDs are stable within the snapshot but have no public ongoing
     merge/split or cross-provider resolution service.
11. **Evidence**
   - [WY-PAPER], [WY-FIGSHARE], [CC-BY].
12. **Data-owner/legal questions**
   - Confirm database-right chain and whether any Wyscout source terms survive the CC
     grant; preferred attribution text; acceptable model-output attribution; known
     identity corrections in v5.

`I:` **Decision:** Accept only as a separately governed frozen benchmark/engineering
fixture after legal confirmation, never as W04's operational source.

### 9. DFL Integrated Data Set for Soccer Analytics (IDSSE)

1. **Provider/product/version**
   - `C:` Bassek et al./DFL-authorised dataset from the 2025 Scientific Data
     publication “An integrated dataset of spatiotemporal and event data in elite
     soccer.” ([IDSSE])
2. **Access model**
   - `C:` Open research dataset under CC BY 4.0 with stated DFL authorisation.
     ([IDSSE])
3. **Price**
   - `C:` Free file dataset; no production service, support or continuity entitlement.
4. **Coverage**
   - `C:` Seven 2022/23 men's matches—two Bundesliga and five Bundesliga 2—covering 207
     players and ten teams. No women/youth or ongoing seasons. ([IDSSE])
5. **Files/endpoints/formats/delivery**
   - `C:` Per-match XML information, event and position files; no API endpoint.
     ([IDSSE])
6. **Fields**
   - `C:` Per-match XML information, event and position files; 11,137 events and
     1,002,644 tracking frames. Data includes teams/players/lineups/formations, event
     types and times, player/event locations and context, tracking x/y, ball height,
     active state and possession state, plus synchronised time information. ([IDSSE])
   - `C:` This is continuous optical tracking/event data rather than an event-only
     freeze-frame product.
7. **Time/correction/version/snapshot**
   - `C:` Frozen research snapshot with described quality controls and synchronisation.
   - `U:` No continuing publication SLA, correction stream, identity updates, or revised
     snapshot policy.
8. **Limits/auth/dependencies**
   - `C:` File-based dataset, no production API/authentication dependency. No data was
     downloaded for this research.
9. **Rights**
   - `C:` CC BY matrix applies; attribution/change notice required on sharing.
   - `I:` Model use is consistent with adaptation but not expressly named.
10. **Risks**
   - `C:` The paper discusses tracking identity swaps and synchronisation/measurement
     quality controls; these remain relevant QA concerns. ([IDSSE])
   - `I:` Seven matches are too small for scouting coverage, transfer evaluation, or
     representative league modelling.
11. **Evidence**
   - [IDSSE], [CC-BY].
12. **Data-owner/legal questions**
   - Preferred attribution; database-right scope; whether future corrected releases are
     planned; exact observed/derived fields; permissible display of player identities.

`I:` **Decision:** Accept only as a separately governed event/tracking QA fixture after
legal review, never as the W04 operational source.

### 10. Metrica Sports Sample Data

1. **Provider/product/version**
   - `C:` Provider: Metrica Sports; dataset: Sample Data, three anonymised matches on a
     mutable GitHub `master` branch. ([METRICA])
2. **Access model**
   - `C:` Public sample repository; no formal licence file was identified.
3. **Price**
   - `C:` Free to access; no support, API, coverage or continuity entitlement.
4. **Coverage**
   - `C:` Three sample matches, no named competition/season/women/youth continuity.
5. **Files/endpoints/formats/delivery**
   - `C:` GitHub files in CSV and JSON, plus an EPTS/FIFA example; no production
     endpoint. ([METRICA])
6. **Fields**
   - `C:` Synchronous tracking and event examples in CSV and JSON, plus an EPTS/FIFA
     example; coordinates and pitch dimensions are documented. ([METRICA])
7. **Time/correction/version/snapshot**
   - `U:` No immutable release, publication/correction timestamps, revision history, or
     service continuity.
8. **Limits/auth/dependencies**
   - `C:` GitHub file delivery without authentication; no service SLA.
9. **Rights**
   - `C:` README asks users to be responsible and acknowledge the source when publishing
     work.
   - `U:` No formal licence grant was identified for retention, copying,
     transformation, ML, internal display, export, redistribution, or commercial use.
10. **Risks**
   - `I:` Legal ambiguity and trivial anonymised coverage are both disqualifying.
11. **Evidence**
   - [METRICA].
12. **Provider/data-owner questions**
   - Ask Metrica for a licence signed by the relevant rights owner and covering all
     required uses; clarify attribution and dataset version.

`U:` **Decision:** Rights are unproven. `I:` Reject for W04 even if clarified because
coverage is only three samples.

## Rejection register

| Candidate | Rejection reason |
|---|---|
| Sportradar Soccer Extended API v4 | `U:` No affirmative published use licence; `C:` standard history/update windows create recovery and reproducibility concerns; exact rights, price and scope require negotiation. |
| Sportmonks Football API v3 | `C:` Advertised events are significant incidents rather than the required full action stream; `U:` core transformation/model/UI/export terms; conflicting public rate-limit labels. |
| API-Football v3.9.3 | `C:` Provider expressly does not supply the underlying use/publication licence and the event feed is limited to goals/cards/substitutions. |
| StatsBomb Open Data | `C:` Commercial use and commercial derived analysis are forbidden; raw redistribution and editing are restricted; project-specific storage/model/UI rights are absent. |
| Wyscout figshare v5 | `C:` Proper CC BY rights and strong event schema, but frozen 2016–2018 male-senior coverage with no continuity, availability timestamps, corrections, women or youth. |
| DFL IDSSE | `C:` Proper CC BY event/tracking dataset, but only seven men's matches and no continuing provider service. |
| Metrica Sample Data | `U:` No formal licence grant; `C:` only three anonymised samples. |

StatsBomb commercial, Wyscout commercial, and Opta are not “accepted”; they remain
conditional finalists. Failure to obtain a complete written answer is a rejection, not
permission to interpret silence.

## Decision-ready W04.1 provider/right/coverage packet

This is the packet to complete from signed evidence. Until every `TBD` is replaced by a
contract or provider document, W04.1 remains blocked.

| W04.1 field | Conditional primary entry |
|---|---|
| Legal provider | **TBD from contracting entity** — expected Hudl/StatsBomb entity; exact legal name and jurisdiction required. |
| Product | StatsBomb Data plus StatsBomb 360; exact commercial package, schema/taxonomy version and support tier **TBD**. |
| Licence class | Commercial, product-specific Order Form overriding identified Hudl MSA restrictions; executed agreement **TBD**. |
| Coverage | Target competition-country-season-gender-age matrix, event/360 tiers, historical start, current update continuity and exclusions **TBD**. |
| Source objects | Competitions, seasons, matches, teams, players, rosters/lineups, substitutions/formations/stints or inputs to derive them, event actions, coordinates, possession context, outcomes, IDs, match time, availability/correction/version metadata; exact schema **TBD**. |
| Delivery | Bounded local API and/or file acquisition only; authentication, page/bulk rules, backfill route, rate/SLA, and recovery **TBD**. |
| Snapshot | Right to retain byte-identical raw responses/files, request metadata, provider version/revision, acquisition UTC, checksum and manifest; provider immutable snapshot or customer snapshot right **TBD**. |
| Temporal contract | Provider definitions and timezones for occurrence, first availability, provisional/final, correction, deletion, replacement, lineup announcement and backfill; historical availability evidence **TBD**. |
| Identity contract | Stable IDs, merge/split/retirement/alias/reuse policy for player, team, competition, season, match and event; correction feed **TBD**. |
| Local retention | Bronze, Silver, Gold, model/evaluation artifacts, audit records and minimal source excerpts during term and defined survival after termination **TBD**. |
| Permitted derivation/model use | Normalisation, possessions/stints/minutes, features, embeddings, versioned local vector artifacts, in-process retrieval/ranking training and evaluation, model artifacts, explanations and audits **TBD**. |
| Display/export | Authorised-user local UI fields; bounded internal raw/derived exports, recipients, purpose, row/field limits, marks/attribution, audit, expiry and revocation **TBD**. |
| Forbidden uses | Public service, public endpoint, external redistribution, raw-data resale, unrelated model training, third-party access and cloud upload, plus contract-specific limits. |
| Attribution | Exact internal UI, report, explanation and export wording/logo requirements **TBD**. |
| Pricing/term | Currency, tax, setup/backfill, packages, competition additions, API overage, support, renewal/indexation, direct-use costs and termination **TBD**. |
| Evidence identifiers | Executed agreement/Order Form version/date, schedule/exhibit names, coverage export date/hash, schema/data-dictionary version/hash, correction/SLA document version/hash **TBD**. |
| Decision owner | User/data owner plus qualified legal/commercial reviewer; approval record **TBD**. |
| Acquisition authority | **NOT GRANTED.** No credentials, payload, adapter, migration, or Bronze/Silver/Gold work until the completed packet is approved. |

If StatsBomb fails, replace the product with Wyscout Data v3 Database + Events and fill
the same fields. Do not silently carry a favourable StatsBomb answer over to Wyscout,
even though both use the Hudl MSA.

## Mandatory written terms

The selected contract must affirmatively state all of the following; a marketing page,
technical capability, internal-use label, or lack of prohibition is insufficient.

1. Local embedded-SQLite/filesystem retention of complete raw API responses/files,
   including repeated and corrected versions.
2. Immutable Bronze preservation with provider IDs, request/response metadata,
   acquisition UTC, hashes, schema version and correction lineage.
3. Normalisation, cleaning, joining, identity crosswalks, Silver tables and derived Gold
   datasets.
4. Derived statistics, features, possession/stint/minutes reconstruction, embeddings and
   vector indices.
5. Training, fitting, validating, testing and evaluating statistical, machine-learning,
   ranking, retrieval and explanation models, including retention/reload of artifacts.
6. Internal scouting and recruitment decision support by named/authorised user classes.
7. Local internal UI display of defined raw fields, derived metrics, charts, maps,
   comparisons, evidence excerpts, source/version metadata and explanations.
8. Generated deterministic or model-assisted explanations derived from the licensed
   data, with required attribution and prohibited claims specified.
9. Audit, reproducibility, incident investigation, backup/restore and legal-compliance
   copies, including what survives subscription termination and for how long.
10. Bounded internal exports: raw versus derived, allowed fields/rows, named recipient
    types, purpose, watermark/attribution, encryption, expiry, audit and deletion.
11. Whether any result may leave the organisation; public publication and redistribution
    remain forbidden unless separately approved.
12. Commercial/internal-business status, territory, affiliates/contractors, device/user
    limits, and any league/federation/direct-use licence.

## Temporal, identity, and snapshot acceptance questions

These are data-product requirements, not optional implementation details:

- What timestamp proves when each event, lineup, correction and player/team fact first
  became available to the customer?
- Is the timestamp provider-generated or merely request time? What timezone and clock
  precision apply?
- Which states mean provisional, confirmed, final, corrected, deleted or superseded?
- Are correction notifications complete? What is their maximum lookback and recovery
  path after downtime?
- Can the customer retrieve prior revisions, or must it preserve every response? Is that
  preservation contractually allowed?
- Can an event ID be reused, removed or reassigned? Can a match ID change after
  postponement/duplication? What supersession link is supplied?
- How are player duplicates, spelling changes, nationality changes, transfers, academy
  promotion, team rebrands and merged identities represented?
- Are lineups and minutes authoritative? How are stoppage time, extra time, abandoned
  matches, bench-only players, sin bins, concussion substitutions and missing players
  handled?
- Is possession provider-defined, reconstructable, versioned and stable across taxonomy
  releases?
- Does a coverage flag distinguish “zero,” “not observed,” “not applicable,”
  “provisional,” and “not licensed”?
- What makes a full competition-season snapshot complete? Is a match count/coverage
  manifest supplied and signed or hashable?
- How much notice is given before schema, taxonomy, coordinate, ID or coverage changes?
  How long are old versions supported?

## Legal and commercial questions still unresolved

1. Which legal entity licenses each finalist, under which governing law, and which
   product-specific document overrides the public master terms?
2. Will the contract enumerate local raw retention, normalisation, derived data, model
   training/evaluation, internal display, explanations, audit copies and raw/derived
   export separately?
3. Who owns customer-created Silver/Gold datasets, features, embeddings, models,
   evaluation results, explanations and identity crosswalks?
4. May those artifacts be retained and used after termination if raw provider fields are
   removed? What must be destroyed, and how is audit reproducibility preserved?
5. Are backups and immutable audit snapshots permitted, and what deletion timetable
   applies to them?
6. Are internal exports permitted to employees, contractors, scouts, recruitment
   committees, board members and professional advisers? May a player/agent receive a
   derived report?
7. Which raw and derived fields may appear in the local UI, screenshots, printed pages,
   PDFs, CSVs and explanations?
8. What attribution, copyright, logo, source, version and disclaimer text is required in
   the UI and each export class?
9. Does “internal business purpose” include every proposed recruitment, benchmarking,
   model-development and evaluation workflow, or only use inside the vendor platform?
10. Do any leagues/federations—especially Football DataCo competitions—require direct-use
    licences, and who obtains/pays for them?
11. Is use by affiliates, consultants or outsourced scouts third-party use?
12. Are player names, biographical data, images, video links or inferred attributes
    subject to additional privacy, publicity, labour, safeguarding or youth-data terms?
13. Are women's and youth competitions licensed on the same basis and at the same field
    depth as men's senior competitions?
14. What happens if a rights owner withdraws a competition? May existing snapshots,
    derived features and models remain?
15. Are vendor-generated or customer-generated IDs and mappings portable at termination?
16. Does a quoted price include historical backfill, corrections, 360/tracking,
    production API calls, support, schema changes, overages, direct-use licences, taxes
    and renewal increases?
17. Will the provider warrant authority to grant the specified uses and indemnify
    relevant IP/database-right claims?
18. What security, audit, breach, permitted-user, local-secret and machine-access terms
    apply to a local-only system?

## Source register

All links were accessed on **2026-07-29**. Dates in titles are source publication or
document dates, not access dates.

### Hudl StatsBomb

- [SB-DATA]: [StatsBomb soccer data product](https://statsbomb.com/what-we-do/soccer-data/)
- [SB-360]: [StatsBomb 360 product](https://statsbomb.com/what-we-do/soccer-data/360-2/)
- [SB-LIVE]: [StatsBomb live-data API guide](https://live-data-api-guide.statsbomb.com/)
- [SB-FREE]: [StatsBomb free-data hub](https://statsbomb.com/what-we-do/hub/free-data/)
- [SB-WOMEN]: [StatsBomb women's-team analytics support and coverage, 2023/24](https://statsbomb.com/news/statsbomb-offers-free-analytics-support-to-womens-teams-in-2023-24/)
- [SB-OPEN]: [Hudl StatsBomb Open Data repository and README](https://github.com/hudl/open-data)
- [SB-PUBLIC-LIC]: [StatsBomb Public Data User Agreement, last updated 2023-09-08](https://github.com/hudl/open-data/blob/master/LICENSE.pdf)
- [SB-DOCS]: [StatsBomb Open Data schema-document directory](https://github.com/hudl/open-data/tree/master/doc)
- [SB-COMP]: [StatsBomb Open Data Competitions v2 schema](https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Competitions%20v2.0.0.pdf)
- [SB-MATCHES]: [StatsBomb Open Data Matches v3 schema](https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Matches%20v3.0.0.pdf)
- [SB-EVENTS]: [StatsBomb Open Data Events v4 schema](https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Events%20v4.0.0.pdf)
- [SB-LINEUPS]: [StatsBomb Open Data Lineups v2 schema](https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Lineups%20v2.0.0.pdf)
- [SB-360-SCHEMA]: [StatsBomb Open Data 360 Frames v1 schema](https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20360%20Frames%20v1.0.0%20%281%29.pdf)

### Hudl Wyscout and Hudl terms

- [WY-DATA]: [Wyscout Data API product](https://www.hudl.com/products/wyscout/data-api)
- [WY-API-PRODUCT]: [Wyscout Football API product and coverage claims](https://www.hudl.com/products/wyscout/football-api)
- [WY-PRICE]: [Wyscout pricing](https://www.hudl.com/products/wyscout/pricing)
- [WY-DOC]: [Wyscout API v3 documentation](https://apidocs.wyscout.com/)
- [WY-OPENAPI]: [Wyscout current OpenAPI specification](https://apidocs.wyscout.com/assets/specs/prod/current.yml)
- [HUDL-MSA]: [Hudl Master Subscription Agreement, 2026-02-09](https://static.hudl.com/craft/legal/Hudl-Master-Subscription-Agreeement_2026-02-09.pdf)

### Stats Perform Opta

- [OP-FEEDS]: [Opta Data Feeds](https://www.statsperform.com/products/opta-data-feeds/)
- [OP-GRANULAR]: [Opta Granular Data, including F24 x/y](https://www.statsperform.com/products/granular-data/)
- [OP-DEFS]: [Official Opta event definitions](https://optaplayerstats.statsperform.com/en_GB/opta-event-definitions)
- [OP-VISION]: [Opta Vision tracking](https://www.statsperform.com/products/opta-vision/)
- [OP-WOMEN]: [Stats Perform women's sports](https://www.statsperform.com/womens-sports/)
- [OP-PRICE]: [Stats Perform pricing and licensing FAQ](https://www.statsperform.com/faqs/stats-perform-faqs-pricing-licensing/)
- [OP-MLA]: [Stats Perform Master License Agreement, December 2025](https://www.statsperform.com/legal/mla-december-2025/)

### Sportradar

- [SR-BASICS]: [Sportradar Soccer API basics](https://developer.sportradar.com/soccer/docs/soccer-ig-api-basics)
- [SR-EXT]: [Sportradar Soccer Extended API overview](https://developer.sportradar.com/soccer/reference/soccer-extended-overview)
- [SR-TIMELINE]: [Soccer Extended sport-event timeline endpoint](https://developer.sportradar.com/soccer/reference/soccer-extended-sport-event-extended-timeline)
- [SR-TIERS]: [Sportradar soccer data-coverage tiers](https://developer.sportradar.com/soccer/docs/soccer-ig-data-coverage-tiers)
- [SR-CHANGES]: [Sportradar monitoring data changes](https://developer.sportradar.com/soccer/docs/monitoring-data-changes)
- [SR-ID]: [Sportradar soccer ID handling](https://developer.sportradar.com/soccer/docs/soccer-ig-id-handling)
- [SR-HISTORY]: [Sportradar soccer historical data](https://developer.sportradar.com/soccer/docs/soccer-ig-historical-data)
- [SR-ACCOUNT]: [Sportradar account, trial and rate-limit documentation](https://developer.sportradar.com/football/docs/football-ig-account-maintenance)

### Sportmonks

- [SM-PRICE]: [Sportmonks Football API plans and pricing](https://www.sportmonks.com/football-api/plans-pricing/)
- [SM-RATE]: [Sportmonks v3 rate limits](https://docs.sportmonks.com/v3/api/rate-limit)
- [SM-EVENTS]: [Sportmonks v3 event include](https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes/events)
- [SM-INCLUDES]: [Sportmonks v3 include catalogue](https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes)
- [SM-LINEUPS]: [Sportmonks v3 lineup include](https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes/lineups)
- [SM-TERMS]: [Sportmonks terms of service](https://www.sportmonks.com/terms-of-service/)

### API-Football

- [AF-PRODUCT]: [API-Football product and endpoint summary](https://api-sports.io/sports/football)
- [AF-DOC]: [API-Football v3.9.3 documentation](https://www.api-football.com/documentation)
- [AF-COVERAGE]: [API-Football coverage matrix](https://www.api-football.com/coverage)
- [AF-PRICE]: [API-Football pricing](https://www.api-football.com/pricing)
- [AF-TERMS]: [API-Football terms](https://www.api-football.com/terms)

### Properly licensed research/open datasets

- [WY-PAPER]: [Pappalardo et al., “A public data set of spatio-temporal match events in soccer competitions,” Scientific Data 2019](https://www.nature.com/articles/s41597-019-0247-7)
- [WY-FIGSHARE]: [Wyscout soccer match-event dataset, figshare collection version 5](https://doi.org/10.6084/m9.figshare.c.4415000.v5)
- [IDSSE]: [Bassek et al., “An integrated dataset of spatiotemporal and event data in elite soccer,” Scientific Data 2025](https://www.nature.com/articles/s41597-025-04505-y)
- [CC-BY]: [Creative Commons Attribution 4.0 International legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en)
- [METRICA]: [Metrica Sports Sample Data repository](https://github.com/metrica-sports/sample-data)

## Research boundary and next gate

- `C:` No credentials, account, click-through acceptance, quote request, purchase, data
  download, provider payload, adapter, schema migration, or real-data implementation was
  created.
- `C:` This packet does not change the existing blocked W04 phase-gate status.
- `I:` The smallest safe next step is non-binding vendor/legal clarification using this
  packet's common questions. Implementation remains out of scope until the user/data
  owner approves an executed provider/right/coverage packet.

[SB-DATA]: https://statsbomb.com/what-we-do/soccer-data/
[SB-360]: https://statsbomb.com/what-we-do/soccer-data/360-2/
[SB-LIVE]: https://live-data-api-guide.statsbomb.com/
[SB-FREE]: https://statsbomb.com/what-we-do/hub/free-data/
[SB-WOMEN]: https://statsbomb.com/news/statsbomb-offers-free-analytics-support-to-womens-teams-in-2023-24/
[SB-OPEN]: https://github.com/hudl/open-data
[SB-PUBLIC-LIC]: https://github.com/hudl/open-data/blob/master/LICENSE.pdf
[SB-DOCS]: https://github.com/hudl/open-data/tree/master/doc
[SB-COMP]: https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Competitions%20v2.0.0.pdf
[SB-MATCHES]: https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Matches%20v3.0.0.pdf
[SB-EVENTS]: https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Events%20v4.0.0.pdf
[SB-LINEUPS]: https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20Lineups%20v2.0.0.pdf
[SB-360-SCHEMA]: https://github.com/hudl/open-data/blob/master/doc/Open%20Data%20360%20Frames%20v1.0.0%20%281%29.pdf
[WY-DATA]: https://www.hudl.com/products/wyscout/data-api
[WY-API-PRODUCT]: https://www.hudl.com/products/wyscout/football-api
[WY-PRICE]: https://www.hudl.com/products/wyscout/pricing
[WY-DOC]: https://apidocs.wyscout.com/
[WY-OPENAPI]: https://apidocs.wyscout.com/assets/specs/prod/current.yml
[HUDL-MSA]: https://static.hudl.com/craft/legal/Hudl-Master-Subscription-Agreeement_2026-02-09.pdf
[OP-FEEDS]: https://www.statsperform.com/products/opta-data-feeds/
[OP-GRANULAR]: https://www.statsperform.com/products/granular-data/
[OP-DEFS]: https://optaplayerstats.statsperform.com/en_GB/opta-event-definitions
[OP-VISION]: https://www.statsperform.com/products/opta-vision/
[OP-WOMEN]: https://www.statsperform.com/womens-sports/
[OP-PRICE]: https://www.statsperform.com/faqs/stats-perform-faqs-pricing-licensing/
[OP-MLA]: https://www.statsperform.com/legal/mla-december-2025/
[SR-BASICS]: https://developer.sportradar.com/soccer/docs/soccer-ig-api-basics
[SR-EXT]: https://developer.sportradar.com/soccer/reference/soccer-extended-overview
[SR-TIMELINE]: https://developer.sportradar.com/soccer/reference/soccer-extended-sport-event-extended-timeline
[SR-TIERS]: https://developer.sportradar.com/soccer/docs/soccer-ig-data-coverage-tiers
[SR-CHANGES]: https://developer.sportradar.com/soccer/docs/monitoring-data-changes
[SR-ID]: https://developer.sportradar.com/soccer/docs/soccer-ig-id-handling
[SR-HISTORY]: https://developer.sportradar.com/soccer/docs/soccer-ig-historical-data
[SR-ACCOUNT]: https://developer.sportradar.com/football/docs/football-ig-account-maintenance
[SM-PRICE]: https://www.sportmonks.com/football-api/plans-pricing/
[SM-RATE]: https://docs.sportmonks.com/v3/api/rate-limit
[SM-EVENTS]: https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes/events
[SM-INCLUDES]: https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes
[SM-LINEUPS]: https://docs.sportmonks.com/v3/tutorials-and-guides/tutorials/includes/lineups
[SM-TERMS]: https://www.sportmonks.com/terms-of-service/
[AF-PRODUCT]: https://api-sports.io/sports/football
[AF-DOC]: https://www.api-football.com/documentation
[AF-COVERAGE]: https://www.api-football.com/coverage
[AF-PRICE]: https://www.api-football.com/pricing
[AF-TERMS]: https://www.api-football.com/terms
[WY-PAPER]: https://www.nature.com/articles/s41597-019-0247-7
[WY-FIGSHARE]: https://doi.org/10.6084/m9.figshare.c.4415000.v5
[IDSSE]: https://www.nature.com/articles/s41597-025-04505-y
[CC-BY]: https://creativecommons.org/licenses/by/4.0/legalcode.en
[METRICA]: https://github.com/metrica-sports/sample-data
