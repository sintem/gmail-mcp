# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""MCP server entrypoint.

Exposes Gmail tools via Dedalus MCP framework.
OAuth handled by LIAM backend which proxies to Google OAuth.
"""

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from gmail import gmail, gmail_tools
from smoke import smoke_tools


def create_server() -> MCPServer:
    """Create MCP server with LIAM as authorization server."""
    # Use Dedalus AS for OAuth (testing if gmail connection causes 401)
    as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")

    server = MCPServer(
        name="gmail-mcp",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=as_url,
    )

    # Collect all tools
    server.collect(*smoke_tools, *gmail_tools)

    return server


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    await server.serve(port=8080)
