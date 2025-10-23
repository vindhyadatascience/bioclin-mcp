# Final Automated Browser Login Solution

## The Problem
Users don't want to manually supply their username and password to the LLM when using Claude Desktop.

## The Solution
**Automated Browser Login with Visible GUI** - The MCP tool now opens a **new Terminal window** on macOS that runs the browser login script, ensuring the browser window is visible to the user.

## How It Works

### From Claude Desktop:

1. **User**: "I need to access my Bioclin data"

2. **Claude** (in Desktop):
   - Checks session: `bioclin_check_session()`
   - If not authenticated, calls: `bioclin_browser_login_auto()`

3. **What Happens**:
   - ✅ A **new Terminal window opens** (visible to user)
   - ✅ Terminal runs: `python bioclin_auth.py login` (option 1)
   - ✅ **Browser window opens** to Bioclin login page
   - ✅ User **enters credentials in browser** (not to LLM!)
   - ✅ Script **auto-detects login** (monitors URL change to /home)
   - ✅ **Cookies captured automatically**
   - ✅ Session **verified with API**
   - ✅ **Saved to ~/.bioclin_session.json**
   - ✅ **Browser closes automatically**
   - ✅ Terminal shows success message

4. **Result**: Claude can now use all 46+ Bioclin tools without asking for credentials!

## Key Improvement (macOS)

### Before (Didn't Work):
```python
# Subprocess ran in background - GUI not visible
process = await asyncio.create_subprocess_shell(
    f'echo "1" | python "{script}" login',
    stdout=PIPE, stderr=PIPE
)
```
❌ Browser opened but wasn't visible to user

### After (Works!):
```python
# Uses osascript to open new Terminal window
terminal_cmd = '''
    tell application "Terminal"
        activate
        do script "python bioclin_auth.py login"
    end tell
'''
process = await asyncio.create_subprocess_exec("osascript", "-e", terminal_cmd)
```
✅ New Terminal window opens that user can see
✅ Browser launches from that Terminal and is visible
✅ User can interact with both Terminal and browser

## User Experience

### Scenario 1: First Time Using Bioclin

```
You: Show me my Bioclin projects

Claude: I see you're not logged in to Bioclin. Let me start the
        automated login process for you.

        [Claude calls bioclin_browser_login_auto()]

        A new Terminal window should open shortly with the login script,
        and then a browser window will open to the Bioclin login page.
        Please log in with your credentials.

[New Terminal window opens]
[Browser opens to https://bioclin.vindhyadatascience.com/login]
[You enter username/password in browser]
[Browser automatically closes after successful login]
[Terminal shows: "✅ Login successful! Session saved."]

Claude: Perfect! Your session is now active. Let me fetch your projects...

        [Shows list of projects]
```

### Scenario 2: Session Already Active

```
You: Show me my Bioclin projects

Claude: [Calls bioclin_check_session()]

        [Calls bioclin_list_projects()]

        Here are your Bioclin projects: ...
```

## Security Benefits

✅ **No credentials exposed to LLM** - You enter them directly in browser
✅ **Official Bioclin website** - Login happens on real bioclin.vindhyadatascience.com
✅ **Session file secured** - 0o600 permissions (owner-only)
✅ **7-day expiration** - Sessions auto-expire for security
✅ **No password storage** - Only session tokens stored
✅ **HTTPS only** - All communication encrypted

## Technical Details

### MCP Tool Implementation

**File**: `bioclin_fastmcp.py`

```python
@mcp.tool()
async def bioclin_browser_login_auto() -> dict:
    """
    Start automated browser-based login with Playwright

    On macOS: Opens new Terminal window to run the auth script
    On Linux/Windows: Runs in background with detached process
    """
    if platform.system() == "Darwin":  # macOS
        # Use osascript to open Terminal.app
        terminal_cmd = f'''
            tell application "Terminal"
                activate
                do script "cd '{script_dir}' && echo '1' | python 'bioclin_auth.py' login"
            end tell
        '''
        await asyncio.create_subprocess_exec("osascript", "-e", terminal_cmd)
    else:
        # Other platforms: detached subprocess
        await asyncio.create_subprocess_shell(
            f'echo "1" | python "{script}" login',
            start_new_session=True
        )
```

### Authentication Script

**File**: `bioclin_auth.py`

```python
def login_browser_auto():
    """Automated browser login with Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Visible browser
        page = browser.new_page()
        page.goto("https://bioclin.vindhyadatascience.com/login")

        # Wait for login (checks URL or cookie)
        while not logged_in:
            check_for_login()
            sleep(2)

        # Capture cookies
        cookies = browser.context.cookies()

        # Verify session
        verify_with_api(cookies)

        # Save to file
        save_session(cookies)

        browser.close()
```

## Platform Support

### macOS ✅ (Fully Tested)
- Opens new Terminal window via osascript
- Browser visible and interactive
- Clean UX with Terminal showing progress

### Linux 🟡 (Should Work)
- Uses `start_new_session=True` to detach process
- Browser should be visible
- May need testing on different DEs (GNOME, KDE, etc.)

### Windows 🟡 (Should Work)
- Uses `start_new_session=True` to detach process
- Browser should be visible
- May need testing with different terminals (CMD, PowerShell, Windows Terminal)

## Requirements

```bash
# Required packages
pip install playwright httpx fastmcp

# Install Chromium browser
playwright install chromium

# Required files
- bioclin_auth.py (authentication script with Playwright)
- bioclin_fastmcp.py (MCP server with browser_login_auto tool)
```

## Testing

### Test the MCP Tool

```python
# In Python REPL or script
import asyncio
from bioclin_fastmcp import mcp, bioclin_browser_login_auto

# Test the login tool
result = await bioclin_browser_login_auto()
print(result)

# Wait for user to complete login in browser
await asyncio.sleep(30)

# Verify session
from bioclin_fastmcp import bioclin_check_session, Context
ctx = Context()
session = await bioclin_check_session(ctx)
print(session)
```

### Test from Claude Desktop

1. Add Bioclin MCP to Claude Desktop config
2. Start Claude Desktop
3. Ask: "Check my Bioclin session"
4. If not logged in, ask: "Log me in to Bioclin"
5. Terminal window should open
6. Browser should open
7. Complete login
8. Ask: "List my Bioclin projects"

## Troubleshooting

### Browser doesn't open
- **Check**: Is Playwright installed? `pip show playwright`
- **Check**: Is Chromium installed? `playwright install chromium`
- **Fallback**: Run manually in terminal: `python bioclin_auth.py login`

### Terminal window doesn't open (macOS)
- **Check**: Permissions for Terminal.app
- **Check**: `osascript` command works: `osascript -e 'tell app "Terminal" to activate'`
- **Fallback**: Run manually in terminal

### Session not saved
- **Check**: `~/.bioclin_session.json` file exists and has correct permissions
- **Check**: File contents: `cat ~/.bioclin_session.json`
- **Verify**: `python bioclin_auth.py status`

## Success Criteria

✅ No username/password entered into Claude Desktop
✅ No manual terminal commands needed (after MCP tool call)
✅ Browser login visible and interactive
✅ Session automatically captured and saved
✅ All Bioclin MCP tools work after authentication
✅ Session persists for 7 days (no repeated logins)

## Summary

The automated browser login is now **fully integrated** into the Bioclin MCP server and provides a **secure, user-friendly authentication experience** for Claude Desktop users.

**No more manual credentials! Just browser-based login with automatic session capture.** 🎉
