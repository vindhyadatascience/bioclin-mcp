#!/bin/bash
# Deploy MCPX Bioclin to Google Cloud Run
# This script builds and deploys the MCPX gateway with Bioclin MCP server

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-mcpx-bioclin}"
MEMORY="${MEMORY:-2Gi}"
CPU="${CPU:-2}"
MAX_INSTANCES="${MAX_INSTANCES:-10}"
MIN_INSTANCES="${MIN_INSTANCES:-0}"
TIMEOUT="${TIMEOUT:-300}"
CONCURRENCY="${CONCURRENCY:-80}"

# Bioclin API URL
BIOCLIN_API_URL="${BIOCLIN_API_URL:-https://bioclin.vindhyadatascience.com/api/v1}"

# Image name
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}Deploying MCPX Bioclin to Google Cloud Run${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found${NC}"
    exit 1
fi

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID not set${NC}"
    echo "Set it with: export GCP_PROJECT_ID=your-actual-project-id"
    exit 1
fi

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Service Name: $SERVICE_NAME"
echo "Image: $IMAGE_NAME"
echo ""

# Set the project
gcloud config set project "$PROJECT_ID"

# Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
cd "$(dirname "$0")/.."

docker build -t "$IMAGE_NAME" -f Dockerfile.mcpx-cloudrun .
echo -e "${GREEN}✓ Docker image built${NC}"
echo ""

# Push the image to Google Container Registry
echo -e "${YELLOW}Pushing image to GCR...${NC}"
docker push "$IMAGE_NAME"
echo -e "${GREEN}✓ Image pushed${NC}"
echo ""

# Check if secrets exist
echo -e "${YELLOW}Checking for secrets...${NC}"
SECRETS_ARGS=""

if gcloud secrets describe auth0-domain --project="$PROJECT_ID" &>/dev/null; then
    SECRETS_ARGS="$SECRETS_ARGS --set-secrets=AUTH0_DOMAIN=auth0-domain:latest"
    echo -e "${GREEN}✓ Found auth0-domain secret${NC}"
fi

if gcloud secrets describe auth0-client-id --project="$PROJECT_ID" &>/dev/null; then
    SECRETS_ARGS="$SECRETS_ARGS,AUTH0_CLIENT_ID=auth0-client-id:latest"
    echo -e "${GREEN}✓ Found auth0-client-id secret${NC}"
fi

if gcloud secrets describe auth0-client-secret --project="$PROJECT_ID" &>/dev/null; then
    SECRETS_ARGS="$SECRETS_ARGS,AUTH0_CLIENT_SECRET=auth0-client-secret:latest"
    echo -e "${GREEN}✓ Found auth0-client-secret secret${NC}"
fi

if [ -z "$SECRETS_ARGS" ]; then
    echo -e "${YELLOW}! No secrets found. Deploying without authentication.${NC}"
    echo -e "${YELLOW}! Run ./setup-gcp-secrets.sh first to enable auth.${NC}"
fi

echo ""

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"

DEPLOY_CMD="gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --no-allow-unauthenticated \
  --set-env-vars BIOCLIN_API_URL=${BIOCLIN_API_URL},PORT=9000,NODE_ENV=production \
  --memory ${MEMORY} \
  --cpu ${CPU} \
  --timeout ${TIMEOUT} \
  --concurrency ${CONCURRENCY} \
  --max-instances ${MAX_INSTANCES} \
  --min-instances ${MIN_INSTANCES} \
  --port 9000"

if [ -n "$SECRETS_ARGS" ]; then
    DEPLOY_CMD="$DEPLOY_CMD $SECRETS_ARGS"
fi

eval "$DEPLOY_CMD"

echo -e "${GREEN}✓ Deployed to Cloud Run${NC}"
echo ""

# Get the service URL
SERVICE_URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --format 'value(status.url)')

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo -e "${BLUE}Service URL:${NC} $SERVICE_URL"
echo ""
echo -e "${BLUE}Test the deployment:${NC}"
echo ""
echo "# Get an identity token:"
echo "  TOKEN=\$(gcloud auth print-identity-token)"
echo ""
echo "# List tools:"
echo "  curl -X POST ${SERVICE_URL}/mcp \\"
echo "    -H \"Authorization: Bearer \$TOKEN\" \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -H \"x-lunar-consumer-tag: Test\" \\"
echo "    -d '{\"method\": \"tools/list\"}'"
echo ""
echo -e "${BLUE}View logs:${NC}"
echo "  gcloud run services logs tail ${SERVICE_NAME} --region ${REGION}"
echo ""
echo -e "${BLUE}Update configuration:${NC}"
echo "  1. Edit mcpx-config/app.yaml"
echo "  2. Run this script again to redeploy"
echo ""
