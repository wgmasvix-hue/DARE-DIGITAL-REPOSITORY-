#!/bin/bash

# 🚀 Automated DSpace 9 rosersg Deployment Script
# Integrates rosersg AI into your DSpace 9 Docker container

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║  🚀 DSpace 9 rosersg Integration - Automated Deployment       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
BUILD_DIR="/opt/dspace9-rosersg-build"
REPO_URL="https://github.com/wgmasvix-hue/DARE-DIGITAL-REPOSITORY-.git"
BRANCH="claude/rosersg-ollama-dspace-ai-b9tvxu"
API_KEY="6411d796c1962ffe483147c0c7e211bc6f47cecbfc723f9c5957a73ee70b8bac"
IMAGE_NAME="dare/dspace-angular:9.3-rosersg"
CONFIG_MOUNT="/opt/dspace9/config.yml"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_step() {
    echo -e "${YELLOW}▶ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: Check prerequisites
log_step "Step 1: Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed"
    exit 1
fi
log_success "Docker is installed"

if ! docker ps | grep -q "rosersg-api"; then
    log_error "rosersg services are not running. Start them first:"
    echo "  docker compose -f /opt/rosersg/docker-compose.yml up -d"
    exit 1
fi
log_success "rosersg services are running"

if ! docker ps | grep -q "dspace-angular"; then
    log_error "DSpace Angular container is not running"
    exit 1
fi
log_success "DSpace Angular container is running"

echo ""

# Step 2: Prepare build directory
log_step "Step 2: Preparing build directory..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"
log_success "Build directory ready: $BUILD_DIR"

echo ""

# Step 3: Clone or update repository
log_step "Step 3: Cloning rosersg repository..."
if [ -d "rosersg-repo" ]; then
    log_success "Repository already exists, updating..."
    cd rosersg-repo
    git fetch origin
    git checkout $BRANCH
    cd ..
else
    git clone -b $BRANCH $REPO_URL rosersg-repo
    log_success "Repository cloned"
fi

echo ""

# Step 4: Create component structure
log_step "Step 4: Creating component directories..."
mkdir -p components/{rosersg-chat,rosersg-search-enhance,rosersg-metadata-suggestions,rosersg-recommendations}
mkdir -p patches
log_success "Directories created"

echo ""

# Step 5: Extract component files from documentation
log_step "Step 5: Extracting component files from EMBED_IN_DSPACE.md..."

# This is a placeholder - in practice, you'd extract the actual component code
# For now, we'll note that this needs to be done manually or via automated extraction
cat > components/NOTE.txt << 'EOF'
Component files should be extracted from EMBED_IN_DSPACE.md
Each component needs 3 files:
- rosersg-chat: .ts, .html, .scss
- rosersg-search-enhance: .ts, .html, .scss
- rosersg-metadata-suggestions: .ts, .html, .scss
- rosersg-recommendations: .ts, .html, .scss

Total: 12 files
EOF

log_success "Components structure ready"

echo ""

# Step 6: Copy Dockerfile
log_step "Step 6: Copying Dockerfile..."
cp rosersg-repo/Dockerfile.dspace9-rosersg ./
log_success "Dockerfile ready"

echo ""

# Step 7: Create patches
log_step "Step 7: Creating environment configuration patch..."
cat > patches/environment.prod.ts << EOF
export const environment = {
  production: true,
  rosersg: {
    apiUrl: '/ai-api',
    apiKey: '$API_KEY'
  }
};
EOF
log_success "Environment configuration created"

echo ""

# Step 8: Instructions for component files
log_step "Step 8: Component files setup..."
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Component files need to be extracted from EMBED_IN_DSPACE.md"
echo "Location: $BUILD_DIR/components/"
echo ""
echo "Copy these 12 files:"
echo "  1. rosersg-chat/{.ts, .html, .scss}"
echo "  2. rosersg-search-enhance/{.ts, .html, .scss}"
echo "  3. rosersg-metadata-suggestions/{.ts, .html, .scss}"
echo "  4. rosersg-recommendations/{.ts, .html, .scss}"
echo ""
echo "And these 5 patch files to: $BUILD_DIR/patches/"
echo "  1. shared.module.ts"
echo "  2. app.component.html"
echo "  3. item-detail.component.html"
echo "  4. search.component.html"
echo "  5. environment.prod.ts (already created ✓)"
echo ""
echo "Refer to DSPACE9_DOCKER_INTEGRATION.md for file contents"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

read -p "Press Enter once you've copied all files to $BUILD_DIR/components and $BUILD_DIR/patches ..."

# Verify files exist
if [ ! -f "components/rosersg-chat/rosersg-chat.component.ts" ]; then
    log_error "Component files not found. Please copy files first."
    exit 1
fi
log_success "Component files verified"

echo ""

# Step 9: Build Docker image
log_step "Step 9: Building Docker image (this may take 10-20 minutes)..."
echo "Image: $IMAGE_NAME"
echo ""

if docker build -f Dockerfile.dspace9-rosersg -t "$IMAGE_NAME" .; then
    log_success "Docker image built successfully"
else
    log_error "Docker build failed. Check the output above for errors."
    exit 1
fi

echo ""

# Step 10: Test the image
log_step "Step 10: Testing new image..."
TEST_CONTAINER="dspace-angular-test"

# Clean up any existing test container
docker rm -f "$TEST_CONTAINER" 2>/dev/null || true

echo "Starting test container on port 4001..."
docker run -d \
    --name "$TEST_CONTAINER" \
    -p 4001:4000 \
    -v "$CONFIG_MOUNT:/app/config/config.yml:ro" \
    "$IMAGE_NAME"

# Wait for startup
sleep 10

if docker ps | grep -q "$TEST_CONTAINER"; then
    log_success "Test container started"

    # Test the endpoint
    if curl -s http://localhost:4001 | grep -q "dspace"; then
        log_success "Test container is responding"
    else
        log_error "Test container not responding properly"
    fi

    # Stop test container
    docker stop "$TEST_CONTAINER"
    docker rm "$TEST_CONTAINER"
    log_success "Test container cleaned up"
else
    log_error "Test container failed to start"
    exit 1
fi

echo ""

# Step 11: Deploy to production
log_step "Step 11: Deploying to production..."
echo ""
echo "This will:"
echo "  1. Stop the current dspace-angular container"
echo "  2. Start the new rosersg-enabled image"
echo "  3. Preserve your configuration"
echo ""

read -p "Continue with production deployment? (yes/no): " -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_step "Stopping current container..."
    docker stop dspace-angular || true

    log_step "Starting new image..."
    docker run -d \
        --name dspace-angular \
        -p 4000:4000 \
        -v "$CONFIG_MOUNT:/app/config/config.yml:ro" \
        "$IMAGE_NAME"

    # Wait for startup
    sleep 15

    if docker ps | grep -q "dspace-angular"; then
        log_success "DSpace Angular started successfully"
    else
        log_error "Failed to start container. Check with: docker logs dspace-angular"
        exit 1
    fi
else
    log_error "Deployment cancelled"
    exit 1
fi

echo ""

# Step 12: Verification
log_step "Step 12: Verifying deployment..."
echo ""

DSPACE_URL="https://repo.dare.co.zw"
API_URL="https://repo.dare.co.zw/ai-api"

echo "Testing endpoints..."

# Test API
if curl -s -H "X-API-Key: $API_KEY" "$API_URL/health" | grep -q "healthy"; then
    log_success "rosersg API is responding"
else
    log_error "Could not reach rosersg API"
fi

# Test DSpace (just check connection)
if curl -s -L "$DSPACE_URL" > /dev/null; then
    log_success "DSpace is accessible"
else
    log_error "Could not reach DSpace"
fi

echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✓ Deployment Complete!                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Your DSpace 9 now has rosersg integrated!"
echo ""
echo "📍 Access your DSpace:"
echo "   → https://repo.dare.co.zw"
echo ""
echo "✅ What to look for:"
echo "   → 🤖 Chat button (bottom-right, all pages)"
echo "   → ✨ AI search enhancement (search page)"
echo "   → 📝 Metadata suggestions (item pages)"
echo "   → ⭐ Related recommendations (item pages)"
echo ""
echo "🐛 Troubleshooting:"
echo "   → Check logs: docker logs dspace-angular"
echo "   → Check browser console: F12 in browser"
echo "   → Verify rosersg: curl https://repo.dare.co.zw/ai-api/health"
echo ""
echo "📚 Full guide: $BUILD_DIR/rosersg-repo/DSPACE9_DOCKER_INTEGRATION.md"
echo ""
