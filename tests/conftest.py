"""Ortak test yardımcıları: şablon scriptlerini import yolu, ffmpeg ile küçük örnek medya üretimi."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "skills" / "reelsmith-media" / "template"
SCRIPTS = TEMPLATE / "scripts"
sys.path.insert(0, str(SCRIPTS))

HAS_FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
needs_ffmpeg = pytest.mark.skipif(not HAS_FFMPEG, reason="ffmpeg/ffprobe not on PATH")

SCENES = ["Merhaba dünya, bu bir deneme.", "İkinci sahne burada bitiyor."]


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def make_clip(path: Path, seconds: float, size: str = "720x1280", audio: bool = True) -> Path:
    inputs = ["-f", "lavfi", "-i", f"testsrc2=size={size}:rate=30:duration={seconds}"]
    if audio:
        inputs += ["-f", "lavfi", "-i", f"sine=frequency=330:duration={seconds}"]
    ffmpeg(*inputs, "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "ultrafast", *(["-shortest"] if audio else []),
           str(path))
    return path


def make_voice(path: Path, seconds: float) -> Path:
    ffmpeg("-f", "lavfi", "-i", f"sine=frequency=220:duration={seconds}", "-ar", "48000", str(path))
    return path


def make_logo(path: Path) -> Path:
    ffmpeg("-f", "lavfi", "-i", "color=c=white@0.0:s=400x120,format=rgba", "-frames:v", "1", str(path))
    return path


def fake_words(scenes: list[str], gap: float = 0.4, start: float = 0.3) -> list[dict]:
    """Sahne metninden Whisper benzeri kelime zamanları üretir (her kelime 0.3 sn)."""
    out, t = [], start
    for text in scenes:
        for w in text.split():
            out.append({"word": " " + w, "start": round(t, 3), "end": round(t + 0.3, 3)})
            t += 0.35
        t += gap
    return out


@pytest.fixture
def source_folder(tmp_path: Path) -> Path:
    """Ön kontrolden geçecek eksiksiz bir kaynak klasör: 2 sahne, seslendirme, logo, sahne metni."""
    src = tmp_path / "my-brand"
    src.mkdir()
    make_clip(src / "scene1.mp4", 1.5)
    make_clip(src / "2sahne.mp4", 1.5, audio=False)
    make_voice(src / "voiceover.wav", 6.0)
    make_logo(src / "logo.png")
    (src / "script.txt").write_text("\n\n".join(SCENES), encoding="utf-8")
    (tmp_path / "font.ttf").write_bytes(b"not a real font, only copied")
    return src
