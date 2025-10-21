# MCPX Configuration Files

**Everything MCPX needs to connect to Bioclin lives here!**

## What's in This Folder?

This directory contains the "brains" of your MCPX setup - the configuration files that tell MCPX how to work with Bioclin.

### The Files

- **app.yaml** - The main configuration file
  - Controls who can access which tools (permissions)
  - Sets up authentication (OAuth, if you want it)
  - Configures the server environment

- **mcp.json** - The server registry
  - Tells MCPX where to find the Bioclin MCP server
  - Defines how to start it up
  - Sets environment variables

- **init.sh** - Dependency installer
  - Automatically installs Python packages Bioclin needs
  - Runs when MCPX starts up

- **.env.template** - Environment variables template
  - Copy this to `.env` and add your secrets (API keys, passwords)
  - Never commit `.env` to git!

- **.gitignore** - Git safety file
  - Makes sure you don't accidentally commit secrets

**Don't worry!** You don't need to edit these files manually. The `start-mcpx.sh` script handles everything for you!

## Quick Start

**The easiest way:** Just run this from the parent directory:

```bash
cd ..
./start-mcpx.sh
```

That's it! The script automatically handles all configuration.

**Want to do it manually?** Here's how:

1. **Start MCPX**
   ```bash
   cd ..
   ./start-mcpx.sh
   ```

2. **Open the Control Plane**

   Open http://localhost:5173 in your browser

   **What to look for:**
   - ✅ "bioclin" server should be listed
   - ✅ All 44 tools should appear
   - ✅ No errors in the server status

3. **Test the Connection**
   ```bash
   ./test-mcpx-simple.sh
   ```

   **Expected:** `✅ Found all 44 Bioclin tools`

## Understanding the Configuration (Optional Reading)

**You don't need to understand this to use MCPX!** But if you're curious...

### Permissions (app.yaml)

This controls who can access Bioclin tools:

```yaml
permissions:
  consumers: {}  # Empty = everyone can access (for local testing)
```

**For production**, you can restrict access:
```yaml
permissions:
  consumers:
    Claude:        # Only Claude Desktop
      allow: ["*"]
    MyChatbot:     # And your custom chatbot
      allow: ["*"]
```

**What's a "consumer"?** It's just a tag that identifies who's making the request (like "Claude" or "MyChatbot").

### Authentication (app.yaml)

Authentication is **disabled by default** - perfect for local testing!

```yaml
auth:
  enabled: false  # No auth needed locally
```

**For production**, you can enable OAuth:
```yaml
auth:
  enabled: true
  provider: auth0  # or google, stytch, workos
  config:
    domain: "${AUTH0_DOMAIN}"
    # ... more OAuth config
```

See `auth-setup-guide.md` for detailed OAuth setup instructions.

### MCP Server Registry (mcp.json)

This tells MCPX how to start the Bioclin MCP server:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "python3",
      "args": ["/workspace/bioclin_mcp_server.py"],
      "env": {
        "BIOCLIN_API_URL": "https://bioclin.vindhyadatascience.com/api/v1"
      }
    }
  }
}
```

**Translation:** "Run this Python script, and set the Bioclin API URL as an environment variable."

## Ports Explained

When MCPX runs, it opens these ports on your computer:

- **:9000** - Main API endpoint (this is where you send requests)
- **:5173** - Control Plane web UI (the pretty dashboard)
- **:9001** - MCPX internal service
- **:3000** - MCPX metrics/monitoring

**You'll mainly use:** Port 9000 (API) and 5173 (dashboard)

## Testing Your Connection

### Quick Test with curl

```bash
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}'
```

**What this does:** Asks MCPX to list all available tools

**Expected:** A JSON response with all 44 Bioclin tools

### Using with Claude Desktop

See the main `MCPX-QUICKSTART.md` guide for complete instructions!

Short version: Add this to your Claude Desktop config:
```json
{
  "mcpServers": {
    "mcpx-bioclin": {
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

## 🔒 Security Notes

**For Local Testing:**
- ✅ Auth is disabled (no passwords needed)
- ✅ Only accessible from your computer (localhost)
- ✅ Perfect for development

**For Production:**
- ⚠️ **ALWAYS enable authentication!**
- ⚠️ Never commit `.env` files to git
- ⚠️ Use Google Secret Manager for secrets
- ⚠️ Enable OAuth 2.1 (see `auth-setup-guide.md`)

**Bottom line:** Local = no auth needed. Production = always use auth!

## What's Next?

Now that you understand the config:

1. ✅ **You've configured MCPX** - Great job!
2. 📖 **Read the full guide** - `../MCPX-QUICKSTART.md`
3. 💬 **Use with Claude** - Follow Phase 2 instructions
4. ☁️ **Deploy to cloud** - Follow Phase 4 instructions
5. 🔒 **Add OAuth** - Follow Phase 3 instructions

**Need help?** Check `../TROUBLESHOOTING.md`
