# Docker-Only Setup Guide

**Goal**: Use Bioclin MCP with Claude Desktop using **only Docker** - no Python installation required on your host machine.

## Prerequisites

- ✅ Docker Desktop installed
- ✅ Git installed
- ❌ No Python required!
- ❌ No Playwright required!

## Quick Setup

### 1. Clone and Build

```bash
git clone https://github.com/vindhyadatascience/bioclin-mcp.git
cd bioclin-mcp
docker build -t bioclin-mcp:latest .
```

### 2. Authenticate via Docker CLI

**This runs entirely in Docker - no browser, no host Python:**

```bash
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  sh -c "echo '2' | python src/bioclin_auth.py login"
```

You'll be prompted for:
- **Email**: your@email.com
- **Password**: ••••••••

Your session will be saved to `~/.bioclin_session.json` and last for 7 days.

**Or use the helper script:**

```bash
./scripts/docker-cli-login.sh
```

### 3. Configure Claude Desktop

Edit your Claude Desktop config:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "/Users/YOUR_USERNAME/.bioclin_session.json:/root/.bioclin_session.json:ro",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

**Important**: Replace `YOUR_USERNAME` with your actual macOS username!

### 4. Restart Claude Desktop

Completely quit and restart Claude Desktop.

### 5. Test It

Ask Claude:
- "Do I have an active Bioclin session?"
- "Show me my Bioclin projects"

## Docker Compose (Alternative)

If you prefer docker-compose:

```bash
docker-compose up -d
```

Then in Claude Desktop config:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "exec", "-i",
        "bioclin-mcp-server",
        "fastmcp", "run", "src/bioclin_fastmcp.py"
      ]
    }
  }
}
```

## Re-authentication After 7 Days

When your session expires:

```bash
# Clear old session
rm ~/.bioclin_session.json

# Login again via Docker
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  sh -c "echo '2' | python src/bioclin_auth.py login"
```

## Troubleshooting

### Session file not found

```bash
# Check if session exists
ls -la ~/.bioclin_session.json

# Check permissions
chmod 600 ~/.bioclin_session.json
```

### Docker can't read session file

```bash
# Make sure the path is correct in your Claude Desktop config
# Use absolute path, not ~
# Example: /Users/alex/.bioclin_session.json
```

### MCP server not connecting

```bash
# Test Docker container manually
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json:ro \
  bioclin-mcp:latest

# You should see FastMCP startup banner
```

## Architecture

```
┌─────────────────┐
│  Claude Desktop │
└────────┬────────┘
         │ (stdio)
         ↓
┌─────────────────┐     ┌──────────────────┐
│ Docker Container│────→│ ~/.bioclin_      │
│  MCP Server     │     │  session.json    │
│                 │     │  (read-only)     │
└────────┬────────┘     └──────────────────┘
         │
         ↓
   ┌─────────────┐
   │  Bioclin    │
   │  API        │
   └─────────────┘
```

## Benefits of Docker-Only Approach

✅ **No Python installation** - runs entirely in Docker
✅ **No Playwright setup** - CLI password auth instead
✅ **Consistent environment** - works the same on any machine
✅ **Easy updates** - just rebuild the Docker image
✅ **Isolated** - no conflicts with system Python
✅ **Portable** - same setup on macOS, Linux, Windows

## Security Notes

- ✅ Credentials entered in your terminal, not stored
- ✅ Only session tokens saved (not passwords)
- ✅ Session file mounted read-only in container
- ✅ Sessions auto-expire after 7 days
- ✅ HTTPS-only API communication
