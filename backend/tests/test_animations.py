from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.app.animations.keyframe_generator import KeyframeGenerator
from backend.app.core.config import settings
from backend.main import app

client = TestClient(app)


# Override lifespan startup loading during tests to avoid actual Whisper download
@pytest.fixture(scope="module", autouse=True)
def mock_lifespan_model():
    with patch(
        "backend.app.services.transcription_service.WhisperModel"
    ) as mock_whisper:
        yield mock_whisper


def test_list_animations():
    response = client.get(f"{settings.API_PREFIX}/animations")
    assert response.status_code == 200
    presets = response.json()
    assert "word_highlight" in presets
    assert "word_pop" in presets
    assert "word_bounce" in presets
    assert "zoom_in" in presets


def test_keyframe_generator_easing_math():
    # Linear: t
    assert KeyframeGenerator.interpolate("linear", 0.5) == 0.5
    # Ease In: t * t
    assert KeyframeGenerator.interpolate("ease_in", 0.5) == 0.25
    # Ease Out: 1.0 - (1.0 - 0.5) * (1.0 - 0.5) = 0.75
    assert KeyframeGenerator.interpolate("ease_out", 0.5) == 0.75
    # Clamp boundaries checks
    assert KeyframeGenerator.interpolate("linear", -0.5) == 0.0
    assert KeyframeGenerator.interpolate("linear", 1.5) == 1.0


def test_apply_word_highlight():
    style = {
        "font_family": "Arial",
        "font_size": 24.0,
        "font_weight": "normal",
        "text_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "outline_color": "#000000",
        "text_effects": {
            "case": "normal",
            "word_highlight": "current",
            "auto_capitalization": True,
            "auto_emoji": False,
        },
    }

    subtitles = [
        {
            "index": 1,
            "start": 0.0,
            "end": 2.0,
            "text": "hello world",
            "words": [
                {"word": "hello", "start": 0.1, "end": 0.8},
                {"word": "world", "start": 0.9, "end": 1.7},
            ],
        }
    ],

    response = client.post(
        f"{settings.API_PREFIX}/animations/apply",
        json={
            "subtitles": subtitles[0],
            "style": style,
            "animation_preset": "word_highlight",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["animation_preset"] == "word_highlight"
    assert data["duration"] == 2.0

    animated_subs = data["animated_subtitles"]
    assert len(animated_subs) == 1

    words = animated_subs[0]["words"]
    assert len(words) == 2

    # Check word 1 highlight keyframe colors and times
    word_1 = words[0]
    assert word_1["word"] == "hello"
    assert word_1["color"] == "#FFFFFF"
    assert word_1["highlight_color"] == "#FFFF00"

    keyframes_1 = word_1["keyframes"]
    assert len(keyframes_1) == 4
    # Frame 0: before start -> text_color
    assert keyframes_1[0]["color"] == "#FFFFFF"
    assert keyframes_1[0]["time"] == 0.09  # start(0.1) - 0.01

    # Frame 1: at start -> highlight_color
    assert keyframes_1[1]["color"] == "#FFFF00"
    assert keyframes_1[1]["time"] == 0.1

    # Frame 2: at end -> highlight_color
    assert keyframes_1[2]["color"] == "#FFFF00"
    assert keyframes_1[2]["time"] == 0.8

    # Frame 3: after end -> text_color
    assert keyframes_1[3]["color"] == "#FFFFFF"
    assert keyframes_1[3]["time"] == 0.81


def test_apply_word_pop():
    style = {
        "font_family": "Arial",
        "font_size": 24.0,
        "font_weight": "normal",
        "text_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "outline_color": "#000000",
        "text_effects": {
            "case": "normal",
            "word_highlight": "current",
            "auto_capitalization": True,
            "auto_emoji": False,
        },
    }

    subtitles = [
        {
            "index": 1,
            "start": 0.0,
            "end": 2.0,
            "text": "pop",
            "words": [{"word": "pop", "start": 0.5, "end": 1.5}],
        }
    ]

    response = client.post(
        f"{settings.API_PREFIX}/animations/apply",
        json={
            "subtitles": subtitles,
            "style": style,
            "animation_preset": "word_pop",
        },
    )

    assert response.status_code == 200
    data = response.json()
    word_pop = data["animated_subtitles"][0]["words"][0]
    keyframes = word_pop["keyframes"]

    # Pop peak scale should pop to 1.35
    scales = [k["scale"] for k in keyframes]
    assert max(scales) == 1.35


def test_apply_word_bounce():
    style = {
        "font_family": "Arial",
        "font_size": 24.0,
        "font_weight": "normal",
        "text_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "outline_color": "#000000",
        "text_effects": {
            "case": "normal",
            "word_highlight": "current",
            "auto_capitalization": True,
            "auto_emoji": False,
        },
    }

    subtitles = [
        {
            "index": 1,
            "start": 0.0,
            "end": 1.0,
            "text": "bounce",
            "words": [{"word": "bounce", "start": 0.2, "end": 0.8}],
        }
    ]

    response = client.post(
        f"{settings.API_PREFIX}/animations/apply",
        json={
            "subtitles": subtitles,
            "style": style,
            "animation_preset": "word_bounce",
        },
    )

    assert response.status_code == 200
    data = response.json()
    word_bounce = data["animated_subtitles"][0]["words"][0]
    keyframes = word_bounce["keyframes"]

    # Bounce Y displacement coordinate checks (up is negative Y, e.g. -15.0)
    offsets_y = [k["position_y"] for k in keyframes]
    assert min(offsets_y) == -15.0


def test_apply_invalid_preset_fallback():
    style = {
        "font_family": "Arial",
        "font_size": 24.0,
        "font_weight": "normal",
        "text_color": "#FFFFFF",
        "highlight_color": "#FFFF00",
        "outline_color": "#000000",
        "text_effects": {
            "case": "normal",
            "word_highlight": "current",
            "auto_capitalization": True,
            "auto_emoji": False,
        },
    }

    subtitles = [
        {
            "index": 1,
            "start": 0.0,
            "end": 1.0,
            "text": "fallback",
            "words": [{"word": "fallback", "start": 0.2, "end": 0.8}],
        }
    ]

    response = client.post(
        f"{settings.API_PREFIX}/animations/apply",
        json={
            "subtitles": subtitles,
            "style": style,
            "animation_preset": "unknown_preset",  # invalid name
        },
    )

    # Returns 200 and falls back to word_highlight
    assert response.status_code == 200
    assert response.json()["animation_preset"] == "word_highlight"
