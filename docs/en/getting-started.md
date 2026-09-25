# Getting started

🇵🇱 [Wersja polska](../pl/getting-started.md) · [← README](../../README.md)

This takes about **10 minutes**. You need a computer (Windows, macOS or Linux) and your Moodle login. No programming knowledge needed.

## 1. Install Python (3.10 or newer)

| System | How |
|---|---|
| **Windows** | Open PowerShell and run `winget install Python.Python.3.12`, or download it from [python.org](https://www.python.org/downloads/) and **tick "Add python.exe to PATH"** in the installer. |
| **macOS** | `brew install python` ([Homebrew](https://brew.sh)), or the installer from [python.org](https://www.python.org/downloads/). |
| **Linux / Raspberry Pi** | Usually already there. Check: `python3 --version`. On Debian, Ubuntu or Raspberry Pi OS also run `sudo apt install python3-venv`. |

## 2. Download moodle-sync

- **Easiest:** on the GitHub page click **Code → Download ZIP** and unpack it, e.g. to `C:\moodle-sync` or `~/moodle-sync`.
- **With git:** `git clone https://github.com/setsun-ai/pg-moodle-sync.git moodle-sync`

> **macOS:** don't put it in *Documents*, *Desktop* or *Downloads*. Background jobs can't access those folders without extra permissions ([details](running.md#macos)).

## 3. Install and run the setup wizard

> Before you start, read **[Responsible use](responsible-use.md)**. It's short, and it's about course materials, other people's data and your university's rules.

| System | How |
|---|---|
| **Windows** | Double-click **`install.bat`** |
| **macOS / Linux** | In a terminal in the project folder: `bash install.sh` |

The script creates a private Python environment (`.venv`), installs the libraries and starts the **setup wizard**:

1. **Moodle address.** Paste any page of your Moodle, e.g. `https://moodle.example.edu/my/`. The wizard checks how your school logs users in.
2. **Token (access to your account).**
   - Normal login form: type your username and password. They are sent only to your Moodle, once, and never stored.
   - Login through the university, Microsoft or Google (SSO): the wizard opens the browser and shows exactly what to copy. See [Token](token.md) for help.
3. **Name and folder.** A short name of your school (used in calendar names) and where to save files.
   Tip: pick a folder inside your **Google Drive / OneDrive / Dropbox** desktop folder, and the files reach the cloud with no further setup.
4. **Notifications** (optional): Telegram, Discord, ntfy or e-mail. A test message is sent at the end. See [Notifications](notifications.md).
5. **Cloud storage** (optional): only needed for rclone (e.g. on a Raspberry Pi). See [Storage](storage.md).
6. **Google Calendar** (optional): see [Google Calendar](google-calendar.md).
7. **First sync:** download everything now, or just remember what's there and only fetch new things from now on.

You can run the wizard again any time. It keeps your current values as defaults:

```
.venv\Scripts\python -m moodle_sync setup      (Windows)
.venv/bin/python -m moodle_sync setup          (macOS / Linux)
```

## 4. Check everything

```
python -m moodle_sync doctor
```

Each line shows one check:
- ✅ works,
- ⏭ optional and not set up,
- ❌ a problem, with a hint on how to fix it.

> In all commands, `python` means the Python from the project environment:
> `.venv\Scripts\python` on Windows, `.venv/bin/python` on macOS/Linux.
> You can also activate the environment once per terminal (`.venv\Scripts\activate` / `source .venv/bin/activate`) and then just type `python`.

## 5. Decide how it should run

| You have... | Do this | Guide |
|---|---|---|
| a laptop, sync when you want | double-click `sync.bat` / run `./sync.sh` | [Running](running.md#manually) |
| a computer that's on during the day | automatic sync every 30 min while you're logged in | [Running](running.md#automatically-on-your-computer) |
| a Raspberry Pi / home server | 24/7 sync every 15 min + Telegram bot | [Raspberry Pi](raspberry-pi.md) |

## All commands

| Command | What it does |
|---|---|
| `setup` | Interactive setup wizard. |
| `doctor` | Check the configuration. |
| `run` | One full sync: files → cloud → calendar → announcements and grades. |
| `token` | Get a new Moodle token (when the old one expired). |
| `download [--dry-run] [--limit N] [--baseline]` | Only download new files. `--dry-run` shows the plan without doing anything. |
| `upload [--dry-run] [--check]` | Only upload to the cloud (rclone). |
| `calendar [--dry-run] [--auth]` | Only sync Google Calendar. `--auth` = one-time Google login. |
| `watch [--dry-run] [--force]` | Only check announcements and grades. |
| `courses` | Preview how files of each course will be categorised. |
| `ics` | Print your calendar subscription URL (Outlook / Apple Calendar). |
| `bot [--setup]` | Run the Telegram bot / connect it to your chat. |
| `notify-test` | Send a test notification to every configured channel. |
