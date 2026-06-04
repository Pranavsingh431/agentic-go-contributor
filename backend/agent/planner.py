import json
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4-5"

SYSTEM_PROMPT = "You are a Go code analysis agent."


def plan(issue: dict, repo_map: dict) -> dict:
    """Call OpenRouter to identify relevant files and draft a fix plan for the issue."""
    file_list = "\n".join(repo_map.get("files", []))
    user_prompt = (
        f"Issue title: {issue['title']}\n\n"
        f"Issue body:\n{issue['body']}\n\n"
        f"Repository .go files:\n{file_list}\n\n"
        "Return ONLY valid JSON in this exact shape:\n"
        '{"relevant_files": ["path/to/file.go"], "plan": "one paragraph describing the fix"}'
    )
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Pranavsingh431/agentic-go-contributor",
    }
    with httpx.Client(timeout=60) as client:
        resp = client.post(OPENROUTER_URL, json=payload, headers=headers)
        resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if the model wraps the JSON
    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {"raw": content}
