#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["anthropic>=0.45.0", "openai>=1.0.0"]
# ///
import os
import json
from typing import Dict, List, Optional
from agent_loop.providers.anthropic import create_anthropic_llm
from agent_loop.providers.openai import create_openai_llm
from agent_loop.tools import TOOLS, TOOL_HANDLERS, display_custom_tools
import argparse
from halo import Halo
from dotenv import load_dotenv
import asyncio
from contextlib import AsyncExitStack, suppress
from agent_loop.mcp_client import MCPManager
import inspect
import datetime
from agent_loop.output import (
    agent_reply,
    agent_tool,
    agent_confirm,
    agent_error,
    agent_info,
)
from agent_loop.cli_input import get_user_command
from agent_loop.signals import setup_signal_handlers
from agent_loop.constants import (
    PLAIN_FORMAT_INSTRUCTION,
    MARKDOWN_FORMAT_INSTRUCTION,
    HELP_MESSAGE,
)
from agent_loop.exceptions import GracefulExit
import importlib.metadata

# Load environment variables - local .env takes priority over config directory
load_dotenv(
    dotenv_path=os.path.expanduser("~/.config/agent-loop/.env"), override=False
)  # Config defaults first
load_dotenv(dotenv_path=".env", override=True)  # Local .env overrides config

mcp_manager = MCPManager()


def display_welcome_message():
    """
    Display a beautiful welcome message with the current version.
    """
    version = importlib.metadata.version("agent-loop")
    welcome_message = f"""
╭────────────────────────────────────────────────────────╮
│                                                        │
│   █████╗  ██████╗ ███████╗███╗   ██╗████████╗          │
│  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝          │
│  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║             │
│  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║             │
│  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║             │
│  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝             │
│                                                        │
│  ██╗      ██████╗  ██████╗ ██████╗                     │
│  ██║     ██╔═══██╗██╔═══██╗██╔══██╗                    │
│  ██║     ██║   ██║██║   ██║██████╔╝                    │
│  ██║     ██║   ██║██║   ██║██╔═══╝                     │
│  ███████╗╚██████╔╝╚██████╔╝██║                         │
│  ╚══════╝ ╚═════╝  ╚═════╝ ╚═╝                         │
│                                                        │
│  Version {version:<43}   │
╰────────────────────────────────────────────────────────╯
    """
    print(welcome_message)


async def run_llm(llm_fn, msg):
    """
    Call llm_fn with msg, supporting both sync and async LLM functions.
    """
    if inspect.iscoroutinefunction(llm_fn):
        return await llm_fn(msg)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, llm_fn, msg)


class AgentLoop:
    """
    Main event loop and state manager for the agent-loop CLI application.
    Handles user input, tool calls, LLM interaction, and signal/key interruption.
    """

    def __init__(
        self, debug: bool = False, safe: bool = False, simple_text: bool = False
    ):
        """
        Initialize the AgentLoop.
        :param debug: Show tool input/output for debugging.
        :param safe: Require confirmation before executing tools.
        :param simple_text: Use plain text output instead of markdown.
        """
        self.debug = debug
        self.safe = safe
        self.simple_text = simple_text
        self.interrupt_event: asyncio.Event = asyncio.Event()

    def user_input(self) -> Optional[List[Dict]]:
        """
        Prompt the user for input using get_user_command, supporting CTRL+D or 'exit'/'quit' for quit and CTRL+C for prompt interruption.
        Returns a message list suitable for LLM input, or None if the user wants to quit.
        """
        user_input = get_user_command(self.simple_text)
        if user_input is None:
            return None

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        format_instruction = (
            PLAIN_FORMAT_INSTRUCTION
            if self.simple_text
            else MARKDOWN_FORMAT_INSTRUCTION
        )
        message_text = (
            f"{user_input}\n(Current date and time: {now})\n{format_instruction}"
        )
        return [{"type": "text", "text": message_text}]

    def _get_tool_info(self, tool_name: str) -> tuple[str, str, bool]:
        """Get tool type, icon, and MCP status for a tool name."""
        is_mcp_tool = "-" in tool_name
        tool_icon = "🔌" if is_mcp_tool else "🛠️"
        tool_type = "MCP" if is_mcp_tool else "Tool"
        return tool_type, tool_icon, is_mcp_tool

    def get_tool_description(self, tool_name: str) -> str:
        """
        Get the description for a tool by name.
        """
        for tool in TOOLS:
            if tool.get("name") == tool_name:
                return tool.get("description", "No description available.")
        return "No description available."

    def confirm_tool_execution(self, tool_name: str, input_data: Dict) -> bool:
        """
        Ask the user to confirm execution of a tool, showing its description and input.
        Returns True if confirmed, False otherwise.
        """
        description = self.get_tool_description(tool_name)
        agent_confirm(
            f"\n⚠️ [CONFIRMATION REQUIRED]\nTool: {tool_name}\nDescription: {description}\nInput: {input_data}",
            simple_text=self.simple_text,
        )
        answer = input("Do you want to execute this command? [y/N]: ").strip().lower()
        return answer in {"y", "yes"}

    async def handle_tool_call(self, tool_call: Dict) -> Dict:
        """
        Execute a tool call, handling confirmation, debug output, and async/sync handlers.
        Returns a tool_result dict for the agent loop.
        """
        name = tool_call["name"]
        input_data = tool_call["input"]

        # Use different icons for regular tools vs MCP tools
        # MCP tools have format: server-name-tool-name (contains dash)
        tool_type, tool_icon, is_mcp_tool = self._get_tool_info(name)

        agent_tool(
            f"{tool_icon} [Agent] Calling {tool_type.lower()}: {name} | Input: {input_data}",
            simple_text=self.simple_text,
        )

        if self.debug:
            agent_info(
                f"\n[{tool_type}: {name}] Input: {input_data}\n",
                simple_text=self.simple_text,
            )

        if self.safe and not self.confirm_tool_execution(name, input_data):
            return {
                "type": "tool_result",
                "tool_use_id": tool_call["id"],
                "content": [
                    {
                        "type": "text",
                        "text": f"⚠️ [SKIPPED] {name} command was not executed by user request.",
                    },
                ],
            }

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            agent_error(f"No handler for tool: {name}", simple_text=self.simple_text)
            raise ValueError(f"No handler for tool: {name}")

        try:
            if inspect.iscoroutinefunction(handler):
                output = await handler(input_data)
            else:
                output = handler(input_data)

            if self.debug:
                agent_info(str(output), simple_text=self.simple_text)

            return {
                "type": "tool_result",
                "tool_use_id": tool_call["id"],
                "content": [{"type": "text", "text": output}],
            }
        except Exception as e:
            error_message = (
                f"❌ [ERROR] {tool_type} '{name}' failed: {type(e).__name__}: {str(e)}"
            )

            if self.debug:
                import traceback

                error_message += f"\n\nInputs: {json.dumps(input_data)}\n\n"
                error_message += f"Stack trace:\n{traceback.format_exc()}"

            agent_error(error_message, simple_text=self.simple_text)

            return {
                "type": "tool_result",
                "tool_use_id": tool_call["id"],
                "content": [{"type": "text", "text": error_message}],
            }

    async def run_loop(self, llm_fn: callable) -> None:
        """
        Main agent loop: handles user input, LLM calls, tool calls, and interruption.
        :param llm_fn: The LLM function to call with messages.
        """
        print(f"\n{HELP_MESSAGE}")
        msg = self.user_input()
        if msg is None:
            return
        while True:
            spinner = Halo(text="Thinking...", spinner="dots")
            spinner.start()
            try:
                self.interrupt_event.clear()
                llm_task = asyncio.create_task(run_llm(llm_fn, msg))
                while not llm_task.done():
                    await asyncio.sleep(0.1)
                    if self.interrupt_event.is_set():
                        break
                if self.interrupt_event.is_set():
                    spinner.stop()
                    msg = self.user_input()
                    if msg is None:
                        return
                    continue
                response, tool_calls = llm_task.result()
            except Exception as e:
                spinner.stop()
                error_msg = f"❌ [LLM Error] {type(e).__name__}: {str(e)}"
                if self.debug:
                    import traceback

                    error_msg += f"\n\nLLM Error Stack trace:\n{traceback.format_exc()}"
                agent_error(error_msg, simple_text=self.simple_text)
                msg = self.user_input()
                if msg is None:
                    return
                continue
            finally:
                spinner.stop()

            agent_reply(f"💬 Agent: {response}", simple_text=self.simple_text)
            if tool_calls:
                tool_results = []

                for tc in tool_calls:
                    self.interrupt_event.clear()
                    try:
                        tool_fut = asyncio.create_task(self.handle_tool_call(tc))

                        # Wait for completion or interruption
                        while not tool_fut.done():
                            await asyncio.sleep(0.1)
                            if self.interrupt_event.is_set():
                                tool_fut.cancel()
                                break

                        if self.interrupt_event.is_set():
                            break

                        result = await tool_fut
                        tool_results.append(result)

                    except asyncio.CancelledError:
                        # This is expected when a task is cancelled due to interruption
                        if self.debug:
                            tool_type, _, _ = self._get_tool_info(tc["name"])
                            agent_info(
                                f"{tool_type} '{tc['name']}' was cancelled",
                                simple_text=self.simple_text,
                            )
                        break
                    except asyncio.InvalidStateError as e:
                        # Handle asyncio state errors
                        tool_type, _, _ = self._get_tool_info(tc["name"])
                        error_message = f"❌ [Asyncio Error] {tool_type} '{tc['name']}' encountered an invalid state: {str(e)}"
                        if self.debug:
                            import traceback

                            error_message += (
                                f"\n\nAsyncio Error Details:\n{traceback.format_exc()}"
                            )
                        agent_error(error_message, simple_text=self.simple_text)

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tc["id"],
                                "content": [{"type": "text", "text": error_message}],
                            }
                        )
                    except Exception as e:
                        # Handle TaskGroup and other unhandled exceptions with detailed reporting
                        tool_type, _, _ = self._get_tool_info(tc["name"])
                        error_type = type(e).__name__
                        error_message = f"❌ [Execution Error] Failed to process {tool_type.lower()} '{tc['name']}': {error_type}: {str(e)}"

                        # Special handling for ExceptionGroup/TaskGroup errors
                        if hasattr(e, "exceptions") and hasattr(e, "__cause__"):
                            error_message += f"\n📋 Exception Group Details:"
                            if hasattr(e, "exceptions"):
                                for i, sub_exc in enumerate(e.exceptions, 1):
                                    error_message += f"\n  {i}. {type(sub_exc).__name__}: {str(sub_exc)}"

                        if self.debug:
                            import traceback

                            error_message += (
                                f"\n\n🔍 Full Stack Trace:\n{traceback.format_exc()}"
                            )
                            error_message += f"\n\n🔧 {tool_type} Input: {json.dumps(tc.get('input', {}), indent=2)}"
                            error_message += (
                                f"\n\n⚙️ {tool_type} ID: {tc.get('id', 'unknown')}"
                            )

                        agent_error(error_message, simple_text=self.simple_text)

                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": tc["id"],
                                "content": [{"type": "text", "text": error_message}],
                            }
                        )

                if self.interrupt_event.is_set():
                    msg = self.user_input()
                    if msg is None:
                        return
                    continue

                msg = tool_results
            else:
                msg = self.user_input()
                if msg is None:
                    return


def create_llm() -> callable:
    """
    Create and return the LLM function using Anthropic or OpenAI, depending on environment variables.
    """
    # Read and validate provider preference
    preferred_provider = os.getenv("AI_PROVIDER", "anthropic").lower()
    if preferred_provider not in ("anthropic", "openai"):
        raise ValueError(
            f"Invalid AI_PROVIDER: {preferred_provider}. Must be 'anthropic' or 'openai'."
        )

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")

    temperature = os.getenv("AI_TEMPERATURE", 0.7)

    # make sure that temperature is a float
    temperature = float(temperature)

    # Debug output
    print(f"🔧 [Config] AI_PROVIDER={preferred_provider}")
    print(f"🔧 [Config] AI_TEMPERATURE={temperature}")
    print(f"🔧 [Config] ANTHROPIC_KEY={'✓' if anthropic_key else '✗'}")
    print(f"🔧 [Config] OPENAI_KEY={'✓' if openai_key else '✗'}")

    if not anthropic_key and not openai_key:
        raise EnvironmentError(
            "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables."
        )

    if anthropic_key:
        print(f"✅ [Provider] Using: Anthropic")
        return create_anthropic_llm(anthropic_model, anthropic_key, temperature)
    elif openai_key:
        print(f"✅ [Provider] Using: OpenAI")
        return create_openai_llm(openai_model, openai_key, temperature)
    else:
        raise EnvironmentError(
            "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables."
        )


async def agent_main() -> None:
    """
    Main async entrypoint: parses arguments, registers tools, and runs the agent loop.
    Handles graceful exit and cancellation.
    """
    try:
        # Display welcome message as the first thing
        display_welcome_message()

        # Display custom tools if any are loaded
        display_custom_tools()

        async with AsyncExitStack() as exit_stack:
            parser = argparse.ArgumentParser(description="Agent Loop")
            parser.add_argument(
                "--debug", action="store_true", help="Show tool input/output"
            )
            parser.add_argument(
                "--safe",
                action="store_true",
                help="Require confirmation before executing tools",
            )
            parser.add_argument(
                "--simple-text",
                "-s",
                action="store_true",
                help="Use plain text output instead of Rich formatting",
            )
            args = parser.parse_args()

            # Start spinner for MCP loading
            mcp_spinner = Halo(text="🔌 Loading MCP servers...", spinner="dots")
            mcp_spinner.start()

            try:
                mcp_count = await mcp_manager.register_tools(
                    exit_stack, debug=args.debug
                )
                mcp_spinner.stop()  # Stop spinner on success
                if mcp_count > 0:
                    print(f"✅ [MCP] Loaded {mcp_count} MCP tool(s)")
                else:
                    print("ℹ️ [MCP] No MCP tools configured")
            except Exception as e:
                mcp_spinner.stop()  # Stop spinner on error
                error_msg = f"❌ [MCP Error] Failed to load MCP servers: {type(e).__name__}: {str(e)}"
                if args.debug:
                    import traceback

                    error_msg += f"\n\nMCP Error Stack trace:\n{traceback.format_exc()}"
                print(error_msg)
                print("⚠️  Continuing without MCP servers...")

            loop_obj = asyncio.get_event_loop()
            agent = AgentLoop(
                debug=args.debug, safe=args.safe, simple_text=args.simple_text
            )
            setup_signal_handlers(loop_obj, agent.interrupt_event)
            await agent.run_loop(create_llm())
        print("\n👋 Goodbye!")
    except GracefulExit:
        print("\n👋 Goodbye!")
    except asyncio.CancelledError:
        print("\n⚠️  Operation cancelled")
    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"\n❌ [Agent Error] {error_type}: {str(e)}"

        # Special handling for ExceptionGroup/TaskGroup errors
        if hasattr(e, "exceptions"):
            error_msg += f"\n\n📋 Exception Group Details:"
            for i, sub_exc in enumerate(e.exceptions, 1):
                error_msg += f"\n  {i}. {type(sub_exc).__name__}: {str(sub_exc)}"

        import traceback

        error_msg += f"\n\n🔍 Stack Trace:\n{traceback.format_exc()}"
        print(error_msg)
        raise


def main() -> None:
    """
    Synchronous entrypoint for the agent-loop CLI application.
    Runs the async agent_main and handles top-level exceptions.
    """
    try:
        asyncio.run(agent_main())
    except GracefulExit:
        print("\n👋 Goodbye!")
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Goodbye!")
    except Exception as e:
        error_type = type(e).__name__
        error_msg = f"\n❌ [Critical Error] {error_type}: {str(e)}"

        # Special handling for ExceptionGroup/TaskGroup errors at top level
        if hasattr(e, "exceptions"):
            error_msg += f"\n\n📋 Exception Group Details:"
            for i, sub_exc in enumerate(e.exceptions, 1):
                error_msg += f"\n  {i}. {type(sub_exc).__name__}: {str(sub_exc)}"

        # Always show stack trace for critical errors
        import traceback

        error_msg += f"\n\n🔍 Stack Trace:\n{traceback.format_exc()}"
        error_msg += f"\n\n💡 If this error persists, please run with --debug for more information."

        print(error_msg)


if __name__ == "__main__":
    main()
