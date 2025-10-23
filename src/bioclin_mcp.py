#!/usr/bin/env python3
"""
Bioclin MCP Server
Wraps Bioclin API endpoints as MCP tools that Claude can call
"""

import json
import os
import sys
import requests
from typing import Any
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent

# Load environment variables
load_dotenv()

# Configuration
BIOCLIN_EMAIL = os.getenv("BIOCLIN_EMAIL")
BIOCLIN_PASSWORD = os.getenv("BIOCLIN_PASSWORD")
BIOCLIN_API_BASE = os.getenv("BIOCLIN_API_BASE", "https://bioclin.vindhyadatascience.com/api/v1")

# Global session with cookies
session = requests.Session()


def authenticate():
    """Authenticate with Bioclin API and store cookies in session"""
    try:
        # API expects form data with 'username' field (not 'email')
        response = session.post(
            f"{BIOCLIN_API_BASE}/identity/login",
            data={"username": BIOCLIN_EMAIL, "password": BIOCLIN_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()

        # Check if we got the access token cookie
        if "access_token" not in session.cookies:
            print(f"✗ No access token in response", file=sys.stderr)
            return False

        print(f"✓ Successfully authenticated with Bioclin API", file=sys.stderr)
        return True
    except Exception as e:
        print(f"✗ Authentication failed: {e}", file=sys.stderr)
        return False


def api_call(method: str, endpoint: str, data: dict = None) -> dict:
    """Make authenticated API call to Bioclin using session cookies"""
    try:
        url = f"{BIOCLIN_API_BASE}{endpoint}"
        headers = {"Content-Type": "application/json"}

        if method == "GET":
            response = session.get(url, headers=headers)
        elif method == "POST":
            response = session.post(url, json=data, headers=headers)
        elif method == "PATCH":
            response = session.patch(url, json=data, headers=headers)
        else:
            return {"error": f"Unsupported method: {method}"}

        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


# Create MCP server
server = Server("bioclin-mcp")


@server.list_tools()
async def list_tools():
    """List available tools"""
    return [
        Tool(
            name="read_user_projects",
            description="Get all projects for the current user",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="read_runs",
            description="Get all runs across all projects",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="read_runs_by_project",
            description="Get runs for a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="create_run",
            description="Create a new run for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "run_name": {"type": "string", "description": "Name for the run"},
                    "analysis_type": {"type": "string", "description": "Type of analysis"}
                },
                "required": ["project_id", "run_name", "analysis_type"]
            }
        ),
        Tool(
            name="read_user_me",
            description="Get current user information",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="read_analysis_types",
            description="Get all available analysis types",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Any:
    """Execute a tool"""
    try:
        if name == "read_user_projects":
            result = api_call("GET", "/project/user_projects/")
        
        elif name == "read_runs":
            result = api_call("GET", "/project/runs")
        
        elif name == "read_runs_by_project":
            project_id = arguments.get("project_id")
            result = api_call("GET", f"/project/runs_by_project?project_id={project_id}")
        
        elif name == "create_run":
            data = {
                "project_id": arguments.get("project_id"),
                "run_name": arguments.get("run_name"),
                "analysis_type": arguments.get("analysis_type")
            }
            result = api_call("POST", "/project/create_run", data)
        
        elif name == "read_user_me":
            result = api_call("GET", "/identity/user_me")
        
        elif name == "read_analysis_types":
            result = api_call("GET", "/project/analysis_types/")
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    """Start the MCP server"""
    # Authenticate first
    if not authenticate():
        sys.exit(1)

    # Start server on stdio
    from mcp.server.stdio import stdio_server

    print("✓ Bioclin MCP Server started", file=sys.stderr)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())