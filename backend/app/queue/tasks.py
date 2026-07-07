import json
import time
from datetime import datetime
import redis
import threading
from sqlalchemy.orm import Session

from backend.app.database.session import SessionLocal
from backend.app.models.job import Job
from backend.app.models.project import Project
from backend.app.queue.celery_app import REDIS_URL, celery_app
from backend.app.services.alignment_service import AlignmentService
from backend.app.services.audio_service import AudioService
from backend.app.services.project_service import ProjectService
from backend.app.services.subtitle_service import SubtitleService
from backend.app.services.transcription_service import TranscriptionService


class InMemoryTracker:
    _lock = threading.Lock()
    _states = {}

    @classmethod
    def update(cls, job_id: str, data: dict):
        with cls._lock:
            cls._states[job_id] = data

    @classmethod
    def get(cls, job_id: str):
        with cls._lock:
            return cls._states.get(job_id)


redis_client = None
try:
    redis_client = redis.from_url(REDIS_URL)
except Exception:
    pass


def broadcast_update(
    job_id: str,
    status: str,
    progress: int,
    current_step: str,
    error_message: str = None,
):
    payload = {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "current_step": current_step,
        "error_message": error_message,
    }

    # Save to SQLite database
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = status
            job.progress = progress
            job.current_step = current_step
            if error_message:
                job.error_message = error_message
            if status == "completed":
                job.completed_at = datetime.utcnow()
            elif status == "extracting_audio" and not job.started_at:
                job.started_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()

    # Publish to Redis channel
    if redis_client:
        try:
            redis_client.publish(f"job_progress_{job_id}", json.dumps(payload))
        except Exception:
            pass

    # Update local in-memory fallback
    InMemoryTracker.update(job_id, payload)


@celery_app.task(bind=True, name="process_caption_pipeline")
def process_caption_pipeline_task(self, job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        db.close()
        return f"Job ID '{job_id}' not found"

    project_id = job.project_id
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        db.close()
        return f"Project ID '{project_id}' not found"

    video_id = project.video_id
    db.close()

    try:
        # Step 1: Extract Audio
        broadcast_update(
            job_id, "extracting_audio", 15, "Isolating audio channels..."
        )
        audio = AudioService.extract_audio(video_id)
        audio_id = audio.id

        # Step 2: Transcribe
        broadcast_update(
            job_id, "transcribing", 45, "Running Whisper speech recognition..."
        )
        transcript = TranscriptionService.transcribe_audio(audio_id)
        transcript_id = transcript.id

        # Step 3: Align
        broadcast_update(
            job_id, "aligning", 70, "Aligning word-level timestamps..."
        )
        alignment = AlignmentService.align_transcript(audio_id, transcript_id)
        alignment_id = alignment.id

        # Step 4: Subtitle Generation
        broadcast_update(
            job_id, "subtitle_generation", 85, "Generating SRT and JSON subtitles..."
        )
        SubtitleService.generate_subtitles(alignment_id, "json")

        # Update project captions data
        db = SessionLocal()
        try:
            proj = db.query(Project).filter(Project.id == project_id).first()
            if proj:
                # Reload project to populate aligned segments
                updated_proj = ProjectService.create_project(
                    db, video_id, video_id
                )
                proj.captions_data = updated_proj.captions_data
                db.commit()
        finally:
            db.close()

        # Completed
        broadcast_update(
            job_id, "completed", 100, "Pipeline completed successfully!"
        )

    except Exception as e:
        error_msg = str(e)
        broadcast_update(
            job_id,
            "failed",
            45,  # keep progress of failure step for diagnostic references
            f"Error: {error_msg}",
            error_message=error_msg,
        )
        return f"Pipeline failed: {error_msg}"

    return "Pipeline completed successfully"
