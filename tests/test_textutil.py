from moodle_sync.textutil import (
    MAX_COMPONENT_BYTES,
    clean_text,
    normalize_for_matching,
    pick_language,
    sanitize_component,
)


class TestPickLanguage:
    def test_mlang2_syntax_picks_requested_language(self):
        text = "{mlang pl}Lipidomika{mlang}{mlang en}Lipidomics{mlang}"
        assert pick_language(text, "pl") == "Lipidomika"
        assert pick_language(text, "en") == "Lipidomics"

    def test_falls_back_to_first_variant(self):
        assert pick_language("{mlang de}Vorlesung{mlang}", "pl") == "Vorlesung"

    def test_span_syntax(self):
        text = '<span lang="en" class="multilang">Lecture</span><span lang="pl" class="multilang">Wykład</span>'
        assert pick_language(text, "pl") == "Wykład"

    def test_plain_text_untouched_but_tags_removed(self):
        assert pick_language("Plain <b>name</b>", "en") == "Plain name"


class TestCleanText:
    def test_html_table_becomes_one_line_per_row(self):
        html = "<table>\n<tr>\n<td>ID</td>\n<td>Grade</td>\n</tr>\n<tr><td>123</td><td> </td><td>5</td></tr></table>"
        assert clean_text(html) == "ID | Grade\n123 | 5"

    def test_html_newlines_in_source_are_ignored(self):
        assert clean_text("<p>one\ntwo</p><p>three</p>") == "one two\nthree"

    def test_plain_text_keeps_paragraphs(self):
        assert clean_text("line\nnext\n\n\n\nparagraph") == "line\nnext\n\nparagraph"

    def test_entities_are_decoded(self):
        assert clean_text("R&amp;D&nbsp;lab") == "R&D lab"


class TestSanitizeComponent:
    def test_windows_forbidden_characters(self):
        assert sanitize_component('Lecture 1: Intro?.pdf') == "Lecture 1_ Intro_.pdf"

    def test_reserved_windows_names(self):
        assert sanitize_component("CON.txt") == "_CON.txt"
        assert sanitize_component("nul") == "_nul"

    def test_cannot_escape_directory(self):
        assert sanitize_component("..") == "_"
        assert sanitize_component(".") == "_"

    def test_trailing_dots_and_spaces_removed(self):
        assert sanitize_component(" name. ") == "name"

    def test_truncates_by_utf8_bytes_and_keeps_extension(self):
        result = sanitize_component("ż" * 200 + ".pptx")
        assert result.endswith(".pptx")
        assert len(result.encode("utf-8")) <= MAX_COMPONENT_BYTES

    def test_nfd_is_normalized_to_nfc(self):
        assert sanitize_component("ták.pdf") == "ták.pdf"

    def test_multilang_and_newlines(self):
        assert sanitize_component("{mlang en}Data{mlang}\nsets", lang="en") == "Data sets"


def test_normalize_for_matching_removes_diacritics():
    assert normalize_for_matching("WYKŁADY i Ćwiczenia") == "wyklady i cwiczenia"
