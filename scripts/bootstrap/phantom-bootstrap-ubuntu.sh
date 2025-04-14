#!/bin/bash
set -e

echo "🚀 Starting Phantom Ubuntu Bootstrap..."

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

echo "🔧 [1/10] Updating system packages..."
sudo apt update -y && sudo apt upgrade -y

echo "🐍 [2/10] Checking Python..."
if ! command_exists python3; then
    sudo apt install -y python3
fi
if ! command_exists pip; then
    sudo apt install -y python3-pip
fi
sudo apt install -y python3-venv

echo "📁 [3/10] Setting up virtual environment..."
if [ ! -d "phantom-env" ]; then
    python3 -m venv phantom-env
fi
source phantom-env/bin/activate

echo "🐳 [4/10] Installing Docker..."
if ! command_exists docker; then
    sudo apt install -y docker.io
    sudo systemctl enable docker
fi
sudo systemctl start docker

echo "🔐 [5/10] Fixing Docker permissions..."
sudo usermod -aG docker "$USER"
newgrp docker

echo "🧪 [6/10] Verifying Docker works..."
docker info > /dev/null 2>&1 && echo "✅ Docker is ready!" || echo "❌ Docker daemon not accessible"

echo "🧰 [7/10] Installing Azure CLI..."
if ! command_exists az; then
    curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

echo "🧰 [8/10] Installing Azure Developer CLI (azd)..."
if ! command_exists azd; then
    curl -fsSL https://aka.ms/install-azd.sh | bash
fi

echo "📚 [9/10] Installing Phantom Python dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "🧠 requirements.txt not found, generating..."
    echo "fastapi" > requirements.txt
    echo "uvicorn[standard]" >> requirements.txt
    echo "semantic-router[hybrid]" >> requirements.txt
    echo "python-dotenv" >> requirements.txt
    echo "websockets" >> requirements.txt
    echo "pydantic" >> requirements.txt
    echo "aiohttp" >> requirements.txt
fi
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ [10/10] Phantom Dev Environment setup complete!"
echo "👉 Activate environment: source phantom-env/bin/activate"
echo "👉 Deploy with: azd up"
echo "💡 If Docker permission errors persist, run: sudo chmod 666 /var/run/docker.sock"
