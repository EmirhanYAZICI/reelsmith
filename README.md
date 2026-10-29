<div align="center">

<img src="assets/banner.svg" width="100%" alt="Reelsmith Media: an AI agent turns a folder with a voiceover, scene clips, a script and a logo into a captioned 1080x1920 Instagram Reel"/>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=23F7DD&center=true&vCenter=true&width=900&lines=Folder+in.+Instagram+Reel+out.;Local+Whisper+captions%2C+no+API+keys;Claude+Code%2C+Codex%2C+Cursor%2C+OpenCode%2C+Antigravity" alt="Folder in. Instagram Reel out."/>

<a href="#quick-start"><img src="https://img.shields.io/badge/skills.sh-npx_skills_add-000000?style=for-the-badge&labelColor=23F7DD" alt="Install with npx skills add"/></a>
<a href="#quick-start"><img src="https://img.shields.io/badge/Claude_Code-Skill_%2B_Plugin-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code skill and plugin"/></a>
<a href="#quick-start"><img src="https://img.shields.io/badge/Agent_Skills-SKILL.md-23F7DD?style=for-the-badge&labelColor=000000" alt="Open SKILL.md format"/></a>
<img src="https://img.shields.io/badge/Whisper-local-412991?style=for-the-badge&logo=openai&logoColor=white" alt="Local Whisper"/>
<img src="https://img.shields.io/badge/HyperFrames-GSAP-88CE02?style=for-the-badge&logo=greensock&logoColor=black" alt="HyperFrames"/>
<img src="https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white" alt="FFmpeg"/>
<a href="#cost"><img src="https://img.shields.io/badge/Paid_API-none-2EA44F?style=for-the-badge&labelColor=000000" alt="No paid API"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-white?style=for-the-badge&labelColor=000000" alt="MIT License"/></a>
<br/>
<a href="https://github.com/EmirhanYAZICI/reelsmith-media/actions/workflows/ci.yml"><img src="https://github.com/EmirhanYAZICI/reelsmith-media/actions/workflows/ci.yml/badge.svg" alt="CI"/></a>
<a href="https://skills.sh/EmirhanYAZICI/reelsmith-media"><img src="https://skills.sh/b/EmirhanYAZICI/reelsmith-media" alt="skills.sh installs"/></a>

An agent skill that turns a folder of raw material into a finished, Instagram-ready vertical Reel.

[Demo](#demo) · [Cost](#cost) · [Quick start](#quick-start) · [How it works](#how-it-works) · [Options](#captions-fixed-placement-flexible-look) · [FAQ](#faq) · [Türkçe](#türkçe)

</div>

---

## Demo

A real project made with Reelsmith Media: a 7-scene, 2:22 Reel about the gemstone "Zebercet" (peridot) for Taş Galerisi.

<div align="center">

<img src="assets/demo-before-after.gif" width="540" alt="Left: the raw scene clip. Right: the same scene in the finished Reel with slow camera move, captions and the logo watermark"/>

<img src="assets/demo-frames.jpg" width="100%" alt="Five frames from the finished Reel, each with word-timed yellow captions and the moving logo"/>

**[Watch the full Reel (2:22, 48 MB)](https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v1.3.0/reelsmith-demo-zebercet.mp4)**

</div>

| | Input | Output |
|---|---|---|
| Video | 7 clips, 10 s each, 720x1280, no captions | 2:22, 1080x1920, 30 fps, H.264 + AAC |
| Audio | 2:22 voiceover + the clips' own sound | -14 LUFS, peak -0.9 dBFS, clip sound ducked under speech |
| Text | Scene script, 239 words | 97 word-timed caption blocks |
| Brand | `logo.png` | Moving watermark, corner to corner |

Time: about 15-25 minutes for a 2-3 minute Reel on a mid-range laptop (tested on Intel i5-13420H, 16 GB RAM), mostly clip slow-motion and the render. Whisper and alignment take under a minute.

## Why Reelsmith Media

- **You keep the creative part.** You write the script, pick the voice and generate the clips. The skill does the slow, repetitive part: timing, captions, transitions, logo, audio mix and export.
- **Captions match your script, not a guess.** Whisper gives the timing; your script gives the spelling. Brand names and special words come out exactly as you wrote them.
- **Same look every time.** Caption placement, camera motion, loudness and export settings are fixed, so a series of Reels looks like one brand.
- **Checked before and after.** A preflight check catches missing or broken files before the slow steps start, and an output check confirms size, frame rate, loudness and that no part of the video froze.
- **Any brand, any agent.** The logo in the folder is the brand. The same skill runs in Claude Code, Codex, Cursor, OpenCode and Antigravity.

## Cost

No paid API, no API key, no per-video fee. Whisper, alignment, clip preparation, the HyperFrames render and the audio mix all run on your own machine.

The only tokens spent are your agent's. The agent reads about 20K tokens of instructions (the skill, its guide and OpenMontage's `AGENT_GUIDE.md`) and runs around ten short commands. Video and audio never go through the model; it only sees file lists, short command output and the check results. On a subscription plan (Claude Pro/Max, ChatGPT Plus and so on) a Reel uses part of your normal limit; nothing is billed per video.

---

## Quick start

### Fastest: one line with the skills CLI

```bash
npx skills add EmirhanYAZICI/reelsmith-media
```

The open [skills](https://skills.sh/EmirhanYAZICI/reelsmith-media) CLI copies both skills (`reelsmith-media` and `whisper-tr`) into Claude Code, Cursor, Codex, OpenCode, Antigravity and other agents. It asks which agents to install for.

This adds the skills only. The video tools (ffmpeg, Python 3.10-3.12 with faster-whisper, HyperFrames, OpenMontage) still have to be on your machine. The installer below sets them up, and the skill's preflight check tells you exactly what is missing.

### Install everything with one command

The installer checks the tools, gets OpenMontage, creates its Python environment, installs faster-whisper and HyperFrames, and copies the skills into every agent it finds on your machine.

```powershell
# Windows (PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith-media/main/install.ps1)))
```

```bash
# macOS / Linux / Git Bash
curl -fsSL https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith-media/main/install.sh | bash
```

### Verified install (read the script first)

Prefer to read the script before it runs, or want a fixed version? Download the release, check its SHA-256, read `install.ps1` / `install.sh`, then run it from the folder. It uses the downloaded files and clones nothing.

```powershell
# Windows (PowerShell)
irm https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v2.0.0/reelsmith-media-v2.0.0.zip -OutFile reelsmith-media-v2.0.0.zip
irm https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v2.0.0/SHA256SUMS.txt -OutFile SHA256SUMS.txt
(Get-FileHash reelsmith-media-v2.0.0.zip -Algorithm SHA256).Hash   # must match the line in SHA256SUMS.txt
Expand-Archive reelsmith-media-v2.0.0.zip .; notepad reelsmith-media\install.ps1
powershell -ExecutionPolicy Bypass -File reelsmith-media\install.ps1
```

```bash
# macOS / Linux / Git Bash
curl -fsSLO https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v2.0.0/reelsmith-media-v2.0.0.zip -fsSLO https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v2.0.0/SHA256SUMS.txt
sha256sum -c SHA256SUMS.txt --ignore-missing      # macOS: shasum -a 256 -c SHA256SUMS.txt --ignore-missing
unzip -q reelsmith-media-v2.0.0.zip && less reelsmith-media/install.sh
./reelsmith-media/install.sh
```

The installer never deletes your edits. If an installed `reelsmith-media` or `whisper-tr` folder differs from the new one, it is moved to `~/.reelsmith-backups/<time>/` first. It requires Python 3.10-3.12 and stops with a clear message otherwise.

### Install for one agent only

| Agent | Install | Then |
|---|---|---|
| **Claude Code** | `/plugin marketplace add EmirhanYAZICI/reelsmith-media`<br/>`/plugin install reelsmith-media@reelsmith-media` | Type `/reelsmith-media my-brand` |
| **OpenAI Codex CLI** | installer with `-Agents codex` / `--agents=codex` | Ask: *use the reelsmith-media skill on my-brand* |
| **Cursor** | installer with `-Agents cursor` / `--agents=cursor` | Ask in Agent chat: *use the reelsmith-media skill on my-brand* |
| **OpenCode** | installer with `-Agents opencode` / `--agents=opencode` | Ask: *use the reelsmith-media skill on my-brand* |
| **Google Antigravity** | installer with `-Agents antigravity` / `--agents=antigravity` | Ask: *use the reelsmith-media skill on my-brand* |
| **Any other agent** | `npx skills add EmirhanYAZICI/reelsmith-media` | It reads [`AGENTS.md`](AGENTS.md) if it has no skill support |

From a clone of this repo: `.\install.ps1 -Agents codex` or `./install.sh --agents=codex`.

### Prepare your material

Reelsmith Media edits your clips; it does not generate them. Make them first:

1. **Write the script, scene by scene.** Split the narration into scenes (5-10 is typical). Each scene's text is exactly what the voiceover says during that scene.
2. **Generate one clip per scene, in order,** with any video tool: Google Gemini (Veo), Kling, Runway, Sora, or your own footage. Vertical 9:16, about 8-10 seconds each. Write each prompt from that scene's text. The clips can keep their own music and sound effects; Reelsmith Media keeps them and lowers them under the voice.
3. **Name the clips by scene number:** `scene1.mp4`, `scene2.mp4`, ... The number decides which scene a clip belongs to. Two clips for one scene: `scene3.mp4` and `scene3_b.mp4`.
4. **Record or generate the voiceover** reading the script, in the same order.
5. **Add your logo** as a transparent `logo.png`.

Example script (`script.txt`), one paragraph per scene:

```
This green stone comes from deep inside the Earth.

Volcanoes carry its crystals up to the surface.

Some of it even fell from space, inside meteorites.
```

### Make a Reel

Put your files in a folder on the Desktop:

```
my-brand/
├── voiceover.mp3      the narration
├── scene1.mp4         scene 1 clip   (scene2.mp4, scene3.mp4 ...)
├── script.txt         the text of each scene
└── logo.png           your logo, used as the moving watermark
```

Then call the skill. Caption wishes in plain words are optional:

```
/reelsmith-media my-brand reel.mp4 white text, box style, word by word
```

Before anything slow starts, the agent runs a preflight check and tells you what is missing or broken: a missing scene number, a corrupt clip, no logo, a missing tool. You can run it yourself too:

```bash
python skills/reelsmith-media/template/scripts/check.py --src=~/Desktop/my-brand
```

The finished `reel.mp4` is saved in `my-brand/` and in a `cikti/` folder next to it.

---

## How it works

1. **Transcribes the voiceover locally with Whisper** (faster-whisper, Turkish by default). It produces word-level timestamps and needs no API key and no paid service.
2. **Aligns the transcript to your script.** Captions use your spelling, not Whisper's guesses. Scene boundaries come from when each scene's text is actually spoken.
3. **Fits every clip to its scene.**
   - Each ~10 s clip is slowed down to match the length of its narration.
   - Motion-compensated frame interpolation (ffmpeg `minterpolate`) keeps the slowdown smooth.
   - Clips are cropped to 9:16 and lightly color-graded.
4. **Builds the edit with HyperFrames (HTML + GSAP):**
   - crossfade transitions with a light leak
   - one slow, continuous camera move per scene (no sudden zooms)
   - film grain and dust overlay
   - word-timed captions, 2-3 words per block
5. **Adds a moving logo watermark.** Your logo glides slowly from corner to corner for the whole video, which makes the Reel hard to crop and re-upload. It is kept exactly as uploaded: full opacity, no effects.
6. **Mixes the audio:**
   - The voiceover is normalized to -14 LUFS.
   - The clips keep their own music and sound effects, ducked by 9 dB while someone speaks.
   - A soft whoosh plays on scene changes.
   - A limiter caps peaks at about -1 dBFS.
7. **Renders and checks the result:** 1080x1920, 30 fps, H.264 High + AAC, `faststart`. The output check verifies size, frame rate, codecs, loudness, peak, frozen sections and duration, then the video is copied next to your source files.

### Captions: fixed placement, flexible look

Captions always sit in the same place: Calibri Bold 75 px, 450 px from the bottom, centered. Only the look changes:

| Option | Default | Values |
|---|---|---|
| `--caption-color` | `yellow` | `yellow`, `white`, `green`, `gold`, `orange`, `red`, `pink`, `blue`, `purple`, `black`, or any `#RRGGBB` |
| `--caption-outline` | `#000000` | same list (outline / shadow color) |
| `--caption-style` | `outline` | `outline`, `box`, `shadow`, `double` |
| `--caption-anim` | `pop` | `pop`, `hop`, `word-hop` (each word jumps in exactly when it is spoken), `bounce`, `wave` |

Through an agent you can describe the captions in plain words, for example: `/reelsmith-media my-folder white text, boxed, words hop in one by one`.
See [`CAPTION-STYLES.md`](skills/reelsmith-media/CAPTION-STYLES.md) for the full list and ready-made presets.

### Logo: moving, fixed or intro/outro

| Option | Default | Values |
|---|---|---|
| `--logo-mode` | `move` | `move` (glides corner to corner, hard to crop out), `corner` (stays in one corner), `ends` (large and centered at the start and the end). `ends` combines with the others: `move,ends`, `corner,ends` |
| `--logo-pos` | `bottom-left` | `bottom-left`, `bottom-right`, `top-left`, `top-right` (start corner for `move`, the corner for `corner`) |
| `--logo-size` | `258` | width in px, 80-700 |
| `--logo-moves` | `6` | how many corner-to-corner moves over the whole video (fewer = slower) |

The logo is always used as uploaded: original colors, full opacity, no effects. You can say it in words too: `/reelsmith-media my-folder logo fixed top right, also big at the start and end`.

---

## Requirements

| Tool | Notes |
|---|---|
| An agent with a local shell | Claude Code, Cursor, Codex CLI, OpenCode, Antigravity... Web chat apps without a local shell cannot run it |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Workspace and Python 3.12 virtual environment |
| Python packages | `faster-whisper`, `numpy` (see `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes@0.8` (tested with 0.8.x) |
| ffmpeg / ffprobe | Must be on `PATH` |
| Calibri Bold font | Ships with Windows (`C:\Windows\Fonts\calibrib.ttf`). It is **not** included here for licensing reasons. On other systems pass `--font=<path>` |

## Install in detail

### Installer options

From a clone: `.\install.ps1` or `./install.sh`.

| PowerShell | Bash | Effect |
|---|---|---|
| `-Agents claude,cursor` | `--agents=claude,cursor` | Pick agents (`auto` = found on this machine, `all`) |
| `-Project` | `--project` | Install into the current project folder instead of your home |
| `-OM <path>` | `--om=<path>` | OpenMontage location |
| `-SkillsOnly` | `--skills-only` | Copy the skills only, skip dependencies |
| `-NoBackup` | `--no-backup` | Replace changed skill folders without keeping a backup |
| `-DryRun` | `--dry-run` | Show what would happen, change nothing |

The installer does not install system tools for you. If `git`, `node`, `ffmpeg` or Python 3.10-3.12 is missing, it stops and prints the command (`winget`, `brew`, `apt`). It checks the real version of the Python it would use (and of an existing `.venv`), not just the command name. It only touches the `reelsmith-media` and `whisper-tr` folders in each skills folder: identical copies are left alone, changed ones are backed up first. An old `reelsmith` folder from version 1.x is moved to the backup folder too.

### Manual install

**1. Shared dependencies (once)**

```bash
OM=~/Projects/OpenMontage                      # wherever OpenMontage lives
$OM/.venv/Scripts/python.exe -m pip install faster-whisper numpy   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes@0.8
npx hyperframes skills                         # official HyperFrames skills for your agents
```

If OpenMontage is not in `~/Projects/OpenMontage`, set the `OPENMONTAGE_DIR` environment variable to its path.

**2. The skills**

Copy `skills/reelsmith-media` and `skills/whisper-tr` into your tool's skills folder:

| Tool | Skills folder (user-wide / per project) |
|---|---|
| Claude Code | `~/.claude/skills/` / `.claude/skills/` |
| OpenAI Codex | `~/.codex/skills/` / `.codex/skills/` |
| OpenCode | `~/.config/opencode/skills/` / `.opencode/skills/` |
| Cursor | `~/.cursor/skills/` / `.cursor/skills/` |
| Google Antigravity | `~/.gemini/antigravity/skills/` / `.agent/skills/` |

Folder names can change between tool versions. If a path does not work, check your tool's docs or use `npx skills add`.
Tools that do not load skills still read [`AGENTS.md`](AGENTS.md), which points them to the right `SKILL.md`.

To check the install in Claude Code, type `/`. You should see `reelsmith-media` and `whisper-tr`.

## Usage in detail

| File | Rule |
|---|---|
| Voiceover | Name contains `voice`, `vo` or `seslendirme` (`.mp3`, `.wav`, `.m4a`) |
| Scene clips | `scene1.mp4`, `scene2.mp4`, ... (Turkish `1sahne.mp4` also works). Vertical, about 10 s each. Their own audio is kept |
| Scene script | `.txt` or `.md` with exactly the text spoken in each scene: one paragraph per scene (blank line between), or one `Text: "..."` line per scene |
| Logo | `logo.png`, transparent background |
| Optional | A `REELS-REHBERI.md` (or any `*.md` guide) with project-specific rules. It overrides the bundled guide |

You can use any number of scenes. The number of scenes in the clips and in the script must match.

```
/reelsmith-media <folder name or path> <output_name>.mp4 [caption and logo wishes]
```

To run it by hand without an agent, see step 3 in [`skills/reelsmith-media/SKILL.md`](skills/reelsmith-media/SKILL.md).

## Supported and not supported

| Supported | Not supported (yet) |
|---|---|
| Vertical 1080x1920 at 30 fps | Other sizes or frame rates (16:9, 1:1, 60 fps) |
| Any number of scenes, one or more clips per scene | Cutting clips on music beats (clips are fitted to the narration) |
| Turkish voiceover out of the box | Other languages need a one-line change (`language="tr"` in `transcribe.py`) |
| Windows (tested end to end); macOS and Linux run the installer and tests in CI | Rendering without Node.js / Chromium |
| Agents with a local shell | ChatGPT or Claude web chat (no local shell) |
| Editing clips you made | Generating clips, voiceover or translations |

The tested project is 2:22 long. Longer videos work the same way but take proportionally longer, mostly in clip slow-motion and the render.

## FAQ

**Does anything leave my computer?**
No media does. Your video, audio and logo are processed locally. The only thing sent anywhere is your normal conversation with your agent.

**Can I upload the result straight to Instagram?**
Yes. The output is 1080x1920, 30 fps, H.264 + AAC with `faststart`, which is what Instagram expects for Reels. A 2-3 minute Reel is around 100-150 MB, well within Instagram's limits.

**Do I need OpenMontage?**
Yes. The skill uses its workspace and its Python environment. The installer gets it for you.

**What if something fails?**
Run the preflight check (`check.py`) and fix what it reports. If the problem is still there, open an [issue](https://github.com/EmirhanYAZICI/reelsmith-media/issues/new/choose) with the preflight output.

**I used version 1.x (`/reelsmith`). What changed?**
Only the name. The skill is now `reelsmith-media` and the command is `/reelsmith-media`. Run the installer again; it moves the old `reelsmith` folder to the backup folder. See [`CHANGELOG.md`](CHANGELOG.md).

## Development and tests

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

The tests cover scene file names, script parsing, caption and logo options, Whisper-to-script alignment (misheard and missing words), the preflight check with real generated media, a full build without the final render (clip slow-motion, 1080x1920 crop, composition data, audio mix) and the output check (`verify.py`). If HyperFrames is installed, the generated composition is also linted. CI runs them on Windows and Ubuntu and installs the skills with both installers on Windows, macOS and Ubuntu.

What was tested where, installer scenarios, the end-to-end render and what is not covered yet: [`TESTING.md`](TESTING.md). Changes per version: [`CHANGELOG.md`](CHANGELOG.md).

## Repository layout

| Path | Purpose |
|---|---|
| `skills/reelsmith-media/SKILL.md` | The steps the agent follows |
| `skills/reelsmith-media/REELS-REHBERI.md` | Every setting: captions, logo, camera, audio, format, troubleshooting (Turkish) |
| `skills/reelsmith-media/CAPTION-STYLES.md` | Caption colors, styles, animations and presets |
| `skills/reelsmith-media/template/` | Python scripts and the HyperFrames template copied into each project |
| `skills/reelsmith-media/template/scripts/check.py` | Preflight check: tools, clips, voiceover, logo, script |
| `skills/reelsmith-media/template/scripts/verify.py` | Output check after render: size, fps, codecs, loudness, peak, freezes, faststart |
| `skills/whisper-tr/` | Companion skill: local Whisper transcription with word timestamps |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests |
| `AGENTS.md` | Pointer for agents that read `AGENTS.md` instead of skills |
| `install.ps1`, `install.sh` | One-command installer (Windows / macOS, Linux, Git Bash) |
| `tests/`, `TESTING.md` | pytest suite and the test report |
| `assets/` | Banner, social preview image and demo images |

## Origin

The skill was built and tested on a real project: a 7-scene, 2:22 Reel about the gemstone "Zebercet" (peridot) for Taş Galerisi. The demo is shared with the client's permission.

## License

MIT, see [`LICENSE`](LICENSE). You can use, change and share this code, including for commercial work; keep the copyright notice.

This repository contains only its own code. The tools it runs are separate projects under their own licenses and are not bundled here:

- [OpenMontage](https://github.com/calesthio/OpenMontage): AGPL-3.0
- [HyperFrames](https://www.npmjs.com/package/hyperframes): Apache-2.0
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): MIT
- FFmpeg: LGPL/GPL, depending on the build
- Calibri is a Microsoft font and is not part of this repository.

The demo video and images belong to Taş Galerisi and are not covered by the MIT license.

---

## Türkçe

Bir klasördeki ham malzemeden Instagram'a hazır dikey Reels videosu üreten ajan skill'i.

### Demo

Reelsmith Media ile yapılmış gerçek bir proje: Taş Galerisi için "Zebercet" taşı hakkında 7 sahneli, 2:22'lik bir Reels. Görseller ve video yukarıdaki [Demo](#demo) bölümünde. [Videonun tamamını izle (2:22, 48 MB)](https://github.com/EmirhanYAZICI/reelsmith-media/releases/download/v1.3.0/reelsmith-demo-zebercet.mp4).

| | Girdi | Çıktı |
|---|---|---|
| Video | 7 klip, 10'ar sn, 720x1280, altyazısız | 2:22, 1080x1920, 30 fps, H.264 + AAC |
| Ses | 2:22 seslendirme + kliplerin kendi sesi | -14 LUFS, tepe -0.9 dBFS, klip sesi konuşmada kısılır |
| Metin | Sahne metni, 239 kelime | 97 kelime zamanlı altyazı bloğu |
| Marka | `logo.png` | Köşeden köşeye kayan logo |

Süre: orta seviye bir dizüstünde (Intel i5-13420H, 16 GB RAM) 2-3 dakikalık bir Reels için yaklaşık 15-25 dakika. Zamanın çoğu klip yavaşlatma ve render'da geçer. Whisper ve eşleştirme bir dakikadan kısa sürer.

### Neden Reelsmith Media

- **Yaratıcı kısım sende kalır.** Metni sen yazarsın, sesi sen seçersin, klipleri sen üretirsin. Skill yavaş ve tekrarlı işi yapar: zamanlama, altyazı, geçişler, logo, ses miksajı ve çıktı.
- **Altyazı tahmin değil, senin metnin.** Zamanlamayı Whisper verir, yazımı senin metnin. Marka adları ve özel kelimeler yazdığın gibi çıkar.
- **Her seferinde aynı görünüm.** Altyazı yeri, kamera hareketi, ses seviyesi ve çıktı ayarları sabittir. Bir dizi Reels tek bir marka gibi görünür.
- **Önce ve sonra kontrol.** Ön kontrol, uzun işler başlamadan eksik ya da bozuk dosyayı yakalar. Çıktı kontrolü boyutu, fps'i, ses seviyesini ve videonun hiçbir yerinin donmadığını doğrular.
- **Her marka, her ajan.** Klasördeki logo markadır. Aynı skill Claude Code, Codex, Cursor, OpenCode ve Antigravity'de çalışır.

### Maliyet

Ücretli API yok, API anahtarı yok, video başı ücret yok. Whisper, eşleştirme, klip hazırlama, HyperFrames render ve ses miksajı kendi bilgisayarında çalışır.

Harcanan tek şey ajanının token'ı. Ajan yaklaşık 20K token talimat okur (skill, rehberi ve OpenMontage'ın `AGENT_GUIDE.md` dosyası) ve on kadar kısa komut çalıştırır. Video ve ses modele gönderilmez; model yalnızca dosya listesini, kısa komut çıktılarını ve kontrol sonuçlarını görür. Abonelik planında (Claude Pro/Max, ChatGPT Plus vb.) bir Reels normal kullanım hakkının bir kısmını harcar; video başına ücret yoktur.

### Hızlı başlangıç

**En hızlısı: skills aracıyla tek satır**

```bash
npx skills add EmirhanYAZICI/reelsmith-media
```

Açık [skills](https://skills.sh/EmirhanYAZICI/reelsmith-media) aracı iki skill'i (`reelsmith-media` ve `whisper-tr`) Claude Code, Cursor, Codex, OpenCode, Antigravity ve diğer ajanlara kopyalar. Hangi ajanlara kurulacağını sorar.

Bu sadece skill'leri ekler. Video araçlarının (ffmpeg, faster-whisper ile Python 3.10-3.12, HyperFrames, OpenMontage) bilgisayarında olması gerekir. Aşağıdaki kurulum aracı bunları kurar, skill'in ön kontrolü de tam olarak neyin eksik olduğunu söyler.

**Her şeyi tek komutla kur**

Kurulum aracı araçları kontrol eder, OpenMontage'ı indirir, Python ortamını kurar, faster-whisper ve HyperFrames'i yükler ve skill'leri bilgisayarında bulduğu her ajana kopyalar.

```powershell
# Windows (PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith-media/main/install.ps1)))
```

```bash
# macOS / Linux / Git Bash
curl -fsSL https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith-media/main/install.sh | bash
```

Script'i çalışmadan önce okumak ya da sabit bir sürüm kurmak istersen: Release'i indir, SHA-256 değerini kontrol et, `install.ps1` / `install.sh` dosyasını oku, sonra klasörden çalıştır. Komutlar İngilizce bölümdeki [Verified install](#verified-install-read-the-script-first) kısmında.

Kurulum aracı senin değişikliklerini silmez. Kurulu `reelsmith-media` ya da `whisper-tr` klasörü yenisinden farklıysa önce `~/.reelsmith-backups/<zaman>/` içine taşınır. Python 3.10-3.12 ister, başka sürümde açık bir mesajla durur.

**Sadece tek bir ajana kur**

| Ajan | Kurulum | Sonra |
|---|---|---|
| **Claude Code** | `/plugin marketplace add EmirhanYAZICI/reelsmith-media`<br/>`/plugin install reelsmith-media@reelsmith-media` | `/reelsmith-media markam` yaz |
| **OpenAI Codex CLI** | kurulum aracı `-Agents codex` / `--agents=codex` | Yaz: *markam klasöründe reelsmith-media skill'ini kullan* |
| **Cursor** | kurulum aracı `-Agents cursor` / `--agents=cursor` | Agent sohbetinde yaz: *markam klasöründe reelsmith-media skill'ini kullan* |
| **OpenCode** | kurulum aracı `-Agents opencode` / `--agents=opencode` | Yaz: *markam klasöründe reelsmith-media skill'ini kullan* |
| **Google Antigravity** | kurulum aracı `-Agents antigravity` / `--agents=antigravity` | Yaz: *markam klasöründe reelsmith-media skill'ini kullan* |
| **Diğer ajanlar** | `npx skills add EmirhanYAZICI/reelsmith-media` | Skill desteği yoksa [`AGENTS.md`](AGENTS.md) dosyasını okur |

### Malzemeyi hazırla

Reelsmith Media kliplerini kurgular, klip üretmez. Önce onları hazırla:

1. **Metni sahne sahne yaz.** Anlatımı sahnelere böl (genelde 5-10 sahne). Her sahnenin metni, o sahnede seslendirmede okunan yazının aynısı olsun.
2. **Her sahne için sırayla bir video üret:** Google Gemini (Veo), Kling, Runway, Sora ya da kendi çekimin. Dikey 9:16, her biri 8-10 saniye. Her videonun komutunu (prompt) o sahnenin metnine göre yaz. Videoların kendi müziği ve efekti olabilir; Reelsmith Media onları korur ve konuşma sırasında kısar.
3. **Videoları sahne numarasıyla adlandır:** `1sahne.mp4`, `2sahne.mp4`, ... (ya da `scene1.mp4`). Hangi videonun hangi sahneye gideceğini numara belirler. Bir sahneye iki video: `3sahne.mp4` ve `3sahne_b.mp4`.
4. **Seslendirmeyi** aynı sırayla metni okuyarak kaydet ya da ürettir.
5. **Logonu** şeffaf `logo.png` olarak ekle.

Örnek sahne metni (`metin.txt`), her sahne bir paragraf:

```
Bu yeşil taş Dünya'nın derinliklerinden gelir.

Volkanlar kristallerini yeryüzüne taşır.

Bir kısmı ise göktaşlarının içinde uzaydan düşmüştür.
```

### Reels'i yap

Dosyaları Masaüstünde bir klasöre koy:

```
markam/
├── seslendirme.mp3    anlatım sesi
├── 1sahne.mp4         1. sahne videosu   (2sahne.mp4 ... ya da scene1.mp4)
├── metin.txt          her sahnenin metni
└── logo.png           logon, video boyunca köşeden köşeye gezer
```

Sonra skill'i çağır. Altyazı isteğini cümleyle yazmak isteğe bağlı:

```
/reelsmith-media markam reels.mp4 beyaz yazı, kutulu, kelime kelime hoplasın
```

Uzun işler başlamadan önce ajan bir ön kontrol çalıştırır ve eksik ya da bozuk olanı söyler: eksik sahne numarası, bozuk klip, logo yok, eksik araç. İstersen kendin de çalıştırabilirsin:

```bash
python skills/reelsmith-media/template/scripts/check.py --src=~/Desktop/markam
```

Bitmiş `reels.mp4` hem `markam/` içine hem de yanındaki `cikti/` klasörüne kaydedilir.

### Nasıl çalışır

1. **Seslendirmeyi yerel Whisper ile yazıya döker** (faster-whisper, varsayılan Türkçe). Kelime kelime zaman çıkarır. API anahtarı ya da ücretli servis gerekmez.
2. **Dökümü senin metninle hizalar.** Altyazı Whisper'ın yazımıyla değil, senin yazımınla çıkar. Sahne sınırları her sahnenin metninin gerçekten okunduğu ana göre belirlenir.
3. **Her klibi kendi sahnesine uydurur.**
   - ~10 sn'lik her klip, o sahnenin konuşma süresine kadar yavaşlatılır.
   - Hareket telafili kare ara-değerleme (ffmpeg `minterpolate`) sayesinde takılma olmaz.
   - Klipler 9:16'ya kırpılır ve hafif renk düzeltmesi yapılır.
4. **Kurguyu HyperFrames (HTML + GSAP) ile kurar:**
   - ışık süzmeli crossfade geçişler
   - her sahnede tek, yavaş, kesintisiz kamera hareketi (ani zoom yok)
   - film greni ve toz katmanı
   - kelime zamanlı altyazı, blok başına 2-3 kelime
5. **Hareketli logo filigranı ekler.** Logon video boyunca köşeden köşeye yavaşça kayar. Bu sayede video kırpılıp başkası tarafından yüklenemez. Logo yüklendiği gibi kalır: tam opak, efektsiz.
6. **Sesi miksler:**
   - Seslendirme -14 LUFS'a ayarlanır.
   - Kliplerin kendi müziği ve efekti kalır, konuşma sırasında 9 dB kısılır.
   - Sahne geçişlerinde hafif bir whoosh duyulur.
   - Limiter tepeleri yaklaşık -1 dBFS'de tutar.
7. **Render alır ve sonucu kontrol eder:** 1080x1920, 30 fps, H.264 High + AAC, `faststart`. Çıktı kontrolü boyutu, fps'i, codec'leri, ses seviyesini, tepeyi, donan bölümleri ve süreyi doğrular. Sonra video kaynak dosyalarının yanına kopyalanır.

### Altyazı: yeri sabit, görünüşü seçilebilir

Altyazı hep aynı yerdedir: Calibri Bold 75 px, alttan 450 px, ortalı. Sadece görünüş değişir:

| Seçenek | Varsayılan | Değerler |
|---|---|---|
| `--caption-color` | `yellow` | `yellow`, `white`, `green`, `gold`, `orange`, `red`, `pink`, `blue`, `purple`, `black` ya da herhangi bir `#RRGGBB`. Türkçe adlar da olur (`sari`, `beyaz`...) |
| `--caption-outline` | `#000000` | aynı liste (kontur / gölge rengi) |
| `--caption-style` | `outline` | `outline` (kontur), `box` (kutulu), `shadow` (gölgeli), `double` (çift kontur) |
| `--caption-anim` | `pop` | `pop`, `hop`, `word-hop` (her kelime söylendiği anda zıplar), `bounce`, `wave` |

Ajana cümleyle de söyleyebilirsin, örneğin: `/reelsmith-media klasorum beyaz yazı, kutulu, kelime kelime hoplasın`.
Tüm liste ve hazır kombinasyonlar: [`CAPTION-STYLES.md`](skills/reelsmith-media/CAPTION-STYLES.md).

### Logo: hareketli, sabit ya da açılış/kapanış

| Seçenek | Varsayılan | Değerler |
|---|---|---|
| `--logo-mode` | `move` | `move` (köşeden köşeye kayar, kesip atmak zor), `corner` (tek köşede sabit), `ends` (açılışta ve kapanışta ortada büyük). `ends` diğerleriyle birleşir: `move,ends`, `corner,ends` |
| `--logo-pos` | `bottom-left` | `bottom-left`, `bottom-right`, `top-left`, `top-right` (`move` için başlangıç köşesi, `corner` için durduğu köşe) |
| `--logo-size` | `258` | px cinsinden genişlik, 80-700 |
| `--logo-moves` | `6` | video boyunca kaç kez köşe değiştirir (az = daha yavaş) |

Logo hep yüklendiği gibi kullanılır: kendi rengi, tam opak, efektsiz. Cümleyle de söyleyebilirsin: `/reelsmith-media klasorum logo sağ üstte sabit dursun, başta ve sonda da büyük çıksın`.

### Gereksinimler

| Araç | Not |
|---|---|
| Yerel terminali olan bir ajan | Claude Code, Cursor, Codex CLI, OpenCode, Antigravity... Yerel terminali olmayan web sohbet uygulamaları bunu çalıştıramaz |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Çalışma alanı ve Python 3.12 sanal ortamı |
| Python paketleri | `faster-whisper`, `numpy` (bkz. `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes@0.8` (0.8.x ile test edildi) |
| ffmpeg / ffprobe | `PATH`'te olmalı |
| Calibri Bold | Windows'ta hazır gelir (`C:\Windows\Fonts\calibrib.ttf`). Lisans gereği bu repoda **yok**. Başka sistemde `--font=<yol>` ver |

### Kurulum ayrıntıları

Repo indirildiyse: `.\install.ps1` ya da `./install.sh`.

| PowerShell | Bash | Etkisi |
|---|---|---|
| `-Agents claude,cursor` | `--agents=claude,cursor` | Ajanları seç (`auto` = bu bilgisayarda bulunanlar, `all` = hepsi) |
| `-Project` | `--project` | Ana klasör yerine şu anki proje klasörüne kur |
| `-OM <yol>` | `--om=<yol>` | OpenMontage'ın yeri |
| `-SkillsOnly` | `--skills-only` | Sadece skill'leri kopyala, bağımlılıkları atla |
| `-NoBackup` | `--no-backup` | Değişmiş skill klasörlerini yedeksiz değiştir |
| `-DryRun` | `--dry-run` | Ne yapacağını göster, hiçbir şeyi değiştirme |

Kurulum aracı sistem programlarını kendisi kurmaz. `git`, `node`, `ffmpeg` ya da Python 3.10-3.12 eksikse durur ve kurulum komutunu (`winget`, `brew`, `apt`) yazar. Kullanacağı Python'un (ve varsa mevcut `.venv`'in) gerçek sürümünü kontrol eder. Skill klasörlerinde sadece `reelsmith-media` ve `whisper-tr` klasörlerine dokunur: aynıysa bırakır, farklıysa önce yedekler. 1.x sürümünden kalan eski `reelsmith` klasörü de yedek klasörüne taşınır.

**Elle kurulum**

```bash
OM=~/Projects/OpenMontage                      # OpenMontage nerede ise
$OM/.venv/Scripts/python.exe -m pip install faster-whisper numpy   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes@0.8
npx hyperframes skills                         # resmi HyperFrames skill'leri
```

OpenMontage `~/Projects/OpenMontage` dışında bir yerdeyse `OPENMONTAGE_DIR` ortam değişkenine yolunu yaz. Sonra `skills/reelsmith-media` ve `skills/whisper-tr` klasörlerini aracının skill klasörüne kopyala:

| Araç | Skill klasörü (kullanıcı geneli / proje) |
|---|---|
| Claude Code | `~/.claude/skills/` / `.claude/skills/` |
| OpenAI Codex | `~/.codex/skills/` / `.codex/skills/` |
| OpenCode | `~/.config/opencode/skills/` / `.opencode/skills/` |
| Cursor | `~/.cursor/skills/` / `.cursor/skills/` |
| Google Antigravity | `~/.gemini/antigravity/skills/` / `.agent/skills/` |

Araç skill yüklemiyorsa bile [`AGENTS.md`](AGENTS.md) dosyasını okur; o dosya ajanı doğru `SKILL.md`'ye yönlendirir. Claude Code'da kontrol için `/` yaz. Listede `reelsmith-media` ve `whisper-tr` görünmeli.

### Kullanım ayrıntıları

| Dosya | Kural |
|---|---|
| Seslendirme | Adında `seslendirme`, `voice` ya da `vo` geçsin (`.mp3`, `.wav`, `.m4a`) |
| Sahne videoları | `1sahne.mp4` ya da `scene1.mp4`, ... Dikey, her biri ~10 sn. Kendi sesleri korunur |
| Sahne metni | `.txt` ya da `.md`, her sahnede okunan metnin aynısı: her sahne bir paragraf (arada boş satır), ya da her sahne için bir `Metin: "..."` satırı, ya da orijinal `Metin karşılığı: "...")` satırları |
| Logo | `logo.png`, şeffaf arka plan |
| İsteğe bağlı | `REELS-REHBERI.md` (ya da herhangi bir `*.md` rehber): projeye özel kurallar. Skill'deki rehberin yerine geçer |

Sahne sayısı serbesttir. Videolardaki ve metindeki sahne sayısı eşit olmalı.

```
/reelsmith-media <klasör adı ya da yolu> <video_adı>.mp4 [altyazı ve logo isteği]
```

Ajan olmadan elle çalıştırmak için [`skills/reelsmith-media/SKILL.md`](skills/reelsmith-media/SKILL.md) içindeki 3. adıma bak.

### Desteklenenler ve desteklenmeyenler

| Destekleniyor | Henüz desteklenmiyor |
|---|---|
| Dikey 1080x1920, 30 fps | Başka boyut ya da fps (16:9, 1:1, 60 fps) |
| İstediğin kadar sahne, sahne başına bir ya da daha fazla klip | Klipleri müzik vuruşuna göre kesmek (klipler anlatıma göre ayarlanır) |
| Türkçe seslendirme (hazır) | Başka dil için tek satır değişiklik gerekir (`transcribe.py` içinde `language="tr"`) |
| Windows (uçtan uca test edildi); macOS ve Linux'ta kurulum ve testler CI'da çalışır | Node.js / Chromium olmadan render |
| Yerel terminali olan ajanlar | ChatGPT ya da Claude web sohbeti (yerel terminal yok) |
| Senin ürettiğin klipleri kurgulamak | Klip, seslendirme ya da çeviri üretmek |

Test edilen proje 2:22 uzunluğunda. Daha uzun videolar da aynı şekilde çalışır ama süre orantılı uzar; en çok klip yavaşlatma ve render zaman alır.

### Sık sorulanlar

**Bilgisayarımdan dışarı bir şey gidiyor mu?**
Medya gitmez. Video, ses ve logo kendi bilgisayarında işlenir. Dışarı giden tek şey ajanınla normal yazışman.

**Çıktıyı doğrudan Instagram'a yükleyebilir miyim?**
Evet. Çıktı 1080x1920, 30 fps, H.264 + AAC ve `faststart`; Instagram Reels'in beklediği biçim bu. 2-3 dakikalık bir Reels yaklaşık 100-150 MB olur, Instagram sınırlarının çok altında.

**OpenMontage şart mı?**
Evet. Skill onun çalışma alanını ve Python ortamını kullanır. Kurulum aracı onu senin için indirir.

**Bir şey hata verirse?**
Ön kontrolü (`check.py`) çalıştır ve söylediğini düzelt. Sorun devam ederse ön kontrol çıktısıyla bir [issue](https://github.com/EmirhanYAZICI/reelsmith-media/issues/new/choose) aç.

**1.x sürümünü (`/reelsmith`) kullanıyordum. Ne değişti?**
Sadece ad. Skill artık `reelsmith-media`, komut `/reelsmith-media`. Kurulum aracını tekrar çalıştır; eski `reelsmith` klasörünü yedek klasörüne taşır. Bkz. [`CHANGELOG.md`](CHANGELOG.md).

### Geliştirme ve testler

```bash
pip install -r requirements-dev.txt
python -m pytest tests
```

Testler şunları kontrol eder: sahne dosya adları, sahne metni okuma, altyazı ve logo seçenekleri, Whisper ile metin eşleştirme (yanlış duyulan ve hiç duyulmayan kelimeler), gerçek üretilmiş medya ile ön kontrol, son render hariç tam kurgu (klip yavaşlatma, 1080x1920 kırpma, kompozisyon verisi, ses miksajı) ve çıktı kontrolü (`verify.py`). HyperFrames kuruluysa üretilen kompozisyon lint'ten de geçer. CI bunları Windows ve Ubuntu'da çalıştırır, iki kurulum aracıyla skill'leri Windows, macOS ve Ubuntu'ya kurar.

Nerede neyin test edildiği ve henüz kapsanmayanlar: [`TESTING.md`](TESTING.md). Sürüm sürüm değişiklikler: [`CHANGELOG.md`](CHANGELOG.md).

### Nereden çıktı

Skill gerçek bir projede kurulup test edildi: Taş Galerisi için "Zebercet" taşı hakkında 7 sahneli, 2:22'lik bir Reels videosu. Demo, firmanın izniyle paylaşıldı.

### Lisans

MIT, bkz. [`LICENSE`](LICENSE). Bu kodu ticari işler dahil kullanabilir, değiştirebilir ve paylaşabilirsin; telif notunu koruman yeterli.

Bu repo yalnızca kendi kodunu içerir. Çalıştırdığı araçlar kendi lisansları olan ayrı projelerdir ve buraya dahil edilmez: OpenMontage (AGPL-3.0), HyperFrames (Apache-2.0), faster-whisper (MIT), FFmpeg (derlemeye göre LGPL/GPL). Calibri Microsoft'un fontudur ve bu repoda yoktur.

Demo video ve görseller Taş Galerisi'ne aittir ve MIT lisansının kapsamında değildir.
