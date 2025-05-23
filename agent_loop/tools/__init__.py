from agent_loop.tools import (
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
    http,
    filesystem,
    node_eval,
    sympy,
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
    http.tool_definition,
    filesystem.tool_definition,
    node_eval.tool_definition,
    sympy.tool_definition,
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
    "http": http.handle_tool_call,
    "filesystem": filesystem.handle_tool_call,
    "node": node_eval.handle_tool_call,
    "sympy": sympy.handle_tool_call,
}
