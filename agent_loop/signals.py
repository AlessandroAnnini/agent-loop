import signal
from agent_loop.exceptions import GracefulExit
import asyncio


def setup_signal_handlers(
    loop: asyncio.AbstractEventLoop, interrupt_event: asyncio.Event
) -> None:
    r"""
    Set up signal handler for SIGINT (CTRL+C) to support interruption.
    SIGINT sets interrupt_event.
    """

    def handle_sigint(signum, frame):
        print("\n[Interrupted] Returning to prompt. (Press CTRL+D to quit)")
        loop.call_soon_threadsafe(interrupt_event.set)

    signal.signal(signal.SIGINT, handle_sigint)
