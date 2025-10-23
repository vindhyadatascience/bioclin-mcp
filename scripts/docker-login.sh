#!/bin/bash
# Docker-based Bioclin login with browser access

# Ensure session file exists (not a directory) before Docker mount
if [ -d ~/.bioclin_session.json ]; then
    echo "⚠️  Removing incorrect directory at ~/.bioclin_session.json"
    rm -rf ~/.bioclin_session.json
fi

if [ ! -f ~/.bioclin_session.json ]; then
    touch ~/.bioclin_session.json
fi

# Run authentication container with display and volume mounts
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login

echo "✅ Authentication complete! Session saved."
