"""Render sonrası çıktı kontrolü (verify.py): doğru videoyu geçirir, hatalı olanları yakalar."""
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SCRIPTS, ffmpeg, needs_ffmpeg

pytestmark = needs_ffmpeg

# -14 LUFS'a ayarlanmış pembe gürültü (iki geçişli loudnorm yerine sabit kazanç, ölçüm kararlı olsun diye)
AUDIO = "anoisesrc=color=pink:amplitude=0.1:seed=7:duration={d},loudnorm=I=-14:TP=-2:LRA=7,aresample=48000"


def make_reel(path: Path, seconds: float = 4.0, size: str = "1080x1920", rate: int = 30, still: bool = False,
              audio: bool = True, faststart: bool = True) -> Path:
    src = f"color=c=gray:s={size}:r={rate}:d={seconds}" if still else f"testsrc2=size={size}:rate={rate}:duration={seconds}"
    args = ["-f", "lavfi", "-i", src]
    if audio:
        args += ["-f", "lavfi", "-i", AUDIO.format(d=seconds)]
    args += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", str(rate)]
    if audio:
        args += ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest"]
    if faststart:
        args += ["-movflags", "+faststart"]
    ffmpeg(*args, str(path))
    return path


def run_verify(path: Path, *extra: str) -> tuple[int, str]:
    out = subprocess.run([sys.executable, str(SCRIPTS / "verify.py"), str(path), *extra],
                         capture_output=True, text=True, encoding="utf-8")
    return out.returncode, out.stdout


def test_correct_reel_passes(tmp_path):
    code, out = run_verify(make_reel(tmp_path / "ok.mp4"), "--duration=4")
    assert code == 0, out
    assert "PASSED" in out


@pytest.mark.parametrize("kw,expect", [
    ({"size": "720x1280"}, "size 720x1280"),
    ({"rate": 25}, "frame rate 25.00"),
    ({"still": True}, "frozen sections"),
    ({"audio": False}, "no audio stream"),
    ({"faststart": False}, "faststart"),
])
def test_bad_reel_fails_with_reason(tmp_path, kw, expect):
    code, out = run_verify(make_reel(tmp_path / "bad.mp4", **kw))
    assert code == 1
    assert any(line.startswith("FAIL") and expect in line for line in out.splitlines()), out


def test_wrong_duration_fails(tmp_path):
    code, out = run_verify(make_reel(tmp_path / "short.mp4"), "--duration=10")
    assert code == 1 and "FAIL  duration" in out


def test_unreadable_file_fails(tmp_path):
    bad = tmp_path / "broken.mp4"
    bad.write_bytes(b"not a video")
    code, out = run_verify(bad)
    assert code == 1
