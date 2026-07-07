import os
from celery import Celery
import redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "ai_caption_studio", broker=REDIS_URL, backend=REDIS_URL
)

# Test Redis connection to enable eager mode fallback if offline on Windows
redis_available = False
try:
    client = redis.from_url(REDIS_URL, socket_timeout=1)
    client.ping()
    redis_available = True
except Exception:
    redis_available = False

# Enable in-memory task runner fallback if Celery/Redis is not running
if (
    not redis_available
    or os.getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
):
    celery_app.conf.update(
        task_always_eager=True, task_eager_propagates=True
    )

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    imports=["backend.app.queue.tasks"],
)
