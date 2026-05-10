from fastapi import APIRouter, Request, Depends, Body
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import data_cleaning, data_prep, extract_id, parse_article
from app.crud import get_article_by_id, save_article
from app.crud.status import create_task_status, get_task_status
from app.schemas import URLRequest
from app.task import process_text_task
from app.cache import get_from_cached, save_to_cache

router = APIRouter(prefix="/predict")


@router.post("/text")
async def predict_text(
        request: Request,
        text: str = Body(None, media_type="text/plain"),
        db: Session = Depends(get_db)
):
    if text:
        # Если пришел JSON с полем text
        cleaned_text = data_cleaning(text)
    else:
        body = await request.body()
        text = body.decode("utf-8", errors="ignore")
        if text.startswith("\ufeff"):
            text = text[1:]
        cleaned_text = data_cleaning(text)

    task = process_text_task.delay(cleaned_text, None, None)

    create_task_status(
        db=db,
        task_id=task.id,
        article_id=None,
        url=None
    )

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "Текст в очереди"
    }


@router.post("/url")
async def predict_url(
        body: URLRequest,
        db: Session = Depends(get_db)
):
    url = str(body.url)
    article_id = extract_id(url)

    if not article_id:
        return {"predicted_class": "Некорректный URL"}

    existing_article = get_article_by_id(db, article_id)
    if existing_article:
        return {"predicted_class": existing_article.predicted_class}

    article_data = await parse_article(url)
    if not article_data or not article_data["full_text"]:
        return {"predicted_class": "Не удалось получить текст"}

    final_text = data_prep(
        article_data["full_text"],
        article_data["topics"],
        article_data["title"],
    )

    task = process_text_task.delay(final_text, int(article_id), url)

    create_task_status(
        db=db,
        task_id=task.id,
        article_id=int(article_id),
        url=url
    )

    return {
        "task_id": task.id,
        "status": "pending",
        "message": "URL в очереди"
    }


@router.get("/task/{task_id}")
async def get_task_status_endpoint(
        task_id: str,
        db: Session = Depends(get_db)
):
    cached = get_from_cached(task_id)
    if cached:
        return {
            "task_id": task_id,
            "status": cached["status"],
            "result": cached.get("result"),
            "error": cached.get("error"),
            "cached": True
        }

    db_status = get_task_status(db, task_id)

    if not db_status:
        return {
            "task_id": task_id,
            "status": "not_found",
            "message": "Задача не найдена"
        }

    if db_status.status in ("completed", "failed"):
        get_from_cached(task_id, db_status.status, db_status.result, db_status.error)

    if db_status.status == "completed":
        return {
            "task_id": task_id,
            "status": "completed",
            "result": db_status.result
        }
    elif db_status.status == "failed":
        return {
            "task_id": task_id,
            "status": "failed",
            "error": db_status.error
        }
    elif db_status.status == "processing":
        return {
            "task_id": task_id,
            "status": "processing",
            "started_at": db_status.started_at
        }
    else:
        return {
            "task_id": task_id,
            "status": "pending",
            "created_at": db_status.created_at
        }