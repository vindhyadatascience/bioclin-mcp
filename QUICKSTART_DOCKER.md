# Docker Quick Start

## 1. Build
```bash
docker build -t bioclin-mcp:latest .
```

## 2. Authenticate

### Option A: Interactive (Recommended)
```bash
./docker-login.sh
# Enter email and password when prompted
```

### Option B: Environment Variables
```bash
docker run --rm \
  -e BIOCLIN_EMAIL="your@email.com" \
  -e BIOCLIN_PASSWORD="your-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

### Option C: Export Variables First
```bash
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your-password"
./docker-login.sh
```

## 3. Run Server

### Docker Compose
```bash
docker-compose up
```

### Direct Docker
```bash
docker run -i --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json:ro \
  bioclin-mcp:latest
```

## 4. Add to Claude Desktop

**macOS**: Edit `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows**: Edit `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "${HOME}/.bioclin_session.json:/root/.bioclin_session.json:ro",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

## 5. Restart Claude Desktop

## Common Issues

### "Session file is a directory"
```bash
rm -rf ~/.bioclin_session.json
./docker-login.sh
```

### "EOFError: EOF when reading a line"
Use `./docker-login.sh` or environment variables with `--cli` flag

### Check session status
```bash
docker run --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json:ro \
  bioclin-mcp:latest \
  python src/bioclin_auth.py status
```

## Security Notes

- ✅ `./docker-login.sh` is most secure (no history)
- ⚠️  Environment variables may appear in process lists
- 🔒 Session tokens auto-expire after 7 days

## Need Help?

- Full guide: [README.md](README.md)
- Docker details: [docs/DOCKER_AUTH.md](docs/DOCKER_AUTH.md)
- Session fix: [DOCKER_SESSION_FIX.md](DOCKER_SESSION_FIX.md)
