# W04 governed source card — Wyscout Figshare v5

Status: **authorised for a frozen local proof of concept**

## Exact source

- Dataset: *Soccer match event dataset*
- Source data provider: Wyscout
- Dataset authors: Pappalardo et al.
- Publisher: figshare
- Collection: version 5
- DOI: `10.6084/m9.figshare.c.4415000.v5`
- Collection release used as source availability: `2020-01-28T14:24:27Z`
- Data paper: `10.1038/s41597-019-0247-7`
- Licence: Creative Commons Attribution 4.0 International

The checked-in configuration
[`configs/sources/w04-provider.yaml`](../../configs/sources/w04-provider.yaml) is the
normative file, archive-member, rights, coverage, and acquisition declaration.

Each exact `ndownloader.figshare.com` object URL currently responds with one HTTP 302
to Figshare's `s3-eu-west-1.amazonaws.com/pfigshare-u-files` delivery path. The
normative configuration permits only that one hop, the exact file-ID/name path, and
the reviewed short-lived AWS signature fields. The observed credential scope uses
literal `/` separators; encoded separator aliases are not admitted. A different host,
bucket path, file identity, query shape or encoding, status, second redirect, or
expiry over 60 seconds fails closed. This is transport for the same Figshare object,
not authority for remote storage or transfer after acquisition.

## Intended use

This source supports one local, frozen engineering and player-retrieval proof. It may
be retained, normalised, aggregated, used for feature/model work, and displayed in the
local application with attribution. Raw exports and all external hosting, sharing,
model calls, telemetry, and deployment remain disabled by the stricter project
boundary even where CC BY would permit them.

It does not support claims about current player availability, present-day competition
coverage, live provider continuity, women or youth populations, prospective
recruitment effectiveness, or equivalence to a current commercial Wyscout product.

## Population and coverage

The first pass admits the complete 2017/18 English, French, German, Italian, and
Spanish top-flight source partitions. Euro 2016 and World Cup 2018 are present in the
published ZIP directories but excluded from the first-pass data product. Their four
known archive members are directory-verified and deliberately not extracted or
admitted. Any other archive member remains an unknown-member failure.

The publication reports 1,941 matches, 3,251,294 events, and 4,299 players across all
seven published competitions. W04 must measure and report the exact admitted counts
for the five domestic partitions after acquisition; those counts are not guessed here.

The population is historical male senior football. There is no women or youth
coverage. Native possession identifiers, continuous tracking, freeze frames,
per-record first-publication times, and a correction ledger are absent. Possessions and
lineup stints are project-derived transformations and must be labelled as such.

## Temporal and leakage boundary

Match and event occurrence time comes from `dateutc`, `matchPeriod`, and `eventSec`.
No source record is treated as knowable before the v5 collection release at
`2020-01-28T14:24:27Z`. File acquisition time is operational metadata, not evidence of
historical availability.

Publication-time player master data may contain facts that post-date individual
matches. Historical joins therefore use match-bound team, lineup, bench, substitution,
and event evidence. Unversioned player-master attributes must not be used as
historical features.

## Rights and attribution

CC BY 4.0 permits copying, redistribution, transformation, and use for any purpose,
subject to attribution, a licence link, and an indication of changes. This project
uses the following attribution:

> Data source: Pappalardo et al., Soccer match event dataset, supplied by Wyscout,
> figshare collection v5, licensed CC BY 4.0.

Change notice: the project normalises source JSON, reconstructs lineup stints and
possessions, and derives player-window aggregates.

This card records the implementation classification and is not legal advice.

## Known risks

- The data is old and cannot establish current scouting value.
- One season limits trajectory and longitudinal claims.
- Provider identifiers are stable only inside the frozen snapshot.
- Possession and minutes reconstruction can be wrong and require reconciliation.
- Event collection is observational and inherits provider taxonomy and operator bias.
- Cross-league comparisons require explicit context and must not be presented as
  competition-strength adjustment.
