from fastapi import FastAPI

app = FastAPI(title="Agentic Go Contributor")


@app.get("/health")
def health_check():
    return {"status": "ok"}
