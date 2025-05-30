import subprocess

tool_definition = {
    "name": "http",
    "description": "Make HTTP requests using HTTPie (`http` CLI). Easier JSON and header handling than curl.",
    "input_schema": {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "description": "HTTP method (GET, POST, PUT, DELETE, etc.)",
            },
            "url": {"type": "string", "description": "Target URL"},
            "headers": {
                "type": "string",
                "description": "Optional headers in 'Key:Value\\nKey2:Value2' format",
                "default": "",
            },
            "body": {
                "type": "string",
                "description": "Optional request body (JSON string or key=value pairs)",
                "default": "",
            },
        },
        "required": ["method", "url"],
    },
}


def handle_call(input_data):
    method = input_data["method"].upper()
    url = input_data["url"]
    headers = input_data.get("headers", "")
    body = input_data.get("body", "")

    cmd = ["http", method, url, "--print=hb"]

    if headers:
        for line in headers.strip().splitlines():
            if ":" in line:
                cmd.append(f"{line.strip()}")

    if body:
        # Assume it's either JSON or form-like string
        if body.strip().startswith("{"):
            cmd.append(f"'{body.strip()}'")  # raw JSON
        else:
            for part in body.strip().splitlines():
                cmd.append(part.strip())

    try:
        result = subprocess.run(
            " ".join(cmd), shell=True, capture_output=True, text=True, timeout=15
        )
        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"EXIT CODE: {result.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "HTTPie command timed out."
    except Exception as e:
        return f"Error executing HTTPie command: {e}"
