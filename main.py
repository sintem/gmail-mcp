"""
LIAM Gmail MCP Server

This MCP server provides Gmail access through LIAM's CASA-compliant OAuth infrastructure.
Users authenticate via LIAM, and all Gmail API calls are routed through LIAM's backend
to preserve security and compliance.

Deployment: Dedalus Labs Marketplace
"""

import os
from dataclasses import dataclass
from typing import Optional, List

# Dedalus SDK imports (install via: pip install dedalus)
from dedalus import MCPServer, Connection, OAuthConfig, tool


# =============================================================================
# Configuration
# =============================================================================

# LIAM API base URL (production)
LIAM_API_BASE = os.getenv("LIAM_API_BASE", "https://us-central1-liam-ai-assistant.cloudfunctions.net")

# LIAM OAuth endpoints
# Note: account_type=mcp tells LIAM to create a lightweight MCP account (no Gmail watch/processing)
LIAM_AUTHORIZE_URL = f"{LIAM_API_BASE}/authorize?account_type=mcp"
LIAM_TOKEN_URL = f"{LIAM_API_BASE}/token"

# OAuth scopes (LIAM-specific, maps to Gmail permissions)
LIAM_SCOPES = os.getenv("LIAM_SCOPES", "gmail.readonly").split(",")


# =============================================================================
# Connection Setup
# =============================================================================

liam = Connection(
    name="gmail-liam",  # Must match deployment slug on Dedalus
    oauth=OAuthConfig(
        client_id=os.getenv("LIAM_MCP_CLIENT_ID"),
        client_secret=os.getenv("LIAM_MCP_CLIENT_SECRET"),
        authorize_url=LIAM_AUTHORIZE_URL,
        token_url=LIAM_TOKEN_URL,
        scopes=LIAM_SCOPES,
    ),
    auth_header_format="Bearer {access_token}",
)

server = MCPServer(
    connections=[liam],
    allow_dns_rebinding=False,
    stateless_http=True,
)


# =============================================================================
# Response Types
# =============================================================================

@dataclass
class EmailSummary:
    """Summary of an email message"""
    id: str
    thread_id: str
    snippet: str
    from_address: Optional[str]
    to_address: Optional[str]
    subject: Optional[str]
    date: Optional[str]
    labels: List[str]


@dataclass
class EmailDetail:
    """Full email content"""
    id: str
    thread_id: str
    from_address: Optional[str]
    to_address: Optional[str]
    cc: Optional[str]
    subject: Optional[str]
    date: Optional[str]
    body_plain: str
    body_html: str
    labels: List[str]
    snippet: str
    has_attachments: bool


@dataclass
class GmailProfile:
    """Gmail account profile"""
    email_address: str
    messages_total: int
    threads_total: int


# =============================================================================
# Gmail Tools
# =============================================================================

@tool(tags=["gmail"], readOnlyHint=True)
async def list_emails(
    ctx,
    max_results: int = 10,
    query: Optional[str] = None,
    page_token: Optional[str] = None,
) -> dict:
    """
    List recent emails from the user's Gmail inbox.

    Args:
        max_results: Maximum number of emails to return (1-100, default: 10)
        query: Gmail search query (e.g., "from:boss@company.com is:unread")
        page_token: Pagination token for fetching the next page of results

    Returns:
        Dictionary containing:
        - messages: List of email summaries
        - next_page_token: Token for fetching next page (if available)
        - result_size_estimate: Estimated total matching messages
    """
    params = {"max": max_results}
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

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def get_email(ctx, message_id: str) -> dict:
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
        f"{LIAM_API_BASE}/mcpGmailGetMessage/{message_id}",
    )

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def search_emails(
    ctx,
    query: str,
    max_results: int = 20,
    page_token: Optional[str] = None,
) -> dict:
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
        Dictionary containing matching messages and pagination info
    """
    params = {"q": query, "max": max_results}
    if page_token:
        params["pageToken"] = page_token

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailSearch",
        params=params,
    )

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def list_threads(
    ctx,
    max_results: int = 10,
    query: Optional[str] = None,
    page_token: Optional[str] = None,
) -> dict:
    """
    List email conversation threads from the user's inbox.

    Threads group related emails together (replies, forwards in the same conversation).

    Args:
        max_results: Maximum threads to return (1-100, default: 10)
        query: Gmail search query to filter threads
        page_token: Pagination token for next page

    Returns:
        Dictionary containing thread IDs, snippets, and pagination info
    """
    params = {"max": max_results}
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

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def get_thread(ctx, thread_id: str, include_html: bool = False) -> dict:
    """
    Get a full email thread with all messages in the conversation.

    Args:
        thread_id: The Gmail thread ID to retrieve
        include_html: Whether to include HTML body content (default: False)

    Returns:
        Full thread with:
        - threadId, subject, participants
        - All messages in chronological order
        - Message count and date range
    """
    params = {}
    if include_html:
        params["includeHtml"] = "true"

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailGetThread/{thread_id}",
        params=params,
    )

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def list_labels(ctx, include_stats: bool = False) -> dict:
    """
    List all Gmail labels in the user's account.

    Labels include both system labels (INBOX, SENT, SPAM, etc.) and user-created labels.

    Args:
        include_stats: Whether to include message/thread counts for each label

    Returns:
        Dictionary containing list of labels with their IDs, names, and types
    """
    params = {}
    if include_stats:
        params["includeStats"] = "true"

    response = await ctx.dispatch(
        liam,
        "GET",
        f"{LIAM_API_BASE}/mcpGmailListLabels",
        params=params,
    )

    return response.json()


@tool(tags=["gmail"], readOnlyHint=True)
async def get_profile(ctx) -> dict:
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

    return response.json()


# =============================================================================
# Server Entry Point
# =============================================================================

if __name__ == "__main__":
    server.run()
