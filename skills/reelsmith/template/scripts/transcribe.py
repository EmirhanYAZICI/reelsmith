"""faster-whisper ile kelime zamanlı döküm (PyAV yerine ffmpeg ile ses çözülür)."""
import json, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

src, out = sys.argv[1], sys.argv[2]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
model = WhisperModel("small", device="cpu", compute_type="int8")
segs, info = model.transcribe(audio, language="tr", word_timestamps=True, beam_size=5,
                              initial_prompt=sys.argv[3] if len(sys.argv) > 3 else None)  # özel isimler ipucu (isteğe bağlı)
words, text = [], []
for s in segs:
    text.append(s.text)
    for w in s.words:
        words.append({"word": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "probability": round(w.probability, 3)})
json.dump({"text": " ".join(text), "word_timestamps": words, "language": "tr", "duration": round(len(audio) / 16000, 3),
           "model_size": "small"}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("kelime:", len(words), "süre:", round(len(audio) / 16000, 2))
