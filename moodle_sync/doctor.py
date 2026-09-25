"""
python -m moodle_sync doctor - checks the whole setup and says what to fix.

✅ works   ⏭ optional and not configured   ❌ problem (with a hint)
"""

import shutil
import sys

from . import calendar_sync, config, moodle, notify, storage
from .i18n import t

# Functions the tool needs from the token; missing ones disable a feature.
REQUIRED_FUNCTIONS = {
    "core_enrol_get_users_courses": "doc_fn_courses",
    "core_course_get_contents": "doc_fn_files",
    "core_calendar_get_calendar_events": "doc_fn_calendar",
    "mod_forum_get_forum_discussions": "doc_fn_forums",
    "mod_assign_get_submission_status": "doc_fn_grades",
}


def run() -> int:
    problems = 0

    def ok(text):
        print(f"✅ {text}")

    def skip(text):
        print(f"⏭  {text}")

    def bad(text):
        nonlocal problems
        problems += 1
        print(f"❌ {text}")

    print(t("doc_header") + "\n")

    # (Older Pythons can't even import this code - install.bat/install.sh check the version.)
    ok(f"Python {sys.version.split()[0]}")

    if not config.ENV_FILE.exists():
        bad(t("doc_no_env"))
        return 1

    url = config.moodle_base_url()
    if not url:
        bad(t("doc_no_url"))
    else:
        try:
            public = moodle.public_config(url)
            ok(t("doc_site_ok", name=public.get("sitename", "?"), url=url))
        except Exception as e:
            bad(t("doc_site_failed", url=url, error=e))

    info = None
    try:
        info = moodle.site_info()
        ok(t("doc_token_ok", name=info.get("fullname"), release=info.get("release", "?")))
    except Exception as e:
        bad(t("doc_token_failed", error=moodle.redact(str(e))))

    if info:
        allowed = {f["name"] for f in info.get("functions", [])}
        for fn, key in REQUIRED_FUNCTIONS.items():
            if fn not in allowed:
                bad(t("doc_fn_missing", fn=fn, feature=t(key)))
        try:
            ok(t("doc_courses", n=len(moodle.my_courses())))
        except Exception as e:
            bad(str(e))

    folder = config.download_dir()
    try:
        folder.mkdir(parents=True, exist_ok=True)
        free = shutil.disk_usage(folder).free / 1e9
        (ok if free > 1 else bad)(t("doc_folder", dir=folder, free=free))
    except OSError as e:
        bad(t("doc_folder_failed", dir=folder, error=e))

    usable, reason = storage.status()
    (ok if usable else skip)(t("doc_storage", status=reason))

    usable, reason = calendar_sync.status()
    (ok if usable else skip)(t("doc_calendar", status=reason))

    channels = notify.channels()
    (ok if channels else skip)(t("doc_notify", channels=", ".join(channels) or t("doc_none")))
    (ok if config.env("HEALTHCHECK_URL") else skip)(t("doc_healthcheck"))

    courses_file = config.courses_file()
    if courses_file.exists():
        try:
            config.load_courses_config()
            ok(t("doc_courses_file", file=courses_file.name))
        except ValueError as e:
            bad(t("doc_courses_file_bad", file=courses_file.name, error=e))

    print("\n" + (t("doc_all_ok") if not problems else t("doc_problems", n=problems)))
    return 1 if problems else 0
