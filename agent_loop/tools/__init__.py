import importlib.util
import sys
from pathlib import Path

# Directories to scan for tools
BUILTIN_TOOLS_DIR = Path(__file__).parent
USER_TOOLS_DIR = Path.home() / ".config/agent-loop/tools"

TOOLS = []
TOOL_HANDLERS = {}
CUSTOM_TOOLS = []  # Track custom tools for display


def load_tools_from_dir(directory, is_custom=False):
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
            tool_info = {
                "definition": mod.tool_definition,
                "handler": mod.handle_call,
                "file_name": file.name,
                "is_custom": is_custom,
            }

            # print file name
            print(f"[agent-loop] Loaded tool: {file.name}")

            tools.append(tool_info)
    return tools


def display_custom_tools():
    """Display loaded custom tools during startup"""
    if not CUSTOM_TOOLS:
        return

    print(
        f"\n🔧 [Custom Tools] Loaded {len(CUSTOM_TOOLS)} custom tool(s) from ~/.config/agent-loop/tools:"
    )
    for tool in CUSTOM_TOOLS:
        tool_def = tool["definition"]
        description = tool_def.get("description", "No description")
        # Truncate long descriptions
        if len(description) > 60:
            description = description[:57] + "..."
        print(f"  • {tool_def['name']} ({tool['file_name']}) - {description}")


# Load built-in and user tools
builtin_tools = load_tools_from_dir(BUILTIN_TOOLS_DIR, is_custom=False)
custom_tools = load_tools_from_dir(USER_TOOLS_DIR, is_custom=True)

# Store custom tools for display
CUSTOM_TOOLS = custom_tools.copy()

# Register all tools
all_tools = builtin_tools + custom_tools
for tool_info in all_tools:
    tool_def = tool_info["definition"]
    handler = tool_info["handler"]
    TOOLS.append(tool_def)
    TOOL_HANDLERS[tool_def["name"]] = handler
