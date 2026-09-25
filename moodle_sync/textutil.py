"""
Text helpers: Moodle multi-language names, HTML -> plain text, and safe file names.

All functions here are pure (no network, no files), which makes them easy to
unit-test - see tests/test_textutil.py.
"""

import html
import os
import re
import unicodedata

# --- multi-language names -------------------------------------------------------------
# Moodle sites often store names in two languages using one of two filter syntaxes:
#   {mlang pl}Wykład{mlang}{mlang en}Lecture{mlang}                      (filter_multilang2)
#   <span lang="pl" class="multilang">Wykład</span><span lang="en" ...>  (filter_multilang)
# The web service returns them raw, without applying the filter.
_MLANG_BLOCK = re.compile(r"\{mlang\s+([\w-]+)\s*\}(.*?)\{mlang\}", re.S | re.I)
_MLANG_SPAN = re.compile(
    r'<span[^>]*\blang="([\w-]+)"[^>]*class="multilang"[^>]*>(.*?)</span>'
    r'|<span[^>]*class="multilang"[^>]*\blang="([\w-]+)"[^>]*>(.*?)</span>',
    re.S | re.I,
)
# A "run" = consecutive variants of the same text; each run is replaced in place,
# so text around it keeps its order and several multi-language parts can coexist.
_MLANG_BLOCK_RUN = re.compile(r"(?:\{mlang\s+[\w-]+\s*\}.*?\{mlang\}\s*)+", re.S | re.I)
_MLANG_SPAN_RUN = re.compile(r'(?:<span[^>]*class="multilang"[^>]*>.*?</span>\s*)+', re.S | re.I)
_HTML_TAG = re.compile(r"<[^>]+>")


def _choose(variants: list[tuple[str, str]], lang: str) -> str:
    return next((text for code, text in variants if code.lower() == lang), variants[0][1])


def pick_language(text: str, lang: str) -> str:
    """Keep the variant in `lang` (or the first one), drop the rest and any HTML tags."""

    def replace(run: re.Match, variants: list[tuple[str, str]]) -> str:
        trailing = " " if run.group(0)[-1:].isspace() else ""
        return _choose(variants, lang) + trailing

    text = _MLANG_BLOCK_RUN.sub(lambda m: replace(m, _MLANG_BLOCK.findall(m.group(0))), text or "")
    text = _MLANG_SPAN_RUN.sub(
        lambda m: replace(m, [(a or c, b or d) for a, b, c, d in _MLANG_SPAN.findall(m.group(0))]), text)
    return _HTML_TAG.sub("", text)


def clean_text(text: str, lang: str = "en") -> str:
    """Moodle HTML (forum posts, descriptions, names) -> readable plain text."""
    text = text or ""
    if re.search(r"<(p|br|div|td|table|li|span)\b", text, flags=re.I):
        # It's HTML: newlines in the source mean nothing, only tags do.
        text = re.sub(r"\s+", " ", text)
    # Tables (e.g. grade lists in announcements): cell -> " | ", row -> line.
    text = re.sub(r"</t[dh]\s*>", " | ", text, flags=re.I)
    text = re.sub(r"<br\s*/?>|</p>|</li>|</tr>|</div>|</h\d>", "\n", text, flags=re.I)
    text = html.unescape(pick_language(text, lang)).replace("\r\n", "\n")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t\xa0]+", " ", line).strip()
        line = re.sub(r"(\s*\|\s*)+$", "", line)            # trailing separators
        line = re.sub(r"(\|\s*){2,}", "| ", line).strip()   # empty cells
        lines.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def shorten(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def normalize_for_matching(text: str, lang: str = "en") -> str:
    """'WYKŁADY i Ćwiczenia' -> 'wyklady i cwiczenia' (no diacritics, lower case)."""
    text = pick_language(html.unescape(text or ""), lang).lower().replace("ł", "l")
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


# --- safe file names -------------------------------------------------------------------

# Linux (ext4) limits a name to 255 BYTES, and Polish letters take 2 bytes in
# UTF-8. Windows without "long paths" limits the whole path to 260 characters -
# hence the margin instead of cutting at 255.
MAX_COMPONENT_BYTES = 120

# Characters forbidden in Windows file names (+ control characters). Linux only
# forbids '/' and NUL, so this is the common, safe subset.
_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f\x7f]')
_WINDOWS_RESERVED = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _truncate_utf8(name: str, max_bytes: int) -> str:
    """Cut the name to max_bytes of UTF-8, keeping the extension."""
    if len(name.encode("utf-8")) <= max_bytes:
        return name
    stem, ext = os.path.splitext(name)
    if len(ext.encode("utf-8")) > 16:  # not an extension, just a dot in the name
        stem, ext = name, ""
    budget = max_bytes - len(ext.encode("utf-8"))
    # errors="ignore" drops a multi-byte character cut in half
    stem = stem.encode("utf-8")[:budget].decode("utf-8", errors="ignore").rstrip(". ")
    return (stem or "_") + ext


def sanitize_component(name: str, fallback: str = "_", lang: str = "en") -> str:
    """
    One path component (course / folder / file name) that is valid on both
    Windows and Linux. Non-ASCII letters are kept - Google Drive, OneDrive,
    NTFS and ext4 all handle them - but normalised to NFC, because files
    uploaded from macOS are often NFD ("a" + a separate accent), which would
    make the same name look like two different ones.
    """
    name = html.unescape(pick_language(name or "", lang))
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r"\s+", " ", name)  # newlines/tabs in names -> space
    name = _INVALID_CHARS.sub("_", name)
    # Windows forbids a trailing dot/space; this also turns "." and ".." into
    # an empty string, so a name can never escape its directory.
    name = name.strip().rstrip(". ")
    if not name:
        return fallback
    if name.split(".")[0].strip().upper() in _WINDOWS_RESERVED:
        name = "_" + name
    return _truncate_utf8(name, MAX_COMPONENT_BYTES)
