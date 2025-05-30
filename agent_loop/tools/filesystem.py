import os

tool_definition = {
    "name": "filesystem",
    "description": "Read, create, update, append, delete files, or modify specific lines. Only supports UTF-8 encoded text files.",
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "description": "File operation to perform",
                "enum": [
                    "create",
                    "read",
                    "update",
                    "append",
                    "delete",
                    "insert_line",
                    "delete_line",
                ],
            },
            "path": {"type": "string", "description": "Path to the file"},
            "content": {
                "type": "string",
                "description": "Content for create, update, append, insert_line",
                "default": "",
            },
            "line_number": {
                "type": "integer",
                "description": "Line number (0-based) for insert_line or delete_line",
                "default": None,
            },
        },
        "required": ["operation", "path"],
    },
}


def handle_call(input_data):
    operation = input_data["operation"]
    path = input_data["path"]
    content = input_data.get("content", "")
    line_number = input_data.get("line_number")

    try:
        if operation == "create":
            if os.path.exists(path):
                return f"❌ File already exists: {path}"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Created file: {path}"

        elif operation == "read":
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            with open(path, "r", encoding="utf-8") as f:
                return f"📄 Content of {path}:\n\n{f.read()}"

        elif operation == "update":
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"✅ File updated: {path}"

        elif operation == "append":
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            return f"✅ Appended to file: {path}"

        elif operation == "delete":
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            os.remove(path)
            return f"🗑️ Deleted file: {path}"

        elif operation == "insert_line":
            if line_number is None:
                return "❌ Missing 'line_number' for insert_line"
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if line_number < 0 or line_number > len(lines):
                return f"❌ Invalid line number: {line_number}"
            lines.insert(line_number, content + "\n")
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return f"✅ Inserted line at {line_number} in {path}"

        elif operation == "delete_line":
            if line_number is None:
                return "❌ Missing 'line_number' for delete_line"
            if not os.path.exists(path):
                return f"❌ File does not exist: {path}"
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if line_number < 0 or line_number >= len(lines):
                return f"❌ Invalid line number: {line_number}"
            removed = lines.pop(line_number)
            with open(path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return f"🗑️ Deleted line {line_number} from {path}: {removed.strip()}"

        else:
            return f"❌ Unsupported operation: {operation}"

    except Exception as e:
        return f"⚠️ Error performing filesystem operation: {e}"
