import subprocess

tool_definition = {
    "name": "git",
    "description": "Run Git commands in the current repository",
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": "Arguments for the git command, e.g., 'status', 'log --oneline', 'branch -a'",
            }
        },
        "required": ["args"],
    },
}


def handle_call(input_data):
    args = input_data["args"]
    cmd = ["git"] + args.strip().split()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
    except Exception as e:
        return f"Error executing git command: {e}"
