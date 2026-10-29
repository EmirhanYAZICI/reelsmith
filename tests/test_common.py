from pathlib import Path

import pytest

from common import (OptionError, caption_options, group_clips, logo_options, parse_color, plan_segments,
                    scene_number, scene_texts)


def opts(**kw):
    """build_video.py'deki _opt gibi: --a-b=değer -> kw['a_b']."""
    return lambda name, default="": kw.get(name.replace("-", "_"), default)


# ---------- sahne adı tanıma ----------
@pytest.mark.parametrize("stem,n", [
    ("1sahne", 1), ("sahne 2", 2), ("1.sahne", 1), ("Sahne_3", 3), ("4sahen", 4), ("ikinci sahne", 2),
    ("scene1", 1), ("Scene 3", 3), ("scene_4b", 4), ("5scene", 5), ("third scene", 3), ("second_scene", 2),
])
def test_scene_number_recognises_names(stem, n):
    assert scene_number(stem) == n


@pytest.mark.parametrize("stem", ["logo", "music", "k", "zebercet_reels_final", "intro"])
def test_scene_number_ignores_other_files(stem):
    assert scene_number(stem) is None


def test_scene_number_respects_scene_count():
    assert scene_number("scene9", n_scenes=7) is None
    assert scene_number("scene7", n_scenes=7) == 7


def test_group_clips_reports_missing_and_groups_extras(tmp_path: Path):
    for name in ["scene1.mp4", "1sahne_b.mov", "scene3.mp4", "logo.png", "notes.txt"]:
        (tmp_path / name).write_bytes(b"")
    found, missing = group_clips(tmp_path, 3)
    assert missing == [2]
    assert sorted(p.name for p in found[1]) == ["1sahne_b.mov", "scene1.mp4"]


# ---------- sahne metni ----------
def test_scene_texts_turkish_label():
    raw = 'Sahne 1 (Metin karşılığı: "Merhaba  dünya.")\nSahne 2 (Metin karşılığı: "Bu \nikinci.")'
    assert scene_texts(raw) == ["Merhaba dünya.", "Bu ikinci."]


def test_scene_texts_english_label():
    raw = 'Scene 1\nText: "Hello world."\n\nScene 2\nText: "Second one."\n'
    assert scene_texts(raw) == ["Hello world.", "Second one."]


def test_scene_texts_paragraphs_fallback_skips_headings():
    raw = "# My reel\n\nFirst scene line one\nline two.\n\n\nSecond scene.\n"
    assert scene_texts(raw) == ["First scene line one line two.", "Second scene."]


# ---------- altyazı seçenekleri ----------
def test_parse_color_names_aliases_and_hex():
    assert parse_color("yellow") == "#F8D85A"
    assert parse_color("Sarı") == "#F8D85A"
    assert parse_color("ff00aa") == "#FF00AA"
    with pytest.raises(OptionError):
        parse_color("mauve")


def test_caption_defaults_and_old_turkish_flags():
    assert caption_options(opts()) == {"fill": "#F8D85A", "stroke": "#000000", "style": "outline", "anim": "pop"}
    c = caption_options(opts(renk="beyaz", stil="box", anim="word-hop"))
    assert (c["fill"], c["style"], c["anim"]) == ("#FFFFFF", "box", "word-hop")
    assert caption_options(opts(caption_color="blue", renk="red"))["fill"] == "#5AC8FA"  # yeni ad kazanır


@pytest.mark.parametrize("kw", [{"caption_style": "neon"}, {"caption_anim": "spin"}])
def test_caption_rejects_unknown(kw):
    with pytest.raises(OptionError):
        caption_options(opts(**kw))


# ---------- logo seçenekleri ----------
def test_logo_defaults_match_original_watermark():
    assert logo_options(opts()) == {"modes": ["move"], "pos": "bottom-left", "size": 258, "moves": 6}


def test_logo_combined_modes():
    o = logo_options(opts(logo_mode="corner,ends", logo_pos="top-right", logo_size="200"))
    assert o["modes"] == ["corner", "ends"] and o["pos"] == "top-right" and o["size"] == 200


@pytest.mark.parametrize("kw", [
    {"logo_mode": "spin"}, {"logo_mode": "move,corner"}, {"logo_pos": "center"},
    {"logo_size": "20"}, {"logo_size": "big"}, {"logo_moves": "0"},
])
def test_logo_rejects_bad_values(kw):
    with pytest.raises(OptionError):
        logo_options(opts(**kw))


# ---------- sahne planı ----------
def test_plan_segments_splits_scene_and_overlaps_transitions():
    scenes = [{"index": 1, "start": 0.0, "end": 4.0}, {"index": 2, "start": 4.0, "end": 10.0}]
    clips = {1: [Path("a.mp4")], 2: [Path("b.mp4"), Path("c.mp4")]}
    segs = plan_segments(scenes, clips, duration=10.0, tr=0.8)
    assert [(s["scene"], s["start"], s["end"], s["first"]) for s in segs] == [
        (1, 0.0, 4.0, True), (2, 4.0, 7.0, True), (2, 7.0, 10.0, False)]
    assert segs[0]["vstart"] == 0.0 and segs[-1]["vend"] == 10.0
    assert segs[1]["vstart"] == 3.6 and segs[1]["vend"] == 7.4  # tr/2 bindirme
