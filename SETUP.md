# Bioclin MCP Server Setup for Claude Desktop

This MCP server allows Claude Desktop to interact with the Bioclin API.

## Prerequisites

1. Docker installed and running
2. Claude Desktop installed
3. Bioclin API credentials (email and password)

## Setup Instructions

### 1. Build the Docker Image

First, ensure you're in the project directory and build the Docker image:

```bash
docker build -t bioclin-mcp:latest .
```

### 2. Configure Claude Desktop

Claude Desktop needs to be configured to use this MCP server. The configuration file location varies by OS:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the following to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

**Note**: If you already have other MCP servers configured, add the "bioclin" entry to the existing "mcpServers" object.

### 3. Restart Claude Desktop

After updating the configuration:
1. Quit Claude Desktop completely
2. Restart Claude Desktop
3. The Bioclin MCP server should now be available

## Verifying the Setup

Once Claude Desktop restarts, you should see the Bioclin tools available. You can test it by asking Claude:

- "What are my Bioclin projects?"
- "Show me my user information from Bioclin"
- "List analysis types available in Bioclin"

## Available Tools

The server provides these tools:
- `read_user_projects` - Get all projects for the current user
- `read_runs` - Get all runs across all projects
- `read_runs_by_project` - Get runs for a specific project
- `create_run` - Create a new run for a project
- `read_user_me` - Get current user information
- `read_analysis_types` - Get all available analysis types

## Troubleshooting

### Server not appearing in Claude Desktop
1. Check that the Docker image is built: `docker images | grep bioclin-mcp`
2. Verify the config file path is correct for your OS
3. Check the JSON syntax is valid (no trailing commas, proper quotes)
4. Restart Claude Desktop completely

### Authentication errors
1. Verify your credentials in the `.env` file
2. Ensure the `.env` file is in the project directory when building
3. Rebuild the Docker image: `docker build -t bioclin-mcp:latest .`

### Docker errors
1. Make sure Docker Desktop is running
2. Test the container manually: `docker run bioclin-mcp:latest`
3. Check Docker has permission to run

## Security Notes

- The `.env` file containing your credentials is copied into the Docker image
- Keep the Docker image private and don't push it to public registries
- Consider using Docker secrets or environment variable passing for production use

## Updating

To update the server after making changes:

1. Rebuild the Docker image:
   ```bash
   docker build -t bioclin-mcp:latest .
   ```

2. Restart Claude Desktop

No configuration changes needed unless you change the server name.
