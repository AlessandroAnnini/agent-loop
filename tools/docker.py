import subprocess

tool_definition = {
    "name": "docker",
    "description": "Run Docker CLI commands",
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": "Arguments to pass to the Docker CLI, e.g., 'ps', 'images', 'compose ls'",
            }
        },
        "required": ["args"],
    },
}


def handle_tool_call(input_data):
    args = input_data["args"]
    cmd = ["docker"] + args.strip().split()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
    except Exception as e:
        return f"Error executing docker command: {e}"
