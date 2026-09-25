#!/usr/bin/env bash
# moodle-sync on an always-on Linux machine: Raspberry Pi, home server, VPS.
# Run from the project folder as a normal user (NOT with sudo):
#     bash deploy/linux/install-server.sh
# Safe to run again, e.g. after updating the code or changing the timer.
set -euo pipefail

DIR="$(cd "$(dirname "$0")/../.." && pwd)"
USER_NAME="$(id -un)"

if [ "$(id -u)" -eq 0 ]; then
    echo "Run as a normal user (the script asks for sudo itself)." >&2
    exit 1
fi
echo "==> Project: $DIR (user: $USER_NAME)"

if command -v apt-get >/dev/null; then
    echo "==> System packages + automatic security updates (unattended-upgrades)"
    sudo apt-get update -qq
    sudo apt-get install -y -qq python3-venv python3-pip curl unzip unattended-upgrades >/dev/null
    # Daily: refresh package lists and install security fixes. No automatic
    # reboots - kernel fixes apply at the next restart.
    printf 'APT::Periodic::Update-Package-Lists "1";\nAPT::Periodic::Unattended-Upgrade "1";\n' \
        | sudo tee /etc/apt/apt.conf.d/20auto-upgrades >/dev/null
fi

echo "==> Python environment (.venv)"
[ -x "$DIR/.venv/bin/python" ] || python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/pip" install -q --upgrade pip
"$DIR/.venv/bin/pip" install -q -r "$DIR/requirements.txt"

echo "==> Checking the configuration"
if [ ! -f "$DIR/.env" ]; then
    echo "   No .env - run the wizard first:  .venv/bin/python -m moodle_sync setup" >&2
    exit 1
fi
"$DIR/.venv/bin/python" -m moodle_sync doctor || echo "   (fix the ❌ items above; the timer is installed anyway)"
command -v rclone >/dev/null || echo "   note: no rclone - cloud upload will be skipped (curl https://rclone.org/install.sh | sudo bash)"

echo "==> systemd units"
for unit in moodle-sync.service moodle-sync.timer moodle-sync-bot.service; do
    sed -e "s|@DIR@|$DIR|g" -e "s|@USER@|$USER_NAME|g" "$DIR/deploy/linux/$unit" \
        | sudo tee "/etc/systemd/system/$unit" >/dev/null
done
sudo systemctl daemon-reload
sudo systemctl enable --now moodle-sync.timer

if grep -q '^TELEGRAM_CHAT_ID=.' "$DIR/.env"; then
    echo "==> Telegram bot"
    sudo systemctl enable moodle-sync-bot.service
    sudo systemctl restart moodle-sync-bot.service   # restart = load new code and .env
else
    echo "   (Telegram bot not enabled - no TELEGRAM_CHAT_ID in .env)"
    sudo systemctl disable --now moodle-sync-bot.service 2>/dev/null || true
fi

echo
systemctl list-timers moodle-sync.timer --no-pager
echo
echo "Run now:       sudo systemctl start moodle-sync"
echo "Logs:          journalctl -u moodle-sync -f"
echo "Bot logs:      journalctl -u moodle-sync-bot -f"
