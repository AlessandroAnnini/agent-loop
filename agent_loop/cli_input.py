import sys
import readline
import signal
from typing import Optional


class InterruptHandler:
    """Handle CTRL+C during input without exiting"""

    def __init__(self):
        self.interrupted = False

    def __enter__(self):
        self.old_handler = signal.signal(signal.SIGINT, self._handle_interrupt)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.signal(signal.SIGINT, self.old_handler)

    def _handle_interrupt(self, signum, frame):
        self.interrupted = True


def get_user_command(simple_text: bool) -> Optional[str]:
    """
    Read a user command from the terminal using readline for proper editing support.
    Supports:
    - Arrow keys for navigation and history
    - Proper backspace/delete across line wraps
    - CTRL+C for prompt interruption (returns to prompt)
    - CTRL+D or typing 'exit'/'quit' to quit

    Returns the command string, or None if the user wants to quit.
    """
    # Configure readline for better editing experience
    readline.parse_and_bind("tab: complete")
    readline.parse_and_bind("set editing-mode emacs")

    while True:
        try:
            with InterruptHandler() as handler:
                try:
                    user_input = input("dev@agent-loop:~$ ")
                except EOFError:
                    return None

                # Check if CTRL+C was pressed during input
                if handler.interrupted:
                    print("[Interrupted] Returning to prompt. (Press CTRL+D to quit)")
                    continue

                # Handle quit commands
                if user_input.lower().strip() in {"exit", "quit"}:
                    return None

                return user_input.strip()

        except KeyboardInterrupt:
            print("\n[Interrupted] Returning to prompt. (Press CTRL+D to quit)")
            continue
        except Exception as e:
            print(f"\nInput error: {e}")
            continue
