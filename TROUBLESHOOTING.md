# MCPX Bioclin Troubleshooting Guide

Common issues and solutions when running MCPX with Bioclin MCP server.

## Issue 1: Permission Denied - Docker Socket

**Error:**
```
docker: permission denied while trying to connect to the Docker daemon socket
```

**Cause:** MCPX container can't access the host Docker daemon (Docker-in-Docker issue).

**Solution:** Use Python directly instead of Docker for the Bioclin MCP server.

The configuration has been updated to use `python3` instead of `docker` in `mcp.json`.

**For local testing, use this command:**
```bash
docker run --rm --pull always \
  --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 9000:9000 \
  -p 5173:5173 \
  -e BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
```

Key changes:
- Added `-v $(pwd):/workspace` to mount current directory
- Added `-w /workspace` to set working directory
- Removed Docker socket mount (not needed)

## Issue 2: Required ToolGroup * Not Found

**Error:**
```
Required ToolGroup * not found, review config
```

**Cause:** MCPX requires wildcards to be defined as tool groups before use.

**Solution:** The `app.yaml` has been updated to define the `*` tool group:

```yaml
permissions:
  toolGroups:
    - name: "*"
      tools: ["*"]
      description: "All tools"

  consumers:
    Claude:
      allow: ["*"]  # Now references the defined tool group
```

## Issue 3: Bioclin MCP Server Not Starting

**Error:**
```
Failed to initiate client: MCP error -32000: Connection closed
```

**Possible Causes:**
1. Python dependencies not installed in MCPX container
2. Bioclin MCP server script not found
3. Python path issues

**Solution 1: Install Dependencies**

The MCPX container needs the Bioclin MCP dependencies. Create a custom setup:

```bash
# Create a startup script
cat > mcpx-config/install-deps.sh << 'EOF'
#!/bin/bash
pip3 install mcp httpx pydantic python-json-logger
EOF

chmod +x mcpx-config/install-deps.sh
```

**Solution 2: Use Sidecar Pattern (Recommended for Production)**

For Cloud Run, use the sidecar Dockerfile that includes everything:

```bash
docker build -f Dockerfile.mcpx-cloudrun -t mcpx-bioclin:latest .
docker run -p 9000:9000 -p 5173:5173 mcpx-bioclin:latest
```

This image includes:
- MCPX
- Python 3
- Bioclin MCP server files
- All dependencies pre-installed

## Issue 4: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:** Install dependencies in the MCPX container:

```bash
# Option A: Install via Docker exec (if container is running)
docker exec mcpx pip3 install mcp httpx pydantic python-json-logger

# Option B: Create custom image (better)
# See Dockerfile.mcpx-cloudrun for reference
```

## Issue 5: File Not Found

**Error:**
```
FileNotFoundError: bioclin_mcp_server.py
```

**Solution:** Ensure files are mounted correctly:

```bash
# Check the mount
docker exec mcpx ls -la /workspace

# Should see:
# bioclin_mcp_server.py
# bioclin_schemas.py
# requirements.txt
```

If files are missing, remount:
```bash
docker stop mcpx
docker run --rm --pull always \
  --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v $(pwd):/workspace \
  -w /workspace \
  -p 9000:9000 \
  -p 5173:5173 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
```

## Issue 6: Bioclin API Connection Fails

**Error:**
```
Connection refused to bioclin.vindhyadatascience.com
```

**Diagnosis:**
```bash
# Test Bioclin API directly
curl https://bioclin.vindhyadatascience.com/api/v1/docs

# Should return API documentation
```

**Solutions:**
- Check network connectivity
- Verify API URL is correct
- Check if Bioclin API is operational
- Try with VPN if behind corporate firewall

## Issue 7: MCPX Control Plane Not Loading

**Error:** Browser shows "Connection refused" at http://localhost:5173

**Solutions:**

1. **Check if port is mapped:**
   ```bash
   docker ps | grep mcpx
   # Should show: 0.0.0.0:5173->5173/tcp
   ```

2. **Check MCPX logs:**
   ```bash
   docker logs mcpx | grep 5173
   # Should see: "Accepting connections at http://localhost:5173"
   ```

3. **Try alternative port:**
   ```bash
   # Stop current container
   docker stop mcpx

   # Start with different port
   docker run ... -p 8080:5173 ...

   # Access at http://localhost:8080
   ```

## Issue 8: OAuth Authentication Errors

**Error:**
```
Invalid token / Unauthorized
```

**Solutions:**

1. **Verify token:**
   ```bash
   # Get token
   TOKEN=$(curl -s --request POST \
     --url "https://${AUTH0_DOMAIN}/oauth/token" \
     --header 'content-type: application/json' \
     --data "{
       \"client_id\":\"${AUTH0_CLIENT_ID}\",
       \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
       \"audience\":\"mcpx-bioclin\",
       \"grant_type\":\"client_credentials\"
     }" | jq -r '.access_token')

   # Decode token (check at jwt.io)
   echo $TOKEN
   ```

2. **Check audience:**
   - Token `aud` claim must match `mcpx-bioclin`
   - Update in Auth0 API settings if needed

3. **Check expiration:**
   - Tokens expire (typically 24 hours)
   - Get a fresh token

## Recommended Setup for Local Development

For the smoothest local development experience:

### Option A: Sidecar Container (Easiest)

```bash
# Build sidecar image (includes everything)
docker build -f Dockerfile.mcpx-cloudrun -t mcpx-bioclin:local .

# Run it
docker run --rm \
  -p 9000:9000 \
  -p 5173:5173 \
  -e BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1 \
  mcpx-bioclin:local
```

### Option B: Separate Containers (More flexible)

```bash
# Terminal 1: Run Bioclin MCP
python bioclin_mcp_server.py

# Terminal 2: Run MCPX pointing to local Bioclin
# Update mcp.json to use local connection
# Then: docker run ... mcpx
```

### Option C: Direct Python (No Docker)

If you have MCPX installed locally:
```bash
# Install MCPX
npm install -g @lunar/mcpx

# Run it
mcpx start --config mcpx-config/app.yaml
```

## Getting Help

### Check Logs

**MCPX logs:**
```bash
docker logs -f mcpx
```

**Bioclin MCP logs:**
```bash
# Inside MCPX container
docker exec mcpx tail -f /var/log/bioclin-mcp.log

# Or check stderr
docker logs mcpx 2>&1 | grep bioclin
```

### Test Components Separately

**Test Bioclin MCP directly:**
```bash
# Run server
python bioclin_mcp_server.py

# In another terminal, test it
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python bioclin_mcp_server.py
```

**Test MCPX health:**
```bash
curl http://localhost:9000/health
```

**Test MCPX MCP endpoint:**
```bash
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}'
```

## Quick Fixes

### Reset Everything

```bash
# Stop all containers
docker stop mcpx
docker rm mcpx

# Remove old images
docker rmi mcpx-bioclin:local

# Rebuild
docker build -f Dockerfile.mcpx-cloudrun -t mcpx-bioclin:local .

# Start fresh
docker run --rm -p 9000:9000 -p 5173:5173 mcpx-bioclin:local
```

### Check Configuration

```bash
# Validate YAML
python -c "import yaml; yaml.safe_load(open('mcpx-config/app.yaml'))"

# Validate JSON
python -c "import json; json.load(open('mcpx-config/mcp.json'))"
```

### Update MCPX

```bash
# Pull latest MCPX image
docker pull us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# Rebuild sidecar with new base
docker build -f Dockerfile.mcpx-cloudrun -t mcpx-bioclin:local .
```

## Still Having Issues?

1. **Check the logs** - Almost all issues show up in logs
2. **Test components separately** - Isolate the problem
3. **Verify configurations** - Double-check YAML/JSON syntax
4. **Review the guides:**
   - MCPX-DEPLOYMENT.md
   - MCPX-QUICKSTART.md
   - mcpx-config/README.md

## Common Success Indicators

When everything is working, you should see:

**MCPX logs:**
```
✓ Starting MCPX server...
✓ Starting Prometheus metrics endpoint
✓ Initializing TargetClients with servers (count=1)
✓ TargetClients initialized
✓ HTTP server listening on port 9000
```

**Control Plane:**
```
✓ Opens at http://localhost:5173
✓ Shows "bioclin" server
✓ Lists 44 tools
✓ No error indicators
```

**Tests pass:**
```bash
./tests/test-integration.sh
# Result: 9/9 tests passing
```
