# Install in detail

[README](../README.md) · [Türkçe](#kurulum-ayrıntıları)

## Installer options

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

## Manual install

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
Tools that do not load skills still read [`AGENTS.md`](../AGENTS.md), which points them to the right `SKILL.md`.

To check the install in Claude Code, type `/`. You should see `reelsmith-media` and `whisper-tr`.

---

# Kurulum ayrıntıları

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

## Elle kurulum

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

Araç skill yüklemiyorsa bile [`AGENTS.md`](../AGENTS.md) dosyasını okur; o dosya ajanı doğru `SKILL.md`'ye yönlendirir. Claude Code'da kontrol için `/` yaz. Listede `reelsmith-media` ve `whisper-tr` görünmeli.

