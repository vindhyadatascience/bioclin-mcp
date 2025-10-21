# MCPX Bioclin Test Suite

**Make sure everything works! Run these tests to verify your MCPX + Bioclin setup.**

## What Are These Tests For?

These tests verify that:
- ✅ MCPX is running and accessible
- ✅ All 44 Bioclin tools are available
- ✅ You can log in to Bioclin
- ✅ You can create projects and runs
- ✅ Error handling works correctly

**Think of it as:** A health check for your entire MCPX + Bioclin system.

## The Test Files

### test-integration.sh (Bash Script)
**What it does:** Tests the MCPX gateway and Bioclin integration

**Tests included:**
- MCPX health check
- Tool listing (checks all 44 tools are there)
- Bioclin login
- User info retrieval
- Project listing
- Error handling

**When to use:** After starting MCPX locally or deploying to Cloud Run

### test-chatbot-client.py (Python Script)
**What it does:** Tests the Python chatbot client library

**Tests included:**
- Client initialization
- Async operations
- All wrapper methods (login, list_projects, etc.)
- Error handling

**When to use:** Before building a chatbot or after making changes to the client

### run-all-tests.sh (Convenience Script)
**What it does:** Runs both test suites in sequence

**When to use:** Before committing code or deploying to production

## Quick Start

### Test Your Local MCPX

**Step 1:** Make sure MCPX is running
```bash
./start-mcpx.sh
```

**Step 2:** Run the tests
```bash
./test-mcpx-simple.sh
```

**Expected output:**
```
Testing MCPX Bioclin Integration...

Test 1: Listing tools...
✅ Found all 44 Bioclin tools

Sample tools:
  - bioclin_login
  - bioclin_get_user_me
  - bioclin_get_projects
  - bioclin_create_project
  - bioclin_create_run

MCPX is running successfully!
  • API: http://localhost:9000
  • Control Plane: http://localhost:5173
```

### Run Full Integration Tests

For more comprehensive testing:

```bash
./tests/test-integration.sh
```

**You'll see:**
```
========================================
MCPX Bioclin Integration Test Suite
========================================

✓ PASS Health endpoint responding
✓ PASS Found 44 tools
✓ PASS Tool present: bioclin_login
✓ PASS Tool present: bioclin_get_user_me
✓ PASS Bioclin login successful
✓ PASS Got user info: test@example.com
✓ PASS Found 5 projects

========================================
Test Summary
========================================

Tests Passed: 15
Tests Failed: 0

✓ All tests passed!
```

### Run Python Client Tests

```bash
# Install dependencies first (if needed)
pip install httpx pytest

# Run tests
python tests/test-chatbot-client.py
```

## Configuration

### Default Settings

By default, tests use:
- **MCPX URL:** http://localhost:9000
- **No authentication** (perfect for local testing)

### Custom Settings

Want to test against a different setup? Set these environment variables:

```bash
# Test against Cloud Run
export MCPX_URL="https://mcpx-bioclin-xxxxx-uc.a.run.app"

# Use different Bioclin credentials
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your_password"

# Then run tests
./tests/test-integration.sh
```

### Testing with OAuth (Production)

If your deployment uses OAuth:

```bash
export AUTH0_DOMAIN="your-app.us.auth0.com"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"

./tests/test-integration.sh
```

### Using a .env File

Create `tests/.env` for convenience:

```bash
# tests/.env
MCPX_URL=http://localhost:9000
BIOCLIN_EMAIL=test@example.com
BIOCLIN_PASSWORD=your_password

# Uncomment for OAuth testing
# AUTH0_DOMAIN=your-app.us.auth0.com
# AUTH0_CLIENT_ID=your_client_id
# AUTH0_CLIENT_SECRET=your_client_secret
```

Load it before running tests:
```bash
source tests/.env
./tests/test-integration.sh
```

## Common Testing Scenarios

### Scenario 1: After Starting MCPX Locally

**When:** You just ran `./start-mcpx.sh`

**Test command:**
```bash
./test-mcpx-simple.sh
```

**What to expect:** Should see "✅ Found all 44 Bioclin tools"

### Scenario 2: Before Deploying to Cloud Run

**When:** You want to make sure everything works before deployment

**Test command:**
```bash
./tests/run-all-tests.sh
```

**What to expect:** All tests should pass (0 failures)

### Scenario 3: After Deploying to Cloud Run

**When:** You deployed to Cloud Run and want to verify it works

**Test commands:**
```bash
# Get your Cloud Run URL
export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
  --region us-central1 \
  --format 'value(status.url)')

# Set OAuth credentials (if enabled)
export AUTH0_DOMAIN="your-app.us.auth0.com"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"

# Run tests
./tests/test-integration.sh
```

**What to expect:** All tests pass, connecting to your Cloud Run service

### Scenario 4: Before Building a Chatbot

**When:** You're about to build a chatbot using the Python client

**Test command:**
```bash
python tests/test-chatbot-client.py
```

**What to expect:** All client methods work correctly

## Troubleshooting Tests

### Problem: "Connection refused" error

**Cause:** MCPX isn't running

**Fix:**
```bash
# Check if MCPX is running
docker ps | grep mcpx

# Not running? Start it
./start-mcpx.sh

# Check health
curl http://localhost:9000/health
```

### Problem: "Tool not found" error

**Cause:** Bioclin MCP server didn't start correctly

**Fix:**
```bash
# Check MCPX logs
docker logs mcpx

# Look for "STDIO client connected"
# If not there, restart MCPX
docker restart mcpx

# Wait a bit, then check logs again
sleep 5
docker logs mcpx | tail -20
```

### Problem: "Bioclin login failed"

**Cause:** Invalid credentials or Bioclin API is down

**Fix:**
```bash
# Test Bioclin API directly
curl -X POST https://bioclin.vindhyadatascience.com/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=your_password"

# If this fails, check:
# 1. Are your credentials correct?
# 2. Is the Bioclin API accessible?
# 3. Do you have internet connection?
```

### Problem: "OAuth authentication failed"

**Cause:** Wrong OAuth credentials or Auth0 not configured

**Fix:**
```bash
# Test OAuth token directly
curl --request POST \
  --url "https://${AUTH0_DOMAIN}/oauth/token" \
  --header 'content-type: application/json' \
  --data "{
    \"client_id\":\"${AUTH0_CLIENT_ID}\",
    \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
    \"audience\":\"mcpx-bioclin\",
    \"grant_type\":\"client_credentials\"
  }" | jq .

# If this fails, check:
# 1. Is AUTH0_DOMAIN correct? (should be like: your-app.us.auth0.com)
# 2. Are CLIENT_ID and CLIENT_SECRET correct?
# 3. Is the Auth0 API configured correctly?
```

### Problem: "Wrong number of tools" (not 44)

**Cause:** Some tools didn't load or configuration issue

**Fix:**
```bash
# List all tools to see what's available
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools[] | .name'

# Count them
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools | length'

# If less than 44, check MCPX logs for errors
docker logs mcpx 2>&1 | grep -i error
```

## Test Results Explained

### What "PASS" Means

✅ **PASS Health endpoint responding** - MCPX is running and accessible
✅ **PASS Found 44 tools** - All Bioclin tools are loaded
✅ **PASS Tool present: bioclin_login** - Login tool is available
✅ **PASS Bioclin login successful** - Can authenticate with Bioclin API
✅ **PASS Got user info** - Can retrieve user data from Bioclin
✅ **PASS Found X projects** - Can list projects

### What "FAIL" Means

❌ **FAIL** means something is broken and needs fixing

**Common failures:**
- Health endpoint - MCPX not running
- Tool count - MCP server didn't start
- Login - Wrong credentials or Bioclin API down
- OAuth - Authentication not configured correctly

**What to do:** Check the error message and see the Troubleshooting section above.

## When to Run Tests

### Always Run Tests

✅ **Before deploying to Cloud Run** - Make sure everything works locally first
✅ **After configuration changes** - Verify changes didn't break anything
✅ **Before building a chatbot** - Ensure the client library works
✅ **After updating MCPX** - Verify compatibility with new version

### Optional (But Good Practice)

✅ **After git pull** - Make sure new changes work
✅ **Before committing code** - Don't break the build!
✅ **Daily/Weekly** - Catch issues early

## Advanced: CI/CD Integration

Want tests to run automatically? Add them to GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Test MCPX Bioclin

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Start MCPX
        run: ./start-mcpx.sh

      - name: Wait for MCPX
        run: sleep 10

      - name: Run tests
        run: ./tests/run-all-tests.sh
```

## Quick Reference

### Most Common Commands

```bash
# Quick test (after starting MCPX locally)
./test-mcpx-simple.sh

# Full integration tests
./tests/test-integration.sh

# Python client tests
python tests/test-chatbot-client.py

# Run all tests
./tests/run-all-tests.sh

# Test against Cloud Run
export MCPX_URL="https://your-service.run.app"
./tests/test-integration.sh
```

### Useful Debugging Commands

```bash
# Check if MCPX is running
docker ps | grep mcpx

# View MCPX logs
docker logs -f mcpx

# Test MCPX health
curl http://localhost:9000/health

# List all tools
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq .
```

## Need Help?

- 📖 **Full deployment guide:** `../MCPX-DEPLOYMENT.md`
- 🆘 **Troubleshooting:** `../TROUBLESHOOTING.md`
- 🔧 **Configuration:** `../mcpx-config/README.md`

## Contributing

Adding new features? Please:
1. ✅ Add corresponding tests
2. ✅ Update this README with examples
3. ✅ Make sure all tests pass before committing
4. ✅ Update expected results if API changes

**Remember:** Good tests make everyone's life easier! 🎉
