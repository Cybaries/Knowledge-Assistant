from fastapi import FastAPI

app = FastAPI(title="Knowledge Assistant AI Service")


@app.get("/health")
def health():
    return {"status": "ok"}

from embeddings import embed_texts
from fastapi import FastAPI
from schemas import EmbedRequest, EmbedResponse

app = FastAPI(title="Knowledge Assistant AI Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    embeddings = embed_texts(request.texts)

    return EmbedResponse(embeddings=embeddings)