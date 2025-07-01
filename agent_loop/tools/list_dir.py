import os

tool_definition = {
    "name": "list_dir",
    "description": (
        "List the contents of a directory. The quick tool to use for discovery, "
        "before using more targeted tools like semantic search or file reading. "
        "Useful to try to understand the file structure before diving deeper into specific files."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "relative_workspace_path": {
                "type": "string",
                "description": "Path to list contents of, relative to the workspace root.",
            },
            "explanation": {
                "type": "string",
                "description": "Why the agent is listing this directory and how it helps.",
            },
        },
        "required": ["relative_workspace_path"],
    },
}


def handle_call(input_data):
    path = input_data["relative_workspace_path"]

    try:
        entries = os.listdir(path)
        entries_info = []
        for entry in sorted(entries):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                entry_type = "directory"
            elif os.path.isfile(full_path):
                entry_type = "file"
            else:
                entry_type = "other"
            entries_info.append({"name": entry, "type": entry_type})

        return {"path": path, "contents": entries_info}

    except Exception as e:
        return {"error": f"Could not list directory '{path}': {e}"}
