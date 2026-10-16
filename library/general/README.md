# `general/` — the packaged starter set

Five scrubbed, estate-neutral graphs that ship with the plugin. The door
resolves `from: general/<name>` against them whenever your private library
(``<runs_root>/library/general/``) misses, so a fresh install can run a real
DAG without authoring anything first. Precedence is
**runs_root library > legacy launch root > this packaged set**: shelve a
tuned copy under the same address (`workflow save name=general/<name>`) and
your copy shadows the packaged one; the packaged files are never written by
the door.

| Address | Reach for it when | Showcase |
|---|---|---|
| `general/pr-review-light` | an open PR needs an advisory second read before a human looks | fan-out over a string list; run-dir scratch |
| `general/issue-triage` | a queue needs the standing rule applied while you sleep | the `{run.KEY}` seed contract, declared in the description |
| `general/test-first-feature-slice` | one behavior is worth a red-green-proof slice | build chain + independent verifier that re-runs, not re-reads |
| `general/fan-out-audit-census` | a tree needs a per-file audit with an honest tally | the 8 KB per-parent input cap by example: paths in item goals, schemas pin the `path` key |
| `general/report-and-verify` | a producer will drop a report later and you want zero tokens while waiting | machine `wait` gate: fixed `until_argv`, `every_s`/`timeout_s`, timeout = failure |

All five route every agent through model **tiers** — no graph names a
vendor model. Configure at least `worker` and `manager` in the plugin
settings (see the README two levels up), e.g.:

```yaml
plugins:
  entries:
    hermes-workflows:
      settings:
        models:
          worker: seat-fast      # placeholders: your own alias or model id
          manager: seat-strong
```

Customize one, then share it back: run it, tune it, `save` it under the same
`general/` address to shadow it, and send the tuned graph to
`workflow submit` — the study inbox is how this set grows (issue #50).
