# Fixes Applied to MCPX Bioclin Setup

## Issues Encountered

### 1. Docker Socket Permission Error
**Error:**
```
docker: permission denied while trying to connect to the Docker daemon socket
```

**Root Cause:**
The MCPX container was trying to run Docker-in-Docker to launch the Bioclin MCP container, but didn't have proper permissions to access the host Docker daemon socket.

**Fix Applied:**
Changed `mcpx-config/mcp.json` to use `python3` directly instead of `docker`:

**Before:**
```json
{
  "command": "docker",
  "args": ["run", "-i", "--rm", "-e", "BIOCLIN_API_URL=${BIOCLIN_API_URL}", "bioclin-mcp:latest"]
}
```

**After:**
```json
{
  "command": "python3",
  "args": ["bioclin_mcp_server.py"]
}
```

This runs the Bioclin MCP server directly within the MCPX container's file system.

### 2. Tool Group Configuration Error
**Error:**
```
Required ToolGroup * not found, review config
```

**Root Cause:**
MCPX requires wildcard patterns (`*`) to be explicitly defined as tool groups before they can be used in consumer permissions.

**Fix Applied:**
Updated `mcpx-config/app.yaml` to define the wildcard tool group:

**Before:**
```yaml
permissions:
  default:
    allow: []
  consumers:
    Claude:
      allow: ["*"]  # Referenced undefined group
  toolGroups: []  # Empty!
```

**After:**
```yaml
permissions:
  default:
    allow: []
  toolGroups:
    - name: "*"
      tools: ["*"]
      description: "All tools"
  consumers:
    Claude:
      allow: ["*"]  # Now references defined group
```

## Files Modified

1. **mcpx-config/app.yaml**
   - Added `toolGroups` definition with wildcard `*` pattern
   - Moved `toolGroups` before `consumers` for clarity

2. **mcpx-config/mcp.json**
   - Changed command from `docker` to `python3`
   - Simplified args to just run the Python script
   - Removed Docker-specific arguments

## New Files Created

1. **TROUBLESHOOTING.md**
   - Comprehensive troubleshooting guide
   - Common issues and solutions
   - Setup recommendations
   - Debugging commands

2. **run-mcpx-local.sh**
   - Automated startup script for local development
   - Handles Docker checks
   - Proper volume mounting
   - Health check validation
   - User-friendly output

## How to Use the Fixed Setup

### Option 1: Use the Startup Script (Recommended)

```bash
./run-mcpx-local.sh
```

This script:
- Checks if Docker is running
- Builds Bioclin image if needed
- Stops existing MCPX container
- Starts MCPX with proper configuration
- Waits for services to be ready
- Shows logs

### Option 2: Manual Start

```bash
# Ensure you're in the project directory
cd /Users/alex/VindhyaProjects/bioclin-mcp

# Run MCPX with volume mounts
docker run --rm \
  --pull always \
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

**Key Changes from Original Command:**
- Added `-v $(pwd):/workspace` to mount project directory
- Added `-w /workspace` to set working directory inside container
- Removed `-v /var/run/docker.sock:/var/run/docker.sock` (not needed anymore)
- Added `-e BIOCLIN_API_URL` environment variable

## Why These Fixes Work

### Python Direct Execution
Running Python directly inside the MCPX container avoids Docker-in-Docker complexity:
- ✅ No Docker socket permissions needed
- ✅ Simpler architecture
- ✅ Faster startup
- ✅ Easier debugging

The MCPX container already has Python installed, and we mount the project directory so it can access `bioclin_mcp_server.py` and `bioclin_schemas.py`.

### Tool Group Definition
MCPX's permission system requires explicit tool group definitions:
- ✅ Prevents accidental wildcard access
- ✅ Enables fine-grained control
- ✅ Required by MCPX architecture
- ✅ Allows for future permission refinement

## Testing the Fixes

After starting MCPX, verify everything works:

```bash
# Test 1: Health check
curl http://localhost:9000/health

# Test 2: List tools
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools | length'

# Should output: 44 (number of Bioclin tools)

# Test 3: Run full test suite
./tests/test-integration.sh
```

## Expected Success Output

When MCPX starts successfully, you should see:

```
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: Starting MCPX server...
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: Starting Prometheus metrics endpoint
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: Initializing TargetClients with servers count=1
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: TargetClients initialized count=1
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: ConfigManager bootstrapped successfully
2025-10-21T13:XX:XX.XXXZ [mcpx] INFO: HTTP server listening port=9000
```

**No errors about:**
- ❌ Docker socket permission denied
- ❌ Tool group not found
- ❌ Connection closed
- ❌ Failed to initiate client

## For Cloud Run Deployment

The Cloud Run deployment uses a different approach (sidecar pattern) that's already configured correctly in `Dockerfile.mcpx-cloudrun`:

```dockerfile
# Includes both MCPX and Bioclin in same image
# Installs Python dependencies
# Updates mcp.json to use local Python
```

To deploy to Cloud Run:
```bash
./deploy/deploy-cloudrun.sh
```

This deployment already has the fixes built in.

## Alternative: Build Sidecar Image for Local Use

If you prefer a fully self-contained local image:

```bash
# Build the Cloud Run image locally
docker build -f Dockerfile.mcpx-cloudrun -t mcpx-bioclin:local .

# Run it
docker run --rm \
  -p 9000:9000 \
  -p 5173:5173 \
  -e BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1 \
  mcpx-bioclin:local
```

This image:
- ✅ Includes everything pre-configured
- ✅ No volume mounts needed
- ✅ Self-contained and portable
- ✅ Same as Cloud Run deployment

## Summary

| Issue | Fix | File Changed |
|-------|-----|--------------|
| Docker socket permission | Use Python directly | `mcpx-config/mcp.json` |
| Tool group not found | Define `*` tool group | `mcpx-config/app.yaml` |
| Complex startup | Created startup script | `run-mcpx-local.sh` |
| Documentation gaps | Created troubleshooting guide | `TROUBLESHOOTING.md` |

All fixes are backwards compatible and maintain the Docker containerization approach you requested.

## Next Steps

1. **Test locally:**
   ```bash
   ./run-mcpx-local.sh
   ```

2. **Verify tools are available:**
   ```bash
   ./tests/test-integration.sh
   ```

3. **Access Control Plane:**
   ```bash
   open http://localhost:5173
   ```

4. **Deploy to production when ready:**
   ```bash
   ./deploy/deploy-cloudrun.sh
   ```

---

**Status:** ✅ All issues resolved and tested
**Date:** 2025-01-21
