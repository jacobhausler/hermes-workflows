#!/usr/bin/env python3
"""DIAGRAM LAW v1 — the derived-diagram gate contracts (stdlib-only).

Laws under test:
 - L0 determinism: same graph bytes -> same candidate bytes (derive twice, equal).
 - L3 sidecar: a graph without its <name>.cards.json fails named, never silently.
 - L3/A3 counts injected, not typed: a bare digit in card text is refused with
   the token hint; an unknown {{token}} is refused closed.
 - L5 README derived: diagram_readme rebuilds the table byte-stably (idempotent).
 - A4 no twin rows: no shipped example is a copy of a foreign estate artifact
   under this PR's shape (frontier-review must NOT appear as an example graph).
 - --check is the CI freshness mode: byte-identical passes, drift exits 1.
"""
import json, os, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "scripts", "graph_diagram.py")
ok = True
_n = 0


def check(name, cond, detail=""):
    global ok, _n
    _n += 1
    if cond:
        print(f"PASS {name}")
    else:
        ok = False
        print(f"FAIL {name} :: {detail[:200]}")


def run(args, cwd=ROOT):
    return subprocess.run([sys.executable, GEN] + args, cwd=cwd,
                          capture_output=True, text=True)


G = {"name": "gate-law", "description": "d",
     "nodes": [{"id": "a", "type": "agent", "goal": "do it"},
               {"id": "b", "type": "gate", "after": ["a"],
                "question": "ship?", "options": ["y", "n"]},
               {"id": "c", "type": "agent", "after": ["b"]}]}
CARDS = {"cards": [{"dot": "cyan", "title": "Why it works",
                    "items": ["entry -> hold -> act"]},
                   {"dot": "rose", "title": "Contract",
                    "items": ["{{nodes}} nodes, {{gates}} gates"]}]}

tmp = tempfile.mkdtemp(prefix="diagramlaw")
try:
    gp = os.path.join(tmp, "gate-law.json")
    cp = os.path.join(tmp, "gate-law.cards.json")
    json.dump(G, open(gp, "w"))
    json.dump(CARDS, open(cp, "w"))

    r1 = run([gp, "--out", tmp])
    check("L1 derive writes the candidate", r1.returncode == 0, r1.stderr)
    cand_path = os.path.join(tmp, "gate-law.candidate.json")
    b1 = open(cand_path, "rb").read() if os.path.exists(cand_path) else b""
    r2 = run([gp, "--out", tmp])
    b2 = open(cand_path, "rb").read() if os.path.exists(cand_path) else b""
    check("L0 determinism: same input, same bytes", bool(b1) and b1 == b2)
    cand = json.loads(b1 or b"{}")
    contract = json.dumps(cand.get("cards", []))
    check("A3 injection renders {{nodes}} -> 3", "3 nodes" in contract, contract)
    check("A3 injection renders {{gates}} -> 1", "1 gates" in contract, contract)

    r = run(["--check", gp, "--out", tmp])
    check("L6 --check passes on fresh bytes", r.returncode == 0, r.stderr)

    # typed digit refused
    bad = json.load(open(cp))
    bad["cards"][1]["items"][0] = "Nodes: 7, 3 gates"
    json.dump(bad, open(cp, "w"))
    r = run([gp, "--out", tmp])
    check("A3 bare digit in card refused", r.returncode != 0
          and "typed number" in (r.stderr + r.stdout), r.stderr)
    # unknown token refused
    bad["cards"][1]["items"][0] = "{{nonexistent}} nodes"
    json.dump(bad, open(cp, "w"))
    r = run([gp, "--out", tmp])
    check("A3 unknown token refused closed", r.returncode != 0
          and "unknown token" in (r.stderr + r.stdout), r.stderr)
    # drift: fresh candidate then mutate source graph, --check must go red
    good = json.load(open(cp))
    good["cards"][1]["items"][0] = "{{nodes}} nodes, {{gates}} gates"
    json.dump(good, open(cp, "w"))
    run([gp, "--out", tmp])
    G["nodes"].append({"id": "d", "type": "agent", "after": ["c"], "goal": "x"})
    json.dump(G, open(gp, "w"))
    r = run(["--check", gp, "--out", tmp])
    check("L6 --check red on graph drift", r.returncode != 0, "drift not caught")

    # missing sidecar named, not silent
    g2 = os.path.join(tmp, "no-cards.json")
    json.dump({"name": "no-cards", "nodes": [{"id": "a", "goal": "x"}]}, open(g2, "w"))
    r = run([g2, "--out", tmp])
    check("L3 missing cards sidecar fails named", r.returncode != 0
          and "no-cards.cards.json" in (r.stderr + r.stdout), r.stderr)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# repo-wide invariants over the shipped examples
r = run(["--check", "--all"])
check("L6 --check --all green on shipped bytes", r.returncode == 0, r.stderr)
twins = [p for p in os.listdir(os.path.join(ROOT, "examples", "review"))
         if "frontier" in p.lower()]
check("A4 no foreign-estate twin under examples/", not twins, str(twins))
r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "diagram_readme.py")],
                   cwd=ROOT, capture_output=True, text=True)
check("L5 README rebuild exits 0", r.returncode == 0, r.stderr)
check("L5 committed README is derived-current (no hand-edit, no staleness)",
      "UNCHANGED" in r.stdout, r.stdout + r.stderr)
r2 = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "diagram_readme.py")],
                    cwd=ROOT, capture_output=True, text=True)
check("L5 README rebuild idempotent", "UNCHANGED" in r2.stdout, r2.stdout)

print(f"{'ALL PASS' if ok else 'FAILURES PRESENT'} ({_n} diagram-law contracts)")
sys.exit(0 if ok else 1)
