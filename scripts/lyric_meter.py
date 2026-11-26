#!/usr/bin/env python3
"""lyric_meter.py: syllable counter and rhyme-scheme checker for song lyrics
(English, Spanish, Brazilian Portuguese and Russian).

Zero dependencies. Reads lyrics with Suno-style section tags ([Verse], [Chorus], ...),
counts syllables per line, derives the rhyme scheme per section and flags lines whose
length drifts from the section median.

    python3 scripts/lyric_meter.py lyrics.txt
    python3 scripts/lyric_meter.py --lang es examples/lyrics/luna-de-neon.es.txt
    python3 scripts/lyric_meter.py --lang pt --json examples/lyrics/baile-na-laje.pt.txt
    cat lyrics.txt | python3 scripts/lyric_meter.py -

Heuristics, not a dictionary: English counts are usually within one syllable of a
phonetic count; Spanish and Portuguese counts follow spelling rules (diphthongs, hiatus,
written accents) and merge a vowel that ends a word with the vowel that starts the next
one (sinalefa / elisão), the way a sung line is phrased; Russian counts are exact for
standard spelling. Spanish and Portuguese rhymes run from the stressed vowel (written
accent, else the penultimate/last-syllable rule), so consonant rhyme is a full rhyme and
assonance (same vowels) a slant rhyme. See README "Limits".
"""
import argparse
import json
import re
import sys
from statistics import median

__version__ = "0.2.0"

TAG_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
EN_VOWELS = "aeiouy"
RU_VOWELS = "аеёиоуыэюя"
CYRILLIC_RE = re.compile(r"[а-яё]", re.IGNORECASE)
LATIN_RE = re.compile(r"[a-z]", re.IGNORECASE)
ROMANCE = ("es", "pt")
# strong vowels (a, e, o and any vowel with an acute/circumflex/tilde) vs weak (i, u, ü)
ES_STRONG = set("aeoáéíóúàâêôãõ")
ES_WEAK = set("iuüy")
ROMANCE_VOWELS = ES_STRONG | ES_WEAK
PLAIN = str.maketrans("áéíóúàâêôãõü", "aeiouaaeoaou")
MARKERS = {
    "es": {"que", "el", "la", "los", "las", "de", "y", "mi", "tu", "yo", "me", "te", "en", "un", "una", "por", "con", "no", "es", "lo", "pero", "como", "noche", "quiero", "corazón", "baila", "contigo", "amor"},
    "pt": {"que", "o", "a", "os", "as", "de", "e", "meu", "minha", "você", "eu", "me", "te", "em", "um", "uma", "por", "com", "não", "é", "mas", "como", "noite", "quero", "coração", "dança", "contigo", "amor", "do", "da", "no", "na", "pra", "tô", "tá"},
    "en": {"the", "and", "you", "i", "me", "my", "your", "in", "on", "of", "to", "is", "it", "a", "we", "love", "night", "dance", "with", "for", "but", "all", "take", "home"},
}


# ----------------------------------------------------------------------------- syllables

def syllables_en(word):
    """Approximate syllable count for one English word."""
    w = re.sub(r"[^a-z]", "", word.lower().replace("'", ""))
    if not w:
        return 0
    if len(w) <= 3:
        return 1
    count = len(re.findall(r"[aeiouy]+", w))
    # silent final e: "time", "love" (but not "table", "free", "eye")
    if w.endswith("e") and not w.endswith(("le", "ee", "ye", "oe", "ue")) and count > 1:
        count -= 1
    # -ed is silent unless after t/d: "walked" 1, "wanted" 2
    elif w.endswith("ed") and not re.search(r"[td]ed$", w) and count > 1:
        count -= 1
    # -es is silent unless after a sibilant: "waves" 1, "boxes" 2
    elif w.endswith("es") and not re.search(r"(ss|sh|ch|x|z|[cg])es$", w) and count > 1:
        count -= 1
    # vowel pairs that are usually two syllables: "idea", "radio", "ruin", "create"
    count += len(re.findall(r"(?<=[^aeiouy])i[ao](?![nl])|ui(?!t)|eate", w))
    # -le after a consonant is its own syllable: "table", "little"
    if re.search(r"[^aeiouy]le$", w) and count == 1:
        count += 1
    return max(1, count)


def syllables_ru(word):
    """Syllable count for one Russian word: one vowel letter, one syllable."""
    w = word.lower()
    return sum(1 for ch in w if ch in RU_VOWELS)


def _romance_word(word):
    w = word.lower().replace("'", "")
    w = re.sub(r"[^a-zñçáéíóúàâêôãõü]", "", w)
    # "qu"/"gu" before e/i: the u is silent (que, guitarra); ü is sung (pingüino)
    w = re.sub(r"([qg])u(?=[eiéí])", r"\1", w)
    # y is a consonant before a vowel (yo, ayer), a vowel elsewhere (hoy, muy, y)
    w = re.sub(r"y(?=[aeiouáéíóú])", "j", w)
    return w


def _nuclei(w, lang="es"):
    """Vowel nuclei of a Spanish/Portuguese word as (start, end) spans: a diphthong or
    triphthong is one nucleus; two strong vowels side by side (hiatus) are two. In
    Portuguese a final -ia/-io/-ua/-uo after a consonant is a hiatus too (di-a, ru-a,
    fri-o), which Spanish marks with an accent (dí-a)."""
    if lang == "pt":
        m = re.search(r"(?<=[^aeiouáéíóúâêôãõgq])([iu])([aoe]s?)$", w)
        if m and len(w) > 2:
            head = _nuclei(w[:m.start(2)], "es")
            return head + [(m.start(2), len(w) - (1 if w.endswith("s") else 0))]
    spans = []
    i = 0
    while i < len(w):
        if w[i] not in ROMANCE_VOWELS:
            i += 1
            continue
        start = i
        while i + 1 < len(w) and w[i + 1] in ROMANCE_VOWELS:
            a, b = w[i], w[i + 1]
            nasal = a in "ãõ" or (b in "ãõ" and a in "ae")
            if a in ES_STRONG and b in ES_STRONG and not nasal:
                break  # hiatus: po-e-ta, ma-íz, dí-a; but ão, õe, ãe stay one nucleus
            i += 1
        spans.append((start, i + 1))
        i += 1
    return spans


def syllables_es(word):
    """Syllable count for one Spanish word (spelling rules, no dictionary)."""
    return len(_nuclei(_romance_word(word)))


def syllables_pt(word):
    """Syllable count for one Brazilian Portuguese word (spelling rules, no dictionary)."""
    return len(_nuclei(_romance_word(word), "pt"))


def _starts_with_vowel(w):
    w = _romance_word(w)
    w = w[1:] if w.startswith("h") else w
    return bool(w) and w[0] in ROMANCE_VOWELS


def _ends_with_vowel(w):
    w = _romance_word(w)
    return bool(w) and w[-1] in ROMANCE_VOWELS


def count_line(line, lang):
    words = tokenize(line)
    if lang in ROMANCE:
        fn = syllables_es if lang == "es" else syllables_pt
        total = sum(fn(w) for w in words)
        # sinalefa / elisão: "te amo" is sung as two syllables, not three
        for a, b in zip(words, words[1:]):
            if _ends_with_vowel(a) and _starts_with_vowel(b) and fn(a) and fn(b):
                total -= 1
        return total
    fn = syllables_ru if lang == "ru" else syllables_en
    return sum(fn(w) for w in words)


def tokenize(line):
    # drop stage directions in parentheses that are not sung words? No: Suno sings
    # parenthesised backing vocals, so keep them. Only drop the tag brackets.
    line = re.sub(r"\[[^\]]*\]", " ", line)
    return [w for w in re.findall(r"[A-Za-zÀ-ÿА-Яа-яЁё']+", line) if re.search(r"[A-Za-zÀ-ÿА-Яа-яЁё]", w)]


# ----------------------------------------------------------------------------- rhyme

def rhyme_key_en(word):
    w = re.sub(r"[^a-z]", "", word.lower().replace("'", ""))
    if not w:
        return ""
    core = w
    if len(core) > 3 and core.endswith("s") and not core.endswith("ss"):
        core = core[:-1]  # plural / 3rd person: miles -> mile
    if len(core) > 2 and core.endswith("e") and not core.endswith(("le", "ee", "ye", "oe", "ue")):
        core = core[:-1]  # silent e: time/rhyme -> tim/rhym
    m = re.search(r"[aeiouy]+[^aeiouy]*$", core)
    key = m.group(0) if m else core
    return key.replace("y", "i")


def rhyme_key_ru(word):
    w = word.lower().replace("ё", "о")
    if not w:
        return ""
    vowel_idx = [i for i, ch in enumerate(w) if ch in RU_VOWELS]
    if not vowel_idx:
        return w
    # Russian rhyme runs from the stressed vowel; without stress data take the last vowel and
    # its coda, and for open endings (word ends in a vowel) include the consonant before it,
    # so окно/давно -> "но"/"но" and дорога/нога -> "га"/"га".
    start = vowel_idx[-1]
    if start == len(w) - 1 and start > 0:
        start -= 1
    return w[start:]


def _stressed(w, lang):
    """Index into _nuclei(w) of the stressed nucleus."""
    nuc = _nuclei(w, lang)
    if not nuc:
        return None, nuc
    for k, (a, b) in enumerate(nuc):
        if any(ch in "áéíóúâêôàãõ" for ch in w[a:b]):
            if lang == "pt" and k == len(nuc) - 2 and any(ch in "ãõ" for ch in w[a:b]) and any(ch in "áéíóúâêô" for ch in w[nuc[-1][0]:]):
                continue
            return k, nuc
    if len(nuc) == 1:
        return 0, nuc
    if lang == "es":
        paroxytone = w[-1] in "aeiouns"  # llana: ends in a vowel, n or s
    else:
        paroxytone = bool(re.search(r"([aeo]s?|em|ens|am)$", w))
    return (len(nuc) - 2 if paroxytone else len(nuc) - 1), nuc


def rhyme_key_romance(word, lang="es"):
    """Rhyme key from the stressed vowel to the end, accents removed: corazón/canción -> 'on'."""
    w = _romance_word(word)
    if not w:
        return ""
    k, nuc = _stressed(w, lang)
    if k is None:
        return w.translate(PLAIN)
    a, b = nuc[k]
    seg = w[a:b]
    # start at the strong vowel of a diphthong: tiempo -> 'empo', fuego -> 'ego'
    off = next((j for j, ch in enumerate(seg) if ch in ES_STRONG), 0)
    key = w[a + off:].translate(PLAIN)
    return key.replace("ç", "s").replace("ñ", "ny")


def assonance(key):
    """Vowels of a rhyme key: noche/sombra differ, luna/cuna/fortuna share 'ua'."""
    return "".join(ch for ch in key if ch in "aeiou")


def is_backing(line):
    """True when the whole line is a (parenthesised) backing vocal or ad-lib."""
    s = line.strip()
    return s.startswith("(") and s.endswith(")")


def last_word(line):
    words = tokenize(line)
    return words[-1] if words else ""


def rhyme_scheme(lines, lang):
    """Return (scheme string, keys). Uppercase = full rhyme, lowercase = slant rhyme."""
    if lang in ROMANCE:
        keyfn = lambda wd: rhyme_key_romance(wd, lang)
    else:
        keyfn = rhyme_key_ru if lang == "ru" else rhyme_key_en
    keys = [keyfn(last_word(ln)) for ln in lines]
    letters = []
    groups = []  # (letter, key)
    for key in keys:
        letter = None
        if key:
            for lt, k in groups:
                if k == key:
                    letter = lt
                    break
            if letter is None:
                for lt, k in groups:
                    if lang in ROMANCE:
                        slant = assonance(k) and assonance(k) == assonance(key)
                    else:
                        slant = len(k) >= 2 and len(key) >= 2 and k[-2:] == key[-2:]
                    if slant:
                        letter = lt.lower()
                        break
        if letter is None:
            letter = chr(ord("A") + len(groups)) if len(groups) < 26 else "?"
            groups.append((letter, key))
        letters.append(letter)
    return "".join(letters), keys


# ----------------------------------------------------------------------------- parsing

def detect_lang(text):
    cyr = len(CYRILLIC_RE.findall(text))
    lat = len(LATIN_RE.findall(text))
    if cyr > lat:
        return "ru"
    low = re.sub(r"\[[^\]]*\]", " ", text.lower())
    words = re.findall(r"[a-zñçáéíóúàâêôãõü]+", low)
    score = {lg: sum(1 for w in words if w in m) for lg, m in MARKERS.items()}
    score["es"] += 3 * len(re.findall(r"ñ|¿|¡|ción\b", low))
    score["pt"] += 3 * len(re.findall(r"ã|õ|ç|ção\b|\bvocê\b|\bnão\b", low))
    best = max(("en", "es", "pt"), key=lambda lg: score[lg])
    return best if score[best] > score["en"] else "en"


def parse_sections(text):
    """Split lyrics into [(tag, [lines])]. Lines before the first tag go to tag ''."""
    sections = []
    tag, lines = "", []
    for raw in text.splitlines():
        line = raw.strip()
        m = TAG_RE.match(line)
        if m:
            if lines or tag:
                sections.append((tag, lines))
            tag, lines = m.group(1).strip(), []
            continue
        if not line:
            continue
        lines.append(line)
    if lines or tag:
        sections.append((tag, lines))
    return sections


# ----------------------------------------------------------------------------- report

def analyse(text, lang="auto", max_dev=2):
    if lang == "auto":
        lang = detect_lang(text)
    report = {"lang": lang, "sections": [], "warnings": []}
    for tag, lines in parse_sections(text):
        if not lines:
            report["sections"].append({"tag": tag, "lines": [], "scheme": "", "min": 0, "max": 0, "median": 0})
            continue
        counts = [count_line(ln, lang) for ln in lines]
        scheme, keys = rhyme_scheme(lines, lang)
        med = median(counts)
        sec = {
            "tag": tag, "scheme": scheme, "min": min(counts), "max": max(counts), "median": med,
            "lines": [{"n": i + 1, "syllables": c, "text": ln, "rhyme": scheme[i], "key": keys[i]}
                      for i, (ln, c) in enumerate(zip(lines, counts))],
        }
        report["sections"].append(sec)
        label = "[%s]" % tag if tag else "(untagged)"
        for i, c in enumerate(counts):
            if is_backing(lines[i]):
                sec["lines"][i]["backing"] = True
                continue  # (parenthesised) backing vocals are short by design
            if abs(c - med) > max_dev:
                sign = "+" if c > med else "-"
                report["warnings"].append("%s line %d has %d syllables, section median %g (%s%g)"
                                          % (label, i + 1, c, med, sign, abs(c - med)))
        if len(lines) >= 4 and len(set(scheme.upper())) == len(scheme):
            report["warnings"].append("%s has no rhymes in %d lines (scheme %s)" % (label, len(lines), scheme))
    return report


def format_text(report, name):
    out = ["lyric_meter  %s  (lang: %s)" % (name, report["lang"])]
    for sec in report["sections"]:
        label = "[%s]" % sec["tag"] if sec["tag"] else "(untagged)"
        if not sec["lines"]:
            out.append("%-14s empty" % label)
            continue
        span = "%d" % sec["min"] if sec["min"] == sec["max"] else "%d-%d" % (sec["min"], sec["max"])
        out.append("%-14s %d lines · syllables %s · scheme %s" % (label, len(sec["lines"]), span, sec["scheme"]))
        for ln in sec["lines"]:
            out.append("  %2d  %2d  %-44s %s" % (ln["n"], ln["syllables"], ln["text"][:44], ln["rhyme"]))
    for w in report["warnings"]:
        out.append("! " + w)
    if not report["warnings"]:
        out.append("+ no length or rhyme warnings")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Syllable counter and rhyme-scheme checker for EN/ES/PT/RU lyrics with Suno section tags.")
    ap.add_argument("files", nargs="+", help="lyrics file(s); '-' reads stdin")
    ap.add_argument("--lang", choices=["auto", "en", "es", "pt", "ru"], default="auto", help="language (default: auto-detect per file)")
    ap.add_argument("--max-deviation", type=int, default=2, metavar="N", help="warn when a line is more than N syllables from the section median (default 2)")
    ap.add_argument("--json", action="store_true", help="print JSON instead of text")
    ap.add_argument("--version", action="version", version=__version__)
    a = ap.parse_args(argv)
    reports = []
    for f in a.files:
        text = sys.stdin.read() if f == "-" else open(f, encoding="utf-8").read()
        rep = analyse(text, a.lang, a.max_deviation)
        rep["file"] = f
        reports.append(rep)
    if a.json:
        print(json.dumps(reports if len(reports) > 1 else reports[0], ensure_ascii=False, indent=2))
    else:
        print("\n\n".join(format_text(r, r["file"]) for r in reports))
    return 0


if __name__ == "__main__":
    sys.exit(main())
