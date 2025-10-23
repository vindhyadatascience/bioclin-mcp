#!/usr/bin/env python3
"""
Bioclin MCP Server
A Model Context Protocol server for the Bioclin API

This server provides tools to interact with the Bioclin API including:
- User authentication and management
- Organization management
- Project management
- Run management
- Parameter and analysis type management
- Google Cloud Storage operations
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, List
from urllib.parse import urljoin
import httpx

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from pydantic import AnyUrl

from bioclin_schemas import *

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bioclin-mcp")

# Default base URL - can be overridden via environment variable or initialization
DEFAULT_BASE_URL = "https://bioclin.vindhyadatascience.com/api/v1"


class BioclinClient:
    """HTTP client for Bioclin API with session management"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.cookies: Dict[str, str] = {}
        self.csrf_token: Optional[str] = None

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers including CSRF token if available"""
        headers = {"Content-Type": "application/json"}
        if self.csrf_token:
            headers["X-CSRF-Token"] = self.csrf_token
        return headers

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an authenticated request to the API"""
        url = urljoin(self.base_url, endpoint)

        headers = self._get_headers()

        try:
            if form_data:
                # For form-encoded requests (like login)
                response = await self.client.request(
                    method,
                    url,
                    data=form_data,
                    params=params,
                    cookies=self.cookies,
                    headers={"X-CSRF-Token": self.csrf_token} if self.csrf_token else {},
                )
            else:
                response = await self.client.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    cookies=self.cookies,
                    headers=headers,
                )

            # Update cookies from response
            if response.cookies:
                self.cookies.update(dict(response.cookies))
                # Extract CSRF token from cookie if present
                if 'csrf_token' in response.cookies:
                    self.csrf_token = response.cookies['csrf_token']

            response.raise_for_status()

            # Handle different content types
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                return {"content": response.text, "content_type": content_type}

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            try:
                error_json = e.response.json()
                error_detail = json.dumps(error_json, indent=2)
            except:
                pass
            raise Exception(f"HTTP {e.response.status_code}: {error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


class BioclinMCPServer:
    """MCP Server for Bioclin API"""

    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.server = Server("bioclin-mcp")
        self.client = BioclinClient(base_url)
        self._setup_handlers()

    def _setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools() -> list[Tool]:
            """List all available tools"""
            return [
                # ========== Authentication ==========
                Tool(
                    name="bioclin_login",
                    description="Login to Bioclin API with username and password. Returns session cookies for subsequent requests.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {"type": "string", "description": "Username or email"},
                            "password": {"type": "string", "description": "Password"},
                        },
                        "required": ["username", "password"],
                    },
                ),
                Tool(
                    name="bioclin_logout",
                    description="Logout from Bioclin API and clear session",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="bioclin_validate_token",
                    description="Validate current access token",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="bioclin_refresh_token",
                    description="Refresh access token",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),

                # ========== User Management ==========
                Tool(
                    name="bioclin_create_user",
                    description="Create a new user account",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "password": {"type": "string", "minLength": 8, "maxLength": 40},
                        },
                        "required": ["first_name", "last_name", "email", "password"],
                    },
                ),
                Tool(
                    name="bioclin_create_admin",
                    description="Create a new admin user (requires admin privileges)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "password": {"type": "string", "minLength": 8, "maxLength": 40},
                        },
                        "required": ["first_name", "last_name", "email", "password"],
                    },
                ),
                Tool(
                    name="bioclin_get_users",
                    description="Get list of all users (requires admin privileges)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_get_user_me",
                    description="Get current user information",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="bioclin_get_user_context",
                    description="Get current user context including user info, active org, and all orgs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "orgs_skip": {"type": "integer", "default": 0},
                            "orgs_limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_update_user_me",
                    description="Update current user information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string"},
                            "last_name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "password": {"type": "string", "minLength": 8, "maxLength": 40},
                        },
                        "required": ["first_name", "last_name", "email", "password"],
                    },
                ),
                Tool(
                    name="bioclin_set_user_admin",
                    description="Set user admin status (requires admin privileges)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "format": "uuid"},
                            "is_admin": {"type": "boolean"},
                        },
                        "required": ["user_id", "is_admin"],
                    },
                ),
                Tool(
                    name="bioclin_set_user_active",
                    description="Set user active status (requires admin privileges)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "format": "uuid"},
                            "is_active": {"type": "boolean"},
                        },
                        "required": ["user_id", "is_active"],
                    },
                ),
                Tool(
                    name="bioclin_recover_password",
                    description="Send password recovery email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "email": {"type": "string", "format": "email"},
                        },
                        "required": ["email"],
                    },
                ),
                Tool(
                    name="bioclin_reset_password",
                    description="Reset password with token from email",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "token": {"type": "string"},
                            "new_password": {"type": "string", "minLength": 8},
                        },
                        "required": ["token", "new_password"],
                    },
                ),
                Tool(
                    name="bioclin_delete_user",
                    description="Delete a user (requires admin privileges)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "user_id": {"type": "string", "format": "uuid"},
                        },
                        "required": ["user_id"],
                    },
                ),

                # ========== Organization Management ==========
                Tool(
                    name="bioclin_create_org",
                    description="Create a new organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                        },
                        "required": ["name", "description"],
                    },
                ),
                Tool(
                    name="bioclin_get_orgs",
                    description="Get list of all organizations",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_get_org",
                    description="Get organization by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "org_id": {"type": "string", "format": "uuid"},
                        },
                        "required": ["org_id"],
                    },
                ),
                Tool(
                    name="bioclin_get_user_orgs",
                    description="Get organizations for current user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_update_active_org",
                    description="Update active organization for current user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "org_id": {"type": "string", "format": "uuid"},
                        },
                        "required": ["org_id"],
                    },
                ),
                Tool(
                    name="bioclin_add_user_to_org",
                    description="Add user to organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "orgname": {"type": "string"},
                        },
                        "required": ["username", "orgname"],
                    },
                ),

                # ========== Permission Management ==========
                Tool(
                    name="bioclin_get_roles",
                    description="Get all roles",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),
                Tool(
                    name="bioclin_get_permissions",
                    description="Get all permissions",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                    },
                ),

                # ========== Parameter Management ==========
                Tool(
                    name="bioclin_create_param",
                    description="Create a new parameter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "help": {"type": "string"},
                            "type": {"type": "string", "default": "text_box"},
                        },
                        "required": ["name", "description", "help"],
                    },
                ),
                Tool(
                    name="bioclin_get_params",
                    description="Get all parameters",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_update_param",
                    description="Update a parameter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "param_id": {"type": "string"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "help": {"type": "string"},
                            "type": {"type": "string"},
                        },
                        "required": ["param_id"],
                    },
                ),
                Tool(
                    name="bioclin_delete_param",
                    description="Delete a parameter",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "param_id": {"type": "string"},
                        },
                        "required": ["param_id"],
                    },
                ),

                # ========== Analysis Type Management ==========
                Tool(
                    name="bioclin_create_analysis_type",
                    description="Create a new analysis type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "image_name": {"type": "string"},
                            "image_hash": {"type": "string"},
                            "param_ids": {"type": "array", "items": {"type": "string", "format": "uuid"}},
                        },
                        "required": ["name", "description", "image_name", "image_hash", "param_ids"],
                    },
                ),
                Tool(
                    name="bioclin_get_analysis_types",
                    description="Get all analysis types",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_update_analysis_type",
                    description="Update an analysis type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type_name": {"type": "string"},
                            "description": {"type": "string"},
                            "image_name": {"type": "string"},
                            "image_hash": {"type": "string"},
                            "param_ids": {"type": "array", "items": {"type": "string", "format": "uuid"}},
                        },
                        "required": ["analysis_type_name"],
                    },
                ),
                Tool(
                    name="bioclin_delete_analysis_type",
                    description="Delete an analysis type",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type_id": {"type": "string"},
                        },
                        "required": ["analysis_type_id"],
                    },
                ),

                # ========== Project Management ==========
                Tool(
                    name="bioclin_create_project",
                    description="Create a new project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "analysis_type_id": {"type": "string", "format": "uuid"},
                            "project_params": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "param_id": {"type": "string", "format": "uuid"},
                                        "pattern": {"type": "string"},
                                    },
                                    "required": ["param_id", "pattern"],
                                },
                            },
                        },
                        "required": ["name", "analysis_type_id"],
                    },
                ),
                Tool(
                    name="bioclin_get_projects",
                    description="Get all projects",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_get_user_projects",
                    description="Get projects for current user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_get_project",
                    description="Get project by ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "format": "uuid"},
                        },
                        "required": ["project_id"],
                    },
                ),
                Tool(
                    name="bioclin_delete_project",
                    description="Delete a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string"},
                        },
                        "required": ["project_id"],
                    },
                ),

                # ========== Run Management ==========
                Tool(
                    name="bioclin_create_run",
                    description="Create a new run for a project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "project_id": {"type": "string", "format": "uuid"},
                        },
                        "required": ["name", "project_id"],
                    },
                ),
                Tool(
                    name="bioclin_get_runs",
                    description="Get all runs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                    },
                ),
                Tool(
                    name="bioclin_get_runs_by_project",
                    description="Get runs for a specific project",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "project_id": {"type": "string", "format": "uuid"},
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                        "required": ["project_id"],
                    },
                ),
                Tool(
                    name="bioclin_get_runs_by_org",
                    description="Get runs for a specific organization",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "organization_id": {"type": "string", "format": "uuid"},
                            "skip": {"type": "integer", "default": 0},
                            "limit": {"type": "integer", "default": 100},
                        },
                        "required": ["organization_id"],
                    },
                ),
                Tool(
                    name="bioclin_delete_run",
                    description="Delete a run",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "run_id": {"type": "string"},
                        },
                        "required": ["run_id"],
                    },
                ),

                # ========== Google Cloud Storage ==========
                Tool(
                    name="bioclin_generate_signed_url",
                    description="Generate a signed URL for a file in Google Cloud Storage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bucket_name": {"type": "string"},
                            "file_name": {"type": "string"},
                            "response_type": {"type": "string", "default": "text/html"},
                            "expiration_minutes": {"type": "integer", "default": 60},
                            "force_download": {"type": "boolean", "default": False},
                        },
                        "required": ["bucket_name", "file_name"],
                    },
                ),
                Tool(
                    name="bioclin_get_html_report",
                    description="Get HTML report from Google Cloud Storage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bucket_name": {"type": "string"},
                            "file_name": {"type": "string"},
                        },
                        "required": ["bucket_name", "file_name"],
                    },
                ),
                Tool(
                    name="bioclin_download_file",
                    description="Download a file from Google Cloud Storage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bucket_name": {"type": "string"},
                            "file_name": {"type": "string"},
                        },
                        "required": ["bucket_name", "file_name"],
                    },
                ),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Any) -> list[TextContent]:
            """Handle tool calls"""
            try:
                result = await self._handle_tool_call(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                logger.error(error_msg)
                return [TextContent(type="text", text=json.dumps({"error": error_msg}, indent=2))]

    async def _handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""

        # ========== Authentication ==========
        if name == "bioclin_login":
            return await self.client.request(
                "POST",
                "/api/v1/identity/login",
                form_data={
                    "username": arguments["username"],
                    "password": arguments["password"],
                    "grant_type": "password",
                },
            )

        elif name == "bioclin_logout":
            return await self.client.request("POST", "/api/v1/identity/logout")

        elif name == "bioclin_validate_token":
            return await self.client.request("POST", "/api/v1/identity/token/validate")

        elif name == "bioclin_refresh_token":
            return await self.client.request("POST", "/api/v1/identity/token/refresh")

        # ========== User Management ==========
        elif name == "bioclin_create_user":
            return await self.client.request("POST", "/api/v1/identity/create_user", data=arguments)

        elif name == "bioclin_create_admin":
            return await self.client.request("POST", "/api/v1/identity/create_admin", data=arguments)

        elif name == "bioclin_get_users":
            return await self.client.request("GET", "/api/v1/identity/users/", params=arguments)

        elif name == "bioclin_get_user_me":
            return await self.client.request("GET", "/api/v1/identity/user_me")

        elif name == "bioclin_get_user_context":
            return await self.client.request("GET", "/api/v1/identity/user_context", params=arguments)

        elif name == "bioclin_update_user_me":
            return await self.client.request("PATCH", "/api/v1/identity/users_update_me", data=arguments)

        elif name == "bioclin_set_user_admin":
            user_id = arguments.pop("user_id")
            return await self.client.request(
                "PATCH",
                f"/api/v1/identity/set_user_admin/{user_id}",
                params=arguments
            )

        elif name == "bioclin_set_user_active":
            user_id = arguments.pop("user_id")
            return await self.client.request(
                "PATCH",
                f"/api/v1/identity/set_user_active/{user_id}",
                params=arguments
            )

        elif name == "bioclin_recover_password":
            email = arguments["email"]
            return await self.client.request("POST", f"/api/v1/identity/recover_password/{email}")

        elif name == "bioclin_reset_password":
            return await self.client.request("POST", "/api/v1/identity/reset_password", data=arguments)

        elif name == "bioclin_delete_user":
            return await self.client.request("POST", "/api/v1/identity/delete_user", params=arguments)

        # ========== Organization Management ==========
        elif name == "bioclin_create_org":
            return await self.client.request("POST", "/api/v1/identity/create_org", data=arguments)

        elif name == "bioclin_get_orgs":
            return await self.client.request("GET", "/api/v1/identity/orgs/", params=arguments)

        elif name == "bioclin_get_org":
            org_id = arguments["org_id"]
            return await self.client.request("GET", f"/api/v1/identity/orgs/{org_id}")

        elif name == "bioclin_get_user_orgs":
            return await self.client.request("GET", "/api/v1/identity/users/me/orgs", params=arguments)

        elif name == "bioclin_update_active_org":
            return await self.client.request("PATCH", "/api/v1/identity/users/update_active_org", params=arguments)

        elif name == "bioclin_add_user_to_org":
            return await self.client.request("POST", "/api/v1/identity/add_user_to_org", params=arguments)

        # ========== Permission Management ==========
        elif name == "bioclin_get_roles":
            return await self.client.request("GET", "/api/v1/identity/roles")

        elif name == "bioclin_get_permissions":
            return await self.client.request("GET", "/api/v1/identity/permissions")

        # ========== Parameter Management ==========
        elif name == "bioclin_create_param":
            return await self.client.request("POST", "/api/v1/project/create_param", data=arguments)

        elif name == "bioclin_get_params":
            return await self.client.request("GET", "/api/v1/project/params/", params=arguments)

        elif name == "bioclin_update_param":
            param_id = arguments.pop("param_id")
            return await self.client.request(
                "PATCH",
                "/api/v1/project/update_param",
                params={"param_id": param_id},
                data=arguments
            )

        elif name == "bioclin_delete_param":
            return await self.client.request("POST", "/api/v1/project/delete_param", params=arguments)

        # ========== Analysis Type Management ==========
        elif name == "bioclin_create_analysis_type":
            return await self.client.request("POST", "/api/v1/project/create_analysis_type", data=arguments)

        elif name == "bioclin_get_analysis_types":
            return await self.client.request("GET", "/api/v1/project/analysis_types/", params=arguments)

        elif name == "bioclin_update_analysis_type":
            analysis_type_name = arguments.pop("analysis_type_name")
            return await self.client.request(
                "PATCH",
                f"/api/v1/project/update_analysis_type/{analysis_type_name}",
                data=arguments
            )

        elif name == "bioclin_delete_analysis_type":
            return await self.client.request("POST", "/api/v1/project/delete_analysis_type", params=arguments)

        # ========== Project Management ==========
        elif name == "bioclin_create_project":
            return await self.client.request("POST", "/api/v1/project/create_project", data=arguments)

        elif name == "bioclin_get_projects":
            return await self.client.request("GET", "/api/v1/project/projects/", params=arguments)

        elif name == "bioclin_get_user_projects":
            return await self.client.request("GET", "/api/v1/project/user_projects/", params=arguments)

        elif name == "bioclin_get_project":
            project_id = arguments["project_id"]
            return await self.client.request("GET", f"/api/v1/project/projects/{project_id}")

        elif name == "bioclin_delete_project":
            return await self.client.request("POST", "/api/v1/project/delete_project", params=arguments)

        # ========== Run Management ==========
        elif name == "bioclin_create_run":
            return await self.client.request("POST", "/api/v1/project/create_run", data=arguments)

        elif name == "bioclin_get_runs":
            return await self.client.request("GET", "/api/v1/project/runs", params=arguments)

        elif name == "bioclin_get_runs_by_project":
            return await self.client.request("GET", "/api/v1/project/runs_by_project", params=arguments)

        elif name == "bioclin_get_runs_by_org":
            return await self.client.request("GET", "/api/v1/project/runs_by_org", params=arguments)

        elif name == "bioclin_delete_run":
            return await self.client.request("POST", "/api/v1/project/delete_run", params=arguments)

        # ========== Google Cloud Storage ==========
        elif name == "bioclin_generate_signed_url":
            return await self.client.request("POST", "/api/v1/google-ops/generate_signed_url", params=arguments)

        elif name == "bioclin_get_html_report":
            return await self.client.request("GET", "/api/v1/google-ops/get_html_report", params=arguments)

        elif name == "bioclin_download_file":
            return await self.client.request("GET", "/api/v1/google-ops/download_file", params=arguments)

        else:
            raise ValueError(f"Unknown tool: {name}")

    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point"""
    import os

    # Get base URL from environment or use default
    base_url = os.getenv("BIOCLIN_API_URL", DEFAULT_BASE_URL)

    server = BioclinMCPServer(base_url)
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
