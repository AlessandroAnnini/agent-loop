import subprocess

tool_definition = {
    "name": "codebase_search",
    "description": (
        "Find snippets of code from the codebase most relevant to the search query. "
        "This is a semantic search tool, so the query should ask for something semantically matching what is needed. "
        "Use target_directories to scope the search. Reuse the user's exact query unless there's a clear reason not to."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query to find relevant code. Reuse the user's exact wording.",
            },
            "target_directories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Glob patterns for directories to search over.",
            },
            "explanation": {
                "type": "string",
                "description": "Why the agent is performing this semantic search and how it helps.",
            },
        },
        "required": ["query"],
    },
}


def handle_call(input_data):
    query = input_data["query"]
    target_dirs = input_data.get("target_directories", ["."])

    try:
        args = [
            "semantic-code-search",
            "--query",
            query,
        ]

        for directory in target_dirs:
            args.extend(["--dir", directory])

        result = subprocess.run(args, capture_output=True, text=True, timeout=20)

        if result.returncode != 0:
            return {"error": result.stderr.strip(), "exit_code": result.returncode}

        return {
            "query": query,
            "output": result.stdout.strip(),
            "exit_code": result.returncode,
        }

    except Exception as e:
        return {"error": f"Execution error: {e}"}
