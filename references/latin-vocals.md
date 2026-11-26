# Spanish and Portuguese vocals, Latin genres, DJ edits

What changes when the song is in Spanish or Brazilian Portuguese, or when it is meant to be played in a DJ set. Everything else (tags, structure, the Style field) works as in English.

## Language in the Style field

- Write the Style field in English: the model reads descriptors, not the song's language. Set the language once, at the end: `Spanish-language vocals, Latin American Spanish` or `Brazilian Portuguese vocals, clear diction`. `brief.py --lang es` / `--lang pt` adds them.
- For a Caribbean or Rioplatense accent, say it in one word (`Caribbean Spanish`, `Rioplatense Spanish`); for Portugal, `European Portuguese vocals`. One accent word only.
- Lyrics stay in the language of the song. Do not translate tags: `[Chorus]`, not `[Coro]` or `[Refrão]`, which the model may sing.

## Counting syllables the way they are sung

`lyric_meter.py --lang es|pt` (auto-detected when the lyrics are clearly Spanish or Portuguese):

- **Diphthongs are one syllable** (`cie-lo`, `bai-le`, `cou-ro`); two strong vowels are two (`po-e-ta`, `pe-rre-o`); a written accent on i/u breaks the diphthong (`dí-a`, `ra-íz`).
- **Portuguese final -ia/-io/-ua** after a consonant counts as two (`di-a`, `ru-a`, `fri-o`), as it is sung. Nasal `ão`, `õe`, `ãe` are one (`co-ra-ção`).
- **Sinalefa / elisão:** a word that ends in a vowel and a word that starts with a vowel (or a silent h) merge: `te a-mo` is two sung syllables, `has-ta el a-ma-ne-cer` is six. This is what a singer does, so the count matches the phrase length, not the dictionary.
- Budgets: verses 8–10 syllables in Spanish, 7–10 in Portuguese; choruses 6–9; hooks 5–8. Spanish and Portuguese lines run one or two syllables longer than English for the same bar, because unstressed syllables are shorter.

## Rhyme

- The rhyme key runs from the stressed vowel (written accent, else the penultimate syllable for words ending in a vowel, `n` or `s` in Spanish, `-a/-e/-o/-as/-es/-os/-em/-am` in Portuguese, else the last).
- **Consonant rhyme** (`corazón` / `canción`, `noche` / `coche`) is a full rhyme: uppercase in the scheme.
- **Assonance** (same vowels, `luna` / `cuna` / `ciudad` / `mirar`) is a slant rhyme: lowercase. Assonant rhyme is normal in reggaeton, cumbia and funk; the meter just shows it so the choice is yours.

## Latin and Brazilian genres in `genres.json`

reggaeton, dembow, latin trap, cumbia, bachata, salsa, merengue, corridos tumbados, latin pop, moombahton, guaracha, latin house, funk carioca, brazilian phonk, piseiro, sertanejo, pagode, plus club genres DJs mix them with (tech house, afro house, amapiano, house, techno). Tempo ranges are editorial defaults; check a reference track with the [BPM and key finder](https://hablamusic.github.io/bpm-key-finder/) and override with `--bpm`.

Genre words carry most of the weight. `dembow drums`, `tamborzão drums`, `güiro`, `requinto guitar`, `log drums`, `cavaquinho` are understood; name the instrument rather than the scene.

## DJ edits

A DJ needs bars at both ends of a track with no vocal, so it can be beatmatched in and out of the next one.

- `brief.py --dj` adds `extended instrumental intro, extended instrumental outro, DJ-friendly arrangement` to every variant and turns the [Intro] and [Outro] notes into "keep this instrumental".
- In the lyrics, leave `[Intro]` and `[Outro]` empty (just the tag). `suno_lint.py --dj` warns (`L017`) when the first tag is not [Intro], the last is not [Outro], or either one has sung lines.
- Generated intros are often shorter than 16 bars. If the intro is too short for a long blend, loop the first bars in the DJ software or extend it with the "extend" feature from a point before the first vocal.
- Pick the key from the Camelot wheel of the set you are building: a key in the prompt is a request the model often ignores, so measure the result before you tag it. On 19 AI-generated tracks the model followed the prompt's tempo almost every time and its key once ([measured](https://github.com/hablamusic/bpm-key-finder#accuracy-tested-on-19-ai-generated-tracks)).

## Artist references

Suno rejects artist names, and the lint flags `al estilo de` and `no estilo de` as well as the English phrases (`L007`). Translate the reference into sound: era, instruments, production, vocal. A named reggaeton star becomes `reggaeton, 94 BPM, F minor, dembow drums, deep 808 bass, sub-heavy club mix, smooth male vocal with autotune, Spanish-language vocals`.
