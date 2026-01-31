# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server - Minimal test version
"""

from dedalus_mcp import MCPServer, tool


@tool(description="Test tool - returns hello")
def hello(name: str = "World") -> str:
    """Say hello."""
    return f"Hello, {name}!"


server = MCPServer("gmail-mcp")
server.collect(hello)
app = server


if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve(port=8080))
