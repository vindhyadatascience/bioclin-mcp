# Bioclin MCP Server 🧬

A Model Context Protocol (MCP) server for the Bioclin bioinformatics API with **secure automated browser authentication**.

> **Key Feature**: Log in via browser - never expose credentials to the LLM! 🔒

## Quick Start

**Choose your installation method:**
- 🐳 **[Docker](#option-1-docker-recommended-)** - Best for production, complete isolation
- ⚡ **[uv (Astral)](#option-2-local-python-with-uv)** - Ultra-fast, modern Python tooling ([Full uv guide →](QUICKSTART_UV.md))
- 🐍 **[pip/venv](#alternative-traditional-pipvenv-installation)** - Traditional Python setup

### Option 1: Docker (Recommended) 🐳

**Docker-only setup - no Python installation required!**

```bash
# 1. Clone and build
git clone https://github.com/vindhyadatascience/bioclin-mcp.git
cd bioclin-mcp
docker build -t bioclin-mcp:latest .

# 2. Authenticate (Docker CLI method)
# Option A: Interactive script (recommended)
./docker-login.sh

# Option B: Direct command with environment variables
docker run --rm \
  -e BIOCLIN_EMAIL="your@email.com" \
  -e BIOCLIN_PASSWORD="your-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli

# 3. Run with Docker Compose
docker-compose up --build

# Or run manually:
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json:ro \
  bioclin-mcp:latest
```

**Alternative: Browser-based login (requires Python on host)**
```bash
# If you prefer browser login, install Python deps on your Mac with uv:
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install playwright
uv tool install httpx
uvx playwright install chromium
python src/bioclin_auth.py login  # Browser opens
```

### Option 2: Local Python (with uv)

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone and setup
git clone https://github.com/vindhyadatascience/bioclin-mcp.git
cd bioclin-mcp

# 3. Install dependencies with uv
uv sync
uv run playwright install chromium

# 4. Authenticate
uv run python src/bioclin_auth.py login
# Browser opens → log in → done!

# 5. Run server
uv run fastmcp run src/bioclin_fastmcp.py
```

<details>
<summary><b>Alternative: Traditional pip/venv installation</b></summary>

```bash
# 1. Install
git clone https://github.com/vindhyadatascience/bioclin-mcp.git
cd bioclin-mcp

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
playwright install chromium

# 4. Authenticate
python src/bioclin_auth.py login

# 5. Run server
fastmcp run src/bioclin_fastmcp.py
```
</details>

## Features

- 🔐 **Secure Browser Login** - Automated with Playwright, no credentials to LLM
- ⚡ **46+ API Tools** - Full Bioclin API coverage
- 🤖 **Claude Desktop Ready** - Seamless integration
- 💾 **Session Management** - 7-day persistence
- 🎯 **FastMCP** - Modern, fast MCP implementation

## Authentication

### Option 1: Browser Login (Recommended) ⭐

```bash
$ python src/bioclin_auth.py login

Choose login method:
  1. Browser (recommended) - Automated login
  2. CLI - Enter credentials in terminal

Enter choice [1]: 1

🌐 Bioclin Automated Browser Login
✓ Browser window opens
✓ You log in on official Bioclin website
✓ Session captured automatically
✓ Browser closes
✅ Done! Session saved for 7 days
```

**Why this is secure:**
- ✅ Credentials entered directly on bioclin.vindhyadatascience.com
- ✅ Never exposed to LLM or stored in plaintext
- ✅ Only session tokens saved locally

### Option 2: CLI Login

```bash
$ python src/bioclin_auth.py login
Enter choice [2]: 2
Email: your@email.com
Password: ••••••••
✅ Login successful!
```

**[Full Authentication Guide →](docs/AUTHENTICATION.md)**

## Claude Desktop Setup

### 1. Add to Configuration

Edit your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

**Using Docker (Recommended)**:
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "${HOME}/.bioclin_session.json:/root/.bioclin_session.json:ro",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

**Using Local Python with uv**:
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/bioclin-mcp",
        "run",
        "fastmcp",
        "run",
        "src/bioclin_fastmcp.py"
      ]
    }
  }
}
```

**Using Local Python (traditional)**:
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "fastmcp",
      "args": ["run", "/absolute/path/to/bioclin-mcp/src/bioclin_fastmcp.py"]
    }
  }
}
```

### 2. Restart Claude Desktop

### 3. Test It

Ask Claude:
- *"Do I have an active Bioclin session?"*
- *"Show me my Bioclin projects"*

If not authenticated, Claude will trigger the browser login automatically!

```mermaid
sequenceDiagram
    User->>Claude: Show my projects
    Claude->>MCP: bioclin_check_session()
    MCP-->>Claude: not_authenticated
    Claude->>MCP: bioclin_browser_login_auto()
    MCP->>Browser: Open & wait for login
    Browser-->>User: Login page
    User->>Browser: Enter credentials
    Browser->>MCP: Session captured!
    Claude->>MCP: bioclin_list_projects()
    MCP-->>Claude: Projects data
    Claude-->>User: Here are your projects...
```

## Available Tools

### Authentication & Session
- `bioclin_check_session()` - Check if authenticated
- `bioclin_browser_login_auto()` - Automated browser login
- `bioclin_login()` - Direct credential login (fallback)
- `bioclin_logout()` - Clear session
- `bioclin_token_validate()` - Validate token
- `bioclin_token_refresh()` - Refresh token

### User Management (11 tools)
Create, read, update users | Admin operations | Password recovery

### Organization Management (6 tools)
Create orgs | Manage members | Switch active org

### Project Management (8 tools)
Create projects | List projects | Configure parameters

### Run Management (5 tools)
Create runs | Track status | View results

### Analysis Types & Parameters (8 tools)
Define reusable analysis types | Configure parameters

### Google Cloud Storage (3 tools)
Generate signed URLs | Download files | Access reports

**Total: 46+ tools** | [See complete list in code →](src/bioclin_fastmcp.py)

## Usage Examples

### Example 1: First Time Use

```
You: "I need to work with Bioclin"

Claude: Let me check if you're authenticated...
        [Checks session - not authenticated]
        I'll start the automated login process.
        [Terminal window opens with browser]

You: [Log in via browser]

Claude: Perfect! You're now authenticated.
        What would you like to do with Bioclin?

You: "Show me my projects"

Claude: [Lists all your projects with details]
```

### Example 2: Create and Run Analysis

```
You: "Create a project called 'RNA-Seq Study'"

Claude: [Creates project]
        Created project "RNA-Seq Study" (ID: abc-123)

You: "Create a run for this project"

Claude: [Creates run]
        Run created successfully. Status: PENDING

You: "What's the status now?"

Claude: [Checks run status]
        Status: RUNNING - Your analysis is in progress
```

## File Structure

```
bioclin-mcp/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose config
│
├── src/                         # Source code
│   ├── bioclin_fastmcp.py      # Main MCP server (FastMCP)
│   ├── bioclin_auth.py         # Authentication (Browser + CLI)
│   ├── bioclin_mcp_server.py   # Legacy MCP server
│   └── bioclin_schemas.py      # Pydantic schemas
│
├── docs/                        # Documentation
│   ├── AUTHENTICATION.md       # Browser/CLI authentication guide
│   └── DOCKER_AUTH.md          # Docker-specific authentication
│
├── scripts/                     # Utility scripts
│   └── build.sh                # Docker build helper
│
├── config/                      # Claude Desktop configuration
│   └── claude-desktop-config.json  # All 3 methods (Docker/uv/pip)
│
├── tests/                       # Test files
│   └── test_schemas.py
│
└── examples/                    # Usage examples
    └── example_usage.py
```

## Requirements

**Python:** 3.11 or higher

**Dependencies** (automatically installed via `uv sync` or `pip install -r requirements.txt`):
```txt
fastmcp>=0.2.0
httpx>=0.24.0
playwright>=1.40.0      # For automated browser login
pydantic>=2.0.0
```

**Installation methods:**
- **uv** (recommended): `uv sync` - Fast, modern, automatic
- **pip**: `pip install -r requirements.txt` - Traditional
- **Docker**: No local Python needed - everything in container

## Session Management

Sessions are stored in `~/.bioclin_session.json`:

```json
{
  "cookies": { "access_token": "...", "csrf_token": "...", "refresh_token": "..." },
  "user": { "email": "user@example.com", "username": "username", "id": "uuid" },
  "created_at": "2025-10-23T14:17:13",
  "expires_at": "2025-10-30T14:17:13"
}
```

- **Permissions**: `0o600` (owner-only read/write)
- **Expiration**: 7 days
- **Commands**: `status`, `login`, `logout`

## Environment Variables

```bash
# For Docker/automation (CLI login without prompts)
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your-password"

# Optional: Override default API URL
export BIOCLIN_API_URL="https://your-instance.com/api/v1"
```

Default API URL: `https://bioclin.vindhyadatascience.com/api/v1`

## Troubleshooting

### Browser doesn't open

```bash
# Check Playwright
pip show playwright
playwright install chromium

# Or use CLI method
python src/bioclin_auth.py login  # Choose option 2
```

### Session expires

```bash
# Sessions last 7 days - just log in again
python src/bioclin_auth.py login
```

### Session file is a directory

**Problem**: Docker creates `~/.bioclin_session.json` as a directory if it doesn't exist

**Fix**:
```bash
# Remove the directory
rm -rf ~/.bioclin_session.json

# Use the helper script (it handles this automatically)
./docker-login.sh
```

### MCP not connecting

```bash
# Verify config path is absolute
# Check Claude Desktop config syntax
# Restart Claude Desktop completely
```

**[More troubleshooting →](docs/AUTHENTICATION.md#troubleshooting)**

## Docker Deployment

```bash
# Build
docker build -t bioclin-mcp:latest .

# Run
docker run -it --rm bioclin-mcp:latest
```

**[Full Docker guide →](docs/DOCKER.md)**

## Security

- 🔒 Credentials entered only on official Bioclin website
- 🔒 Never logged or exposed to LLM
- 🔒 Session file secured with `0o600` permissions
- 🔒 Auto-expiration after 7 days
- 🔒 HTTPS-only API communication
- 🔒 Token-based authentication (no password storage)

## Contributing

Contributions welcome! Please:
- Maintain security best practices
- Add tests for new features
- Update documentation
- Follow existing code style

## Documentation

- **[AUTHENTICATION.md](docs/AUTHENTICATION.md)** - Complete auth guide with Mermaid diagrams
- **[DOCKER.md](docs/DOCKER.md)** - Docker deployment
- **[bioclin_fastmcp.py](src/bioclin_fastmcp.py)** - Source code with tool definitions

## Version

**v1.1.0** - Automated Browser Authentication

### Changelog

**v1.1.0** (2025-10-23)
- ✨ Automated browser-based authentication with Playwright
- ✨ New `bioclin_browser_login_auto()` MCP tool
- ✨ macOS Terminal.app integration for visible GUI
- 🔒 Enhanced security - no credential exposure to LLM
- 🎯 Seamless Claude Desktop integration
- 📝 Comprehensive documentation with Mermaid diagrams

**v1.0.0** (Initial Release)
- 🎉 Initial Bioclin MCP server
- 46+ API tools
- FastMCP implementation
- Basic authentication support

## License

MIT License

## Support

- **Issues**: [GitHub Issues](https://github.com/vindhyadatascience/bioclin-mcp/issues)
- **Bioclin API**: Contact your Bioclin administrator
- **MCP Protocol**: https://modelcontextprotocol.io

---

Made with ❤️ for bioinformatics research

**🔒 Secure by Design** | **⚡ Fast & Modern** | **🤖 Claude Desktop Ready**
