import subprocess

tool_definition = {
    "name": "curl",
    "description": "Make HTTP requests using curl",
    "input_schema": {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL to request"},
            "method": {
                "type": "string",
                "description": "HTTP method to use (GET, POST, PUT, etc.)",
                "default": "GET",
            },
            "headers": {
                "type": "string",
                "description": "Optional headers, formatted like 'Key: Value\\nAnother: Header'",
                "default": "",
            },
            "data": {
                "type": "string",
                "description": "Data to send in the request body (for POST, PUT, etc.)",
                "default": "",
            },
        },
        "required": ["url"],
    },
}


def handle_call(input_data):
    url = input_data["url"]
    method = input_data.get("method", "GET").upper()
    headers = input_data.get("headers", "")
    data = input_data.get("data", "")

    cmd = ["curl", "-X", method, url, "-i", "--max-time", "10"]

    if headers:
        for header in headers.strip().splitlines():
            cmd.extend(["-H", header])

    if data:
        cmd.extend(["--data", data])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}\nEXIT CODE: {result.returncode}"
    except Exception as e:
        return f"Error executing curl: {e}"
