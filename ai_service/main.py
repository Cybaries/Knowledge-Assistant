from fastapi import FastAPI

app = FastAPI(title="Knowledge Assistant AI Service")


@app.get("/health")
def health():
    return {"status": "ok"}