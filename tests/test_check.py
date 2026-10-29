"""Ön kontrol (check.py) gerçek, küçük medya dosyalarıyla."""
import os
import subprocess
import sys
from pathlib import Path

from conftest import SCRIPTS, make_clip, needs_ffmpeg

pytestmark = needs_ffmpeg


def run_check(src: Path, *extra: str) -> tuple[int, str]:
    font = src.parent / "font.ttf"
    out = subprocess.run([sys.executable, str(SCRIPTS / "check.py"), f"--src={src}", f"--font={font}",
                          "--skip-tools", *extra], capture_output=True, text=True, encoding="utf-8")
    return out.returncode, out.stdout


def test_complete_folder_is_ready(source_folder):
    code, out = run_check(source_folder)
    assert code == 0, out
    assert "READY" in out and "2 scenes" in out


def test_missing_scene_clip_fails(source_folder):
    (source_folder / "2sahne.mp4").unlink()
    code, out = run_check(source_folder)
    assert code == 1
    assert "missing scene clips" in out and "[2]" in out


def test_corrupt_clip_fails(source_folder):
    (source_folder / "2sahne.mp4").write_bytes(b"this is not a video")
    code, out = run_check(source_folder)
    assert code == 1
    assert "2sahne.mp4 is unreadable" in out


def test_missing_logo_fails(source_folder):
    (source_folder / "logo.png").unlink()
    code, out = run_check(source_folder)
    assert code == 1 and "logo not found" in out


def test_landscape_clip_only_warns(source_folder):
    make_clip(source_folder / "scene1.mp4", 1.5, size="1280x720")
    code, out = run_check(source_folder)
    assert code == 0
    assert "WARN" in out and "landscape" in out


def test_bad_option_fails(source_folder):
    code, out = run_check(source_folder, "--logo-mode=spin")
    assert code == 1 and "--logo-mode" in out


def test_missing_folder_fails(tmp_path):
    (tmp_path / "font.ttf").write_bytes(b"x")
    code, out = run_check(tmp_path / "nope")
    assert code == 1 and "source folder not found" in out


def test_tilde_in_src_is_expanded(source_folder):
    home = source_folder.parent
    env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)}
    out = subprocess.run([sys.executable, str(SCRIPTS / "check.py"), f"--src=~/{source_folder.name}",
                          f"--font={home / 'font.ttf'}", "--skip-tools"],
                         capture_output=True, text=True, encoding="utf-8", env=env)
    assert out.returncode == 0, out.stdout + out.stderr
