from . import (
    bash,
    python_eval,
    curl,
    git,
    docker,
    project_inspector,
    kubectl,
    aws_cli,
    jira,
    confluence,
    json,
)

TOOLS = [
    bash.tool_definition,
    python_eval.tool_definition,
    curl.tool_definition,
    git.tool_definition,
    docker.tool_definition,
    project_inspector.tool_definition,
    kubectl.tool_definition,
    aws_cli.tool_definition,
    jira.tool_definition,
    confluence.tool_definition,
    json.tool_definition,
]

TOOL_HANDLERS = {
    "bash": bash.handle_tool_call,
    "python": python_eval.handle_tool_call,
    "curl": curl.handle_tool_call,
    "git": git.handle_tool_call,
    "docker": docker.handle_tool_call,
    "project_inspector": project_inspector.handle_tool_call,
    "kubectl": kubectl.handle_tool_call,
    "aws_cli": aws_cli.handle_tool_call,
    "jira": jira.handle_tool_call,
    "confluence": confluence.handle_tool_call,
    "json": json.handle_tool_call,
}
