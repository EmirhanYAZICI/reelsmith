---
name: whisper-tr
description: Yerel ve ücretsiz Whisper (faster-whisper) ile Türkçe konuşmayı yazıya döker, kelime kelime zaman çıkarır (altyazı, sahne zamanlaması). API anahtarı istemez. Kullan - "whisper", "transkript", "konuşmayı yazıya dök", "altyazı zamanla", "kelime zamanları" denince ya da reels-edit skill'i seslendirmeyi zamanlarken.
argument-hint: "<ses ya da video dosyası> [özel isimler]"
---

# Whisper (Türkçe, yerel)

Ücretli `speech-to-text` (ElevenLabs) yerine bunu kullan. İnternet ve anahtar gerekmez. Model ilk seferde indirilir, sonra diskten gelir.

## Ortam
- OpenMontage Python ortamı: `OM="${OPENMONTAGE_DIR:-$HOME/Projects/OpenMontage}"`, Python `$OM/.venv/Scripts/python.exe` (Windows) / `$OM/.venv/bin/python`.
- Paket: `faster-whisper` (`$OM/.venv` içinde kurulu olmalı). Yoksa: `"$PY" -m pip install faster-whisper numpy`.
- `ffmpeg` PATH'te olmalı.
- Ortam değişkenleri: `PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_XET=1`. Bu ikincisi model indirmesinin takılmasını önler.

## Çalıştır
Script `reels-edit` skill'i ile birlikte gelir: `~/.claude/skills/reels-edit/template/scripts/transcribe.py`.

```bash
OM="${OPENMONTAGE_DIR:-$HOME/Projects/OpenMontage}"; PY="$OM/.venv/Scripts/python.exe"
export PYTHONIOENCODING=utf-8 HF_HUB_DISABLE_XET=1
"$PY" ~/.claude/skills/reels-edit/template/scripts/transcribe.py "<ses.mp3>" "<cikti.json>" "Özel isim 1, Özel isim 2"
```

- Üçüncü argüman isteğe bağlı. Konudaki özel isimleri (marka, taş adı, kişi) yazarsan Whisper onları doğru duyar.
- Model `small`, `language="tr"`, `word_timestamps=True`, CPU int8. 2-3 dakikalık ses birkaç dakikada biter.
- Video da verilebilir. ffmpeg sesi kendisi ayırır.

## Çıktı (`cikti.json`)
```json
{"text": "...", "word_timestamps": [{"word": "Dünyanın", "start": 0.12, "end": 0.58, "probability": 0.97}],
 "language": "tr", "duration": 142.5, "model_size": "small"}
```

## Notlar
- OpenMontage'ın kendi `transcriber` aracı bu sistemde PyAV hatası veriyor (`metadata_errors`). Bu script sesi ffmpeg ile çözdüğü için o hatayı aşar.
- Yazım hatası olabilir. Doğru yazım için metni senaryoyla hizala: `reels-edit/template/scripts/align.py`.
- Daha doğru sonuç gerekirse script içinde `"small"` yerine `"medium"` ya da `"large-v3"` yaz. Daha yavaştır.
