# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""LIAM Gmail MCP Server.

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
    # LIAM serves OAuth endpoints via Cloudflare Worker at api-dev.doitliam.com
    # - /.well-known/oauth-authorization-server → OAuth metadata
    # - /.well-known/jwks.json → JWKS for token verification
    # - /authorize → Authorization endpoint
    # - /token → Token endpoint
    # Use LIAM or Dedalus AS based on environment
    # For testing, DEDALUS_AS_URL can be set to use standard Dedalus auth
    auth_server = os.getenv("DEDALUS_AS_URL", os.getenv("LIAM_API_URL", "https://api-dev.doitliam.com"))

    return MCPServer(
        name="gmail-mcp",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=auth_server,
    )


async def main() -> None:
    """Start MCP server locally."""
    server = create_server()
    server.collect(*smoke_tools, *gmail_tools)
    await server.serve(port=8080)


# Create and configure server for Dedalus deployment
server = create_server()
server.collect(*smoke_tools, *gmail_tools)

# Export for Dedalus deployment
app = server
