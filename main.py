#!/usr/bin/env -S uv run --script
# /// script
# dependencies = ["anthropic>=0.45.0"]
# ///
import os
from typing import Dict, List
import anthropic
from tools import TOOLS, TOOL_HANDLERS
import argparse
from halo import Halo


def user_input() -> List[Dict]:
    x = input("\ndev@agent-loop:~$ ")
    if x.lower() in {"exit", "quit"}:
        print("Goodbye!")
        raise SystemExit
    return [{"type": "text", "text": x}]


def create_llm(model: str):
    if "ANTHROPIC_API_KEY" not in os.environ:
        raise EnvironmentError("ANTHROPIC_API_KEY not set.")

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    messages = []

    def call_llm(content):
        messages.append({"role": "user", "content": content})
        content[-1]["cache_control"] = {"type": "ephemeral"}

        if not os.path.exists("SYSTEM_PROMPT.txt"):
            raise FileNotFoundError("SYSTEM_PROMPT.txt does not exist.")

        with open("SYSTEM_PROMPT.txt", "r") as f:
            system_prompt = f.read()

        response = client.messages.create(
            model=model,
            system=system_prompt,
            max_tokens=20_000,
            messages=messages,
            tools=TOOLS,
        )

        del content[-1]["cache_control"]

        output, tool_calls = "", []
        assistant_content = {"role": "assistant", "content": []}
        for part in response.content:
            if part.type == "text":
                output += part.text
                assistant_content["content"].append({"type": "text", "text": part.text})
            elif part.type == "tool_use":
                assistant_content["content"].append(part)
                tool_calls.append(
                    {"id": part.id, "name": part.name, "input": part.input}
                )

        messages.append(assistant_content)
        return output, tool_calls

    return call_llm


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
        msg = (
            [handle_tool_call(tc, debug=debug, safe=safe) for tc in tool_calls]
            if tool_calls
            else user_input()
        )


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
        loop(create_llm("claude-3-7-sonnet-latest"), debug=args.debug, safe=args.safe)
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")


if __name__ == "__main__":
    main()
