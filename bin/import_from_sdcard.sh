#!/bin/bash

# import_from_sdcard.sh - Import photos from SD card to organized directories
# Usage: ./bin/import_from_sdcard.sh

set -e

# Configuration
DEST_BASE="$HOME/camera"
PHOTO_EXTENSIONS="jpg jpeg JPG JPEG heic HEIC hif HIF cr3 CR3 raw RAW dng DNG"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

# Function to convert bytes to human readable format
bytes_to_human() {
    local bytes=$1
    if [ $bytes -lt 1024 ]; then
        echo "${bytes}B"
    elif [ $bytes -lt 1048576 ]; then
        echo "$(( bytes / 1024 ))KB"
    elif [ $bytes -lt 1073741824 ]; then
        echo "$(( bytes / 1048576 ))MB"
    else
        # Use bc for floating point calculation
        if command -v bc &> /dev/null; then
            echo "$(echo "scale=2; $bytes / 1073741824" | bc)GB"
        else
            # Fallback to integer division
            echo "$(( bytes / 1073741824 ))GB"
        fi
    fi
}

# Function to get file creation date
get_file_date() {
    local file="$1"
    # Try to get date from EXIF data first
    if command -v exiftool &> /dev/null; then
        local exif_date=$(exiftool -DateTimeOriginal -s3 "$file" 2>/dev/null)
        if [ -n "$exif_date" ]; then
            echo "$exif_date" | sed 's/[: ]/-/g' | cut -d'-' -f1-3
            return
        fi
    fi
    
    # Fall back to file modification date
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        stat -f "%Sm" -t "%Y-%m-%d" "$file"
    else
        # Linux
        stat -c "%y" "$file" | cut -d' ' -f1
    fi
}

# Function to find SD cards
find_sdcards() {
    local sdcards=()
    
    # Look for mounted volumes that might be SD cards
    for volume in /Volumes/*; do
        if [ -d "$volume" ]; then
            # Check if it contains DCIM directory (common for cameras)
            if [ -d "$volume/DCIM" ]; then
                sdcards+=("$volume")
            # Check for common SD card names
            elif [[ "$(basename "$volume")" =~ ^(SDCARD|SD|EOS_DIGITAL|CANON|NIKON|SONY|NO NAME|Untitled).*$ ]]; then
                sdcards+=("$volume")
            # Check if it contains image files at root or common directories
            elif find "$volume" -maxdepth 3 -type f \( -iname "*.jpg" -o -iname "*.cr3" -o -iname "*.raw" \) -print -quit 2>/dev/null | grep -q .; then
                sdcards+=("$volume")
            fi
        fi
    done
    
    printf '%s\n' "${sdcards[@]}"
}

# Main script
print_header "SD Card Photo Importer"

# Find SD cards
print_status "Searching for SD cards..."
SDCARDS=($(find_sdcards))

if [ ${#SDCARDS[@]} -eq 0 ]; then
    print_error "No SD cards found in /Volumes"
    print_status "Make sure your SD card is mounted and contains photos"
    exit 1
fi

# If multiple SD cards, let user choose
if [ ${#SDCARDS[@]} -gt 1 ]; then
    print_status "Found multiple potential SD cards:"
    for i in "${!SDCARDS[@]}"; do
        echo "  $((i+1)). ${SDCARDS[$i]}"
    done
    read -p "Select SD card (1-${#SDCARDS[@]}): " choice
    SDCARD="${SDCARDS[$((choice-1))]}"
else
    SDCARD="${SDCARDS[0]}"
fi

print_status "Using SD card: $SDCARD"

# Find all photo files
print_status "Searching for photos..."
PHOTO_FILES=()
for ext in $PHOTO_EXTENSIONS; do
    while IFS= read -r -d '' file; do
        PHOTO_FILES+=("$file")
    done < <(find "$SDCARD" -type f -iname "*.$ext" -print0 2>/dev/null)
done

if [ ${#PHOTO_FILES[@]} -eq 0 ]; then
    print_error "No photo files found on SD card"
    exit 1
fi

print_status "Found ${#PHOTO_FILES[@]} photo(s)"

# Get date range
print_status "Analyzing photo dates..."
FIRST_DATE=""
LAST_DATE=""
TOTAL_SIZE=0

for file in "${PHOTO_FILES[@]}"; do
    # Get file date
    FILE_DATE=$(get_file_date "$file")
    
    # Update first and last dates
    if [ -z "$FIRST_DATE" ] || [[ "$FILE_DATE" < "$FIRST_DATE" ]]; then
        FIRST_DATE="$FILE_DATE"
    fi
    if [ -z "$LAST_DATE" ] || [[ "$FILE_DATE" > "$LAST_DATE" ]]; then
        LAST_DATE="$FILE_DATE"
    fi
    
    # Add to total size
    if [[ "$OSTYPE" == "darwin"* ]]; then
        FILE_SIZE=$(stat -f%z "$file")
    else
        FILE_SIZE=$(stat -c%s "$file")
    fi
    TOTAL_SIZE=$((TOTAL_SIZE + FILE_SIZE))
done

# Create destination directory name
BASE_DIR_NAME="${FIRST_DATE}_${LAST_DATE}"
DEST_DIR="$DEST_BASE/$BASE_DIR_NAME"
COUNTER=1

# Handle existing directories
while [ -d "$DEST_DIR" ]; do
    DEST_DIR="$DEST_BASE/${BASE_DIR_NAME}_$(printf "%03d" $COUNTER)"
    COUNTER=$((COUNTER + 1))
done

# Create destination directory
print_status "Creating directory: $DEST_DIR"
mkdir -p "$DEST_DIR"

# Copy files with progress
print_header "Copying Photos"
COPIED_COUNT=0
FAILED_COUNT=0

for i in "${!PHOTO_FILES[@]}"; do
    file="${PHOTO_FILES[$i]}"
    filename=$(basename "$file")
    
    # Show progress
    echo -ne "\r${GREEN}[PROGRESS]${NC} Copying file $((i+1))/${#PHOTO_FILES[@]}: $filename"
    
    # Copy file
    if cp "$file" "$DEST_DIR/"; then
        COPIED_COUNT=$((COPIED_COUNT + 1))
    else
        FAILED_COUNT=$((FAILED_COUNT + 1))
        echo -e "\n${RED}[ERROR]${NC} Failed to copy: $filename"
    fi
done

echo "" # New line after progress

# Calculate human readable size
HUMAN_SIZE=$(bytes_to_human $TOTAL_SIZE)

# Print summary
print_header "Import Summary"
echo -e "${GREEN}✓ Copied $HUMAN_SIZE and $COPIED_COUNT photos from $FIRST_DATE to $LAST_DATE into $(basename "$DEST_DIR")${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    print_warning "Failed to copy $FAILED_COUNT file(s)"
fi

print_status "Photos imported to: $DEST_DIR"

# Ask if user wants to unmount the SD card
echo ""
read -p "Unmount SD card? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if diskutil unmount "$SDCARD" 2>/dev/null; then
        print_status "SD card unmounted safely"
    else
        print_warning "Could not unmount SD card"
    fi
fi 