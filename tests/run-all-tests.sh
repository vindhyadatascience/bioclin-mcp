#!/bin/bash
# Run all tests for MCPX Bioclin integration

set -e

echo "Running all MCPX Bioclin tests..."
echo ""

# Track overall result
OVERALL_RESULT=0

# Run integration tests
echo "===== Integration Tests ====="
if ./tests/test-integration.sh; then
    echo "✓ Integration tests passed"
else
    echo "✗ Integration tests failed"
    OVERALL_RESULT=1
fi

echo ""

# Run chatbot client tests
echo "===== Chatbot Client Tests ====="
if python tests/test-chatbot-client.py; then
    echo "✓ Chatbot client tests passed"
else
    echo "✗ Chatbot client tests failed"
    OVERALL_RESULT=1
fi

echo ""
echo "====================================="

if [ $OVERALL_RESULT -eq 0 ]; then
    echo "✓ All test suites passed!"
else
    echo "✗ Some test suites failed"
fi

exit $OVERALL_RESULT
