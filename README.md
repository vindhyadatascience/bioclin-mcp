# Bioclin MCP Server

A Model Context Protocol (MCP) server for the Bioclin API, providing comprehensive access to bioinformatics workflow management through Claude and other MCP clients.

## Features

This MCP server provides access to all Bioclin API functionality including:

### Authentication & User Management
- Login/logout with session management
- Token validation and refresh
- User creation and management
- Password recovery and reset
- Admin user operations

### Organization Management
- Create and manage organizations
- User-organization relationships
- Switch active organizations
- Organization permissions

### Project Management
- Create and manage analysis projects
- Configure project parameters
- Link projects to analysis types
- Track project runs

### Run Management
- Create and monitor analysis runs
- Track run status (PENDING, LAUNCHING, QUEUED, SCHEDULED, RUNNING, SUCCEEDED, FAILED)
- View run results
- Manage run parameters

### Analysis Types & Parameters
- Define reusable analysis types
- Configure analysis parameters
- Version management for analysis types
- Link parameters to Docker images

### Google Cloud Storage Integration
- Generate signed URLs for file access
- Download analysis results
- Access HTML reports
- Secure file sharing

## Installation

### Option 1: Docker (Recommended for Portability)

The easiest way to run the Bioclin MCP Server is using Docker, which handles all dependencies automatically.

**Quick Start with Docker:**
```bash
# Build the image
docker build -t bioclin-mcp:latest .

# Run the container
docker run -it --rm \
  -e BIOCLIN_API_URL="https://bioclin.vindhyadatascience.com/api/v1" \
  bioclin-mcp:latest
```

**Or use Docker Compose:**
```bash
# Set your API URL
export BIOCLIN_API_URL="https://bioclin.vindhyadatascience.com/api/v1"

# Start the server
docker-compose up -d
```

For detailed Docker instructions, see [DOCKER.md](DOCKER.md)

### Option 2: Local Python Installation

1. Clone this repository or copy the files to your project directory:

```bash
cd /path/to/your/project
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Set the Bioclin API base URL (optional, defaults to https://bioclin.vindhyadatascience.com/api/v1):

```bash
export BIOCLIN_API_URL="https://your-bioclin-instance.com/api/v1"
```

## Running the Server

### As a Standalone Server (Python)

```bash
python bioclin_mcp_server.py
```

### As a Docker Container

```bash
docker run -it --rm \
  -e BIOCLIN_API_URL="https://bioclin.vindhyadatascience.com/api/v1" \
  bioclin-mcp:latest
```

See [DOCKER.md](DOCKER.md) for more Docker options.

### With Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### Using Python (Local Installation):
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "python",
      "args": ["/path/to/bioclin-mcp/bioclin_mcp_server.py"],
      "env": {
        "BIOCLIN_API_URL": "https://bioclin.vindhyadatascience.com/api/v1"
      }
    }
  }
}
```

#### Using Docker (Recommended):
```json
{
  "mcpServers": {
    "bioclin": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1",
        "bioclin-mcp:latest"
      ]
    }
  }
}
```

### With Other MCP Clients

The server uses stdio transport and can be integrated with any MCP-compatible client.

## Available Tools

### Authentication (4 tools)
- `bioclin_login` - Login with username/password
- `bioclin_logout` - Logout and clear session
- `bioclin_validate_token` - Validate current token
- `bioclin_refresh_token` - Refresh access token

### User Management (11 tools)
- `bioclin_create_user` - Create new user
- `bioclin_create_admin` - Create admin user
- `bioclin_get_users` - List all users (admin)
- `bioclin_get_user_me` - Get current user info
- `bioclin_get_user_context` - Get user context with orgs
- `bioclin_update_user_me` - Update current user
- `bioclin_set_user_admin` - Set admin status (admin)
- `bioclin_set_user_active` - Set active status (admin)
- `bioclin_recover_password` - Send recovery email
- `bioclin_reset_password` - Reset password with token
- `bioclin_delete_user` - Delete user (admin)

### Organization Management (6 tools)
- `bioclin_create_org` - Create organization
- `bioclin_get_orgs` - List all organizations
- `bioclin_get_org` - Get organization by ID
- `bioclin_get_user_orgs` - Get user's organizations
- `bioclin_update_active_org` - Switch active org
- `bioclin_add_user_to_org` - Add user to org

### Permission Management (2 tools)
- `bioclin_get_roles` - Get all roles
- `bioclin_get_permissions` - Get all permissions

### Parameter Management (4 tools)
- `bioclin_create_param` - Create parameter
- `bioclin_get_params` - List parameters
- `bioclin_update_param` - Update parameter
- `bioclin_delete_param` - Delete parameter

### Analysis Type Management (4 tools)
- `bioclin_create_analysis_type` - Create analysis type
- `bioclin_get_analysis_types` - List analysis types
- `bioclin_update_analysis_type` - Update analysis type
- `bioclin_delete_analysis_type` - Delete analysis type

### Project Management (5 tools)
- `bioclin_create_project` - Create project
- `bioclin_get_projects` - List all projects
- `bioclin_get_user_projects` - List user's projects
- `bioclin_get_project` - Get project by ID
- `bioclin_delete_project` - Delete project

### Run Management (5 tools)
- `bioclin_create_run` - Create analysis run
- `bioclin_get_runs` - List all runs
- `bioclin_get_runs_by_project` - List runs by project
- `bioclin_get_runs_by_org` - List runs by organization
- `bioclin_delete_run` - Delete run

### Google Cloud Storage (3 tools)
- `bioclin_generate_signed_url` - Generate signed URL
- `bioclin_get_html_report` - Get HTML report
- `bioclin_download_file` - Download file

**Total: 44 tools**

## Usage Examples

### Example 1: Login and Get User Info

```
User: Login to Bioclin with username "researcher@example.com" and password "mypassword"

Claude: [Uses bioclin_login tool]

User: Show me my user information

Claude: [Uses bioclin_get_user_me tool]
```

### Example 2: Create and Run a Project

```
User: Create a new project called "RNA-Seq Analysis" using analysis type ID "123e4567-e89b-12d3-a456-426614174000"

Claude: [Uses bioclin_create_project tool]

User: Create a run for this project named "Sample Batch 1"

Claude: [Uses bioclin_create_run tool]

User: Check the status of all runs for this project

Claude: [Uses bioclin_get_runs_by_project tool]
```

### Example 3: Organization Management

```
User: Create an organization called "Research Lab" with description "Genomics research laboratory"

Claude: [Uses bioclin_create_org tool]

User: Add user "colleague@example.com" to this organization

Claude: [Uses bioclin_add_user_to_org tool]

User: Switch my active organization to this new one

Claude: [Uses bioclin_update_active_org tool]
```

### Example 4: Analysis Type Configuration

```
User: Create a parameter for "Read Length" with description "Length of sequencing reads"

Claude: [Uses bioclin_create_param tool]

User: Create an analysis type for "RNA-Seq" using this parameter

Claude: [Uses bioclin_create_analysis_type tool]
```

## Schema Documentation

All API schemas are defined in `bioclin_schemas.py` using Pydantic models. Key schemas include:

- **User Schemas**: UserCreate, UserPublic, UserPrivate
- **Organization Schemas**: OrgCreate, OrgPublic, OrgPrivate
- **Project Schemas**: ProjectCreate, ProjectPublic, ProjectParamCreate
- **Run Schemas**: RunCreate, Run, RunPrivate, RunStatus (enum)
- **Analysis Schemas**: AnalysisTypeCreate, AnalysisType, AnalysisTypePrivate
- **Parameter Schemas**: ParamCreate, Param, ParamUpdate

## Architecture

### Components

1. **bioclin_schemas.py** - Pydantic models for all API data structures
2. **bioclin_mcp_server.py** - Main MCP server implementation
   - `BioclinClient` - HTTP client with session management
   - `BioclinMCPServer` - MCP server with tool handlers

### Session Management

The server maintains:
- HTTP cookies for session persistence
- CSRF token handling for secure requests
- Automatic token refresh capabilities

### Error Handling

All tools return structured JSON responses with:
- Success data on 2xx responses
- Error messages with HTTP status codes on failures
- Detailed validation errors for invalid inputs

## Security Considerations

1. **Authentication**: All authenticated endpoints require valid session cookies
2. **CSRF Protection**: CSRF tokens are automatically managed
3. **Admin Operations**: Certain operations require admin privileges
4. **Password Security**: Minimum 8 characters enforced
5. **Session Management**: Secure cookie-based sessions

## Development

### File Structure

```
bioclin-mcp/
├── bioclin_schemas.py       # Pydantic schemas
├── bioclin_mcp_server.py    # MCP server implementation
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Adding New Tools

To add a new tool:

1. Add the tool definition in `list_tools()` handler
2. Add the request handler in `_handle_tool_call()` method
3. Update this README with the new tool documentation

### Testing

Test individual tools using an MCP client or by running:

```bash
# Set up environment
export BIOCLIN_API_URL="http://localhost:8000"

# Run the server
python bioclin_mcp_server.py
```

## Troubleshooting

### Connection Issues

- Verify `BIOCLIN_API_URL` is set correctly
- Check network connectivity to Bioclin API
- Verify API server is running

### Authentication Issues

- Ensure credentials are correct
- Check if session cookies are being persisted
- Verify CSRF token handling

### Tool Execution Errors

- Check tool input parameters match schema
- Verify user has required permissions
- Check API server logs for backend errors

## API Reference

For complete API documentation, refer to the OpenAPI specification at your Bioclin instance:
```
https://your-bioclin-instance.com/docs
```

## License

This MCP server implementation is provided as-is for use with the Bioclin API.

## Support

For issues specific to:
- **MCP Server**: Create an issue in this repository
- **Bioclin API**: Contact your Bioclin administrator
- **MCP Protocol**: See https://modelcontextprotocol.io

## Version History

- **1.1.0** (2025-10-23) - Automated Browser Authentication
  - ✨ Added automated browser-based authentication with Playwright
  - ✨ New `bioclin_browser_login_auto()` MCP tool
  - ✨ macOS Terminal.app integration for visible GUI
  - 🔒 Enhanced security - credentials never exposed to LLM
  - 🎯 Seamless Claude Desktop integration
  - 📝 Comprehensive authentication documentation

- **1.0.0** (2025-01-20) - Initial release
  - Full API coverage (44 tools)
  - Session management
  - CSRF protection
  - Comprehensive schema support
