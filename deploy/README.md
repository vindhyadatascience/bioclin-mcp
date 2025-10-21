# Cloud Run Deployment Scripts

This directory contains scripts for deploying the MCPX Bioclin server to Google Cloud Run.

## Prerequisites

1. **Google Cloud SDK** installed and configured
   ```bash
   gcloud init
   gcloud auth login
   ```

2. **Docker** installed and running

3. **GCP Project** with billing enabled

4. **Environment variables** set:
   ```bash
   export GCP_PROJECT_ID="your-gcp-project-id"
   export GCP_REGION="us-central1"  # optional, defaults to us-central1
   ```

## Deployment Steps

### Step 1: Setup GCP Secrets (One-time)

This creates secrets in Google Secret Manager for OAuth credentials:

```bash
./deploy/setup-gcp-secrets.sh
```

You'll be prompted to enter:
- Auth0 Domain
- Auth0 Client ID
- Auth0 Client Secret

**Note:** You can skip this if deploying without authentication initially.

### Step 2: Deploy to Cloud Run

This builds the Docker image and deploys to Cloud Run:

```bash
./deploy/deploy-cloudrun.sh
```

The script will:
1. Build the Docker image
2. Push to Google Container Registry
3. Deploy to Cloud Run
4. Configure secrets and environment variables
5. Output the service URL

### Step 3: Test the Deployment

After deployment, test the service:

```bash
# Get identity token
export TOKEN=$(gcloud auth print-identity-token)

# List tools
curl -X POST https://your-service.run.app/mcp \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}'
```

## Configuration Options

### Environment Variables

Set these before running deployment scripts:

```bash
# Required
export GCP_PROJECT_ID="your-project-id"

# Optional (with defaults)
export GCP_REGION="us-central1"
export SERVICE_NAME="mcpx-bioclin"
export MEMORY="2Gi"
export CPU="2"
export MAX_INSTANCES="10"
export BIOCLIN_API_URL="https://bioclin.vindhyadatascience.com/api/v1"
```

### Deployment Modes

#### 1. Without Authentication (Development)
```bash
# Just deploy without running setup-gcp-secrets.sh
./deploy/deploy-cloudrun.sh
```

Auth will be disabled by default in `mcpx-config/app.yaml`.

#### 2. With Authentication (Production)
```bash
# First, setup secrets
./deploy/setup-gcp-secrets.sh

# Then deploy
./deploy/deploy-cloudrun.sh
```

Make sure `mcpx-config/app.yaml` has `auth.enabled: true`.

## Updating the Deployment

### Update Configuration Only

If you only changed `mcpx-config/app.yaml` or `mcpx-config/mcp.json`:

```bash
./deploy/deploy-cloudrun.sh
```

This rebuilds and redeploys with the new config.

### Update Secrets

```bash
# Update a specific secret
echo -n "new-secret-value" | \
  gcloud secrets versions add SECRET_NAME --data-file=-

# Then redeploy to pick up new version
./deploy/deploy-cloudrun.sh
```

## Monitoring and Debugging

### View Logs

```bash
# Tail logs in real-time
gcloud run services logs tail mcpx-bioclin --region us-central1

# View logs in Cloud Console
gcloud run services describe mcpx-bioclin --region us-central1
```

### Check Service Status

```bash
gcloud run services describe mcpx-bioclin --region us-central1
```

### Access MCPX Control Plane

The MCPX Control Plane UI is not exposed in Cloud Run by default for security.
To access it:

1. **Use Cloud Run Proxy:**
   ```bash
   gcloud run services proxy mcpx-bioclin --port=5173 --region=us-central1
   ```
   Then open http://localhost:5173

2. **Or enable public access** (not recommended for production):
   Deploy with `--allow-unauthenticated` flag (modify script)

## Troubleshooting

### "Permission denied" errors

Ensure the service account has required roles:
```bash
gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
  --member="serviceAccount:mcpx-bioclin@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### "Image not found" errors

Make sure you've pushed the image:
```bash
docker push gcr.io/${GCP_PROJECT_ID}/mcpx-bioclin:latest
```

### "Service unhealthy" errors

Check health endpoint:
```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  https://your-service.run.app/health
```

Check logs for startup errors:
```bash
gcloud run services logs tail mcpx-bioclin --region us-central1
```

### Authentication issues

Verify secrets are accessible:
```bash
gcloud secrets list
gcloud secrets versions access latest --secret=auth0-domain
```

## Cost Optimization

Cloud Run pricing is based on:
- CPU and memory allocation
- Number of requests
- Request duration

To optimize costs:

1. **Set min-instances to 0** (default in script)
   - Service scales to zero when not in use
   - Small cold start delay on first request

2. **Adjust memory and CPU**
   ```bash
   export MEMORY="1Gi"  # Reduce if sufficient
   export CPU="1"       # Reduce if sufficient
   ```

3. **Set appropriate max-instances**
   ```bash
   export MAX_INSTANCES="5"  # Lower limit prevents runaway costs
   ```

4. **Monitor usage**
   ```bash
   gcloud run services describe mcpx-bioclin \
     --region us-central1 \
     --format="value(status.traffic)"
   ```

## CI/CD Integration

To integrate with Cloud Build:

1. Create `cloudbuild.yaml`:
   ```yaml
   steps:
     - name: 'gcr.io/cloud-builders/docker'
       args: ['build', '-t', 'gcr.io/$PROJECT_ID/mcpx-bioclin', '-f', 'Dockerfile.mcpx-cloudrun', '.']
     - name: 'gcr.io/cloud-builders/docker'
       args: ['push', 'gcr.io/$PROJECT_ID/mcpx-bioclin']
     - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
       entrypoint: gcloud
       args:
         - 'run'
         - 'deploy'
         - 'mcpx-bioclin'
         - '--image=gcr.io/$PROJECT_ID/mcpx-bioclin'
         - '--region=us-central1'
         - '--platform=managed'
   ```

2. Trigger builds on git push:
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```

## Security Best Practices

✅ **Always use `--no-allow-unauthenticated`** (default in script)
✅ **Store secrets in Secret Manager** (never in code or env vars)
✅ **Enable auth in production** (`auth.enabled: true` in app.yaml)
✅ **Use HTTPS only** (Cloud Run enforces this automatically)
✅ **Rotate secrets regularly** (every 90 days)
✅ **Monitor access logs** for suspicious activity
✅ **Use VPC connector** if accessing private resources

## Next Steps

After successful deployment:
1. ✅ Test the deployment with curl
2. ⏭️ Configure chatbot client to use the Cloud Run URL
3. ⏭️ Set up monitoring and alerting
4. ⏭️ Configure custom domain (optional)
5. ⏭️ Set up CI/CD pipeline (optional)
