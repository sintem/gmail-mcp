# LIAM Gmail MCP

Secure Gmail access powered by LIAM's CASA-compliant OAuth infrastructure. Search emails, read messages, browse threads, and list labels—all through LIAM's enterprise-grade backend.

**Deployed on Dedalus**: `sintem/gmail-mcp`

## Architecture

```
User → LIAM Web App → Authenticate → Get JWT
                                        ↓
run.py → Credential(token=JWT) → Dedalus → MCP Server → LIAM Backend → Gmail API
```

- Users authenticate via LIAM (doitliam.com)
- MCP server receives JWT tokens via Dedalus Credential mechanism
- All Gmail API calls go through LIAM backend (RS256 JWT verification)
- OAuth is handled by LIAM, not at the MCP level

## Tools

### Profile
- `gmail_get_profile` - Get Gmail profile (email address, message counts)

### Messages
- `gmail_list_messages` - List emails with optional search query
- `gmail_get_message` - Get full content of a specific email by ID
- `gmail_search` - Search emails using Gmail query syntax

### Threads
- `gmail_list_threads` - List email threads/conversations
- `gmail_get_thread` - Get full thread with all messages

### Labels
- `gmail_list_labels` - List all Gmail labels (folders/categories)

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

- Python 3.10+
- Dedalus API key (from dedaluslabs.ai)
- LIAM access token (JWT from doitliam.com)

### Environment Variables

Create `.env` file:

```bash
# Required for Dedalus API
DEDALUS_API_KEY=dsk-live-your-key-here

# Required for LIAM authentication
# Get from LIAM web app: DevTools > Application > Local Storage > accessToken
LIAM_ACCESS_TOKEN=eyJhbGciOiJSUzI1NiIs...

# Optional: MCP server name (defaults to sintem/gmail-mcp)
MCP_SERVER=sintem/gmail-mcp
```

### Running Locally

```bash
cd gmail-liam-mcp
uv sync
python run.py
```

Example session:
```
Gmail MCP Agent (type 'quit' to exit)
MCP Server: sintem/gmail-mcp
LIAM Token: eyJhbGciOiJSUzI1Ni...

You: Show me my unread emails
Agent: You have 3 unread emails...

You: quit
```

### Deploying to Dedalus

```bash
dedalus deploy
```

## Project Structure

```
gmail-liam-mcp/
├── main.py          # MCP server (tools + LIAM connection)
├── run.py           # Test runner with Dedalus SDK
├── pyproject.toml   # Dependencies
├── .env             # Environment variables (not committed)
└── README.md
```

## Key Implementation Details

### Connection Setup (main.py)

```python
from dedalus_mcp import MCPServer, tool, HttpMethod, HttpRequest, get_context
from dedalus_mcp.auth import Connection, SecretKeys
from dedalus_mcp.server import AuthorizationConfig, TransportSecuritySettings

# Connection to LIAM backend
liam = Connection(
    name="liam",
    secrets=SecretKeys(token="LIAM_ACCESS_TOKEN"),
    base_url="https://us-central1-liam1-dev.cloudfunctions.net",
    auth_header_format="Bearer {api_key}",
)

# MCP Server with OAuth disabled (tokens passed via Credential)
server = MCPServer(
    name="gmail-mcp",
    connections=[liam],
    http_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
    authorization=AuthorizationConfig(enabled=False),
)
```

### Credential Passing (run.py)

```python
from dedalus_labs.types import Credential

credentials = [
    Credential(
        connection_name="liam",  # Matches Connection(name="liam")
        values={"token": liam_token}  # Matches SecretKeys(token=...)
    )
]

response = await runner.run(
    input=prompt,
    mcp_servers=["sintem/gmail-mcp"],
    credentials=credentials,
)
```

## Security

- LIAM issues RS256 JWTs (asymmetric signing)
- JWKS endpoint available at `/.well-known/jwks.json` for token verification
- Google credentials encrypted at rest (AES-256-GCM)
- OAuth tokens never touch MCP server directly
- All API calls authenticated via LIAM backend

## Support

- Email: support@doitliam.com

## License

MIT License
