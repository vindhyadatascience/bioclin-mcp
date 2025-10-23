#!/bin/bash
# Docker Login Helper for Bioclin MCP
#
# Usage:
#   ./docker-login.sh                    # Prompts for credentials
#   BIOCLIN_EMAIL=user@example.com \
#   BIOCLIN_PASSWORD=pass \
#   ./docker-login.sh                    # Uses environment variables

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Bioclin Docker Login${NC}"
echo "========================================"

# Check if credentials are provided via environment
if [ -z "$BIOCLIN_EMAIL" ]; then
    echo ""
    read -p "Email: " BIOCLIN_EMAIL
fi

if [ -z "$BIOCLIN_PASSWORD" ]; then
    echo ""
    read -sp "Password: " BIOCLIN_PASSWORD
    echo ""
fi

echo ""
echo -e "${YELLOW}🐳 Authenticating with Docker container...${NC}"

# Ensure session file exists (not a directory) before Docker mount
# If it's a directory, remove it; if it doesn't exist, create empty file
if [ -d ~/.bioclin_session.json ]; then
    echo -e "${YELLOW}⚠️  Removing incorrect directory at ~/.bioclin_session.json${NC}"
    rm -rf ~/.bioclin_session.json
fi

if [ ! -f ~/.bioclin_session.json ]; then
    touch ~/.bioclin_session.json
fi

# Run authentication in Docker
docker run --rm \
  -e BIOCLIN_EMAIL="$BIOCLIN_EMAIL" \
  -e BIOCLIN_PASSWORD="$BIOCLIN_PASSWORD" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Authentication successful!${NC}"
    echo ""
    echo "Your session is saved at: ~/.bioclin_session.json"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "  1. Test the MCP server: ./docker/run.sh"
    echo "  2. Add to Claude Desktop (see setup/README.md)"
else
    echo ""
    echo -e "${RED}❌ Authentication failed${NC}"
    echo "Please check your credentials and try again"
    exit 1
fi
