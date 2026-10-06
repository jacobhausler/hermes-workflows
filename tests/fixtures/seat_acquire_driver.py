#!/usr/bin/env python3
"""est-g2xx seat-semaphore driver fixture.

Usage: seat_acquire_driver.py <seats_dir> <name> <hold_s> <cap> [bounded_s]

Acquires a global agent seat through wf._seat_acquire (the SAME entry the
runner's spawn seam uses), holds it hold_s seconds, releases, and prints one
JSON row to stdout:
  {"ok": true, "name", "acquired_after", "released_at", "waited_s"}
or on bounded-wait expiry:
  {"ok": false, "error_class": "seat_wait", "waited_s"}
"""
import importlib.util
import json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("hw_g2xx_driver", ROOT / "wf.py")
wf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(wf)

seats_dir, name, hold_s, cap = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
bounded = float(sys.argv[5]) if len(sys.argv) > 5 else 30.0

t0 = time.time()
got = wf._seat_acquire(Path(seats_dir), name, cap, bounded)
waited = time.time() - t0
if got is None:
    print(json.dumps({"ok": False, "name": name, "error_class": "seat_wait",
                      "waited_s": round(waited, 3)}))
    sys.exit(2)
acquired_after = time.time()
time.sleep(hold_s)
wf._seat_release(got)
print(json.dumps({"ok": True, "name": name,
                  "acquired_after": round(acquired_after, 6),
                  "released_at": round(time.time(), 6),
                  "waited_s": round(waited, 3)}))
