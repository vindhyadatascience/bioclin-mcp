#!/usr/bin/env python3
"""
Automated Browser Authentication for Bioclin
Opens a browser, waits for user to log in, captures cookies automatically
"""
import json
import httpx
from pathlib import Path
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Session storage location
SESSION_FILE = Path.home() / ".bioclin_session.json"

# Bioclin URLs
BIOCLIN_BASE_URL = "https://bioclin.vindhyadatascience.com"
BIOCLIN_LOGIN_URL = f"{BIOCLIN_BASE_URL}/login"
BIOCLIN_API_URL = f"{BIOCLIN_BASE_URL}/api/v1"


def auto_browser_login():
    """
    Opens browser, waits for user to log in, captures cookies automatically
    """
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

            # Wait for navigation away from login page (indicates successful login)
            # We'll wait for the URL to change or for specific cookies to appear
            try:
                # Wait for URL to change from login page OR for access_token cookie (max 5 minutes)
                print("   🔍 Checking cookies every 2 seconds...")

                for i in range(150):  # 150 * 2 seconds = 5 minutes
                    current_url = page.url
                    cookies_str = page.evaluate("() => document.cookie")

                    # Check if we've navigated away from login or have auth cookies
                    if '/login' not in current_url or 'access_token' in cookies_str or 'session' in cookies_str:
                        print(f"\n✓ Login detected! (URL: {current_url})")
                        print(f"   Cookies: {cookies_str[:100]}...")
                        break

                    page.wait_for_timeout(2000)  # Wait 2 seconds
                else:
                    # Timeout
                    print("\n❌ Timeout: No login detected within 5 minutes")
                    print(f"   Final URL: {page.url}")
                    print(f"   Final cookies: {page.evaluate('() => document.cookie')}")
                    browser.close()
                    return False

            except PlaywrightTimeout:
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
            try:
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
                print(f"\n❌ Error verifying session: {e}")
                return False

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Note: This requires Playwright to be installed:")
        print("   pip install playwright")
        print("   playwright install chromium")
        return False


if __name__ == "__main__":
    auto_browser_login()
