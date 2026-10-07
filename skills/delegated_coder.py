import os
import sys
import json
import secrets
import subprocess
from openai import OpenAI

def execute(instruction, target_dir="."):
    workspace = os.path.abspath(target_dir)
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.unorouter.com/v1")
    model = os.getenv("WORKER_MODEL", "deepseek-v4-flash:free")

    # Strip provider prefix if present (e.g. openai/deepseek-v4-flash:free -> deepseek-v4-flash:free)
    if "/" in model:
        model = model.split("/", 1)[1]

    if not api_key:
        return json.dumps({"status": "FAILED", "reason": "OPENAI_API_KEY is not set in .env"})

    # 1. Create isolated Git checkpoint branch
    checkpoint_id = secrets.token_hex(3)
    branch_name = f"hermes/patch-{checkpoint_id}"
    try:
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=workspace, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return json.dumps({"status": "FAILED", "reason": f"Git checkpoint failed: {e.stderr.decode()}"})

    # 2. Call UnoRouter Free Tier
    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = (
        "You are an expert autonomous software engineer. "
        "Analyze the repository, fulfill the instruction accurately, and provide a clear, concise summary."
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ],
            temperature=0.2
        )

        reply = response.choices[0].message.content

        # 3. Check for any Git changes made
        diff_res = subprocess.run(["git", "diff", "HEAD"], cwd=workspace, capture_output=True, text=True)
        diff_text = diff_res.stdout if diff_res.stdout else "No file changes staged."

        return json.dumps({
            "status": "SUCCESS",
            "model_used": model,
            "branch": branch_name,
            "response": reply,
            "git_diff_preview": diff_text[:2000]
        }, indent=2)

    except Exception as ex:
        # Revert branch on error
        subprocess.run(["git", "checkout", "-"], cwd=workspace, capture_output=True)
        return json.dumps({
            "status": "ERROR",
            "model_attempted": model,
            "error": str(ex)
        }, indent=2)

if __name__ == "__main__":
    test_task = sys.argv[1] if len(sys.argv) > 1 else "List repository files"
    print(execute(test_task))
