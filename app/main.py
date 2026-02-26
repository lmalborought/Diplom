from fastapi import FastAPI, Request, Depends
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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
    print("Loading model")
    app.state.inference_service = InferenceService()
    yield


app = FastAPI(title="Text Classification API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def get_inference_service(request: Request) -> InferenceService:
    return request.app.state.inference_service


@app.post("/predict/text", response_model=PredictResponse)
async def predict_text(
    request: Request,
    inference: InferenceService = Depends(get_inference_service),
):
    body = await request.body()
    text = body.decode("utf-8", errors="ignore")
    if text.startswith("\ufeff"):
        text = text[1:]
    cleaned_text = data_cleaning(text)
    predicted = await run_in_threadpool(inference.predict, cleaned_text)
    return {"predicted_class": predicted}


@app.post("/predict/url", response_model=PredictResponse)
async def predict_url(
    body: URLRequest,
    db: AsyncSession = Depends(get_db),
    inference: InferenceService = Depends(get_inference_service),
):
    url = str(body.url)
    article_id = extract_id(url)

    if not article_id:
        return {"predicted_class": "Некорректный URL"}

    existing_article = await get_article_by_id(db, article_id)
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

    predicted = await run_in_threadpool(inference.predict, final_text)

    await save_article(
        db=db,
        url=article_data["url"],
        article_id=int(article_id),
        predicted_class=predicted,
    )

    return {"predicted_class": predicted}


@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

