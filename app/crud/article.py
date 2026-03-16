from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Article


async def save_article(
    db: AsyncSession,
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
    await db.commit()
    await db.refresh(article)
    return article


async def get_article_by_id(db: AsyncSession, article_id: int):
    res = await db.execute(select(Article).where(Article.article_id == article_id))
    return res.scalar_one_or_none()
