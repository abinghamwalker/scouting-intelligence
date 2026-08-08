# Historical player comparison participant-language and UX specification

- Packet: `W10-PARTICIPANT-LANGUAGE-UX-01`
- Status: bounded implementation specification; master acceptance and implementation verification remain required
- Audience: eligible football professionals who have no knowledge of this repository, its phases, its data contracts, or its retrieval implementation
- Participant entry point: `http://127.0.0.1:8771/historical-player-comparison`
- Scope: participant-visible content hierarchy, plain-language mappings, forbidden-language inventory, and UX acceptance criteria
- Non-scope: scorer, feature, matrix, ranking, protected-label, threshold, scheduling, storage, or authority semantics

## Evidence classification and reason for this rework

The first v2 attempt was stopped after the product owner found that the participant surface read
like an internal engineering console. Terms such as “Neutral recorded start locations,”
“independent families,” “observed value,” and “predicate” were not meaningful without operator
translation; the duplicated evidence sections were difficult to navigate; and internal phase
references were irrelevant to an external participant.

These findings are **product-owner/operator usability evidence only**. They are not
eligible-reviewer evidence. Nothing reviewed for this specification proves or implies that the
product owner met the football-domain eligibility requirements, and these findings must not enter
football-relevance ratings, formal evidence, or the protected result.

The rework is a genuine comprehension correction. It must preserve the scientific reason for the
additional evidence: the participant's judgement must not merely restate the statistics that were
used to select the comparison. The participant interface therefore distinguishes the selection
statistics from additional football evidence in plain language, while governed contracts retain
their exact purpose and family identities internally.

## Participant-language principles

1. Write to a football professional, not a repository contributor. A participant must not need
   to know any internal phase, gate, pack, contract, authority, version, or algorithm name.
2. Lead with the football question. Explain research and data limitations only where they help the
   participant answer it.
3. Call the two people **Player A** and **Player B** everywhere. Do not use “exemplar,”
   “candidate,” “retrieved,” “control,” or any label that suggests which answer is preferred.
4. Use one shared row structure for both players. Labels, definitions, units, chart scales,
   ordering, and missingness treatment must be identical on both sides.
5. Use “Recorded value” for a rate or count and “Compared with players in the same position” for
   the reference view. Do not expose “raw value,” “within-position percentile” as a bare label,
   or an availability enum.
6. State limitations once at the closest useful level. Do not duplicate the same minutes,
   direction, source, or claim warning in both player columns.
7. Use progressive disclosure for definitions and limitations, but not a stack of duplicated
   technical accordions. Core evidence is visible; supporting definitions can expand alongside a
   single shared comparison row.
8. A chart describes recorded actions, never quality, effectiveness, causality, tactical intent,
   recruitment value, or future performance unless the retained evidence actually establishes
   that construct. It currently does not.
9. Every validation message names the question to fix and the next action. Never render a Python,
   Pydantic, SQLite, UUID, enum, contract, revision, token, digest, or authority error to a
   participant.
10. Internal governed values may be submitted in hidden controls and stored for exact replay, but
    they must not appear in visible text, accessible names, the friendly URL, downloadable
    participant content, or participant-facing error payloads.

## Approved content hierarchy and copy

### 1. Global shell and friendly URL

The address bar must settle on `/historical-player-comparison`. A legacy internal route may issue
an immediate redirect, but it must never be the URL given to a participant and must not remain in
the address bar. Participant form actions and participant-facing asset paths should use neutral
names so internal phase codes do not appear in returned HTML.

Use this shell:

- Browser title and page heading: **Historical Player Comparison**
- Eyebrow: **Research form trial**
- Lede: **Compare two players from a historical season using the football information shown.**
- Badge: **Stored on this computer**
- Skip link: **Skip to main content**
- Navigation: **About this form**, **Current comparison**, **Review and submit**
- Boundary heading: **Historical research, not recruitment advice**
- Boundary text: **This form asks about historical playing-style comparisons. It does not assess
  current ability, future performance, price, availability, squad fit, or whether a club should
  recruit a player.**
- Footer: **Your answers are stored locally under your participant code. The form does not show an
  expected answer.**

Do not put study status, phase status, authority status, pilot/formal lane status, ranking
provenance, or implementation commentary in the shell.

### 2. Introduction, purpose, storage, and withdrawal boundary

Use the following introduction before eligibility questions:

> This is a trial of a historical player-comparison research form. You will review five pairs of
> players and answer one question about each pair. We are testing whether the football information
> in the form is clear and sufficient for a professional judgement.
>
> Your answers are saved on this computer under a participant code rather than your name. They are
> not sent over the internet. You can stop before final submission. After you press “Submit final
> answers,” the stored response is locked and cannot be edited through this form.
>
> This research is about historical playing style. It is not recruitment advice and must not be
> used as a recommendation about a player.

If the number of comparisons is authority-driven, substitute the exact frozen count for “five”
without exposing a pack or version identifier.

### 3. Eligibility and conflict check

Heading: **Before you begin**

Introductory copy:

> This trial is for people with at least two years of relevant professional football experience
> who have assessed players professionally within the last five years.

Fields and choices:

- **Participant code**
  - Help: **Use the code provided to you, not your name. It must contain 6–32 capital letters,
    numbers, or hyphens.**
- **How many years of relevant professional football experience do you have?**
- **Which experience applies to you? Select all that apply.**
  - Professional scouting
  - Recruitment analysis
  - Performance analysis
  - Professional coaching
  - Professional playing
- **Have you assessed players professionally within the last five years?** — Yes / No
- **Do you have a current or recent conflict involving any player or club that may appear?** —
  No / Yes
  - Help: **Examples include working for the player or club, advising on a current decision about
    them, a close personal relationship, or a financial interest. If you are unsure, answer Yes.**
  - If Yes: **You cannot take part in this trial because the comparison must be independent. No
    football answers have been requested.**

Conflict status is an eligibility boundary, not a free-text research question. Do not request a
detailed conflict note from a participant who is immediately ineligible unless the governing
contract explicitly needs one; if a note remains required internally, ask only **Briefly describe
the conflict so the study team can confirm that you should not continue.**

Inline eligibility messages:

- Under two years: **This trial requires at least two years of relevant professional football
  experience.**
- No experience selected: **Select at least one type of professional football experience.**
- No recent assessment: **This trial requires professional player assessment within the last five
  years.**
- Conflict declared: **You cannot continue with a player or club conflict.**

### 4. Consent

Heading: **Your agreement**

Intro: **Please confirm each statement before starting.**

Required statements:

1. **I am taking part voluntarily.**
2. **I understand that my participant code and answers are stored only on this computer.**
3. **I understand that I can stop before final submission.**
4. **I understand that final submission locks my answers so they cannot be edited through this
   form.**
5. **I understand that this is historical playing-style research, not recruitment advice.**

Button: **Start comparisons**

Missing-consent error: **Confirm all five statements before starting.**

### 5. Progress, resume, and clear task

At the top of each task show a real progress element and the text **Comparison 2 of 5**. On resume,
show **Welcome back. Your saved answers are still here. Continue with comparison 2 of 5.** Do not
show a bare revision number, judgement count, phase label, or lane label.

Task heading and prompt:

> **How credible is Player B as a historical playing-style comparison to Player A, based on the
> information shown?**

Supporting copy:

> Compare the players using the historical season, position, playing statistics, and additional
> evidence below. Judge only what the information can support. The form does not show which answer
> is expected.

### 6. Side-by-side player comparison

Use a shared comparison table or aligned cards with **Player A** always on the left and **Player
B** always on the right at desktop sizes. On a narrow screen, repeat the statistic label before
each pair of values and keep Player A before Player B. Do not make one player visually dominant.

Context row order:

1. Name
2. Position in words
3. Historical season and evidence window
4. Competition
5. Club or clubs in that window
6. Recorded minutes

Shared minutes notice, shown once:

> **About recorded minutes:** The available minutes are a conservative minimum. The true total may
> be higher, so rates per 90 minutes can appear higher than they would with complete minutes.

Do not show a minute-state enum, player/grain ID, source lineage, rank, score, selection origin,
repeat marker, or expected result.

### 7. Statistics used to find similar players

Section heading: **Statistics used to find similar players**

Introductory copy:

> These recorded rates were used to find players with a similar statistical profile. Rates are
> shown per 90 recorded minutes. You can also compare each value with historical players listed in
> the same broad position. These statistics describe recorded actions; they do not by themselves
> prove that two players had the same role or playing style.

Display one aligned row per statistic, with the two recorded values and the two same-position
comparisons visible together. The control may switch between:

- **Recorded rate per 90 minutes**
- **Compared with players in the same position**

When showing the reference view, prefer **Higher than 72% of recorded players in the same
position** over the bare label “72 percentile.” The 16 football-readable row names remain:

1. Passes
2. Accurate passes
3. Crosses
4. Smart passes
5. Shots
6. Shots on target
7. Goals
8. Key passes
9. Assists
10. Duels
11. Duels won
12. Interceptions
13. Clearances
14. Accelerations
15. Fouls
16. Touches

“Smart pass” is a retained provider category and must be defined in the shared **How to read this
information** disclosure; do not invent a more specific football meaning. Event numbers, tag
numbers, registry names, exact predicates, and governed feature names remain internal.

### 8. Additional playing evidence

Section heading: **Additional playing evidence**

Required lead sentence:

> **This information provides extra context that was not used to select the comparison.**

Follow with:

> It can help describe the kinds and recorded locations of actions. It cannot establish quality,
> effectiveness, tactical instructions, or cause and effect.

The most position-relevant available family appears first:

- Goalkeeper: Goalkeeper action mix — not save quality
- Defender: Where defensive actions occurred
- Defensive midfield comparison: Where defensive actions occurred
- Attacking/shooting midfield comparison: Where shots were taken
- Forward: Where shots were taken

Then show the remaining applicable families in the governed shared order. Hide every
not-applicable family completely; it must not create a card, heading, status, empty chart, or
accessible-tree node. Do not duplicate six family sections in each player column. Each family is
one shared comparison row with Player A and Player B values/charts aligned.

For every distribution show understandable category names, an exact count, and a percentage. A
screen-reader-accessible table must carry the same information as the visual. Definitions and
limitations belong in one **What this can and cannot show** disclosure for that shared family, not
in two player-specific accordions.

Family copy:

| Internal family | Participant heading | What it can show | What it cannot show |
|---|---|---|---|
| `ID-LOC-01` | **Where recorded actions began** | The distribution of valid recorded action starts across a neutral 3×3 map. | Pitch direction and true left/right side are unavailable; the chart cannot show progression, territorial success, quality, or tactical intent. |
| `ID-PASS-01` | **Types of passes attempted** | Counts and percentages for the four retained pass categories among all recorded passes. | It does not show completion, pass quality, difficulty, direction, or outcome. Categories outside the four shown remain in the percentage denominator and should be grouped as **Other recorded pass types** if the remainder is displayed. |
| `ID-DUEL-01` | **Types of duels contested** | Counts and percentages for aerial, attacking ground, defending ground, and loose-ball ground duels. | It does not show whether a duel was won, its importance, or player quality. |
| `ID-DEFLOC-01` | **Where defensive actions occurred** | Separate neutral-map distributions for defending duels, interceptions, and clearances. | Pitch direction is unavailable. The chart does not show success, defensive quality, pressing, tactical instructions, or cause and effect. |
| `ID-SHOTLOC-01` | **Where shots were taken** | The distribution of valid recorded shot starts across a neutral map. | Pitch direction is unavailable. The chart does not show chance quality, expected goals, shot outcome, or finishing ability. |
| `ID-GK-01` | **Goalkeeper action mix — not save quality** | Goal-kick and leaving-line rates plus the recorded mix of save-attempt categories. | It does not show shots faced, save percentage, shot-stopping quality, goals prevented, errors, claims, or sweeping effectiveness. |

Availability wording:

| Internal state | Participant treatment |
|---|---|
| `observed_value` | Show the count/rate and percentage/reference comparison without an availability label. |
| `observed_zero` | Show **0 recorded** and 0%; do not imply missingness. |
| `insufficient_opportunities` | **Not enough recorded actions to show a stable breakdown.** Show the available action count, but suppress the derived percentage/reference comparison. |
| `not_applicable` | Render nothing. |
| `not_captured` | **This information was not recorded for this comparison.** No zero or estimate. |
| `invalid_missing` | **This information cannot be shown because the recorded coverage is incomplete.** No zero or estimate. |

Shared location notice, immediately before the first location chart:

> **Pitch direction is unavailable.** The grid preserves recorded locations but cannot identify
> attacking direction or true left/right pitch side. Area names describe only the neutral map you
> can see.

Neutral grid labels must replace raw coordinate identifiers:

| Internal bin | Visible and accessible label |
|---|---|
| `recorded_x_0_33__recorded_y_0_33` | Neutral map area 1 — row 1, column 1 |
| `recorded_x_0_33__recorded_y_34_66` | Neutral map area 2 — row 1, column 2 |
| `recorded_x_0_33__recorded_y_67_100` | Neutral map area 3 — row 1, column 3 |
| `recorded_x_34_66__recorded_y_0_33` | Neutral map area 4 — row 2, column 1 |
| `recorded_x_34_66__recorded_y_34_66` | Neutral map area 5 — row 2, column 2 |
| `recorded_x_34_66__recorded_y_67_100` | Neutral map area 6 — row 2, column 3 |
| `recorded_x_67_100__recorded_y_0_33` | Neutral map area 7 — row 3, column 1 |
| `recorded_x_67_100__recorded_y_34_66` | Neutral map area 8 — row 3, column 2 |
| `recorded_x_67_100__recorded_y_67_100` | Neutral map area 9 — row 3, column 3 |

The map itself is the primary spatial label. Do not interpret row/column numbers as attacking
thirds or left/right flanks.

Category translations:

| Current label | Participant label |
|---|---|
| Hand pass share | Hand passes — recorded provider category |
| High pass share | High passes |
| Launch share | Launches |
| Simple pass share | Simple passes — recorded provider category |
| Air duel share | Aerial duels |
| Ground attacking duel share | Attacking ground duels |
| Ground defending duel share | Defending ground duels |
| Ground loose-ball duel share | Loose-ball ground duels |
| Goal kicks per 90 | Goal kicks per 90 recorded minutes |
| Leaving-line actions per 90 | Leaving-line actions per 90 recorded minutes |
| Reflex save-attempt share | Reflex-labelled save attempts |
| Generic save-attempt share | Other recorded save attempts |

### 9. Shared definitions and limitations

Use one progressive disclosure titled **How to read this information** after the first visible
evidence block. It may contain:

- **Recorded value:** the count, percentage, or rate reconstructed from retained historical
  records.
- **Per 90 recorded minutes:** the recorded count scaled to 90 of the available minutes.
- **Compared with players in the same position:** where the value sits among comparable
  historical players in the same broad position; it is not a quality grade.
- **Coverage:** how much usable recorded information was available for a chart. Describe the
  participant consequence, not an internal threshold or formula.
- **Smart pass / hand pass / simple pass:** recorded provider categories whose names do not prove
  intent, difficulty, or outcome.

Use one disclosure titled **What this information cannot tell you** for the shared unsupported
constructs. Plainly group current and future ability, off-ball behaviour, tactical instruction,
opponent adjustment, recruitment outcomes, availability, fit, value, and the position-specific
goalkeeper limitations. Do not render internal inference IDs, `UNSUPPORTED_INFERENCE`, “canonical
source,” `not_captured`, or a duplicated list in both player columns.

### 10. Plain response form

Use this question order and visible wording:

1. **Can you make a fair comparison from the information provided?**
   - Yes
   - No — I do not have enough information
   - I prefer not to answer this comparison
2. **How credible is Player B as a historical playing-style comparison to Player A?**
   - 0 — Not credible from this information
   - 1 — Slightly credible
   - 2 — Mixed evidence
   - 3 — Credible
   - 4 — Strongly credible
3. **How confident are you?**
   - 1 — Very low
   - 2 — Low
   - 3 — Moderate
   - 4 — High
   - 5 — Very high
4. **What did you base your answer on?**
   - Only the information shown in this form
   - My prior professional knowledge
   - Both the information shown and my prior professional knowledge
   - I could not make a fair judgement
5. **What information helped you most? Select all that apply.**
   - Render only the applicable participant family labels, while submitting their stable internal
     family IDs.
6. **Was important information missing?** — No / Yes
7. If Yes: **What was missing?**
   - Too few recorded actions
   - A type of playing evidence was missing
   - The recorded coverage was incomplete
   - The player, position, season, competition, or club context was unclear
   - Something else
8. **Please explain anything that was unclear or insufficient.**

Behaviour and internal mapping:

| Participant answer | Internal governed meaning |
|---|---|
| Fair comparison = Yes | `state=rated`, with relevance and confidence required; `evidence_sufficiency=sufficient`. |
| Fair comparison = No — not enough information | `state=unable_to_assess`, `evidence_sufficiency=insufficient`, `assessment_basis=unable_to_assess`; missing category and explanation required. |
| Prefer not to answer | `state=abstain`; no relevance or confidence values. Ask the basis and missing-information question without inventing a rating. |
| Information shown / prior knowledge / both / could not judge | `assessment_basis` stable enums remain internal. |
| Information helped most | `cited_independent_family_ids`; visible labels are never used as stored identity. |
| Missing-information choices | `evidence_gap` stable enums remain internal. |

The first question controls later requirements. Hide or disable inapplicable questions and explain
why in plain text. Suggested status messages:

- **You can now rate the comparison and your confidence.**
- **Because you selected “No,” choose what was missing and explain what prevented a fair
  judgement.**
- **Because you prefer not to answer, no credibility or confidence rating will be recorded.**
- **Select at least one kind of additional information that helped your answer.**

Button: **Save and continue**. Do not use “response state,” “rated response,” “explicit
missingness,” “citation,” “independent family,” “qualitative note,” or enum-derived underscores.

### 11. Review, correction, and immutable submission

Heading: **Review your answers**

Intro:

> Check each comparison and the trial-feedback answers below. You can make changes now. Saving a
> change keeps the earlier answer in the local research record, but the review shows only your
> latest answer.

Each review card shows **Comparison 1: Player A and Player B**, fair-comparison answer, credibility,
confidence, basis, helpful information, missing information, and explanation in the same plain
language used on entry. Buttons are **Change this answer** and **Save changes**. Do not show
judgement states, revisions, command IDs, presentation tokens, append-only terminology, or internal
family values.

Immediately before the final button:

> **Final submission cannot be undone in this form.** After you submit, your answers are locked
> and cannot be edited. If you want to stop without submitting, close the form now.

Final button: **Submit final answers**

### 12. Self-contained trial feedback

Heading: **Tell us about the form**

Intro:

> These questions are about whether the form worked for you. They are stored separately from your
> football-comparison ratings and do not change those ratings.

Preserve these four semantics exactly, with No / Yes choices and a required explanation only when
Yes is selected:

1. **For any comparison, were the player names or recorded minutes the only information you could
   use?**
   - If Yes: **Which comparison, and why was the other information not usable?**
2. **Did any position lack enough playing evidence for a fair comparison?**
   - If Yes: **Which position, and what evidence was missing?**
3. **Was any label, chart, warning, or navigation step unclear?**
   - If Yes: **What was unclear?**
4. **Did the form appear to reveal which comparison the system preferred?**
   - If Yes: **What appeared to reveal a preference?**

These answers must use a separately versioned debrief contract and separate storage fields. They
must never be projected into relevance, sufficiency, confidence, agreement, or formal outcome
calculations.

### 13. Completion receipt

Heading: **Thank you — your answers have been submitted**

Body:

> Your answers are stored locally and are now locked. This confirms completion of the historical
> player-comparison form trial.

Show only participant-useful receipt fields:

- **Participant code:** the entered code or a safe masked form
- **Comparisons completed:** 5 of 5
- **Submitted on this computer:** human-readable local date and time with timezone
- **Status:** Submitted and locked

Buttons: **Print receipt** and **Finish**. A download, if offered, must be named
`historical-player-comparison-receipt` and contain the same plain fields. Do not expose session,
participant, authority, response, or completion IDs; hashes/digests; versions; phase codes; lane
names; query-pack identity; or database details.

### 14. Unavailable and recoverable-error states

Unavailable heading: **Historical player-comparison form unavailable**

Unavailable copy: **The form cannot start safely right now. No answers have been recorded. Please
tell the study operator.** A more specific operator-only diagnostic may be logged outside the
participant page.

Participant error mappings:

| Current technical/error text class | Participant message |
|---|---|
| unsupported/oversized/non-UTF-8/unexpected/duplicate form field | **This page could not read the form safely. Reload the page and try again.** |
| local form expired / CSRF | **This form has expired. Reload the page; your previously saved answers will remain.** |
| participant code format/digest error | **Enter the supplied participant code using 6–32 capital letters, numbers, or hyphens.** |
| every v2 consent item / eligible conflict-free reviewer | Use the specific inline eligibility or consent message above; do not collapse several causes into one error. |
| participant pseudonym already has a v2 session | **This participant code has already started a form. Continue in the original browser.** |
| v2/study session unavailable | **Your saved form could not be opened in this browser. Stop here and tell the study operator.** |
| presentation unavailable | **This comparison is no longer current. Reload the page to continue safely.** |
| session changed / stale revision | **Your saved answers changed in another tab. Reload the page before continuing.** |
| command ID reused / command conflict / payload conflict | **The form could not save this answer safely. Reload and try again; do not re-enter answers unless the page asks you to.** |
| final v2 submission immutable | **These answers have already been submitted and cannot be changed.** |
| citations must be mandatory families / response contract validation | Focus the first invalid visible field and state its question-specific requirement. Never return the contract error text. |
| all responses current before submit | **Save an answer for every comparison and resolve any highlighted questions before submitting.** |
| integrity/configuration/database/authority reconstruction failure | **The form stopped to protect your answers. Your existing saved answers were not changed. Tell the study operator.** |

## Position translation

The broad source position remains governed internally. Never show the code alone.

| Internal position | Participant position | Additional focus text |
|---|---|---|
| `GK` | Goalkeeper | none |
| `DF` | Defender | none |
| `MD` with `DEFENSIVE` branch | Midfielder | **This comparison focuses on defensive midfield evidence.** |
| `MD` with `SHOOTING` branch | Midfielder | **This comparison focuses on attacking and shooting evidence.** |
| `FW` | Forward | none |

The focus text describes the evidence branch, not a newly inferred fine-grained player position.

## Governed identities versus participant text

The presentation layer must use an explicit mapping. It must never obtain participant copy by
title-casing enum values, replacing underscores, or rendering contract labels verbatim.

| Internal governed field/value | Participant text or treatment |
|---|---|
| `position_code`, `md_subrubric` | Position translation table above. |
| `W09-INPUT-01`, `purpose=W09_INPUT`, `used_by_w09_ranking=true` | **Statistics used to find similar players**. |
| `ID-LOC-01`, `ID-PASS-01`, `ID-DUEL-01`, `ID-DEFLOC-01`, `ID-SHOTLOC-01`, `ID-GK-01` | Six family headings in the Additional playing evidence table. IDs remain hidden form values/storage only. |
| `metric_id`, `family_id`, `component_id` | Never rendered. Use an explicit reviewed label map. |
| `exact_predicate`, event/sub-event/tag expressions | Never rendered. Use reviewed football definitions. |
| `raw_value` | **Recorded value** or **Recorded rate per 90 minutes**. |
| `within_position_percentile` | **Compared with players in the same position**, expressed as “Higher than N% …”. |
| `raw_numerator`, `raw_opportunity_denominator` | **N of M recorded actions (P%)** where applicable. Do not call M a denominator. |
| `governed_minutes`, `minute_state=conservative_lower_bound` | **At least N recorded minutes** plus the one shared minutes notice. |
| `availability` enums | Availability table above. Never title-case the enum. |
| `state` enums | Fair-comparison choices. |
| `relevance_rating` | **How credible is the comparison?** |
| `confidence` | **How confident are you?** |
| `evidence_sufficiency` | **Was important information missing?** plus the fair-comparison answer. |
| `assessment_basis` | **What did you base your answer on?** |
| `cited_independent_family_ids` | **What information helped you most?** Visible checkbox labels map to stable IDs. |
| `evidence_gap` | **What was missing?** choices. |
| `explanation` | **Please explain anything that was unclear or insufficient.** |
| presentation/session/participant/query/candidate IDs, tokens, revisions, command IDs | Hidden governed transport/storage only; never participant content. |
| schema/response/evidence/policy/derivation/threshold/authority versions and digests | Governed reconstruction only; never participant content. |
| debrief field IDs | Four exact trial-feedback questions; stored separately from football answers. |

## Current participant-surface audit

This inventory covers fixed template strings, JavaScript messages, route-generated strings, and
dynamic evidence text currently capable of reaching participant bytes.

### Base shell

| Current text | Disposition |
|---|---|
| W10 expert relevance study; Scouting Intelligence · W10; Football-expert relevance study | Replace with the neutral shell. |
| A blinded, local assessment of retained 2017/18 football comparisons. | Replace with the shell lede; “blinded” and “retained” are implementation language. |
| Skip to study content | Replace with **Skip to main content**. |
| Local only | Replace with **Stored on this computer**. |
| Study home; Evidence boundary; Current step | Replace with neutral navigation. |
| Claim boundary; Football relevance, not recruitment advice | Replace with **Historical research, not recruitment advice** and approved boundary copy. |
| Participant-safe presentation authority · no ranking provenance or relevance verdict is shown. | Remove. Use the approved footer. |

### Start and unavailable pages

| Current text | Disposition |
|---|---|
| W10 v2 mechanics pilot; Mechanics pilot only · not formal evidence; Start a pseudonymous v2 pilot session; Start v2 mechanics pilot | Replace with **Historical Player Comparison**, **Research form trial**, and **Start comparisons**. |
| This pilot tests whether supplied historical football evidence is usable. There is no formal-study route, approval, or recommendation here. | Replace with the introduction; remove process/authority commentary. |
| Participant pseudonym | Replace with **Participant code** and help text. |
| Years of relevant football experience | Replace with the full question. |
| Relevant football experience | Replace with **Which experience applies to you?** |
| I have assessed players professionally within the last five years. | Convert to explicit Yes/No question. |
| I have a present or recent conflict involving a displayed player or club. | Convert to the explicit conflict question and examples. |
| Conflict note (required if declared) | Replace with the bounded plain conflict follow-up, only if retained. |
| Consent — every item is required | Replace with **Your agreement** and intro. |
| My participation is voluntary; pseudonymous responses stay in local storage; stop before final submission; final submission is immutable; historical role/style evidence | Replace with the five approved consent statements. |
| W10 v2 unavailable; V2 mechanics pilot is unavailable; No v1 authority, approval, database, or session can substitute for v2. | Replace with the neutral unavailable state; keep diagnostics operator-only. |

### Comparison and evidence page

| Current text/term | Disposition |
|---|---|
| W10 v2 evidence assessment; Mechanics pilot only; Historical role/style comparison N of N | Replace with title and **Comparison N of N**. |
| exemplar; candidate | Replace everywhere, including captions and accessible names, with **Player A; Player B**. |
| position codes GK/DF/MD/FW | Translate per the position table. |
| Evidence quantity; governed minutes; conservative lower bound; per-90 values can overstate rates | Replace with **Recorded minutes** and the single shared minutes notice. |
| Is this candidate a credible historical role/style comparison to the exemplar, given the football evidence presented? | Replace with the approved task question. |
| Player identities and governed football evidence are visible; retrieval provenance remains hidden. No panel is closer, recommended, or better. | Replace with **Judge only the information shown. The form does not show which answer is expected.** |
| Display preference; Show within-position percentiles instead of raw values | Replace with the two participant view labels. |
| Compact W09-input profile; These 16 bars reconstruct the governed within-position percentiles; raw/percentile preference | Replace with **Statistics used to find similar players** and approved explanation. |
| Frozen W09 model inputs; transparency only; used by the scorer; W09 model inputs | Remove internal method language. |
| Metric; Raw per 90; Raw value; Within-position percentile; percentile; Definition / coverage | Use **Statistic**, **Recorded rate per 90 minutes**, **Compared with players in the same position**, and **About this statistic**. |
| Independent descriptors; Required/Supplementary family; not used by W09 ranking; position-specific assessment | Replace with **Additional playing evidence**; do not label family governance status. |
| observed value; observed zero; insufficient opportunities; not applicable; not captured; invalid missing | Apply the availability table. |
| Opportunity / coverage; raw opportunity denominator; opportunity floor; threshold rationale | Replace with participant consequence and counts, or keep internal only. |
| Seven repeated family/unsupported accordions per player | Replace with shared aligned family rows; hide not-applicable families. |
| Unsupported inferences — do not infer these from this evidence; not captured | Replace with one shared **What this information cannot tell you** disclosure. |
| Shared evidence glossary; identical meaning; governed evidence; evidence purpose; denominator; coverage; interpretation boundary; known limitation | Replace with **How to read this information** and short, participant-useful definitions. |
| used by the frozen W09 scorer; not used by W09 ranking | Use the two section headings and the one required Additional playing evidence sentence. |
| retained canonical source; retained actions; exact values; exact predicate; event_id; sub_event_id; tag_ids; coordinate_evidence_state; neutral bin | Never render. Use approved football definitions and neutral-map labels. |
| all comparable observed GK/DF/MD/FW matrix rows | Replace with **historical players in the same position**. |
| Descriptive only; no better/worse, attacking-direction or pitch-side meaning. | Replace with chart-specific can/cannot copy and the shared direction notice. |
| share | Present a count and percentage, e.g. **12 of 40 recorded passes (30%)**. |

### Response, review, completion, and JavaScript

| Current text | Disposition |
|---|---|
| Evidence sufficiency; Sufficient; Insufficient | Replace with fair-comparison and missing-information questions. |
| Assessment basis; Exactly supplied evidence; Prior professional knowledge; Both; Unable to assess | Replace with **What did you base your answer on?** and its full choices. |
| Response; Rated; Abstain; Unable to assess | Replace with the fair-comparison choices. |
| Relevance (0–4); weak/strongly credible | Replace with the approved credibility question and anchors. |
| Confidence (1–5) | Replace with the approved confidence question and anchors. |
| Independent families cited (required for supplied/both); Independent citation | Replace with **What information helped you most?** and participant family labels. |
| Gap category; sparse opportunities; missing descriptor; coverage limitation; context ambiguity; other | Replace with **What was missing?** choices. |
| Qualitative note | Replace with the approved explanation question. |
| Save response | Replace with **Save and continue**. |
| Rated response selected. Relevance and confidence are required. | Replace with **You can now rate the comparison and your confidence.** |
| Explicit abstain or unable-to-assess selected. Rating controls are disabled. | Use the relevant approved status message. |
| Required before saving: relevance and confidence, an independent-evidence citation, a gap category and qualitative note. | Use question-specific plain requirements. |
| Select response state, evidence sufficiency and assessment basis. | Replace with **Answer the highlighted questions before continuing.** |
| Review and correct before immutable submission; correction appended to revision history; Assessment N; Correct response state | Replace with the approved review introduction and summaries. |
| Save append-only correction | Replace with **Save changes**. |
| When correct, submission is immutable; Submit mechanics-pilot responses | Replace with the final warning and **Submit final answers**. |
| V2 pilot submitted; response set is immutable; mechanics-pilot record is not formal evidence | Replace with the completion receipt. |
| Finish and prepare next participant | Replace with **Finish**. Participant pages must not contain operator turnover instructions. |

### Route, dynamic builder, and validation text

| Current text class | Disposition |
|---|---|
| `/w10/v2`, `/w10/v2/sessions`, `/w10/v2/judgements`, `/w10/v2/corrections`, `/w10/v2/submit`, `/w10/v2/detach`, `/static/w10-expert-study/...` | Use friendly/neutral participant paths or redirect before render. Internal aliases must not appear in visible URL or returned participant HTML. |
| Football-expert evidence mechanics pilot; local visible-identity assessment of governed 2017/18 football evidence; retrieval provenance remains hidden | Replace with neutral shell copy. |
| W10 v2 is available only on a loopback host. | Replace participant response with **This form is available only on the study computer.** Keep diagnostic code internal. |
| unsupported form; oversized form; strict UTF-8; unexpected field; fields exactly once | Map to the generic safe-form message. |
| participant code must be 6-32 uppercase alphanumeric/hyphen characters | Use participant-code help/error copy. |
| every v2 pilot consent item must be accepted; v2 mechanics pilot requires an eligible, conflict-free football reviewer | Split into the specific inline messages. |
| this participant pseudonym already has a v2 pilot session | Use duplicate-code mapping. |
| v2 session unavailable; presentation unavailable; v2 session changed; current revision; command ID/payload/command conflict | Use the recoverable-error mappings. |
| final v2 submission is immutable; all v2 pilot responses must be saved at the current revision | Use final/review mappings. |
| response/citation contract errors such as rated v2 response, mandatory family roster, descriptor family, qualitative evidence gap | Never render; translate from validated visible fields. |
| Neutral recorded start locations; Passing subtype distribution; Duel subtype distribution; Neutral defensive-action locations; Neutral shot start locations; Narrow goalkeeper involvement mix | Use the six approved family headings. |
| Frozen W09 scorer inputs | Use **Statistics used to find similar players**. |
| Recorded event-8/event-10/event-1; sub-event-XX; tag XXX; predicate expressions | Never render. |
| all nine `recorded_x_*__recorded_y_*` bin names | Use the neutral-grid labels and visual. |
| observed state labels, W09/ID family identifiers, metric IDs, purpose values, version/digest/lineage fields | Never render. |

## Forbidden participant-language inventory

The participant-surface scan is case-insensitive and applies to rendered text, titles, headings,
help, validation, ARIA labels/descriptions, table captions, chart labels, button text, URLs left in
the address bar, returned participant HTML/JSON, participant downloads, and receipt content.
Operator-only logs and governed storage may retain these terms.

### Internal programme and gate language

- `W03` through `W10`, including `W09-input`, `W10 v2`, and `/w10`
- `G-RW4`, `A5`, `08D`, `08E`, `08F`, and any A0–A8 or work-package shorthand
- v1/v2 when used as an authority, protocol, response, evidence, pilot, or presentation version
- phase, gate, checkpoint, acceptance, REWORK, PASS/FAIL/INSUFFICIENT_EVIDENCE
- formal route, formal evidence, protected outcome, pilot pack, query pack

### Internal retrieval, evidence, and contract language

- matrix, scorer, feature registry, canonical authority, canonical source
- predicate, exact predicate, digest, lineage, schema version, policy digest, authority version
- presentation version, response version, evidence version, derivation version, threshold policy
- query-pack identifier, authority identifier, presentation token, command ID, revision
- independent descriptor, independent family, family ID, mandatory family, family roster
- `W09-INPUT-01`, every `ID-*-01`, and every metric/component/inference identifier
- raw coordinate identifiers beginning `recorded_x_` or containing `__recorded_y_`
- `event_id`, `sub_event_id`, `tag_ids`, `coordinate_evidence_state`
- observed value, observed zero, raw value, governed minutes, opportunity denominator, opportunity
  floor, retained action, matrix row
- participant-safe, presentation authority, evidence lane, claim boundary, evidence boundary,
  retrieval provenance, ranking provenance, relevance verdict
- unexplained “mechanics pilot”; participant copy uses **research form trial** or **form trial**

### Protected/blinding language and values

- rank, aggregate score, distance, similarity score, expected answer/result/outcome
- retrieved, control, origin, selection rule, evidence band, difficulty label
- repeat, repeat anchor, repeat linkage, previous response, aggregate response
- closer, better, recommended, system preferred, except in the debrief question that asks whether
  the form *appeared* to reveal a preference
- player/grain/query/candidate/session IDs and UUID-like opaque identities

The ordinary football word “score” may appear only when it unambiguously means a match score; the
participant comparison surface currently has no need to use it. “Rank” and “matrix” likewise have
no participant use and should be blocked without exceptions.

## UX and content acceptance checklist

### Comprehension and journey

- [ ] A participant who knows nothing about the repository can explain the purpose, task, local
  storage, withdrawal boundary, immutable final submission, and non-recruitment boundary from the
  start page alone.
- [ ] Eligibility and conflicts are stated as direct Yes/No questions with examples and inline
  reasons when the participant cannot continue.
- [ ] The task question uses Player A and Player B and asks about a historical playing-style
  comparison based on the information shown.
- [ ] Progress reads **Comparison N of total** and resume restores the next comparison without an
  operator translating the state.
- [ ] Review summarizes answers in the same wording used to collect them; corrections are described
  as changes, not revision commands.
- [ ] The four trial-feedback questions are completed in-form, remain semantically exact, and are
  stored separately from football-relevance answers.
- [ ] Completion produces the plain local receipt and contains no project/version/authority codes.

### Evidence and scientific boundary

- [ ] Player A and Player B use the same context fields, evidence schema, row order, units, scales,
  definitions, missingness rules, and accessible alternatives.
- [ ] The 16 selection statistics appear under **Statistics used to find similar players**.
- [ ] Independent evidence appears under **Additional playing evidence** with the exact sentence
  **This information provides extra context that was not used to select the comparison.**
- [ ] The position-relevant additional evidence appears first; every applicable family remains
  available and no not-applicable section reaches the DOM or accessibility tree.
- [ ] Additional-evidence charts show category names, counts, and percentages for both players.
- [ ] Each chart has one nearby can/cannot explanation; every location chart clearly states that
  pitch direction is unavailable.
- [ ] No text or visual implies effectiveness, quality, causal meaning, tactical instruction,
  progression, pitch side, or attacking direction unsupported by the data.
- [ ] Participant copy does not reveal rank, score, origin, repeat identity, control/retrieved arm,
  expected answer, or previous/aggregate outcomes.
- [ ] Internal IDs and exact values still submit to the governed store so audit reconstruction is
  exact; visible labels are explicit mappings rather than stored identities.

### Accessibility, mobile, and interaction

- [ ] Headings form one logical hierarchy; every fieldset has a clear legend; help and error text
  is programmatically associated with its control.
- [ ] First invalid field receives focus; an error summary links to every invalid question; status
  changes use a polite live region and do not overwrite useful instructions.
- [ ] Every action is keyboard reachable, has a visible focus indicator, and works without pointer
  precision. No accordion or toggle traps focus.
- [ ] Charts have equivalent tables or textual summaries. Colour is never the only differentiator,
  and Player A/B are named in accessible labels.
- [ ] At 320 CSS pixels wide there is no horizontal page scroll, clipped label, inaccessible table,
  overlapping control, or side-by-side value whose player identity becomes ambiguous.
- [ ] Touch targets are at least 44 by 44 CSS pixels where practical, labels activate their
  controls, and no essential definition depends on hover.
- [ ] Reduced motion, 200% text zoom, and browser back/forward do not lose saved answers or hide
  the current validation state.

### Leakage and validation

- [ ] Case-insensitive scans of participant HTML, JSON, browser-accessible payloads, titles, ARIA,
  errors, receipt, and downloadable content find none of the forbidden inventory.
- [ ] The friendly route remains in the address bar and internal route/asset names do not appear in
  participant HTML.
- [ ] No raw coordinate identifier appears as visible or accessible text.
- [ ] No enum value is generated by replacing underscores or title-casing contract values.
- [ ] No contract/storage exception is interpolated directly into a participant page.
- [ ] Invalid start, judgement, correction, debrief, and submit attempts receive a specific
  understandable message without internal identifiers.
- [ ] Browser verification records no external request, console error, page error, or protected
  field in the participant payload.

## Residual design risks for master review

1. The current response contract couples a rated judgement to sufficient evidence and requires an
   additional-evidence citation when the supplied information is used. The implementation must
   preserve those semantics while presenting one coherent sequence; it must not silently reinterpret
   “Was important information missing?” independently of fair-comparison state.
2. Current pass subtype names are provider categories. “Hand pass” and “Simple pass” need the
   explicit provider-category qualifier above; inventing a conventional football definition would
   overclaim source semantics.
3. The neutral 3×3 map lacks direction and true pitch-side meaning. Visual orientation can still
   invite inference, so the direction warning, neutral area labels, and adversarial browser review
   are required.
4. The current storage can emit detailed internal exceptions. Route-level participant error
   mapping must be exhaustive, with full diagnostics retained only for operator evidence.
5. A displayed receipt must not reuse a governed digest or UUID as participant content. If a
   participant-visible reference is later required, it needs a separate non-authoritative human
   reference contract and review.
