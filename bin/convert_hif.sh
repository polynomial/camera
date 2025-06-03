#!/bin/bash

# convert_hif.sh - Convert HIF files to JPEG
# Usage: ./convert_hif.sh <input.HIF> [output.jpg]

set -e  # Exit on error

# Configuration
DEFAULT_QUALITY=100

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check arguments
if [ $# -lt 1 ]; then
    print_error "No input file specified"
    echo "Usage: $0 <input.HIF> [output.jpg]"
    echo "If output is not specified, it will use the same name with .jpg extension"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-}"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    print_error "Input file not found: $INPUT_FILE"
    exit 1
fi

# Check if ImageMagick is installed
if ! command -v magick &> /dev/null; then
    print_error "ImageMagick not found. Please install imagemagick"
    echo "Run: brew install imagemagick"
    exit 1
fi

# If no output file specified, generate one
if [ -z "$OUTPUT_FILE" ]; then
    # Get the base name without extension
    BASE_NAME="${INPUT_FILE%.*}"
    OUTPUT_FILE="${BASE_NAME}.jpg"
fi

# Check if output file already exists
if [ -f "$OUTPUT_FILE" ]; then
    print_error "Output file already exists: $OUTPUT_FILE"
    echo "Please remove it or specify a different output filename"
    exit 1
fi

# Get file info
INPUT_SIZE=$(ls -lh "$INPUT_FILE" | awk '{print $5}')
print_status "Converting HIF to JPEG..."
print_status "Input: $INPUT_FILE ($INPUT_SIZE)"
print_status "Output: $OUTPUT_FILE"
print_status "Quality: $DEFAULT_QUALITY"

# Perform conversion
if magick "$INPUT_FILE" -quality "$DEFAULT_QUALITY" "$OUTPUT_FILE"; then
    OUTPUT_SIZE=$(ls -lh "$OUTPUT_FILE" | awk '{print $5}')
    print_status "✅ Conversion successful!"
    print_status "Output size: $OUTPUT_SIZE"
else
    print_error "Conversion failed"
    exit 1
fi 