import os
import shutil
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.transcript import Transcript, TranscriptSegment
from backend.app.services.alignment_service import AlignmentService
from backend.main import app

client = TestClient(app)


# Override lifespan startup model loading during tests to avoid actual Whisper download
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
    if os.path.exists(settings.AUDIO_FOLDER):
        shutil.rmtree(settings.AUDIO_FOLDER, ignore_errors=True)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def dummy_audio_file():
    audio_id = "test-audio-id-align"
    audio_path = os.path.join(settings.AUDIO_FOLDER, f"{audio_id}.wav")
    os.makedirs(settings.AUDIO_FOLDER, exist_ok=True)
    with open(audio_path, "wb") as f:
        f.write(b"dummy audio wav content")
    yield audio_id
    if os.path.exists(audio_path):
        os.remove(audio_path)


@pytest.fixture
def dummy_transcript(db_session):
    t_id = "test-transcript-id-align"
    db_transcript = Transcript(
        id=t_id,
        audio_id="test-audio-id-align",
        language="en",
        status="completed",
    )
    db_session.add(db_transcript)
    db_session.commit()

    db_seg = TranscriptSegment(
        transcript_id=t_id,
        start=0.0,
        end=4.0,
        text="Hello world.",
    )
    db_session.add(db_seg)
    db_session.commit()
    db_session.refresh(db_transcript)

    yield db_transcript

    # Cleanup
    db_session.delete(db_transcript)
    db_session.commit()


@patch("whisperx.load_audio")
@patch("whisperx.load_align_model")
@patch("whisperx.align")
def test_successful_alignment(
    mock_align, mock_load_model, mock_load_audio, dummy_audio_file, dummy_transcript
):
    mock_load_audio.return_value = [0.0] * 16000  # 1 second of audio
    mock_load_model.return_value = (MagicMock(), MagicMock())

    mock_align.return_value = {
        "segments": [
            {
                "start": 0.0,
                "end": 4.0,
                "text": "Hello world.",
                "words": [
                    {
                        "word": "Hello",
                        "start": 0.05,
                        "end": 0.45,
                        "score": 0.99,
                    },
                    {
                        "word": "world.",
                        "start": 0.45,
                        "end": 0.95,
                        "score": 0.98,
                    },
                ],
            }
        ]
    }

    # Reset cached alignment models to force reload
    AlignmentService._align_models = {}

    response = client.post(
        f"{settings.API_PREFIX}/align",
        json={
            "audio_id": dummy_audio_file,
            "transcript_id": dummy_transcript.id,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["language"] == "en"
    assert data["status"] == "completed"
    assert len(data["words"]) == 2
    assert data["words"][0]["word"] == "Hello"
    assert data["words"][0]["start"] == 0.05
    assert data["words"][0]["confidence"] == 0.99


def test_alignment_missing_transcript(dummy_audio_file):
    response = client.post(
        f"{settings.API_PREFIX}/align",
        json={
            "audio_id": dummy_audio_file,
            "transcript_id": "non-existent-transcript",
        },
    )
    assert response.status_code == 404
    assert "Transcript record with ID" in response.json()["detail"]


def test_alignment_missing_audio(dummy_transcript):
    response = client.post(
        f"{settings.API_PREFIX}/align",
        json={
            "audio_id": "missing-audio-id",
            "transcript_id": dummy_transcript.id,
        },
    )
    assert response.status_code == 404
    assert "Audio file with ID" in response.json()["detail"]


@patch("whisperx.load_audio")
@patch("whisperx.load_align_model")
def test_alignment_model_loading_failure(
    mock_load_model, mock_load_audio, dummy_audio_file, dummy_transcript
):
    mock_load_audio.return_value = [0.0] * 16000
    mock_load_model.side_effect = Exception("CUDA error loading alignment model")

    AlignmentService._align_models = {}

    response = client.post(
        f"{settings.API_PREFIX}/align",
        json={
            "audio_id": dummy_audio_file,
            "transcript_id": dummy_transcript.id,
        },
    )
    assert response.status_code == 500
    assert "Alignment model loading failure" in response.json()["detail"]


@patch("whisperx.load_audio")
@patch("whisperx.load_align_model")
@patch("whisperx.align")
def test_alignment_execution_failure(
    mock_align, mock_load_model, mock_load_audio, dummy_audio_file, dummy_transcript
):
    mock_load_audio.return_value = [0.0] * 16000
    mock_load_model.return_value = (MagicMock(), MagicMock())
    mock_align.side_effect = Exception("Phoneme matching failed")

    AlignmentService._align_models = {}

    response = client.post(
        f"{settings.API_PREFIX}/align",
        json={
            "audio_id": dummy_audio_file,
            "transcript_id": dummy_transcript.id,
        },
    )
    assert response.status_code == 500
    assert "Internal alignment execution failed" in response.json()["detail"]
