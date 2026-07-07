import os
import shutil
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

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


@pytest.fixture(scope="module", autouse=True)
def clean_custom_styles():
    custom_dir = os.path.join(settings.STYLES_DIR, "custom")
    os.makedirs(custom_dir, exist_ok=True)
    yield
    # Clean up custom folder
    if os.path.exists(custom_dir):
        shutil.rmtree(custom_dir, ignore_errors=True)


def test_list_styles():
    response = client.get(f"{settings.API_PREFIX}/styles")
    assert response.status_code == 200
    styles = response.json()
    assert "default" in styles
    assert "tiktok" in styles
    assert "instagram" in styles
    assert "mrbeast" in styles


def test_apply_style_success():
    payload = {
        "style_name": "tiktok",
        "width": 1080,
        "height": 1920,
        "aspect_ratio": "vertical",
        "subtitles": [
            {
                "index": 1,
                "start": 0.0,
                "end": 2.0,
                "text": "this is a cool fire game",
                "words": [
                    {"word": "this", "start": 0.0, "end": 0.3},
                    {"word": "is", "start": 0.3, "end": 0.6},
                    {"word": "a", "start": 0.6, "end": 0.8},
                    {"word": "cool", "start": 0.8, "end": 1.2},
                    {"word": "fire", "start": 1.2, "end": 1.6},
                    {"word": "game", "start": 1.6, "end": 2.0},
                ],
            }
        ],
    }

    response = client.post(f"{settings.API_PREFIX}/styles/apply", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["style_name"] == "tiktok"
    assert data["width"] == 1080
    assert data["aspect_ratio"] == "vertical"

    # Verify properties
    properties = data["style_properties"]
    assert properties["font_family"] == "Montserrat"
    assert properties["font_weight"] == "bold"

    # Verify styled subtitles text effects
    styled_subs = data["styled_subtitles"]
    assert len(styled_subs) == 1

    text = styled_subs[0]["text"]
    # TikTok style has case: uppercase and auto_emoji: True
    # "cool" -> "COOL 😎", "fire" -> "FIRE 🔥", "game" -> "GAME 🎮"
    assert "COOL 😎" in text
    assert "FIRE 🔥" in text
    assert "GAME 🎮" in text

    # Assert word lists got formatted too
    words = styled_subs[0]["words"]
    assert words[3]["word"] == "COOL 😎"
    assert words[4]["word"] == "FIRE 🔥"
    assert words[5]["word"] == "GAME 🎮"


def test_apply_style_responsive_scaling():
    # Test font sizes scale proportionally between 1080p (factor 1.0) and 4K (factor 2.0)
    subtitles = [
        {
            "index": 1,
            "start": 0.0,
            "end": 1.0,
            "text": "test",
            "words": [{"word": "test", "start": 0.0, "end": 1.0}],
        }
    ]

    # 1. Base run at 1080p vertical
    response_1080 = client.post(
        f"{settings.API_PREFIX}/styles/apply",
        json={
            "style_name": "tiktok",
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "vertical",
            "subtitles": subtitles,
        },
    )
    assert response_1080.status_code == 200
    font_size_1080 = response_1080.json()["style_properties"]["font_size"]

    # 2. 4K vertical run (width 2160)
    response_2160 = client.post(
        f"{settings.API_PREFIX}/styles/apply",
        json={
            "style_name": "tiktok",
            "width": 2160,
            "height": 3840,
            "aspect_ratio": "vertical",
            "subtitles": subtitles,
        },
    )
    assert response_2160.status_code == 200
    font_size_2160 = response_2160.json()["style_properties"]["font_size"]

    # Font size at 2160 should be exactly 2x that of 1080
    assert font_size_2160 == font_size_1080 * 2.0


def test_create_custom_style_and_apply():
    custom_style_properties = {
        "font_family": "Courier New",
        "font_size": 20.0,
        "font_weight": "normal",
        "text_color": "#FF5500",
        "highlight_color": "#00FF55",
        "outline_color": "#000000",
        "outline_width": 1.0,
        "shadow_color": "#000000",
        "shadow_offset_x": 0.0,
        "shadow_offset_y": 0.0,
        "background_box": True,
        "background_color": "#111111",
        "background_opacity": 0.9,
        "border_radius": 2.0,
        "padding": 5.0,
        "line_spacing": 1.5,
        "letter_spacing": 0.0,
        "safe_margin": 10.0,
        "vertical_position": "top",
        "horizontal_position": "left",
        "max_width_pct": 90.0,
        "alignment": "left",
        "opacity": 0.8,
        "text_effects": {
            "case": "lowercase",
            "word_highlight": "none",
            "auto_capitalization": False,
            "auto_emoji": False,
        },
    }

    # Save custom style
    response = client.post(
        f"{settings.API_PREFIX}/styles/custom",
        json={
            "style_name": "fancy_custom",
            "style_properties": custom_style_properties,
        },
    )
    assert response.status_code == 201
    assert "fancy_custom" in response.json()["message"]

    # Assert custom style exists in styles list
    list_response = client.get(f"{settings.API_PREFIX}/styles")
    assert "fancy_custom" in list_response.json()

    # Apply custom style
    apply_response = client.post(
        f"{settings.API_PREFIX}/styles/apply",
        json={
            "style_name": "fancy_custom",
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "vertical",
            "subtitles": [
                {
                    "index": 1,
                    "start": 0.0,
                    "end": 1.0,
                    "text": "Hello World",
                    "words": [
                        {"word": "Hello", "start": 0.0, "end": 0.5},
                        {"word": "World", "start": 0.5, "end": 1.0},
                    ],
                }
            ],
        },
    )
    assert apply_response.status_code == 200
    data = apply_response.json()
    assert data["style_properties"]["font_family"] == "Courier New"
    assert data["styled_subtitles"][0]["text"] == "hello world"


def test_apply_style_not_found():
    response = client.post(
        f"{settings.API_PREFIX}/styles/apply",
        json={
            "style_name": "non_existent_style",
            "width": 1080,
            "height": 1920,
            "aspect_ratio": "vertical",
            "subtitles": [],
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_custom_style_validation_errors():
    # Try to save with invalid color code structure
    response = client.post(
        f"{settings.API_PREFIX}/styles/custom",
        json={
            "style_name": "bad_color",
            "style_properties": {
                "font_family": "Arial",
                "font_size": 20.0,
                "font_weight": "normal",
                "text_color": "not-a-hex-color",  # invalid format
                "highlight_color": "#00FF00",
                "outline_color": "#000000",
                "text_effects": {
                    "case": "normal",
                    "word_highlight": "none",
                    "auto_capitalization": True,
                    "auto_emoji": False,
                },
            },
        },
    )
    assert response.status_code == 422
