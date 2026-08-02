#!/bin/bash
# Example harvest scripts for MIT Papers Harvester
# Customize these examples for your specific needs

# Configuration
MIT_DSPACE_URL="https://dspace.mit.edu"
OUTPUT_DIR="./harvest_output"
LOG_LEVEL="INFO"

echo "MIT Papers Harvester - Example Scripts"
echo "======================================"
echo ""

# Example 1: List all available collections
echo "[Example 1] Listing available collections..."
# python harvest_cli.py --url "$MIT_DSPACE_URL" --list-sets
echo "To list all collections, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --list-sets"
echo ""

# Example 2: Harvest all papers
echo "[Example 2] Harvesting all papers..."
echo "To harvest all papers, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --output $OUTPUT_DIR"
echo ""

# Example 3: Harvest papers from the last 30 days
echo "[Example 3] Harvesting recent papers (last 30 days)..."
echo "To harvest papers from the last 30 days, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --recent 30 --output $OUTPUT_DIR"
echo ""

# Example 4: Harvest papers from a specific collection
echo "[Example 4] Harvesting from specific collection..."
echo "To harvest from a specific collection (e.g., theses), run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --set 'com_1721.1_49604' --output $OUTPUT_DIR"
echo ""

# Example 5: Harvest papers from a date range
echo "[Example 5] Harvesting papers from a specific date range..."
echo "To harvest papers from 2024-01-01 to 2024-12-31, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --from 2024-01-01 --until 2024-12-31 --output $OUTPUT_DIR"
echo ""

# Example 6: Harvest and save as JSON only
echo "[Example 6] Harvesting and saving as JSON only..."
echo "To save as JSON format only, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --format json --output $OUTPUT_DIR"
echo ""

# Example 7: Harvest with debug logging
echo "[Example 7] Harvesting with debug logging..."
echo "To enable detailed logging, run:"
echo "  python harvest_cli.py --url $MIT_DSPACE_URL --log-level DEBUG --output $OUTPUT_DIR"
echo ""

# Example 8: Automated daily harvest
echo "[Example 8] Set up automated daily harvests..."
echo "Add this to your crontab (runs daily at 2 AM):"
echo "  0 2 * * * cd /path/to/harvester && python harvest_cli.py --url $MIT_DSPACE_URL --recent 1 >> harvest_cron.log 2>&1"
echo ""

# Example 9: Monthly harvest archive
echo "[Example 9] Create monthly harvest archives..."
echo "Example script:"
cat << 'EOF'
#!/bin/bash
MONTH=$(date +%Y-%m)
python harvest_cli.py \
  --url https://dspace.mit.edu \
  --from ${MONTH}-01 \
  --until ${MONTH}-31 \
  --output ./archives/monthly_${MONTH} \
  --format both
EOF
echo ""

# Example 10: Harvest multiple collections
echo "[Example 10] Harvest multiple collections..."
echo "Example script:"
cat << 'EOF'
#!/bin/bash
COLLECTIONS=("com_1721.1_49604" "com_1721.1_2015" "com_1721.1_3")
for COLLECTION in "${COLLECTIONS[@]}"; do
  echo "Harvesting collection: $COLLECTION"
  python harvest_cli.py \
    --url https://dspace.mit.edu \
    --set "$COLLECTION" \
    --output "./harvest_${COLLECTION}"
done
EOF
echo ""

echo "======================================"
echo "Note: Uncomment the actual python commands in this script to run them"
echo "Or copy them directly to your terminal"
echo ""
