from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.predict import router
from app.services import InferenceService


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model")
    app.state.inference_service = InferenceService()
    yield


app = FastAPI(title="Text Classification API", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "healthy"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
