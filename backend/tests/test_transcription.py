import os
import shutil
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, engine
from backend.app.services.transcription_service import TranscriptionService
from backend.main import app

client = TestClient(app)


# Override lifespan startup loading during tests to avoid actual model download
@pytest.fixture(scope="module", autouse=True)
def mock_lifespan_model():
    with patch(
        "backend.app.services.transcription_service.WhisperModel"
    ) as mock_whisper:
        yield mock_whisper


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./sql_app.db"):
        try:
            os.remove("./sql_app.db")
        except PermissionError:
            pass


@pytest.fixture(scope="module", autouse=True)
def setup_dirs():
    os.makedirs(settings.AUDIO_FOLDER, exist_ok=True)
    yield
    if os.path.exists(settings.AUDIO_FOLDER):
        shutil.rmtree(settings.AUDIO_FOLDER, ignore_errors=True)


@pytest.fixture
def dummy_audio_file():
    audio_id = "test-audio-id-999"
    audio_path = os.path.join(settings.AUDIO_FOLDER, f"{audio_id}.wav")
    with open(audio_path, "wb") as f:
        f.write(b"dummy wav content")
    yield audio_id
    if os.path.exists(audio_path):
        os.remove(audio_path)


@patch("backend.app.services.transcription_service.WhisperModel")
def test_successful_transcription(mock_whisper_class, dummy_audio_file):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model

    mock_info = MagicMock()
    mock_info.language = "en"
    mock_info.language_probability = 0.98
    mock_info.duration = 4.2

    mock_seg = MagicMock()
    mock_seg.start = 0.0
    mock_seg.end = 4.0
    mock_seg.text = "Hello transcription world."

    mock_model.transcribe.return_value = ([mock_seg], mock_info)

    # Force reset of the singleton to reload with mock
    TranscriptionService._model = None

    response = client.post(
        f"{settings.API_PREFIX}/transcribe",
        json={"audio_id": dummy_audio_file},
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["language"] == "en"
    assert data["duration"] == 4.2
    assert len(data["segments"]) == 1
    assert data["segments"][0]["text"] == "Hello transcription world."
    assert data["status"] == "completed"


def test_transcription_missing_audio():
    response = client.post(
        f"{settings.API_PREFIX}/transcribe",
        json={"audio_id": "non-existent-audio-id"},
    )
    assert response.status_code == 404
    assert "not found on disk" in response.json()["detail"]


@patch("backend.app.services.transcription_service.WhisperModel")
def test_transcription_model_loading_failure(
    mock_whisper_class, dummy_audio_file
):
    mock_whisper_class.side_effect = Exception("Model initialization error")
    TranscriptionService._model = None

    response = client.post(
        f"{settings.API_PREFIX}/transcribe",
        json={"audio_id": dummy_audio_file},
    )
    assert response.status_code == 500
    assert "Model loading failure" in response.json()["detail"]


@patch("backend.app.services.transcription_service.WhisperModel")
def test_transcription_execution_failure(mock_whisper_class, dummy_audio_file):
    mock_model = MagicMock()
    mock_whisper_class.return_value = mock_model
    mock_model.transcribe.side_effect = Exception("Audio read failure")

    TranscriptionService._model = mock_model

    response = client.post(
        f"{settings.API_PREFIX}/transcribe",
        json={"audio_id": dummy_audio_file},
    )
    assert response.status_code == 500
    assert (
        "Internal transcription execution failed" in response.json()["detail"]
    )
