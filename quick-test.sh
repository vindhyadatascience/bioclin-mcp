#!/bin/bash
# Quick test to verify MCPX setup is working

# Stop any existing container
docker stop mcpx 2>/dev/null || true
docker rm mcpx 2>/dev/null || true

# Start MCPX
echo "Starting MCPX..."
docker run -d \
  --pull always \
  --privileged \
  -v "$(pwd)/mcpx-config:/lunar/packages/mcpx-server/config" \
  -v "$(pwd):/workspace" \
  -w /workspace \
  -p 9000:9000 \
  -p 5173:5173 \
  -e BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# Wait a bit
echo "Waiting 10 seconds for startup..."
sleep 10

# Show logs
echo ""
echo "=== MCPX Logs ==="
docker logs mcpx 2>&1 | tail -20

# Test if files are accessible
echo ""
echo "=== File Check ==="
docker exec mcpx ls -la /workspace/ | grep bioclin

# Test if config is loaded
echo ""
echo "=== Config Check ==="
docker exec mcpx cat /lunar/packages/mcpx-server/config/app.yaml | grep -A 3 "toolGroups:"

echo ""
echo "=== Done ==="
echo "View full logs: docker logs -f mcpx"
echo "Stop container: docker stop mcpx"
