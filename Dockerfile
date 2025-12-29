# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy the project configuration
COPY pyproject.toml uv.lock ./

# Install dependencies
# We use --frozen to ensure we use the lockfile versions
RUN uv sync --frozen --no-cache

# Install Playwright Browsers and Deps
# We need to install system dependencies for Playwright
RUN uv run playwright install-deps
RUN uv run playwright install chromium

# Copy the source code
COPY . .

# Install the project itself
RUN uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Default command
CMD ["python", "-m", "src.main"]
