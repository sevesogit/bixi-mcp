FROM python:3.12-slim

# Install uv
RUN pip install uv

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync

# Copy the entire project
COPY . .

# Set working directory for the server
WORKDIR /app/mcp_server

# Run the server
CMD ["uv", "run", "python", "server.py"]