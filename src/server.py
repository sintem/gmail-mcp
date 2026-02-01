# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""LIAM Gmail MCP Server.

OAuth Flow (handled by Dedalus):
1. User connects to MCP via Dedalus
2. Dedalus shows OAuth popup → LIAM → Google
3. After auth, Dedalus passes token to MCP
4. MCP uses token to call LIAM backend → Gmail API
"""

from dedalus_mcp import MCPServer
from dedalus_mcp.server import AuthorizationConfig, TransportSecuritySettings

from gmail import gmail_tools, gmail
from smoke import smoke_tools


def create_server() -> MCPServer:
    """Create the MCP server.

    OAuth is handled by Dedalus platform via popup flow.
    Server doesn't enforce auth - Dedalus injects tokens after OAuth.
    """
    server = MCPServer(
        name="gmail-mcp",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        # Disable server-side auth - Dedalus handles OAuth via popup
        authorization=AuthorizationConfig(enabled=False),
    )

    return server


async def main() -> None:
    """Start the MCP server locally."""
    server = create_server()
    server.collect(*gmail_tools)
    await server.serve(port=8080)


# Create and configure server for Dedalus deployment
server = create_server()
server.collect(*smoke_tools, *gmail_tools)

# Export for Dedalus deployment
app = server
