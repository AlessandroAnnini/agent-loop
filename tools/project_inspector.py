import os

tool_definition = {
    "name": "project_inspector",
    "description": "Inspect the current project directory and preview source files",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to inspect (relative or absolute)",
                "default": ".",
            },
            "max_depth": {
                "type": "integer",
                "description": "Maximum directory depth to walk",
                "default": 2,
            },
            "preview_bytes": {
                "type": "integer",
                "description": "Number of bytes to preview from each file",
                "default": 500,
            },
        },
        "required": [],
    },
}


def handle_tool_call(input_data):
    path = input_data.get("path", ".")
    max_depth = input_data.get("max_depth", 2)
    preview_bytes = input_data.get("preview_bytes", 500)

    output = []

    try:
        for root, dirs, files in os.walk(path):
            depth = os.path.relpath(root, path).count(os.sep)
            if depth > max_depth:
                dirs[:] = []
                continue

            indent = "  " * depth
            output.append(f"{indent}{os.path.basename(root)}/")

            for f in files:
                file_path = os.path.join(root, f)
                output.append(f"{indent}  {f}")
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as fp:
                        content = fp.read(preview_bytes)
                        snippet = content.strip().replace("\n", " ")[:200]
                        output.append(f"{indent}    Preview: {snippet}")
                except Exception as e:
                    output.append(f"{indent}    Error reading file: {e}")
    except Exception as e:
        return f"Error walking project directory: {e}"

    return "\n".join(output)
