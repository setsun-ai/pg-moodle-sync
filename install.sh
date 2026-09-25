#!/usr/bin/env bash
# moodle-sync - installation on macOS / Linux (incl. Raspberry Pi).
# Usage:  bash install.sh
# Creates .venv, installs the libraries and starts the setup wizard.
set -euo pipefail
cd "$(dirname "$0")"

PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null && "$candidate" -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
        PY="$candidate"; break
    fi
done
if [ -z "$PY" ]; then
    echo "[PL] Brak Pythona 3.10+. macOS: brew install python   Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3"
    echo "[EN] Python 3.10+ not found. macOS: brew install python   Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3"
    exit 1
fi

if [ ! -x .venv/bin/python ]; then
    echo "Creating .venv ..."
    if ! "$PY" -m venv .venv; then
        echo "[PL] Nie udało się utworzyć .venv. Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3-venv"
        echo "[EN] Couldn't create .venv. Debian/Ubuntu/Raspberry Pi OS: sudo apt install python3-venv"
        exit 1
    fi
fi
echo "Installing libraries ..."
.venv/bin/python -m pip install --upgrade pip -q
.venv/bin/python -m pip install -r requirements.txt -q

.venv/bin/python -m moodle_sync setup
