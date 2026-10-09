from pydantic import BaseModel


class EmbedRequest(BaseModel):
    texts: list[str]


class EmbedResponse(BaseModel):
    embeddings: list[list[float]]

class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    text: str