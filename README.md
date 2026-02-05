# LIAM Gmail MCP

Provided by LIAM (`doitliam.com`). This MCP server gives Gmail access using LIAM OAuth and Dedalus DAuth.

**Hosted on Dedalus**: `sintem/gmail-mcp`

## Auth Flow (DAuth + LIAM OAuth)

1. Client connects to the MCP server on Dedalus.
2. Dedalus DAuth handles MCP authorization; if the Gmail connection is not yet authorized, the client receives a `connect_url` to start OAuth.
3. User completes LIAM OAuth (and Google consent) in the browser.
4. Dedalus AS stores the LIAM OAuth access token and issues a JWT containing connection handles (`ddls:connections`).
5. The MCP server uses Dedalus dispatch + the connection handle to call the Gmail API.

## Tools

| Tool | Description |
|------|-------------|
| `gmail_get_profile` | Get Gmail profile (email, message/thread counts) |
| `gmail_list_messages` | List messages with optional Gmail query |
| `gmail_get_message` | Get a specific message by ID |
| `gmail_send_message` | Send an email |
| `gmail_trash_message` | Move a message to trash |
| `gmail_untrash_message` | Remove a message from trash |
| `gmail_modify_message` | Add/remove labels on a message |
| `gmail_list_threads` | List email threads |
| `gmail_get_thread` | Get a specific thread by ID |
| `gmail_trash_thread` | Move a thread to trash |
| `gmail_untrash_thread` | Remove a thread from trash |
| `gmail_modify_thread` | Add/remove labels on a thread |
| `gmail_list_labels` | List all labels |
| `gmail_get_label` | Get label details by ID |
| `gmail_create_label` | Create a new label |
| `gmail_delete_label` | Delete a user label |
| `gmail_list_drafts` | List drafts |
| `gmail_get_draft` | Get a draft by ID |
| `gmail_create_draft` | Create a draft |
| `gmail_send_draft` | Send a draft |
| `gmail_delete_draft` | Delete a draft |
| `gmail_get_attachment` | Get a message attachment |

Smoke tools (debug):

| Tool | Description |
|------|-------------|
| `smoke_echo` | Echo input (sanity check) |
| `smoke_info` | Server info (sanity check) |

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
DEDALUS_AS_URL=https://as.dedaluslabs.ai

# MCP server slug (LIAM hosted or your own)
MCP_SERVER=sintem/gmail-mcp

# Gmail API base URL (optional override)
GMAIL_API_URL=https://gmail.googleapis.com

# Optional: direct LIAM OAuth token for local testing
LIAM_ACCESS_TOKEN=liam-jwt-here
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

OAuth (recommended, uses DAuth + LIAM OAuth):
```bash
python src/_client.py
```

Manual LIAM token (advanced/testing only):
```bash
# Interactive mode
python run.py

# Single query
python run.py "show my unread emails"
```

## Project Structure

```
gmail-liam-mcp/
├── run.py            # Local test client with LIAM token
├── src/
│   ├── main.py       # MCP server (Dedalus entrypoint)
│   ├── gmail.py      # Tools (modular version)
│   ├── server.py     # Server config
│   └── _client.py    # OAuth/DAuth client example
├── pyproject.toml
├── .env.example
└── README.md
```

## License

MIT
