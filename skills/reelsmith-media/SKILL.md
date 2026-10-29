---
name: reelsmith-media
description: "Create Instagram Reels from a local folder: voiceover, numbered scene clips (scene1.mp4 or 1sahne.mp4), a scene-by-scene script and a logo. Automates Whisper word-timed captions, scene editing, audio mixing and 1080x1920 rendering with FFmpeg and HyperFrames. Works with Turkish narration. Use when the user says \"make a reel\", \"reels yap\", \"reels videosu\", \"klasörü koydum başla\" or \"/reelsmith-media <folder>\"."
argument-hint: "<folder name or path> [output filename]"
---

# Reelsmith Media (firma bağımsız)

Her firma için çalışır. Marka = klasördeki logo. Logo ve firma adı asla sabit kodlanmaz.
Örnek proje: Taş Galerisi, "Zebercet" Reels. Logoyu her projede kullanıcı koyar. Kendin logo seçme ya da üretme.

Girdi: `$ARGUMENTS`. İlk kelime(ler) klasör adı/yolu, varsa sonrası çıktı video adı.
Bu skill'in klasörü aşağıda `SKILL_DIR` diye geçer (bu dosyanın bulunduğu klasör, ör. `~/.claude/skills/reelsmith-media`, `.cursor/skills/reelsmith-media`, `~/.codex/skills/reelsmith-media`).

## 0. Klasörü bul
- Tam yol verildiyse onu kullan.
- Sadece ad verildiyse önce `~/Desktop/<ad>`, sonra Desktop altında 2 seviye ara.
- Klasör yoksa ya da ad verilmediyse kullanıcıya klasör adını sor. Başka bir şey yapma.

## 1. Kuralları ve yardımcı skill'leri yükle (sıra önemli)
1. Klasörde `REELS-REHBERI.md` (ya da başka bir `*.md` rehber) varsa **onu oku. O kazanır.**
2. Yoksa `SKILL_DIR/REELS-REHBERI.md` dosyasını oku.
3. OpenMontage'ın `AGENT_GUIDE.md` dosyası repo kuralıdır. Onu da oku.
4. Yardımcı skill'leri yükle (Skill aracıyla; listede yoksa atla, şablon onlarsız da çalışır):
   - `whisper-tr`: yerel Whisper ile Türkçe kelime zamanları. Ücretli `speech-to-text` (ElevenLabs) **kullanma**.
   - `hyperframes-core` + `hyperframes-cli`: kompozisyon kuralları, `lint` / `snapshot` / `render`. Şablonun `index.html`'ini değiştireceksen önce bunları oku.
   - `ffmpeg`: klip kırpma, yavaşlatma ve ses işleri gerekirse (OpenMontage içinde yüklüdür).

## 2. Klasörü tara ve listele
Dosyaları türüne göre ayır: seslendirme, sahne videoları (numaralarıyla), sahne metni, logo, müzik, diğer.
- Logo: klasördeki png. Birden fazla görsel varsa ve hangisinin logo olduğu belli değilse sor. Logo yoksa sor.
- Video sayısı = metindeki `Metin karşılığı` sayısı mı? Değilse eksik numarayı söyle ve sor.
- Ayrı müzik dosyası varsa: varsayılan kural "ayrı müzik yok, kliplerin kendi sesi kalır". Kullanıcı müziği kendisi koyduysa ne yapılacağını bir cümleyle sor.
- Belirsiz bir şey yoksa sorma, devam et. Kullanıcı "plan sorma" dediyse planı sadece bilgi olarak yaz.
- Sahne metni üç biçimden biri olabilir: `Metin karşılığı: "…")` satırları, `Metin:`/`Text:` satırları ya da her sahne bir paragraf.
- Altyazı rengi / stili / animasyonu kullanıcı söylediyse (ör. "beyaz, kutulu, kelime kelime hoplasın") `SKILL_DIR/CAPTION-STYLES.md`'den karşılığını bul. Söylemediyse varsayılan: sarı + kontur + pop.

## 2b. Ön kontrol (her zaman, uzun işlerden önce)
Proje kopyalanmadan önce de çalışır (`OM` için 3. adıma bak):
```bash
"$OM/.venv/Scripts/python.exe" "SKILL_DIR/template/scripts/check.py" --src="<klasör>" [--script=] [--vo=] [--logo=] [--caption-*=] [--logo-*=]
```
- FAIL varsa dur, sorunu ve çözümü kullanıcıya düz cümleyle söyle (ör. "3. sahnenin videosu yok", "2sahne.mp4 bozuk görünüyor"). Düzeltince tekrar çalıştır.
- WARN render'ı durdurmaz; kullanıcıya bir cümleyle bildir (ör. yatay klip kırpılacak, logo şeffaf değil).

## 3. Çalıştır
Kod bu skill'in içinde: `SKILL_DIR/template/` (Python scriptleri + HyperFrames şablonu).
Çalışma yeri OpenMontage repo kökü (`OM`). İş `projects/<proje-id>/` içinde yapılır (OpenMontage kuralı).
`OM` şu sırayla bulunur: şu anki klasör OpenMontage ise orası; değilse `$OPENMONTAGE_DIR`; o da yoksa `~/Projects/OpenMontage`. Hiçbiri yoksa kullanıcıya sor.
Skill her klasörden çağrılabilir. Komutlar yine OpenMontage içinde çalışır.

```bash
OM="${OPENMONTAGE_DIR:-$HOME/Projects/OpenMontage}"; P="$OM/projects/<konu>-reels"
cp -r "SKILL_DIR/template" "$P" && mkdir -p "$P/artifacts" "$P/assets/audio" && cd "$P"
PY=../../.venv/Scripts/python.exe          # Linux/macOS: ../../.venv/bin/python
export PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_XET=1
STIL="--caption-color=yellow --caption-style=outline --caption-anim=pop"   # CAPTION-STYLES.md
LOGO="--logo-mode=move --logo-pos=bottom-left"                            # REELS-REHBERI.md > Logo
$PY scripts/check.py --src="<klasör>" $STIL $LOGO                                          # FAIL varsa dur
$PY scripts/transcribe.py "<seslendirme>" artifacts/voiceover_transcript.json "<metindeki özel isimler>" --language=tr   # İngilizce: en, bilinmiyor: auto
$PY scripts/align.py "<sahne metni>"
$PY scripts/build_video.py --src="<klasör>" --name=<konu>_reels_final.mp4 $STIL $LOGO --no-render
(cd composition_video && npx --no-install hyperframes snapshot --at 0.5,10,30,60,90 --no-end)   # kareleri gör
$PY scripts/build_video.py --src="<klasör>" --name=<konu>_reels_final.mp4 $STIL $LOGO --skip-prep    # render, arka planda
```
- Altyazı (`--caption-*`) ve logo (`--logo-mode`, `--logo-pos`, `--logo-size`, `--logo-moves`) seçenekleri bütün komutlarda aynı verilmeli.
- Kullanıcı logo için bir şey söylemediyse `$LOGO` varsayılan kalır (hareketli, sol alttan). "Sabit", "sağ üstte", "başta ve sonda büyük" gibi istekleri `REELS-REHBERI.md` > Logo tablosundan çevir.
- Render yarıda kesilirse klipler hazırdır: aynı komutu `--skip-prep` ile tekrar çalıştır.
- Seslendirme Türkçe değilse `transcribe.py`'ye dilini ver: `--language=en`, `--language=de`... Emin değilsen `--language=auto`.
- Altyazı fontu: Windows'ta Calibri Bold (`C:\Windows\Fonts\calibrib.ttf`), yoksa repodaki Carlito Bold (`template/fonts/`, Calibri ile aynı ölçüler, OFL lisanslı). Başka bir font için `--font=<yol>` ver.
- Klip hazırlığı + render 15-25 dk sürer. Arka planda çalıştır, bitince bildirim gelir. Bekleme döngüsü kurma.

## 4. Kontrol et ve teslim et
- `build_video.py` render sonunda `scripts/verify.py`'yi kendisi çalıştırır: 1080x1920, 30 fps, H.264 + AAC, ≈ -14 LUFS, tepe < -0.5 dBFS, 0 donma, faststart, süre.
- Elle: `$PY scripts/verify.py renders/<isim>.mp4 --duration=<timeline süresi>`. FAIL varsa kullanıcıya hangi kontrolün kaldığını düz cümleyle söyle.
- Video kaynak klasöre ve `<üst klasör>/cikti/` klasörüne kopyalanır. İki yolu da kullanıcıya ver.

## Şablonu güncel tut
Bir projede kullanıcı onaylı yeni bir ayar yapılırsa (logo, altyazı, ses…) değişen dosyayı `SKILL_DIR/template/` içine de kopyala ve `REELS-REHBERI.md`'ye yaz. Sonraki projeler aynı ayarla başlar.

## Değişmez kurallar (rehber yoksa bile)
- Orijinal dosyaları değiştirme ya da silme. Kullanıcının söylemediği dosyayı kullanma.
- Ücretli API (Veo, Kling, ElevenLabs…) kullanmadan önce sor.
- Altyazı: yer ve boyut sabit (dikey, Calibri Bold 75px, alttan 450px, 2-3 kelime, yazım metinden). Sadece renk, stil ve animasyon değişir. Varsayılan sarı `#F8D85A` + siyah kontur + pop.
- Logo yüklendiği gibi (rengi neyse o) ve tam opak. Soluk değil, efekt yok. Varsayılan: sol alttan başlar, video boyunca köşeden köşeye yavaşça kayar. Kullanıcı isterse sabit köşe ya da açılış/kapanış logosu (`--logo-mode`).
- Ani zoom ya da punch-in yok. Sahne boyunca tek yumuşak dolly.
- Klip sesleri kalır. Konuşmada -9 dB kısılır. Ayrı müzik yok.
- 30 FPS.
- Kullanıcıyla Türkçe, sade konuş.
