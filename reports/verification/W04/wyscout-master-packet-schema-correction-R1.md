# W04 master packet schema correction R1

## Decision

`CORRECTED_FOR_VERIFIER_REVIEW`.

The independent phase-verifier review correctly required a master-owned task
packet to satisfy the repository's canonical mandatory field contract before
that packet can support an empty delegated-return exemption.

The master audited every packet with `assigned_role: master` against
`scripts.verify_task_return.REQUIRED_PACKET_FIELDS`. Only two packets associated
with current W04 registry tasks that intentionally have empty return lists were
incomplete:

| Packet | Missing mandatory field |
| --- | --- |
| `orchestration/task_packets/W04-SOURCE-AUTHORITY-01-R2.yaml` | `read_first` |
| `orchestration/task_packets/W04-SOURCE-ACQUIRE-01-R1.yaml` | `return_template` |

The correction adds the standard bounded `read_first` roster to the source
authority R2 packet and the canonical
`orchestration/templates/subagent_return.md` reference to the source-acquisition
packet. No task objective, authority, allowed path, forbidden path, dependency,
acceptance check, acquisition behavior, data-rights decision, lifecycle state,
or product semantic changed.

The remaining schema-incomplete master packets all have retained returns and
therefore do not request or receive this narrowly guarded exemption. They remain
visible audit findings for their own future lifecycle work; the R21 correction
does not mutate them.
