#!/usr/bin/env nix-shell
#!nix-shell -i bash -p ngrok curl

# Test ngrok authentication
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Testing ngrok Authentication${NC}"
echo "============================="

# Load .env file
if [ -f ".env" ]; then
    source .env
    echo -e "${GREEN}✓${NC} Found .env file"
else
    echo -e "${RED}✗${NC} No .env file found"
    exit 1
fi

# Check for ngrok token
echo ""
echo "Checking for ngrok auth token..."

if [ ! -z "$NGROK_API_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Found NGROK_API_TOKEN"
    export NGROK_AUTHTOKEN="$NGROK_API_TOKEN"
elif [ ! -z "$NGROK_API_KEY" ]; then
    echo -e "${GREEN}✓${NC} Found NGROK_API_KEY"
    export NGROK_AUTHTOKEN="$NGROK_API_KEY"
elif [ ! -z "$NGROK_AUTHTOKEN" ]; then
    echo -e "${GREEN}✓${NC} Found NGROK_AUTHTOKEN"
else
    echo -e "${RED}✗${NC} No ngrok token found in environment"
    echo ""
    echo "Please add one of these to your .env file:"
    echo "  NGROK_API_TOKEN=your_token_here"
    echo "  NGROK_API_KEY=your_token_here"
    echo ""
    echo "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Test the token
echo ""
echo "Testing ngrok connection..."
echo "Token: ${NGROK_AUTHTOKEN:0:10}...${NGROK_AUTHTOKEN: -4}"

# Start a test tunnel
ngrok tcp 22 --authtoken="$NGROK_AUTHTOKEN" --log=stdout > /tmp/ngrok_test.log 2>&1 &
NGROK_PID=$!

# Wait and check
sleep 3

if ps -p $NGROK_PID > /dev/null; then
    # Check if tunnel started
    if curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -q "public_url"; then
        echo -e "${GREEN}✓${NC} ngrok is working!"
        echo ""
        echo "Test tunnel info:"
        curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"[^"]*' | head -1
        kill $NGROK_PID 2>/dev/null
        echo ""
        echo -e "${GREEN}Your ngrok token is valid!${NC}"
        echo "You can now run: ./photo-upload --ftp-server"
    else
        echo -e "${RED}✗${NC} ngrok started but no tunnel created"
        kill $NGROK_PID 2>/dev/null
    fi
else
    echo -e "${RED}✗${NC} ngrok failed to start"
    echo ""
    echo "Error log:"
    grep -E "(ERROR:|ERR_NGROK)" /tmp/ngrok_test.log | head -10
    echo ""
    echo "This usually means:"
    echo "1. Your auth token is invalid or expired"
    echo "2. You need to get a new token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    echo "3. Update your .env file with the new token"
fi

rm -f /tmp/ngrok_test.log 