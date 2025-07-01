import subprocess

tool_definition = {
    "name": "file_search",
    "description": (
        "Fast file search based on fuzzy matching against file path. "
        "Use if you know part of the file path but don't know where it's located exactly. "
        "Response will be capped to 10 results. Make your query more specific if need to filter results further."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Fuzzy filename to search for"},
            "explanation": {
                "type": "string",
                "description": "Why the agent is performing this file search and how it helps.",
            },
        },
        "required": ["query", "explanation"],
    },
}


def handle_call(input_data):
    query = input_data["query"]

    try:
        result = subprocess.run(
            ["fdfind", query], capture_output=True, text=True, timeout=10
        )

        if result.returncode not in [0, 1]:  # 0: found, 1: not found
            return {"error": result.stderr.strip(), "exit_code": result.returncode}

        matches = result.stdout.strip().splitlines()[:10]

        return {"query": query, "matches": matches, "exit_code": result.returncode}

    except Exception as e:
        return {"error": f"Execution error: {e}"}
