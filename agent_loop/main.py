#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["anthropic>=0.45.0", "openai>=1.0.0"]
# ///
import os
from typing import Dict, List
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

load_dotenv(dotenv_path=os.path.expanduser("~/.config/agent-loop/.env"))

mcp_manager = MCPManager()


def user_input(simple_text: bool = False) -> List[Dict]:
    x = input("\ndev@agent-loop:~$ ")
    if x.lower() in {"exit", "quit"}:
        print("👋 Goodbye!")
        raise SystemExit
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if simple_text:
        format_instruction = "(Format your answer as plain ASCII text, optimized for CLI readability. Do not use markdown or special formatting.)"
    else:
        format_instruction = "(Format your answer using markdown syntax. Use markdown features for clarity and readability in a terminal that supports markdown rendering.)"
    x = f"{x}\n(Current date and time: {now})\n{format_instruction}"
    return [{"type": "text", "text": x}]


def create_llm():
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


def get_tool_description(tool_name: str) -> str:
    for tool in TOOLS:
        if tool.get("name") == tool_name:
            return tool.get("description", "No description available.")
    return "No description available."


def confirm_tool_execution(
    tool_name: str, input_data: Dict, simple_text: bool = False
) -> bool:
    description = get_tool_description(tool_name)
    agent_confirm(
        f"\n⚠️ [CONFIRMATION REQUIRED]\nTool: {tool_name}\nDescription: {description}\nInput: {input_data}",
        simple_text=simple_text,
    )
    answer = input("Do you want to execute this command? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


async def handle_tool_call(
    tool_call: Dict, debug: bool = False, safe: bool = False, simple_text: bool = False
) -> Dict:
    name = tool_call["name"]
    input_data = tool_call["input"]
    agent_tool(
        f"🛠️ [Agent] Calling tool: {name} | Input: {input_data}", simple_text=simple_text
    )
    if debug:
        agent_info(f"\n[Tool: {name}] Input: {input_data}\n", simple_text=simple_text)
    if safe and not confirm_tool_execution(name, input_data, simple_text=simple_text):
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
        agent_error(f"No handler for tool: {name}", simple_text=simple_text)
        raise ValueError(f"No handler for tool: {name}")
    if inspect.iscoroutinefunction(handler):
        output = await handler(input_data)
    else:
        output = handler(input_data)
    if debug:
        agent_info(str(output), simple_text=simple_text)
    return {
        "type": "tool_result",
        "tool_use_id": tool_call["id"],
        "content": [{"type": "text", "text": output}],
    }


async def loop(
    llm_fn, debug: bool = False, safe: bool = False, simple_text: bool = False
):
    msg = user_input(simple_text=simple_text)
    while True:
        spinner = Halo(text="Thinking...", spinner="dots")
        spinner.start()
        try:
            response, tool_calls = llm_fn(msg)
        finally:
            spinner.stop()
        agent_reply(f"💬 Agent: {response}", simple_text=simple_text)
        if tool_calls:
            tool_results = [
                await handle_tool_call(
                    tc, debug=debug, safe=safe, simple_text=simple_text
                )
                for tc in tool_calls
            ]
            msg = tool_results
        else:
            msg = user_input(simple_text=simple_text)


async def agent_main():
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
            try:
                await loop(
                    create_llm(),
                    debug=args.debug,
                    safe=args.safe,
                    simple_text=args.simple_text,
                )
            except KeyboardInterrupt:
                agent_info("\n👋 Interrupted. Goodbye!", simple_text=args.simple_text)
    except asyncio.CancelledError:
        pass


def main():
    try:
        asyncio.run(agent_main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted. Goodbye!")


if __name__ == "__main__":
    main()
