# WOFification — converting a way-of-working repo into a shelf pack

WOFification turns a *way-of-working repo* (skills tree, playbooks, agent
personas, automation packs, guide docs) into a *pack*: converted wf/1 workflow
graphs, adapted skills, and compact rules, ready to adopt with copy and
`workflow save` lines. The five-lane conversion factory graph lives on the
shelf (`wofification-factory`); this plugin ships the deterministic seam it
runs on: `scripts/wofify.py`. Like the vaporized `wf_dialect.py` before it, it
is authoring-time only and deliberately NOT a door action.

## Pack layout (what every verb reads and writes)

    <pack>/
      inventory.json   census written by `inventory`; classification is
                       path shape only — prose never sets a kind
      pack.json        manifest of ADOPTED units (id, disposition, artifact,
                       sha256) written by the convert lanes after review
      README.md        install instructions (`scaffold` stubs it)
      skills/          adapted skill bodies (disposition: skill|rule)
      workflows/       converted graphs (+ optional .cards.json sidecars,
                       which validation skips — sidecars are not graphs)
      rules/ reports/  compact rules and gap reports

Dispositions are a closed set: `skill | wof | rule | skip`.

## Verbs and exit law

| verb | what | fails (exit 1, named) when |
|---|---|---|
| `inventory <repo> --out <pack>` | census to `inventory.json`, creates the tree | repo has zero units (a silent zero hides a wrong path) |
| `scaffold <pack> [--source U] [--commit S]` | `pack.json` + README skeleton | either file exists — authored state is never clobbered |
| `validate <pack>` | compiles each `workflows/*.json` (includes expanded) then measures it with the door's own `validate_graph_full` | zero graphs, or any defect — every defect names its file |
| `shelf <pack> [--skills-dir D]` | prints the adoption script (save/run lines, cp lines) | no units, missing artifact, sha256 drift, unknown disposition |

Same tree, same bytes: the census sorts its walks and carries no clock.
`validate` refusing on zero graphs is the loud-zero law — an empty directory
is never green. Stdlib only; no subprocess, no network, no door writes.

## Division of labour

Deterministic seams belong to the script; judgement belongs to the graph.
Classifying an inventory unit's disposition (skill / wof / rule / skip) and
rewriting a procedure into nodes is agent work under the honesty rules — the
script never guesses dispositions, and `shelf` refuses to invent them: it
reads exactly what `pack.json` says and proves every artifact's bytes.
