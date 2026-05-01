# Stage 1: Builder
FROM python:3.12-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runner
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# Install runtime dependencies and upgrade system packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy installed python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Ensure session and logs directories exist
RUN mkdir -p sessions logs

# Run the application
CMD ["python", "main.py"]
