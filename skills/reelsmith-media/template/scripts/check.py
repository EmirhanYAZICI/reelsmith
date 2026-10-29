"""Ön kontrol: render'a başlamadan önce araçları ve kaynak klasörü kontrol eder.

Kullanım:
  python check.py --src=<kaynak klasör> [--script=metin.txt] [--vo=ses.mp3] [--logo=logo.png]
                  [--font=<bold .ttf>] [--tools-only | --skip-tools] [--json]
                  [--caption-*=...] [--logo-mode=...] (seçenekleri de doğrular)

Her satır OK / WARN / FAIL. FAIL varsa çıkış kodu 1 olur; WARN render'ı durdurmaz.
Hiçbir dosyayı değiştirmez.
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import (AUDIO_EXT, OptionError, caption_font, caption_options, group_clips, logo_options,  # noqa: E402
                    scene_number, scene_texts)

GUIDE_NAMES = re.compile(r"rehber|guide|readme|agents|claude", re.I)
results: list[tuple[str, str]] = []


def opt(name: str, default: str = "") -> str:
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), default)
    return str(Path(v).expanduser()) if v.startswith("~") else v


def ok(msg: str) -> None:
    results.append(("OK", msg))


def warn(msg: str) -> None:
    results.append(("WARN", msg))


def fail(msg: str) -> None:
    results.append(("FAIL", msg))


def probe(p: Path) -> dict | None:
    """ffprobe ile akışları okur; okunamazsa None."""
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                              "stream=codec_type,width,height,pix_fmt:format=duration", "-of", "json", str(p)],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if out.returncode:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def version(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                             shell=sys.platform == "win32" and cmd[0] in ("npx", "npm"))
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return (out.stdout or out.stderr).strip().splitlines()[0] if out.returncode == 0 and (out.stdout or out.stderr) else None


def check_tools() -> None:
    v = sys.version_info
    if (3, 10) <= v[:2] <= (3, 12):
        ok(f"Python {v.major}.{v.minor}")
    else:
        fail(f"Python {v.major}.{v.minor}: faster-whisper needs 3.10-3.12 / 3.10-3.12 gerekli (winget install Python.Python.3.12)")
    for mod in ("numpy", "faster_whisper"):
        if importlib.util.find_spec(mod):
            ok(f"python package {mod}")
        else:
            fail(f"python package {mod} missing / eksik: pip install -r requirements.txt")
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool):
            ok(tool)
        else:
            fail(f"{tool} not on PATH / PATH'te yok (Windows: winget install Gyan.FFmpeg)")
    if not shutil.which("node"):
        fail("Node.js not found / bulunamadı (Windows: winget install OpenJS.NodeJS.LTS)")
        return
    hf_bin = shutil.which("hyperframes")  # Windows: hyperframes.cmd, tam yolla çalışır
    hf = version([hf_bin, "--version"]) if hf_bin else None
    if hf is None:
        fail("HyperFrames not installed / kurulu değil: npm i -g hyperframes@0.8")
    elif not re.search(r"\b0\.8\.", hf):
        warn(f"HyperFrames {hf}: tested with 0.8.x / 0.8.x ile test edildi")
    else:
        ok(f"HyperFrames {hf}")


def check_options() -> None:
    try:
        caption_options(opt)
        logo_options(opt)
        ok("caption and logo options / altyazı ve logo seçenekleri")
    except OptionError as e:
        fail(str(e))


def check_folder(src: Path) -> None:
    if not src.is_dir():
        fail(f"source folder not found / kaynak klasör yok: {src}")
        return
    files = [p for p in src.iterdir() if p.is_file()]

    # sahne metni
    if opt("script"):
        script = Path(opt("script"))
    else:
        texts = [p for p in files if p.suffix.lower() in (".txt", ".md") and not GUIDE_NAMES.search(p.stem)]
        script = texts[0] if len(texts) == 1 else None
        if len(texts) > 1:
            fail(f"several text files, pass --script= / birden fazla metin dosyası: {[p.name for p in texts]}")
            return
    if not script or not script.is_file():
        fail("scene script (.txt/.md) not found / sahne metni bulunamadı")
        return
    scenes = scene_texts(script.read_text(encoding="utf-8", errors="replace"))
    if not scenes:
        fail(f"no scene text in {script.name} / sahne metni boş")
        return
    ok(f"script {script.name}: {len(scenes)} scenes, {sum(len(s.split()) for s in scenes)} words")
    short = [i + 1 for i, s in enumerate(scenes) if len(s.split()) < 3]
    if short:
        warn(f"very short scene text / çok kısa sahne metni: {short}")

    # sahne videoları
    clips, missing = group_clips(src, len(scenes))
    if missing:
        fail(f"missing scene clips / eksik sahne videoları: {missing} (name them scene1.mp4 or 1sahne.mp4)")
    extra = sorted({p.name for p in files if p.suffix.lower() in {".mp4", ".mov", ".webm", ".mkv"}
                    and scene_number(p.stem) and not scene_number(p.stem, len(scenes))})
    if extra:
        warn(f"clips beyond the scene count are ignored / fazla klipler kullanılmaz: {extra}")
    for n, paths in sorted(clips.items()):
        for p in paths:
            info = probe(p)
            video = next((s for s in (info or {}).get("streams", []) if s.get("codec_type") == "video"), None)
            if not video:
                fail(f"scene {n}: {p.name} is unreadable or has no video / okunamıyor, bozuk olabilir")
                continue
            dur = float((info.get("format") or {}).get("duration") or 0)
            w, h = int(video.get("width") or 0), int(video.get("height") or 0)
            if dur < 0.5:
                fail(f"scene {n}: {p.name} is too short ({dur:.2f}s)")
            elif w > h:
                warn(f"scene {n}: {p.name} is landscape {w}x{h}; it will be cropped to 9:16 / yatay, kırpılacak")
            else:
                ok(f"scene {n}: {p.name} {w}x{h} {dur:.1f}s")

    # seslendirme
    audio = sorted(p for p in files if p.suffix.lower() in AUDIO_EXT)
    vo = Path(opt("vo")) if opt("vo") else next(
        (p for p in audio if re.search(r"seslendirme|voice|\bvo\b", p.stem.lower())), audio[0] if audio else None)
    if not vo or not vo.is_file():
        fail("voiceover (.mp3/.wav/.m4a) not found / seslendirme bulunamadı")
    else:
        info = probe(vo)
        has_audio = any(s.get("codec_type") == "audio" for s in (info or {}).get("streams", []))
        dur = float(((info or {}).get("format") or {}).get("duration") or 0)
        if not has_audio or dur < 1:
            fail(f"voiceover {vo.name} is unreadable or empty / okunamıyor ya da boş")
        else:
            ok(f"voiceover {vo.name} {dur:.1f}s")
            if len(audio) > 1 and not opt("vo"):
                warn(f"several audio files, using {vo.name}; pass --vo= to choose / birden fazla ses dosyası")

    # logo
    pngs = sorted(p for p in files if p.suffix.lower() == ".png")
    logo = Path(opt("logo")) if opt("logo") else next(
        (p for p in pngs if "logo" in p.stem.lower()), pngs[0] if len(pngs) == 1 else None)
    if not logo or not logo.is_file():
        fail("logo not found: add a png with 'logo' in its name or pass --logo= / logo bulunamadı")
    else:
        info = probe(logo)
        st = next((s for s in (info or {}).get("streams", []) if s.get("codec_type") == "video"), None)
        if not st:
            fail(f"logo {logo.name} is unreadable / okunamıyor")
        else:
            ok(f"logo {logo.name} {st.get('width')}x{st.get('height')}")
            if "a" not in str(st.get("pix_fmt", "")):
                warn(f"logo {logo.name} has no transparency; it will show as a box / şeffaf değil")

    # font
    font = caption_font(opt("font"))
    if font.is_file():
        ok(f"font {font.name}")
    else:
        fail(f"caption font not found: {font}. Pass --font=<bold .ttf> / altyazı fontu bulunamadı")


def main() -> None:
    if "--skip-tools" not in sys.argv:
        check_tools()
    check_options()
    if not opt("src") and "--tools-only" not in sys.argv:
        fail("pass --src=<folder> / kaynak klasörü ver (ya da --tools-only)")
    elif "--tools-only" not in sys.argv:
        check_folder(Path(opt("src")))
    if "--json" in sys.argv:
        print(json.dumps([{"level": lv, "message": m} for lv, m in results], ensure_ascii=False, indent=1))
    else:
        for lv, m in results:
            print(f"{lv:<5} {m}")
        n_fail = sum(lv == "FAIL" for lv, _ in results)
        n_warn = sum(lv == "WARN" for lv, _ in results)
        print(f"\n{'READY / HAZIR' if not n_fail else 'NOT READY / HAZIR DEĞİL'}: {n_fail} fail, {n_warn} warn")
    sys.exit(1 if any(lv == "FAIL" for lv, _ in results) else 0)


if __name__ == "__main__":
    main()
