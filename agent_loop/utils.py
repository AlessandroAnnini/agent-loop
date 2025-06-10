import os
import importlib.resources


def load_system_prompt() -> str:
    # First try ~/.config/agent-loop/SYSTEM_PROMPT.txt
    user_path = os.path.expanduser("~/.config/agent-loop/SYSTEM_PROMPT.txt")
    if os.path.exists(user_path):
        with open(user_path, "r", encoding="utf-8") as f:
            return f.read()

    # Fallback to packaged version
    try:
        with (
            importlib.resources.files("agent_loop")
            .joinpath("SYSTEM_PROMPT.txt")
            .open("r", encoding="utf-8") as f
        ):
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            "SYSTEM_PROMPT.txt not found in package or config directory."
        )
