import asyncio
import json
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from pydantic import BaseModel
import redis
from sqlalchemy.orm import Session

from backend.app.database.session import get_db
from backend.app.models.job import Job
from backend.app.queue.celery_app import REDIS_URL, celery_app
from backend.app.queue.tasks import InMemoryTracker, process_caption_pipeline_task
from backend.app.schemas.job import JobResponse

router = APIRouter()


class JobCreatePayload(BaseModel):
    project_id: str


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreatePayload, db: Session = Depends(get_db)):
    job = Job(
        project_id=payload.project_id,
        status="queued",
        current_step="Adding to Celery queue...",
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Trigger Celery Task async in background worker
    process_caption_pipeline_task.delay(job.id)

    return job


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.delete("/{job_id}")
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = "cancelled"
    job.current_step = "Job aborted by user request"
    db.commit()

    # Revoke Celery task execution
    celery_app.control.revoke(job.id, terminate=True)
    return {"message": "Job cancellation request sent successfully"}


@router.websocket("/{job_id}/progress")
async def job_progress_ws(websocket: WebSocket, job_id: str, db: Session = Depends(get_db)):
    await websocket.accept()

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        await websocket.send_json({"error": "Job not found"})
        await websocket.close()
        return

    # Setup Redis PubSub subscription if online
    try:
        redis_client = redis.from_url(REDIS_URL, socket_timeout=1)
        redis_client.ping()

        pubsub = redis_client.pubsub()
        pubsub.subscribe(f"job_progress_{job_id}")

        while True:
            # Check for Redis pubsub message (non-blocking)
            msg = pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if msg:
                data = json.loads(msg["data"].decode("utf-8"))
                await websocket.send_json(data)
                if data["status"] in ["completed", "failed", "cancelled"]:
                    break
            else:
                # Query DB to check if the status was updated
                db.refresh(job)
                await websocket.send_json(
                    {
                        "job_id": job.id,
                        "status": job.status,
                        "progress": job.progress,
                        "current_step": job.current_step,
                        "error_message": job.error_message,
                    }
                )
                if job.status in ["completed", "failed", "cancelled"]:
                    break
            await asyncio.sleep(0.1)

    except (WebSocketDisconnect, ConnectionError):
        pass
    except Exception:
        # Fallback to in-memory/polling check if Redis connection is not established
        try:
            while True:
                # Read from InMemoryTracker or DB directly
                tracker_state = InMemoryTracker.get(job_id)
                if tracker_state:
                    await websocket.send_json(tracker_state)
                    if tracker_state["status"] in [
                        "completed",
                        "failed",
                        "cancelled",
                    ]:
                        break
                else:
                    # Query SQLite DB directly as fallback
                    job_db = db.query(Job).filter(Job.id == job_id).first()
                    if job_db:
                        await websocket.send_json(
                            {
                                "job_id": job_db.id,
                                "status": job_db.status,
                                "progress": job_db.progress,
                                "current_step": job_db.current_step,
                                "error_message": job_db.error_message,
                            }
                        )
                        if job_db.status in [
                            "completed",
                            "failed",
                            "cancelled",
                        ]:
                            break
                await asyncio.sleep(0.3)
        except WebSocketDisconnect:
            pass
        finally:
            try:
                await websocket.close()
            except Exception:
                pass
