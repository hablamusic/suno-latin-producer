# Examples

Every file in `outputs/` is produced by the command next to it, from the inputs in this folder. `python3 tests/run.py` re-runs each command and fails if the output differs by a byte; `python3 examples/regen.py` rewrites them after an intentional change. The list of commands is `manifest.json`.

| Output | Command | What it shows |
|---|---|---|
| `outputs/luna-de-neon.meter.txt` | `python3 scripts/lyric_meter.py examples/lyrics/luna-de-neon.es.txt` | Spanish reggaeton DJ edit: sung syllables with sinalefa, consonant and assonant rhyme |
| `outputs/baile-na-laje.meter.txt` | `python3 scripts/lyric_meter.py examples/lyrics/baile-na-laje.pt.txt` | Brazilian funk carioca DJ edit: Portuguese syllables (final -ua hiatus, nasal ão), rhyme |
| `outputs/midnight-bus.meter.txt` | `python3 scripts/lyric_meter.py examples/lyrics/midnight-bus.txt` | English synthwave / indie-pop song; no warnings |
| `outputs/midnight-bus.meter.json` | `python3 scripts/lyric_meter.py --json examples/lyrics/midnight-bus.txt` | Same report as JSON |
| `outputs/luna-de-neon.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/luna-de-neon.es.txt --dj --style examples/style/luna-de-neon.es.txt` | Clean pass with the DJ-edit rule |
| `outputs/baile-na-laje.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/baile-na-laje.pt.txt --dj --style examples/style/baile-na-laje.pt.txt` | Clean pass with the DJ-edit rule |
| `outputs/midnight-bus.dj-lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/midnight-bus.txt --dj --style examples/style/midnight-bus.txt` | L017: the English song has a sung outro, so it is not a DJ edit |
| `outputs/midnight-bus.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/midnight-bus.txt --style examples/style/midnight-bus.txt` | A clean pass |
| `outputs/bad-tags.lint.txt` | `python3 scripts/suno_lint.py examples/lyrics/bad-tags.txt --style examples/style/bad-style.txt` | Exit 1; most rules firing on a deliberately broken file |
| `outputs/brief-reggaeton-dj.es.txt` | `python3 scripts/brief.py --genre reggaeton --mood playful --lang es --dj --seed 4` | Spanish reggaeton DJ-edit brief: variants, perreo structure, Spanish lyric notes |
| `outputs/brief-funk-carioca-dj.pt.txt` | `python3 scripts/brief.py --genre "funk carioca" --mood euphoric --lang pt --dj --seed 2` | Portuguese funk carioca DJ-edit brief |
| `outputs/brief-cumbia-latin-house.es.txt` | `python3 scripts/brief.py --genre cumbia --fuse "latin house" --mood warm --lang es --seed 7` | Cumbia fused with latin house (tempo overlap) |
| `outputs/brief-house.json` | `python3 scripts/brief.py --genre house --mood euphoric --variants 4 --seed 11 --json` | Four variants (base, vocal, production, tempo) as JSON |
| `outputs/brief-list.txt` | `python3 scripts/brief.py --list` | Available genres, moods, vocal types and structures |

## Inputs

- `lyrics/luna-de-neon.es.txt` + `style/luna-de-neon.es.txt`: a Spanish reggaeton DJ edit (empty [Intro] and [Outro]), original lyrics written for this repo.
- `lyrics/baile-na-laje.pt.txt` + `style/baile-na-laje.pt.txt`: a Brazilian funk carioca DJ edit, original lyrics written for this repo.
- `lyrics/midnight-bus.txt` + `style/midnight-bus.txt`: a complete English song, original lyrics.
- `lyrics/bad-tags.txt` + `style/bad-style.txt`: a file that breaks most lint rules on purpose.

All lyrics here are original and released under the repo's MIT license. Do not add copyrighted lyrics as examples.
