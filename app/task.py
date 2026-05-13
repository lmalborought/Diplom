from celery import Celery
import os
from typing import Optional
import time

from app.services.inference import InferenceService
from app.database import SessionLocal
from app.crud.status import update_task_status
from app.crud import save_article
from app.cache import save_to_cache

from celery.signals import worker_process_init

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


celery_app = Celery(
    'tasks',
    broker=RABBITMQ_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=3,
)

inference = None


@worker_process_init.connect
def load_model(**kwargs):
    start_time = time.time()
    global inference
    inference = InferenceService()
    print(f"Model loaded in {time.time() - start_time:.2f} seconds")


@celery_app.task(bind=True, name='process_text')
def process_text_task(self, text: str, article_id: Optional[int] = None, url: Optional[str] = None):
    global inference

    task_id = self.request.id
    total_start = time.time()


    self.update_state(
        state='PROCESSING',
        meta={'text': text[:50], 'task_id': task_id, 'article_id': article_id}
    )

    db = SessionLocal()

    try:
        update_task_status(db, task_id, "processing")

        start_inference = time.time()
        predicted = inference.predict(text)
        inference_time = time.time() - start_inference
        print(f"[{task_id}] Инференс модели: {inference_time:.4f} сек")

        if article_id and url:
            save_article(
                db=db,
                url=url,
                article_id=article_id,
                predicted_class=predicted,
            )

        update_task_status(db, task_id, "completed", result=predicted)
        save_to_cache(task_id, "completed", result=predicted)

        total_time = time.time() - total_start
        print(f"[{task_id}] Общее время воркера: {total_time:.4f} сек")
        return {"predicted_class": predicted}

    except Exception as ex:
        print(f"Error in task {task_id}: {ex}")
        update_task_status(db, task_id, "failed", error=str(ex))
        save_to_cache(task_id, "failed", error=str(ex))
        raise

    finally:
        db.close()

