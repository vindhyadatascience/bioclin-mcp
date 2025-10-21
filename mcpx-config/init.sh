#!/bin/sh
# Initialization script for MCPX container
# Installs Python dependencies needed for Bioclin MCP server

echo "Installing Bioclin MCP dependencies..."
pip3 install --quiet --no-cache-dir --break-system-packages \
  mcp>=0.9.0 \
  httpx>=0.25.0 \
  'pydantic>=2.0.0' \
  'pydantic[email]>=2.0.0' \
  python-json-logger>=2.0.0

echo "Dependencies installed successfully"
