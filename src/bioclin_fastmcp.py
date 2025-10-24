#!/usr/bin/env python3
"""
Bioclin FastMCP Server
A simplified Model Context Protocol server for the Bioclin API using FastMCP

This server provides 46 tools to interact with the Bioclin API including:
- User authentication and management (6 tools)
- Organization management
- Project management
- Run management
- Parameter and analysis type management
- Google Cloud Storage operations
"""

import os
import json
import subprocess
import webbrowser
import httpx
from pathlib import Path
from typing import Optional, Dict, Any
from fastmcp import FastMCP, Context
from pydantic import EmailStr

# Default base URL - can be overridden via environment variable
BIOCLIN_API_URL = os.getenv(
    "BIOCLIN_API_URL",
    "https://bioclin.vindhyadatascience.com/api/v1"
)

# Session storage location
SESSION_FILE = Path.home() / ".bioclin_session.json"

# Bioclin URLs
BIOCLIN_LOGIN_URL = "https://bioclin.vindhyadatascience.com/login"
BIOCLIN_AUTH_SCRIPT = Path(__file__).parent / "bioclin_auth.py"

# Create FastMCP server
mcp = FastMCP("Bioclin 🧬")


def load_stored_session() -> Optional[Dict[str, Any]]:
    """
    Load stored session credentials from disk

    Returns:
        dict: Session data or None if not available
    """
    if not SESSION_FILE.exists():
        return None

    try:
        session_data = json.loads(SESSION_FILE.read_text())
        return session_data
    except Exception:
        return None


# Helper function for authenticated requests
async def bioclin_request(
    ctx: Context,
    method: str,
    endpoint: str,
    **kwargs
) -> dict:
    """
    Make an authenticated request to the Bioclin API

    Args:
        ctx: FastMCP context
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint (e.g., "/user/me")
        **kwargs: Additional arguments to pass to httpx (json, data, params, etc.)

    Returns:
        dict: JSON response from API
    """
    # Load session from disk (primary source)
    stored_session = load_stored_session()

    if stored_session:
        cookies = stored_session.get("cookies", {})
        csrf_token = stored_session.get("csrf_token")
    else:
        # No stored session available
        cookies = {}
        csrf_token = None

    # Build headers
    headers = kwargs.pop("headers", {})
    if csrf_token:
        headers["X-CSRF-Token"] = csrf_token

    # Make request
    url = f"{BIOCLIN_API_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.request(
            method,
            url,
            cookies=cookies,
            headers=headers,
            **kwargs
        )

        # Handle response
        response.raise_for_status()

        # Handle empty responses
        if response.status_code == 204:
            return {"status": "success", "message": "No content"}

        # Try to parse JSON
        try:
            return response.json()
        except:
            return {"status": "success", "data": response.text}


# ============================================================================
# AUTHENTICATION TOOLS (6)
# ============================================================================

@mcp.tool()
async def bioclin_check_session(ctx: Context) -> dict:
    """
    Check if there is an active Bioclin session

    This checks for a stored session file created by the bioclin_auth.py script.
    If no session exists, you can use bioclin_browser_login_auto for automated login.

    Returns:
        dict: Session status and user information if logged in
    """
    # Check for stored session
    stored_session = load_stored_session()

    if stored_session:
        return {
            "status": "authenticated",
            "user": stored_session.get("user"),
            "created_at": stored_session.get("created_at"),
            "expires_at": stored_session.get("expires_at"),
            "message": "Session active. You can use Bioclin tools without providing credentials."
        }
    else:
        return {
            "status": "not_authenticated",
            "message": "No active session found.",
            "instructions": "Use 'bioclin_browser_login_auto' for automated browser-based login (RECOMMENDED!)"
        }


@mcp.tool()
async def bioclin_browser_login_auto() -> dict:
    """
    Start automated browser-based login with Playwright

    This tool launches the automated browser login workflow that:
    1. Opens a browser window to the Bioclin login page
    2. Waits for you to complete login
    3. Automatically captures session cookies when login is detected
    4. Verifies the session with the API
    5. Saves credentials to ~/.bioclin_session.json
    6. Closes the browser

    This is the RECOMMENDED login method - no manual cookie copying required!

    Requirements:
    - Playwright must be installed (pip install playwright && playwright install chromium)
    - The bioclin_auth.py script must be in the same directory

    Returns:
        dict: Login process status and instructions
    """
    # Check if running in Docker
    if Path("/.dockerenv").exists() or os.environ.get("DOCKER_CONTAINER"):
        return {
            "status": "docker_detected",
            "message": "Browser login cannot run inside Docker container",
            "instructions": [
                "You are running the MCP server in Docker. To authenticate:",
                "",
                "Option 1 - Interactive Helper (Recommended):",
                "  ./docker-login.sh",
                "",
                "Option 2 - Environment Variables:",
                "  docker run --rm \\",
                "    -e BIOCLIN_EMAIL='your@email.com' \\",
                "    -e BIOCLIN_PASSWORD='your-password' \\",
                "    -v ~/.bioclin_session.json:/root/.bioclin_session.json \\",
                "    bioclin-mcp:latest \\",
                "    python src/bioclin_auth.py login --cli",
                "",
                "Option 3 - Browser Login (requires uv/Python on host):",
                "  uv run python src/bioclin_auth.py login",
                "  # OR: python src/bioclin_auth.py login",
                "",
                "After authentication, restart Claude Desktop to use the new session."
            ],
            "docker_login_script": "./docker-login.sh"
        }

    if not BIOCLIN_AUTH_SCRIPT.exists():
        return {
            "status": "error",
            "message": f"Authentication script not found at: {BIOCLIN_AUTH_SCRIPT}",
            "instructions": "Please ensure bioclin_auth.py is in the correct location"
        }

    try:
        # Check if Playwright is available
        try:
            import playwright
            playwright_available = True
        except ImportError:
            playwright_available = False

        if not playwright_available:
            return {
                "status": "playwright_not_installed",
                "message": "Playwright is required for automated browser login",
                "instructions": [
                    "Install Playwright with these commands:",
                    "  pip install playwright",
                    "  playwright install chromium",
                    "",
                    "After installation, try this tool again."
                ],
                "fallback": "You can use 'bioclin_open_login' for manual login instead"
            }

        # Launch the automated browser login
        # On macOS, use osascript to open Terminal.app with the command
        # This ensures the browser window will be visible to the user
        import asyncio
        import platform

        if platform.system() == "Darwin":  # macOS
            # Use osascript to open a new Terminal window and run the command
            terminal_cmd = f'''
                tell application "Terminal"
                    activate
                    do script "cd '{BIOCLIN_AUTH_SCRIPT.parent}' && echo '1' | python '{BIOCLIN_AUTH_SCRIPT}' login && echo '\\n✅ Login complete! You can close this window.' && read -p 'Press Enter to close...'"
                end tell
            '''
            process = await asyncio.create_subprocess_exec(
                "osascript", "-e", terminal_cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

            return {
                "status": "login_started",
                "message": "🌐 Automated browser login initiated!",
                "instructions": [
                    "✓ A new Terminal window has opened with the login script",
                    "✓ A browser window should open shortly to the Bioclin login page",
                    "✓ Please log in with your credentials in the browser",
                    "✓ The session will be captured automatically when you log in",
                    "✓ The browser will close automatically after successful login",
                    "",
                    "⏳ This process may take 10-30 seconds...",
                    "",
                    "After you've logged in, use 'bioclin_check_session' to verify."
                ],
                "note": "The login process is running in a new Terminal window. Complete the login in the browser."
            }
        else:
            # For non-macOS systems, use the standard approach
            process = await asyncio.create_subprocess_shell(
                f'echo "1" | python -u "{BIOCLIN_AUTH_SCRIPT}" login',
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
                start_new_session=True
            )

            return {
                "status": "login_started",
                "message": "🌐 Automated browser login initiated!",
                "instructions": [
                    "✓ A browser window should open shortly to the Bioclin login page",
                    "✓ Please log in with your credentials in the browser",
                    "✓ The session will be captured automatically when you log in",
                    "✓ The browser will close automatically after successful login",
                    "",
                    "⏳ This process may take 10-30 seconds...",
                    "",
                    "💡 If you don't see a browser window, try running this in your terminal:",
                    f"   python {BIOCLIN_AUTH_SCRIPT} login",
                    "",
                    "After you've logged in, use 'bioclin_check_session' to verify."
                ],
                "process_id": process.pid,
                "note": "The login process is running. Complete the login in the browser window that opens."
            }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to start automated login: {str(e)}",
            "fallback": "Try running manually in terminal: python src/bioclin_auth.py login"
        }


@mcp.tool()
async def bioclin_open_login(method: Optional[str] = "browser") -> dict:
    """
    Open the Bioclin login page for authentication (legacy method)

    RECOMMENDED: Use 'bioclin_browser_login_auto' instead for fully automated login!

    This tool will either:
    1. Open your browser to the Bioclin login page (browser method)
    2. Provide CLI login instructions (cli method)

    Args:
        method: Login method - "browser" (default) or "cli"

    Returns:
        dict: Instructions and status
    """
    if method == "browser":
        # Open browser to Bioclin login page
        try:
            webbrowser.open(BIOCLIN_LOGIN_URL)

            return {
                "status": "browser_opened",
                "message": "Browser opened to Bioclin login page",
                "instructions": [
                    "1. Login to Bioclin with your credentials in the browser that just opened",
                    "2. After successful login, run the following command in your terminal:",
                    "   python src/bioclin_auth.py login",
                    "   Then choose option 1 (Browser) and follow the prompts",
                    "3. Once complete, use 'bioclin_check_session' to verify your login",
                    "",
                    "💡 TIP: Use 'bioclin_browser_login_auto' for fully automated login instead!"
                ],
                "login_url": BIOCLIN_LOGIN_URL
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to open browser: {str(e)}",
                "fallback": "Please manually visit: " + BIOCLIN_LOGIN_URL
            }

    elif method == "cli":
        # Run the auth script
        if not BIOCLIN_AUTH_SCRIPT.exists():
            return {
                "status": "error",
                "message": f"Authentication script not found at: {BIOCLIN_AUTH_SCRIPT}",
                "instructions": "Please run manually: python src/bioclin_auth.py login"
            }

        return {
            "status": "script_available",
            "message": "CLI login method requires terminal access",
            "instructions": [
                "Please run the following command in your terminal:",
                f"python {BIOCLIN_AUTH_SCRIPT} login",
                "Then choose option 2 (CLI) and enter your credentials securely"
            ],
            "note": "The CLI method cannot be automated from Claude Desktop for security reasons"
        }

    else:
        return {
            "status": "error",
            "message": f"Invalid method: {method}",
            "valid_methods": ["browser", "cli"]
        }


@mcp.tool()
async def bioclin_login(
    username: str,
    password: str,
    ctx: Context
) -> dict:
    """
    Login to Bioclin and obtain session credentials

    SECURITY NOTE: This method requires providing your password directly.
    For better security, use: python src/bioclin_auth.py login
    This will securely store your session without exposing credentials to the LLM.

    Args:
        username: User email address
        password: User password

    Returns:
        dict: User information and authentication status
    """
    return await bioclin_request(
        ctx,
        "POST",
        "/identity/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )


@mcp.tool()
async def bioclin_logout(ctx: Context) -> dict:
    """
    Logout from Bioclin and clear session

    Returns:
        dict: Logout status
    """
    try:
        result = await bioclin_request(ctx, "POST", "/identity/logout")
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    # Delete stored session file
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()
        result["session_file_deleted"] = True
    else:
        result["session_file_deleted"] = False

    return result


@mcp.tool()
async def bioclin_validate_token(ctx: Context) -> dict:
    """
    Validate current session token

    Returns:
        dict: Token validation status
    """
    return await bioclin_request(ctx, "POST", "/identity/validate_token")


@mcp.tool()
async def bioclin_refresh_token(ctx: Context) -> dict:
    """
    Refresh the current session token

    Returns:
        dict: New token information
    """
    return await bioclin_request(ctx, "POST", "/identity/refresh_token")


# ============================================================================
# USER MANAGEMENT TOOLS (11)
# ============================================================================

@mcp.tool()
async def bioclin_create_user(
    email: EmailStr,
    password: str,
    username: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    is_active: bool = True,
    ctx: Context = None
) -> dict:
    """
    Create a new user in Bioclin

    Args:
        email: User's email address
        password: User's password
        username: Unique username
        first_name: User's first name (optional)
        last_name: User's last name (optional)
        is_active: Whether the user account is active (default: True)

    Returns:
        dict: Created user information
    """
    data = {
        "email": email,
        "password": password,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
        "is_active": is_active,
    }
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "POST", "/identity/create_user", json=data)


@mcp.tool()
async def bioclin_create_admin(
    email: EmailStr,
    password: str,
    username: str,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new admin user in Bioclin

    Args:
        email: Admin user's email address
        password: Admin user's password
        username: Unique admin username
        first_name: Admin user's first name (optional)
        last_name: Admin user's last name (optional)

    Returns:
        dict: Created admin user information
    """
    data = {
        "email": email,
        "password": password,
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "POST", "/identity/create_admin", json=data)


@mcp.tool()
async def bioclin_get_users(ctx: Context) -> dict:
    """
    Get all users (admin only)

    Returns:
        dict: List of all users
    """
    return await bioclin_request(ctx, "GET", "/identity/users/")


@mcp.tool()
async def bioclin_get_user_me(ctx: Context) -> dict:
    """
    Get current user's information

    Returns:
        dict: Current user's profile information
    """
    return await bioclin_request(ctx, "GET", "/identity/user_me")


@mcp.tool()
async def bioclin_get_user_context(
    orgs_skip: int = 0,
    orgs_limit: int = 100,
    ctx: Context = None
) -> dict:
    """
    Get current user's context including organizations and permissions

    Args:
        orgs_skip: Number of organizations to skip for pagination
        orgs_limit: Maximum number of organizations to return

    Returns:
        dict: User context with organizations and roles
    """
    return await bioclin_request(
        ctx,
        "GET",
        "/identity/user_context",
        params={"orgs_skip": orgs_skip, "orgs_limit": orgs_limit}
    )


@mcp.tool()
async def bioclin_update_user_me(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    email: Optional[EmailStr] = None,
    ctx: Context = None
) -> dict:
    """
    Update current user's profile information

    Args:
        first_name: Updated first name (optional)
        last_name: Updated last name (optional)
        email: Updated email address (optional)

    Returns:
        dict: Updated user information
    """
    data = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "PUT", "/identity/user_me", json=data)


@mcp.tool()
async def bioclin_set_user_admin(
    user_id: str,
    is_admin: bool,
    ctx: Context
) -> dict:
    """
    Set user's admin status (admin only)

    Args:
        user_id: UUID of the user
        is_admin: True to grant admin, False to revoke

    Returns:
        dict: Updated user information
    """
    return await bioclin_request(
        ctx,
        "PUT",
        f"/identity/set_user_admin/{user_id}",
        json={"is_admin": is_admin}
    )


@mcp.tool()
async def bioclin_set_user_active(
    user_id: str,
    is_active: bool,
    ctx: Context
) -> dict:
    """
    Set user's active status (admin only)

    Args:
        user_id: UUID of the user
        is_active: True to activate, False to deactivate

    Returns:
        dict: Updated user information
    """
    return await bioclin_request(
        ctx,
        "PUT",
        f"/identity/set_user_active/{user_id}",
        json={"is_active": is_active}
    )


@mcp.tool()
async def bioclin_recover_password(email: EmailStr, ctx: Context) -> dict:
    """
    Initiate password recovery for a user

    Args:
        email: User's email address

    Returns:
        dict: Password recovery status
    """
    return await bioclin_request(
        ctx,
        "POST",
        "/identity/recover",
        data={"email": email},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )


@mcp.tool()
async def bioclin_reset_password(
    token: str,
    password: str,
    ctx: Context
) -> dict:
    """
    Reset password using recovery token

    Args:
        token: Password recovery token from email
        password: New password

    Returns:
        dict: Password reset status
    """
    return await bioclin_request(
        ctx,
        "POST",
        "/identity/reset",
        data={"token": token, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )


@mcp.tool()
async def bioclin_delete_user(user_id: str, ctx: Context) -> dict:
    """
    Delete a user (admin only)

    Args:
        user_id: UUID of the user to delete

    Returns:
        dict: Deletion status
    """
    return await bioclin_request(ctx, "DELETE", f"/identity/users/{user_id}")


# ============================================================================
# ORGANIZATION TOOLS (6)
# ============================================================================

@mcp.tool()
async def bioclin_create_org(
    name: str,
    description: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new organization

    Args:
        name: Organization name
        description: Organization description (optional)

    Returns:
        dict: Created organization information
    """
    data = {"name": name}
    if description:
        data["description"] = description

    return await bioclin_request(ctx, "POST", "/identity/create_org", json=data)


@mcp.tool()
async def bioclin_get_orgs(ctx: Context) -> dict:
    """
    Get all organizations

    Returns:
        dict: List of all organizations
    """
    return await bioclin_request(ctx, "GET", "/identity/orgs/")


@mcp.tool()
async def bioclin_get_org(org_id: str, ctx: Context) -> dict:
    """
    Get organization by ID

    Args:
        org_id: UUID of the organization

    Returns:
        dict: Organization information
    """
    return await bioclin_request(ctx, "GET", f"/identity/orgs/{org_id}")


@mcp.tool()
async def bioclin_get_user_orgs(ctx: Context) -> dict:
    """
    Get current user's organizations

    Returns:
        dict: List of organizations the user belongs to
    """
    return await bioclin_request(ctx, "GET", "/identity/users/me/orgs")


@mcp.tool()
async def bioclin_update_active_org(org_id: str, ctx: Context) -> dict:
    """
    Update user's active organization

    Args:
        org_id: UUID of the organization to set as active

    Returns:
        dict: Updated user context
    """
    return await bioclin_request(
        ctx,
        "PATCH",
        "/identity/users/update_active_org",
        params={"org_id": org_id}
    )


@mcp.tool()
async def bioclin_add_user_to_org(
    user_id: str,
    org_id: str,
    role_id: str,
    ctx: Context
) -> dict:
    """
    Add a user to an organization with a specific role

    Args:
        user_id: UUID of the user
        org_id: UUID of the organization
        role_id: UUID of the role to assign

    Returns:
        dict: Organization membership information
    """
    return await bioclin_request(
        ctx,
        "POST",
        "/identity/add_user_to_org",
        json={
            "user_id": user_id,
            "organization_id": org_id,
            "role_id": role_id,
        }
    )


# ============================================================================
# PERMISSION TOOLS (2)
# ============================================================================

@mcp.tool()
async def bioclin_get_roles(ctx: Context) -> dict:
    """
    Get all available roles

    Returns:
        dict: List of all roles with their permissions
    """
    return await bioclin_request(ctx, "GET", "/identity/roles/")


@mcp.tool()
async def bioclin_get_permissions(ctx: Context) -> dict:
    """
    Get all available permissions

    Returns:
        dict: List of all permissions in the system
    """
    return await bioclin_request(ctx, "GET", "/identity/permissions/")


# ============================================================================
# PARAMETER TOOLS (4)
# ============================================================================

@mcp.tool()
async def bioclin_create_param(
    name: str,
    param_type: str,
    description: Optional[str] = None,
    default_value: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new parameter

    Args:
        name: Parameter name
        param_type: Parameter type (string, number, boolean, etc.)
        description: Parameter description (optional)
        default_value: Default value for the parameter (optional)

    Returns:
        dict: Created parameter information
    """
    data = {
        "name": name,
        "type": param_type,
        "description": description,
        "default_value": default_value,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "POST", "/project/create_param", json=data)


@mcp.tool()
async def bioclin_get_params(ctx: Context) -> dict:
    """
    Get all parameters

    Returns:
        dict: List of all parameters
    """
    return await bioclin_request(ctx, "GET", "/project/params/")


@mcp.tool()
async def bioclin_update_param(
    param_id: str,
    name: Optional[str] = None,
    param_type: Optional[str] = None,
    description: Optional[str] = None,
    default_value: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Update a parameter

    Args:
        param_id: UUID of the parameter to update
        name: Updated parameter name (optional)
        param_type: Updated parameter type (optional)
        description: Updated description (optional)
        default_value: Updated default value (optional)

    Returns:
        dict: Updated parameter information
    """
    data = {
        "name": name,
        "type": param_type,
        "description": description,
        "default_value": default_value,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "PUT", f"/project/params/{param_id}", json=data)


@mcp.tool()
async def bioclin_delete_param(param_id: str, ctx: Context) -> dict:
    """
    Delete a parameter

    Args:
        param_id: UUID of the parameter to delete

    Returns:
        dict: Deletion status
    """
    return await bioclin_request(ctx, "DELETE", f"/project/params/{param_id}")


# ============================================================================
# ANALYSIS TYPE TOOLS (4)
# ============================================================================

@mcp.tool()
async def bioclin_create_analysis_type(
    name: str,
    description: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new analysis type

    Args:
        name: Analysis type name (e.g., "RNA-Seq", "WGS")
        description: Analysis type description (optional)

    Returns:
        dict: Created analysis type information
    """
    data = {"name": name}
    if description:
        data["description"] = description

    return await bioclin_request(ctx, "POST", "/project/create_analysis_type", json=data)


@mcp.tool()
async def bioclin_get_analysis_types(ctx: Context) -> dict:
    """
    Get all analysis types

    Returns:
        dict: List of all available analysis types
    """
    return await bioclin_request(ctx, "GET", "/project/analysis_types/")


@mcp.tool()
async def bioclin_update_analysis_type(
    analysis_type_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Update an analysis type

    Args:
        analysis_type_id: UUID of the analysis type
        name: Updated name (optional)
        description: Updated description (optional)

    Returns:
        dict: Updated analysis type information
    """
    data = {}
    if name:
        data["name"] = name
    if description:
        data["description"] = description

    return await bioclin_request(
        ctx,
        "PUT",
        f"/project/analysis_types/{analysis_type_id}",
        json=data
    )


@mcp.tool()
async def bioclin_delete_analysis_type(
    analysis_type_id: str,
    ctx: Context
) -> dict:
    """
    Delete an analysis type

    Args:
        analysis_type_id: UUID of the analysis type to delete

    Returns:
        dict: Deletion status
    """
    return await bioclin_request(ctx, "DELETE", f"/project/analysis_types/{analysis_type_id}")


# ============================================================================
# PROJECT TOOLS (5)
# ============================================================================

@mcp.tool()
async def bioclin_create_project(
    name: str,
    analysis_type_id: str,
    description: Optional[str] = None,
    organization_id: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new project

    Args:
        name: Project name
        analysis_type_id: UUID of the analysis type
        description: Project description (optional)
        organization_id: UUID of the organization (optional, uses active org if not provided)

    Returns:
        dict: Created project information
    """
    data = {
        "name": name,
        "analysis_type_id": analysis_type_id,
        "description": description,
        "organization_id": organization_id,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "POST", "/project/create_project", json=data)


@mcp.tool()
async def bioclin_get_projects(ctx: Context) -> dict:
    """
    Get all projects (admin only)

    Returns:
        dict: List of all projects
    """
    return await bioclin_request(ctx, "GET", "/project/projects/")


@mcp.tool()
async def bioclin_get_user_projects(ctx: Context) -> dict:
    """
    Get current user's projects

    Returns:
        dict: List of projects accessible to the current user
    """
    return await bioclin_request(ctx, "GET", "/project/user_projects/")


@mcp.tool()
async def bioclin_get_project(project_id: str, ctx: Context) -> dict:
    """
    Get project by ID

    Args:
        project_id: UUID of the project

    Returns:
        dict: Project information
    """
    return await bioclin_request(ctx, "GET", f"/project/projects/{project_id}")


@mcp.tool()
async def bioclin_delete_project(project_id: str, ctx: Context) -> dict:
    """
    Delete a project

    Args:
        project_id: UUID of the project to delete

    Returns:
        dict: Deletion status
    """
    return await bioclin_request(ctx, "DELETE", f"/project/projects/{project_id}")


# ============================================================================
# RUN TOOLS (5)
# ============================================================================

@mcp.tool()
async def bioclin_create_run(
    name: str,
    project_id: str,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    ctx: Context = None
) -> dict:
    """
    Create a new analysis run

    Args:
        name: Run name
        project_id: UUID of the project
        description: Run description (optional)
        parameters: Run parameters as key-value pairs (optional)

    Returns:
        dict: Created run information
    """
    data = {
        "name": name,
        "project_id": project_id,
        "description": description,
        "parameters": parameters,
    }
    data = {k: v for k, v in data.items() if v is not None}

    return await bioclin_request(ctx, "POST", "/project/create_run", json=data)


@mcp.tool()
async def bioclin_get_runs(ctx: Context) -> dict:
    """
    Get all runs (admin only)

    Returns:
        dict: List of all runs
    """
    return await bioclin_request(ctx, "GET", "/project/runs/")


@mcp.tool()
async def bioclin_get_runs_by_project(
    project_id: str,
    skip: int = 0,
    limit: int = 100,
    ctx: Context = None
) -> dict:
    """
    Get all runs for a specific project

    Args:
        project_id: UUID of the project
        skip: Number of runs to skip for pagination
        limit: Maximum number of runs to return

    Returns:
        dict: List of runs for the project
    """
    return await bioclin_request(
        ctx,
        "GET",
        "/project/runs_by_project",
        params={"project_id": project_id, "skip": skip, "limit": limit}
    )


@mcp.tool()
async def bioclin_get_runs_by_org(
    org_id: str,
    skip: int = 0,
    limit: int = 100,
    ctx: Context = None
) -> dict:
    """
    Get all runs for a specific organization

    Args:
        org_id: UUID of the organization
        skip: Number of runs to skip for pagination
        limit: Maximum number of runs to return

    Returns:
        dict: List of runs for the organization
    """
    return await bioclin_request(
        ctx,
        "GET",
        "/project/runs_by_org",
        params={"org_id": org_id, "skip": skip, "limit": limit}
    )


@mcp.tool()
async def bioclin_delete_run(run_id: str, ctx: Context) -> dict:
    """
    Delete a run

    Args:
        run_id: UUID of the run to delete

    Returns:
        dict: Deletion status
    """
    return await bioclin_request(ctx, "DELETE", f"/project/runs/{run_id}")


# ============================================================================
# GOOGLE CLOUD STORAGE TOOLS (3)
# ============================================================================

@mcp.tool()
async def bioclin_generate_signed_url(
    bucket_name: str,
    blob_name: str,
    expiration_minutes: int = 60,
    ctx: Context = None
) -> dict:
    """
    Generate a signed URL for accessing a file in Google Cloud Storage

    Args:
        bucket_name: GCS bucket name
        blob_name: Path to the file in the bucket
        expiration_minutes: URL expiration time in minutes (default: 60)

    Returns:
        dict: Signed URL and metadata
    """
    return await bioclin_request(
        ctx,
        "POST",
        "/google-ops/generate_signed_url",
        json={
            "bucket_name": bucket_name,
            "blob_name": blob_name,
            "expiration_minutes": expiration_minutes,
        }
    )


@mcp.tool()
async def bioclin_get_html_report(
    bucket_name: str,
    blob_name: str,
    ctx: Context
) -> dict:
    """
    Get HTML report from Google Cloud Storage

    Args:
        bucket_name: GCS bucket name
        blob_name: Path to the HTML file in the bucket

    Returns:
        dict: HTML content and metadata
    """
    return await bioclin_request(
        ctx,
        "GET",
        "/google-ops/get_html_report",
        params={"bucket_name": bucket_name, "blob_name": blob_name}
    )


@mcp.tool()
async def bioclin_download_file(
    bucket_name: str,
    blob_name: str,
    ctx: Context
) -> dict:
    """
    Download a file from Google Cloud Storage

    Args:
        bucket_name: GCS bucket name
        blob_name: Path to the file in the bucket

    Returns:
        dict: File content or download URL
    """
    return await bioclin_request(
        ctx,
        "GET",
        "/google-ops/download",
        params={"bucket_name": bucket_name, "blob_name": blob_name}
    )


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    # Run with STDIO transport (for Claude Desktop)
    mcp.run()

    # Alternatively, run with HTTP transport (for web deployments):
    # mcp.run(transport="http", host="0.0.0.0", port=8000)

    # Or with SSE transport (for streaming):
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)
