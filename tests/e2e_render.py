"""Uçtan uca gerçek üretim: gerçek Whisper, gerçek HyperFrames render ve çıktı kontrolü (verify.py).

pytest bunu toplamaz (dakikalar sürer, Whisper modeli ve Chromium ister). CI'da ayrı bir işte çalışır.

Kullanım: python tests/e2e_render.py <seslendirme.wav> [--language=en]
Seslendirme E2E_SCENES metnini okumalı (CI'da espeak-ng ile üretilir).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from conftest import TEMPLATE, make_clip, make_logo  # noqa: E402

E2E_SCENES = ["This green stone comes from deep inside the Earth.",
              "Volcanoes carry its crystals up to the surface."]


def step(name: str, cmd: list[str]) -> None:
    print(f"\n== {name}", flush=True)
    if subprocess.run(cmd).returncode:
        raise SystemExit(f"FAILED: {name}")


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    lang = next((a for a in sys.argv[1:] if a.startswith("--language=")), "--language=en")
    tmp = Path(tempfile.mkdtemp(prefix="reelsmith-e2e-"))
    src = tmp / "my-brand"
    src.mkdir()
    for i in (1, 2):
        make_clip(src / f"scene{i}.mp4", 3.0)
    shutil.copy2(args[0], src / "voiceover.wav")
    make_logo(src / "logo.png")
    (src / "script.txt").write_text("\n\n".join(E2E_SCENES), encoding="utf-8")
    proj = tmp / "proj"
    shutil.copytree(TEMPLATE, proj, ignore=shutil.ignore_patterns("__pycache__", "data.js", "assets", ".hyperframes"))
    (proj / "artifacts").mkdir()
    py, s = sys.executable, proj / "scripts"

    step("preflight", [py, str(s / "check.py"), f"--src={src}"])
    step("whisper", [py, str(s / "transcribe.py"), str(src / "voiceover.wav"),
                     str(proj / "artifacts" / "voiceover_transcript.json"), lang])
    step("align", [py, str(s / "align.py"), str(src / "script.txt")])
    step("build + render + verify", [py, str(s / "build_video.py"), f"--src={src}", "--name=e2e.mp4"])
    out = src / "e2e.mp4"
    if not out.is_file():
        raise SystemExit(f"FAILED: {out} was not written")
    print(f"\nOK: {out}")


if __name__ == "__main__":
    main()
