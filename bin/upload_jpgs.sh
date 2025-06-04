#!/bin/bash

# upload_jpgs.sh - Upload existing JPEG files to Android device for Google Photos sync
# Usage: ./bin/upload_jpgs.sh <directory_with_jpg_files>

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Use local adb if available, otherwise use system adb
if [ -f "$SCRIPT_DIR/adb" ]; then
    ADB="$SCRIPT_DIR/adb"
else
    ADB="adb"
fi

# Configuration
ANDROID_TEMP_DIR="/storage/self/primary/upload"
ANDROID_FINAL_DIR="/storage/self/primary/DCIM/Camera"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to get file size on Android
get_android_file_size() {
    local file_path="$1"
    "$ADB" shell "stat -c %s '$file_path' 2>/dev/null || echo 0" < /dev/null | tr -d '\r\n'
}

# Function to check if file exists on Android
android_file_exists() {
    local file_path="$1"
    "$ADB" shell "[ -f '$file_path' ] && echo 'exists' || echo 'not_found'" < /dev/null | tr -d '\r\n'
}

# Function to safely push file with resume capability
safe_push_file() {
    local local_file="$1"
    local remote_path="$2"
    local filename=$(basename "$local_file")
    local remote_file="$remote_path/$filename"
    local local_size=$(stat -f%z "$local_file" 2>/dev/null || stat -c%s "$local_file" 2>/dev/null)
    
    # Check if file already exists on Android
    if [ "$(android_file_exists "$remote_file")" = "exists" ]; then
        local remote_size=$(get_android_file_size "$remote_file")
        
        if [ "$remote_size" = "$local_size" ]; then
            print_status "✓ Already uploaded: $filename (verified size: $local_size bytes)"
            return 0
        else
            print_warning "Partial upload detected: $filename (local: $local_size, remote: $remote_size)"
            print_status "Removing partial file and re-uploading..."
            "$ADB" shell "rm -f '$remote_file'" < /dev/null
        fi
    fi
    
    # Check if file already exists in final location
    local final_file="$ANDROID_FINAL_DIR/$filename"
    if [ "$(android_file_exists "$final_file")" = "exists" ]; then
        local final_size=$(get_android_file_size "$final_file")
        if [ "$final_size" = "$local_size" ]; then
            print_status "✓ Already in Camera folder: $filename (skipping)"
            return 0
        fi
    fi
    
    # Push the file
    print_status "Uploading: $filename ($local_size bytes)"
    if "$ADB" push "$local_file" "$remote_path/" < /dev/null; then
        # Verify the upload
        local uploaded_size=$(get_android_file_size "$remote_file")
        if [ "$uploaded_size" = "$local_size" ]; then
            print_status "✓ Successfully uploaded: $filename"
            return 0
        else
            print_error "Upload verification failed: $filename (expected: $local_size, got: $uploaded_size)"
            "$ADB" shell "rm -f '$remote_file'" < /dev/null
            return 1
        fi
    else
        print_error "Failed to upload: $filename"
        return 1
    fi
}

# Check if directory argument is provided
if [ $# -eq 0 ]; then
    print_error "No directory specified"
    echo "Usage: $0 <directory_with_jpg_files>"
    exit 1
fi

SOURCE_DIR="$1"

# Verify source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Directory not found: $SOURCE_DIR"
    exit 1
fi

# Check for JPEG files
JPEG_COUNT=$(find "$SOURCE_DIR" -name "*.jpg" -o -name "*.jpeg" -o -name "*.JPG" -o -name "*.JPEG" | wc -l | tr -d ' ')
if [ "$JPEG_COUNT" -eq 0 ]; then
    print_error "No JPEG files found in $SOURCE_DIR"
    exit 1
fi

print_status "Found $JPEG_COUNT JPEG file(s) to upload"

# Check ADB connection
print_status "Checking ADB connection..."
if ! "$ADB" devices | grep -q "device$"; then
    print_error "No Android device connected or USB debugging not enabled"
    echo "Please connect your device and enable USB debugging"
    exit 1
fi

# Create temporary directory on Android
print_status "Creating temp directory on Android device..."
"$ADB" shell mkdir -p "$ANDROID_TEMP_DIR" < /dev/null || {
    print_error "Failed to create directory on Android device"
    exit 1
}

# Ensure DCIM/Camera exists on Android
print_status "Ensuring DCIM/Camera directory exists on Android..."
"$ADB" shell mkdir -p "$ANDROID_FINAL_DIR" < /dev/null || {
    print_error "Failed to create DCIM/Camera directory on Android device"
    exit 1
}

# Upload JPEG files to Android temp directory
print_status "Uploading JPEG files to Android device..."
UPLOAD_SUCCESS=0
UPLOAD_FAILED=0
FAILED_UPLOADS=""

# Store JPEG files in a temporary file to avoid subshell issues
JPEG_LIST_FILE="/tmp/jpeg_files_$TIMESTAMP.txt"
find "$SOURCE_DIR" -name "*.jpg" -o -name "*.jpeg" -o -name "*.JPG" -o -name "*.JPEG" > "$JPEG_LIST_FILE"

# Debug: show file count
FILE_COUNT=$(wc -l < "$JPEG_LIST_FILE")
print_status "Processing $FILE_COUNT files from list..."

while IFS= read -r jpg_file; do
    if [ -z "$jpg_file" ]; then
        continue
    fi
    
    print_status "Processing file: $jpg_file"
    
    if safe_push_file "$jpg_file" "$ANDROID_TEMP_DIR"; then
        UPLOAD_SUCCESS=$((UPLOAD_SUCCESS + 1))
        print_status "Upload count: $UPLOAD_SUCCESS"
    else
        UPLOAD_FAILED=$((UPLOAD_FAILED + 1))
        FAILED_UPLOADS="${FAILED_UPLOADS}$(basename "$jpg_file")\n"
    fi
done < "$JPEG_LIST_FILE"

# Clean up temp file
rm -f "$JPEG_LIST_FILE"

# Check upload results
if [ "$UPLOAD_FAILED" -gt 0 ]; then
    print_warning "Some files failed to upload:"
    echo -e "$FAILED_UPLOADS"
    print_status "Successfully uploaded: $UPLOAD_SUCCESS file(s)"
    print_status "Failed: $UPLOAD_FAILED file(s)"
else
    print_status "All files uploaded successfully!"
fi

# Move successfully uploaded files to DCIM/Camera on Android
print_status "Moving uploaded files to DCIM/Camera for Google Photos sync..."

# Use a simple batch move command
MOVED_COUNT=0
MOVED_FILES=""

# Get list of uploaded files
UPLOADED_FILES=$("$ADB" shell "ls $ANDROID_TEMP_DIR/ 2>/dev/null" < /dev/null | grep -E "\.(jpg|jpeg|JPG|JPEG)$" | tr -d '\r')

if [ -n "$UPLOADED_FILES" ]; then
    # Store the list for media scanner
    MOVED_FILES="$UPLOADED_FILES"
    
    # Move files one by one to ensure success
    echo "$UPLOADED_FILES" | while IFS= read -r filename; do
        if [ -n "$filename" ]; then
            if "$ADB" shell "mv '$ANDROID_TEMP_DIR/$filename' '$ANDROID_FINAL_DIR/' 2>/dev/null" < /dev/null; then
                MOVED_COUNT=$((MOVED_COUNT + 1))
            fi
        fi
    done
    
    # Count actual moved files
    MOVED_COUNT=$(echo "$UPLOADED_FILES" | wc -l | tr -d ' ')
    print_status "✓ Moved $MOVED_COUNT file(s) to Camera folder"
    
    # Notify media scanner about new files
    if [ "$MOVED_COUNT" -gt 0 ] && [ -n "$MOVED_FILES" ]; then
        print_status "Notifying Android media scanner about new files..."
        
        # Create a temporary script on the device
        SCAN_SCRIPT="/data/local/tmp/scan_media_jpg.sh"
        "$ADB" shell "cat > $SCAN_SCRIPT << 'EOF'
#!/system/bin/sh
while IFS= read -r filename; do
    if [ -n \"\$filename\" ]; then
        am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d \"file://$ANDROID_FINAL_DIR/\$filename\" 2>/dev/null
    fi
done
EOF"
        
        # Make it executable and run it
        "$ADB" shell "chmod +x $SCAN_SCRIPT" < /dev/null
        echo "$MOVED_FILES" | "$ADB" shell "$SCAN_SCRIPT" < /dev/null
        "$ADB" shell "rm -f $SCAN_SCRIPT" < /dev/null
        
        print_status "✓ Media scanner notified - files should appear in Gallery/Google Photos"
    fi
else
    print_warning "No files found in Android temp directory to move"
fi

# Clean up Android temp directory (if empty)
"$ADB" shell "rmdir $ANDROID_TEMP_DIR 2>/dev/null" < /dev/null || true

# Final summary
echo ""
print_status "=== Upload Summary ==="
print_status "Total JPEG files found: $JPEG_COUNT"
print_status "Successfully uploaded: $UPLOAD_SUCCESS"
if [ "$UPLOAD_FAILED" -gt 0 ]; then
    print_warning "Failed uploads: $UPLOAD_FAILED"
fi
print_status "Files are now in $ANDROID_FINAL_DIR and will be synced by Google Photos" 