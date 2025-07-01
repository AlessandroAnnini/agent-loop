import subprocess
import shlex

tool_definition = {
    "name": "grep_search",
    "description": (
        "Search for exact strings or regular expressions using `grep`. "
        "This tool is ideal when the agent knows exactly what to look for (e.g., symbols, patterns, or keywords in files). "
        "Use include/exclude filters to narrow down scope."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Regex or literal pattern to search for.",
            },
            "include_pattern": {
                "type": "string",
                "description": "Glob pattern for files to include, e.g. '*.py'",
            },
            "exclude_pattern": {
                "type": "string",
                "description": "Glob pattern for files to exclude, e.g. '*test*'",
            },
            "case_sensitive": {
                "type": "boolean",
                "description": "Case-sensitive search or not.",
            },
            "explanation": {
                "type": "string",
                "description": "Why the agent is performing this search.",
            },
            "directory": {
                "type": "string",
                "description": "Base directory to search in (default: current directory)",
                "default": ".",
            },
        },
        "required": ["query"],
    },
}


def handle_call(input_data):
    query = input_data["query"]
    include = input_data.get("include_pattern")
    exclude = input_data.get("exclude_pattern")
    case_sensitive = input_data.get("case_sensitive", True)
    directory = input_data.get("directory", ".")

    # Base grep command
    cmd = ["grep", "-r", "--line-number", "--color=never"]

    if not case_sensitive:
        cmd.append("-i")

    if include:
        cmd.extend(["--include", include])

    if exclude:
        cmd.extend(["--exclude", exclude])

    cmd.extend([shlex.quote(query), shlex.quote(directory)])

    try:
        result = subprocess.run(
            " ".join(cmd), shell=True, capture_output=True, text=True, timeout=15
        )
        output = result.stdout.strip()
        if result.returncode == 0 or output:
            return {
                "matches": output.splitlines()[:50],
                "exit_code": result.returncode,
                "stderr": result.stderr,
            }
        else:
            return {
                "matches": [],
                "exit_code": result.returncode,
                "stderr": result.stderr,
            }
    except Exception as e:
        return {"error": f"Execution error: {e}"}
