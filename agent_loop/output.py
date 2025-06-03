from rich.console import Console
from rich.markdown import Markdown
from typing import Optional
from agent_loop.theme import get_rich_theme

# Create a Rich Console with the loaded theme
_console = Console(theme=get_rich_theme())


def agent_print(
    msg: str, style: Optional[str] = None, simple_text: bool = False
) -> None:
    """
    Print a message using Rich with the given style, or plain print if simple_text is True.
    """
    if simple_text or style is None:
        print(msg)
    else:
        _console.print(msg, style=style)


def agent_reply(msg: str, simple_text: bool = False) -> None:
    if simple_text:
        print(msg)
    else:
        _console.print(Markdown(msg), style="agent.reply")


def agent_tool(msg: str, simple_text: bool = False) -> None:
    agent_print(msg, style="agent.tool", simple_text=simple_text)


def agent_confirm(msg: str, simple_text: bool = False) -> None:
    agent_print(msg, style="agent.confirm", simple_text=simple_text)


def agent_error(msg: str, simple_text: bool = False) -> None:
    agent_print(msg, style="agent.error", simple_text=simple_text)


def agent_info(msg: str, simple_text: bool = False) -> None:
    agent_print(msg, style="agent.info", simple_text=simple_text)
