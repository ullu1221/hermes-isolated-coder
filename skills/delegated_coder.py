import os
import sys
import json
import re
import secrets
import subprocess
from openai import OpenAI

def get_workspace_tree(root="."):
    tree = []
    ignore_dirs = {".git", ".venv", "node_modules", "__pycache__", ".crg"}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for f in filenames:
            rel = os.path.relpath(os.path.join(dirpath, f), root)
            tree.append(rel)
    return sorted(tree)

def read_file(path, workspace="."):
    target = os.path.abspath(os.path.join(workspace, path))
    if not target.startswith(os.path.abspath(workspace)):
        return "Error: Path traversal detected."
    try:
        with open(target, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path, content, workspace="."):
    target = os.path.abspath(os.path.join(workspace, path))
    if not target.startswith(os.path.abspath(workspace)):
        return "Error: Path traversal detected."
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def run_shell(command, workspace="."):
    try:
        res = subprocess.run(command, shell=True, cwd=workspace, capture_output=True, text=True, timeout=60)
        return (res.stdout + res.stderr)[:2000] if (res.stdout or res.stderr) else "Command completed (no output)."
    except Exception as e:
        return f"Command execution error: {e}"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read file contents in workspace",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite file in workspace",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run shell command in workspace",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    }
]

def auto_save_markdown_blocks(text, workspace="."):
    pattern = r"(?:`|\*\*|\#\s*)([a-zA-Z0-9_\-\.\/]+\.[a-zA-Z0-9]+)(?:`|\*\*|\n)?[\s\S]*?```(?:[a-zA-Z0-9_\-]+)?\n([\s\S]*?)```"
    matches = re.findall(pattern, text)
    saved = []
    for filename, code in matches:
        if not filename.startswith("."):
            write_file(filename.strip(), code, workspace)
            saved.append(filename.strip())
    return saved

def execute(instruction, target_dir="."):
    workspace = os.path.abspath(target_dir)
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.unorouter.com/v1")
    model = os.getenv("WORKER_MODEL", "openrouter/free")

    if not api_key:
        return json.dumps({"status": "FAILED", "reason": "OPENAI_API_KEY not set in .env"})

    # 1. Clean Git checkpoint branched from master
    checkpoint_id = secrets.token_hex(3)
    branch_name = f"hermes/patch-{checkpoint_id}"
    try:
        subprocess.run(["git", "checkout", "master"], cwd=workspace, check=True, capture_output=True)
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=workspace, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        return json.dumps({"status": "FAILED", "reason": f"Git checkout failed: {e.stderr.decode()}"})

    # 2. Preload workspace structure
    file_tree = get_workspace_tree(workspace)
    system_prompt = (
        "You are an autonomous senior software engineer working in a git repository.\n"
        "Files in workspace:\n" + "\n".join(f"- {f}" for f in file_tree) + "\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Whenever creating or modifying files, you MUST invoke 'write_file'.\n"
        "2. To inspect code, use 'read_file'.\n"
        "3. Always run tests using 'run_shell' before finishing."
    )

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        max_retries=0,
        timeout=45.0,
        default_headers={"HTTP-Referer": "https://localhost", "X-Title": "Hermes-Coder"}
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instruction}
    ]

    try:
        final_reply = ""
        tools_invoked = False

        for _ in range(8):
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.1
            )
            msg = response.choices[0].message
            messages.append(msg)

            if not msg.tool_calls:
                final_reply = msg.content or "(Task finished)"
                break

            tools_invoked = True
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}

                if fn_name == "read_file":
                    result = read_file(args.get("path", ""), workspace)
                elif fn_name == "write_file":
                    result = write_file(args.get("path", ""), args.get("content", ""), workspace)
                elif fn_name == "run_shell":
                    result = run_shell(args.get("command", ""), workspace)
                else:
                    result = f"Unknown tool: {fn_name}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": str(result)
                })

        # Safe extraction if loop ended on a tool turn
        if not final_reply:
            last = messages[-1]
            final_reply = last.get("content") if isinstance(last, dict) else getattr(last, "content", "(Task finished)")

        # Fallback for models outputting raw markdown code blocks
        if not tools_invoked and ("```" in final_reply):
            auto_save_markdown_blocks(final_reply, workspace)

        # 3. Stage changes to capture new and modified files
        subprocess.run(["git", "add", "-A"], cwd=workspace, capture_output=True)
        diff_res = subprocess.run(["git", "diff", "--staged", "HEAD"], cwd=workspace, capture_output=True, text=True)
        diff_text = diff_res.stdout if diff_res.stdout else "No file changes detected."

        return json.dumps({
            "status": "SUCCESS",
            "model": model,
            "branch": branch_name,
            "response": final_reply,
            "git_diff_preview": diff_text[:2500]
        }, indent=2)

    except Exception as ex:
        subprocess.run(["git", "checkout", "master"], cwd=workspace, capture_output=True)
        return json.dumps({
            "status": "ERROR",
            "details": str(ex)
        }, indent=2)

if __name__ == "__main__":
    test_task = sys.argv[1] if len(sys.argv) > 1 else "List repository files"
    print(execute(test_task))
