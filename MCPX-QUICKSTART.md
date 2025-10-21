# MCPX Bioclin Quick Start Guide

**Get your Bioclin tools accessible via HTTP in under 10 minutes!**

## What is MCPX?

Think of MCPX as a **smart gateway** that sits between your applications (like Claude, chatbots, or custom tools) and the Bioclin MCP server. It adds:

- 🔒 **Authentication** - Control who can access your Bioclin tools
- 🌐 **HTTP Access** - Use Bioclin from anywhere, not just locally
- 📊 **Monitoring** - Track usage and performance
- 🎛️ **Control Panel** - Visual interface to manage everything

**Before MCPX:**
```
Your App → Bioclin MCP (local only, no auth, command-line)
```

**After MCPX:**
```
Your App → MCPX Gateway → Bioclin MCP (anywhere, secure, HTTP)
         (http://localhost:9000)
```

## What You'll Need

- ✅ **Docker Desktop** installed and running ([Get Docker](https://www.docker.com/products/docker-desktop))
- ✅ **Bioclin account** with username and password
- ✅ **10 minutes** of your time
- ⚠️ **Note**: You don't need to know anything about MCPX or MCP to follow this guide!

## 🚀 The Easiest Way: One-Command Startup

**Just want it to work? Run this:**

```bash
./start-mcpx.sh
```

That's it! This script does everything:
- ✅ Checks if Docker is running
- ✅ Installs all dependencies
- ✅ Starts MCPX
- ✅ Connects to Bioclin
- ✅ Shows you when it's ready

**What you'll see:**
```
🚀 Starting MCPX with Bioclin MCP Server
Installing Python dependencies...
✅ MCPX is ready!

Access Points:
  • MCPX API:      http://localhost:9000
  • Control Plane: http://localhost:5173
```

**Next:** Open your browser to http://localhost:5173

You'll see a beautiful control panel showing all 44 Bioclin tools! 🎉

---

## 📖 Want to Understand What's Happening?

<details>
<summary>Click to see the step-by-step explanation</summary>

### What the script does behind the scenes:

**Step 1: Starts MCPX Container**
- Downloads the MCPX Docker image
- Mounts your Bioclin code so MCPX can access it
- Opens ports 9000 (API) and 5173 (Control Panel)

**Step 2: Installs Dependencies**
- Installs Python packages Bioclin needs (mcp, httpx, pydantic)
- This happens automatically inside the container

**Step 3: Connects to Bioclin**
- MCPX discovers all 44 Bioclin tools
- Sets up the HTTP gateway
- Starts the visual control panel

**Step 4: Ready!**
- MCPX is now running and ready to use
- All Bioclin operations are now accessible via HTTP
- You can monitor everything in the control panel

</details>

---

## 💬 Use Bioclin in Claude Desktop (2 minutes)

Want to use Bioclin tools directly in Claude Desktop? Here's how!

**Prerequisites:** Make sure MCPX is running (run `./start-mcpx.sh` first)

### Step 1: Find Your Claude Config File

**macOS:**
```bash
open ~/Library/Application\ Support/Claude/
```
Then edit `claude_desktop_config.json`

**Windows:**
```
Open: %APPDATA%/Claude/claude_desktop_config.json
```

**Don't see the file?** Create it! It should look like this to start:
```json
{
  "mcpServers": {}
}
```

### Step 2: Add Bioclin Connection

Add this inside the `mcpServers` section:
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

**What this does:** Tells Claude to connect to your local MCPX gateway (which connects to Bioclin).

### Step 3: Restart Claude Desktop

Close Claude Desktop completely and reopen it.

### Step 4: Try It Out!

Type this in Claude:
```
"Login to Bioclin and show me my projects"
```

You should see Claude using the Bioclin tools! ✨

**Troubleshooting:**
- **Tools not showing?** Make sure MCPX is running: `docker ps | grep mcpx`
- **Connection refused?** Check that port 9000 is open: `lsof -i :9000`

## ☁️ Deploy to Google Cloud (10 minutes)

Want to access Bioclin from anywhere on the internet? Deploy to Google Cloud Run!

**Why deploy to the cloud?**
- ✅ Access from anywhere (not just localhost)
- ✅ Always-on availability
- ✅ Automatic scaling
- ✅ Production-grade security

### Prerequisites

**Step 1:** Install Google Cloud SDK

If you don't have it yet: [Download here](https://cloud.google.com/sdk/docs/install)

**Step 2:** Login and Setup
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (replace with your actual project ID)
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

**Don't have a GCP project?** [Create one here](https://console.cloud.google.com/projectcreate) (free trial available!)

### Deploy in 2 Steps

**Step 1 (Optional):** Setup OAuth for production security
```bash
./deploy/setup-gcp-secrets.sh
```
**Skip this for now** if you just want to test the deployment first. You can add authentication later!

**Step 2:** Deploy!
```bash
./deploy/deploy-cloudrun.sh
```

This script automatically:
- Builds a Docker image with MCPX + Bioclin
- Uploads it to Google Container Registry
- Deploys to Cloud Run
- Configures auto-scaling and health checks

**Wait time:** About 3-5 minutes for first deployment ☕

### Get Your Public URL

After deployment completes:
```bash
export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
  --region us-central1 \
  --format 'value(status.url)')

echo "Your MCPX URL: $MCPX_URL"
```

You'll see something like: `https://mcpx-bioclin-xxxxx-uc.a.run.app`

### Test Your Deployment

```bash
# Get an auth token
TOKEN=$(gcloud auth print-identity-token)

# List all tools
curl -X POST $MCPX_URL/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq .
```

**Success!** You should see all 44 Bioclin tools listed! 🎉

**Troubleshooting:**
- **Authentication error?** Make sure you're logged in: `gcloud auth list`
- **Permission denied?** Check your project has Cloud Run enabled: `gcloud services enable run.googleapis.com`
- **Build fails?** See detailed logs with: `gcloud builds log --region=us-central1`

## 🤖 Build Your Own Chatbot (5 minutes)

Want to build a custom chatbot that uses Bioclin? We've included a ready-to-use Python client!

### What You Can Build

With the Bioclin chatbot client, you can:
- 💬 Create conversational interfaces for Bioclin
- 🔗 Integrate Bioclin into existing applications
- 🤝 Connect to LangChain, FastAPI, or other frameworks
- 🎯 Build custom automation workflows

### Quick Start

**Step 1:** Install the client library
```bash
pip install httpx
```

**Step 2:** Create your first chatbot

Create a file called `my_chatbot.py`:
```python
import asyncio
from chatbot.bioclin_chatbot_client import BioclinChatbotClient

async def main():
    # Connect to your local MCPX (make sure it's running!)
    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="MyChatbot"
    )

    async with client:
        # Login to Bioclin
        print("Logging in to Bioclin...")
        await client.login_bioclin(
            "your-email@example.com",
            "your-password"
        )

        # Get your projects
        print("\nFetching your projects...")
        projects = await client.list_projects()
        print(f"\n✅ You have {projects['count']} projects:\n")

        # Display them nicely
        for project in projects['data']:
            print(f"  📁 {project['name']}")
            print(f"     {project['description']}\n")

if __name__ == "__main__":
    asyncio.run(main())
```

**Step 3:** Run it!
```bash
python my_chatbot.py
```

**You'll see:**
```
Logging in to Bioclin...

Fetching your projects...

✅ You have 3 projects:

  📁 Cancer Research Study
     Genomic analysis of tumor samples

  📁 COVID-19 Variants
     Tracking viral mutations

  📁 Microbiome Project
     Gut bacteria diversity analysis
```

**That's it!** You've built a working Bioclin chatbot! 🎉

### Next Steps

Want to do more? Check out:
- **Full client API:** `chatbot/README.md`
- **LangChain integration:** `chatbot/bioclin_chatbot_client.py` (see examples)
- **FastAPI integration:** Build a web API for your chatbot

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

## 🔧 Troubleshooting Common Issues

Having trouble? Here are the most common issues and how to fix them!

### MCPX Won't Start

**Symptom:** Running `./start-mcpx.sh` fails or hangs

**Fixes to try:**

**1. Is Docker running?**
```bash
docker ps
```
**No output?** Start Docker Desktop first!

**2. Port already in use?**
```bash
lsof -i :9000
```
**Something listed?** Stop that service first, or stop the old MCPX:
```bash
docker stop mcpx
docker rm mcpx
```

**3. Need latest version?**
```bash
docker pull us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest
```

### Tools Not Showing Up in Claude Desktop

**Symptom:** Claude doesn't show Bioclin tools

**Fixes to try:**

**1. Is MCPX actually running?**
```bash
docker ps | grep mcpx
```
**Not running?** Start it: `./start-mcpx.sh`

**2. Check the MCPX logs for errors**
```bash
docker logs mcpx
```
Look for "STDIO client connected" - that's good! Look for errors in red.

**3. Test the tools are available**
```bash
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools | length'
```
**Expected output:** `44`

**4. Restart Claude Desktop**
Sometimes Claude needs a full restart (quit completely, then reopen).

### Bioclin Login Fails

**Symptom:** "Login failed" or authentication error

**Fixes to try:**

**1. Check your credentials are correct**
Try logging in via the web interface: https://bioclin.vindhyadatascience.com

**2. Test the API directly**
```bash
curl -X POST https://bioclin.vindhyadatascience.com/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=your_password"
```
**Should return:** A JSON object with a token

**3. Check your internet connection**
The Bioclin API is online, so you need internet access.

### Cloud Run Deployment Fails

**Symptom:** `./deploy/deploy-cloudrun.sh` fails

**Fixes to try:**

**1. Are you logged in to Google Cloud?**
```bash
gcloud auth list
```
**Not logged in?** Run: `gcloud auth login`

**2. Is your project set correctly?**
```bash
gcloud config get-value project
```
**Wrong or empty?** Set it: `gcloud config set project YOUR_PROJECT_ID`

**3. Are required APIs enabled?**
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

**4. Check build logs**
```bash
gcloud builds log --region=us-central1
```

### Still Having Issues?

See the detailed troubleshooting guide: `TROUBLESHOOTING.md`

Or check the logs:
```bash
# Local MCPX logs
docker logs -f mcpx

# Cloud Run logs
gcloud run services logs tail mcpx-bioclin --region us-central1
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
