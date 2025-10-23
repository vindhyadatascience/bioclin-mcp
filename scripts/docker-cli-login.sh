#!/bin/bash
# Docker-only CLI login for Bioclin (no browser required)

echo "🐳 Bioclin Docker CLI Login"
echo "=========================================="
echo "This will run the Bioclin auth script in Docker"
echo "and save your session to ~/.bioclin_session.json"
echo ""

# Ensure session file exists (not a directory) before Docker mount
# If it's a directory, remove it; if it doesn't exist, create empty file
if [ -d ~/.bioclin_session.json ]; then
    echo "⚠️  Removing incorrect directory at ~/.bioclin_session.json"
    rm -rf ~/.bioclin_session.json
fi

if [ ! -f ~/.bioclin_session.json ]; then
    touch ~/.bioclin_session.json
fi

# Run interactive Docker container with CLI login
# Note: We use a custom Python script to auto-select option 2
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python -c "
import sys
sys.path.insert(0, '/app/src')
from bioclin_auth import login_cli
login_cli()
"

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Authentication complete!"
  echo "   Session saved to ~/.bioclin_session.json"
  echo ""
  echo "Next steps:"
  echo "  1. Your Claude Desktop config is ready to use"
  echo "  2. Restart Claude Desktop"
  echo "  3. Session expires in 7 days"
else
  echo ""
  echo "❌ Authentication failed"
  echo "   Please check your credentials and try again"
fi
