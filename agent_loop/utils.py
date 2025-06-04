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


def get_ai_temperature() -> float:
    """
    Parse and validate AI temperature from environment variable.
    Returns a float between 0.0 and 2.0, defaulting to 0.7.
    """
    try:
        temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        if not 0.0 <= temperature <= 2.0:
            raise ValueError(
                f"Temperature must be between 0.0 and 2.0, got: {temperature}"
            )
        return temperature
    except ValueError as e:
        if "could not convert" in str(e):
            raise ValueError(
                f"Invalid AI_TEMPERATURE value: {os.getenv('AI_TEMPERATURE')}. Must be a number."
            )
        raise
