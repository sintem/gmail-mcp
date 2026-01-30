# LIAM Gmail

Secure Gmail access powered by CASA-compliant OAuth. Search emails, read messages, browse threads, and list labels—all through LIAM's enterprise-grade infrastructure.

## Overview

This MCP server provides Gmail access through LIAM's CASA-compliant Google OAuth infrastructure. Users authenticate via LIAM, and all Gmail API calls are routed through LIAM's backend to preserve security and compliance.

**Account Type**: Creates lightweight "mcp" accounts that provide direct API access without Gmail watch notifications or automatic draft generation.

## Tools

### Messages

- `gmail_list_messages` - List messages with search queries
- `gmail_get_message` - Get a specific message by ID
- `gmail_search_messages` - Search using Gmail query syntax

### Threads

- `gmail_list_threads` - List email threads (conversations)
- `gmail_get_thread` - Get a thread with all messages

### Labels

- `gmail_list_labels` - List all labels

### Profile

- `gmail_get_profile` - Get user's Gmail profile

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

Combine queries: `from:boss@company.com is:unread has:attachment`

## Setup

### Prerequisites

- Dedalus API key
- Python 3.10+

### Environment Variables

```
DEDALUS_API_KEY=dsk-live-your-key-here
DEDALUS_API_URL=https://api.dedaluslabs.ai
DEDALUS_AS_URL=https://as.dedaluslabs.ai
```

### Local Development

```bash
cd gmail-liam-mcp
uv sync
uv run python main.py
```

## Security

- All Gmail API calls go through LIAM's CASA-compliant backend
- Google credentials are encrypted at rest (AES-256-GCM)
- OAuth tokens never touch the MCP server directly
- Your credentials are never exposed to third parties

## Support

- Email: support@doitliam.com

## License

MIT License
