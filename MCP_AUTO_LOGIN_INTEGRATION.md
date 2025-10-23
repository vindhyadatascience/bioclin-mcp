# Automated Browser Login - MCP Integration

## New MCP Tool: `bioclin_browser_login_auto`

The Bioclin MCP server now includes a new tool that enables **fully automated browser-based authentication** directly from Claude Desktop!

## How It Works

When Claude calls the `bioclin_browser_login_auto` tool:

1. **Checks for Playwright** - Verifies that Playwright is installed
2. **Launches auth script** - Runs `python bioclin_auth.py login` with browser option
3. **Opens browser** - A browser window opens to Bioclin login page
4. **User logs in** - You enter your credentials normally
5. **Auto-capture** - Script detects login and captures cookies automatically
6. **Saves session** - Session stored to `~/.bioclin_session.json`
7. **Closes browser** - Browser closes automatically
8. **Ready to use** - All Bioclin MCP tools now work without re-authentication

## Usage from Claude Desktop

### Simple Flow

**You**: "I need to use Bioclin"

**Claude**: *Checks session with `bioclin_check_session`*
- If not authenticated, Claude will call `bioclin_browser_login_auto`
- Browser opens, you log in
- Session captured automatically
- Claude can now use all Bioclin tools

### Example Conversation

```
You: List my Bioclin projects

Claude: Let me check if you're authenticated first...
        [Calls bioclin_check_session]
        I see you're not logged in. Let me start the automated login process.
        [Calls bioclin_browser_login_auto]

        A browser window should open shortly. Please log in with your credentials.

You: [Logs in via browser]

Claude: Great! Your session is now active. Let me fetch your projects...
        [Calls bioclin_list_projects]

        Here are your Bioclin projects: ...
```

## Tool Details

### `bioclin_browser_login_auto()`

**Description**: Start automated browser-based login with Playwright

**Returns**:
```json
{
  "status": "login_started",
  "message": "🌐 Automated browser login initiated!",
  "instructions": [
    "✓ A browser window should open shortly",
    "✓ Please log in with your credentials",
    "✓ Session will be captured automatically",
    "✓ Browser will close automatically"
  ],
  "process_id": 12345,
  "note": "Complete the login in the browser window"
}
```

**Error Cases**:
- Playwright not installed → Returns installation instructions
- Auth script not found → Returns error with path
- Process failed → Returns fallback instructions

## Authentication Tools Overview

The MCP server now has 3 login methods:

### 1. `bioclin_browser_login_auto()` ⭐ RECOMMENDED
- **Fully automated** browser login
- No manual cookie copying
- Playwright-based
- Most secure and user-friendly

### 2. `bioclin_open_login(method="browser")`
- Opens browser to login page
- Requires manual terminal commands after
- Legacy method

### 3. `bioclin_login(username, password)`
- Direct credential passing
- NOT RECOMMENDED (exposes password to LLM)
- Fallback only

## Requirements

### For Automated Login

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium
```

### Files Required

- `bioclin_auth.py` - Authentication script with Playwright support
- `bioclin_fastmcp.py` - MCP server with `bioclin_browser_login_auto` tool

## Security

- **No credentials exposed to LLM** - You enter them directly in browser
- **Session file secured** - `0o600` permissions (owner-only read/write)
- **7-day expiration** - Sessions automatically expire
- **Official Bioclin website** - Login happens on actual Bioclin domain

## Code Implementation

### MCP Tool (bioclin_fastmcp.py:154-237)

```python
@mcp.tool()
async def bioclin_browser_login_auto() -> dict:
    """
    Start automated browser-based login with Playwright

    Launches browser, waits for login, captures cookies automatically
    """
    # Check Playwright availability
    # Launch auth script with subprocess
    # Return status and instructions
```

### Auth Script (bioclin_auth.py:89-217)

```python
def login_browser_auto():
    """
    Automated browser-based login using Playwright

    Opens browser, detects login, captures cookies, verifies session
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        # ... wait for login detection
        # ... capture cookies
        # ... verify with API
        # ... save session
```

## Benefits

✅ **Seamless UX** - Claude can trigger login when needed
✅ **No manual steps** - Everything automated except entering credentials
✅ **Secure** - Credentials never exposed to LLM
✅ **Fast** - Complete login in 10-30 seconds
✅ **Reliable** - Automatic cookie capture, no manual copying
✅ **Claude Desktop ready** - Works directly from Claude interface

## Testing

Test the integration:

```python
# 1. Check session
await bioclin_check_session()

# 2. Trigger auto login
await bioclin_browser_login_auto()

# 3. Log in via browser (user action)

# 4. Verify session
await bioclin_check_session()
# Should show authenticated

# 5. Use any Bioclin tool
await bioclin_list_projects()
```

## Future Enhancements

Potential improvements:
- [ ] Add session refresh when tokens expire
- [ ] Support for multiple Bioclin environments
- [ ] Remember last login method preference
- [ ] Auto-refresh tokens before expiration
- [ ] Browser profile persistence for faster logins

## Summary

The automated browser login integration makes Bioclin authentication **seamless from Claude Desktop**. Users can now:

1. Ask Claude to use Bioclin
2. Claude detects no session
3. Claude triggers automated login
4. User logs in via browser (one time)
5. Claude can now access all Bioclin features

No manual terminal commands, no cookie copying, no friction! 🎉
