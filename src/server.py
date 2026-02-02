# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""MCP server entrypoint.

Exposes Gmail tools via Dedalus MCP framework.
Credentials (OAuth2 access token) provided by clients at runtime via token exchange.
"""

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from smoke import smoke_tools


def create_server() -> MCPServer:
    """Create MCP server with current env config."""
    as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    return MCPServer(
        name="gmail-mcp",
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=as_url,
    )


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    server.collect(*smoke_tools)
    await server.serve(port=8080)
