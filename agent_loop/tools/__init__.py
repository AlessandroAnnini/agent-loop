import importlib.util
import sys
from pathlib import Path

# Directories to scan for tools
BUILTIN_TOOLS_DIR = Path(__file__).parent
USER_TOOLS_DIR = Path.home() / ".config/agent-loop/tools"

TOOLS = []
TOOL_HANDLERS = {}


def load_tools_from_dir(directory):
    if not directory.exists() or not directory.is_dir():
        return []
    tools = []
    for file in directory.iterdir():
        if file.suffix != ".py" or not file.is_file():
            continue
        if file.name == "__init__.py":
            continue
        spec = importlib.util.spec_from_file_location(file.stem, str(file))
        mod = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(mod)
        except Exception as e:
            print(f"[agent-loop] Failed to import {file}: {e}", file=sys.stderr)
            continue
        if hasattr(mod, "tool_definition") and hasattr(mod, "handle_call"):
            tools.append((mod.tool_definition, mod.handle_call))
    return tools


# Load built-in and user tools
all_tools = load_tools_from_dir(BUILTIN_TOOLS_DIR) + load_tools_from_dir(USER_TOOLS_DIR)

for tool_def, handler in all_tools:
    TOOLS.append(tool_def)
    TOOL_HANDLERS[tool_def["name"]] = handler
