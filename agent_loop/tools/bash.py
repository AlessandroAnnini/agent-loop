import subprocess

tool_definition = {
    "name": "bash",
    "description": "Execute bash commands",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Shell command to execute"},
        },
        "required": ["command"],
    },
}


def handle_call(input_data):
    command = input_data["command"]
    try:
        result = subprocess.run(
            ["bash", "-c", command], capture_output=True, text=True, timeout=10
        )
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
    except Exception as e:
        return f"Error executing bash: {e}"
