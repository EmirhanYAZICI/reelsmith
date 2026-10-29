# Reelsmith

An agent skill that turns a folder of raw material into a finished, Instagram-ready vertical Reel.
Works with Claude Code, Cursor, OpenAI Codex, OpenCode, Google Antigravity and other tools that support the open `SKILL.md` format.

Bir klasördeki ham malzemeden Instagram'a hazır dikey Reels videosu üreten ajan skill'i.
Claude Code, Cursor, OpenAI Codex, OpenCode, Google Antigravity ve açık `SKILL.md` formatını destekleyen diğer araçlarla çalışır.

**English** | [Türkçe](#türkçe)

---

## English

### What it does

You put a voiceover, numbered scene clips, a scene script and your logo in a folder. Then you ask your agent:

```
/reelsmith my-folder my_reel.mp4
```

The skill then does the following:

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
7. **Renders and checks the result:** 1080x1920, 30 fps, H.264 High + AAC, `faststart`. The skill verifies resolution, loudness and frozen frames, then copies the video next to your source files.

It works for any brand. The logo you drop in the folder is the brand.

### Captions: fixed placement, flexible look

Captions always sit in the same place: Calibri Bold 75 px, 450 px from the bottom, centered. Only three things change:

| Option | Default | Values |
|---|---|---|
| `--caption-color` | `yellow` | `yellow`, `white`, `green`, `gold`, `orange`, `red`, `pink`, `blue`, `purple`, `black`, or any `#RRGGBB` |
| `--caption-outline` | `#000000` | same list (outline / shadow color) |
| `--caption-style` | `outline` | `outline`, `box`, `shadow`, `double` |
| `--caption-anim` | `pop` | `pop`, `hop`, `word-hop` (each word jumps in exactly when it is spoken), `bounce`, `wave` |

Through an agent, you can describe the captions in plain words, for example: `/reelsmith my-folder white text, boxed, words hop in one by one`.
See [`CAPTION-STYLES.md`](skills/reelsmith/CAPTION-STYLES.md) for the full list and ready-made presets.

### Requirements

| Tool | Notes |
|---|---|
| An agent with a local shell | Claude Code, Cursor, Codex CLI, OpenCode, Antigravity... Web chat apps without a local shell cannot run it |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Workspace and Python 3.12 virtual environment |
| Python packages | `faster-whisper`, `numpy` (see `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes` (tested with 0.8.x) |
| ffmpeg / ffprobe | Must be on `PATH` |
| Calibri Bold font | Ships with Windows (`C:\Windows\Fonts\calibrib.ttf`). It is **not** included here for licensing reasons. On other systems pass `--font=<path>` |

No API keys are needed. Everything runs locally.

### Install

**Quick install (recommended)**

One command checks the tools, gets OpenMontage, creates its Python 3.12 environment, installs `faster-whisper`, HyperFrames and its skills, and copies the skills into every agent it finds (Claude Code, Codex, OpenCode, Cursor, Antigravity).

```powershell
# Windows (PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.ps1)))
```

```bash
# macOS / Linux / Git Bash
curl -fsSL https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.sh | bash
```

From a clone: `.\install.ps1` or `./install.sh`. Options:

| PowerShell | Bash | Effect |
|---|---|---|
| `-Agents claude,cursor` | `--agents=claude,cursor` | Pick agents (`auto` = found on this machine, `all`) |
| `-Project` | `--project` | Install into the current project folder instead of your home |
| `-OM <path>` | `--om=<path>` | OpenMontage location |
| `-SkillsOnly` | `--skills-only` | Copy the skills only, skip dependencies |
| `-DryRun` | `--dry-run` | Show what would happen, change nothing |

The installer does not install system tools for you. If `git`, `node`, `ffmpeg` or Python 3.12 is missing, it stops and prints the command (`winget`, `brew`, `apt`). It only replaces the `reelsmith` and `whisper-tr` folders in each skills folder.

The manual steps below do the same thing by hand.

**1. Shared dependencies (once)**

```bash
OM=~/Projects/OpenMontage                      # wherever OpenMontage lives
$OM/.venv/Scripts/python.exe -m pip install faster-whisper numpy   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes
npx hyperframes skills                         # official HyperFrames skills for your agents
```

If OpenMontage is not in `~/Projects/OpenMontage`, set the `OPENMONTAGE_DIR` environment variable to its path.

**2. The skills: pick your tool**

| Tool | Install |
|---|---|
| Claude Code (plugin) | `/plugin marketplace add EmirhanYAZICI/reelsmith`, then `/plugin install reelsmith@reelsmith` |
| Any supported agent | `npx skills add EmirhanYAZICI/reelsmith` (the open [skills](https://skills.sh) CLI; it asks which agents to install for) |
| Manual | Copy `skills/reelsmith` and `skills/whisper-tr` into your tool's skills folder (table below) |

| Tool | Skills folder (user-wide / per project) |
|---|---|
| Claude Code | `~/.claude/skills/` / `.claude/skills/` |
| OpenAI Codex | `~/.codex/skills/` / `.codex/skills/` |
| OpenCode | `~/.config/opencode/skills/` / `.opencode/skills/` |
| Cursor | `~/.cursor/skills/` / `.cursor/skills/` |
| Google Antigravity | `~/.gemini/antigravity/skills/` / `.agent/skills/` |

Folder names can change between tool versions. If a path does not work, check your tool's docs or use `npx skills add`.
Tools that do not load skills still read [`AGENTS.md`](AGENTS.md), which points them to the right `SKILL.md`.

To check the install in Claude Code, type `/`. You should see `reelsmith` and `whisper-tr`.

### Usage

1. Create a folder and put these files in it:

   | File | Rule |
   |---|---|
   | Voiceover | Name contains `seslendirme`, `voice` or `vo` (`.mp3`, `.wav`, `.m4a`) |
   | Scene clips | `1sahne.mp4`, `2sahne.mp4`, ... vertical, about 10 s each. Their own audio is kept |
   | Scene script | `.txt` or `.md` with one `Metin karşılığı: "...")` line per scene, holding exactly the text spoken in that scene |
   | Logo | `logo.png`, transparent background |
   | Optional | `REELS-REHBERI.md` with project-specific rules. It overrides the bundled guide |

   You can use any number of scenes. The number of clips must match the number of script entries.
2. Ask your agent:
   ```
   /reelsmith <folder name or path> <output_name>.mp4 [caption wishes]
   ```
3. Clip preparation and rendering take about 15-25 minutes. The finished video is copied into your folder and into a `cikti/` folder next to it.

To run it by hand without an agent, see step 3 in [`skills/reelsmith/SKILL.md`](skills/reelsmith/SKILL.md).

### Repository layout

| Path | Purpose |
|---|---|
| `skills/reelsmith/SKILL.md` | The steps the agent follows |
| `skills/reelsmith/REELS-REHBERI.md` | Every setting: captions, logo, camera, audio, format, troubleshooting (Turkish) |
| `skills/reelsmith/CAPTION-STYLES.md` | Caption colors, styles, animations and presets (English / Turkish) |
| `skills/reelsmith/template/` | Python scripts and the HyperFrames template copied into each project |
| `skills/whisper-tr/` | Companion skill: local Whisper transcription with word timestamps |
| `.claude-plugin/` | Claude Code plugin and marketplace manifests |
| `AGENTS.md` | Pointer for agents that read `AGENTS.md` instead of skills |
| `install.ps1`, `install.sh` | One-command installer (Windows / macOS, Linux, Git Bash) |

### Origin

The skill was built and tested on a real project, a 7-scene, 2:22 Reel about the gemstone "Zebercet" (peridot) for Taş Galerisi.

---

## Türkçe

### Ne yapar

Bir klasöre seslendirme, numaralı sahne videoları, sahne metni ve logonu koyarsın. Sonra ajanına şunu yazarsın:

```
/reelsmith klasorum videom.mp4
```

Skill şunları yapar:

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
7. **Render alır ve sonucu kontrol eder:** 1080x1920, 30 fps, H.264 High + AAC, `faststart`. Skill çözünürlüğü, ses seviyesini ve donan kareleri kontrol eder, sonra videoyu kaynak dosyalarının yanına kopyalar.

Her firma için çalışır. Klasöre koyduğun logo, markadır.

### Altyazı: yeri sabit, görünüşü seçilebilir

Altyazı hep aynı yerdedir: Calibri Bold 75 px, alttan 450 px, ortalı. Sadece üç şey değişir:

| Seçenek | Varsayılan | Değerler |
|---|---|---|
| `--caption-color` | `yellow` | `yellow`, `white`, `green`, `gold`, `orange`, `red`, `pink`, `blue`, `purple`, `black` ya da herhangi bir `#RRGGBB`. Türkçe adlar da olur (`sari`, `beyaz`...) |
| `--caption-outline` | `#000000` | aynı liste (kontur / gölge rengi) |
| `--caption-style` | `outline` | `outline` (kontur), `box` (kutulu), `shadow` (gölgeli), `double` (çift kontur) |
| `--caption-anim` | `pop` | `pop`, `hop`, `word-hop` (her kelime söylendiği anda zıplar), `bounce`, `wave` |

Ajana cümleyle de söyleyebilirsin, örneğin: `/reelsmith klasorum beyaz yazı, kutulu, kelime kelime hoplasın`.
Tüm liste ve hazır kombinasyonlar: [`CAPTION-STYLES.md`](skills/reelsmith/CAPTION-STYLES.md).

### Gereksinimler

| Araç | Not |
|---|---|
| Yerel terminali olan bir ajan | Claude Code, Cursor, Codex CLI, OpenCode, Antigravity... Yerel terminali olmayan web sohbet uygulamaları bunu çalıştıramaz |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Çalışma alanı ve Python 3.12 sanal ortamı |
| Python paketleri | `faster-whisper`, `numpy` (bkz. `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes` (0.8.x ile test edildi) |
| ffmpeg / ffprobe | `PATH`'te olmalı |
| Calibri Bold | Windows'ta hazır gelir (`C:\Windows\Fonts\calibrib.ttf`). Lisans gereği bu repoda **yok**. Başka sistemde `--font=<yol>` ver |

API anahtarı gerekmez. Her şey senin bilgisayarında çalışır.

### Kurulum

**Hızlı kurulum (önerilen)**

Tek komut araçları kontrol eder, OpenMontage'ı indirir, Python 3.12 ortamını kurar, `faster-whisper`, HyperFrames ve skill'lerini yükler. Sonra skill'leri bilgisayarda bulduğu her ajana kopyalar (Claude Code, Codex, OpenCode, Cursor, Antigravity).

```powershell
# Windows (PowerShell)
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.ps1)))
```

```bash
# macOS / Linux / Git Bash
curl -fsSL https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.sh | bash
```

Repo indirildiyse: `.\install.ps1` ya da `./install.sh`. Seçenekler yukarıdaki İngilizce tabloda (`-Agents`, `-Project`, `-OM`, `-SkillsOnly`, `-DryRun`).

Kurulum aracı sistem programlarını kendisi kurmaz. `git`, `node`, `ffmpeg` ya da Python 3.12 eksikse durur ve kurulum komutunu (`winget`, `brew`, `apt`) yazar. Skill klasörlerinde sadece `reelsmith` ve `whisper-tr` klasörlerini değiştirir.

Aşağıdaki elle kurulum adımları aynı işi tek tek yapar.

**1. Ortak bağımlılıklar (bir kere)**

```bash
OM=~/Projects/OpenMontage                      # OpenMontage nerede ise
$OM/.venv/Scripts/python.exe -m pip install faster-whisper numpy   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes
npx hyperframes skills                         # resmi HyperFrames skill'leri
```

OpenMontage `~/Projects/OpenMontage` dışında bir yerdeyse `OPENMONTAGE_DIR` ortam değişkenine yolunu yaz.

**2. Skill'ler: aracını seç**

| Araç | Kurulum |
|---|---|
| Claude Code (plugin) | `/plugin marketplace add EmirhanYAZICI/reelsmith`, sonra `/plugin install reelsmith@reelsmith` |
| Desteklenen her ajan | `npx skills add EmirhanYAZICI/reelsmith` (açık [skills](https://skills.sh) aracı; hangi ajanlara kurulacağını sorar) |
| Elle | `skills/reelsmith` ve `skills/whisper-tr` klasörlerini aracının skill klasörüne kopyala (yukarıdaki İngilizce bölümdeki tablo) |

Araç skill yüklemiyorsa bile [`AGENTS.md`](AGENTS.md) dosyasını okur. O dosya ajanı doğru `SKILL.md`'ye yönlendirir.
Claude Code'da kontrol için `/` yaz. Listede `reelsmith` ve `whisper-tr` görünmeli.

### Kullanım

1. Bir klasör aç ve içine şunları koy:

   | Dosya | Kural |
   |---|---|
   | Seslendirme | Adında `seslendirme`, `voice` ya da `vo` geçsin (`.mp3`, `.wav`, `.m4a`) |
   | Sahne videoları | `1sahne.mp4`, `2sahne.mp4`, ... dikey, her biri ~10 sn. Kendi sesleri korunur |
   | Sahne metni | `.txt` ya da `.md`. Her sahne için bir `Metin karşılığı: "...")` satırı. İçinde o sahnede okunan metin olsun |
   | Logo | `logo.png`, şeffaf arka plan |
   | İsteğe bağlı | `REELS-REHBERI.md`: projeye özel kurallar. Skill'deki rehberin yerine geçer |

   Sahne sayısı serbesttir. Video sayısı ile metindeki sahne sayısı eşit olmalı.
2. Ajanına şunu yaz:
   ```
   /reelsmith <klasör adı ya da yolu> <video_adı>.mp4 [altyazı isteği]
   ```
3. Klip hazırlığı ve render yaklaşık 15-25 dakika sürer. Bitmiş video senin klasörüne ve yanındaki `cikti/` klasörüne kopyalanır.

Ajan olmadan elle çalıştırmak için [`skills/reelsmith/SKILL.md`](skills/reelsmith/SKILL.md) içindeki 3. adıma bak.

### Nereden çıktı

Skill gerçek bir projede kurulup test edildi: Taş Galerisi için "Zebercet" taşı hakkında 7 sahneli, 2:22'lik bir Reels videosu.

---

## License / Lisans

MIT, see [`LICENSE`](LICENSE). Calibri is a Microsoft font and is not part of this repository. OpenMontage and HyperFrames are separate projects with their own licenses.

MIT, bkz. [`LICENSE`](LICENSE). Calibri Microsoft'un fontudur ve bu repoya dahil değildir. OpenMontage ve HyperFrames kendi lisansları olan ayrı projelerdir.
