import asyncio
import json
import os
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolManager:
    def __init__(self):
        self._servers: dict[str, StdioServerParameters] = {}
        self._tool_to_server: dict[str, str] = {}
        self._tool_definitions: list[dict] = []

    def add_server(self, name: str, command: str, args: list[str] | None = None, env: dict | None = None):
        merged_env = None
        if env:
            merged_env = {**os.environ, **env}
        self._servers[name] = StdioServerParameters(
            command=command,
            args=args or [],
            env=merged_env,
        )

    async def discover_tools(self):
        self._tool_to_server.clear()
        self._tool_definitions.clear()

        for server_name, params in self._servers.items():
            try:
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        result = await session.list_tools()

                        for tool in result.tools:
                            prefixed_name = f"mcp__{server_name}__{tool.name}"
                            self._tool_to_server[prefixed_name] = server_name

                            self._tool_definitions.append({
                                "type": "function",
                                "function": {
                                    "name": prefixed_name,
                                    "description": f"[MCP:{server_name}] {tool.description}",
                                    "parameters": tool.inputSchema,
                                },
                            })

                        print(f"  [MCP] Connected to '{server_name}': {len(result.tools)} tools discovered")

            except Exception as e:
                print(f"  [MCP] Failed to connect to '{server_name}': {e}")

    @property
    def tool_definitions(self) -> list[dict]:
        return self._tool_definitions

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        if tool_name not in self._tool_to_server:
            return f"Error: MCP tool '{tool_name}' not found."

        server_name = self._tool_to_server[tool_name]
        original_name = tool_name.removeprefix(f"mcp__{server_name}__")
        params = self._servers[server_name]

        try:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(original_name, arguments)

                    text_parts = []
                    for content in result.content:
                        if hasattr(content, "text"):
                            text_parts.append(content.text)
                        else:
                            text_parts.append(str(content))

                    return "\n".join(text_parts) if text_parts else "(no output)"

        except Exception as e:
            return f"Error: MCP call failed for '{tool_name}': {e}"


def load_mcp_servers_from_config() -> MCPToolManager:
    manager = MCPToolManager()

    config_path = _find_config_file()
    if not config_path:
        return manager

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    for server in config.get("mcpServers", []):
        name = server["name"]
        command = server["command"]
        args = server.get("args", [])
        env = server.get("env")
        manager.add_server(name, command, args, env)
        print(f"  [MCP] Registered server: {name} ({command} {' '.join(args)})")

    return manager


def _find_config_file() -> str | None:
    candidates = [
        os.path.join(os.path.dirname(__file__), "..", "mcp_servers.json"),
        os.path.expanduser("~/.config/mini_agentloop/mcp_servers.json"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None
