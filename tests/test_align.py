import pytest
from conftest import SCENES, fake_words

from align import build_timeline, norm


def test_norm_ignores_case_accents_and_punctuation():
    assert norm("Dünya,") == norm("dunya") == "dunya"
    assert norm("İkinci") == norm("ikinci")
    assert norm("hikâyesi") == norm("hikayesi")


def test_exact_transcript_keeps_script_spelling_and_times():
    hyp = fake_words(SCENES)
    tl, matched = build_timeline(SCENES, hyp, duration=6.0)
    assert matched == len(hyp)
    assert [w["text"] for w in tl["words"]] == " ".join(SCENES).split()
    assert [(w["start"], w["end"]) for w in tl["words"]] == [(h["start"], h["end"]) for h in hyp]


def test_scene_boundaries_follow_first_spoken_word():
    hyp = fake_words(SCENES)
    tl, _ = build_timeline(SCENES, hyp, duration=6.0)
    second_start = hyp[len(SCENES[0].split())]["start"]
    assert tl["scenes"][0] == {"index": 1, "start": 0.0, "end": round(second_start - 0.25, 3)}
    assert tl["scenes"][1]["start"] == round(second_start - 0.25, 3)
    assert tl["scenes"][1]["end"] == 6.0


def test_misheard_word_takes_whisper_time_but_script_spelling():
    hyp = fake_words(SCENES)
    hyp[0]["word"] = " Merhabaa"  # Whisper yanlış duydu
    tl, matched = build_timeline(SCENES, hyp, duration=6.0)
    assert tl["words"][0]["text"] == "Merhaba"
    assert (tl["words"][0]["start"], tl["words"][0]["end"]) == (hyp[0]["start"], hyp[0]["end"])
    assert matched == len(hyp) - 1


def test_missing_words_are_filled_in_order():
    hyp = fake_words(SCENES)
    del hyp[2:4]  # Whisper iki kelimeyi hiç duymadı
    tl, _ = build_timeline(SCENES, hyp, duration=6.0)
    starts = [w["start"] for w in tl["words"]]
    assert len(tl["words"]) == len(" ".join(SCENES).split())
    assert starts == sorted(starts)
    assert all(w["end"] >= w["start"] for w in tl["words"])


def test_chunks_cover_every_word_once_and_stay_short():
    tl, _ = build_timeline(SCENES, fake_words(SCENES), duration=6.0)
    covered = [i for c in tl["chunks"] for i in c["words"]]
    assert covered == list(range(len(tl["words"])))
    assert all(1 <= len(c["words"]) <= 3 for c in tl["chunks"])
    for c in tl["chunks"]:  # bir altyazı bloğu iki sahneye taşmaz
        assert len({tl["words"][i]["scene"] for i in c["words"]}) == 1


@pytest.mark.parametrize("scenes,hyp", [([], [{"word": "a", "start": 0, "end": 1}]), (SCENES, [])])
def test_empty_input_raises_clear_error(scenes, hyp):
    with pytest.raises(ValueError):
        build_timeline(scenes, hyp)
