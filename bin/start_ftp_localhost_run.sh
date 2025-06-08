#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.pyftpdlib python3Packages.watchdog python3Packages.python-dotenv openssh

# Start FTP Server with localhost.run tunnel (no auth required!)
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FTP_SCRIPT="$SCRIPT_DIR/ftp_server.py"

# Load environment variables
if [ -f "$SCRIPT_DIR/../.env" ]; then
    export $(grep -v '^#' "$SCRIPT_DIR/../.env" | xargs)
fi

# Default FTP port
FTP_PORT="${FTP_PORT:-2121}"

echo -e "${BLUE}Canon R3 FTP Upload Service (localhost.run)${NC}"
echo "============================================"
echo -e "${CYAN}Using localhost.run - no authentication required!${NC}"
echo ""

# Create upload directory
mkdir -p ~/camera/ftp_uploads

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill FTP server
    if [ ! -z "$FTP_PID" ]; then
        kill $FTP_PID 2>/dev/null || true
    fi
    
    # Kill SSH tunnel
    if [ ! -z "$SSH_PID" ]; then
        kill $SSH_PID 2>/dev/null || true
    fi
    
    echo -e "${GREEN}Services stopped${NC}"
}

trap cleanup EXIT

# Start FTP server in background
echo -e "${CYAN}Starting FTP server on port $FTP_PORT...${NC}"
python3 "$FTP_SCRIPT" &
FTP_PID=$!

# Wait for FTP server to start
sleep 2

# Check if FTP server is running
if ! kill -0 $FTP_PID 2>/dev/null; then
    echo -e "${RED}FTP server failed to start${NC}"
    exit 1
fi

# Start localhost.run tunnel
echo -e "${CYAN}Starting localhost.run tunnel...${NC}"
echo -e "${YELLOW}When prompted, type 'yes' to accept the SSH fingerprint${NC}"
echo ""

# Create SSH tunnel and capture output
ssh -R 80:localhost:$FTP_PORT localhost.run 2>&1 | while read line; do
    # Look for the URL in the output
    if echo "$line" | grep -q "https://"; then
        URL=$(echo "$line" | grep -o 'https://[^ ]*' | head -1)
        # Convert https to tcp format for FTP
        HOST=$(echo "$URL" | sed 's|https://||' | sed 's|/||')
        
        echo ""
        echo -e "${GREEN}✅ FTP Server is ready!${NC}"
        echo ""
        echo -e "${CYAN}Configure your Canon R3 with these settings:${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo -e "FTP Server: ${YELLOW}$HOST${NC}"
        echo -e "Port:       ${YELLOW}80${NC}"
        echo -e "Username:   ${YELLOW}${CANON_R3_USERNAME:-admin}${NC}"
        echo -e "Password:   ${YELLOW}[Your password from .env]${NC}"
        echo -e "Directory:  ${YELLOW}/${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        echo -e "${CYAN}Features:${NC}"
        echo "• Automatic JPEG conversion (95% quality)"
        echo "• Auto-upload to Android device"
        echo "• Files saved to ~/camera/ftp_uploads/"
        echo ""
        echo -e "${YELLOW}Keep this terminal open!${NC}"
        echo ""
    else
        echo "$line"
    fi
done &

SSH_PID=$!

# Keep script running
wait $FTP_PID 