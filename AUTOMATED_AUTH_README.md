# Automated Browser Authentication for Bioclin MCP

## Overview

The Bioclin MCP server now supports **fully automated browser-based authentication** using Playwright. No more manual cookie copying!

## How It Works

1. Run `python bioclin_auth.py login`
2. Choose option 1 (Browser - recommended)
3. A browser window opens to the Bioclin login page
4. You log in with your credentials
5. **Claude Code automatically detects the login and captures your session cookies**
6. The browser closes and your session is saved to `~/.bioclin_session.json`

That's it! No manual cookie copying, no DevTools, just log in normally.

## Installation

### First Time Setup

```bash
# Install Playwright
pip install playwright

# Install Chromium browser
playwright install chromium
```

### Usage

```bash
# Login (automated browser method)
python bioclin_auth.py login

# Check status
python bioclin_auth.py status

# Logout
python bioclin_auth.py logout
```

## Authentication Methods

The script now supports two methods:

### 1. Browser (Recommended) - Automated
- Opens a real browser window
- You log in normally on the official Bioclin website
- Cookies are captured automatically after successful login
- Browser closes automatically
- Session saved to `~/.bioclin_session.json`

**Requirements**: Playwright installed

### 2. CLI (Fallback)
- Enter email and password in terminal
- Credentials sent directly to Bioclin API
- No browser required

## Technical Details

### Cookie Detection

The automated browser script:
- Opens Chromium in non-headless mode (visible browser)
- Navigates to `https://bioclin.vindhyadatascience.com/login`
- Polls every 2 seconds for:
  - URL change from `/login` to `/home`
  - Presence of `access_token` cookie
- Captures all cookies from the browser context
- Filters for authentication cookies: `access_token`, `csrf_token`, `refresh_token`
- Verifies the session by calling `/api/v1/identity/user_me`
- Saves the session data with 7-day expiration

### Session File Format

```json
{
  "cookies": {
    "access_token": "eyJhbG...",
    "csrf_token": "DbutW3cf...",
    "refresh_token": "eyJhbG..."
  },
  "csrf_token": "DbutW3cf...",
  "user": {
    "email": "user@example.com",
    "username": "username",
    "id": "user-id-uuid"
  },
  "created_at": "2025-10-23T13:14:33.386985",
  "expires_at": "2025-10-30T13:14:33.386993"
}
```

### Security

- Session file has `0o600` permissions (read/write for owner only)
- Stored in user's home directory (`~/.bioclin_session.json`)
- Sessions expire after 7 days
- Tokens are never logged or displayed

## Troubleshooting

### "Playwright not available"

```bash
pip install playwright
playwright install chromium
```

### "Timeout: No login detected"

- Make sure you complete the login within 5 minutes
- Check that you're redirected to `/home` after login
- Verify cookies are being set by checking browser DevTools

### Browser won't open / Firewall issues

- Allow Chromium through your firewall when prompted
- On macOS: System Settings → Privacy & Security → Firewall → Allow Chromium

### Session expired

```bash
python bioclin_auth.py login
```

Sessions expire after 7 days and need to be renewed.

## Files

- `bioclin_auth.py` - Main authentication script with automated browser support
- `auto_browser_auth.py` - Standalone automated authentication script
- `~/.bioclin_session.json` - Stored session credentials

## Examples

### Quick Login
```bash
$ python bioclin_auth.py login
Choose option 1 (Browser)
[Browser opens, you log in]
✅ Login successful!
   User: username (user@example.com)
   Session saved to: /Users/you/.bioclin_session.json
```

### Check Status
```bash
$ python bioclin_auth.py status
✅ Logged in
   User: username (user@example.com)
   Logged in: 2025-10-23T13:14:33.386985
   Expires: 2025-10-30T13:14:33.386993
```

## Benefits Over Manual Cookie Copy

✅ **No DevTools needed** - Just log in normally
✅ **Automatic detection** - Script knows when you're logged in
✅ **More reliable** - Captures all required cookies
✅ **Better UX** - No copying/pasting
✅ **Faster** - Complete login in seconds

## Implementation

The automated authentication is implemented using:
- **Playwright** for browser automation
- **Chromium** browser for compatibility
- **JavaScript evaluation** for cookie detection
- **httpx** for API verification
