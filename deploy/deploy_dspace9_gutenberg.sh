#!/bin/bash
# Deploy Gutenberg to DSpace 9 at repo.dare.co.zw
# DSpace 9 specific deployment script

set -e

echo "========================================"
echo "DSpace 9 Gutenberg Deployment"
echo "========================================"
echo ""

DSPACE_URL="https://repo.dare.co.zw"
DSPACE_VERSION="9.x"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Configuration:"
echo "  DSpace URL: $DSPACE_URL"
echo "  Version: $DSPACE_VERSION"
echo "  Repository: $REPO_DIR"
echo ""

# Step 1: Test DSpace connectivity
echo "Step 1: Testing DSpace 9 connectivity..."
if curl -s -I "$DSPACE_URL/server/api" | head -1 | grep -q "200\|301\|302"; then
    echo "✓ DSpace 9 API is accessible"
else
    echo "✗ Cannot reach DSpace 9 at $DSPACE_URL"
    exit 1
fi

# Step 2: Check Python and dependencies
echo ""
echo "Step 2: Checking Python dependencies..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "✗ Missing 'requests' module"
    echo "Install with: pip install requests"
    exit 1
fi
echo "✓ Python dependencies OK"

# Step 3: Verify data files
echo ""
echo "Step 3: Verifying Gutenberg data files..."
if [ ! -f "$REPO_DIR/gutenberg_data/gutenberg_books_latest.json" ]; then
    echo "✗ Missing: gutenberg_books_latest.json"
    exit 1
fi
echo "✓ Data files found"

# Step 4: Display instructions
echo ""
echo "========================================"
echo "DSpace 9 Ingest Instructions"
echo "========================================"
echo ""
echo "To ingest Gutenberg books into DSpace 9:"
echo ""
echo "1. Authenticate to DSpace 9:"
echo ""
echo "   curl -X POST $DSPACE_URL/server/api/authn/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"user\": \"admin@example.com\", \"password\": \"password\"}'"
echo ""
echo "   Copy the 'token' from response"
echo ""
echo "2. Export token:"
echo ""
echo "   export DSPACE_TOKEN='your_token_here'"
echo ""
echo "3. Find or create Gutenberg collection:"
echo ""
echo "   # List existing collections"
echo "   curl -s '$DSPACE_URL/server/api/core/collections' \\"
echo "     -H \"Authorization: Bearer \$DSPACE_TOKEN\" | jq '.[] | {name, handle}'"
echo ""
echo "4. Export collection handle:"
echo ""
echo "   export COLLECTION_HANDLE='123456789/10'"
echo ""
echo "5. Run ingest script:"
echo ""
echo "   python3 $REPO_DIR/deploy/dspace_gutenberg_ingest.py \\"
echo "     --url $DSPACE_URL \\"
echo "     --token \$DSPACE_TOKEN \\"
echo "     --collection \$COLLECTION_HANDLE \\"
echo "     --json $REPO_DIR/gutenberg_data/gutenberg_books_latest.json"
echo ""
echo "6. Monitor progress and verify in DSpace UI:"
echo ""
echo "   $DSPACE_URL/"
echo ""
echo "========================================"
echo ""
echo "ℹ️  For detailed DSpace 9 documentation:"
echo "   See: DSPACE_INGEST_GUIDE.md"
echo ""
echo "✓ All prerequisites met. Ready to ingest!"
echo ""
