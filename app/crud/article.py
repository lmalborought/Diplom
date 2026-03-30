from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models import Article


def save_article(
    db: Session,
    url: str,
    article_id: int,
    predicted_class: str,
):
    article = Article(
        url=url,
        article_id=article_id,
        predicted_class=predicted_class,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article_by_id(db: Session, article_id: int):
    res = db.execute(select(Article).where(Article.article_id == article_id))
    return res.scalar_one_or_none()