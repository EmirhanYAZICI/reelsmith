---
name: reels-edit
description: Herhangi bir firma/marka için Instagram Reels videosu üretir (OpenMontage + Whisper + HyperFrames + ffmpeg). Kullanıcı bir klasör açar; içine seslendirme, sahne videoları (1sahne.mp4…), sahne metni, logo ve isteğe bağlı REELS-REHBERI.md koyar. Kullan - kullanıcı "reels yap", "reels videosu", "klasörü koydum başla", "/reels-edit <klasör>" dediğinde.
argument-hint: "<klasör adı veya yolu> [video adı]"
---

# Reels Edit (firma bağımsız)

Her firma için çalışır. Marka = klasördeki logo. Logo ve firma adı asla sabit kodlanmaz.
Örnek proje: Taş Galerisi, "Zebercet" Reels. Logoyu her projede kullanıcı koyar. Kendin logo seçme ya da üretme.

Girdi: `$ARGUMENTS`. İlk kelime(ler) klasör adı/yolu, varsa sonrası çıktı video adı.
Bu skill'in klasörü aşağıda `SKILL_DIR` diye geçer (bu dosyanın bulunduğu klasör, genelde `~/.claude/skills/reels-edit`).

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
- Altyazı rengi / stili / animasyonu kullanıcı söylediyse (ör. "beyaz, kutulu, kelime kelime hoplasın") `SKILL_DIR/ALTYAZI-STILLERI.md`'den karşılığını bul. Söylemediyse varsayılan: sarı + kontur + pop.

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
$PY scripts/transcribe.py "<seslendirme>" artifacts/voiceover_transcript.json "<metindeki özel isimler>"
$PY scripts/align.py "<sahne metni>"
STIL="--renk=sari --stil=outline --anim=pop"   # ALTYAZI-STILLERI.md
$PY scripts/build_video.py --src="<klasör>" --name=<konu>_reels_final.mp4 $STIL --no-render
(cd composition_video && npx --no-install hyperframes snapshot --at 0.5,10,30,60,90 --no-end)   # kareleri gör
$PY scripts/build_video.py --src="<klasör>" --name=<konu>_reels_final.mp4 $STIL --skip-prep    # render, arka planda
```
- Altyazı seçenekleri (`--renk`, `--kontur`, `--stil`, `--anim`) iki komutta da aynı verilmeli.
- Altyazı fontu Calibri Bold. Lisans gereği repoda yok. Script Windows'taki `C:\Windows\Fonts\calibrib.ttf` dosyasını kopyalar. Başka sistemde `--font=<yol>` ver.
- Klip hazırlığı + render 15-25 dk sürer. Arka planda çalıştır, bitince bildirim gelir. Bekleme döngüsü kurma.

## 4. Kontrol et ve teslim et
- ffprobe: 1080x1920, 30 fps.
- ebur128: ≈ -14 LUFS, tepe < -1 dBFS.
- freezedetect: 0 donma.
- Video kaynak klasöre ve `<üst klasör>/cikti/` klasörüne kopyalanır. İki yolu da kullanıcıya ver.

## Şablonu güncel tut
Bir projede kullanıcı onaylı yeni bir ayar yapılırsa (logo, altyazı, ses…) değişen dosyayı `SKILL_DIR/template/` içine de kopyala ve `REELS-REHBERI.md`'ye yaz. Sonraki projeler aynı ayarla başlar.

## Değişmez kurallar (rehber yoksa bile)
- Orijinal dosyaları değiştirme ya da silme. Kullanıcının söylemediği dosyayı kullanma.
- Ücretli API (Veo, Kling, ElevenLabs…) kullanmadan önce sor.
- Altyazı: yer ve boyut sabit (dikey, Calibri Bold 75px, alttan 450px, 2-3 kelime, yazım metinden). Sadece renk, stil ve animasyon değişir. Varsayılan sarı `#F8D85A` + siyah kontur + pop.
- Logo yüklendiği gibi (rengi neyse o) ve tam opak. Soluk değil, efekt yok. Sol alttan başlar, video boyunca köşeden köşeye yavaşça kayar.
- Ani zoom ya da punch-in yok. Sahne boyunca tek yumuşak dolly.
- Klip sesleri kalır. Konuşmada -9 dB kısılır. Ayrı müzik yok.
- 30 FPS.
- Kullanıcıyla Türkçe, sade konuş.
