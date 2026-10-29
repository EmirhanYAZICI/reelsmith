# Reelsmith Rehberi (genel komut, firma bağımsız)

> Her firma/marka için aynı akış. Marka = klasördeki logo. Firma adı ya da logo koda sabit yazılmaz.

> Claude: Bu dosyayı okuduysan, kullanıcının verdiği klasörle aşağıdaki akışı aynen uygula.
> Örnek proje: Taş Galerisi, "Zebercet" Reels (Ekim 2026). Bu akış o projede denendi ve onaylandı.
> Logoyu her projede kullanıcı kendisi koyar. Sahneler, metin ve altyazı konuya göre şekillenir.
> Hazır kod: skill klasöründeki `template/`.

## 0. Kullanıcı nasıl başlatır (tek mesaj)

OpenMontage repo kökünde Claude Code aç ve yaz (ya da `/reelsmith <klasör>`):

```
<klasör yolu> klasörünü kullan. REELS-REHBERI.md'yi oku ve ona göre yap.
Video adı: <konu>_reels_final.mp4. Plan sorma, direkt render al.
```

Claude ne yapar: md'yi okur, klasörü tarar, Whisper ile metni zamanlar, sahneleri kurar, render alır, kontrol eder ve çıktının yolunu söyler.
"Plan sorma" kısmını silersen render öncesi sahne listesi ve süreleri gösterip onay ister.

---

## 1. Kullanıcı ne verir

Bir klasör, örnek: `~/Desktop/<proje klasörü>/`. Yer değişebilir, kullanıcı yolu söyler.

| Dosya | Açıklama |
|---|---|
| Seslendirme (`.mp3` / `.wav`) | Adında "seslendirme" geçer. Tüm videonun süresini bu belirler. |
| Sahne videoları | Kullanıcı Gemini (Veo) ile üretir. Her biri ~10 sn, dikey, **kendi müziği/efekti var**. Adları `1sahne.mp4`, `2sahne.mp4` … gibi. Yazım hatası olabilir (`4sahen.mp4`), script bunu tanır. Bir sahneye 2 video da konabilir (`3sahne_b.mp4`). |
| Sahne metni (`.txt` / `.md`) | Her sahne için `Metin karşılığı: "…")` satırı. Bu metin seslendirmede okunan yazıdır ve altyazının doğru yazımı buradan gelir. |
| Logo (`.png`, şeffaf) | Firmanın logosu. Adında "logo" geçen png; yoksa klasördeki tek png. Birden fazla görsel varsa hangisi olduğunu sor. Script bunu otomatik alır, `assets/logo.png` yapar, yüksekliği logonun oranına göre ayarlar ve **hareketli** gösterir (bkz. Logo bölümü). Farklı adlıysa `--logo=<dosya>` ver. Logo yoksa script durur ve logo ister. |

**Sahne sayısı sabit değil.** Kullanıcı kaç sahne verirse (5, 7, 10…) o kadar sahne kurulur:
- Sahne metnindeki her `Metin karşılığı: "…")` = 1 sahne.
- Her sahneye numarası eşleşen video(lar) konur (`1sahne` → 1. sahne metni).
- Video sayısı ile sahne metni sayısı eşit olmalı. Eksik varsa script "Eksik sahne videoları: [n]" der, kullanıcıya sor.
- Her videonun süresi, Whisper'ın bulduğu o sahnenin konuşma süresine göre yavaşlatılarak ayarlanır.

Kurallar:
- Klasörü tara, dosyaları listele, neyin ne olduğunu kullanıcıyla teyit et.
- Kullanıcının söylemediği dosyayı kullanma. Orijinal dosyaları değiştirme ya da silme.
- Ayrı arka plan müziği koyma. Klasörde müzik dosyası olsa bile kullanıcı istemedikçe kullanma.
- Ücretli API (Kling, Veo, ElevenLabs…) kullanma. Gerekirse önce sor.
- Render öncesi kısa plan göster (sahne listesi, süreler, format), onay al.

---

## 2. Kullanılan araçlar ve skill'ler

| Araç | Ne için |
|---|---|
| **OpenMontage** ([calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)) | Ana çatı. Önce `AGENT_GUIDE.md` okunur. Çalışma alanı `projects/<proje-id>/`. |
| **Whisper** (`faster-whisper`, model `small`, `language="tr"`, kelime zamanları) | Seslendirmedeki her kelimenin saniyesi. Altyazı ve sahne sınırları bundan çıkar. |
| **HyperFrames** (`npx hyperframes`, v0.8.x) | HTML + GSAP ile kompozisyon: klipler, altyazı, logo animasyonu, ışık efektleri. Komutlar: `lint`, `snapshot`, `render`. |
| **ffmpeg** | Klip yavaşlatma (minterpolate), 9:16 kırpma, renk, ses miksajı, son kodlama. |
| Python | OpenMontage `.venv` (3.12). `PYTHONIOENCODING=utf-8` ile çalıştır. |

Skill'ler: `hyperframes`, `hyperframes-core`, `hyperframes-cli` (HyperFrames kuralları), `ffmpeg`, `speech-to-text` / OpenMontage `transcriber` (Whisper).

Not: OpenMontage `transcriber` aracı PyAV hatası verdi (`metadata_errors`). Bu yüzden `scripts/transcribe.py` sesi ffmpeg ile çözüp faster-whisper'a verir.

---

## 3. Adım adım akış

Skill'deki şablonu yeni proje olarak kopyala:

```bash
cd <OpenMontage>/projects
cp -r ~/.claude/skills/reelsmith/template <yeni-proje-id>
mkdir -p <yeni-proje-id>/artifacts <yeni-proje-id>/assets/audio && cd <yeni-proje-id>
PY=../../.venv/Scripts/python.exe          # Linux/macOS: ../../.venv/bin/python
export PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_XET=1
SRC="<kullanıcının verdiği klasör>"       # her zaman --src ile ver
```

**1) Whisper ile döküm**
```bash
$PY scripts/transcribe.py "$SRC/<seslendirme>.mp3" artifacts/voiceover_transcript.json "Özel isimler, virgülle"
```
Üçüncü argüman isteğe bağlı. Konudaki özel isimleri yazarsan Whisper onları doğru duyar.

**2) Metinle hizalama** (sahne süreleri + altyazı blokları)
```bash
$PY scripts/align.py "$SRC/<sahne metni>.txt"
```
Çıktı `artifacts/timeline.json`. Ekrana her sahnenin başlangıç/bitiş saniyesi yazılır. Bunu kullanıcıya plan olarak göster.

**3) Kurgu + render**
```bash
$PY scripts/build_video.py --src="$SRC" --name=<konu>_reels_final.mp4 --no-render   # önce hazırlık + kontrol
(cd composition_video && npx --no-install hyperframes snapshot --at 0.5,1.5,3,30,60)   # contact-sheet.jpg'ye bak
$PY scripts/build_video.py --src="$SRC" --name=<konu>_reels_final.mp4 --skip-prep   # render
```
- `--src=` kaynak klasör (zorunlu). Seslendirme ve logo otomatik bulunur. Bulamazsa `--vo=<dosya>` / `--logo=<dosya>` ver.
- Font: Calibri Bold Windows'tan (`C:\Windows\Fonts\calibrib.ttf`) kopyalanır. Lisans gereği repoda yok. Başka sistemde `--font=<yol>`.
- `--skip-prep` hazırlanmış klipleri tekrar işlemez. Sadece kompozisyon değişince kullan.
- Uzun sürer (klip hazırlığı + render ~15-25 dk). Arka planda çalıştır.

**4) Kontrol**
```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate:format=duration <final>
ffmpeg -i <final> -af ebur128=peak=true -f null -     # hedef ≈ -14 LUFS, tepe < -1 dBFS
ffmpeg -i <final> -vf freezedetect=n=0.003:d=1 -an -f null -   # donma olmamalı
```

**5) Teslim**
Son video iki yere kopyalanır (script otomatik yapar):
- kaynak klasör: `<proje klasörü>\<isim>.mp4`
- kaynak klasörün bir üstündeki `cikti\` klasörü: `<üst klasör>\cikti\<isim>.mp4`. Klasör yoksa oluşturulur.

---

## 4. Sabit ayarlar (kullanıcı onaylı, değiştirme)

### Format
- 1080x1920, **30 FPS** (Instagram'da kasmasın diye), H.264 High 4.2, CRF 18, maxrate 16M, AAC 256k 48 kHz, `+faststart`.

### Klipler (sahne videoları)
- Her klip kendi sahnesinin seslendirme süresine **yavaşlatılır**. Takılma olmasın diye ffmpeg `minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1` kullanılır.
- 720x1280 kırp/ölçekle, sonra 1080x1920'ye büyüt. Hafif renk düzeltme (eq + colorbalance + unsharp).
- Sahne geçişi: 0.8 sn crossfade + ışık süzmesi (light leak) + hafif sarsıntı/flash.

### Kamera hareketi
- **Ani zoom / punch-in YOK.** Sahte kesme/geçiş gibi görünür.
- Her sahne boyunca tek, yumuşak, kesintisiz dolly: scale 1.06 → 1.13 ve hafif yanal/dikey kayma (`sine.inOut`). Yön sahneden sahneye değişir.
- Üstte toz zerreleri, film greni, vinyet (canvas FX).

### Altyazı (yer ve boyut sabit, renk/stil/animasyon seçilebilir)
- **Sabit:**
  - Font **Calibri Bold** (`assets/calibrib.ttf`), boyut **75px**, alttan **450px** (720p'de 50 / 300'e karşılık gelir).
  - Dikey videoda ortalı.
  - 2-3 kelime, tek satır. Cümle sonunda her zaman böl. Karaoke ya da renkli vurgu yok.
- **Seçilebilir** (ayrıntı: `ALTYAZI-STILLERI.md`):
  - Renk `--renk=` (sari, beyaz, yesil, altin, turuncu, kirmizi, pembe, mavi, mor, siyah ya da `#RRGGBB`). Kontur rengi `--kontur=`.
  - Yazı şekli `--stil=`: `outline`, `box`, `shadow`, `double`.
  - Hoplayan giriş `--anim=`: `pop`, `hop`, `word-hop`, `bounce`, `wave`.
- **Varsayılan** (örnek proje Zebercet'te kullanılan): sarı `#F8D85A` + 10px siyah kontur + gölge (`outline`) + `pop` (opacity 0→1, scale 0.88→1, `back.out`). Sonraki blok gelince kaybolur.
- Yazım her zaman sahne metnindeki gibi olur (Whisper'ın yazımı değil).

### Logo (firmanın logosu) — HER ZAMAN HAREKETLİ
Kayan filigran. Amaç videonun çalınmasını, logonun kırpılıp atılmasını zorlaştırmak.
- Kullanıcının verdiği logo **yüklendiği gibi** kullanılır: rengi neyse o, **tam opak**. Soluk/saydam değil, gölge, parlama ya da ışık efekti yok.
- Boyut ~**260 px** genişlik (340 × 0.76, yükseklik orana göre).
- Başlangıç: **sol alt** köşe (altyazının hemen üstü), ilk karede görünür.
- Hareket: video boyunca **köşeden köşeye yavaşça** kayar, hiç durmaz. Sıra: sol alt → sağ üst → sağ alt → sol üst → sol alt …
  - Video süresi 6 ayağa bölünür. 2 dk'lık videoda her ayak ~24 sn, ease `sine.inOut`.
  - Köşeler: x 40 / 1080-genişlik-40, y 140 / altyazı bandının üstü (1370 - logo yüksekliği). Altyazının üstüne binmez.
- Ayarlar `composition_video/index.html` içinde: `LOGO_SCALE`, `CORNER_LEGS`.
- YAPMA: üst ortada sabit logo, hızlı zıplama, soluklaştırma, renk değiştirme, efekt. 

### Ses
- Seslendirme: loudnorm **-14 LUFS**, her zaman en önde.
- Klip sesleri (videoların kendi müziği/efekti) **kalır**. Normal hızda çalar (yavaşlatılmaz), sahne boyunca döngüyle uzatılır, kenarlarında fade vardır.
- Klip sesi: loudnorm -21 LUFS. Konuşma sırasında **-9 dB** kısılır (ducking), konuşma bitince geri gelir.
- Ekstra efekt az: sadece sahne geçişlerinde hafif whoosh (-22 dB).
- Ayrı arka plan müziği **yok**.
- Sonda alimiter (tepe ≈ -1 dBFS).

---

## 5. Dosya haritası (`projects/<proje-id>/`)

| Dosya | Görev |
|---|---|
| `scripts/transcribe.py` | Whisper → `artifacts/voiceover_transcript.json` |
| `scripts/align.py` | Döküm + sahne metni → `artifacts/timeline.json` (sahneler, kelimeler, altyazı blokları) |
| `scripts/build.py` | SFX üretimi, ducking ifadesi, `timeline.json` yükleme |
| `scripts/build_video.py` | Klip bulma, yavaşlatma, ses hazırlama, miks, `data.js` yazma, HyperFrames render, mux, kopyalama |
| `composition_video/index.html` | HyperFrames şablonu: klipler, altyazı stili, logo animasyonu, kamera hareketi, FX |
| `composition_video/data.js` | Otomatik üretilir (segmentler, altyazılar). Elle düzenleme. |
| `composition_video/assets/` | `logo.png` ve `calibrib.ttf` (script kopyalar), `clips/` (hazırlanmış klipler) |
| `assets/audio/` | SFX ve son miks (`mix.wav`) |

HyperFrames kuralları (bozma):
- `<video>` öğeleri root'un doğrudan çocuğu olmalı.
- GSAP timeline `paused` olur ve `window.__timelines["main"]` altına kaydedilir.
- Rastgelelik sabit tohumlu (seeded) olmalı, sonsuz `repeat: -1` olmamalı.
- Render öncesi `npx hyperframes lint` 0 hata vermeli.

---

## 6. Sık sorunlar

| Sorun | Çözüm |
|---|---|
| Whisper modeli indirmede takılıyor | `HF_HUB_DISABLE_XET=1` ile `small` modeli kullan. |
| `transcriber` PyAV hatası | `scripts/transcribe.py` kullan (ffmpeg ile çözer). |
| "Eksik sahne videoları: [n]" | Dosya adında sahne numarası yok. Kullanıcıya sor, adı değiştirmeden `sahneler\` alt klasörüne doğru adla kopya koy. |
| Altyazıda iki cümle tek blokta | `align.py` cümle sonunda zaten böler. Metinde noktalama eksik olabilir. |
| "Font bulunamadı" | Calibri Bold yolunu `--font=` ile ver. |
| Font lint hatası | Kullanılan her font için `@font-face` olmalı, yedek font adı yazma. |
| Sahne metni farklı formatta | `align.py` `Metin karşılığı: "…")` arar. Farklıysa `scene_texts()` regex'ini uyarla. |
