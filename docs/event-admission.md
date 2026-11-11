# Event admission — the wake-route law

A wake is an event, and events are cheap to lose and expensive to replay wrong.
This is the admission law for the wake route: what a payload may carry, who
re-checks eligibility on both sides, what a consumer answers with, and what
recovers a dropped wake.

## The 5-hop map

```
┌───────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐
│ publisher │───▶│ wake route │───▶│ guards  │───▶│ dead-man │───▶│ graphs │
└───────────┘    └────────────┘    └─────────┘    └──────────┘    └────────┘
  ids+actor+      one mechanical    the woken      fixed tick      the work
  time only —     script per        session        re-runs the     runs on the
  the body        route; pipe,      re-reads       guard over      survivors of
  stays in        not actor         the body       the live        the re-decide,
  the ledger                        before         pile; events    never on the
                                    deciding       it missed       memory of a
                                                                  dropped wake
```

Five legs, three laws: the payload is a pointer, never truth; the guard answers
in typed codes; the dead-man makes loss survivable. This map is the worked
diagram reference for every section below.

## Triggers, never truth

Event payloads carry ids+actor+time only — the body stays in the ledger and
every woken consumer re-reads it before deciding. One mechanical script per
wake route: the woken session is the pipe, not the actor. And the event bus is
an accelerator, not a database: a cron dead-man re-runs the guard over the live
pile on a fixed tick, so dropped events self-heal.

## Emit == consume

The fanout filter on the publish side and the re-check on the dispatch side
must import ONE predicate module; two hand-written copies drift and replays
turn into dead-on-arrival wakes — cost paid, no effect. The predicate should
also encode hands-off law in one place: an assignee set or human owner means
claimed; a creator-stamped `owner` field is provenance, not a claim.

## Three answers, three codes

A consumer guard that re-decides a subject needs a typed three-state return:

| answer | ledger | exit |
|---|---|---|
| permanent no | written — the subject goes silent, never re-presented | 0 |
| deferred (memory pressure, provisioning failure, transient) | NOTHING written | 3 |
| real error | — | non-zero, loud |

A guard that collapses deferred into "no" loses work silently; one that writes
the ledger on deferred replays forever. This is the mirror of the plugin's
documented gate-probe polarity law
([operator playbook](../references/operator-playbook.md)) — same discipline,
moved to the consumer's ledger.

## Day-one pitfalls: burst-shed

Burst-shed loss: catch-up drains batch events since the cursor and the
wake-window coalescer keeps the FIRST payload per window and ack-drops the rest
— silently, no marker on the subject. On a busy bus you must verify
per-subject that the consumer acted (space test triggers wider than the
coalescer window); a missing verdict is a lost event until proven otherwise,
and the dead-man tick is the recovery path — this is why the dead-man leg is
not optional.
