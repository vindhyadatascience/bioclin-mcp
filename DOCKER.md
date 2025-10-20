# Bioclin MCP Server - Docker Deployment Guide

This guide explains how to build and run the Bioclin MCP Server using Docker for improved portability and dependency management.

## Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose 2.0+ (optional, but recommended)
- Access to a Bioclin API instance

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/alex/VindhyaProjects/bioclin-mcp
   ```

2. **Set the Bioclin API URL (optional):**
   ```bash
   export BIOCLIN_API_URL="http://your-bioclin-instance:8000"
   ```

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **View logs:**
   ```bash
   docker-compose logs -f bioclin-mcp
   ```

5. **Stop the server:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t bioclin-mcp:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -it --rm \
     --name bioclin-mcp \
     -e BIOCLIN_API_URL="http://host.docker.internal:8000" \
     bioclin-mcp:latest
   ```

## Configuration

### Environment Variables

The container supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `BIOCLIN_API_URL` | URL of the Bioclin API server | `http://localhost:8000` |

### Setting Environment Variables

**Docker Compose (.env file):**
Create a `.env` file in the project root:
```bash
BIOCLIN_API_URL=http://your-bioclin-instance:8000
```

**Docker CLI:**
```bash
docker run -e BIOCLIN_API_URL="http://your-api:8000" bioclin-mcp:latest
```

## Using with Claude Desktop

To use the Dockerized MCP server with Claude Desktop, you need to configure Claude to run the Docker container.

### Configuration for macOS/Linux

Edit your Claude Desktop config:
```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux
nano ~/.config/Claude/claude_desktop_config.json
```

Add the following configuration:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network=host",
        "-e", "BIOCLIN_API_URL=http://localhost:8000",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

### Configuration for Windows

Edit your Claude Desktop config:
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

Add:
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "BIOCLIN_API_URL=http://host.docker.internal:8000",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

**Note:** On Windows, use `host.docker.internal` to access services running on your host machine.

## Network Configuration

### Accessing Localhost Services

When your Bioclin API is running on your host machine (localhost):

**Linux:**
Use `--network=host` mode:
```bash
docker run --network=host -e BIOCLIN_API_URL="http://localhost:8000" bioclin-mcp:latest
```

**macOS/Windows:**
Use `host.docker.internal`:
```bash
docker run -e BIOCLIN_API_URL="http://host.docker.internal:8000" bioclin-mcp:latest
```

### Accessing External Services

For external Bioclin API servers, just use the full URL:
```bash
docker run -e BIOCLIN_API_URL="https://bioclin.example.com" bioclin-mcp:latest
```

## Building the Image

### Standard Build
```bash
docker build -t bioclin-mcp:latest .
```

### Build with Specific Tag
```bash
docker build -t bioclin-mcp:1.0.0 .
```

### Build with Build Arguments (if needed)
```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  -t bioclin-mcp:latest \
  .
```

## Advanced Usage

### Interactive Shell in Container

To debug or explore the container:
```bash
docker run -it --rm \
  --entrypoint /bin/bash \
  bioclin-mcp:latest
```

### Mount Local Code for Development

Useful for testing changes without rebuilding:
```bash
docker run -it --rm \
  -v $(pwd)/bioclin_mcp_server.py:/app/bioclin_mcp_server.py \
  -v $(pwd)/bioclin_schemas.py:/app/bioclin_schemas.py \
  -e BIOCLIN_API_URL="http://host.docker.internal:8000" \
  bioclin-mcp:latest
```

### Resource Limits

Limit CPU and memory usage:
```bash
docker run -it --rm \
  --cpus="1.0" \
  --memory="512m" \
  bioclin-mcp:latest
```

### Custom Logging

Configure JSON logging:
```bash
docker run -it --rm \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  bioclin-mcp:latest
```

## Docker Compose Advanced Features

### Full docker-compose.yml Example

```yaml
version: '3.8'

services:
  bioclin-mcp:
    build:
      context: .
      dockerfile: Dockerfile
    image: bioclin-mcp:latest
    container_name: bioclin-mcp-server

    environment:
      - BIOCLIN_API_URL=${BIOCLIN_API_URL:-http://host.docker.internal:8000}

    stdin_open: true
    tty: true

    # For Linux: use host network
    # network_mode: host

    # For Mac/Windows: use bridge network
    networks:
      - bioclin-network

    restart: unless-stopped

    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  bioclin-network:
    driver: bridge
```

### Running Multiple Instances

To run multiple MCP servers (e.g., for different API endpoints):

```yaml
version: '3.8'

services:
  bioclin-mcp-prod:
    image: bioclin-mcp:latest
    environment:
      - BIOCLIN_API_URL=https://prod.bioclin.example.com
    stdin_open: true
    tty: true

  bioclin-mcp-staging:
    image: bioclin-mcp:latest
    environment:
      - BIOCLIN_API_URL=https://staging.bioclin.example.com
    stdin_open: true
    tty: true
```

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker logs bioclin-mcp
```

**Run in foreground to see errors:**
```bash
docker run -it bioclin-mcp:latest
```

### Cannot Connect to Bioclin API

**Test connectivity from container:**
```bash
docker run -it --rm --entrypoint /bin/bash bioclin-mcp:latest
# Inside container:
apt-get update && apt-get install -y curl
curl http://host.docker.internal:8000/
```

**Check network mode:**
- Linux: Use `--network=host`
- Mac/Windows: Use `host.docker.internal`

### Permission Issues

**Check file permissions:**
```bash
docker run -it --rm --entrypoint ls bioclin-mcp:latest -la
```

### Python Module Import Errors

**Verify dependencies:**
```bash
docker run -it --rm --entrypoint pip bioclin-mcp:latest list
```

### Health Check Failures

**Check health status:**
```bash
docker inspect --format='{{.State.Health.Status}}' bioclin-mcp
```

**View health check logs:**
```bash
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' bioclin-mcp
```

## Image Management

### List Images
```bash
docker images | grep bioclin-mcp
```

### Remove Image
```bash
docker rmi bioclin-mcp:latest
```

### Clean Up Old Images
```bash
docker image prune -a
```

### Export/Import Image

**Export:**
```bash
docker save bioclin-mcp:latest | gzip > bioclin-mcp.tar.gz
```

**Import:**
```bash
docker load < bioclin-mcp.tar.gz
```

### Push to Registry

**Tag for registry:**
```bash
docker tag bioclin-mcp:latest your-registry/bioclin-mcp:latest
```

**Push:**
```bash
docker push your-registry/bioclin-mcp:latest
```

## Security Best Practices

1. **Don't include secrets in the image:**
   - Use environment variables
   - Use Docker secrets for sensitive data

2. **Run as non-root user (optional enhancement):**
   Add to Dockerfile:
   ```dockerfile
   RUN useradd -m -u 1000 mcpuser
   USER mcpuser
   ```

3. **Use specific base image versions:**
   ```dockerfile
   FROM python:3.11.7-slim
   ```

4. **Scan for vulnerabilities:**
   ```bash
   docker scan bioclin-mcp:latest
   ```

5. **Keep base images updated:**
   ```bash
   docker pull python:3.11-slim
   docker build --no-cache -t bioclin-mcp:latest .
   ```

## Performance Optimization

### Multi-stage Build Benefits

The Dockerfile uses a multi-stage build to:
- Reduce final image size
- Separate build and runtime dependencies
- Improve build caching

### Layer Caching

Optimize rebuilds by ordering Dockerfile instructions:
1. Base image
2. System dependencies (rarely change)
3. requirements.txt (changes occasionally)
4. Application code (changes frequently)

### Build Cache

Speed up rebuilds:
```bash
docker build --cache-from bioclin-mcp:latest -t bioclin-mcp:latest .
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build image
        run: docker build -t bioclin-mcp:latest .

      - name: Test image
        run: |
          docker run --rm bioclin-mcp:latest python -c "import bioclin_mcp_server"

      - name: Push to registry
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USERNAME }}" --password-stdin
          docker push your-registry/bioclin-mcp:latest
```

## Monitoring

### Container Stats
```bash
docker stats bioclin-mcp
```

### Logs with Timestamps
```bash
docker logs -f --timestamps bioclin-mcp
```

### Export Logs
```bash
docker logs bioclin-mcp > mcp-server.log
```

## Support

For Docker-specific issues:
1. Check Docker daemon status: `docker info`
2. Verify Docker version: `docker --version`
3. Check disk space: `docker system df`
4. Review logs: `docker logs bioclin-mcp`

For application issues, see main [README.md](README.md)

---

**Quick Reference:**

```bash
# Build
docker build -t bioclin-mcp:latest .

# Run (Linux)
docker run -it --rm --network=host -e BIOCLIN_API_URL="http://localhost:8000" bioclin-mcp:latest

# Run (Mac/Windows)
docker run -it --rm -e BIOCLIN_API_URL="http://host.docker.internal:8000" bioclin-mcp:latest

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```
