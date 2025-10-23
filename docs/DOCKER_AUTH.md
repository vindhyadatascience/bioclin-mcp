# Docker Authentication Guide

## Problem

Docker containers cannot accept interactive stdin input when using pipe redirects like `echo '2' | python`. This causes `EOFError` when the script tries to read subsequent input.

## Solution

The authentication script now supports **environment variables** for non-interactive authentication in Docker containers.

## Usage Methods

### Method 1: Interactive Helper Script (Recommended)

```bash
./docker-login.sh
```

This script will:
1. Prompt for your email and password
2. Run the Docker container with credentials
3. Save the session to `~/.bioclin_session.json`

### Method 2: Environment Variables

```bash
docker run --rm \
  -e BIOCLIN_EMAIL="your@email.com" \
  -e BIOCLIN_PASSWORD="your-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

### Method 3: Export Environment Variables

```bash
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your-password"

docker run --rm \
  -e BIOCLIN_EMAIL \
  -e BIOCLIN_PASSWORD \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

## Command-Line Options

The `bioclin_auth.py` script now supports these flags:

```bash
# Interactive mode (choose browser or CLI)
python bioclin_auth.py login

# Direct CLI login (prompts for credentials if not in env)
python bioclin_auth.py login --cli

# Direct browser login (requires Playwright)
python bioclin_auth.py login --browser

# Check session status
python bioclin_auth.py status

# Logout (remove session)
python bioclin_auth.py logout
```

## Implementation Details

### Changes Made

1. **Environment Variable Support** (`src/bioclin_auth.py:247-256`)
   - `BIOCLIN_EMAIL`: Email address
   - `BIOCLIN_PASSWORD`: Password
   - Checked before prompting for interactive input

2. **Command-Line Flags** (`src/bioclin_auth.py:414-424`)
   - `--cli`: Skip method selection, go directly to CLI login
   - `--browser`: Skip method selection, go directly to browser login

3. **Helper Script** (`docker-login.sh`)
   - Interactive wrapper for Docker authentication
   - Handles credential prompts outside of Docker
   - Provides colored output and clear feedback

### Credential Priority

The script checks for credentials in this order:

1. **Function arguments** (for programmatic use)
2. **Environment variables** (`BIOCLIN_EMAIL`, `BIOCLIN_PASSWORD`)
3. **Interactive prompts** (if running in a TTY)

## Security Considerations

- Environment variables are visible in process lists
- For production use, consider using Docker secrets or vault solutions
- The interactive script is more secure as credentials are not stored in shell history
- Session tokens are still saved with `0o600` permissions

## Testing

Test the Docker authentication:

```bash
# Build the image
docker build -t bioclin-mcp:latest .

# Test with environment variables (will fail with invalid credentials)
docker run --rm \
  -e BIOCLIN_EMAIL="test@example.com" \
  -e BIOCLIN_PASSWORD="test-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli

# Expected output: Connection attempt, followed by 401 error for invalid credentials
# No EOFError!
```

## Docker Compose Integration

Update your `docker-compose.yml` to include environment variables:

```yaml
services:
  bioclin-mcp:
    build: .
    environment:
      - BIOCLIN_EMAIL=${BIOCLIN_EMAIL}
      - BIOCLIN_PASSWORD=${BIOCLIN_PASSWORD}
    volumes:
      - ~/.bioclin_session.json:/root/.bioclin_session.json:ro
```

Then use a `.env` file:

```bash
# .env
BIOCLIN_EMAIL=your@email.com
BIOCLIN_PASSWORD=your-password
```

**Important**: Add `.env` to `.gitignore` to avoid committing credentials!

## Troubleshooting

### EOFError: EOF when reading a line

**Old behavior**: Using `echo '2' | python` consumed stdin

**Fix**: Use `--cli` flag with environment variables:
```bash
docker run --rm \
  -e BIOCLIN_EMAIL="..." \
  -e BIOCLIN_PASSWORD="..." \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

### the input device is not a TTY

**Problem**: Using `-it` flag when stdin is not available

**Fix**: Remove `-it` flag when using environment variables:
```bash
# Bad
docker run -it --rm ...

# Good
docker run --rm ...
```

### Session file is a directory instead of a file

**Problem**: Docker creates `~/.bioclin_session.json` as a directory when mounting a non-existent file

**Symptoms**:
- `ls -la ~/.bioclin_session.json` shows it's a directory
- Authentication appears to succeed but session doesn't persist
- MCP server can't read session data

**Fix**:
```bash
# Remove the incorrect directory
rm -rf ~/.bioclin_session.json

# Create an empty file
touch ~/.bioclin_session.json

# Now run authentication again
./docker-login.sh
```

**Prevention**: The `docker-login.sh` script now automatically handles this by ensuring the file exists before running Docker.

### Credentials not being read from environment

**Check**:
1. Verify environment variables are set: `echo $BIOCLIN_EMAIL`
2. Ensure you're using `-e` flag: `docker run -e BIOCLIN_EMAIL ...`
3. Confirm you're using `--cli` flag: `python ... login --cli`

## Migration from Old Approach

**Before**:
```bash
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  sh -c "echo '2' | python src/bioclin_auth.py login"
```

**After**:
```bash
./docker-login.sh
```

Or:
```bash
docker run --rm \
  -e BIOCLIN_EMAIL="your@email.com" \
  -e BIOCLIN_PASSWORD="your-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

## See Also

- [Main README](../README.md)
- [Authentication Guide](AUTHENTICATION.md)
- [Docker Guide](DOCKER.md)
