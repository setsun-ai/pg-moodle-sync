#!/usr/bin/env bash
# moodle-sync: sync once now (macOS / Linux).  Usage: ./sync.sh
cd "$(dirname "$0")"
PY=.venv/bin/python
[ -x "$PY" ] || PY=python3
exec "$PY" -m moodle_sync run "$@"
