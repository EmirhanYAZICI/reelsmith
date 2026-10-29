# reels-edit

A Claude Code skill that turns a folder of raw material into a finished, Instagram-ready vertical Reel.
Bir klasördeki ham malzemeden Instagram'a hazır dikey Reels videosu üreten Claude Code skill'i.

**English** | [Türkçe](#türkçe)

---

## English

### What it does

You put a voiceover, numbered scene clips, a scene script and your logo in a folder. Then you type one command:

```
/reels-edit my-folder my_reel.mp4
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

| Option | Values |
|---|---|
| `--renk` (color) | `sari` (yellow, default), `beyaz`, `yesil`, `altin`, `turuncu`, `kirmizi`, `pembe`, `mavi`, `mor`, `siyah`, or any `#RRGGBB` |
| `--kontur` (outline color) | same list, default black |
| `--stil` (text style) | `outline` (default), `box`, `shadow`, `double` |
| `--anim` (entry animation) | `pop` (default), `hop`, `word-hop` (each word jumps in exactly when it is spoken), `bounce`, `wave` |

When you run it through Claude, you can describe the captions in plain words, for example: `/reels-edit my-folder white text, boxed, words hop in one by one`.
See [`ALTYAZI-STILLERI.md`](ALTYAZI-STILLERI.md) for the full list and ready-made combinations.

### Requirements

| Tool | Notes |
|---|---|
| [Claude Code](https://claude.com/claude-code) | Runs the skill |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Workspace and Python 3.12 virtual environment |
| Python packages | `faster-whisper`, `numpy` (see `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes` (tested with 0.8.x) |
| ffmpeg / ffprobe | Must be on `PATH` |
| Calibri Bold font | Ships with Windows (`C:\Windows\Fonts\calibrib.ttf`). It is **not** included here for licensing reasons. On other systems pass `--font=<path>` |

No API keys are needed. Everything runs locally.

### Install

```bash
OM=~/Projects/OpenMontage                      # wherever OpenMontage lives
git clone https://github.com/EmirhanYAZICI/reels-edit ~/.claude/skills/reels-edit

# companion skills, so they load from any folder
cp -r ~/.claude/skills/reels-edit/extras/whisper-tr ~/.claude/skills/
cp -r $OM/.agents/skills/hyperframes $OM/.agents/skills/hyperframes-core $OM/.agents/skills/hyperframes-cli ~/.claude/skills/

# Python packages into the OpenMontage venv, HyperFrames globally
$OM/.venv/Scripts/python.exe -m pip install -r ~/.claude/skills/reels-edit/requirements.txt   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes
```

If OpenMontage is not in `~/Projects/OpenMontage`, set the `OPENMONTAGE_DIR` environment variable to its path.
To check the install, type `/` in Claude Code. You should see `reels-edit`, `whisper-tr` and `hyperframes-core` in the list.

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
2. Open Claude Code. OpenMontage is the best place, but any folder works. Then run:
   ```
   /reels-edit <folder name or path> <output_name>.mp4 [caption wishes]
   ```
3. Clip preparation and rendering take about 15-25 minutes. The finished video is copied into your folder and into a `cikti/` folder next to it.

To run it by hand without Claude, see step 3 in [`SKILL.md`](SKILL.md).

### Repository layout

| Path | Purpose |
|---|---|
| `SKILL.md` | The steps Claude follows |
| `REELS-REHBERI.md` | Every setting: captions, logo, camera, audio, format, troubleshooting (Turkish) |
| `ALTYAZI-STILLERI.md` | Caption colors, styles, animations and presets (Turkish) |
| `extras/whisper-tr/SKILL.md` | Companion skill for local Turkish Whisper transcription |
| `template/scripts/transcribe.py` | Whisper: audio to word timestamps |
| `template/scripts/align.py` | Transcript + script to `timeline.json` (scenes, caption blocks) |
| `template/scripts/build.py` | Synthesized SFX and the speech-ducking expression |
| `template/scripts/build_video.py` | Clip prep, mix, composition, render, delivery |
| `template/composition_video/index.html` | HyperFrames template (GSAP) |

### Origin

The skill was built and tested on a real project, a 7-scene, 2:22 Reel about the gemstone "Zebercet" (peridot) for Taş Galerisi.

---

## Türkçe

### Ne yapar

Bir klasöre seslendirme, numaralı sahne videoları, sahne metni ve logonu koyarsın. Sonra tek komut yazarsın:

```
/reels-edit klasorum videom.mp4
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

| Seçenek | Değerler |
|---|---|
| `--renk` | `sari` (varsayılan), `beyaz`, `yesil`, `altin`, `turuncu`, `kirmizi`, `pembe`, `mavi`, `mor`, `siyah` ya da herhangi bir `#RRGGBB` |
| `--kontur` | aynı liste, varsayılan siyah |
| `--stil` (yazı şekli) | `outline` (varsayılan), `box` (kutulu), `shadow` (gölgeli), `double` (çift kontur) |
| `--anim` (giriş animasyonu) | `pop` (varsayılan), `hop`, `word-hop` (her kelime söylendiği anda zıplar), `bounce`, `wave` |

Claude üzerinden çalıştırırken cümleyle söyleyebilirsin, örneğin: `/reels-edit klasorum beyaz yazı, kutulu, kelime kelime hoplasın`.
Tüm liste ve hazır kombinasyonlar: [`ALTYAZI-STILLERI.md`](ALTYAZI-STILLERI.md).

### Gereksinimler

| Araç | Not |
|---|---|
| [Claude Code](https://claude.com/claude-code) | Skill'i çalıştırır |
| [OpenMontage](https://github.com/calesthio/OpenMontage) | Çalışma alanı ve Python 3.12 sanal ortamı |
| Python paketleri | `faster-whisper`, `numpy` (bkz. `requirements.txt`) |
| Node.js + [HyperFrames](https://www.npmjs.com/package/hyperframes) | `npm i -g hyperframes` (0.8.x ile test edildi) |
| ffmpeg / ffprobe | `PATH`'te olmalı |
| Calibri Bold | Windows'ta hazır gelir (`C:\Windows\Fonts\calibrib.ttf`). Lisans gereği bu repoda **yok**. Başka sistemde `--font=<yol>` ver |

API anahtarı gerekmez. Her şey senin bilgisayarında çalışır.

### Kurulum

```bash
OM=~/Projects/OpenMontage                      # OpenMontage nerede ise
git clone https://github.com/EmirhanYAZICI/reels-edit ~/.claude/skills/reels-edit

# yardımcı skill'ler, her klasörden yüklensin diye
cp -r ~/.claude/skills/reels-edit/extras/whisper-tr ~/.claude/skills/
cp -r $OM/.agents/skills/hyperframes $OM/.agents/skills/hyperframes-core $OM/.agents/skills/hyperframes-cli ~/.claude/skills/

# Python paketleri OpenMontage venv'ine, HyperFrames global
$OM/.venv/Scripts/python.exe -m pip install -r ~/.claude/skills/reels-edit/requirements.txt   # Linux/macOS: $OM/.venv/bin/python
npm i -g hyperframes
```

OpenMontage `~/Projects/OpenMontage` dışında bir yerdeyse `OPENMONTAGE_DIR` ortam değişkenine yolunu yaz.
Kontrol için Claude Code'da `/` yaz. Listede `reels-edit`, `whisper-tr` ve `hyperframes-core` görünmeli.

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
2. Claude Code'u aç. En iyisi OpenMontage klasörü ama her klasörden çalışır. Sonra şunu yaz:
   ```
   /reels-edit <klasör adı ya da yolu> <video_adı>.mp4 [altyazı isteği]
   ```
3. Klip hazırlığı ve render yaklaşık 15-25 dakika sürer. Bitmiş video senin klasörüne ve yanındaki `cikti/` klasörüne kopyalanır.

Claude olmadan elle çalıştırmak için [`SKILL.md`](SKILL.md) içindeki 3. adıma bak.

### Repo düzeni

| Yol | Görev |
|---|---|
| `SKILL.md` | Claude'un izlediği adımlar |
| `REELS-REHBERI.md` | Tüm ayarlar: altyazı, logo, kamera, ses, format, sık sorunlar |
| `ALTYAZI-STILLERI.md` | Altyazı renkleri, stilleri, animasyonları ve hazır kombinasyonlar |
| `extras/whisper-tr/SKILL.md` | Yerel Türkçe Whisper için yardımcı skill |
| `template/scripts/transcribe.py` | Whisper: sesten kelime zamanlarına |
| `template/scripts/align.py` | Döküm + metin → `timeline.json` (sahneler, altyazı blokları) |
| `template/scripts/build.py` | Sentez SFX ve konuşmada kısma (ducking) ifadesi |
| `template/scripts/build_video.py` | Klip hazırlama, miks, kompozisyon, render, teslim |
| `template/composition_video/index.html` | HyperFrames şablonu (GSAP) |

### Nereden çıktı

Skill gerçek bir projede kurulup test edildi: Taş Galerisi için "Zebercet" taşı hakkında 7 sahneli, 2:22'lik bir Reels videosu.

---

## License / Lisans

MIT, see [`LICENSE`](LICENSE). Calibri is a Microsoft font and is not part of this repository. OpenMontage and HyperFrames are separate projects with their own licenses.

MIT, bkz. [`LICENSE`](LICENSE). Calibri Microsoft'un fontudur ve bu repoya dahil değildir. OpenMontage ve HyperFrames kendi lisansları olan ayrı projelerdir.
