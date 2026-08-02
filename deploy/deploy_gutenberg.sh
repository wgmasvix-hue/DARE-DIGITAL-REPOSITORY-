#!/bin/bash
# Deploy Gutenberg dataset to DARE server
# Usage: ./deploy_gutenberg.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "========================================"
echo "DARE Gutenberg Deployment"
echo "========================================"
echo "Environment: $ENVIRONMENT"
echo "Repository: $REPO_DIR"
echo "Timestamp: $TIMESTAMP"
echo ""

# Configuration
case $ENVIRONMENT in
    production)
        SERVER="dspace.dare.co.zw"
        DEPLOY_USER="dspace"
        DEPLOY_PATH="/opt/dspace/data/gutenberg"
        API_URL="https://dspace.dare.co.zw"
        ;;
    staging)
        SERVER="staging.dare.co.zw"
        DEPLOY_USER="dspace"
        DEPLOY_PATH="/opt/dspace/data/gutenberg"
        API_URL="https://staging.dare.co.zw"
        ;;
    *)
        echo "Usage: $0 [production|staging]"
        exit 1
        ;;
esac

echo "Deployment Configuration:"
echo "  Server: $SERVER"
echo "  User: $DEPLOY_USER"
echo "  Path: $DEPLOY_PATH"
echo "  API: $API_URL"
echo ""

# Step 1: Check SSH connectivity
echo "Step 1: Verifying SSH connectivity to $SERVER..."
if ssh -o ConnectTimeout=5 "$DEPLOY_USER@$SERVER" "echo 'SSH OK'" >/dev/null 2>&1; then
    echo "✓ SSH connection successful"
else
    echo "✗ Cannot connect to $SERVER"
    exit 1
fi

# Step 2: Prepare deployment package
echo ""
echo "Step 2: Preparing deployment package..."
DEPLOY_PACKAGE="/tmp/gutenberg_deploy_$TIMESTAMP.tar.gz"

# Create temporary directory
TEMP_DIR="/tmp/gutenberg_temp_$TIMESTAMP"
mkdir -p "$TEMP_DIR/gutenberg_data"

# Copy files
cp "$REPO_DIR/harvest_gutenberg.py" "$TEMP_DIR/"
cp "$REPO_DIR/GUTENBERG_DATASET.md" "$TEMP_DIR/"
cp -r "$REPO_DIR/gutenberg_data/"* "$TEMP_DIR/gutenberg_data/" 2>/dev/null || true

# Create deployment manifest
cat > "$TEMP_DIR/DEPLOYMENT.md" << EOF
# Gutenberg Deployment Manifest

**Deployment Date**: $TIMESTAMP
**Environment**: $ENVIRONMENT
**Repository**: $REPO_DIR

## Files Deployed
- harvest_gutenberg.py - Data harvester script
- GUTENBERG_DATASET.md - Documentation
- gutenberg_data/ - Sample data and configuration

## Post-Deployment Steps
1. Extract to $DEPLOY_PATH
2. Run setup script
3. Configure cron job for automated harvests
4. Test API endpoint

## Rollback
To rollback this deployment:
\`\`\`bash
rm -rf $DEPLOY_PATH
# Restore from backup
\`\`\`

EOF

# Create tarball
tar -czf "$DEPLOY_PACKAGE" -C /tmp "gutenberg_temp_$TIMESTAMP"
echo "✓ Package created: $DEPLOY_PACKAGE"

# Step 3: Upload to server
echo ""
echo "Step 3: Uploading to $SERVER..."
scp -r "$DEPLOY_PACKAGE" "$DEPLOY_USER@$SERVER:/tmp/"
echo "✓ Upload successful"

# Step 4: Extract and setup on server
echo ""
echo "Step 4: Setting up on server..."
ssh "$DEPLOY_USER@$SERVER" << 'EOSSH'
    # Variables
    DEPLOY_PATH="/opt/dspace/data/gutenberg"
    PACKAGE_FILE="/tmp/gutenberg_deploy_$TIMESTAMP.tar.gz"

    # Create directory structure
    sudo mkdir -p "$DEPLOY_PATH"
    sudo chown dspace:dspace "$DEPLOY_PATH"

    # Extract files
    tar -xzf "$PACKAGE_FILE" -C /tmp

    # Copy files to deployment location
    cp -r /tmp/gutenberg_temp_*/gutenberg_data/* "$DEPLOY_PATH/"
    cp /tmp/gutenberg_temp_*/harvest_gutenberg.py "$DEPLOY_PATH/"
    cp /tmp/gutenberg_temp_*/GUTENBERG_DATASET.md "$DEPLOY_PATH/"
    cp /tmp/gutenberg_temp_*/DEPLOYMENT.md "$DEPLOY_PATH/"

    # Set permissions
    chmod 755 "$DEPLOY_PATH/harvest_gutenberg.py"
    chmod 644 "$DEPLOY_PATH"/*.json "$DEPLOY_PATH"/*.csv "$DEPLOY_PATH"/*.md

    # Cleanup
    rm -rf /tmp/gutenberg_temp_*
    rm "$PACKAGE_FILE"

    echo "✓ Files deployed to $DEPLOY_PATH"
EOSSH

# Step 5: Verify deployment
echo ""
echo "Step 5: Verifying deployment..."
ssh "$DEPLOY_USER@$SERVER" "ls -lah $DEPLOY_PATH"

# Step 6: Create API endpoint
echo ""
echo "Step 6: Setting up API endpoints..."
ssh "$DEPLOY_USER@$SERVER" << 'EOSSH'
    # Create symlink for web access
    WEB_ROOT="/var/www/dspace/data"
    sudo mkdir -p "$WEB_ROOT"
    sudo ln -sf /opt/dspace/data/gutenberg "$WEB_ROOT/gutenberg" 2>/dev/null || true

    # Create JSON API endpoint
    mkdir -p "/opt/dspace/api/gutenberg"
    cat > "/opt/dspace/api/gutenberg/books.json" << 'EOF'
    {
      "status": "success",
      "data_url": "/data/gutenberg/gutenberg_books_latest.json",
      "csv_url": "/data/gutenberg/gutenberg_books_latest.csv",
      "documentation": "/data/gutenberg/GUTENBERG_DATASET.md",
      "sample_url": "/data/gutenberg/gutenberg_books_sample.json",
      "last_updated": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    }
EOF

    echo "✓ API endpoints created"
EOSSH

# Step 7: Setup cron job
echo ""
echo "Step 7: Setting up automated harvesting..."
ssh "$DEPLOY_USER@$SERVER" << 'EOSSH'
    # Create harvest script
    cat > "/opt/dspace/scripts/harvest_gutenberg_daily.sh" << 'EOF'
#!/bin/bash
cd /opt/dspace/data/gutenberg
python3 harvest_gutenberg.py >> /var/log/dspace/gutenberg_harvest.log 2>&1
EOF

    chmod 755 "/opt/dspace/scripts/harvest_gutenberg_daily.sh"

    # Add to crontab (run daily at 2 AM)
    (crontab -l 2>/dev/null | grep -v "harvest_gutenberg"; echo "0 2 * * * /opt/dspace/scripts/harvest_gutenberg_daily.sh") | crontab -

    echo "✓ Cron job configured (runs daily at 2:00 AM)"
EOSSH

# Step 8: Test endpoints
echo ""
echo "Step 8: Testing deployment..."
echo "Testing Gutenberg data endpoint:"
curl -s "$API_URL/data/gutenberg/gutenberg_books_sample.json" 2>/dev/null | head -20 || echo "Endpoint not yet available"

echo ""
echo "✓ API Endpoint: $API_URL/api/gutenberg/books.json"
echo "✓ JSON Data: $API_URL/data/gutenberg/gutenberg_books_latest.json"
echo "✓ CSV Data: $API_URL/data/gutenberg/gutenberg_books_latest.csv"

# Cleanup local files
rm -rf "$TEMP_DIR" "$DEPLOY_PACKAGE"

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Verify data is accessible at:"
echo "   $API_URL/data/gutenberg/"
echo ""
echo "2. Test API endpoint:"
echo "   curl $API_URL/api/gutenberg/books.json"
echo ""
echo "3. Monitor harvest logs:"
echo "   ssh $DEPLOY_USER@$SERVER tail -f /var/log/dspace/gutenberg_harvest.log"
echo ""
echo "4. To manually trigger harvest:"
echo "   ssh $DEPLOY_USER@$SERVER /opt/dspace/scripts/harvest_gutenberg_daily.sh"
echo ""
