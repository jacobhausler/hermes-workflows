#!/usr/bin/env python3
"""est-i24i: the graphify-out orphan check must be DELETION-AWARE.

The trap (adversary 231 counterfactual, ADVERSARY-231.md + graph-gate-counterfactual.json):
a PR that DELETES source files cannot regenerate graphify-out/ (single-writer law,
scripts/graph_path_ban.py), yet the committed graph still indexes the deleted paths.
The old test_graph_gate.py:34-37 orphan check — "every source_file the graph indexes
is tracked in THIS tree" — fails exactly that PR, while regenerating in-PR fails the
path ban. Both repairs were impossible; the gates contradicted each other.

The reconciled law pinned here:
  * orphans whose source EXISTS in the PR's base commit are expected-and-tolerated
    until the next single-writer regen (that is what the single-writer gate exists for);
  * orphans indexing sources that were NEVER in the base remain hard failures;
  * tolerance applies ONLY in PR context (a resolvable PR base). On main the graph
    must be exactly current (graph-main CI proves it) — no tolerance there;
  * an unresolvable base fails CLOSED: every orphan is reported, none tolerated;
  * the exact-head freshness check (graph_check STALE on edited source) is
    UNTOUCHED and stays red for stale graphs; the path ban and the chore/graph-
    branch exemption are UNTOUCHED (a control case here asserts the ban stays red
    for a source branch that touches graphify-out/).

RED on base: scripts/graph_orphans.py does not exist (the library the reconciled
check lives in), so every case here fails; the counterfactual PR fails the
test_graph_gate orphan check exactly as the adversary's without-regen worktree did.

Hermetic: synthetic git repos with a HAND-WRITTEN graph.json (the orphan check reads
only source_file/community fields), so the core cases need no graphify CLI. The
exact-head STALE case uses the real CLI when it is on PATH and SKIPs otherwise
(test_graph_gate already fails closed on the missing declared dep).
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checks = 0
failures = 0


def check(label, cond, detail=""):
    global checks, failures
    checks += 1
    if cond:
        print(f"PASS " + label)
    else:
        failures += 1
        print(f"FAIL {label}: {detail}")


_lib_path = ROOT / "scripts" / "graph_orphans.py"
go = None
if _lib_path.exists():
    go = load("graph_orphans_i24i", _lib_path)
check("scripts/graph_orphans.py exists (the orphan library)", go is not None,
      "library missing — RED: the deletion-aware orphan logic has no home")


# --- synthetic repo builders -------------------------------------------------------

def git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, env=env)


def commit_all(repo, msg):
    r = git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "add", "-A")
    assert r.returncode == 0, r.stderr
    staged = git(repo, "diff", "--cached", "--name-only")
    if not staged.stdout.strip():  # nothing moved: pin the current HEAD instead
        r = git(repo, "rev-parse", "HEAD")
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()
    e = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    r = git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", msg, env=e)
    assert r.returncode == 0, r.stderr
    r = git(repo, "rev-parse", "HEAD")
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


CORE_SOURCES = ["__init__.py", "wf.py", "wfcommon.py", "desktop/plugin.js"]
GITIGNORE_TEXT = ("graphify-out/graph.html\ngraphify-out/cache/\n"
                  "graphify-out/cost.json\n")


def all_graph_sources(sources):
    """Every path graph_json will index: the case sources padded to >500 nodes
    with pad/mod_*.py (never colliding with the case sources)."""
    uniq = sorted(set(sources))
    pad = []
    pad_i = 0
    while len(uniq) + len(pad) < 600:
        cand = f"pad/mod_{pad_i}.py"
        pad_i += 1
        if cand not in uniq:
            pad.append(cand)
    return uniq + pad


def graph_json(sources):
    """Hand-written graph.json satisfying test_graph_gate's shape asserts:
    >500 nodes, >1000 edges, real community_name on every node, and the
    door/runner/read-model/desktop half covered in `sources`."""
    all_src = all_graph_sources(sources)
    nodes = [{"id": f"m{i}_{s.replace('/', '_').replace('.', '_')}",
              "label": s, "source_file": s, "community": i % 7,
              "community_name": f"Group {i % 7}"}
             for i, s in enumerate(all_src)]
    links = [{"source": nodes[0]["id"], "target": nodes[i]["id"], "relation": "imports"}
             for i in range(1, len(nodes))]
    links += [{"source": nodes[i]["id"], "target": nodes[i + 1]["id"], "relation": "calls"}
              for i in range(0, len(nodes) - 1, 2)]
    links += [{"source": nodes[i]["id"], "target": nodes[(i + 3) % len(nodes)]["id"],
               "relation": "uses"} for i in range(0, len(nodes), 3)]
    return json.dumps({"multigraph": False, "nodes": nodes, "links": links},
                      indent=2) + "\n"


def build_repo(td, sources, graph_sources, absent=()):
    """Repo with committed sources + committed graph indexing graph_sources,
    wired so tests/test_graph_gate.py can be replayed inside it (it re-reads
    ROOT/graphify-out and ROOT's tracked tree relative to its own location).
    Every source the graph indexes becomes a real tracked file at the base
    commit UNLESS listed in `absent` (the fabricated-orphan case) — the
    deletion cases then DELETE exactly the ones under test."""
    repo = Path(td) / "repo"
    repo.mkdir()
    all_files = (set(sources) | set(CORE_SOURCES)
                 | set(all_graph_sources(graph_sources)) - set(absent))
    for rel in sorted(all_files):
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"def {Path(rel).stem}():\n    return 1\n")
    (repo / "scripts").mkdir(exist_ok=True)
    (repo / "scripts" / "graph_orphans.py").write_text(_lib_path.read_text())
    (repo / "scripts" / "graph_check.py").write_text(
        (ROOT / "scripts" / "graph_check.py").read_text())
    (repo / "tests").mkdir(exist_ok=True)
    (repo / "tests" / "test_graph_gate.py").write_text(
        (ROOT / "tests" / "test_graph_gate.py").read_text())
    (repo / "tests" / "graph_gate_dep.py").write_text(
        (ROOT / "tests" / "graph_gate_dep.py").read_text())
    (repo / ".gitignore").write_text(GITIGNORE_TEXT)
    gdir = repo / "graphify-out"
    gdir.mkdir(exist_ok=True)
    (gdir / "graph.json").write_text(graph_json(graph_sources))
    git(repo, "init", "-q")
    sha = commit_all(repo, "init")
    return repo, sha


def pr_env(repo_sha_map, event_extra=None):
    ev = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    json.dump({"pull_request": {"base": {"sha": repo_sha_map}, "number": 1}}, ev)
    ev.close()
    return {**os.environ, "GITHUB_HEAD_REF": "fix/delete-something",
            "GITHUB_BASE_REF": "main", "GITHUB_EVENT_NAME": "pull_request",
            "GITHUB_EVENT_PATH": ev.name}


NO_PR_ENV = {k: v for k, v in os.environ.items()
            if k not in ("GITHUB_HEAD_REF", "GITHUB_BASE_REF",
                        "GITHUB_EVENT_NAME", "GITHUB_EVENT_PATH")}


def run_cli(repo, extra_args, env=None):
    return subprocess.run(
        [sys.executable, str(repo / "scripts" / "graph_orphans.py"),
         "--repo-dir", str(repo), *extra_args],
        capture_output=True, text=True, env=env if env is not None else NO_PR_ENV)


if go is not None:
    # --- control: the single-writer ban stays RED (untouched) --------------------------
    gpb = load("graph_path_ban_i24i", ROOT / "scripts" / "graph_path_ban.py")
    check("ban_decision stays RED for a source branch that touches graphify-out "
          "(single-writer gate untouched — control case)",
          gpb.ban_decision(["a.py", "graphify-out/graph.json"], "fix/some-lane")
          == ["graphify-out/graph.json"],
          "the path ban decision was weakened")
    check("ban_decision still EXEMPTS the regen lane (chore/graph- + graph-only diff)",
          gpb.ban_decision(["graphify-out/graph.json"], "chore/graph-abc1234") is None,
          "the regen exemption was weakened")

    # --- counterfactual 1: PR deletes a source the base graph indexes -> tolerated ----
    # Mirror of #231: base graph indexes a.py + gone.py; the PR `git rm`'s gone.py
    # (and nothing else) and leaves graphify-out/ untouched.
    with tempfile.TemporaryDirectory(prefix="gorph-del-") as td:
        repo, base_sha = build_repo(td, ["a.py", "gone.py"],
                                    CORE_SOURCES + ["a.py", "gone.py"])
        (repo / "gone.py").unlink()
        commit_all(repo, "delete gone")

        r = run_cli(repo, ["--base", base_sha], env=pr_env(base_sha))
        check("deletion PR: orphan whose source was deleted BY this PR is tolerated",
              r.returncode == 0 and "tolerated" in r.stdout,
              (r.stdout + r.stderr).strip()[-250:])

        # The gate test itself passes on the deletion-PR tree under PR CI env —
        # exactly the shape the suite runs under on a PR checkout (the adversary's
        # without-regen repro, which used to FAIL 1 at test_graph_gate.py:34-37).
        r2 = subprocess.run([sys.executable, str(repo / "tests" / "test_graph_gate.py")],
                            capture_output=True, text=True, cwd=repo,
                            env=pr_env(base_sha))
        check("test_graph_gate passes on the deletion-PR tree (base graph, no regen)",
              r2.returncode == 0 and "FAIL every file the graph indexes" not in r2.stdout,
              (r2.stdout + r2.stderr)[-400:])

        # WITHOUT PR context the tolerance must NOT apply (main stays exact).
        r3 = run_cli(repo, ["--base", base_sha])
        check("outside PR context (main) the orphan check stays hard-red",
              r3.returncode == 1 and "gone.py" in r3.stdout,
              (r3.stdout + r3.stderr).strip()[-250:])

    # --- counterfactual 2: graph indexes a source that was NEVER in the base ----------
    with tempfile.TemporaryDirectory(prefix="gorph-fab-") as td:
        repo, base_sha = build_repo(td, ["a.py"],
                                    CORE_SOURCES + ["a.py", "never_existed.py"],
                                    absent=("never_existed.py",))
        commit_all(repo, "nothing changes yet")
        r = run_cli(repo, ["--base", base_sha], env=pr_env(base_sha))
        check("fabricated orphan (never in base) stays a HARD failure even in PR context",
              r.returncode == 1 and "never_existed.py" in r.stdout,
              (r.stdout + r.stderr).strip()[-250:])
        r2 = subprocess.run([sys.executable, str(repo / "tests" / "test_graph_gate.py")],
                            capture_output=True, text=True, cwd=repo,
                            env=pr_env(base_sha))
        check("test_graph_gate still FAILS the fabricated-orphan tree in PR context",
              r2.returncode == 1 and "never_existed.py" in r2.stdout,
              (r2.stdout + r2.stderr)[-400:])

    # --- counterfactual 3: unresolvable base fails CLOSED ------------------------------
    with tempfile.TemporaryDirectory(prefix="gorph-uc-") as td:
        repo, base_sha = build_repo(td, ["a.py", "gone.py"],
                                    CORE_SOURCES + ["a.py", "gone.py"])
        (repo / "gone.py").unlink()
        commit_all(repo, "delete gone")
        bad_env = {**os.environ, "GITHUB_HEAD_REF": "fix/delete",
                   "GITHUB_EVENT_NAME": "pull_request",
                   "GITHUB_EVENT_PATH": str(Path(td) / "no-such-event.json")}
        r = run_cli(repo, ["--base", "0" * 40], env=bad_env)
        check("unresolvable base fails CLOSED (orphan reported, nothing tolerated)",
              r.returncode == 1 and "gone.py" in r.stdout,
              (r.stdout + r.stderr).strip()[-250:])

    # --- pure decision unit (graph_path_ban_153 idiom: semantics without git) ----------
    if hasattr(go, "orphan_decision"):
        in_base = {"was_here.py"}
        d = go.orphan_decision({"was_here.py", "never_existed.py"}, in_base.__contains__)
        check("orphan_decision splits tolerated vs missing exactly",
              set(d["tolerated"]) == {"was_here.py"} and set(d["missing"]) == {"never_existed.py"},
              str(d))
        d2 = go.orphan_decision({"x.py"}, None)  # base unresolvable
        check("orphan_decision with no base reports every orphan (fail-closed)",
              set(d2["missing"]) == {"x.py"} and not d2["tolerated"], str(d2))
        d3 = go.orphan_decision(set(), None)
        check("orphan_decision on a clean graph is clean",
              not d3["missing"] and not d3["tolerated"], str(d3))
    else:
        check("graph_orphans exposes the pure orphan_decision", False, "attribute missing")

# --- exact-head freshness stays RED (graph_check UNTOUCHED) ---------------------
if shutil.which("graphify"):
    env_g = {**os.environ, "GRAPHIFY_NO_LLM": "1"}
    with tempfile.TemporaryDirectory(prefix="gorph-stale-") as td:
        repo = Path(td) / "repo"
        (repo / "scripts").mkdir(parents=True)
        (repo / "scripts" / "graph_check.py").write_text(
            (ROOT / "scripts" / "graph_check.py").read_text())
        (repo / "a.py").write_text("def alpha():\n    return beta()\n\ndef beta():\n    return 1\n")
        (repo / ".gitignore").write_text("graphify-out/graph.html\ngraphify-out/cache/\n")
        git(repo, "init", "-q")
        commit_all(repo, "init")
        subprocess.run(["graphify", "update", str(repo), "--force"],
                       capture_output=True, env=env_g)
        (repo / "a.py").write_text("def alpha():\n    return beta()\n\ndef beta():\n    return gamma()\n\ndef gamma():\n    return 2\n")
        r = subprocess.run([sys.executable, "scripts/graph_check.py"], cwd=repo,
                           capture_output=True, text=True, env=env_g)
        check("edited source, old graph → STALE exit 1 naming the new symbol (unchanged)",
              r.returncode == 1 and "STALE" in r.stdout and "gamma" in r.stdout,
              r.stdout.strip()[-200:])
else:
    print("SKIP exact-head STALE case (graphify CLI absent; test_graph_gate fails closed on it)")

print("ALL PASS" if not failures else f"FAIL {failures}")
sys.exit(1 if failures else 0)
