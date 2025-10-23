#!/bin/bash
# Docker-based Bioclin login with browser access

# Run authentication container with display and volume mounts
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  -v /tmp/.X11-unix:/tmp/.X11-unix \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login

echo "✅ Authentication complete! Session saved."
