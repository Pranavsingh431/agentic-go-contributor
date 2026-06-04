import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.runner import run_agent, run_agent_stream

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


def _sse_generator(issue_url: str, repo_url: str):
    """Wrap run_agent_stream events as SSE data frames."""
    for event in run_agent_stream(issue_url, repo_url):
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/run/stream")
def run_stream(req: RunRequest):
    """Stream agent pipeline progress as Server-Sent Events."""
    return StreamingResponse(
        _sse_generator(req.issue_url, req.repo_url),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
