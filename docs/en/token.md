# The Moodle token

🇵🇱 [Wersja polska](../pl/token.md) · [← README](../../README.md)

## What it is

moodle-sync talks to Moodle through its official **Web Service API**, the same one the official **Moodle mobile app** uses. To do that it needs a **token**: a long random string that works like a password to **your** account, limited to what the mobile app can do.

- The token is stored only in the `.env` file on your computer. It is never uploaded anywhere and never printed in logs.
- moodle-sync only **reads** your data. It never submits, posts or changes anything in Moodle.
- **Treat the token like a password.** Anyone who has it can act as you in Moodle (including submitting assignments and posting in forums).

## Getting it: the easy way

Run `python -m moodle_sync setup` (or `python -m moodle_sync token` to only renew the token). The wizard asks your Moodle how you log in and picks the method.

### A) Normal login form (username + password)

The wizard asks for your username and password and exchanges them for a token at `<moodle>/login/token.php`, Moodle's standard endpoint. The password goes only to your Moodle over HTTPS, once, and is not saved.

### B) Login through the browser (SSO: CAS, university login, Microsoft, Google...)

Here Moodle never sees your password, so the token has to come through the browser, exactly like with the mobile app:

1. The wizard opens a link like
   `https://<your-moodle>/admin/tool/mobile/launch.php?service=moodle_mobile_app&passport=...&urlscheme=moodlemobile`
2. Log in as usual. Moodle then tries to send the token to the Moodle app with a `moodlemobile://token=...` link. Your browser can't open it: the page seems to "do nothing" or asks whether to open an app. Cancel that dialog.
3. Get the link:
   - **Chrome / Edge:** press **F12** and open the **Console** tab. There's an error like
     `Failed to launch 'moodlemobile://token=ZmY1...' because the scheme does not have a registered handler.`
     Copy the text from `moodlemobile://` up to the closing quote.
   - **Firefox:** press **F12** and open the **Network** tab. Reload the login page if needed. The last request (`launch.php`) has a `Location: moodlemobile://token=...` response header.
4. Paste it into the wizard. It decodes the token and checks it immediately.

> If nothing shows up in the Console, open DevTools *before* logging in (F12, then open the link again).

### C) You already have a token

Choose "I already have a token" and paste it.

## When the token stops working

You'll get an error notification ("The Moodle token expired...") or see `invalidtoken` in the logs. Common reasons:
- your site limits how long tokens are valid,
- you changed your password,
- you reset your keys (see below).

Fix it with `python -m moodle_sync token`. On a Raspberry Pi, also restart the bot: `sudo systemctl restart moodle-sync-bot`.

## Revoking the token (e.g. if it leaked)

In Moodle open **your profile menu → Preferences → Security keys** (`/user/managetoken.php`) and click **Reset** next to *Moodle mobile web service*. The old token stops working immediately. This also logs out your Moodle mobile app, so log in there again.

## "This site doesn't allow mobile app access"

moodle-sync can only work if the site has *mobile web services* enabled (Site administration → Mobile app). Nearly all universities have it on because students use the app. If yours doesn't, the wizard reports the site doesn't respond like Moodle with the mobile app enabled, and the only way is to ask the administrators.

## One Moodle per academic year?

Some schools start a new Moodle every year (e.g. `https://school.edu/2025` → `/2026`). Then at the start of the year run `python -m moodle_sync token`, give the new address and log in. New courses get new folders, and old files stay where they are.
