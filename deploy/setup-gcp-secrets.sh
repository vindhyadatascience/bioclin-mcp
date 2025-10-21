#!/bin/bash
# Setup Google Cloud Platform Secrets for MCPX Bioclin Deployment
# This script creates secrets in Google Secret Manager

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="${GCP_PROJECT_ID:-your-gcp-project-id}"
REGION="${GCP_REGION:-us-central1}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}Setting up GCP Secrets for MCPX Bioclin${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI not found. Please install it first.${NC}"
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if PROJECT_ID is set
if [ "$PROJECT_ID" = "your-gcp-project-id" ]; then
    echo -e "${YELLOW}Warning: GCP_PROJECT_ID not set${NC}"
    echo "Please set it:"
    echo "  export GCP_PROJECT_ID=your-actual-project-id"
    echo "  ./setup-gcp-secrets.sh"
    exit 1
fi

echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set the project
echo -e "${YELLOW}Setting GCP project...${NC}"
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo -e "${YELLOW}Enabling required GCP APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    --project="$PROJECT_ID"

echo -e "${GREEN}✓ APIs enabled${NC}"
echo ""

# Create secrets for OAuth (Auth0 example)
echo -e "${YELLOW}Creating OAuth secrets...${NC}"
echo "Please enter your Auth0 credentials (or press Enter to skip):"
echo ""

read -p "Auth0 Domain (e.g., dev-xxxxx.us.auth0.com): " AUTH0_DOMAIN
if [ -n "$AUTH0_DOMAIN" ]; then
    echo -n "$AUTH0_DOMAIN" | gcloud secrets create auth0-domain \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID" 2>/dev/null \
        && echo -e "${GREEN}✓ Created auth0-domain secret${NC}" \
        || echo -e "${YELLOW}! auth0-domain secret already exists${NC}"
fi

read -p "Auth0 Client ID: " AUTH0_CLIENT_ID
if [ -n "$AUTH0_CLIENT_ID" ]; then
    echo -n "$AUTH0_CLIENT_ID" | gcloud secrets create auth0-client-id \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID" 2>/dev/null \
        && echo -e "${GREEN}✓ Created auth0-client-id secret${NC}" \
        || echo -e "${YELLOW}! auth0-client-id secret already exists${NC}"
fi

read -sp "Auth0 Client Secret: " AUTH0_CLIENT_SECRET
echo ""
if [ -n "$AUTH0_CLIENT_SECRET" ]; then
    echo -n "$AUTH0_CLIENT_SECRET" | gcloud secrets create auth0-client-secret \
        --data-file=- \
        --replication-policy="automatic" \
        --project="$PROJECT_ID" 2>/dev/null \
        && echo -e "${GREEN}✓ Created auth0-client-secret secret${NC}" \
        || echo -e "${YELLOW}! auth0-client-secret secret already exists${NC}"
fi

echo ""

# Get the Cloud Run service account
SERVICE_ACCOUNT=$(gcloud iam service-accounts list \
    --project="$PROJECT_ID" \
    --filter="email:*-compute@developer.gserviceaccount.com" \
    --format="value(email)" | head -n 1)

if [ -z "$SERVICE_ACCOUNT" ]; then
    echo -e "${YELLOW}Warning: Could not find default compute service account${NC}"
    echo "Creating a custom service account for Cloud Run..."

    SERVICE_ACCOUNT="mcpx-bioclin@${PROJECT_ID}.iam.gserviceaccount.com"
    gcloud iam service-accounts create mcpx-bioclin \
        --display-name="MCPX Bioclin Service Account" \
        --project="$PROJECT_ID"
fi

echo "Service Account: $SERVICE_ACCOUNT"
echo ""

# Grant Secret Manager access to the service account
echo -e "${YELLOW}Granting Secret Manager access to service account...${NC}"

for secret in auth0-domain auth0-client-id auth0-client-secret; do
    if gcloud secrets describe "$secret" --project="$PROJECT_ID" &>/dev/null; then
        gcloud secrets add-iam-policy-binding "$secret" \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/secretmanager.secretAccessor" \
            --project="$PROJECT_ID" \
            && echo -e "${GREEN}✓ Granted access to $secret${NC}"
    fi
done

echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}✓ GCP Secrets setup complete!${NC}"
echo -e "${GREEN}==================================================${NC}"
echo ""
echo "Next steps:"
echo "1. Review secrets: gcloud secrets list --project=$PROJECT_ID"
echo "2. Deploy to Cloud Run: ./deploy-cloudrun.sh"
echo ""
