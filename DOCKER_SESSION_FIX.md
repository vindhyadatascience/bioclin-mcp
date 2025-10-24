# Docker Session File Regression Fix

## Issue Summary

Two related Docker issues were identified and fixed:

### Issue 1: EOFError with stdin
**Problem**: Using `echo '2' | python` to pipe input caused `EOFError` when the script tried to read subsequent inputs (email/password).

**Root Cause**: When using pipe redirection, stdin is consumed by the first `input()` call, leaving nothing for subsequent prompts.

### Issue 2: Session file created as directory
**Problem**: Docker creates `~/.bioclin_session.json` as a **directory** instead of a file when the file doesn't exist during volume mounting.

**Root Cause**: Docker's default behavior is to create a directory when mounting a non-existent path with `-v`.

**Impact**:
- Session appears to save but doesn't persist
- MCP server can't read session data
- Authentication fails silently

## Solutions Implemented

### 1. Environment Variable Support

**File**: `src/bioclin_auth.py`

Added support for credentials via environment variables:
- `BIOCLIN_EMAIL`: Email address
- `BIOCLIN_PASSWORD`: Password

**Priority order**:
1. Function arguments (programmatic use)
2. Environment variables
3. Interactive prompts

**Changes**:
```python
# src/bioclin_auth.py:247-256
if email is None:
    email = os.environ.get("BIOCLIN_EMAIL")
if password is None:
    password = os.environ.get("BIOCLIN_PASSWORD")

if email is None:
    email = input("Email: ")
if password is None:
    password = getpass.getpass("Password: ")
```

### 2. Command-Line Flags

**File**: `src/bioclin_auth.py`

Added direct method selection flags:
- `login --cli`: Skip interactive menu, go directly to CLI login
- `login --browser`: Skip interactive menu, go directly to browser login

**Usage**:
```bash
# Direct CLI login (uses env vars if available, otherwise prompts)
python bioclin_auth.py login --cli

# Direct browser login
python bioclin_auth.py login --browser
```

### 3. Session File Validation

**File**:
- `docker-login.sh` (root directory - consolidated helper)

Added pre-flight checks to ensure session file exists as a **file** (not directory):

```bash
# Remove directory if it exists
if [ -d ~/.bioclin_session.json ]; then
    echo "⚠️  Removing incorrect directory at ~/.bioclin_session.json"
    rm -rf ~/.bioclin_session.json
fi

# Create empty file if it doesn't exist
if [ ! -f ~/.bioclin_session.json ]; then
    touch ~/.bioclin_session.json
fi
```

### 4. Enhanced Helper Script

**File**: `docker-login.sh`

Created user-friendly script with:
- Colored output for better UX
- Automatic session file validation
- Environment variable support
- Clear success/failure messages
- Next-steps guidance

## Testing Results

### Test 1: Environment Variables (Non-Interactive)
```bash
docker run --rm \
  -e BIOCLIN_EMAIL="test@example.com" \
  -e BIOCLIN_PASSWORD="test123" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

**Result**: ✅ No EOFError, credentials read from environment, API call made successfully

### Test 2: Session File Remains a File
```bash
touch ~/.bioclin_session.json
# Run Docker authentication
ls -la ~/.bioclin_session.json
```

**Result**: ✅ File remains a file, not converted to directory

### Test 3: Helper Script
```bash
./docker-login.sh
# Enter credentials
```

**Result**: ✅ Prompts for credentials, validates session file, runs Docker correctly

## Migration Guide

### Old Approach (Broken)
```bash
docker run -it --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  sh -c "echo '2' | python src/bioclin_auth.py login"
```

**Issues**:
- ❌ EOFError on email prompt
- ❌ Creates directory if file doesn't exist
- ❌ Confusing error messages

### New Approach (Fixed)

**Option A: Interactive Script**
```bash
./docker-login.sh
```

**Option B: Environment Variables**
```bash
docker run --rm \
  -e BIOCLIN_EMAIL="your@email.com" \
  -e BIOCLIN_PASSWORD="your-password" \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json \
  bioclin-mcp:latest \
  python src/bioclin_auth.py login --cli
```

**Option C: From Shell Variables**
```bash
export BIOCLIN_EMAIL="your@email.com"
export BIOCLIN_PASSWORD="your-password"
./docker-login.sh
```

## Troubleshooting

### If you already have a directory at `~/.bioclin_session.json`

```bash
# Check if it's a directory
ls -la ~/.bioclin_session.json

# If it shows 'd' at the start, it's a directory - remove it
rm -rf ~/.bioclin_session.json

# Now use the helper script
./docker-login.sh
```

### Verify session file is correct
```bash
# Should show a file (starting with '-'), not a directory ('d')
ls -la ~/.bioclin_session.json

# Should show JSON content (if authenticated)
cat ~/.bioclin_session.json
```

### Check authentication status
```bash
# Local Python
python src/bioclin_auth.py status

# Docker
docker run --rm \
  -v ~/.bioclin_session.json:/root/.bioclin_session.json:ro \
  bioclin-mcp:latest \
  python src/bioclin_auth.py status
```

## Files Modified

1. **src/bioclin_auth.py**
   - Lines 233-256: Added environment variable support to `login_cli()`
   - Lines 414-427: Added `--cli` and `--browser` flags

2. **docker-login.sh** (NEW)
   - Interactive helper script
   - Session file validation
   - Colored output

3. **docker-login.sh**
   - Consolidated authentication helper script
   - Session file validation
   - Environment variable support

5. **README.md**
   - Updated Quick Start section
   - Added troubleshooting for directory issue

6. **docs/DOCKER_AUTH.md** (NEW)
   - Comprehensive Docker authentication guide
   - Troubleshooting section

## Security Considerations

### Environment Variables
- ⚠️  Environment variables are visible in process lists
- ⚠️  May be logged in shell history
- ✅  Better than hardcoded credentials
- 💡  For production: Use Docker secrets or vault solutions

### Helper Script
- ✅  Credentials entered interactively (not in history)
- ✅  Password masked with `-sp` flag
- ✅  More secure than environment variables

### Session File
- ✅  Permissions should be `0o600` (read/write for owner only)
- ✅  Auto-expires after 7 days
- ✅  Contains only session tokens, not passwords

## Verification Checklist

- [x] EOFError fixed - environment variables work
- [x] Session file validation in all scripts
- [x] `--cli` and `--browser` flags working
- [x] Helper script handles edge cases
- [x] Documentation updated
- [x] Tested with Docker
- [x] Session persists correctly as a file

## Related Documentation

- [DOCKER_AUTH.md](docs/DOCKER_AUTH.md) - Complete Docker authentication guide
- [README.md](README.md) - Main project documentation
- [AUTHENTICATION.md](docs/AUTHENTICATION.md) - General authentication guide

## Version

Fixed in: **v1.1.1** (2025-10-23)

## Next Steps

Users should:
1. Remove any existing `~/.bioclin_session.json` directory: `rm -rf ~/.bioclin_session.json`
2. Use the new `./docker-login.sh` script
3. Or use environment variables with `--cli` flag
4. Verify session file is a file, not a directory

---

**Status**: ✅ Both issues resolved and tested
