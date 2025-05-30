import subprocess

tool_definition = {
    "name": "kubectl",
    "description": "Run kubectl commands to interact with a Kubernetes cluster",
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": "Arguments to pass to kubectl (e.g., 'get pods -n default')",
            }
        },
        "required": ["args"],
    },
}


def handle_call(input_data):
    args = input_data["args"]
    cmd = ["kubectl"] + args.strip().split()

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
    except subprocess.TimeoutExpired:
        return "kubectl command timed out."
    except Exception as e:
        return f"Error executing kubectl command: {e}"
