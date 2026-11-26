import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import brief  # noqa: E402

DATA = brief.load_data()


class GenreData(unittest.TestCase):
    def test_every_genre_is_complete(self):
        for name, g in DATA["genres"].items():
            for k in ("bpm", "keys", "feel", "instruments", "production", "default_vocal", "structure"):
                self.assertIn(k, g, "%s missing %s" % (name, k))
            lo, hi = g["bpm"]
            self.assertTrue(30 <= lo < hi <= 220, name)
            self.assertIn(g["default_vocal"], DATA["vocals"], name)
            self.assertIn(g["structure"], DATA["structures"], name)
            self.assertGreaterEqual(len(g["instruments"]), 2, name)
            self.assertGreaterEqual(len(g["production"]), 2, name)
            self.assertEqual(name, name.lower(), name)

    def test_structures_have_a_repeated_section(self):
        for name, secs in DATA["structures"].items():
            bases = [brief.base(s) for s in secs]
            self.assertTrue(any(b in bases for b in ("chorus", "hook", "drop")), name)


class Build(unittest.TestCase):
    def test_deterministic(self):
        a = brief.build(DATA, "synthwave", "indie pop", "melancholic", seed=7)
        b = brief.build(DATA, "synthwave", "indie pop", "melancholic", seed=7)
        self.assertEqual(a, b)
        c = brief.build(DATA, "synthwave", "indie pop", "melancholic", seed=8)
        self.assertNotEqual(a["style_prompts"], c["style_prompts"])

    def test_variants_change_one_axis(self):
        b = brief.build(DATA, "house", mood="euphoric", variants=4, seed=3)
        self.assertEqual(b["style_prompts"][0]["axis"], "base")
        base_parts = b["style_prompts"][0]["prompt"].split(", ")
        for v in b["style_prompts"][1:]:
            parts = v["prompt"].split(", ")
            self.assertEqual(len(parts), len(base_parts), v)
            diff = [i for i, (x, y) in enumerate(zip(base_parts, parts)) if x != y]
            self.assertEqual(len(diff), 1, (v["axis"], diff))

    def test_bpm_overlap_and_overrides(self):
        b = brief.build(DATA, "synthwave", "indie pop", "warm", seed=1)
        self.assertEqual(b["bpm_range"], [98, 118])
        self.assertTrue(98 <= b["bpm"] <= 118)
        b = brief.build(DATA, "synthwave", mood="warm", bpm=100, key="D minor", seed=1)
        self.assertEqual(b["bpm"], 100)
        self.assertIn("100 BPM", b["style_prompts"][0]["prompt"])
        self.assertIn("D minor", b["style_prompts"][0]["prompt"])

    def test_language_words(self):
        b = brief.build(DATA, "reggaeton", mood="playful", lang="es", seed=1)
        self.assertIn("Spanish-language vocals", b["style_prompts"][0]["prompt"])
        self.assertTrue(all(item["note"] for item in b["lyric_brief"]))
        b = brief.build(DATA, "funk carioca", mood="euphoric", lang="pt", seed=1)
        self.assertIn("Brazilian Portuguese vocals", b["style_prompts"][0]["prompt"])
        b = brief.build(DATA, "indie rock", mood="dark", lang="ru", seed=1)
        self.assertIn("Russian-language vocals", b["style_prompts"][0]["prompt"])
        self.assertTrue(all(item["note"] for item in b["lyric_brief"]))
        b = brief.build(DATA, "ambient", mood="dreamy", lang="ru", seed=1)
        self.assertNotIn("Russian-language vocals", b["style_prompts"][0]["prompt"])  # instrumental

    def test_dj_edit(self):
        b = brief.build(DATA, "dembow", mood="playful", lang="es", seed=2, dj=True)
        for v in b["style_prompts"]:
            self.assertIn("extended instrumental intro", v["prompt"])
            self.assertIn("extended instrumental outro", v["prompt"])
        notes = {i["section"]: i["note"] for i in b["lyric_brief"]}
        self.assertIn("instrumental", notes["Intro"])
        self.assertIn("instrumental", notes["Outro"])
        plain = brief.build(DATA, "dembow", mood="playful", lang="es", seed=2)
        self.assertNotIn("DJ-friendly", plain["style_prompts"][0]["prompt"])

    def test_latin_genres_present(self):
        for g in ("reggaeton", "dembow", "cumbia", "bachata", "salsa", "corridos tumbados", "funk carioca", "piseiro", "guaracha"):
            self.assertIn(g, DATA["genres"])

    def test_unknown_inputs_fail_loudly(self):
        with self.assertRaises(SystemExit):
            brief.build(DATA, "polka metal")
        with self.assertRaises(SystemExit):
            brief.build(DATA, "house", mood="confused")


if __name__ == "__main__":
    unittest.main()
