import os

from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "all-MiniLM-L6-v2",
)

_model = SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]) -> list[list[float]]:
    embeddings = _model.encode(texts)

    return embeddings.tolist()