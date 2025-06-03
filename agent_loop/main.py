#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["anthropic>=0.45.0", "openai>=1.0.0"]
# ///
import os
import json
from typing import Dict, List, Optional
from agent_loop.providers.anthropic import create_anthropic_llm
from agent_loop.providers.openai import create_openai_llm
from agent_loop.tools import TOOLS, TOOL_HANDLERS
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

load_dotenv(dotenv_path=os.path.expanduser("~/.config/agent-loop/.env"))

mcp_manager = MCPManager()


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
        Prompt the user for input using get_user_command, supporting CTRL+Q for quit and CTRL+C for prompt interruption.
        Returns a message list suitable for LLM input, or None if the user wants to quit.
        """
        x = get_user_command(self.simple_text)
        if x is None:
            return None
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        format_instruction = (
            PLAIN_FORMAT_INSTRUCTION
            if self.simple_text
            else MARKDOWN_FORMAT_INSTRUCTION
        )
        x = f"{x}\n(Current date and time: {now})\n{format_instruction}"
        return [{"type": "text", "text": x}]

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
        agent_tool(
            f"🛠️ [Agent] Calling tool: {name} | Input: {input_data}",
            simple_text=self.simple_text,
        )
        
        if self.debug:
            agent_info(
                f"\n[Tool: {name}] Input: {input_data}\n", simple_text=self.simple_text
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
            error_message = f"❌ [ERROR] Tool '{name}' failed: {type(e).__name__}: {str(e)}"
            
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
                        raise
                    except Exception as e:
                        # Handle TaskGroup or other unhandled exceptions
                        error_message = f"❌ [Error] Failed to process tool '{tc['name']}': {e}"
                        agent_error(error_message, simple_text=self.simple_text)
                        
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": tc["id"],
                            "content": [{"type": "text", "text": error_message}],
                        })
                
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
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")
    if not anthropic_key and not openai_key:
        raise EnvironmentError(
            "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY environment variables."
        )
    if anthropic_key:
        return create_anthropic_llm(anthropic_model, anthropic_key)
    return create_openai_llm(openai_model, openai_key)


async def agent_main() -> None:
    """
    Main async entrypoint: parses arguments, registers tools, and runs the agent loop.
    Handles graceful exit and cancellation.
    """
    try:
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
            spinner = Halo(text="Loading MCP servers...", spinner="dots")
            spinner.start()
            try:
                await mcp_manager.register_tools(exit_stack, debug=args.debug)
            finally:
                spinner.stop()
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
        pass


def main() -> None:
    """
    Synchronous entrypoint for the agent-loop CLI application.
    Runs the async agent_main and handles top-level exceptions.
    """
    try:
        asyncio.run(agent_main())
    except GracefulExit:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n[Error] {e}")


if __name__ == "__main__":
    main()