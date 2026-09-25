# Running: manually, automatically, or 24/7

🇵🇱 [Wersja polska](../pl/running.md) · [← README](../../README.md)

| Option | Good for | Runs when |
|---|---|---|
| [Manually](#manually) | trying it out, occasional use | you double-click it |
| [Automatically on your computer](#automatically-on-your-computer) | a laptop/PC you use every day | every 30 min while you're logged in |
| [24/7 on a Raspberry Pi / server](raspberry-pi.md) | "set and forget", Telegram commands at any time | every 15 min, day and night |

All options use the same files, so you can start manually and switch later. **Never run two machines at the same time with the same setup**: see [Moving to another machine](#moving-to-another-machine).

## Manually

| System | How |
|---|---|
| Windows | double-click **`sync.bat`** |
| macOS / Linux | `./sync.sh` in the project folder |
| any | `python -m moodle_sync run` |

A run takes a few seconds when nothing is new. The first run downloads everything, which can take a while.

## Automatically on your computer

The sync runs in the background every 30 minutes while you're logged in, plus right after you log in. A run missed while the computer was asleep starts when it wakes up. Output goes to `logs/sync.log`.

### Windows (Task Scheduler)

Double-click **`deploy\windows\schedule.bat`**, or in PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1              # every 30 min
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Minutes 60  # every hour
powershell -ExecutionPolicy Bypass -File deploy\windows\schedule.ps1 -Remove      # turn off
```

- It runs **hidden** (`pythonw.exe`), so no window pops up every half hour.
- No administrator rights or password are needed, because it runs as you while you're logged in.
- You can see it in *Task Scheduler → moodle-sync*.

### macOS

```bash
bash deploy/macos/schedule.sh           # every 30 min
bash deploy/macos/schedule.sh 60        # every hour
bash deploy/macos/schedule.sh --remove  # turn off
```

> **Privacy protection:** macOS blocks background jobs from reading *Documents*, *Desktop*, *Downloads* and iCloud Drive unless you grant "Full Disk Access".
> - Keep the project in your home folder, e.g. `~/moodle-sync`.
> - If `DOWNLOAD_DIR` points into one of those folders, either move it or grant Full Disk Access to `.venv/bin/python` (*System Settings → Privacy & Security → Full Disk Access*).

### Linux (desktop)

```bash
bash deploy/linux/schedule-user.sh           # every 30 min, systemd user timer
bash deploy/linux/schedule-user.sh --remove
```

Logs: `journalctl --user -u moodle-sync`. To keep it running while you're logged out, run `sudo loginctl enable-linger $USER`.

## How often?

- **15-30 min** is plenty. Teachers don't upload that often, and each run makes a few dozen requests to your university's server.
- **Don't go below 15 minutes.** Announcements are checked at most every 30 min and grades every hour anyway.

## Moving to another machine

1. Stop the old one: remove the scheduler with `-Remove` / `--remove`, and stop the bot.
2. Copy these files to the new machine:
   - `.env`, `state.json`, `courses.json` / `przedmioty.json`,
   - `google_token.json` (if you use the calendar),
   - `~/.config/rclone/rclone.conf` or `%APPDATA%\rclone\rclone.conf` (if you use rclone).
3. You don't need to copy `downloads/`. `state.json` knows what was already downloaded (and uploaded).

Two machines with the same setup would both download the same files and send the same notifications. Two Telegram bots with the same token fight over messages (`409 Conflict`).

## Why not "in the cloud" (GitHub Actions, free hosting...)?

It sounds attractive: no hardware at all. We deliberately don't recommend it:
- **Your university password-equivalent in someone else's cloud.** The Moodle token would sit in a third-party service, and a leaked log or a misconfigured public fork would expose it.
- **State between runs:** scheduled CI jobs are stateless, so remembering what was downloaded means workarounds (caches, commits) that are easy to get wrong.
- **Reliability:** scheduled GitHub workflows get delayed at busy times and are automatically disabled after 60 days without activity in public repositories. Some universities also block datacenter IPs.

A laptop with the Task Scheduler, or a €40 Raspberry Pi, avoids all of that.
