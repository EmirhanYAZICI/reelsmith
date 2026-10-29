# Altyazı Stilleri

Altyazının **yeri ve boyutu sabittir**: dikey 1080x1920, Calibri Bold 75px, alttan 450px, ortalı, tek satır, 2-3 kelime.
Sadece üç şey değişir: **renk**, **yazı şekli (stil)**, **giriş animasyonu**.
Hepsi `build_video.py` seçenekleriyle verilir. Verilmezse varsayılan kullanılır (sarı + kontur + pop).

```bash
$PY scripts/build_video.py --src="<klasör>" --renk=beyaz --stil=box --anim=word-hop
```

## Renk: `--renk=` ve `--kontur=`

| Ad | Renk | Not |
|---|---|---|
| `sari` (varsayılan) | `#F8D85A` | Klasik Reels altyazısı |
| `beyaz` | `#FFFFFF` | Her videoya uyar |
| `yesil` | `#B8E04A` | Doğa, taş, sağlık |
| `altin` | `#E8C15A` | Mücevher, lüks |
| `turuncu` | `#FFA53D` | Enerji, yemek |
| `kirmizi` | `#FF5A5A` | Uyarı, dikkat |
| `pembe` | `#FF7AC6` | Moda, güzellik |
| `mavi` | `#5AC8FA` | Teknoloji, deniz |
| `mor` | `#B79CFF` | Mistik, gece |
| `siyah` | `#111111` | Açık renk kontur/kutu ile kullan |

- Hazır ad yerine `#RRGGBB` de yazılabilir: `--renk=#00E5A0`.
- `--kontur=` kontur/gölge rengidir. Varsayılan `#000000`. Hazır ad ya da `#RRGGBB` alır.
- Türkçe karakterli yazım da kabul edilir: `sarı`, `yeşil`, `kırmızı`.

## Yazı şekli: `--stil=`

| Stil | Görünüm | Ne zaman |
|---|---|---|
| `outline` (varsayılan) | Kalın kontur + alt gölge | Her zemin. En okunaklı |
| `box` | Her kelime koyu, yuvarlak köşeli kutu içinde, kontursuz | Çok hareketli/karışık görüntü |
| `shadow` | Kontur yok. Altta sert gölge + yumuşak koyu hale | Sade, sinematik videolar |
| `double` | Kontur + dışta ince ikinci halka | Dikkat çekici, eğlenceli içerik |

## Animasyon (hoplayan yazılar): `--anim=`

| Animasyon | Hareket |
|---|---|
| `pop` (varsayılan) | Blok hafifçe büyüyerek belirir (0.12 sn) |
| `hop` | Blok aşağıdan zıplayarak gelir, hafif taşıp yerine oturur |
| `word-hop` | Her kelime **kendi söylendiği anda** tek tek zıplar (Whisper kelime zamanı) |
| `bounce` | Blok yukarıdan düşer, yere çarpıp seker |
| `wave` | Blok belirir, kelimeler sırayla dalga gibi yukarı-aşağı hoplar |

Tüm animasyonlarda blok, bir sonraki blok gelince kaybolur. Karaoke ya da renk değiştiren vurgu yoktur.

## Hazır kombinasyonlar

| Konu | Komut |
|---|---|
| Taş / mücevher (örnek proje: Taş Galerisi, Zebercet) | `--renk=sari --stil=outline --anim=pop` |
| Lüks ürün | `--renk=altin --stil=shadow --anim=hop` |
| Hızlı, enerjik içerik | `--renk=beyaz --stil=box --anim=word-hop` |
| Eğlenceli / genç kitle | `--renk=pembe --kontur=#2A0018 --stil=double --anim=wave` |
| Doğa, sağlık | `--renk=yesil --stil=outline --anim=bounce` |

## Kurallar

- Yer, boyut ve font **değişmez**. Kullanıcı açıkça istemedikçe `index.html` içindeki `.chunk` ve `.w` ölçülerine dokunma.
- Kullanıcı stil söylemezse varsayılanı kullan. Kendi başına stil değiştirme.
- Yeni stil ya da animasyon eklenirse üç yer birlikte güncellenir:
  - `template/composition_video/index.html`: CSS `.style-<ad>` ve JS `CAP.anim` dalı.
  - `template/scripts/build_video.py`: `STYLES` / `ANIMS` / `COLORS`.
  - Bu dosya.
