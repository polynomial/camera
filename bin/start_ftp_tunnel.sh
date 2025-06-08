#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.pyftpdlib python3Packages.watchdog python3Packages.python-dotenv ngrok

# Start FTP Server with ngrok tunnel for Canon R3
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

# Set ngrok auth token if provided in .env
if [ ! -z "$NGROK_API_TOKEN" ]; then
    export NGROK_AUTHTOKEN="$NGROK_API_TOKEN"
elif [ ! -z "$NGROK_API_KEY" ]; then
    export NGROK_AUTHTOKEN="$NGROK_API_KEY"
fi

echo -e "${BLUE}Canon R3 FTP Upload Service${NC}"
echo "================================"

# Check if ngrok is configured
if ! ngrok config check >/dev/null 2>&1 && [ -z "$NGROK_AUTHTOKEN" ]; then
    echo -e "${YELLOW}ngrok not configured!${NC}"
    echo ""
    echo "Please sign up for a free ngrok account at: https://ngrok.com"
    echo "Then either:"
    echo "  1. Run: ngrok config add-authtoken YOUR_AUTH_TOKEN"
    echo "  2. Add NGROK_API_TOKEN=your_token to your .env file"
    exit 1
fi

# Create upload directory
mkdir -p ~/camera/ftp_uploads

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill FTP server
    if [ ! -z "$FTP_PID" ]; then
        kill $FTP_PID 2>/dev/null || true
    fi
    
    # Kill ngrok
    if [ ! -z "$NGROK_PID" ]; then
        kill $NGROK_PID 2>/dev/null || true
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

# Start ngrok tunnel
echo -e "${CYAN}Starting ngrok tunnel...${NC}"

# Debug: Show which token we're using
if [ ! -z "$NGROK_AUTHTOKEN" ]; then
    echo "Using ngrok auth token from environment"
else
    echo -e "${RED}No ngrok auth token found!${NC}"
    exit 1
fi

# Start ngrok with explicit auth token
ngrok tcp $FTP_PORT --authtoken="$NGROK_AUTHTOKEN" --log=stdout > /tmp/ngrok.log 2>&1 &
NGROK_PID=$!

# Wait for ngrok to start
echo -n "Waiting for tunnel..."
for i in {1..30}; do
    sleep 1
    
    # Check for errors first
    if grep -q "ERR_NGROK" /tmp/ngrok.log 2>/dev/null; then
        echo -e " ${RED}✗${NC}"
        echo ""
        echo -e "${RED}ngrok error detected:${NC}"
        grep -A5 "ERROR:" /tmp/ngrok.log | tail -20
        exit 1
    fi
    
    # Check for success
    if grep -q "started tunnel" /tmp/ngrok.log 2>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
done

# Get ngrok URL from API
sleep 2
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"[^"]*' | grep -o 'tcp://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo -e "${RED}Failed to get ngrok URL${NC}"
    echo "Check /tmp/ngrok.log for errors"
    exit 1
fi

# Parse host and port from ngrok URL
NGROK_HOST=$(echo $NGROK_URL | sed 's|tcp://||' | cut -d: -f1)
NGROK_PORT=$(echo $NGROK_URL | sed 's|tcp://||' | cut -d: -f2)

echo ""
echo -e "${GREEN}✅ FTP Server is ready!${NC}"
echo ""
echo -e "${CYAN}Configure your Canon R3 with these settings:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "FTP Server: ${YELLOW}$NGROK_HOST${NC}"
echo -e "Port:       ${YELLOW}$NGROK_PORT${NC}"
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
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Keep script running and show FTP server output
wait $FTP_PID 