import subprocess

# Define allowed services and read-only operations
ALLOWED_SERVICES = {
    "s3",
    "ec2",
    "iam",
    "sts",
    "cloudwatch",
    "logs",
    "ecr",
    "eks",
    "rds",
    "lambda",
}
ALLOWED_VERBS = {"list", "describe", "get"}

tool_definition = {
    "name": "aws_cli",
    "description": "Run AWS CLI v2 read-only commands to interact with AWS services",
    "input_schema": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": (
                    "Arguments to pass to the AWS CLI, e.g., "
                    "'s3 ls', 'ec2 describe-instances', or 'sts get-caller-identity'. "
                    "Only safe read-only operations are allowed."
                ),
            }
        },
        "required": ["args"],
    },
}


def is_safe_aws_command(cmd: list) -> bool:
    if len(cmd) < 3:
        return False
    service, operation = cmd[1], cmd[2]
    return service in ALLOWED_SERVICES and any(
        operation.startswith(verb) for verb in ALLOWED_VERBS
    )


def handle_tool_call(input_data):
    args = input_data["args"]
    cmd = ["aws"] + args.strip().split()

    if not is_safe_aws_command(cmd):
        return (
            "⚠️ Unsafe or unsupported AWS CLI command.\n\n"
            f"Allowed services: {', '.join(sorted(ALLOWED_SERVICES))}\n"
            f"Allowed operations: {', '.join(sorted(ALLOWED_VERBS))}\n"
            "Example: 'aws ec2 describe-instances'"
        )

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return (
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}\n"
            f"EXIT CODE: {result.returncode}"
        )
    except subprocess.TimeoutExpired:
        return "AWS CLI command timed out."
    except Exception as e:
        return f"Error executing AWS CLI command: {e}"
