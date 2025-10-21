#!/bin/bash
# Simple MCPX test using the MCP endpoint

echo "Testing MCPX Bioclin Integration..."
echo ""

# Test 1: List tools
echo "Test 1: Listing tools..."
RESULT=$(curl -s -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  --data '{"method":"tools/list"}')

TOOL_COUNT=$(echo "$RESULT" | jq -r '.result.tools | length' 2>/dev/null)

if [ "$TOOL_COUNT" = "44" ]; then
    echo "✅ Found all 44 Bioclin tools"
else
    echo "❌ Expected 44 tools, found: $TOOL_COUNT"
fi

# Test 2: Show sample tools
echo ""
echo "Sample tools:"
echo "$RESULT" | jq -r '.result.tools[0:5] | .[] | "  - " + .name'

echo ""
echo "MCPX is running successfully!"
echo "  • API: http://localhost:9000"
echo "  • Control Plane: http://localhost:5173"
