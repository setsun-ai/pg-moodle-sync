#!/usr/bin/env bash
# moodle-sync: automatic sync on a Linux desktop/laptop (systemd user timer).
# Runs while you're logged in; for a 24/7 Raspberry Pi / server use install-server.sh.
#   bash deploy/linux/schedule-user.sh          # every 30 min
#   bash deploy/linux/schedule-user.sh 60
#   bash deploy/linux/schedule-user.sh --remove
set -euo pipefail
DIR="$(cd "$(dirname "$0")/../.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"

if [ "${1:-}" = "--remove" ]; then
    systemctl --user disable --now moodle-sync.timer 2>/dev/null || true
    rm -f "$UNIT_DIR/moodle-sync.service" "$UNIT_DIR/moodle-sync.timer"
    systemctl --user daemon-reload
    echo "[PL] Wyłączono. / [EN] Turned off."
    exit 0
fi

MINUTES="${1:-30}"
[ -x "$DIR/.venv/bin/python" ] || { echo "[PL] Najpierw: bash install.sh / [EN] First run: bash install.sh"; exit 1; }
mkdir -p "$UNIT_DIR"
cat > "$UNIT_DIR/moodle-sync.service" <<UNIT
[Unit]
Description=moodle-sync (one run)
Wants=network-online.target
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=$DIR
ExecStart=$DIR/.venv/bin/python -m moodle_sync run
Nice=10
UNIT
cat > "$UNIT_DIR/moodle-sync.timer" <<UNIT
[Unit]
Description=moodle-sync every $MINUTES min

[Timer]
OnStartupSec=3min
OnUnitInactiveSec=${MINUTES}min
Persistent=true

[Install]
WantedBy=timers.target
UNIT
systemctl --user daemon-reload
systemctl --user enable --now moodle-sync.timer
echo "[PL] Gotowe: co $MINUTES min, gdy jesteś zalogowany. Logi: journalctl --user -u moodle-sync"
echo "[EN] Done: every $MINUTES min while you're logged in. Logs: journalctl --user -u moodle-sync"
echo "     (24/7 bez logowania / without being logged in: sudo loginctl enable-linger $USER)"
