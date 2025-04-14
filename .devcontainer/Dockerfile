# .devcontainer/Dockerfile
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    libffi-dev \
    libpq-dev \
    docker.io \
    azure-cli \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install azd (Azure Developer CLI)
RUN curl -fsSL https://aka.ms/install-azd.sh | bash

# Install Node.js (needed for frontend & telemetry)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# Set workdir and create venv
WORKDIR /workspace
