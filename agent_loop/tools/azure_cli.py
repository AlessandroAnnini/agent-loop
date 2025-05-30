import subprocess

# Define allowed services and read-only operations
ALLOWED_SERVICES = {
    "vm",
    "group",
    "account",
    "storage",
    "network",
    "aks",
    "monitor",
    "role",
    "ad",
}
ALLOWED_VERBS = {"list", "show", "display", "get"}

tool_definition = {
    "name": "azure_cli",
    "description": "Run Azure CLI read-only commands to interact with Azure services.",
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": (
                    "Arguments to pass to the Azure CLI, e.g., "
                    "'vm list', 'group show', or 'account show'. "
                    "Only safe read-only operations are allowed."
                ),
            }
        },
        "required": ["args"],
    },
}


def is_safe_azure_command(cmd: list) -> bool:
    if len(cmd) < 3:
        return False
    service, operation = cmd[1], cmd[2]
    return service in ALLOWED_SERVICES and any(
        operation.startswith(verb) for verb in ALLOWED_VERBS
    )


def handle_call(input_data):
    args = input_data["args"]
    cmd = ["az"] + args.strip().split()

    if not is_safe_azure_command(cmd):
        return (
            "⚠️ Unsafe or unsupported Azure CLI command.\n\n"
            f"Allowed services: {', '.join(sorted(ALLOWED_SERVICES))}\n"
            f"Allowed operations: {', '.join(sorted(ALLOWED_VERBS))}\n"
            "Example: 'az vm list' or 'az group show'"
        )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"EXIT CODE: {result.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "Azure CLI command timed out."
    except Exception as e:
        return f"Error executing Azure CLI command: {e}"
