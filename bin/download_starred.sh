#!/usr/bin/env nix-shell
#!nix-shell -i bash -p python3 python3Packages.requests python3Packages.python-dotenv

# Canon R3 Starred Image Downloader Wrapper
# This script wraps the Python downloader with nix-shell for dependency management

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/download_starred_from_r3.py"

# Check if .env file exists
if [ ! -f "$SCRIPT_DIR/../.env" ]; then
    echo "Error: .env file not found!"
    echo ""
    echo "Please create a .env file in the repository root with:"
    echo "  CANON_R3_IP=192.168.1.2"
    echo "  CANON_R3_PORT=8080"
    echo "  CANON_R3_USERNAME=admin"
    echo "  CANON_R3_PASSWORD=your_password_here"
    exit 1
fi

# Run the Python script with all arguments
exec python3 "$PYTHON_SCRIPT" "$@" 