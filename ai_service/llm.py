import os

import httpx


def generate(prompt: str) -> str:
    ollama_url = os.getenv(
        "OLLAMA_URL",
        "http://ollama:11434",
    )
    model = os.getenv("OLLAMA_MODEL", "llama3.2:1b-smallctx")

    try:
        response = httpx.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=300.0,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise RuntimeError("Failed to generate text with Ollama.") from exc

    return response.json()["response"]
