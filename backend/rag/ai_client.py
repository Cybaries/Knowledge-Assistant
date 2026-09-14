import os

import httpx


class AIServiceError(Exception):
    """Raised when the AI service cannot generate embeddings."""


def get_embeddings(texts: list[str]) -> list[list[float]]:
    base_url = os.getenv("AI_SERVICE_URL", "http://ai_service:8001")
    url = f"{base_url}/embed"

    try:
        response = httpx.post(
            url,
            json={"texts": texts},
            timeout=120.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise AIServiceError("Failed to generate embeddings.") from exc

    data = response.json()

    return data["embeddings"]