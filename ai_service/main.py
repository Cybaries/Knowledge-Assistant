from embeddings import embed_texts
from fastapi import FastAPI
from llm import generate
from schemas import (EmbedRequest, EmbedResponse, GenerateRequest,
                     GenerateResponse)

app = FastAPI(title="Knowledge Assistant AI Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest):
    embeddings = embed_texts(request.texts)
    return EmbedResponse(embeddings=embeddings)


@app.post("/generate", response_model=GenerateResponse)
def generate_text(request: GenerateRequest):
    text = generate(request.prompt)
    return GenerateResponse(text=text)