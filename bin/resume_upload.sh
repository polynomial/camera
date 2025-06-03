#!/bin/bash

# resume_upload.sh - Resume interrupted uploads to Android device
# Usage: ./bin/resume_upload.sh [temp_directory]

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Use local adb if available
if [ -f "$SCRIPT_DIR/adb" ]; then
    ADB="$SCRIPT_DIR/adb"
else
    ADB="adb"
fi

# Configuration
ANDROID_TEMP_DIR="/storage/self/primary/upload"
ANDROID_FINAL_DIR="/storage/self/primary/DCIM/Camera"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to get file size on Android
get_android_file_size() {
    local file_path="$1"
    "$ADB" shell "stat -c %s '$file_path' 2>/dev/null || echo 0" | tr -d '\r\n'
}

# Function to check if file exists on Android
android_file_exists() {
    local file_path="$1"
    "$ADB" shell "[ -f '$file_path' ] && echo 'exists' || echo 'not_found'" | tr -d '\r\n'
}

# Find temp directory
if [ $# -eq 1 ]; then
    TEMP_DIR="$1"
else
    # Find most recent temp directory
    TEMP_DIR=$(find "$PROJECT_ROOT/temp" -name "upload_*" -type d 2>/dev/null | sort -r | head -n 1)
fi

if [ -z "$TEMP_DIR" ] || [ ! -d "$TEMP_DIR" ]; then
    print_error "No temp directory found. Nothing to resume."
    echo "Usage: $0 [temp_directory]"
    exit 1
fi

print_status "Resuming upload from: $TEMP_DIR"

# Check ADB connection
if ! "$ADB" devices | grep -q "device$"; then
    print_error "No Android device connected"
    exit 1
fi

# Count files to process
JPEG_COUNT=$(find "$TEMP_DIR" -name "*.jpg" 2>/dev/null | wc -l | tr -d ' ')
if [ "$JPEG_COUNT" -eq 0 ]; then
    print_warning "No JPEG files found in temp directory"
    exit 1
fi

print_status "Found $JPEG_COUNT JPEG file(s) to check/upload"

# Check and upload files
ALREADY_UPLOADED=0
NEWLY_UPLOADED=0
FAILED=0

# Store JPEG files in a temporary file to avoid subshell issues
JPEG_LIST_FILE="$TEMP_DIR/.jpeg_files"
find "$TEMP_DIR" -name "*.jpg" 2>/dev/null > "$JPEG_LIST_FILE"

while IFS= read -r jpg_file; do
    if [ -z "$jpg_file" ]; then
        continue
    fi
    
    filename=$(basename "$jpg_file")
    remote_file="$ANDROID_TEMP_DIR/$filename"
    local_size=$(stat -f%z "$jpg_file" 2>/dev/null || stat -c%s "$jpg_file" 2>/dev/null)
    
    # Check if file exists on Android
    if [ "$(android_file_exists "$remote_file")" = "exists" ]; then
        remote_size=$(get_android_file_size "$remote_file")
        
        if [ "$remote_size" = "$local_size" ]; then
            print_status "✓ Already uploaded: $filename"
            ALREADY_UPLOADED=$((ALREADY_UPLOADED + 1))
            
            # Try to move to final location if not already there
            final_file="$ANDROID_FINAL_DIR/$filename"
            if [ "$(android_file_exists "$final_file")" != "exists" ]; then
                if "$ADB" shell "mv '$remote_file' '$ANDROID_FINAL_DIR/' 2>/dev/null"; then
                    print_status "  → Moved to Camera folder"
                fi
            fi
            continue
        else
            print_warning "Partial upload detected: $filename (removing and re-uploading)"
            "$ADB" shell "rm -f '$remote_file'"
        fi
    fi
    
    # Upload the file
    print_status "Uploading: $filename"
    if "$ADB" push "$jpg_file" "$ANDROID_TEMP_DIR/"; then
        # Verify upload
        uploaded_size=$(get_android_file_size "$remote_file")
        if [ "$uploaded_size" = "$local_size" ]; then
            print_status "✓ Successfully uploaded: $filename"
            NEWLY_UPLOADED=$((NEWLY_UPLOADED + 1))
            
            # Move to final location
            if "$ADB" shell "mv '$remote_file' '$ANDROID_FINAL_DIR/' 2>/dev/null"; then
                print_status "  → Moved to Camera folder"
            fi
        else
            print_error "Upload verification failed: $filename"
            FAILED=$((FAILED + 1))
        fi
    else
        print_error "Failed to upload: $filename"
        FAILED=$((FAILED + 1))
    fi
done < "$JPEG_LIST_FILE"

# Clean up temp file
rm -f "$JPEG_LIST_FILE"

# Clean up Android temp directory if empty
"$ADB" shell "rmdir $ANDROID_TEMP_DIR 2>/dev/null" || true

# Summary
echo ""
print_status "=== Resume Summary ==="
print_status "Already uploaded: $ALREADY_UPLOADED"
print_status "Newly uploaded: $NEWLY_UPLOADED"
if [ "$FAILED" -gt 0 ]; then
    print_warning "Failed: $FAILED"
    print_status "Temp directory kept: $TEMP_DIR"
else
    print_status "All files processed successfully!"
    
    # Ask if user wants to clean up
    echo -e "${YELLOW}Delete temp directory? (y/N)${NC}"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf "$TEMP_DIR"
        print_status "Temp directory deleted"
    else
        print_status "Temp directory kept: $TEMP_DIR"
    fi
fi 