#!/bin/bash

##############################################################################
# rosersg Deployment Script for Live DSpace Instance
#
# This script deploys rosersg to a live DSpace server at dspace.dare.co.zw
# Prerequisites: Docker, Docker Compose, git
##############################################################################

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   rosersg Deployment to DSpace                            ║${NC}"
echo -e "${BLUE}║   Target: dspace.dare.co.zw                               ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Detect OS
OS="$(uname)"
if [[ "$OS" == "Darwin" ]]; then
    DOCKER_INSTALL_LINK="https://docs.docker.com/desktop/install/mac-install/"
elif [[ "$OS" == "Linux" ]]; then
    DOCKER_INSTALL_LINK="https://docs.docker.com/engine/install/"
else
    DOCKER_INSTALL_LINK="https://docs.docker.com/get-docker/"
fi

# Check prerequisites
echo -e "${YELLOW}✓ Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from: $DOCKER_INSTALL_LINK"
    exit 1
fi
echo -e "${GREEN}✓ Docker is installed${NC}"

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is installed${NC}"

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed${NC}"
    echo "Please install Git from: https://git-scm.com/download"
    exit 1
fi
echo -e "${GREEN}✓ Git is installed${NC}"

echo ""
echo -e "${YELLOW}✓ Checking network connectivity...${NC}"

# Check connectivity to DSpace
if curl -s -m 5 https://dspace.dare.co.zw/server/api > /dev/null 2>&1; then
    echo -e "${GREEN}✓ DSpace (https://dspace.dare.co.zw) is reachable${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Could not reach DSpace API${NC}"
    echo "  This might be due to:"
    echo "  - Network/firewall issues"
    echo "  - DSpace being offline"
    echo "  - SSL certificate issues"
    read -p "  Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${YELLOW}► Step 1: Clone/Update Repository${NC}"

REPO_DIR="/opt/rosersg"

if [ -d "$REPO_DIR" ]; then
    echo "  Repository exists at $REPO_DIR"
    read -p "  Update existing installation? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$REPO_DIR"
        git fetch origin
        git checkout claude/rosersg-ollama-dspace-ai-b9tvxu
        git pull origin claude/rosersg-ollama-dspace-ai-b9tvxu
    fi
else
    echo "  Creating directory: $REPO_DIR"
    sudo mkdir -p "$REPO_DIR"

    echo "  Cloning repository..."
    sudo git clone -b claude/rosersg-ollama-dspace-ai-b9tvxu \
        https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git \
        "$REPO_DIR"
fi

cd "$REPO_DIR"
echo -e "${GREEN}✓ Repository ready${NC}"

echo ""
echo -e "${YELLOW}► Step 2: Configure Environment${NC}"

if [ ! -f .env ]; then
    echo "  Creating .env from template..."
    cp .env.example .env

    # Generate secure API key
    API_KEY=$(openssl rand -hex 32)

    # Update .env
    sed -i.bak "s|DSPACE_ENDPOINT=.*|DSPACE_ENDPOINT=https://dspace.dare.co.zw|" .env
    sed -i.bak "s|ROSERSG_API_KEY=.*|ROSERSG_API_KEY=$API_KEY|" .env
    rm .env.bak 2>/dev/null || true

    echo -e "${GREEN}✓ Environment configured${NC}"
    echo "  API Key: $API_KEY"
    echo "  DSpace: https://dspace.dare.co.zw"
else
    echo "  .env file already exists"
    echo "  Current DSpace endpoint:"
    grep "DSPACE_ENDPOINT" .env

    read -p "  Update DSpace endpoint? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "  Enter DSpace URL [https://dspace.dare.co.zw]: " DSPACE_URL
        DSPACE_URL=${DSPACE_URL:-https://dspace.dare.co.zw}
        sed -i "s|DSPACE_ENDPOINT=.*|DSPACE_ENDPOINT=$DSPACE_URL|" .env
    fi
fi

echo ""
echo -e "${YELLOW}► Step 3: Update rosersg Configuration${NC}"

echo "  Updating rosersg-config.json..."
sed -i.bak 's|"endpoint": "https://dspace.dare.co.zw"|"endpoint": "https://dspace.dare.co.zw"|' \
    rosersg-config.json
rm rosersg-config.json.bak 2>/dev/null || true

echo -e "${GREEN}✓ Configuration complete${NC}"

echo ""
echo -e "${YELLOW}► Step 4: Build Docker Images${NC}"

echo "  Building rosersg API image..."
sudo docker build -t rosersg:latest .

echo -e "${GREEN}✓ Docker image built${NC}"

echo ""
echo -e "${YELLOW}► Step 5: Start Services${NC}"

echo "  Starting services with Docker Compose..."
sudo docker-compose up -d

echo "  Waiting for services to start (60 seconds)..."
sleep 60

echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo -e "${YELLOW}► Step 6: Verify Installation${NC}"

# Check API health
echo "  Testing API health..."
API_RESPONSE=$(curl -s http://localhost:5000/health)
if echo "$API_RESPONSE" | grep -q '"status":"healthy"'; then
    echo -e "${GREEN}✓ API is responding${NC}"
else
    echo -e "${YELLOW}⚠ API may not be ready yet${NC}"
fi

# Check DSpace connection
echo "  Testing DSpace connection..."
API_KEY=$(grep ROSERSG_API_KEY .env | cut -d= -f2)
DSPACE_RESPONSE=$(curl -s -H "X-API-Key: $API_KEY" \
    http://localhost:5000/api/dspace/health)

if echo "$DSPACE_RESPONSE" | grep -q '"online"'; then
    echo -e "${GREEN}✓ DSpace connection confirmed${NC}"
elif echo "$DSPACE_RESPONSE" | grep -q '"offline"'; then
    echo -e "${YELLOW}⚠ DSpace appears to be offline${NC}"
    echo "  Check that DSpace URL is correct in .env"
else
    echo -e "${YELLOW}⚠ Could not determine DSpace status${NC}"
fi

echo ""
echo -e "${YELLOW}► Step 7: Configure Nginx (Optional)${NC}"

read -p "Configure Nginx reverse proxy? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v nginx &> /dev/null; then
        echo "  Creating Nginx configuration..."

        # Backup existing config
        if [ -f /etc/nginx/sites-enabled/dspace ]; then
            sudo cp /etc/nginx/sites-enabled/dspace \
                /etc/nginx/sites-enabled/dspace.backup
            echo -e "${GREEN}✓ Backed up existing Nginx config${NC}"
        fi

        echo "  You should manually add the following to your Nginx config:"
        echo ""
        echo "  location /ai-api/ {"
        echo "      proxy_pass http://localhost:5000/;"
        echo "      proxy_set_header Host \$host;"
        echo "      proxy_set_header X-Real-IP \$remote_addr;"
        echo "  }"
        echo ""
        echo "  location /ai/ {"
        echo "      proxy_pass http://localhost:3000/;"
        echo "      proxy_set_header Host \$host;"
        echo "  }"
        echo ""
        echo "  Then run: sudo systemctl restart nginx"
    else
        echo "  Nginx not found. Manual configuration needed."
    fi
fi

echo ""
echo -e "${YELLOW}► Step 8: Setup Monitoring${NC}"

read -p "Setup log rotation and monitoring? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  Creating logrotate configuration..."

    sudo tee /etc/logrotate.d/rosersg > /dev/null <<EOF
$REPO_DIR/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root root
}
EOF

    echo -e "${GREEN}✓ Logrotate configured${NC}"
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           ✅ Installation Complete!                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo "📊 Service Status:"
sudo docker-compose ps

echo ""
echo "🚀 Access rosersg:"
echo "   Frontend:  http://localhost:3000"
echo "   API:       http://localhost:5000"
echo "   Ollama:    http://localhost:11434"
echo ""
echo "   (Use Nginx reverse proxy or SSH tunnel for remote access)"
echo ""

echo "🔑 Configuration:"
echo "   Location: $REPO_DIR"
echo "   Environment: $REPO_DIR/.env"
echo "   Config: $REPO_DIR/rosersg-config.json"
echo ""

echo "📖 Documentation:"
echo "   Main: $REPO_DIR/ROSERSG.md"
echo "   Integration: $REPO_DIR/DSPACE_INTEGRATION.md"
echo "   Quick Start: $REPO_DIR/QUICKSTART.md"
echo ""

echo "🔍 Useful Commands:"
echo "   View logs:      sudo docker-compose -f $REPO_DIR/docker-compose.yml logs -f rosersg-api"
echo "   Restart:        sudo docker-compose -f $REPO_DIR/docker-compose.yml restart"
echo "   Stop:           sudo docker-compose -f $REPO_DIR/docker-compose.yml down"
echo "   Test DSpace:    curl -H \"X-API-Key: \$(grep ROSERSG_API_KEY $REPO_DIR/.env | cut -d= -f2)\" http://localhost:5000/api/dspace/health"
echo ""

echo "✅ Next Steps:"
echo "   1. Test the installation at http://localhost:3000"
echo "   2. Configure Nginx if needed (see above)"
echo "   3. Review DSPACE_INTEGRATION.md for advanced setup"
echo "   4. Set up SSL/HTTPS for production"
echo "   5. Configure firewall rules"
echo ""

echo -e "${GREEN}Deployment complete! Enjoy rosersg with your DSpace! 🤖${NC}"
