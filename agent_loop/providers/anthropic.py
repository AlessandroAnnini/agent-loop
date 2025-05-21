import anthropic
from agent_loop.tools import TOOLS
from agent_loop.utils import load_system_prompt


def create_anthropic_llm(model: str, api_key: str):
    client = anthropic.Anthropic(api_key=api_key)
    messages = []

    def call_llm(content):
        messages.append({"role": "user", "content": content})
        content[-1]["cache_control"] = {"type": "ephemeral"}

        system_prompt = load_system_prompt()

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
