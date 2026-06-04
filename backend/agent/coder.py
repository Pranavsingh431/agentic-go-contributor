import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "anthropic/claude-sonnet-4-5"

SYSTEM_PROMPT = (
    "You are a Go engineer. Return ONLY a unified diff in standard patch format.\n"
    "No explanation. No markdown. No backticks. No prose before or after.\n"
    "Start your response with --- and end with the last line of the diff."
)
MAX_FILES = 5
MAX_LINES = 300


def _read_file(repo_path: str, rel_path: str) -> str:
    """Read a file from the repo, capping at MAX_LINES lines."""
    full = Path(repo_path) / rel_path
    if not full.exists():
        return f"# file not found: {rel_path}"
    lines = full.read_text(errors="replace").splitlines()[:MAX_LINES]
    return "\n".join(lines)


def generate_patch(issue: dict, relevant_files: list, repo_path: str) -> dict:
    """Call OpenRouter with issue details and file contents, return patch + PR metadata."""
    files_block = ""
    for rel in relevant_files[:MAX_FILES]:
        content = _read_file(repo_path, rel)
        files_block += f"\n--- {rel} ---\n{content}\n"

    user_prompt = (
        f"Issue #{issue['number']}: {issue['title']}\n\n"
        f"{issue['body']}\n\n"
        f"Relevant files:\n{files_block}\n\n"
        "Produce a unified diff that fixes the issue. "
        "After the diff, on separate lines write:\n"
        "PR_TITLE: <one line>\n"
        "PR_BODY: <two to four sentences>"
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
    with httpx.Client(timeout=120) as client:
        resp = client.post(OPENROUTER_URL, json=payload, headers=headers)
        resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]
    return _parse_response(raw)


def _parse_response(raw: str) -> dict:
    """Split the model response into patch, PR title, and PR body."""
    pr_title, pr_body, patch_lines = "", "", []
    for line in raw.splitlines():
        if line.startswith("PR_TITLE:"):
            pr_title = line.removeprefix("PR_TITLE:").strip()
        elif line.startswith("PR_BODY:"):
            pr_body = line.removeprefix("PR_BODY:").strip()
        else:
            patch_lines.append(line)
    return {
        "patch": "\n".join(patch_lines).strip(),
        "pr_title": pr_title,
        "pr_body": pr_body,
    }
