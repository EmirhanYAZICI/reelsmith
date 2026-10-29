# AGENTS.md

This repository contains two agent skills in the open `SKILL.md` format:

| Skill | Path | Purpose |
|---|---|---|
| `reelsmith-media` | `skills/reelsmith-media/SKILL.md` | Build an Instagram Reel from a folder (voiceover, scene clips, scene script, logo) |
| `whisper-tr` | `skills/whisper-tr/SKILL.md` | Local Whisper transcription with word timestamps (Turkish by default) |

If your tool does not load skills automatically, read the matching `SKILL.md` when the user asks for a Reel, a captioned vertical video, or a Whisper transcript. Then follow its steps exactly.

Requirements: the agent must be able to run shell commands locally (Python, ffmpeg, Node.js). Web chat apps without a local shell cannot run this workflow.

The skill docs (`SKILL.md`, `REELS-REHBERI.md`) are written in Turkish. `CAPTION-STYLES.md` and `README.md` are bilingual (English / Turkish).
