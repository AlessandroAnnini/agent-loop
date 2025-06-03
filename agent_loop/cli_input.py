from agent_loop.exceptions import GracefulExit
import sys
import termios
import tty
from typing import Optional


def get_user_command(simple_text: bool) -> Optional[str]:
    """
    Read a user command from the terminal in raw mode, supporting CTRL+Q for quit and CTRL+C for prompt interruption.
    Returns the raw command string (no formatting or time), or None if the user wants to quit.
    """
    print("\ndev@agent-loop:~$ ", end="", flush=True)
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        chars: list[str] = []
        while True:
            ch = sys.stdin.read(1)
            if ch == "\x11":  # CTRL+Q
                return None
            if ch in ("\r", "\n"):
                print()
                break
            if ch == "\x03":  # CTRL+C
                print("\n[Interrupted] Returning to prompt. (Press CTRL+Q to quit)")
                return get_user_command(simple_text)
            if ch == "\x7f":  # Backspace
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            chars.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
        x = "".join(chars)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    if x.lower() in {"exit", "quit"}:
        return None
    return x
