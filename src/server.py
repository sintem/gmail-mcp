# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""LIAM Gmail MCP Server.

OAuth Flow:
1. User connects to MCP
2. Dedalus discovers LIAM OAuth via /.well-known/oauth-authorization-server
3. User is redirected to LIAM → Google OAuth
4. After auth, LIAM issues JWT
5. MCP uses JWT to call LIAM backend → Gmail API
"""

import os

from dedalus_mcp import MCPServer
from dedalus_mcp.server import TransportSecuritySettings

from src.gmail import gmail_tools, gmail


def create_server() -> MCPServer:
    """Create the MCP server with LIAM as authorization server."""
    # LIAM backend URL - also serves as OAuth authorization server
    liam_url = os.getenv("LIAM_API_URL", "https://us-central1-liam1-dev.cloudfunctions.net")

    server = MCPServer(
        name="gmail-mcp",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=liam_url,
    )

    return server


async def main() -> None:
    """Start the MCP server locally."""
    server = create_server()
    server.collect(*gmail_tools)
    await server.serve(port=8080)


# Create and configure server for Dedalus deployment
server = create_server()
server.collect(*gmail_tools)

# Export for Dedalus deployment
app = server
