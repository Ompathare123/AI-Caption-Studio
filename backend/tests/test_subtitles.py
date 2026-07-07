import json
import os
import shutil
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.alignment import Alignment
from backend.app.models.transcript import Transcript
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
def setup_database():
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.SUBTITLES_OUTPUT_DIR, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("./sql_app.db"):
        try:
            os.remove("./sql_app.db")
        except PermissionError:
            pass
    if os.path.exists(settings.SUBTITLES_OUTPUT_DIR):
        shutil.rmtree(settings.SUBTITLES_OUTPUT_DIR, ignore_errors=True)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def dummy_alignment(db_session):
    align_id = "test-align-uuid-999"
    t_id = "test-transcript-uuid-999"

    db_transcript = Transcript(
        id=t_id,
        audio_id="test-audio-uuid-999",
        language="en",
        status="completed",
    )
    db_session.add(db_transcript)
    db_session.commit()

    words_data = [
        {"word": "Hello", "start": 0.1, "end": 0.5, "confidence": 0.99},
        {"word": "everyone,", "start": 0.5, "end": 1.0, "confidence": 0.98},
        {"word": "welcome", "start": 1.1, "end": 1.5, "confidence": 0.95},
        {"word": "to", "start": 1.5, "end": 1.8, "confidence": 0.96},
        {"word": "Caption", "start": 1.8, "end": 2.2, "confidence": 0.99},
        {"word": "Studio.", "start": 2.2, "end": 2.8, "confidence": 0.97},
        {"word": "Let's", "start": 3.5, "end": 3.8, "confidence": 0.99},
        {"word": "generate", "start": 3.8, "end": 4.2, "confidence": 0.95},
        {"word": "subtitles.", "start": 4.2, "end": 4.9, "confidence": 0.99},
    ]

    db_alignment = Alignment(
        id=align_id,
        transcript_id=t_id,
        audio_id="test-audio-uuid-999",
        language="en",
        duration=5.0,
        status="completed",
        words_json=json.dumps(words_data),
    )
    db_session.add(db_alignment)
    db_session.commit()
    db_session.refresh(db_alignment)

    yield db_alignment

    # Clean up database records
    db_session.delete(db_alignment)
    db_session.delete(db_transcript)
    db_session.commit()


def test_generate_subtitles_success(dummy_alignment):
    response = client.post(
        f"{settings.API_PREFIX}/subtitles/generate",
        json={
            "alignment_id": dummy_alignment.id,
            "style": "default",
            "max_words_per_line": 5,
            "max_lines": 2,
            "output_formats": ["json", "srt", "ass"],
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["status"] == "completed"
    assert data["caption_count"] > 0

    files = data["subtitle_files"]
    assert "json" in files
    assert "srt" in files
    assert "ass" in files

    # Verify files exist and are not empty
    for fmt, path in files.items():
        assert os.path.exists(path)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content) > 0

            # Check format specific markers
            if fmt == "srt":
                assert "1" in content
                assert "-->" in content
            elif fmt == "ass":
                assert "[Script Info]" in content
                assert "[Events]" in content
                assert "Dialogue:" in content
            elif fmt == "json":
                parsed = json.loads(content)
                assert len(parsed) > 0
                assert "text" in parsed[0]
                assert "words" in parsed[0]


def test_generate_subtitles_missing_alignment():
    response = client.post(
        f"{settings.API_PREFIX}/subtitles/generate",
        json={
            "alignment_id": "non-existent-alignment-uuid",
            "style": "default",
            "max_words_per_line": 5,
            "max_lines": 2,
            "output_formats": ["srt"],
        },
    )
    assert response.status_code == 404
    assert "Alignment record with ID" in response.json()["detail"]


def test_layout_segmentation_punctuation_and_caps(dummy_alignment):
    words_data = json.loads(dummy_alignment.words_json)
    from backend.app.services.subtitle_builder import SubtitleBuilder

    captions = SubtitleBuilder.build_captions(
        words=words_data,
        max_words_per_line=5,
        max_lines=2,
        reading_speed=18,
    )

    # The sentence "Studio." ends with a period, forcing a split there
    assert len(captions) >= 2
    assert "Studio." in captions[0]["text"]
    assert "subtitles." in captions[1]["text"]
