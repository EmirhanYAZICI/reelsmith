# Changelog

All notable changes to Reelsmith. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [1.3.2] - 2026-10-30

### Fixed
- Audio mix failed on ffmpeg 7+ builds that removed `-filter_complex_script`. The mix now uses `-/filter_complex` on ffmpeg 7+ and keeps the old option for ffmpeg 6. Found by the first Windows CI run.

### Added
- GitHub Actions CI: tests on Windows and Ubuntu, both installers on Windows, macOS and Ubuntu.
- `CHANGELOG.md`.

## [1.3.1] - 2026-10-30

### Added
- `verify.py`: post-render check for size, frame rate, codecs, loudness, true peak, frozen picture, faststart and duration. `build_video.py` runs it after every render.
- Verified install path: release zip plus `SHA256SUMS.txt`, read the script, then run it locally.
- `REELSMITH_REF` pins the version the remote installer clones.
- `TESTING.md` test report.

### Changed
- Installers check the real Python version (3.10-3.12) of the interpreter and of an existing `.venv`, and stop with a clear message otherwise.
- Installed skill folders are left alone when identical and backed up to `~/.reelsmith-backups/` before being replaced. `--no-backup` / `-NoBackup` opts out.
- `check.py` fails on unsupported Python versions.

## [1.3.0] - 2026-10-30

### Added
- `check.py` preflight: tools, scene script, clips (readable, vertical), voiceover, logo, font and options, with OK / WARN / FAIL output.
- Logo options: `--logo-mode=move|corner|ends`, `--logo-pos`, `--logo-size`, `--logo-moves`.
- English scene file names (`scene1.mp4`, `third scene.mp4`) and two more script formats (`Text:` lines, one paragraph per scene).
- pytest suite, issue templates, demo (before/after GIF, frames, full Reel).

### Changed
- Missing tools and ffmpeg failures are reported with the step and file instead of a traceback.
- Dependency ranges pinned; HyperFrames 0.8.

## [1.2.0] - 2026-10-30

### Added
- One-command installers `install.ps1` and `install.sh` for Claude Code, Codex, OpenCode, Cursor and Antigravity.
- Animated README banner and quick start.

## [1.1.0] - 2026-10-30

### Added
- Multi-agent skill pack layout (`skills/<name>/SKILL.md`), Claude Code plugin manifests, `AGENTS.md`.
- English caption flags: `--caption-color`, `--caption-outline`, `--caption-style`, `--caption-anim`.

## [1.0.0] - 2026-10-30

### Added
- First release: Instagram Reel from a folder with local Whisper captions, HyperFrames edit, moving logo watermark and a balanced audio mix.

[1.3.2]: https://github.com/EmirhanYAZICI/reelsmith/compare/v1.3.1...v1.3.2
[1.3.1]: https://github.com/EmirhanYAZICI/reelsmith/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/EmirhanYAZICI/reelsmith/releases/tag/v1.3.0
