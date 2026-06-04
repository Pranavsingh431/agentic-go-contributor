from fastapi import FastAPI
from api.routes import router

app = FastAPI(title="Agentic Go Contributor")
app.include_router(router)
