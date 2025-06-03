# 🌟 Creating New Tools for Agent Loop

Welcome! This guide will show you how to create your own tools for Agent Loop using **functional programming** principles. Tools are now **auto-discovered**—just drop your `.py` file in the right folder and you're ready to go!

---

## 🚨 Important Policy for Custom Tools

> **Custom tools (in `~/.config/agent-loop/tools/`) must NOT use their own external dependencies.**
>
> - Only use the Python standard library and what is already available in Agent Loop.
> - Do NOT import or require packages that are not already installed.
> - **Environment variables are allowed** for configuration, secrets, or API keys.
> - This keeps your environment stable and avoids dependency issues.

> **Built-in tools** (in `agent_loop/tools/`) may use dependencies, as these are managed centrally.

---

## 🧩 What is a Tool?

A tool is a Python module with:

- A **tool definition**: describes the tool, its purpose, and its input schema
- A **handler function**: a pure function that processes input and returns output

---

## 🚀 Quick Start: Minimal Example

Create a file named `hello.py` in either:

- Built-in tools: `agent_loop/tools/`
- User tools: `~/.config/agent-loop/tools/`

```python
# hello.py

tool_definition = {
    "name": "hello",
    "description": "Returns a friendly greeting.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Name to greet"}
        },
        "required": ["name"],
    },
}

def handle_call(input_data):
    name = input_data.get("name", "world")
    return f"Hello, {name}!"
```

That's it! Your tool will be **automatically loaded** the next time Agent Loop starts.

---

## 🏗️ Tool Structure

### 1. Tool Definition

A dictionary describing:

- `name`: Unique tool name (string)
- `description`: What the tool does (string)
- `input_schema`: JSON Schema for input validation (dict)

### 2. Handler Function

A pure function:

- Signature: `def handle_call(input_data): ...`
- Input: `input_data` (dict, validated by your schema)
- Output: String (or structured data, if needed)

---

## 📦 Where to Put Your Tool

- **Built-in**: `agent_loop/tools/` (for core tools)
- **User**: `~/.config/agent-loop/tools/` (for your custom tools)

> **Tip:** No need to edit `__init__.py` or register your tool. Just drop the file in the folder!

---

## 📝 Input Schema Guidelines

- Use [JSON Schema](https://json-schema.org/) for clarity and validation
- Mark required parameters
- Provide helpful descriptions

**Example:**

```python
"input_schema": {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["create", "read", "update", "delete"],
            "description": "The operation to perform"
        },
        "target": {
            "type": "string",
            "description": "The target resource"
        },
        "options": {
            "type": "object",
            "properties": {
                "recursive": {"type": "boolean", "description": "Apply recursively?"},
                "format": {"type": "string", "enum": ["json", "yaml", "text"], "description": "Output format"}
            }
        }
    },
    "required": ["operation", "target"]
}
```

---

## 🧑‍💻 Handler Function Best Practices

- **Pure**: No side effects, same output for same input
- **Validate**: Check for required parameters
- **Error Handling**: Return clear, helpful error messages
- **Return**: Prefer simple, readable output

**Example:**

```python
def handle_call(input_data):
    try:
        if "required_param" not in input_data:
            return "❌ Missing required parameter: required_param"
        # ... your logic ...
        return f"✅ Success: did something with {input_data['required_param']}"
    except Exception as e:
        return f"❌ Error: {e}"
```

---

## 🔐 Environment Variables

- Use environment variables for configuration, secrets, or API keys.
- You may use [python-dotenv](https://pypi.org/project/python-dotenv/) **if it is already available** in Agent Loop.
- Do **not** require users to install new packages for your custom tool.

**Example:**

```python
import os
API_KEY = os.getenv("MY_API_KEY")

def handle_call(input_data):
    if not API_KEY:
        return "❌ Missing MY_API_KEY environment variable"
    # ... your logic ...
```

---

## 🧪 Testing Your Tool

- Test with valid and invalid inputs
- Check error handling
- Try edge cases

---

## 🌈 Best Practices

- **Keep it simple**: One tool, one job
- **Document**: Clear descriptions help users and AI
- **Validate**: Always check inputs
- **Handle errors**: Be user-friendly
- **Functional style**: Pure functions, no side effects
- **Secure secrets**: Use environment variables
- **No extra dependencies**: Custom tools must not require new packages

---

## 🏁 Recap: How to Add a Tool

1. **Write** your tool as a `.py` file with `tool_definition` and `handle_call`
2. **Place** it in `agent_loop/tools/` or `~/.config/agent-loop/tools/`
3. **Restart** Agent Loop—your tool is ready!

---

## 📚 Example: Weather Tool (Built-in Only)

> **Note:** This example uses `requests` and is only valid for built-in tools. Custom tools must not use extra dependencies.

```python
# weather.py (for built-in tools only)
import os
import requests
from dotenv import load_dotenv
load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

tool_definition = {
    "name": "weather",
    "description": "Get current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {"type": "string", "description": "City name"},
            "units": {"type": "string", "enum": ["metric", "imperial"], "description": "Units"}
        },
        "required": ["location"]
    }
}

def handle_call(input_data):
    if not WEATHER_API_KEY:
        return "❌ Missing WEATHER_API_KEY"
    location = input_data["location"]
    units = input_data.get("units", "metric")
    try:
        resp = requests.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": WEATHER_API_KEY, "q": location, "units": units},
            timeout=10
        )
        if resp.status_code != 200:
            return f"❌ API Error: {resp.status_code} - {resp.text}"
        data = resp.json()
        temp = data["current"]["temp_c"] if units == "metric" else data["current"]["temp_f"]
        cond = data["current"]["condition"]["text"]
        return f"Weather in {location}: {cond}, {temp}°{'C' if units == 'metric' else 'F'}"
    except Exception as e:
        return f"❌ Error: {e}"
```

---

> **✨ That's it!**
>
> Your tool is now part of Agent Loop. Build, test, and share your creations!
