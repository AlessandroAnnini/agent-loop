import json

tool_definition = {
    "name": "json",
    "description": "Validate and format JSON. Supports pretty-printing, minifying, and sorting keys.",
    "input_schema": {
        "type": "object",
        "properties": {
            "json_string": {
                "type": "string",
                "description": "The raw JSON string to validate and format",
            },
            "mode": {
                "type": "string",
                "description": "Choose 'pretty', 'minify', or 'validate'",
                "enum": ["pretty", "minify", "validate"],
            },
            "sort_keys": {
                "type": "boolean",
                "description": "Sort JSON object keys alphabetically (applies to pretty or minify)",
                "default": False,
            },
        },
        "required": ["json_string", "mode"],
    },
}


def handle_tool_call(input_data):
    raw = input_data["json_string"]
    mode = input_data["mode"]
    sort_keys = input_data.get("sort_keys", False)

    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as e:
        return f"❌ Invalid JSON: {e}"

    if mode == "validate":
        return "✅ JSON is valid."

    if mode == "pretty":
        return json.dumps(obj, indent=2, sort_keys=sort_keys)

    if mode == "minify":
        return json.dumps(obj, separators=(",", ":"), sort_keys=sort_keys)

    return "⚠️ Unknown mode. Please use 'pretty', 'minify', or 'validate'."
