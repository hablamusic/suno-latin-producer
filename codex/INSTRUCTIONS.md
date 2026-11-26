# suno-latin-producer for Codex

Paste the block below into your project's AGENTS.md (or Codex custom instructions),
and copy `SKILL.md`, `scripts/` and `references/` from https://github.com/hablamusic/suno-latin-producer into `.agents/skills/suno-latin-producer/`.

---
When the user asks for a Suno prompt, Suno style tags or meta-tags, a song structure, lyrics for Suno, or an A/B variant of a song (in Spanish, Portuguese or English; "prompt para Suno", "letra para Suno", a DJ edit), follow `.agents/skills/suno-latin-producer/SKILL.md`. Run `python3 .agents/skills/suno-latin-producer/scripts/suno_lint.py` and `lyric_meter.py` on the result before handing it back.
---
