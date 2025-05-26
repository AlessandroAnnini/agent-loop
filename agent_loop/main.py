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

load_dotenv(dotenv_path=os.path.expanduser("~/.config/agent-loop/.env"))


def user_input() -> List[Dict]:
    x = input("\ndev@agent-loop:~$ ")
    if x.lower() in {"exit", "quit"}:
        print("Goodbye!")
        raise SystemExit
    return [{"type": "text", "text": x}]


def create_llm():
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL", "gpt-4o")

    if not anthropic_key and not openai_key:
        raise EnvironmentError(
            "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "environment variables. If both are set, ANTHROPIC_API_KEY will be used."
        )

    # Check available API keys and select provider
    if anthropic_key:
        # Use Anthropic if its key is available (priority)
        return create_anthropic_llm(anthropic_model, anthropic_key)
    elif openai_key:
        # Fallback to OpenAI if only its key is available
        return create_openai_llm(openai_model, openai_key)
    else:
        # No API keys available
        raise EnvironmentError(
            "No API keys found. Please set either ANTHROPIC_API_KEY or OPENAI_API_KEY "
            "environment variables. If both are set, ANTHROPIC_API_KEY will be used."
        )


def get_tool_description(tool_name: str) -> str:
    """Return the description for a tool given its name."""
    for tool in TOOLS:
        if tool.get("name") == tool_name:
            return tool.get("description", "No description available.")
    return "No description available."


def confirm_tool_execution(tool_name: str, input_data: Dict) -> bool:
    """Prompt the user to confirm execution of a tool call."""
    description = get_tool_description(tool_name)
    print(f"\n[CONFIRMATION REQUIRED]")
    print(f"Tool: {tool_name}")
    print(f"Description: {description}")
    print(f"Input: {input_data}")
    print("Do you want to execute this command? [y/N]: ", end="")
    answer = input().strip().lower()
    return answer in {"y", "yes"}


def handle_tool_call(tool_call: Dict, debug: bool = False, safe: bool = False) -> Dict:
    name = tool_call["name"]
    input_data = tool_call["input"]
    if debug:
        print(f"\n[Tool: {name}] Input: {input_data}\n")

    if safe and not confirm_tool_execution(name, input_data):
        return {
            "type": "tool_result",
            "tool_use_id": tool_call["id"],
            "content": [
                {
                    "type": "text",
                    "text": f"[SKIPPED] {name} command was not executed by user request.",
                }
            ],
        }

    handler = TOOL_HANDLERS.get(name)
    if not handler:
        raise ValueError(f"No handler for tool: {name}")

    output = handler(input_data)
    if debug:
        print(output)
    return {
        "type": "tool_result",
        "tool_use_id": tool_call["id"],
        "content": [{"type": "text", "text": output}],
    }


def loop(llm_fn, debug: bool = False, safe: bool = False):
    msg = user_input()
    while True:
        spinner = Halo(text="Thinking...", spinner="dots")
        spinner.start()
        try:
            response, tool_calls = llm_fn(msg)
        finally:
            spinner.stop()
        print("Agent:", response)

        if tool_calls:
            tool_results = [
                handle_tool_call(tc, debug=debug, safe=safe) for tc in tool_calls
            ]
            msg = tool_results
        else:
            msg = user_input()


def main():
    parser = argparse.ArgumentParser(description="Agent Loop")
    parser.add_argument("--debug", action="store_true", help="Show tool input/output")
    parser.add_argument(
        "--safe",
        action="store_true",
        help="Require confirmation before executing tools",
    )
    args = parser.parse_args()

    try:
        loop(create_llm(), debug=args.debug, safe=args.safe)
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")


if __name__ == "__main__":
    main()
