#!/usr/bin/env nix-shell
#!nix-shell -i bash -p imagemagick

# Process downloaded Canon R3 images
# Converts CR3 to JPEG and uploads to Android device

set -e
# set -x  # Uncomment for debugging

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
    export $(grep -v '^#' "$PROJECT_ROOT/.env" | xargs)
fi

# Default settings
DOWNLOAD_DIR="${1:-canon_r3_downloads}"
JPEG_QUALITY="${JPEG_QUALITY:-95}"
ANDROID_PORT="${ANDROID_PORT:-8080}"
TEMP_DIR="/tmp/r3_jpeg_$$"

# Check if download directory exists
if [ ! -d "$DOWNLOAD_DIR" ]; then
    echo -e "${RED}Error: Directory '$DOWNLOAD_DIR' not found${NC}"
    exit 1
fi

# Check Android device connection
if ! adb devices | grep -q "device$"; then
    echo -e "${RED}Error: No Android device connected${NC}"
    echo "Please connect your Android device with USB debugging enabled"
    exit 1
fi

# Ensure DCIM/Camera directory exists on Android
adb shell mkdir -p /storage/emulated/0/DCIM/Camera

echo -e "${BLUE}Canon R3 Download Processor${NC}"
echo "============================"
echo -e "Source: ${CYAN}$DOWNLOAD_DIR${NC}"
echo -e "Android: ${CYAN}Connected via ADB${NC}"
echo -e "JPEG Quality: ${CYAN}$JPEG_QUALITY%${NC}"
echo ""

# Create temp directory for JPEGs
mkdir -p "$TEMP_DIR"

# Cleanup on exit
cleanup() {
    rm -rf "$TEMP_DIR"
}
trap cleanup EXIT

# Find all CR3 files
CR3_FILES=($(find "$DOWNLOAD_DIR" -name "*.CR3" -type f))
TOTAL_FILES=${#CR3_FILES[@]}

if [ $TOTAL_FILES -eq 0 ]; then
    echo -e "${YELLOW}No CR3 files found in $DOWNLOAD_DIR${NC}"
    exit 0
fi

echo -e "${CYAN}Found $TOTAL_FILES CR3 files to process${NC}"
echo ""

# Process each file
SUCCESS_COUNT=0
UPLOAD_COUNT=0

for i in "${!CR3_FILES[@]}"; do
    CR3_FILE="${CR3_FILES[$i]}"
    FILENAME=$(basename "$CR3_FILE" .CR3)
    JPEG_FILE="$TEMP_DIR/${FILENAME}.jpg"
    
    echo -e "${BLUE}[$((i+1))/$TOTAL_FILES]${NC} Processing $FILENAME..."
    
    # Convert CR3 to JPEG
    echo -n "  Converting to JPEG... "
    if magick "$CR3_FILE" -quality "$JPEG_QUALITY" "$JPEG_FILE" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        ((SUCCESS_COUNT++)) || true
        
        # Upload to Android
        echo -n "  Uploading to Android... "
        
        # Push file via ADB
        if adb push "$JPEG_FILE" "/storage/emulated/0/DCIM/Camera/${FILENAME}.jpg" >/dev/null 2>&1; then
            echo -e "${GREEN}✓${NC}"
            ((UPLOAD_COUNT++)) || true
            
            # Trigger media scan
            echo -n "  Triggering media scan... "
            if adb shell am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "file:///storage/emulated/0/DCIM/Camera/${FILENAME}.jpg" >/dev/null 2>&1; then
                echo -e "${GREEN}✓${NC}"
            else
                echo -e "${YELLOW}⚠${NC}"
            fi
        else
            echo -e "${RED}✗${NC}"
            echo "    Error: Failed to push file to Android"
        fi
        
        # Clean up temp file
        rm -f "$JPEG_FILE"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    echo ""
done

# Summary
echo "================================"
echo -e "${GREEN}Processing Complete!${NC}"
echo "================================"
echo -e "Files processed: ${CYAN}$TOTAL_FILES${NC}"
echo -e "Converted to JPEG: ${GREEN}$SUCCESS_COUNT${NC}"
echo -e "Uploaded to Android: ${GREEN}$UPLOAD_COUNT${NC}"

if [ $UPLOAD_COUNT -gt 0 ]; then
    echo ""
    echo -e "${CYAN}Photos are now available in your Android gallery!${NC}"
fi 