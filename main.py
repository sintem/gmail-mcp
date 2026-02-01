# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server

Provides Gmail access through LIAM's CASA-compliant OAuth infrastructure.
Users authenticate via LIAM, and all Gmail API calls go through LIAM backend.

Deployed on Dedalus marketplace as: sintem/gmail-mcp
"""

import httpx
from dedalus_mcp import MCPServer, tool, SecretKeys
from pydantic import Field


# LIAM Backend Configuration
LIAM_API_BASE = "https://us-central1-liam1-dev.cloudfunctions.net"


# Helper to call LIAM backend with user's JWT
async def call_liam_api(endpoint: str, secrets: SecretKeys, params: dict = None) -> dict:
    """Call LIAM backend MCP endpoint with user's access token."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{LIAM_API_BASE}/{endpoint}",
            headers={"Authorization": f"Bearer {secrets.access_token}"},
            params=params or {},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()


# Gmail Tools

@tool(description="Get your Gmail profile information including email address and message counts")
async def gmail_get_profile(secrets: SecretKeys) -> dict:
    """Get the user's Gmail profile."""
    return await call_liam_api("mcpGmailGetProfile", secrets)


@tool(description="List emails from your inbox with optional search query")
async def gmail_list_messages(
    secrets: SecretKeys,
    query: str = Field(default="in:inbox", description="Gmail search query (e.g., 'is:unread', 'from:boss@company.com')"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of messages to return"),
) -> dict:
    """List emails matching the query."""
    return await call_liam_api("mcpGmailListMessages", secrets, {
        "q": query,
        "max": max_results,
    })


@tool(description="Get full content of a specific email by its ID")
async def gmail_get_message(
    secrets: SecretKeys,
    message_id: str = Field(description="The Gmail message ID"),
) -> dict:
    """Get a specific email message."""
    return await call_liam_api(f"mcpGmailGetMessage/{message_id}", secrets)


@tool(description="List email threads/conversations with optional search")
async def gmail_list_threads(
    secrets: SecretKeys,
    query: str = Field(default="in:inbox", description="Gmail search query"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum number of threads to return"),
) -> dict:
    """List email threads."""
    return await call_liam_api("mcpGmailListThreads", secrets, {
        "q": query,
        "max": max_results,
    })


@tool(description="Get a full email thread/conversation with all messages")
async def gmail_get_thread(
    secrets: SecretKeys,
    thread_id: str = Field(description="The Gmail thread ID"),
    include_html: bool = Field(default=False, description="Include HTML body content"),
) -> dict:
    """Get a specific email thread with all messages."""
    return await call_liam_api(f"mcpGmailGetThread/{thread_id}", secrets, {
        "includeHtml": str(include_html).lower(),
    })


@tool(description="List all Gmail labels (folders/categories)")
async def gmail_list_labels(
    secrets: SecretKeys,
    include_stats: bool = Field(default=False, description="Include message counts for each label"),
) -> dict:
    """List Gmail labels."""
    return await call_liam_api("mcpGmailListLabels", secrets, {
        "includeStats": str(include_stats).lower(),
    })


@tool(description="Search emails using Gmail's powerful query syntax")
async def gmail_search(
    secrets: SecretKeys,
    query: str = Field(description="Gmail search query (e.g., 'subject:meeting after:2024/01/01 has:attachment')"),
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results"),
) -> dict:
    """Search emails using Gmail query syntax."""
    return await call_liam_api("mcpGmailSearch", secrets, {
        "q": query,
        "max": max_results,
    })


# Create MCP Server with LIAM as OAuth authorization server
server = MCPServer(
    "gmail-mcp",
    authorization_server=LIAM_API_BASE,
)

# Register all tools
server.collect(gmail_get_profile)
server.collect(gmail_list_messages)
server.collect(gmail_get_message)
server.collect(gmail_list_threads)
server.collect(gmail_get_thread)
server.collect(gmail_list_labels)
server.collect(gmail_search)

# Export for Dedalus deployment
app = server


if __name__ == "__main__":
    import asyncio
    asyncio.run(server.serve(port=8080))
