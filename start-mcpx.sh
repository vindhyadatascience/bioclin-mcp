#!/bin/bash
# Start MCPX with Bioclin MCP Server - Production Ready
# This script properly sets up and starts MCPX with all dependencies

set -e

echo "🚀 Starting MCPX with Bioclin MCP Server"
echo ""

# Stop and remove old container
docker stop mcpx 2>/dev/null || true
docker rm mcpx 2>/dev/null || true

# Start MCPX
echo "Starting MCPX container..."
docker run -d \
  --pull always \
  --privileged \
  -v "$(pwd)/mcpx-config:/lunar/packages/mcpx-server/config" \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -p 9000:9000 \
  -p 5173:5173 \
  -p 9001:9001 \
  -p 3000:3000 \
  -e BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# Wait for container to start
echo "Waiting for container to initialize..."
sleep 3

# Install Python dependencies
echo "Installing Python dependencies..."
docker exec mcpx sh /workspace/mcpx-config/init.sh

# Restart MCPX to pick up the new dependencies
echo "Restarting MCPX to load configuration..."
docker exec mcpx supervisorctl restart mcpx || docker restart mcpx

# Wait for services to be ready
echo "Waiting for MCPX to be ready..."
MAX_WAIT=30
WAITED=0
while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:9000/health > /dev/null 2>&1; then
        break
    fi
    sleep 1
    WAITED=$((WAITED + 1))
    printf "."
done

echo ""
echo ""

if [ $WAITED -eq $MAX_WAIT ]; then
    echo "❌ Timeout waiting for MCPX"
    echo "Check logs: docker logs mcpx"
    exit 1
fi

echo "✅ MCPX is ready!"
echo ""
echo "📊 Access Points:"
echo "  • MCPX API:      http://localhost:9000"
echo "  • Control Plane: http://localhost:5173"
echo "  • Metrics:       http://localhost:3000"
echo ""
echo "🧪 Test it:"
echo "  ./tests/test-integration.sh"
echo ""
echo "📝 View logs:"
echo "  docker logs -f mcpx"
echo ""
echo "🛑 Stop:"
echo "  docker stop mcpx"
echo ""
