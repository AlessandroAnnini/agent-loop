import asyncio
import json
import os
from typing import Dict, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from agent_loop.tools import TOOL_HANDLERS, TOOLS

CONFIG_PATH = os.path.expanduser("~/.config/agent-loop/mcp.json")


class MCPManager:
    def __init__(self, debug: bool = False):
        self.session_map: Dict[str, Any] = {}
        self.debug = debug

    @staticmethod
    def extract_text_content(result):
        if isinstance(result, list):
            return "\n".join(MCPManager.extract_text_content(item) for item in result)
        if hasattr(result, "text"):
            return result.text
        if isinstance(result, dict) and "text" in result:
            return result["text"]
        return str(result)

    async def load_mcp_config(self, path: str = CONFIG_PATH) -> Dict[str, Any]:
        """Load MCP config from the given path."""

        def _read():
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        return await asyncio.to_thread(_read)

    async def start_mcp_session(
        self, name: str, server_cfg: Dict[str, Any], exit_stack: AsyncExitStack
    ):
        """Start an MCP session for a single server and return (name, session, tools)."""
        params = StdioServerParameters(
            command=server_cfg["command"],
            args=server_cfg.get("args", []),
            env=server_cfg.get("env", None),
        )
        stdio, write = await exit_stack.enter_async_context(stdio_client(params))
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        tools = (await session.list_tools()).tools
        return name, session, tools

    def tool_handler_factory(self, server_name, service_name):
        debug = self.debug

        async def handler(input_data):
            session = self.session_map.get(server_name)
            if not session:
                return f"[ERROR] No MCP session for server: {server_name}"
            try:
                result = await session.call_tool(service_name, input_data)
                if debug:
                    print(
                        f"[DEBUG] MCP result for {server_name}-{service_name}: {result!r}"
                    )
                content = getattr(result, "content", result)
                return MCPManager.extract_text_content(content)
            except Exception as e:
                import traceback

                print(f"[ERROR] Exception in MCP tool call: {type(e).__name__}: {e}")
                traceback.print_exc()
                return f"[ERROR] MCP tool call failed: {type(e).__name__}: {e}"

        return handler

    async def register_tools(self, exit_stack: AsyncExitStack, debug: bool = False):
        """
        Start all MCP sessions and return the number of MCP tools loaded.
        """
        self.debug = debug
        config = await self.load_mcp_config()
        servers = config.get("mcpServers", {})
        tool_defs = []
        for name, server_cfg in servers.items():
            try:
                name, session, tools = await self.start_mcp_session(
                    name, server_cfg, exit_stack
                )
                self.session_map[name] = session
                for tool in tools:
                    tool_name = f"{name}-{tool.name}"
                    tool_def = {
                        "name": tool_name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                    }
                    tool_defs.append(tool_def)
                    if "-" in tool_name:
                        server, service = tool_name.rsplit("-", 1)
                        TOOL_HANDLERS[tool_name] = self.tool_handler_factory(
                            server, service
                        )
            except Exception as e:
                print(f"Failed to start session for {name}: {e}")
        TOOLS.extend(tool_defs)
        if debug:
            print(f"[INFO] Loaded {len(tool_defs)} MCP tools")
            for tool in tool_defs:
                print(f"Tool: {tool['name']}")
                print(f"Description: {tool['description']}")
                print(f"Input Schema: {tool['input_schema']}")
                print("-" * 50)

        return len(tool_defs)
