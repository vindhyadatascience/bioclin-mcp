# MCPX Configuration for Bioclin MCP Server

This directory contains the configuration files for MCPX, which acts as a gateway/aggregator for the Bioclin MCP server.

## Files

- **app.yaml** - Main MCPX configuration (permissions, auth, environment)
- **mcp.json** - MCP server registry (defines how to connect to Bioclin MCP server)
- **.env.template** - Environment variable template (copy to `.env` for local use)
- **.gitignore** - Git ignore rules for secrets

## Quick Start (Local Testing)

1. **Copy environment template:**
   ```bash
   cp .env.template .env
   # Edit .env with your values if needed
   ```

2. **Build Bioclin Docker image (if not already built):**
   ```bash
   cd ..
   docker build -t bioclin-mcp:latest .
   ```

3. **Run MCPX with Docker:**
   ```bash
   docker run --rm --pull always \
     --privileged \
     -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -p 9000:9000 \
     -p 5173:5173 \
     -p 9001:9001 \
     -p 3000:3000 \
     --env-file mcpx-config/.env \
     --name mcpx \
     us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
   ```

4. **Access MCPX Control Plane:**
   - Open browser to http://localhost:5173
   - Verify Bioclin server appears
   - Check that all 44 tools are listed

## Configuration Details

### Permissions (app.yaml)

Permissions control which consumers can access which tools:

```yaml
permissions:
  consumers:
    Claude:        # Consumer tag for Claude Desktop
      allow: ["*"] # Allow all tools
    Chatbot:       # Consumer tag for future chatbot
      allow: ["*"]
```

### Authentication (app.yaml)

Authentication is **disabled by default** for local testing. To enable:

```yaml
auth:
  enabled: true
  provider: auth0  # or google, stytch, workos, custom
  config:
    domain: "${AUTH0_DOMAIN}"
    clientId: "${AUTH0_CLIENT_ID}"
    clientSecret: "${AUTH0_CLIENT_SECRET}"
```

### MCP Server Registry (mcp.json)

Defines how MCPX connects to the Bioclin MCP server:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": ["run", "-i", "--rm", ...],
      "env": { ... }
    }
  }
}
```

## Port Mapping

- **9000** - MCPX HTTP API endpoint
- **5173** - MCPX Control Plane (web UI)
- **9001** - Additional MCPX service port
- **3000** - Additional MCPX service port

## Testing Connection

### From curl:
```bash
# List tools (no auth required when auth.enabled=false)
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}'
```

### From Claude Desktop:
Update your Claude Desktop config:
```json
{
  "mcpServers": {
    "mcpx": {
      "command": "npx",
      "args": [
        "mcp-remote@0.1.21",
        "http://localhost:9000/mcp",
        "--header",
        "x-lunar-consumer-tag: Claude"
      ]
    }
  }
}
```

## Security Notes

⚠️ **IMPORTANT:**
- `.env` contains secrets - never commit to git
- `auth.enabled: false` is for **local testing only**
- **Always enable auth for production deployments**
- Use Google Secret Manager for production secrets

## Next Steps

1. ✅ Configure MCPX locally
2. ⏭️ Test connection from Claude Desktop
3. ⏭️ Enable OAuth authentication
4. ⏭️ Deploy to Cloud Run

See parent directory README.md for full deployment guide.
