"""Uçtan uca (render hariç): şablonu geçici projeye kopyalar, timeline üretir, build_video.py --no-render çalıştırır.

Klip hazırlama (kırpma + kare ara-değerleme), logo, kompozisyon ve ses miksajı gerçek ffmpeg ile çalışır.
HyperFrames kuruluysa üretilen kompozisyon lint'ten de geçirilir.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from conftest import SCENES, TEMPLATE, fake_words, needs_ffmpeg

from align import build_timeline

pytestmark = needs_ffmpeg


def probe(p: Path, entries: str) -> str:
    return subprocess.run(["ffprobe", "-v", "error", "-show_entries", entries, "-of", "csv=p=0", str(p)],
                          capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture(scope="module")
def built(tmp_path_factory) -> dict:
    import conftest
    tmp = tmp_path_factory.mktemp("pipe")
    src = tmp / "my-brand"
    src.mkdir()
    conftest.make_clip(src / "scene1.mp4", 2.0)               # sahneden kısa: yavaşlatılır
    conftest.make_clip(src / "2sahne.mp4", 4.0, audio=False)  # sesi yok: sessizlik
    conftest.make_voice(src / "voiceover.wav", 6.0)
    conftest.make_logo(src / "logo.png")
    font = tmp / "font.ttf"
    font.write_bytes(b"x")

    proj = tmp / "proj"
    shutil.copytree(TEMPLATE, proj, ignore=shutil.ignore_patterns("__pycache__"))
    (proj / "artifacts").mkdir()
    tl, _ = build_timeline(SCENES, fake_words(SCENES), duration=6.0)
    (proj / "artifacts" / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")

    out = subprocess.run([sys.executable, str(proj / "scripts" / "build_video.py"), f"--src={src}",
                          f"--font={font}", "--no-render", "--logo-mode=move,ends", "--caption-color=white",
                          "--caption-style=box"], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stdout + out.stderr
    return {"proj": proj, "comp": proj / "composition_video", "tl": tl}


def test_clips_are_vertical_1080x1920_30fps(built):
    for i in range(2):
        seg = built["comp"] / "assets" / "clips" / f"seg{i:02d}.mp4"
        assert probe(seg, "stream=width,height,r_frame_rate").split(",") == ["1080", "1920", "30/1"]


def test_short_clip_is_slowed_to_cover_its_scene(built):
    seg = built["comp"] / "assets" / "clips" / "seg00.mp4"
    data = json.loads(re.sub(r"^window\.REEL = |;\s*$", "", (built["comp"] / "data.js").read_text(encoding="utf-8")))
    s = data["segments"][0]
    assert float(probe(seg, "format=duration")) >= s["vend"] - s["vstart"]


def test_composition_data_has_options_and_duration(built):
    data = json.loads(re.sub(r"^window\.REEL = |;\s*$", "", (built["comp"] / "data.js").read_text(encoding="utf-8")))
    assert data["caption"] == {"fill": "#FFFFFF", "stroke": "#000000", "style": "box", "anim": "pop"}
    assert data["logo"]["modes"] == ["move", "ends"]
    assert len(data["segments"]) == 2
    html = (built["comp"] / "index.html").read_text(encoding="utf-8")
    assert 'data-duration="6.000"' in html and 'id="seg-1"' in html


def test_audio_mix_matches_video_length(built):
    mix = built["proj"] / "assets" / "audio" / "mix.wav"
    assert abs(float(probe(mix, "format=duration")) - built["tl"]["duration"]) < 0.1


@pytest.mark.skipif(not shutil.which("hyperframes"), reason="HyperFrames not installed")
def test_composition_passes_hyperframes_lint(built):
    out = subprocess.run([shutil.which("hyperframes"), "lint"], cwd=built["comp"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    assert out.returncode == 0 and "0 error" in out.stdout + out.stderr, out.stdout + out.stderr


def test_transitions_flash_without_shake(built):
    data = json.loads(re.sub(r"^window\.REEL = |;\s*$", "", (built["comp"] / "data.js").read_text(encoding="utf-8")))
    assert len(data["flashes"]) == 1 and "impacts" not in data
    assert "shake" not in (built["comp"] / "index.html").read_text(encoding="utf-8")


def test_single_scene_reel_builds(tmp_path):
    """Tek sahne: geçiş yok, whoosh yok (eskiden asplit=0 ile ffmpeg hata veriyordu)."""
    import conftest
    src = tmp_path / "one"
    src.mkdir()
    conftest.make_clip(src / "scene1.mp4", 3.0)
    conftest.make_voice(src / "voiceover.wav", 4.0)
    conftest.make_logo(src / "logo.png")
    font = tmp_path / "font.ttf"
    font.write_bytes(b"x")
    proj = tmp_path / "proj"
    shutil.copytree(TEMPLATE, proj, ignore=shutil.ignore_patterns("__pycache__"))
    (proj / "artifacts").mkdir()
    scenes = [SCENES[0]]
    tl, _ = build_timeline(scenes, fake_words(scenes), duration=4.0)
    (proj / "artifacts" / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
    out = subprocess.run([sys.executable, str(proj / "scripts" / "build_video.py"), f"--src={src}",
                          f"--font={font}", "--no-render"], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stdout + out.stderr
    mix = proj / "assets" / "audio" / "mix.wav"
    assert abs(float(probe(mix, "format=duration")) - 4.0) < 0.1


def test_misspelled_option_stops_build(tmp_path):
    out = subprocess.run([sys.executable, str(TEMPLATE / "scripts" / "build_video.py"), f"--src={tmp_path}",
                          "--caption-colour=white", "--no-render"], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode != 0 and "--caption-color" in out.stdout + out.stderr


def test_heavy_slowdown_warns(tmp_path):
    import conftest
    src = tmp_path / "slow"
    src.mkdir()
    conftest.make_clip(src / "scene1.mp4", 1.0)  # 1 sn klip, ~4 sn sahne: x4
    conftest.make_voice(src / "voiceover.wav", 4.0)
    conftest.make_logo(src / "logo.png")
    font = tmp_path / "font.ttf"
    font.write_bytes(b"x")
    proj = tmp_path / "proj"
    shutil.copytree(TEMPLATE, proj, ignore=shutil.ignore_patterns("__pycache__"))
    (proj / "artifacts").mkdir()
    tl, _ = build_timeline([SCENES[0]], fake_words([SCENES[0]]), duration=4.0)
    (proj / "artifacts" / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False), encoding="utf-8")
    out = subprocess.run([sys.executable, str(proj / "scripts" / "build_video.py"), f"--src={src}",
                          f"--font={font}", "--no-render"], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "UYARI / WARN" in out.stdout and "scene1.mp4" in out.stdout
