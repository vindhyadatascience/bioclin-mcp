# Test Suite for MCPX Bioclin Integration

Comprehensive testing tools for validating the MCPX Bioclin deployment.

## Test Files

### 1. test-integration.sh
Bash-based integration tests for MCPX gateway and Bioclin MCP server.

**Tests:**
- MCPX health endpoint
- Tool listing via MCP protocol
- Bioclin-specific tools presence
- Login functionality
- User info retrieval
- Project listing
- Error handling

**Usage:**
```bash
# Local testing (no auth)
./tests/test-integration.sh

# With OAuth
export AUTH0_DOMAIN="your-domain.us.auth0.com"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"
./tests/test-integration.sh

# Against Cloud Run deployment
export MCPX_URL="https://your-service.run.app"
./tests/test-integration.sh

# With custom credentials
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your_password"
./tests/test-integration.sh
```

### 2. test-chatbot-client.py
Python-based tests for the chatbot client library.

**Tests:**
- Client initialization
- Async context manager
- Tool listing
- Bioclin login
- User info and context
- Project and organization listing
- Error handling

**Usage:**
```bash
# Install dependencies
pip install httpx pytest

# Run tests
python tests/test-chatbot-client.py

# Or with pytest
python -m pytest tests/test-chatbot-client.py -v

# With custom MCPX URL
export MCPX_URL="https://your-service.run.app"
python tests/test-chatbot-client.py
```

## Test Configuration

### Environment Variables

```bash
# Required
MCPX_URL="http://localhost:9000"              # MCPX gateway URL
BIOCLIN_EMAIL="test@example.com"              # Bioclin user email
BIOCLIN_PASSWORD="password"                   # Bioclin user password

# Optional - for OAuth testing
AUTH0_DOMAIN="your-domain.us.auth0.com"
AUTH0_CLIENT_ID="your_client_id"
AUTH0_CLIENT_SECRET="your_client_secret"
CONSUMER_TAG="Test"                           # Consumer tag for MCPX
```

### .env File

Create a `.env` file in the tests directory:

```bash
# tests/.env
MCPX_URL=http://localhost:9000
BIOCLIN_EMAIL=test@example.com
BIOCLIN_PASSWORD=your_password

# OAuth (optional)
# AUTH0_DOMAIN=your-domain.us.auth0.com
# AUTH0_CLIENT_ID=your_client_id
# AUTH0_CLIENT_SECRET=your_client_secret
```

Then source it:
```bash
source tests/.env
./tests/test-integration.sh
```

## Running All Tests

Use the convenience script:

```bash
# Run all tests
./tests/run-all-tests.sh

# Or manually
./tests/test-integration.sh
python tests/test-chatbot-client.py
```

## Test Scenarios

### Scenario 1: Local Development
Test MCPX running locally with Docker:

```bash
# 1. Start MCPX locally
docker run --rm --pull always \
  --privileged \
  -v $(pwd)/mcpx-config:/lunar/packages/mcpx-server/config \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -p 9000:9000 \
  -p 5173:5173 \
  --name mcpx \
  us-central1-docker.pkg.dev/prj-common-442813/mcpx/mcpx:latest

# 2. Run tests
./tests/test-integration.sh
```

### Scenario 2: Cloud Run Deployment
Test production deployment:

```bash
# 1. Deploy to Cloud Run
./deploy/deploy-cloudrun.sh

# 2. Get service URL
export MCPX_URL=$(gcloud run services describe mcpx-bioclin \
  --region us-central1 \
  --format 'value(status.url)')

# 3. Run tests with OAuth
export AUTH0_DOMAIN="your-domain.us.auth0.com"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"
./tests/test-integration.sh
```

### Scenario 3: CI/CD Pipeline
Integrate tests into CI/CD:

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
        run: |
          docker-compose -f docker-compose.cloudrun-test.yml up -d
          sleep 10

      - name: Run integration tests
        run: ./tests/test-integration.sh

      - name: Run Python tests
        run: |
          pip install httpx pytest
          python tests/test-chatbot-client.py
```

## Expected Results

### All Tests Passing
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

## Troubleshooting

### MCPX not responding
```bash
# Check if MCPX is running
curl http://localhost:9000/health

# Check MCPX logs
docker logs mcpx
```

### Authentication failures
```bash
# Verify OAuth token
curl --request POST \
  --url "https://${AUTH0_DOMAIN}/oauth/token" \
  --header 'content-type: application/json' \
  --data "{
    \"client_id\":\"${AUTH0_CLIENT_ID}\",
    \"client_secret\":\"${AUTH0_CLIENT_SECRET}\",
    \"audience\":\"mcpx-bioclin\",
    \"grant_type\":\"client_credentials\"
  }" | jq .
```

### Bioclin login failures
```bash
# Test Bioclin API directly
curl -X POST https://bioclin.vindhyadatascience.com/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=your_password"
```

### Tool not found errors
```bash
# List all available tools
curl -X POST http://localhost:9000/mcp \
  -H "Content-Type: application/json" \
  -H "x-lunar-consumer-tag: Test" \
  -d '{"method": "tools/list"}' | jq '.result.tools[] | .name'
```

## Continuous Testing

### Watch mode for development
```bash
# Re-run tests on file changes (requires entr)
ls tests/*.sh tests/*.py | entr -c ./tests/test-integration.sh
```

### Scheduled testing
```bash
# Add to cron for periodic health checks
# Run every hour
0 * * * * cd /path/to/bioclin-mcp && ./tests/test-integration.sh >> /var/log/mcpx-tests.log 2>&1
```

## Performance Testing

For load testing, use tools like:
- **Apache Bench (ab)**
- **wrk**
- **Locust**

Example with `ab`:
```bash
# 100 requests, 10 concurrent
ab -n 100 -c 10 -T 'application/json' \
  -H 'x-lunar-consumer-tag: Test' \
  -p payload.json \
  http://localhost:9000/mcp
```

## Contributing

When adding new features:
1. Add corresponding tests
2. Update this README
3. Ensure all tests pass before committing
4. Update test expectations if API changes

## References

- [MCP Protocol Spec](https://modelcontextprotocol.io/)
- [MCPX Documentation](https://docs.lunar.dev/mcpx/)
- [Bioclin API Docs](https://bioclin.vindhyadatascience.com/docs)
