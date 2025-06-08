#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.pyftpdlib python3Packages.watchdog python3Packages.python-dotenv

# Start FTP Server locally (no ngrok) for Canon R3
set -e

# Colors
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}Canon R3 FTP Upload Service (Local Mode)${NC}"
echo "=========================================="
echo ""
echo -e "${CYAN}This runs FTP server on your local network only.${NC}"
echo -e "${CYAN}Your Canon R3 must be on the same WiFi network.${NC}"
echo ""

# Get local IP address
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')

echo -e "${CYAN}Configure your Canon R3 with these settings:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "FTP Server: ${YELLOW}$LOCAL_IP${NC}"
echo -e "Port:       ${YELLOW}2121${NC}"
echo -e "Username:   ${YELLOW}admin${NC}"
echo -e "Password:   ${YELLOW}[Your password from .env]${NC}"
echo -e "Directory:  ${YELLOW}/${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Run the FTP server
exec python3 "$SCRIPT_DIR/ftp_server.py" 