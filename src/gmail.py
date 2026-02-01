# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""Gmail tools using LIAM backend.

All Gmail API calls go through LIAM backend which holds the Google OAuth tokens.
The MCP server receives a LIAM JWT via OAuth flow.
"""

import os

from pydantic import Field

from dedalus_mcp import HttpMethod, HttpRequest, get_context, tool
from dedalus_mcp.auth import Connection, SecretKeys


# LIAM backend URL (via Cloudflare Worker for .well-known routing)
LIAM_API_URL = os.getenv("LIAM_API_URL", "https://api-dev.doitliam.com")

# Connection to LIAM backend
# Token is provided via OAuth flow (LIAM issues JWT after Google auth)
gmail = Connection(
    name="gmail-mcp",
    secrets=SecretKeys(token="access_token"),
    base_url=LIAM_API_URL,
    auth_header_format="Bearer {api_key}",
)


async def _req(method: HttpMethod, path: str) -> dict:
    """Make request to LIAM backend."""
    ctx = get_context()
    request = HttpRequest(method=method, path=path)
    response = await ctx.dispatch("gmail-mcp", request)

    if response.success:
        return response.response.body or {}

    error_msg = response.error.message if response.error else "Request failed"
    raise Exception(error_msg)


# --- Profile ---

@tool(description="Get Gmail profile information (email address, message counts)")
async def gmail_get_profile() -> dict:
    """Get the authenticated user's Gmail profile."""
    return await _req(HttpMethod.GET, "/mcpGmailGetProfile")


# --- Messages ---

@tool(description="List emails with optional search query")
async def gmail_list_messages(
    query: str = Field(default="in:inbox", description="Gmail search query"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum messages"),
) -> dict:
    """List emails matching the search query."""
    return await _req(HttpMethod.GET, f"/mcpGmailListMessages?q={query}&max={max_results}")


@tool(description="Get full content of a specific email by ID")
async def gmail_get_message(
    message_id: str = Field(description="The Gmail message ID"),
) -> dict:
    """Get a specific email message with full content."""
    return await _req(HttpMethod.GET, f"/mcpGmailGetMessage/{message_id}")


@tool(description="Search emails using Gmail query syntax")
async def gmail_search(
    query: str = Field(description="Gmail search query"),
    max_results: int = Field(default=20, ge=1, le=100, description="Maximum results"),
) -> dict:
    """Search emails using Gmail query syntax."""
    return await _req(HttpMethod.GET, f"/mcpGmailSearch?q={query}&max={max_results}")


# --- Threads ---

@tool(description="List email threads/conversations")
async def gmail_list_threads(
    query: str = Field(default="in:inbox", description="Gmail search query"),
    max_results: int = Field(default=10, ge=1, le=100, description="Maximum threads"),
) -> dict:
    """List email threads matching the query."""
    return await _req(HttpMethod.GET, f"/mcpGmailListThreads?q={query}&max={max_results}")


@tool(description="Get a full email thread with all messages")
async def gmail_get_thread(
    thread_id: str = Field(description="The Gmail thread ID"),
) -> dict:
    """Get a specific email thread with all messages."""
    return await _req(HttpMethod.GET, f"/mcpGmailGetThread/{thread_id}")


# --- Labels ---

@tool(description="List all Gmail labels (folders/categories)")
async def gmail_list_labels() -> dict:
    """List all Gmail labels."""
    return await _req(HttpMethod.GET, "/mcpGmailListLabels")


# Export all tools
gmail_tools = [
    gmail_get_profile,
    gmail_list_messages,
    gmail_get_message,
    gmail_search,
    gmail_list_threads,
    gmail_get_thread,
    gmail_list_labels,
]
