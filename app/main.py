from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path

from contextlib import asynccontextmanager

from app.database import get_db
from app.inference import InferenceService
from app.parser import (
    data_cleaning,
    data_prep,
    extract_id,
    parse_article,
)
from app.crud import get_article_by_id, save_article
from app.schemas import PredictResponse, URLRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.inference_service = InferenceService()
        print("Модель загружена")
    except Exception as e:
        print(f"Ошибка загрузки модели: {e}")
        raise
    yield


app = FastAPI(title="Text Classification API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
try:
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
except Exception:
    print("Папка static не найдена")



@app.post("/predict/text", response_model=PredictResponse)
async def predict_text(
    request: Request,
):
    try:
        inference = request.app.state.inference_service
        body = await request.body()
        if not body:
            return {"predicted_class": "Пустой запрос"}
        
        text = body.decode("utf-8", errors="ignore")
        if text.startswith("\ufeff"):
            text = text[1:]
        
        if not text.strip():
            return {"predicted_class": "Пустой текст"}
        
        cleaned_text = data_cleaning(text)
        predicted = await run_in_threadpool(inference.predict, cleaned_text)
        
        return {"predicted_class": predicted}
    
    except Exception:
        return {"predicted_class": "Ошибка обработки текста"}


@app.post("/predict/url", response_model=PredictResponse)
async def predict_url(
    request: Request,
    body: URLRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        inference = request.app.state.inference_service
        url = str(body.url)
    
        
        article_id = extract_id(url)
        if not article_id:
            return {"predicted_class": "Некорректный URL"}

        try:
            existing_article = await get_article_by_id(db, article_id)
            if existing_article:
                return {"predicted_class": existing_article.predicted_class}
        except Exception:
            pass

        try:
            article_data = await parse_article(url)
            if not article_data or not article_data.get("full_text"):
                return {"predicted_class": "Не удалось получить текст"}
        except Exception:
            return {"predicted_class": "Ошибка парсинга статьи"}

        try:
            final_text = data_prep(
                article_data["full_text"],
                article_data.get("topics", []),
                article_data.get("title", ""),
            )
        except Exception:
            return {"predicted_class": "Ошибка подготовки текста"}

        try:
            predicted = await run_in_threadpool(inference.predict, final_text)
        except Exception:
            return {"predicted_class": "Ошибка модели"}

        try:
            await save_article(
                db=db,
                url=article_data["url"],
                article_id=int(article_id),
                predicted_class=predicted,
            )
        except Exception:
            pass

        return {"predicted_class": predicted}
    
    except Exception:
        return {"predicted_class": "Внутренняя ошибка сервера"}


@app.get("/")
async def root():
    try:
        return FileResponse(STATIC_DIR / "index.html")
    except Exception:
        return JSONResponse(
            status_code=404,
            content={"message": "Frontend not found"}
        )