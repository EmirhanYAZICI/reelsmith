# Test report / Test raporu

What is tested, how, and where. Updated with each release.
Neyin, nasıl ve nerede test edildiği. Her sürümde güncellenir.

## Automated tests (pytest)

Run: `pip install -r requirements-dev.txt && python -m pytest tests`

| File | What it proves |
|---|---|
| `tests/test_common.py` | Scene file names (`scene1`, `1sahne`, `4sahen`, `third scene`...) map to the right scene; other files are ignored; the three script formats parse; caption and logo options accept valid values and reject bad ones with a message; scene timing is split and overlapped correctly |
| `tests/test_align.py` | Whisper-to-script alignment: exact match keeps script spelling and Whisper times; a misheard word gets the right time but the script spelling; words Whisper missed are filled in order; scene boundaries follow the first spoken word; caption blocks cover every word once, stay 1-3 words and never cross a scene; empty input gives a clear error |
| `tests/test_check.py` | Preflight on real generated media: a complete folder is READY; a missing scene clip, a corrupt clip, a missing logo, a bad option and a missing folder FAIL with the reason; a landscape clip only warns |
| `tests/test_pipeline.py` | Full build without the final render on generated clips: clips come out 1080x1920 at 30 fps; a clip shorter than its scene is slowed to cover it; a clip with no sound gets silence; composition data carries the caption and logo options; the audio mix matches the timeline length; the composition passes `hyperframes lint` (when HyperFrames is installed) |
| `tests/test_verify.py` | Output check: a correct Reel passes; wrong size, wrong frame rate, a frozen picture, no audio, missing faststart, wrong duration and an unreadable file all FAIL with the reason |

## Installer scenarios

Checked by hand on Windows 11 with both `install.ps1` and `install.sh` (Git Bash), in an isolated home folder:

| Scenario | Expected | Result |
|---|---|---|
| Fresh install | Skills copied | Pass |
| Run again, nothing changed | "already up to date", nothing touched | Pass |
| User edited the installed skill | Old copy moved to `~/.reelsmith-backups/<time>/<agent>/`, new copy installed | Pass |
| Existing `.venv` uses Python 3.14 | Stops with "needs 3.10-3.12" and how to fix it | Pass |
| `--dry-run` / `-DryRun` | Prints the plan, changes nothing | Pass |

CI (`.github/workflows/ci.yml`) repeats the install on Windows, macOS and Ubuntu and checks that every agent folder received both skills.

## End-to-end render

| Project | Machine | Result |
|---|---|---|
| Zebercet / Taş Galerisi, 7 scenes, 2:22 | Windows 11, Intel i5-13420H, 16 GB RAM, Python 3.12.9, ffmpeg 8.1.1, HyperFrames 0.8.216 | `verify.py`: 1080x1920, 30 fps, H.264 + AAC 48 kHz, -14.5 LUFS, true peak -0.9 dBFS, 0 frozen sections, faststart. All checks passed |

The alignment code was refactored in 1.3.0; re-running it on the Zebercet transcript produced the same scene times and the same 97 caption blocks as the original render.

## Last local run

2026-10-30, Windows 11, Python 3.12.9, ffmpeg 8.1.1, HyperFrames 0.8.216: **63 passed**.

## Not covered yet

- A full HyperFrames render inside CI (it needs Chromium and takes minutes; the composition is linted instead).
- Real Whisper transcription inside CI (the model download is large; alignment is tested with Whisper-shaped data).
- macOS and Linux end-to-end renders (installer and unit tests only).
