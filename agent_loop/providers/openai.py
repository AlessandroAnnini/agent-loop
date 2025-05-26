import openai
from agent_loop.tools import TOOLS
import json
from agent_loop.utils import load_system_prompt


def create_openai_llm(model: str, api_key: str):
    client = openai.OpenAI(api_key=api_key)
    messages = []

    print(f"Using OpenAI model: {model}")

    def call_llm(content):
        # Add content to messages with standardized format
        if isinstance(content, list) and any(
            item.get("type") == "tool_result"
            for item in content
            if isinstance(item, dict)
        ):
            # Convert tool results to OpenAI format directly
            for tool_result in content:
                if tool_result.get("type") == "tool_result":
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_result["tool_use_id"],
                            "content": (
                                tool_result["content"][0]["text"]
                                if isinstance(tool_result["content"], list)
                                else tool_result["content"]
                            ),
                        }
                    )
        else:
            # Add user message directly in OpenAI format
            messages.append({"role": "user", "content": content})

        system_prompt = load_system_prompt()

        # Prepare messages for OpenAI
        openai_messages = [{"role": "system", "content": system_prompt}] + messages

        # Convert tools format
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in TOOLS
        ]

        # Make API call
        response = client.chat.completions.create(
            model="gpt-4o" if model.startswith("claude") else model,
            messages=openai_messages,
            tools=openai_tools,
            tool_choice="auto",
        )

        # Process response
        output = response.choices[0].message.content or ""
        tool_calls = []

        # Handle tool calls if present
        if (
            hasattr(response.choices[0].message, "tool_calls")
            and response.choices[0].message.tool_calls
        ):
            for tc in response.choices[0].message.tool_calls:
                if tc.type == "function":
                    tool_calls.append(
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "input": json.loads(tc.function.arguments),
                        }
                    )

        # Add assistant response to message history
        messages.append(
            {
                "role": "assistant",
                "content": output,
                "tool_calls": (
                    [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in response.choices[0].message.tool_calls
                        if tc.type == "function"
                    ]
                    if response.choices[0].message.tool_calls
                    else None
                ),
            }
        )

        return output, tool_calls

    return call_llm
