# Gmail MCP Server (Powered by LIAM)

Access Gmail through LIAM's CASA-compliant Google OAuth infrastructure via the Model Context Protocol (MCP).

## Overview

This MCP server allows AI agents to interact with Gmail on behalf of authenticated users. All Gmail API calls are routed through LIAM's backend, preserving CASA compliance and security.

**Account Type**: This MCP creates lightweight "mcp" accounts that provide direct API access without Gmail watch notifications or automatic draft generation (those features are exclusive to full LIAM users).

## Features

- **List Emails** - Browse inbox messages with filtering
- **Get Email** - Retrieve full email content
- **Search Emails** - Use Gmail's powerful query syntax
- **List/Get Threads** - Work with conversation threads
- **List Labels** - Access Gmail labels and categories
- **Get Profile** - Retrieve account information

## Authentication

Users authenticate via LIAM's OAuth flow, which handles:
- Google OAuth consent
- Token storage and encryption
- Automatic token refresh
- CASA compliance

## Available Tools

### `list_emails`
List recent emails from the user's inbox.

```python
# Example: Get 20 unread emails
result = await list_emails(max_results=20, query="is:unread")
```

### `get_email`
Get full email content by message ID.

```python
# Example: Get specific email
result = await get_email(message_id="18abc123def")
```

### `search_emails`
Search using Gmail query syntax.

```python
# Example: Find emails from a specific sender this month
result = await search_emails(
    query="from:boss@company.com after:2024/01/01",
    max_results=50
)
```

### `list_threads` / `get_thread`
Work with conversation threads.

```python
# Example: Get recent threads
threads = await list_threads(max_results=10)

# Example: Get full thread with all messages
thread = await get_thread(thread_id="thread123", include_html=True)
```

### `list_labels`
Get all Gmail labels.

```python
# Example: Get labels with message counts
labels = await list_labels(include_stats=True)
```

### `get_profile`
Get Gmail account information.

```python
profile = await get_profile()
# Returns: { email_address, messages_total, threads_total }
```

## Gmail Query Syntax

The `query` parameter supports Gmail's search syntax:

| Query | Description |
|-------|-------------|
| `from:email@example.com` | From specific sender |
| `to:email@example.com` | To specific recipient |
| `subject:keyword` | Subject contains keyword |
| `is:unread` | Unread messages |
| `is:starred` | Starred messages |
| `has:attachment` | Has attachments |
| `after:2024/01/01` | After date |
| `before:2024/12/31` | Before date |
| `in:inbox` | In inbox |
| `label:custom-label` | Has specific label |
| `-category:promotions` | Exclude promotions |

Combine queries: `from:boss@company.com is:unread has:attachment`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `LIAM_MCP_CLIENT_ID` | OAuth client ID from LIAM | Yes |
| `LIAM_MCP_CLIENT_SECRET` | OAuth client secret from LIAM | Yes |
| `LIAM_API_BASE` | LIAM API base URL (default: production) | No |
| `LIAM_SCOPES` | Comma-separated scopes (default: gmail.readonly) | No |

## Deployment

### Dedalus Labs Marketplace

1. Fork this repository
2. Connect to Dedalus Dashboard
3. Configure environment variables
4. Deploy and publish

### Local Development

```bash
# Install dependencies
pip install -e .

# Run locally (requires LIAM credentials)
python main.py
```

## Security

- All Gmail API calls go through LIAM's CASA-compliant backend
- Tokens are encrypted at rest (AES-256-GCM)
- OAuth tokens never touch the MCP server directly
- Protected by Cloudflare infrastructure

## Support

- Documentation: [docs.doitliam.com](https://docs.doitliam.com)
- Issues: [GitHub Issues](https://github.com/sintem/gmail-mcp/issues)
- Email: support@doitliam.com

## License

MIT License - see LICENSE file for details.
