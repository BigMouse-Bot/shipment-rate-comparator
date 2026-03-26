# setup_complete.sh
#!/bin/bash

echo "🚀 Setting up Shipment Rate Comparator..."

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing dependencies..."
pip install python-dotenv pandas tabulate colorama pydantic aiohttp requests

# Create necessary directories
mkdir -p agents utils tests

# Create __init__.py files
touch agents/__init__.py
touch utils/__init__.py
touch tests/__init__.py

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
TINYFISH_API_KEY=your_api_key_here
TINYFISH_API_URL=https://api.tinyfish.ai/v1
LOG_LEVEL=INFO
HEADLESS_MODE=false
TIMEOUT_SECONDS=30
MAX_RETRIES=3
EOF
    echo "⚠️  Please edit .env and add your TinyFish API key!"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your actual TinyFish API key"
echo "2. Run: python test_tinyfish.py"
echo "3. Run: python test_environment.py"
echo "4. Run: python main.py"