#!/usr/bin/env python3
"""Export the data cubes (the messages read in the shop's Data menu) as a script for voicing.

Reads the six episodes' cube files (cubetxt1-5.dat from the game's data, cubetxt6.dat that
tools/content/episode6/build.py makes) the way src/game_menu.c load_cube() does: the n-th cube
is the text after the n-th string that starts with '*' ("*NN MM ...": NN is only the writers'
label, MM the portrait, face_sprite = MM - 1, -1 without one; strtol reads it from buf[4], so a
short header line reads whatever an earlier, longer string left there), then a title (80
characters at most), a sender line (12 at most) and the text up to the next '*' string. The text
is wrapped as the game wraps it (35 characters and 150 pixels of the tiny font a line, 90 lines),
so the script holds exactly the words the reader shows.

Writes data/voices/script.json (per cube: episode, number, title, sender, portrait, speaker, the
text cleaned for speech and split into segments of one speaker each, the game's wrapped lines)
and data/voices/script.html (a review copy). The game's text and anything made from it stay under
data/ (the voices are in the repository, the game's data is downloaded); tools/voices/cast.json (the speakers, their voices, which cubes they read,
the few cubes split between several voices) is ours and in the repository. Updates the "usage"
of every speaker in cast.json (its cubes, portraits and characters).

Local corrections that quote the game's text go in data/voices/overrides.json (same keys as
cast.json's "cube_rules", plus "tts_replace": [[old, new], ...] for a cube's spoken text).

usage: tools/voices/export_cubes.py [--data DIR] [--episode6 DIR] [--episode7 DIR] [--out DIR] [--show E:N]
"""
import argparse
import base64
import datetime
import html
import json
import os
import re
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CAST = os.path.join(HERE, "cast.json")
PRONUNCIATION = os.path.join(HERE, "pronunciation.json")
NAMES = set()  # lower-case proper nouns (pronunciation.json and a few more), for un-capitalizing highlighted names

CRYPT_KEY = [204, 129, 63, 255, 71, 19, 25, 62, 1, 99]  # tools/levels.py

# src/fonthand.c font_ascii: a byte's sprite in a font (-1: none, not drawn, no width).
FONT_ASCII = (
    [-1] * 32
    + [-1, 26, 33, 60, 61, 62, -1, 32, 64, 65, 63, 84, 29, 83, 28, 80,
       79, 70, 71, 72, 73, 74, 75, 76, 77, 78, 31, 30, -1, 85, -1, 27,
       -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
       15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 68, 82, 69, -1, -1,
       -1, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48,
       49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 66, 81, 67, -1, -1]
    + list(range(86, 127)) + [-1] * 87
)
assert len(FONT_ASCII) == 256

TINY_FONT, FACE_SHAPES = 2, 4      # src/sprite.h
CUBE_LINE_CHARS = 35               # sizeof(cube->text[0]) - 1
CUBE_LINE_WIDTH = 150
CUBE_LINES = 90                    # COUNTOF(cube->text)
TITLE_SIZE, HEADER_SIZE = 81, 13   # cube_struct title[81], header[13]
FACEPAL = [1, 2, 3, 4, 6, 9, 11, 12, 16, 13, 14, 15]  # src/pcxmast.c facepal

# Misspellings in the text that a voice would stumble over; the subtitles keep the game's words.
SPELLING = {
    "sqadron": "squadron", "apprxxme": "appro...", "Copmputer": "Computer", "Priortily": "Priority",
    "trasmission": "transmission", "decieved": "deceived", "frieghter": "freighter",
    "simulatneously": "simultaneously", "restauraunts": "restaurants", "denziens": "denizens",
    "delectible": "delectable", "regrettible": "regrettable", "invoved": "involved",
    "labrynthine": "labyrinthine", "undergound": "underground", "skiiers": "skiers", "skiier": "skier",
    "quintissential": "quintessential", "damand": "demand", "Absorbtion": "Absorption",
    "agressive": "aggressive", "observence": "observance", "alowing": "allowing",
    "berillium": "beryllium", "vaccuum": "vacuum", "millenia": "millennia", "Marbelized": "Marbleized",
    "occured": "occurred", "manuever": "maneuver", "manuvering": "maneuvering", "commited": "committed",
    "androi": "androi-",
    "insignifigant": "insignificant", "deceivied": "deceived", "forefeit": "forfeit",
}

# Paragraphs that are the comm system's own notes, not the sender's words (whole paragraphs).
SYSTEM_PARAGRAPH = re.compile(
    r"^(Tightbeam private coded message|Attached messages? included|Decoded transmission follows"
    r"|Recorded VidCom|Computer translation of)", re.I)
BRACKETED = re.compile(r"^\s*(?:\[([^\[\]]*)\]|<([^<>]*)>)\s*\.?\s*$")
SYSTEM_NOTE = re.compile(r"^(end of|transmission end|message (repeats|amplified)|program stopped"
                         r"|computer log|copmputer log|!)", re.I)


# --- the game's files -------------------------------------------------------------------------

def read_strings(path):
    """Encrypted Pascal strings, decrypted as src/helptext.c decrypt_string() does (bytes)."""
    with open(path, "rb") as f:
        data = f.read()
    strings, i = [], 0
    while i < len(data):
        length = data[i]
        s = bytearray(data[i + 1:i + 1 + length])
        i += 1 + length
        for j in range(length - 1, -1, -1):
            s[j] ^= CRYPT_KEY[j % len(CRYPT_KEY)]
            if j > 0:
                s[j] ^= s[j - 1]
        strings.append(bytes(s))
    return strings


def sprite_table(shp, table):
    """A sprite table of tyrian.shp (src/sprite.c load_sprites): (width, height, data) or None."""
    count = struct.unpack_from("<H", shp, 0)[0]
    offsets = struct.unpack_from("<%di" % count, shp, 2)
    pos = offsets[table]
    n = struct.unpack_from("<H", shp, pos)[0]
    pos += 2
    sprites = []
    for _ in range(n):
        populated = shp[pos]
        pos += 1
        if not populated:
            sprites.append(None)
            continue
        w, h, size = struct.unpack_from("<HHH", shp, pos)
        pos += 6
        sprites.append((w, h, shp[pos:pos + size]))
        pos += size
    return sprites


def text_width(word, font):
    """src/fonthand.c JE_textWidth."""
    x = 0
    for b in word:
        sid = FONT_ASCII[b]
        if b == 32:
            x += 6
        elif sid != -1:
            x += (font[sid][0] if sid < len(font) and font[sid] else 0) + 1
    return x


def strtol(buf, start):
    """C strtol(&buf[start], ..., 10) on a NUL-terminated buffer."""
    i = start
    while i < len(buf) and buf[i] in b" \t\n\v\f\r":
        i += 1
    sign = 1
    if i < len(buf) and buf[i] in b"+-":
        sign = -1 if buf[i] == 45 else 1
        i += 1
    j = i
    while j < len(buf) and 48 <= buf[j] <= 57:
        j += 1
    return sign * int(buf[i:j]) if j > i else 0


def atoi(s, pos):
    return strtol(s + b"\0", pos) if pos < len(s) else 0


def load_cube(strings, cube_index, font):
    """src/game_menu.c load_cube(): the cube_index-th cube (1-based) of a file's strings."""
    buf = bytearray(257)  # char buf[256]; never-written bytes read as 0 here
    pos = 0

    def read_into_buf():
        nonlocal pos
        s = strings[pos]
        pos += 1
        buf[0:len(s)] = s
        buf[len(s)] = 0
        return s

    remaining = cube_index
    header_line = b""
    while remaining > 0:
        header_line = read_into_buf()
        if header_line[:1] == b"*":
            remaining -= 1
    face_sprite = strtol(buf, 4) - 1
    title_full, header_full = strings[pos], strings[pos + 1]
    pos += 2
    cube = {
        "header_line": header_line, "face_sprite": face_sprite,
        "title": title_full[:TITLE_SIZE - 1], "header": header_full[:HEADER_SIZE - 1],
        "title_full": title_full, "header_full": header_full,
        "source_lines": [], "words": [], "lines": [b""] * CUBE_LINES, "last_line": 0, "dropped": [],
    }
    line = line_chars = line_width = 0
    while True:
        s = read_into_buf()
        if s[:1] == b"*":
            break
        li = len(cube["source_lines"])
        cube["source_lines"].append(s)
        if len(s) == 0:
            if line_chars == 0:
                line += 4  # subsequent new paragraphs indicate 4-line break
            else:
                line += 1
            line_chars = line_width = 0
            continue
        parts = s.split(b" ")
        for wi, word in enumerate(parts):
            word_chars, word_width = len(word), text_width(word, font)
            if word_chars > CUBE_LINE_CHARS or word_width > CUBE_LINE_WIDTH:
                cube["dropped"].append(b" ".join(parts[wi:]))  # the game skips the rest of the line
                for w in parts[wi:]:
                    cube["words"].append({"line": li, "word": w, "game_line": None})
                break
            prepend_space = True
            line_chars += word_chars + 1
            line_width += word_width + 6
            if line_chars > CUBE_LINE_CHARS or line_width > CUBE_LINE_WIDTH:
                line += 1
                line_chars, line_width = word_chars, word_width
                prepend_space = False
            shown = line < CUBE_LINES
            if shown:
                cube["lines"][line] += (b" " if prepend_space else b"") + word
                cube["last_line"] = line + 1
            cube["words"].append({"line": li, "word": word, "game_line": line if shown else None})
    hidden = [w["word"] for w in cube["words"] if w["game_line"] is None and w["word"]]
    if hidden and not cube["dropped"]:
        cube["dropped"].append(b" ".join(hidden))
    return cube


def text_hash(lines):
    """The game's hash of a text (src/voiceover.c voiceover_hash): 32-bit FNV-1a over each line's
    bytes and a newline, as 8 hex digits. A voice plays only over the text it was made from."""
    h = 2166136261
    for line in lines:
        for b in line + b"\n":
            h = ((h ^ b) * 16777619) & 0xFFFFFFFF
    return f"{h:08x}"


def load_stories(levels_path):
    """The story texts of an episode's script (src/tyrian2.c): each ']W' command's lines up to the
    next '#' (a text between levels; ']Wy' a warning), and the nine secret hints after ']Q' (an
    episode's end shows its score and one of them). As cubes, each is a cube-like dict whose
    source_lines are the lines the game keeps in levelWarningText; its voice is found by their
    hash (text_hash), whatever the order the game reaches them in."""
    stories = []
    if not os.path.exists(levels_path):
        return stories
    strings = read_strings(levels_path)
    i = 0
    while i < len(strings):
        s = strings[i]
        kind = None
        if s.startswith(b"]W"):
            kind = "warning" if s[2:3] == b"y" else "text"
            blocks = 1
        elif s.startswith(b"]Q"):
            kind, blocks = "hint", 9
        i += 1
        if kind is None:
            continue
        for _ in range(blocks):
            lines = []
            while i < len(strings) and strings[i][:1] != b"#":
                lines.append(strings[i])
                i += 1
            i += 1  # the '#'
            if any(has_words(cp437(l)) for l in lines):
                stories.append({"kind": kind, "source_lines": lines})
    return stories


def story_raw(lines, kind):
    """A story's lines as load_cube's result, for paragraphs_of: every word shown. A hint's
    "Secret Hint 1-2-3:" label is not read, and its heading ("ASTEROID 2") is a paragraph."""
    if kind == "hint" and lines and re.match(rb"^Secret Hint [\d-]+:\s*$", lines[0]):
        rest = lines[1:]
        while rest and not rest[0].strip():
            rest = rest[1:]
        lines = rest[:1] + [b""] + rest[1:] if len(rest) > 1 else rest
    raw = {"source_lines": lines, "words": [], "lines": [], "last_line": 0, "dropped": []}
    for li, line in enumerate(lines):
        if not line:
            continue  # (an empty line has no words: a paragraph break, as in a cube)
        for w in line.split(b" "):
            raw["words"].append({"line": li, "word": w, "game_line": li})
    return raw


def cube_count(strings):
    """Cubes a file holds: '*' strings, less the last one, which only ends the last cube."""
    return max(0, sum(1 for s in strings if s[:1] == b"*") - 1)


def referenced_cubes(levels_path):
    """The cubes an episode's script lists in its ']?' commands (src/tyrian2.c), the only way
    a cube reaches the Data menu."""
    found = set()
    if not os.path.exists(levels_path):
        return None
    for s in read_strings(levels_path):
        if s.startswith(b"]?"):
            count = atoi(s, 4)
            for i in range(count):
                n = atoi(s, 3 + (i + 1) * 4)
                if n > 0:
                    found.add(n)
    return found


# --- cleaning for speech --------------------------------------------------------------------

def cp437(b):
    return b.decode("cp437")


def clean_display(text):
    """The text as the reader shows it, without the highlight markers and runs of spaces."""
    return re.sub(r"\s+", " ", text.replace("~", "")).strip()


def has_words(text):
    return re.search(r"[A-Za-z0-9]", text) is not None


def fix_spelling(text):
    def repl(m):
        return SPELLING.get(m.group(0), m.group(0))
    return re.sub(r"[A-Za-z]+", repl, text)


def tag(name):
    """An audio tag of ours, kept apart from the game's own brackets until the end."""
    return "\x01" + name + "\x02"


def normalize_tts(text, speaker_info):
    """Text for the voice: tags for the sounds the text writes out, abbreviations and numbers
    readable, the game's brackets turned into parentheses (eleven_v3/v4 read [..] as directions,
    and the generator drops [..] for models without audio tags)."""
    t = fix_spelling(text)
    t = t.replace("<!>", " ")
    t = re.sub(r"<\s*(cough|hack)\s*>", tag("coughs"), t, flags=re.I)
    t = re.sub(r"\[\s*chuckle\s*\]", tag("chuckles"), t, flags=re.I)
    t = re.sub(r"^Sigh\.\.\.$", tag("sighs"), t)
    t = re.sub(r"<([^<>]*)>", r"\1", t)
    if speaker_info.get("sings"):
        t = re.sub(r"\[([^\[\]]+)\]", lambda m: tag(m.group(1).strip().lower()), t)  # stage directions as tags
    else:
        t = re.sub(r"\[\s*([^\[\]]*?)\s*\]", r"(\1)", t)
    t = t.replace("\x01", "[").replace("\x02", "]")
    # A transmission breaking up: runs of dot-and-dash tokens.
    t = re.sub(r"(?:(?<=\s)|^)(?:[-.]+(?:\s+|$)){2,}", " ... ", t)
    t = re.sub(r"(\w)-{2,}(\w)", lambda m: m.group(1) * 4 + m.group(2), t)  # "i----t": a held note
    t = re.sub(r"\b(\w)-{2,}(?=\W|$)", r"\1-", t)                              # "f---": cut off
    t = re.sub(r"(?<!\.)\.\.(?!\.)", "...", t)
    t = re.sub(r"\.{4,}", "...", t)
    t = re.sub(r"\?{3,}", "unknown", t)
    t = re.sub(r"#(\d)", r"number \1", t)
    t = re.sub(r"\bLevel (\d+)-(\d+)", r"Levels \1 to \2", t)
    t = re.sub(r"\bLevel -(\d+)", r"Level minus \1", t)
    t = re.sub(r"(\d+)-unknown\s*pts\b", r"\1-plus points", t)
    t = re.sub(r"(\d+)-(\d+)(\s*pts\b)", r"\1 to \2\3", t)
    t = re.sub(r"\bpts\b", "points", t)
    t = re.sub(r"\b(\d+)\s*cr\b", r"\1 credits", t)
    t = re.sub(r"\b(\d+)\s*Cs\b", r"\1 C's", t)
    t = re.sub(r"\b(\d+)\s*ms\b", r"\1 milliseconds", t)
    t = re.sub(r"\b(\d+)\s*Gs\b", r"\1 G's", t)
    t = re.sub(r"\b(\d+)G\b", r"\1 G", t)
    t = re.sub(r"(\d)\s*°", r"\1 degrees", t)
    t = t.replace("miles/sec", "miles per second")
    t = re.sub(r"\b(\d+) ?x ?(\d+)(?!\.\d|\d)", r"\1 by \2", t)
    t = re.sub(r"(?<=\w)\+(?=\w)", " plus ", t)
    t = re.sub(r"\+(\d)", r"plus \1", t)
    t = re.sub(r"\s+/\s+", ", ", t)
    t = re.sub(r"(?<=[A-Za-z])/(?=[A-Za-z])", " or ", t)
    t = re.sub(r"\bALT-(\d+)", r"Alt \1", t)
    t = t.replace("V.I.P.s", "VIPs").replace("@", " at ")
    t = re.sub(r"\s+\.\.\.(\s+\.\.\.)+", " ...", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" ([,!?;:]|\.(?!\.))", r"\1", t)
    t = uncapitalize(t, speaker_info.get("narrator"))
    return t.strip()


def title_word(w):
    """'ZINGLON'S' -> "Zinglon's", 'ASTEROID' -> 'Asteroid'; letters only, the rest kept."""
    out, first = [], True
    for ch in w:
        if ch.isalpha():
            out.append(ch.upper() if first else ch.lower())
            first = False
        else:
            out.append(ch)
            if ch != "'":
                first = True  # after '(' or '-': a new word part
    return "".join(out)


def is_caps(token):
    letters = [c for c in token if c.isalpha()]
    return len(letters) >= 2 and not any(c.islower() for c in letters)


def uncapitalize(t, narrator):
    """The game highlights names and headings in capitals; eleven_v3 reads capitals as shouting.
    Headings ('TYRIAN:', 'ZINGLON'S ALE:'), a narrator's all-capital headlines and runs of
    capitals with a known name in them become title case; shouting ('GET ME OUT OF HERE!',
    'SEND SOMEONE OUT NOW YOU STUPID') stays."""
    letters = [c for c in t if c.isalpha()]
    if not letters:
        return t
    all_caps = not any(c.islower() for c in letters)
    if all_caps:
        heading = t.rstrip().endswith(":") and len(t) <= 60
        if heading or (narrator and "!" not in t):
            return " ".join(title_word(w) if is_caps(w) else w for w in t.split(" "))
        return t
    words = t.split(" ")
    i = 0
    while i < len(words):
        if not is_caps(words[i]):
            i += 1
            continue
        j = i
        while j < len(words) and is_caps(words[j]):
            j += 1
        run = words[i:j]
        named = any(re.sub(r"('S|[^A-Za-z-])", "", w.upper()).lower() in NAMES for w in run)
        heading = run[-1].endswith(":")
        if (named or heading) and not any("!" in w or "?" in w for w in run):
            words[i:j] = [title_word(w) for w in run]
        i = j
    return " ".join(words)


# --- segmentation -----------------------------------------------------------------------------

def paragraphs_of(cube):
    """Paragraphs for speech: the shown words, broken where the source has empty lines (two or
    more: a section break), and before a line indented by 10 or more spaces (a signature)."""
    paras, cur, blank_run, last_line = [], None, 0, None
    word_pos = []  # per word record: (paragraph, offset) or None
    for w in cube["words"]:
        li = w["line"]
        if li != last_line:
            # empty source lines between the previous word's line and this one
            if last_line is not None:
                blank_run = sum(1 for k in range(last_line + 1, li) if len(cube["source_lines"][k]) == 0)
            else:
                blank_run = sum(1 for k in range(0, li) if len(cube["source_lines"][k]) == 0)
            src = cube["source_lines"][li]
            indent = len(src) - len(src.lstrip(b" "))
            if cur is None or blank_run > 0 or indent >= 10:
                cur = {"text": "", "break": "section" if blank_run >= 2 else ("paragraph" if (blank_run or cur is None) else "line")}
                paras.append(cur)
            last_line = li
        shown = w["game_line"] is not None
        word = clean_display(cp437(w["word"])) if shown else ""
        if not word:
            word_pos.append(None)
            continue
        if cur["text"]:
            cur["text"] += " "
        word_pos.append((len(paras) - 1, len(cur["text"])))
        cur["text"] += word
    # drop empty paragraphs (only highlight markers or spaces), keeping indices of the rest
    keep = [i for i, p in enumerate(paras) if p["text"]]
    remap = {old: new for new, old in enumerate(keep)}
    paras = [paras[i] for i in keep]
    word_pos = [(remap[p[0]], p[1]) if p is not None else None for p in word_pos]
    if paras:
        paras[0]["break"] = "paragraph"
    return paras, word_pos


def game_lines(cube, word_pos):
    """The reader's lines with the paragraph and offset where each line's first word starts."""
    first = {}
    for w, pos in zip(cube["words"], word_pos):
        if pos is not None and w["game_line"] is not None and w["game_line"] not in first:
            first[w["game_line"]] = pos
    out = []
    for i in range(cube["last_line"]):
        p = first.get(i)
        out.append({"text": clean_display(cp437(cube["lines"][i])), "p": p[0] if p else None,
                    "o": p[1] if p else None})
    return out


def find_quotes(paras):
    """Spans inside double quotes over the whole cube: (p0, a0, p1, b1), the quote marks excluded."""
    spans, open_at = [], None
    for pi, p in enumerate(paras):
        for m in re.finditer('"', p["text"]):
            if open_at is None:
                open_at = (pi, m.end())
            else:
                spans.append((open_at[0], open_at[1], pi, m.start()))
                open_at = None
    return spans


def bracketed(text):
    """A paragraph that is one [..] or <..> group: (inner text, start, end, "[" or "<"), else kind None."""
    m = BRACKETED.match(text)
    if not m:
        return "", 0, 0, None
    g = 1 if m.group(1) is not None else 2
    return m.group(g).strip(), m.start(g), m.end(g), "[" if g == 1 else "<"


def segment_cube(cube_id, paras, speaker, rules, cast):
    """Units of (speaker, paragraph, start, end), from the cube's speaker and its rules."""
    units = [{"speaker": speaker, "p": i, "a": 0, "b": len(p["text"]), "fixed": False}
             for i, p in enumerate(paras)]
    by_para = {}
    for spk, idxs in (rules.get("paragraphs") or {}).items():
        for i in idxs:
            by_para[i] = spk
    for u in units:
        text = paras[u["p"]]["text"]
        inner, a, b, kind = bracketed(text)
        if u["p"] in by_para:
            u["speaker"], u["fixed"] = by_para[u["p"]], True
            if kind and not cast["speakers"].get(u["speaker"], {}).get("sings"):
                u["a"], u["b"] = a, b
            continue
        if SYSTEM_PARAGRAPH.match(text) or text.startswith("<!>"):
            u["speaker"] = "system"
        elif kind and re.fullmatch(r"(?i)(cough|hack|chuckle|sigh)s?", inner):
            continue  # the sender's own cough: an audio tag in its voice
        elif kind == "[" and not SYSTEM_NOTE.match(inner):
            u["speaker"] = "editor"  # the network's editor: cuts, stage directions
            u["a"], u["b"] = a, b
        elif kind == "<" and inner.lower().startswith("archive note"):
            u["a"], u["b"] = a, b  # the archive's own note: its voice
        elif kind:
            u["speaker"] = "system"
            u["a"], u["b"] = a, b
        else:
            continue
        u["fixed"] = True
    for pattern, spk in rules.get("labels") or []:
        rx = re.compile(r"^\s*(?:" + pattern + r")\s*:?\s*")
        for u in units:
            if u["fixed"]:
                continue
            m = rx.match(paras[u["p"]]["text"])
            if m:
                u["speaker"], u["a"], u["fixed"] = spk, m.end(), True
    quotes = rules.get("quotes")
    if quotes:
        names = quotes.get("by_name") if isinstance(quotes, dict) else None
        units = split_quotes(units, paras, quotes if isinstance(quotes, str) else None, names)
    for pattern, spk in rules.get("inline") or []:
        units = split_inline(units, paras, re.compile(pattern), spk)
    return [u for u in units if u["b"] > u["a"]]


def split_quotes(units, paras, speaker, names):
    out = []
    spans = find_quotes(paras)
    last_name = None
    for u in units:
        if u["fixed"]:
            out.append(u)
            continue
        pi, text = u["p"], paras[u["p"]]["text"]
        cuts = []  # (start, end, quoted?)
        pos = u["a"]
        for (p0, a0, p1, b1) in spans:
            if p1 < pi or p0 > pi:
                continue
            qa = a0 if p0 == pi else u["a"]
            qb = b1 if p1 == pi else u["b"]
            qa, qb = max(qa, u["a"]), min(qb, u["b"])
            if qb <= qa:
                continue
            start_mark = qa - 1 if p0 == pi else qa
            if start_mark > pos:
                cuts.append((pos, start_mark, False))
            cuts.append((qa, qb, True))
            pos = qb + 1 if p1 == pi else qb
        if pos < u["b"]:
            cuts.append((pos, u["b"], False))
        for a, b, quoted in cuts:
            piece = text[a:b]
            if not quoted and names:
                for m in re.finditer("|".join(re.escape(n) for n in names), piece):
                    last_name = m.group(0)
            spk = u["speaker"]
            if quoted:
                spk = names.get(last_name, u["speaker"]) if names else speaker
            out.append({"speaker": spk, "p": pi, "a": a, "b": b, "fixed": quoted})
    return out


def split_inline(units, paras, rx, speaker):
    out = []
    for u in units:
        text = paras[u["p"]]["text"]
        pos = u["a"]
        for m in rx.finditer(text, u["a"], u["b"]):
            if m.start() > pos:
                out.append(dict(u, a=pos, b=m.start()))
            _, ia, ib, kind = bracketed(m.group(0))
            a, b = (m.start() + ia, m.start() + ib) if kind else (m.start(), m.end())
            out.append({"speaker": speaker, "p": u["p"], "a": a, "b": b, "fixed": True})
            pos = m.end()
        if pos < u["b"]:
            out.append(dict(u, a=pos, b=u["b"]))
    return out


def trim_range(text, a, b):
    while a < b and text[a] in " \t,":
        a += 1
    while b > a and text[b - 1] in " \t":
        b -= 1
    return a, b


def build_segments(cube_id, paras, units, cast, max_chars, tts_replace):
    """Consecutive units of one speaker make a segment, broken at section breaks and before
    max_chars; a segment is pieces (paragraph, start, end) with their display and spoken text."""
    segments, cur = [], None
    prev_p = None
    for u in units:
        text = paras[u["p"]]["text"]
        a, b = trim_range(text, u["a"], u["b"])
        if b <= a:
            continue
        shown = text[a:b]
        if not has_words(shown):
            prev_p = u["p"]
            continue
        info = cast["speakers"].get(u["speaker"], {})
        tts = normalize_tts(shown, info)
        for old, new in tts_replace:
            tts = tts.replace(old, new)
        tag_only = not has_words(re.sub(r"\[[^\]]*\]", "", tts))
        if tag_only and not re.search(r"\[[^\]]+\]", tts):
            prev_p = u["p"]
            continue
        new_para = u["p"] != prev_p
        brk = paras[u["p"]]["break"] if new_para else "inline"
        if tag_only and cur is not None and cur["speaker"] == u["speaker"]:
            brk = "paragraph"  # a cough between sections stays with its speaker's words
        piece = {"p": u["p"], "a": a, "b": b, "text": shown, "tts": tts, "sep": "\n\n" if new_para else " "}
        length = len(tts)
        if (cur is None or cur["speaker"] != u["speaker"] or brk == "section"
                or (new_para and cur["chars"] + length > max_chars)):
            cur = {"speaker": u["speaker"], "break": brk, "pieces": [], "chars": 0}
            segments.append(cur)
            piece["sep"] = ""
        cur["pieces"].append(piece)
        cur["chars"] += length + len(piece["sep"])
        prev_p = u["p"]
    for i, s in enumerate(segments):
        s["index"] = i
        s["text"] = "".join(("\n\n" if p["sep"] == "\n\n" else p["sep"]) + p["text"] for p in s["pieces"])
        s["tts"] = "".join(p["sep"] + p["tts"] for p in s["pieces"])
        s["chars"] = len(s["tts"])
    return segments


# --- speakers ---------------------------------------------------------------------------------

def assign_speaker(cast, cube_id, title, sender, face):
    rules = cast.get("cube_rules", {}).get(cube_id, {})
    if rules.get("speaker"):
        return rules["speaker"], "cube rule"
    for key, spk in cast["speakers"].items():
        if cube_id in spk.get("match", {}).get("cubes", []):
            return key, "cube"
    for key, spk in cast["speakers"].items():
        for rx in spk.get("match", {}).get("titles", []):
            if re.search(rx, title):
                return key, "title"
    for key, spk in cast["speakers"].items():
        if sender.lower() in [s.lower() for s in spk.get("match", {}).get("senders", [])]:
            return key, "sender"
    return None, "unassigned"


def resolve_voice(cast, key):
    seen = set()
    while key in cast["speakers"] and cast["speakers"][key].get("voice_of") and key not in seen:
        seen.add(key)
        key = cast["speakers"][key]["voice_of"]
    return key


# --- output -----------------------------------------------------------------------------------

def png_data_uri(sprite, palette, scale=2):
    w, h, data = sprite
    img = [[None] * w for _ in range(h)]
    x = y = k = 0
    while k < len(data):
        c = data[k]
        if c == 255:
            k += 1
            x += data[k]
        elif c == 254:
            x = w
        elif c == 253:
            x += 1
        else:
            if y < h and x < w:
                img[y][x] = c
            x += 1
        if x >= w:
            x, y = 0, y + 1
        k += 1
    rows = []
    for yy in range(h * scale):
        row = bytearray(b"\0")
        for xx in range(w * scale):
            c = img[yy // scale][xx // scale]
            row += bytes(palette[c]) + b"\xff" if c is not None else b"\0\0\0\0"
        rows.append(bytes(row))

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w * scale, h * scale, 8, 6, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(b"".join(rows), 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


def palettes(path):
    with open(path, "rb") as f:
        pal = f.read()
    out = []
    for p in range(len(pal) // 768):
        out.append([((pal[p * 768 + i * 3] << 2) | (pal[p * 768 + i * 3] >> 4),
                     (pal[p * 768 + i * 3 + 1] << 2) | (pal[p * 768 + i * 3 + 1] >> 4),
                     (pal[p * 768 + i * 3 + 2] << 2) | (pal[p * 768 + i * 3 + 2] >> 4)) for i in range(256)])
    return out


COLORS = ["#c0392b", "#2471a3", "#1e8449", "#b9770e", "#7d3c98", "#117a65", "#a04000", "#2e4053",
          "#943126", "#1a5276", "#196f3d", "#9a7d0a", "#5b2c6f", "#0e6655", "#6e2c00", "#4d5656"]


def write_html(path, script, cast, faces):
    spk_keys = list(cast["speakers"].keys())
    color = {k: COLORS[i % len(COLORS)] for i, k in enumerate(spk_keys)}
    e = html.escape
    out = ["<!doctype html><html><head><meta charset='utf-8'><title>Tyrian data cube voices</title>",
           "<meta name='viewport' content='width=device-width, initial-scale=1'><style>",
           ":root{--bg:#f6f3ee;--fg:#222;--mute:#777;--card:#fff;--line:#ddd}",
           "@media (prefers-color-scheme:dark){:root{--bg:#1b1a18;--fg:#e8e4dc;--mute:#9a958c;--card:#262421;--line:#3a3733}}",
           "body{background:var(--bg);color:var(--fg);font:15px/1.45 -apple-system,Segoe UI,sans-serif;margin:0 auto;max-width:980px;padding:16px}",
           "h1{font-size:22px}h2{margin-top:36px;border-bottom:2px solid var(--line)}",
           ".cube{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:14px 0}",
           ".head{display:flex;gap:12px;align-items:flex-start}.head img{image-rendering:pixelated;border-radius:4px}",
           ".id{font-weight:700}.meta{color:var(--mute);font-size:13px}.skip{opacity:.55}",
           ".seg{border-left:4px solid;padding:4px 10px;margin:8px 0;white-space:pre-wrap}",
           ".who{font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.04em}",
           ".tts{color:var(--mute);font-size:13px;margin-top:4px;white-space:pre-wrap}",
           ".chip{display:inline-block;border-radius:10px;padding:0 8px;color:#fff;font-size:12px;margin:2px}",
           ".note{color:#b03a2e;font-size:13px}table{border-collapse:collapse}td,th{padding:2px 8px;border-bottom:1px solid var(--line);text-align:left}",
           "</style></head><body>"]
    t = script["totals"]
    out.append(f"<h1>Tyrian data cube voices: review copy</h1><p class='meta'>Made by tools/voices/export_cubes.py "
               f"on {e(script['generated'])}. {t['cubes_voiced']} cubes voiced ({t['cubes_skipped']} skipped), "
               f"{t['segments']} segments, {t['characters']:,} characters to speak. The grey line under a segment "
               f"is what the voice is sent before the pronunciation aliases (only where it differs). "
               f"Corrections: tools/voices/cast.json (speakers, splits) or data/voices/overrides.json (wording).</p>")
    out.append("<h2>Speakers</h2><table><tr><th>speaker</th><th>voice</th><th>cubes</th><th>characters</th></tr>")
    for k in spk_keys:
        s = cast["speakers"][k]
        u = s.get("usage", {})
        if not u.get("characters"):
            continue
        v = resolve_voice(cast, k)
        out.append(f"<tr><td><span class='chip' style='background:{color[k]}'>{e(k)}</span> {e(s.get('name', ''))}</td>"
                   f"<td>{e(v if v != k else 'own')}</td><td>{len(u.get('cubes', []))}</td><td>{u.get('characters', 0):,}</td></tr>")
    out.append("</table>")
    for ep in script["episodes"]:
        out.append(f"<h2>Episode {ep['episode']}</h2><p class='meta'>{e(ep['file'])}: {len(ep['cubes'])} cubes, "
                   f"{sum(c['chars'] for c in ep['cubes']):,} characters</p>")
        for c in ep["cubes"]:
            img = ""
            if c["face_sprite"] >= 0 and c["face_sprite"] < len(faces) and faces[c["face_sprite"]]:
                img = f"<img src='{faces[c['face_sprite']]}' width='130' alt='portrait {c['face_sprite'] + 1}'>"
            cls = "cube skip" if c["skip"] else "cube"
            out.append(f"<div class='{cls}' id='c{c['episode']}-{c['cube']}'><div class='head'>{img}<div>"
                       f"<div class='id'>{c['episode']}:{c['cube']} &nbsp; {e(c['title'])}</div>"
                       f"<div class='meta'>sender <b>{e(c['sender'])}</b> · portrait {c['face_sprite'] + 1 if c['face_sprite'] >= 0 else 'none'}"
                       f" · header line <code>{e(c['header_line'])}</code> · {'in the episode script' if c['referenced'] else '<b>never listed by the episode script</b>'}"
                       f" · {c['chars']:,} characters · speaker by {e(c['speaker_by'])}</div>")
            rule = cast.get("cube_rules", {}).get(c["id"], {})
            if rule.get("why"):
                out.append(f"<div class='meta'>split: {e(rule['why'])}</div>")
            if c["skip"]:
                out.append(f"<div class='note'>skipped: {e(c['skip'])}</div>")
            for n in c["notes"]:
                out.append(f"<div class='note'>{e(n)}</div>")
            out.append("</div></div>")
            for s in c["segments"]:
                k = s["speaker"]
                v = resolve_voice(cast, k)
                who = f"{k}" + (f" (voice of {v})" if v != k else "")
                paras = sorted({p["p"] for p in s["pieces"]})
                out.append(f"<div class='seg' style='border-color:{color.get(k, '#888')}'><div class='who' style='color:{color.get(k, '#888')}'>"
                           f"{e(who)} · {s['chars']} ch · ¶{','.join(map(str, paras))}{' · after a section break' if s['break'] == 'section' else ''}</div>"
                           f"{e(s['text'])}")
                if s["tts"] != s["text"]:
                    out.append(f"<div class='tts'>{e(s['tts'])}</div>")
                out.append("</div>")
            out.append("</div>")
    out.append("</body></html>")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--data", default=os.path.join(ROOT, "data", "tyrian2000"), help="the game's data (cubetxt1-5.dat, levels1-5.dat, tyrian.shp)")
    ap.add_argument("--episode6", default=os.path.join(ROOT, "assets", "content", "episode6"), help="cubetxt6.dat and levels6.dat")
    ap.add_argument("--episode7", default=os.path.join(ROOT, "assets", "content", "episode7"),
                    help="cubetxt7.dat and levels7.dat (the Game Boy Color episode, made from the user's ROM: tools/content/gbc/build.py)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "voices"), help="where script.json and script.html go")
    ap.add_argument("--cast", default=CAST)
    ap.add_argument("--show", action="append", default=[], metavar="E:N", help="print a cube's paragraphs and segments")
    ap.add_argument("--no-cast-update", action="store_true", help="do not write the speakers' usage into cast.json")
    args = ap.parse_args()

    with open(args.cast, encoding="utf-8") as f:
        cast = json.load(f)
    with open(PRONUNCIATION, encoding="utf-8") as f:
        for term in json.load(f)["terms"]:
            if term.get("kind") in ("person", "place", "organisation", "people", "ship"):
                NAMES.update(w.lower() for w in re.split(r"[\s-]+", term["term"]) if w.isalpha())
    NAMES.update({"fluxnet", "trent", "hawkins", "zinglon", "transon", "lohk", "remus"})
    overrides_path = os.path.join(args.out, "overrides.json")
    overrides = {}
    if os.path.exists(overrides_path):
        with open(overrides_path, encoding="utf-8") as f:
            overrides = json.load(f)
    max_chars = cast.get("defaults", {}).get("max_segment_chars", 2500)

    with open(os.path.join(args.data, "tyrian.shp"), "rb") as f:
        shp = f.read()
    font = sprite_table(shp, TINY_FONT)
    face_sprites = sprite_table(shp, FACE_SHAPES)
    pals = palettes(os.path.join(args.data, "palette.dat"))
    faces = [png_data_uri(s, pals[FACEPAL[i] if i < len(FACEPAL) else 0]) if s else None
             for i, s in enumerate(face_sprites)]

    script = {"version": 1, "generated": datetime.datetime.now().isoformat(timespec="seconds"),
              "note": "Made from the game's data by tools/voices/export_cubes.py; keep it out of git.",
              "episodes": []}
    usage = {k: {"cubes": [], "characters": 0, "segments": 0, "portraits": set()} for k in cast["speakers"]}
    problems = []
    for episode in range(1, 8):
        base = {6: args.episode6, 7: args.episode7}.get(episode, args.data)
        path = os.path.join(base, f"cubetxt{episode}.dat")
        if not os.path.exists(path):
            problems.append(f"episode {episode}: {path} missing")
            continue
        strings = read_strings(path)
        listed = referenced_cubes(os.path.join(base, f"levels{episode}.dat"))
        ep = {"episode": episode, "file": os.path.relpath(path, ROOT), "cubes": []}
        for n in range(1, cube_count(strings) + 1):
            raw = load_cube(strings, n, font)
            cube_id = f"{episode}:{n}"
            title, sender = clean_display(cp437(raw["title"])), clean_display(cp437(raw["header"]))
            rules = dict(cast.get("cube_rules", {}).get(cube_id, {}))
            local = overrides.get(cube_id, {})
            for k, v in local.items():
                if k != "tts_replace":
                    rules[k] = v
            notes = []
            if len(raw["title_full"]) >= TITLE_SIZE or len(raw["header_full"]) >= HEADER_SIZE:
                notes.append("title or sender line longer than the game keeps (cut, as the game cuts it)")
            for d in raw["dropped"]:
                notes.append("the reader does not show: " + clean_display(cp437(d)))
            paras, word_pos = paragraphs_of(raw)
            skip = rules.get("skip")
            if not skip and raw["title"][:1] == b"*":
                skip = "its title is another cube's header line (the file has consecutive '*' lines)"
            if not skip and not paras:
                skip = "no text"
            speaker, how = assign_speaker(cast, cube_id, title, sender, raw["face_sprite"] + 1)
            if not skip and speaker is None:
                problems.append(f"{cube_id} ({sender!r}): no speaker in cast.json")
                speaker = "archive"
            segments = []
            if not skip:
                units = segment_cube(cube_id, paras, speaker, rules, cast)
                segments = build_segments(cube_id, paras, units, cast, max_chars, local.get("tts_replace", []))
            cube = {
                "id": cube_id, "episode": episode, "cube": n,
                "header_line": clean_display(cp437(raw["header_line"])), "title": title, "sender": sender,
                "face_sprite": raw["face_sprite"], "referenced": (listed is None) or (n in listed),
                "skip": skip, "speaker": speaker, "speaker_by": how,
                "speakers": sorted({s["speaker"] for s in segments}),
                "paragraphs": [{"text": p["text"], "break": p["break"]} for p in paras],
                "segments": segments, "lines": game_lines(raw, word_pos),
                "chars": sum(s["chars"] for s in segments), "notes": notes,
                "audio": f"e{episode}/{n}.wav", "text_hash": text_hash(raw["source_lines"]),
            }
            voices_here = {}
            for s in segments:
                if s["speaker"] not in cast["speakers"]:
                    problems.append(f"{cube_id}: speaker {s['speaker']!r} is not in cast.json")
                    continue
                v = resolve_voice(cast, s["speaker"])
                if voices_here.setdefault(v, s["speaker"]) != s["speaker"]:
                    problems.append(f"{cube_id}: {voices_here[v]} and {s['speaker']} would have the same voice ({v})")
                u = usage[s["speaker"]]
                if cube_id not in u["cubes"]:
                    u["cubes"].append(cube_id)
                u["characters"] += s["chars"]
                u["segments"] += 1
                if raw["face_sprite"] >= 0 and s["speaker"] == speaker:
                    u["portraits"].add(raw["face_sprite"] + 1)
                if s["chars"] > 4800:
                    problems.append(f"{cube_id} segment {s['index']}: {s['chars']} characters (eleven_v3 takes 5000)")
            ep["cubes"].append(cube)

        # The story texts between levels, numbered from 101 in each episode (the hints from 201).
        ep["stories"] = []
        counts = {"text": 100, "warning": 100, "hint": 200}
        for st in load_stories(os.path.join(base, f"levels{episode}.dat")):
            kind = "hint" if st["kind"] == "hint" else "text"
            counts[kind] += 1
            n = counts[kind]
            story_id = f"{episode}:{n}"
            raw = story_raw(st["source_lines"], st["kind"])
            paras, _ = paragraphs_of(raw)
            rules = dict(cast.get("cube_rules", {}).get(story_id, {}))
            # A warning in the comm system's voice, a hint in the designer's, the rest told by the narrator.
            warning = st["kind"] == "warning" and st["source_lines"][0].startswith(b"Warning")
            speaker = rules.get("speaker") or ("system" if warning else "designer" if st["kind"] == "hint" else "narrator")
            segments = build_segments(story_id, paras, segment_cube(story_id, paras, speaker, rules, cast), cast, max_chars, [])
            story = {
                "id": story_id, "episode": episode, "cube": n, "kind": "story", "story_kind": st["kind"],
                "title": clean_display(cp437(st["source_lines"][0])), "sender": "", "face_sprite": -1,
                "referenced": True, "skip": rules.get("skip"), "speaker": speaker, "speaker_by": "story rule" if rules.get("speaker") else st["kind"],
                "speakers": sorted({x["speaker"] for x in segments}),
                "paragraphs": [{"text": p["text"], "break": p["break"]} for p in paras],
                "segments": segments, "lines": [], "chars": sum(x["chars"] for x in segments), "notes": [],
                # (levelWarningText keeps 60 characters and a NUL; a longer line runs into the next row)
                "audio": f"story/e{episode}_{n}.wav", "text_hash": text_hash([l[:61] for l in st["source_lines"]]),
                "text": " ".join(p["text"] for p in paras),
            }
            for x in segments:
                if x["speaker"] not in cast["speakers"]:
                    problems.append(f"{story_id}: speaker {x['speaker']!r} is not in cast.json")
                    continue
                u = usage[x["speaker"]]
                if story_id not in u["cubes"]:
                    u["cubes"].append(story_id)
                u["characters"] += x["chars"]
                u["segments"] += 1
            ep["stories"].append(story)
        script["episodes"].append(ep)

    all_cubes = [c for ep in script["episodes"] for c in ep["cubes"]]
    voiced = [c for c in all_cubes if not c["skip"]]
    script["totals"] = {
        "cubes": len(all_cubes), "cubes_voiced": len(voiced), "cubes_skipped": len(all_cubes) - len(voiced),
        "cubes_not_listed": [c["id"] for c in voiced if not c["referenced"]],
        "segments": sum(len(c["segments"]) for c in voiced), "characters": sum(c["chars"] for c in voiced),
        "characters_by_episode": {str(ep["episode"]): sum(c["chars"] for c in ep["cubes"]) for ep in script["episodes"]},
        "stories": sum(len(ep["stories"]) for ep in script["episodes"]),
        "story_characters": sum(st["chars"] for ep in script["episodes"] for st in ep["stories"] if not st["skip"]),
    }
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "script.json"), "w", encoding="utf-8") as f:
        json.dump(script, f, indent=1, ensure_ascii=False)
    for k, u in usage.items():
        cast["speakers"][k]["usage"] = {"cubes": u["cubes"], "segments": u["segments"], "characters": u["characters"],
                                         "portraits": sorted(u["portraits"])}
    if not args.no_cast_update:
        with open(args.cast, "w", encoding="utf-8") as f:
            json.dump(cast, f, indent=2, ensure_ascii=False)
            f.write("\n")
    write_html(os.path.join(args.out, "script.html"), script, cast, faces)

    for want in args.show:
        for c in all_cubes + [st for ep in script["episodes"] for st in ep["stories"]]:
            if c["id"] == want:
                print(f"== {c['id']} {c['title']!r} sender {c['sender']!r} face {c['face_sprite'] + 1} speaker {c['speaker']} skip {c['skip']}")
                for i, p in enumerate(c["paragraphs"]):
                    print(f"  ¶{i} [{p['break']}] {p['text']}")
                for s in c["segments"]:
                    print(f"  -- seg {s['index']} {s['speaker']} ({s['chars']} ch, {s['break']}): {s['tts']!r}")
    t = script["totals"]
    print(f"{t['cubes']} cubes in 6 episodes: {t['cubes_voiced']} to voice, {t['cubes_skipped']} skipped "
          f"(placeholders); {t['segments']} segments, {t['characters']:,} characters")
    print("characters by episode: " + ", ".join(f"{k}: {v:,}" for k, v in t["characters_by_episode"].items()))
    print(f"{t['stories']} story texts between levels and hints (numbered from 101 and 201 in each episode): "
          f"{t['story_characters']:,} characters")
    if t["cubes_not_listed"]:
        print("voiced but never listed by their episode's script: " + " ".join(t["cubes_not_listed"]))
    for c in all_cubes:
        if c["skip"]:
            print(f"skipped {c['id']}: {c['skip']}")
    for p in problems:
        print("warning: " + p)
    print(f"wrote {os.path.relpath(os.path.join(args.out, 'script.json'), ROOT)} and script.html")
    return 1 if any("no speaker" in p or "not in cast" in p for p in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
