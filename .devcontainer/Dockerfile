FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update && apt-get install -y \
    curl gnupg software-properties-common \
    ca-certificates git lsb-release unzip \
    wget docker.io docker-compose \
    python3 python3-pip python3-venv \
    nodejs npm && apt-get clean

SHELL ["/bin/bash", "-c"]

ENV VIRTUAL_ENV=/workspace/phantom-env
RUN python3 -m venv $VIRTUAL_ENV && \
    echo "source $VIRTUAL_ENV/bin/activate" >> ~/.bashrc

RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    curl -fsSL https://aka.ms/azd/install.sh | bash
