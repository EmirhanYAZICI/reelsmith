"""Ortak yardımcılar: timeline.json yükleme, sentez SFX (whoosh/boom/shimmer), konuşmada kısma (ducking) ifadesi."""
import json
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
AUDIO = ROOT / "assets" / "audio"
TL = json.loads((ROOT / "artifacts" / "timeline.json").read_text(encoding="utf-8"))
SR = 48000


def save_wav(path: Path, x: np.ndarray) -> None:
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def one_pole(x: np.ndarray, coef: np.ndarray) -> np.ndarray:
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += coef[i] * (x[i] - acc)
        y[i] = acc
    return y


def make_sfx() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    rnd = np.random.default_rng(7)
    # whoosh: kesim frekansı yükselip inen filtrelenmiş gürültü
    n = int(SR * 1.2)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t) ** 2
    cut = 0.01 + 0.25 * np.sin(np.pi * t) ** 3
    noise = rnd.standard_normal(n)
    lp = one_pole(noise, cut)
    hp = lp - one_pole(lp, np.full(n, 0.004))
    save_wav(AUDIO / "sfx_whoosh.wav", hp / np.abs(hp).max() * env * 0.9)

    # derin sub-bass vuruş: 70 Hz'den 32 Hz'e inen sinüs
    n = int(SR * 2.2)
    tt = np.arange(n) / SR
    f = 32 + 38 * np.exp(-tt * 5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-tt * 1.8)
    click = rnd.standard_normal(n) * np.exp(-tt * 60) * 0.25
    save_wav(AUDIO / "sfx_boom.wav", (boom + one_pole(click, np.full(n, 0.08))) * 0.95)

    # kristal tınlama (shimmer)
    n = int(SR * 2.8)
    tt = np.arange(n) / SR
    sh = np.zeros(n)
    for k, fr in enumerate([1760, 2349, 2637, 3520, 4699, 5274]):
        sh += np.sin(2 * np.pi * fr * tt + k) * np.exp(-tt * (1.6 + k * 0.35)) * (0.5 + 0.5 * np.sin(2 * np.pi * (5 + k) * tt))
    sh *= np.minimum(1, tt / 0.03)
    save_wav(AUDIO / "sfx_shimmer.wav", sh / np.abs(sh).max() * 0.8)


def speech_regions(gap: float = 0.6) -> list[tuple[float, float]]:
    regs = []
    for w in TL["words"]:
        if regs and w["start"] - regs[-1][1] < gap:
            regs[-1][1] = w["end"]
        else:
            regs.append([w["start"], w["end"]])
    return [(a, b) for a, b in regs]


def duck_expr(duck_db: float = -14.0, ramp: float = 0.3) -> str:
    """Konuşma bölgelerinde müziği duck_db kadar kısan volume ifadesi."""
    low = 10 ** (duck_db / 20)
    parts = []
    for a, b in speech_regions():
        # bölge içinde 1, kenarlarda ramp ile yumuşak geçiş
        parts.append(f"clip(min((t-{a - ramp:.3f})/{ramp},({b + ramp:.3f}-t)/{ramp}),0,1)")
    inside = "max(" + ",".join(parts[:1] + ["0"]) + ")"
    for p in parts[1:]:
        inside = f"max({inside},{p})"
    return f"1-(1-{low:.4f})*{inside}"
