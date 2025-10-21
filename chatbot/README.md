# Bioclin Chatbot Client

Python client library for integrating chatbots with the MCPX Bioclin gateway.

## Features

- ✅ OAuth 2.1 authentication support
- ✅ Async/await interface
- ✅ Type hints for better IDE support
- ✅ Session management
- ✅ Convenient wrapper methods for common Bioclin operations
- ✅ Error handling and token refresh

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage (No Auth)

```python
from bioclin_chatbot_client import BioclinChatbotClient

client = BioclinChatbotClient(
    mcpx_url="http://localhost:9000",
    consumer_tag="MyChatbot"
)

async with client:
    # Login to Bioclin
    await client.login_bioclin("user@example.com", "password")

    # Get user info
    user_info = await client.get_user_info()
    print(user_info)

    # List projects
    projects = await client.list_projects()
    print(projects)
```

### With OAuth Authentication

```python
client = BioclinChatbotClient(
    mcpx_url="https://your-service.run.app",
    oauth_config={
        "token_url": "https://your-domain.us.auth0.com/oauth/token",
        "client_id": "your_client_id",
        "client_secret": "your_client_secret",
        "audience": "mcpx-bioclin"
    },
    consumer_tag="MyChatbot"
)

async with client:
    # OAuth token is automatically obtained and refreshed

    await client.login_bioclin("user@example.com", "password")

    # Create a project
    project = await client.create_project(
        name="RNA-Seq Analysis",
        analysis_type_id="123e4567-e89b-12d3-a456-426614174000"
    )
```

## Available Methods

### Authentication & User Management

- `login_bioclin(username, password)` - Login to Bioclin API
- `get_user_info()` - Get current user info
- `get_user_context()` - Get user context with orgs

### Project Management

- `list_projects()` - List user's projects
- `create_project(name, analysis_type_id, ...)` - Create new project

### Run Management

- `create_run(name, project_id)` - Create new run
- `get_runs_by_project(project_id)` - Get runs for a project

### Organizations

- `list_organizations()` - List user's organizations
- `switch_organization(org_id)` - Switch active organization

### Analysis Types

- `list_analysis_types()` - List available analysis types

### Low-Level Methods

- `list_tools()` - List all available MCP tools
- `call_tool(name, arguments)` - Execute any MCP tool

## Examples

### Complete Workflow

```python
async def create_and_run_analysis():
    client = BioclinChatbotClient(mcpx_url="http://localhost:9000")

    async with client:
        # 1. Login
        await client.login_bioclin("researcher@lab.org", "password")

        # 2. Get user context
        context = await client.get_user_context()
        print(f"Working as: {context['user']['username']}")
        print(f"Organization: {context['active_org']['name']}")

        # 3. List analysis types
        types = await client.list_analysis_types()
        rna_seq_type = next(
            t for t in types["data"]
            if "RNA-Seq" in t["name"]
        )

        # 4. Create project
        project = await client.create_project(
            name="Patient Cohort Analysis",
            analysis_type_id=rna_seq_type["id"],
            description="Analysis of patient RNA samples"
        )

        # 5. Create and monitor run
        run = await client.create_run(
            name="Batch 001",
            project_id=project["id"]
        )

        print(f"Run created with status: {run['status']}")
        return run

# Run the workflow
import asyncio
asyncio.run(create_and_run_analysis())
```

### Integration with LangChain

```python
from langchain.tools import Tool
from bioclin_chatbot_client import BioclinChatbotClient

# Initialize client
client = BioclinChatbotClient(mcpx_url="http://localhost:9000")

# Create LangChain tools
tools = [
    Tool(
        name="list_bioclin_projects",
        description="List all Bioclin projects for the current user",
        func=lambda _: asyncio.run(client.list_projects())
    ),
    Tool(
        name="create_bioclin_project",
        description="Create a new Bioclin project. Input should be JSON with 'name' and 'analysis_type_id'",
        func=lambda input: asyncio.run(
            client.create_project(**eval(input))
        )
    ),
    # Add more tools as needed
]

# Use with LangChain agent
from langchain.agents import initialize_agent, AgentType
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Ask the agent to interact with Bioclin
response = agent.run(
    "Create a new RNA-Seq project called 'Test Analysis'"
)
```

### Integration with FastAPI

```python
from fastapi import FastAPI, Depends
from bioclin_chatbot_client import BioclinChatbotClient
from typing import Dict, Any

app = FastAPI()

# Dependency for client
async def get_bioclin_client():
    client = BioclinChatbotClient(
        mcpx_url="https://your-service.run.app",
        oauth_config={...}
    )
    async with client:
        yield client

@app.post("/login")
async def login(
    username: str,
    password: str,
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    result = await client.login_bioclin(username, password)
    return result

@app.get("/projects")
async def get_projects(
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    projects = await client.list_projects()
    return projects

@app.post("/projects")
async def create_project(
    name: str,
    analysis_type_id: str,
    description: str = None,
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    project = await client.create_project(
        name=name,
        analysis_type_id=analysis_type_id,
        description=description
    )
    return project
```

## Error Handling

The client raises standard `httpx` exceptions for HTTP errors:

```python
from httpx import HTTPStatusError

async with client:
    try:
        await client.login_bioclin("user@example.com", "wrong_password")
    except HTTPStatusError as e:
        if e.response.status_code == 401:
            print("Invalid credentials")
        elif e.response.status_code == 403:
            print("Access forbidden")
        else:
            print(f"HTTP error: {e}")
```

## Configuration

### Environment Variables

You can configure the client using environment variables:

```bash
export MCPX_URL="https://your-service.run.app"
export AUTH0_TOKEN_URL="https://your-domain.us.auth0.com/oauth/token"
export AUTH0_CLIENT_ID="your_client_id"
export AUTH0_CLIENT_SECRET="your_client_secret"
export AUTH0_AUDIENCE="mcpx-bioclin"
```

Then in your code:

```python
import os

client = BioclinChatbotClient(
    mcpx_url=os.getenv("MCPX_URL"),
    oauth_config={
        "token_url": os.getenv("AUTH0_TOKEN_URL"),
        "client_id": os.getenv("AUTH0_CLIENT_ID"),
        "client_secret": os.getenv("AUTH0_CLIENT_SECRET"),
        "audience": os.getenv("AUTH0_AUDIENCE")
    }
)
```

## Testing

Run the example scripts:

```bash
# Basic usage
python bioclin_chatbot_client.py

# Or run specific examples in the file
```

## API Reference

See docstrings in `bioclin_chatbot_client.py` for detailed API documentation.

## License

Same as the parent Bioclin MCP project.
