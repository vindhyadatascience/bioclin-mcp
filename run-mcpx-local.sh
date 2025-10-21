#!/bin/bash
# Run MCPX locally with Bioclin MCP server
# This script handles all the setup needed for local development

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Starting MCPX with Bioclin MCP Server...${NC}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

# Check if Bioclin image needs to be built
if ! docker images | grep -q "bioclin-mcp"; then
    echo -e "${YELLOW}Bioclin MCP image not found. Building...${NC}"
    docker build -t bioclin-mcp:latest .
fi

# Stop existing MCPX container if running
if docker ps -a | grep -q "mcpx"; then
    echo -e "${YELLOW}Stopping existing MCPX container...${NC}"
    docker stop mcpx 2>/dev/null || true
    docker rm mcpx 2>/dev/null || true
fi

# Check if port 9000 is available
if lsof -Pi :9000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${RED}Error: Port 9000 is already in use${NC}"
    echo "Stop the process using port 9000 or use a different port"
    exit 1
fi

# Set environment variables
export BIOCLIN_API_URL="${BIOCLIN_API_URL:-https://bioclin.vindhyadatascience.com/api/v1}"

echo -e "${GREEN}Configuration:${NC}"
echo "  Bioclin API: $BIOCLIN_API_URL"
echo "  MCPX API: http://localhost:9000"
echo "  Control Plane: http://localhost:5173"
echo ""

# Run MCPX with proper volume mounts
echo -e "${GREEN}Starting MCPX container...${NC}"
docker run --rm \
  --pull always \
  --privileged \
  -v "$(pwd)/mcpx-config:/lunar/packages/mcpx-server/config" \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -p 9000:9000 \
  -p 5173:5173 \
  -p 9001:9001 \
  -p 3000:3000 \
  -e BIOCLIN_API_URL="$BIOCLIN_API_URL" \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest &

MCPX_PID=$!

echo ""
echo -e "${GREEN}MCPX is starting...${NC}"
echo ""
echo "Waiting for services to be ready..."

# Wait for MCPX to be ready
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
    WAITED=$((WAITED + 1))
    echo -n "."
done

echo ""

if [ $WAITED -eq $MAX_WAIT ]; then
    echo -e "${RED}Timeout waiting for MCPX to start${NC}"
    echo "Check logs with: docker logs mcpx"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ MCPX is ready!${NC}"
echo ""
echo -e "${GREEN}Access Points:${NC}"
echo "  • MCPX API:        http://localhost:9000"
echo "  • Control Plane:   http://localhost:5173"
echo "  • Metrics:         http://localhost:3000"
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Open Control Plane: open http://localhost:5173"
echo "  2. Run tests: ./tests/test-integration.sh"
echo "  3. View logs: docker logs -f mcpx"
echo ""
echo -e "${YELLOW}To stop:${NC} docker stop mcpx"
echo ""

# Follow logs
echo -e "${GREEN}Showing logs (Ctrl+C to exit, container will keep running):${NC}"
echo ""
docker logs -f mcpx
