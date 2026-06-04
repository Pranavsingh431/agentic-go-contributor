from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.runner import run_agent

router = APIRouter()


class RunRequest(BaseModel):
    issue_url: str
    repo_url: str


@router.get("/health")
def health():
    """Return service health status."""
    return {"status": "ok"}


@router.post("/run")
def run(req: RunRequest):
    """Trigger the agent pipeline for a given issue URL and repo URL."""
    try:
        result = run_agent(req.issue_url, req.repo_url)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return result
