import os
import requests
from dotenv import load_dotenv

# Load .env once at module level
load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

tool_definition = {
    "name": "jira",
    "description": "Query JIRA via REST API using safe, read-only endpoints",
    "input_schema": {
        "type": "object",
        "properties": {
            "endpoint": {
                "type": "string",
                "description": (
                    "JIRA API endpoint path, e.g., '/rest/api/3/issue/ISSUE-123' or '/rest/api/3/project'"
                ),
            },
            "params": {
                "type": "object",
                "description": "Optional query parameters as a key-value object",
            },
        },
        "required": ["endpoint"],
    },
}


def handle_tool_call(input_data):
    if not all([JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN]):
        return "Missing JIRA credentials. Please set JIRA_BASE_URL, JIRA_EMAIL, and JIRA_API_TOKEN in your .env file."

    endpoint = input_data["endpoint"]
    params = input_data.get("params", {})

    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint

    url = JIRA_BASE_URL.rstrip("/") + endpoint

    try:
        response = requests.get(
            url,
            auth=(JIRA_EMAIL, JIRA_API_TOKEN),
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
