# MCPX Bioclin Quick Start Guide

Get up and running with MCPX Bioclin in under 10 minutes.

## Prerequisites

- ✅ Docker installed and running
- ✅ Bioclin account credentials
- ✅ (Optional) Google Cloud account for production deployment

## Option 1: Local Development (5 minutes)

### Step 1: Build Bioclin Image
```bash
docker build -t bioclin-mcp:latest .
```

### Step 2: Start MCPX
```bash
docker run --rm --pull always \
  --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 9000:9000 \
  -p 5173:5173 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
```

### Step 3: Verify
```bash
# In a new terminal
./mcpx-config/test-mcpx-local.sh
```

### Step 4: Open Control Plane
```bash
open http://localhost:5173
```

**Done!** MCPX is running locally with all 44 Bioclin tools.

## Option 2: Claude Desktop Integration (2 minutes)

### Step 1: Update Config

**macOS:** Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** Edit `%APPDATA%/Claude/claude_desktop_config.json`

Add this:
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

### Step 2: Restart Claude Desktop

**Done!** Bioclin tools are now available in Claude.

### Try It:
```
"Login to Bioclin and show me my projects"
```

## Option 3: Cloud Run Deployment (10 minutes)

### Prerequisites
```bash
# Install Google Cloud SDK if not already installed
# https://cloud.google.com/sdk/docs/install

gcloud auth login
export GCP_PROJECT_ID="your-project-id"
```

### Step 1: Setup Secrets (Optional, for OAuth)
```bash
./deploy/setup-gcp-secrets.sh
```

**Skip this if deploying without authentication initially.**

### Step 2: Deploy
```bash
./deploy/deploy-cloudrun.sh
```

### Step 3: Get Service URL
```bash
export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
  --region us-central1 \
  --format 'value(status.url)')

echo "Your MCPX URL: $MCPX_URL"
```

### Step 4: Test
```bash
TOKEN=$(gcloud auth print-identity-token)

curl -X POST $MCPX_URL/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq .
```

**Done!** Your MCPX is now running on Cloud Run.

## Option 4: Python Chatbot (5 minutes)

### Step 1: Install Client
```bash
pip install httpx
```

### Step 2: Create Chatbot Script

**chatbot.py:**
```python
import asyncio
from chatbot.bioclin_chatbot_client import BioclinChatbotClient

async def main():
    # Local MCPX
    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="MyChatbot"
    )

    async with client:
        # Login to Bioclin
        await client.login_bioclin(
            "your-email@example.com",
            "your-password"
        )

        # Get projects
        projects = await client.list_projects()
        print(f"You have {projects['count']} projects")

        # List them
        for project in projects['data']:
            print(f"- {project['name']}: {project['description']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 3: Run
```bash
python chatbot.py
```

**Done!** You have a working chatbot client.

## Testing Your Setup

### Quick Test
```bash
# Run integration tests
./tests/test-integration.sh

# Run client tests
python tests/test-chatbot-client.py

# Run all tests
./tests/run-all-tests.sh
```

### Expected Output
```
========================================
MCPX Bioclin Integration Test Suite
========================================

✓ PASS Health endpoint responding
✓ PASS Found 44 tools
✓ PASS Bioclin login successful
✓ PASS Got user info: user@example.com

========================================
Test Summary
========================================

Tests Passed: 15
Tests Failed: 0

✓ All tests passed!
```

## Common Tasks

### View MCPX Logs (Local)
```bash
docker logs -f mcpx
```

### View Cloud Run Logs
```bash
gcloud run services logs tail mcpx-bioclin --region us-central1
```

### Stop MCPX (Local)
```bash
docker stop mcpx
```

### Restart MCPX (Local)
```bash
docker restart mcpx
```

### Update Cloud Run Deployment
```bash
# Edit config in mcpx-config/app.yaml
# Then redeploy
./deploy/deploy-cloudrun.sh
```

### Enable OAuth (Production)

**Step 1:** Create Auth0 account at https://auth0.com

**Step 2:** Create API with identifier `mcpx-bioclin`

**Step 3:** Get credentials and update `.env`:
```bash
cp mcpx-config/.env.template mcpx-config/.env
# Edit .env with your Auth0 credentials
```

**Step 4:** Update `app.yaml`:
```bash
# Set auth.enabled: true in mcpx-config/app.yaml
```

**Step 5:** Restart MCPX or redeploy

See `mcpx-config/auth-setup-guide.md` for detailed instructions.

## Available Tools (44 Total)

### Authentication (4)
- bioclin_login
- bioclin_logout
- bioclin_validate_token
- bioclin_refresh_token

### User Management (11)
- bioclin_create_user
- bioclin_get_users
- bioclin_get_user_me
- bioclin_update_user_me
- ... and more

### Projects (5)
- bioclin_create_project
- bioclin_get_projects
- bioclin_get_user_projects
- bioclin_get_project
- bioclin_delete_project

### Runs (5)
- bioclin_create_run
- bioclin_get_runs
- bioclin_get_runs_by_project
- bioclin_get_runs_by_org
- bioclin_delete_run

**+ Organizations (6)**
**+ Analysis Types (4)**
**+ Parameters (4)**
**+ Permissions (2)**
**+ Google Cloud Storage (3)**

Full list at: http://localhost:5173 (when MCPX is running)

## Troubleshooting

### MCPX Won't Start
```bash
# Check if Docker is running
docker ps

# Check for port conflicts
lsof -i :9000

# Pull latest MCPX image
docker pull us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
```

### Tools Not Showing Up
```bash
# Verify Bioclin image exists
docker images | grep bioclin-mcp

# Check MCPX logs
docker logs mcpx

# Test tool listing
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools | length'
```

### Bioclin Login Fails
```bash
# Test Bioclin API directly
curl -X POST https://bioclin.vindhyadatascience.com/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=your_password"
```

### Cloud Run Deployment Fails
```bash
# Check GCP authentication
gcloud auth list

# Verify project
gcloud config get-value project

# Check service account permissions
gcloud projects get-iam-policy $(gcloud config get-value project)
```

## Next Steps

After getting started:

1. **Read the full guide:** `MCPX-DEPLOYMENT.md`
2. **Configure OAuth:** `mcpx-config/auth-setup-guide.md`
3. **Deploy to production:** `deploy/README.md`
4. **Build a chatbot:** `chatbot/README.md`
5. **Run tests:** `tests/README.md`

## Quick Reference

### URLs
- **MCPX API:** http://localhost:9000
- **Control Plane:** http://localhost:5173
- **Health Check:** http://localhost:9000/health
- **Bioclin API:** https://bioclin.vindhyadatascience.com/api/v1

### Ports
- **9000** - MCPX HTTP API
- **5173** - MCPX Control Plane
- **9001** - MCPX Additional Service
- **3000** - MCPX Additional Service

### Key Files
- **mcpx-config/app.yaml** - Main configuration
- **mcpx-config/mcp.json** - Server registry
- **mcpx-config/.env** - Environment variables
- **deploy/deploy-cloudrun.sh** - Deployment script
- **tests/test-integration.sh** - Test script

### Helpful Commands
```bash
# Start MCPX
docker run --rm --pull always --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 9000:9000 -p 5173:5173 --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# Test
./tests/test-integration.sh

# Deploy to Cloud Run
./deploy/deploy-cloudrun.sh

# View logs
docker logs -f mcpx
gcloud run services logs tail mcpx-bioclin --region us-central1
```

## Support

- **Documentation:** See `MCPX-DEPLOYMENT.md`
- **Issues:** Check troubleshooting section above
- **MCPX Docs:** https://docs.lunar.dev/mcpx/
- **MCP Protocol:** https://modelcontextprotocol.io/

---

**Ready? Pick your option above and get started! 🚀**
