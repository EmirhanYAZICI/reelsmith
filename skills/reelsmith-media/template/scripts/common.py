"""Yan etkisiz ortak yardımcılar: sahne adı tanıma, sahne metni okuma, altyazı ve logo seçenekleri.

build_video.py, check.py ve testler bunu kullanır. Dosya okumak dışında hiçbir şey yapmaz.
"""
import re
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO_EXT = {".mp3", ".wav", ".m4a"}

# ---------- altyazı fontu ----------
CALIBRI = Path(r"C:\Windows\Fonts\calibrib.ttf")
CARLITO = Path(__file__).resolve().parent.parent / "fonts" / "Carlito-Bold.ttf"  # Calibri ile aynı ölçüler, OFL


def caption_font(given: str = "") -> Path:
    """--font verildiyse o; yoksa sistemde Calibri Bold varsa o; yoksa repodaki Carlito Bold."""
    if given:
        return Path(given)
    return CALIBRI if CALIBRI.is_file() else CARLITO

# ---------- sahne videoları ----------
ORDINALS = {"birinci": 1, "ilk": 1, "ikinci": 2, "üçüncü": 3, "ucuncu": 3, "dördüncü": 4, "dorduncu": 4,
            "beşinci": 5, "besinci": 5, "altıncı": 6, "altinci": 6, "yedinci": 7,
            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7}


def scene_number(stem: str, n_scenes: int = 99) -> int | None:
    """'sahne 1', '1.sahne', 'ikinci sahne', 'scene1', 'scene_2b', 'third scene' -> sahne numarası."""
    s = re.sub(r"scene|sah[en]{2}|shane|sahn", "sahne", stem.lower())  # 'sahen' gibi yazım hataları
    if "sahne" not in s:
        return None
    m = re.search(r"sahne\s*[._-]?\s*(\d+)", s) or re.search(r"(\d+)\s*[._-]?\s*\.?\s*sahne", s)
    if m:
        n = int(m.group(1))
        return n if 1 <= n <= n_scenes else None
    for word, n in ORDINALS.items():
        if word in s:
            return n if n <= n_scenes else None
    return None


def group_clips(folder: Path, n_scenes: int) -> tuple[dict[int, list[Path]], list[int]]:
    """Klasördeki videoları sahne numarasına göre gruplar. (bulunanlar, eksik numaralar) döner."""
    found: dict[int, list[Path]] = {}
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() in VIDEO_EXT:
            n = scene_number(p.stem, n_scenes)
            if n:
                found.setdefault(n, []).append(p)
    return found, [n for n in range(1, n_scenes + 1) if n not in found]


def plan_segments(scenes: list[dict], clips: dict[int, list[Path]], duration: float, tr: float) -> list[dict]:
    """Her sahnenin süresini o sahnenin klipleri arasında eşit böler; geçiş için tr/2 bindirme ekler."""
    segs = []
    for sc in scenes:
        files = clips[sc["index"]]
        a, b = sc["start"], sc["end"]
        step = (b - a) / len(files)
        for k, f in enumerate(files):
            segs.append({"scene": sc["index"], "file": str(f), "first": k == 0,
                         "start": round(a + k * step, 3), "end": round(a + (k + 1) * step, 3)})
    for i, s in enumerate(segs):
        s["vstart"] = 0.0 if i == 0 else round(s["start"] - tr / 2, 3)
        s["vend"] = duration if i == len(segs) - 1 else round(s["end"] + tr / 2, 3)
    return segs


# ---------- sahne metni ----------
def scene_texts(raw: str) -> list[str]:
    """Sahne metninden her sahnede okunan yazıyı çıkarır. Üç biçim kabul edilir (ilk bulunan kazanır):
    1. `Metin karşılığı: "..."`)  (orijinal biçim)
    2. `Text: "..."` ya da `Metin: "..."` satırları
    3. Etiket yoksa: boş satırla ayrılmış her paragraf bir sahne ('#' ile başlayan satırlar atlanır)
    """
    found = re.findall(r'Metin karşılığı:\s*"(.+?)"\)', raw, flags=re.S)
    if not found:
        found = re.findall(r'^\s*(?:Text|Metin|Script)\s*:\s*"(.+?)"\s*\)?\s*$', raw, flags=re.M | re.I)
    if not found:
        body = "\n".join(line for line in raw.splitlines() if not line.lstrip().startswith("#"))
        found = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    return [" ".join(t.split()) for t in found]


# ---------- altyazı ----------
COLORS = {"yellow": "#F8D85A", "white": "#FFFFFF", "green": "#B8E04A", "gold": "#E8C15A", "orange": "#FFA53D",
          "red": "#FF5A5A", "pink": "#FF7AC6", "blue": "#5AC8FA", "purple": "#B79CFF", "black": "#111111"}
COLOR_ALIASES = {"sari": "yellow", "beyaz": "white", "yesil": "green", "altin": "gold", "turuncu": "orange",
                 "kirmizi": "red", "pembe": "pink", "mavi": "blue", "mor": "purple", "siyah": "black"}
STYLES = ("outline", "box", "shadow", "double")
ANIMS = ("pop", "hop", "word-hop", "bounce", "wave")


class OptionError(ValueError):
    pass


def parse_color(v: str) -> str:
    v = v.lower()
    for a, b in zip("ışğüöç", "isguoc"):
        v = v.replace(a, b)
    v = COLOR_ALIASES.get(v, v)
    if v in COLORS:
        return COLORS[v]
    if re.fullmatch(r"#?[0-9a-f]{6}", v):
        return "#" + v.lstrip("#").upper()
    raise OptionError(f"Unknown color / bilinmeyen renk: {v}. Options: {', '.join(COLORS)} or #RRGGBB")


def caption_options(opt) -> dict:
    """opt(name) -> komut satırı değeri ya da ''. Eski Türkçe adlar da çalışır: --renk, --kontur, --stil, --anim."""
    def cap(name, old, default):
        return opt(f"caption-{name}") or opt(old) or default
    c = {"fill": parse_color(cap("color", "renk", "yellow")), "stroke": parse_color(cap("outline", "kontur", "#000000")),
         "style": cap("style", "stil", "outline"), "anim": cap("anim", "anim", "pop")}
    if c["style"] not in STYLES:
        raise OptionError(f"Unknown style / bilinmeyen stil: {c['style']}. Options: {', '.join(STYLES)}")
    if c["anim"] not in ANIMS:
        raise OptionError(f"Unknown animation / bilinmeyen animasyon: {c['anim']}. Options: {', '.join(ANIMS)}")
    return c


# ---------- logo ----------
LOGO_MODES = ("move", "corner", "ends")  # kayan filigran / sabit köşe / açılış + kapanış
LOGO_POSITIONS = ("bottom-left", "bottom-right", "top-left", "top-right")


def logo_options(opt) -> dict:
    """--logo-mode=move|corner|ends (birleştirilebilir: corner,ends), --logo-pos, --logo-size (px), --logo-moves."""
    modes = [m.strip() for m in (opt("logo-mode") or "move").split(",") if m.strip()]
    bad = [m for m in modes if m not in LOGO_MODES]
    if bad or not modes or ("move" in modes and "corner" in modes):
        raise OptionError(f"Bad --logo-mode: {opt('logo-mode')}. Options: move, corner, ends "
                          "(ends can be combined: move,ends or corner,ends)")
    pos = opt("logo-pos") or "bottom-left"
    if pos not in LOGO_POSITIONS:
        raise OptionError(f"Bad --logo-pos: {pos}. Options: {', '.join(LOGO_POSITIONS)}")
    try:
        size = int(opt("logo-size") or 258)
        moves = int(opt("logo-moves") or 6)
    except ValueError:
        raise OptionError("--logo-size and --logo-moves must be whole numbers") from None
    if not 80 <= size <= 700:
        raise OptionError(f"--logo-size must be 80-700 px (got {size})")
    if not 1 <= moves <= 60:
        raise OptionError(f"--logo-moves must be 1-60 (got {moves})")
    return {"modes": modes, "pos": pos, "size": size, "moves": moves}
