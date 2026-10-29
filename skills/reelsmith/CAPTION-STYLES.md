# Caption Styles / Altyazı Stilleri

Caption **placement and size are fixed**: vertical 1080x1920, Calibri Bold 75 px, 450 px from the bottom, centered, one line, 2-3 words.
Only three things change: **color**, **text style**, **entry animation**.

Altyazının **yeri ve boyutu sabittir**: dikey 1080x1920, Calibri Bold 75 px, alttan 450 px, ortalı, tek satır, 2-3 kelime.
Sadece üç şey değişir: **renk**, **yazı şekli**, **giriş animasyonu**.

```bash
$PY scripts/build_video.py --src="<folder>" --caption-color=white --caption-style=box --caption-anim=word-hop
```

| Option | Default | Values |
|---|---|---|
| `--caption-color` | `yellow` | color name or `#RRGGBB` |
| `--caption-outline` | `#000000` | color name or `#RRGGBB` (outline / shadow color) |
| `--caption-style` | `outline` | `outline`, `box`, `shadow`, `double` |
| `--caption-anim` | `pop` | `pop`, `hop`, `word-hop`, `bounce`, `wave` |

Older Turkish flags still work: `--renk`, `--kontur`, `--stil`, `--anim`.
Eski Türkçe seçenekler de çalışır: `--renk`, `--kontur`, `--stil`, `--anim`.

## Colors / Renkler

| Name | Türkçe | Hex | Good for / Uygun konu |
|---|---|---|---|
| `yellow` | `sari` | `#F8D85A` | Classic Reels caption / klasik Reels altyazısı |
| `white` | `beyaz` | `#FFFFFF` | Anything / her video |
| `green` | `yesil` | `#B8E04A` | Nature, stones, health / doğa, taş, sağlık |
| `gold` | `altin` | `#E8C15A` | Jewelry, luxury / mücevher, lüks |
| `orange` | `turuncu` | `#FFA53D` | Energy, food / enerji, yemek |
| `red` | `kirmizi` | `#FF5A5A` | Alerts / uyarı, dikkat |
| `pink` | `pembe` | `#FF7AC6` | Fashion, beauty / moda, güzellik |
| `blue` | `mavi` | `#5AC8FA` | Tech, sea / teknoloji, deniz |
| `purple` | `mor` | `#B79CFF` | Mystic, night / mistik, gece |
| `black` | `siyah` | `#111111` | Use with a light outline or box / açık kontur ya da kutu ile |

Any hex also works / herhangi bir hex de olur: `--caption-color=#00E5A0`. Turkish spelling with special letters is accepted too (`sarı`, `yeşil`).

## Text styles / Yazı şekilleri: `--caption-style`

| Style | Look / Görünüm | Use when / Ne zaman |
|---|---|---|
| `outline` | Thick outline + drop shadow / kalın kontur + alt gölge | Any background, most readable / her zemin, en okunaklı |
| `box` | Each word in a dark rounded label, no outline / her kelime koyu yuvarlak kutuda | Busy footage / hareketli, karışık görüntü |
| `shadow` | No outline, hard drop + soft dark halo / kontursuz, sert gölge + yumuşak hale | Clean, cinematic / sade, sinematik |
| `double` | Outline plus a thin second ring / kontur + ince ikinci halka | Playful, eye-catching / eğlenceli, dikkat çekici |

## Entry animations / Giriş animasyonları: `--caption-anim`

| Animation | Motion / Hareket |
|---|---|
| `pop` | Block scales up slightly into place (0.12 s) / blok hafifçe büyüyerek belirir |
| `hop` | Block jumps up from below, overshoots, settles / blok aşağıdan zıplayıp yerine oturur |
| `word-hop` | Each word jumps in **exactly when it is spoken** (Whisper word timing) / her kelime söylendiği anda zıplar |
| `bounce` | Block drops from above and bounces / blok yukarıdan düşüp seker |
| `wave` | Block appears, words ripple up and down in sequence / kelimeler sırayla dalga gibi hoplar |

Every block disappears when the next one arrives. There is no karaoke or color-changing highlight.
Her blok bir sonraki gelince kaybolur. Karaoke ya da renk değiştiren vurgu yoktur.

## Presets / Hazır kombinasyonlar

| Topic / Konu | Flags |
|---|---|
| Gems, jewelry (reference project: Taş Galerisi, "Zebercet") | `--caption-color=yellow --caption-style=outline --caption-anim=pop` |
| Luxury product / lüks ürün | `--caption-color=gold --caption-style=shadow --caption-anim=hop` |
| Fast, energetic / hızlı, enerjik | `--caption-color=white --caption-style=box --caption-anim=word-hop` |
| Fun, young audience / eğlenceli, genç kitle | `--caption-color=pink --caption-outline=#2A0018 --caption-style=double --caption-anim=wave` |
| Nature, health / doğa, sağlık | `--caption-color=green --caption-style=outline --caption-anim=bounce` |

## Rules for the agent / Ajan için kurallar

- Never change placement, size or font unless the user explicitly asks (`.chunk` and `.w` in `index.html`).
- If the user names no style, use the defaults. Do not pick a style on your own.
- Pass the same caption flags to both `build_video.py` runs (`--no-render` and `--skip-prep`).
- To add a style or animation, update three places together:
  - `template/composition_video/index.html`: CSS `.style-<name>` and the JS `CAP.anim` branch.
  - `template/scripts/build_video.py`: `STYLES` / `ANIMS` / `COLORS`.
  - This file.
