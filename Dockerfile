# Multi-stage build for Bioclin MCP Server with FastMCP
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies and Playwright system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Install Playwright browsers (Chromium for automated login)
RUN /root/.local/bin/playwright install --with-deps chromium

# Final stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies for Playwright
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy Playwright browsers from builder
COPY --from=builder /root/.cache /root/.cache

# Copy application files
COPY src/ /app/src/

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Default environment variable for Bioclin API URL
ENV BIOCLIN_API_URL=https://bioclin.vindhyadatascience.com/api/v1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, '/app'); import src.bioclin_fastmcp" || exit 1

# Run the FastMCP server
CMD ["fastmcp", "run", "src/bioclin_fastmcp.py"]
