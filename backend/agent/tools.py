import os
import subprocess
import tempfile
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def fetch_issue(issue_url: str) -> dict:
    """Fetch a GitHub issue and return title, body, number, and labels."""
    # e.g. https://github.com/owner/repo/issues/123
    parts = issue_url.rstrip("/").split("/")
    owner, repo, number = parts[-4], parts[-3], parts[-1]
    api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    with httpx.Client(timeout=30) as client:
        resp = client.get(api_url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
    return {
        "title": data.get("title", ""),
        "body": data.get("body", "") or "",
        "number": data.get("number"),
        "labels": [lbl["name"] for lbl in data.get("labels", [])],
    }


def clone_repo(repo_url: str, dest: str = "") -> str:
    """Clone a git repository into a temp directory and return its path."""
    target = dest if dest else tempfile.mkdtemp(prefix="agc_")
    subprocess.run(
        ["git", "clone", "--depth=1", repo_url, target],
        check=True,
        capture_output=True,
    )
    return target


def map_repo(repo_path: str) -> dict:
    """Walk a repo directory and return relative paths of all .go files."""
    root = Path(repo_path)
    files = []
    for p in root.rglob("*.go"):
        rel = p.relative_to(root)
        parts = rel.parts
        if "vendor" in parts or "testdata" in parts:
            continue
        files.append(str(rel))
    return {"files": sorted(files)}


def run_go_checks(repo_path: str) -> dict:
    """Run go vet and go test in the repo, returning stdout and return codes."""
    def _run(cmd: list) -> dict:
        try:
            result = subprocess.run(
                cmd,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return {"stdout": result.stdout + result.stderr, "returncode": result.returncode}
        except subprocess.TimeoutExpired:
            return {"stdout": "timeout after 60s", "returncode": -1}
        except Exception as exc:
            return {"stdout": str(exc), "returncode": -1}

    return {
        "vet": _run(["go", "vet", "./..."]),
        "test": _run(["go", "test", "./..."]),
    }
