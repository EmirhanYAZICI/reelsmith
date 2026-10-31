"""Sahne videolarından final Reels videosunu üretir.

Kullanım:
  python build_video.py --src=<kaynak klasör> [--name=video.mp4] [--vo=ses.mp3] [--logo=logo.png]
                        [--font=<bold .ttf>] [--caption-color=yellow] [--caption-outline=#000000]
                        [--caption-style=outline] [--caption-anim=pop]
                        [--skip-prep] [--no-render] [<sahne klasörü>]

1. sahne videolarını numarasına göre bulur (1sahne, sahne 1, sahne1_a, ikinci sahne ...)
2. her klibi sahne süresine göre 1080x1920/30fps'e kırpar, kare ara-değerlemeyle yavaşlatır, renk düzenler
3. logoyu ve fontu kompozisyona kopyalar, composition_video/index.html'e video etiketlerini ve data.js'yi yazar
4. ses miksajını yapar (seslendirme + kliplerin kendi sesi, konuşmada kısılır + geçişte whoosh)
5. HyperFrames ile render alır, sesi ekleyip Instagram'a uygun kodlar, çıktıyı kopyalar
   (aynı adlı dosya varsa üzerine yazmaz, ad_2.mp4 olarak kaydeder)

Import edilince hiçbir şey yapmaz; ayarları configure(argv) okur (testler doğrudan çağırabilir).
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
from common import (MAX_SLOW, OptionError, caption_font, caption_options, check_unknown_options,  # noqa: E402
                    free_path, get_opt, group_clips, logo_options, pick_voiceover, plan_segments, slow_factor)

COMP = ROOT / "composition_video"
CLIPS = COMP / "assets" / "clips"
LOGO_W = 340  # logo-wrap taban genişliği (px); ekrandaki boyutu --logo-size belirler
TR = 0.8  # geçiş süresi
FPS = 30

# configure() doldurur
ARGV: list[str] = []
TL: dict = {}
N_SCENES = 0
SRC_DIR = VO = LOGO = FONT = None
FINAL_NAME = "reels_final.mp4"
CAPTION: dict = {}
LOGO_OPT: dict = {}
WARNINGS: list[str] = []


def _opt(name: str, default: str = "") -> str:
    return get_opt(ARGV, name, default)


def configure(argv: list[str], timeline: dict | None = None) -> None:
    """Komut satırını okur, doğrular ve modül ayarlarını doldurur. Hata varsa SystemExit."""
    global ARGV, TL, N_SCENES, SRC_DIR, VO, LOGO, FONT, FINAL_NAME, CAPTION, LOGO_OPT
    ARGV = list(argv)
    try:
        check_unknown_options(ARGV)
    except OptionError as e:
        raise SystemExit(str(e)) from None
    if not _opt("src"):
        raise SystemExit("Kaynak klasörü ver: --src=<klasör>  (seslendirme, sahne videoları, logo)")
    SRC_DIR = Path(_opt("src"))
    if not SRC_DIR.is_dir():
        raise SystemExit(f"Kaynak klasör yok / source folder not found: {SRC_DIR}")
    # Seslendirme: --vo, yoksa adı seslendirme/voice/vo olan dosya, yoksa klasördeki tek ses dosyası.
    # Birden fazla ses dosyası varsa tahmin etmez (müzik dosyası seçilmesin).
    audio = sorted(p for p in SRC_DIR.iterdir() if p.suffix.lower() in {".mp3", ".wav", ".m4a"})
    try:
        VO = pick_voiceover(audio, _opt("vo"))
    except OptionError as e:
        raise SystemExit(str(e)) from None
    FINAL_NAME = _opt("name", "reels_final.mp4")
    # Logo (firma bağımsız): --logo= verilmezse adında "logo" geçen png, yoksa klasördeki tek png;
    # bulunamazsa script durur ve logo ister
    pngs = sorted(p for p in SRC_DIR.iterdir() if p.suffix.lower() == ".png")
    LOGO = Path(_opt("logo")) if _opt("logo") else next(
        (p for p in pngs if re.search(r"logo", p.stem.lower())), pngs[0] if len(pngs) == 1 else None)
    # Altyazı fontu: --font, yoksa Windows'taki Calibri Bold, yoksa repodaki Carlito Bold (aynı ölçüler)
    FONT = caption_font(_opt("font", ""))
    # Altyazı görünümü: yer/boyut sabit, sadece renk + yazı şekli + animasyon değişir (bkz. CAPTION-STYLES.md)
    # Logo: --logo-mode=move|corner|ends, --logo-pos, --logo-size, --logo-moves (bkz. REELS-REHBERI.md)
    try:
        CAPTION = caption_options(_opt)
        LOGO_OPT = logo_options(_opt)
    except OptionError as e:
        raise SystemExit(str(e)) from None
    TL = timeline if timeline is not None else build.load_timeline()
    N_SCENES = len(TL["scenes"])
    WARNINGS.clear()


def sh(cmd: list[str], what: str) -> str:
    """Komutu çalıştırır; araç yoksa ya da hata verirse ne olduğunu anlaşılır yazıp durur."""
    try:
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              check=True).stdout
    except FileNotFoundError:
        raise SystemExit(f"{cmd[0]} bulunamadı / not found. Kur ve PATH'e ekle, sonra scripts/check.py ile kontrol et.")
    except subprocess.CalledProcessError as e:
        tail = "\n".join((e.stderr or "").strip().splitlines()[-6:])
        raise SystemExit(f"{what} başarısız / failed ({cmd[0]} çıkış kodu {e.returncode}):\n{tail}")


def probe_duration(p: Path) -> float:
    out = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
             f"süre okuma: {p.name}")
    try:
        return float(out.strip())
    except ValueError:
        raise SystemExit(f"Video okunamadı / unreadable (bozuk olabilir): {p}") from None


def find_clips(folder: Path) -> dict[int, list[Path]]:
    found, missing = group_clips(folder, N_SCENES)
    if missing:
        raise SystemExit(f"Eksik sahne videoları / missing scene clips: {missing}  (klasör: {folder})")
    return found


def plan(clips: dict[int, list[Path]]) -> list[dict]:
    return plan_segments(TL["scenes"], clips, TL["duration"], TR)


def prep_clip(i: int, s: dict) -> str:
    """Klibi 1080x1920'ye kırpar, gerekirse kare ara-değerlemeyle yavaşlatır, renk düzenler."""
    src = Path(s["file"])
    out = CLIPS / f"seg{i:02d}.mp4"
    need = s["vend"] - s["vstart"] + 0.2
    have = probe_duration(src)
    f = slow_factor(need, have)
    slow = f"setpts={f:.4f}*PTS,minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1," if f > 1.05 else ""
    vf = (f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,{slow}fps={FPS},"
          "scale=1080:1920:flags=lanczos,"
          "eq=contrast=1.07:saturation=1.12:gamma=0.97,"
          "colorbalance=rs=-0.04:gs=0.02:bs=0.03:rh=0.05:gh=0.03:bh=-0.06,"
          "unsharp=5:5:0.4,format=yuv420p")
    sh(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-t", f"{need:.3f}", "-vf", vf, "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-g", "15", str(out)], f"klip hazırlama: {src.name}")
    msg = f"seg{i:02d} <- {src.name} ({have:.1f}s, x{f:.2f} yavaş)"
    if f > MAX_SLOW:
        WARNINGS.append(f"{src.name}: {have:.1f} sn'lik klip {need:.1f} sn'ye x{f:.1f} yavaşlatıldı, görüntüde "
                        "bozulma olabilir. Daha uzun bir klip ya da o sahneye ikinci bir klip koy "
                        f"(clip slowed x{f:.1f}, may show artifacts)")
    return msg


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
        sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={build.SR}:cl=stereo",
            "-t", f"{L:.3f}", str(out)], "sessizlik üretme")
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
    sh(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(fc),
        "-map", "[out]", "-c:a", "pcm_s16le", str(out)], f"klip sesi: {src.name}")
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
    expr = build.duck_expr(TL["words"], duck_db=-9.0)
    fc.append("".join(bed) + f"amix=inputs={len(bed)}:normalize=0:duration=first,atrim=0:{dur},"
              f"loudnorm=I=-21:TP=-4:LRA=14,volume='{expr}':eval=frame[bed]")
    labels = ["[vo]", "[bed]"]
    k0 = len(segs) + 1
    whooshes = [sc["start"] - 0.7 for sc in TL["scenes"][1:]]  # tek sahnede geçiş yok, whoosh da yok
    if whooshes:
        inputs += ["-i", str(build.AUDIO / "sfx_whoosh.wav")]
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
    sh(["ffmpeg", "-v", "error", "-y", *inputs, *filter_script_args(script),
        "-map", "[out]", "-c:a", "pcm_s16le", str(out)], "ses miksajı")
    return out


def filter_script_args(script: Path) -> list[str]:
    """Filtre grafiğini dosyadan okutur (komut satırı uzunluk sınırına takılmasın diye).
    ffmpeg 7+ '-/filter_complex <dosya>' ister ve yeni sürümlerde '-filter_complex_script' kaldırıldı;
    ffmpeg 6 ve öncesi sadece '-filter_complex_script' bilir."""
    m = re.search(r"ffmpeg version n?(\d+)", sh(["ffmpeg", "-version"], "ffmpeg sürümü"))
    if m and int(m.group(1)) >= 7:
        return ["-/filter_complex", str(script)]
    return ["-filter_complex_script", str(script)]


def use_logo() -> None:
    """Kullanıcının logosunu kompozisyona kopyalar, yüksekliği logonun oranına göre ayarlar."""
    if not LOGO:
        if not (COMP / "assets" / "logo.png").exists():
            raise SystemExit("Logo bulunamadı: klasöre adında 'logo' geçen bir png koy ya da --logo=<dosya> ver.")
        return
    dst = COMP / "assets" / "logo.png"
    shutil.copy2(LOGO, dst)
    w, h = map(int, sh(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height", "-of", "csv=p=0", str(dst)], f"logo okuma: {LOGO.name}").strip().split(",")[:2])
    html = (COMP / "index.html").read_text(encoding="utf-8")
    html = re.sub(r"--logo-h: \d+px;", f"--logo-h: {round(LOGO_W * h / w)}px;", html)
    (COMP / "index.html").write_text(html, encoding="utf-8")
    print(f"logo: {LOGO.name} ({w}x{h}) -> {LOGO_W}x{round(LOGO_W * h / w)}")


def use_font() -> None:
    dst = COMP / "assets" / "calibrib.ttf"
    if dst.exists():
        return
    if not FONT.exists():
        raise SystemExit(f"Font bulunamadı: {FONT}. Kalın bir .ttf dosyasını --font=<yol> ile ver.")
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
    data = dict(TL, segments=segs, transition=TR, flashes=flashes(), caption=CAPTION, logo=LOGO_OPT)
    (COMP / "data.js").write_text("window.REEL = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")


def flashes() -> list[dict]:
    """Sahne geçişlerinde hafif ışık parlaması. Sarsıntı yok (kural: ani hareket yok)."""
    return [{"t": sc["start"] + 0.05, "power": 0.8} for sc in TL["scenes"][1:]]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("$", " ".join(cmd[:4]), "...")
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=sys.platform == "win32" and cmd[0] == "npx")
    except FileNotFoundError:
        raise SystemExit(f"{cmd[0]} bulunamadı / not found. scripts/check.py ile eksikleri gör.")
    except subprocess.CalledProcessError as e:
        raise SystemExit(f"{' '.join(cmd[:4])} başarısız / failed (çıkış kodu {e.returncode}). Yukarıdaki çıktıya bak. "
                         "Klipler hazırsa --skip-prep ile kaldığın yerden devam edebilirsin.")


def show_warnings() -> None:
    for w in WARNINGS:
        print("UYARI / WARN:", w)


def main(argv: list[str] | None = None) -> None:
    configure(sys.argv[1:] if argv is None else argv)
    args = [a for a in ARGV if not a.startswith("--")]
    folder = Path(args[0]) if args else (SRC_DIR / "sahneler" if (SRC_DIR / "sahneler").is_dir() else SRC_DIR)
    render = "--no-render" not in ARGV
    clips = find_clips(folder)
    segs = plan(clips)
    for n in range(1, N_SCENES + 1):
        print(f"Sahne {n}: {[Path(p).name for p in clips[n]]}")

    CLIPS.mkdir(parents=True, exist_ok=True)
    if "--skip-prep" not in ARGV:  # klipler hazırsa sadece kurgu + render
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
    show_warnings()
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
        free = free_path(dst)  # kullanıcının dosyasının üzerine asla yazma
        shutil.copy2(final, free)
        print("kopyalandı:", free, "" if free == dst else f"({dst.name} zaten vardı, üzerine yazılmadı)")
    show_warnings()
    print("\nçıktı kontrolü / output check:")  # FAIL olsa da video kopyalanmış olur; sonucu kullanıcıya söyle
    sys.exit(subprocess.run([sys.executable, str(Path(__file__).parent / "verify.py"), str(final),
                             f"--duration={TL['duration']:.3f}"]).returncode)


if __name__ == "__main__":
    main()
