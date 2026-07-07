import os
import shutil
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.video import Video
from backend.main import app

client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # Setup test database tables before each test
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables, dispose engine to unlock connection handles, and cleanup files
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    if os.path.exists("./sql_app.db"):
        try:
            os.remove("./sql_app.db")
        except PermissionError:
            pass  # Fallback if Windows file lock is persistent

    if os.path.exists(settings.UPLOAD_DIR):
        shutil.rmtree(settings.UPLOAD_DIR, ignore_errors=True)
    if os.path.exists(settings.TEMP_DIR):
        shutil.rmtree(settings.TEMP_DIR, ignore_errors=True)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_valid_test_video(path: str, color_offset: int = 0):
    """Generate a tiny unique 1-frame valid MP4 video file programmatically."""
    # Add a color offset to make the content unique and avoid hash collision
    img = np.zeros((64, 64, 3), dtype=np.uint8) + color_offset
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(path, fourcc, 10.0, (64, 64))
    out.write(img)
    out.release()


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "running",
        "project": settings.APP_NAME,
    }


def test_successful_video_upload(db_session):
    video_filename = "test_valid.mp4"
    create_valid_test_video(video_filename, color_offset=1)

    try:
        with open(video_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (video_filename, f, "video/mp4")},
            )
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["filename"] == video_filename
        assert data["size"] > 0
        assert data["duration"] > 0
        assert data["status"] == "uploaded"

        # Verify database record exists
        db_video = (
            db_session.query(Video).filter(Video.id == data["id"]).first()
        )
        assert db_video is not None
        assert db_video.filename == video_filename
        assert os.path.exists(db_video.stored_path)
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)


def test_upload_invalid_extension():
    dummy_filename = "test.txt"
    with open(dummy_filename, "w") as f:
        f.write("hello world")

    try:
        with open(dummy_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (dummy_filename, f, "video/mp4")},
            )
        assert response.status_code == 400
        assert "Extension not allowed" in response.json()["detail"]
    finally:
        if os.path.exists(dummy_filename):
            os.remove(dummy_filename)


def test_upload_invalid_mime_type():
    video_filename = "test_invalid_mime.mp4"
    create_valid_test_video(video_filename, color_offset=2)

    try:
        with open(video_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (video_filename, f, "text/plain")},
            )
        assert response.status_code == 400
        assert "MIME type not allowed" in response.json()["detail"]
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)


def test_upload_corrupted_video():
    corrupted_filename = "test_corrupted.mp4"
    with open(corrupted_filename, "wb") as f:
        f.write(b"invalid header, not a valid video file")

    try:
        with open(corrupted_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (corrupted_filename, f, "video/mp4")},
            )
        assert response.status_code == 400
        detail = response.json()["detail"]
        assert "Corrupted" in detail or "Invalid video properties" in detail
    finally:
        if os.path.exists(corrupted_filename):
            os.remove(corrupted_filename)


def test_upload_empty_file():
    empty_filename = "test_empty.mp4"
    with open(empty_filename, "wb") as f:
        pass

    try:
        with open(empty_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (empty_filename, f, "video/mp4")},
            )
        assert response.status_code == 400
        assert "Empty upload file" in response.json()["detail"]
    finally:
        if os.path.exists(empty_filename):
            os.remove(empty_filename)


def test_upload_duplicate_file():
    video_filename = "test_duplicate.mp4"
    create_valid_test_video(video_filename, color_offset=3)

    try:
        # First upload
        with open(video_filename, "rb") as f:
            response1 = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (video_filename, f, "video/mp4")},
            )
        assert response1.status_code == 201

        # Second upload
        with open(video_filename, "rb") as f:
            response2 = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (video_filename, f, "video/mp4")},
            )
        assert response2.status_code == 409
        assert "Duplicate upload" in response2.json()["detail"]
    finally:
        if os.path.exists(video_filename):
            os.remove(video_filename)


def test_upload_file_too_large():
    video_filename = "test_too_large.mp4"
    create_valid_test_video(video_filename, color_offset=4)

    # Set Max limit to 10 bytes to trigger Payload Too Large
    original_max_size = settings.MAX_UPLOAD_SIZE
    settings.MAX_UPLOAD_SIZE = 10

    try:
        with open(video_filename, "rb") as f:
            response = client.post(
                f"{settings.API_PREFIX}/upload",
                files={"file": (video_filename, f, "video/mp4")},
            )
        assert response.status_code == 413
        assert (
            "File size exceeds the maximum limit" in response.json()["detail"]
        )
    finally:
        settings.MAX_UPLOAD_SIZE = original_max_size
        if os.path.exists(video_filename):
            os.remove(video_filename)
