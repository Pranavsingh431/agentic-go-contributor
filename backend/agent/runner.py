from .tools import fetch_issue, clone_repo, map_repo, run_go_checks
from .planner import plan
from .coder import generate_patch


def run_agent_stream(issue_url: str, repo_url: str):
    """Generator that yields SSE-ready dicts after each pipeline step."""

    def event(step, label, status, data=None):
        e = {"step": step, "label": label, "status": status}
        if data is not None:
            e["data"] = data
        return e

    # Step 1 — fetch issue
    yield event(1, "Fetching issue", "running")
    try:
        issue = fetch_issue(issue_url)
    except Exception as exc:
        yield event(1, "Fetching issue", "error", {"error": str(exc)})
        return
    yield event(1, "Fetching issue", "done", issue)

    # Step 2 — clone repo
    yield event(2, "Cloning repository", "running")
    try:
        repo_path = clone_repo(repo_url)
    except Exception as exc:
        yield event(2, "Cloning repository", "error", {"error": str(exc)})
        return
    yield event(2, "Cloning repository", "done", {"repo_path": repo_path})

    # Step 3 — map repo
    yield event(3, "Mapping repository", "running")
    repo_map = map_repo(repo_path)
    yield event(3, "Mapping repository", "done", repo_map)

    # Step 4 — plan
    yield event(4, "Planning fix", "running")
    try:
        plan_result = plan(issue, repo_map)
    except Exception as exc:
        yield event(4, "Planning fix", "error", {"error": str(exc)})
        return
    yield event(4, "Planning fix", "done", plan_result)

    # Step 5 — generate patch
    relevant_files = plan_result.get("relevant_files", [])
    yield event(5, "Generating patch", "running")
    try:
        patch_result = generate_patch(issue, relevant_files, repo_path)
    except Exception as exc:
        yield event(5, "Generating patch", "error", {"error": str(exc)})
        return
    yield event(5, "Generating patch", "done", patch_result)

    # Step 6 — go checks
    yield event(6, "Running Go checks", "running")
    checks = run_go_checks(repo_path)
    yield event(6, "Running Go checks", "done", checks)

    # Final summary event
    full_result = {
        "issue": issue,
        "repo_map": repo_map,
        "plan": plan_result,
        "patch": patch_result.get("patch"),
        "pr_title": patch_result.get("pr_title"),
        "pr_body": patch_result.get("pr_body"),
        "checks": checks,
    }
    yield event(6, "Complete", "done", full_result)


def run_agent(issue_url: str, repo_url: str) -> dict:
    """Orchestrate the full agent pipeline from issue fetch to patch generation."""
    print("[STEP 1/6] Fetching issue...")
    issue = fetch_issue(issue_url)

    print("[STEP 2/6] Cloning repository...")
    repo_path = clone_repo(repo_url)

    print("[STEP 3/6] Mapping repository...")
    repo_map = map_repo(repo_path)

    print("[STEP 4/6] Planning fix...")
    plan_result = plan(issue, repo_map)

    relevant_files = plan_result.get("relevant_files", [])
    print(f"[STEP 5/6] Generating patch for {len(relevant_files)} file(s)...")
    patch_result = generate_patch(issue, relevant_files, repo_path)

    print("[STEP 6/6] Running Go checks...")
    checks = run_go_checks(repo_path)

    return {
        "issue": issue,
        "repo_map": repo_map,
        "plan": plan_result,
        "patch": patch_result.get("patch"),
        "pr_title": patch_result.get("pr_title"),
        "pr_body": patch_result.get("pr_body"),
        "checks": checks,
    }
