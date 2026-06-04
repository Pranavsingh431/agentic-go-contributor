from agent.tools import fetch_issue, clone_repo, map_repo, run_go_checks
from agent.planner import plan
from agent.coder import generate_patch


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
