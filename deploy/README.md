# Cloud Run Deployment Scripts

**Deploy MCPX + Bioclin to Google Cloud so you can access it from anywhere!**

## What is This?

These scripts help you deploy your MCPX + Bioclin setup to **Google Cloud Run** - a serverless platform that:

- ✅ Makes your deployment accessible from anywhere on the internet
- ✅ Scales automatically based on usage (even to zero when not in use!)
- ✅ Only charges you for what you use
- ✅ Handles all the infrastructure for you

**Think of it as:** Moving your local MCPX setup to the cloud, so you and your team can access it from anywhere.

## Before You Start

### What You Need

1. **Google Cloud Account**
   - Sign up at https://cloud.google.com
   - Free trial includes $300 credit!
   - Create a project: https://console.cloud.google.com/projectcreate

2. **Google Cloud SDK** (command-line tools)
   - Download: https://cloud.google.com/sdk/docs/install
   - After installing, run:
     ```bash
     gcloud init
     gcloud auth login
     ```

3. **Docker Desktop** running on your computer
   - Already have this if you ran MCPX locally!

4. **Bioclin Account**
   - Your username and password for https://bioclin.vindhyadatascience.com

### Set Your Project

Before running any commands, tell Google Cloud which project to use:

```bash
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID
```

**Where do I find my project ID?** Go to https://console.cloud.google.com and look at the top of the page.

## 🚀 Quick Deployment (No Auth)

**Want to deploy as quickly as possible?** Start without authentication:

```bash
./deploy/deploy-cloudrun.sh
```

**What this does:**
1. Builds a Docker image with MCPX + Bioclin
2. Uploads it to Google Container Registry
3. Deploys to Cloud Run
4. Shows you the public URL

**Wait time:** 3-5 minutes ☕

**You'll see:**
```
Deploying to Cloud Run...
✅ Deployment successful!

Service URL: https://mcpx-bioclin-xxxxx-uc.a.run.app

Test it:
  TOKEN=$(gcloud auth print-identity-token)
  curl -X POST https://mcpx-bioclin-xxxxx-uc.a.run.app/mcp \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"method": "tools/list"}'
```

## 🔒 Production Deployment (With Auth)

For production use, add OAuth authentication:

### Step 1: Setup OAuth Secrets

First, create an Auth0 account (or use Google OAuth):
- Sign up at https://auth0.com
- Create an API with identifier `mcpx-bioclin`
- Get your domain, client ID, and client secret

Then run:
```bash
./deploy/setup-gcp-secrets.sh
```

**You'll be prompted for:**
- Auth0 Domain (like `your-app.auth0.com`)
- Auth0 Client ID (long alphanumeric string)
- Auth0 Client Secret (another long string)

**What this does:** Stores your OAuth credentials securely in Google Secret Manager.

### Step 2: Enable Auth in Config

Edit `mcpx-config/app.yaml` and change:
```yaml
auth:
  enabled: false
```

To:
```yaml
auth:
  enabled: true
  provider: auth0
  config:
    domain: "${AUTH0_DOMAIN}"
    clientId: "${AUTH0_CLIENT_ID}"
    clientSecret: "${AUTH0_CLIENT_SECRET}"
    audience: "mcpx-bioclin"
```

### Step 3: Deploy

```bash
./deploy/deploy-cloudrun.sh
```

**Now your deployment requires OAuth tokens!** Much more secure for production use.

## Testing Your Deployment

### Step 1: Get Your Service URL

After deployment, you'll see a URL like:
```
https://mcpx-bioclin-xxxxx-uc.a.run.app
```

Save it for easy access:
```bash
export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
  --region us-central1 \
  --format 'value(status.url)')

echo "Your MCPX URL: $MCPX_URL"
```

### Step 2: Test the Connection

```bash
# Get an authentication token
TOKEN=$(gcloud auth print-identity-token)

# List all Bioclin tools
curl -X POST $MCPX_URL/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq .
```

**Expected:** A JSON response listing all 44 Bioclin tools!

## Viewing Logs

**See what's happening in real-time:**

```bash
gcloud run services logs tail mcpx-bioclin --region us-central1
```

**Check service status:**

```bash
gcloud run services describe mcpx-bioclin --region us-central1
```

## Updating Your Deployment

### Changed Configuration?

If you edited `mcpx-config/app.yaml` or `mcpx-config/mcp.json`:

```bash
./deploy/deploy-cloudrun.sh
```

This rebuilds and redeploys with your changes.

### Changed OAuth Secrets?

Update the secret in Google Cloud:

```bash
echo -n "new-secret-value" | \
  gcloud secrets versions add auth0-client-secret --data-file=-
```

Then redeploy:

```bash
./deploy/deploy-cloudrun.sh
```

## Configuration Options

### Environment Variables

Customize your deployment by setting these before running the script:

```bash
# Required
export GCP_PROJECT_ID="your-project-id"

# Optional (these have sensible defaults)
export GCP_REGION="us-central1"          # Cloud Run region
export SERVICE_NAME="mcpx-bioclin"        # Service name
export MEMORY="2Gi"                       # Memory allocation
export CPU="2"                            # CPU count
export MAX_INSTANCES="10"                 # Max auto-scaling limit
```

**Example:** Deploy with less memory to save costs:
```bash
export MEMORY="1Gi"
export CPU="1"
./deploy/deploy-cloudrun.sh
```

## 💰 Cost Optimization

**Good news:** Cloud Run is very affordable!

### How You're Charged

- **Only when in use** - Scales to zero when idle
- **Based on requests** - Pay per API call
- **Resource allocation** - More CPU/memory = higher cost

### Save Money

**1. Start with minimum resources:**
```bash
export MEMORY="1Gi"
export CPU="1"
```

**2. Set a max instances limit:**
```bash
export MAX_INSTANCES="5"
```
This prevents runaway costs from unexpected traffic spikes.

**3. Monitor your usage:**
```bash
gcloud run services describe mcpx-bioclin --region us-central1
```

**Typical costs:** With low usage, expect $1-5/month. Heavy usage might be $20-50/month.

## 🔧 Troubleshooting

### "Permission denied" errors

**Problem:** Service account doesn't have access to secrets

**Fix:**
```bash
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:mcpx-bioclin@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### "Service unhealthy" errors

**Problem:** MCPX isn't starting correctly

**Fix:** Check the logs:
```bash
gcloud run services logs tail mcpx-bioclin --region us-central1
```

Look for error messages (usually in red).

### "Image not found" errors

**Problem:** Docker image wasn't pushed to Container Registry

**Fix:** Enable required APIs:
```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

Then redeploy:
```bash
./deploy/deploy-cloudrun.sh
```

### Can't access tools

**Problem:** Authentication not working

**Fix:** Verify secrets are accessible:
```bash
gcloud secrets list
gcloud secrets versions access latest --secret=auth0-domain
```

If secrets are missing, run `./deploy/setup-gcp-secrets.sh` again.

## 🔒 Security Best Practices

When deploying to production:

✅ **Always enable authentication** - Edit `app.yaml` to set `auth.enabled: true`
✅ **Use Secret Manager** - Never put passwords in code or config files
✅ **Restrict access** - The default deployment requires authentication (good!)
✅ **Monitor logs** - Check for suspicious activity regularly
✅ **Rotate secrets** - Change OAuth credentials every 90 days

**Never do this:**
❌ Don't disable authentication in production
❌ Don't commit `.env` files to git
❌ Don't share your OAuth credentials

## What's Next?

After successful deployment:

1. ✅ **Test with curl** - Verify all 44 tools are accessible
2. 🤖 **Update your chatbot** - Point it to the Cloud Run URL
3. 📊 **Set up monitoring** - Track usage and errors
4. 🌐 **Custom domain** (optional) - Use your own domain name
5. 🔄 **CI/CD pipeline** (optional) - Auto-deploy on git push

**Need help?** Check the main `TROUBLESHOOTING.md` guide!

## Quick Reference

### Useful Commands

```bash
# Deploy or update
./deploy/deploy-cloudrun.sh

# View logs
gcloud run services logs tail mcpx-bioclin --region us-central1

# Get service URL
gcloud run services describe mcpx-bioclin --region us-central1 --format 'value(status.url)'

# Delete deployment
gcloud run services delete mcpx-bioclin --region us-central1

# List all Cloud Run services
gcloud run services list
```

### Default Resource Allocation

- **Memory:** 2Gi
- **CPU:** 2
- **Max Instances:** 10
- **Min Instances:** 0 (scales to zero)
- **Region:** us-central1

**Want to change these?** Set environment variables before deploying (see Configuration Options above).
