#!/bin/bash

# upload_to_android.sh - Upload HIF files to Android device for Google Photos sync
# Usage: ./bin/upload_to_android.sh <directory_with_hif_files>

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
JPEG_QUALITY=${JPEG_QUALITY:-100}  # Use environment variable if set, otherwise default to 100
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
    "$ADB" shell "stat -c %s '$file_path' 2>/dev/null || echo 0" | tr -d '\r\n'
}

# Function to check if file exists on Android
android_file_exists() {
    local file_path="$1"
    "$ADB" shell "[ -f '$file_path' ] && echo 'exists' || echo 'not_found'" | tr -d '\r\n'
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
            "$ADB" shell "rm -f '$remote_file'"
        fi
    fi
    
    # Push the file
    print_status "Uploading: $filename ($local_size bytes)"
    if "$ADB" push "$local_file" "$remote_path/"; then
        # Verify the upload
        local uploaded_size=$(get_android_file_size "$remote_file")
        if [ "$uploaded_size" = "$local_size" ]; then
            print_status "✓ Successfully uploaded: $filename"
            return 0
        else
            print_error "Upload verification failed: $filename (expected: $local_size, got: $uploaded_size)"
            "$ADB" shell "rm -f '$remote_file'"
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
    echo "Usage: $0 <directory_with_hif_files>"
    exit 1
fi

SOURCE_DIR="$1"

# Verify source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    print_error "Directory not found: $SOURCE_DIR"
    exit 1
fi

# Check for HIF files
HIF_COUNT=$(find "$SOURCE_DIR" -name "*.HIF" -o -name "*.hif" | wc -l | tr -d ' ')
if [ "$HIF_COUNT" -eq 0 ]; then
    print_error "No HIF files found in $SOURCE_DIR"
    exit 1
fi

print_status "Found $HIF_COUNT HIF file(s) to process"

# Check dependencies
if ! "$ADB" version &> /dev/null; then
    print_error "ADB not found or not working"
    exit 1
fi

if ! command -v magick &> /dev/null; then
    print_error "ImageMagick not found. Please run this script within nix-shell"
    exit 1
fi

# Check ADB connection
print_status "Checking ADB connection..."
if ! "$ADB" devices | grep -q "device$"; then
    print_error "No Android device connected or USB debugging not enabled"
    echo "Please connect your device and enable USB debugging"
    exit 1
fi

# Create temporary directory locally
LOCAL_TEMP_DIR="$PROJECT_ROOT/temp/upload_${TIMESTAMP}"
mkdir -p "$LOCAL_TEMP_DIR"
print_status "Created local temp directory: $LOCAL_TEMP_DIR"

# Create state file to track progress
STATE_FILE="$LOCAL_TEMP_DIR/.upload_state"
touch "$STATE_FILE"

# Create temporary directory on Android
print_status "Creating temp directory on Android device..."
"$ADB" shell mkdir -p "$ANDROID_TEMP_DIR" || {
    print_error "Failed to create directory on Android device"
    exit 1
}

# Ensure DCIM/Camera exists on Android
print_status "Ensuring DCIM/Camera directory exists on Android..."
"$ADB" shell mkdir -p "$ANDROID_FINAL_DIR" || {
    print_error "Failed to create DCIM/Camera directory on Android device"
    exit 1
}

# Convert HIF files to JPEG
print_status "Converting HIF files to JPEG..."
CONVERTED_COUNT=0
FAILED_CONVERSIONS=""

# Store HIF files in a temporary file to avoid subshell issues
HIF_LIST_FILE="$LOCAL_TEMP_DIR/.hif_files"
find "$SOURCE_DIR" -name "*.HIF" -o -name "*.hif" > "$HIF_LIST_FILE"

while IFS= read -r hif_file; do
    filename=$(basename "$hif_file")
    base_name="${filename%.*}"
    output_file="$LOCAL_TEMP_DIR/${base_name}.jpg"
    
    # Check if already converted
    if [ -f "$output_file" ]; then
        print_status "✓ Already converted: $filename"
        CONVERTED_COUNT=$((CONVERTED_COUNT + 1))
        continue
    fi
    
    print_status "Converting: $filename"
    
    if magick "$hif_file" -quality "$JPEG_QUALITY" "$output_file" 2>/dev/null; then
        CONVERTED_COUNT=$((CONVERTED_COUNT + 1))
        print_status "✓ Converted: $filename → ${base_name}.jpg"
        echo "CONVERTED:$output_file" >> "$STATE_FILE"
    else
        print_warning "Failed to convert: $filename"
        FAILED_CONVERSIONS="${FAILED_CONVERSIONS}$filename\n"
    fi
done < "$HIF_LIST_FILE"

# Clean up temp file
rm -f "$HIF_LIST_FILE"

# Check if any files were converted
JPEG_COUNT=$(find "$LOCAL_TEMP_DIR" -name "*.jpg" | wc -l | tr -d ' ')
if [ "$JPEG_COUNT" -eq 0 ]; then
    print_error "No files were successfully converted"
    rm -rf "$LOCAL_TEMP_DIR"
    exit 1
fi

print_status "Successfully converted $JPEG_COUNT file(s)"

# Upload files to Android temp directory with resume capability
print_status "Uploading files to Android device..."
UPLOAD_SUCCESS=0
UPLOAD_FAILED=0
FAILED_UPLOADS=""

# Use a different approach to avoid subshell issues
for jpg_file in "$LOCAL_TEMP_DIR"/*.jpg; do
    if [ -f "$jpg_file" ]; then
        if safe_push_file "$jpg_file" "$ANDROID_TEMP_DIR"; then
            UPLOAD_SUCCESS=$((UPLOAD_SUCCESS + 1))
            echo "UPLOADED:$(basename "$jpg_file")" >> "$STATE_FILE"
        else
            UPLOAD_FAILED=$((UPLOAD_FAILED + 1))
            FAILED_UPLOADS="${FAILED_UPLOADS}$(basename "$jpg_file")\n"
        fi
    fi
done

# Check upload results
if [ "$UPLOAD_FAILED" -gt 0 ]; then
    print_warning "Some files failed to upload:"
    echo -e "$FAILED_UPLOADS"
    print_status "Successfully uploaded: $UPLOAD_SUCCESS file(s)"
    print_status "Failed: $UPLOAD_FAILED file(s)"
    print_warning "You can re-run this script to retry failed uploads"
else
    print_status "All files uploaded successfully!"
fi

# Move successfully uploaded files to DCIM/Camera on Android
print_status "Moving uploaded files to DCIM/Camera for Google Photos sync..."

# Use a simple batch move command
MOVED_COUNT=0
MOVED_FILES=""

if "$ADB" shell "ls $ANDROID_TEMP_DIR/*.jpg 2>/dev/null" | grep -q ".jpg"; then
    # Count files before move
    FILES_TO_MOVE=$("$ADB" shell "ls $ANDROID_TEMP_DIR/*.jpg 2>/dev/null | wc -l" | tr -d '\r\n ')
    
    # Get list of files to track for media scanner
    MOVED_FILES=$("$ADB" shell "ls $ANDROID_TEMP_DIR/*.jpg 2>/dev/null" | tr -d '\r' | while read -r f; do basename "$f"; done)
    
    # Move all files at once
    if "$ADB" shell "cd $ANDROID_TEMP_DIR && mv *.jpg $ANDROID_FINAL_DIR/ 2>/dev/null"; then
        MOVED_COUNT=$FILES_TO_MOVE
        print_status "✓ Moved $MOVED_COUNT file(s) to Camera folder"
    else
        # If batch move fails, try one by one
        print_warning "Batch move failed, trying individual moves..."
        MOVED_FILES=""
        
        "$ADB" shell "ls $ANDROID_TEMP_DIR/*.jpg 2>/dev/null" | tr -d '\r' | while IFS= read -r temp_file; do
            if [ -n "$temp_file" ]; then
                filename=$(basename "$temp_file")
                if "$ADB" shell "mv '$temp_file' '$ANDROID_FINAL_DIR/' 2>/dev/null"; then
                    MOVED_COUNT=$((MOVED_COUNT + 1))
                    MOVED_FILES="${MOVED_FILES}${filename}\n"
                    print_status "✓ Moved to Camera: $filename"
                else
                    print_warning "Failed to move: $filename"
                fi
            fi
        done
    fi
    
    # Notify media scanner about new files
    if [ "$MOVED_COUNT" -gt 0 ] && [ -n "$MOVED_FILES" ]; then
        print_status "Notifying Android media scanner about new files..."
        
        # Create a temporary script on the device
        SCAN_SCRIPT="/data/local/tmp/scan_media.sh"
        "$ADB" shell "cat > $SCAN_SCRIPT << 'EOF'
#!/system/bin/sh
while IFS= read -r filename; do
    if [ -n \"\$filename\" ]; then
        am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d \"file://$ANDROID_FINAL_DIR/\$filename\" 2>/dev/null
    fi
done
EOF"
        
        # Make it executable and run it
        "$ADB" shell "chmod +x $SCAN_SCRIPT"
        echo -e "$MOVED_FILES" | "$ADB" shell "$SCAN_SCRIPT"
        "$ADB" shell "rm -f $SCAN_SCRIPT"
        
        print_status "✓ Media scanner notified - files should appear in Gallery/Google Photos"
    fi
else
    print_warning "No files found in Android temp directory to move"
fi

# Clean up local temp directory (optional - based on success)
if [ "$UPLOAD_FAILED" -eq 0 ]; then
    print_status "Cleaning up local temporary files..."
    rm -rf "$LOCAL_TEMP_DIR"
else
    print_warning "Keeping local temp files due to failed uploads: $LOCAL_TEMP_DIR"
    print_status "Re-run the script to retry failed uploads"
fi

# Clean up Android temp directory (if empty)
"$ADB" shell "rmdir $ANDROID_TEMP_DIR 2>/dev/null" || true

# Final summary
echo ""
print_status "=== Upload Summary ==="
print_status "Total HIF files found: $HIF_COUNT"
print_status "Successfully converted: $JPEG_COUNT"
print_status "Successfully uploaded: $UPLOAD_SUCCESS"
print_status "Successfully moved to Camera: $MOVED_COUNT"
if [ "$UPLOAD_FAILED" -gt 0 ]; then
    print_warning "Failed uploads: $UPLOAD_FAILED (kept in $LOCAL_TEMP_DIR)"
fi
print_status "Files are now in $ANDROID_FINAL_DIR and will be synced by Google Photos" 