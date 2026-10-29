"""Render sonrası çıktı kontrolü: bitmiş videonun Instagram Reels hedeflerine uyduğunu doğrular.

Kullanım:
  python verify.py <video.mp4> [--duration=<beklenen sn>] [--lufs=-14] [--json]

Kontroller: 1080x1920, 30 fps, H.264 + AAC 48 kHz stereo, süre, ses yüksekliği (≈ -14 LUFS),
tepe (< -0.5 dBFS), donmuş görüntü (freezedetect), faststart (moov başta).
Her satır OK / FAIL. FAIL varsa çıkış kodu 1. Dosyayı değiştirmez.
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def opt(name: str, default: str = "") -> str:
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), default)
    return str(Path(v).expanduser()) if v.startswith("~") else v


def ffprobe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if out.returncode:
        raise SystemExit(f"FAIL  unreadable video / video okunamıyor: {path}")
    return json.loads(out.stdout)


def loudness(path: Path) -> tuple[float | None, float | None]:
    """ebur128 ile (integrated LUFS, true peak dBFS)."""
    err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-map", "0:a:0",
                          "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    summary = err[err.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+|-inf) LUFS", summary)
    p = re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summary)
    as_float = lambda m: None if not m or m.group(1) == "-inf" else float(m.group(1))  # noqa: E731
    return as_float(i), as_float(p)


def freezes(path: Path) -> int:
    err = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(path), "-map", "0:v:0",
                          "-vf", "freezedetect=n=0.003:d=1", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return err.count("freeze_start")


def faststart(path: Path) -> bool:
    """moov atomu mdat'tan önce mi (Instagram'da hızlı başlama)?"""
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    m, d = head.find(b"moov"), head.find(b"mdat")
    return m != -1 and (d == -1 or m < d)


def verify(path: Path, duration: float | None = None, target_lufs: float = -14.0) -> list[tuple[str, str]]:
    res: list[tuple[str, str]] = []
    check = lambda cond, msg: res.append(("OK" if cond else "FAIL", msg))  # noqa: E731
    info = ffprobe(path)
    v = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    a = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    dur = float(info["format"].get("duration") or 0)
    if not v:
        return [("FAIL", "no video stream / video akışı yok")]
    num, den = map(int, v.get("r_frame_rate", "0/1").split("/"))
    fps = num / den if den else 0
    check((v.get("width"), v.get("height")) == (1080, 1920), f"size {v.get('width')}x{v.get('height')} (1080x1920)")
    check(abs(fps - 30) < 0.01, f"frame rate {fps:.2f} fps (30)")
    check(v.get("codec_name") == "h264", f"video codec {v.get('codec_name')} (h264)")
    if not a:
        res.append(("FAIL", "no audio stream / ses yok"))
    else:
        check(a.get("codec_name") == "aac" and a.get("sample_rate") == "48000" and a.get("channels") == 2,
              f"audio {a.get('codec_name')} {a.get('sample_rate')} Hz {a.get('channels')} ch (aac 48000 Hz 2 ch)")
        lufs, peak = loudness(path)
        check(lufs is not None and abs(lufs - target_lufs) <= 1.5, f"loudness {lufs} LUFS ({target_lufs} ±1.5)")
        check(peak is not None and peak < -0.5, f"true peak {peak} dBFS (< -0.5)")
    if duration:
        check(abs(dur - duration) <= 0.5, f"duration {dur:.2f}s (expected {duration:.2f}s ±0.5)")
    else:
        res.append(("OK", f"duration {dur:.2f}s"))
    n = freezes(path)
    check(n == 0, f"frozen sections {n} (0)")
    check(faststart(path), "faststart (moov before mdat)")
    return res


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit("Kullanım: verify.py <video.mp4> [--duration=sn] [--lufs=-14] [--json]")
    res = verify(Path(args[0]).expanduser(), float(opt("duration")) if opt("duration") else None, float(opt("lufs", "-14")))
    if "--json" in sys.argv:
        print(json.dumps([{"level": lv, "message": m} for lv, m in res], indent=1))
    else:
        for lv, m in res:
            print(f"{lv:<5} {m}")
        n = sum(lv == "FAIL" for lv, _ in res)
        print(f"\n{'PASSED / GEÇTİ' if not n else 'FAILED / KALDI'}: {n} fail")
    sys.exit(1 if any(lv == "FAIL" for lv, _ in res) else 0)


if __name__ == "__main__":
    main()
