import os
import requests
from dotenv import load_dotenv

# Load credentials once
load_dotenv()

CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_EMAIL = os.getenv("CONFLUENCE_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")

tool_definition = {
    "name": "confluence",
    "description": "Query Atlassian Confluence Cloud via REST API (read-only)",
    "input_schema": {
        "type": "object",
        "properties": {
            "endpoint": {
                "type": "string",
                "description": (
                    "Confluence REST API endpoint path, e.g., '/wiki/rest/api/content/{id}' or '/wiki/rest/api/space'"
                ),
            },
            "params": {
                "type": "object",
                "description": "Optional query parameters (as key-value object)",
            },
        },
        "required": ["endpoint"],
    },
}


def handle_tool_call(input_data):
    if not all([CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN]):
        return "Missing Confluence credentials. Please set CONFLUENCE_BASE_URL, CONFLUENCE_EMAIL, and CONFLUENCE_API_TOKEN in your .env file."

    endpoint = input_data["endpoint"]
    params = input_data.get("params", {})

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    url = CONFLUENCE_BASE_URL.rstrip("/") + endpoint

    try:
        response = requests.get(
            url,
            auth=(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN),
            params=params,
            headers={"Accept": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return f"Response ({response.status_code}):\n{response.json()}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP Error: {e.response.status_code} {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"Request failed: {e}"
