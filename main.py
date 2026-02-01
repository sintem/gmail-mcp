# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server

Provides Gmail access through LIAM's CASA-compliant OAuth infrastructure.
All Gmail API calls go through LIAM backend.

Token Flow:
1. User authenticates with LIAM (web app or OAuth)
2. User passes LIAM JWT via Credential to MCP
3. MCP uses JWT to call LIAM backend → Gmail API

Deployed on Dedalus marketplace as: sintem/gmail-mcp
"""

import os

from dedalus_mcp import MCPServer, tool, HttpMethod, HttpRequest, get_context
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.server import AuthorizationConfig, TransportSecuritySettings
from pydantic import Field


# LIAM Backend Configuration (also serves as OAuth Authorization Server)
LIAM_API_BASE = os.getenv("LIAM_API_URL", "https://us-central1-liam1-dev.cloudfunctions.net")


# Connection to LIAM backend - token provided by OAuth flow
liam = Connection(
    name="liam",
    secrets=SecretKeys(token="access_token"),  # Populated by OAuth flow
    base_url=LIAM_API_BASE,
    auth_header_format="Bearer {api_key}",
)


# Helper to call LIAM backend via the connection
async def _req(method: HttpMethod, path: str) -> dict:
    """Call LIAM backend using the OAuth token."""
    ctx = get_context()
    request = HttpRequest(method=method, path=path)
    response = await ctx.dispatch("liam", request)

    if response.success:
        return response.response.body or {}

    error_msg = response.error.message if response.error else "Request failed"
    raise Exception(error_msg)


# Gmail Tools

@tool(description="Get your Gmail profile information including email address and message counts")
async def gmail_get_profile() -> dict:
    """Get the user's Gmail profile."""
    return await _req(HttpMethod.GET, "/mcpGmailGetProfile")


@tool(description="List emails from your inbox with optional search query")
async def gmail_list_messages(
    query: str = Field(default="in:inbox", description="Gmail search query (e.g., 'is:unread', 'from:boss@company.com')"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of messages to return"),
) -> dict:
    """List emails matching the query."""
    return await _req(HttpMethod.GET, f"/mcpGmailListMessages?q={query}&max={max_results}")


@tool(description="Get full content of a specific email by its ID")
async def gmail_get_message(
    message_id: str = Field(description="The Gmail message ID"),
) -> dict:
    """Get a specific email message."""
    return await _req(HttpMethod.GET, f"/mcpGmailGetMessage/{message_id}")


@tool(description="List email threads/conversations with optional search")
async def gmail_list_threads(
    query: str = Field(default="in:inbox", description="Gmail search query"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of threads to return"),
) -> dict:
    """List email threads."""
    return await _req(HttpMethod.GET, f"/mcpGmailListThreads?q={query}&max={max_results}")


@tool(description="Get a full email thread/conversation with all messages")
async def gmail_get_thread(
    thread_id: str = Field(description="The Gmail thread ID"),
) -> dict:
    """Get a specific email thread with all messages."""
    return await _req(HttpMethod.GET, f"/mcpGmailGetThread/{thread_id}")


@tool(description="List all Gmail labels (folders/categories)")
async def gmail_list_labels() -> dict:
    """List Gmail labels."""
    return await _req(HttpMethod.GET, "/mcpGmailListLabels")


@tool(description="Search emails using Gmail's powerful query syntax")
async def gmail_search(
    query: str = Field(description="Gmail search query (e.g., 'subject:meeting after:2024/01/01 has:attachment')"),
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results"),
) -> dict:
    """Search emails using Gmail query syntax."""
    return await _req(HttpMethod.GET, f"/mcpGmailSearch?q={query}&max={max_results}")


# All tools
gmail_tools = [
    gmail_get_profile,
    gmail_list_messages,
    gmail_get_message,
    gmail_list_threads,
    gmail_get_thread,
    gmail_list_labels,
    gmail_search,
]


# Create MCP Server
# OAuth disabled at MCP level - tokens passed via Credential mechanism
server = MCPServer(
    name="gmail-mcp",
    connections=[liam],
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    authorization=AuthorizationConfig(enabled=False),
)

# Register all tools
server.collect(*gmail_tools)

# Export for Dedalus deployment
app = server


if __name__ == "__main__":
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(server.serve(port=8080))
