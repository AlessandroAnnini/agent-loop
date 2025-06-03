import os
import http.client
import json

# Tool definition for Serper

tool_definition = {
    "name": "serper",
    "description": "Search using the Serper API (Google Search)",
    "input_schema": {
        "type": "object",
        "properties": {
            "q": {"type": "string", "description": "Search query"},
        },
        "required": ["q"],
    },
}


def handle_call(input_data):
    api_key = os.environ.get("SERPER_API_KEY")
    if not api_key:
        return "Error: SERPER_API_KEY environment variable not set."
    query = input_data["q"]
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({"q": query})
    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    try:
        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return data.decode("utf-8")
    except Exception as e:
        return f"Error executing Serper search: {e}"
    finally:
        conn.close()
