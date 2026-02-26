from pydantic import BaseModel, HttpUrl


class TextRequest(BaseModel):
    text: str


class URLRequest(BaseModel):
    url: HttpUrl


class PredictResponse(BaseModel):
    predicted_class: str
