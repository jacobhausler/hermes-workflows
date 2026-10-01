"""Pin test door writers to WF_RUNS_ROOT even if owner settings specify a root.

The door's owner settings override the environment by design. Tests need both
paths resolved to their scratch directory, without changing production precedence.
"""
import os


def install(door):
    inner = door._owner_setting_read
    def pinned(key):
        if key == "runs_root" and os.environ.get("WF_RUNS_ROOT"):
            return os.environ["WF_RUNS_ROOT"]
        return inner(key)
    door._common.set_owner_setting_reader(pinned)
    return pinned
