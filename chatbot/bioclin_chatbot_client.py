"""
Bioclin Chatbot Client
A Python client for integrating chatbots with the MCPX Bioclin gateway

This client handles:
- OAuth authentication
- MCP protocol communication
- Tool discovery and execution
- Session management with Bioclin API
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class BioclinSession:
    """Represents an authenticated Bioclin session"""
    access_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    bioclin_logged_in: bool = False


class BioclinChatbotClient:
    """
    Client for chatbot integration with MCPX Bioclin gateway

    Example:
        client = BioclinChatbotClient(
            mcpx_url="https://your-service.run.app",
            oauth_config={
                "token_url": "https://your-domain.us.auth0.com/oauth/token",
                "client_id": "your_client_id",
                "client_secret": "your_client_secret",
                "audience": "mcpx-bioclin"
            }
        )

        async with client:
            # Login to Bioclin
            await client.login_bioclin("user@example.com", "password")

            # List tools
            tools = await client.list_tools()

            # Create a project
            result = await client.create_project(
                name="RNA-Seq Analysis",
                analysis_type_id="123e4567-e89b-12d3-a456-426614174000"
            )
    """

    def __init__(
        self,
        mcpx_url: str,
        oauth_config: Optional[Dict[str, str]] = None,
        consumer_tag: str = "Chatbot",
        timeout: float = 30.0
    ):
        """
        Initialize the chatbot client

        Args:
            mcpx_url: URL of the MCPX gateway (e.g., https://your-service.run.app)
            oauth_config: OAuth configuration dict with keys:
                - token_url: OAuth token endpoint
                - client_id: OAuth client ID
                - client_secret: OAuth client secret
                - audience: OAuth audience (API identifier)
            consumer_tag: Consumer tag for MCPX permissions (default: "Chatbot")
            timeout: HTTP request timeout in seconds
        """
        self.mcpx_url = mcpx_url.rstrip('/')
        self.oauth_config = oauth_config
        self.consumer_tag = consumer_tag
        self.timeout = timeout

        self.session = BioclinSession()
        self.http_client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.http_client = httpx.AsyncClient(timeout=self.timeout)

        # Authenticate with OAuth if config provided
        if self.oauth_config:
            await self._get_oauth_token()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.http_client:
            await self.http_client.aclose()

    async def _get_oauth_token(self):
        """Get OAuth access token using client credentials flow"""
        if not self.oauth_config:
            return

        response = await self.http_client.post(
            self.oauth_config["token_url"],
            json={
                "client_id": self.oauth_config["client_id"],
                "client_secret": self.oauth_config["client_secret"],
                "audience": self.oauth_config["audience"],
                "grant_type": "client_credentials"
            }
        )
        response.raise_for_status()

        data = response.json()
        self.session.access_token = data["access_token"]

        # Calculate token expiration
        expires_in = data.get("expires_in", 3600)
        self.session.expires_at = datetime.now() + timedelta(seconds=expires_in)

    async def _ensure_token_valid(self):
        """Ensure OAuth token is valid, refresh if needed"""
        if not self.oauth_config:
            return

        if not self.session.access_token or \
           (self.session.expires_at and datetime.now() >= self.session.expires_at):
            await self._get_oauth_token()

    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for MCPX requests"""
        headers = {
            "Content-Type": "application/json",
            "x-lunar-consumer-tag": self.consumer_tag
        }

        if self.session.access_token:
            headers["Authorization"] = f"Bearer {self.session.access_token}"

        return headers

    async def _call_mcp(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Call MCP protocol method

        Args:
            method: MCP method name (e.g., "tools/list", "tools/call")
            params: Method parameters

        Returns:
            MCP response dict
        """
        await self._ensure_token_valid()

        payload = {"method": method}
        if params:
            payload["params"] = params

        response = await self.http_client.post(
            f"{self.mcpx_url}/mcp",
            json=payload,
            headers=self._get_headers()
        )
        response.raise_for_status()

        return response.json()

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available Bioclin tools

        Returns:
            List of tool definitions with name, description, and inputSchema
        """
        result = await self._call_mcp("tools/list")
        return result.get("result", {}).get("tools", [])

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a Bioclin tool

        Args:
            tool_name: Name of the tool (e.g., "bioclin_login")
            arguments: Tool arguments as dict

        Returns:
            Tool execution result
        """
        result = await self._call_mcp(
            "tools/call",
            {
                "name": tool_name,
                "arguments": arguments
            }
        )

        # Extract content from MCP response
        content = result.get("result", {}).get("content", [])
        if content and len(content) > 0:
            # Parse JSON from text content
            text = content[0].get("text", "{}")
            return json.loads(text)

        return result

    # ========== Bioclin-Specific Methods ==========

    async def login_bioclin(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to Bioclin API

        Args:
            username: Bioclin username or email
            password: Bioclin password

        Returns:
            Login response from Bioclin API
        """
        result = await self.call_tool(
            "bioclin_login",
            {"username": username, "password": password}
        )

        if "error" not in result:
            self.session.bioclin_logged_in = True

        return result

    async def get_user_info(self) -> Dict[str, Any]:
        """Get current Bioclin user information"""
        return await self.call_tool("bioclin_get_user_me", {})

    async def get_user_context(self) -> Dict[str, Any]:
        """Get user context including active org and all orgs"""
        return await self.call_tool("bioclin_get_user_context", {})

    async def list_projects(self) -> Dict[str, Any]:
        """List all projects accessible to user"""
        return await self.call_tool("bioclin_get_user_projects", {})

    async def create_project(
        self,
        name: str,
        analysis_type_id: str,
        description: Optional[str] = None,
        project_params: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Create a new Bioclin project

        Args:
            name: Project name
            analysis_type_id: UUID of the analysis type
            description: Optional project description
            project_params: Optional list of project parameters

        Returns:
            Created project details
        """
        args = {
            "name": name,
            "analysis_type_id": analysis_type_id
        }

        if description:
            args["description"] = description
        if project_params:
            args["project_params"] = project_params

        return await self.call_tool("bioclin_create_project", args)

    async def create_run(self, name: str, project_id: str) -> Dict[str, Any]:
        """
        Create a new run for a project

        Args:
            name: Run name
            project_id: UUID of the project

        Returns:
            Created run details
        """
        return await self.call_tool(
            "bioclin_create_run",
            {"name": name, "project_id": project_id}
        )

    async def get_runs_by_project(self, project_id: str) -> Dict[str, Any]:
        """Get all runs for a specific project"""
        return await self.call_tool(
            "bioclin_get_runs_by_project",
            {"project_id": project_id}
        )

    async def list_analysis_types(self) -> Dict[str, Any]:
        """List all available analysis types"""
        return await self.call_tool("bioclin_get_analysis_types", {})

    async def list_organizations(self) -> Dict[str, Any]:
        """List all organizations accessible to user"""
        return await self.call_tool("bioclin_get_user_orgs", {})

    async def switch_organization(self, org_id: str) -> Dict[str, Any]:
        """
        Switch to a different active organization

        Args:
            org_id: UUID of the organization to switch to

        Returns:
            Update result
        """
        return await self.call_tool(
            "bioclin_update_active_org",
            {"org_id": org_id}
        )


# ========== Example Usage ==========

async def example_basic_usage():
    """Example: Basic usage without OAuth"""

    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="Test"
    )

    async with client:
        # List available tools
        tools = await client.list_tools()
        print(f"Available tools: {len(tools)}")

        # Login to Bioclin
        login_result = await client.login_bioclin(
            "user@example.com",
            "password"
        )
        print(f"Login result: {login_result}")

        # Get user info
        user_info = await client.get_user_info()
        print(f"User: {user_info}")


async def example_with_oauth():
    """Example: Using OAuth authentication"""

    client = BioclinChatbotClient(
        mcpx_url="https://your-service.run.app",
        oauth_config={
            "token_url": "https://your-domain.us.auth0.com/oauth/token",
            "client_id": "your_client_id",
            "client_secret": "your_client_secret",
            "audience": "mcpx-bioclin"
        },
        consumer_tag="Chatbot"
    )

    async with client:
        # OAuth token is automatically obtained

        # Login to Bioclin
        await client.login_bioclin("user@example.com", "password")

        # Get analysis types
        analysis_types = await client.list_analysis_types()
        print(f"Analysis types: {analysis_types}")

        # Create a project
        project = await client.create_project(
            name="Test RNA-Seq",
            analysis_type_id="123e4567-e89b-12d3-a456-426614174000",
            description="Test project from chatbot"
        )
        print(f"Created project: {project}")


async def example_complete_workflow():
    """Example: Complete workflow from login to run creation"""

    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="Test"
    )

    async with client:
        # 1. Login
        await client.login_bioclin("user@example.com", "password")

        # 2. Get user context
        context = await client.get_user_context()
        print(f"User: {context['user']['username']}")
        print(f"Active org: {context['active_org']['name']}")

        # 3. List analysis types
        analysis_types = await client.list_analysis_types()
        first_type = analysis_types["data"][0]
        print(f"Using analysis type: {first_type['name']}")

        # 4. Create project
        project = await client.create_project(
            name="My RNA-Seq Project",
            analysis_type_id=first_type["id"],
            description="Automated project creation"
        )
        project_id = project["id"]
        print(f"Created project: {project_id}")

        # 5. Create run
        run = await client.create_run(
            name="Batch 001",
            project_id=project_id
        )
        print(f"Created run: {run['name']} with status {run['status']}")

        # 6. Check runs for project
        runs = await client.get_runs_by_project(project_id)
        print(f"Project has {runs['count']} runs")


if __name__ == "__main__":
    # Run examples
    print("Example 1: Basic Usage")
    asyncio.run(example_basic_usage())

    # Uncomment to run other examples:
    # asyncio.run(example_with_oauth())
    # asyncio.run(example_complete_workflow())
