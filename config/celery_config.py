from celery import Celery
from config.config import settings
from core.logging import logger

try:
    # Celery instance with Redis as broker using the dynamic settings
    celery_app = Celery(
        'scraper',
        broker=settings.REDIS_URI
    )
    logger.info("Celery app created with broker: %s", settings.REDIS_URI)
except Exception as e:
    logger.error("Error initializing Celery app", exc_info=True)
    raise e from None

# Celery configuration optimized for Upstash Redis
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry_on_startup=True,  # Retry if Redis connection fails
    broker_transport_options={
        'visibility_timeout': 3600  # 1 hour timeout for tasks
    },
    result_backend=None  # Disable result backend (Upstash Redis not ideal for storing results)
)

# Optional: Auto-discover tasks in the 'app.tasks' module for modularity
celery_app.autodiscover_tasks(['app.tasks'])

logger.info("Celery configuration updated.")