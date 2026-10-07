import subprocess
import json
import os
import secrets

def execute(instruction, target_dir="."):
    workspace = os.path.abspath(target_dir)
    model = os.getenv("WORKER_MODEL", "openrouter/deepseek/deepseek-v4-flash")

    crg_dir = os.path.join(workspace, ".crg")
    if not os.path.exists(crg_dir):
        subprocess.run(["npx", "code-review-graph", "index", workspace], capture_output=True, cwd=workspace)

    checkpoint_id = secrets.token_hex(3)
    branch_name = f"hermes/patch-{checkpoint_id}"

    try:
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=workspace, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return json.dumps({"status": "FAILED", "reason": f"Git checkpoint failed: {e.stderr.decode()}"})

    env = os.environ.copy()
    env["MODEL"] = model

    cmd = ["npx", "opencode", "run", "--non-interactive", "--prompt", instruction]

    try:
        res = subprocess.run(cmd, cwd=workspace, env=env, capture_output=True, text=True, timeout=900)
        diff_res = subprocess.run(["git", "diff", "HEAD~1"], cwd=workspace, capture_output=True, text=True)
        diff_text = diff_res.stdout if diff_res.stdout else "No git commit created or changes unstaged."

        if res.returncode == 0:
            return json.dumps({
                "status": "SUCCESS",
                "branch": branch_name,
                "summary": "Task completed successfully.",
                "git_diff_preview": diff_text[:3000]
            }, indent=2)
        else:
            subprocess.run(["git", "checkout", "-"], cwd=workspace, capture_output=True)
            return json.dumps({
                "status": "FAILED",
                "branch_reverted": True,
                "error_log": res.stderr[-1000:] if res.stderr else res.stdout[-1000:]
            }, indent=2)

    except Exception as ex:
        subprocess.run(["git", "checkout", "-"], cwd=workspace, capture_output=True)
        return json.dumps({"status": "ERROR", "exception": str(ex)})

if __name__ == "__main__":
    import sys
    test_task = sys.argv[1] if len(sys.argv) > 1 else "Check directory and report structure"
    print(execute(test_task))
