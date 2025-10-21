#!/bin/bash
# Test script for local MCPX setup
# This script validates that MCPX is running and can communicate with Bioclin MCP server

set -e

MCPX_URL="http://localhost:9000"
CONSUMER_TAG="Test"

echo "🧪 Testing MCPX Integration with Bioclin MCP Server"
echo "=================================================="

# Test 1: Health Check
echo ""
echo "Test 1: MCPX Health Check"
echo "-------------------------"
if curl -f -s "${MCPX_URL}/health" > /dev/null 2>&1; then
    echo "✅ MCPX health endpoint responded"
else
    echo "❌ MCPX health endpoint failed - is MCPX running?"
    exit 1
fi

# Test 2: List Tools
echo ""
echo "Test 2: List MCP Tools"
echo "----------------------"
TOOLS_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
  -d '{"method": "tools/list"}')

echo "Response: ${TOOLS_RESPONSE}" | jq '.' 2>/dev/null || echo "${TOOLS_RESPONSE}"

# Count tools
TOOL_COUNT=$(echo "${TOOLS_RESPONSE}" | jq '.result.tools | length' 2>/dev/null || echo "0")
echo ""
if [ "${TOOL_COUNT}" -gt 0 ]; then
    echo "✅ Found ${TOOL_COUNT} tools"
    echo ""
    echo "Sample tools:"
    echo "${TOOLS_RESPONSE}" | jq '.result.tools[0:3] | .[] | {name: .name, description: .description}' 2>/dev/null || echo "Could not parse tools"
else
    echo "❌ No tools found - check Bioclin MCP server connection"
    exit 1
fi

# Test 3: Check for specific Bioclin tools
echo ""
echo "Test 3: Verify Bioclin-specific Tools"
echo "--------------------------------------"
BIOCLIN_TOOLS=("bioclin_login" "bioclin_get_user_me" "bioclin_get_projects" "bioclin_create_run")

for tool in "${BIOCLIN_TOOLS[@]}"; do
    if echo "${TOOLS_RESPONSE}" | jq -e ".result.tools[] | select(.name==\"${tool}\")" > /dev/null 2>&1; then
        echo "✅ Found tool: ${tool}"
    else
        echo "❌ Missing expected tool: ${tool}"
    fi
done

# Test 4: Check MCPX Control Plane
echo ""
echo "Test 4: MCPX Control Plane"
echo "--------------------------"
if curl -f -s "http://localhost:5173" > /dev/null 2>&1; then
    echo "✅ MCPX Control Plane is accessible at http://localhost:5173"
else
    echo "⚠️  MCPX Control Plane not accessible (this is optional)"
fi

echo ""
echo "=================================================="
echo "✅ All critical tests passed!"
echo ""
echo "Next steps:"
echo "1. Open MCPX Control Plane: http://localhost:5173"
echo "2. Update Claude Desktop config with: mcpx-config/claude-desktop-config.json"
echo "3. Test from Claude Desktop"
echo ""
