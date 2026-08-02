#!/bin/bash
set -e

echo "🤖 rosersg Setup Script"
echo "========================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Setup environment
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env

    # Generate random API key
    API_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secure-api-key-here-change-in-production/$API_KEY/" .env
    echo "✓ Generated secure API key"
else
    echo "✓ .env file already exists"
fi

# Create UI directories
echo "📁 Setting up UI directories..."
mkdir -p ui/src
mkdir -p ui/public
echo "✓ UI directories created"

# Verify key files
echo "🔍 Verifying setup..."
files=(
    "rosersg.py"
    "rosersg-config.json"
    "requirements.txt"
    "Dockerfile"
    "docker-compose.yml"
    ".env"
    "ui/package.json"
    "ui/src/App.jsx"
    "ui/public/index.html"
    "ROSERSG.md"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "❌ Missing $file"
        exit 1
    fi
done

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Review configuration:"
echo "   cat .env"
echo ""
echo "2. Update .env with your settings (if needed)"
echo ""
echo "3. Start services with Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo "4. Wait for services to start (30-60 seconds)"
echo ""
echo "5. Access rosersg:"
echo "   Frontend:  http://localhost:3000"
echo "   API:       http://localhost:5000"
echo "   Ollama:    http://localhost:11434"
echo ""
echo "6. Test API health:"
echo "   curl http://localhost:5000/health"
echo ""
echo "📖 For more information, see ROSERSG.md"
echo ""
