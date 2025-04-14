#!/bin/bash
echo "🔧 Bootstrapping Phantom inside DevContainer..."
source /workspace/phantom-env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Phantom environment bootstrapped!"
