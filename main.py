# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server

Provides Gmail access through LIAM's CASA-compliant OAuth infrastructure.
Users authenticate via LIAM, and all Gmail API calls are routed through
LIAM's backend to preserve security and compliance.

Deployment: Dedalus Labs Marketplace
"""

import os
from typing import Optional

from dedalus_mcp import MCPServer, Connection, OAuthConfig
from dedalus_mcp.server import TransportSecuritySettings


# =============================================================================
# Configuration
# =============================================================================

# LIAM API base URL
# Dev: liam1-dev, Prod: liam-ai-assistant
LIAM_PROJECT_ID = os.getenv("LIAM_PROJECT_ID", "liam1-dev")
LIAM_API_BASE = os.getenv("LIAM_API_BASE", f"https://us-central1-{LIAM_PROJECT_ID}.cloudfunctions.net")

# Dedalus Authorization Server
DEDALUS_AS_URL = os.getenv("DEDALUS_AS_URL", "https://as.dedaluslabs.ai")


# =============================================================================
# Connection Setup
# =============================================================================

# Connection to LIAM backend
# LIAM acts as the OAuth provider - users authenticate with Google through LIAM
# account_type=mcp tells LIAM to create a lightweight MCP account (no Gmail watch)
liam = Connection(
    name="LIAM_ACCESS_TOKEN",
    oauth=OAuthConfig(
        client_id=os.getenv("LIAM_MCP_CLIENT_ID", ""),
        client_secret=os.getenv("LIAM_MCP_CLIENT_SECRET", ""),
        authorize_url=f"{LIAM_API_BASE}/authorize?account_type=mcp",
        token_url=f"{LIAM_API_BASE}/token",
        scopes=["gmail.readonly"],
    ),
)


def create_server() -> MCPServer:
    """Create MCP server with current env config."""
    return MCPServer(
        name="liam-gmail",
        connections=[liam],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        authorization_server=DEDALUS_AS_URL,
    )


# =============================================================================
# Gmail Tools
# =============================================================================

# Tool collection for server.collect()
gmail_tools = []


def tool(tags=None, readOnlyHint=True):
    """Decorator to register tools and add metadata."""
    def decorator(func):
        func._tool_tags = tags or []
        func._tool_readonly = readOnlyHint
        gmail_tools.append(func)
        return func
    return decorator


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_list_messages(
    ctx,
    max_results: int = 10,
    query: Optional[str] = None,
    page_token: Optional[str] = None,
) -> str:
    """
    List recent emails from the user's Gmail inbox.

    Args:
        max_results: Maximum number of emails to return (1-100, default: 10)
        query: Gmail search query (e.g., "from:boss@company.com is:unread")
        page_token: Pagination token for fetching the next page of results

    Returns:
        JSON with messages list, next_page_token, and result_size_estimate
    """
    params = {"max": str(max_results)}
    if query:
        params["q"] = query
    if page_token:
        params["pageToken"] = page_token

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailListMessages",
        params=params,
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_get_message(ctx, message_id: str) -> str:
    """
    Get the full content of a specific email by its message ID.

    Args:
        message_id: The Gmail message ID to retrieve

    Returns:
        Full email content including headers, body (plain and HTML), and metadata
    """
    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailGetMessage",
        params={"id": message_id},
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_search_messages(
    ctx,
    query: str,
    max_results: int = 20,
    page_token: Optional[str] = None,
) -> str:
    """
    Search emails using Gmail's powerful query syntax.

    Args:
        query: Gmail search query. Examples:
            - "from:john@example.com" - Emails from a specific sender
            - "subject:meeting" - Emails with subject containing "meeting"
            - "is:unread" - Unread emails
            - "has:attachment" - Emails with attachments
            - "after:2024/01/01 before:2024/12/31" - Date range
            - "in:inbox -category:promotions" - Inbox excluding promotions
        max_results: Maximum results to return (1-100, default: 20)
        page_token: Pagination token for next page

    Returns:
        JSON with matching messages and pagination info
    """
    params = {"q": query, "max": str(max_results)}
    if page_token:
        params["pageToken"] = page_token

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailSearch",
        params=params,
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_list_threads(
    ctx,
    max_results: int = 10,
    query: Optional[str] = None,
    page_token: Optional[str] = None,
) -> str:
    """
    List email conversation threads from the user's inbox.

    Threads group related emails together (replies, forwards in the same conversation).

    Args:
        max_results: Maximum threads to return (1-100, default: 10)
        query: Gmail search query to filter threads
        page_token: Pagination token for next page

    Returns:
        JSON with thread IDs, snippets, and pagination info
    """
    params = {"max": str(max_results)}
    if query:
        params["q"] = query
    if page_token:
        params["pageToken"] = page_token

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailListThreads",
        params=params,
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_get_thread(ctx, thread_id: str) -> str:
    """
    Get a full email thread with all messages in the conversation.

    Args:
        thread_id: The Gmail thread ID to retrieve

    Returns:
        Full thread with all messages in chronological order
    """
    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailGetThread",
        params={"id": thread_id},
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_list_labels(ctx) -> str:
    """
    List all Gmail labels in the user's account.

    Labels include both system labels (INBOX, SENT, SPAM, etc.) and user-created labels.

    Returns:
        JSON with list of labels including IDs, names, and types
    """
    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailListLabels",
    )
    return response.text


@tool(tags=["gmail"], readOnlyHint=True)
async def gmail_get_profile(ctx) -> str:
    """
    Get the connected Gmail account profile information.

    Returns:
        Account info including email address and total message/thread counts
    """
    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailGetProfile",
    )
    return response.text


# =============================================================================
# Server Entry Point
# =============================================================================

async def main() -> None:
    """Start MCP server."""
    server = create_server()
    server.collect(*gmail_tools)
    await server.serve(port=8080)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
