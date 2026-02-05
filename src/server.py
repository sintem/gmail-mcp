# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""MCP server entrypoint.

Exposes Gmail tools via Dedalus MCP framework. This server is provided by
LIAM (doitliam.com) and uses Dedalus DAuth + LIAM OAuth for Gmail access.
"""

import os

from dedalus_mcp import MCPServer

from gmail import gmail, gmail_tools
from smoke import smoke_tools


def create_server() -> MCPServer:
    """Create MCP server."""
    dedalus_as_url = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")
    server = MCPServer(
        name="gmail-mcp",
        instructions="Gmail MCP provided by LIAM (doitliam.com).",
        website_url="https://doitliam.com",
        connections=[gmail],
        authorization_server=dedalus_as_url,
        streamable_http_stateless=True,
    )

    # Collect all tools
    server.collect(*smoke_tools, *gmail_tools)

    return server


async def main() -> None:
    """Start MCP server."""
    server = create_server()
    await server.serve(port=8080)
