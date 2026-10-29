"""Sahne videolarından final Reels videosunu üretir.

Kullanım:
  python build_video.py --src=<kaynak klasör> [--name=video.mp4] [--vo=ses.mp3] [--logo=logo.png]
                        [--font=calibrib.ttf] [--caption-color=yellow] [--caption-outline=#000000]
                        [--caption-style=outline] [--caption-anim=pop]
                        [--skip-prep] [--no-render] [<sahne klasörü>]

1. sahne videolarını numarasına göre bulur (1sahne, sahne 1, sahne1_a, ikinci sahne ...)
2. her klibi sahne süresine göre 1080x1920/30fps'e kırpar, kare ara-değerlemeyle yavaşlatır, renk düzenler
3. logoyu ve fontu kompozisyona kopyalar, composition_video/index.html'e video etiketlerini ve data.js'yi yazar
4. ses miksajını yapar (seslendirme + kliplerin kendi sesi, konuşmada kısılır + geçişte whoosh)
5. HyperFrames ile render alır, sesi ekleyip Instagram'a uygun kodlar, çıktıyı kopyalar
"""
import json
import math
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402  (SFX + miks fonksiyonları)

COMP = ROOT / "composition_video"
CLIPS = COMP / "assets" / "clips"
def _opt(name: str, default: str = "") -> str:
    """--isim=değer şeklindeki komut satırı seçeneği."""
    return next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), default)


if not _opt("src"):
    raise SystemExit("Kaynak klasörü ver: --src=<klasör>  (seslendirme, sahne videoları, logo)")
SRC_DIR = Path(_opt("src"))
# Seslendirme: --vo= verilmezse adında "seslendirme/voice/vo" geçen ses dosyası, yoksa ilk ses dosyası
_audio = sorted(p for p in SRC_DIR.iterdir() if p.suffix.lower() in {".mp3", ".wav", ".m4a"})
VO = Path(_opt("vo")) if _opt("vo") else next(
    (p for p in _audio if re.search(r"seslendirme|voice|\bvo\b", p.stem.lower())),
    _audio[0] if _audio else SRC_DIR / "seslendirme.mp3")
FINAL_NAME = _opt("name", "reels_final.mp4")
# Logo (firma bağımsız): --logo= verilmezse adında "logo" geçen png, yoksa klasördeki tek png;
# bulunamazsa script durur ve logo ister
_pngs = sorted(p for p in SRC_DIR.iterdir() if p.suffix.lower() == ".png")
LOGO = Path(_opt("logo")) if _opt("logo") else next(
    (p for p in _pngs if re.search(r"logo", p.stem.lower())), _pngs[0] if len(_pngs) == 1 else None)
LOGO_W = 340  # ekrandaki logo genişliği (px)
# Altyazı fontu Calibri Bold: lisans gereği repoda yok, Windows'tan (ya da --font=) kopyalanır
FONT = Path(_opt("font", r"C:\Windows\Fonts\calibrib.ttf"))
# Altyazı görünümü: yer/boyut sabit, sadece renk + yazı şekli + animasyon değişir (bkz. CAPTION-STYLES.md)
# Seçenekler: --caption-color, --caption-outline, --caption-style, --caption-anim
# (eski Türkçe adlar da çalışır: --renk, --kontur, --stil, --anim)
COLORS = {"yellow": "#F8D85A", "white": "#FFFFFF", "green": "#B8E04A", "gold": "#E8C15A", "orange": "#FFA53D",
          "red": "#FF5A5A", "pink": "#FF7AC6", "blue": "#5AC8FA", "purple": "#B79CFF", "black": "#111111"}
COLOR_ALIASES = {"sari": "yellow", "beyaz": "white", "yesil": "green", "altin": "gold", "turuncu": "orange",
                 "kirmizi": "red", "pembe": "pink", "mavi": "blue", "mor": "purple", "siyah": "black"}
STYLES = ("outline", "box", "shadow", "double")
ANIMS = ("pop", "hop", "word-hop", "bounce", "wave")


def _color(v: str) -> str:
    v = v.lower()
    for a, b in zip("ışğüöç", "isguoc"):
        v = v.replace(a, b)
    v = COLOR_ALIASES.get(v, v)
    if v in COLORS:
        return COLORS[v]
    if re.fullmatch(r"#?[0-9a-f]{6}", v):
        return "#" + v.lstrip("#").upper()
    raise SystemExit(f"Unknown color / bilinmeyen renk: {v}. Options: {', '.join(COLORS)} or #RRGGBB")


def _cap(name: str, old: str, default: str) -> str:
    return _opt(f"caption-{name}") or _opt(old) or default


CAPTION = {"fill": _color(_cap("color", "renk", "yellow")), "stroke": _color(_cap("outline", "kontur", "#000000")),
           "style": _cap("style", "stil", "outline"), "anim": _cap("anim", "anim", "pop")}
if CAPTION["style"] not in STYLES:
    raise SystemExit(f"Unknown style / bilinmeyen stil: {CAPTION['style']}. Options: {', '.join(STYLES)}")
if CAPTION["anim"] not in ANIMS:
    raise SystemExit(f"Unknown animation / bilinmeyen animasyon: {CAPTION['anim']}. Options: {', '.join(ANIMS)}")
TR = 0.8  # geçiş süresi
TL = build.TL
FPS = 30
N_SCENES = len(TL["scenes"])


def probe_duration(p: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


ORDINALS = {"birinci": 1, "ilk": 1, "ikinci": 2, "üçüncü": 3, "ucuncu": 3, "dördüncü": 4, "dorduncu": 4,
            "beşinci": 5, "besinci": 5, "altıncı": 6, "altinci": 6, "yedinci": 7,
            "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7}


def scene_number(stem: str) -> int | None:
    """'sahne 1', '1.sahne', 'ikinci sahne', 'scene1', 'scene_2b', 'third scene' -> sahne numarası."""
    s = re.sub(r"scene|sah[en]{2}|shane|sahn", "sahne", stem.lower())  # 'sahen' gibi yazım hataları
    if "sahne" not in s:
        return None
    m = re.search(r"sahne\s*[._-]?\s*(\d+)", s) or re.search(r"(\d+)\s*[._-]?\s*\.?\s*sahne", s)
    if m:
        n = int(m.group(1))
        return n if 1 <= n <= N_SCENES else None
    for word, n in ORDINALS.items():
        if word in s:
            return n
    return None


def find_clips(folder: Path) -> dict[int, list[Path]]:
    found: dict[int, list[Path]] = {}
    for p in sorted(folder.iterdir()):
        if p.suffix.lower() not in {".mp4", ".mov", ".webm", ".mkv"}:
            continue
        n = scene_number(p.stem)
        if n:
            found.setdefault(n, []).append(p)
    missing = [n for n in range(1, N_SCENES + 1) if n not in found]
    if missing:
        raise SystemExit(f"Eksik sahne videoları: {missing}  (klasör: {folder})")
    return found


def plan_segments(clips: dict[int, list[Path]]) -> list[dict]:
    dur = TL["duration"]
    segs = []
    for sc in TL["scenes"]:
        n = sc["index"]
        files = clips[n]
        a, b = sc["start"], sc["end"]
        step = (b - a) / len(files)
        for k, f in enumerate(files):
            segs.append({"scene": n, "file": str(f), "first": k == 0,
                         "start": round(a + k * step, 3), "end": round(a + (k + 1) * step, 3)})
    for i, s in enumerate(segs):
        s["vstart"] = 0.0 if i == 0 else round(s["start"] - TR / 2, 3)
        s["vend"] = dur if i == len(segs) - 1 else round(s["end"] + TR / 2, 3)
    return segs


def prep_clip(i: int, s: dict) -> str:
    """Klibi 1080x1920'ye kırpar, gerekirse kare ara-değerlemeyle yavaşlatır, renk düzenler."""
    src = Path(s["file"])
    out = CLIPS / f"seg{i:02d}.mp4"
    need = s["vend"] - s["vstart"] + 0.2
    have = probe_duration(src)
    f = max(1.0, need / have)
    slow = f"setpts={f:.4f}*PTS,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if f > 1.05 else ""
    vf = (f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{slow}fps={FPS},"
          "scale=1080:1920:flags=lanczos,"
          "eq=contrast=1.07:saturation=1.12:gamma=0.97,"
          "colorbalance=rs=-0.04:gs=0.02:bs=0.03:rh=0.05:gh=0.03:bh=-0.06,"
          "unsharp=5:5:0.4,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{need:.3f}", "-vf", vf, "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "15", str(out)], check=True)
    return f"seg{i:02d} <- {src.name} ({have:.1f}s, x{f:.2f} yavaş)"


def has_audio(p: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return bool(out.strip())


def prep_audio(i: int, s: dict) -> str:
    """Klibin kendi sesini (müzik + ortam efekti) normal hızda, sahne süresine kadar
    yumuşak geçişli döngüyle uzatır. Video yavaşlasa da ses bozulmaz."""
    src = Path(s["file"])
    out = CLIPS / f"seg{i:02d}.wav"
    L = s["vend"] - s["vstart"]
    if not has_audio(src):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={build.SR}:cl=stereo",
                        "-t", f"{L:.3f}", str(out)], check=True)
        return f"seg{i:02d}: ses yok, sessizlik"
    have = probe_duration(src)
    xf = min(1.5, have / 4)
    n = max(1, math.ceil((L - xf) / (have - xf)) + 1)
    inputs, fc, last = [], [], "[0:a]"
    for k in range(n):
        inputs += ["-i", str(src)]
    for k in range(1, n):
        fc.append(f"{last}[{k}:a]acrossfade=d={xf:.2f}:c1=tri:c2=tri[x{k}]")
        last = f"[x{k}]"
    fc.append(f"{last}aresample={build.SR},aformat=channel_layouts=stereo,atrim=0:{L:.3f},"
              f"afade=t=in:d=0.4,afade=t=out:st={max(0, L - 0.6):.3f}:d=0.6[out]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
                    "-map", "[out]", "-c:a", "pcm_s16le", str(out)], check=True)
    return f"seg{i:02d}: klip sesi {have:.1f}s -> {L:.1f}s ({n} döngü)"


def mix_audio(segs: list[dict]) -> Path:
    """Seslendirme (-14 LUFS) + kliplerin kendi sesi (konuşmada kısılır) + geçişlerde hafif whoosh."""
    dur = TL["duration"]
    out = ROOT / "assets" / "audio" / "mix.wav"
    inputs = ["-i", str(VO)]
    fc = [f"[0:a]aresample={build.SR},aformat=channel_layouts=stereo,loudnorm=I=-14:TP=-1.5:LRA=11,apad=whole_dur={dur}[vo]"]
    bed = []
    for i, s in enumerate(segs):
        inputs += ["-i", str(CLIPS / f"seg{i:02d}.wav")]
        ms = int(s["vstart"] * 1000)
        fc.append(f"[{i + 1}:a]adelay={ms}|{ms},apad=whole_dur={dur}[c{i}]")
        bed.append(f"[c{i}]")
    expr = build.duck_expr(duck_db=-9.0)
    fc.append("".join(bed) + f"amix=inputs={len(bed)}:normalize=0:duration=first,atrim=0:{dur},"
              f"loudnorm=I=-21:TP=-4:LRA=14,volume='{expr}':eval=frame[bed]")
    labels = ["[vo]", "[bed]"]
    k0 = len(segs) + 1
    inputs += ["-i", str(build.AUDIO / "sfx_whoosh.wav")]
    whooshes = [sc["start"] - 0.7 for sc in TL["scenes"][1:]]
    fc.append(f"[{k0}:a]aresample={build.SR},aformat=channel_layouts=stereo,volume=-22dB,"
              f"asplit={len(whooshes)}" + "".join(f"[w{j}]" for j in range(len(whooshes))))
    for j, t in enumerate(whooshes):
        ms = int(max(0, t) * 1000)
        fc.append(f"[w{j}]adelay={ms}|{ms},apad=whole_dur={dur}[wd{j}]")
        labels.append(f"[wd{j}]")
    fc.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,"
              f"atrim=0:{dur},alimiter=limit=0.89:level=false[out]")
    script = ROOT / "artifacts" / "mix_filter.txt"
    script.write_text(";\n".join(fc), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex_script", str(script),
                    "-map", "[out]", "-c:a", "pcm_s16le", str(out)], check=True)
    return out


def use_logo() -> None:
    """Kullanıcının logosunu kompozisyona kopyalar, yüksekliği logonun oranına göre ayarlar."""
    if not LOGO:
        if not (COMP / "assets" / "logo.png").exists():
            raise SystemExit("Logo bulunamadı: klasöre adında 'logo' geçen bir png koy ya da --logo=<dosya> ver.")
        return
    dst = COMP / "assets" / "logo.png"
    shutil.copy2(LOGO, dst)
    w, h = map(int, subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                                    "stream=width,height", "-of", "csv=p=0", str(dst)],
                                   capture_output=True, text=True, check=True).stdout.strip().split(","))
    html = (COMP / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"--logo-h: \d+px;", f"--logo-h: {round(LOGO_W * h / w)}px;", html)
    (COMP / "index.html").write_text(html, encoding="utf-8")
    print(f"logo: {LOGO.name} ({w}x{h}) -> {LOGO_W}x{round(LOGO_W * h / w)}")


def use_font() -> None:
    dst = COMP / "assets" / "calibrib.ttf"
    if dst.exists():
        return
    if not FONT.exists():
        raise SystemExit(f"Font bulunamadı: {FONT}. Calibri Bold dosyasını --font=<yol> ile ver.")
    shutil.copy2(FONT, dst)


def write_composition(segs: list[dict]) -> None:
    tags = []
    for i, s in enumerate(segs):
        tags.append(f'      <video id="seg-{i}" class="clip seg" src="assets/clips/seg{i:02d}.mp4" '
                    f'data-start="{s["vstart"]:.3f}" data-duration="{s["vend"] - s["vstart"]:.3f}" '
                    f'data-track-index="{1 + i % 2}" muted playsinline></video>')
    html = (COMP / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"<!--VIDEOS-START-->.*?<!--VIDEOS-END-->",
                  "<!--VIDEOS-START-->\n" + "\n".join(tags) + "\n      <!--VIDEOS-END-->", html, flags=re.S)
    html = re.sub(r'data-duration="__DURATION__"', f'data-duration="{TL["duration"]:.3f}"', html)
    html = re.sub(r'(id="(?:bg|fx|grade|captions|logo)-clip"[^>]*data-duration=")[^"]*"',
                  lambda m: m.group(1) + f'{TL["duration"]:.3f}"', html)
    html = re.sub(r'(data-composition-id="main"[^>]*data-duration=")[^"]*"',
                  lambda m: m.group(1) + f'{TL["duration"]:.3f}"', html)
    (COMP / "index.html").write_text(html, encoding="utf-8")
    data = dict(TL, segments=segs, transition=TR, impacts=impacts(), caption=CAPTION)
    (COMP / "data.js").write_text("window.ZEB = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")


def impacts() -> list[dict]:
    """Sahne geçişlerinde sarsıntı (ses efektindeki sub-bass vuruşlarıyla aynı an)."""
    return [{"t": sc["start"] + 0.05, "power": 0.8} for sc in TL["scenes"][1:]]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("$", " ".join(cmd[:4]), "...")
    subprocess.run(cmd, check=True, cwd=cwd, shell=sys.platform == "win32" and cmd[0] == "npx")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    folder = Path(args[0]) if args else (SRC_DIR / "sahneler" if (SRC_DIR / "sahneler").is_dir() else SRC_DIR)
    render = "--no-render" not in sys.argv
    clips = find_clips(folder)
    segs = plan_segments(clips)
    for n in range(1, N_SCENES + 1):
        print(f"Sahne {n}: {[Path(p).name for p in clips[n]]}")

    CLIPS.mkdir(parents=True, exist_ok=True)
    if "--skip-prep" not in sys.argv:  # klipler hazırsa sadece kurgu + render
        for old in CLIPS.glob("seg*.*"):
            old.unlink()
        with ThreadPoolExecutor(3) as ex:
            for msg in ex.map(lambda a: prep_clip(*a), enumerate(segs)):
                print(" ", msg)
        for i, s in enumerate(segs):
            print(" ", prep_audio(i, s))
    use_logo()
    use_font()
    write_composition(segs)

    build.make_sfx()
    mix = mix_audio(segs)
    print("miks:", mix)
    if not render:
        return

    renders = ROOT / "renders"
    renders.mkdir(exist_ok=True)
    silent = renders / "video_silent.mp4"
    run(["npx", "--no-install", "hyperframes", "lint"], cwd=COMP)
    run(["npx", "--no-install", "hyperframes", "render", "--fps", str(FPS), "--quality", "delivery",
         "--output", str(silent)], cwd=COMP)
    final = renders / FINAL_NAME
    run(["ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(mix), "-map", "0:v", "-map", "1:a",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-maxrate", "16M", "-bufsize", "32M",
         "-profile:v", "high", "-level", "4.2", "-pix_fmt", "yuv420p", "-r", str(FPS), "-g", "60",
         "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-ac", "2", "-shortest", "-movflags", "+faststart", str(final)])
    for dst in (SRC_DIR / FINAL_NAME, SRC_DIR.parent / "cikti" / FINAL_NAME):
        dst.parent.mkdir(exist_ok=True)
        shutil.copy2(final, dst)
        print("kopyalandı:", dst)


if __name__ == "__main__":
    main()
