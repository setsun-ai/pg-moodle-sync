"""
state.json - the program's memory between runs.

Keys (all optional; missing ones are created on demand):
    downloaded     file id -> {"path", "key", "ts", "skipped"?}
    remote_moves   pending moves on the cloud drive after re-categorisation
    calendar       Google calendar ids + synced events (fingerprints)
    watch          seen forum discussions, known grades
    alerts         last error notification per step (to avoid spamming)
    last_run       result of the last run (for /status)
    weekly         when the weekly summary was last sent

Deleting state.json is safe (see docs: troubleshooting) - everything is
idempotent - it just makes the next run re-download and re-check everything.
"""

import json
import os
import time

from . import config


def load() -> dict:
    if config.STATE_FILE.exists():
        return json.loads(config.STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save(state: dict) -> None:
    # Write to a temp file and atomically swap it in: the Telegram bot may read
    # state.json at any moment, and a power cut on a Raspberry Pi mid-write
    # must not leave a half-written (corrupted) file behind.
    path = config.STATE_FILE
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:  # Windows: file briefly opened by another process
            time.sleep(0.2 * (attempt + 1))
    os.replace(tmp, path)
