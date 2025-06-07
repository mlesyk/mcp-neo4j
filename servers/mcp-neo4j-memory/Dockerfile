# Build stage
FROM python:3.11-slim as builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY pyproject.toml README.md ./
RUN pip install --user hatchling && \
    pip install --user mcp>=0.10.0 neo4j>=5.26.0 fastapi>=0.104.0 "uvicorn[standard]>=0.24.0"

# Copy source and build package
COPY src/ ./src/
RUN pip install --user -e .

# Runtime stage
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/mcp/.local/bin:$PATH"

WORKDIR /app

# Create user
RUN useradd --create-home --shell /bin/bash mcp

# Copy installed packages from builder
COPY --from=builder --chown=mcp:mcp /root/.local /home/mcp/.local
COPY --from=builder --chown=mcp:mcp /app /app

USER mcp

EXPOSE 3001

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import mcp_neo4j_memory; print('OK')" || exit 1

CMD ["mcp-neo4j-memory", "--mode", "http"]
