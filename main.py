# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server

Provides Gmail access through LIAM's CASA-compliant OAuth infrastructure.
Users authenticate via LIAM (which wraps Google OAuth), and all Gmail API
calls are routed through LIAM's backend where tokens are securely stored.

OAuth Flow:
1. User triggers a Gmail tool
2. MCP needs LIAM_ACCESS_TOKEN (JWT)
3. User is redirected to LIAM's /authorize → Google OAuth
4. After auth, LIAM's /token issues a JWT
5. JWT is stored and injected into requests to LIAM backend
6. LIAM backend uses stored Google tokens to access Gmail

Deployment: Dedalus Labs Marketplace
"""

import json
from typing import Optional

from dedalus_mcp import (
    MCPServer,
    tool,
    Context,
    Connection,
    SecretKeys,
    HttpMethod,
    HttpRequest,
)
from dedalus_mcp.server import TransportSecuritySettings


# =============================================================================
# Configuration
# =============================================================================

# LIAM Backend - where Gmail API calls are proxied through
LIAM_API_BASE = "https://us-central1-liam1-dev.cloudfunctions.net"

# LIAM Authorization Server - handles OAuth flow
# This is where Dedalus should send users to authenticate
LIAM_AUTH_BASE = LIAM_API_BASE  # Same base, endpoints: /authorize, /callback, /token


# =============================================================================
# Connection Setup
# =============================================================================

# Connection to LIAM backend
# LIAM_ACCESS_TOKEN is a JWT issued by LIAM's /token endpoint
# Dedalus should configure OAuth with:
#   - Authorization URL: {LIAM_AUTH_BASE}/authorize
#   - Token URL: {LIAM_AUTH_BASE}/token
#   - Requires: client_secret (MCP_CLIENT_SECRET), account_type=mcp
liam = Connection(
    name="liam",
    secrets=SecretKeys(token="LIAM_ACCESS_TOKEN"),
    base_url=LIAM_API_BASE,
)


# =============================================================================
# Gmail Tools
# =============================================================================


@tool()
async def gmail_list_messages(
    ctx: Context,
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
    params = [f"max={max_results}"]
    if query:
        params.append(f"q={query}")
    if page_token:
        params.append(f"pageToken={page_token}")

    path = "/mcpGmailListMessages"
    if params:
        path = f"{path}?{'&'.join(params)}"

    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path=path)
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_get_message(ctx: Context, message_id: str) -> str:
    """
    Get the full content of a specific email by its message ID.

    Args:
        message_id: The Gmail message ID to retrieve

    Returns:
        Full email content including headers, body (plain and HTML), and metadata
    """
    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path=f"/mcpGmailGetMessage?id={message_id}")
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_search_messages(
    ctx: Context,
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
    params = [f"q={query}", f"max={max_results}"]
    if page_token:
        params.append(f"pageToken={page_token}")

    path = f"/mcpGmailSearch?{'&'.join(params)}"

    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path=path)
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_list_threads(
    ctx: Context,
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
    params = [f"max={max_results}"]
    if query:
        params.append(f"q={query}")
    if page_token:
        params.append(f"pageToken={page_token}")

    path = "/mcpGmailListThreads"
    if params:
        path = f"{path}?{'&'.join(params)}"

    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path=path)
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_get_thread(ctx: Context, thread_id: str) -> str:
    """
    Get a full email thread with all messages in the conversation.

    Args:
        thread_id: The Gmail thread ID to retrieve

    Returns:
        Full thread with all messages in chronological order
    """
    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path=f"/mcpGmailGetThread?id={thread_id}")
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_list_labels(ctx: Context) -> str:
    """
    List all Gmail labels in the user's account.

    Labels include both system labels (INBOX, SENT, SPAM, etc.) and user-created labels.

    Returns:
        JSON with list of labels including IDs, names, and types
    """
    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path="/mcpGmailListLabels")
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


@tool()
async def gmail_get_profile(ctx: Context) -> str:
    """
    Get the connected Gmail account profile information.

    Returns:
        Account info including email address and total message/thread counts
    """
    response = await ctx.dispatch(
        liam,
        HttpRequest(method=HttpMethod.GET, path="/mcpGmailGetProfile")
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


# =============================================================================
# Server Entry Point
# =============================================================================


def create_server() -> MCPServer:
    """Create MCP server with LIAM connection."""
    return MCPServer(
        name="gmail-mcp",  # Must match deployment slug
        connections=[liam],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
        # authorization_server=LIAM_AUTH_BASE,  # TODO: Enable once LIAM has .well-known endpoint
    )


def create_app():
    """Create and configure the MCP server for deployment."""
    server = create_server()
    server.collect(
        gmail_list_messages,
        gmail_get_message,
        gmail_search_messages,
        gmail_list_threads,
        gmail_get_thread,
        gmail_list_labels,
        gmail_get_profile,
    )
    return server


# Create server instance for Dedalus deployment
server = create_app()
app = server  # Alias for Dedalus entrypoint


async def main() -> None:
    """Start MCP server locally."""
    print("Starting LIAM Gmail MCP server...")
    print(f"LIAM API Base: {LIAM_API_BASE}")
    print("Server will be available at: http://127.0.0.1:8080/mcp")
    await server.serve(port=8080)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
