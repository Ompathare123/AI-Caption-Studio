import os
from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient

from backend.app.core.config import settings
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models.project import Project
from backend.app.models.video import Video
from backend.main import app

client = TestClient(app)


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
def configure_celery():
    from backend.app.queue.celery_app import celery_app

    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)
    yield


@pytest.fixture
def mock_project(db_session):
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

    project = Project(
        id="test-project-uuid",
        video_id="test-video-uuid",
        captions_data=[],
        style_data={},
        animation_preset="word_highlight",
    )
    db_session.add(project)
    db_session.commit()
    db_session.refresh(project)
    return project


@patch("backend.app.queue.tasks.AudioService.extract_audio")
@patch("backend.app.queue.tasks.TranscriptionService.transcribe_audio")
@patch("backend.app.queue.tasks.AlignmentService.align_transcript")
@patch("backend.app.queue.tasks.SubtitleService.generate_subtitles")
def test_job_processing_lifecycle(
    mock_sub, mock_align, mock_transcribe, mock_extract, mock_project
):
    mock_extract.return_value = MagicMock(id="audio-123")
    mock_transcribe.return_value = MagicMock(id="trans-123", text="hello")
    mock_align.return_value = MagicMock(id="align-123")

    # 1. Create Job
    response = client.post(
        f"{settings.API_PREFIX}/jobs", json={"project_id": "test-project-uuid"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["project_id"] == "test-project-uuid"

    job_id = data["id"]

    # 2. Get Job Details (synced instantly in eager task runner mode)
    get_resp = client.get(f"{settings.API_PREFIX}/jobs/{job_id}")
    assert get_resp.status_code == 200
    job_data = get_resp.json()
    assert job_data["status"] == "completed"
    assert job_data["progress"] == 100

    # 3. Test Invalid Job Lookups
    fail_resp = client.get(f"{settings.API_PREFIX}/jobs/invalid-job-id")
    assert fail_resp.status_code == 404

    # 4. Cancel Job
    cancel_resp = client.delete(f"{settings.API_PREFIX}/jobs/{job_id}")
    assert cancel_resp.status_code == 200
    assert (
        cancel_resp.json()["message"]
        == "Job cancellation request sent successfully"
    )

if __name__ == '__main__':
    # Force eager execution mode in Celery during manual execution
    from backend.app.queue.celery_app import celery_app
    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)
    
    # Initialize DB tables
    Base.metadata.create_all(bind=engine)
    try:
        db = SessionLocal()
        # Cleanup
        db.query(Video).delete()
        db.query(Project).delete()
        db.query(Job).delete()
        db.commit()
        
        video = Video(
            id="test-video-uuid",
            filename="test.mp4",
            stored_path="/path/to/test.mp4",
            file_hash="dummyhash",
            size=1024,
            duration=10.0,
            status="uploaded",
        )
        db.add(video)
        db.commit()
        
        project = Project(
            id="test-project-uuid",
            video_id="test-video-uuid",
            captions_data=[],
            style_data={},
            animation_preset="word_highlight",
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        
        with patch("backend.app.queue.tasks.AudioService.extract_audio") as mock_extract, \
             patch("backend.app.queue.tasks.TranscriptionService.transcribe_audio") as mock_transcribe, \
             patch("backend.app.queue.tasks.AlignmentService.align_transcript") as mock_align, \
             patch("backend.app.queue.tasks.SubtitleService.generate_subtitles") as mock_sub:
             
            mock_extract.return_value = MagicMock(id="audio-123")
            mock_transcribe.return_value = MagicMock(id="trans-123", text="hello")
            mock_align.return_value = MagicMock(id="align-123")
            
            # Execute create job POST
            response = client.post(
                f"{settings.API_PREFIX}/jobs",
                json={"project_id": "test-project-uuid"}
            )
            assert response.status_code == 201
            print("Create Job: PASS")
            
            job_id = response.json()["id"]
            
            # Execute get job GET
            get_resp = client.get(f"{settings.API_PREFIX}/jobs/{job_id}")
            assert get_resp.status_code == 200
            assert get_resp.json()["status"] == "completed"
            assert get_resp.json()["progress"] == 100
            print("Get Job Status: PASS")
            
            # Execute cancel DELETE
            cancel_resp = client.delete(f"{settings.API_PREFIX}/jobs/{job_id}")
            assert cancel_resp.status_code == 200
            print("Cancel Job: PASS")
            
            # Test Invalid ID
            fail_resp = client.get(f"{settings.API_PREFIX}/jobs/invalid-id")
            assert fail_resp.status_code == 404
            print("Get Invalid Job: PASS")
            
        print("ALL TESTS PASSED SUCCESSFULLY!")
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
