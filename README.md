# LIAM Gmail MCP

Gmail access through LIAM's CASA-compliant OAuth infrastructure.

**Deployed on Dedalus**: `sintem/gmail-mcp`

## OAuth Flow

```
1. User connects to MCP (via Dedalus or local client)
2. Dedalus/Client discovers LIAM OAuth via /.well-known/oauth-authorization-server
3. User is redirected to LIAM → Google OAuth
4. User authenticates with Google
5. LIAM issues JWT, user returns to MCP
6. MCP uses JWT to call LIAM backend → Gmail API
```

## Tools

| Tool | Description |
|------|-------------|
| `gmail_get_profile` | Get Gmail profile (email, message counts) |
| `gmail_list_messages` | List emails with search query |
| `gmail_get_message` | Get specific email by ID |
| `gmail_search` | Search emails with Gmail query syntax |
| `gmail_list_threads` | List email threads |
| `gmail_get_thread` | Get thread with all messages |
| `gmail_list_labels` | List all Gmail labels |

## Gmail Query Syntax

```
from:email@example.com    # From sender
to:email@example.com      # To recipient
subject:keyword           # Subject contains
is:unread                 # Unread only
is:starred                # Starred only
has:attachment            # Has attachments
after:2024/01/01          # After date
before:2024/12/31         # Before date
in:inbox                  # In inbox
```

Combine: `from:boss@company.com is:unread has:attachment`

## Setup

### 1. Environment

Create `.env`:
```bash
# Required
DEDALUS_API_KEY=dsk-live-your-key

# Optional (defaults shown)
DEDALUS_API_URL=https://api.dedaluslabs.ai
LIAM_API_URL=https://us-central1-liam1-dev.cloudfunctions.net
MCP_SERVER=sintem/gmail-mcp
```

### 2. Install

```bash
cd gmail-liam-mcp
uv sync --all-extras
```

### 3. Deploy to Dedalus

```bash
dedalus deploy
```

### 4. Test locally

```bash
# Interactive mode
python run.py

# Single query
python run.py "show my unread emails"
```

On first run, browser opens for Google OAuth via LIAM.

## Project Structure

```
gmail-liam-mcp/
├── main.py           # MCP server (Dedalus entrypoint)
├── run.py            # Local test client with OAuth
├── src/
│   ├── gmail.py      # Tools (modular version)
│   ├── server.py     # Server config
│   └── _client.py    # Full client example
├── pyproject.toml
├── .env.example
└── README.md
```

## License

MIT
