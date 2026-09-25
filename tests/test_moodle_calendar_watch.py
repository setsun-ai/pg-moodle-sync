import base64

from moodle_sync import calendar_sync, moodle, watch


class TestMoodle:
    def test_decode_sso_token_from_full_url(self):
        encoded = base64.b64encode(b"abc123signature:::THE_TOKEN:::private").decode().rstrip("=")
        assert moodle.decode_sso_token(f"moodlemobile://token={encoded}") == "THE_TOKEN"
        assert moodle.decode_sso_token(encoded) == "THE_TOKEN"

    def test_file_url_gets_token_and_webservice_path(self):
        url = moodle.file_url_with_token("https://m.example/pluginfile.php/5/a%20b.pdf?forcedownload=1&token=old", "T")
        assert url == "https://m.example/webservice/pluginfile.php/5/a%20b.pdf?forcedownload=1&token=T"

    def test_redact_hides_the_token(self, monkeypatch):
        monkeypatch.setenv("MOODLE_TOKEN", "secret123")
        assert moodle.redact("GET https://x/?token=secret123 failed") == "GET https://x/?token=*** failed"

    def test_skip_courses(self):
        assert moodle.course_skipped({"fullname": "Library Training 2025"}, {"skip": ["library training"]})
        assert not moodle.course_skipped({"fullname": "Algorithms"}, {"skip": ["library"]})


class TestCalendar:
    event = {"id": 7, "name": "Report 1 is due", "eventtype": "due", "modulename": "assign",
             "timestart": 1_800_000_000, "timeduration": 0, "courseid": None, "description": ""}

    def test_is_done_uses_open_action_events(self):
        assert calendar_sync.is_done(self.event, open_ids={7}) is False
        assert calendar_sync.is_done(self.event, open_ids=set()) is True
        assert calendar_sync.is_done(self.event, open_ids=None) is None
        assert calendar_sync.is_done({**self.event, "eventtype": "course"}, open_ids=set()) is None

    def test_done_event_has_check_mark_and_no_reminders(self):
        cal, body = calendar_sync.build_event(self.event, {}, done=True, cfg={})
        assert cal == "deadlines" and body["summary"].startswith("✅")
        assert body["reminders"]["overrides"] == []
        _, open_body = calendar_sync.build_event(self.event, {}, done=False, cfg={})
        assert open_body["summary"].startswith("⏰") and open_body["reminders"]["overrides"]
        assert calendar_sync.fingerprint(cal, body) != calendar_sync.fingerprint(cal, open_body)

    def test_attendance_goes_to_classes_calendar(self):
        cal, body = calendar_sync.build_event({**self.event, "eventtype": "attendance", "timeduration": 5400}, {},
                                              cfg={})
        assert cal == "classes" and body["transparency"] == "opaque"
        assert body["end"]["dateTime"] != body["start"]["dateTime"]

    def test_calendar_names_follow_language(self, monkeypatch):
        monkeypatch.setenv("SITE_LABEL", "PG")
        monkeypatch.setenv("LANGUAGE", "pl")
        assert calendar_sync.calendar_names() == {"deadlines": "PG – terminy", "classes": "PG – zajęcia"}


class TestWatch:
    def test_plain_grade(self):
        assert watch.plain_grade("90,00&nbsp;/&nbsp;100,00") == "90 / 100"
        assert watch.plain_grade("<b>4.50</b> / 5.00") == "4.50 / 5"

    def test_newly_watched_forum_is_remembered_silently(self, monkeypatch):
        """Regression: enabling WATCH_ALL_FORUMS must not report old posts as new."""
        forums = [{"id": 1, "type": "news", "name": "Announcements", "course": 10},
                  {"id": 2, "type": "general", "name": "Group 4 discussion", "course": 10}]
        discussions = {1: [{"discussion": 11, "created": 1}], 2: [{"discussion": 21, "created": 1}]}

        def fake_call(fn, **kw):
            if fn == "mod_forum_get_forums_by_courses":
                return forums
            return {"discussions": discussions[kw["forumid"]]}

        monkeypatch.setattr(moodle, "call", fake_call)
        sent = []
        monkeypatch.setattr(watch, "notify", lambda *a, **k: sent.append(a))
        section: dict = {}
        watch.check_forums([{"id": 10}], {}, section, {}, dry_run=False)          # first run: baseline
        monkeypatch.setenv("WATCH_ALL_FORUMS", "1")
        assert watch.check_forums([{"id": 10}], {}, section, {}, dry_run=False) == 0  # forum 2 now watched
        discussions[2].append({"discussion": 22, "created": 2, "subject": "New post", "message": "hi"})
        assert watch.check_forums([{"id": 10}], {}, section, {}, dry_run=False) == 1  # a genuinely new post
        assert len(sent) == 1
