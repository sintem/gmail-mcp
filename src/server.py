# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""MCP server entrypoint.

Exposes Gmail tools via Dedalus MCP framework.
OAuth configured via Dedalus dashboard environment variables.
"""

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from gmail import gmail, gmail_tools
from smoke import smoke_tools


def create_server() -> MCPServer:
    """Create MCP server."""
    server = MCPServer(
        name="gmail-mcp",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
    )

    # Collect all tools
    server.collect(*smoke_tools, *gmail_tools)

    return server


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    await server.serve(port=8080)
