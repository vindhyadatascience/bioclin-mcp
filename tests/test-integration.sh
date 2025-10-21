#!/bin/bash
# Comprehensive Integration Test Suite for MCPX Bioclin
# Tests the complete stack: MCPX gateway + Bioclin MCP server

set -e

# Configuration
MCPX_URL="${MCPX_URL:-http://localhost:9000}"
CONSUMER_TAG="${CONSUMER_TAG:-Test}"
BIOCLIN_EMAIL="${BIOCLIN_EMAIL:-test@example.com}"
BIOCLIN_PASSWORD="${BIOCLIN_PASSWORD:-password}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}✓ PASS${NC} $1"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}✗ FAIL${NC} $1"
    ((TESTS_FAILED++))
}

log_skip() {
    echo -e "${YELLOW}⊘ SKIP${NC} $1"
}

log_info() {
    echo -e "${BLUE}ℹ INFO${NC} $1"
}

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is required but not installed${NC}"
    echo "Install with: brew install jq (macOS) or apt-get install jq (Linux)"
    exit 1
fi

# Check if curl is installed
if ! command -v curl &> /dev/null; then
    echo -e "${RED}Error: curl is required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MCPX Bioclin Integration Test Suite${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Configuration:"
echo "  MCPX URL: $MCPX_URL"
echo "  Consumer: $CONSUMER_TAG"
echo ""

# Get OAuth token if AUTH variables are set
if [ -n "$AUTH0_DOMAIN" ] && [ -n "$AUTH0_CLIENT_ID" ] && [ -n "$AUTH0_CLIENT_SECRET" ]; then
    log_test "Getting OAuth token..."

    TOKEN_RESPONSE=$(curl -s --request POST \
        --url "https://${AUTH0_DOMAIN}/oauth/token" \
        --header 'content-type: application/json' \
        --data "{
            \"client_id\":\"${AUTH0_CLIENT_ID}\",
            \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
            \"audience\":\"mcpx-bioclin\",
            \"grant_type\":\"client_credentials\"
        }")

    ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token')

    if [ "$ACCESS_TOKEN" != "null" ] && [ -n "$ACCESS_TOKEN" ]; then
        log_pass "OAuth token obtained"
        AUTH_HEADER="Authorization: Bearer $ACCESS_TOKEN"
    else
        log_fail "Failed to get OAuth token"
        echo "Response: $TOKEN_RESPONSE"
        AUTH_HEADER=""
    fi
else
    log_info "No OAuth config - testing without authentication"
    AUTH_HEADER=""
fi

echo ""

# Test 1: Health Check
log_test "Test 1: MCPX Health Check"
if curl -sf "${MCPX_URL}/health" > /dev/null; then
    log_pass "Health endpoint responding"
else
    log_fail "Health endpoint not responding"
fi

# Test 2: List Tools
log_test "Test 2: List MCP Tools"
TOOLS_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
    -H "${AUTH_HEADER}" \
    -d '{"method": "tools/list"}')

TOOL_COUNT=$(echo "$TOOLS_RESPONSE" | jq '.result.tools | length' 2>/dev/null || echo "0")

if [ "$TOOL_COUNT" -gt 0 ]; then
    log_pass "Found $TOOL_COUNT tools"
else
    log_fail "No tools found or invalid response"
    echo "Response: $TOOLS_RESPONSE"
fi

# Test 3: Verify Bioclin Tools Present
log_test "Test 3: Verify Bioclin-specific Tools"
REQUIRED_TOOLS=("bioclin_login" "bioclin_get_user_me" "bioclin_get_projects" "bioclin_create_run")

for tool in "${REQUIRED_TOOLS[@]}"; do
    if echo "$TOOLS_RESPONSE" | jq -e ".result.tools[] | select(.name==\"${tool}\")" > /dev/null 2>&1; then
        log_pass "Tool present: $tool"
    else
        log_fail "Tool missing: $tool"
    fi
done

# Test 4: Call Tool - Login
log_test "Test 4: Bioclin Login Tool"
LOGIN_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
    -H "${AUTH_HEADER}" \
    -d "{
        \"method\": \"tools/call\",
        \"params\": {
            \"name\": \"bioclin_login\",
            \"arguments\": {
                \"username\": \"${BIOCLIN_EMAIL}\",
                \"password\": \"${BIOCLIN_PASSWORD}\"
            }
        }
    }")

# Check if login was successful
if echo "$LOGIN_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
    # Check for error in the response content
    ERROR_CHECK=$(echo "$LOGIN_RESPONSE" | jq -r '.result.content[0].text' | jq -r '.error' 2>/dev/null || echo "null")

    if [ "$ERROR_CHECK" = "null" ]; then
        log_pass "Bioclin login successful"
        LOGGED_IN=true
    else
        log_fail "Bioclin login failed: $ERROR_CHECK"
        LOGGED_IN=false
    fi
else
    log_fail "Bioclin login tool call failed"
    echo "Response: $LOGIN_RESPONSE"
    LOGGED_IN=false
fi

# Test 5: Get User Info (requires login)
if [ "$LOGGED_IN" = true ]; then
    log_test "Test 5: Get Bioclin User Info"
    USER_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
        -H "Content-Type: application/json" \
        -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
        -H "${AUTH_HEADER}" \
        -d '{
            "method": "tools/call",
            "params": {
                "name": "bioclin_get_user_me",
                "arguments": {}
            }
        }')

    if echo "$USER_RESPONSE" | jq -e '.result.content[0].text' > /dev/null 2>&1; then
        USERNAME=$(echo "$USER_RESPONSE" | jq -r '.result.content[0].text' | jq -r '.username' 2>/dev/null || echo "null")

        if [ "$USERNAME" != "null" ]; then
            log_pass "Got user info: $USERNAME"
        else
            log_fail "Could not parse user info"
        fi
    else
        log_fail "Failed to get user info"
    fi
else
    log_skip "Test 5: Get User Info (login required)"
fi

# Test 6: List Projects (requires login)
if [ "$LOGGED_IN" = true ]; then
    log_test "Test 6: List User Projects"
    PROJECTS_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
        -H "Content-Type: application/json" \
        -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
        -H "${AUTH_HEADER}" \
        -d '{
            "method": "tools/call",
            "params": {
                "name": "bioclin_get_user_projects",
                "arguments": {}
            }
        }')

    if echo "$PROJECTS_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
        PROJECT_COUNT=$(echo "$PROJECTS_RESPONSE" | jq -r '.result.content[0].text' | jq -r '.count' 2>/dev/null || echo "0")
        log_pass "Found $PROJECT_COUNT projects"
    else
        log_fail "Failed to list projects"
    fi
else
    log_skip "Test 6: List Projects (login required)"
fi

# Test 7: List Analysis Types (requires login)
if [ "$LOGGED_IN" = true ]; then
    log_test "Test 7: List Analysis Types"
    TYPES_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
        -H "Content-Type: application/json" \
        -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
        -H "${AUTH_HEADER}" \
        -d '{
            "method": "tools/call",
            "params": {
                "name": "bioclin_get_analysis_types",
                "arguments": {}
            }
        }')

    if echo "$TYPES_RESPONSE" | jq -e '.result' > /dev/null 2>&1; then
        TYPE_COUNT=$(echo "$TYPES_RESPONSE" | jq -r '.result.content[0].text' | jq -r '.count' 2>/dev/null || echo "0")
        log_pass "Found $TYPE_COUNT analysis types"
    else
        log_fail "Failed to list analysis types"
    fi
else
    log_skip "Test 7: List Analysis Types (login required)"
fi

# Test 8: Error Handling - Invalid Tool
log_test "Test 8: Error Handling (Invalid Tool)"
ERROR_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
    -H "${AUTH_HEADER}" \
    -d '{
        "method": "tools/call",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    }')

if echo "$ERROR_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    log_pass "Properly returned error for invalid tool"
else
    log_fail "Did not return error for invalid tool"
fi

# Test 9: Error Handling - Missing Arguments
log_test "Test 9: Error Handling (Missing Arguments)"
ERROR_RESPONSE=$(curl -s -X POST "${MCPX_URL}/mcp" \
    -H "Content-Type: application/json" \
    -H "x-lunar-consumer-tag: ${CONSUMER_TAG}" \
    -H "${AUTH_HEADER}" \
    -d '{
        "method": "tools/call",
        "params": {
            "name": "bioclin_create_project",
            "arguments": {}
        }
    }')

# Should get an error for missing required arguments
if echo "$ERROR_RESPONSE" | jq -e '.error' > /dev/null 2>&1 || \
   echo "$ERROR_RESPONSE" | jq -e '.result.content[0].text' | grep -q "error"; then
    log_pass "Properly handled missing arguments"
else
    log_fail "Did not properly handle missing arguments"
fi

# Print summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Test Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
