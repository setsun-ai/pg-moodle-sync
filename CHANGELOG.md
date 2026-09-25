# Changelog

## 1.0.1 (2026-09)

- **Safety fuse:** if a settings change would move a large part of the already downloaded archive, nothing is moved or downloaded until you confirm with `download --reorganize`. The error notification explains why. Found in real use: `LANGUAGE` was lost in a glued `.env` line, and every folder started to be renamed to English.
- `doctor` shows the effective language and folder names, and detects broken `.env` lines (glued or without `=`).
- New `set KEY VALUE` command to change `.env` safely. `.env` is always written with LF line endings.
- **Cloud moves are "netted" first.** One listing of the cloud folder, then only the moves that are really needed: already-done moves and round trips (A→B→A) cost nothing, and chains collapse. They run 3 in parallel and save progress every 20 files. Before this, an interrupted re-organisation meant hundreds of useless ~8 s rclone calls on a Raspberry Pi, and "source doesn't exist" was wrongly retried as an error.

## 1.0.0 (2026-09)

First public release: a universal tool for any Moodle.

- Python package `moodle_sync` with one CLI: `setup`, `doctor`, `run`, `token`, `download`, `upload`, `calendar`, `watch`, `courses`, `ics`, `bot`, `notify-test`.
- **Setup wizard:** detects password vs. SSO login and gets the token (incl. the `moodlemobile://` flow).
- **Files:** categories (Lectures / Exercises / Labs / Projects / Other) in Polish or English, own rules and names in `courses.json`, automatic moving after rule changes (locally and in the cloud), safe file names for Windows and Linux, size limit.
- **Cloud:** rclone (Google Drive, OneDrive, Dropbox...), or simply a folder synced by a desktop app; backup of `state.json`.
- **Calendar:** Google Calendar sync with ✅ for submitted work, a separate calendar for classes, notifications about moved deadlines; `.ics` subscription URL for other calendars.
- **Watch:** announcements and grades (with teacher feedback), throttled requests, no floods on the first run or when a new forum gets watched.
- **Notifications:** Telegram (with commands), Discord webhook, ntfy, e-mail; per-kind muting; weekly summary; healthchecks.io dead-man alarm.
- **Running:** manual launchers, Windows Task Scheduler, macOS launchd, Linux user timer, Raspberry Pi / server systemd units with automatic security updates.
- Polish and English UI and docs, tests and CI on Windows, macOS and Linux.

## 0.x

Personal scripts for Gdańsk University of Technology (eNauczanie PG), the origin of this project.
