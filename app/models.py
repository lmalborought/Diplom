from sqlalchemy import Column, Integer, String

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=True)
    article_id = Column(Integer, nullable=False)
    predicted_class = Column(String, nullable=False)
