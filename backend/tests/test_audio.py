import os
import shutil
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.video import Video
from backend.main import app

client = TestClient(app)


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
    if os.path.exists(settings.AUDIO_FOLDER):
        shutil.rmtree(settings.AUDIO_FOLDER, ignore_errors=True)
    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR, ignore_errors=True)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def dummy_video(db_session):
    video_id = "test-video-id-123"
    dummy_path = os.path.join(settings.UPLOAD_DIR, "dummy_video.mp4")

    # Ensure directory and file exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(dummy_path, "wb") as f:
        f.write(b"dummy video data")

    db_video = Video(
        id=video_id,
        filename="dummy_video.mp4",
        stored_path=dummy_path,
        file_hash="dummy_hash_123",
        size=16,
        duration=10.5,
        status="uploaded",
    )
    db_session.add(db_video)
    db_session.commit()
    db_session.refresh(db_video)

    yield db_video

    # Cleanup
    db_session.delete(db_video)
    db_session.commit()
    if os.path.exists(dummy_path):
        os.remove(dummy_path)


@patch("backend.app.utils.ffmpeg.is_ffmpeg_installed")
@patch("subprocess.run")
def test_successful_audio_extraction(mock_run, mock_check, dummy_video):
    mock_check.return_value = True

    # Set up mock run completed successfully
    mock_response = MagicMock()
    mock_response.returncode = 0
    mock_run.return_value = mock_response

    # Define side effect to actually create the WAV file so checks pass
    def side_effect(cmd, *args, **kwargs):
        audio_path = cmd[-1]
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        with open(audio_path, "wb") as f:
            f.write(b"dummy wav data")
        return mock_response

    mock_run.side_effect = side_effect

    response = client.post(
        f"{settings.API_PREFIX}/audio/extract",
        json={"video_id": dummy_video.id},
    )

    assert response.status_code == 200
    data = response.json()
    assert "audio_id" in data
    assert data["status"] == "completed"
    assert data["duration"] == dummy_video.duration
    assert data["sample_rate"] == settings.AUDIO_SAMPLE_RATE
    assert data["channels"] == settings.AUDIO_CHANNELS
    assert os.path.exists(data["audio_path"])

    # Cleanup generated audio
    if os.path.exists(data["audio_path"]):
        os.remove(data["audio_path"])


def test_extraction_video_not_found():
    response = client.post(
        f"{settings.API_PREFIX}/audio/extract",
        json={"video_id": "non-existent-id"},
    )
    assert response.status_code == 404
    assert "Video record with ID" in response.json()["detail"]


def test_extraction_file_missing_on_disk(db_session):
    video_id = "test-missing-file-id"
    db_video = Video(
        id=video_id,
        filename="missing.mp4",
        stored_path="some/missing/path.mp4",
        file_hash="missing_hash_321",
        size=100,
        duration=5.0,
        status="uploaded",
    )
    db_session.add(db_video)
    db_session.commit()

    try:
        response = client.post(
            f"{settings.API_PREFIX}/audio/extract",
            json={"video_id": video_id},
        )
        assert response.status_code == 404
        assert "Video file not found on disk" in response.json()["detail"]
    finally:
        db_session.delete(db_video)
        db_session.commit()


@patch("backend.app.utils.ffmpeg.is_ffmpeg_installed")
def test_extraction_ffmpeg_not_available(mock_check, dummy_video):
    mock_check.return_value = False

    response = client.post(
        f"{settings.API_PREFIX}/audio/extract",
        json={"video_id": dummy_video.id},
    )
    assert response.status_code == 500
    assert "FFmpeg installation is not available" in response.json()["detail"]


@patch("backend.app.utils.ffmpeg.is_ffmpeg_installed")
@patch("subprocess.run")
def test_extraction_ffmpeg_execution_failure(
    mock_run, mock_check, dummy_video
):
    mock_check.return_value = True

    # Set up mock run completed with error code
    mock_response = MagicMock()
    mock_response.returncode = 1
    mock_response.stderr = "FFmpeg: Output file does not contain any stream"
    mock_run.return_value = mock_response
    mock_run.side_effect = None

    response = client.post(
        f"{settings.API_PREFIX}/audio/extract",
        json={"video_id": dummy_video.id},
    )
    assert response.status_code == 500
    assert "does not contain any audio track" in response.json()["detail"]
