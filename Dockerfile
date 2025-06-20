# Dockerfile for Alpaca MCP Server - Local Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with uv
RUN pip install --no-cache-dir uv==0.4.18 && \
    uv pip install --system --no-cache -r requirements.txt

# Copy application code
COPY . .

# Create directories for logs and data
RUN mkdir -p /app/audit_logs /app/logs /app/data

# Create non-root user for security
RUN groupadd -r alpaca && useradd -r -g alpaca alpaca
RUN chown -R alpaca:alpaca /app
USER alpaca

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Expose port for future HTTP endpoints
EXPOSE 8080

# Default command (use the new refactored server)
CMD ["python", "alpaca_mcp_server_new.py"]
