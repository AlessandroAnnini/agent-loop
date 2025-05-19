# Creating New Tools for Agent Loop

This guide will walk you through the process of creating a new tool for Agent Loop using functional programming principles.

## Tool Structure

Each tool in Agent Loop consists of:

1. **Tool Definition**: A dictionary describing the tool, its purpose, and input schema
2. **Handler Function**: A pure function that processes the tool's inputs and returns its outputs

## Step-by-Step Guide

### 1. Create a New Tool File

Create a new Python file in the `tools` directory. Name it according to your tool's purpose (e.g., `my_tool.py`).

```python
# tools/my_tool.py

tool_definition = {
    "name": "my_tool",
    "description": "Concise description of what your tool does and how to use it",
    "input_schema": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of the first parameter"
            },
            "param2": {
                "type": "integer",
                "description": "Description of the second parameter"
            },
            # Add more parameters as needed
        },
        "required": ["param1"],  # List parameters that are required
    },
}


def handle_tool_call(input_data):
    """
    Process the tool call with the given input data.

    Args:
        input_data: A dictionary containing the tool's input parameters

    Returns:
        A string containing the tool's output
    """
    param1 = input_data["param1"]
    param2 = input_data.get("param2", 0)  # Use get() with default for optional params

    # Implement your tool's functionality here
    result = f"Processed {param1} with value {param2}"

    return result
```

### 2. Register Your Tool

Add your tool to `tools/__init__.py`:

```python
from . import (
    bash,
    # ... other imports
    my_tool,  # Add your tool here
)

TOOLS = [
    bash.tool_definition,
    # ... other tool definitions
    my_tool.tool_definition,  # Add your tool definition here
]

TOOL_HANDLERS = {
    "bash": bash.handle_tool_call,
    # ... other handler mappings
    "my_tool": my_tool.handle_tool_call,  # Add your tool handler here
}
```

### 3. Input Schema Guidelines

Follow these guidelines for your input schema:

- Use clear, descriptive parameter names
- Provide helpful descriptions for each parameter
- Mark essential parameters as "required"
- Use appropriate JSON Schema types:
  - `string`: For text input
  - `integer`: For whole numbers
  - `number`: For decimal values
  - `boolean`: For true/false values
  - `object`: For nested parameters
  - `array`: For lists

Example of a more complex schema:

```python
"input_schema": {
    "type": "object",
    "properties": {
        "operation": {
            "type": "string",
            "enum": ["create", "read", "update", "delete"],
            "description": "The operation to perform"
        },
        "target": {
            "type": "string",
            "description": "The target resource for the operation"
        },
        "options": {
            "type": "object",
            "properties": {
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to apply recursively"
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "yaml", "text"],
                    "description": "Output format"
                }
            }
        }
    },
    "required": ["operation", "target"]
}
```

### 4. Handler Function Best Practices

Follow these functional programming principles:

1. **Pure functions**: Ensure your handler produces the same output for the same input
2. **Error handling**: Properly catch and report errors to the user
3. **Input validation**: Validate inputs before processing
4. **Meaningful returns**: Return clear, structured outputs

Example of a handler with proper error handling:

```python
def handle_tool_call(input_data):
    try:
        # Validate required inputs
        if "required_param" not in input_data:
            return "❌ Missing required parameter: required_param"

        # Process the inputs
        result = process_data(input_data)

        # Return formatted output
        return f"✅ Operation completed successfully: {result}"

    except Exception as e:
        return f"❌ Error executing tool: {e}"
```

### 5. Environment Variables

If your tool requires API keys or other configuration:

1. Add them to the `.env` file
2. Load them in your tool file using `dotenv`

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MY_TOOL_API_KEY")
BASE_URL = os.getenv("MY_TOOL_BASE_URL")

# Then check these in your handler:
def handle_tool_call(input_data):
    if not API_KEY or not BASE_URL:
        return "❌ Missing required environment variables in .env"

    # Rest of your handler code...
```

### 6. External Dependencies

If your tool requires additional Python packages:

1. Add them to `requirements.txt`
2. Document the dependency in your tool's header comment

## Testing Your Tool

Test your tool thoroughly before integration:

1. Create test cases with various inputs
2. Test with valid and invalid parameters
3. Verify error handling works correctly
4. Check for expected outputs

## Example: Complete Tool Implementation

Here's a complete example of a weather tool that checks the weather in a given city:

```python
# tools/weather.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_BASE_URL = "https://api.weatherapi.com/v1"

tool_definition = {
    "name": "weather",
    "description": "Get current weather information for a specified location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "City name or location to get weather for"
            },
            "units": {
                "type": "string",
                "enum": ["metric", "imperial"],
                "description": "Temperature units (metric for Celsius, imperial for Fahrenheit)"
            }
        },
        "required": ["location"]
    }
}

def handle_tool_call(input_data):
    if not WEATHER_API_KEY:
        return "❌ Missing WEATHER_API_KEY environment variable"

    location = input_data["location"]
    units = input_data.get("units", "metric")

    try:
        response = requests.get(
            f"{WEATHER_BASE_URL}/current.json",
            params={
                "key": WEATHER_API_KEY,
                "q": location,
                "units": units
            },
            timeout=10
        )

        if response.status_code != 200:
            return f"❌ API Error: {response.status_code} - {response.text}"

        data = response.json()
        temp = data["current"]["temp_c"] if units == "metric" else data["current"]["temp_f"]
        condition = data["current"]["condition"]["text"]

        return f"Weather in {location}: {condition}, {temp}°{'C' if units == 'metric' else 'F'}"

    except Exception as e:
        return f"❌ Error getting weather data: {e}"
```

## Best Practices Summary

1. **Keep it simple**: Each tool should do one thing well
2. **Document thoroughly**: Clear descriptions help both users and AI
3. **Validate inputs**: Check required parameters and value ranges
4. **Handle errors gracefully**: Provide helpful error messages
5. **Follow FP principles**: Pure functions, immutability, no side effects
6. **Secure credentials**: Use environment variables for secrets

By following these guidelines, you'll create tools that integrate seamlessly with Agent Loop while maintaining its functional programming approach and user-friendly design.
