import sys
import os

# Allow running as: python -m evals.run_eval from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from agent.runner import run_agent

KNOWN_ISSUES = [
    {
        "issue_url": "https://github.com/spf13/cobra/issues/2393",
        "repo_url": "https://github.com/spf13/cobra",
        "expected_files": ["completions.go"],
    },
]


def check_file_match(relevant_files: list, expected_files: list) -> list:
    """Return which expected files appear in the relevant_files list."""
    relevant_basenames = {os.path.basename(f) for f in relevant_files}
    return [e for e in expected_files if e in relevant_basenames]


def run_eval():
    """Run all known issues through the agent and report pass/fail."""
    total = len(KNOWN_ISSUES)
    passed = 0

    for entry in KNOWN_ISSUES:
        issue_url = entry["issue_url"]
        print(f"\n{'='*60}")
        print(f"Evaluating: {issue_url}")

        try:
            result = run_agent(issue_url, entry["repo_url"])
        except Exception as exc:
            print(f"FAIL — agent error: {exc}")
            continue

        relevant = result.get("plan", {}).get("relevant_files", [])
        matched = check_file_match(relevant, entry["expected_files"])

        if matched:
            print(f"PASS — {issue_url} — matched files: {matched}")
            passed += 1
        else:
            print(f"FAIL — {issue_url} — expected {entry['expected_files']}, got {relevant}")

        test_rc = result.get("checks", {}).get("test", {}).get("returncode", -1)
        test_status = "PASS" if test_rc == 0 else "FAIL"
        print(f"go test: {test_status} (returncode={test_rc})")

    print(f"\n{'='*60}")
    print(f"Summary: {passed}/{total} issues passed file identification")


if __name__ == "__main__":
    run_eval()
