"""Yan etkisiz ortak yardımcılar: sahne adı tanıma, sahne metni okuma, altyazı ve logo seçenekleri.

build_video.py, check.py ve testler bunu kullanır. Dosya okumak dışında hiçbir şey yapmaz.
"""
import re
from difflib import get_close_matches
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}
AUDIO_EXT = {".mp3", ".wav", ".m4a"}

# ---------- komut satırı ----------
# build_video.py ve check.py aynı seçenekleri kabul eder (SKILL.md iki komuta da aynı $STIL $LOGO'yu verir).
VALUE_OPTIONS = ("src", "name", "vo", "logo", "font", "script",
                 "caption-color", "caption-outline", "caption-style", "caption-anim",
                 "renk", "kontur", "stil", "anim",  # eski Türkçe adlar
                 "logo-mode", "logo-pos", "logo-size", "logo-moves")
FLAG_OPTIONS = ("skip-prep", "no-render", "tools-only", "skip-tools", "json")


def get_opt(argv: list[str], name: str, default: str = "") -> str:
    """--isim=değer seçeneği. ~ ile başlayan yollar açılır (--src=~/Desktop/x)."""
    v = next((a.split("=", 1)[1] for a in argv if a.startswith(f"--{name}=")), default)
    return str(Path(v).expanduser()) if v.startswith("~") else v


def check_unknown_options(argv: list[str]) -> None:
    """Yazım hatalı seçenekler sessizce yok sayılmasın (--caption-colour=white sarı altyazı vermesin)."""
    bad = []
    for a in argv:
        if not a.startswith("--"):
            continue
        key, eq, _ = a[2:].partition("=")
        if (eq and key in VALUE_OPTIONS) or (not eq and key in FLAG_OPTIONS):
            continue
        if not eq and key in VALUE_OPTIONS:
            bad.append(f"{a} (needs a value: --{key}=...)")
            continue
        near = get_close_matches(key, VALUE_OPTIONS + FLAG_OPTIONS, n=1, cutoff=0.6)
        bad.append(f"{a}" + (f" (did you mean --{near[0]}?)" if near else ""))
    if bad:
        raise OptionError("Unknown option / bilinmeyen seçenek: " + "; ".join(bad))


# ---------- seslendirme ----------
VO_NAMES = re.compile(r"seslendirme|voice|narrat|anlat[iı]m|d[iı][sş]\s*ses|(?:^|[^a-z])vo(?:[^a-z]|$)", re.I)


def pick_voiceover(audio: list[Path], given: str = "") -> Path:
    """--vo verildiyse o; yoksa adı seslendirme/voice/vo olan dosya; klasörde tek ses dosyası varsa o.
    Birden fazla ses dosyası var ve hiçbirinin adı seslendirme değilse tahmin etmez (müzik seçilebilir)."""
    if given:
        return Path(given)
    named = [p for p in audio if VO_NAMES.search(p.stem)]
    if len(named) == 1 or (named and len(audio) == len(named)):
        return named[0]
    if len(named) > 1:
        raise OptionError(f"several voiceover-like files / birden fazla seslendirme adayı: {[p.name for p in named]}. "
                          "Pass --vo=<file> / --vo= ile seç")
    if len(audio) == 1:
        return audio[0]
    if not audio:
        raise OptionError("voiceover (.mp3/.wav/.m4a) not found / seslendirme bulunamadı")
    raise OptionError(f"several audio files and none is named voiceover / seslendirme hangisi belli değil: "
                      f"{[p.name for p in audio]}. Pass --vo=<file> or put 'seslendirme' or 'voice' in its name")


# ---------- güvenli kopya ----------
def free_path(p: Path) -> Path:
    """p varsa üzerine yazmamak için ad_2, ad_3 ... döner."""
    if not p.exists():
        return p
    k = 2
    while (q := p.with_name(f"{p.stem}_{k}{p.suffix}")).exists():
        k += 1
    return q


# ---------- yavaşlatma ----------
MAX_SLOW = 2.0  # bundan fazla yavaşlatılan klipte kare ara-değerleme artefaktı görülebilir


def slow_factor(need: float, have: float) -> float:
    """Klibin sahneyi doldurması için gereken yavaşlatma (1 = normal hız)."""
    return max(1.0, need / have)


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
