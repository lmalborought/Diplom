from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import datetime
from app.models.status import TaskStatus


def create_task_status(db: Session, task_id: str, article_id: int = None, url: str = None) -> TaskStatus:
    task_status = TaskStatus(
        task_id=task_id,
        status="pending",
        article_id=article_id,
        url=url
    )
    db.add(task_status)
    db.commit()
    db.refresh(task_status)
    return task_status


def update_task_status(db: Session, task_id: str, status: str, result: str = None, error: str = None) -> None:
    updates = {"status": status, "updated_at": datetime.utcnow()}

    if status == "processing":
        updates["started_at"] = datetime.utcnow()
    elif status == "completed" and result:
        updates["result"] = result
        updates["completed_at"] = datetime.utcnow()
    elif status == "failed" and error:
        updates["error"] = error
        updates["completed_at"] = datetime.utcnow()

    db.execute(
        update(TaskStatus)
            .where(TaskStatus.task_id == task_id)
            .values(**updates)
    )
    db.commit()


def get_task_status(db: Session, task_id: str) -> TaskStatus | None:
    result = db.execute(
        select(TaskStatus).where(TaskStatus.task_id == task_id)
    )
    return result.scalar_one_or_none()