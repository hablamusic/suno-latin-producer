---
name: suno-latin-producer
description: Writes Suno-ready song briefs from a plain description: a one-line style prompt (genre, BPM, key, mood, instruments, production, vocal), a tagged structure ([Intro], [Verse], [Chorus], [Drop], [Outro]), lyrics that fit it, and A/B variants that change one axis at a time, then checks the result with a syllable/rhyme meter (Spanish, Brazilian Portuguese, English, Russian) and a tag lint, with a DJ-edit mode for clean intros and outros. Built for Latin and Brazilian genres (reggaeton, dembow, cumbia, bachata, corridos, funk carioca, piseiro) and club tracks DJs can mix. Use when the user asks for a Suno prompt, Suno style tags or meta-tags, a song structure, lyrics for Suno, an AI song or a DJ edit, "prompt para Suno", "letra para Suno", "canción de reggaetón con IA", "música com IA no Suno", or asks why Suno rushed or ignored a section. Not for mixing or mastering advice, for other music models' syntax, for reproducing existing copyrighted lyrics, or for imitating a named artist.
license: MIT
metadata:
  version: 0.2.0
  author: HablaMusic
  homepage: https://github.com/hablamusic/suno-latin-producer
---

# Suno Latin producer

Turn "a sad synthwave song about a night bus, female vocal" into something Suno can actually follow: a style prompt that describes sound rather than names, a tagged structure, lyrics whose lines are the same length inside each section, and two or three variants that differ in exactly one thing. The most common trigger is "write me a Suno prompt for ...". It is written for the two fields the Suno editor exposes, Style and Lyrics. The tag list and budgets were compiled against Suno v4.5 and later (v5.5 is current as of 2026-10); nothing here is a per-version spec, the editor shows the live limits and the lint budgets are flags you can override. The scripts are plain Python 3 with no packages. This is the HablaMusic edition of [suno-producer](https://github.com/uniqaiapp/suno-producer): Spanish and Portuguese meter and rhyme, Latin, Brazilian and club genres, and a DJ-edit mode.

## When to use

- The user wants a Suno prompt, style tags, meta-tags, or a lyrics layout with `[Section]` tags.
- The user has an idea ("reggaeton for my set, Spanish, male vocal", "funk de baile em português") and wants a complete brief: style, structure, lyrics.
- A DJ wants a track to mix: instrumental intro and outro, a tempo and key that fit the set (`--dj`).
- The user pastes lyrics or a style prompt and asks why Suno sang the tag names, rushed a section, ignored the chorus, or produced the wrong genre.
- The user wants to A/B test a song: which vocal, tempo or production change made the difference.
- Spanish or Portuguese lyrics (see `references/latin-vocals.md`): sung syllable counts (diphthongs, sinalefa) and assonant rhyme differ from English. Russian is also supported (`references/russian-vocals.md`).

## When NOT to use

- Mixing, mastering, stems, or anything after the generation step.
- Other models (Udio, MusicGen, Stable Audio): the tag vocabulary and field limits differ; only the lyric-craft part transfers.
- Requests to reproduce or lightly rewrite existing copyrighted lyrics. Decline and offer an original lyric on the same theme.
- "In the style of <living artist>". Suno rejects artist names and the request is an imitation; describe the sound instead (`references/style-prompts.md` has the translation table: artist → era, instruments, production, vocal).
- Instrumental-only requests that need no lyrics: use only step 2 and `scripts/brief.py`.

## How it works

1. **Clarify the brief in one question or none.** You need: genre (one, or two to fuse), mood, language of the vocal, vocal type (female / male / duet / none), rough length (short: five sections; standard: ten), and the song's one sentence ("what happens"). If the user gave most of this, do not ask; pick sensible defaults and say which you picked.

2. **Generate the skeleton.** Run

   ```bash
   python3 scripts/brief.py --genre "<genre>" [--fuse "<genre2>"] --mood <mood> --vocal <type> --lang en|es|pt|ru [--dj] [--bpm N] [--key "A minor"] --variants 3 --seed <any int>
   ```

   It prints: style prompt A plus variants B/C (each changes one axis: vocal, production, tempo), the section structure for that genre, and a lyric brief with lines-per-section and syllable targets. `--list` shows the available genres, moods, vocal types and structures; unknown genres fail loudly rather than guessing. The genre table is `references/genres.json`; extend it when the user's genre is missing instead of inventing descriptors in prose.

3. **Write the style prompt by hand if the generated one is off.** Rules (full list in `references/style-prompts.md`):
   - One line, comma-separated descriptors, most important first: genre, fusion genre, tempo (`104 BPM` or a feel word), key, two mood words, two or three instruments, one or two production words, the vocal, then language if not English.
   - Sound words, never names: no artists, bands, song titles or labels.
   - No `[tags]` in the style field, no sentences, no "a song about…" (that goes in the lyrics).
   - Keep it well under the field limit; the lint defaults to 1000 characters, override with `--max-style` if the editor shows another number.

4. **Write the lyrics into the structure.** Rules (details and examples in `references/lyric-craft.md`):
   - One tag per line, Capitalised, on its own line: `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`. Tags from `references/section-tags.md`; anything else may be sung aloud.
   - Lines inside a section stay within about two syllables of each other; verses 7–9 syllables in English, 8–10 in Spanish and Portuguese, choruses shorter and simpler than verses.
   - The chorus carries the title phrase on its first and last line and repeats verbatim each time. The bridge never reuses the title line.
   - Concrete nouns over abstractions; one scene per verse; the pre-chorus ends unresolved.
   - Backing vocals and ad-libs go in `(parentheses)` on their own line.
   - Nothing before the first tag; `[Intro]` first, `[Outro]` last; `[Instrumental]`, `[Guitar Solo]`, `[Drop]` may be empty.

5. **Check, then fix.** Run both scripts and act on every line they print:

   ```bash
   python3 scripts/lyric_meter.py lyrics.txt            # syllables per line, rhyme scheme per section, length drift
   python3 scripts/suno_lint.py lyrics.txt --style style.txt [--dj]   # tag, structure, budget, imitation and DJ-edit checks
   ```

   `lyric_meter` prints `[Verse 1]  4 lines · syllables 7-8 · scheme ABAB` per section and `!` warnings for lines that drift from the section median. Fix drift by cutting words, not by adding filler. Lowercase letters in a scheme are slant rhymes; decide whether they are intentional. `suno_lint` exits 1 on errors (unbalanced tags, artist phrases, over-budget fields) and lists warnings with stable rule ids (`L001`–`L017`); the README has the table.

6. **Deliver in this order, nothing else between the blocks:**

   ```
   Style (paste into Style):
   <one line>

   Lyrics (paste into Lyrics):
   [Intro]
   ...

   Variants to try (change one thing each):
   B (vocal): <line>
   C (production): <line>
   ```

   Then two or three sentences: what the user should listen for in A vs B vs C, and the one thing to change next if the chorus does not land (usually: shorter chorus lines, or a `[Pre-Chorus]` that ends unresolved).

7. **If the user comes back with a result** ("it sang the word Chorus", "the bridge is missing", "it rushed the second verse"), look up the symptom in `references/troubleshooting.md` and change one thing at a time; re-run the lint before handing back.

## Inputs / outputs

| Input | Output |
|---|---|
| A sentence describing the song (genre, mood, language, vocal) | Style prompt A + variants B/C, structure, lyric brief (`scripts/brief.py`) |
| Lyrics with `[Section]` tags | Syllables per line, rhyme scheme per section, drift warnings (`scripts/lyric_meter.py`) |
| Lyrics + style prompt | Errors/warnings with rule ids and line numbers, exit code (`scripts/suno_lint.py`) |
| A failed generation described in words | A single change from `references/troubleshooting.md` |

All scripts take `--json` for machine-readable output and `--help` for the flags.

## Examples

- `examples/lyrics/midnight-bus.txt` with `examples/style/midnight-bus.txt`: a complete English synthwave/indie-pop song that passes the lint clean; output in `examples/outputs/midnight-bus.*`.
- `examples/lyrics/luna-de-neon.es.txt`: a Spanish reggaeton DJ edit (empty [Intro]/[Outro]) that passes `--dj` clean; `examples/outputs/luna-de-neon.meter.txt` shows sinalefa and assonant rhyme.
- `examples/lyrics/baile-na-laje.pt.txt`: a Brazilian funk carioca DJ edit; `examples/outputs/baile-na-laje.meter.txt`.
- `examples/lyrics/bad-tags.txt`: a deliberately broken file that trips most lint rules; see `examples/outputs/bad-tags.lint.txt`.
- `python3 scripts/brief.py --genre reggaeton --mood playful --lang es --dj --seed 4` reproduces `examples/outputs/brief-reggaeton-dj.es.txt`.

`examples/README.md` lists the exact command for every committed output.

## Limits

- Syllable counts are heuristics: English is usually within one syllable of a dictionary count (words like "fire", "idea", "every" are the usual misses); Spanish and Portuguese follow spelling rules with sinalefa, so they match a sung phrase; loanwords and names ("DJ", "reggaetón") can be off by one. Russian counts vowels.
- Spanish/Portuguese rhyme uses the written-accent and penultimate-syllable rules, not a dictionary; English and Russian compare word endings without stress data.
- Field budgets (`--max-style`, `--max-lyrics`) are defaults, not a spec; the Suno editor shows the live limit.
- The genre table is editorial: typical tempo ranges and instrument lists, not measurements. Treat it as a starting point and edit `references/genres.json`.
- The scripts do not call Suno and cannot predict whether a generation will be good; they remove the known causes of bad ones.

## References

- `references/section-tags.md`: every tag the lint knows, what it does, and where it goes.
- `references/style-prompts.md`: descriptor order, vocabulary by axis, artist-to-sound translation, length rules.
- `references/lyric-craft.md`: syllable budgets, rhyme schemes, hook placement, cliché list, worked example.
- `references/latin-vocals.md`: Spanish and Portuguese vocals, syllable and rhyme rules, Latin/Brazilian genres, DJ edits.
- `references/russian-vocals.md`: Russian-language specifics.
- `references/ab-testing.md`: how to run one-axis variants and read the results.
- `references/troubleshooting.md`: symptom → single change.
- `references/genres.json`: the data behind `scripts/brief.py`.
