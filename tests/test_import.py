"""Scriptler import edilince dosya okumaz, argüman işlemez (testlerden doğrudan çağrılabilir)."""
import sys

import pytest


def test_build_modules_import_without_timeline(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["pytest"])  # --src yok, timeline.json yok
    for m in ("build", "build_video"):
        sys.modules.pop(m, None)
    import build  # noqa: F401
    import build_video
    assert build_video.TL == {} and build_video.SRC_DIR is None


def test_configure_reads_options_and_given_timeline(tmp_path):
    import build_video
    (tmp_path / "voiceover.wav").write_bytes(b"")
    (tmp_path / "logo.png").write_bytes(b"")
    tl = {"scenes": [{"index": 1, "start": 0, "end": 3}], "words": [], "duration": 3.0}
    build_video.configure([f"--src={tmp_path}", "--caption-color=white", "--name=x.mp4"], timeline=tl)
    assert build_video.N_SCENES == 1 and build_video.FINAL_NAME == "x.mp4"
    assert build_video.CAPTION["fill"] == "#FFFFFF" and build_video.VO.name == "voiceover.wav"


def test_configure_rejects_unknown_option(tmp_path):
    import build_video
    with pytest.raises(SystemExit, match="caption-color"):
        build_video.configure([f"--src={tmp_path}", "--caption-colour=white"], timeline={"scenes": []})
