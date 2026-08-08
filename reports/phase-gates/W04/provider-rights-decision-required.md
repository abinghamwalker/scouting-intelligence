# W04.1 provider and rights decision

Status: **DECIDED — WYSCOUT FIGSHARE V5 AUTHORISED FOR FROZEN LOCAL POC**

Recorded at `2026-07-29T12:57:56Z` after creating local annotated start tag
`checkpoint/w04-start` from accepted W03 commit
`f29d71c3cb8e6457f7ea9f61ffa4feff28d44572`.

## User decision

On 2026-07-29 the user selected the older Wyscout open dataset for the first-pass
proof of concept after reviewing the StatsBomb and open-dataset trade-offs.

- Exact dataset: *Soccer match event dataset*
- Source provider: Wyscout
- Publisher: figshare
- Exact collection: version 5
- DOI: `10.6084/m9.figshare.c.4415000.v5`
- Licence: CC BY 4.0
- First-pass scope: complete 2017/18 English, French, German, Italian, and Spanish
  top-flight partitions
- Excluded initially: the explicitly named Euro 2016 and World Cup 2018 archive
  members, which are directory-verified but not extracted or admitted
- Boundary: frozen, local-only proof of concept; no current, live, women/youth, or
  prospective scouting claim

The normative machine-readable authority packet is
[`configs/sources/w04-provider.yaml`](../../../configs/sources/w04-provider.yaml).
The human-readable classification is
[`docs/dataset-cards/w04-source.md`](../../../docs/dataset-cards/w04-source.md).

## Research available

The primary-source comparison, conditional shortlist, published-rights matrix,
provider questions, and unfilled decision schedule are recorded in
[`provider-rights-research-packet.md`](provider-rights-research-packet.md). That research
does not grant acquisition authority or change this blocked status.

## Why the prior blocker is closed

The user supplied the material product and data-rights decision that implementation
could not make. The publication states that the data is CC BY 4.0, and the licence
permits reproduction and adaptation with attribution. The exact public file IDs,
sizes, provider MD5 digests, and allowed archive members are now frozen.

Project controls remain stricter than the licence: raw export, external sharing,
public/hosted display, remote storage, deployment, and external model calls remain
forbidden. All derived artifacts must retain the source manifest, attribution, licence,
change notice, and frozen historical claim boundary.

## Temporal decision

The source has match/event occurrence time but no per-record first-publication or
correction history. The collection v5 publication time
`2020-01-28T14:24:27Z` is therefore the earliest permitted `available_at` for every
record. No historical replay may claim the facts were knowable before that instant.
Publication-time player-master attributes are excluded from historical feature joins
unless independently supported by match-bound evidence.

## Acquisition authority

One bounded, unauthenticated HTTPS acquisition is authorised from the exact Figshare
file URLs in the normative source config. Files must remain under guarded ignored
local roots, match exact name/size/MD5 declarations, receive computed SHA-256 digests,
and pass safe-archive admission before a completion manifest is written.
The exact URLs currently return one HTTP 302 to Figshare's S3 delivery backend. That
single transport hop is authorised only when it is HTTPS, uses the exact reviewed
host and file-ID/name path, has the exact short-lived AWS signature query shape with
literal `/` credential-scope separators and an expiry no greater than 60 seconds, and
is followed by no further redirect. Encoded separator aliases and any other redirect
fail closed.
The published archives contain two additional, explicitly named tournament members
each. Those entries are classified `scope_excluded`; their payloads are not extracted
or admitted. Any member outside the five admitted and two known-excluded names remains
an unknown-member failure.

No account, credential, payment, click-through acceptance, cloud resource, hosted CI,
remote repository, public endpoint, or deployment is authorised or required.

`git remote` must remain empty and the W01 push guard remains active.
