"""Whisper kelimelerini senaryo metniyle hizalar.

Çıktı: artifacts/timeline.json
  - words:  senaryodaki doğru yazımla, Whisper zamanlarıyla
  - scenes: her sahnenin başlangıç/bitiş saniyesi
  - chunks: 2-3 kelimelik altyazı blokları
"""
import json
import re
import sys
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import scene_texts  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT = ROOT / "artifacts" / "voiceover_transcript.json"
OUT = ROOT / "artifacts" / "timeline.json"

KEYWORDS: set[str] = set()  # isteğe bağlı: vurgulanacak anahtar kelimeler (küçük harf)


def norm(w: str) -> str:
    w = w.replace("’", "'").lower()
    w = unicodedata.normalize("NFKD", w)
    w = "".join(c for c in w if not unicodedata.combining(c))
    w = w.replace("ı", "i")
    return re.sub(r"[^\w]", "", w)


def build_timeline(scenes: list[str], hyp: list[dict], duration: float | None = None) -> tuple[dict, int]:
    """Sahne metinleri + Whisper kelimeleri -> (timeline, birebir eşleşen kelime sayısı).
    Yazım her zaman sahne metninden gelir; Whisper sadece zamanı verir. Whisper'ın yanlış duyduğu
    kelime aynı yerdeyse zamanını alır, eşleşmeyen kelimeler komşu kelimelerin zamanıyla doldurulur."""
    n_sc = len(scenes)
    if not n_sc:
        raise ValueError("sahne metni boş / no scene text")
    if not hyp:
        raise ValueError("Whisper hiç kelime bulmadı / transcript has no words")
    ref = []  # (word, scene_index)
    for si, text in enumerate(scenes):
        for w in text.split():
            ref.append((w, si))

    a = [norm(w) for w, _ in ref]
    b = [norm(w["word"]) for w in hyp]
    sm = SequenceMatcher(a=a, b=b, autojunk=False)

    times: list[tuple[float, float] | None] = [None] * len(ref)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1):
                h = hyp[j1 + k]
                times[i1 + k] = (h["start"], h["end"])
        elif tag == "replace" and j2 > j1:
            # Farklı sayıda kelime: Whisper aralığını orantılı böl
            s, e = hyp[j1]["start"], hyp[j2 - 1]["end"]
            n = i2 - i1
            for k in range(n):
                times[i1 + k] = (s + (e - s) * k / n, s + (e - s) * (k + 1) / n)

    # Eşleşmeyen kelimeleri komşulardan doldur
    for i, t in enumerate(times):
        if t is None:
            prev = next((times[j][1] for j in range(i - 1, -1, -1) if times[j]), 0.0)
            nxt = next((times[j][0] for j in range(i + 1, len(times)) if times[j]), prev + 0.3)
            times[i] = (prev, max(prev + 0.05, nxt))

    words = [{"text": w, "start": round(t[0], 3), "end": round(t[1], 3), "scene": si,
              "key": norm(w) in {norm(k) for k in KEYWORDS}}
             for (w, si), t in zip(ref, times)]

    # Sahne sınırları: sahnenin ilk kelimesi başladığında sahne değişir
    starts = [next(w["start"] for w in words if w["scene"] == si) for si in range(n_sc)]
    total = float(duration or words[-1]["end"] + 2.0)
    scene_list = []
    for si in range(n_sc):
        s = 0.0 if si == 0 else round(starts[si] - 0.25, 3)
        e = total if si == n_sc - 1 else round(starts[si + 1] - 0.25, 3)
        scene_list.append({"index": si + 1, "start": s, "end": round(e, 3)})

    # Altyazı blokları: 2-4 kelime, noktalama ve sahne sınırında böl
    chunks, cur = [], []
    for i, w in enumerate(words):
        cur.append(i)
        nxt = words[i + 1] if i + 1 < len(words) else None
        punct = w["text"][-1] in ".,;!?:"
        gap = nxt and nxt["start"] - w["end"] > 0.35
        scene_break = nxt and nxt["scene"] != w["scene"]
        chars = sum(len(words[j]["text"]) for j in cur)
        sentence_end = w["text"][-1] in ".!?;:"
        if len(cur) >= 3 or chars >= 17 or not nxt or scene_break or sentence_end or ((punct or gap) and len(cur) >= 2):
            chunks.append(cur)
            cur = []
    # Tek kelimelik blokları öncekiyle birleştir (aynı sahnedeyse)
    merged = []
    for c in chunks:
        if (len(c) == 1 and merged and words[merged[-1][-1]]["scene"] == words[c[0]]["scene"]
                and len(merged[-1]) < 3 and sum(len(words[j]["text"]) for j in merged[-1] + c) <= 22):
            merged[-1].extend(c)
        else:
            merged.append(c)
    chunk_list = [{"start": words[c[0]]["start"], "end": words[c[-1]]["end"], "words": c} for c in merged]

    matched = sum(op[2] - op[1] for op in sm.get_opcodes() if op[0] == "equal")
    return {"duration": total, "scenes": scene_list, "words": words, "chunks": chunk_list}, matched


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Kullanım: align.py <sahne metni.txt>")
    scenes = scene_texts(Path(sys.argv[1]).expanduser().read_text(encoding="utf-8"))
    data = json.loads(TRANSCRIPT.read_text(encoding="utf-8"))
    hyp = [w for w in data["word_timestamps"] if w.get("word", "").strip()]
    try:
        tl, matched = build_timeline(scenes, hyp, data.get("duration"))
    except ValueError as e:
        raise SystemExit(str(e)) from None
    OUT.write_text(json.dumps(tl, ensure_ascii=False, indent=1), encoding="utf-8")
    ref, scene_list, chunk_list = tl["words"], tl["scenes"], tl["chunks"]
    print(f"kelime: {len(ref)} senaryo / {len(hyp)} whisper, birebir eşleşme: {matched}")
    for s in scene_list:
        print(f"Sahne {s['index']}: {s['start']:.2f} - {s['end']:.2f}  ({s['end'] - s['start']:.1f} sn)")
    print(f"altyazı bloğu: {len(chunk_list)}")


if __name__ == "__main__":
    main()
