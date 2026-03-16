from pydantic import BaseModel, HttpUrl


class URLRequest(BaseModel):
    url: HttpUrl


class PredictResponse(BaseModel):
    predicted_class: str
