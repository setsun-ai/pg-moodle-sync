# Deadlines in your calendar

🇵🇱 [Wersja polska](../pl/google-calendar.md) · [← README](../../README.md)

Two ways to do it:

| | **Google Calendar (sync)** | **Subscription URL (any calendar)** |
|---|---|---|
| Setup | ~10 min, once | 1 min |
| Works with | Google Calendar | Google, Outlook, Apple, Thunderbird... |
| Updates | every run (15-30 min) | when the calendar app refreshes (Google: up to ~24 h) |
| ✅ for submitted work, own reminders, separate calendar for classes | ✅ | – |
| Notification when a deadline moves | ✅ | – |

## Option 1: subscription URL (no setup)

```
python -m moodle_sync ics
```

This prints your private Moodle calendar URL. Add it to your calendar app:
- **Google:** *Other calendars → + → From URL*
- **Outlook:** *Add calendar → Subscribe from web*
- **Apple:** *File → New Calendar Subscription*

The URL contains a secret key, so don't share it.

## Option 2: Google Calendar sync

### What you get

Two new calendars:

| Calendar | What's in it |
|---|---|
| **"<SITE_LABEL> – deadlines"** | Assignment due dates, quiz opening/closing, events added by teachers. Reminders 1 day and 2 hours before. |
| **"<SITE_LABEL> – classes"** | Attendance sessions, i.e. in practice your timetable, without reminders. Hide it with one click next to its name, or turn it off with `SYNC_CLASSES=0`. |

- A **submitted** assignment or **finished** quiz gets **✅** and loses its reminders.
- A deadline **moved** by the teacher is updated, and you get a notification.
- An event deleted in Moodle disappears from the calendar too.
- moodle-sync can **only** see the calendars it created (scope `calendar.app.created`), not your personal calendar.

> Dates written only in text (an announcement, a PDF) aren't calendar events. The [announcement notifications](notifications.md) cover those.

### 1. Google Cloud project (once, ~10 min)

Go to <https://console.cloud.google.com> and log in with the Google account whose calendar you want to use.

1. **Project:** click the project list at the top → **New project** → name it `moodle-sync` → **Create**. Make sure it's selected.
2. **APIs:** ☰ → **APIs & Services → Library** → search **Google Calendar API** → **Enable**. If you'll use rclone with Google Drive, enable **Google Drive API** too.
3. **Consent screen:** ☰ → **APIs & Services → OAuth consent screen**, called *Google Auth Platform* in the new console. Click **Get started**:
   - app name `moodle-sync` and your e-mail,
   - **Audience: External**,
   - contact e-mail, accept, **Create**.
4. **⚠️ Publish the app:** under **Audience** click **Publish app** so that the status is **In production**.

> In *Testing* status Google invalidates your login after **7 days**, and the sync would silently stop after a week. Verification by Google is **not** needed. When logging in you'll see "Google hasn't verified this app": click **Advanced → Go to moodle-sync**. It's your own app.

5. **Client:** **Google Auth Platform → Clients → Create client** → type **Desktop app** → **Create** → **Download JSON**. Save it in the project folder as **`client_secret.json`**.

### 2. Log in

```
python -m moodle_sync calendar --auth
```

A browser opens. After you log in, `google_token.json` is saved. It's a password-equivalent, so don't share it. `client_secret.json` is only needed for this step.

### 3. Test

```
python -m moodle_sync calendar --dry-run     # what would be added
python -m moodle_sync calendar               # do it
```

After that it runs as part of every `python -m moodle_sync run`.

### Customising

At the top of `moodle_sync/calendar_sync.py`:
- `REMINDERS` / `DEFAULT_REMINDERS`: minutes before the event,
- `PAST_DAYS` / `FUTURE_DAYS`: the sync window.

Calendar names come from `SITE_LABEL` and `LANGUAGE`. Change them before the first sync; afterwards, rename the calendars in Google directly.

On a Raspberry Pi, just copy `google_token.json`. No browser is needed there.
