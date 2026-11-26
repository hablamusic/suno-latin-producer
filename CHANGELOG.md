# Changelog

All notable changes to this project are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [0.2.0] - 2026-11-26

HablaMusic edition, forked from [uniqaiapp/suno-producer](https://github.com/uniqaiapp/suno-producer) 0.1.0.

### Added

- Spanish and Brazilian Portuguese in `lyric_meter.py` (`--lang es|pt`, auto-detected): diphthongs, hiatus, written accents, Portuguese final -ia/-ua hiatus, sinalefa/elisão across words; rhyme from the stressed vowel, consonant rhyme as full and assonance as slant.
- `brief.py --lang es|pt` with Spanish/Portuguese lyric briefs and language descriptors; `--dj` for DJ edits (extended instrumental intro and outro).
- `suno_lint.py --dj`: rule `L017` (instrumental [Intro] first and [Outro] last); Spanish/Portuguese artist-imitation phrases for `L007`.
- 19 Latin, Brazilian and club genres in `references/genres.json` (dembow, latin trap, cumbia, bachata, salsa, merengue, corridos tumbados, latin pop, moombahton, guaracha, latin house, tech house, afro house, amapiano, funk carioca, brazilian phonk, piseiro, sertanejo, pagode) and a `perreo` structure.
- `references/latin-vocals.md`; Spanish and Portuguese example songs (DJ edits) with committed outputs.
- In-browser version on GitHub Pages (EN/ES/PT): https://hablamusic.github.io/suno-latin-producer/
- README in English, Spanish and Portuguese with a beginner path.

### Removed

- The Russian genre presets and Russian example song (Russian syllable counting stays), and the Chinese, Japanese, Korean and Russian READMEs of the original.

## [0.1.0] - 2026-10-28 (upstream, UniqAI)

### Added

- `SKILL.md`: the Suno producer skill (brief → style prompt → structure → lyrics → checks → delivery), with Claude Code, Cursor and Codex adapters.
- `scripts/brief.py`: style prompt with one-axis A/B/C variants, section structure and lyric brief from `references/genres.json` (23 genres, 7 moods, 5 vocal types, 8 structures).
- `scripts/lyric_meter.py`: syllable counter (English heuristic, Russian vowel count), rhyme scheme per section with full/slant marking, drift warnings, JSON output.
- `scripts/suno_lint.py`: 16 lint rules (`L001`–`L016`) for tags, structure, budgets and artist-imitation phrases in lyrics and style prompts.
- References: section tags, style prompt vocabulary and artist-to-sound translation, lyric craft, Russian vocals (in Russian), A/B testing, troubleshooting.
- Examples: an English synthwave/indie-pop song, a Russian rock ballad, a deliberately broken file, and committed outputs reproduced by the tests.
- Tests (`python3 tests/run.py`): meter, lint, brief data and determinism, script help/version, byte-for-byte example reproduction, adapter consistency and forbidden strings.
- Animated README banner, terminal demo and social preview from the shared uniqaiapp design kit.
