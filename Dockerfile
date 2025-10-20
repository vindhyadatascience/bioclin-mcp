# Multi-stage build for Bioclin MCP Server
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application files
COPY bioclin_schemas.py .
COPY bioclin_mcp_server.py .

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default environment variable for Bioclin API URL
ENV BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1

# Health check (optional - checks if Python can import the modules)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import bioclin_mcp_server; import bioclin_schemas" || exit 1

# Make the server executable
RUN chmod +x bioclin_mcp_server.py

# Run the MCP server
ENTRYPOINT ["python", "bioclin_mcp_server.py"]
