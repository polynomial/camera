#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.pyftpdlib python3Packages.watchdog python3Packages.python-dotenv

# Simple FTP Server for Canon R3
set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FTP_SCRIPT="$SCRIPT_DIR/ftp_server.py"

# Load environment variables
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/../.env" | xargs)
fi

# Create upload directory
mkdir -p ~/camera/ftp_uploads

echo "Canon R3 FTP Upload Service"
echo "==========================="
echo ""
echo "Starting FTP server on port 2121..."
echo ""

# Run FTP server
python3 "$FTP_SCRIPT" 