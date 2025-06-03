import os
import json
from rich.theme import Theme
from typing import Dict

DEFAULT_THEME = {
    "agent.reply": "bold cyan",
    "agent.tool": "bold magenta",
    "agent.confirm": "bold yellow",
    "agent.error": "bold red",
    "agent.info": "dim white",
}

CONFIG_PATH = os.path.expanduser("~/.config/agent-loop/theme.json")


def load_theme_from_file(path: str = CONFIG_PATH) -> Dict[str, str]:
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(
                "Theme JSON must be a dict of style names to style strings."
            )
        return data
    except Exception:
        return DEFAULT_THEME


def get_rich_theme() -> Theme:
    """Return a Rich Theme object loaded from config or default."""
    theme_dict = load_theme_from_file()
    return Theme(theme_dict)
