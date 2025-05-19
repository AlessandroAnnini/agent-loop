import os
import requests
from dotenv import load_dotenv
from .home_assistant_api.client import HassClient

load_dotenv()

HA_URL = os.getenv("HA_URL")
HA_TOKEN = os.getenv("HA_ACCESS_TOKEN")

tool_definition = {
    "name": "home_assistant",
    "description": (
        "Use this tool to control devices in your Home Assistant setup or get information about available entities. "
        "You can turn lights and switches on or off, adjust thermostats, or call any other service exposed by Home Assistant.\n\n"
        "To use this tool, provide:\n"
        "- 'operation': either 'control' (to control devices) or 'get_entities' (to list available entities)\n"
        "- For 'control' operation:\n"
        "  - 'domain': the category of the device or service (e.g., 'light', 'switch', 'climate')\n"
        "  - 'service': the action to perform (e.g., 'turn_on', 'turn_off', 'set_temperature')\n"
        "  - 'service_data': the parameters required for the action, such as the target entity_id and optional attributes.\n"
        "- For 'get_entities' operation:\n"
        "  - 'domain': optional - the type of entities to list (e.g., 'switch', 'light')\n\n"
        "Examples:\n"
        "- Turn on the living room light:\n"
        "  operation: 'control'\n"
        "  domain: 'light'\n"
        "  service: 'turn_on'\n"
        '  service_data: {"entity_id": "light.living_room"}\n\n'
        "- List all switches:\n"
        "  operation: 'get_entities'\n"
        "  domain: 'switch'"
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["control", "get_entities"],
                "description": "The operation to perform - either control devices or get entity information",
            },
            "domain": {
                "type": "string",
                "description": "The domain of the device (e.g., 'light', 'switch', 'climate')",
            },
            "service": {
                "type": "string",
                "description": "The action to perform (e.g., 'turn_on', 'turn_off', 'toggle', 'set_temperature')",
            },
            "service_data": {
                "type": "object",
                "description": (
                    "Parameters for the service, such as the 'entity_id' and optional fields like brightness or temperature."
                ),
                "properties": {
                    "entity_id": {
                        "type": "string",
                        "description": "The target entity (e.g., 'light.living_room')",
                    }
                },
            },
        },
        "required": ["operation"],
        # The allOf construct isn't supported at the top level by Claude's tool schema
        # Instead we'll validate requirements in the code
    },
}


def handle_tool_call(input_data):
    if not HA_URL or not HA_TOKEN:
        return "❌ Missing HA_URL or HA_ACCESS_TOKEN in your .env file."

    try:
        ha = HassClient(HA_URL, HA_TOKEN)
        operation = input_data["operation"]

        if operation == "control":
            # Validate required fields for control operation
            if "domain" not in input_data:
                return "❌ Missing required parameter: domain"
            if "service" not in input_data:
                return "❌ Missing required parameter: service"
            if "service_data" not in input_data:
                return "❌ Missing required parameter: service_data"

            return handle_control_operation(ha, input_data)
        elif operation == "get_entities":
            return handle_get_entities_operation(ha, input_data)
        else:
            return f"❌ Unknown operation: {operation}"

    except Exception as e:
        return f"❌ Failed to execute operation: {e}"


def handle_control_operation(ha, input_data):
    """Handle device control operations."""
    domain = input_data["domain"]
    service = input_data["service"]
    service_data = input_data.get("service_data", {})
    result = ha.call_service(domain, service, service_data)

    if isinstance(result, list):
        summaries = [
            f"- {s.entity_id} is now '{s.state}' (attrs: {s.attributes})"
            for s in result
        ]
        return f"✅ Service '{service}' called on domain '{domain}':\n" + "\n".join(
            summaries
        )
    return "✅ Service executed successfully."


def handle_get_entities_operation(ha, input_data):
    """Handle entity discovery operations."""
    domain = input_data.get("domain")
    all_states = ha.get_all_states()

    if domain:
        # Filter entities by the specified domain
        domain_entities = [
            state for state in all_states if state.entity_id.startswith(f"{domain}.")
        ]

        if not domain_entities:
            return f"No entities found for domain '{domain}'."

        result = f"Available {domain} entities:\n"
        for entity in domain_entities:
            result += f"- {entity.entity_id}: '{entity.state}'\n"
        return result
    else:
        # Group entities by domain
        domains = {}
        for state in all_states:
            domain = state.entity_id.split(".")[0]
            if domain not in domains:
                domains[domain] = []
            domains[domain].append(state.entity_id)

        result = "Available entity domains:\n"
        for domain, entities in domains.items():
            result += f"- {domain}: {len(entities)} entities\n"
        return result
