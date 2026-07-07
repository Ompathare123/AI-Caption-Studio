from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.rendering.font_manager import FontManager
from backend.app.rendering.timeline_player import TimelinePlayer
from backend.main import app

client = TestClient(app)


# Override lifespan startup loading during tests to avoid actual Whisper download
@pytest.fixture(scope="module", autouse=True)
def mock_lifespan_model():
    with patch(
        "backend.app.services.transcription_service.WhisperModel"
    ) as mock_whisper:
        yield mock_whisper


def test_font_manager_resolving():
    # Resolves Arial or default
    font_file = FontManager.get_font_file("Arial")
    assert isinstance(font_file, str)

    font = FontManager.load_truetype_font("Arial", 24)
    assert font is not None


def test_timeline_player_interpolation():
    # Values
    assert TimelinePlayer.interpolate_value(10.0, 20.0, 0.5) == 15.0
    # Colors
    assert (
        TimelinePlayer.interpolate_color("#000000", "#FFFFFF", 0.5) == "#7F7F7F"
    )

    # Word keyframe timelines state interpolation checks
    word_info = {
        "word": "test",
        "start": 1.0,
        "end": 2.0,
        "keyframes": [
            {"time": 1.0, "scale": 1.0, "color": "#000000"},
            {"time": 2.0, "scale": 2.0, "color": "#FFFFFF"},
        ],
    }
    state = TimelinePlayer.get_word_properties_at_time(word_info, 1.5)
    assert state["scale"] == 1.5
    assert state["color"] == "#7F7F7F"


@patch("backend.app.rendering.asset_manager.AssetManager.get_video_path")
@patch("backend.app.rendering.asset_manager.AssetManager.get_subtitles_json_path")
@patch("backend.app.services.render_service.open")
@patch("backend.app.rendering.renderer.Renderer.render")
def test_render_endpoints(
    mock_render, mock_open, mock_sub_path, mock_video_path
):
    mock_video_path.return_value = "/path/to/video.mp4"
    mock_sub_path.return_value = "/path/to/subtitles.json"

    # Mock subtitles file loader content returning an empty segment array
    mock_file = MagicMock()
    mock_file.__enter__.return_value.read.return_value = "[]"
    mock_open.return_value = mock_file

    with patch("backend.app.api.v1.endpoints.render.get_db") as mock_get_db:
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db

        # 1. Trigger POST render request
        response = client.post(
            f"{settings.API_PREFIX}/render",
            json={
                "video_id": "dummy_video_id",
                "subtitle_id": "dummy_subtitle_id",
                "style_name": "default",
                "animation_preset": "word_highlight",
            },
        )
        assert response.status_code == 202
        data = response.json()
        assert "render_id" in data
        assert data["status"] in ["processing", "rendering", "completed"]

        render_id = data["render_id"]

        # 2. Query GET progress status
        status_resp = client.get(f"{settings.API_PREFIX}/render/{render_id}")
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        assert status_data["render_id"] == render_id
        assert status_data["status"] in ["processing", "rendering", "completed"]


def test_get_nonexistent_render_status():
    response = client.get(f"{settings.API_PREFIX}/render/invalid-render-id")
    assert response.status_code == 404
