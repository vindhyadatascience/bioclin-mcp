#!/usr/bin/env python3
"""
Bioclin Authentication Helper
Securely stores session credentials for use with the Bioclin MCP server

Supports two login methods:
1. Browser-based: Opens Bioclin login page in browser (recommended)
2. CLI-based: Enter credentials in terminal (fallback)
"""

import os
import json
import httpx
import getpass
import webbrowser
import time
from pathlib import Path
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Try to import Playwright for automated browser auth
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Session storage location
SESSION_FILE = Path.home() / ".bioclin_session.json"

# Bioclin URLs
BIOCLIN_BASE_URL = "https://bioclin.vindhyadatascience.com"
BIOCLIN_LOGIN_URL = f"{BIOCLIN_BASE_URL}/login"
BIOCLIN_API_URL = f"{BIOCLIN_BASE_URL}/api/v1"

# Local callback server for browser-based auth
CALLBACK_PORT = 9876
CALLBACK_URL = f"http://localhost:{CALLBACK_PORT}/callback"


class CallbackHandler(BaseHTTPRequestHandler):
    """HTTP handler for browser callback"""

    received_cookies = None

    def do_GET(self):
        """Handle callback from browser after login"""
        if self.path.startswith('/callback'):
            # Extract cookies from request
            cookie_header = self.headers.get('Cookie', '')

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Bioclin Login Success</title>
                <style>
                    body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                    .success { color: #28a745; font-size: 24px; }
                    .message { margin-top: 20px; color: #666; }
                </style>
            </head>
            <body>
                <div class="success">✅ Login Successful!</div>
                <div class="message">You can close this window and return to the terminal.</div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())

            # Store cookies for parent thread
            CallbackHandler.received_cookies = cookie_header
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Suppress logging"""
        pass


def login_browser_auto():
    """
    Automated browser-based login using Playwright

    Opens a browser window, waits for user to log in, then automatically
    captures the session cookies.
    """
    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not installed. Installing...")
        print("   Run: pip install playwright && playwright install chromium")
        return False

    print("🌐 Bioclin Automated Browser Login")
    print("=" * 60)
    print("\n📋 How this works:")
    print("1. A browser window will open to the Bioclin login page")
    print("2. Log in with your credentials")
    print("3. After successful login, cookies will be captured automatically")
    print("4. The browser will close and your session will be saved")
    print("\n⏳ Starting browser...")

    try:
        with sync_playwright() as p:
            # Launch browser (headless=False so you can see it)
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # Navigate to login page
            print(f"\n🔓 Opening: {BIOCLIN_LOGIN_URL}")
            page.goto(BIOCLIN_LOGIN_URL)

            print("\n👤 Please log in to Bioclin in the browser window...")
            print("   (Waiting for you to complete login...)")
            print("   🔍 Checking for login every 2 seconds...")

            # Wait for navigation away from login page
            for i in range(150):  # 150 * 2 seconds = 5 minutes
                current_url = page.url
                cookies_str = page.evaluate("() => document.cookie")

                # Check if we've navigated away from login or have auth cookies
                if '/login' not in current_url or 'access_token' in cookies_str:
                    print(f"\n✓ Login detected! (URL: {current_url})")
                    break

                page.wait_for_timeout(2000)  # Wait 2 seconds
            else:
                # Timeout
                print("\n❌ Timeout: No login detected within 5 minutes")
                browser.close()
                return False

            # Give it a moment for all cookies to be set
            page.wait_for_timeout(2000)

            # Extract cookies
            cookies = context.cookies()
            print(f"\n✓ Captured {len(cookies)} cookies from browser")

            # Convert to dict
            cookies_dict = {}
            csrf_token = None

            for cookie in cookies:
                name = cookie['name']
                value = cookie['value']
                cookies_dict[name] = value
                if name == 'csrf_token':
                    csrf_token = value

            # Filter to only the ones we need
            required_cookies = ['access_token', 'csrf_token', 'refresh_token']
            filtered_cookies = {k: v for k, v in cookies_dict.items() if k in required_cookies}

            print(f"✓ Found authentication cookies: {list(filtered_cookies.keys())}")

            # Close browser
            browser.close()
            print("\n✓ Browser closed")

            if not filtered_cookies:
                print("❌ No authentication cookies found. Please try again.")
                return False

            # Verify session
            print("\n🔍 Verifying session with Bioclin API...")
            client = httpx.Client(timeout=30.0, follow_redirects=True)
            user_response = client.get(
                f"{BIOCLIN_API_URL}/identity/user_me",
                cookies=filtered_cookies,
                headers={"X-CSRF-Token": csrf_token} if csrf_token else {}
            )
            user_response.raise_for_status()
            user_info = user_response.json()

            print(f"✓ Session verified!")

            # Save session
            session_data = {
                "cookies": filtered_cookies,
                "csrf_token": csrf_token,
                "user": {
                    "email": user_info.get("email"),
                    "username": user_info.get("username"),
                    "id": user_info.get("id"),
                },
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }

            SESSION_FILE.write_text(json.dumps(session_data, indent=2))
            SESSION_FILE.chmod(0o600)

            print("\n✅ Login successful!")
            print(f"   User: {user_info.get('username')} ({user_info.get('email')})")
            print(f"   Session saved to: {SESSION_FILE}")
            print(f"   Session expires: ~7 days from now")
            print("\n💡 Your Claude Desktop can now use Bioclin without passwords!")

            client.close()
            return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure Playwright is properly installed:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return False


def login_browser():
    """
    Browser-based login: Try automated first, fall back to manual
    """
    if PLAYWRIGHT_AVAILABLE:
        return login_browser_auto()
    else:
        print("⚠️  Playwright not available for automated login")
        print("   Install with: pip install playwright && playwright install chromium")
        print("\n💡 Falling back to CLI login...")
        return login_cli()


def login_cli():
    """
    CLI-based login: Enter credentials in terminal

    This is a fallback method if browser-based login doesn't work.
    """
    print("🔐 Bioclin CLI Login")
    print("=" * 50)

    # Get credentials securely (password won't be echoed)
    email = input("Email: ")
    password = getpass.getpass("Password: ")

    # Login to Bioclin
    print("\nLogging in to Bioclin...")

    try:
        client = httpx.Client(timeout=30.0, follow_redirects=True)
        response = client.post(
            f"{BIOCLIN_API_URL}/identity/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()

        # Extract session cookies
        cookies = dict(response.cookies)
        csrf_token = response.cookies.get("csrf_token")

        # Get user info to verify login
        user_response = client.get(
            f"{BIOCLIN_API_URL}/user/me",
            cookies=cookies,
            headers={"X-CSRF-Token": csrf_token} if csrf_token else {}
        )
        user_info = user_response.json()

        # Save session
        session_data = {
            "cookies": cookies,
            "csrf_token": csrf_token,
            "user": {
                "email": user_info.get("email"),
                "username": user_info.get("username"),
                "id": user_info.get("id"),
            },
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
        }

        # Save to file with restricted permissions
        SESSION_FILE.write_text(json.dumps(session_data, indent=2))
        SESSION_FILE.chmod(0o600)  # Read/write for owner only

        print("\n✅ Login successful!")
        print(f"   User: {user_info.get('username')} ({user_info.get('email')})")
        print(f"   Session saved to: {SESSION_FILE}")
        print(f"   Session expires: ~7 days from now")
        print("\n💡 Your Claude Desktop can now use Bioclin without passwords!")

        client.close()
        return True

    except httpx.HTTPStatusError as e:
        print(f"\n❌ Login failed: {e.response.status_code}")
        print(f"   {e.response.text}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def login_interactive():
    """
    Interactive login with method selection
    """
    print("\n🔐 Bioclin Authentication")
    print("=" * 50)
    print("\nChoose login method:")

    if PLAYWRIGHT_AVAILABLE:
        print("  1. Browser (recommended) - Automated login with browser window")
        print("  2. CLI - Enter credentials securely in terminal")
        default_choice = "1"
    else:
        print("  1. Browser - Requires Playwright (not installed)")
        print("  2. CLI (recommended) - Enter credentials securely in terminal")
        default_choice = "2"

    choice = input(f"\nEnter choice [{default_choice}]: ").strip() or default_choice

    if choice == "1":
        return login_browser()
    elif choice == "2":
        return login_cli()
    else:
        print("❌ Invalid choice")
        return False


def get_session():
    """
    Get stored session credentials

    Returns:
        dict: Session data or None if not logged in
    """
    if not SESSION_FILE.exists():
        return None

    try:
        session_data = json.loads(SESSION_FILE.read_text())

        # Check if expired
        expires_at = datetime.fromisoformat(session_data["expires_at"])
        if datetime.now() > expires_at:
            print("⚠️  Session expired. Please run: python bioclin_auth.py login")
            return None

        return session_data
    except Exception as e:
        print(f"⚠️  Error reading session: {e}")
        return None


def logout():
    """
    Remove stored session credentials
    """
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        print("✅ Logged out. Session credentials removed.")
    else:
        print("ℹ️  No active session found.")


def status():
    """
    Show current session status
    """
    session = get_session()
    if session:
        print("✅ Logged in")
        print(f"   User: {session['user']['username']} ({session['user']['email']})")
        print(f"   Logged in: {session['created_at']}")
        print(f"   Expires: {session['expires_at']}")
    else:
        print("❌ Not logged in")
        print("   Run: python bioclin_auth.py login")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Bioclin Authentication Helper")
        print("\nUsage:")
        print("  python bioclin_auth.py login    - Securely login and store session")
        print("  python bioclin_auth.py status   - Check login status")
        print("  python bioclin_auth.py logout   - Remove stored session")
        sys.exit(1)

    command = sys.argv[1]

    if command == "login":
        login_interactive()
    elif command == "status":
        status()
    elif command == "logout":
        logout()
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
