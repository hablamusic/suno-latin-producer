import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import lyric_meter as lm  # noqa: E402


class SyllablesEn(unittest.TestCase):
    def test_common_words(self):
        cases = {"cat": 1, "time": 1, "love": 1, "table": 2, "little": 2, "walked": 1, "wanted": 2,
                 "boxes": 2, "waves": 1, "radio": 3, "nation": 2, "free": 1, "midnight": 2,
                 "telephone": 3, "beautiful": 3, "window": 2, "ceiling": 2, "fruit": 1}
        for word, n in cases.items():
            self.assertEqual(lm.syllables_en(word), n, word)

    def test_empty_and_punctuation(self):
        self.assertEqual(lm.syllables_en("..."), 0)
        self.assertEqual(lm.count_line("Rain keeps tapping on the glass", "en"), 7)


class SyllablesRu(unittest.TestCase):
    def test_vowel_count(self):
        self.assertEqual(lm.syllables_ru("северный"), 3)
        self.assertEqual(lm.syllables_ru("в"), 0)
        self.assertEqual(lm.syllables_ru("ёлка"), 2)
        self.assertEqual(lm.count_line("Северный ветер стучится в окно", "ru"), 10)


class Rhymes(unittest.TestCase):
    def test_en_keys(self):
        self.assertEqual(lm.rhyme_key_en("home"), lm.rhyme_key_en("chrome"))
        self.assertEqual(lm.rhyme_key_en("time"), lm.rhyme_key_en("rhyme"))
        self.assertEqual(lm.rhyme_key_en("miles"), lm.rhyme_key_en("while"))
        self.assertEqual(lm.rhyme_key_en("glass"), lm.rhyme_key_en("pass"))
        self.assertNotEqual(lm.rhyme_key_en("home"), lm.rhyme_key_en("back"))

    def test_ru_keys(self):
        self.assertEqual(lm.rhyme_key_ru("окно"), lm.rhyme_key_ru("давно"))
        self.assertEqual(lm.rhyme_key_ru("горит"), lm.rhyme_key_ru("говорит"))
        self.assertEqual(lm.rhyme_key_ru("окне"), lm.rhyme_key_ru("мне"))
        self.assertEqual(lm.rhyme_key_ru("дорога"), lm.rhyme_key_ru("нога"))
        self.assertNotEqual(lm.rhyme_key_ru("окно"), lm.rhyme_key_ru("слов"))

    def test_scheme(self):
        abab = ["Streetlights hum a tired song", "Rain keeps tapping on the glass",
                "Every stop takes twice as long", "Watching all the faces pass"]
        self.assertEqual(lm.rhyme_scheme(abab, "en")[0], "ABAB")
        aabb = ["take me home", "made of chrome", "a telephone", "ringing on"]
        self.assertEqual(lm.rhyme_scheme(aabb, "en")[0], "AABB")
        self.assertEqual(lm.rhyme_scheme(["by the door", "waiting for"], "en")[0], "Aa")  # slant
        ru = ["стучится в окно", "остывает давно", "тысячу слов", "молчать я готов"]
        self.assertEqual(lm.rhyme_scheme(ru, "ru")[0], "AABB")


class Romance(unittest.TestCase):
    def test_spanish_syllables(self):
        for word, n in [("corazón", 3), ("canción", 2), ("poeta", 3), ("día", 2), ("fuego", 2), ("guitarra", 3), ("hoy", 1), ("ayer", 2), ("perreo", 3)]:
            self.assertEqual(lm.syllables_es(word), n, word)

    def test_portuguese_syllables(self):
        for word, n in [("coração", 3), ("não", 1), ("mãe", 1), ("saudade", 3), ("rua", 2), ("dia", 2), ("água", 2), ("noite", 2)]:
            self.assertEqual(lm.syllables_pt(word), n, word)

    def test_sinalefa(self):
        self.assertEqual(lm.count_line("Te quiero ver bailar", "es"), 6)
        self.assertEqual(lm.count_line("Baila conmigo hasta el amanecer", "es"), 10)
        self.assertEqual(lm.count_line("O tamborzão chama, a rua vem", "pt"), 9)

    def test_rhyme_keys(self):
        self.assertEqual(lm.rhyme_key_romance("corazón"), lm.rhyme_key_romance("canción"))
        self.assertEqual(lm.rhyme_key_romance("noche"), lm.rhyme_key_romance("coche"))
        self.assertEqual(lm.rhyme_key_romance("coração", "pt"), lm.rhyme_key_romance("paredão", "pt"))
        self.assertNotEqual(lm.rhyme_key_romance("luna"), lm.rhyme_key_romance("noche"))

    def test_assonance_is_slant(self):
        self.assertEqual(lm.rhyme_scheme(["bajo la luna", "como ninguna", "prende la ciudad", "nadie va a mirar"], "es")[0], "AABb")

    def test_detect(self):
        self.assertEqual(lm.detect_lang("Baila conmigo, mami, que la noche es nuestra"), "es")
        self.assertEqual(lm.detect_lang("Eu quero dançar com você no baile"), "pt")


class Analyse(unittest.TestCase):
    def test_sections_and_warnings(self):
        text = "[Verse]\nline one is short\nline two is short\n\n[Chorus]\nshort\nthis is a very much longer line indeed\n"
        rep = lm.analyse(text, "en")
        self.assertEqual([s["tag"] for s in rep["sections"]], ["Verse", "Chorus"])
        self.assertTrue(any("[Chorus] line 2" in w for w in rep["warnings"]))

    def test_backing_vocals_skip_deviation(self):
        rep = lm.analyse("[Outro]\nMidnight bus, take me home\n(take me home)\n", "en")
        self.assertEqual(rep["warnings"], [])
        self.assertTrue(rep["sections"][0]["lines"][1].get("backing"))

    def test_auto_detect(self):
        self.assertEqual(lm.detect_lang("Северный ветер"), "ru")
        self.assertEqual(lm.detect_lang("Midnight bus"), "en")


if __name__ == "__main__":
    unittest.main()
