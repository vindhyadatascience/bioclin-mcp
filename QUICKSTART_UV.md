# Quick Start with uv

This guide shows how to set up Bioclin MCP using [uv](https://docs.astral.sh/uv/), Astral's ultra-fast Python package manager.

## Why uv?

- ⚡ **10-100x faster** than pip
- 🔒 **Deterministic installs** with lock files
- 📦 **No virtualenv needed** - uv manages it automatically
- 🎯 **Drop-in replacement** for pip, pip-tools, and virtualenv
- 🦀 **Written in Rust** for maximum performance

## Installation

### 1. Install uv

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew:**
```bash
brew install uv
```

**WinGet:**
```bash
winget install --id=astral-sh.uv -e
```

### 2. Clone Repository

```bash
git clone https://github.com/vindhyadatascience/bioclin-mcp.git
cd bioclin-mcp
```

### 3. Install Dependencies

```bash
# uv automatically creates and manages a virtual environment
uv sync

# Install Playwright browser
uv run playwright install chromium
```

That's it! No manual virtualenv creation needed.

### 4. Authenticate

```bash
# Browser login (recommended)
uv run python src/bioclin_auth.py login

# Or CLI login
uv run python src/bioclin_auth.py login --cli
```

### 5. Run the Server

```bash
uv run fastmcp run src/bioclin_fastmcp.py
```

## Claude Desktop Configuration

Edit your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bioclin": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/bioclin-mcp",
        "run",
        "fastmcp",
        "run",
        "src/bioclin_fastmcp.py"
      ]
    }
  }
}
```

**Important:** Replace `/absolute/path/to/bioclin-mcp` with the actual path on your system.

## Common Commands

### Check Session Status
```bash
uv run python src/bioclin_auth.py status
```

### Logout
```bash
uv run python src/bioclin_auth.py logout
```

### Update Dependencies
```bash
uv sync --upgrade
```

### Add a New Package
```bash
uv add package-name
```

### Run Tests
```bash
uv run pytest
```

### Format Code
```bash
uv run ruff format .
```

### Lint Code
```bash
uv run ruff check .
```

## Project Structure

With uv, the project structure is:

```
bioclin-mcp/
├── pyproject.toml          # Project metadata & dependencies
├── uv.lock                 # Lock file (auto-generated)
├── .venv/                  # Virtual environment (auto-managed)
├── src/
│   ├── bioclin_fastmcp.py  # MCP server
│   ├── bioclin_auth.py     # Authentication
│   └── ...
└── ...
```

## Advantages Over pip/venv

| Feature | uv | pip + venv |
|---------|----|-----------|
| Speed | 10-100x faster | Baseline |
| Lock files | Built-in (`uv.lock`) | Requires pip-tools |
| Virtualenv | Automatic | Manual activation |
| Python install | Can install Python | Requires pre-install |
| Dependency resolution | Advanced resolver | Basic resolver |
| Cross-platform | Single tool | Multiple tools |

## Troubleshooting

### Command not found: uv

Make sure uv is in your PATH. The installer typically adds it to `~/.local/bin`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this to your `~/.bashrc` or `~/.zshrc` to make it permanent.

### Using a specific Python version

uv can install and manage Python versions:

```bash
# Install Python 3.11
uv python install 3.11

# Use it for this project
uv venv --python 3.11
```

### Lock file out of sync

If `uv.lock` is out of sync with `pyproject.toml`:

```bash
uv lock
```

### Clear cache

If you encounter weird issues:

```bash
uv cache clean
```

## Migrating from pip/venv

If you already have a virtualenv setup:

```bash
# Remove old virtualenv
rm -rf venv/

# Let uv take over
uv sync
```

Your `requirements.txt` is no longer needed - dependencies are in `pyproject.toml`.

## Learn More

- **uv Documentation:** https://docs.astral.sh/uv/
- **Why uv?** https://astral.sh/blog/uv
- **Migrating to uv:** https://docs.astral.sh/uv/guides/migration/

## Comparison with Other Methods

### Docker (Best for production/isolation)
- ✅ Complete isolation
- ✅ Consistent across systems
- ❌ Slower startup
- ❌ Larger footprint

### uv (Best for development)
- ✅ Extremely fast
- ✅ Great developer experience
- ✅ Easy dependency management
- ❌ Requires Python ecosystem

### Traditional pip/venv (Works everywhere)
- ✅ Universal compatibility
- ✅ Well-documented
- ❌ Slower
- ❌ Manual virtualenv management

## Next Steps

- [Main README](README.md)
- [Docker Quick Start](QUICKSTART_DOCKER.md)
- [Authentication Guide](docs/AUTHENTICATION.md)
- [Docker Authentication](docs/DOCKER_AUTH.md)
