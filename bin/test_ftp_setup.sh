#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.pyftpdlib python3Packages.watchdog python3Packages.python-dotenv ngrok curl imagemagick

echo "Testing FTP Server Setup"
echo "========================"

# Test Python modules
echo -n "Python modules: "
if python3 -c "import pyftpdlib, watchdog, dotenv" 2>/dev/null; then
    echo "✓ OK"
else
    echo "✗ FAILED"
    exit 1
fi

# Test ngrok
echo -n "ngrok: "
if which ngrok >/dev/null 2>&1; then
    echo "✓ OK ($(ngrok version | head -1))"
else
    echo "✗ FAILED"
    exit 1
fi

# Test ImageMagick
echo -n "ImageMagick: "
if which magick >/dev/null 2>&1; then
    echo "✓ OK"
else
    echo "✗ FAILED"
    exit 1
fi

# Test environment
echo -n "Environment: "
source .env 2>/dev/null || true
if [ -f ".env" ] && grep -q "CANON_R3_PASSWORD" .env; then
    echo "✓ .env found"
else
    echo "✗ .env missing or incomplete"
fi

# Test ngrok auth
echo -n "ngrok auth: "
if [ ! -z "$NGROK_API_KEY" ] || [ ! -z "$NGROK_API_TOKEN" ]; then
    export NGROK_AUTHTOKEN="${NGROK_API_KEY:-$NGROK_API_TOKEN}"
    echo "✓ Token found"
else
    echo "✗ No token in environment"
fi

echo ""
echo "All dependencies OK! You can run: ./photo-upload --ftp-server" 