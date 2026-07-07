import os
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.video import Video
from backend.app.models.user import User
from backend.app.api.v1.endpoints.auth import get_current_user
from backend.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth_dependency(db_session):
    # Setup mock user in database
    user = User(
        id="test-user-id",
        email="test@example.com",
        hashed_password="dummy",
        name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    def mock_get_current_user():
        return user

    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function", autouse=True)
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


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module", autouse=True)
def mock_lifespan_model():
    with patch(
        "backend.app.services.transcription_service.WhisperModel"
    ) as mock_whisper:
        yield mock_whisper


@pytest.fixture
def mock_video(db_session):
    video = Video(
        id="test-video-uuid",
        filename="test.mp4",
        stored_path="/path/to/test.mp4",
        file_hash="dummyhash",
        size=1024,
        duration=10.0,
        status="uploaded",
    )
    db_session.add(video)
    db_session.commit()
    db_session.refresh(video)
    return video


def test_project_crud_lifecycle(mock_video):
    # 1. Create project
    response = client.post(
        f"{settings.API_PREFIX}/projects", json={"video_id": "test-video-uuid"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["video_id"] == "test-video-uuid"
    assert data["animation_preset"] == "word_highlight"
    assert "style_data" in data

    project_id = data["id"]

    # 2. Get project details
    get_resp = client.get(f"{settings.API_PREFIX}/projects/{project_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == project_id

    # 3. Update project details
    updated_captions = [
        {
            "index": 1,
            "start": 1.0,
            "end": 3.0,
            "text": "edited text",
            "words": [{"word": "edited", "start": 1.0, "end": 2.0}],
        }
    ]
    updated_style = {
        "font_family": "Montserrat",
        "font_size": 30,
        "text_color": "#FF0000",
    }

    put_resp = client.put(
        f"{settings.API_PREFIX}/projects/{project_id}",
        json={
            "captions_data": updated_captions,
            "style_data": updated_style,
            "animation_preset": "word_pop",
        },
    )
    assert put_resp.status_code == 200
    updated_data = put_resp.json()
    assert updated_data["animation_preset"] == "word_pop"
    assert updated_data["captions_data"] == updated_captions
    assert updated_data["style_data"]["font_family"] == "Montserrat"
    assert updated_data["style_data"]["font_size"] == 30

    # 4. Get invalid project
    fail_resp = client.get(f"{settings.API_PREFIX}/projects/invalid-project-id")
    assert fail_resp.status_code == 404
