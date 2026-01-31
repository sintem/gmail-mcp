# Copyright (c) 2026 LIAM Team
# SPDX-License-Identifier: MIT

"""
LIAM Gmail MCP Server

Provides Gmail access via Google OAuth through Dedalus Labs marketplace.
Uses the same architecture as annyzhou/gmail-mcp for seamless OAuth flow.

Deployment: Dedalus Labs Marketplace
"""

import base64
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
# Connection Setup
# =============================================================================

# Connection to Gmail API
# OAuth token is managed by Dedalus - users authenticate through Google OAuth
gmail = Connection(
    name="gmail-mcp",
    secrets=SecretKeys(token="GMAIL_ACCESS_TOKEN"),
    base_url="https://gmail.googleapis.com",
)


# =============================================================================
# Helper Functions
# =============================================================================

def decode_base64(data: str) -> str:
    """Decode base64url encoded data."""
    # Add padding if needed
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")


def extract_email_body(payload: dict) -> dict:
    """Extract plain text and HTML body from email payload."""
    result = {"plain": "", "html": ""}

    def process_part(part: dict) -> None:
        mime_type = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data", "")

        if data:
            decoded = decode_base64(data)
            if mime_type == "text/plain":
                result["plain"] = decoded
            elif mime_type == "text/html":
                result["html"] = decoded

        # Recursively process nested parts
        for subpart in part.get("parts", []):
            process_part(subpart)

    process_part(payload)
    return result


def extract_headers(headers: list) -> dict:
    """Extract common headers into a dict."""
    header_dict = {}
    for h in headers:
        name = h.get("name", "").lower()
        if name in ["from", "to", "subject", "date", "cc", "bcc"]:
            header_dict[name] = h.get("value", "")
    return header_dict


def format_message(msg: dict) -> dict:
    """Format a Gmail message for output."""
    payload = msg.get("payload", {})
    headers = extract_headers(payload.get("headers", []))
    body = extract_email_body(payload)

    return {
        "id": msg.get("id"),
        "threadId": msg.get("threadId"),
        "labelIds": msg.get("labelIds", []),
        "snippet": msg.get("snippet", ""),
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "cc": headers.get("cc", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
        "body_plain": body["plain"],
        "body_html": body["html"],
    }


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
    params = [f"maxResults={max_results}"]
    if query:
        params.append(f"q={query}")
    if page_token:
        params.append(f"pageToken={page_token}")

    path = f"/gmail/v1/users/me/messages?{'&'.join(params)}"

    response = await ctx.dispatch(
        gmail,
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
    path = f"/gmail/v1/users/me/messages/{message_id}?format=full"

    response = await ctx.dispatch(
        gmail,
        HttpRequest(method=HttpMethod.GET, path=path)
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    if response.response.body:
        formatted = format_message(response.response.body)
        return json.dumps(formatted)
    return "{}"


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
    params = [f"q={query}", f"maxResults={max_results}"]
    if page_token:
        params.append(f"pageToken={page_token}")

    path = f"/gmail/v1/users/me/messages?{'&'.join(params)}"

    response = await ctx.dispatch(
        gmail,
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
    params = [f"maxResults={max_results}"]
    if query:
        params.append(f"q={query}")
    if page_token:
        params.append(f"pageToken={page_token}")

    path = f"/gmail/v1/users/me/threads?{'&'.join(params)}"

    response = await ctx.dispatch(
        gmail,
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
    path = f"/gmail/v1/users/me/threads/{thread_id}?format=full"

    response = await ctx.dispatch(
        gmail,
        HttpRequest(method=HttpMethod.GET, path=path)
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    if response.response.body:
        thread = response.response.body
        # Format each message in the thread
        if "messages" in thread:
            thread["messages"] = [format_message(msg) for msg in thread["messages"]]
        return json.dumps(thread)
    return "{}"


@tool()
async def gmail_list_labels(ctx: Context) -> str:
    """
    List all Gmail labels in the user's account.

    Labels include both system labels (INBOX, SENT, SPAM, etc.) and user-created labels.

    Returns:
        JSON with list of labels including IDs, names, and types
    """
    response = await ctx.dispatch(
        gmail,
        HttpRequest(method=HttpMethod.GET, path="/gmail/v1/users/me/labels")
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
        gmail,
        HttpRequest(method=HttpMethod.GET, path="/gmail/v1/users/me/profile")
    )

    if not response.success:
        return json.dumps({"error": response.error.message})

    return json.dumps(response.response.body) if response.response.body else "{}"


# =============================================================================
# Server Entry Point
# =============================================================================


def create_server() -> MCPServer:
    """Create MCP server with Gmail connection."""
    return MCPServer(
        name="liam-gmail",
        connections=[gmail],
        http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
        streamable_http_stateless=True,
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
# Dedalus will import this and call serve() or run() as needed
server = create_app()
app = server  # Alias for Dedalus entrypoint


async def main() -> None:
    """Start MCP server locally."""
    print("Starting LIAM Gmail MCP server...")
    print("Server will be available at: http://127.0.0.1:8080/mcp")
    await server.serve(port=8080)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
