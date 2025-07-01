import anthropic
from agent_loop.tools import TOOLS
from agent_loop.utils import load_system_prompt


def create_anthropic_llm(model: str, api_key: str, temperature: float):
    client = anthropic.Anthropic(api_key=api_key)
    messages = []

    print(f"Using Anthropic model: {model} (temperature: {temperature})")

    def call_llm(content):
        def extract_tool_result_content(result_content):
            """Extract text content from tool result, ensuring we always return a string."""
            # Handle string directly
            if isinstance(result_content, str):
                return result_content

            # Handle list: [{"type": "text", "text": "content"}] -> "content"
            if isinstance(result_content, list) and result_content:
                first_item = result_content[0]
                if isinstance(first_item, dict) and first_item.get("type") == "text":
                    return str(first_item.get("text", ""))
                return str(first_item)

            # Handle dict: {"type": "text", "text": "content"} -> "content"
            if (
                isinstance(result_content, dict)
                and result_content.get("type") == "text"
            ):
                return str(result_content.get("text", ""))

            # Fallback: convert anything to string
            return str(result_content) if result_content is not None else ""

        def add_cache_control(content_list):
            """Add ephemeral cache control to the last item in content list."""
            if content_list:
                content_list[-1]["cache_control"] = {"type": "ephemeral"}

        def remove_cache_control():
            """Remove cache control from the last message after API call."""
            if messages and messages[-1]["role"] == "user":
                last_content = messages[-1]["content"]
                if isinstance(last_content, list) and last_content:
                    last_content[-1].pop("cache_control", None)

        # Convert content to Anthropic format
        if isinstance(content, list) and any(
            item.get("type") == "tool_result" for item in content
        ):
            # Handle tool results
            user_content = [
                {
                    "type": "tool_result",
                    "tool_use_id": item["tool_use_id"],
                    "content": extract_tool_result_content(item.get("content", "")),
                }
                for item in content
                if item.get("type") == "tool_result"
            ]
        else:
            # Handle regular messages
            if isinstance(content, str):
                user_content = [{"type": "text", "text": content}]
            elif isinstance(content, list):
                user_content = content
            else:
                user_content = [{"type": "text", "text": str(content)}]

                add_cache_control(user_content)
        messages.append({"role": "user", "content": user_content})

        # Make API call
        response = client.messages.create(
            model=model,
            system=load_system_prompt(),
            max_tokens=20_000,
            temperature=temperature,
            messages=messages,
            tools=TOOLS,
        )

        remove_cache_control()

        # Process response
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
