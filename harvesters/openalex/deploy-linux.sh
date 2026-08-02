#!/bin/bash
# OpenAlex Harvester Deployment Script for Linux/Systemd

set -e

HARVESTER_DIR="/opt/dare/harvesters/openalex"
CONFIG_DIR="/etc/dare/harvester"
DATA_DIR="/var/lib/dare/harvester"
LOG_DIR="/var/log/dare/harvester"
USER="dare"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   OpenAlex Harvester - Linux Deployment Script               ║"
echo "╚════════════════════════════════════════════════════════════════╝"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root"
   exit 1
fi

echo "📦 Step 1: Creating system user..."
if ! id -u "$USER" >/dev/null 2>&1; then
    useradd -r -s /bin/false -d "$DATA_DIR" "$USER"
    echo "✓ User '$USER' created"
else
    echo "✓ User '$USER' already exists"
fi

echo ""
echo "📁 Step 2: Creating directories..."
mkdir -p "$HARVESTER_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$LOG_DIR"
echo "✓ Directories created"

echo ""
echo "📋 Step 3: Installing harvester..."
cp "$(dirname "$0")/openalex-harvester" "$HARVESTER_DIR/"
chmod 755 "$HARVESTER_DIR/openalex-harvester"
echo "✓ Harvester installed to $HARVESTER_DIR"

echo ""
echo "⚙️  Step 4: Installing configuration..."
cp "$(dirname "$0")/configs/config.yaml" "$CONFIG_DIR/"
chmod 640 "$CONFIG_DIR/config.yaml"
echo "✓ Configuration installed to $CONFIG_DIR"

echo ""
echo "🔧 Step 5: Installing systemd service..."
cp "$(dirname "$0")/systemd/openalex-harvester.service" /etc/systemd/system/
cp "$(dirname "$0")/systemd/openalex-harvester.timer" /etc/systemd/system/
cp "$(dirname "$0")/systemd/openalex-harvester.env" "$CONFIG_DIR/"
chmod 640 "$CONFIG_DIR/openalex-harvester.env"
echo "✓ Systemd files installed"

echo ""
echo "👤 Step 6: Setting ownership..."
chown -R "$USER:$USER" "$HARVESTER_DIR"
chown -R "$USER:$USER" "$CONFIG_DIR"
chown -R "$USER:$USER" "$DATA_DIR"
chown -R "$USER:$USER" "$LOG_DIR"
echo "✓ Ownership set to $USER:$USER"

echo ""
echo "🔄 Step 7: Enabling systemd service..."
systemctl daemon-reload
systemctl enable openalex-harvester.timer
echo "✓ Timer enabled (will start automatically on reboot)"

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                 ✅ DEPLOYMENT COMPLETE                        ║"
echo "╚════════════════════════════════════════════════════════════════╝"

echo ""
echo "📝 NEXT STEPS:"
echo "───────────────────────────────────────────────────────────────"
echo ""
echo "1. ⚙️  CONFIGURE:"
echo "   Edit the configuration file:"
echo "   $ sudo vi $CONFIG_DIR/config.yaml"
echo ""
echo "   Important settings:"
echo "   - openalex.email: Set your email for OpenAlex API"
echo "   - dspace.api_key: Set your DSpace 9 API key"
echo "   - dspace.url: Verify DSpace URL is correct"
echo ""
echo "2. 🧪 TEST:"
echo "   Test API connectivity:"
echo "   $ sudo -u $USER $HARVESTER_DIR/openalex-harvester -test-api"
echo ""
echo "   Test DSpace connection:"
echo "   $ sudo -u $USER $HARVESTER_DIR/openalex-harvester -test-dspace"
echo ""
echo "3. 🚀 RUN MANUAL HARVEST (optional):"
echo "   $ sudo -u $USER $HARVESTER_DIR/openalex-harvester -topic 'machine learning' -limit 10"
echo ""
echo "4. ⏰ START SCHEDULED HARVESTING:"
echo "   $ sudo systemctl start openalex-harvester.timer"
echo ""
echo "5. 📊 MONITOR:"
echo "   Check service status:"
echo "   $ sudo systemctl status openalex-harvester.timer"
echo ""
echo "   View logs:"
echo "   $ sudo journalctl -u openalex-harvester -f"
echo ""
echo "6. 📖 DOCUMENTATION:"
echo "   CLI Usage: $(dirname "$0")/CLI_USAGE.md"
echo "   Deployment: $(dirname "$0")/DEPLOYMENT.md"
echo "   README: $(dirname "$0")/README.md"
echo ""
echo "───────────────────────────────────────────────────────────────"
