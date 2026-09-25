#!/usr/bin/env bash
# moodle-sync: automatic sync on macOS (launchd) while you're logged in.
#   bash deploy/macos/schedule.sh          # every 30 min
#   bash deploy/macos/schedule.sh 60       # every 60 min
#   bash deploy/macos/schedule.sh --remove # turn off
#
# NOTE (macOS privacy): background jobs can't read ~/Documents, ~/Desktop or
# ~/Downloads without "Full Disk Access". Keep the project (and DOWNLOAD_DIR)
# elsewhere, e.g. ~/moodle-sync - see docs/*/running.md.
set -euo pipefail
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LABEL="io.github.moodle-sync"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
DOMAIN="gui/$(id -u)"

if [ "${1:-}" = "--remove" ]; then
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"
    echo "[PL] Wyłączono automatyczną synchronizację. / [EN] Automatic sync turned off."
    exit 0
fi

MINUTES="${1:-30}"
PY="$DIR/.venv/bin/python"
[ -x "$PY" ] || { echo "[PL] Najpierw: bash install.sh / [EN] First run: bash install.sh"; exit 1; }
case "$DIR" in
    "$HOME/Documents"*|"$HOME/Desktop"*|"$HOME/Downloads"*)
        echo "[PL] UWAGA: projekt jest w $DIR - launchd może nie mieć tam dostępu (przenieś np. do ~/moodle-sync)."
        echo "[EN] WARNING: the project is in $DIR - launchd may be denied access (move it e.g. to ~/moodle-sync).";;
esac
mkdir -p "$HOME/Library/LaunchAgents" "$DIR/logs"

cat > "$PLIST" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>$LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PY</string><string>-m</string><string>moodle_sync</string>
        <string>run</string><string>--log-file</string><string>$DIR/logs/sync.log</string>
    </array>
    <key>WorkingDirectory</key><string>$DIR</string>
    <key>StartInterval</key><integer>$((MINUTES * 60))</integer>
    <key>RunAtLoad</key><true/>
    <key>ProcessType</key><string>Background</string>
</dict>
</plist>
PLIST

launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
launchctl bootstrap "$DOMAIN" "$PLIST"
echo "[PL] Gotowe: synchronizacja co $MINUTES min. Log: $DIR/logs/sync.log"
echo "[EN] Done: sync every $MINUTES min. Log: $DIR/logs/sync.log"
