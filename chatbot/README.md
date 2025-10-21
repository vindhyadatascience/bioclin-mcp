# Bioclin Chatbot Client

**Build custom chatbots and applications that use Bioclin!**

## What is This?

This is a Python library that makes it super easy to build applications that interact with Bioclin through MCPX. Think of it as a "Bioclin SDK for Python."

**What can you build with it?**
- 🤖 Custom chatbots (using LangChain, OpenAI, etc.)
- 🌐 Web APIs (using FastAPI, Flask, etc.)
- 📊 Data analysis scripts
- 🔄 Automation workflows
- 💬 Conversational interfaces for Bioclin

**No MCP knowledge required!** This library handles all the complex MCP protocol stuff for you.

## Features

- ✅ **Super simple API** - Easy-to-use methods like `login_bioclin()` and `list_projects()`
- ✅ **OAuth support** - Built-in authentication for production use
- ✅ **Async/await** - Modern Python async patterns
- ✅ **Type hints** - Great IDE autocomplete and type checking
- ✅ **Session management** - Automatic cookie handling
- ✅ **Error handling** - Clear error messages and token refresh

## Installation

**Step 1:** Install dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install httpx  # That's it!
```

**Step 2:** Start MCPX (if not already running)

```bash
cd ..
./start-mcpx.sh
```

## Quick Start

### Your First Chatbot (5 minutes)

Create a file called `my_first_chatbot.py`:

```python
import asyncio
from bioclin_chatbot_client import BioclinChatbotClient

async def main():
    # Connect to your local MCPX
    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="MyChatbot"
    )

    async with client:
        # Login to Bioclin
        print("Logging in...")
        await client.login_bioclin(
            "your-email@example.com",
            "your-password"
        )

        # Get your user info
        user = await client.get_user_info()
        print(f"\nWelcome, {user['username']}!")

        # List your projects
        projects = await client.list_projects()
        print(f"\nYou have {projects['count']} projects:")

        for project in projects['data']:
            print(f"  • {project['name']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**
```bash
python my_first_chatbot.py
```

**Output:**
```
Logging in...

Welcome, researcher@lab.org!

You have 3 projects:
  • RNA-Seq Analysis
  • Cancer Genomics Study
  • COVID-19 Variants
```

**Congratulations!** You just built your first Bioclin chatbot! 🎉

## Available Methods

### 🔐 Authentication & User

| Method | What It Does |
|--------|--------------|
| `login_bioclin(username, password)` | Log in to Bioclin |
| `get_user_info()` | Get current user details |
| `get_user_context()` | Get user info with organizations |

### 📁 Projects

| Method | What It Does |
|--------|--------------|
| `list_projects()` | List all your projects |
| `create_project(name, analysis_type_id, ...)` | Create a new project |

### 🚀 Runs (Analyses)

| Method | What It Does |
|--------|--------------|
| `create_run(name, project_id)` | Start a new analysis run |
| `get_runs_by_project(project_id)` | Get all runs for a project |

### 🏢 Organizations

| Method | What It Does |
|--------|--------------|
| `list_organizations()` | List organizations you belong to |
| `switch_organization(org_id)` | Change your active organization |

### 🔬 Analysis Types

| Method | What It Does |
|--------|--------------|
| `list_analysis_types()` | Get available analysis types (RNA-Seq, etc.) |

### 🛠️ Low-Level (Advanced)

| Method | What It Does |
|--------|--------------|
| `list_tools()` | List all 44 available MCP tools |
| `call_tool(name, arguments)` | Call any MCP tool directly |

## Examples

### Example 1: Complete Workflow

This example shows a complete Bioclin workflow: login → list analysis types → create project → create run.

```python
import asyncio
from bioclin_chatbot_client import BioclinChatbotClient

async def run_complete_workflow():
    client = BioclinChatbotClient(
        mcpx_url="http://localhost:9000",
        consumer_tag="WorkflowBot"
    )

    async with client:
        # 1. Login
        print("Step 1: Logging in...")
        await client.login_bioclin("researcher@lab.org", "password")

        # 2. Get user context
        print("\nStep 2: Getting user context...")
        context = await client.get_user_context()
        print(f"  Working as: {context['user']['username']}")
        print(f"  Organization: {context['active_org']['name']}")

        # 3. List analysis types
        print("\nStep 3: Finding RNA-Seq analysis type...")
        types = await client.list_analysis_types()
        rna_seq = next(
            t for t in types["data"]
            if "RNA-Seq" in t["name"]
        )
        print(f"  Found: {rna_seq['name']}")

        # 4. Create project
        print("\nStep 4: Creating project...")
        project = await client.create_project(
            name="Patient Cohort Analysis",
            analysis_type_id=rna_seq["id"],
            description="Analysis of patient RNA samples"
        )
        print(f"  Created: {project['name']}")

        # 5. Create run
        print("\nStep 5: Creating analysis run...")
        run = await client.create_run(
            name="Batch 001",
            project_id=project["id"]
        )
        print(f"  Run created with status: {run['status']}")

        print("\n✅ Workflow complete!")
        return run

# Run it
asyncio.run(run_complete_workflow())
```

### Example 2: Using with Cloud Run (Production)

If you deployed MCPX to Google Cloud Run, use this setup:

```python
client = BioclinChatbotClient(
    mcpx_url="https://mcpx-bioclin-xxxxx-uc.a.run.app",  # Your Cloud Run URL
    oauth_config={
        "token_url": "https://your-app.us.auth0.com/oauth/token",
        "client_id": "your_auth0_client_id",
        "client_secret": "your_auth0_client_secret",
        "audience": "mcpx-bioclin"
    },
    consumer_tag="ProductionBot"
)

async with client:
    # OAuth token is automatically obtained and refreshed!
    await client.login_bioclin("user@example.com", "password")

    # Rest of your code...
    projects = await client.list_projects()
```

### Example 3: Integration with LangChain

Build an AI agent that can interact with Bioclin:

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain_anthropic import ChatAnthropic
from bioclin_chatbot_client import BioclinChatbotClient
import asyncio

# Initialize Bioclin client
bioclin_client = BioclinChatbotClient(mcpx_url="http://localhost:9000")

# Create LangChain tools
tools = [
    Tool(
        name="list_bioclin_projects",
        description="List all Bioclin projects for the current user",
        func=lambda _: asyncio.run(bioclin_client.list_projects())
    ),
    Tool(
        name="create_bioclin_project",
        description="Create a new Bioclin project. Input: JSON with 'name' and 'analysis_type_id'",
        func=lambda input_json: asyncio.run(
            bioclin_client.create_project(**eval(input_json))
        )
    ),
]

# Initialize Claude
llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Create agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Use the agent!
response = agent.run("Create a new RNA-Seq project called 'Test Analysis'")
print(response)
```

### Example 4: Web API with FastAPI

Build a REST API for Bioclin:

```python
from fastapi import FastAPI, Depends, HTTPException
from bioclin_chatbot_client import BioclinChatbotClient
from pydantic import BaseModel

app = FastAPI(title="Bioclin API")

# Request models
class LoginRequest(BaseModel):
    username: str
    password: str

class CreateProjectRequest(BaseModel):
    name: str
    analysis_type_id: str
    description: str = None

# Dependency: Get Bioclin client
async def get_bioclin_client():
    client = BioclinChatbotClient(mcpx_url="http://localhost:9000")
    async with client:
        yield client

# Endpoints
@app.post("/api/login")
async def login(
    request: LoginRequest,
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    """Login to Bioclin"""
    try:
        result = await client.login_bioclin(
            request.username,
            request.password
        )
        return {"message": "Login successful", "data": result}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/projects")
async def get_projects(
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    """Get all projects"""
    projects = await client.list_projects()
    return projects

@app.post("/api/projects")
async def create_project(
    request: CreateProjectRequest,
    client: BioclinChatbotClient = Depends(get_bioclin_client)
):
    """Create a new project"""
    project = await client.create_project(
        name=request.name,
        analysis_type_id=request.analysis_type_id,
        description=request.description
    )
    return {"message": "Project created", "data": project}

# Run with: uvicorn my_api:app --reload
```

## Error Handling

The client raises standard `httpx` exceptions:

```python
from httpx import HTTPStatusError

async with client:
    try:
        await client.login_bioclin("user@example.com", "wrong_password")
    except HTTPStatusError as e:
        if e.response.status_code == 401:
            print("❌ Invalid credentials")
        elif e.response.status_code == 403:
            print("❌ Access forbidden")
        elif e.response.status_code == 404:
            print("❌ Resource not found")
        else:
            print(f"❌ HTTP error: {e}")
```

## Configuration

### Using Environment Variables

For production, use environment variables for sensitive data:

```bash
# .env file
MCPX_URL=https://mcpx-bioclin-xxxxx-uc.a.run.app
AUTH0_TOKEN_URL=https://your-app.us.auth0.com/oauth/token
AUTH0_CLIENT_ID=your_client_id
AUTH0_CLIENT_SECRET=your_client_secret
AUTH0_AUDIENCE=mcpx-bioclin
```

Then in your code:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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

### Run the Built-in Examples

The client file includes test examples:

```bash
python bioclin_chatbot_client.py
```

### Run Tests

```bash
# From the parent directory
./tests/test-chatbot-client.py
```

## What's Next?

Now that you have the chatbot client:

1. 📖 **Read the examples above** - Pick one that matches your use case
2. 🛠️ **Build something!** - Try creating a simple automation script
3. 🚀 **Deploy to production** - Use the Cloud Run setup with OAuth
4. 🤖 **Integrate with AI** - Try the LangChain example
5. 🌐 **Build a web app** - Try the FastAPI example

## API Reference

For detailed API documentation, see the docstrings in `bioclin_chatbot_client.py`.

**Quick tip:** Your IDE (VS Code, PyCharm) will show you all available methods and their parameters with autocomplete!

## Need Help?

- 📖 **Full deployment guide:** `../MCPX-DEPLOYMENT.md`
- 🆘 **Troubleshooting:** `../TROUBLESHOOTING.md`
- 🧪 **Integration tests:** `../tests/README.md`

## License

Same as the parent Bioclin MCP project.
