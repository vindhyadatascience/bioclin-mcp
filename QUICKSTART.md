# Bioclin MCP Server - Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies

```bash
cd /Users/alex/VindhyaProjects/bioclin-mcp
pip install -r requirements.txt
```

### Step 2: Configure Environment

Set your Bioclin API URL (optional, defaults to http://localhost:8000):

```bash
export BIOCLIN_API_URL="https://your-bioclin-instance.com"
```

### Step 3: Test the Server

Run a quick test:

```bash
python bioclin_mcp_server.py
```

The server should start without errors. Press Ctrl+C to stop.

## Using with Claude Desktop

### Step 1: Locate Claude Config

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

### Step 2: Add Bioclin MCP Server

Edit the config file and add:

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "python",
      "args": ["/Users/alex/VindhyaProjects/bioclin-mcp/bioclin_mcp_server.py"],
      "env": {
        "BIOCLIN_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

**Important**: Replace `/Users/alex/VindhyaProjects/bioclin-mcp/bioclin_mcp_server.py` with the absolute path to your installation.

### Step 3: Restart Claude Desktop

Completely quit and restart Claude Desktop for changes to take effect.

### Step 4: Verify Installation

In Claude Desktop, ask:

```
Can you list the available Bioclin tools?
```

Claude should respond with a list of 44 available tools.

## First Steps

### 1. Login

```
Login to Bioclin with username "your-email@example.com" and password "yourpassword"
```

### 2. Check Your Profile

```
Show me my user information and context
```

### 3. List Your Projects

```
Show me all my projects
```

### 4. Create a Project

```
Create a project called "Test Project" with analysis type ID "..." and description "My test project"
```

### 5. Create a Run

```
Create a run called "Test Run 1" for project ID "..."
```

## Common Workflows

### Workflow 1: New Research Project

1. Login to Bioclin
2. Create or select an organization
3. List available analysis types
4. Create a project with appropriate parameters
5. Create a run for the project
6. Monitor run status

### Workflow 2: Organization Management

1. Login as admin
2. Create an organization
3. Invite users to the organization
4. Set user permissions
5. Create shared projects

### Workflow 3: Analysis Configuration

1. Create parameters for your analysis
2. Create an analysis type with Docker image reference
3. Associate parameters with the analysis type
4. Use the analysis type in projects

## Troubleshooting

### "Connection refused" error

- Check that BIOCLIN_API_URL is correct
- Verify the Bioclin API server is running
- Test the URL in your browser

### "Authentication failed" error

- Verify your username and password
- Check if your account is active
- Try the password recovery flow

### "Tool not found" error

- Restart Claude Desktop
- Verify the config file is valid JSON
- Check the absolute path to bioclin_mcp_server.py

### Claude doesn't see the tools

1. Check Claude Desktop config location
2. Verify JSON syntax (use a JSON validator)
3. Check file permissions on bioclin_mcp_server.py
4. Look at Claude Desktop logs for errors

## Getting Help

### Check Logs

Claude Desktop logs can be found at:
- **macOS**: `~/Library/Logs/Claude/`
- **Windows**: `%APPDATA%/Claude/logs/`

### Test Connection Manually

```bash
# Test API endpoint
curl http://localhost:8000/

# Test login
curl -X POST http://localhost:8000/api/v1/identity/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your-email@example.com&password=yourpassword&grant_type=password"
```

### Enable Debug Logging

Edit `bioclin_mcp_server.py` and change:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. Read the full [README.md](README.md) for comprehensive documentation
2. Explore all 44 available tools
3. Review [bioclin_schemas.py](bioclin_schemas.py) for data structures
4. Check the Bioclin API docs at your instance's `/docs` endpoint

## Example Conversations

### Example 1: Project Setup

```
You: Login with username "researcher@example.com" and password "mypass123"
Claude: [Logs in successfully]

You: What organizations am I part of?
Claude: [Shows organization list]

You: Create a new project called "RNA-Seq Batch 5" using the RNA-Seq analysis type
Claude: [Creates project and returns project details]

You: Start a run for this project called "Samples 1-10"
Claude: [Creates run and shows run details]
```

### Example 2: Admin Tasks

```
You: Login as admin
Claude: [Logs in]

You: Show me all users
Claude: [Lists all users]

You: Create a new admin user with email "new-admin@example.com"
Claude: [Creates admin user]

You: Add user "researcher@example.com" to organization "Research Lab"
Claude: [Adds user to organization]
```

### Example 3: Results Access

```
You: What runs do I have for project "..."?
Claude: [Lists runs]

You: Generate a signed URL for the results file in bucket "bioclin-results" at path "run-123/results.html"
Claude: [Generates signed URL]

You: Get the HTML report from that bucket and path
Claude: [Retrieves and displays report]
```

## Tips for Best Results

1. **Always login first** before trying authenticated operations
2. **Use specific UUIDs** when referencing projects, runs, organizations
3. **Check run status** before accessing results
4. **Create parameters** before creating analysis types
5. **Set active organization** before creating projects

## Security Notes

- Never commit credentials to version control
- Use environment variables for sensitive configuration
- Rotate passwords regularly
- Review user permissions periodically
- Use HTTPS in production (set BIOCLIN_API_URL to https://...)

## Performance Tips

- Use pagination (skip/limit) for large lists
- Cache frequently accessed data (analysis types, parameters)
- Batch related operations in single conversations
- Use specific queries instead of listing everything

---

**Ready to start? Try: "Login to Bioclin and show me my user context"**
