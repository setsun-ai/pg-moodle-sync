# Changelog

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
