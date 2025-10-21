# MCPX Bioclin Deployment Guide

Complete guide for deploying Bioclin MCP Server with MCPX gateway for production use.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Phase 1: Local MCPX Setup](#phase-1-local-mcpx-setup)
5. [Phase 2: Claude Desktop Integration](#phase-2-claude-desktop-integration)
6. [Phase 3: OAuth Authentication](#phase-3-oauth-authentication)
7. [Phase 4: Cloud Run Deployment](#phase-4-cloud-run-deployment)
8. [Phase 5: Chatbot Integration](#phase-5-chatbot-integration)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

## Overview

This deployment integrates:
- **Bioclin MCP Server** (44 tools for bioinformatics workflows)
- **MCPX Gateway** (aggregator with auth, permissions, monitoring)
- **OAuth 2.1** (enterprise-grade authentication)
- **Google Cloud Run** (scalable serverless deployment)
- **Chatbot Client** (Python library for integration)

### What You'll Get

✅ Production-ready MCPX gateway on Cloud Run
✅ Secure OAuth 2.1 authentication
✅ All 44 Bioclin tools accessible via HTTP
✅ Python client library for chatbot integration
✅ Comprehensive test suite
✅ Local development environment

## Architecture

```
[Chatbot/Claude Client]
       ↓ (HTTP + OAuth Bearer Token)
    [MCPX on Cloud Run] (Port 9000)
       ↓ (MCP stdio protocol)
[Bioclin MCP Server] (sidecar in same container)
       ↓ (HTTP with session cookies)
[Bioclin API] (https://bioclin.vindhyadatascience.com)
```

### Key Components

| Component | Purpose | Technology |
|-----------|---------|------------|
| **MCPX Gateway** | Aggregator, auth, permissions | Node.js container |
| **Bioclin MCP** | MCP server with 44 tools | Python (stdio) |
| **OAuth Provider** | Authentication | Auth0/Google/Custom |
| **Cloud Run** | Hosting platform | Google Cloud |
| **Chatbot Client** | Integration library | Python (httpx) |

## Quick Start

### Prerequisites

- Docker installed
- Google Cloud SDK (for Cloud Run deployment)
- Python 3.10+ (for chatbot client)
- Bioclin account credentials

### 5-Minute Local Setup

```bash
# 1. Build Bioclin Docker image
docker build -t bioclin-mcp:latest .

# 2. Run MCPX locally
docker run --rm --pull always \
  --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 9000:9000 \
  -p 5173:5173 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# 3. Test it
./tests/test-integration.sh

# 4. Open MCPX Control Plane
open http://localhost:5173
```

## Phase 1: Local MCPX Setup

### Configuration Files

All configuration is in `mcpx-config/`:

```
mcpx-config/
├── app.yaml              # MCPX configuration (permissions, auth)
├── mcp.json             # MCP server registry
├── .env.template        # Environment variables template
└── README.md            # Configuration documentation
```

### Setup Steps

1. **Review configuration:**
   ```bash
   cat mcpx-config/app.yaml
   cat mcpx-config/mcp.json
   ```

2. **Create environment file:**
   ```bash
   cp mcpx-config/.env.template mcpx-config/.env
   # Edit .env with your values
   ```

3. **Build Bioclin image:**
   ```bash
   docker build -t bioclin-mcp:latest .
   ```

4. **Start MCPX:**
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

5. **Verify:**
   - MCPX API: http://localhost:9000/health
   - Control Plane: http://localhost:5173
   - Run tests: `./mcpx-config/test-mcpx-local.sh`

## Phase 2: Claude Desktop Integration

### Update Claude Desktop Config

Location:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Content:
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

### Test Connection

1. Restart Claude Desktop
2. Look for Bioclin tools in the tools panel
3. Try: "Login to Bioclin with my credentials and list my projects"

## Phase 3: OAuth Authentication

### Why OAuth?

- **Security**: No hardcoded credentials
- **Scalability**: Centralized user management
- **Compliance**: Enterprise SSO support
- **Auditability**: Track all access

### Recommended: Auth0 Setup

**See:** `mcpx-config/auth-setup-guide.md` for detailed instructions

Quick version:

1. **Create Auth0 account** at https://auth0.com

2. **Create API:**
   - Name: `MCPX Bioclin API`
   - Identifier: `mcpx-bioclin`
   - Permissions: `read:tools`, `execute:tools`

3. **Create Application:**
   - Type: `Machine to Machine`
   - Authorize with your API

4. **Configure MCPX:**
   ```bash
   # Update .env
   AUTH0_DOMAIN=your-domain.us.auth0.com
   AUTH0_CLIENT_ID=your_client_id
   AUTH0_CLIENT_SECRET=your_client_secret

   # Update app.yaml
   # Set auth.enabled: true
   ```

5. **Test OAuth:**
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

   # Use token
   curl -X POST http://localhost:9000/mcp \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"method": "tools/list"}'
   ```

## Phase 4: Cloud Run Deployment

### Prerequisites

```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login and set project
gcloud auth login
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

### Deployment Steps

**See:** `deploy/README.md` for detailed instructions

1. **Setup secrets (one-time):**
   ```bash
   ./deploy/setup-gcp-secrets.sh
   ```

   Enter your Auth0 credentials when prompted.

2. **Deploy to Cloud Run:**
   ```bash
   ./deploy/deploy-cloudrun.sh
   ```

   This will:
   - Build Docker image
   - Push to GCR
   - Deploy to Cloud Run
   - Configure secrets
   - Output service URL

3. **Get service URL:**
   ```bash
   export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
     --region us-central1 \
     --format 'value(status.url)')

   echo "Service URL: $MCPX_URL"
   ```

4. **Test deployment:**
   ```bash
   TOKEN=$(gcloud auth print-identity-token)

   curl -X POST $MCPX_URL/mcp \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -H "x-lunar-consumer-tag: Test" \
     -d '{"method": "tools/list"}'
   ```

### Monitoring

```bash
# View logs
gcloud run services logs tail mcpx-bioclin --region us-central1

# View metrics in Cloud Console
open "https://console.cloud.google.com/run/detail/us-central1/mcpx-bioclin"
```

## Phase 5: Chatbot Integration

### Python Client Library

**See:** `chatbot/README.md` for detailed documentation

### Basic Usage

```python
from chatbot.bioclin_chatbot_client import BioclinChatbotClient

# Create client
client = BioclinChatbotClient(
    mcpx_url="https://your-service.run.app",
    oauth_config={
        "token_url": "https://your-domain.us.auth0.com/oauth/token",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "audience": "mcpx-bioclin"
    }
)

# Use it
async with client:
    # Login to Bioclin
    await client.login_bioclin("user@example.com", "password")

    # Get projects
    projects = await client.list_projects()
    print(f"Found {projects['count']} projects")

    # Create a run
    run = await client.create_run(
        name="My Analysis",
        project_id="project-uuid-here"
    )
```

### LangChain Integration

```python
from langchain.tools import Tool
from chatbot.bioclin_chatbot_client import BioclinChatbotClient

client = BioclinChatbotClient(mcpx_url="https://your-service.run.app")

tools = [
    Tool(
        name="list_projects",
        description="List Bioclin projects",
        func=lambda _: asyncio.run(client.list_projects())
    ),
    # Add more tools...
]

# Use with LangChain agent
```

## Testing

### Local Testing

```bash
# Integration tests
./tests/test-integration.sh

# Python client tests
python tests/test-chatbot-client.py

# All tests
./tests/run-all-tests.sh
```

### Cloud Run Testing

```bash
# Set service URL
export MCPX_URL="https://your-service.run.app"

# Set OAuth credentials
export AUTH0_DOMAIN="your-domain.us.auth0.com"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"

# Run tests
./tests/test-integration.sh
```

**See:** `tests/README.md` for complete testing documentation

## Troubleshooting

### MCPX Not Starting

```bash
# Check Docker
docker ps
docker logs mcpx

# Check Bioclin image
docker images | grep bioclin-mcp
```

### OAuth Token Issues

```bash
# Verify secrets
gcloud secrets list --project=$GCP_PROJECT_ID

# Test token endpoint
curl --request POST \
  --url "https://${AUTH0_DOMAIN}/oauth/token" \
  --header 'content-type: application/json' \
  --data "{
    \"client_id\":\"${AUTH0_CLIENT_ID}\",
    \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
    \"audience\":\"mcpx-bioclin\",
    \"grant_type\":\"client_credentials\"
  }" | jq .
```

### Bioclin API Connection

```bash
# Test Bioclin API directly
curl -X POST https://bioclin.vindhyadatascience.com/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password"
```

### Cloud Run Errors

```bash
# Check service status
gcloud run services describe mcpx-bioclin --region us-central1

# View logs
gcloud run services logs tail mcpx-bioclin --region us-central1

# Check service account permissions
gcloud projects get-iam-policy $GCP_PROJECT_ID \
  --flatten="bindings[].members" \
  --format='table(bindings.role)' \
  --filter="bindings.members:serviceAccount:mcpx-bioclin@*"
```

## File Structure

```
bioclin-mcp/
├── mcpx-config/              # MCPX configuration
│   ├── app.yaml              # Main config
│   ├── app-with-auth.yaml    # Auth examples
│   ├── mcp.json              # Server registry
│   ├── auth-setup-guide.md   # OAuth guide
│   └── README.md
├── deploy/                   # Deployment scripts
│   ├── setup-gcp-secrets.sh
│   ├── deploy-cloudrun.sh
│   └── README.md
├── chatbot/                  # Python client library
│   ├── bioclin_chatbot_client.py
│   ├── requirements.txt
│   └── README.md
├── tests/                    # Test suite
│   ├── test-integration.sh
│   ├── test-chatbot-client.py
│   ├── run-all-tests.sh
│   └── README.md
├── Dockerfile.cloudrun       # Cloud Run Dockerfile
├── Dockerfile.mcpx-cloudrun  # MCPX Cloud Run Dockerfile
└── MCPX-DEPLOYMENT.md        # This file
```

## Key Deliverables

### ✅ Completed

1. **MCPX Configuration**
   - Local development setup
   - OAuth authentication config
   - Permission management

2. **Docker Containers**
   - Bioclin MCP Server image
   - MCPX gateway image
   - Sidecar architecture

3. **Cloud Run Deployment**
   - Automated deployment scripts
   - Secret management
   - Environment configuration

4. **Chatbot Integration**
   - Python client library
   - LangChain integration examples
   - FastAPI integration examples

5. **Testing Suite**
   - Integration tests
   - Client library tests
   - Automated test runner

6. **Documentation**
   - Setup guides
   - API references
   - Troubleshooting guides

## Next Steps

After successful deployment:

1. **Configure Monitoring:**
   - Set up Cloud Monitoring alerts
   - Configure log-based metrics
   - Enable error reporting

2. **Setup CI/CD:**
   - Integrate tests into GitHub Actions
   - Automate deployments
   - Configure staging environment

3. **Build Chatbot:**
   - Use Python client library
   - Integrate with LLM framework
   - Deploy chatbot interface

4. **Add Features:**
   - Custom domain name
   - Rate limiting
   - API usage analytics

## Support & Resources

- **MCPX Docs**: https://docs.lunar.dev/mcpx/
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Bioclin API**: https://bioclin.vindhyadatascience.com/docs
- **Cloud Run**: https://cloud.google.com/run/docs
- **Auth0**: https://auth0.com/docs

## Security Checklist

- [ ] OAuth enabled in production (`auth.enabled: true`)
- [ ] Secrets stored in Secret Manager (not in code)
- [ ] `--no-allow-unauthenticated` flag set
- [ ] Secrets rotated every 90 days
- [ ] Cloud Logging enabled
- [ ] Service account has minimal permissions
- [ ] CORS configured properly for web clients
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting configured

## License

Same as parent Bioclin MCP project.

---

**Ready to deploy? Start with Phase 1!**
